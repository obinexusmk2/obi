#ifndef POLYCALL_H
#define POLYCALL_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

/* OBI Context - opaque handle */
typedef struct obi_context {
    void* _internal;
} obi_context_t;

/* OBI Tensor structure */
typedef struct {
    size_t ndim;
    size_t* shape;
    double* data;
} obi_tensor_t;

/* PolyCall Game Theory Solver - opaque handle */
typedef struct polycall_solver {
    void* _internal;
} polycall_solver;

/* PolyCall Solution Result */
typedef struct {
    uint32_t status;           /* 0 = success, non-zero = error code */
    float* payoff_matrix;      /* Solution equilibrium payoff matrix */
    uint32_t matrix_rows;      /* Rows in solution matrix */
    uint32_t matrix_cols;      /* Columns in solution matrix */
    float* mixed_strategy;     /* Mixed strategy probabilities */
    uint32_t strategy_len;     /* Length of mixed strategy array */
} polycall_solution;

/* OBI Context Function Declarations */
obi_context_t* obi_create_context(const char* config);
void obi_destroy_context(obi_context_t* ctx);
int obi_process_tensor(obi_context_t* ctx, obi_tensor_t* input, obi_tensor_t* output);
const char* obi_get_version(void);
int obi_set_log_level(int level);

/* PolyCall Game Theory Solver Function Declarations */
polycall_solver* polycall_solver_create(const char* solver_type);
void polycall_solver_destroy(polycall_solver* solver);
polycall_solution polycall_solve_game(
    polycall_solver* solver,
    const float* payoff_matrix,
    uint32_t rows,
    uint32_t cols,
    uint32_t max_iterations
);
float polycall_compute_entropy(const float* distribution, uint32_t len);
float polycall_compute_divergence(const float* p, const float* q, uint32_t len);

#ifdef __cplusplus
}
#endif

#endif /* POLYCALL_H */
