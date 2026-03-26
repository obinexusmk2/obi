#!/usr/bin/env python3
"""
build_cython.py - Cython extension definitions for the OBIAI SDK obi/ workspace.

Provides get_extensions() consumed by the root setup.py. Platform detection
mirrors the logic from the original obi-sdk/setup.py but with corrected paths
rooted at obi/ instead of obi-sdk/.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import List, Optional, Tuple

# Setuptools / Cython imports are deferred so this module can be imported
# outside a build context (e.g. for testing path logic).
_MISSING: List[str] = []
try:
    import numpy as np
except ImportError:
    _MISSING.append("numpy")
try:
    from setuptools import Extension
except ImportError:
    _MISSING.append("setuptools")

_IMPORTS_OK = len(_MISSING) == 0


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

IS_WINDOWS = platform.system() == "Windows"
IS_WSL = "microsoft" in platform.release().lower() or "WSL" in platform.release()
IS_LINUX = platform.system() == "Linux" and not IS_WSL


def _compile_args() -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
    """Return (extra_compile_args, extra_link_args, define_macros) for this platform."""
    compile_args: List[str] = []
    link_args: List[str] = []
    macros: List[Tuple[str, str]] = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]

    if IS_WINDOWS:
        compile_args.extend(["/O2", "/W3", "/GL", "/MD", "/std:c11"])
        link_args.extend(["/LTCG", "/DLL"])
        macros.extend([("WIN32", "1"), ("_WINDOWS", "1"), ("OBI_EXPORTS", "1")])
    elif IS_WSL or IS_LINUX:
        compile_args.extend([
            "-O3", "-march=native", "-fPIC", "-Wall", "-Wextra",
            "-fvisibility=hidden", "-std=c11", "-ffast-math",
        ])
        link_args.extend(["-shared", "-fvisibility=hidden"])
        if IS_WSL:
            macros.append(("WSL_BUILD", "1"))

    return compile_args, link_args, macros


# ---------------------------------------------------------------------------
# Extension factory
# ---------------------------------------------------------------------------

def get_extensions(
    monorepo_root: Path,
    extra_include_dirs: Optional[List[str]] = None,  # noqa: F821
    extra_lib_dirs: Optional[List[str]] = None,
    extra_libraries: Optional[List[str]] = None,
) -> List["Extension"]:  # noqa: F821
    """
    Return Cython Extension objects for all obi.* Cython modules.

    Args:
        monorepo_root:      Absolute path to the obiai-sdk/ root.
        extra_include_dirs: Additional -I paths (e.g. libpolycall-v1/include).
        extra_lib_dirs:     Additional -L paths.
        extra_libraries:    Additional -l libraries.

    Returns:
        List[Extension] ready to be passed to cythonize().
    """
    if not _IMPORTS_OK:
        raise ImportError(
            f"Missing build dependencies: {', '.join(_MISSING)}\n"
            "Install with:\n"
            "  pip install numpy setuptools Cython\n"
            "or in conda:\n"
            "  conda install numpy setuptools cython"
        )

    compile_args, link_args, macros = _compile_args()

    include_dirs: List[str] = [
        np.get_include(),
        str(monorepo_root / "obi" / "bindings" / "c" / "include"),
        str(monorepo_root / "obi" / "bindings" / "cython"),
    ]
    if extra_include_dirs:
        include_dirs.extend(extra_include_dirs)

    lib_dirs: List[str] = list(extra_lib_dirs or [])
    libraries: List[str] = list(extra_libraries or [])

    # Resolve source paths relative to monorepo root
    core_pyx = str(monorepo_root / "obi" / "bindings" / "cython" / "_core.pyx")
    poly_pyx = str(monorepo_root / "obi" / "drivers" / "core" / "_poly_driver.pyx")

    extensions = [
        Extension(
            "obi.bindings._core",
            sources=[core_pyx],
            include_dirs=include_dirs,
            library_dirs=lib_dirs,
            libraries=libraries,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
            define_macros=macros,
            language="c",
        ),
        Extension(
            "obi.drivers._poly_driver",
            sources=[poly_pyx],
            include_dirs=include_dirs,
            library_dirs=lib_dirs,
            libraries=libraries,
            extra_compile_args=compile_args,
            extra_link_args=link_args,
            define_macros=macros,
            language="c",
        ),
    ]

    return extensions


# ---------------------------------------------------------------------------
# Cython compiler directives
# ---------------------------------------------------------------------------

CYTHON_DIRECTIVES: dict = {
    "language_level": "3",
    "embedsignature": True,
    "boundscheck": False,
    "wraparound": False,
    "cdivision": True,
    "profile": os.environ.get("CYTHON_TRACE", "0") == "1",
    "linetrace": os.environ.get("CYTHON_TRACE", "0") == "1",
}


# ---------------------------------------------------------------------------
# Standalone diagnostic
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parent.parent
    print(f"Monorepo root: {root}")
    print(f"Platform: Windows={IS_WINDOWS}, WSL={IS_WSL}, Linux={IS_LINUX}")

    # Probe libpolycall-v1
    libpoly = os.environ.get("LIBPOLYCALL_ROOT", str(root / "obi-sdk" / "libpolycall-v1"))
    libpoly_path = Path(libpoly)
    print(f"libpolycall-v1: {libpoly_path} ({'found' if libpoly_path.exists() else 'NOT FOUND'})")

    if _IMPORTS_OK:
        extra_incs = [str(libpoly_path / "include")] if libpoly_path.exists() else []
        extra_libs = [str(libpoly_path / "lib")] if libpoly_path.exists() else []
        extra_libnames = ["polycall"] if libpoly_path.exists() else []
        exts = get_extensions(root, extra_incs, extra_libs, extra_libnames)
        print("\nExtensions:")
        for ext in exts:
            print(f"  {ext.name}")
            print(f"    sources: {ext.sources}")
    else:
        print("\n[WARN] numpy/setuptools not available — skipping extension list.")

    sys.exit(0)
