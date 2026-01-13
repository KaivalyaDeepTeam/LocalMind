"""
Unit tests for LocalMind workers module.
"""

import pytest
from unittest.mock import MagicMock, patch

from localmind.workers.base import BaseWorker, WorkerState
from localmind.workers.transcription_worker import (
    TranscriptionResult,
    TranscriptionSegment,
)
from localmind.workers.merge_worker import MergeResult, MergedSegment
from localmind.workers.audit_worker import (
    AuditResult,
    ParameterScore,
    DEFAULT_PARAMETERS,
)
from localmind.workers.model_download_worker import (
    ModelInfo,
    ModelType,
    AVAILABLE_MODELS,
    SetupWizardData,
)


class TestWorkerState:
    """Tests for WorkerState enum."""

    def test_all_states(self):
        """Test all worker states exist."""
        states = [
            WorkerState.IDLE,
            WorkerState.RUNNING,
            WorkerState.PAUSED,
            WorkerState.STOPPING,
            WorkerState.FINISHED,
            WorkerState.ERROR,
        ]

        for state in states:
            assert isinstance(state, WorkerState)


class TestTranscriptionResult:
    """Tests for TranscriptionResult."""

    def test_create_result(self):
        """Test creating a transcription result."""
        segments = [
            TranscriptionSegment(start=0.0, end=2.0, text="Hello"),
            TranscriptionSegment(start=2.0, end=4.0, text="World"),
        ]

        result = TranscriptionResult(
            text="Hello World",
            segments=segments,
            language="en",
            duration=4.0,
        )

        assert result.text == "Hello World"
        assert len(result.segments) == 2
        assert result.language == "en"
        assert result.duration == 4.0

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = TranscriptionResult(
            text="Test",
            segments=[TranscriptionSegment(start=0.0, end=1.0, text="Test")],
            language="en",
        )

        data = result.to_dict()

        assert data["text"] == "Test"
        assert len(data["segments"]) == 1
        assert data["language"] == "en"


class TestTranscriptionSegment:
    """Tests for TranscriptionSegment."""

    def test_create_segment(self):
        """Test creating a segment."""
        seg = TranscriptionSegment(
            start=0.0,
            end=2.5,
            text="Hello there",
            speaker="Agent",
            confidence=0.95,
        )

        assert seg.start == 0.0
        assert seg.end == 2.5
        assert seg.text == "Hello there"
        assert seg.speaker == "Agent"
        assert seg.confidence == 0.95

    def test_to_dict(self):
        """Test converting segment to dictionary."""
        seg = TranscriptionSegment(start=1.0, end=3.0, text="Test", speaker="Customer")
        data = seg.to_dict()

        assert data["start"] == 1.0
        assert data["end"] == 3.0
        assert data["text"] == "Test"
        assert data["speaker"] == "Customer"


class TestMergeResult:
    """Tests for MergeResult."""

    def test_create_result(self):
        """Test creating a merge result."""
        segments = [
            MergedSegment(start=0.0, end=2.0, speaker="Agent", text="Hello"),
            MergedSegment(start=2.0, end=4.0, speaker="Customer", text="Hi"),
        ]

        result = MergeResult(
            merged_text="[Agent] Hello\n[Customer] Hi",
            segments=segments,
            summary="Test call",
        )

        assert len(result.segments) == 2
        assert result.summary == "Test call"

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = MergeResult(
            merged_text="Test",
            segments=[MergedSegment(start=0.0, end=1.0, speaker="Agent", text="Test")],
        )

        data = result.to_dict()

        assert data["merged_text"] == "Test"
        assert len(data["segments"]) == 1


class TestAuditResult:
    """Tests for AuditResult."""

    def test_create_result(self):
        """Test creating an audit result."""
        scores = [
            ParameterScore(name="greeting", score=8.0, max_score=10.0, weight=1.0),
            ParameterScore(name="empathy", score=7.0, max_score=10.0, weight=1.5),
        ]

        result = AuditResult(
            overall_score=75.0,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["Good greeting"],
            improvements=["More empathy"],
            summary="Good call",
        )

        assert result.overall_score == 75.0
        assert len(result.parameter_scores) == 2
        assert len(result.strengths) == 1
        assert len(result.improvements) == 1

    def test_percentage(self):
        """Test percentage calculation."""
        result = AuditResult(overall_score=75.0, max_score=100.0)
        assert result.percentage == 75.0

        result2 = AuditResult(overall_score=0.0, max_score=0.0)
        assert result2.percentage == 0.0

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = AuditResult(
            overall_score=80.0,
            max_score=100.0,
            compliance_score=85.0,
            quality_score=75.0,
            summary="Test",
        )

        data = result.to_dict()

        assert data["overall_score"] == 80.0
        assert data["compliance_score"] == 85.0
        assert data["quality_score"] == 75.0


class TestParameterScore:
    """Tests for ParameterScore."""

    def test_create_score(self):
        """Test creating a parameter score."""
        score = ParameterScore(
            name="greeting",
            score=8.5,
            max_score=10.0,
            weight=1.5,
            feedback="Good greeting",
        )

        assert score.name == "greeting"
        assert score.score == 8.5
        assert score.max_score == 10.0
        assert score.weight == 1.5

    def test_weighted_score(self):
        """Test weighted score calculation."""
        score = ParameterScore(name="test", score=8.0, max_score=10.0, weight=1.5)

        assert score.weighted_score == 12.0  # 8.0 * 1.5
        assert score.weighted_max == 15.0  # 10.0 * 1.5


class TestDefaultParameters:
    """Tests for default audit parameters."""

    def test_default_parameters_exist(self):
        """Test that default parameters are defined."""
        assert len(DEFAULT_PARAMETERS) > 0

    def test_default_parameters_structure(self):
        """Test default parameters have required fields."""
        for param in DEFAULT_PARAMETERS:
            assert "name" in param
            assert "max_score" in param
            assert "weight" in param
            assert "description" in param


class TestModelInfo:
    """Tests for ModelInfo."""

    def test_create_model_info(self):
        """Test creating model info."""
        info = ModelInfo(
            name="test-model",
            display_name="Test Model",
            model_type=ModelType.WHISPER,
            size_gb=1.5,
            repo_id="test/model",
            filename="model.bin",
            description="Test description",
        )

        assert info.name == "test-model"
        assert info.model_type == ModelType.WHISPER
        assert info.size_gb == 1.5


class TestAvailableModels:
    """Tests for available models."""

    def test_available_models_exist(self):
        """Test that available models are defined."""
        assert len(AVAILABLE_MODELS) > 0

    def test_whisper_models_exist(self):
        """Test that Whisper models are included."""
        whisper_models = [m for m in AVAILABLE_MODELS if m.model_type == ModelType.WHISPER]
        assert len(whisper_models) > 0

    def test_local_llm_models_exist(self):
        """Test that local LLM models are included."""
        llm_models = [m for m in AVAILABLE_MODELS if m.model_type == ModelType.LOCAL_LLM]
        assert len(llm_models) > 0

    def test_required_models(self):
        """Test that required models are marked."""
        required = [m for m in AVAILABLE_MODELS if m.required]
        assert len(required) > 0


class TestSetupWizardData:
    """Tests for SetupWizardData."""

    def test_default_values(self):
        """Test default wizard data values."""
        data = SetupWizardData()

        assert data.whisper_model == "whisper-large-v3"
        assert data.download_local_llm is False
        assert data.use_gpu is True

    def test_get_models_to_download(self):
        """Test getting models to download."""
        data = SetupWizardData()
        models = data.get_models_to_download()

        assert len(models) >= 1
        assert any(m.name == "whisper-large-v3" for m in models)

    def test_get_models_with_llm(self):
        """Test getting models with LLM enabled."""
        data = SetupWizardData()
        data.download_local_llm = True
        data.local_llm_model = "phi-3.5-mini"

        models = data.get_models_to_download()

        assert len(models) >= 2
        assert any(m.name == "phi-3.5-mini" for m in models)

    def test_get_total_download_size(self):
        """Test calculating total download size."""
        data = SetupWizardData()
        size = data.get_total_download_size()

        assert size > 0
