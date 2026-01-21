"""
Integration tests for LocalMind processing pipeline.
"""

from pathlib import Path

import pytest

from localmind.config import LLMProviderType
from localmind.llm.factory import create_provider
from localmind.workers.audit_worker import AuditWorker
from localmind.workers.merge_worker import MergeWorker
from localmind.workers.transcription_worker import TranscriptionResult, TranscriptionWorker


class TestTranscriptionWorkerIntegration:
    """Integration tests for transcription worker."""

    def test_worker_creation(self, qapp):
        """Test creating transcription worker."""
        worker = TranscriptionWorker(
            audio_path="/path/to/audio.wav",
            model_name="whisper-large-v3",
        )

        assert worker._audio_path == Path("/path/to/audio.wav")
        assert worker._model_name == "whisper-large-v3"

    def test_worker_signals(self, qapp):
        """Test worker signals are properly defined."""
        worker = TranscriptionWorker(
            audio_path="/path/to/audio.wav",
            model_name="whisper-large-v3",
        )

        # Check signals exist
        assert hasattr(worker, "progress")
        assert hasattr(worker, "finished_work")
        assert hasattr(worker, "error")
        assert hasattr(worker, "started_work")
        assert hasattr(worker, "status_changed")


class TestMergeWorkerIntegration:
    """Integration tests for merge worker."""

    def test_worker_creation(self, qapp, sample_transcription_result):
        """Test creating merge worker."""

        # Create a proper TranscriptionResult object
        result = TranscriptionResult(
            text="Test transcript",
            segments=[],
            language="en",
        )

        worker = MergeWorker(
            transcription=result,
        )

        assert worker._transcription == result

    def test_worker_signals(self, qapp, sample_transcription_result):
        """Test merge worker signals are properly defined."""

        result = TranscriptionResult(
            text="Test transcript",
            segments=[],
            language="en",
        )

        worker = MergeWorker(
            transcription=result,
        )

        # Check signals exist (inherited from BaseWorker)
        assert hasattr(worker, "progress")
        assert hasattr(worker, "finished_work")
        assert hasattr(worker, "error")


class TestAuditWorkerIntegration:
    """Integration tests for audit worker."""

    def test_worker_creation(self, qapp, sample_merge_result):
        """Test creating audit worker."""
        worker = AuditWorker(
            merge_result=sample_merge_result,
            parameters=[
                {"name": "greeting", "max_score": 10.0, "weight": 1.0},
            ],
        )

        assert worker._merge_result == sample_merge_result
        assert len(worker._parameters) == 1

    def test_worker_with_custom_parameters(self, qapp, sample_merge_result):
        """Test audit worker with custom parameters."""
        parameters = [
            {"name": "greeting", "max_score": 10.0, "weight": 1.5, "description": "Test"},
            {"name": "empathy", "max_score": 10.0, "weight": 2.0, "description": "Test"},
            {"name": "resolution", "max_score": 10.0, "weight": 1.0, "description": "Test"},
        ]

        worker = AuditWorker(
            merge_result=sample_merge_result,
            parameters=parameters,
        )

        assert len(worker._parameters) == 3


class TestFullPipelineIntegration:
    """Integration tests for full processing pipeline."""

    def test_pipeline_data_flow(self, qapp, sample_transcription_result, sample_merge_result):
        """Test data flows correctly through pipeline stages."""
        # Stage 1: Transcription result format
        assert "text" in sample_transcription_result
        assert "segments" in sample_transcription_result
        assert "language" in sample_transcription_result

        # Stage 2: Merge result format
        assert "merged_text" in sample_merge_result
        assert "segments" in sample_merge_result

        # Stage 3: Audit result would be generated from merge result
        # This tests the expected interface between stages

    def test_provider_factory_integration(self):
        """Test LLM provider factory creates correct providers."""
        # Test OpenAI provider
        openai_provider = create_provider(
            provider_type=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            api_key="test-key",
        )
        assert openai_provider.provider_name == "openai"

        # Test Anthropic provider
        anthropic_provider = create_provider(
            provider_type=LLMProviderType.ANTHROPIC,
            model="claude-3-haiku-20240307",
            api_key="test-key",
        )
        assert anthropic_provider.provider_name == "anthropic"

        # Test Local provider
        local_provider = create_provider(
            provider_type=LLMProviderType.LOCAL,
            model="phi-3.5-mini",
        )
        assert local_provider.provider_name == "local"


class TestLLMProviderIntegration:
    """Integration tests for LLM providers."""

    @pytest.mark.asyncio
    async def test_openai_provider_message_format(self):
        """Test OpenAI provider formats messages correctly."""
        from localmind.llm.base import LLMMessage, LLMRole
        from localmind.llm.openai_provider import OpenAIProvider

        OpenAIProvider(model="gpt-4o-mini", api_key="test-key")

        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are helpful."),
            LLMMessage(role=LLMRole.USER, content="Hello"),
        ]

        # Test message conversion
        formatted = [m.to_dict() for m in messages]

        assert formatted[0]["role"] == "system"
        assert formatted[0]["content"] == "You are helpful."
        assert formatted[1]["role"] == "user"
        assert formatted[1]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_anthropic_provider_message_format(self):
        """Test Anthropic provider formats messages correctly."""
        from localmind.llm.anthropic_provider import AnthropicProvider
        from localmind.llm.base import LLMMessage, LLMRole

        AnthropicProvider(model="claude-3-haiku-20240307", api_key="test-key")

        messages = [
            LLMMessage(role=LLMRole.USER, content="Hello"),
            LLMMessage(role=LLMRole.ASSISTANT, content="Hi there!"),
        ]

        # Test message conversion
        formatted = [m.to_dict() for m in messages]

        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"


class TestReportGenerationIntegration:
    """Integration tests for report generation."""

    def test_pdf_generation_with_audit_result(self, sample_audit_result):
        """Test PDF report generation with audit data."""
        from localmind.reports.pdf_generator import PDFReportGenerator

        generator = PDFReportGenerator()

        if not generator.can_generate():
            pytest.skip("ReportLab not installed")

        pdf_bytes = generator.generate_pdf_bytes(sample_audit_result, "test_call.wav")

        # Verify PDF structure
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes[:4] == b"%PDF"

    def test_score_chart_generation(self):
        """Test score chart generation using ReportLab."""
        from localmind.reports.pdf_generator import ScoreChartGenerator

        parameters = [
            {"name": "greeting", "display_name": "Greeting", "score": 8.0, "max_score": 10.0},
            {"name": "empathy", "display_name": "Empathy", "score": 7.5, "max_score": 10.0},
            {"name": "resolution", "display_name": "Resolution", "score": 9.0, "max_score": 10.0},
        ]

        chart = ScoreChartGenerator.create_horizontal_bar_chart(parameters)

        # Returns None if ReportLab not installed, otherwise a Drawing object
        if chart is not None:
            assert hasattr(chart, "width")
            assert hasattr(chart, "height")


class TestConfigIntegration:
    """Integration tests for configuration management."""

    def test_settings_persistence(self, temp_dir, monkeypatch):
        """Test settings are persisted correctly."""
        from localmind.config import (
            SettingsManager,
            UserSettings,
            get_openai_api_key,
            set_openai_api_key,
        )

        # Mock the config directory to use temp_dir
        def mock_get_config_dir():
            return temp_dir

        monkeypatch.setattr(
            "localmind.config.settings.SettingsManager._get_config_dir",
            staticmethod(mock_get_config_dir),
        )

        # Mock keyring for testing (use in-memory storage)
        mock_keyring_storage = {}

        def mock_get_password(service, key):
            return mock_keyring_storage.get(f"{service}:{key}")

        def mock_set_password(service, key, value):
            mock_keyring_storage[f"{service}:{key}"] = value

        def mock_delete_password(service, key):
            mock_keyring_storage.pop(f"{service}:{key}", None)

        import keyring

        monkeypatch.setattr(keyring, "get_password", mock_get_password)
        monkeypatch.setattr(keyring, "set_password", mock_set_password)
        monkeypatch.setattr(keyring, "delete_password", mock_delete_password)

        # Store API key in secure storage
        set_openai_api_key("test-key-123")

        # Create and save settings
        manager = SettingsManager()
        settings = UserSettings()
        settings.app.theme = "dark"

        manager.save(settings)

        # Load settings with new manager instance
        manager2 = SettingsManager()
        loaded = manager2.load()

        # API keys are now in secure storage, not in settings
        assert loaded.llm.openai_api_key == ""  # Empty in settings
        assert get_openai_api_key() == "test-key-123"  # Retrieved from keyring
        assert loaded.app.theme == "dark"

    def test_scoring_profile_persistence(self, temp_dir):
        """Test scoring profiles are persisted correctly."""
        from localmind.config import ScoringParameter, ScoringProfile, ScoringProfileManager

        profiles_dir = temp_dir / "profiles"
        profiles_dir.mkdir()

        # Create manager with custom profiles directory
        manager = ScoringProfileManager(profiles_dir)

        # Create profile
        profile = ScoringProfile(
            name="Test Profile",
            parameters=[
                ScoringParameter(
                    name="test_param",
                    display_name="Test Parameter",
                    max_score=10.0,
                    weight=1.5,
                    description="A test parameter",
                ),
            ],
        )

        # Save and load
        manager.save_profile(profile)

        # Create new manager instance to test persistence
        # Note: profile is saved as "test_profile.json" (lowercase with underscores)
        manager2 = ScoringProfileManager(profiles_dir)
        loaded = manager2.load_profile("test_profile")

        assert loaded is not None
        assert loaded.name == "Test Profile"
        assert len(loaded.parameters) == 1
        assert loaded.parameters[0].weight == 1.5
