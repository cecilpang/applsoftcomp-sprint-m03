"""Pytest configuration and fixtures."""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def config_path():
    """Path to travel config."""
    return str(Path(__file__).parent.parent / "config" / "travel_sites.json")


@pytest.fixture
def templates_dir():
    """Path to templates directory."""
    return str(Path(__file__).parent.parent / "templates")


@pytest.fixture
def working_dir(tmp_path):
    """Temporary working directory."""
    return str(tmp_path / "trip_working")


@pytest.fixture(autouse=True)
def reset_imports():
    """Reset any cached imports between tests."""
    yield
