"""PSC-aligned tests for OBIAI data drift mitigation API."""

import obi


def test_drift_vector_classification_prefers_raw_feature_shift():
    baseline = obi.data_point(
        [0.9, 0.1],
        context_features=[0.5, 0.5],
        knowledge_embedding=[1.0, 0.0],
    )
    current = obi.data_point(
        [0.1, 0.9],
        context_features=[0.5, 0.5],
        knowledge_embedding=[1.0, 0.0],
    )

    assert obi.classify_drift_vector(current, baseline) == "phenomenological"


def test_signed_failure_scale_and_zone_classification():
    baseline = obi.data_point([0.9, 0.1])
    human_current = obi.data_point([0.1, 0.9], drift_source="human_context")
    ai_current = obi.data_point([0.1, 0.9], drift_source="ai_system")

    human_drift = obi.drift_measure(human_current, baseline)
    ai_drift = obi.drift_measure(ai_current, baseline)

    assert human_drift > 9.0
    assert ai_drift < -9.0
    assert obi.classify_drift_zone(human_drift) == "human_distress"
    assert obi.classify_drift_zone(ai_drift) == "ai_panic"
    assert obi.zone_response("ai_caution").cascade == "uche"


def test_diram_cascade_activates_uche_and_eze_by_threshold():
    cascade = obi.diram_cascade()

    assert cascade.get_active_tiers() == ["obinexus"]
    assert cascade.activate_for_drift(7.0) == ["obinexus", "uche", "eze"]


def test_filter_flash_engine_routes_by_confidence():
    engine = obi.filter_flash_engine()
    high_confidence = obi.data_point([1000.0, 0.0, 0.0])
    low_confidence = obi.data_point([1.0, 1.0, 1.0])

    filter_output = engine.process(high_confidence)
    flash_output = engine.process(low_confidence)

    assert filter_output.source == "filter"
    assert high_confidence.id in engine.filter_memory
    assert flash_output.source == "flash"
    assert low_confidence.id in engine.flash_memory


def test_mitigate_drift_escalates_to_eze_and_preserves_coherence():
    baseline = obi.data_point([1.0, 0.0, 0.0])
    current = obi.data_point([0.0, 1.0, 0.0], drift_source="human_context")

    result = obi.mitigate_drift(current, baseline)

    assert result.observation.zone == "human_distress"
    assert result.observation.vector_type == "phenomenological"
    assert result.cascade.get_active_tiers() == ["obinexus", "uche", "eze"]
    assert result.output.eze_override is True
    assert result.output.coherence >= obi.C_COHERENCE


def test_storage_layer_and_manifest_dump_support_drift_result(tmp_path):
    point = obi.data_point(
        [2.0, 0.0],
        metadata={"cultural_context": "nsibidi", "love_anchor": "community"},
    )
    record = obi.storage_layer(point)
    result = obi.mitigate_drift(point, obi.data_point([2.0, 0.0]))
    path = tmp_path / "drift_manifest.json"

    obi.dump_manifest(result, path)

    assert len(record.retrieval_key) == 64
    assert "measure_drift" in path.read_text(encoding="utf-8")


def test_malpaartice_monitor_audit_and_prevention():
    result = obi.mitigate_drift(
        obi.data_point([0.0, 1.0], drift_source="human_context"),
        obi.data_point([1.0, 0.0]),
    )
    framework = obi.malpaartice_framework()

    monitor_record = framework.monitor(result)
    audit_report = framework.audit()
    prevention = framework.prevent(4.0)

    assert monitor_record["zone"] == "human_distress"
    assert audit_report["compliance_rate"] == 1.0
    assert prevention["type"] == "pre_activate_uche"


def test_triangi_validation_tracks_coherence_curve():
    engine = obi.filter_flash_engine()
    cases = [
        {"input": obi.data_point([1000.0, 0.0]), "drift_magnitude": 0.0},
        {"input": obi.data_point([0.0, 1000.0]), "drift_magnitude": 12.0},
    ]

    report = obi.triangi_validate(engine, cases)

    assert report.threshold_met is True
    assert report.overall_score == 1.0
    assert set(report.coherence_curve) == {0.0, 12.0}
