#!/usr/bin/env python3
"""
OBIAI SDK - Root setup.py

Builds Cython extensions for the obi.* namespace.
Run from: C:\\Users\\OBINexus\\Projects\\obiai-sdk\\
    python setup.py build_ext --inplace

All source paths are relative to this file (the monorepo root), NOT to obi-sdk/.
"""

import os
import platform
import sys
from pathlib import Path

from setuptools import setup, find_packages
from Cython.Build import cythonize

IS_WINDOWS = platform.system() == "Windows"

# Resolve monorepo root (same directory as this file)
MONOREPO_ROOT = Path(__file__).resolve().parent

# Add scripts/ to path so we can import build helpers
sys.path.insert(0, str(MONOREPO_ROOT / "scripts"))
from build_cython import get_extensions, CYTHON_DIRECTIVES  # noqa: E402

# ---------------------------------------------------------------------------
# libpolycall-v1 location
# Only link against it if the compiled library actually exists on disk.
# The directory may exist (e.g. empty clone) without a built library.
# ---------------------------------------------------------------------------
LIBPOLYCALL_ROOT = Path(
    os.environ.get("LIBPOLYCALL_ROOT", str(MONOREPO_ROOT / "obi-sdk" / "libpolycall-v1"))
)

extra_include_dirs = []
extra_lib_dirs = []
extra_libraries = []

if LIBPOLYCALL_ROOT.exists():
    inc = LIBPOLYCALL_ROOT / "include"
    lib_dir = LIBPOLYCALL_ROOT / "lib"
    built_so = LIBPOLYCALL_ROOT / "build" / "libpolycall.so"
    built_dll = LIBPOLYCALL_ROOT / "build" / "Release" / "polycall.dll"

    if inc.exists():
        extra_include_dirs.append(str(inc))

    # Only add linker flags if the library is actually compiled
    if built_so.exists() or built_dll.exists():
        if lib_dir.exists():
            extra_lib_dirs.append(str(lib_dir))
        extra_libraries.append("polycall")
        print(f"INFO: Linking against libpolycall-v1 at {LIBPOLYCALL_ROOT}")
    else:
        print(
            f"INFO: libpolycall-v1 source found at {LIBPOLYCALL_ROOT} but not yet built.\n"
            "      Building without polycall linkage (stub-only mode).\n"
            "      To enable: build libpolycall-v1 first, then re-run setup.py.",
            file=sys.stderr,
        )
else:
    print(f"INFO: libpolycall-v1 not found at {LIBPOLYCALL_ROOT} — stub-only build.", file=sys.stderr)

# ---------------------------------------------------------------------------
# Cython extensions (paths rooted at obi/)
# ---------------------------------------------------------------------------
EXTENSIONS = get_extensions(
    MONOREPO_ROOT,
    extra_include_dirs=extra_include_dirs,
    extra_lib_dirs=extra_lib_dirs,
    extra_libraries=extra_libraries,
)

ext_modules = cythonize(
    EXTENSIONS,
    compiler_directives=CYTHON_DIRECTIVES,
    annotate=os.environ.get("CYTHON_ANNOTATE", "0") == "1",
    # nthreads > 0 uses multiprocessing which requires if __name__=='__main__'
    # on Windows (spawn-based). Always use 0 (single-threaded) to avoid the
    # RuntimeError: "attempt to start new process before bootstrapping" crash.
    nthreads=0 if IS_WINDOWS else int(os.environ.get("CYTHON_NTHREADS", "4")),
)

# ---------------------------------------------------------------------------
# Custom build_ext: build libpolycall-v1 first if needed, copy DLLs on Windows
# ---------------------------------------------------------------------------

from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    def run(self):
        self._build_libpolycall()
        super().run()
        if IS_WINDOWS:
            self._copy_windows_dlls()

    def _build_libpolycall(self):
        if not LIBPOLYCALL_ROOT.exists():
            return
        cmake_lists = LIBPOLYCALL_ROOT / "CMakeLists.txt"
        if not cmake_lists.exists():
            print(
                f"INFO: Skipping libpolycall-v1 build — CMakeLists.txt not found at {LIBPOLYCALL_ROOT}",
                file=sys.stderr,
            )
            return
        build_dir = LIBPOLYCALL_ROOT / "build"
        so = build_dir / "libpolycall.so"
        dll = build_dir / "Release" / "polycall.dll"
        if so.exists() or dll.exists():
            return
        print("Building libpolycall-v1...")
        import subprocess
        build_dir.mkdir(exist_ok=True)
        cmake_args = ["-DCMAKE_BUILD_TYPE=Release"]
        if IS_WINDOWS:
            cmake_args.append("-A x64")
        subprocess.run(["cmake", str(LIBPOLYCALL_ROOT)] + cmake_args, cwd=build_dir, check=True)
        subprocess.run(
            ["cmake", "--build", ".", "--config", "Release"],
            cwd=build_dir,
            check=True,
        )

    def _copy_windows_dlls(self):
        import shutil
        dll_source = LIBPOLYCALL_ROOT / "build" / "Release" / "polycall.dll"
        if not dll_source.exists():
            return
        for ext in self.extensions:
            ext_path = Path(self.get_ext_fullpath(ext.name))
            shutil.copy2(dll_source, ext_path.parent)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
setup(
    name="obi-sdk",
    version="0.1.0-alpha",
    description="Ontological Bayesian Intelligence SDK — obi namespace",
    author="Nnamdi Michael Okpala",
    license="MIT",
    packages=find_packages(include=["obi", "obi.*"]),
    package_dir={"": "."},
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.9",
)
