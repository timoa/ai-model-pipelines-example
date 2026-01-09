# Black Formatting - Phase 7 (Optional)

## Overview

This document describes how to apply Black 24.3.0 formatting to the src/ directory. Black was upgraded from version 23.12.1 to 24.3.0 as part of fixing security vulnerability PYSEC-2024-48 (ReDoS).

## Why This Step Is Optional

Black 24.x may format code differently than Black 23.x due to style improvements and bug fixes in the formatter. Running Black on the codebase after the upgrade ensures consistent formatting but is not required for the security fixes to take effect.

## Prerequisites

Black must be installed before running the formatter:

```bash
pip install -r requirements.txt
```

This will install black==24.3.0 along with all other dependencies.

## Running Black Formatter

### Option 1: Using the provided script

```bash
./run_black_formatting.sh
```

This script will:
1. Check if Black is installed
2. Show the Black version
3. Check if formatting changes are needed
4. Apply formatting if needed
5. Provide instructions for committing the changes

### Option 2: Manual execution

Check for formatting changes:
```bash
black --check src/
```

Or using Python module:
```bash
python3 -m black --check src/
```

Apply formatting:
```bash
black src/
```

Or using Python module:
```bash
python3 -m black src/
```

## Expected Behavior

### Case 1: No Formatting Changes Needed
If the code is already formatted according to Black 24.x rules:
```
All done! ✨ 🍰 ✨
2 files would be left unchanged.
```

### Case 2: Formatting Changes Applied
If Black makes formatting changes:
```
reformatted src/train.py
reformatted src/evaluate.py
All done! ✨ 🍰 ✨
2 files reformatted.
```

## What Changed in Black 24.x

Black 24.x includes several formatting improvements over 23.x:
- More consistent line breaking in long expressions
- Improved formatting of type hints
- Better handling of trailing commas
- Fixes for edge cases in string formatting

These changes are intentional improvements and not regressions.

## Committing Formatting Changes

If Black reformats any files, review and commit the changes separately:

```bash
# Review the changes
git diff

# If changes look good, commit them
git add .
git commit -m "auto-claude: subtask-7-1 - Apply black 24.x formatting to src/"
```

## Verification

After applying formatting, verify the code still works:

```bash
# Import test (if environment is set up)
python3 -c "import sys; sys.path.insert(0, 'src'); from train import *; from evaluate import *; print('✓ All imports successful')"

# Run tests (if pytest is available and tests exist)
pytest -v
```

## Troubleshooting

### Black not found
**Error:** `command not found: black` or `No module named black`

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Permission denied
**Error:** `Permission denied: ./run_black_formatting.sh`

**Solution:** Make the script executable:
```bash
chmod +x ./run_black_formatting.sh
```

### Virtual environment not activated
If you're using a virtual environment, make sure it's activated:
```bash
source .venv/bin/activate  # or your virtual environment path
```

## References

- Black documentation: https://black.readthedocs.io/
- Black 24.3.0 changelog: https://github.com/psf/black/releases/tag/24.3.0
- PYSEC-2024-48 vulnerability: https://github.com/advisories/GHSA-fxcj-6gjv-v5jv
