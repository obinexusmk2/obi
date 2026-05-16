"""Package and OBIContext smoke tests."""

from obi import OBIContext, ReasoningResult


def test_package_import_surface():
    import obi

    assert obi.__version__ == "0.1.0-alpha"
    assert hasattr(obi, "OBIContext")
    assert hasattr(obi, "internal_probe")
    assert hasattr(obi, "DataProbeAdapter")


def test_context_creation_and_reasoning():
    ctx = OBIContext(confidence_threshold=0.954)
    state = ctx.probe_internal(
        {
            "speed_mph": 65,
            "distance_m": 50,
            "friction": 0.45,
        }
    )
    result = ctx.infer(state)

    assert isinstance(result, ReasoningResult)
    assert result.action == "BRAKE"
    assert result.confidence >= 0.954
    assert "FACT:" in result.reasoning_chain


def test_context_history_is_copied():
    ctx = OBIContext()
    state = ctx.probe_internal({"speed_mph": 30, "distance_m": 150, "friction": 0.7})
    ctx.infer(state)

    history = ctx.get_history()
    history.clear()

    assert len(ctx.get_history()) == 1
