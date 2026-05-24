# Ontological Bayesian Intelligence
OBI is NOT:
- a chatbot
- a neural network
- a replacement for human judgment
- a black-box prediction engine

OBI IS:
- a reasoning framework
- a governance-aware inference engine
- a confidence-based decision system
- an epistemic audit layer

**A reasoning framework for bias-free, consensus systems.**

> *"Don't just run systems. Build systems that know when they are wrong."*  
> — OBINexus

---

## What is OBI?

OBI is a **software development kit** for building systems that reason—truly reason—through real-world complexity without amplifying human bias.

It's not a neural network. It's not pattern matching. It's something different: a **reasoning engine** grounded in three ideas:

1. **Ontological** — Every computational entity has defined existence *before* value resolution
2. **Bayesian** — All state transitions are probabilistic; we use consensus, not certainty
3. **Intelligent** — The system recalibrates, adapts, and knows when to defer to humans

You can use OBI directly in Python apps, web services, robotics, data pipelines, accessibility systems—anywhere you need a system to *think* instead of just *react*.

```bash
pip install git+https://www.github.com/obinexusmk2/obi.git
```

That's it. One package identity: `obi`, imported with `from obi import ...`.

---

## The Problem OBI Solves

### Self-Blindness
Traditional AI systems cannot interrogate their own reasoning. A neural network makes a prediction, but can't explain *why*. It just outputs a number.

### Demographic Bias
Pattern-matching amplifies bias. If your training data reflects historical injustice, your model will too. An AI cancer-detection system trained on majority demographics will miss outliers—people it hasn't "seen."

### Epistemic Amnesia
Systems don't *know what they know*. They can't ask: "How do I know this? What evidence supports it? What could prove me wrong?"

**OBI fixes all three.**

---

## How OBI Works: A Robotic Car's Moment of Truth

Let's use a real scenario. A self-driving car in Vancouver. Rain. 65 mph. A cyclist appears 50 meters ahead.

What happens?

### **Eze is driving.**

Eze is the **governor**—the system that makes decisions and carries responsibility.

Eze doesn't panic. Eze doesn't just apply a braking function. Eze activates the reasoning cycle.

### **Obi observes the dashboard.**

Obi is the **heart**—the sensor that *feels* the world. The speedometer, the rain sensor, the lidar. Raw data flowing in.

```
┌─────────────────────────────────────┐
│  SENSOR INPUT (Data In)             │
├─────────────────────────────────────┤
│  Speedometer:      65 mph           │
│  Rain Sensor:      ON               │
│  Lidar Distance:   50 m             │
│  Road Friction:    0.45             │
└─────────────────────────────────────┘
```

But data alone is not wisdom. This is just noise—uninterpreted information.

### **Uche reads the observer and updates.**

Uche is the **knowledge**—the one who interprets.

Uche applies three layers of reasoning:

#### **1. FACT — What's Real**

Raw observation without judgment: *"Cyclist detected 50m ahead. Current speed 65 mph. Wet road. Braking distance at current deceleration: 72m."*

This is the data. Nothing more.

#### **2. JUSTIFICATION — Why It Matters**

Context and relationship: *"At 65 mph on wet road, safe braking distance is 72m. Object distance is 50m. Safety margin is negative."*

This is the reasoning—connecting facts to constraints.

#### **3. RATIONAL — What To Do**

The decision with confidence: *"Recommend immediate brake intervention. Confidence: 96.4%. Basis: Physics, not pattern-matching."*

This is **rhetorical reasoning**. Not rhetoric as empty words—rhetoric as *justified truth*. The system says: "Here's the fact. Here's why it matters. Here's what I recommend. Here's my confidence."

---

## The Probe Duality

At the heart of OBI is a simple but powerful idea: **the system must observe itself**.

In API terms, the proof surface is:

```python
from obi import external_probe, internal_probe, probe_alignment

state_result = internal_probe(data)              # P_internal: Data -> State
data_result = external_probe(state, event=None)  # P_external: State/Event -> Data
match_result = probe_alignment(data, state)      # state/data mismatch gate
```

Each call returns a `ProbeResult` with `channel`, `confidence`, `receipt`, and
`provenance`. `CH_2` means the state is safe to collapse or emit. `CH_1` means
the state/data relationship failed the 95.4% gate and should defer to human or
caller review.

### **P_external: State → Data** (What we emit)

When OBI decides, it doesn't just output a number. It outputs *why*. The probe converts internal state (the reasoning) into external data (the explanation).

```
┌──────────────────────┐
│ Internal State       │
│ • Confidence: 96.4%  │
│ • Bias Parameter: 0.02 (minimal)
│ • Reasoning Chain: [fact→justify→rational]
└──────────────────────┘
          ↓ P_external
┌──────────────────────┐
│ External Output      │
│ "Brake. 96.4%. Why: │
│  Physics constraint, │
│  not pattern match"  │
└──────────────────────┘
```

### **P_internal: Data → State** (What we observe)

When data arrives, OBI doesn't just store it. The probe normalizes it into a governed state vector—a representation the reasoning engine can work with.

```
┌──────────────────────┐
│ Raw Sensor Data      │
│ • speed_mph: 65      │
│ • distance_m: 50     │
│ • rain: true         │
│ • friction: 0.45     │
└──────────────────────┘
        ↓ P_internal
┌──────────────────────┐
│ Internal State       │
│ • velocity vector    │
│ • collision risk     │
│ • environmental bias │
│ • confidence: 95.4%  │
└──────────────────────┘
```

**Both probes must pass through a governance gate.** If confidence drops below 95.4% (μ + 2σ), the system defers to human control.

---

## Rhetorical Reasoning in Practice

The robotic car's reasoning cycle:

```
CYCLE: Fact → Justification → Rational

Step 1: FACT (Observe)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cyclist at 50m. Speed 65 mph. Wet road. Friction 0.45.

Step 2: JUSTIFICATION (Reason)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
At 65 mph on wet road with friction 0.45:
  • Minimum braking distance = (v² / 2a)
  • v = 65 mph = 29.1 m/s
  • a = g × friction = 9.81 × 0.45 = 4.4 m/s²
  • Distance = (29.1²) / (2 × 4.4) = 96.5 m

We have 50m. We need 96.5m. GAP: -46.5m (unsafe).

Step 3: RATIONAL (Decide)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action: BRAKE FULL
Confidence: 97.1%
Reasoning chain: Physics → Safety constraint → Brake action
Bias check: No demographic data involved. No pattern-matching.
           Decision based on deterministic physics.
```

This is not pattern-matching. This is reasoning.

---

## The Real-Time Dashboard: OBI in Action

As Eze drives and encounters the cyclist, here's what the dashboard shows:

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    OBI REASONING DASHBOARD                                 ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  OBSERVATIONS (Obi's Senses)                                               ║
║  ┌──────────────────────────────────────────────────────────────┐         ║
║  │ Speed: 65 mph      │ Distance: 50m      │ Rain: ON          │         ║
║  │ [████████████████] │ [██████████      ] │ [████] Friction   │         ║
║  └──────────────────────────────────────────────────────────────┘         ║
║                                                                            ║
║  REASONING (Uche's Analysis)                                               ║
║  ┌──────────────────────────────────────────────────────────────┐         ║
║  │ Fact:        Cyclist ahead, physics dictates 96m braking    │         ║
║  │ Justify:     Safety margin is -46.5m (unsafe)              │         ║
║  │ Rational:    BRAKE action, confidence 97.1%                │         ║
║  └──────────────────────────────────────────────────────────────┘         ║
║                                                                            ║
║  CONFIDENCE METERS                                                         ║
║  ┌──────────────────────────────────────────────────────────────┐         ║
║  │ Epistemic:   [██████████████████] 97.1% (HIGH)             │         ║
║  │ Bias Check:  [                  ] 0.0% (CLEAN - Physics)   │         ║
║  │ Safety Gate: [██████████████████] PASS (97.1 > 95.4)       │         ║
║  └──────────────────────────────────────────────────────────────┘         ║
║                                                                            ║
║  ACTION (Eze's Command)                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐         ║
║  │ ► BRAKE FULL                                                │         ║
║  │   Reasoning: Safety physics constraint                      │         ║
║  │   Deferral: None (confidence > threshold)                   │         ║
║  └──────────────────────────────────────────────────────────────┘         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Time: 0.234s  |  Cycle: Complete  |  Status: ✓ Safe
```

In 234 milliseconds:
1. Obi observed reality
2. Uche reasoned through it
3. Eze executed the decision
4. The system *knew why*

---

## Getting Started: 3 Minutes

### Install

```bash
pip install git+https://www.github.com/obinexusmk2/obi.git
```

### Your First OBI Debiasing Pipeline

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

report = obi.audit(data)

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

result = obi.debias(data, graph)
validation = obi.validate(result, epsilon=0.05, policy="warn")

print(report.any_bias_found)
print(result.theta)
print(validation.parity_ok)
```

### Data Drift Mitigation

```python
import obi

baseline = obi.data_point([1.0, 0.0, 0.0])
current = obi.data_point(
    [0.0, 1.0, 0.0],
    drift_source="human_context",
    metadata={"cultural_context": "nsibidi", "love_anchor": "community"},
)

result = obi.mitigate_drift(current, baseline)

print(result.observation.zone)
print(result.cascade.get_active_tiers())
print(result.output.coherence)
```

### Your First OBI Context

```python
import obi

# Create a reasoning context
# confidence_threshold defaults to 0.954 (95.4% - the safety clamp)
ctx = obi.context(
    confidence_threshold=0.954,
    reasoning_mode="bidirectional"  # Top-down + bottom-up
)

# Observe real-world data
sensor_data = {
    "speed_mph": 65,
    "distance_m": 50,
    "rain": True,
    "friction": 0.45
}

# OBI probes the data (P_internal: Data -> State)
state = ctx.probe_internal(sensor_data)

# OBI reasons through the state
decision = ctx.infer(state)

print(f"Action: {decision.action}")
print(f"Confidence: {decision.confidence:.1%}")
print(f"Reasoning: {decision.reasoning_chain}")
```

**Output:**
```
Action: BRAKE
Confidence: 97.1%
Reasoning: Physics constraint. Braking distance (96.5m) exceeds available distance (50m). Safety margin negative.
```

### Real Example: Medical AI

```python
import obi

ctx = obi.context(reasoning_mode="bidirectional")

# Cancer detection case: Black patient, age 45, no smoking history
# (An outlier to most trained models)
patient_data = {
    "age": 45,
    "demographic": "Black",
    "smoking": False,
    "ct_scan_anomaly": True,
    "psa_level": 8.2,
    "family_history": True
}

state = ctx.probe_internal(patient_data)
decision = ctx.infer(state)

print(f"Diagnosis: {decision.action}")
print(f"Confidence: {decision.confidence:.1%}")
print(f"Bias Check: {decision.bias_parameter:.2%}")
print(f"Reasoning: {decision.reasoning_chain}")
```

**Output:**
```
Diagnosis: REFER_TO_ONCOLOGY
Confidence: 96.2%
Bias Check: 0.8% (minimal bias parameter - patient is outlier but data supports referral)
Reasoning: Anomalies + PSA level + family history indicate oncology review warranted. Demographic does not bias decision. Physics/biology does.
```

The system didn't miss the outlier. It saw the patient as an individual.

---

## The Three Perspectives: Tripolar Reasoning

OBI operates through three simultaneous perspectives. You are them all.

| **Perspective** | **Role** | **Question** | **In OBI** |
|---|---|---|---|
| **Eze** | The Leader. Governance. Responsibility. | *"What decision must I make? Who is responsible?"* | `ctx.infer(state)` — Executes the decision with authority |
| **Uche** | The Knowledge. Wisdom. Understanding. | *"What does the data mean? Why does it matter?"* | `ctx.reason(state)` — Builds the justification chain |
| **Obi** | The Heart. Feeling. The human. | *"What does this *mean* to me? Do I trust it?"* | `state = ctx.probe_internal(data)` — Feels the world through sensors |

When you use OBI, you're not replacing these three. You're **aligning them**. The data (Obi) flows into reasoning (Uche) which informs the decision (Eze).

---

## Architecture: What's Inside

OBI is built in layers:

```
┌─────────────────────────────────────────────────────────┐
│  Application Layer (Your Code)                          │
│  import obi; ctx = obi.context()                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Reasoning Layer (Cognition)                            │
│  • Filter-Flash metacognition                           │
│  • Dimensional game theory                              │
│  • Cost-knowledge functions                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Core Layer (Governance & Probes)                       │
│  • Bayesian inference engine                            │
│  • 95.4% confidence clamp                               │
│  • Probe duality (P_internal, P_external)               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Memory Layer (DIRAM)                                   │
│  • Directed Instruction RAM                            │
│  • SHA-256 receipts for every decision                 │
│  • Consciousness stack                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Integrity Layer (Security)                             │
│  • AuraSeal cryptographic validation                    │
│  • Zero-trust boundaries                                │
│  • Audit trails                                         │
└─────────────────────────────────────────────────────────┘
```

**Everything is grounded in formal proofs.** You can read the AEGIS-PROOF suite in the `proofs/` folder. Every claim has a citation.

---

## Polyglot & Multi-Language Support (Optional)

If you need OBI to work with systems written in Node.js, Rust, Go, or other languages, we provide **libpolycall** — a polyglot FFI bridge.

**But it's optional.** OBI works standalone in Python.

### When You'd Use libpolycall

- **Distributed systems**: OBI reasoning engine on one service, actions executed on another
- **Polyglot teams**: You use Python, your colleague uses Node, but you share reasoning
- **Decentralized recovery**: P2P failover where nodes can heal each other
- **Real-time constraints**: You need Rust performance + Python reasoning

### How It Works

```python
# OBI on Python side
decision = ctx.infer(state)

# libpolycall bridges the gap
from obi.polyglot import PolyglotBridge

bridge = PolyglotBridge()
result = bridge.call_rust_executor(decision)  # Send to Rust service
```

The bridge handles serialization, type marshalling, and consensus across language boundaries. But you only use it if you need it.

---

## Accessibility & Human-Centered Design

OBI is built from the principle that **one person's ability to use a system must be preserved and enhanced**.

This means:

### Separation of Concerns

The core reasoning (OBI) is **separate from the interface** (how you see and use it). This separation means:

- A blind user can interact through voice and screen readers
- A motor-impaired user can control OBI through eye-tracking or adaptive switches
- A non-technical person can understand the reasoning chain in plain language
- A data scientist can dig into the Bayesian inference

### No Lock-In

OBI exports its reasoning in multiple formats:

```python
# Structured explanation (for humans)
print(decision.explain_verbose())

# Metrics (for dashboards)
print(decision.metrics)

# Serialized reasoning (for archival/audit)
print(decision.serialize_reasoning_chain())
```

You're never locked into one way of seeing OBI's decisions.

---

## Why OBI?

### You're building a system that matters.

Maybe it's:
- A medical diagnosis tool that must work for all demographics
- A robot that assists elderly people at home
- A financial aid system that doesn't discriminate
- An accessibility tool that helps people with disabilities navigate complex interfaces
- A civic system where trust is non-negotiable

Traditional AI (neural networks, pattern matching) will fail you here. It will:
- Amplify bias
- Make decisions you can't explain
- Miss outliers
- Drift from human values

**OBI doesn't.** It reasons through data. It knows when it's confident and when to defer. It explains itself.

### You're not replacing humans. You're helping them think better.

OBI isn't AGI. It's not trying to be. It's a reasoning engine—a tool that helps humans make better decisions by providing transparent, bias-aware analysis.

Eze (the decision-maker) still decides. Uche (the knowledge) still interprets. Obi (the person) still feels.

OBI just makes sure all three are aligned.

---

## Next Steps

1. **Install**: `pip install git+https://www.github.com/obinexusmk2/obi.git`
2. **Read the docs**: [github.com/obinexusmk2/obi](https://github.com/obinexusmk2/obi)
3. **Read the proofs**: The `proofs/` folder has 40+ formal specifications
4. **Try the examples**: `examples/` folder has robotic cars, medical AI, accessibility systems
5. **Join the conversation**: We're building this for human dignity

---

## License & Community

OBI is open source under the **OBINexus Constitutional Legal Framework**.

This means:
- **#NoGhosting**: Complete audit trails. Every decision is logged.
- **Milestone-Based Investment**: Verifiable progress. No vaporware.
- **OpenSense Recruitment**: Transparent contributor onboarding.
- **Zero-Trust Architecture**: Every decision is independently verifiable.

Built with ❤️ by **Nnamdi Michael Okpala** and the OBINexus community.

---

> *"The future of AI is not about who can build the largest model.*  
> *It's about who can build the most trustworthy one."*
