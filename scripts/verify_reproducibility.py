import argparse
import torch
import sys


def compare_checkpoints(checkpoint1_path: str, checkpoint2_path: str, tolerance: float = 1e-6):
    print(f"Loading checkpoint 1: {checkpoint1_path}")
    ckpt1 = torch.load(checkpoint1_path, map_location="cpu")
    
    print(f"Loading checkpoint 2: {checkpoint2_path}")
    ckpt2 = torch.load(checkpoint2_path, map_location="cpu")
    
    if "model" in ckpt1:
        state_dict1 = ckpt1["model"]
        state_dict2 = ckpt2["model"]
    else:
        state_dict1 = ckpt1
        state_dict2 = ckpt2
    
    if set(state_dict1.keys()) != set(state_dict2.keys()):
        print("ERROR: Checkpoints have different keys!")
        print(f"Keys in checkpoint 1 only: {set(state_dict1.keys()) - set(state_dict2.keys())}")
        print(f"Keys in checkpoint 2 only: {set(state_dict2.keys()) - set(state_dict1.keys())}")
        sys.exit(1)
    
    all_close = True
    max_diff = 0.0
    
    for key in state_dict1.keys():
        tensor1 = state_dict1[key]
        tensor2 = state_dict2[key]
        
        if tensor1.shape != tensor2.shape:
            print(f"ERROR: Shape mismatch for {key}")
            print(f"  Checkpoint 1: {tensor1.shape}")
            print(f"  Checkpoint 2: {tensor2.shape}")
            all_close = False
            continue
        
        diff = torch.abs(tensor1 - tensor2).max().item()
        max_diff = max(max_diff, diff)
        
        if not torch.allclose(tensor1, tensor2, atol=tolerance):
            print(f"WARNING: Difference in {key}: max diff = {diff}")
            all_close = False
    
    print(f"\nMaximum difference across all parameters: {max_diff}")
    
    if all_close:
        print("✓ Checkpoints are identical (within tolerance)")
        print("Training is reproducible!")
        sys.exit(0)
    else:
        print("✗ Checkpoints differ")
        print("Training is NOT reproducible!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Verify training reproducibility")
    parser.add_argument(
        "--checkpoint1",
        type=str,
        required=True,
        help="Path to first checkpoint",
    )
    parser.add_argument(
        "--checkpoint2",
        type=str,
        required=True,
        help="Path to second checkpoint",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help="Tolerance for floating point comparison",
    )
    args = parser.parse_args()
    
    compare_checkpoints(args.checkpoint1, args.checkpoint2, args.tolerance)


if __name__ == "__main__":
    main()
