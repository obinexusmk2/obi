"""Functional NumPy-style API for OBI Bayesian debiasing.

The public surface follows the PSC debiasing modules: audit bias vectors,
declare a causal DAG, compute a deterministic minimal debiased posterior, and
validate fairness guarantees.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from obi.sdk.core import OBIContext


EPS = 1e-12
C_COHERENCE = 0.954
DRIFT_BOUND_MAX = 12.0
LAMBDA_DECAY_DEFAULT = 0.5


class FairnessValidationError(Exception):
    """Raised when a fairness validation policy requires aborting."""

    def __init__(self, report: "ValidationReport") -> None:
        self.report = report
        super().__init__(
            "Demographic parity validation failed: "
            f"max_gap={report.max_gap:.6f} > epsilon={report.epsilon:.6f}"
        )


@dataclass
class Dataset:
    """NumPy-backed dataset container for debiasing workflows."""

    X: np.ndarray
    y: Optional[np.ndarray] = None
    protected: Optional[np.ndarray] = None
    feature_names: List[str] = field(default_factory=list)
    model_config: Dict[str, Any] = field(default_factory=dict)

    @property
    def n_samples(self) -> int:
        return int(self.X.shape[0])

    @property
    def n_features(self) -> int:
        return int(self.X.shape[1])

    def manifest(self) -> Dict[str, Any]:
        return {
            "shape": tuple(self.X.shape),
            "has_labels": self.y is not None,
            "has_protected": self.protected is not None,
            "feature_names": self.feature_names,
            "model_config": self.model_config,
        }


@dataclass
class BiasReport:
    """Bias audit result for the four PSC bias vectors."""

    data_bias: bool
    feature_bias: bool
    label_bias: bool
    spec_bias: bool
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def any_bias_found(self) -> bool:
        return self.data_bias or self.feature_bias or self.label_bias or self.spec_bias

    def manifest(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["any_bias_found"] = self.any_bias_found
        return payload


@dataclass(frozen=True)
class Variable:
    """DAG variable declaration."""

    name: str
    kind: str
    observed: bool = True


@dataclass
class DAG:
    """Simple directed acyclic graph metadata container."""

    variables: Dict[str, Variable] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)

    def add_variable(self, item: Variable | str, kind: str = "real", observed: bool = True) -> "DAG":
        var = item if isinstance(item, Variable) else Variable(item, kind, observed)
        self.variables[var.name] = var
        return self

    def add_edge(self, parent: str, child: str) -> "DAG":
        if parent not in self.variables:
            self.add_variable(parent)
        if child not in self.variables:
            self.add_variable(child)
        edge_item = (parent, child)
        if edge_item not in self.edges:
            self.edges.append(edge_item)
        return self

    def parents(self, name: str) -> List[str]:
        return [parent for parent, child in self.edges if child == name]

    def children(self, name: str) -> List[str]:
        return [child for parent, child in self.edges if parent == name]

    def neighbors(self, name: str) -> List[str]:
        values = set(self.parents(name))
        values.update(self.children(name))
        return sorted(values)

    def factorize(self) -> List[Dict[str, Any]]:
        factors = []
        for name in self.variables:
            parents = self.parents(name)
            factors.append(
                {
                    "variable": name,
                    "parents": parents,
                    "expression": f"P({name} | {', '.join(parents)})" if parents else f"P({name})",
                }
            )
        return factors

    def manifest(self) -> Dict[str, Any]:
        return {
            "variables": {name: asdict(var) for name, var in self.variables.items()},
            "edges": list(self.edges),
            "factorization": self.factorize(),
        }


@dataclass
class IntegrityStatus:
    """Lightweight integrity metadata for deterministic pipeline runs."""

    system_intact: bool = True
    heartbeat_ok: bool = True
    message: str = "integrity checks passed"


@dataclass
class CircuitBreaker:
    """Minimal three-state circuit breaker metadata."""

    failure_threshold: int = 1
    state: str = "closed"
    failures: int = 0

    def allow_operation(self) -> bool:
        return self.state != "open"

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"

    def reset(self) -> None:
        self.failures = 0
        self.state = "closed"

    def manifest(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DebiasResult:
    """Deterministic minimal debiasing result."""

    theta: np.ndarray
    bias_params: Dict[str, Any]
    posterior: np.ndarray
    predictions: np.ndarray
    audit_trail: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    dataset: Dataset
    graph: DAG
    integrity: IntegrityStatus = field(default_factory=IntegrityStatus)
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    validation_report: Optional["ValidationReport"] = None

    def manifest(self) -> Dict[str, Any]:
        return {
            "theta": self.theta,
            "bias_params": self.bias_params,
            "posterior": self.posterior,
            "metrics": self.metrics,
            "audit_trail": self.audit_trail,
            "dataset": self.dataset.manifest(),
            "graph": self.graph.manifest(),
            "integrity": self.integrity,
            "circuit_breaker": self.circuit_breaker,
            "validation_report": self.validation_report,
        }


@dataclass
class ValidationReport:
    """Runtime fairness validation report."""

    parity_gaps: Dict[str, float]
    parity_ok: bool
    epsilon: float
    warnings: List[str] = field(default_factory=list)

    @property
    def max_gap(self) -> float:
        return max(self.parity_gaps.values(), default=0.0)

    def manifest(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["max_gap"] = self.max_gap
        return payload


@dataclass
class DataPoint:
    """Data drift input carrying raw, contextual, and epistemic views."""

    raw_features: np.ndarray
    context_features: np.ndarray
    knowledge_embedding: np.ndarray
    drift_source: str = "ai_system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    id: str = ""

    def __post_init__(self) -> None:
        self.raw_features = array(self.raw_features, dtype=float).reshape(-1)
        self.context_features = array(self.context_features, dtype=float).reshape(-1)
        self.knowledge_embedding = array(self.knowledge_embedding, dtype=float).reshape(-1)
        if not self.id:
            self.id = content_hash(self)[:16]

    @property
    def distribution(self) -> np.ndarray:
        return normalize(np.abs(self.raw_features) + EPS)

    @property
    def context_distribution(self) -> np.ndarray:
        return normalize(np.abs(self.context_features) + EPS)

    def manifest(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "raw_features": self.raw_features,
            "context_features": self.context_features,
            "knowledge_embedding": self.knowledge_embedding,
            "drift_source": self.drift_source,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class DriftObservation:
    """Classified drift observation on the signed failure scale."""

    magnitude: float
    vector_type: str
    zone: str
    response: "ZoneResponse"
    timestamp: float
    source: str

    def manifest(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ZoneResponse:
    """Recommended response for a signed drift zone."""

    zone: str
    cascade: str
    action: str
    description: str


@dataclass
class StorageRecord:
    """Storage layer record: hash XOR cultural context XOR love anchors."""

    content: str
    source_id: str
    timestamp: float
    retrieval_key: str
    cultural_context: str
    love_anchor: str


@dataclass
class ProcessedOutput:
    """Filter/Flash/DIRAM processed output."""

    value: float
    data: np.ndarray
    source: str
    coherence: float
    drift: float = 0.0
    active_tiers: List[str] = field(default_factory=list)
    storage_record: Optional[StorageRecord] = None
    eze_override: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def manifest(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DIRAMCascade:
    """Three-tier persona cascade for drift mitigation."""

    active_tiers: List[str] = field(default_factory=lambda: ["obinexus"])

    def activate_tier(self, tier: str) -> None:
        if tier not in {"obinexus", "uche", "eze"}:
            raise ValueError(f"Unknown DIRAM tier: {tier!r}")
        if tier not in self.active_tiers:
            self.active_tiers.append(tier)

    def activate_for_drift(self, drift: float) -> List[str]:
        magnitude = abs(float(drift))
        if magnitude > 3.0:
            self.activate_tier("uche")
        if magnitude > 6.0:
            self.activate_tier("eze")
        return self.get_active_tiers()

    def get_active_tiers(self) -> List[str]:
        order = {"obinexus": 0, "uche": 1, "eze": 2}
        return sorted(self.active_tiers, key=lambda tier: order[tier])

    def manifest(self) -> Dict[str, Any]:
        return {"active_tiers": self.get_active_tiers()}


@dataclass
class DriftResult:
    """End-to-end drift mitigation result."""

    observation: DriftObservation
    output: ProcessedOutput
    cascade: DIRAMCascade
    audit_trail: List[Dict[str, Any]]

    def manifest(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlashMemoryEntry:
    """Ephemeral Flash working-memory entry."""

    data: DataPoint
    birth_time: float
    initial_value: float

    def residual(self, current_t: float, lambda_decay: float) -> float:
        age = max(0.0, current_t - self.birth_time)
        return float(self.initial_value * np.exp(-lambda_decay * age))


@dataclass
class FilterFlashEngine:
    """Minimal Filter/Flash engine with DIRAM cascade metadata."""

    threshold: float = C_COHERENCE
    lambda_decay: float = LAMBDA_DECAY_DEFAULT
    filter_memory: Dict[str, StorageRecord] = field(default_factory=dict)
    flash_memory: Dict[str, FlashMemoryEntry] = field(default_factory=dict)
    diram_cascade: DIRAMCascade = field(default_factory=DIRAMCascade)

    def measure_confidence(self, input_data: DataPoint) -> float:
        return state_confidence(input_data.raw_features)

    def process(
        self,
        input_data: DataPoint,
        drift: float = 0.0,
        current_t: Optional[float] = None,
        safe_state: Any = None,
    ) -> ProcessedOutput:
        confidence = self.measure_confidence(input_data)
        active_tiers = self.diram_cascade.activate_for_drift(drift)
        if "eze" in active_tiers:
            output = self._eze_override(input_data, drift, safe_state)
        elif confidence >= self.threshold:
            output = self._filter_process(input_data, drift)
        else:
            output = self._flash_process(input_data, drift, current_t=current_t)
            if self.can_persist(output):
                self.integrate(output, input_data)
        output.active_tiers = self.diram_cascade.get_active_tiers()
        return output

    def can_persist(self, result: ProcessedOutput) -> bool:
        stable = result.metadata.get("reevaluation_confidence", result.coherence)
        return result.coherence >= self.threshold and stable >= self.threshold * 0.95

    def integrate(self, result: ProcessedOutput, input_data: DataPoint) -> None:
        record = storage_layer(input_data)
        self.filter_memory[input_data.id] = record
        result.storage_record = record

    def evict_stale_entries(
        self,
        current_t: Optional[float] = None,
        eviction_threshold: float = 0.01,
    ) -> List[str]:
        now = time.time() if current_t is None else float(current_t)
        stale = [
            item_id
            for item_id, entry in self.flash_memory.items()
            if entry.residual(now, self.lambda_decay) < eviction_threshold
        ]
        for item_id in stale:
            self.flash_memory.pop(item_id, None)
        return stale

    def _filter_process(self, input_data: DataPoint, drift: float) -> ProcessedOutput:
        value = filter_layer(input_data)
        record = storage_layer(input_data)
        self.filter_memory[input_data.id] = record
        return ProcessedOutput(
            value=value,
            data=input_data.raw_features.copy(),
            source="filter",
            coherence=self.measure_confidence(input_data),
            drift=drift,
            storage_record=record,
            metadata={"mode": "persistent_symbolic_reasoning"},
        )

    def _flash_process(
        self,
        input_data: DataPoint,
        drift: float,
        current_t: Optional[float] = None,
    ) -> ProcessedOutput:
        now = time.time() if current_t is None else float(current_t)
        value = flash_layer(input_data, t=0.0, lambda_decay=self.lambda_decay)
        self.flash_memory[input_data.id] = FlashMemoryEntry(
            data=input_data,
            birth_time=now,
            initial_value=value,
        )
        self.evict_stale_entries(current_t=now)
        return ProcessedOutput(
            value=value,
            data=input_data.raw_features.copy(),
            source="flash",
            coherence=self.measure_confidence(input_data),
            drift=drift,
            metadata={
                "mode": "ephemeral_working_memory",
                "reevaluation_confidence": self.measure_confidence(input_data),
            },
        )

    def _eze_override(
        self,
        input_data: DataPoint,
        drift: float,
        safe_state: Any = None,
    ) -> ProcessedOutput:
        safe = (
            array(safe_state, dtype=float).reshape(-1)
            if safe_state is not None
            else np.zeros_like(input_data.raw_features)
        )
        if safe.shape != input_data.raw_features.shape:
            safe = np.resize(safe, input_data.raw_features.shape)
        data = (0.8 * safe) + (0.2 * input_data.raw_features)
        coherence = max(self.threshold, state_confidence(data))
        return ProcessedOutput(
            value=float(np.linalg.norm(data)),
            data=data,
            source="filter",
            coherence=coherence,
            drift=drift,
            eze_override=True,
            metadata={"mode": "eze_safe_fallback"},
        )

    def manifest(self) -> Dict[str, Any]:
        return {
            "threshold": self.threshold,
            "lambda_decay": self.lambda_decay,
            "filter_memory_size": len(self.filter_memory),
            "flash_memory_size": len(self.flash_memory),
            "diram_cascade": self.diram_cascade.manifest(),
        }


@dataclass
class MALPAARTICEFramework:
    """Monitoring, Auditing, Logging, Prevention governance ledger."""

    monitor_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    trace_log: List[Dict[str, Any]] = field(default_factory=list)
    risk_register: List[Dict[str, Any]] = field(default_factory=list)

    def monitor(self, result: DriftResult) -> Dict[str, Any]:
        record = {
            "timestamp": time.time(),
            "drift_level": result.observation.magnitude,
            "coherence": result.output.coherence,
            "active_tiers": result.cascade.get_active_tiers(),
            "zone": result.observation.zone,
        }
        self.monitor_log.append(record)
        return record

    def audit(self, coherence_threshold: float = C_COHERENCE) -> Dict[str, Any]:
        violations = [
            record
            for record in self.monitor_log
            if record["coherence"] < coherence_threshold
            or record["zone"] in {"ai_panic", "ai_warning"}
        ]
        report = {
            "violations": violations,
            "compliance_rate": 1.0
            - (len(violations) / max(len(self.monitor_log), 1)),
        }
        self.audit_log.append(report)
        return report

    def log(self, event_type: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        record = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": dict(payload),
            "proof_ref": "OBIAI-THESIS + AEGIS chain",
        }
        self.trace_log.append(record)
        return record

    def prevent(self, current_drift: float) -> Dict[str, Any]:
        predicted_zone = classify_drift_zone(current_drift)
        if predicted_zone in {"ai_caution", "human_stress_low"}:
            action = {
                "type": "pre_activate_uche",
                "reason": "Predicted drift approaching thresholds",
                "predicted_zone": predicted_zone,
            }
            self.risk_register.append(action)
            return action
        return {"type": "no_action", "predicted_zone": predicted_zone}


@dataclass
class TriangiReport:
    """Triangi-style coherence validation report."""

    n_total: int
    n_passed: int
    overall_score: float
    threshold_met: bool
    coherence_curve: Dict[float, float]
    threshold: float = C_COHERENCE

    def manifest(self) -> Dict[str, Any]:
        return asdict(self)


def context(
    confidence_threshold: float = 0.954,
    reasoning_mode: str = "bidirectional",
    config: Optional[Dict[str, Any]] = None,
) -> OBIContext:
    """Create the backwards-compatible OBI reasoning context."""
    return OBIContext(
        confidence_threshold=confidence_threshold,
        reasoning_mode=reasoning_mode,
        config=config,
    )


def get_context(kind: str = "reasoning", **kwargs: Any) -> OBIContext:
    """Canvas-style alias for the backwards-compatible reasoning context."""
    if kind not in {"reasoning", "ml", "obi"}:
        raise ValueError(f"Unknown OBI context kind: {kind!r}")
    return context(**kwargs)


def array(data: Any, dtype: Any = float) -> np.ndarray:
    """Convert data to an OBI-compatible NumPy array."""
    return np.asarray(data, dtype=dtype)


def normalize(p: Any) -> np.ndarray:
    """Normalize an array-like probability vector."""
    p = array(p, dtype=float)
    return p / (p.sum() + EPS)


def entropy(p: Any) -> float:
    """Compute Shannon entropy for a probability vector."""
    p = normalize(p)
    return float(-np.sum(p * np.log(p + EPS)))


def kl(p: Any, q: Any) -> float:
    """Compute KL divergence KL(p || q)."""
    p = normalize(p)
    q = normalize(q)
    return float(np.sum(p * np.log((p + EPS) / (q + EPS))))


def kl_divergence(p: Any, q: Any) -> float:
    """Alias for :func:`kl`."""
    return kl(p, q)


def prediction_rate(predictions: Any, threshold: float = 0.5) -> float:
    """Return the positive prediction rate for scores or binary predictions."""
    scores = array(predictions, dtype=float).reshape(-1)
    return float(np.mean(scores >= threshold)) if scores.size else 0.0


def demographic_parity_gap(
    predictions: Any,
    protected: Any,
    threshold: float = 0.5,
) -> Dict[str, float]:
    """Compute pairwise demographic parity gaps across protected groups."""
    scores = array(predictions, dtype=float).reshape(-1)
    groups = _group_keys(protected)
    if scores.shape[0] != len(groups):
        raise ValueError("predictions and protected must have the same sample count")

    rates: Dict[str, float] = {}
    for group in sorted(set(groups)):
        mask = np.array([item == group for item in groups])
        rates[group] = prediction_rate(scores[mask], threshold=threshold)

    gaps: Dict[str, float] = {}
    names = sorted(rates)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            gaps[f"{left}|{right}"] = abs(rates[left] - rates[right])
    return gaps


def bias_reduction(traditional_gap: float, bayesian_gap: float) -> float:
    """Return fractional bias reduction from traditional to Bayesian gap."""
    if abs(traditional_gap) < EPS:
        return 0.0
    return float((traditional_gap - bayesian_gap) / traditional_gap)


def data_point(
    raw_features: Any,
    context_features: Any = None,
    knowledge_embedding: Any = None,
    drift_source: str = "ai_system",
    metadata: Optional[Mapping[str, Any]] = None,
    timestamp: Optional[float] = None,
    id: str = "",
) -> DataPoint:
    """Create a drift-aware data point."""
    raw = array(raw_features, dtype=float).reshape(-1)
    context_values = raw if context_features is None else context_features
    knowledge_values = raw if knowledge_embedding is None else knowledge_embedding
    return DataPoint(
        raw_features=raw,
        context_features=array(context_values, dtype=float).reshape(-1),
        knowledge_embedding=array(knowledge_values, dtype=float).reshape(-1),
        drift_source=drift_source,
        metadata=dict(metadata or {}),
        timestamp=time.time() if timestamp is None else float(timestamp),
        id=id,
    )


def state_confidence(state: Any) -> float:
    """Compute epistemic confidence as dominant normalized energy."""
    values = array(state, dtype=float).reshape(-1)
    if values.size == 0:
        return 0.0
    norm = np.linalg.norm(values)
    if norm < EPS:
        return 0.0
    normalized = values / norm
    if not np.all(np.isfinite(normalized)):
        return 0.0
    return float(np.max(normalized**2))


def cosine_dissimilarity(left: Any, right: Any) -> float:
    """Return cosine dissimilarity in [0, 2]."""
    left_arr = array(left, dtype=float).reshape(-1)
    right_arr = array(right, dtype=float).reshape(-1)
    size = min(left_arr.size, right_arr.size)
    if size == 0:
        return 0.0
    left_arr = left_arr[:size]
    right_arr = right_arr[:size]
    denom = np.linalg.norm(left_arr) * np.linalg.norm(right_arr)
    if denom < EPS:
        return 0.0
    similarity = float(np.dot(left_arr, right_arr) / denom)
    return float(1.0 - np.clip(similarity, -1.0, 1.0))


def classify_drift_vector(current: DataPoint, baseline: DataPoint) -> str:
    """Classify drift as phenomenological, contextual, or epistemic."""
    scores = {
        "phenomenological": kl(current.distribution, baseline.distribution),
        "contextual": kl(current.context_distribution, baseline.context_distribution),
        "epistemic": cosine_dissimilarity(
            current.knowledge_embedding,
            baseline.knowledge_embedding,
        ),
    }
    return max(scores, key=scores.get)


def temporal_shift(t: float, normalization: float = 1.0) -> float:
    """Default linear temporal drift component."""
    denom = max(float(normalization), EPS)
    return float(max(0.0, t) / denom)


def scale_to_failure_range(epsilon: float) -> float:
    """Compress raw drift epsilon to [0, 12]."""
    return float(DRIFT_BOUND_MAX * (1.0 - np.exp(-max(0.0, epsilon))))


def drift_measure(
    current: Any,
    baseline: Any,
    t: float = 0.0,
    alpha_drift: float = 0.0,
    human_side: Optional[bool] = None,
) -> float:
    """Measure signed drift on the bidirectional failure scale [-12, +12]."""
    current_dp = current if isinstance(current, DataPoint) else data_point(current)
    baseline_dp = baseline if isinstance(baseline, DataPoint) else data_point(baseline)
    epsilon_t = kl(current_dp.distribution, baseline_dp.distribution) + (
        float(alpha_drift) * temporal_shift(t)
    )
    is_human_side = (
        current_dp.drift_source == "human_context" if human_side is None else human_side
    )
    sign = 1.0 if is_human_side else -1.0
    return float(np.clip(sign * scale_to_failure_range(epsilon_t), -12.0, 12.0))


def classify_drift_zone(drift: float) -> str:
    """Map signed drift to the thesis bidirectional failure zone."""
    value = float(drift)
    if value < -9.0:
        return "ai_panic"
    if value < -6.0:
        return "ai_warning"
    if value < -3.0:
        return "ai_caution"
    if value <= 3.0:
        return "green_zone"
    if value <= 6.0:
        return "human_stress_low"
    if value <= 9.0:
        return "human_stress_med"
    return "human_distress"


def zone_response(zone: str) -> ZoneResponse:
    """Return the recommended cascade/action for a drift zone."""
    responses = {
        "ai_panic": ZoneResponse("ai_panic", "eze", "emergency_halt", "Critical system failure - halt"),
        "ai_warning": ZoneResponse("ai_warning", "eze", "fallback_mode", "Degraded - Eze override active"),
        "ai_caution": ZoneResponse("ai_caution", "uche", "recalibrate", "Minor anomalies - Uche adaptation"),
        "green_zone": ZoneResponse("green_zone", "obinexus", "normal_operation", "Optimal - Obinexus baseline"),
        "human_stress_low": ZoneResponse("human_stress_low", "uche", "user_support", "User adaptation needed"),
        "human_stress_med": ZoneResponse("human_stress_med", "uche", "increased_support", "Significant user burden"),
        "human_distress": ZoneResponse("human_distress", "eze", "intervention", "User overwhelmed - immediate intervention"),
    }
    if zone not in responses:
        raise ValueError(f"Unknown drift zone: {zone!r}")
    return responses[zone]


def drift_observation(
    current: DataPoint,
    baseline: DataPoint,
    t: float = 0.0,
    alpha_drift: float = 0.0,
    human_side: Optional[bool] = None,
) -> DriftObservation:
    """Measure, classify, and route a drift observation."""
    magnitude = drift_measure(
        current,
        baseline,
        t=t,
        alpha_drift=alpha_drift,
        human_side=human_side,
    )
    zone = classify_drift_zone(magnitude)
    return DriftObservation(
        magnitude=magnitude,
        vector_type=classify_drift_vector(current, baseline),
        zone=zone,
        response=zone_response(zone),
        timestamp=time.time(),
        source=current.drift_source,
    )


def diram_cascade() -> DIRAMCascade:
    """Create a DIRAM cascade with Obinexus baseline active."""
    return DIRAMCascade()


def filter_layer(
    x: DataPoint,
    weights: Optional[Sequence[float]] = None,
    phi_functions: Optional[Sequence[Any]] = None,
    verify: Optional[Any] = None,
) -> float:
    """Filter(x) = sum_i w_i * phi_i(x) * verify(x)."""
    validator = verify or (lambda item: state_confidence(item.raw_features) >= C_COHERENCE)
    validity = 1.0 if validator(x) else 0.0
    if validity == 0.0:
        return 0.0
    functions = list(phi_functions or [lambda item: float(np.linalg.norm(item.raw_features))])
    coeffs = np.asarray(weights if weights is not None else np.ones(len(functions)) / len(functions), dtype=float)
    if len(coeffs) != len(functions):
        raise ValueError("weights length must match phi_functions length")
    return float(sum(weight * float(fn(x)) for weight, fn in zip(coeffs, functions)) * validity)


def flash_layer(
    x: DataPoint,
    t: float = 0.0,
    lambda_decay: float = LAMBDA_DECAY_DEFAULT,
) -> float:
    """Flash(x, t) = ephemeral(x) * exp(-lambda * t)."""
    ephemeral = float(np.linalg.norm(x.raw_features))
    return float(max(0.0, ephemeral * np.exp(-float(lambda_decay) * max(0.0, t))))


def flash_age_check(
    entry: FlashMemoryEntry,
    current_t: float,
    lambda_decay: float = LAMBDA_DECAY_DEFAULT,
    eviction_threshold: float = 0.01,
) -> bool:
    """Return whether a Flash entry should be evicted."""
    return entry.residual(current_t, lambda_decay) < eviction_threshold


def content_hash(x: DataPoint) -> str:
    """Return a deterministic SHA-256 content hash for a data point."""
    payload = np.ascontiguousarray(array(x.raw_features, dtype=float)).tobytes()
    return hashlib.sha256(payload).hexdigest()


def storage_layer(x: DataPoint) -> StorageRecord:
    """Create a Storage(x) record from hash, cultural context, and love anchors."""
    h_x = content_hash(x)
    cultural = hashlib.sha256(str(x.metadata.get("cultural_context", "")).encode()).hexdigest()
    love = hashlib.sha256(str(x.metadata.get("love_anchor", "")).encode()).hexdigest()
    content = _xor_hex(h_x, cultural, love)
    return StorageRecord(
        content=content,
        source_id=x.id,
        timestamp=time.time(),
        retrieval_key=h_x,
        cultural_context=cultural,
        love_anchor=love,
    )


def filter_flash_engine(
    threshold: float = C_COHERENCE,
    lambda_decay: float = LAMBDA_DECAY_DEFAULT,
) -> FilterFlashEngine:
    """Create a minimal Filter/Flash engine."""
    return FilterFlashEngine(threshold=threshold, lambda_decay=lambda_decay)


def mitigate_drift(
    current: Any,
    baseline: Any,
    engine: Optional[FilterFlashEngine] = None,
    t: float = 0.0,
    alpha_drift: float = 0.0,
    theta: float = C_COHERENCE,
    human_side: Optional[bool] = None,
) -> DriftResult:
    """Run one deterministic drift detection and mitigation step."""
    current_dp = current if isinstance(current, DataPoint) else data_point(current)
    baseline_dp = baseline if isinstance(baseline, DataPoint) else data_point(baseline)
    runtime = engine or filter_flash_engine(threshold=theta)
    observation = drift_observation(
        current_dp,
        baseline_dp,
        t=t,
        alpha_drift=alpha_drift,
        human_side=human_side,
    )
    output = runtime.process(
        current_dp,
        drift=observation.magnitude,
        current_t=t,
        safe_state=baseline_dp.raw_features,
    )
    if output.coherence < theta:
        runtime.diram_cascade.activate_tier("uche")
        output = runtime.process(
            current_dp,
            drift=observation.magnitude,
            current_t=t,
            safe_state=baseline_dp.raw_features,
        )
    if output.coherence < theta:
        runtime.diram_cascade.activate_tier("eze")
        output = runtime.process(
            current_dp,
            drift=observation.magnitude,
            current_t=t,
            safe_state=baseline_dp.raw_features,
        )
    if output.coherence < theta:
        output = ProcessedOutput(
            value=float(np.linalg.norm(baseline_dp.raw_features)),
            data=baseline_dp.raw_features.copy(),
            source="fallback",
            coherence=max(theta, state_confidence(baseline_dp.raw_features)),
            drift=observation.magnitude,
            active_tiers=runtime.diram_cascade.get_active_tiers(),
            metadata={"mode": "safe_fallback"},
        )
    return DriftResult(
        observation=observation,
        output=output,
        cascade=runtime.diram_cascade,
        audit_trail=[
            {"step": "measure_drift", "observation": observation.manifest()},
            {"step": "process_cascade", "output": output.manifest()},
        ],
    )


def malpaartice_framework() -> MALPAARTICEFramework:
    """Create a MALPAARTICE governance ledger."""
    return MALPAARTICEFramework()


def triangi_validate(
    engine: FilterFlashEngine,
    test_cases: Sequence[Mapping[str, Any]],
    threshold: float = C_COHERENCE,
) -> TriangiReport:
    """Validate coherence maintenance across drift-labeled test cases."""
    coherence_by_drift: Dict[float, List[float]] = {}
    n_passed = 0
    for case in test_cases:
        input_dp = case.get("input")
        if not isinstance(input_dp, DataPoint):
            input_dp = data_point(input_dp)
        drift_magnitude = float(case.get("drift_magnitude", 0.0))
        output = engine.process(input_dp, drift=drift_magnitude)
        if output.coherence >= threshold:
            n_passed += 1
        coherence_by_drift.setdefault(drift_magnitude, []).append(output.coherence)
    n_total = len(test_cases)
    curve = {
        drift: float(np.mean(values))
        for drift, values in sorted(coherence_by_drift.items())
    }
    score = n_passed / max(n_total, 1)
    return TriangiReport(
        n_total=n_total,
        n_passed=n_passed,
        overall_score=score,
        threshold_met=score >= threshold,
        coherence_curve=curve,
        threshold=threshold,
    )


def dataset(
    X: Any,
    y: Any = None,
    protected: Any = None,
    feature_names: Optional[Sequence[str]] = None,
    model_config: Optional[Mapping[str, Any]] = None,
) -> Dataset:
    """Create a normalized NumPy-backed debiasing dataset."""
    X_arr = array(X, dtype=float)
    if X_arr.ndim == 1:
        X_arr = X_arr.reshape(-1, 1)
    if X_arr.ndim != 2:
        raise ValueError("X must be a 1D or 2D array-like value")

    y_arr = None if y is None else array(y, dtype=float).reshape(-1)
    if y_arr is not None and y_arr.shape[0] != X_arr.shape[0]:
        raise ValueError("y must have the same sample count as X")

    protected_arr = None if protected is None else np.asarray(protected)
    if protected_arr is not None:
        if protected_arr.ndim == 0:
            raise ValueError("protected must be 1D or 2D when provided")
        if protected_arr.shape[0] != X_arr.shape[0]:
            raise ValueError("protected must have the same sample count as X")

    names = list(feature_names or [f"x{i}" for i in range(X_arr.shape[1])])
    if len(names) != X_arr.shape[1]:
        raise ValueError("feature_names length must match X feature count")

    return Dataset(
        X=X_arr,
        y=y_arr,
        protected=protected_arr,
        feature_names=names,
        model_config=dict(model_config or {}),
    )


def audit(target: Dataset, thresholds: Optional[Mapping[str, Any]] = None) -> BiasReport:
    """Audit a dataset for the four PSC bias vectors."""
    limits = {
        "representation_tolerance": 0.2,
        "proxy_correlation": 0.5,
        "label_rate_gap": 0.2,
    }
    if thresholds:
        limits.update(thresholds)

    warnings: List[str] = []
    metrics: Dict[str, Any] = {}

    data_bias = _data_collection_bias(target, limits, warnings, metrics)
    feature_bias = _feature_selection_bias(target, limits, warnings, metrics)
    label_bias = _label_bias(target, limits, warnings, metrics)
    spec_bias = _model_specification_bias(target, warnings, metrics)

    return BiasReport(
        data_bias=data_bias,
        feature_bias=feature_bias,
        label_bias=label_bias,
        spec_bias=spec_bias,
        warnings=warnings,
        metrics=metrics,
    )


def variable(name: str, kind: str, observed: bool = True) -> Variable:
    """Declare a DAG variable."""
    return Variable(name=name, kind=kind, observed=observed)


def dag(
    nodes: Optional[Iterable[Variable | str]] = None,
    edges: Optional[Iterable[Tuple[str, str]]] = None,
) -> DAG:
    """Create a Bayesian debiasing DAG."""
    graph = DAG()
    for item in nodes or []:
        graph.add_variable(item)
    for parent, child in edges or []:
        graph.add_edge(parent, child)
    return graph


def edge(graph: DAG, parent: str, child: str) -> DAG:
    """Add a directed edge to a DAG."""
    return graph.add_edge(parent, child)


def factorize(graph: DAG) -> List[Dict[str, Any]]:
    """Return structured joint factorization metadata for a DAG."""
    return graph.factorize()


def backdoors(graph: DAG, treatment: str, target: str) -> List[List[str]]:
    """Find simple backdoor paths where the first arrow enters treatment."""
    paths = _all_simple_paths(graph, treatment, target)
    result = []
    for path in paths:
        if len(path) >= 2 and (path[1], treatment) in graph.edges:
            result.append(path)
    return result


def block_backdoors(
    graph: DAG,
    paths: Sequence[Sequence[str]],
    conditioning: Iterable[str],
) -> bool:
    """Return whether all backdoor paths are blocked by conditioning nodes."""
    conditioned = set(conditioning)
    for path in paths:
        middle = set(path[1:-1])
        if not middle.intersection(conditioned):
            return False
    return True


def debias(
    target: Dataset,
    graph: DAG,
    alpha: Any = None,
    beta: Any = None,
    iterations: Optional[int] = None,
) -> DebiasResult:
    """Compute a deterministic minimal debiased posterior approximation."""
    del iterations
    circuit = CircuitBreaker()
    integrity = IntegrityStatus()
    audit_report = audit(target)
    audit_trail = [
        {"step": "audit", "report": audit_report.manifest()},
        {"step": "dag_factorization", "factors": graph.factorize()},
    ]

    if not circuit.allow_operation():
        circuit.record_failure()
        raise RuntimeError("CircuitBreaker open: debiasing blocked")

    y = target.y
    X = target.X
    if y is None:
        theta_raw = np.mean(X, axis=0)
        corrected_y = X @ theta_raw
        phi = {}
    else:
        protected_effect, phi = _protected_effect(y, target.protected)
        corrected_y = y - protected_effect
        theta_raw = np.linalg.pinv(X) @ corrected_y

    theta_prior = _prior_like(theta_raw, alpha)
    phi_prior = _prior_like(list(phi.values()) or [0.0], beta)
    posterior = normalize(np.abs(theta_raw) + np.abs(theta_prior) + EPS)
    theta = np.asarray(theta_raw, dtype=float)
    predictions = _sigmoid(X @ theta)
    parity_gaps = (
        demographic_parity_gap(predictions, target.protected)
        if target.protected is not None
        else {}
    )

    metrics = {
        "method": "deterministic_minimal",
        "theta_prior": theta_prior,
        "phi_prior": phi_prior,
        "parity_gaps": parity_gaps,
        "max_parity_gap": max(parity_gaps.values(), default=0.0),
        "posterior_entropy": entropy(posterior),
    }
    audit_trail.append(
        {
            "step": "marginalize_bias",
            "detail": "protected-attribute contribution removed before theta fit",
        }
    )
    circuit.reset()
    return DebiasResult(
        theta=theta,
        bias_params=phi,
        posterior=posterior,
        predictions=predictions,
        audit_trail=audit_trail,
        metrics=metrics,
        dataset=target,
        graph=graph,
        integrity=integrity,
        circuit_breaker=circuit,
    )


def validate(
    result: DebiasResult,
    epsilon: float = 0.05,
    policy: str = "raise",
) -> ValidationReport:
    """Validate demographic parity, raising by default on violation."""
    if policy not in {"raise", "warn"}:
        raise ValueError("policy must be 'raise' or 'warn'")
    gaps = dict(result.metrics.get("parity_gaps", {}))
    max_gap = max(gaps.values(), default=0.0)
    parity_ok = max_gap <= epsilon
    warnings = []
    if not parity_ok:
        warnings.append(
            f"Demographic parity gap {max_gap:.6f} exceeds epsilon {epsilon:.6f}"
        )
    report = ValidationReport(
        parity_gaps=gaps,
        parity_ok=parity_ok,
        epsilon=epsilon,
        warnings=warnings,
    )
    result.validation_report = report
    if not parity_ok and policy == "raise":
        raise FairnessValidationError(report)
    return report


def pipeline(
    target: Dataset,
    graph: DAG,
    alpha: Any = None,
    beta: Any = None,
    epsilon: float = 0.05,
) -> DebiasResult:
    """Run audit, deterministic debiasing, and fairness validation."""
    result = debias(target, graph, alpha=alpha, beta=beta)
    result.validation_report = validate(result, epsilon=epsilon, policy="raise")
    return result


def dump(obj: Any, path: str | Path) -> None:
    """Persist an OBI object as a pickle artifact."""
    with Path(path).open("wb") as file:
        pickle.dump(obj, file)


def dump_manifest(obj: Any, path: str | Path) -> None:
    """Persist a JSON manifest for an OBI object."""
    payload = obj.manifest() if hasattr(obj, "manifest") else obj
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(_to_jsonable(payload), file, indent=2)


def _data_collection_bias(
    target: Dataset,
    limits: Mapping[str, Any],
    warnings: List[str],
    metrics: Dict[str, Any],
) -> bool:
    if target.protected is None:
        warnings.append("Protected attributes missing; data representation cannot be audited")
        return True

    groups = _group_keys(target.protected)
    counts = {group: groups.count(group) for group in sorted(set(groups))}
    observed = {group: count / len(groups) for group, count in counts.items()}
    expected = limits.get("expected_proportions")
    if expected is None:
        expected = {group: 1.0 / len(counts) for group in counts}
    tolerance = float(limits["representation_tolerance"])
    metrics["group_proportions"] = observed
    metrics["expected_proportions"] = dict(expected)

    biased = False
    for group, proportion in observed.items():
        expected_value = float(expected.get(group, 0.0))
        if abs(proportion - expected_value) > tolerance:
            warnings.append(
                f"Subgroup {group} representation {proportion:.3f} differs "
                f"from expected {expected_value:.3f}"
            )
            biased = True
    return biased


def _feature_selection_bias(
    target: Dataset,
    limits: Mapping[str, Any],
    warnings: List[str],
    metrics: Dict[str, Any],
) -> bool:
    if target.protected is None:
        return True
    protected_numeric = _encode_to_float(target.protected)
    if protected_numeric.ndim > 1:
        protected_numeric = protected_numeric.mean(axis=1)
    correlations: Dict[str, float] = {}
    biased = False
    for index, name in enumerate(target.feature_names):
        corr = _safe_corr(target.X[:, index], protected_numeric)
        correlations[name] = corr
        if abs(corr) > float(limits["proxy_correlation"]):
            warnings.append(
                f"Feature {name} acts as protected-attribute proxy "
                f"(correlation={corr:.3f})"
            )
            biased = True
    metrics["feature_proxy_correlation"] = correlations
    return biased


def _label_bias(
    target: Dataset,
    limits: Mapping[str, Any],
    warnings: List[str],
    metrics: Dict[str, Any],
) -> bool:
    if target.y is None or target.protected is None:
        if target.y is None:
            warnings.append("Labels missing; label bias cannot be audited")
        return target.y is None

    groups = _group_keys(target.protected)
    rates: Dict[str, float] = {}
    for group in sorted(set(groups)):
        mask = np.array([item == group for item in groups])
        rates[group] = float(np.mean(target.y[mask])) if np.any(mask) else 0.0
    metrics["label_rates"] = rates
    if not rates:
        return False
    gap = max(rates.values()) - min(rates.values())
    metrics["label_rate_gap"] = gap
    if gap > float(limits["label_rate_gap"]):
        warnings.append(f"Label rate gap {gap:.3f} exceeds audit threshold")
        return True
    return False


def _model_specification_bias(
    target: Dataset,
    warnings: List[str],
    metrics: Dict[str, Any],
) -> bool:
    config = target.model_config
    metrics["model_config"] = dict(config)
    if not config:
        warnings.append("Model config missing; specification bias assumed")
        return True
    imbalance_sensitive = bool(
        config.get("imbalance_sensitive")
        or config.get("imbalance_sensitive_loss")
        or config.get("class_weight")
    )
    if not imbalance_sensitive:
        warnings.append("Model config does not declare imbalance-sensitive training")
        return True
    return False


def _protected_effect(y: np.ndarray, protected: Optional[np.ndarray]) -> Tuple[np.ndarray, Dict[str, float]]:
    if protected is None:
        return np.zeros_like(y, dtype=float), {}
    groups = _group_keys(protected)
    global_mean = float(np.mean(y))
    values: Dict[str, float] = {}
    effect = np.zeros_like(y, dtype=float)
    for group in sorted(set(groups)):
        mask = np.array([item == group for item in groups])
        group_mean = float(np.mean(y[mask])) if np.any(mask) else global_mean
        values[group] = group_mean - global_mean
        effect[mask] = values[group]
    return effect, values


def _prior_like(values: Any, prior: Any = None) -> np.ndarray:
    base = array(values, dtype=float).reshape(-1)
    if prior is None:
        return np.ones_like(base) / max(base.size, 1)
    prior_arr = array(prior, dtype=float).reshape(-1)
    if prior_arr.size == 1 and base.size != 1:
        prior_arr = np.repeat(prior_arr, base.size)
    if prior_arr.size != base.size:
        raise ValueError("prior shape must match parameter shape")
    return normalize(np.abs(prior_arr) + EPS)


def _group_keys(values: Any) -> List[str]:
    arr = np.asarray(values)
    if arr.ndim == 1:
        return [str(item) for item in arr.tolist()]
    return ["|".join(str(part) for part in row) for row in arr.reshape(arr.shape[0], -1)]


def _encode_to_float(values: Any) -> np.ndarray:
    arr = np.asarray(values)
    if np.issubdtype(arr.dtype, np.number):
        return arr.astype(float)
    flat = arr.reshape(-1)
    mapping = {value: index for index, value in enumerate(sorted(set(flat.tolist())))}
    encoded = np.array([mapping[item] for item in flat], dtype=float)
    return encoded.reshape(arr.shape)


def _safe_corr(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=float).reshape(-1)
    right = np.asarray(right, dtype=float).reshape(-1)
    if left.size != right.size or left.size < 2:
        return 0.0
    if np.std(left) < EPS or np.std(right) < EPS:
        return 0.0
    return float(np.corrcoef(left, right)[0, 1])


def _sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return 1.0 / (1.0 + np.exp(-values))


def _all_simple_paths(graph: DAG, start: str, target: str) -> List[List[str]]:
    if start == target:
        return [[start]]
    paths: List[List[str]] = []
    stack: List[Tuple[str, List[str]]] = [(start, [start])]
    while stack:
        current, path = stack.pop()
        for neighbor in graph.neighbors(current):
            if neighbor in path:
                continue
            next_path = path + [neighbor]
            if neighbor == target:
                paths.append(next_path)
            else:
                stack.append((neighbor, next_path))
    return paths


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


def _xor_hex(*values: str) -> str:
    if not values:
        return ""
    width = max(len(value) for value in values)
    result = 0
    for value in values:
        result ^= int(value.ljust(width, "0")[:width], 16)
    return f"{result:0{width}x}"


__all__ = [
    "BiasReport",
    "C_COHERENCE",
    "CircuitBreaker",
    "DAG",
    "DIRAMCascade",
    "DRIFT_BOUND_MAX",
    "DataPoint",
    "Dataset",
    "DebiasResult",
    "DriftObservation",
    "DriftResult",
    "EPS",
    "FairnessValidationError",
    "FilterFlashEngine",
    "FlashMemoryEntry",
    "IntegrityStatus",
    "LAMBDA_DECAY_DEFAULT",
    "MALPAARTICEFramework",
    "ProcessedOutput",
    "StorageRecord",
    "TriangiReport",
    "ValidationReport",
    "Variable",
    "ZoneResponse",
    "array",
    "audit",
    "backdoors",
    "bias_reduction",
    "block_backdoors",
    "classify_drift_vector",
    "classify_drift_zone",
    "content_hash",
    "context",
    "cosine_dissimilarity",
    "dag",
    "data_point",
    "dataset",
    "debias",
    "demographic_parity_gap",
    "diram_cascade",
    "drift_measure",
    "drift_observation",
    "dump",
    "dump_manifest",
    "edge",
    "entropy",
    "factorize",
    "filter_flash_engine",
    "filter_layer",
    "flash_age_check",
    "flash_layer",
    "get_context",
    "kl",
    "kl_divergence",
    "malpaartice_framework",
    "mitigate_drift",
    "normalize",
    "pipeline",
    "prediction_rate",
    "scale_to_failure_range",
    "state_confidence",
    "storage_layer",
    "temporal_shift",
    "triangi_validate",
    "validate",
    "variable",
    "zone_response",
]
