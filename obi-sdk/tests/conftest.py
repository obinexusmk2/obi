"""
Pytest configuration for OBIAI SDK tests
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "wsl: marks tests as WSL-specific"
    )
    config.addinivalue_line(
        "markers", "windows: marks tests as Windows-specific"
    )
