import argparse
import numpy as np
import json
from pathlib import Path


def analyze_data(data_file: Path):
    print(f"Analyzing {data_file}...")
    data = np.memmap(data_file, dtype=np.uint16, mode="r")
    
    stats = {
        "file": str(data_file),
        "total_tokens": int(len(data)),
        "file_size_gb": data_file.stat().st_size / (1024**3),
        "vocab_size": int(data.max()) + 1,
        "unique_tokens": int(len(np.unique(data))),
        "min_token_id": int(data.min()),
        "max_token_id": int(data.max()),
    }
    
    token_counts = np.bincount(data)
    top_10_indices = np.argsort(token_counts)[-10:][::-1]
    
    stats["top_10_tokens"] = [
        {"token_id": int(idx), "count": int(token_counts[idx])}
        for idx in top_10_indices
    ]
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Generate statistics for tokenized data")
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Directory containing tokenized data",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/data_stats.json",
        help="Output file for statistics",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_file = Path(args.output)
    
    data_files = list(data_dir.glob("**/*.bin"))
    
    if not data_files:
        raise ValueError(f"No .bin files found in {data_dir}")
    
    all_stats = []
    for data_file in data_files:
        stats = analyze_data(data_file)
        all_stats.append(stats)
        
        print(f"\nStatistics for {data_file.name}:")
        print(f"  Total tokens: {stats['total_tokens']:,}")
        print(f"  File size: {stats['file_size_gb']:.2f} GB")
        print(f"  Vocab size: {stats['vocab_size']:,}")
        print(f"  Unique tokens: {stats['unique_tokens']:,}")
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(all_stats, f, indent=2)
    
    print(f"\nStatistics saved to {output_file}")


if __name__ == "__main__":
    main()
