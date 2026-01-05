import argparse
import time
import torch
from torch.utils.data import DataLoader
from pathlib import Path

from data.dataset import TextDataset


def benchmark_dataloader(data_dir: str, batch_size: int, num_workers: int, num_batches: int = 100):
    print(f"Benchmarking DataLoader:")
    print(f"  Data dir: {data_dir}")
    print(f"  Batch size: {batch_size}")
    print(f"  Num workers: {num_workers}")
    print(f"  Num batches: {num_batches}")
    
    dataset = TextDataset(data_dir=data_dir, block_size=1024)
    print(f"  Dataset size: {len(dataset)} samples")
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        pin_memory=True,
        prefetch_factor=2 if num_workers > 0 else None,
    )
    
    print(f"\nWarming up...")
    for i, (x, y) in enumerate(dataloader):
        if i >= 10:
            break
    
    print(f"\nBenchmarking...")
    start_time = time.time()
    total_tokens = 0
    
    for i, (x, y) in enumerate(dataloader):
        if i >= num_batches:
            break
        
        total_tokens += x.numel()
        
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            batches_per_sec = (i + 1) / elapsed
            tokens_per_sec = total_tokens / elapsed
            
            print(f"Batch {i+1}/{num_batches}: {batches_per_sec:.2f} batches/s, {tokens_per_sec/1e6:.2f}M tokens/s")
    
    total_time = time.time() - start_time
    batches_per_sec = num_batches / total_time
    tokens_per_sec = total_tokens / total_time
    
    print(f"\n{'='*60}")
    print(f"Benchmark Results:")
    print(f"{'='*60}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Batches/sec: {batches_per_sec:.2f}")
    print(f"Tokens/sec: {tokens_per_sec/1e6:.2f}M")
    print(f"Time per batch: {total_time/num_batches*1000:.2f}ms")
    print(f"Total tokens: {total_tokens/1e6:.2f}M")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark data loading performance")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing training data")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--num-workers", type=int, default=4, help="Number of data loading workers")
    parser.add_argument("--num-batches", type=int, default=100, help="Number of batches to benchmark")
    args = parser.parse_args()
    
    benchmark_dataloader(args.data_dir, args.batch_size, args.num_workers, args.num_batches)
