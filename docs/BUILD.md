# Building OBI SDK

This guide explains how to build, test, and distribute the OBI (Ontological Bayesian Intelligence) SDK.

## Prerequisites

- Python 3.9 or later
- Cython 3.0 or later
- C compiler (MSVC 2019+ on Windows, GCC on Linux/WSL, Clang on macOS)

## Installation

### Step 1: Install Build Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install cython>=3.0.0
pip install numpy>=1.20
```

### Step 2: Install OBI in Development Mode

From the repo root (where `setup.py` lives):

```bash
# Clone and navigate
git clone https://github.com/obinexusmk2/obi.git
cd obi

# Install in editable mode (compiles Cython extensions)
pip install -e .
```

This will:
- Scan the `obi/` directory for `.pyx` files
- Compile them to C extensions
- Install OBI in your Python environment

## Building from Source

### Build Cython Extensions In-Place

```bash
python setup.py build_ext --inplace
```

This compiles `.pyx` files but doesn't install the package. Useful for development.

### Build a Wheel Distribution

```bash
pip install build
python -m build
```

This creates:
- `dist/obi-0.1.0a0-cp39-cp39-win_amd64.whl` (or your platform)
- `dist/obi-0.1.0a0.tar.gz` (source distribution)

### Install the Wheel

```bash
pip install dist/obi-0.1.0a0-cp39-cp39-win_amd64.whl
```

## Testing the Build

After installation, verify OBI imports:

```python
python -c "from obi import OBIContext; print('OBI loaded successfully')"
```

## Environment Variables

You can control the build process with environment variables:

```bash
# Enable Cython annotations (generates .html files showing Python/C interaction)
export CYTHON_ANNOTATE=1

# Control number of parallel Cython threads (Linux/WSL only; Windows uses nthreads=0)
export CYTHON_NTHREADS=8
```

Example:

```bash
CYTHON_NTHREADS=8 python setup.py build_ext --inplace
```

## Common Issues

### Issue: "Cython is required"

**Solution:**
```bash
pip install cython>=3.0
```

### Issue: "Microsoft Visual C++ 14.0 is required" (Windows)

**Solution:** Install Microsoft C++ Build Tools:
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Or install Visual Studio Community with C++ development tools

### Issue: Redefinition errors during Cython compilation

**Cause:** Duplicate function declarations in `.pyx` and `.pxd` files

**Solution:** 
- Remove duplicate declarations from `.pxd` files
- Use `cdef extern from "header.h": pass` to import headers
- Check that libpolycall has been removed (should be no libpolycall references)

## Development Workflow

For active development:

1. **Make code changes** to `.py` or `.pyx` files
2. **Rebuild Cython extensions:**
   ```bash
   python setup.py build_ext --inplace
   ```
3. **Run tests:**
   ```bash
   pytest tests/
   ```
4. **Commit and push**

## Publishing to PyPI (Maintainers Only)

### 1. Update Version

Edit `setup.py` and `pyproject.toml`:
```
version = "0.1.0"  # Remove -alpha suffix for releases
```

### 2. Build Distribution

```bash
pip install twine
python -m build
```

### 3. Upload to PyPI

```bash
twine upload dist/*
```

For TestPyPI first:
```bash
twine upload --repository testpypi dist/*
```

## Package Structure

```
obi/
├── setup.py                    # Build configuration
├── pyproject.toml             # PEP 517 metadata
├── MANIFEST.in                # Files to include in distribution
├── README.md                  # Package documentation
├── BUILD.md                   # This file
│
├── obi/                       # Main package
│   ├── __init__.py
│   ├── core/
│   │   ├── probe.pyx          # Cython: data → state probing
│   │   ├── bayesian.pyx       # Cython: Bayesian inference
│   │   └── governance.pyx     # Cython: 95.4% confidence gate
│   ├── memory/
│   │   ├── diram.pyx          # Cython: Directed Instruction RAM
│   │   └── quantum.pyx        # Cython: Quantum-classical bridge
│   ├── cognition/
│   │   ├── filterflash.py     # Python: metacognition cycles
│   │   └── dimensional.py     # Python: game theory reasoning
│   └── ...
│
├── proofs/                    # Formal specifications (AEGIS suite)
│   ├── AEGIS_PROOF_1_1.md
│   ├── AEGIS_PROOF_3_1.md
│   └── ...
│
├── examples/                  # Usage examples
│   ├── robotic_car.py
│   ├── medical_ai.py
│   └── ...
│
└── tests/                     # Test suite
    ├── test_core.py
    ├── test_cognition.py
    └── ...
```

## CI/CD Integration

For GitHub Actions, create `.github/workflows/build.yml`:

```yaml
name: Build & Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - run: pip install --upgrade pip setuptools wheel cython
      - run: pip install -e .[dev]
      - run: pytest tests/ -v
      - run: python -m build
```

## Questions?

See [README.md](README.md) for the full OBI documentation.

For technical issues, open an issue on GitHub: https://github.com/obinexusmk2/obi/issues
