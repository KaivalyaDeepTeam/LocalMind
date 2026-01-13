"""LocalMind configuration management."""

from localmind.config.settings import (
    get_settings,
    get_settings_manager,
    save_settings,
    UserSettings,
    LLMProviderType,
    SettingsManager,
)
from localmind.config.scoring_parameters import (
    ScoringParameter,
    ScoringProfile,
    ParameterCategory,
    ScoringProfileManager,
    get_profile_manager,
    get_default_profile,
)

__all__ = [
    # Settings
    "get_settings",
    "get_settings_manager",
    "save_settings",
    "UserSettings",
    "LLMProviderType",
    "SettingsManager",
    # Scoring
    "ScoringParameter",
    "ScoringProfile",
    "ParameterCategory",
    "ScoringProfileManager",
    "get_profile_manager",
    "get_default_profile",
]
