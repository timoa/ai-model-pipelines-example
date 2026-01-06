#!/usr/bin/env python3
"""
Test script to verify all upgraded packages import correctly
and meet minimum version requirements.
"""
import sys

def check_version(package_name, current_version, min_version):
    """Check if current version meets minimum requirement."""
    from packaging import version
    if version.parse(current_version) >= version.parse(min_version):
        print(f"✓ {package_name}: {current_version} (>= {min_version})")
        return True
    else:
        print(f"✗ {package_name}: {current_version} (< {min_version})")
        return False

# Import all upgraded packages
try:
    import torch
    import transformers
    import black
    import pyarrow
    import tqdm
    from packaging import version

    print("=" * 60)
    print("Package Import Verification")
    print("=" * 60)
    print("\nAll imports successful!\n")

    # Check versions meet minimum requirements
    print("Version Requirements Check:")
    print("-" * 60)

    all_pass = True
    all_pass &= check_version("torch", torch.__version__, "2.2.0")
    all_pass &= check_version("transformers", transformers.__version__, "4.53.0")
    all_pass &= check_version("black", black.__version__, "24.3.0")
    all_pass &= check_version("pyarrow", pyarrow.__version__, "15.0.0")
    all_pass &= check_version("tqdm", tqdm.__version__, "4.66.5")

    print("-" * 60)

    if all_pass:
        print("\n✓ All packages meet minimum version requirements!")
        sys.exit(0)
    else:
        print("\n✗ Some packages do not meet minimum version requirements")
        sys.exit(1)

except ImportError as e:
    print(f"✗ Import failed: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)
