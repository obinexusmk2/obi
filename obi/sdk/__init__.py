"""
OBIAI SDK - Ontological Bayesian Intelligence
Non-monolithic AI infrastructure for unbiased reasoning

This SDK provides:
- Ontological Bayesian inference engines
- Dimensional game theory solvers
- Filter-Flash memory architectures
- Non-monolithic plugin systems
"""

__version__ = "0.1.0-alpha"
__author__ = "Nnamdi Michael Okpala (OBINexus)"

from obi_sdk.sdk.core.context import OBIContext
from obi_sdk.sdk.core.tensor import OBITensor
from obi_sdk.sdk.core.inference import BayesianEngine

__all__ = ["OBIContext", "OBITensor", "BayesianEngine"]
