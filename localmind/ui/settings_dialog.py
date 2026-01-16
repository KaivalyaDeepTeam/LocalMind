"""
LocalMind Settings Dialog

Configuration dialog for LLM providers, API keys, and preferences.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QLabel, QPushButton, QGroupBox, QMessageBox,
    QDialogButtonBox, QFileDialog,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QObject

from localmind.config import (
    get_settings, save_settings, UserSettings, LLMProviderType,
)
from localmind.ui.loading_indicator import LoadingButton, InlineLoadingIndicator


class LLMSettingsTab(QWidget):
    """Tab for LLM provider settings."""

    def __init__(self, settings: UserSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = settings
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)

        # Provider selection
        provider_group = QGroupBox(self.tr("LLM Provider"))
        provider_layout = QFormLayout(provider_group)

        self._provider_combo = QComboBox()
        self._provider_combo.addItem(self.tr("Local LLM (Free, Offline)"), LLMProviderType.LOCAL)
        self._provider_combo.addItem(self.tr("OpenAI API"), LLMProviderType.OPENAI)
        self._provider_combo.addItem(self.tr("Anthropic API"), LLMProviderType.ANTHROPIC)
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_layout.addRow(self.tr("Provider:"), self._provider_combo)

        layout.addWidget(provider_group)

        # Local LLM settings
        self._local_group = QGroupBox(self.tr("Local LLM Settings"))
        local_layout = QFormLayout(self._local_group)

        self._local_model_combo = QComboBox()
        self._local_model_combo.addItem(self.tr("Phi-3.5-mini (2.4 GB) - Recommended"), "phi-3.5-mini")
        self._local_model_combo.addItem(self.tr("Llama 3.2 (3B) (2.0 GB)"), "llama-3.2-3b")
        self._local_model_combo.addItem(self.tr("Qwen 2.5 (3B) (2.0 GB)"), "qwen-2.5-3b")
        local_layout.addRow(self.tr("Model:"), self._local_model_combo)

        self._download_button = QPushButton(self.tr("Download Model"))
        self._download_button.clicked.connect(self._on_download_model)
        local_layout.addRow("", self._download_button)

        self._local_status = QLabel(self.tr("Status: Not downloaded"))
        self._local_status.setStyleSheet("color: gray;")
        local_layout.addRow("", self._local_status)

        layout.addWidget(self._local_group)

        # OpenAI settings
        self._openai_group = QGroupBox(self.tr("OpenAI Settings"))
        openai_layout = QFormLayout(self._openai_group)

        self._openai_key = QLineEdit()
        self._openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._openai_key.setPlaceholderText("sk-...")
        openai_layout.addRow(self.tr("API Key:"), self._openai_key)

        self._openai_model = QComboBox()
        self._openai_model.addItem("gpt-4o", "gpt-4o")
        self._openai_model.addItem("gpt-4o-mini", "gpt-4o-mini")
        self._openai_model.addItem("gpt-4-turbo", "gpt-4-turbo")
        openai_layout.addRow(self.tr("Model:"), self._openai_model)

        self._openai_test_btn = LoadingButton(self.tr("Test Connection"))
        self._openai_test_btn.clicked.connect(self._test_openai)
        self._openai_status = QLabel("")
        openai_test_row = QHBoxLayout()
        openai_test_row.addWidget(self._openai_test_btn)
        openai_test_row.addWidget(self._openai_status)
        openai_test_row.addStretch()
        openai_layout.addRow("", openai_test_row)

        layout.addWidget(self._openai_group)

        # Anthropic settings
        self._anthropic_group = QGroupBox(self.tr("Anthropic Settings"))
        anthropic_layout = QFormLayout(self._anthropic_group)

        self._anthropic_key = QLineEdit()
        self._anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._anthropic_key.setPlaceholderText("sk-ant-...")
        anthropic_layout.addRow(self.tr("API Key:"), self._anthropic_key)

        self._anthropic_model = QComboBox()
        self._anthropic_model.addItem("claude-sonnet-4-20250514", "claude-sonnet-4-20250514")
        self._anthropic_model.addItem("claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20241022")
        self._anthropic_model.addItem("claude-3-haiku-20240307", "claude-3-haiku-20240307")
        anthropic_layout.addRow(self.tr("Model:"), self._anthropic_model)

        self._anthropic_test_btn = LoadingButton(self.tr("Test Connection"))
        self._anthropic_test_btn.clicked.connect(self._test_anthropic)
        self._anthropic_status = QLabel("")
        anthropic_test_row = QHBoxLayout()
        anthropic_test_row.addWidget(self._anthropic_test_btn)
        anthropic_test_row.addWidget(self._anthropic_status)
        anthropic_test_row.addStretch()
        anthropic_layout.addRow("", anthropic_test_row)

        layout.addWidget(self._anthropic_group)

        layout.addStretch()

    def _load_settings(self) -> None:
        """Load settings into UI."""
        # Set provider
        index = self._provider_combo.findData(self._settings.llm.provider)
        if index >= 0:
            self._provider_combo.setCurrentIndex(index)

        # Set API keys
        self._openai_key.setText(self._settings.llm.openai_api_key or "")
        self._anthropic_key.setText(self._settings.llm.anthropic_api_key or "")

        # Set models
        openai_idx = self._openai_model.findData(self._settings.llm.openai_model)
        if openai_idx >= 0:
            self._openai_model.setCurrentIndex(openai_idx)

        anthropic_idx = self._anthropic_model.findData(self._settings.llm.anthropic_model)
        if anthropic_idx >= 0:
            self._anthropic_model.setCurrentIndex(anthropic_idx)

        local_idx = self._local_model_combo.findData(self._settings.llm.local_model)
        if local_idx >= 0:
            self._local_model_combo.setCurrentIndex(local_idx)

        self._on_provider_changed()

    def save_settings(self) -> None:
        """Save settings from UI."""
        self._settings.llm.provider = self._provider_combo.currentData()
        self._settings.llm.openai_api_key = self._openai_key.text() or None
        self._settings.llm.anthropic_api_key = self._anthropic_key.text() or None
        self._settings.llm.openai_model = self._openai_model.currentData()
        self._settings.llm.anthropic_model = self._anthropic_model.currentData()
        self._settings.llm.local_model = self._local_model_combo.currentData()

    @Slot()
    def _on_provider_changed(self) -> None:
        """Handle provider change."""
        provider = self._provider_combo.currentData()

        self._local_group.setVisible(provider == LLMProviderType.LOCAL)
        self._openai_group.setVisible(provider == LLMProviderType.OPENAI)
        self._anthropic_group.setVisible(provider == LLMProviderType.ANTHROPIC)

    @Slot()
    def _on_download_model(self) -> None:
        """Handle model download."""
        # TODO: Implement model download
        QMessageBox.information(
            self, self.tr("Download Model"),
            self.tr("Model download will be implemented in a future update.")
        )

    @Slot()
    def _test_openai(self) -> None:
        """Test OpenAI API connection."""
        api_key = self._openai_key.text().strip()
        if not api_key:
            self._openai_status.setText("No API key")
            self._openai_status.setStyleSheet("color: #DC2626;")
            return

        self._openai_status.setText("")
        self._openai_test_btn.set_loading(True, "Testing")

        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            # Make a minimal API call to test the key
            client.models.list()
            self._openai_status.setText("Connected")
            self._openai_status.setStyleSheet("color: #059669;")
        except Exception as e:
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            self._openai_status.setText(f"{error_msg}")
            self._openai_status.setStyleSheet("color: #DC2626;")
        finally:
            self._openai_test_btn.set_loading(False)

    @Slot()
    def _test_anthropic(self) -> None:
        """Test Anthropic API connection."""
        api_key = self._anthropic_key.text().strip()
        if not api_key:
            self._anthropic_status.setText("No API key")
            self._anthropic_status.setStyleSheet("color: #DC2626;")
            return

        self._anthropic_status.setText("")
        self._anthropic_test_btn.set_loading(True, "Testing")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Make a minimal API call to test the key
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            self._anthropic_status.setText("Connected")
            self._anthropic_status.setStyleSheet("color: #059669;")
        except Exception as e:
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            self._anthropic_status.setText(f"{error_msg}")
            self._anthropic_status.setStyleSheet("color: #DC2626;")
        finally:
            self._anthropic_test_btn.set_loading(False)


class TranscriptionSettingsTab(QWidget):
    """Tab for transcription settings."""

    def __init__(self, settings: UserSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = settings
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)

        # Whisper settings
        whisper_group = QGroupBox(self.tr("Whisper Settings"))
        whisper_layout = QFormLayout(whisper_group)

        self._whisper_model = QComboBox()
        self._whisper_model.addItem(self.tr("Large V3 (Best Quality)"), "large-v3")
        self._whisper_model.addItem(self.tr("Medium (Faster)"), "medium")
        self._whisper_model.addItem(self.tr("Small (Fastest)"), "small")
        whisper_layout.addRow(self.tr("Model:"), self._whisper_model)

        self._language = QComboBox()
        self._language.addItem(self.tr("Auto-detect"), "auto")
        self._language.addItem(self.tr("English"), "en")
        self._language.addItem(self.tr("Hindi"), "hi")
        self._language.addItem(self.tr("Spanish"), "es")
        self._language.addItem(self.tr("French"), "fr")
        whisper_layout.addRow(self.tr("Language:"), self._language)

        self._use_gpu = QCheckBox(self.tr("Use GPU acceleration (if available)"))
        whisper_layout.addRow("", self._use_gpu)

        layout.addWidget(whisper_group)

        # Advanced settings
        advanced_group = QGroupBox(self.tr("Advanced Settings"))
        advanced_layout = QFormLayout(advanced_group)

        self._chunk_length = QSpinBox()
        self._chunk_length.setRange(10, 60)
        self._chunk_length.setValue(30)
        self._chunk_length.setSuffix(self.tr(" seconds"))
        advanced_layout.addRow(self.tr("Chunk Length:"), self._chunk_length)

        self._batch_size = QSpinBox()
        self._batch_size.setRange(1, 32)
        self._batch_size.setValue(16)
        advanced_layout.addRow(self.tr("Batch Size:"), self._batch_size)

        layout.addWidget(advanced_group)

        layout.addStretch()

    def _load_settings(self) -> None:
        """Load settings into UI."""
        idx = self._whisper_model.findData(self._settings.transcription.whisper_model)
        if idx >= 0:
            self._whisper_model.setCurrentIndex(idx)

        lang_idx = self._language.findData(self._settings.transcription.language)
        if lang_idx >= 0:
            self._language.setCurrentIndex(lang_idx)

        self._use_gpu.setChecked(self._settings.transcription.use_gpu)
        self._chunk_length.setValue(self._settings.transcription.chunk_length)
        self._batch_size.setValue(self._settings.transcription.batch_size)

    def save_settings(self) -> None:
        """Save settings from UI."""
        self._settings.transcription.whisper_model = self._whisper_model.currentData()
        self._settings.transcription.language = self._language.currentData()
        self._settings.transcription.use_gpu = self._use_gpu.isChecked()
        self._settings.transcription.chunk_length = self._chunk_length.value()
        self._settings.transcription.batch_size = self._batch_size.value()


class OutputSettingsTab(QWidget):
    """Tab for output settings."""

    def __init__(self, settings: UserSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = settings
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)

        # Output directory
        output_group = QGroupBox(self.tr("Output Settings"))
        output_layout = QFormLayout(output_group)

        dir_layout = QHBoxLayout()
        self._output_dir = QLineEdit()
        self._output_dir.setReadOnly(True)
        dir_layout.addWidget(self._output_dir)

        self._browse_button = QPushButton(self.tr("Browse..."))
        self._browse_button.clicked.connect(self._on_browse)
        dir_layout.addWidget(self._browse_button)

        output_layout.addRow(self.tr("Output Directory:"), dir_layout)

        self._auto_export_json = QCheckBox(self.tr("Auto-export JSON after processing"))
        output_layout.addRow("", self._auto_export_json)

        self._auto_export_pdf = QCheckBox(self.tr("Auto-export PDF after processing"))
        output_layout.addRow("", self._auto_export_pdf)

        layout.addWidget(output_group)

        # PDF settings
        pdf_group = QGroupBox(self.tr("PDF Report Settings"))
        pdf_layout = QFormLayout(pdf_group)

        self._include_transcript = QCheckBox(self.tr("Include full transcript"))
        self._include_transcript.setChecked(True)
        pdf_layout.addRow("", self._include_transcript)

        self._include_scores = QCheckBox(self.tr("Include score breakdown"))
        self._include_scores.setChecked(True)
        pdf_layout.addRow("", self._include_scores)

        layout.addWidget(pdf_group)

        layout.addStretch()

    def _load_settings(self) -> None:
        """Load settings into UI."""
        self._output_dir.setText(self._settings.output.output_directory or "")
        self._auto_export_json.setChecked(self._settings.output.auto_export_json)
        self._auto_export_pdf.setChecked(self._settings.output.auto_export_pdf)
        self._include_transcript.setChecked(self._settings.output.include_transcript)
        self._include_scores.setChecked(self._settings.output.include_scores)

    def save_settings(self) -> None:
        """Save settings from UI."""
        self._settings.output.output_directory = self._output_dir.text() or ""
        self._settings.output.auto_export_json = self._auto_export_json.isChecked()
        self._settings.output.auto_export_pdf = self._auto_export_pdf.isChecked()
        self._settings.output.include_transcript = self._include_transcript.isChecked()
        self._settings.output.include_scores = self._include_scores.isChecked()

    @Slot()
    def _on_browse(self) -> None:
        """Browse for output directory."""
        from pathlib import Path
        directory = QFileDialog.getExistingDirectory(
            self, self.tr("Select Output Directory"),
            self._output_dir.text() or str(Path.home())
        )
        if directory:
            self._output_dir.setText(directory)


class AppearanceSettingsTab(QWidget):
    """Tab for appearance settings."""

    def __init__(self, settings: UserSettings, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = settings
        self._initial_language = settings.app.language
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)

        # Language settings
        language_group = QGroupBox(self.tr("Language"))
        language_layout = QFormLayout(language_group)

        self._language_combo = QComboBox()
        from localmind.i18n import TranslationManager
        for code, name in TranslationManager.LANGUAGES.items():
            self._language_combo.addItem(name, code)
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        language_layout.addRow(self.tr("UI Language:"), self._language_combo)

        self._language_note = QLabel("")
        self._language_note.setStyleSheet("color: #6B7280; font-size: 11px;")
        language_layout.addRow("", self._language_note)

        layout.addWidget(language_group)

        # Theme settings
        theme_group = QGroupBox(self.tr("Theme"))
        theme_layout = QFormLayout(theme_group)

        self._theme_combo = QComboBox()
        self._theme_combo.addItem(self.tr("System (Auto)"), "system")
        self._theme_combo.addItem(self.tr("Light"), "light")
        self._theme_combo.addItem(self.tr("Dark"), "dark")
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addRow(self.tr("Theme:"), self._theme_combo)

        theme_note = QLabel(self.tr("Theme changes apply immediately"))
        theme_note.setStyleSheet("color: #6B7280; font-size: 11px;")
        theme_layout.addRow("", theme_note)

        layout.addWidget(theme_group)

        # Accessibility settings
        accessibility_group = QGroupBox(self.tr("Accessibility"))
        accessibility_layout = QFormLayout(accessibility_group)

        self._colorblind_checkbox = QCheckBox(self.tr("Colorblind-friendly mode"))
        self._colorblind_checkbox.setToolTip(
            self.tr("Use blue-purple-orange colors instead of green-yellow-red\n"
            "for better visibility with red-green color blindness")
        )
        self._colorblind_checkbox.stateChanged.connect(self._on_colorblind_changed)
        accessibility_layout.addRow("", self._colorblind_checkbox)

        colorblind_note = QLabel(self.tr("Uses blue/purple/orange colors for score gauges"))
        colorblind_note.setStyleSheet("color: #6B7280; font-size: 11px;")
        accessibility_layout.addRow("", colorblind_note)

        layout.addWidget(accessibility_group)
        layout.addStretch()

    def _load_settings(self) -> None:
        """Load settings into UI."""
        # Load language
        lang_idx = self._language_combo.findData(self._settings.app.language)
        if lang_idx >= 0:
            self._language_combo.setCurrentIndex(lang_idx)

        # Load theme
        idx = self._theme_combo.findData(self._settings.app.theme)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        self._colorblind_checkbox.setChecked(self._settings.app.colorblind_mode)

    def save_settings(self) -> None:
        """Save settings from UI."""
        self._settings.app.language = self._language_combo.currentData()
        self._settings.app.theme = self._theme_combo.currentData()
        self._settings.app.colorblind_mode = self._colorblind_checkbox.isChecked()

    @Slot()
    def _on_language_changed(self) -> None:
        """Show restart note when language is changed."""
        current = self._language_combo.currentData()
        if current != self._initial_language:
            self._language_note.setText(self.tr("Restart required to apply language change"))
            self._language_note.setStyleSheet("color: #D97706; font-size: 11px;")
        else:
            self._language_note.setText("")

    @Slot()
    def _on_theme_changed(self) -> None:
        """Apply theme immediately when changed."""
        from localmind.ui.theme_manager import get_theme_manager
        theme = self._theme_combo.currentData()
        manager = get_theme_manager()
        if manager:
            manager.set_theme(theme)

    @Slot()
    def _on_colorblind_changed(self) -> None:
        """Apply colorblind mode immediately when changed."""
        from localmind.ui.results_viewer import CircularScoreGauge
        enabled = self._colorblind_checkbox.isChecked()
        CircularScoreGauge.set_colorblind_mode(enabled)


class SettingsDialog(QDialog):
    """Main settings dialog."""

    settings_saved = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings = get_settings()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setWindowTitle(self.tr("Settings"))
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        # Tab widget
        self._tabs = QTabWidget()

        self._llm_tab = LLMSettingsTab(self._settings)
        self._tabs.addTab(self._llm_tab, self.tr("LLM Provider"))

        self._transcription_tab = TranscriptionSettingsTab(self._settings)
        self._tabs.addTab(self._transcription_tab, self.tr("Transcription"))

        self._output_tab = OutputSettingsTab(self._settings)
        self._tabs.addTab(self._output_tab, self.tr("Output"))

        self._appearance_tab = AppearanceSettingsTab(self._settings)
        self._tabs.addTab(self._appearance_tab, self.tr("Appearance"))

        layout.addWidget(self._tabs)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply)

        layout.addWidget(button_box)

    def _save_all(self) -> None:
        """Save all settings."""
        self._llm_tab.save_settings()
        self._transcription_tab.save_settings()
        self._output_tab.save_settings()
        self._appearance_tab.save_settings()
        save_settings(self._settings)
        self.settings_saved.emit()

    @Slot()
    def _on_accept(self) -> None:
        """Handle OK button."""
        self._save_all()
        self.accept()

    @Slot()
    def _on_apply(self) -> None:
        """Handle Apply button."""
        self._save_all()
        QMessageBox.information(self, self.tr("Settings Saved"), self.tr("Settings have been saved."))
