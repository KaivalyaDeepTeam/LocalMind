"""
Unit tests for LocalMind configuration module.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from localmind.config.settings import (
    UserSettings,
    LLMSettings,
    TranscriptionSettings,
    LLMProviderType,
    SettingsManager,
)
from localmind.config.scoring_parameters import (
    ScoringParameter,
    ScoringProfile,
    ParameterCategory,
    ScoringProfileManager,
    get_default_profile,
)


class TestUserSettings:
    """Tests for UserSettings dataclass."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = UserSettings()

        assert settings.llm.provider == LLMProviderType.LOCAL
        assert settings.llm.openai_model == "gpt-4o"
        assert settings.transcription.language == "auto"
        assert settings.app.first_run_complete is False

    def test_llm_settings(self):
        """Test LLM settings."""
        llm = LLMSettings(
            provider=LLMProviderType.OPENAI,
            openai_api_key="sk-test",
            openai_model="gpt-4o-mini",
        )

        assert llm.provider == LLMProviderType.OPENAI
        assert llm.openai_api_key == "sk-test"
        assert llm.openai_model == "gpt-4o-mini"

    def test_transcription_settings(self):
        """Test transcription settings."""
        trans = TranscriptionSettings(
            language="en",
            romanize=True,
            device="cuda",
        )

        assert trans.language == "en"
        assert trans.romanize is True
        assert trans.device == "cuda"

    def test_settings_to_dict(self):
        """Test converting settings to dictionary."""
        settings = UserSettings()
        data = settings.to_dict()

        assert "llm" in data
        assert "transcription" in data
        assert "app" in data
        assert data["llm"]["provider"] == "local"

    def test_settings_from_dict(self):
        """Test creating settings from dictionary."""
        data = {
            "llm": {
                "provider": "openai",
                "openai_api_key": "test-key",
                "openai_model": "gpt-4o",
                "anthropic_api_key": "",
                "anthropic_model": "claude-sonnet-4-20250514",
                "local_model": "phi-3.5-mini",
                "local_model_downloaded": False,
            },
            "transcription": {
                "language": "en",
                "romanize": False,
                "device": "auto",
            },
        }

        settings = UserSettings.from_dict(data)

        assert settings.llm.provider == LLMProviderType.OPENAI
        assert settings.llm.openai_api_key == "test-key"
        assert settings.transcription.language == "en"


class TestSettingsManager:
    """Tests for SettingsManager."""

    def test_create_manager(self):
        """Test creating a settings manager."""
        manager = SettingsManager()

        assert manager._config_dir is not None
        assert manager._config_file is not None

    def test_load_default_settings(self):
        """Test loading returns default settings when no file exists."""
        with patch.object(Path, 'exists', return_value=False):
            manager = SettingsManager()
            settings = manager.load()

            assert settings.llm.provider == LLMProviderType.LOCAL

    def test_settings_property(self):
        """Test settings property returns UserSettings."""
        manager = SettingsManager()
        settings = manager.settings

        assert isinstance(settings, UserSettings)


class TestScoringParameter:
    """Tests for ScoringParameter."""

    def test_create_parameter(self):
        """Test creating a scoring parameter."""
        param = ScoringParameter(
            name="test_param",
            display_name="Test Parameter",
            description="A test parameter",
            max_score=10.0,
            weight=1.5,
            category=ParameterCategory.QUALITY,
        )

        assert param.name == "test_param"
        assert param.display_name == "Test Parameter"
        assert param.max_score == 10.0
        assert param.weight == 1.5
        assert param.category == ParameterCategory.QUALITY
        assert param.enabled is True

    def test_to_dict(self):
        """Test converting parameter to dictionary."""
        param = ScoringParameter(
            name="greeting",
            display_name="Greeting",
            description="Proper greeting",
            max_score=10.0,
            weight=1.0,
        )

        data = param.to_dict()

        assert data["name"] == "greeting"
        assert data["display_name"] == "Greeting"
        assert data["max_score"] == 10.0

    def test_from_dict(self):
        """Test creating parameter from dictionary."""
        data = {
            "name": "empathy",
            "display_name": "Empathy",
            "description": "Shows empathy",
            "max_score": 10.0,
            "weight": 1.5,
            "category": "communication",
        }

        param = ScoringParameter.from_dict(data)

        assert param.name == "empathy"
        assert param.weight == 1.5
        assert param.category == ParameterCategory.COMMUNICATION


class TestScoringProfile:
    """Tests for ScoringProfile."""

    def test_create_profile(self):
        """Test creating a scoring profile."""
        params = [
            ScoringParameter(name="p1", display_name="P1", description=""),
            ScoringParameter(name="p2", display_name="P2", description="", enabled=False),
        ]

        profile = ScoringProfile(
            name="Test Profile",
            description="Test description",
            parameters=params,
        )

        assert profile.name == "Test Profile"
        assert len(profile.parameters) == 2

    def test_get_enabled_parameters(self):
        """Test getting only enabled parameters."""
        params = [
            ScoringParameter(name="p1", display_name="P1", description="", enabled=True),
            ScoringParameter(name="p2", display_name="P2", description="", enabled=False),
            ScoringParameter(name="p3", display_name="P3", description="", enabled=True),
        ]

        profile = ScoringProfile(name="Test", parameters=params)
        enabled = profile.get_enabled_parameters()

        assert len(enabled) == 2
        assert all(p.enabled for p in enabled)

    def test_get_total_weight(self):
        """Test calculating total weight."""
        params = [
            ScoringParameter(name="p1", display_name="P1", description="", weight=1.0),
            ScoringParameter(name="p2", display_name="P2", description="", weight=1.5),
            ScoringParameter(name="p3", display_name="P3", description="", weight=2.0, enabled=False),
        ]

        profile = ScoringProfile(name="Test", parameters=params)

        assert profile.get_total_weight() == 2.5  # Only enabled params

    def test_default_profile(self):
        """Test default profile has expected parameters."""
        profile = get_default_profile()

        assert profile.name == "Default"
        assert len(profile.parameters) == 10

        # Check some expected parameters
        param_names = [p.name for p in profile.parameters]
        assert "greeting" in param_names
        assert "active_listening" in param_names
        assert "compliance" in param_names


class TestScoringProfileManager:
    """Tests for ScoringProfileManager."""

    def test_create_manager(self, temp_dir):
        """Test creating a profile manager."""
        manager = ScoringProfileManager(profiles_dir=temp_dir / "profiles")

        # Default profile should be created
        profiles = manager.list_profiles()
        assert "default" in profiles

    def test_save_and_load_profile(self, temp_dir):
        """Test saving and loading profiles."""
        manager = ScoringProfileManager(profiles_dir=temp_dir / "profiles")

        # Create custom profile
        profile = ScoringProfile(
            name="Custom",
            description="Custom profile",
            parameters=[
                ScoringParameter(name="test", display_name="Test", description=""),
            ],
        )

        manager.save_profile(profile)

        # Load and verify
        loaded = manager.load_profile("custom")
        assert loaded.name == "Custom"
        assert len(loaded.parameters) == 1

    def test_duplicate_profile(self, temp_dir):
        """Test duplicating a profile."""
        manager = ScoringProfileManager(profiles_dir=temp_dir / "profiles")

        duplicated = manager.duplicate_profile("default", "My Custom")

        assert duplicated.name == "My Custom"
        assert "Copy of" in duplicated.description
        assert len(duplicated.parameters) == 10

    def test_delete_profile(self, temp_dir):
        """Test deleting a profile."""
        manager = ScoringProfileManager(profiles_dir=temp_dir / "profiles")

        # Create and delete
        profile = ScoringProfile(name="ToDelete", parameters=[])
        manager.save_profile(profile)

        assert "todelete" in manager.list_profiles()

        manager.delete_profile("todelete")

        assert "todelete" not in manager.list_profiles()

    def test_cannot_delete_default(self, temp_dir):
        """Test that default profile cannot be deleted."""
        manager = ScoringProfileManager(profiles_dir=temp_dir / "profiles")

        with pytest.raises(ValueError, match="Cannot delete"):
            manager.delete_profile("default")
