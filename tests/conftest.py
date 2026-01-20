"""
LocalMind Test Configuration

Pytest fixtures and configuration for testing.
"""

import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_settings(temp_dir: Path, monkeypatch):
    """Create mock settings with temporary directory."""
    from localmind.config.settings import SettingsManager

    # Create a settings manager and override its paths
    manager = SettingsManager()
    manager._config_dir = temp_dir
    manager._config_file = temp_dir / "settings.json"

    # Patch only the settings module level variable
    monkeypatch.setattr("localmind.config.settings._settings_manager", manager)

    return manager


@pytest.fixture
def sample_audit_result() -> dict:
    """Sample audit result for testing."""
    return {
        "overall_score": 75.5,
        "max_score": 100.0,
        "compliance_score": 80.0,
        "quality_score": 72.0,
        "parameter_scores": {
            "greeting": {"score": 8.0, "max": 10, "weight": 1.0, "feedback": "Good greeting"},
            "active_listening": {
                "score": 7.5,
                "max": 10,
                "weight": 1.5,
                "feedback": "Shows engagement",
            },
            "problem_identification": {
                "score": 8.0,
                "max": 10,
                "weight": 1.5,
                "feedback": "Correctly identified issue",
            },
            "solution_provided": {
                "score": 7.0,
                "max": 10,
                "weight": 2.0,
                "feedback": "Adequate solution",
            },
            "communication_clarity": {
                "score": 8.5,
                "max": 10,
                "weight": 1.0,
                "feedback": "Clear communication",
            },
        },
        "strengths": [
            "Good rapport building",
            "Clear communication",
            "Professional tone",
        ],
        "improvements": [
            "Could provide more detailed solutions",
            "Follow up on customer concerns",
        ],
        "summary": "Overall good call with room for improvement in solution depth.",
        "transcript": "[Agent] Hello, thank you for calling.\n[Customer] Hi, I need help with my order.\n[Agent] I'd be happy to help you with that.",
    }


@pytest.fixture
def sample_transcription_segments() -> list:
    """Sample transcription segments for testing."""
    return [
        {"start": 0.0, "end": 2.5, "text": "Hello, thank you for calling.", "speaker": "Agent"},
        {"start": 2.5, "end": 5.0, "text": "Hi, I need help with my order.", "speaker": "Customer"},
        {
            "start": 5.0,
            "end": 8.0,
            "text": "I'd be happy to help you with that.",
            "speaker": "Agent",
        },
    ]


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider for testing."""
    from localmind.llm.base import LLMResponse

    provider = MagicMock()
    provider.provider_name = "mock"
    provider.model = "mock-model"
    provider.is_initialized = True

    async def mock_generate(*args, **kwargs):
        return LLMResponse(
            content='{"score": 8, "feedback": "Good performance"}',
            model="mock-model",
            provider="mock",
            usage={"input_tokens": 100, "output_tokens": 50},
        )

    provider.generate = mock_generate
    provider.generate_json = MagicMock(return_value={"score": 8, "feedback": "Good"})

    return provider


@pytest.fixture
def sample_transcription_result() -> dict:
    """Sample transcription result for testing."""
    return {
        "text": "Hello, thank you for calling. Hi, I need help with my order. I'd be happy to help you with that.",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "Hello, thank you for calling.", "speaker": "Agent"},
            {
                "start": 2.5,
                "end": 5.0,
                "text": "Hi, I need help with my order.",
                "speaker": "Customer",
            },
            {
                "start": 5.0,
                "end": 8.0,
                "text": "I'd be happy to help you with that.",
                "speaker": "Agent",
            },
        ],
        "language": "en",
        "duration": 8.0,
    }


@pytest.fixture
def sample_merge_result() -> dict:
    """Sample merge result for testing."""
    return {
        "merged_text": "[Agent] Hello, thank you for calling.\n[Customer] Hi, I need help with my order.\n[Agent] I'd be happy to help you with that.",
        "segments": [
            {"start": 0.0, "end": 2.5, "text": "Hello, thank you for calling.", "speaker": "Agent"},
            {
                "start": 2.5,
                "end": 5.0,
                "text": "Hi, I need help with my order.",
                "speaker": "Customer",
            },
            {
                "start": 5.0,
                "end": 8.0,
                "text": "I'd be happy to help you with that.",
                "speaker": "Agent",
            },
        ],
        "summary": "Customer called about order issue. Agent provided assistance.",
    }


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for GUI tests."""
    from PySide6.QtWidgets import QApplication

    # Check if app already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app
