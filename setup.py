#!/usr/bin/env python3
"""
OBI SDK (Ontological Bayesian Intelligence) — setup.py

Build and install the OBI reasoning framework as pure Python.

Installation:
    pip install obi

Install in development mode:
    pip install -e .
"""

import os
import platform
from pathlib import Path

from setuptools import setup, find_packages

# Root directory (where this file lives)
ROOT = Path(__file__).resolve().parent

# Read the README for PyPI long description
README_PATH = ROOT / "README.md"
if README_PATH.exists():
    with open(README_PATH, "r", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = "Ontological Bayesian Intelligence SDK"

# Setup
setup(
    # Metadata
    name="obi",
    version="0.1.0-alpha",
    author="Nnamdi Michael Okpala",
    author_email="okpalan@protonmail.com",
    description="Ontological Bayesian Intelligence — A reasoning framework for bias-free, consensus systems",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/obinexusmk2/obi",
    license="MIT",

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # Package discovery
    packages=find_packages(include=["obi", "obi.*"]),
    package_dir={"": "."},

    # No Cython extensions - OBI is pure Python
    ext_modules=[],

    # Dependencies
    install_requires=[],

    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },

    # Build options
    zip_safe=False,
    include_package_data=True,

    # Python requirement
    python_requires=">=3.9",
)
