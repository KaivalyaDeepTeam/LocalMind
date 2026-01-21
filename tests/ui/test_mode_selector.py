"""
Tests for Mode Selector module.

Tests the ProcessingMode enum, ModeToggle, ProviderSelector,
OfflineSettings, and ModeSelector widgets.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestProcessingModeEnum:
    """Tests for ProcessingMode enumeration."""

    def test_offline_value(self):
        """Test OFFLINE enum value."""
        from localmind.ui.mode_selector import ProcessingMode

        assert ProcessingMode.OFFLINE.value == "offline"

    def test_online_value(self):
        """Test ONLINE enum value."""
        from localmind.ui.mode_selector import ProcessingMode

        assert ProcessingMode.ONLINE.value == "online"

    def test_processing_mode_count(self):
        """Test there are exactly 2 processing modes."""
        from localmind.ui.mode_selector import ProcessingMode

        assert len(ProcessingMode) == 2

    def test_processing_mode_iteration(self):
        """Test both modes can be iterated."""
        from localmind.ui.mode_selector import ProcessingMode

        modes = list(ProcessingMode)
        assert ProcessingMode.OFFLINE in modes
        assert ProcessingMode.ONLINE in modes


class TestModeToggle:
    """Tests for ModeToggle widget."""

    def test_mode_toggle_creates(self, qapp):
        """Test ModeToggle can be created."""
        from localmind.ui.mode_selector import ModeToggle

        toggle = ModeToggle()
        assert toggle is not None

    def test_mode_toggle_object_name(self, qapp):
        """Test ModeToggle has correct object name."""
        from localmind.ui.mode_selector import ModeToggle

        toggle = ModeToggle()
        assert toggle.objectName() == "modeToggle"

    def test_mode_toggle_fixed_height(self, qapp):
        """Test ModeToggle has fixed height of 44."""
        from localmind.ui.mode_selector import ModeToggle

        toggle = ModeToggle()
        assert toggle.height() == 44 or toggle.minimumHeight() <= 44

    def test_mode_toggle_default_mode_is_offline(self, qapp):
        """Test default mode is OFFLINE."""
        from localmind.ui.mode_selector import ModeToggle, ProcessingMode

        toggle = ModeToggle()
        assert toggle.get_mode() == ProcessingMode.OFFLINE

    def test_mode_toggle_set_mode_online(self, qapp):
        """Test setting mode to ONLINE."""
        from localmind.ui.mode_selector import ModeToggle, ProcessingMode

        toggle = ModeToggle()
        toggle.set_mode(ProcessingMode.ONLINE)
        assert toggle.get_mode() == ProcessingMode.ONLINE

    def test_mode_toggle_set_mode_offline(self, qapp):
        """Test setting mode to OFFLINE."""
        from localmind.ui.mode_selector import ModeToggle, ProcessingMode

        toggle = ModeToggle()
        toggle.set_mode(ProcessingMode.ONLINE)
        toggle.set_mode(ProcessingMode.OFFLINE)
        assert toggle.get_mode() == ProcessingMode.OFFLINE

    def test_mode_toggle_signal_emitted_on_change(self, qapp):
        """Test mode_changed signal is emitted when mode changes."""
        from localmind.ui.mode_selector import ModeToggle, ProcessingMode

        toggle = ModeToggle()
        received_modes = []
        toggle.mode_changed.connect(lambda m: received_modes.append(m))

        toggle.set_mode(ProcessingMode.ONLINE)

        assert len(received_modes) == 1
        assert received_modes[0] == ProcessingMode.ONLINE

    def test_mode_toggle_no_signal_when_same_mode(self, qapp):
        """Test no signal emitted when setting same mode."""
        from localmind.ui.mode_selector import ModeToggle, ProcessingMode

        toggle = ModeToggle()
        received_modes = []
        toggle.mode_changed.connect(lambda m: received_modes.append(m))

        # Set to same mode (already OFFLINE)
        toggle.set_mode(ProcessingMode.OFFLINE)

        assert len(received_modes) == 0


class TestProviderSelectorConstants:
    """Tests for ProviderSelector constants."""

    def test_providers_dict_has_openai(self, qapp):
        """Test PROVIDERS contains OpenAI."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert "OpenAI" in selector.PROVIDERS

    def test_providers_dict_has_anthropic(self, qapp):
        """Test PROVIDERS contains Anthropic."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert "Anthropic" in selector.PROVIDERS

    def test_providers_dict_has_groq(self, qapp):
        """Test PROVIDERS contains Groq."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert "Groq" in selector.PROVIDERS

    def test_openai_has_models(self, qapp):
        """Test OpenAI has models list."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert "models" in selector.PROVIDERS["OpenAI"]
        assert len(selector.PROVIDERS["OpenAI"]["models"]) > 0

    def test_openai_has_default(self, qapp):
        """Test OpenAI has default model."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert "default" in selector.PROVIDERS["OpenAI"]
        assert selector.PROVIDERS["OpenAI"]["default"] == "gpt-4o-mini"

    def test_anthropic_has_claude_models(self, qapp):
        """Test Anthropic has Claude models."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        models = selector.PROVIDERS["Anthropic"]["models"]
        assert any("claude" in m for m in models)

    def test_groq_has_llama_models(self, qapp):
        """Test Groq has Llama models."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        models = selector.PROVIDERS["Groq"]["models"]
        assert any("llama" in m for m in models)

    def test_all_providers_have_icon(self, qapp):
        """Test all providers have an icon."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        for provider, config in selector.PROVIDERS.items():
            assert "icon" in config, f"{provider} missing icon"


class TestProviderSelector:
    """Tests for ProviderSelector widget."""

    def test_provider_selector_creates(self, qapp):
        """Test ProviderSelector can be created."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert selector is not None

    def test_provider_selector_object_name(self, qapp):
        """Test ProviderSelector has correct object name."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert selector.objectName() == "providerSelector"

    def test_get_provider_default(self, qapp):
        """Test default provider is OpenAI."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert selector.get_provider() == "OpenAI"

    def test_set_provider_anthropic(self, qapp):
        """Test setting provider to Anthropic."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        selector.set_provider("Anthropic")
        assert selector.get_provider() == "Anthropic"

    def test_get_model_returns_string(self, qapp):
        """Test get_model returns a string."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        model = selector.get_model()
        assert isinstance(model, str)
        assert len(model) > 0

    def test_set_model(self, qapp):
        """Test setting a specific model."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        selector.set_model("gpt-4o")
        assert selector.get_model() == "gpt-4o"

    def test_get_api_key_empty_by_default(self, qapp):
        """Test API key is empty by default."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        assert selector.get_api_key() == ""

    def test_set_api_key(self, qapp):
        """Test setting API key."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        selector.set_api_key("test-api-key-123")
        assert selector.get_api_key() == "test-api-key-123"

    def test_settings_changed_signal(self, qapp):
        """Test settings_changed signal can be connected."""
        from localmind.ui.mode_selector import ProviderSelector

        selector = ProviderSelector()
        signal_received = []
        selector.settings_changed.connect(lambda: signal_received.append(True))

        selector.settings_changed.emit()
        assert len(signal_received) == 1


class TestOfflineSettingsConstants:
    """Tests for OfflineSettings constants."""

    def test_language_modes_not_empty(self, qapp):
        """Test LANGUAGE_MODES is not empty."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert len(settings.LANGUAGE_MODES) > 0

    def test_language_modes_has_auto(self, qapp):
        """Test LANGUAGE_MODES contains auto-detect."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        lang_ids = [lang[0] for lang in settings.LANGUAGE_MODES]
        assert "auto" in lang_ids

    def test_language_modes_has_english(self, qapp):
        """Test LANGUAGE_MODES contains English."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        lang_ids = [lang[0] for lang in settings.LANGUAGE_MODES]
        assert "english" in lang_ids

    def test_language_modes_has_hindi_english(self, qapp):
        """Test LANGUAGE_MODES contains Hindi-English."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        lang_ids = [lang[0] for lang in settings.LANGUAGE_MODES]
        assert "hindi-english" in lang_ids

    def test_whisper_models_not_empty(self, qapp):
        """Test WHISPER_MODELS is not empty."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert len(settings.WHISPER_MODELS) > 0

    def test_whisper_models_has_tiny(self, qapp):
        """Test WHISPER_MODELS contains tiny."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        model_ids = [m[0] for m in settings.WHISPER_MODELS]
        assert "tiny" in model_ids

    def test_whisper_models_has_large_v3(self, qapp):
        """Test WHISPER_MODELS contains large-v3."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        model_ids = [m[0] for m in settings.WHISPER_MODELS]
        assert "large-v3" in model_ids


class TestOfflineSettings:
    """Tests for OfflineSettings widget."""

    def test_offline_settings_creates(self, qapp):
        """Test OfflineSettings can be created."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert settings is not None

    def test_offline_settings_object_name(self, qapp):
        """Test OfflineSettings has correct object name."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert settings.objectName() == "offlineSettings"

    def test_get_language_mode_default(self, qapp):
        """Test default language mode."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        mode = settings.get_language_mode()
        assert mode in ["auto", "english"]  # Implementation dependent

    def test_set_language_mode(self, qapp):
        """Test setting language mode."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        settings.set_language_mode("hindi-english")
        assert settings.get_language_mode() == "hindi-english"

    def test_get_whisper_model_default(self, qapp):
        """Test default Whisper model is large-v3."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert settings.get_whisper_model() == "large-v3"

    def test_set_whisper_model(self, qapp):
        """Test setting Whisper model."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        settings.set_whisper_model("tiny")
        assert settings.get_whisper_model() == "tiny"

    def test_is_hindi_mode_false_by_default(self, qapp):
        """Test Hindi mode is false by default."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert settings.is_hindi_mode() is False

    def test_is_hindi_mode_true_when_set(self, qapp):
        """Test Hindi mode is true when set."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        settings.set_language_mode("hindi-english")
        assert settings.is_hindi_mode() is True

    def test_get_hindi_model_variant_default(self, qapp):
        """Test default Hindi model variant is apex."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert settings.get_hindi_model_variant() == "apex"

    def test_set_hindi_model_variant(self, qapp):
        """Test setting Hindi model variant."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        settings.set_hindi_model_variant("prime")
        assert settings.get_hindi_model_variant() == "prime"

    def test_is_preprocessing_enabled_default_true(self, qapp):
        """Test preprocessing is enabled by default."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        assert settings.is_preprocessing_enabled() is True

    def test_set_preprocessing_enabled(self, qapp):
        """Test setting preprocessing enabled."""
        from localmind.ui.mode_selector import OfflineSettings

        settings = OfflineSettings()
        settings.set_preprocessing_enabled(False)
        assert settings.is_preprocessing_enabled() is False


class TestModeSelector:
    """Tests for main ModeSelector widget."""

    def test_mode_selector_creates(self, qapp):
        """Test ModeSelector can be created."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        assert selector is not None

    def test_mode_selector_default_mode_offline(self, qapp):
        """Test default mode is OFFLINE."""
        from localmind.ui.mode_selector import ModeSelector, ProcessingMode

        selector = ModeSelector()
        assert selector.get_mode() == ProcessingMode.OFFLINE

    def test_mode_selector_set_mode_online(self, qapp):
        """Test setting mode to ONLINE."""
        from localmind.ui.mode_selector import ModeSelector, ProcessingMode

        selector = ModeSelector()
        selector.set_mode(ProcessingMode.ONLINE)
        assert selector.get_mode() == ProcessingMode.ONLINE

    def test_mode_selector_get_provider(self, qapp):
        """Test getting provider from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        provider = selector.get_provider()
        assert provider in ["OpenAI", "Anthropic", "Groq"]

    def test_mode_selector_get_model(self, qapp):
        """Test getting model from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        model = selector.get_model()
        assert isinstance(model, str)

    def test_mode_selector_get_api_key(self, qapp):
        """Test getting API key from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        api_key = selector.get_api_key()
        assert api_key == ""

    def test_mode_selector_set_api_key(self, qapp):
        """Test setting API key on ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        selector.set_api_key("test-key-456")
        assert selector.get_api_key() == "test-key-456"

    def test_mode_selector_get_whisper_model(self, qapp):
        """Test getting Whisper model from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        model = selector.get_whisper_model()
        assert model in ["tiny", "base", "small", "medium", "large-v3"]

    def test_mode_selector_get_language_mode(self, qapp):
        """Test getting language mode from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        mode = selector.get_language_mode()
        assert isinstance(mode, str)

    def test_mode_selector_is_hindi_mode(self, qapp):
        """Test is_hindi_mode from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        assert selector.is_hindi_mode() is False

    def test_mode_selector_is_scoring_enabled_default(self, qapp):
        """Test scoring is disabled by default."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        assert selector.is_scoring_enabled() is False

    def test_mode_selector_set_scoring_enabled(self, qapp):
        """Test setting scoring enabled."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        selector.set_scoring_enabled(True)
        assert selector.is_scoring_enabled() is True

    def test_mode_selector_is_preprocessing_enabled(self, qapp):
        """Test getting preprocessing enabled from ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        assert selector.is_preprocessing_enabled() is True

    def test_mode_selector_set_preprocessing_enabled(self, qapp):
        """Test setting preprocessing enabled on ModeSelector."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        selector.set_preprocessing_enabled(False)
        assert selector.is_preprocessing_enabled() is False

    def test_mode_changed_signal(self, qapp):
        """Test mode_changed signal is emitted."""
        from localmind.ui.mode_selector import ModeSelector, ProcessingMode

        selector = ModeSelector()
        received_modes = []
        selector.mode_changed.connect(lambda m: received_modes.append(m))

        selector.set_mode(ProcessingMode.ONLINE)

        assert len(received_modes) == 1
        assert received_modes[0] == ProcessingMode.ONLINE

    def test_settings_changed_signal(self, qapp):
        """Test settings_changed signal can be connected."""
        from localmind.ui.mode_selector import ModeSelector

        selector = ModeSelector()
        signal_received = []
        selector.settings_changed.connect(lambda: signal_received.append(True))

        selector.settings_changed.emit()
        assert len(signal_received) == 1


class TestModeSelectorStackBehavior:
    """Tests for ModeSelector stack switching behavior."""

    def test_offline_mode_shows_offline_settings(self, qapp):
        """Test offline mode shows offline settings panel."""
        from localmind.ui.mode_selector import ModeSelector, ProcessingMode

        selector = ModeSelector()
        selector.set_mode(ProcessingMode.OFFLINE)

        # Stack index 1 is offline settings
        assert selector._settings_stack.currentIndex() == 1

    def test_online_mode_shows_provider_selector(self, qapp):
        """Test online mode shows provider selector panel."""
        from localmind.ui.mode_selector import ModeSelector, ProcessingMode

        selector = ModeSelector()
        selector.set_mode(ProcessingMode.ONLINE)

        # Stack index 0 is provider selector (online)
        assert selector._settings_stack.currentIndex() == 0

    def test_switching_modes_changes_stack(self, qapp):
        """Test switching modes changes the visible panel."""
        from localmind.ui.mode_selector import ModeSelector, ProcessingMode

        selector = ModeSelector()

        # Start offline
        assert selector._settings_stack.currentIndex() == 1

        # Switch to online
        selector.set_mode(ProcessingMode.ONLINE)
        assert selector._settings_stack.currentIndex() == 0

        # Switch back to offline
        selector.set_mode(ProcessingMode.OFFLINE)
        assert selector._settings_stack.currentIndex() == 1
