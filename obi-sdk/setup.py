#!/usr/bin/env python3
"""
OBIAI SDK Setup Script
Handles Cython compilation with platform-specific optimizations for WSL/Windows
"""

import os
import sys
import platform
from pathlib import Path

from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_WSL = "microsoft" in platform.release().lower() or "WSL" in platform.release()
IS_LINUX = platform.system() == "Linux" and not IS_WSL

# Compiler flags
EXTRA_COMPILE_ARGS = []
EXTRA_LINK_ARGS = []
DEFINE_MACROS = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]

if IS_WINDOWS:
    # MSVC flags
    EXTRA_COMPILE_ARGS.extend(["/O2", "/W3", "/GL", "/MD", "/std:c11"])
    EXTRA_LINK_ARGS.extend(["/LTCG", "/DLL"])
    DEFINE_MACROS.extend([("WIN32", "1"), ("_WINDOWS", "1"), ("OBI_EXPORTS", "1")])
elif IS_WSL or IS_LINUX:
    # GCC/Clang flags
    EXTRA_COMPILE_ARGS.extend([
        "-O3", "-march=native", "-fPIC", "-Wall", "-Wextra",
        "-fvisibility=hidden",  # Hide symbols by default
        "-std=c11", "-ffast-math"
    ])
    EXTRA_LINK_ARGS.extend(["-shared", "-fvisibility=hidden"])
    if IS_WSL:
        DEFINE_MACROS.append(("WSL_BUILD", "1"))

# Include directories
INCLUDE_DIRS = [
    np.get_include(),
    "bindings/c/include",
    "bindings/cython",
]

# Library directories (for libpolycall-v1)
LIBRARY_DIRS = []
LIBRARIES = []

# Try to find libpolycall-v1
LIBPOLYCALL_ROOT = os.environ.get("LIBPOLYCALL_ROOT", "../libpolycall-v1")
if Path(LIBPOLYCALL_ROOT).exists():
    INCLUDE_DIRS.append(f"{LIBPOLYCALL_ROOT}/include")
    LIBRARY_DIRS.append(f"{LIBPOLYCALL_ROOT}/lib")
    LIBRARIES.append("polycall")

# Cython extensions
EXTENSIONS = [
    Extension(
        "obi_sdk.bindings._core",
        sources=["bindings/cython/_core.pyx"],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        extra_link_args=EXTRA_LINK_ARGS,
        define_macros=DEFINE_MACROS,
        language="c",
    ),
    Extension(
        "obi_sdk.drivers._poly_driver",
        sources=["drivers/core/_poly_driver.pyx"],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        libraries=LIBRARIES,
        extra_compile_args=EXTRA_COMPILE_ARGS,
        extra_link_args=EXTRA_LINK_ARGS,
        define_macros=DEFINE_MACROS,
        language="c",
    ),
]

# Cython compiler directives
CYTHON_DIRECTIVES = {
    "language_level": "3",
    "embedsignature": True,
    "boundscheck": False,
    "wraparound": False,
    "cdivision": True,
    "profile": os.environ.get("CYTHON_TRACE", "0") == "1",
    "linetrace": os.environ.get("CYTHON_TRACE", "0") == "1",
}

# Custom build command to handle libpolycall-v1
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    def run(self):
        # Ensure libpolycall-v1 is built first
        self._build_libpolycall()
        super().run()
        
        # Post-build: copy DLLs on Windows
        if IS_WINDOWS:
            self._copy_windows_dlls()
    
    def _build_libpolycall(self):
        """Build libpolycall-v1 if not already built"""
        lib_root = Path(LIBPOLYCALL_ROOT)
        if not lib_root.exists():
            print(f"WARNING: libpolycall-v1 not found at {lib_root}")
            return
        
        build_dir = lib_root / "build"
        if not (build_dir / "libpolycall.so").exists() and not (build_dir / "polycall.dll").exists():
            print("Building libpolycall-v1...")
            import subprocess
            build_dir.mkdir(exist_ok=True)
            
            cmake_args = ["-DCMAKE_BUILD_TYPE=Release"]
            if IS_WINDOWS:
                cmake_args.append("-A x64")
            
            subprocess.run(["cmake", ".."] + cmake_args, cwd=build_dir, check=True)
            subprocess.run(["cmake", "--build", ".", "--config", "Release"], cwd=build_dir, check=True)
    
    def _copy_windows_dlls(self):
        """Copy required DLLs to package directory on Windows"""
        import shutil
        dll_source = Path(LIBPOLYCALL_ROOT) / "build" / "Release" / "polycall.dll"
        if dll_source.exists():
            for ext in self.extensions:
                ext_path = Path(self.get_ext_fullpath(ext.name))
                shutil.copy2(dll_source, ext_path.parent)

# Cythonize extensions
ext_modules = cythonize(
    EXTENSIONS,
    compiler_directives=CYTHON_DIRECTIVES,
    annotate=os.environ.get("CYTHON_ANNOTATE", "0") == "1",
    nthreads=int(os.environ.get("CYTHON_NTHREADS", "4")),
)

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_dir={"": "."},
    zip_safe=False,
)
