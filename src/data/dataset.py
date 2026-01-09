import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path


class TextDataset(Dataset):
    def __init__(self, data_dir: str, block_size: int = 1024):
        self.block_size = block_size
        data_path = Path(data_dir)

        if not data_path.exists():
            raise ValueError(f"Data directory {data_dir} does not exist")

        data_files = sorted(data_path.glob("*.bin"))
        if not data_files:
            raise ValueError(f"No .bin files found in {data_dir}")

        self.data = np.memmap(data_files[0], dtype=np.uint16, mode="r")

    def __len__(self):
        return len(self.data) // self.block_size

    def __getitem__(self, idx):
        start_idx = idx * self.block_size
        end_idx = start_idx + self.block_size + 1

        chunk = torch.from_numpy((self.data[start_idx:end_idx]).astype(np.int64))
        x = chunk[:-1]
        y = chunk[1:]
        return x, y
