import argparse
from pathlib import Path
from datasets import load_dataset


def download_openwebtext(output_dir: Path):
    print("Downloading OpenWebText dataset...")
    dataset = load_dataset("openwebtext", split="train")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset.save_to_disk(str(output_dir / "openwebtext"))
    print(f"Dataset saved to {output_dir / 'openwebtext'}")


def download_wikipedia(output_dir: Path):
    print("Downloading Wikipedia dataset...")
    dataset = load_dataset("wikipedia", "20220301.en", split="train")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset.save_to_disk(str(output_dir / "wikipedia"))
    print(f"Dataset saved to {output_dir / 'wikipedia'}")


def main():
    parser = argparse.ArgumentParser(description="Download datasets for training")
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        choices=["openwebtext", "wikipedia", "custom"],
        help="Dataset to download",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw",
        help="Output directory for downloaded data",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if args.dataset == "openwebtext":
        download_openwebtext(output_dir)
    elif args.dataset == "wikipedia":
        download_wikipedia(output_dir)
    elif args.dataset == "custom":
        print("Custom dataset download not implemented")
        print("Please place your custom dataset in the output directory")


if __name__ == "__main__":
    main()
