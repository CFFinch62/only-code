#!/bin/bash
# Build script for macOS
# Creates executable in dist/OnlyCode/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "Building Only Code for macOS"
echo "=========================================="

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install PyInstaller if not present
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build
echo "Building..."
python build.py "$@"

# Make executable
if [ -f "dist/OnlyCode/OnlyCode" ]; then
    chmod +x dist/OnlyCode/OnlyCode
    echo ""
    echo "Build successful!"
    echo "Run with: ./dist/OnlyCode/OnlyCode"
fi

