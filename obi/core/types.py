# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core.types
# Problem: [PROB-01] Self-Blindness — The system cannot interrogate its own state
# Proof Source: Probe Hypothesis, AEGIS-PROOF-1.1
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
#
# Governance: CH_0 (Observe) | CH_1 (Defer) | CH_2 (Collapse)
# Confidence Threshold: 95.4%
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Fundamental OBI type space (probe duality)
# ---------------------------------------------------------------------------

# D: raw external data — unprocessed, ungoverned input arriving from outside
D = np.ndarray

# S: internal state vector — normalized, governed, cryptographically receipted
S = np.ndarray


# ---------------------------------------------------------------------------
# Trident Channel architecture
# ---------------------------------------------------------------------------

class Channel(Enum):
    """
    [PROB-01] Trident Channel — routes computation based on epistemic confidence.

    CH_0: Read-only observation; state is inspected but never mutated.
    CH_1: Confidence < 0.954 — defer to human, 60s retry window.
    CH_2: Confidence >= 0.954 — collapse to validated output.
    """
    CH_0 = "observe"
    CH_1 = "defer"
    CH_2 = "collapse"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    """
    Probe configuration carrying the epistemic threshold and operational params.

    threshold : float
        Minimum cosine-alignment confidence to collapse (default 0.954 = μ+2σ).
    max_iterations : int
        Maximum Filter-Mode recursion depth before CH_1 is forced.
    context_id : str, optional
        Opaque identifier linking this config to an OBIContext instance.
    """
    threshold: float = 0.954
    max_iterations: int = 100
    context_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError(
                f"Config.threshold must be in [0, 1], got {self.threshold}"
            )
        if self.max_iterations < 1:
            raise ValueError(
                f"Config.max_iterations must be >= 1, got {self.max_iterations}"
            )


# ---------------------------------------------------------------------------
# Governed probe output
# ---------------------------------------------------------------------------

@dataclass
class ProbeResult:
    """
    [PROB-01] Governed state output carrying cryptographic DIRAM receipt.

    state      : S      — normalized state vector after D→S transform.
    confidence : float  — epistemic confidence in [0, 1].
    channel    : Channel — which Trident channel handled this result.
    receipt    : str    — SHA-256 hex digest (DIRAM memory-allocation protocol).
    provenance : dict   — full audit trail for human review.
    """
    state: S
    confidence: float
    channel: Channel
    receipt: str
    provenance: dict = field(default_factory=dict)

    @property
    def is_collapsed(self) -> bool:
        return self.channel == Channel.CH_2

    @property
    def is_deferred(self) -> bool:
        return self.channel == Channel.CH_1

    @property
    def is_observation(self) -> bool:
        return self.channel == Channel.CH_0


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class EpistemicThresholdError(Exception):
    """
    [PROB-01] Raised when confidence < 0.954 and no safe deferral path exists.

    Carries the DIRAM receipt and channel metadata so callers can reconstruct
    provenance without re-running the probe.
    """
    def __init__(self, message: str, receipt: str = "", confidence: float = 0.0):
        super().__init__(message)
        self.receipt = receipt
        self.confidence = confidence


class GovernanceViolationError(Exception):
    """
    Raised when a function attempts to cross the probe duality boundary without
    passing through the governance gate (e.g., emitting un-validated state).
    """
