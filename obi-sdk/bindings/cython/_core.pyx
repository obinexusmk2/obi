# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
OBIAI SDK Core - Ontological Bayesian Intelligence
Non-monolithic Cython extension for libpolycall-v1
"""

import os
import sys
from libc.stdlib cimport malloc, free
from libc.string cimport strcpy, strlen
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cimport libpolycall as lp

# Version info
__version__ = "0.1.0-alpha"
__author__ = "Nnamdi Michael Okpala (OBINexus)"

# Platform-specific DLL loading
cdef void _ensure_dll_path():
    """Ensure DLLs are loadable on Windows/WSL"""
    if sys.platform == "win32":
        import os
        # Add conda Library/bin to PATH if in conda env
        conda_prefix = os.environ.get("CONDA_PREFIX")
        if conda_prefix:
            os.add_dll_directory(os.path.join(conda_prefix, "Library", "bin"))
        # Add local lib directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.add_dll_directory(os.path.join(script_dir, "..", "..", "lib"))

# Initialize on import
_ensure_dll_path()

cdef class OBIContext:
    """
    OBI AI Context - Manages ontological Bayesian inference session
    
    This is the core handle for interacting with libpolycall-v1.
    Non-monolithic: contexts are isolated and can be dynamically loaded.
    """
    cdef lp.obi_context_t* _ctx
    cdef bint _initialized
    cdef str _config
    
    def __cinit__(self, str config_json=None):
        self._ctx = NULL
        self._initialized = False
        self._config = config_json or "{}"
        
        cdef bytes config_bytes = self._config.encode('utf-8')
        cdef char* c_config = config_bytes
        
        with nogil:
            self._ctx = lp.obi_create_context(c_config)
        
        if self._ctx is NULL:
            raise RuntimeError("Failed to create OBI context")
        self._initialized = True
    
    def __dealloc__(self):
        if self._ctx is not NULL:
            lp.obi_destroy_context(self._ctx)
            self._ctx = NULL
    
    cpdef bint is_valid(self):
        """Check if context is still valid"""
        return self._ctx is not NULL and self._initialized
    
    cpdef str get_version(self):
        """Get libpolycall version"""
        cdef const char* ver = lp.obi_get_version()
        return ver.decode('utf-8') if ver else "unknown"
    
    @staticmethod
    def set_log_level(int level):
        """Set logging level (0=ERROR, 1=WARN, 2=INFO, 3=DEBUG)"""
        lp.obi_set_log_level(level)

cdef class OBITensor:
    """
    OBI Tensor - 4D tensor for ontological Bayesian operations
    
    Wraps obi_tensor_t with numpy array interface for zero-copy
    interoperability.
    """
    cdef lp.obi_tensor_t* _tensor
    cdef object __array_interface__
    
    def __cinit__(self, object shape not None):
        cdef size_t ndim = len(shape)
        cdef size_t total_size = 1
        
        self._tensor = <lp.obi_tensor_t*>PyMem_Malloc(sizeof(lp.obi_tensor_t))
        if self._tensor is NULL:
            raise MemoryError("Failed to allocate tensor")
        
        self._tensor.ndim = ndim
        self._tensor.shape = <size_t*>PyMem_Malloc(ndim * sizeof(size_t))
        if self._tensor.shape is NULL:
            raise MemoryError("Failed to allocate shape")
        
        for i in range(ndim):
            self._tensor.shape[i] = shape[i]
            total_size *= shape[i]
        
        self._tensor.data = <double*>PyMem_Malloc(total_size * sizeof(double))
        if self._tensor.data is NULL:
            raise MemoryError("Failed to allocate data")
    
    def __dealloc__(self):
        if self._tensor is not NULL:
            if self._tensor.shape is not NULL:
                PyMem_Free(self._tensor.shape)
            if self._tensor.data is not NULL:
                PyMem_Free(self._tensor.data)
            PyMem_Free(self._tensor)
