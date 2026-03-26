# cython: language_level=3, embedsignature=True, boundscheck=False, wraparound=False, cdivision=True

"""
OBI Core Cython Extension - Direct libpolycall-v1 bindings
Ontological Bayesian Intelligence - Core C/C++ interface
"""

import numpy as np
from typing import Dict, Any, Optional
from libc.stdint cimport uint32_t, uint64_t, int32_t
from libc.string cimport memcpy

# External C declarations for libpolycall-v1
cdef extern from "polycall.h" nogil:
    ctypedef struct polycall_context:
        pass

    ctypedef struct polycall_result:
        uint32_t code
        const char* message

    # Core API functions
    polycall_context* polycall_context_create(const char* config)
    void polycall_context_destroy(polycall_context* ctx)

    polycall_result polycall_infer(
        polycall_context* ctx,
        const float* evidence,
        uint32_t evidence_len,
        float* posterior,
        uint32_t posterior_len
    ) nogil

    const char* polycall_get_version()
    uint32_t polycall_is_valid(polycall_context* ctx)


cdef class OBIContext:
    """
    High-level wrapper for libpolycall-v1 context
    Manages lifecycle and exposes inference operations
    """
    cdef polycall_context* _ctx
    cdef str _id
    cdef dict _config

    def __cinit__(self, config: Optional[Dict[str, Any]] = None, context_id: Optional[str] = None):
        """Initialize OBI context with libpolycall-v1"""
        self._config = config or {}
        self._id = context_id or f"ctx_{id(self)}"

        # Convert config to JSON string for C function
        import json
        config_json = json.dumps(self._config)
        cdef bytes config_bytes = config_json.encode('utf-8')

        with nogil:
            self._ctx = polycall_context_create(config_bytes)

        if self._ctx == NULL:
            raise RuntimeError("Failed to create OBI context in libpolycall-v1")

    def __dealloc__(self):
        """Cleanup context"""
        if self._ctx != NULL:
            with nogil:
                polycall_context_destroy(self._ctx)
            self._ctx = NULL

    @property
    def id(self) -> str:
        """Get context ID"""
        return self._id

    @property
    def config(self) -> Dict[str, Any]:
        """Get context configuration"""
        return self._config.copy()

    def get_version(self) -> str:
        """Get libpolycall-v1 version"""
        cdef const char* version
        with nogil:
            version = polycall_get_version()
        return version.decode('utf-8') if version != NULL else "unknown"

    def is_valid(self) -> bool:
        """Check if context is still valid"""
        cdef uint32_t valid
        with nogil:
            valid = polycall_is_valid(self._ctx)
        return bool(valid)

    def infer(self, evidence: np.ndarray, prior: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Perform Bayesian inference using libpolycall-v1

        Args:
            evidence: Input evidence array (float32)
            prior: Optional prior distribution

        Returns:
            Posterior distribution (float32)
        """
        # Ensure contiguous float32 array
        evidence = np.ascontiguousarray(evidence, dtype=np.float32)
        cdef uint32_t evidence_len = evidence.size
        cdef float[::1] evidence_view = evidence.flatten()

        # Allocate posterior array
        posterior = np.zeros(evidence.size, dtype=np.float32)
        cdef float[::1] posterior_view = posterior

        # Call libpolycall-v1 inference
        cdef polycall_result result
        with nogil:
            result = polycall_infer(
                self._ctx,
                &evidence_view[0],
                evidence_len,
                &posterior_view[0],
                evidence_len
            )

        if result.code != 0:
            msg = result.message.decode('utf-8') if result.message != NULL else "Unknown error"
            raise RuntimeError(f"Inference failed: {msg}")

        return posterior.reshape(evidence.shape)


cdef class OBITensor:
    """
    Lightweight tensor wrapper for OBI operations
    Enforces 4D structure for dimensional consistency
    """
    cdef np.ndarray _data

    def __cinit__(self, data: np.ndarray, dtype=np.float32):
        """Initialize tensor with 4D validation"""
        arr = np.asarray(data, dtype=dtype)
        self._data = self._ensure_4d(arr)

    cdef np.ndarray _ensure_4d(self, np.ndarray arr):
        """Ensure tensor is 4D"""
        if arr.ndim == 4:
            return arr
        elif arr.ndim < 4:
            shape = tuple([1] * (4 - arr.ndim) + list(arr.shape))
            return arr.reshape(shape)
        else:
            # Reduce to 4D by flattening middle dimensions
            shape = (arr.shape[0], -1, arr.shape[-2], arr.shape[-1])
            return arr.reshape(shape)

    @property
    def data(self) -> np.ndarray:
        """Get underlying numpy array"""
        return self._data

    @property
    def shape(self) -> tuple:
        """Get tensor shape"""
        return tuple(self._data.shape)

    def __repr__(self) -> str:
        return f"OBITensor(shape={self.shape})"
