"""Tests for the Bayesian inference helper."""

import numpy as np

from obi import OBIContext
from obi.sdk.core.inference import BayesianEngine, ReasoningMode


def test_top_down_reasoning():
    engine = BayesianEngine(OBIContext(), mode=ReasoningMode.TOP_DOWN)
    evidence = np.random.default_rng(1).dirichlet(np.ones(10), size=1).reshape(1, 1, 2, 5)

    result, meta = engine.infer(evidence)

    assert result.shape == evidence.shape
    assert np.isclose(np.sum(result), 1.0)
    assert meta["mode"] == "TOP_DOWN"


def test_bottom_up_reasoning():
    engine = BayesianEngine(OBIContext(), mode=ReasoningMode.BOTTOM_UP)
    evidence = np.random.default_rng(2).random((2, 3, 4, 5))

    result, meta = engine.infer(evidence)

    assert result.shape == evidence.shape
    assert np.isfinite(result).all()
    assert np.isclose(np.sum(result), 1.0)
    assert meta["mode"] == "BOTTOM_UP"


def test_bidirectional_reasoning():
    engine = BayesianEngine(OBIContext(), mode=ReasoningMode.BIDIRECTIONAL)
    evidence = np.random.default_rng(3).random((1, 1, 10, 10))

    result, meta = engine.infer(evidence)

    assert result.shape == evidence.shape
    assert np.isclose(np.sum(result), 1.0, atol=1e-5)
    assert meta["mode"] == "BIDIRECTIONAL"


def test_dimensional_reduction_to_4d():
    engine = BayesianEngine(OBIContext())

    cases = [
        np.random.default_rng(4).random(5),
        np.random.default_rng(5).random((3, 4)),
        np.random.default_rng(6).random((2, 3, 4)),
        np.random.default_rng(7).random((1, 2, 3, 4)),
        np.random.default_rng(8).random((2, 3, 4, 5, 6)),
    ]

    for case in cases:
        assert engine._ensure_4d(case).ndim == 4


def test_entropy_calculation():
    engine = BayesianEngine(OBIContext())

    uniform = np.ones(10) / 10
    deterministic = np.zeros(10)
    deterministic[0] = 1.0

    assert engine._entropy(uniform) > engine._entropy(deterministic)
    assert engine._entropy(deterministic) == 0.0
