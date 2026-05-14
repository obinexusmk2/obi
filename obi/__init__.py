"""
obi — Ontological Bayesian Intelligence v0.1.0 "Phoenix Rising"

Package hierarchy (agents.md §2.2):

    obi.core.*        Cython hot-path: probes, memory, governance
    obi.cognition.*   Python orchestration: Filter-Flash, dimensional strategy
    obi.memory.*      Cython: DIRAM gates, consciousness stack
    obi.integrity.*   Cython: AuraSeal, ZID auth
    obi.data.*        Python: marshalling, polyglot adapters
    obi.telemetry.*   Python: intention promotion, sensor fusion

Entry-point for [PROB-01] probe system:

    from obi.core import ProbeEngine, Config, Channel
"""

from obi.core import ProbeEngine, Config, Channel  # noqa: F401
