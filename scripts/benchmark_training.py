import argparse
import time
import torch
import yaml
from pathlib import Path

from models.gpt import GPT, GPTConfig


def benchmark_training(config_path: str, steps: int = 100):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    model_config = GPTConfig(**config["model"])
    model = GPT(model_config).to(device)

    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {num_params/1e6:.2f}M")

    batch_size = config["training"]["batch_size"]
    block_size = model_config.block_size

    x = torch.randint(0, model_config.vocab_size, (batch_size, block_size), device=device)
    y = torch.randint(0, model_config.vocab_size, (batch_size, block_size), device=device)

    model.train()
    optimizer = model.configure_optimizers(
        weight_decay=0.1,
        learning_rate=1e-3,
        betas=(0.9, 0.95),
        device_type=device.split(":")[0]
    )

    print(f"\nWarming up...")
    for _ in range(10):
        logits, loss = model(x, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    if device == "cuda":
        torch.cuda.synchronize()

    print(f"\nBenchmarking {steps} steps...")
    start_time = time.time()

    for step in range(steps):
        logits, loss = model(x, y)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if (step + 1) % 10 == 0:
            if device == "cuda":
                torch.cuda.synchronize()
            elapsed = time.time() - start_time
            steps_per_sec = (step + 1) / elapsed
            tokens_per_sec = steps_per_sec * batch_size * block_size

            print(f"Step {step+1}/{steps}: {steps_per_sec:.2f} steps/s, {tokens_per_sec/1000:.1f}K tokens/s")

    if device == "cuda":
        torch.cuda.synchronize()

    total_time = time.time() - start_time
    steps_per_sec = steps / total_time
    tokens_per_sec = steps_per_sec * batch_size * block_size

    print(f"\n{'='*60}")
    print(f"Benchmark Results:")
    print(f"{'='*60}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Steps/sec: {steps_per_sec:.2f}")
    print(f"Tokens/sec: {tokens_per_sec/1000:.1f}K")
    print(f"Time per step: {total_time/steps*1000:.2f}ms")

    if device == "cuda":
        print(f"\nGPU Memory:")
        print(f"Allocated: {torch.cuda.memory_allocated()/1e9:.2f} GB")
        print(f"Reserved: {torch.cuda.memory_reserved()/1e9:.2f} GB")
        print(f"Max allocated: {torch.cuda.max_memory_allocated()/1e9:.2f} GB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark training performance")
    parser.add_argument("--config", type=str, required=True, help="Path to config file")
    parser.add_argument("--steps", type=int, default=100, help="Number of steps to benchmark")
    args = parser.parse_args()

    benchmark_training(args.config, args.steps)
