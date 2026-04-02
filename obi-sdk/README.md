# OBI SDK

**Ontological Bayesian Intelligence — NSIGII Protocol Development Kit**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Cython 3.0+](https://img.shields.io/badge/Cython-3.0+-orange.svg)](https://cython.org/)
[![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange.svg)](https://github.com/obinexusmk2/obi)
[![MMUKO-OS](https://img.shields.io/badge/runtime-MMUKO--OS-1A2F5A.svg)](https://github.com/obinexusmk2/mmuko-os)

---

## Overview

OBI SDK is the official software development kit for building and implementing the **NSIGII protocol** within the OBINexus / MMUKO-OS ecosystem.

It provides a structured framework for designing systems that can:

- **Transmit**
- **Receive**
- **Verify**

…across noisy, adversarial, or unstable environments.

Unlike traditional SDKs, OBI is not just about execution — it is about **calibration, verification, and consensus-driven computation**.

> A complete system must know it can be jammed — and therefore must be anti-jammable.

---

## What O.B.I Stands For

| Letter | Term | Meaning in this SDK |
|--------|------|---------------------|
| **O** | Ontological | Every computational entity carries defined existence before value resolution. A bit is not just 0 or 1 — it has a spin, a compass direction, and a state. |
| **B** | Bayesian | All state transitions are probabilistic. The 95.4% consensus threshold (μ + 2σ) governs Flash vs. Filter mode selection. |
| **I** | Intelligence | The system recalibrates, adapts to jamming, votes to exclude hostile channels, and accumulates epistemic knowledge over time. |

---

## Core Philosophy

### 1. Trident Computation

All operations are resolved through three channels:

```
Transmit (CH0) → Receive (CH1) → Verify (CH2)
```

No signal is trusted unless it passes through all three. Each channel holds 120° of the Rational Wheel — a full 360° rotation confirms verification.

| Channel | Role | Permission | Loopback | Codec Ratio |
|---------|------|------------|----------|-------------|
| CH0 | Transmitter | WRITE (0x02) | 127.0.0.1 | 1/3 |
| CH1 | Receiver | READ (0x04) | 127.0.0.2 | 2/3 |
| CH2 | Verifier | EXECUTE (0x01) | 127.0.0.3 | 3/3 |

Full RWX (`0x07`) is issued only at the Verifier after wheel completion.

### 2. Your Noise Is My Signal

Noise is not failure — it is uninterpreted data. The system:

1. detects noise
2. classifies ambiguity
3. recalibrates
4. converts noise into usable signal

This is the anti-jamming inversion principle: what a hostile system treats as interference, a constitutional system treats as information.

### 3. Calibration Before Assertion

The system does not assume truth. It:

1. **calibrates** (probe establishes MuConv reference frame)
2. **establishes ground state** (vacuum medium, G_MUON = 0.098)
3. **verifies** state independently
4. **then acts**

---

## Signal State Model

The SDK operates across a 4×4 calibration matrix of real-world signal conditions:

```
┌──────────────────┬──────────────────┐
│  Maybe Noise     │  Maybe No Noise  │
│  Maybe Signal    │  Maybe No Signal │
└──────────────────┴──────────────────┘
```

These intermediate states ("maybe", "maybe not") are first-class — the system does not collapse them prematurely. The four confirmed states are `UP`, `DOWN`, `CHARM`, and `STRANGE`, derived from each bit's relationship with its neighbour.

---

## Architecture

The system is split across two primary repositories:

```
mmuko-os/   → Native runtime + boot model  (NASM/C++/Python)
obi/        → SDK + protocol development   (Python/Cython/C/Lua/Go)
```

### Layered Stack

```
┌─────────────────────────────────────────┐
│  Protocol Layer    NSIGII Trident C&C   │  ← Lua / Python
├─────────────────────────────────────────┤
│  SDK Layer         OBI SDK (this repo)  │  ← Python / Cython
├─────────────────────────────────────────┤
│  Bindings Layer    C / FFI / libpolycall │  ← C / Cython .pyx
├─────────────────────────────────────────┤
│  Native Layer      MMUKO-OS runtime     │  ← NASM / C++
└─────────────────────────────────────────┘
```

### Repository Layout

```
obi-sdk/
├── bindings/           # Cython/C interface layer
│   ├── cython/         # .pyx and .pxd files
│   └── c/              # C headers for libpolycall-v1
├── drivers/
│   └── core/           # poly driver (libpolycall bridge)
├── sdk/
│   └── core/           # OBIContext, BayesianEngine, ReasoningMode
├── tests/              # Test suite
├── pseudocode/         # 35+ .psc canonical specification files
├── transcripts/        # Voice session design transcripts (source of truth)
├── uche-prproof/       # 40+ formal mathematical specification PDFs
└── environment.yml     # Conda environment
```

> **Design law:** Transcripts are the source-of-truth design layer. PSC files are their formal encoding. Code is the implementation of PSC. The `transcripts/` folder is a first-class artefact.

---

## Core Modules

| # | Module | Description |
|---|--------|-------------|
| 01 | Core Consensus | 95.4% threshold Filter-Flash state machine. OBI_STATE vs DISCORD_STATE via cosine similarity between Eze (inductive) and Uche (deductive) persona vectors. |
| 02 | DIRAM Memory | Directed Instruction Random Access Memory. SHA-256 receipt per allocation, Sinphase governance (max 3 heap events/epoch), zero-trust PID binding. |
| 03 | Dimensional Game Theory | Multi-domain strategic reasoning via Nash equilibrium with dimensional extensions. |
| 04 | OBINexus Gating | Pre-Gate (95%) / Dev-Gate (90%) / Post-Gate (100%) milestone architecture. |
| 05 | Bias Mitigation | Bayesian top-down/bottom-up demographic bias detection and correction. |
| 06 | Tier Management | Stable / Experimental / Legacy component classification and plugin loading order. |
| 07 | Filter-Flash Cognition | Cost-knowledge function `C(K,S) = H(S) * exp(-K/t)`. KL divergence traversal. |
| 08 | Consciousness Stack | DIRAM-backed integrity: `00`=null, `01`=partial, `10`=collapse → sovereign reconstruction, `11`=intact. |
| 09 | Epistemic Actor | Hierarchical actor orchestration with DIRAM-backed epistemic validation. |

---

## NSIGII Protocol: Here and Now / Where and When / There and Then

The three temporal reference frames of the NSIGII protocol:

| Frame | Component | Role |
|-------|-----------|------|
| **Here and Now** | Membrane Calibration | Present state. Probe establishes MuConv ground reference. Signal classification via 4×4 matrix. |
| **Where and When** | Tripartite Discriminant Analysis | Spatial/temporal context. Loopback coordinate frame. Lattice-grid positioning. |
| **There and Then** | Byzantine Pushdown Automaton | Historical consensus. Three Trident nodes vote to exclude hostile channels. |

### Example Flow

```
Input arrives
  → Classify state (signal / noise / maybe / maybe-not)
    → Probe calibrates reference frame (MuConv)
      → Trident channels process (Transmit → Receive → Verify)
        → Consensus vote (2/3 threshold = 0.67)
          → ACCEPT / REJECT / RECALIBRATE
```

### Human Rights Tags

Every NSIGII packet carries a Human Rights Tag in its HMAC-SHA256 consensus signature:

```
NSIGII_HR_TRANSMIT  →  NSIGII_HR_RECEIVE  →  NSIGII_HR_VERIFY  →  NSIGII_HR_VERIFIED
```

---

## MMUKO-OS Boot Sequence

The SDK is grounded in the MMUKO-OS 6-phase constitutional boot model. Boot proceeds via a **diamond traversal** `[12, 6, 8, 4, 10, 2, 1]` — never linear — to prevent lock-in.

| Phase | Name | Requirement |
|-------|------|-------------|
| 1 | NEED_STATE_INIT | Tier-1 state is not null (breathing pointer check) |
| 2 | SAFETY_SCAN | NSIGII minimum safety envelope active |
| 3 | IDENTITY_CALIBRATION | Operator identity and temporal frame bound to handoff |
| 4 | GOVERNANCE_CHECK | Execution policy, provenance chain, FAT12 target verified |
| 5 | INTERNAL_PROBE | NSIGII firmware compatibility confirmed |
| 6 | INTEGRITY_VERIFICATION | CRC32 handoff checksum; magic `MMKO`; PASS = `0xAA` |

> **Invariant:** `BREATHING > LIVING > WORKING`. No system may ever demand WORKING before confirming BREATHING and LIVING. This is encoded as a hard abort condition.

---

## Quick Start

### Prerequisites

- Python 3.9+
- Conda (recommended) or pip
- C compiler: GCC on Linux/WSL, MSVC 2019+ on Windows
- [libpolycall-v1](https://github.com/obinexusmk2/libpolycall-v1)
- **Cython 3.0+** — required; install via `conda install -c conda-forge cython`

### Installation

```bash
# Clone
git clone https://github.com/obinexusmk2/obi.git
cd obi/obi-sdk

# Create environment
conda env create -f environment.yml
conda activate obi-sdk-dev

# Install Cython (required — build will fail without it)
conda install -c conda-forge "cython>=3.0.0"

# Build Cython extensions
python setup.py build_ext --inplace

# Or full package build
python -m build
```

### Usage

```python
from obi_sdk.sdk.core.context import OBIContext
from obi_sdk.sdk.core.inference import BayesianEngine, ReasoningMode
import numpy as np

with OBIContext(config={"model": "standard"}) as ctx:
    engine = BayesianEngine(
        ctx,
        mode=ReasoningMode.BIDIRECTIONAL,
        confidence_threshold=0.954   # 95.4% — mu + 2 sigma
    )

    evidence = np.random.rand(1, 3, 64, 64)   # 4D tensor input
    result, metadata = engine.infer(evidence)

    print(f"Result shape: {result.shape}")
    print(f"Inference chain: {metadata['chain']}")
```

---

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux (x86_64) | ✅ Supported | Primary development target |
| WSL2 | ✅ Supported | Full Linux compatibility |
| Windows 10/11 | ✅ Supported | MSVC 2019+ required |
| macOS | ⚠️ Experimental | Community support only |

---

## Development Stack

| Language | Role |
|----------|------|
| C / C++ | Native bindings, DIRAM memory manager, firmware |
| Python / Cython | SDK orchestration, inference engine, bindings |
| Lua | State machine interpreter (FSM evaluation) |
| Go | Networking layer, Trident channel pipelines |
| JavaScript | Web interface, AeroSSR integration |

---

## Development Roadmap

| Milestone | Description | Gate |
|-----------|-------------|------|
| M0 | Build unblocked — Cython installed, `import obi_sdk` succeeds | Build |
| M1 | DIRAM core live — SHA-256 receipts, Sinphase governance passing tests | Dev-Gate 90% |
| M2 | Filter-Flash engine — BayesianEngine with 95.4% threshold on Triangi dataset | Dev-Gate 90% |
| M3 | NSIGII bindings — Trident CH0/CH1/CH2 loopback channels, HMAC-SHA256 packets | Dev-Gate 90% |
| M4 | MMUKO-OS boot integration — boot phases 1–6 with Python handoff | Post-Gate 100% |
| M5 | Formal proof alignment — test assertions match AEGIS proof corpus | Post-Gate 100% |
| M6 | Public SDK release — PyPI packaging, conda-forge recipe, full docs | Release |

---

## Constitutional Framework

Every layer of OBI SDK is governed by the OBINexus Constitutional Framework:

- **#NoGhosting** — complete audit trails for all interactions via DIRAM SHA-256 receipts
- **Milestone-Based Investment** — verifiable progress gates before components advance
- **OpenSense Recruitment** — transparent contributor onboarding aligned to sensory/motor profile spec
- **Zero-Trust Architecture** — every allocation, channel, and binding verified independently

---

## Formal Specification

All design work is specified first in `.psc` (OBINexus Pseudocode) files before implementation begins. The `pseudocode/` directory contains 35+ canonical specification files. The `uche-prproof/` directory contains 40+ formal mathematical proofs (the AEGIS proof corpus) backing every module.

Key proofs:

- `AEGIS_PROOF_3_1/3_2` — Filter-Flash monotonicity and Hybrid Mode Convergence
- `Formal Specification — 95.4% Consensus Threshold in OBIAI` — mathematical derivation of the core threshold
- `Directed Instruction Random Access Memory` — DIRAM full formal specification
- `Dimensional_Game_Theory` — fault-tolerant cryptographic integration with AuraSeal
- `The Heart AI — Patent Filing Specification` — IP protection for core OBI inference architecture

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Nnamdi Michael Okpala** — OBINexus Computing

- SDK: [github.com/obinexusmk2/obi](https://github.com/obinexusmk2/obi)
- Runtime: [github.com/obinexusmk2/mmuko-os](https://github.com/obinexusmk2/mmuko-os)

---

> *Don't just run systems. Build systems that know when they are wrong.*
>
> — OBINexus R&D
