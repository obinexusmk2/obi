#!/usr/bin/env bash
# Installation script for OBIAI SDK

set -e

echo "Installing OBIAI SDK..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
if [[ "$(printf '%s\n' "3.9" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.9" ]]; then
    echo "ERROR: Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

# Create conda environment if it doesn't exist
cat > ${PROJECT_NAME}/sdk/__init__.py << 'EOF'
"""
OBIAI SDK - Ontological Bayesian Intelligence
Non-monolithic AI infrastructure for unbiased reasoning
"""

__version__ = "0.1.0-alpha"
__author__ = "Nnamdi Michael Okpala (OBINexus)"

# Conditional environment setup
if ! conda env list | grep -q "obi-sdk-dev"; then
    echo "Creating conda environment..."
    conda env create -f environment.yml
fi

# Activate environment
conda activate obi-sdk-dev

# Clone dependencies if not present
if [ ! -d "../libpolycall-v1" ]; then
    echo "Cloning libpolycall-v1..."
    git clone https://github.com/obinexusmk2/libpolycall-v1.git ../libpolycall-v1
fi

# Build and install
./scripts/build.sh Release

echo "Installation complete!"
echo "Activate with: conda activate obi-sdk-dev"
