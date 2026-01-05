import argparse
import numpy as np
from pathlib import Path
from datasets import load_from_disk
from transformers import AutoTokenizer
from tqdm import tqdm
import multiprocessing as mp


def tokenize_batch(batch, tokenizer):
    return tokenizer(batch["text"], truncation=False, padding=False)


def process_dataset(dataset_path: Path, output_dir: Path, tokenizer_name: str, num_workers: int):
    print(f"Loading dataset from {dataset_path}...")
    dataset = load_from_disk(str(dataset_path))
    
    print(f"Loading tokenizer: {tokenizer_name}")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    
    print("Tokenizing dataset...")
    tokenized = dataset.map(
        lambda batch: tokenize_batch(batch, tokenizer),
        batched=True,
        num_proc=num_workers,
        remove_columns=dataset.column_names,
        desc="Tokenizing",
    )
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Converting to binary format...")
    all_tokens = []
    for example in tqdm(tokenized, desc="Collecting tokens"):
        all_tokens.extend(example["input_ids"])
    
    tokens_array = np.array(all_tokens, dtype=np.uint16)
    
    output_file = output_dir / "data.bin"
    tokens_array.tofile(str(output_file))
    
    print(f"Tokenized data saved to {output_file}")
    print(f"Total tokens: {len(tokens_array):,}")
    print(f"File size: {output_file.stat().st_size / (1024**3):.2f} GB")


def main():
    parser = argparse.ArgumentParser(description="Tokenize dataset for training")
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Input directory containing raw dataset",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for tokenized data",
    )
    parser.add_argument(
        "--tokenizer",
        type=str,
        default="gpt2",
        help="Tokenizer to use (HuggingFace model name)",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=mp.cpu_count(),
        help="Number of worker processes",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    dataset_dirs = [d for d in input_dir.iterdir() if d.is_dir()]
    
    if not dataset_dirs:
        raise ValueError(f"No dataset directories found in {input_dir}")
    
    for dataset_dir in dataset_dirs:
        print(f"\nProcessing {dataset_dir.name}...")
        dataset_output_dir = output_dir / dataset_dir.name
        process_dataset(dataset_dir, dataset_output_dir, args.tokenizer, args.num_workers)


if __name__ == "__main__":
    main()
