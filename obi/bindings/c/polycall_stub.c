#include "polycall.h"
#include <stdlib.h>
#include <string.h>

/* Macro for exported symbols (override hidden visibility) */
#if defined(_WIN32) || defined(__CYGWIN__)
#  define EXPORT __declspec(dllexport)
#else
#  define EXPORT __attribute__((visibility("default")))
#endif

/* Stub implementations for polycall functions */

EXPORT obi_context_t* obi_create_context(const char* config) {
    obi_context_t* ctx = (obi_context_t*)malloc(sizeof(obi_context_t));
    if (ctx) {
        ctx->_internal = NULL;
    }
    return ctx;
}

EXPORT void obi_destroy_context(obi_context_t* ctx) {
    if (ctx) {
        free(ctx);
    }
}

EXPORT int obi_process_tensor(obi_context_t* ctx, obi_tensor_t* input, obi_tensor_t* output) {
    /* Stub: return success */
    return 0;
}

EXPORT const char* obi_get_version(void) {
    return "0.1.0-alpha-stub";
}

EXPORT int obi_set_log_level(int level) {
    /* Stub: accept any level */
    return 0;
}

/* ============================================================================
   PolyCall Game Theory Solver Stub Implementations
   ============================================================================ */

EXPORT polycall_solver* polycall_solver_create(const char* solver_type) {
    polycall_solver* solver = (polycall_solver*)malloc(sizeof(polycall_solver));
    if (solver) {
        solver->_internal = NULL;
    }
    return solver;
}

EXPORT void polycall_solver_destroy(polycall_solver* solver) {
    if (solver) {
        free(solver);
    }
}

EXPORT polycall_solution polycall_solve_game(
    polycall_solver* solver,
    const float* payoff_matrix,
    uint32_t rows,
    uint32_t cols,
    uint32_t max_iterations
) {
    polycall_solution result;
    result.status = 0;  /* Success */
    result.payoff_matrix = NULL;
    result.matrix_rows = rows;
    result.matrix_cols = cols;
    result.mixed_strategy = NULL;
    result.strategy_len = 0;
    return result;
}

EXPORT float polycall_compute_entropy(const float* distribution, uint32_t len) {
    /* Stub: return 0.0 */
    return 0.0f;
}

EXPORT float polycall_compute_divergence(const float* p, const float* q, uint32_t len) {
    /* Stub: return 0.0 */
    return 0.0f;
}
