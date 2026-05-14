# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""
OBIAI SDK Core - Ontological Bayesian Intelligence
Non-monolithic Cython extension for libpolycall-v1

Problem: [PROB-01] Self-Blindness — enable system to interrogate internal state
Proof Source: Probe Hypothesis, AEGIS-PROOF-1.1
License: OBINexus Constitutional Legal Framework
Confidence Threshold: 95.4%
"""

import os
import sys
import numpy as np
from libc.stdlib cimport malloc, free
from libc.string cimport strcpy, strlen
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.bytes cimport PyBytes_AsString

cimport numpy as cnp

# Initialize numpy for array interface
cnp.import_array()

# Include libpolycall header definitions inline
cdef extern from "polycall.h" nogil:
    ctypedef struct obi_context_t:
        pass

    ctypedef struct obi_tensor_t:
        size_t ndim
        size_t* shape
        double* data

    # OBI Core functions
    obi_context_t* obi_create_context(const char* config) except NULL
    void obi_destroy_context(obi_context_t* ctx) noexcept
    int obi_process_tensor(obi_context_t* ctx, obi_tensor_t* input, obi_tensor_t* output) except -1
    const char* obi_get_version() noexcept
    int obi_set_log_level(int level) noexcept

# Version info
__version__ = "0.1.0-alpha"
__author__ = "Nnamdi Michael Okpala (OBINexus)"

# Platform-specific DLL loading
cdef void _ensure_dll_path():
    """Ensure DLLs are loadable on Windows/WSL"""
    if sys.platform == "win32":
        import os
        conda_prefix = os.environ.get("CONDA_PREFIX")
        if conda_prefix:
            os.add_dll_directory(os.path.join(conda_prefix, "Library", "bin"))
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.add_dll_directory(os.path.join(script_dir, "..", "..", "lib"))

# Initialize on import
_ensure_dll_path()

cdef class OBIContext:
    """
    [PROB-05] OBI AI Context - Manages ontological Bayesian inference session
    
    This is the core handle for interacting with libpolycall-v1.
    Non-monolithic: contexts are isolated and can be dynamically loaded.
    """
    cdef obi_context_t* _ctx
    cdef bint _initialized
    cdef str _config
    
    def __cinit__(self, str config_json=None):
        """Initialize OBI context with governance gate"""
        self._ctx = NULL
        self._initialized = False
        self._config = config_json or "{}"
        
        cdef bytes config_bytes = self._config.encode('utf-8')
        cdef const char* c_config = PyBytes_AsString(config_bytes)
        
        if c_config is NULL:
            raise ValueError("Failed to encode config string")
        
        with nogil:
            self._ctx = obi_create_context(c_config)
        
        if self._ctx is NULL:
            raise RuntimeError("Failed to create OBI context from libpolycall-v1")
        self._initialized = True
    
    def __dealloc__(self):
        if self._ctx is not NULL:
            obi_destroy_context(self._ctx)
            self._ctx = NULL
    
    cpdef bint is_valid(self):
        """Check if context is still valid"""
        return self._ctx is not NULL and self._initialized
    
    cpdef str get_version(self):
        """Get libpolycall version"""
        cdef const char* ver = obi_get_version()
        return ver.decode('utf-8') if ver else "unknown"
    
    @staticmethod
    def set_log_level(int level):
        """Set logging level (0=ERROR, 1=WARN, 2=INFO, 3=DEBUG)"""
        obi_set_log_level(level)

cdef class OBITensor:
    """
    [PROB-04] OBI Tensor - 4D consciousness-aware tensor wrapper
    
    Wraps obi_tensor_t with zero-copy numpy array interface.
    Enforces 4D dimensional consistency per OBI memory architecture.
    """
    cdef obi_tensor_t* _tensor
    cdef object _data_view
    
    def __cinit__(self, object shape not None, dtype=np.float32):
        """Initialize tensor with 4D validation."""
        cdef size_t i
        cdef size_t ndim = len(shape)
        cdef size_t total_size = 1
        
        if ndim != 4:
            raise ValueError(f"OBI tensors must be 4D, got {ndim}D shape: {shape}")
        
        # Allocate tensor struct
        self._tensor = <obi_tensor_t*>PyMem_Malloc(sizeof(obi_tensor_t))
        if self._tensor is NULL:
            raise MemoryError("Failed to allocate obi_tensor_t struct")
        
        # Allocate and populate shape array
        self._tensor.ndim = ndim
        self._tensor.shape = <size_t*>PyMem_Malloc(ndim * sizeof(size_t))
        if self._tensor.shape is NULL:
            PyMem_Free(self._tensor)
            raise MemoryError("Failed to allocate shape array")
        
        for i in range(ndim):
            if shape[i] <= 0:
                PyMem_Free(self._tensor.shape)
                PyMem_Free(self._tensor)
                raise ValueError(f"Shape dimension {i} must be > 0, got {shape[i]}")
            self._tensor.shape[i] = shape[i]
            total_size *= shape[i]
        
        # Allocate data buffer
        self._tensor.data = <double*>PyMem_Malloc(total_size * sizeof(double))
        if self._tensor.data is NULL:
            PyMem_Free(self._tensor.shape)
            PyMem_Free(self._tensor)
            raise MemoryError("Failed to allocate tensor data buffer")
        
        self._data_view = None
    
    def __dealloc__(self):
        """Clean up allocated memory."""
        if self._tensor is not NULL:
            if self._tensor.shape is not NULL:
                PyMem_Free(self._tensor.shape)
            if self._tensor.data is not NULL:
                PyMem_Free(self._tensor.data)
            PyMem_Free(self._tensor)
            self._tensor = NULL
