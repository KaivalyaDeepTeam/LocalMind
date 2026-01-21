"""
UI Test Configuration

Fixtures specific to UI component testing.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_app(qapp):
    """Create a mock QApplication with necessary attributes."""
    return qapp


@pytest.fixture
def mock_settings_manager():
    """Create a mock settings manager for UI tests."""
    mock = MagicMock()
    mock.app.theme = "light"
    mock.app.recent_files = []
    return mock


@pytest.fixture
def mock_subprocess_result():
    """Create a mock subprocess result for theme detection."""
    result = MagicMock()
    result.stdout = ""
    result.returncode = 0
    return result
