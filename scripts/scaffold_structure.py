#!/usr/bin/env python3
"""
scaffold_structure.py - Directory and stub-file creation utilities for the OBIAI monorepo.

Provides safe, idempotent operations for building out the obi/ workspace tree,
migrating existing .pyx/.pxd/.h files, and writing __init__.py stubs.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def create_directory(path: Path) -> bool:
    """Create directory (and parents) if it doesn't exist. Returns True if created."""
    if path.exists():
        return False
    path.mkdir(parents=True, exist_ok=True)
    print(f"  [mkdir] {path}")
    return True


def write_init_stub(
    directory: Path,
    module_name: str,
    description: str = "",
    exports: Optional[List[str]] = None,
) -> bool:
    """
    Write an __init__.py stub into *directory* if one doesn't already exist.

    Returns True if the file was written (new), False if it already existed.
    """
    init_path = directory / "__init__.py"
    if init_path.exists():
        return False

    lines = [
        '"""',
        f"{module_name}",
    ]
    if description:
        lines.append("")
        lines.append(description)
    lines += ['"""', ""]

    if exports:
        lines.append("__all__ = [")
        for name in exports:
            lines.append(f'    "{name}",')
        lines.append("]")
        lines.append("")

    init_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [stub]  {init_path}")
    return True


def copy_file_if_newer(src: Path, dst: Path) -> bool:
    """
    Copy src → dst only if:
      - dst doesn't exist, OR
      - src is newer than dst (by mtime).

    Returns True if the file was copied.
    """
    if not src.exists():
        print(f"  [WARN]  Source not found, skipping: {src}")
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        if src.stat().st_mtime <= dst.stat().st_mtime:
            print(f"  [skip]  Up-to-date: {dst.name}")
            return False

    shutil.copy2(src, dst)
    action = "update" if dst.exists() else "copy"
    print(f"  [{action}] {src.name} → {dst}")
    return True


def copy_tree_if_newer(src_dir: Path, dst_dir: Path, glob: str = "**/*") -> int:
    """
    Recursively copy all files matching *glob* from src_dir into dst_dir,
    preserving relative structure. Skips directories. Returns count copied.
    """
    if not src_dir.exists():
        print(f"  [WARN]  Source dir not found, skipping: {src_dir}")
        return 0

    count = 0
    for src_file in src_dir.glob(glob):
        if src_file.is_dir():
            continue
        rel = src_file.relative_to(src_dir)
        dst_file = dst_dir / rel
        if copy_file_if_newer(src_file, dst_file):
            count += 1
    return count


# ---------------------------------------------------------------------------
# Module spec scaffolding
# ---------------------------------------------------------------------------

# Each entry: (relative_dir, module_display_name, description)
OBI_MODULE_SPECS: List[tuple[str, str, str]] = [
    (
        "obi",
        "obi",
        "Ontological Bayesian Intelligence — top-level package namespace",
    ),
    (
        "obi/bindings",
        "obi.bindings",
        "FFI bindings: C layer and Cython wrappers for libpolycall-v1",
    ),
    (
        "obi/bindings/c",
        "obi.bindings.c",
        "C binding utilities — 50 problems: ABI, memory safety, epistemic integration",
    ),
    (
        "obi/bindings/cython",
        "obi.bindings.cython",
        "Cython bindings — 50 problems: GIL, NumPy, data science, deployment",
    ),
    (
        "obi/drivers",
        "obi.drivers",
        "Driver layer — PolyDriver, DimensionalReasoner, dimensional game theory",
    ),
    (
        "obi/drivers/core",
        "obi.drivers.core",
        "Core drivers: mixed-strategy Nash solvers, bidirectional reasoning",
    ),
    (
        "obi/extension",
        "obi.extension",
        "Extension subsystem — plugin ABI and domain-specific extensions",
    ),
    (
        "obi/extension/c",
        "obi.extension.c",
        "C extensions — 50 problems: systems programming, real-time, safety, hardware",
    ),
    (
        "obi/extension/cython",
        "obi.extension.cython",
        "Cython extensions — 50 problems: Python-native, visualization, deployment",
    ),
    (
        "obi/plugins",
        "obi.plugins",
        "Plugin framework — authentication, storage, compute, monitoring",
    ),
    (
        "obi/plugins/c",
        "obi.plugins.c",
        "C plugins — 50 problems: auth, storage, compute, monitoring",
    ),
    (
        "obi/plugins/cython",
        "obi.plugins.cython",
        "Cython plugins — 50 problems: web frameworks, ML platforms, cloud, security",
    ),
    (
        "obi/sdk",
        "obi.sdk",
        "SDK layer — developer-facing C and Python APIs",
    ),
    (
        "obi/sdk/c",
        "obi.sdk.c",
        "C SDK — 50 problems: API design, build system, testing, distribution",
    ),
    (
        "obi/sdk/cython",
        "obi.sdk.cython",
        "Cython SDK — 50 problems: Pythonic API, docs, packaging, IDE integration",
    ),
    (
        "obi/misc",
        "obi.misc",
        "Utilities, devops, docs, operations, community (50 problems)",
    ),
]


def scaffold_obi_workspace(monorepo_root: Path) -> None:
    """
    Create the full obi/ directory tree under *monorepo_root* with __init__.py stubs.
    Idempotent — safe to run multiple times.
    """
    print("\n[scaffold] Creating obi/ workspace structure...")
    for rel, module_name, desc in OBI_MODULE_SPECS:
        directory = monorepo_root / rel
        create_directory(directory)
        write_init_stub(directory, module_name, desc)

    # include/ directory for C headers (no __init__.py)
    include_dir = monorepo_root / "obi" / "bindings" / "c" / "include"
    create_directory(include_dir)
    print("[scaffold] obi/ workspace structure complete.\n")


# ---------------------------------------------------------------------------
# File migration helpers
# ---------------------------------------------------------------------------

def migrate_pyx_files(monorepo_root: Path) -> None:
    """
    Migrate existing .pyx and .pxd files from legacy locations into obi/.

    Migration map:
      bindings/cython/_core.pyx           → obi/bindings/cython/_core.pyx
      drivers/core/_poly_driver.pyx       → obi/drivers/core/_poly_driver.pyx
      obi-sdk/bindings/cython/*.pxd       → obi/bindings/cython/
      obi-sdk/bindings/c/include/*        → obi/bindings/c/include/
    """
    print("[migrate] Migrating .pyx / .pxd / header files...")

    migrations: List[tuple[Path, Path]] = [
        (
            monorepo_root / "bindings" / "cython" / "_core.pyx",
            monorepo_root / "obi" / "bindings" / "cython" / "_core.pyx",
        ),
        (
            monorepo_root / "drivers" / "core" / "_poly_driver.pyx",
            monorepo_root / "obi" / "drivers" / "core" / "_poly_driver.pyx",
        ),
        (
            monorepo_root / "obi-sdk" / "bindings" / "cython" / "libpolycall.pxd",
            monorepo_root / "obi" / "bindings" / "cython" / "libpolycall.pxd",
        ),
    ]

    for src, dst in migrations:
        copy_file_if_newer(src, dst)

    # Bulk-copy C headers
    copy_tree_if_newer(
        monorepo_root / "obi-sdk" / "bindings" / "c" / "include",
        monorepo_root / "obi" / "bindings" / "c" / "include",
    )

    print("[migrate] File migration complete.\n")


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

REQUIRED_FILES: List[str] = [
    "obi/__init__.py",
    "obi/bindings/__init__.py",
    "obi/bindings/c/__init__.py",
    "obi/bindings/cython/__init__.py",
    "obi/bindings/cython/_core.pyx",
    "obi/bindings/cython/libpolycall.pxd",
    "obi/drivers/__init__.py",
    "obi/drivers/core/__init__.py",
    "obi/drivers/core/_poly_driver.pyx",
    "obi/extension/__init__.py",
    "obi/extension/c/__init__.py",
    "obi/extension/cython/__init__.py",
    "obi/plugins/__init__.py",
    "obi/plugins/c/__init__.py",
    "obi/plugins/cython/__init__.py",
    "obi/sdk/__init__.py",
    "obi/sdk/c/__init__.py",
    "obi/sdk/cython/__init__.py",
    "obi/misc/__init__.py",
    "setup.py",
    "setup-obi-sdk-monorepo.py",
]


def verify_structure(monorepo_root: Path) -> bool:
    """
    Check that all required files exist. Prints a status line per file.
    Returns True if all checks pass.
    """
    print("\n[verify] Checking monorepo structure...")
    all_ok = True
    for rel in REQUIRED_FILES:
        path = monorepo_root / rel
        ok = path.exists()
        status = "OK " if ok else "MISSING"
        mark = "\u2713" if ok else "\u2717"
        print(f"  [{mark}] {status}  {rel}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("[verify] All checks passed.\n")
    else:
        print("[verify] Some files are missing. Run with --scaffold first.\n")

    return all_ok
