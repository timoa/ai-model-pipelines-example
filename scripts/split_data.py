import argparse
import numpy as np
from pathlib import Path


def split_data(input_file: Path, train_dir: Path, val_dir: Path, val_split: float):
    print(f"Loading data from {input_file}...")
    data = np.memmap(input_file, dtype=np.uint16, mode="r")
    
    total_tokens = len(data)
    val_tokens = int(total_tokens * val_split)
    train_tokens = total_tokens - val_tokens
    
    print(f"Total tokens: {total_tokens:,}")
    print(f"Train tokens: {train_tokens:,} ({(1-val_split)*100:.1f}%)")
    print(f"Val tokens: {val_tokens:,} ({val_split*100:.1f}%)")
    
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    
    train_data = data[:train_tokens]
    val_data = data[train_tokens:]
    
    train_file = train_dir / "train.bin"
    val_file = val_dir / "val.bin"
    
    print(f"Writing train data to {train_file}...")
    train_data.tofile(str(train_file))
    
    print(f"Writing val data to {val_file}...")
    val_data.tofile(str(val_file))
    
    print("Split complete!")


def main():
    parser = argparse.ArgumentParser(description="Split tokenized data into train/val sets")
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Input directory containing tokenized data",
    )
    parser.add_argument(
        "--train-dir",
        type=str,
        required=True,
        help="Output directory for training data",
    )
    parser.add_argument(
        "--val-dir",
        type=str,
        required=True,
        help="Output directory for validation data",
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.05,
        help="Fraction of data to use for validation (default: 0.05)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    train_dir = Path(args.train_dir)
    val_dir = Path(args.val_dir)
    
    data_files = list(input_dir.glob("**/*.bin"))
    
    if not data_files:
        raise ValueError(f"No .bin files found in {input_dir}")
    
    for data_file in data_files:
        print(f"\nProcessing {data_file}...")
        split_data(data_file, train_dir, val_dir, args.val_split)


if __name__ == "__main__":
    main()
