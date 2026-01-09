import argparse
import numpy as np
from pathlib import Path


def generate_test_data(output_dir: Path, num_tokens: int = 10000):
    """Generate minimal test data for smoke testing."""
    output_dir.mkdir(parents=True, exist_ok=True)

    tokens = np.random.randint(0, 50257, size=num_tokens, dtype=np.uint16)

    output_file = output_dir / "data.bin"
    tokens.tofile(str(output_file))

    print(f"Generated {num_tokens:,} random tokens")
    print(f"Saved to {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.2f} KB")


def main():
    parser = argparse.ArgumentParser(description="Generate test data for CI/smoke testing")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/train",
        help="Output directory for test data",
    )
    parser.add_argument(
        "--num-tokens",
        type=int,
        default=10000,
        help="Number of tokens to generate",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    generate_test_data(output_dir, args.num_tokens)


if __name__ == "__main__":
    main()
