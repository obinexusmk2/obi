#!/usr/bin/env bash
# OBIAI SDK Build Script
# Supports: Linux, WSL, Windows (via WSL cross-compile)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_TYPE="${1:-Release}"
CYTHON_TRACE="${2:-0}"

echo "Building OBIAI SDK..."
echo "Build type: $BUILD_TYPE"
echo "Cython trace: $CYTHON_TRACE"

cd "$PROJECT_ROOT"

# Detect environment
if [[ -n "${CONDA_DEFAULT_ENV:-}" ]]; then
    echo "Conda environment: $CONDA_DEFAULT_ENV"
else
    echo "WARNING: Not in conda environment. Activate with: conda activate obi-sdk-dev"
    exit 1
fi

# Clean previous builds
rm -rf build/ dist/ *.egg-info
find . -name "*.so" -delete -o -name "*.pyd" -delete

# Set build environment
export CYTHON_TRACE=$CYTHON_TRACE
export CYTHON_NTHREADS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Build libpolycall-v1 if present
if [ -d "../libpolycall-v1" ]; then
    echo "Building libpolycall-v1..."
    mkdir -p ../libpolycall-v1/build
    cd ../libpolycall-v1/build
    cmake .. -DCMAKE_BUILD_TYPE=$BUILD_TYPE
    cmake --build . --parallel
    cd "$PROJECT_ROOT"
    export LIBPOLYCALL_ROOT="../libpolycall-v1"
fi

# Build Python extension
cd "$PROJECT_ROOT"
pip install -e . -v --no-build-isolation

# Run tests
echo "Running tests..."
python -m pytest tests/ -v --tb=short

echo "Build complete!"
