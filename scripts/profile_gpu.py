import argparse
import torch
import yaml
from torch.profiler import profile, record_function, ProfilerActivity

from models.gpt import GPT, GPTConfig


def profile_training(config_path: str, steps: int = 10):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    if device == "cpu":
        print("Warning: GPU profiling requires CUDA")
        return

    print(f"Profiling on {torch.cuda.get_device_name(0)}")

    model_config = GPTConfig(**config["model"])
    model = GPT(model_config).to(device)

    batch_size = config["training"]["batch_size"]
    block_size = model_config.block_size

    x = torch.randint(0, model_config.vocab_size, (batch_size, block_size), device=device)
    y = torch.randint(0, model_config.vocab_size, (batch_size, block_size), device=device)

    model.train()
    optimizer = model.configure_optimizers(
        weight_decay=0.1,
        learning_rate=1e-3,
        betas=(0.9, 0.95),
        device_type="cuda"
    )

    print(f"\nProfiling {steps} training steps...")

    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        record_shapes=True,
        profile_memory=True,
        with_stack=True,
    ) as prof:
        for step in range(steps):
            with record_function("forward"):
                logits, loss = model(x, y)

            with record_function("backward"):
                loss.backward()

            with record_function("optimizer"):
                optimizer.step()
                optimizer.zero_grad()

    print("\n" + "="*80)
    print("Top 10 operations by CUDA time:")
    print("="*80)
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

    print("\n" + "="*80)
    print("Top 10 operations by CPU time:")
    print("="*80)
    print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10))

    print("\n" + "="*80)
    print("Top 10 operations by memory:")
    print("="*80)
    print(prof.key_averages().table(sort_by="cuda_memory_usage", row_limit=10))

    output_file = "profile_trace.json"
    prof.export_chrome_trace(output_file)
    print(f"\nProfile trace saved to {output_file}")
    print(f"View in Chrome: chrome://tracing")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile GPU training performance")
    parser.add_argument("--config", type=str, required=True, help="Path to config file")
    parser.add_argument("--steps", type=int, default=10, help="Number of steps to profile")
    args = parser.parse_args()

    profile_training(args.config, args.steps)
