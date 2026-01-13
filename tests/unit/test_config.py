"""
Unit tests for LocalMind configuration module.
"""

import json
from pathlib import Path

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
        assert settings.transcription.whisper_model == "large-v3"
        assert settings.transcription.use_gpu is True
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
            whisper_model="medium",
            language="en",
            use_gpu=False,
        )

        assert trans.whisper_model == "medium"
        assert trans.language == "en"
        assert trans.use_gpu is False


class TestSettingsManager:
    """Tests for SettingsManager."""

    def test_create_manager(self, temp_dir):
        """Test creating a settings manager."""
        manager = SettingsManager(config_dir=temp_dir)

        assert manager.config_dir == temp_dir
        assert manager.settings_file.exists()

    def test_save_and_load_settings(self, temp_dir):
        """Test saving and loading settings."""
        manager = SettingsManager(config_dir=temp_dir)

        # Modify settings
        settings = manager.get_settings()
        settings.llm.provider = LLMProviderType.OPENAI
        settings.llm.openai_api_key = "test-key"
        manager.save_settings(settings)

        # Create new manager and verify
        manager2 = SettingsManager(config_dir=temp_dir)
        loaded = manager2.get_settings()

        assert loaded.llm.provider == LLMProviderType.OPENAI
        assert loaded.llm.openai_api_key == "test-key"

    def test_settings_file_format(self, temp_dir):
        """Test that settings file is valid JSON."""
        manager = SettingsManager(config_dir=temp_dir)

        with open(manager.settings_file) as f:
            data = json.load(f)

        assert "llm" in data
        assert "transcription" in data
        assert "app" in data


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
