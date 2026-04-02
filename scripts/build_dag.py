#!/usr/bin/env python3
"""
build_dag.py - Directed Acyclic Graph for OBIAI SDK module dependency resolution

Implements Kahn's algorithm for topological sort. The DAG encodes the build
order across all 510-problem domains: bindings → drivers → extension → plugins → sdk.
"""

from __future__ import annotations

import sys
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DAGNode:
    """A module node in the OBIAI dependency graph."""
    name: str
    deps: List[str] = field(default_factory=list)
    description: str = ""
    problem_domain: str = ""  # e.g. "binding/c", "binding/cython", etc.


class CycleError(Exception):
    """Raised when a cycle is detected in the DAG."""


class ModuleDAG:
    """
    Directed Acyclic Graph of OBIAI SDK modules.

    Nodes represent SDK sub-modules; edges represent dependencies (A → B means
    A must be built before B). Topological sort determines scaffold/build order.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, DAGNode] = {}

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def add_node(
        self,
        name: str,
        deps: Optional[List[str]] = None,
        description: str = "",
        problem_domain: str = "",
    ) -> None:
        """Register a module node."""
        if name in self._nodes:
            raise ValueError(f"Duplicate node: {name!r}")
        self._nodes[name] = DAGNode(
            name=name,
            deps=deps or [],
            description=description,
            problem_domain=problem_domain,
        )

    def node(self, name: str) -> DAGNode:
        return self._nodes[name]

    @property
    def nodes(self) -> Dict[str, DAGNode]:
        return dict(self._nodes)

    # ------------------------------------------------------------------
    # Topological sort (Kahn's algorithm)
    # ------------------------------------------------------------------

    def topological_sort(self) -> List[str]:
        """
        Return nodes in topological order (dependencies before dependents).

        Raises CycleError if the graph contains a cycle.
        """
        # Build in-degree map and adjacency list
        in_degree: Dict[str, int] = {n: 0 for n in self._nodes}
        adj: Dict[str, List[str]] = {n: [] for n in self._nodes}

        for name, node in self._nodes.items():
            for dep in node.deps:
                if dep not in self._nodes:
                    raise ValueError(
                        f"Node {name!r} depends on unknown node {dep!r}"
                    )
                adj[dep].append(name)
                in_degree[name] += 1

        queue: deque[str] = deque(
            sorted(n for n, d in in_degree.items() if d == 0)
        )
        order: List[str] = []

        while queue:
            n = queue.popleft()
            order.append(n)
            for successor in sorted(adj[n]):
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)

        if len(order) != len(self._nodes):
            remaining = set(self._nodes) - set(order)
            raise CycleError(f"Cycle detected among nodes: {remaining}")

        return order

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def print_graph(self) -> None:
        """Pretty-print the dependency graph."""
        width = max(len(n) for n in self._nodes) + 2
        print("\nOBI SDK Module Dependency Graph")
        print("=" * 60)
        for name in self.topological_sort():
            node = self._nodes[name]
            deps_str = ", ".join(node.deps) if node.deps else "(none)"
            print(f"  {name:<{width}} deps: [{deps_str}]")
            if node.description:
                print(f"  {'':{width}}      {node.description}")
        print()


# ---------------------------------------------------------------------------
# Factory: build the canonical OBIAI module DAG
# ---------------------------------------------------------------------------

def build_obiai_dag() -> ModuleDAG:
    """
    Construct the OBIAI SDK module DAG.

    Dependency order (bindings → drivers → extension → plugins → sdk → misc)
    reflects the 510-problem domain structure from the specification document.
    """
    dag = ModuleDAG()

    dag.add_node(
        "core",
        deps=[],
        description="OBI cognitive core — Heart AI, obicall runtime stubs",
        problem_domain="core",
    )
    dag.add_node(
        "bindings_c",
        deps=["core"],
        description="C FFI layer — ABI stability, memory safety, libpolycall-v1 (50 problems)",
        problem_domain="bindings/c",
    )
    dag.add_node(
        "bindings_cython",
        deps=["bindings_c"],
        description="Cython bindings — GIL management, NumPy integration, Python API (50 problems)",
        problem_domain="bindings/cython",
    )
    dag.add_node(
        "drivers",
        deps=["bindings_cython"],
        description="PolyDriver — dimensional game theory, DimensionalReasoner",
        problem_domain="drivers/core",
    )
    dag.add_node(
        "extension_c",
        deps=["bindings_c"],
        description="C extension plugins — plugin ABI, hot reload, domain models (50 problems)",
        problem_domain="extension/c",
    )
    dag.add_node(
        "extension_cython",
        deps=["extension_c", "bindings_cython"],
        description="Cython extensions — Python-native, visualization, deployment (50 problems)",
        problem_domain="extension/cython",
    )
    dag.add_node(
        "plugins_c",
        deps=["bindings_c"],
        description="C plugins — auth, storage, compute, monitoring (50 problems)",
        problem_domain="plugins/c",
    )
    dag.add_node(
        "plugins_cython",
        deps=["plugins_c", "bindings_cython"],
        description="Cython plugins — web frameworks, ML platforms, cloud, security (50 problems)",
        problem_domain="plugins/cython",
    )
    dag.add_node(
        "sdk_c",
        deps=["extension_c", "plugins_c", "drivers"],
        description="C SDK — API design, build system, testing, distribution (50 problems)",
        problem_domain="sdk/c",
    )
    dag.add_node(
        "sdk_cython",
        deps=["extension_cython", "plugins_cython", "sdk_c"],
        description="Cython SDK — Pythonic API, docs, packaging, IDE integration (50 problems)",
        problem_domain="sdk/cython",
    )
    dag.add_node(
        "misc",
        deps=["sdk_cython"],
        description="Utilities, devops, docs, operations, community (50 problems)",
        problem_domain="misc",
    )

    return dag


if __name__ == "__main__":
    dag = build_obiai_dag()
    dag.print_graph()
    order = dag.topological_sort()
    print("Build order:", " → ".join(order))
    sys.exit(0)
