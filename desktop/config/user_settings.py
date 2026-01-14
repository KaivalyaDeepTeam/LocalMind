"""
User settings and preferences management for CallScore Desktop.

Handles persistent storage of user preferences including API keys,
LLM provider selection, and application settings.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional
import platform


class LLMProviderType(str, Enum):
    """Available LLM providers for merging and auditing."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class LLMSettings:
    """LLM provider configuration."""
    provider: LLMProviderType = LLMProviderType.LOCAL
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    local_model: str = "phi-3.5-mini"
    local_model_downloaded: bool = False


@dataclass
class TranscriptionSettings:
    """Transcription configuration."""
    language: str = "auto"
    romanize: bool = False
    enable_diarization: bool = True
    device: str = "auto"  # auto, cpu, cuda, mps


@dataclass
class OutputSettings:
    """Output configuration."""
    default_output_dir: str = ""
    export_json: bool = True
    export_pdf: bool = True
    auto_open_results: bool = True


@dataclass
class AppSettings:
    """Application-wide settings."""
    theme: str = "system"  # system, light, dark
    check_updates: bool = True
    first_run_complete: bool = False
    whisper_models_downloaded: bool = False
    window_width: int = 1200
    window_height: int = 800
    window_x: int = 100
    window_y: int = 100


@dataclass
class UserSettings:
    """Complete user settings container."""
    llm: LLMSettings = field(default_factory=LLMSettings)
    transcription: TranscriptionSettings = field(default_factory=TranscriptionSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    app: AppSettings = field(default_factory=AppSettings)

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "llm": asdict(self.llm),
            "transcription": asdict(self.transcription),
            "output": asdict(self.output),
            "app": asdict(self.app),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        """Create settings from dictionary."""
        settings = cls()

        if "llm" in data:
            llm_data = data["llm"]
            if "provider" in llm_data:
                llm_data["provider"] = LLMProviderType(llm_data["provider"])
            settings.llm = LLMSettings(**llm_data)

        if "transcription" in data:
            settings.transcription = TranscriptionSettings(**data["transcription"])

        if "output" in data:
            settings.output = OutputSettings(**data["output"])

        if "app" in data:
            settings.app = AppSettings(**data["app"])

        return settings


class SettingsManager:
    """Manages loading and saving of user settings."""

    def __init__(self):
        self._settings: Optional[UserSettings] = None
        self._config_dir = self._get_config_dir()
        self._config_file = self._config_dir / "settings.json"
        self._ensure_config_dir()

    @staticmethod
    def _get_config_dir() -> Path:
        """Get platform-specific configuration directory."""
        system = platform.system()

        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "CallScore"
        elif system == "Windows":
            app_data = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            return Path(app_data) / "CallScore"
        else:  # Linux and others
            xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
            return Path(xdg_config) / "callscore"

    @staticmethod
    def get_models_dir() -> Path:
        """Get platform-specific models directory."""
        system = platform.system()

        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "CallScore" / "models"
        elif system == "Windows":
            local_app_data = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
            return Path(local_app_data) / "CallScore" / "models"
        else:  # Linux and others
            xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
            return Path(xdg_data) / "callscore" / "models"

    @staticmethod
    def get_cache_dir() -> Path:
        """Get platform-specific cache directory."""
        system = platform.system()

        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Caches" / "CallScore"
        elif system == "Windows":
            local_app_data = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
            return Path(local_app_data) / "CallScore" / "cache"
        else:  # Linux and others
            xdg_cache = os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
            return Path(xdg_cache) / "callscore"

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def settings(self) -> UserSettings:
        """Get current settings, loading from disk if necessary."""
        if self._settings is None:
            self._settings = self.load()
        return self._settings

    def load(self) -> UserSettings:
        """Load settings from disk."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return UserSettings.from_dict(data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Warning: Could not load settings, using defaults: {e}")
                return UserSettings()
        return UserSettings()

    def save(self, settings: Optional[UserSettings] = None) -> None:
        """Save settings to disk."""
        if settings is not None:
            self._settings = settings

        if self._settings is None:
            self._settings = UserSettings()

        self._ensure_config_dir()

        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(self._settings.to_dict(), f, indent=2)

    def reset(self) -> UserSettings:
        """Reset settings to defaults."""
        self._settings = UserSettings()
        self.save()
        return self._settings


# Global settings manager instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_settings() -> UserSettings:
    """Convenience function to get current settings."""
    return get_settings_manager().settings


def save_settings(settings: Optional[UserSettings] = None) -> None:
    """Convenience function to save settings."""
    get_settings_manager().save(settings)
