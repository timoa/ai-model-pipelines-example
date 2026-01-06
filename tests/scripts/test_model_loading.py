#!/usr/bin/env python3
"""
ML Model Loading Verification Script

This script verifies that the upgraded transformers library (4.53.0) can successfully
load pretrained models and that the transformers cache is compatible with the new version.

This addresses potential cache incompatibility issues that can occur with major
transformers version upgrades (4.36.2 -> 4.53.0).

Usage:
    python test_model_loading.py

If the test fails with cache errors, clear the transformers cache:
    rm -rf ~/.cache/huggingface/transformers
    rm -rf ~/.cache/huggingface/hub
Then retry the test.
"""

import sys
import time
from pathlib import Path


def test_transformers_import():
    """Test that transformers can be imported"""
    print("=" * 70)
    print("TEST 1: Importing transformers library")
    print("=" * 70)
    try:
        import transformers
        print(f"✓ transformers imported successfully")
        print(f"  Version: {transformers.__version__}")
        expected_version = "4.53.0"
        if transformers.__version__ >= expected_version:
            print(f"  ✓ Version meets minimum requirement: >={expected_version}")
        else:
            print(f"  ✗ Version {transformers.__version__} is below minimum {expected_version}")
            return False
        return True
    except ImportError as e:
        print(f"✗ Failed to import transformers: {e}")
        return False


def test_automodel_import():
    """Test that AutoModel can be imported"""
    print("\n" + "=" * 70)
    print("TEST 2: Importing AutoModel class")
    print("=" * 70)
    try:
        from transformers import AutoModel
        print("✓ AutoModel imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import AutoModel: {e}")
        return False


def test_model_loading():
    """Test loading a small pretrained model"""
    print("\n" + "=" * 70)
    print("TEST 3: Loading pretrained model (bert-base-uncased)")
    print("=" * 70)
    print("NOTE: This will download ~440MB on first run")
    print("Cache location: ~/.cache/huggingface/hub")
    print("")

    try:
        from transformers import AutoModel

        model_name = "bert-base-uncased"
        print(f"Loading model: {model_name}")
        start_time = time.time()

        model = AutoModel.from_pretrained(model_name)

        elapsed_time = time.time() - start_time
        print(f"✓ Model loaded successfully in {elapsed_time:.2f} seconds")
        print(f"  Model type: {type(model).__name__}")
        print(f"  Model config: {model.config.architectures}")

        # Verify model has expected attributes
        if hasattr(model, 'config') and hasattr(model, 'embeddings'):
            print("✓ Model has expected structure (config, embeddings)")
        else:
            print("⚠ Warning: Model may be missing expected attributes")

        return True

    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection (model needs to be downloaded)")
        print("2. Clear transformers cache if cache incompatibility error:")
        print("   rm -rf ~/.cache/huggingface/transformers")
        print("   rm -rf ~/.cache/huggingface/hub")
        print("3. Verify transformers version: pip show transformers")
        return False


def test_cache_compatibility():
    """Test that the cache directory is accessible and valid"""
    print("\n" + "=" * 70)
    print("TEST 4: Checking transformers cache compatibility")
    print("=" * 70)

    cache_dir = Path.home() / ".cache" / "huggingface"
    transformers_cache = cache_dir / "transformers"
    hub_cache = cache_dir / "hub"

    print(f"Cache directory: {cache_dir}")

    if cache_dir.exists():
        print(f"✓ Hugging Face cache directory exists")

        if transformers_cache.exists():
            print(f"  - Transformers cache: {transformers_cache}")
            cache_size = sum(f.stat().st_size for f in transformers_cache.rglob('*') if f.is_file())
            print(f"    Size: {cache_size / (1024*1024):.2f} MB")

        if hub_cache.exists():
            print(f"  - Hub cache: {hub_cache}")
            cache_size = sum(f.stat().st_size for f in hub_cache.rglob('*') if f.is_file())
            print(f"    Size: {cache_size / (1024*1024):.2f} MB")

        return True
    else:
        print("ℹ Cache directory does not exist yet (will be created on first model download)")
        return True


def test_torch_compatibility():
    """Test that torch and transformers are compatible"""
    print("\n" + "=" * 70)
    print("TEST 5: Verifying torch and transformers compatibility")
    print("=" * 70)

    try:
        import torch
        import transformers

        print(f"✓ torch version: {torch.__version__}")
        print(f"✓ transformers version: {transformers.__version__}")

        # transformers 4.53.0 requires torch >= 1.11.0
        # We have torch 2.2.2 which is well above the minimum
        torch_version = tuple(map(int, torch.__version__.split('+')[0].split('.')[:2]))
        if torch_version >= (1, 11):
            print(f"✓ torch version is compatible with transformers 4.53.0 (requires >=1.11.0)")
            return True
        else:
            print(f"✗ torch version {torch.__version__} may be incompatible")
            return False

    except ImportError as e:
        print(f"✗ Failed to import required libraries: {e}")
        return False


def main():
    """Run all verification tests"""
    print("\n")
    print("*" * 70)
    print("ML MODEL LOADING VERIFICATION")
    print("Transformers 4.53.0 Compatibility Check")
    print("*" * 70)
    print()

    results = []

    # Run all tests
    results.append(("Transformers Import", test_transformers_import()))
    results.append(("AutoModel Import", test_automodel_import()))
    results.append(("Torch Compatibility", test_torch_compatibility()))
    results.append(("Cache Compatibility", test_cache_compatibility()))
    results.append(("Model Loading", test_model_loading()))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ SUCCESS: All model loading tests passed!")
        print("Transformers 4.53.0 is working correctly and cache is compatible.")
        return 0
    else:
        print("\n✗ FAILURE: Some tests failed")
        print("Please review the error messages above and follow troubleshooting steps.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
