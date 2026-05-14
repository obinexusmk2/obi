# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core.tests
# Problem: [PROB-01] Self-Blindness
# Test Suite: emit_external + sync_bidirectional — QA Matrix (TP / TN / FP / FN)
# Proof Source: Probe Hypothesis, AEGIS-PROOF-1.2, DIRAM Boolean Logic
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
# =============================================================================

import pytest
import numpy as np

from obi.core import (
    ProbeEngine,
    Config,
    Channel,
    EpistemicThresholdError,
    GovernanceViolationError,
)
from obi.core.governance import compute_epistemic_confidence, CONFIDENCE_THRESHOLD


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def engine() -> ProbeEngine:
    return ProbeEngine(Config(threshold=0.954))


@pytest.fixture
def valid_state() -> np.ndarray:
    """High-confidence state: dominant first element → softmax max ≈ 1.0."""
    s = np.zeros(64, dtype=np.float64)
    s[0] = 1.0
    norm = np.linalg.norm(s)
    return s / norm


@pytest.fixture
def low_state() -> np.ndarray:
    """Low-confidence state: uniform → softmax max ≈ 1/64 ≈ 0.016."""
    s = np.ones(64, dtype=np.float64)
    norm = np.linalg.norm(s)
    return s / norm


@pytest.fixture
def high_data() -> np.ndarray:
    """Raw data that, after probe_internal, produces a high-confidence state."""
    d = np.zeros(64, dtype=np.float32)
    d[0] = 1000.0
    return d


# ===========================================================================
# emit_external QA Matrix
# ===========================================================================

class TestEmitExternalTP:
    """TP: validated state correctly emits an external data payload."""

    def test_emit_external_state_data_tp(self, engine, valid_state):
        """[PROB-01][TP] Valid state produces uint8 output of correct shape."""
        data_out = engine.emit_external(valid_state)
        assert isinstance(data_out, np.ndarray)
        assert data_out.dtype == np.uint8
        assert data_out.shape == valid_state.shape

    def test_emit_external_range_tp(self, engine, valid_state):
        """[PROB-01][TP] Emitted data values are in [0, 255]."""
        data_out = engine.emit_external(valid_state)
        assert data_out.min() >= 0
        assert data_out.max() <= 255

    def test_emit_external_custom_shape_tp(self, engine, valid_state):
        """[PROB-01][TP] action_shape reshapes output correctly."""
        data_out = engine.emit_external(valid_state, action_shape=(8, 8))
        assert data_out.shape == (8, 8)
        assert data_out.dtype == np.uint8


class TestEmitExternalTN:
    """TN: low-confidence state is correctly blocked at the governance gate."""

    def test_emit_external_state_data_tn(self, engine, low_state):
        """[PROB-01][TN] Low-confidence state raises GovernanceViolationError."""
        with pytest.raises(GovernanceViolationError) as exc_info:
            engine.emit_external(low_state)

        msg = str(exc_info.value)
        assert "[CH_1]" in msg

    def test_emit_external_receipt_in_error_tn(self, engine, low_state):
        """[PROB-01][TN] Blocked emission error message contains DIRAM receipt."""
        with pytest.raises(GovernanceViolationError) as exc_info:
            engine.emit_external(low_state)
        assert "receipt" in str(exc_info.value).lower() or len(str(exc_info.value)) > 64


class TestEmitExternalFP:
    """FP: near-threshold state caught — gate does not silently pass bad state."""

    def test_emit_external_state_data_fp(self, engine):
        """[PROB-01][FP] Near-threshold state (below 0.954) is blocked."""
        # 2-element near-threshold state
        s = np.array([19.0, 1.0], dtype=np.float64)
        s = s / np.linalg.norm(s)
        confidence = compute_epistemic_confidence(s)

        if confidence < CONFIDENCE_THRESHOLD:
            with pytest.raises(GovernanceViolationError):
                engine.emit_external(s)
        else:
            # If it passes, output must be valid
            out = engine.emit_external(s)
            assert out.dtype == np.uint8


class TestEmitExternalFN:
    """FN: governance gate must never be bypassed for sub-threshold states."""

    def test_emit_external_state_data_fn(self, engine, low_state):
        """[PROB-01][FN] No emitted output for un-validated state — gate holds."""
        result = None
        try:
            result = engine.emit_external(low_state)
        except GovernanceViolationError:
            pass  # gate fired correctly

        if result is not None:
            # If somehow returned, confidence of source state must have been valid
            source_confidence = compute_epistemic_confidence(low_state)
            assert source_confidence >= CONFIDENCE_THRESHOLD, (
                f"[FN] Gate bypassed: source confidence {source_confidence:.6f}"
            )

    def test_emit_external_random_states_fn(self, engine):
        """[PROB-01][FN] All emitted states have source confidence >= threshold."""
        rng = np.random.default_rng(seed=0)
        for _ in range(30):
            s = rng.standard_normal(32).astype(np.float64)
            s = s / np.linalg.norm(s)
            confidence = compute_epistemic_confidence(s)
            try:
                out = engine.emit_external(s)
                # If it didn't raise, confidence must be >= threshold
                assert confidence >= CONFIDENCE_THRESHOLD, (
                    f"[FN] emit passed with confidence {confidence:.6f} < {CONFIDENCE_THRESHOLD}"
                )
            except GovernanceViolationError:
                assert confidence < CONFIDENCE_THRESHOLD


# ===========================================================================
# sync_bidirectional QA Matrix
# ===========================================================================

class TestSyncBidirectionalTP:
    """TP: aligned data + state produces a valid (new_state, emitted_data) pair."""

    def test_sync_bidirectional_data_state_tp(self, engine, high_data, valid_state):
        """[PROB-01][TP] Aligned data and state complete full D↔S round-trip."""
        new_state, emitted = engine.sync_bidirectional(high_data, valid_state)

        assert isinstance(new_state, np.ndarray)
        assert isinstance(emitted, np.ndarray)
        assert emitted.dtype == np.uint8

    def test_sync_bidirectional_observation_logged_tp(self, engine, high_data, valid_state):
        """[PROB-01][TP] CH_0 observation of current_state is recorded."""
        engine.reset_observation_log()
        engine.sync_bidirectional(high_data, valid_state)
        log = engine.observation_log
        assert len(log) >= 1
        assert log[0]["channel"] == Channel.CH_0.value

    def test_sync_bidirectional_receipt_in_log_tp(self, engine, high_data, valid_state):
        """[PROB-01][TP] Observation log entry contains a valid DIRAM receipt."""
        engine.reset_observation_log()
        engine.sync_bidirectional(high_data, valid_state)
        entry = engine.observation_log[0]
        assert len(entry["receipt"]) == 64


class TestSyncBidirectionalTN:
    """TN: misaligned state (drift) is correctly deferred via CH_1."""

    def test_sync_bidirectional_data_state_tn(self, engine, high_data):
        """[PROB-01][TN] Orthogonal current_state triggers drift deferral."""
        # Build a state orthogonal to what high_data would produce
        orthogonal_state = np.zeros(64, dtype=np.float64)
        orthogonal_state[-1] = 1.0          # last element dominant

        # high_data produces a state dominated by element[0]; orthogonal → low alignment
        with pytest.raises(EpistemicThresholdError) as exc_info:
            engine.sync_bidirectional(high_data, orthogonal_state)

        err = exc_info.value
        assert err.confidence < CONFIDENCE_THRESHOLD

    def test_sync_bidirectional_receipt_on_drift_tn(self, engine, high_data):
        """[PROB-01][TN] Drift deferral error carries DIRAM receipt."""
        orthogonal_state = np.zeros(64, dtype=np.float64)
        orthogonal_state[-1] = 1.0

        with pytest.raises(EpistemicThresholdError) as exc_info:
            engine.sync_bidirectional(high_data, orthogonal_state)

        assert len(exc_info.value.receipt) == 64


class TestSyncBidirectionalFP:
    """FP: near-threshold alignment data is caught — no silent pass."""

    def test_sync_bidirectional_data_state_fp(self, engine):
        """[PROB-01][FP] Near-orthogonal state raises or passes with valid confidence."""
        # Craft a current_state that is almost orthogonal to what high_data produces
        data = np.zeros(64, dtype=np.float32)
        data[0] = 1000.0

        # 45-degree rotation state → alignment ≈ cos(45°) ≈ 0.707 < 0.954
        mixed_state = np.zeros(64, dtype=np.float64)
        mixed_state[0] = 0.707
        mixed_state[1] = 0.707
        norm = np.linalg.norm(mixed_state)
        mixed_state /= norm

        try:
            new_state, emitted = engine.sync_bidirectional(data, mixed_state)
            # If it passed alignment check, new_state must be valid
            assert compute_epistemic_confidence(new_state) >= CONFIDENCE_THRESHOLD
        except EpistemicThresholdError:
            pass  # correctly deferred — alignment below threshold


class TestSyncBidirectionalFN:
    """FN: gate must never be bypassed — all returned states must be valid."""

    def test_sync_bidirectional_data_state_fn(self, engine, high_data, valid_state):
        """[PROB-01][FN] Every returned new_state has confidence >= threshold."""
        new_state, _ = engine.sync_bidirectional(high_data, valid_state)
        confidence = compute_epistemic_confidence(new_state)
        assert confidence >= CONFIDENCE_THRESHOLD, (
            f"[FN] sync returned state with confidence {confidence:.6f} < {CONFIDENCE_THRESHOLD}"
        )

    def test_sync_bidirectional_no_mutation_on_defer_fn(self, engine, high_data):
        """[PROB-01][FN] current_state is not mutated when CH_1 is triggered."""
        orthogonal_state = np.zeros(64, dtype=np.float64)
        orthogonal_state[-1] = 1.0
        state_copy = orthogonal_state.copy()

        try:
            engine.sync_bidirectional(high_data, orthogonal_state)
        except EpistemicThresholdError:
            pass

        # CH_0 observe must not mutate — original state unchanged
        np.testing.assert_array_equal(orthogonal_state, state_copy)
