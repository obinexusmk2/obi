"""PSC-aligned tests for the public Bayesian debiasing API."""

import numpy as np
import pytest

import obi


def biased_dataset():
    return obi.dataset(
        X=[
            [0.0, 1.0],
            [0.0, 0.9],
            [0.0, 0.8],
            [0.0, 0.7],
            [1.0, 0.1],
            [1.0, 0.2],
        ],
        y=[1, 1, 1, 1, 0, 0],
        protected=[0, 0, 0, 0, 1, 1],
        feature_names=["proxy_feature", "clinical_signal"],
        model_config={},
    )


def cancer_dag():
    graph = obi.dag(
        nodes=[
            obi.variable("S", "binary"),
            obi.variable("C", "binary"),
            obi.variable("T", "real"),
            obi.variable("A", "protected_set"),
            obi.variable("phi", "bias", observed=False),
            obi.variable("theta", "parameters", observed=False),
        ]
    )
    obi.edge(graph, "S", "C")
    obi.edge(graph, "A", "C")
    obi.edge(graph, "A", "T")
    obi.edge(graph, "C", "T")
    obi.edge(graph, "phi", "T")
    obi.edge(graph, "theta", "C")
    return graph


def test_audit_detects_all_four_bias_vectors():
    report = obi.audit(
        biased_dataset(),
        thresholds={
            "representation_tolerance": 0.1,
            "proxy_correlation": 0.5,
            "label_rate_gap": 0.2,
        },
    )

    assert report.data_bias is True
    assert report.feature_bias is True
    assert report.label_bias is True
    assert report.spec_bias is True
    assert report.any_bias_found is True


def test_cancer_dag_factorization_and_backdoor_blocking():
    graph = cancer_dag()

    factors = obi.factorize(graph)
    t_factor = next(item for item in factors if item["variable"] == "T")
    paths = obi.backdoors(graph, treatment="C", target="T")

    assert set(t_factor["parents"]) == {"A", "C", "phi"}
    assert ["C", "A", "T"] in paths
    assert obi.block_backdoors(graph, paths, conditioning={"A"}) is True


def test_debias_returns_theta_without_protected_parameter_slot():
    data = biased_dataset()
    result = obi.debias(data, cancer_dag())

    assert result.theta.shape == (data.n_features,)
    assert "0" in result.bias_params
    assert "1" in result.bias_params
    assert result.metrics["method"] == "deterministic_minimal"
    assert result.posterior.shape == result.theta.shape


def test_validate_raises_on_demographic_parity_failure_by_default():
    data = obi.dataset(
        X=[[-1.0], [-1.0], [4.0], [4.0]],
        y=[0, 0, 1, 1],
        protected=[0, 0, 1, 1],
        model_config={"imbalance_sensitive": True},
    )
    result = obi.debias(data, cancer_dag())

    with pytest.raises(obi.FairnessValidationError):
        obi.validate(result, epsilon=0.05)


def test_validate_warn_policy_returns_failed_report():
    data = obi.dataset(
        X=[[-1.0], [-1.0], [4.0], [4.0]],
        y=[0, 0, 1, 1],
        protected=[0, 0, 1, 1],
        model_config={"imbalance_sensitive": True},
    )
    result = obi.debias(data, cancer_dag())

    report = obi.validate(result, epsilon=0.05, policy="warn")

    assert report.parity_ok is False
    assert report.max_gap > 0.05
    assert report.warnings


def test_demographic_helpers_are_numpy_style():
    gaps = obi.demographic_parity_gap(
        predictions=np.array([0.9, 0.8, 0.1, 0.2]),
        protected=np.array(["a", "a", "b", "b"]),
    )

    assert gaps["a|b"] == 1.0
    assert obi.bias_reduction(1.0, 0.15) == pytest.approx(0.85)


def test_dump_manifest_supports_debias_result_dataclasses(tmp_path):
    result = obi.debias(biased_dataset(), cancer_dag())
    path = tmp_path / "manifest.json"

    obi.dump_manifest(result, path)

    content = path.read_text(encoding="utf-8")
    assert "deterministic_minimal" in content
    assert "theta" in content
