#!/bin/bash
# Script to run black formatter on src/ directory
# This script should be run after installing dependencies from requirements.txt

set -e

echo "=== Running Black Formatter on src/ directory ==="
echo ""

# Check if black is installed
if ! command -v black &> /dev/null && ! python3 -m black --version &> /dev/null; then
    echo "ERROR: black is not installed"
    echo "Please install dependencies first:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Show black version
echo "Black version:"
if command -v black &> /dev/null; then
    black --version
else
    python3 -m black --version
fi
echo ""

# Check if formatting changes are needed
echo "Checking if formatting changes are needed..."
if command -v black &> /dev/null; then
    if black --check src/ 2>&1; then
        echo "✓ No formatting changes needed - src/ already formatted correctly"
        exit 0
    else
        echo "Formatting changes detected"
    fi
else
    if python3 -m black --check src/ 2>&1; then
        echo "✓ No formatting changes needed - src/ already formatted correctly"
        exit 0
    else
        echo "Formatting changes detected"
    fi
fi

echo ""
echo "=== Applying Black Formatting ==="
if command -v black &> /dev/null; then
    black src/
else
    python3 -m black src/
fi

echo ""
echo "✓ Black formatting applied successfully"
echo ""
echo "Note: Black 24.x may format differently than 23.x."
echo "This is expected and not a regression."
echo ""
echo "Next steps:"
echo "1. Review the formatting changes: git diff"
echo "2. If changes look good, commit them:"
echo "   git add ."
echo "   git commit -m 'Apply black 24.x formatting to src/'"
