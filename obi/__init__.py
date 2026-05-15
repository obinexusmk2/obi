"""
obi — Ontological Bayesian Intelligence v0.1.0 "Phoenix Rising"

Package hierarchy (agents.md §2.2):

    obi.core.*        Core inference engine (transitioning to pure Python)
    obi.cognition.*   Python orchestration: Filter-Flash, dimensional strategy
    obi.memory.*      Memory management: DIRAM gates, consciousness stack
    obi.integrity.*   Security: AuraSeal, ZID auth
    obi.data.*        Python: marshalling, polyglot adapters
    obi.telemetry.*   Python: intention promotion, sensor fusion

Entry-point for OBI reasoning:

    from obi import OBIContext
"""

from obi.sdk.core import OBIContext, ReasoningResult

__version__ = "0.1.0-alpha"
__author__ = "Nnamdi Michael Okpala (OBINexus)"

__all__ = ["OBIContext", "ReasoningResult"]
