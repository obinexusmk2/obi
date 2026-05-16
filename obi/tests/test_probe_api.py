"""Functional probe and DataProbeAdapter tests."""

import numpy as np

from obi import Config, DataProbeAdapter, external_probe, internal_probe, probe_alignment
from obi.core import Channel


def high_confidence_data(size=64):
    data = np.zeros(size, dtype=np.float32)
    data[0] = 1000.0
    return data


def low_confidence_data(size=64):
    return np.ones(size, dtype=np.float32)


def valid_state(size=64):
    state = np.zeros(size, dtype=np.float64)
    state[0] = 1.0
    return state


def mismatched_state(size=64):
    state = np.zeros(size, dtype=np.float64)
    state[-1] = 1.0
    return state


def test_internal_probe_collapses_high_confidence_data():
    result = internal_probe(high_confidence_data())

    assert result.channel == Channel.CH_2
    assert result.is_collapsed
    assert result.confidence >= 0.954
    assert result.provenance["probe"] == "P_internal"


def test_internal_probe_defers_low_confidence_data():
    result = internal_probe(low_confidence_data())

    assert result.channel == Channel.CH_1
    assert result.is_deferred
    assert result.confidence < 0.954
    assert result.provenance["action"] == "defer_to_human"


def test_external_probe_emits_validated_state():
    result = external_probe(valid_state(), output_shape=(8, 8))

    assert result.channel == Channel.CH_2
    assert result.data.shape == (8, 8)
    assert result.data.dtype == np.uint8
    assert result.provenance["probe"] == "P_external"


def test_external_probe_blocks_weak_state():
    result = external_probe(low_confidence_data().astype(np.float64))

    assert result.channel == Channel.CH_1
    assert result.data is None


def test_probe_alignment_passes_matching_state():
    data = high_confidence_data()
    state = internal_probe(data).state

    result = probe_alignment(data, state)

    assert result.channel == Channel.CH_2
    assert result.confidence >= 0.954


def test_probe_alignment_defers_mismatch():
    result = probe_alignment(high_confidence_data(), mismatched_state())

    assert result.channel == Channel.CH_1
    assert result.provenance["reason"] == "state_data_mismatch"


def test_data_probe_adapter_functional_and_oop_are_equivalent():
    data = high_confidence_data()
    state = internal_probe(data).state
    adapter = DataProbeAdapter(config=Config(threshold=0.954))

    proof = adapter.verify_bijection(data, state)

    assert proof["equivalent"] is True
    assert proof["functional"]["internal"].channel == Channel.CH_2
    assert proof["oop"]["alignment"].channel == Channel.CH_2
