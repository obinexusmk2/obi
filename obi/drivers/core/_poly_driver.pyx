# cython: language_level=3, embedsignature=True, boundscheck=False, wraparound=False, cdivision=True

"""
PolyDriver - Polymorphic driver for dimensional game theory and ontological reasoning
Cython accelerated non-monolithic inference engine
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Callable
from libc.stdint cimport uint32_t, uint64_t, int32_t, float32_t
from libc.math cimport exp, log2, fabs
cimport cython

# Polycall C interface declarations
cdef extern from "polycall.h" nogil:
    ctypedef struct polycall_solver:
        pass

    ctypedef struct polycall_solution:
        uint32_t status
        float* payoff_matrix
        uint32_t matrix_size

    # Dimensional Game Theory solvers
    polycall_solver* polycall_solver_create(const char* solver_type)
    void polycall_solver_destroy(polycall_solver* solver)

    polycall_solution polycall_solve_game(
        polycall_solver* solver,
        const float* payoff,
        uint32_t rows,
        uint32_t cols,
        uint32_t iterations
    ) nogil

    # Game theory utility functions
    float polycall_compute_entropy(const float* dist, uint32_t len) nogil
    float polycall_compute_divergence(const float* p, const float* q, uint32_t len) nogil


cdef class PolyDriver:
    """
    Non-monolithic inference engine for dimensional game theory
    Implements mixed strategy Nash equilibrium solvers with OBI extensions
    """
    cdef polycall_solver* _solver
    cdef str _solver_type
    cdef dict _params
    cdef list _solution_history

    def __cinit__(
        self,
        solver_type: str = "mixed_strategy",
        params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize PolyDriver with specified solver type

        Args:
            solver_type: Type of solver (mixed_strategy, pure_strategy, evolutionary)
            params: Solver configuration parameters
        """
        self._solver_type = solver_type
        self._params = params or {}
        self._solution_history = []

        # Create solver via libpolycall
        cdef bytes solver_bytes = solver_type.encode('utf-8')
        with nogil:
            self._solver = polycall_solver_create(solver_bytes)

        if self._solver == NULL:
            raise RuntimeError(f"Failed to create solver: {solver_type}")

    def __dealloc__(self):
        """Cleanup solver resources"""
        if self._solver != NULL:
            with nogil:
                polycall_solver_destroy(self._solver)
            self._solver = NULL

    def solve_game(
        self,
        payoff_matrix: np.ndarray,
        iterations: uint32_t = 1000
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Solve dimensional game using Nash equilibrium

        Args:
            payoff_matrix: Payoff matrix (float32, shape: (rows, cols))
            iterations: Maximum iterations for convergence

        Returns:
            solution: Mixed strategy probability distribution
            metrics: Convergence and quality metrics
        """
        # Validate and prepare input
        payoff = np.ascontiguousarray(payoff_matrix, dtype=np.float32)
        cdef uint32_t rows = payoff.shape[0]
        cdef uint32_t cols = payoff.shape[1]
        cdef float[::1] payoff_view = payoff.flatten()

        # Call solver
        cdef polycall_solution solution
        with nogil:
            solution = polycall_solve_game(
                self._solver,
                &payoff_view[0],
                rows,
                cols,
                iterations
            )

        if solution.status != 0:
            raise RuntimeError(f"Solver failed with status {solution.status}")

        # Convert result to numpy
        result_array = np.zeros(rows, dtype=np.float32)
        cdef float[::1] result_view = result_array
        if solution.payoff_matrix != NULL:
            memcpy(&result_view[0], solution.payoff_matrix, rows * sizeof(float))

        # Track solution
        metrics = {
            "status": solution.status,
            "rows": rows,
            "cols": cols,
            "iterations": iterations
        }
        self._solution_history.append(metrics)

        return result_array, metrics

    def solve_dimensiona_game(
        self,
        payoff_matrix: np.ndarray,
        dimension_reduction: int = 1,
        iterations: uint32_t = 1000
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Solve game with dimensional reduction (DR = D - 1)

        Args:
            payoff_matrix: Original payoff matrix
            dimension_reduction: How many dimensions to reduce (default: 1)
            iterations: Solver iterations

        Returns:
            solution: Reduced dimensional solution
            metadata: Solution quality and convergence data
        """
        # Apply dimensional reduction
        payoff = np.ascontiguousarray(payoff_matrix, dtype=np.float32)

        # Simple reduction: average over last dimension_reduction axes
        for _ in range(dimension_reduction):
            if payoff.ndim > 2:
                payoff = np.mean(payoff, axis=-1)

        solution, metrics = self.solve_game(payoff, iterations)
        metrics["dimension_reduction"] = dimension_reduction
        metrics["reduced_shape"] = payoff.shape

        return solution, metrics

    def compute_entropy(self, distribution: np.ndarray) -> float:
        """
        Compute Shannon entropy of distribution

        Args:
            distribution: Probability distribution (sum to 1)

        Returns:
            Shannon entropy value
        """
        dist = np.ascontiguousarray(distribution, dtype=np.float32)
        cdef float[::1] dist_view = dist.flatten()
        cdef uint32_t dist_len = dist.size

        cdef float entropy
        with nogil:
            entropy = polycall_compute_entropy(&dist_view[0], dist_len)

        return <float>entropy

    def compute_divergence(
        self,
        p: np.ndarray,
        q: np.ndarray
    ) -> float:
        """
        Compute KL divergence between distributions

        Args:
            p: Reference distribution
            q: Comparison distribution

        Returns:
            KL divergence D(p||q)
        """
        p = np.ascontiguousarray(p, dtype=np.float32).flatten()
        q = np.ascontiguousarray(q, dtype=np.float32).flatten()

        if p.shape != q.shape:
            raise ValueError("Distributions must have same shape")

        cdef float[::1] p_view = p
        cdef float[::1] q_view = q
        cdef uint32_t len_dist = p.size

        cdef float divergence
        with nogil:
            divergence = polycall_compute_divergence(&p_view[0], &q_view[0], len_dist)

        return <float>divergence

    @property
    def solver_type(self) -> str:
        """Get solver type"""
        return self._solver_type

    @property
    def solution_history(self) -> List[Dict[str, Any]]:
        """Get solution history"""
        return self._solution_history.copy()

    def clear_history(self):
        """Clear solution history"""
        self._solution_history.clear()


cdef class DimensionalReasoner:
    """
    Ontological reasoner for dimensional game theory problems
    Combines top-down and bottom-up reasoning with game-theoretic insights
    """
    cdef PolyDriver _driver
    cdef dict _reasoning_state

    def __cinit__(self):
        """Initialize reasoner with default poly driver"""
        self._driver = PolyDriver(solver_type="mixed_strategy")
        self._reasoning_state = {}

    def reason_topdown(
        self,
        principle: np.ndarray,
        specific_case: np.ndarray,
        alpha: float = 0.7
    ) -> np.ndarray:
        """
        Top-down reasoning: from general principles to specific cases

        Args:
            principle: General principle (probability distribution)
            specific_case: Specific case evidence
            alpha: Weighting factor (principle weight)

        Returns:
            Combined reasoning result
        """
        principle = np.ascontiguousarray(principle, dtype=np.float32)
        specific_case = np.ascontiguousarray(specific_case, dtype=np.float32)

        if principle.shape != specific_case.shape:
            raise ValueError("Shapes must match")

        # Top-down combination: weighted average favoring principle
        result = alpha * principle + (1 - alpha) * specific_case
        return result / np.sum(result)  # Normalize

    def reason_bottomup(
        self,
        evidence: np.ndarray,
        prior: Optional[np.ndarray] = None,
        alpha: float = 0.7
    ) -> np.ndarray:
        """
        Bottom-up reasoning: from specific evidence to general principles

        Args:
            evidence: Observed evidence
            prior: Optional prior distribution
            alpha: Weighting factor

        Returns:
            Inferred posterior distribution
        """
        evidence = np.ascontiguousarray(evidence, dtype=np.float32)

        if prior is None:
            prior = np.ones_like(evidence) / evidence.size

        # Simple Bayesian update: likelihood times prior
        likelihood = np.exp(evidence - np.max(evidence))  # Numerical stability
        posterior = likelihood * prior / np.sum(likelihood * prior)

        return posterior

    def reason_bidirectional(
        self,
        principle: np.ndarray,
        evidence: np.ndarray,
        alpha_topdown: float = 0.5,
        alpha_bottomup: float = 0.5,
        consensus_weight: float = 0.5
    ) -> np.ndarray:
        """
        Bidirectional reasoning: combine top-down and bottom-up

        Args:
            principle: General principle
            evidence: Specific evidence
            alpha_topdown: Top-down weight
            alpha_bottomup: Bottom-up weight
            consensus_weight: How much to blend the two approaches

        Returns:
            Consensus reasoning result
        """
        topdown_result = self.reason_topdown(principle, evidence, alpha_topdown)
        bottomup_result = self.reason_bottomup(evidence, principle, alpha_bottomup)

        # Consensus: weighted average
        result = consensus_weight * topdown_result + (1 - consensus_weight) * bottomup_result
        return result / np.sum(result)  # Normalize

    def solve_ontological_game(
        self,
        payoff_matrix: np.ndarray,
        reasoning_mode: str = "bidirectional"
    ) -> Dict[str, Any]:
        """
        Solve game with ontological reasoning integration

        Args:
            payoff_matrix: Game payoff matrix
            reasoning_mode: 'topdown', 'bottomup', or 'bidirectional'

        Returns:
            Complete solution with reasoning trace
        """
        solution, metrics = self._driver.solve_game(payoff_matrix)

        self._reasoning_state = {
            "mode": reasoning_mode,
            "solution": solution.tolist(),
            "metrics": metrics,
            "entropy": self._driver.compute_entropy(solution)
        }

        return self._reasoning_state

    @property
    def reasoning_state(self) -> Dict[str, Any]:
        """Get current reasoning state"""
        return self._reasoning_state.copy()
