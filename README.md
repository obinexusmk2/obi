# OBIAI SDK

**Ontological Bayesian Intelligence SDK** - Non-monolithic AI infrastructure for unbiased reasoning systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Cython 3.0+](https://img.shields.io/badge/Cython-3.0+-orange.svg)](https://cython.org/)

## Overview

OBIAI SDK implements the Ontological Bayesian Intelligence hypothesis—a framework for AI systems that reason rather than merely pattern-match. It addresses the "black box" bias problem through:

- **Top-down and bottom-up reasoning** for demographic bias mitigation
- **Dimensional game theory** for strategic problem-solving
- **Filter-Flash architecture** for conscious, adaptive memory
- **Non-monolithic design** for dynamic plugin loading

## Architecture

```
obi-sdk/
├── bindings/           # Cython/C interface layer
│   ├── cython/        # .pyx and .pxd files
│   └── c/             # C headers for libpolycall-v1
├── drivers/           # Hardware/interface drivers
│   ├── core/          # Essential drivers (poly driver)
│   └── extensions/    # Optional plugins
├── sdk/               # Python SDK
│   ├── core/          # Context, inference engines
│   └── utils/         # Utilities
└── tests/             # Test suite
```

## Quick Start

### Prerequisites

- Python 3.9+
- Conda (recommended) or pip
- C compiler (GCC on Linux/WSL, MSVC on Windows)
- [libpolycall-v1](https://github.com/obinexusmk2/libpolycall-v1)

### Installation

```bash
# Clone repository
git clone https://github.com/obinexusmk2/obi-sdk.git
cd obi-sdk

# Run setup script
./scripts/install.sh

# Or manually:
conda env create -f environment.yml
conda activate obi-sdk-dev
./scripts/build.sh
```

### Usage

```python
from obi_sdk.sdk.core.context import OBIContext
from obi_sdk.sdk.core.inference import BayesianEngine, ReasoningMode
import numpy as np

# Create context
with OBIContext(config={"model": "standard"}) as ctx:
    # Initialize inference engine
    engine = BayesianEngine(
        ctx,
        mode=ReasoningMode.BIDIRECTIONAL,
        confidence_threshold=0.954  # 95.4% per OBI spec
    )
    
    # Run inference
    evidence = np.random.rand(1, 3, 64, 64)  # 4D tensor
    result, metadata = engine.infer(evidence)
    
    print(f"Result shape: {result.shape}")
    print(f"Inference chain: {metadata['chain']}")
```

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux (x86_64) | ✅ Supported | Primary development target |
| WSL2 | ✅ Supported | Full compatibility with Linux |
| Windows 10/11 | ✅ Supported | MSVC 2019+ required |
| macOS | ⚠️ Experimental | Community support |

## Development

### Building from Source

```bash
# Debug build with Cython line tracing
./scripts/build.sh Debug 1

# Release build (optimized)
./scripts/build.sh Release 0

# Windows (native)
scripts\build_windows.bat
```

### Running Tests

```bash
pytest tests/ -v --cov=obi_sdk
```

### Conda Package

```bash
# Build conda package
conda build conda-recipe/

# Install locally
conda install --use-local obi-sdk
```

## Theoretical Foundation

This SDK implements concepts from the OBI AI hypothesis:

1. **Unbiased Modeling**: Uses demographic-aware confounder analysis to prevent training bias
2. **Dimensional Reduction**: `DR = D - 1` recursive tensor reduction for 4D reasoning
3. **QA Matrix**: Validation against true/false positive/negative criteria
4. **Filter-Flash**: Epistemic reasoning with conscious awareness simulation

See the [full specification](https://github.com/obinexus/legislation) for formal proofs.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Attribution

Created by **Nnamdi Michael Okpala** (OBINexus) as part of the OBINexus constitutional framework.

- GitHub: [@obinexusmk2](https://github.com/obinexusmk2)
- Change.org: [obinexus_reform](https://change.org/obinexus_reform)
- YouTube: [Software Development Playlist](https://www.youtube.com/playlist?list=PL0ifFOZbja_Iixdj7mj9xE474HnrItFts)

---

**Note**: This is alpha software (v0.1.0-alpha). APIs are subject to change.
