# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
# =============================================================================

"""
obi.core — Cython-backed hot-path layer for the OBI probe system.

Public surface (Python orchestration side):

    from obi.core import ProbeEngine, Config, Channel
    from obi.core import EpistemicThresholdError, GovernanceViolationError
    from obi.core.governance import compute_epistemic_confidence, validate_gate
"""

from .governance import (
    CONFIDENCE_THRESHOLD,
    compute_epistemic_confidence,
    compute_state_entropy,
    defer_to_human,
    generate_diram_receipt,
    validate_gate,
)
from .probe import ProbeEngine
from .types import (
    Channel,
    Config,
    D,
    EpistemicThresholdError,
    GovernanceViolationError,
    ProbeResult,
    S,
)

__all__ = [
    # Probe engine
    "ProbeEngine",
    # Types
    "D",
    "S",
    "Config",
    "Channel",
    "ProbeResult",
    # Exceptions
    "EpistemicThresholdError",
    "GovernanceViolationError",
    # Governance helpers
    "CONFIDENCE_THRESHOLD",
    "compute_epistemic_confidence",
    "compute_state_entropy",
    "validate_gate",
    "generate_diram_receipt",
    "defer_to_human",
]
