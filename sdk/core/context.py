"""
OBI Context Management - Handles libpolycall-v1 lifecycle
"""

import os
import sys
import warnings
from typing import Optional, Dict, Any
from pathlib import Path

# Import Cython extension
try:
    from obi_sdk.bindings._core import OBIContext as _OBIContext
    from obi_sdk.bindings._core import OBITensor as _OBITensor
except ImportError as e:
    warnings.warn(f"Could not import Cython extensions: {e}. Falling back to mock.")
    _OBIContext = None
    _OBITensor = None


class OBIContext:
    """
    High-level context manager for OBI AI operations.
    
    Non-monolithic design: contexts are isolated, versioned, and
    can be dynamically loaded/unloaded without affecting other
    active contexts.
    """
    
    _registry: Dict[str, 'OBIContext'] = {}
    _version = "0.1.0-alpha"
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        context_id: Optional[str] = None,
        libpolycall_path: Optional[str] = None
    ):
        """
        Initialize OBI context.
        
        Args:
            config: JSON-serializable configuration dict
            context_id: Unique identifier for this context
            libpolycall_path: Override path to libpolycall-v1 library
        """
        self._config = config or {}
        self._id = context_id or f"ctx_{id(self)}"
        self._lib_path = libpolycall_path
        
        # Ensure library is discoverable
        self._setup_library_path()
        
        if _OBIContext is None:
            raise RuntimeError("OBI SDK C extensions not available")
        
        import json
        self._ctx = _OBIContext(json.dumps(self._config))
        OBIContext._registry[self._id] = self
    
    def _setup_library_path(self):
        """Configure library loading paths for WSL/Windows"""
        if self._lib_path:
            lib_path = Path(self._lib_path)
            if sys.platform == "win32":
                os.add_dll_directory(str(lib_path.parent))
            else:
                # WSL/Linux: use LD_LIBRARY_PATH or rpath
                current = os.environ.get("LD_LIBRARY_PATH", "")
                os.environ["LD_LIBRARY_PATH"] = f"{lib_path.parent}:{current}"
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def version(self) -> str:
        return self._ctx.get_version()
    
    def is_valid(self) -> bool:
        """Check if context is active and valid"""
        return self._ctx.is_valid()
    
    def close(self):
        """Explicitly close context and free resources"""
        if self._id in OBIContext._registry:
            del OBIContext._registry[self._id]
        self._ctx = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    @classmethod
    def get_active_contexts(cls) -> Dict[str, 'OBIContext']:
        """Return all active context instances"""
        return cls._registry.copy()
    
    @classmethod
    def shutdown_all(cls):
        """Close all active contexts - use for cleanup"""
        for ctx in list(cls._registry.values()):
            ctx.close()
