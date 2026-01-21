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


# ========== Additional Test Fixtures ==========


@pytest.fixture
def mock_audio_bytes() -> bytes:
    """Generate mock WAV audio bytes for testing.

    Creates a simple 16-bit mono WAV file with a 440Hz sine wave.
    """
    import io
    import struct
    import wave

    import numpy as np

    sr = 16000
    duration = 1.0
    samples = int(sr * duration)

    t = np.linspace(0, duration, samples)
    audio = (np.sin(2 * np.pi * 440 * t) * 32767 * 0.5).astype(np.int16)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(audio.tobytes())

    return buffer.getvalue()


@pytest.fixture
def mock_stereo_audio() -> tuple:
    """Generate mock stereo audio arrays for testing.

    Returns:
        Tuple of (left_channel, right_channel, sample_rate)
    """
    import numpy as np

    sr = 16000
    duration = 1.0
    samples = int(sr * duration)

    t = np.linspace(0, duration, samples)
    left = (np.sin(2 * np.pi * 440 * t) * 0.8).astype(np.float32)  # 440 Hz
    right = (np.sin(2 * np.pi * 880 * t) * 0.5).astype(np.float32)  # 880 Hz

    return left, right, sr


@pytest.fixture
def mock_whisper_model():
    """Create a mock Whisper model for testing.

    Returns a MagicMock that simulates whisper.load_model() output.
    """
    from unittest.mock import MagicMock

    model = MagicMock()
    model.transcribe.return_value = {
        "text": "Hello, this is a test transcription.",
        "language": "en",
        "segments": [{"start": 0.0, "end": 2.5, "text": "Hello, this is a test transcription."}],
    }
    return model


@pytest.fixture
def mock_openai_response():
    """Create a mock successful OpenAI API response."""
    from unittest.mock import MagicMock

    choice = MagicMock()
    choice.message.content = '{"score": 8, "feedback": "Good performance"}'

    response = MagicMock()
    response.choices = [choice]
    response.model = "gpt-4"
    response.usage.prompt_tokens = 100
    response.usage.completion_tokens = 50

    return response


@pytest.fixture
def mock_openai_rate_limit():
    """Create a mock OpenAI 429 rate limit error."""
    from unittest.mock import MagicMock

    try:
        from openai import RateLimitError

        response = MagicMock()
        response.status_code = 429

        return RateLimitError(
            message="Rate limit exceeded. Please retry after 60 seconds.",
            response=response,
            body=None,
        )
    except ImportError:
        # OpenAI not installed, return None
        return None


@pytest.fixture
def sample_scoring_parameters() -> list:
    """Sample scoring parameters for audit testing."""
    return [
        {"name": "greeting", "max_score": 10, "weight": 1.0, "description": "Proper greeting"},
        {
            "name": "active_listening",
            "max_score": 10,
            "weight": 1.5,
            "description": "Shows engagement",
        },
        {
            "name": "problem_identification",
            "max_score": 10,
            "weight": 1.5,
            "description": "Identifies issue",
        },
        {
            "name": "solution_provided",
            "max_score": 10,
            "weight": 2.0,
            "description": "Provides solution",
        },
        {"name": "closing", "max_score": 10, "weight": 1.0, "description": "Proper closing"},
    ]


@pytest.fixture
def sample_llm_audit_response() -> dict:
    """Sample LLM response for audit testing."""
    return {
        "parameter_scores": {
            "greeting": {"score": 8.5, "feedback": "Professional greeting"},
            "active_listening": {"score": 7.5, "feedback": "Shows engagement"},
            "problem_identification": {"score": 8.0, "feedback": "Correctly identified issue"},
            "solution_provided": {"score": 7.0, "feedback": "Adequate solution"},
            "closing": {"score": 7.5, "feedback": "Proper closing"},
        },
        "strengths": [
            "Professional tone throughout the call",
            "Clear communication",
        ],
        "improvements": [
            "Could provide more detailed solutions",
            "Follow up on customer concerns",
        ],
        "summary": "Overall good call with room for improvement in solution depth.",
    }


@pytest.fixture
def error_handler_reset():
    """Reset ErrorHandler singleton between tests.

    Use this fixture when testing ErrorHandler to ensure a clean state.
    """
    from localmind.utils.error_handler import ErrorHandler

    # Store original instance
    original_instance = ErrorHandler._instance

    # Reset singleton
    ErrorHandler._instance = None

    yield

    # Restore original instance after test
    ErrorHandler._instance = original_instance


@pytest.fixture
def mock_llm_timeout():
    """Mock LLM provider that times out.

    Returns an async mock that raises asyncio.TimeoutError.
    """
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    provider = MagicMock()
    provider.provider_name = "mock_timeout"
    provider.model = "mock-model"
    provider._is_initialized = True

    async def timeout_generate(*args, **kwargs):
        raise asyncio.TimeoutError("Request timed out")

    provider.generate = AsyncMock(side_effect=timeout_generate)
    provider.initialize = AsyncMock()
    provider.close = AsyncMock()

    return provider


@pytest.fixture
def mock_orchestrator(qapp):
    """Mock ProcessingOrchestrator for UI tests.

    Returns a MagicMock with all signals as MagicMock objects.
    """
    from unittest.mock import MagicMock

    orchestrator = MagicMock()
    orchestrator.is_processing = False
    orchestrator._should_stop = False

    # Mock signals
    orchestrator.stage_started = MagicMock()
    orchestrator.stage_progress = MagicMock()
    orchestrator.stage_completed = MagicMock()
    orchestrator.stage_error = MagicMock()
    orchestrator.processing_complete = MagicMock()
    orchestrator.processing_error = MagicMock()

    return orchestrator


@pytest.fixture
def sample_mono_audio_file(temp_dir) -> Path:
    """Create a temporary mono WAV file.

    Returns:
        Path to the mono audio file.
    """
    import numpy as np
    import soundfile as sf

    audio_path = temp_dir / "mono_test.wav"
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)

    # Generate mono audio (sine wave)
    t = np.linspace(0, duration, samples)
    audio_data = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)

    sf.write(str(audio_path), audio_data, sample_rate)
    return audio_path


@pytest.fixture
def sample_stereo_audio_file(temp_dir) -> Path:
    """Create a temporary stereo WAV file.

    Returns:
        Path to the stereo audio file.
    """
    import numpy as np
    import soundfile as sf

    audio_path = temp_dir / "stereo_test.wav"
    sample_rate = 16000
    duration = 1.0
    samples = int(sample_rate * duration)

    # Generate stereo audio (different frequencies for L/R)
    t = np.linspace(0, duration, samples)
    left = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)
    right = (np.sin(2 * np.pi * 880 * t) * 0.5).astype(np.float32)
    stereo = np.column_stack([left, right])

    sf.write(str(audio_path), stereo, sample_rate)
    return audio_path


@pytest.fixture
def mock_librosa():
    """Mock librosa for audio detection tests.

    Returns a mock with load() configured for testing.
    """
    from unittest.mock import MagicMock, patch

    import numpy as np

    mock = MagicMock()

    # Mock load to return mono audio by default
    mock.load.return_value = (np.zeros(16000, dtype=np.float32), 16000)

    return mock
