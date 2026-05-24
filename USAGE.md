# OBI Usage Guide

This guide shows the public `import obi` API for the current OBI SDK.

OBI has three practical entry points:

- Bayesian debiasing: audit a dataset, declare a DAG, debias, validate fairness.
- Data drift mitigation: measure drift, route through Filter/Flash, escalate DIRAM tiers.
- Legacy reasoning context: keep using `obi.context()` and probe/inference methods.

## Quick Import

```python
import obi
```

The top-level package is the API. Prefer `import obi` in examples and applications.

## Bayesian Debiasing Pipeline

Create a NumPy-backed dataset:

```python
import obi

data = obi.dataset(
    X=[
        [0.0, 1.0],
        [0.0, 0.9],
        [1.0, 0.2],
        [1.0, 0.1],
    ],
    y=[1, 1, 0, 0],
    protected=[0, 0, 1, 1],
    feature_names=["proxy_feature", "clinical_signal"],
    model_config={"imbalance_sensitive": True},
)
```

Audit for the four PSC bias vectors:

```python
report = obi.audit(data)

print(report.data_bias)
print(report.feature_bias)
print(report.label_bias)
print(report.spec_bias)
print(report.any_bias_found)
print(report.warnings)
```

Build the cancer-detection DAG from the PSC modules:

```python
graph = obi.dag(
    nodes=[
        obi.variable("S", "binary"),
        obi.variable("C", "binary"),
        obi.variable("T", "real"),
        obi.variable("A", "protected_set"),
        obi.variable("phi", "bias", observed=False),
        obi.variable("theta", "parameters", observed=False),
    ],
    edges=[
        ("S", "C"),
        ("A", "C"),
        ("A", "T"),
        ("C", "T"),
        ("phi", "T"),
        ("theta", "C"),
    ],
)

print(obi.factorize(graph))
```

Run deterministic minimal debiasing:

```python
result = obi.debias(data, graph)

print(result.theta)
print(result.bias_params)
print(result.metrics["method"])
print(result.audit_trail)
```

Validate demographic parity:

```python
validation = obi.validate(result, epsilon=0.05, policy="warn")

print(validation.parity_ok)
print(validation.parity_gaps)
print(validation.warnings)
```

By default, `obi.validate(result)` uses `policy="raise"` and raises
`obi.FairnessValidationError` when the demographic parity gap exceeds `epsilon`.

## Data Drift Mitigation

Create baseline and current data points:

```python
baseline = obi.data_point([1.0, 0.0, 0.0])
current = obi.data_point(
    [0.0, 1.0, 0.0],
    context_features=[0.3, 0.7],
    knowledge_embedding=[0.0, 1.0, 0.0],
    drift_source="human_context",
    metadata={
        "cultural_context": "nsibidi",
        "love_anchor": "community",
    },
)
```

Measure and classify drift:

```python
drift = obi.drift_measure(current, baseline)
zone = obi.classify_drift_zone(drift)
vector = obi.classify_drift_vector(current, baseline)
response = obi.zone_response(zone)

print(drift)
print(zone)
print(vector)
print(response.action)
```

Run one mitigation step:

```python
result = obi.mitigate_drift(current, baseline)

print(result.observation.zone)
print(result.observation.vector_type)
print(result.cascade.get_active_tiers())
print(result.output.source)
print(result.output.coherence)
```

The DIRAM cascade always starts with `obinexus`. It activates:

- `uche` when `abs(drift) > 3`
- `eze` when `abs(drift) > 6`

## Filter/Flash Engine

Use the engine directly when you want stateful Filter/Flash memory:

```python
engine = obi.filter_flash_engine()

high_confidence = obi.data_point([1000.0, 0.0, 0.0])
low_confidence = obi.data_point([1.0, 1.0, 1.0])

filter_output = engine.process(high_confidence)
flash_output = engine.process(low_confidence)

print(filter_output.source)
print(flash_output.source)
print(engine.manifest())
```

Filter mode is used when confidence is at least `obi.C_COHERENCE`, currently `0.954`.
Flash mode is used for low-confidence ephemeral working memory.

## MALPAARTICE Governance Ledger

The drift API includes a lightweight Monitoring, Auditing, Logging, Prevention ledger:

```python
framework = obi.malpaartice_framework()
drift_result = obi.mitigate_drift(current, baseline)

monitor_record = framework.monitor(drift_result)
audit_report = framework.audit()
trace = framework.log("drift_mitigation", drift_result.manifest())
prevention = framework.prevent(current_drift=4.0)

print(monitor_record)
print(audit_report)
print(trace["proof_ref"])
print(prevention)
```

## Triangi-Style Validation

Validate coherence maintenance across drift-labeled cases:

```python
engine = obi.filter_flash_engine()
cases = [
    {"input": obi.data_point([1000.0, 0.0]), "drift_magnitude": 0.0},
    {"input": obi.data_point([0.0, 1000.0]), "drift_magnitude": 12.0},
]

report = obi.triangi_validate(engine, cases)

print(report.overall_score)
print(report.threshold_met)
print(report.coherence_curve)
```

## Persistence

Use pickle for Python objects:

```python
obi.dump(result, "obi_result.pkl")
```

Use JSON manifests for audit-friendly records:

```python
obi.dump_manifest(result, "obi_result.json")
```

Do not load pickle files from untrusted sources.

## Legacy Reasoning Context

The older reasoning context remains supported:

```python
ctx = obi.context(confidence_threshold=0.954)

state = ctx.probe_internal({
    "speed_mph": 65,
    "distance_m": 50,
    "friction": 0.45,
    "obstacle": "cyclist",
})

decision = ctx.infer(state)

print(decision.action)
print(decision.confidence)
print(decision.reasoning_chain)
```

The low-level probe API is also still exported:

```python
state_result = obi.internal_probe([1000.0, 0.0, 0.0])
data_result = obi.external_probe(state_result.state)
alignment = obi.probe_alignment([1000.0, 0.0, 0.0], state_result.state)
```

## Current Scope

This API is intentionally lightweight:

- Uses NumPy and the Python standard library.
- Does not implement full MCMC sampling yet.
- Keeps deterministic minimal debiasing runnable for tests and demos.
- Keeps drift mitigation deterministic and inspectable.
- Prioritizes audit trails, explicit metadata, and stable public names.
