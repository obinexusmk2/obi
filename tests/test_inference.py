"""
Tests for Bayesian inference engine
"""

import pytest
import numpy as np
from obi_sdk.sdk.core.inference import BayesianEngine, ReasoningMode, OBIContext


@pytest.fixture
def engine():
    ctx = OBIContext()
    yield BayesianEngine(ctx)
    ctx.close()


def test_top_down_reasoning(engine):
    """Test top-down (deductive) reasoning"""
    engine._mode = ReasoningMode.TOP_DOWN
    evidence = np.random.dirichlet(np.ones(10), size=1).reshape(1, 1, 2, 5)
    
    result, meta = engine.infer(evidence)
    
    assert result.shape == evidence.shape
    assert np.isclose(np.sum(result), 1.0)
    assert meta['mode'] == 'TOP_DOWN'


def test_bottom_up_reasoning(engine):
    """Test bottom-up (inductive) reasoning"""
    engine._mode = ReasoningMode.BOTTOM_UP
    evidence = np.random.rand(2, 3, 4, 5)
    
    result, meta = engine.infer(evidence)
    
    assert np.isfinite(result).all()
    assert meta['mode'] == 'BOTTOM_UP'


def test_bidirectional_reasoning(engine):
    """Test combined reasoning approach"""
    engine._mode = ReasoningMode.BIDIRECTIONAL
    evidence = np.random.rand(1, 1, 10, 10)
    
    result, meta = engine.infer(evidence)
    
    assert np.isclose(np.sum(result), 1.0, atol=1e-5)
    assert meta['mode'] == 'BIDIRECTIONAL'


def test_confidence_threshold(engine):
    """Test QA matrix confidence threshold"""
    engine._threshold = 0.99  # Very high threshold
    
    # Uniform distribution has low max probability
    evidence = np.ones((1, 1, 5, 5)) / 25
    
    result, meta = engine.infer(evidence)
    
    # Should still succeed but with warning
    assert 'warning' in str(meta['chain'])


def test_dimensional_reduction():
    """Test 4D tensor enforcement (DR = D - 1)"""
    from obi_sdk.sdk.core.inference import BayesianEngine
    
    engine = BayesianEngine(None)  # Mock context
    
    # Test various input dimensions
    test_cases = [
        np.random.rand(5),           # 1D -> 4D
        np.random.rand(3, 4),        # 2D -> 4D
        np.random.rand(2, 3, 4),     # 3D -> 4D
        np.random.rand(1, 2, 3, 4),  # 4D -> 4D
        np.random.rand(2, 3, 4, 5, 6),  # 5D -> 4D (recursive reduction)
    ]
    
    for case in test_cases:
        result = engine._ensure_4d(case)
        assert result.ndim == 4, f"Failed for shape {case.shape}"


def test_entropy_calculation():
    """Test uncertainty quantification"""
    from obi_sdk.sdk.core.inference import BayesianEngine
    
    engine = BayesianEngine(None)
    
    # Uniform distribution has max entropy
    uniform = np.ones(10) / 10
    entropy_uniform = engine._entropy(uniform)
    
    # Deterministic distribution has zero entropy
    deterministic = np.zeros(10)
    deterministic[0] = 1.0
    entropy_det = engine._entropy(deterministic)
    
    assert entropy_uniform > entropy_det
    assert entropy_det == 0.0
