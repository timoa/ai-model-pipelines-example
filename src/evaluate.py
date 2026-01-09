import argparse
import os
import torch
import yaml
from pathlib import Path
from typing import List, Dict, Any
import json

from src.models.gpt import GPT, GPTConfig
from transformers import AutoTokenizer

try:
    from python.runfiles import runfiles
    r = runfiles.Create()
    def resolve_path(path):
        """Resolve path for Bazel runfiles or return original path."""
        if r:
            resolved = r.Rlocation(f"_main/{path}")
            return resolved if resolved and os.path.exists(resolved) else path
        return path
except ImportError:
    def resolve_path(path):
        """Fallback when not running under Bazel."""
        return path


def load_model(checkpoint_path: str, device: str) -> GPT:
    checkpoint = torch.load(checkpoint_path, map_location=device)

    if "config" in checkpoint:
        model_config = GPTConfig(**checkpoint["config"]["model"])
    else:
        model_config = GPTConfig()

    model = GPT(model_config)

    if "model" in checkpoint:
        model.load_state_dict(checkpoint["model"])
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()
    return model


def evaluate_perplexity(
    model: GPT, data_path: str, device: str, max_samples: int = 100
) -> float:
    import numpy as np

    data = np.memmap(data_path, dtype=np.uint16, mode="r")
    block_size = model.config.block_size

    total_loss = 0.0
    num_samples = min(max_samples, len(data) // block_size)

    with torch.no_grad():
        for i in range(num_samples):
            start_idx = i * block_size
            end_idx = start_idx + block_size + 1
            chunk = torch.from_numpy((data[start_idx:end_idx]).astype(np.int64))
            x = chunk[:-1].unsqueeze(0).to(device)
            y = chunk[1:].unsqueeze(0).to(device)

            _, loss = model(x, y)
            total_loss += loss.item()

    avg_loss = total_loss / num_samples
    perplexity = torch.exp(torch.tensor(avg_loss)).item()
    return perplexity


def evaluate_generation(
    model: GPT, tokenizer, prompts: List[str], device: str
) -> List[str]:
    generations = []

    with torch.no_grad():
        for prompt in prompts:
            tokens = tokenizer.encode(prompt)
            x = torch.tensor(tokens, dtype=torch.long, device=device).unsqueeze(0)

            y = model.generate(x, max_new_tokens=100, temperature=0.8, top_k=200)
            generated_text = tokenizer.decode(y[0].tolist())
            generations.append(generated_text)

    return generations


def run_evaluation(config_path: str, checkpoint_path: str, output_path: str):
    resolved_config_path = resolve_path(config_path)
    with open(resolved_config_path, "r") as f:
        config = yaml.safe_load(f)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print(f"Loading model from {checkpoint_path}...")
    model = load_model(checkpoint_path, device)
    print(
        f"Model loaded: {sum(p.numel() for p in model.parameters())/1e6:.2f}M parameters"
    )

    results: Dict[str, Any] = {}

    if "eval_data" in config["data"]:
        print("\nEvaluating perplexity...")
        perplexity = evaluate_perplexity(
            model,
            config["data"]["eval_data"],
            device,
            max_samples=config.get("eval", {}).get("max_samples", 100),
        )
        results["perplexity"] = perplexity
        print(f"Perplexity: {perplexity:.2f}")

    if "eval_prompts" in config.get("eval", {}):
        print("\nGenerating samples...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        generations = evaluate_generation(
            model, tokenizer, config["eval"]["eval_prompts"], device
        )
        results["generations"] = [
            {"prompt": p, "generated": g}
            for p, g in zip(config["eval"]["eval_prompts"], generations)
        ]

        for i, (prompt, gen) in enumerate(
            zip(config["eval"]["eval_prompts"], generations)
        ):
            print(f"\nPrompt {i+1}: {prompt}")
            print(f"Generated: {gen[:200]}...")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to config file")
    parser.add_argument(
        "--checkpoint", type=str, required=True, help="Path to model checkpoint"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/eval_results.json",
        help="Output path for results",
    )
    args = parser.parse_args()

    run_evaluation(args.config, args.checkpoint, args.output)
