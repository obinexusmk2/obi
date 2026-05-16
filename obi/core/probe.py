# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core.probe
# Problem: [PROB-01] Self-Blindness
# Proof Source: Probe Hypothesis, AEGIS-PROOF-1.1, AEGIS-PROOF-1.2
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
#
# Governance: CH_0 (Observe) | CH_1 (Defer) | CH_2 (Collapse)
# Confidence Threshold: 95.4%
# =============================================================================

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .governance import (
    compute_epistemic_confidence,
    compute_state_entropy,
    generate_diram_receipt,
)
from .types import (
    Channel,
    Config,
    D,
    EpistemicThresholdError,
    GovernanceViolationError,
    ProbeResult,
    S,
)


def _to_float_array(data: D) -> D:
    """Convert probe input to float64 ndarray without mutating caller data."""
    return np.asarray(data, dtype=np.float64)


def _receipt_for(array: D) -> str:
    """Create a stable DIRAM receipt for any ndarray-like input."""
    return generate_diram_receipt(np.ascontiguousarray(array, dtype=np.float64))


def _normalise_data(data_buffer: D) -> S:
    flat = data_buffer.flatten().astype(np.float64)
    if flat.size == 0:
        raise ValueError("[PROB-01] internal_probe: data_buffer must be non-empty")

    norm = np.linalg.norm(flat)
    with np.errstate(invalid="ignore", divide="ignore"):
        state_flat: S = (flat / norm) if norm > 1e-12 else flat.copy()
    return state_flat.reshape(data_buffer.shape)


def internal_probe(data: D, config: Optional[Config] = None) -> ProbeResult:
    """
    Functional P_internal: Data -> State.

    This is the non-throwing probe API. It always returns a ProbeResult for
    valid array-like input, using CH_2 for collapse and CH_1 for deferral.
    """
    cfg = config or Config()
    data_buffer = _to_float_array(data)
    state_vector = _normalise_data(data_buffer)
    confidence = compute_epistemic_confidence(state_vector)
    channel = Channel.CH_2 if confidence >= cfg.threshold else Channel.CH_1
    receipt = _receipt_for(state_vector)

    provenance: Dict[str, Any] = {
        "probe": "P_internal",
        "transition": "Data->State",
        "data_shape": tuple(data_buffer.shape),
        "state_shape": tuple(state_vector.shape),
        "threshold": cfg.threshold,
        "input_receipt": _receipt_for(data_buffer),
    }
    if channel == Channel.CH_1:
        provenance.update(
            {
                "action": "defer_to_human",
                "retry_seconds": 60,
                "degradation": round(1.0 - confidence / cfg.threshold, 6)
                if cfg.threshold
                else 1.0,
            }
        )

    return ProbeResult(
        state=state_vector,
        confidence=confidence,
        channel=channel,
        receipt=receipt,
        provenance=provenance,
    )


def external_probe(
    state: S,
    event: Optional[Dict[str, Any]] = None,
    output_shape: Optional[tuple] = None,
    config: Optional[Config] = None,
) -> ProbeResult:
    """
    Functional P_external: State/Event -> Data.

    The event is optional context for provenance. It does not alter the state
    transform in this first pure-Python probe implementation.
    """
    cfg = config or Config()
    state_vector = _to_float_array(state)
    confidence = compute_epistemic_confidence(state_vector)
    channel = Channel.CH_2 if confidence >= cfg.threshold else Channel.CH_1
    receipt = _receipt_for(state_vector)
    data_out: Optional[D] = None

    provenance: Dict[str, Any] = {
        "probe": "P_external",
        "transition": "State/Event->Data",
        "state_shape": tuple(state_vector.shape),
        "threshold": cfg.threshold,
    }

    if channel == Channel.CH_2:
        target_shape = output_shape or state_vector.shape
        flat = state_vector.flatten().astype(np.float64)
        v_min, v_max = flat.min(), flat.max()
        span = v_max - v_min
        normalised = (flat - v_min) / span if span > 1e-12 else np.zeros_like(flat)

        emitted = (normalised * 255.0).clip(0, 255).astype(np.uint8)
        target_size = int(np.prod(target_shape))
        if target_size != emitted.size:
            if target_size < emitted.size:
                emitted = emitted[:target_size]
            else:
                emitted = np.pad(emitted, (0, target_size - emitted.size))
        data_out = emitted.reshape(target_shape)
        provenance["data_shape"] = tuple(data_out.shape)
    else:
        provenance.update({"action": "defer_to_human", "retry_seconds": 60})

    return ProbeResult(
        state=state_vector,
        data=data_out,
        event=event,
        confidence=confidence,
        channel=channel,
        receipt=receipt,
        provenance=provenance,
    )


def probe_alignment(
    data: D,
    state: S,
    config: Optional[Config] = None,
) -> ProbeResult:
    """
    Functional mismatch probe.

    Computes P_internal(data) and compares it with the observed state. CH_2
    means data and state agree; CH_1 means replay, drift, or mismatch.
    """
    cfg = config or Config()
    internal = internal_probe(data, cfg)
    current_state = _to_float_array(state)

    old_flat = current_state.flatten().astype(np.float64)
    new_flat = internal.state.flatten().astype(np.float64)
    min_len = min(len(old_flat), len(new_flat))
    old_trimmed = old_flat[:min_len]
    new_trimmed = new_flat[:min_len]
    old_norm = np.linalg.norm(old_trimmed)
    new_norm = np.linalg.norm(new_trimmed)

    if old_norm > 1e-12 and new_norm > 1e-12:
        alignment = float(np.dot(old_trimmed, new_trimmed) / (old_norm * new_norm))
    else:
        alignment = 0.0
    if not np.isfinite(alignment):
        alignment = 0.0

    channel = (
        Channel.CH_2
        if internal.channel == Channel.CH_2 and alignment >= cfg.threshold
        else Channel.CH_1
    )
    provenance: Dict[str, Any] = {
        "probe": "P_alignment",
        "transition": "Data+State->State",
        "alignment": alignment,
        "threshold": cfg.threshold,
        "data_receipt": internal.provenance.get("input_receipt"),
        "current_state_receipt": _receipt_for(current_state),
    }
    if channel == Channel.CH_1:
        provenance.update({"action": "defer_to_human", "reason": "state_data_mismatch"})

    return ProbeResult(
        state=internal.state,
        confidence=alignment,
        channel=channel,
        receipt=internal.receipt,
        provenance=provenance,
    )


class ProbeEngine:
    """
    [PROB-01] Self-interrogation engine implementing the OBI probe duality.

    The functional APIs above are the canonical P_internal/P_external surface.
    This class preserves the original object-oriented methods that return raw
    arrays and raise on CH_1 deferral.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        self._config: Config = config or Config()
        self._observation_log: List[dict] = []

    def observe_state(self, state_vector: S) -> dict:
        """
        CH_0 read-only observation of a governed state vector.
        """
        state = _to_float_array(state_vector)
        confidence = compute_epistemic_confidence(state)
        receipt = _receipt_for(state)
        entropy = compute_state_entropy(state)

        record = {
            "channel": Channel.CH_0.value,
            "confidence": confidence,
            "entropy_bits": entropy,
            "shape": tuple(state.shape),
            "receipt": receipt,
        }
        self._observation_log.append(record)
        return record

    def probe_internal(
        self,
        data_buffer: D,
        probe_config: Optional[Config] = None,
    ) -> S:
        """
        Backward-compatible internal probe. Returns a raw state array on CH_2
        and raises EpistemicThresholdError on CH_1.
        """
        cfg = probe_config or self._config
        result = internal_probe(data_buffer, cfg)
        if result.channel == Channel.CH_1:
            raise EpistemicThresholdError(
                f"[PROB-01][CH_1] probe_internal deferred: "
                f"confidence {result.confidence:.6f} < threshold {cfg.threshold:.4f}. "
                f"Retry in 60s. "
                f"Input receipt: {result.provenance.get('input_receipt')}. "
                f"State receipt: {result.receipt}.",
                receipt=result.receipt,
                confidence=result.confidence,
            )
        return result.state

    def emit_external(
        self,
        state_vector: S,
        action_shape: Optional[tuple] = None,
    ) -> D:
        """
        Backward-compatible external probe. Returns emitted data on CH_2 and
        raises GovernanceViolationError on CH_1.
        """
        result = external_probe(
            state_vector,
            output_shape=action_shape,
            config=self._config,
        )
        if result.channel == Channel.CH_1:
            raise GovernanceViolationError(
                f"[PROB-01][CH_1] emit_external blocked: "
                f"confidence {result.confidence:.6f} < {self._config.threshold}. "
                f"Un-validated state must not be emitted. "
                f"DIRAM receipt: {result.receipt}."
            )
        return result.data

    def sync_bidirectional(
        self,
        data_buffer: D,
        current_state: S,
        config: Optional[Config] = None,
    ) -> Tuple[S, D]:
        """
        Full D<->S round-trip with alignment validation.
        """
        cfg = config or self._config
        self.observe_state(current_state)
        alignment_result = probe_alignment(data_buffer, current_state, cfg)
        if alignment_result.channel == Channel.CH_1:
            raise EpistemicThresholdError(
                f"[PROB-01][CH_1] sync_bidirectional: state drift detected. "
                f"Alignment rho={alignment_result.confidence:.6f} < threshold "
                f"{cfg.threshold}. DIRAM receipt: {alignment_result.receipt}.",
                receipt=alignment_result.receipt,
                confidence=alignment_result.confidence,
            )

        emitted = self.emit_external(alignment_result.state)
        return alignment_result.state, emitted

    @property
    def observation_log(self) -> List[dict]:
        """CH_0 audit trail: immutable copy of all observations."""
        return self._observation_log.copy()

    def reset_observation_log(self) -> None:
        """Clear the CH_0 audit trail between independent probe sessions."""
        self._observation_log.clear()
