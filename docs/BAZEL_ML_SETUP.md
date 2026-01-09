# Bazel for Machine Learning Projects

This document explains how Bazel is configured for this ML project to provide hermetic, reproducible builds while working with PyTorch and other ML dependencies.

## Overview

This project uses Bazel to demonstrate best practices for ML engineering:

- **Hermetic builds**: All dependencies are managed by Bazel, ensuring reproducibility
- **CPU-only PyTorch**: CI uses CPU-optimized PyTorch wheels to avoid large GPU dependencies
- **Dependency management**: Single source of truth for all Python packages
- **Build caching**: Faster builds through Bazel's caching mechanisms

## Configuration

### MODULE.bazel

The core Bazel configuration uses `rules_python` with pip integration:

```python
pip = use_extension("@rules_python//python/extensions:pip.bzl", "pip")
pip.parse(
    hub_name = "pip",
    python_version = "3.11",
    requirements_lock = "//:requirements_lock_cpu.txt",
    extra_pip_args = [
        "--extra-index-url=https://download.pytorch.org/whl/cpu",
    ],
)
```

**Key points:**

- Uses `requirements_lock_cpu.txt` which excludes NVIDIA CUDA packages
- `extra_pip_args` points to PyTorch's CPU-only wheel index
- This avoids downloading large GPU dependencies (triton, nvidia-*, etc.)

### Requirements Files

The project maintains multiple requirements files:

1. **`requirements.txt`**: Source requirements with pinned versions
2. **`requirements_lock.txt`**: Full dependency tree (includes GPU packages)
3. **`requirements_lock_cpu.txt`**: CPU-only dependencies (used by Bazel)

### BUILD Files

Python targets are defined using `py_binary` and `py_library`:

```python
load("@pip//:requirements.bzl", "requirement")

py_binary(
    name = "train",
    srcs = ["train.py"],
    deps = [
        "//src/data",
        "//src/models",
        requirement("torch"),
        requirement("pyyaml"),
    ],
    visibility = ["//visibility:public"],
)
```

## Running Commands

### Training

```bash
# Run training with Bazel
bazel run //src:train -- --config configs/smoke-test.yaml

# Run evaluation
bazel run //src:evaluate -- --config configs/eval.yaml --checkpoint outputs/model.pt
```

### Data Processing

```bash
# Generate test data
bazel run //scripts:generate_test_data -- --output-dir data/train --num-tokens 10000

# Download datasets
bazel run //scripts:download_data -- --dataset openwebtext

# Tokenize data
bazel run //scripts:tokenize_data -- --input data/raw --output data/processed
```

### Linting and Testing

```bash
# Run all tests
bazel test //...

# Run specific tests
bazel test //src/models:gpt_test

# Linting with Bazel-managed tools
bazel run @pip//black:rules_python_wheel_entry_point_black -- --check src/
bazel run @pip//ruff:rules_python_wheel_entry_point_ruff -- check src/
bazel run @pip//mypy:rules_python_wheel_entry_point_mypy -- src/ --ignore-missing-imports
```

### Building Containers

```bash
# Build training container
bazel build //docker/training:image

# Build inference container
bazel build //docker/inference:image
```

## CI/CD Integration

The GitHub Actions workflow uses Bazel for all Python execution:

```yaml
- name: Run smoke test training
  run: |
    bazel run //src:train -- --config configs/smoke-test.yaml
```

**Benefits:**

- No manual pip installations in CI
- Guaranteed reproducibility across environments
- Faster builds with Bazel's remote caching
- Clear dependency graph

## Why CPU-Only in Bazel?

The project uses CPU-only PyTorch in Bazel for several reasons:

1. **CI Environment**: GitHub Actions runners don't have GPUs
2. **Build Speed**: Avoiding large NVIDIA CUDA packages (>2GB) speeds up builds
3. **Hermetic Builds**: CPU wheels are smaller and faster to fetch
4. **Local Development**: Developers with GPUs can still use GPU PyTorch via pip

## Updating Dependencies

### Adding a New Package

1. Add to `requirements.txt`:

   ```text
   new-package==1.0.0
   ```

2. Regenerate the CPU lock file:

   ```bash
   pip-compile requirements.txt --output-file=requirements_lock_cpu.txt \
     --extra-index-url https://download.pytorch.org/whl/cpu
   ```

3. Update BUILD files to include the new requirement:

   ```python
   requirement("new-package")
   ```

### Upgrading PyTorch

1. Update version in `requirements.txt`
2. Regenerate lock file with CPU index
3. Test with Bazel:

   ```bash
   bazel clean
   bazel test //...
   ```

## Troubleshooting

### "Package not found" errors

If Bazel can't find a package:

```bash
# Clear Bazel cache
bazel clean --expunge

# Verify the package is in requirements_lock_cpu.txt
grep "package-name" requirements_lock_cpu.txt
```

### Slow dependency fetching

Bazel caches pip packages. First build will be slow, subsequent builds are fast:

```bash
# Check cache status
bazel info repository_cache

# Use remote cache (if configured)
bazel build //... --config=remote
```

### Version conflicts

If you see version conflicts:

1. Check `requirements_lock_cpu.txt` for the resolved version
2. Ensure `requirements.txt` has compatible constraints
3. Regenerate lock file if needed

## Best Practices

1. **Always use Bazel targets**: Prefer `bazel run //src:train` over `python src/train.py`
2. **Keep lock files in sync**: Regenerate CPU lock file when updating requirements
3. **Test locally first**: Run `bazel test //...` before pushing
4. **Use visibility**: Restrict target visibility to prevent unintended dependencies
5. **Document targets**: Add comments to BUILD files explaining complex targets

## Comparison: Bazel vs. Traditional pip

| Aspect | Bazel | Traditional pip |
|--------|-------|-----------------|
| Reproducibility | ✅ Hermetic | ⚠️ Depends on environment |
| Caching | ✅ Multi-level | ❌ Limited |
| Dependency graph | ✅ Explicit | ⚠️ Implicit |
| Multi-language | ✅ Yes | ❌ Python only |
| Learning curve | ⚠️ Steep | ✅ Easy |
| CI speed | ✅ Fast (with cache) | ⚠️ Variable |

## Resources

- [Bazel Python Rules](https://github.com/bazelbuild/rules_python)
- [PyTorch CPU Wheels](https://download.pytorch.org/whl/cpu)
- [Bazel Best Practices](https://bazel.build/basics/best-practices)
- [Project BUILD files](./src/BUILD.bazel)
