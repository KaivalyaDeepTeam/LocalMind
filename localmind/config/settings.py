"""
LocalMind Settings Management

Handles persistent storage of user preferences including API keys,
LLM provider selection, and application settings.
"""

import json
import logging
import os
import platform
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

# Keyring service name for secure API key storage
KEYRING_SERVICE = "LocalMind"


class LLMProviderType(str, Enum):
    """Available LLM providers."""

    LOCAL = "local"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


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
    device: str = "auto"
    whisper_model: str = "large-v3"
    use_gpu: bool = True
    chunk_length: int = 30
    batch_size: int = 16


@dataclass
class ScoringSettings:
    """Scoring configuration."""

    profile: str = "default"
    custom_parameters_path: str = ""


@dataclass
class OutputSettings:
    """Output configuration."""

    output_directory: str = ""
    auto_export_json: bool = True
    auto_export_pdf: bool = True
    include_transcript: bool = True
    include_scores: bool = True


@dataclass
class AppSettings:
    """Application settings."""

    theme: str = "system"
    language: str = "en"  # UI language (en, ru, es, hi, ar)
    colorblind_mode: bool = False  # Use colorblind-friendly colors
    check_updates: bool = True
    first_run_complete: bool = False
    whisper_models_downloaded: bool = False
    window_width: int = 1200
    window_height: int = 800
    window_x: int = 100
    window_y: int = 100
    recent_files: list = field(default_factory=list)  # Persisted recent files


@dataclass
class UserSettings:
    """Complete user settings."""

    llm: LLMSettings = field(default_factory=LLMSettings)
    transcription: TranscriptionSettings = field(default_factory=TranscriptionSettings)
    scoring: ScoringSettings = field(default_factory=ScoringSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    app: AppSettings = field(default_factory=AppSettings)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "llm": asdict(self.llm),
            "transcription": asdict(self.transcription),
            "scoring": asdict(self.scoring),
            "output": asdict(self.output),
            "app": asdict(self.app),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        """Create from dictionary."""
        settings = cls()

        if "llm" in data:
            llm_data = data["llm"].copy()
            if "provider" in llm_data:
                llm_data["provider"] = LLMProviderType(llm_data["provider"])
            settings.llm = LLMSettings(**llm_data)

        if "transcription" in data:
            settings.transcription = TranscriptionSettings(**data["transcription"])

        if "scoring" in data:
            settings.scoring = ScoringSettings(**data["scoring"])

        if "output" in data:
            output_data = data["output"].copy()
            # Migrate old field names to new ones
            if "default_output_dir" in output_data:
                output_data["output_directory"] = output_data.pop("default_output_dir")
            if "export_json" in output_data:
                output_data["auto_export_json"] = output_data.pop("export_json")
            if "export_pdf" in output_data:
                output_data["auto_export_pdf"] = output_data.pop("export_pdf")
            # Remove old fields that no longer exist
            output_data.pop("auto_open_results", None)
            # Add defaults for new fields
            output_data.setdefault("include_transcript", True)
            output_data.setdefault("include_scores", True)
            settings.output = OutputSettings(**output_data)

        if "app" in data:
            app_data = data["app"].copy()
            # Add defaults for new fields
            app_data.setdefault("recent_files", [])
            app_data.setdefault("colorblind_mode", False)
            app_data.setdefault("language", "en")
            settings.app = AppSettings(**app_data)

        return settings


# =============================================================================
# Secure API Key Storage
# =============================================================================


def get_api_key(key_name: str) -> str:
    """Get API key from secure storage (keyring).

    Args:
        key_name: Name of the key ("openai_api_key" or "anthropic_api_key")

    Returns:
        The API key or empty string if not found
    """
    try:
        import keyring

        value = keyring.get_password(KEYRING_SERVICE, key_name)
        return value or ""
    except Exception as e:
        logger.warning(f"Failed to retrieve API key from keyring: {e}")
        return ""


def set_api_key(key_name: str, value: str) -> bool:
    """Store API key in secure storage (keyring).

    Args:
        key_name: Name of the key ("openai_api_key" or "anthropic_api_key")
        value: The API key value

    Returns:
        True if successful, False otherwise
    """
    try:
        import keyring

        if value:
            keyring.set_password(KEYRING_SERVICE, key_name, value)
        else:
            # Delete key if value is empty
            try:
                keyring.delete_password(KEYRING_SERVICE, key_name)
            except keyring.errors.PasswordDeleteError:
                pass  # Key didn't exist, that's fine
        return True
    except Exception as e:
        logger.warning(f"Failed to store API key in keyring: {e}")
        return False


def delete_api_key(key_name: str) -> bool:
    """Delete API key from secure storage.

    Args:
        key_name: Name of the key to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        import keyring

        keyring.delete_password(KEYRING_SERVICE, key_name)
        return True
    except Exception as e:
        logger.debug(f"Failed to delete API key from keyring (may not exist): {e}")
        return False


def get_openai_api_key() -> str:
    """Get OpenAI API key from secure storage."""
    return get_api_key("openai_api_key")


def set_openai_api_key(value: str) -> bool:
    """Store OpenAI API key in secure storage."""
    return set_api_key("openai_api_key", value)


def get_anthropic_api_key() -> str:
    """Get Anthropic API key from secure storage."""
    return get_api_key("anthropic_api_key")


def set_anthropic_api_key(value: str) -> bool:
    """Store Anthropic API key in secure storage."""
    return set_api_key("anthropic_api_key", value)


class SettingsManager:
    """Manages loading and saving of user settings."""

    def __init__(self):
        self._settings: UserSettings | None = None
        self._config_dir = self._get_config_dir()
        self._config_file = self._config_dir / "settings.json"
        self._ensure_dirs()

    @staticmethod
    def _get_config_dir() -> Path:
        """Get platform-specific config directory."""
        system = platform.system()
        if system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "LocalMind"
        elif system == "Windows":
            app_data = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            return Path(app_data) / "LocalMind"
        else:
            xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
            return Path(xdg_config) / "localmind"

    @staticmethod
    def get_models_dir() -> Path:
        """Get platform-specific models directory."""
        system = platform.system()
        if system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "LocalMind" / "models"
        elif system == "Windows":
            local = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
            return Path(local) / "LocalMind" / "models"
        else:
            xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
            return Path(xdg_data) / "localmind" / "models"

    @staticmethod
    def get_cache_dir() -> Path:
        """Get platform-specific cache directory."""
        system = platform.system()
        if system == "Darwin":
            return Path.home() / "Library" / "Caches" / "LocalMind"
        elif system == "Windows":
            local = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
            return Path(local) / "LocalMind" / "cache"
        else:
            xdg_cache = os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
            return Path(xdg_cache) / "localmind"

    def _ensure_dirs(self) -> None:
        """Ensure directories exist."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self.get_models_dir().mkdir(parents=True, exist_ok=True)
        self.get_cache_dir().mkdir(parents=True, exist_ok=True)

    @property
    def config_dir(self) -> Path:
        """Get the config directory path."""
        return self._config_dir

    @property
    def settings(self) -> UserSettings:
        """Get current settings."""
        if self._settings is None:
            self._settings = self.load()
        return self._settings

    def load(self) -> UserSettings:
        """Load settings from disk."""
        settings = UserSettings()
        needs_save = False

        if self._config_file.exists():
            try:
                with open(self._config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    settings = UserSettings.from_dict(data)

                    # Migrate plaintext API keys to keyring (one-time migration)
                    if "llm" in data:
                        llm_data = data["llm"]
                        if llm_data.get("openai_api_key"):
                            set_openai_api_key(llm_data["openai_api_key"])
                            settings.llm.openai_api_key = ""  # Clear from memory
                            needs_save = True
                            logger.info("Migrated OpenAI API key to secure storage")
                        if llm_data.get("anthropic_api_key"):
                            set_anthropic_api_key(llm_data["anthropic_api_key"])
                            settings.llm.anthropic_api_key = ""  # Clear from memory
                            needs_save = True
                            logger.info("Migrated Anthropic API key to secure storage")
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}")

        # Save to remove plaintext keys from file after migration
        if needs_save:
            self._settings = settings
            self.save()

        return settings

    def save(self, settings: UserSettings | None = None) -> None:
        """Save settings to disk."""
        if settings is not None:
            self._settings = settings
        if self._settings is None:
            self._settings = UserSettings()

        self._ensure_dirs()
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(self._settings.to_dict(), f, indent=2)

    def reset(self) -> UserSettings:
        """Reset to defaults."""
        self._settings = UserSettings()
        self.save()
        return self._settings


_settings_manager: SettingsManager | None = None


def get_settings_manager() -> SettingsManager:
    """Get global settings manager."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_settings() -> UserSettings:
    """Get current settings."""
    return get_settings_manager().settings


def save_settings(settings: UserSettings | None = None) -> None:
    """Save settings."""
    get_settings_manager().save(settings)
