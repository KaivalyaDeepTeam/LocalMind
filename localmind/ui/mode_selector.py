"""
LocalMind Mode Selector

Modern toggle for Online/Offline mode with provider selection.
"""

from typing import Optional
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QStackedWidget, QLineEdit, QCheckBox,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class ProcessingMode(Enum):
    OFFLINE = "offline"
    ONLINE = "online"


class ModeToggle(QFrame):
    """Toggle button for Online/Offline mode."""

    mode_changed = Signal(ProcessingMode)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._mode = ProcessingMode.OFFLINE  # Default to offline mode
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("modeToggle")
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)

        # Offline button
        self._offline_btn = QPushButton(self.tr("Offline"))
        self._offline_btn.setObjectName("modeButton")
        self._offline_btn.setCheckable(True)
        self._offline_btn.setFixedHeight(36)
        self._offline_btn.clicked.connect(lambda: self._set_mode(ProcessingMode.OFFLINE))
        layout.addWidget(self._offline_btn)

        # Online button
        self._online_btn = QPushButton(self.tr("Online"))
        self._online_btn.setObjectName("modeButton")
        self._online_btn.setCheckable(True)
        self._online_btn.setFixedHeight(36)
        self._online_btn.clicked.connect(lambda: self._set_mode(ProcessingMode.ONLINE))
        layout.addWidget(self._online_btn)

        self._update_ui()

    def _set_mode(self, mode: ProcessingMode) -> None:
        if self._mode != mode:
            self._mode = mode
            self._update_ui()
            self.mode_changed.emit(mode)

    def _update_ui(self) -> None:
        is_online = self._mode == ProcessingMode.ONLINE
        self._online_btn.setChecked(is_online)
        self._offline_btn.setChecked(not is_online)

        # Update button properties for styling
        self._online_btn.setProperty("active", is_online)
        self._offline_btn.setProperty("active", not is_online)

        for btn in [self._online_btn, self._offline_btn]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def get_mode(self) -> ProcessingMode:
        return self._mode

    def set_mode(self, mode: ProcessingMode) -> None:
        self._set_mode(mode)


class ProviderSelector(QFrame):
    """Provider and model selector for online mode."""

    settings_changed = Signal()

    # Available providers and their models
    # Using text indicators instead of emojis for better cross-platform support
    PROVIDERS = {
        "OpenAI": {
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "default": "gpt-4o-mini",
            "icon": "[O]",  # OpenAI
        },
        "Anthropic": {
            "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
            "default": "claude-3-5-sonnet-20241022",
            "icon": "[A]",  # Anthropic
        },
        "Groq": {
            "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "default": "llama-3.3-70b-versatile",
            "icon": "[G]",  # Groq
        },
    }

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("providerSelector")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Provider selection
        provider_row = QHBoxLayout()
        provider_label = QLabel(self.tr("Provider"))
        provider_label.setObjectName("fieldLabel")
        provider_row.addWidget(provider_label)

        self._provider_combo = QComboBox()
        self._provider_combo.setObjectName("providerCombo")
        for provider in self.PROVIDERS.keys():
            icon = self.PROVIDERS[provider]["icon"]
            self._provider_combo.addItem(f"{icon} {provider}", provider)
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_row.addWidget(self._provider_combo, stretch=1)

        layout.addLayout(provider_row)

        # Model selection
        model_row = QHBoxLayout()
        model_label = QLabel(self.tr("Model"))
        model_label.setObjectName("fieldLabel")
        model_row.addWidget(model_label)

        self._model_combo = QComboBox()
        self._model_combo.setObjectName("modelCombo")
        self._model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_row.addWidget(self._model_combo, stretch=1)

        layout.addLayout(model_row)

        # API Key input
        api_row = QHBoxLayout()
        api_label = QLabel(self.tr("API Key"))
        api_label.setObjectName("fieldLabel")
        api_row.addWidget(api_label)

        self._api_key_input = QLineEdit()
        self._api_key_input.setObjectName("apiKeyInput")
        self._api_key_input.setPlaceholderText(self.tr("Enter your API key..."))
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.textChanged.connect(self._on_api_key_changed)
        api_row.addWidget(self._api_key_input, stretch=1)

        layout.addLayout(api_row)

        # Status indicator
        self._status_label = QLabel("")
        self._status_label.setObjectName("apiStatus")
        layout.addWidget(self._status_label)

        # Initialize models for default provider
        self._update_models()

    def _on_provider_changed(self) -> None:
        self._update_models()
        self._update_api_key_placeholder()
        self.settings_changed.emit()

    def _on_model_changed(self) -> None:
        self.settings_changed.emit()

    def _on_api_key_changed(self) -> None:
        api_key = self._api_key_input.text()
        if api_key:
            self._status_label.setText(self.tr("API key set"))
            self._status_label.setProperty("valid", True)
        else:
            self._status_label.setText(self.tr("API key required"))
            self._status_label.setProperty("valid", False)

        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)
        self.settings_changed.emit()

    def _update_models(self) -> None:
        provider = self._provider_combo.currentData()
        if provider and provider in self.PROVIDERS:
            self._model_combo.clear()
            for model in self.PROVIDERS[provider]["models"]:
                self._model_combo.addItem(model, model)

            # Set default
            default = self.PROVIDERS[provider]["default"]
            idx = self._model_combo.findData(default)
            if idx >= 0:
                self._model_combo.setCurrentIndex(idx)

    def _update_api_key_placeholder(self) -> None:
        provider = self._provider_combo.currentData()
        placeholders = {
            "OpenAI": "sk-...",
            "Anthropic": "sk-ant-...",
            "Groq": "gsk_...",
        }
        self._api_key_input.setPlaceholderText(placeholders.get(provider, "Enter API key..."))

    def get_provider(self) -> str:
        return self._provider_combo.currentData() or "OpenAI"

    def get_model(self) -> str:
        return self._model_combo.currentData() or "gpt-4o-mini"

    def get_api_key(self) -> str:
        return self._api_key_input.text()

    def set_provider(self, provider: str) -> None:
        idx = self._provider_combo.findData(provider)
        if idx >= 0:
            self._provider_combo.setCurrentIndex(idx)

    def set_model(self, model: str) -> None:
        idx = self._model_combo.findData(model)
        if idx >= 0:
            self._model_combo.setCurrentIndex(idx)

    def set_api_key(self, key: str) -> None:
        self._api_key_input.setText(key)


class OfflineSettings(QFrame):
    """Settings panel for offline mode."""

    settings_changed = Signal()

    LANGUAGE_MODES = [
        ("auto", "Auto-detect Language"),
        ("english", "English"),
        ("hindi-english", "Hindi-English (HindiSTT)"),
        ("spanish", "Spanish"),
        ("french", "French"),
        ("german", "German"),
        ("italian", "Italian"),
        ("portuguese", "Portuguese"),
        ("russian", "Russian"),
        ("japanese", "Japanese"),
        ("korean", "Korean"),
        ("chinese", "Chinese"),
        ("arabic", "Arabic"),
        ("turkish", "Turkish"),
        ("dutch", "Dutch"),
    ]

    WHISPER_MODELS = [
        ("tiny", "Tiny (39 MB) - Fastest"),
        ("base", "Base (141 MB) - Fast"),
        ("small", "Small (461 MB) - Balanced"),
        ("medium", "Medium (1.4 GB) - Accurate"),
        ("large-v3", "Large V3 (2.9 GB) - Best"),
    ]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("offlineSettings")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Info label
        info = QLabel(self.tr("100% Private - No data leaves your device"))
        info.setObjectName("offlineInfo")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # Language Mode selection
        lang_row = QHBoxLayout()
        lang_label = QLabel(self.tr("Language"))
        lang_label.setObjectName("fieldLabel")
        lang_row.addWidget(lang_label)

        self._language_combo = QComboBox()
        self._language_combo.setObjectName("languageCombo")
        for lang_id, lang_name in self.LANGUAGE_MODES:
            self._language_combo.addItem(lang_name, lang_id)
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self._language_combo, stretch=1)

        layout.addLayout(lang_row)

        # Whisper model selection (only shown for English mode)
        self._whisper_row = QHBoxLayout()
        model_label = QLabel(self.tr("Model"))
        model_label.setObjectName("fieldLabel")
        self._whisper_row.addWidget(model_label)

        self._model_combo = QComboBox()
        self._model_combo.setObjectName("whisperModelCombo")
        for model_id, model_name in self.WHISPER_MODELS:
            self._model_combo.addItem(model_name, model_id)

        # Default to large-v3 for best accuracy
        self._model_combo.setCurrentIndex(4)
        self._model_combo.currentIndexChanged.connect(lambda: self.settings_changed.emit())
        self._whisper_row.addWidget(self._model_combo, stretch=1)

        # Create a widget to hold the row so we can show/hide it
        self._whisper_container = QWidget()
        whisper_layout = QHBoxLayout(self._whisper_container)
        whisper_layout.setContentsMargins(0, 0, 0, 0)
        whisper_layout.addLayout(self._whisper_row)
        layout.addWidget(self._whisper_container)

        # Hindi model variant selection (only shown for Hindi mode)
        self._hindi_model_row = QHBoxLayout()
        hindi_model_label = QLabel(self.tr("Hindi Model"))
        hindi_model_label.setObjectName("fieldLabel")
        self._hindi_model_row.addWidget(hindi_model_label)

        self._hindi_model_combo = QComboBox()
        self._hindi_model_combo.setObjectName("hindiModelCombo")
        self._hindi_model_combo.addItem("Apex (Fast, Noisy Audio) - Recommended", "apex")
        self._hindi_model_combo.addItem("Prime (Accurate, Clean Audio)", "prime")
        self._hindi_model_combo.setCurrentIndex(0)  # Default to Apex
        self._hindi_model_combo.currentIndexChanged.connect(lambda: self.settings_changed.emit())
        self._hindi_model_row.addWidget(self._hindi_model_combo, stretch=1)

        # Create a widget to hold the Hindi model row so we can show/hide it
        self._hindi_model_container = QWidget()
        hindi_model_layout = QHBoxLayout(self._hindi_model_container)
        hindi_model_layout.setContentsMargins(0, 0, 0, 0)
        hindi_model_layout.addLayout(self._hindi_model_row)
        self._hindi_model_container.setVisible(False)
        layout.addWidget(self._hindi_model_container)

        # Note: Diarization moved to Settings dialog (File > Settings > Transcription)
        # This simplifies the main UI and groups all transcription settings together

        # Audio preprocessing toggle (shown for ALL modes)
        self._preprocessing_checkbox = QCheckBox(
            self.tr("Apply Audio Preprocessing (Volume leveling, noise reduction)")
        )
        self._preprocessing_checkbox.setObjectName("preprocessingCheckbox")
        self._preprocessing_checkbox.setChecked(True)  # Default ON - recommended for call recordings
        self._preprocessing_checkbox.setToolTip(
            self.tr("Recommended for call recordings:\n"
                    "• Volume leveling (even out quiet/loud speakers)\n"
                    "• Noise reduction and filtering\n"
                    "• Telephone bandwidth optimization\n"
                    "• Dynamic range compression\n\n"
                    "Improves transcription quality for all languages.")
        )
        self._preprocessing_checkbox.stateChanged.connect(lambda: self.settings_changed.emit())
        layout.addWidget(self._preprocessing_checkbox)

        # Hindi-English info (only shown for Hindi mode)
        self._hindi_info = QLabel(
            self.tr("Hindi-English Specialized Model") + "\n\n" +
            self.tr("Outputs romanized text (Hinglish).") + "\n" +
            self.tr("Optimized for Indian call centers with code-switching.")
        )
        self._hindi_info.setObjectName("hindiInfo")
        self._hindi_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hindi_info.setWordWrap(True)
        self._hindi_info.setVisible(False)
        layout.addWidget(self._hindi_info)

        # Download status
        self._status_label = QLabel(self.tr("Model will be downloaded on first use"))
        self._status_label.setObjectName("downloadStatus")
        layout.addWidget(self._status_label)

    def _on_language_changed(self) -> None:
        """Handle language mode change."""
        is_hindi = self._language_combo.currentData() == "hindi-english"
        self._whisper_container.setVisible(not is_hindi)
        self._hindi_model_container.setVisible(is_hindi)
        self._hindi_info.setVisible(is_hindi)
        self.settings_changed.emit()

    def get_language_mode(self) -> str:
        return self._language_combo.currentData() or "english"

    def get_whisper_model(self) -> str:
        return self._model_combo.currentData() or "large-v3"

    def set_language_mode(self, mode: str) -> None:
        idx = self._language_combo.findData(mode)
        if idx >= 0:
            self._language_combo.setCurrentIndex(idx)

    def set_whisper_model(self, model: str) -> None:
        idx = self._model_combo.findData(model)
        if idx >= 0:
            self._model_combo.setCurrentIndex(idx)

    def is_hindi_mode(self) -> bool:
        return self._language_combo.currentData() == "hindi-english"

    def get_hindi_model_variant(self) -> str:
        """Get the selected Hindi model variant (apex or prime)."""
        return self._hindi_model_combo.currentData() or "apex"

    def set_hindi_model_variant(self, variant: str) -> None:
        """Set the Hindi model variant."""
        idx = self._hindi_model_combo.findData(variant)
        if idx >= 0:
            self._hindi_model_combo.setCurrentIndex(idx)

    def is_preprocessing_enabled(self) -> bool:
        """Check if audio preprocessing is enabled."""
        return self._preprocessing_checkbox.isChecked()

    def set_preprocessing_enabled(self, enabled: bool) -> None:
        """Set audio preprocessing enabled state."""
        self._preprocessing_checkbox.setChecked(enabled)


class ModeSelector(QWidget):
    """Complete mode selector with online/offline toggle and settings."""

    mode_changed = Signal(ProcessingMode)
    settings_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header
        header = QLabel(self.tr("Processing Mode"))
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Mode toggle
        self._mode_toggle = ModeToggle()
        self._mode_toggle.mode_changed.connect(self._on_mode_changed)
        layout.addWidget(self._mode_toggle)

        # Settings stack
        self._settings_stack = QStackedWidget()

        # Online settings
        self._provider_selector = ProviderSelector()
        self._provider_selector.settings_changed.connect(self.settings_changed.emit)
        self._settings_stack.addWidget(self._provider_selector)

        # Offline settings
        self._offline_settings = OfflineSettings()
        self._offline_settings.settings_changed.connect(self.settings_changed.emit)
        self._settings_stack.addWidget(self._offline_settings)

        layout.addWidget(self._settings_stack)

        # Scoring toggle
        scoring_frame = QFrame()
        scoring_frame.setObjectName("scoringToggleFrame")
        scoring_layout = QVBoxLayout(scoring_frame)
        scoring_layout.setContentsMargins(12, 12, 12, 12)
        scoring_layout.setSpacing(8)

        self._scoring_checkbox = QCheckBox(self.tr("Enable Quality Scoring"))
        self._scoring_checkbox.setObjectName("scoringCheckbox")
        self._scoring_checkbox.setChecked(False)  # Default to transcription-only
        self._scoring_checkbox.stateChanged.connect(self._on_scoring_changed)
        scoring_layout.addWidget(self._scoring_checkbox)

        scoring_hint = QLabel(self.tr("Transcription only when unchecked. Scoring requires LLM."))
        scoring_hint.setObjectName("scoringHint")
        scoring_hint.setWordWrap(True)
        scoring_layout.addWidget(scoring_hint)

        layout.addWidget(scoring_frame)

        # Show offline settings by default (matches default mode)
        self._settings_stack.setCurrentIndex(1)

    @Slot(ProcessingMode)
    def _on_mode_changed(self, mode: ProcessingMode) -> None:
        if mode == ProcessingMode.ONLINE:
            self._settings_stack.setCurrentIndex(0)
        else:
            self._settings_stack.setCurrentIndex(1)

        self.mode_changed.emit(mode)

    @Slot(int)
    def _on_scoring_changed(self, state: int) -> None:
        self.settings_changed.emit()

    def get_mode(self) -> ProcessingMode:
        return self._mode_toggle.get_mode()

    def get_provider(self) -> str:
        return self._provider_selector.get_provider()

    def get_model(self) -> str:
        return self._provider_selector.get_model()

    def get_api_key(self) -> str:
        return self._provider_selector.get_api_key()

    def get_whisper_model(self) -> str:
        return self._offline_settings.get_whisper_model()

    def get_language_mode(self) -> str:
        return self._offline_settings.get_language_mode()

    def is_hindi_mode(self) -> bool:
        return self._offline_settings.is_hindi_mode()

    def get_hindi_model_variant(self) -> str:
        """Get the selected Hindi model variant."""
        return self._offline_settings.get_hindi_model_variant()

    def is_preprocessing_enabled(self) -> bool:
        """Check if audio preprocessing is enabled."""
        return self._offline_settings.is_preprocessing_enabled()

    def set_preprocessing_enabled(self, enabled: bool) -> None:
        """Set audio preprocessing enabled state."""
        self._offline_settings.set_preprocessing_enabled(enabled)

    def set_mode(self, mode: ProcessingMode) -> None:
        self._mode_toggle.set_mode(mode)

    def set_api_key(self, key: str) -> None:
        self._provider_selector.set_api_key(key)

    def is_scoring_enabled(self) -> bool:
        """Check if quality scoring is enabled."""
        return self._scoring_checkbox.isChecked()

    def set_scoring_enabled(self, enabled: bool) -> None:
        """Set scoring enabled state."""
        self._scoring_checkbox.setChecked(enabled)
