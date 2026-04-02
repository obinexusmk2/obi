# cython: language_level=3

cdef extern from "polycall.h":
    # Platform-specific export macros
    cdef enum:
        OBI_API_EXPORT
        OBI_API_IMPORT
    
    # Core types
    ctypedef struct obi_context_t:
        pass
    
    ctypedef struct obi_tensor_t:
        size_t ndim
        size_t* shape
        double* data
    
    # Function pointers with explicit calling convention
    ctypedef obi_context_t* (*obi_create_context_func)(const char* config) except NULL
    ctypedef void (*obi_destroy_context_func)(obi_context_t* ctx) noexcept
    ctypedef int (*obi_process_tensor_func)(obi_context_t* ctx, obi_tensor_t* input, obi_tensor_t* output) except -1
    
    # API functions
    obi_context_t* obi_create_context(const char* config) except NULL
    void obi_destroy_context(obi_context_t* ctx) noexcept
    int obi_process_tensor(obi_context_t* ctx, obi_tensor_t* input, obi_tensor_t* output) except -1
    const char* obi_get_version() noexcept
    int obi_set_log_level(int level) noexcept

# Platform detection
cdef inline bint is_windows():
    cdef const char* platform = "win32"
    # Runtime platform check
    import sys
    return sys.platform == "win32"

cdef inline bint is_wsl():
    import platform
    return "microsoft" in platform.release().lower()
