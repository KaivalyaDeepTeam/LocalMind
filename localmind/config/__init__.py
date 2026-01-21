"""LocalMind configuration management."""

from localmind.config.scoring_parameters import (
    ParameterCategory,
    ScoringParameter,
    ScoringProfile,
    ScoringProfileManager,
    get_default_profile,
    get_profile_manager,
)
from localmind.config.settings import (
    LLMProviderType,
    SettingsManager,
    UserSettings,
    get_anthropic_api_key,
    get_api_key,
    get_openai_api_key,
    get_settings,
    get_settings_manager,
    save_settings,
    set_anthropic_api_key,
    set_api_key,
    set_openai_api_key,
)

__all__ = [
    # Settings
    "get_settings",
    "get_settings_manager",
    "save_settings",
    "UserSettings",
    "LLMProviderType",
    "SettingsManager",
    # Secure API key storage
    "get_api_key",
    "set_api_key",
    "get_openai_api_key",
    "set_openai_api_key",
    "get_anthropic_api_key",
    "set_anthropic_api_key",
    # Scoring
    "ScoringParameter",
    "ScoringProfile",
    "ParameterCategory",
    "ScoringProfileManager",
    "get_profile_manager",
    "get_default_profile",
]
