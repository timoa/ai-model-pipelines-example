import os
import time
import math
import argparse
from contextlib import nullcontext
from pathlib import Path

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import yaml

from models.gpt import GPT, GPTConfig
from data.dataset import TextDataset


def setup_distributed():
    if "RANK" in os.environ and "WORLD_SIZE" in os.environ:
        rank = int(os.environ["RANK"])
        world_size = int(os.environ["WORLD_SIZE"])
        local_rank = int(os.environ.get("LOCAL_RANK", 0))
        dist.init_process_group(backend="nccl", rank=rank, world_size=world_size)
        torch.cuda.set_device(local_rank)
        return rank, world_size, local_rank
    return 0, 1, 0


def cleanup_distributed():
    if dist.is_initialized():
        dist.destroy_process_group()


def get_lr(it, warmup_iters, learning_rate, lr_decay_iters, min_lr):
    if it < warmup_iters:
        return learning_rate * it / warmup_iters
    if it > lr_decay_iters:
        return min_lr
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)


def train(config_path: str):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    rank, world_size, local_rank = setup_distributed()
    is_master = rank == 0

    torch.manual_seed(config["training"]["seed"] + rank)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    device = f"cuda:{local_rank}" if torch.cuda.is_available() else "cpu"
    device_type = "cuda" if "cuda" in device else "cpu"
    
    ptdtype = {"float32": torch.float32, "bfloat16": torch.bfloat16, "float16": torch.float16}[config["training"]["dtype"]]
    ctx = nullcontext() if device_type == "cpu" else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

    model_config = GPTConfig(**config["model"])
    model = GPT(model_config)
    model.to(device)

    if world_size > 1:
        model = DDP(model, device_ids=[local_rank])
    raw_model = model.module if isinstance(model, DDP) else model

    scaler = torch.cuda.amp.GradScaler(enabled=(config["training"]["dtype"] == "float16"))
    optimizer = raw_model.configure_optimizers(
        weight_decay=config["training"]["weight_decay"],
        learning_rate=config["training"]["learning_rate"],
        betas=(config["training"]["beta1"], config["training"]["beta2"]),
        device_type=device_type,
    )

    train_dataset = TextDataset(
        data_dir=config["data"]["train_dir"],
        block_size=model_config.block_size,
    )
    
    sampler = DistributedSampler(train_dataset, num_replicas=world_size, rank=rank) if world_size > 1 else None
    train_loader = DataLoader(
        train_dataset,
        batch_size=config["training"]["batch_size"],
        sampler=sampler,
        num_workers=config["training"]["num_workers"],
        pin_memory=True,
    )

    output_dir = Path(config["training"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    iter_num = 0
    best_val_loss = 1e9
    running_loss = 0.0

    if is_master:
        print(f"Training GPT model with {sum(p.numel() for p in model.parameters())/1e6:.2f}M parameters")
        print(f"World size: {world_size}, Device: {device}, dtype: {config['training']['dtype']}")

    model.train()
    t0 = time.time()

    for epoch in range(config["training"]["max_epochs"]):
        if sampler:
            sampler.set_epoch(epoch)

        for batch_idx, (x, y) in enumerate(train_loader):
            x, y = x.to(device), y.to(device)

            lr = get_lr(
                iter_num,
                config["training"]["warmup_iters"],
                config["training"]["learning_rate"],
                config["training"]["lr_decay_iters"],
                config["training"]["min_lr"],
            )
            for param_group in optimizer.param_groups:
                param_group["lr"] = lr

            with ctx:
                logits, loss = model(x, y)
                loss = loss / config["training"]["gradient_accumulation_steps"]

            scaler.scale(loss).backward()

            if (batch_idx + 1) % config["training"]["gradient_accumulation_steps"] == 0:
                if config["training"]["grad_clip"] != 0.0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), config["training"]["grad_clip"])
                
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)

            running_loss += loss.item()

            if iter_num % config["training"]["log_interval"] == 0 and is_master:
                t1 = time.time()
                dt = t1 - t0
                lossf = running_loss / config["training"]["log_interval"]
                print(f"iter {iter_num}: loss {lossf:.4f}, lr {lr:.6f}, time {dt*1000:.2f}ms")
                running_loss = 0.0
                t0 = t1

            if iter_num % config["training"]["eval_interval"] == 0 and iter_num > 0:
                if is_master:
                    checkpoint = {
                        "model": raw_model.state_dict(),
                        "optimizer": optimizer.state_dict(),
                        "iter_num": iter_num,
                        "config": config,
                    }
                    checkpoint_path = output_dir / f"checkpoint_{iter_num}.pt"
                    torch.save(checkpoint, checkpoint_path)
                    print(f"Saved checkpoint to {checkpoint_path}")

            iter_num += 1
            if iter_num >= config["training"]["max_iters"]:
                break

        if iter_num >= config["training"]["max_iters"]:
            break

    if is_master:
        final_checkpoint = output_dir / "final_model.pt"
        torch.save(raw_model.state_dict(), final_checkpoint)
        print(f"Training complete. Final model saved to {final_checkpoint}")

    cleanup_distributed()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to config file")
    args = parser.parse_args()
    
    train(args.config)
