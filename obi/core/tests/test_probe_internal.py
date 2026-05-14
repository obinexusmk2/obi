# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core.tests
# Problem: [PROB-01] Self-Blindness
# Test Suite: probe_internal — QA Matrix (TP / TN / FP / FN)
# Proof Source: AEGIS-PROOF-1.1, Probe Hypothesis
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
#
# Naming convention: test_probe_internal_<noun>_<case>
#   _tp  True Positive  — correct detection, confidence >= 0.954
#   _tn  True Negative  — correct rejection, confidence < 0.954 as expected
#   _fp  False Positive — incorrect acceptance caught by governance gate
#   _fn  False Negative — missed deferral caught by EpistemicThresholdError
# =============================================================================

import pytest
import numpy as np

from obi.core import (
    ProbeEngine,
    Config,
    Channel,
    EpistemicThresholdError,
)
from obi.core.governance import compute_epistemic_confidence, CONFIDENCE_THRESHOLD


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> ProbeEngine:
    return ProbeEngine(Config(threshold=0.954))


@pytest.fixture
def high_confidence_data() -> np.ndarray:
    """
    Data that produces a highly peaked (high-confidence) state after L2-norm.
    One dominant component drives softmax max > 0.954.
    """
    data = np.zeros(128, dtype=np.float32)
    data[0] = 1000.0          # dominant spike → softmax max ≈ 1.0 after normalisation
    return data


@pytest.fixture
def low_confidence_data() -> np.ndarray:
    """
    Uniform data that produces a flat distribution after L2-norm.
    Softmax of a flat vector → max = 1/n, far below 0.954 for n > 1.
    """
    return np.ones(128, dtype=np.float32)   # uniform → confidence ≈ 1/128 ≈ 0.0078


# ---------------------------------------------------------------------------
# True Positive — correct detection, confidence >= 0.954
# ---------------------------------------------------------------------------

class TestProbeInternalTP:
    """
    TP: probe_internal correctly identifies high-confidence data and
    returns a governed state without raising.
    """

    def test_probe_internal_data_state_tp(self, engine, high_confidence_data):
        """[PROB-01][TP] High-confidence data collapses to CH_2 state."""
        state = engine.probe_internal(high_confidence_data)

        assert isinstance(state, np.ndarray)
        assert state.shape == high_confidence_data.shape
        assert state.dtype == np.float64

    def test_probe_internal_state_confidence_tp(self, engine, high_confidence_data):
        """[PROB-01][TP] Returned state has confidence >= 0.954 (CH_2)."""
        state = engine.probe_internal(high_confidence_data)
        confidence = compute_epistemic_confidence(state)
        assert confidence >= CONFIDENCE_THRESHOLD, (
            f"Expected confidence >= {CONFIDENCE_THRESHOLD}, got {confidence:.6f}"
        )

    def test_probe_internal_state_normalised_tp(self, engine, high_confidence_data):
        """[PROB-01][TP] Returned state vector is L2-normalised (unit norm)."""
        state = engine.probe_internal(high_confidence_data)
        norm = np.linalg.norm(state.flatten())
        assert abs(norm - 1.0) < 1e-6, f"Expected unit norm, got {norm:.8f}"

    def test_probe_internal_multidimensional_tp(self, engine):
        """[PROB-01][TP] 2-D input with dominant spike is correctly probed."""
        data = np.zeros((4, 32), dtype=np.float32)
        data[0, 0] = 500.0
        state = engine.probe_internal(data)
        assert state.shape == (4, 32)
        confidence = compute_epistemic_confidence(state)
        assert confidence >= CONFIDENCE_THRESHOLD


# ---------------------------------------------------------------------------
# True Negative — correct rejection, deferral triggered as expected
# ---------------------------------------------------------------------------

class TestProbeInternalTN:
    """
    TN: probe_internal correctly defers low-confidence data via CH_1
    (raises EpistemicThresholdError as intended — this is the right behaviour).
    """

    def test_probe_internal_data_state_tn(self, engine, low_confidence_data):
        """[PROB-01][TN] Uniform (low-confidence) data raises EpistemicThresholdError."""
        with pytest.raises(EpistemicThresholdError) as exc_info:
            engine.probe_internal(low_confidence_data)

        err = exc_info.value
        assert err.confidence < CONFIDENCE_THRESHOLD

    def test_probe_internal_receipt_present_tn(self, engine, low_confidence_data):
        """[PROB-01][TN] EpistemicThresholdError carries a non-empty DIRAM receipt."""
        with pytest.raises(EpistemicThresholdError) as exc_info:
            engine.probe_internal(low_confidence_data)

        receipt = exc_info.value.receipt
        assert isinstance(receipt, str)
        assert len(receipt) == 64, f"Expected 64-char SHA-256, got len={len(receipt)}"

    def test_probe_internal_ch1_message_tn(self, engine, low_confidence_data):
        """[PROB-01][TN] Error message carries [CH_1] and retry guidance."""
        with pytest.raises(EpistemicThresholdError) as exc_info:
            engine.probe_internal(low_confidence_data)

        msg = str(exc_info.value)
        assert "[CH_1]" in msg
        assert "Retry" in msg or "retry" in msg

    def test_probe_internal_custom_threshold_tn(self, engine):
        """[PROB-01][TN] Custom threshold=0.1 makes uniform data pass (inverted TN)."""
        permissive_cfg = Config(threshold=0.1)
        data = np.ones(4, dtype=np.float32)
        # confidence = softmax max of [0.25, 0.25, 0.25, 0.25] = 0.25 > 0.1
        state = engine.probe_internal(data, probe_config=permissive_cfg)
        assert state is not None


# ---------------------------------------------------------------------------
# False Positive — incorrect acceptance caught by governance gate
# ---------------------------------------------------------------------------

class TestProbeInternalFP:
    """
    FP: data that looks high-confidence on the surface but is adversarially
    crafted to produce a near-threshold state. The governance gate must
    catch values that appear to pass but fall fractionally short.
    """

    def test_probe_internal_data_state_fp(self, engine):
        """[PROB-01][FP] Near-threshold data (confidence just below 0.954) is deferred."""
        # Craft data whose L2-normalised softmax max lands just below 0.954.
        # A 2-element vector [k, 1] where k is large but not dominant enough.
        # softmax([k/norm, 1/norm]) max ≈ 0.95 < 0.954 when k ≈ 19.
        data = np.array([19.0, 1.0], dtype=np.float32)
        state_or_error = None
        try:
            state_or_error = engine.probe_internal(data)
        except EpistemicThresholdError as e:
            state_or_error = e

        # Either it passed (confidence barely >= 0.954) or was correctly deferred.
        # We assert the governance gate was engaged — no silent pass of bad state.
        if isinstance(state_or_error, np.ndarray):
            confidence = compute_epistemic_confidence(state_or_error)
            assert confidence >= CONFIDENCE_THRESHOLD, (
                "FP guard: governance gate allowed sub-threshold state through"
            )
        else:
            # Correctly caught: this is the expected path for near-threshold data
            assert isinstance(state_or_error, EpistemicThresholdError)

    def test_probe_internal_nan_fp(self, engine):
        """[PROB-01][FP] NaN data does not produce a valid state — gate triggers."""
        data = np.array([float("nan"), 1.0, 2.0], dtype=np.float32)
        with pytest.raises((EpistemicThresholdError, ValueError)):
            engine.probe_internal(data)

    def test_probe_internal_inf_fp(self, engine):
        """[PROB-01][FP] Inf data: normalisation collapses to unit state — gate applied."""
        data = np.array([float("inf"), 1.0], dtype=np.float32)
        try:
            state = engine.probe_internal(data)
            # If it didn't raise, confidence must meet threshold
            confidence = compute_epistemic_confidence(state)
            assert confidence >= CONFIDENCE_THRESHOLD
        except (EpistemicThresholdError, ValueError, FloatingPointError):
            pass  # Gate fired correctly


# ---------------------------------------------------------------------------
# False Negative — missed deferral must be caught; gate must not be bypassed
# ---------------------------------------------------------------------------

class TestProbeInternalFN:
    """
    FN: the governance gate must never silently pass a state whose confidence
    is below 0.954. These tests verify that the gate cannot be bypassed by
    edge-case inputs or configuration drift.
    """

    def test_probe_internal_data_state_fn(self, engine):
        """[PROB-01][FN] All-zeros data (zero-norm) does not silently pass."""
        data = np.zeros(64, dtype=np.float32)
        with pytest.raises((EpistemicThresholdError, ValueError)):
            engine.probe_internal(data)

    def test_probe_internal_gate_not_bypassed_fn(self, engine):
        """[PROB-01][FN] Any returned state must have confidence >= threshold."""
        rng = np.random.default_rng(seed=42)
        passed_states = []

        for _ in range(50):
            data = rng.uniform(0, 1, size=16).astype(np.float32)
            try:
                state = engine.probe_internal(data)
                passed_states.append(state)
            except EpistemicThresholdError:
                pass  # correctly deferred

        for state in passed_states:
            confidence = compute_epistemic_confidence(state)
            assert confidence >= CONFIDENCE_THRESHOLD, (
                f"[FN] Gate bypassed: state confidence {confidence:.6f} < {CONFIDENCE_THRESHOLD}"
            )

    def test_probe_internal_empty_fn(self, engine):
        """[PROB-01][FN] Empty array raises ValueError — never produces a state."""
        with pytest.raises(ValueError, match="non-empty"):
            engine.probe_internal(np.array([], dtype=np.float32))
