# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core.governance
# Problem: [PROB-05] Unsafe Action Thresholds — No formal clamp for deployment
# Proof Source: The_95.4_Metric.md, AEGIS-PROOF-1.1
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
#
# Governance: CH_0 (Observe) | CH_1 (Defer) | CH_2 (Collapse)
# Confidence Threshold: 95.4%
# =============================================================================

from __future__ import annotations

import hashlib
from typing import Union

import numpy as np

from .types import S, Channel, ProbeResult

# ---------------------------------------------------------------------------
# Formal governance constant
# μ + 2σ ≈ 0.954 — derived in proofs/The_95.4_Metric.md
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD: float = 0.954


# ---------------------------------------------------------------------------
# Epistemic confidence measurement
# ---------------------------------------------------------------------------

def compute_epistemic_confidence(state_vector: S) -> float:
    """
    [PROB-05] Compute epistemic confidence from a governed state vector.

    Confidence = max squared component of the L2-normalised state vector.

        confidence(s) = max_i(s_i²)   where  ||s|| = 1

    This measures energy concentration in the dominant dimension:
    - A perfectly peaked state [1, 0, …, 0] → confidence = 1.0
    - A uniform state [1/√n, …, 1/√n] → confidence = 1/n → 0 for large n

    This maps to the μ + 2σ ≈ 0.954 statistical threshold from
    AEGIS-PROOF-1.1: a system with 95.4% of its energy in one state
    dimension is considered epistemically certain.

    Parameters
    ----------
    state_vector : S
        Internal state (any shape; flattened and normalised internally).

    Returns
    -------
    float
        Confidence in [0, 1]. Returns 0.0 for degenerate (zero-norm) input.

    Proof Source
    ------------
    - AEGIS-PROOF-1.1: Cost-Knowledge Function C(K, S) = H(S) * exp(-K/t)
    - The_95.4_Metric.md: statistical derivation of μ + 2σ threshold
    """
    flat = state_vector.flatten().astype(np.float64)
    if flat.size == 0:
        return 0.0

    norm = np.linalg.norm(flat)
    if norm < 1e-12:
        return 0.0

    # Energy concentration in the dominant dimension (scale-invariant)
    normalised = flat / norm
    if not np.all(np.isfinite(normalised)):
        return 0.0
    return float(np.max(normalised ** 2))


# ---------------------------------------------------------------------------
# Trident gate — routes to CH_1 or CH_2
# ---------------------------------------------------------------------------

def validate_gate(confidence: float) -> Channel:
    """
    [PROB-05] Route through Trident Channel based on epistemic confidence.

    Parameters
    ----------
    confidence : float
        Value in [0, 1] from compute_epistemic_confidence.

    Returns
    -------
    Channel
        CH_2 if confidence >= 0.954 (collapse to output).
        CH_1 if confidence < 0.954 (defer, 60s retry).

    Governance
    ----------
    CH_1: deferred — human review required before proceeding.
    CH_2: collapsed — output validated and safe to emit.
    """
    if confidence >= CONFIDENCE_THRESHOLD:
        return Channel.CH_2
    return Channel.CH_1


# ---------------------------------------------------------------------------
# DIRAM cryptographic receipt
# ---------------------------------------------------------------------------

def generate_diram_receipt(state_vector: S) -> str:
    """
    [PROB-05] Generate a SHA-256 DIRAM receipt for a state-vector allocation.

    Every state-space allocation must produce a traceable receipt per the
    DIRAM Boolean Logic spec (proofs/DIRAM_Boolean_Logic_Truth_Table.md).
    Receipt format is a 64-character hex digest.

    Parameters
    ----------
    state_vector : S
        The governed state whose bytes are hashed.

    Returns
    -------
    str
        64-character SHA-256 hex digest.
    """
    return hashlib.sha256(state_vector.tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# Shannon entropy of a state distribution
# ---------------------------------------------------------------------------

def compute_state_entropy(state_vector: S) -> float:
    """
    [PROB-05] Compute Shannon entropy H(S) of the state distribution.

    H(S) = -Σ p(s) log₂ p(s)

    Used in the cost-knowledge function C(K,S) = H(S) * exp(-K/t)
    to measure epistemic uncertainty before collapse.

    Parameters
    ----------
    state_vector : S
        Normalized internal state.

    Returns
    -------
    float
        Shannon entropy in bits. 0.0 for degenerate input.
    """
    flat = state_vector.flatten().astype(np.float64)
    flat_pos = flat[flat > 0]
    if flat_pos.size == 0:
        return 0.0
    return float(-np.sum(flat_pos * np.log2(flat_pos + 1e-12)))


# ---------------------------------------------------------------------------
# CH_1 structured deferral
# ---------------------------------------------------------------------------

def defer_to_human(state_vector: S, confidence: float) -> ProbeResult:
    """
    [PROB-05] CH_1 structured deferral with full provenance audit trail.

    Called when confidence < 0.954. Returns a ProbeResult that carries
    the state, receipt, and retry window so the caller can reconstruct
    provenance and schedule a 60s retry per the emergency protocol.

    Parameters
    ----------
    state_vector : S
        The state that failed to meet the confidence threshold.
    confidence : float
        Measured confidence that triggered deferral.

    Returns
    -------
    ProbeResult
        CH_1 result with DIRAM receipt and retry provenance.

    Governance
    ----------
    CH_1: Defer — no action emitted; human review required.
    """
    receipt = generate_diram_receipt(state_vector)
    degradation = round(1.0 - confidence / CONFIDENCE_THRESHOLD, 6)
    entropy = compute_state_entropy(state_vector)

    return ProbeResult(
        state=state_vector,
        confidence=confidence,
        channel=Channel.CH_1,
        receipt=receipt,
        provenance={
            "action": "defer_to_human",
            "retry_seconds": 60,
            "confidence": confidence,
            "threshold": CONFIDENCE_THRESHOLD,
            "degradation": degradation,
            "entropy_bits": entropy,
        },
    )
