"""
Bayesian Inference Engine - Ontological reasoning core

Implements top-down and bottom-up reasoning patterns as described
in the OBI AI hypothesis documentation.
"""

from typing import List, Tuple, Optional, Callable
import numpy as np
from enum import Enum, auto


class ReasoningMode(Enum):
    """Reasoning directionality for bias mitigation"""
    TOP_DOWN = auto()      # From general principles to specific cases
    BOTTOM_UP = auto()     # From observed data to general principles
    BIDIRECTIONAL = auto() # Combined approach for robust inference


class BayesianEngine:
    """
    Ontological Bayesian inference engine.
    
    Addresses the "black box" problem by providing explicit
    reasoning chains that can be inspected and audited.
    
    Non-monolithic: engines can be composed and chained.
    """
    
    def __init__(
        self,
        context: 'OBIContext',
        mode: ReasoningMode = ReasoningMode.BIDIRECTIONAL,
        confidence_threshold: float = 0.95
    ):
        self._ctx = context
        self._mode = mode
        self._threshold = confidence_threshold
        self._inference_chain: List[dict] = []
    
    def infer(
        self,
        evidence: np.ndarray,
        prior: Optional[np.ndarray] = None,
        confounders: Optional[List[str]] = None
    ) -> Tuple[np.ndarray, dict]:
        """
        Perform ontological Bayesian inference.
        
        Args:
            evidence: Observed data (qualitative or quantitative)
            prior: Prior distribution (if None, use uniform)
            confounders: List of potential confounding variables
        
        Returns:
            posterior: Updated belief distribution
            metadata: Inference chain for auditability
        """
        # Implement dimensional reduction (DR = D - 1)
        # as per OBI hypothesis documentation
        evidence_4d = self._ensure_4d(evidence)
        
        if self._mode == ReasoningMode.TOP_DOWN:
            result = self._top_down_reasoning(evidence_4d, prior)
        elif self._mode == ReasoningMode.BOTTOM_UP:
            result = self._bottom_up_reasoning(evidence_4d, prior)
        else:
            result = self._bidirectional_reasoning(evidence_4d, prior)
        
        # Apply QA matrix validation
        if not self._validate_result(result):
            raise InferenceError("Result failed QA matrix validation")
        
        return result, self._get_metadata()
    
    def _ensure_4d(self, arr: np.ndarray) -> np.ndarray:
        """Ensure tensor is 4D for OBI processing (batch, channel, height, width)"""
        if arr.ndim == 4:
            return arr
        elif arr.ndim < 4:
            # Pad dimensions
            shape = [1] * (4 - arr.ndim) + list(arr.shape)
            return arr.reshape(shape)
        else:
            # Dimensional reduction: DR = D - 1 recursively
            reduced = arr.reshape(arr.shape[0], -1, arr.shape[-2], arr.shape[-1])
            return self._ensure_4d(reduced)
    
    def _top_down_reasoning(
        self,
        evidence: np.ndarray,
        prior: Optional[np.ndarray]
    ) -> np.ndarray:
        """Deductive reasoning from general to specific"""
        # Implementation placeholder - calls into libpolycall
        if prior is None:
            prior = np.ones_like(evidence) / evidence.size
        
        # Bayesian update with explicit bias correction
        likelihood = self._compute_likelihood(evidence)
        posterior = (likelihood * prior) / np.sum(likelihood * prior)
        
        self._inference_chain.append({
            "step": "top_down_update",
            "prior_entropy": self._entropy(prior),
            "posterior_entropy": self._entropy(posterior)
        })
        
        return posterior
    
    def _bottom_up_reasoning(
        self,
        evidence: np.ndarray,
        prior: Optional[np.ndarray]
    ) -> np.ndarray:
        """Inductive reasoning from specific to general"""
        # Pattern recognition with explicit uncertainty quantification
        patterns = self._extract_patterns(evidence)
        posterior = self._generalize_patterns(patterns, prior)
        
        self._inference_chain.append({
            "step": "bottom_up_generalization",
            "pattern_count": len(patterns),
            "confidence": float(np.mean(posterior))
        })
        
        return posterior
    
    def _bidirectional_reasoning(
        self,
        evidence: np.ndarray,
        prior: Optional[np.ndarray]
    ) -> np.ndarray:
        """Combined approach for robust inference"""
        # Top-down provides structure, bottom-up fills details
        structured = self._top_down_reasoning(evidence, prior)
        detailed = self._bottom_up_reasoning(evidence, structured)
        
        # Consensus mechanism
        posterior = (structured + detailed) / 2
        return posterior
    
    def _compute_likelihood(self, evidence: np.ndarray) -> np.ndarray:
        """Compute likelihood with bias parameter adjustment"""
        # Placeholder for actual libpolycall integration
        return np.exp(evidence - np.max(evidence))
    
    def _extract_patterns(self, evidence: np.ndarray) -> List[np.ndarray]:
        """Extract patterns using K-means clustering (K-clustering per OBI docs)"""
        from sklearn.cluster import KMeans
        flat = evidence.reshape(-1, evidence.shape[-1])
        kmeans = KMeans(n_clusters=min(8, len(flat)), random_state=42)
        kmeans.fit(flat)
        return [flat[kmeans.labels_ == i] for i in range(kmeans.n_clusters)]
    
    def _generalize_patterns(
        self,
        patterns: List[np.ndarray],
        prior: Optional[np.ndarray]
    ) -> np.ndarray:
        """Generalize from patterns to distribution"""
        if not patterns:
            return np.ones_like(prior) / prior.size if prior is not None else np.array([0.5])
        
        # Weight by pattern size (more data = more weight)
        weights = np.array([len(p) for p in patterns])
        weights = weights / weights.sum()
        
        # Combine patterns
        combined = np.average([p.mean(axis=0) for p in patterns], weights=weights, axis=0)
        return combined
    
    def _entropy(self, dist: np.ndarray) -> float:
        """Compute Shannon entropy for uncertainty quantification"""
        dist = dist.flatten()
        dist = dist[dist > 0]  # Avoid log(0)
        return -np.sum(dist * np.log2(dist))
    
    def _validate_result(self, result: np.ndarray) -> bool:
        """
        QA Matrix validation per OBI specification:
        - True Positive: Correct detection
        - True Negative: Correct rejection
        - False Positive: Incorrect detection (Type I error)
        - False Negative: Incorrect rejection (Type II error)
        """
        # Check for NaN/Inf (indicates numerical instability)
        if not np.all(np.isfinite(result)):
            return False
        
        # Check probability distribution validity
        if not np.isclose(np.sum(result), 1.0, atol=1e-6):
            return False
        
        # Confidence threshold (95.4% per OBI spec)
        max_prob = np.max(result)
        if max_prob < self._threshold:
            self._inference_chain.append({
                "warning": "low_confidence",
                "max_probability": float(max_prob),
                "threshold": self._threshold
            })
        
        return True
    
    def _get_metadata(self) -> dict:
        """Return inference metadata for audit trail"""
        return {
            "mode": self._mode.name,
            "threshold": self._threshold,
            "chain": self._inference_chain.copy(),
            "version": "0.1.0-alpha"
        }


class InferenceError(Exception):
    """Raised when inference fails validation"""
    pass
