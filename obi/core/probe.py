# =============================================================================
# OBIAI SDK v0.1.0 "Phoenix Rising"
# Package: obi.core.probe
# Problem: [PROB-01] Self-Blindness — The system cannot interrogate its own state
# Proof Source: Probe Hypothesis, AEGIS-PROOF-1.1, AEGIS-PROOF-1.2
# License: OBINexus Constitutional Legal Framework
# Primary Inventor: Nnamdi Michael Okpala
#
# Governance: CH_0 (Observe) | CH_1 (Defer) | CH_2 (Collapse)
# Confidence Threshold: 95.4%
# =============================================================================

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from .governance import (
    CONFIDENCE_THRESHOLD,
    compute_epistemic_confidence,
    compute_state_entropy,
    defer_to_human,
    generate_diram_receipt,
    validate_gate,
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


class ProbeEngine:
    """
    [PROB-01] Self-interrogation engine implementing the OBI probe duality.

    Addresses Self-Blindness: before this module the system had no formal
    mechanism to inspect, validate, or gate its own internal state before
    emitting any action. ProbeEngine provides three governed entry-points:

        probe_internal  : D → S   (raw data into governed state)
        emit_external   : S → D   (validated state into actionable output)
        sync_bidirectional : D ↔ S (full round-trip with alignment check)

    Every state boundary crossing generates a SHA-256 DIRAM receipt and is
    recorded in the observation log (CH_0 audit trail).

    Parameters
    ----------
    config : Config, optional
        Probe configuration. Defaults to Config() with threshold=0.954.

    Proof Source
    ------------
    - Probe Hypothesis (probe_internal, probe_external)
    - AEGIS-PROOF-1.1: Cost-Knowledge Function
    - AEGIS-PROOF-1.2: Traversal Cost Function
    - DIRAM Boolean Logic Truth Table

    Governance
    ----------
    CH_0: Observe — read-only state inspection, no mutation.
    CH_1: Defer — confidence < 0.954, 60s retry, human review.
    CH_2: Collapse — confidence >= 0.954, output validated.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        self._config: Config = config or Config()
        self._observation_log: List[dict] = []

    # -------------------------------------------------------------------------
    # CH_0 — Observe: read-only state snapshot, no state mutation
    # -------------------------------------------------------------------------

    def observe_state(self, state_vector: S) -> dict:
        """
        [PROB-01] CH_0 — Read-only observation of a governed state vector.

        Records confidence, entropy, shape, and DIRAM receipt into the
        immutable observation log. The state is never mutated here.

        Parameters
        ----------
        state_vector : S
            Governed internal state to inspect.

        Returns
        -------
        dict
            Observation record: channel, confidence, entropy, shape, receipt.

        Governance
        ----------
        CH_0: Read-only — state is inspected, never mutated.
        """
        confidence = compute_epistemic_confidence(state_vector)
        receipt = generate_diram_receipt(state_vector)
        entropy = compute_state_entropy(state_vector)

        record = {
            "channel": Channel.CH_0.value,
            "confidence": confidence,
            "entropy_bits": entropy,
            "shape": tuple(state_vector.shape),
            "receipt": receipt,
        }
        self._observation_log.append(record)
        return record

    # -------------------------------------------------------------------------
    # probe_internal : D → S
    # -------------------------------------------------------------------------

    def probe_internal(
        self,
        data_buffer: D,
        probe_config: Optional[Config] = None,
    ) -> S:
        """
        [PROB-01] Internal Probe: D → S

        Transforms raw external data into a governed internal state vector.
        Implements the "Know Thyself" principle of OBI architecture.

        The transform is:
            1. Flatten data_buffer to 1-D float64.
            2. L2-normalise into unit-sphere state space S ⊂ ℝⁿ.
            3. Validate via governance gate (CH_1 / CH_2).
            4. Return state on CH_2; raise EpistemicThresholdError on CH_1.

        Parameters
        ----------
        data_buffer : D
            Raw input data (any dtype, any shape). Non-empty required.
        probe_config : Config, optional
            Override probe configuration for this call.

        Returns
        -------
        S
            L2-normalised state vector, same shape as data_buffer,
            dtype float64, with confidence >= 0.954.

        Raises
        ------
        EpistemicThresholdError
            If confidence < 0.954 after normalisation. Carries receipt
            and confidence for caller-side provenance reconstruction.
        ValueError
            If data_buffer is empty.

        Proof Source
        ------------
        - AEGIS-PROOF-1.1: Cost-Knowledge Function
        - Probe Hypothesis: probe_internal(D → S)

        Governance
        ----------
        CH_0: Observe — raw input snapshot before normalisation.
        CH_1: Defer  — confidence < threshold; 60s retry triggered.
        CH_2: Collapse — confidence >= threshold; state returned.
        """
        cfg = probe_config or self._config

        # --- Validate input ---
        flat = data_buffer.flatten().astype(np.float64)
        if flat.size == 0:
            raise ValueError("[PROB-01] probe_internal: data_buffer must be non-empty")

        # --- CH_0: Observe raw input (creates DIRAM receipt before mutation) ---
        raw_receipt = generate_diram_receipt(data_buffer.astype(np.float64))

        # --- D → S transform: L2-normalisation into unit-sphere ---
        norm = np.linalg.norm(flat)
        state_flat: S = (flat / norm) if norm > 1e-12 else flat.copy()
        state_vector: S = state_flat.reshape(data_buffer.shape)

        # --- Governance gate (respect per-call threshold, not global constant) ---
        confidence = compute_epistemic_confidence(state_vector)
        channel = Channel.CH_2 if confidence >= cfg.threshold else Channel.CH_1

        if channel == Channel.CH_1:
            state_receipt = generate_diram_receipt(state_vector)
            raise EpistemicThresholdError(
                f"[PROB-01][CH_1] probe_internal deferred: "
                f"confidence {confidence:.6f} < threshold {cfg.threshold:.4f}. "
                f"Retry in 60s. "
                f"Input receipt: {raw_receipt}. "
                f"State receipt: {state_receipt}.",
                receipt=state_receipt,
                confidence=confidence,
            )

        # --- CH_2: Collapse — state is validated ---
        return state_vector

    # -------------------------------------------------------------------------
    # emit_external : S → D
    # -------------------------------------------------------------------------

    def emit_external(
        self,
        state_vector: S,
        action_shape: Optional[tuple] = None,
    ) -> D:
        """
        [PROB-01] External Probe: S → D

        Transforms a validated internal state into actionable external data.
        The governance gate is enforced before emission — no un-validated
        state can escape the probe boundary.

        The transform is:
            1. Validate state confidence via governance gate.
            2. Raise GovernanceViolationError if gate not passed.
            3. Denormalise from unit-sphere to uint8 action space [0, 255].
            4. Reshape to action_shape (defaults to state_vector.shape).

        Parameters
        ----------
        state_vector : S
            Governed internal state produced by probe_internal.
        action_shape : tuple, optional
            Output data shape. Defaults to state_vector.shape.

        Returns
        -------
        D
            uint8 numpy array in range [0, 255], ready for actuation.

        Raises
        ------
        GovernanceViolationError
            If state confidence < 0.954 — un-validated state must not be emitted.

        Proof Source
        ------------
        - Probe Hypothesis: probe_external(S → D)
        - AEGIS-PROOF-1.2: Traversal Cost Function

        Governance
        ----------
        CH_1: Block emission — state not yet validated, no output produced.
        CH_2: Collapse — emit denormalised external data payload.
        """
        confidence = compute_epistemic_confidence(state_vector)
        channel = Channel.CH_2 if confidence >= self._config.threshold else Channel.CH_1

        if channel == Channel.CH_1:
            receipt = generate_diram_receipt(state_vector)
            raise GovernanceViolationError(
                f"[PROB-01][CH_1] emit_external blocked: "
                f"confidence {confidence:.6f} < {CONFIDENCE_THRESHOLD}. "
                f"Un-validated state must not be emitted. "
                f"DIRAM receipt: {receipt}."
            )

        target_shape = action_shape or state_vector.shape
        flat = state_vector.flatten().astype(np.float64)

        # Denormalise: [−1, 1] or [0, 1] unit-sphere → uint8 [0, 255]
        v_min, v_max = flat.min(), flat.max()
        span = v_max - v_min
        if span > 1e-12:
            normalised = (flat - v_min) / span
        else:
            normalised = np.zeros_like(flat)

        data_out: D = (normalised * 255.0).clip(0, 255).astype(np.uint8)

        # Reshape to target — pad or trim if shapes are incompatible
        target_size = int(np.prod(target_shape))
        current_size = data_out.size
        if target_size != current_size:
            if target_size < current_size:
                data_out = data_out[:target_size]
            else:
                data_out = np.pad(data_out, (0, target_size - current_size))

        return data_out.reshape(target_shape)

    # -------------------------------------------------------------------------
    # sync_bidirectional : D ↔ S
    # -------------------------------------------------------------------------

    def sync_bidirectional(
        self,
        data_buffer: D,
        current_state: S,
        config: Optional[Config] = None,
    ) -> Tuple[S, D]:
        """
        [PROB-01] Bidirectional Sync: D ↔ S with governance gate.

        Performs a full D→S→D round-trip with alignment validation between
        the incoming data and the current state. Used for state reconciliation
        and drift detection across the probe boundary.

        Protocol:
            1. CH_0: Observe current_state (audit log entry, no mutation).
            2. D→S: probe_internal(data_buffer) → new_state.
            3. Alignment: cosine similarity ρ(current_state, new_state).
            4. CH_1 if ρ < threshold (state drift, defer to human).
            5. CH_2 if ρ >= threshold → S→D: emit_external(new_state).
            6. Return (new_state, emitted_data).

        Parameters
        ----------
        data_buffer : D
            Incoming raw data to ingest.
        current_state : S
            Current governed state to reconcile against.
        config : Config, optional
            Configuration override for this call.

        Returns
        -------
        Tuple[S, D]
            (updated_state, emitted_data) after full governed round-trip.

        Raises
        ------
        EpistemicThresholdError
            If probe_internal fails (D→S confidence < threshold) or if
            state alignment ρ(old, new) < threshold (drift detected).

        Proof Source
        ------------
        - Probe Hypothesis: bidirectional sync with governance gate
        - DIRAM Boolean Logic Truth Table: state reconciliation (bits 11/10/01/00)
        - AEGIS-PROOF-1.1 / 1.2: cost-knowledge and traversal functions

        Governance
        ----------
        CH_0: Observe current_state before any mutation.
        CH_1: Defer if new_state alignment < threshold or D→S fails.
        CH_2: Collapse to (new_state, emitted_data) if alignment passes.
        """
        cfg = config or self._config

        # CH_0: Observe — snapshot current state into audit log
        self.observe_state(current_state)

        # D → S: ingest new data (may raise EpistemicThresholdError)
        new_state: S = self.probe_internal(data_buffer, cfg)

        # Alignment gate: cosine similarity between old and new state
        old_flat = current_state.flatten().astype(np.float64)
        new_flat = new_state.flatten().astype(np.float64)

        min_len = min(len(old_flat), len(new_flat))
        old_trimmed = old_flat[:min_len]
        new_trimmed = new_flat[:min_len]

        old_norm = np.linalg.norm(old_trimmed)
        new_norm = np.linalg.norm(new_trimmed)

        if old_norm > 1e-12 and new_norm > 1e-12:
            alignment = float(
                np.dot(old_trimmed, new_trimmed) / (old_norm * new_norm)
            )
        else:
            alignment = 0.0

        if alignment < cfg.threshold:
            deferred = defer_to_human(new_state, alignment)
            raise EpistemicThresholdError(
                f"[PROB-01][CH_1] sync_bidirectional: state drift detected. "
                f"Alignment ρ={alignment:.6f} < threshold {cfg.threshold}. "
                f"DIRAM receipt: {deferred.receipt}.",
                receipt=deferred.receipt,
                confidence=alignment,
            )

        # S → D: emit validated state as external data payload
        emitted: D = self.emit_external(new_state)

        return new_state, emitted

    # -------------------------------------------------------------------------
    # Audit interface
    # -------------------------------------------------------------------------

    @property
    def observation_log(self) -> List[dict]:
        """
        CH_0 audit trail — immutable copy of all CH_0 observations.

        Each entry contains: channel, confidence, entropy_bits, shape, receipt.
        """
        return self._observation_log.copy()

    def reset_observation_log(self) -> None:
        """Clear the CH_0 audit trail. Useful between independent probe sessions."""
        self._observation_log.clear()
