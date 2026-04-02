"""
Tests for OBI Context management
"""

import pytest
import sys
import platform


def test_import():
    """Test that Cython extensions can be imported"""
    from obi_sdk.bindings import _core
    assert hasattr(_core, 'OBIContext')


def test_context_creation():
    """Test basic context creation"""
    from obi_sdk.sdk.core.context import OBIContext
    
    ctx = OBIContext(config={"test": True})
    assert ctx.is_valid()
    assert ctx.id.startswith("ctx_")
    ctx.close()


def test_context_version():
    """Test version retrieval"""
    from obi_sdk.sdk.core.context import OBIContext
    
    with OBIContext() as ctx:
        version = ctx.version
        assert isinstance(version, str)
        assert len(version) > 0


def test_context_registry():
    """Test context registry management"""
    from obi_sdk.sdk.core.context import OBIContext
    
    OBIContext.shutdown_all()  # Clean slate
    
    ctx1 = OBIContext(context_id="test1")
    ctx2 = OBIContext(context_id="test2")
    
    active = OBIContext.get_active_contexts()
    assert "test1" in active
    assert "test2" in active
    
    OBIContext.shutdown_all()
    assert len(OBIContext.get_active_contexts()) == 0


@pytest.mark.skipif(
    not ("microsoft" in platform.release().lower() or "WSL" in platform.release()),
    reason="WSL-specific test"
)
def test_wsl_library_path():
    """Test library path setup in WSL"""
    from obi_sdk.sdk.core.context import OBIContext
    
    # Should not raise even with complex paths
    ctx = OBIContext()
    assert ctx.is_valid()
    ctx.close()
