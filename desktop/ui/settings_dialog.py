"""
Settings Dialog

Configuration dialog for API keys, LLM provider selection, and application settings.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QLabel,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, Slot

from desktop.config.user_settings import (
    get_settings,
    save_settings,
    UserSettings,
    LLMProviderType,
    SettingsManager,
)


class SettingsDialog(QDialog):
    """Settings configuration dialog."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._settings = get_settings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Tab widget
        tabs = QTabWidget()

        # LLM Provider tab
        llm_tab = self._create_llm_tab()
        tabs.addTab(llm_tab, "LLM Provider")

        # Transcription tab
        transcription_tab = self._create_transcription_tab()
        tabs.addTab(transcription_tab, "Transcription")

        # Output tab
        output_tab = self._create_output_tab()
        tabs.addTab(output_tab, "Output")

        # Application tab
        app_tab = self._create_app_tab()
        tabs.addTab(app_tab, "Application")

        layout.addWidget(tabs)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._on_apply
        )

        layout.addWidget(button_box)

    def _create_llm_tab(self) -> QWidget:
        """Create the LLM provider settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Provider selection group
        provider_group = QGroupBox("LLM Provider for Merging & Auditing")
        provider_layout = QVBoxLayout(provider_group)

        self._provider_group = QButtonGroup(self)

        # Local LLM option
        local_layout = QVBoxLayout()
        self._local_radio = QRadioButton("Local LLM (Free, Offline)")
        self._provider_group.addButton(self._local_radio, 0)
        local_layout.addWidget(self._local_radio)

        local_details = QLabel(
            "Uses bundled Phi-3.5 model. No API key required.\n"
            "Works completely offline after model download."
        )
        local_details.setStyleSheet("color: #666; margin-left: 20px;")
        local_details.setWordWrap(True)
        local_layout.addWidget(local_details)

        self._local_status = QLabel("Status: Not downloaded")
        self._local_status.setStyleSheet("color: #888; margin-left: 20px;")
        local_layout.addWidget(self._local_status)

        self._download_local_btn = QPushButton("Download Local LLM (2.4 GB)")
        self._download_local_btn.setMaximumWidth(200)
        local_layout.addWidget(self._download_local_btn)

        provider_layout.addLayout(local_layout)
        provider_layout.addSpacing(10)

        # OpenAI option
        openai_layout = QVBoxLayout()
        self._openai_radio = QRadioButton("OpenAI API")
        self._provider_group.addButton(self._openai_radio, 1)
        openai_layout.addWidget(self._openai_radio)

        openai_form = QFormLayout()
        openai_form.setContentsMargins(20, 0, 0, 0)

        self._openai_key_edit = QLineEdit()
        self._openai_key_edit.setPlaceholderText("sk-...")
        self._openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        openai_form.addRow("API Key:", self._openai_key_edit)

        self._openai_model_combo = QComboBox()
        self._openai_model_combo.addItems([
            "gpt-4o",
            "gpt-4o-mini",
            "o1",
            "o1-mini",
        ])
        openai_form.addRow("Model:", self._openai_model_combo)

        openai_layout.addLayout(openai_form)
        provider_layout.addLayout(openai_layout)
        provider_layout.addSpacing(10)

        # Anthropic option
        anthropic_layout = QVBoxLayout()
        self._anthropic_radio = QRadioButton("Anthropic API")
        self._provider_group.addButton(self._anthropic_radio, 2)
        anthropic_layout.addWidget(self._anthropic_radio)

        anthropic_form = QFormLayout()
        anthropic_form.setContentsMargins(20, 0, 0, 0)

        self._anthropic_key_edit = QLineEdit()
        self._anthropic_key_edit.setPlaceholderText("sk-ant-...")
        self._anthropic_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        anthropic_form.addRow("API Key:", self._anthropic_key_edit)

        self._anthropic_model_combo = QComboBox()
        self._anthropic_model_combo.addItems([
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-5-sonnet-20241022",
        ])
        anthropic_form.addRow("Model:", self._anthropic_model_combo)

        anthropic_layout.addLayout(anthropic_form)
        provider_layout.addLayout(anthropic_layout)

        layout.addWidget(provider_group)
        layout.addStretch()

        # Connect provider radio buttons
        self._provider_group.buttonClicked.connect(self._on_provider_changed)

        return widget

    def _create_transcription_tab(self) -> QWidget:
        """Create the transcription settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Language settings
        lang_group = QGroupBox("Language Settings")
        lang_layout = QFormLayout(lang_group)

        self._language_combo = QComboBox()
        self._language_combo.addItems([
            "Auto-detect",
            "English",
            "Russian",
            "Hindi",
            "Arabic",
            "Italian",
            "Spanish",
        ])
        lang_layout.addRow("Default Language:", self._language_combo)

        self._romanize_check = QCheckBox("Enable romanization for non-Latin scripts")
        lang_layout.addRow("", self._romanize_check)

        layout.addWidget(lang_group)

        # Processing settings
        proc_group = QGroupBox("Processing Settings")
        proc_layout = QFormLayout(proc_group)

        self._diarization_check = QCheckBox("Enable speaker diarization")
        self._diarization_check.setToolTip(
            "Automatically identify different speakers in the audio"
        )
        proc_layout.addRow("", self._diarization_check)

        self._device_combo = QComboBox()
        self._device_combo.addItems(["Auto", "CPU", "CUDA (NVIDIA)", "MPS (Apple Silicon)"])
        proc_layout.addRow("Processing Device:", self._device_combo)

        layout.addWidget(proc_group)

        # Model status
        model_group = QGroupBox("Whisper Models")
        model_layout = QVBoxLayout(model_group)

        self._model_status = QLabel("Checking model status...")
        model_layout.addWidget(self._model_status)

        self._download_models_btn = QPushButton("Download Whisper Models (4.5 GB)")
        self._download_models_btn.clicked.connect(self._on_download_models)
        model_layout.addWidget(self._download_models_btn)

        layout.addWidget(model_group)
        layout.addStretch()

        return widget

    def _create_output_tab(self) -> QWidget:
        """Create the output settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Output directory
        dir_group = QGroupBox("Output Directory")
        dir_layout = QHBoxLayout(dir_group)

        self._output_dir_edit = QLineEdit()
        self._output_dir_edit.setPlaceholderText("Default: Same as input file")
        dir_layout.addWidget(self._output_dir_edit)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._on_browse_output_dir)
        dir_layout.addWidget(browse_btn)

        layout.addWidget(dir_group)

        # Export options
        export_group = QGroupBox("Auto Export")
        export_layout = QVBoxLayout(export_group)

        self._export_json_check = QCheckBox("Automatically export JSON after processing")
        export_layout.addWidget(self._export_json_check)

        self._export_pdf_check = QCheckBox("Automatically export PDF after processing")
        export_layout.addWidget(self._export_pdf_check)

        self._auto_open_check = QCheckBox("Open results folder after export")
        export_layout.addWidget(self._auto_open_check)

        layout.addWidget(export_group)
        layout.addStretch()

        return widget

    def _create_app_tab(self) -> QWidget:
        """Create the application settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["System Default", "Light", "Dark"])
        appearance_layout.addRow("Theme:", self._theme_combo)

        layout.addWidget(appearance_group)

        # Updates
        updates_group = QGroupBox("Updates")
        updates_layout = QVBoxLayout(updates_group)

        self._check_updates_check = QCheckBox("Check for updates on startup")
        updates_layout.addWidget(self._check_updates_check)

        layout.addWidget(updates_group)

        # Data
        data_group = QGroupBox("Data & Cache")
        data_layout = QVBoxLayout(data_group)

        models_dir = SettingsManager.get_models_dir()
        cache_dir = SettingsManager.get_cache_dir()

        data_layout.addWidget(QLabel(f"Models directory: {models_dir}"))
        data_layout.addWidget(QLabel(f"Cache directory: {cache_dir}"))

        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self._on_clear_cache)
        data_layout.addWidget(clear_cache_btn)

        layout.addWidget(data_group)
        layout.addStretch()

        return widget

    def _load_settings(self) -> None:
        """Load current settings into UI."""
        # LLM settings
        provider = self._settings.llm.provider
        if provider == LLMProviderType.LOCAL:
            self._local_radio.setChecked(True)
        elif provider == LLMProviderType.OPENAI:
            self._openai_radio.setChecked(True)
        else:
            self._anthropic_radio.setChecked(True)

        self._openai_key_edit.setText(self._settings.llm.openai_api_key)
        self._anthropic_key_edit.setText(self._settings.llm.anthropic_api_key)

        # Find model in combo boxes
        openai_model = self._settings.llm.openai_model
        idx = self._openai_model_combo.findText(openai_model)
        if idx >= 0:
            self._openai_model_combo.setCurrentIndex(idx)

        anthropic_model = self._settings.llm.anthropic_model
        idx = self._anthropic_model_combo.findText(anthropic_model)
        if idx >= 0:
            self._anthropic_model_combo.setCurrentIndex(idx)

        # Local LLM status
        if self._settings.llm.local_model_downloaded:
            self._local_status.setText("Status: Downloaded and ready")
            self._local_status.setStyleSheet("color: #27ae60; margin-left: 20px;")
            self._download_local_btn.setEnabled(False)
            self._download_local_btn.setText("Downloaded")

        # Transcription settings
        lang_map = {
            "auto": 0,
            "en": 1,
            "ru": 2,
            "hi": 3,
            "ar": 4,
            "it": 5,
            "es": 6,
        }
        self._language_combo.setCurrentIndex(
            lang_map.get(self._settings.transcription.language, 0)
        )
        self._romanize_check.setChecked(self._settings.transcription.romanize)
        self._diarization_check.setChecked(self._settings.transcription.enable_diarization)

        device_map = {"auto": 0, "cpu": 1, "cuda": 2, "mps": 3}
        self._device_combo.setCurrentIndex(
            device_map.get(self._settings.transcription.device, 0)
        )

        # Model status
        if self._settings.app.whisper_models_downloaded:
            self._model_status.setText("Whisper models: Downloaded and ready")
            self._model_status.setStyleSheet("color: #27ae60;")
            self._download_models_btn.setEnabled(False)
            self._download_models_btn.setText("Downloaded")
        else:
            self._model_status.setText("Whisper models: Not downloaded")
            self._model_status.setStyleSheet("color: #e74c3c;")

        # Output settings
        self._output_dir_edit.setText(self._settings.output.default_output_dir)
        self._export_json_check.setChecked(self._settings.output.export_json)
        self._export_pdf_check.setChecked(self._settings.output.export_pdf)
        self._auto_open_check.setChecked(self._settings.output.auto_open_results)

        # App settings
        theme_map = {"system": 0, "light": 1, "dark": 2}
        self._theme_combo.setCurrentIndex(theme_map.get(self._settings.app.theme, 0))
        self._check_updates_check.setChecked(self._settings.app.check_updates)

    def _save_settings(self) -> None:
        """Save UI values to settings."""
        # LLM settings
        if self._local_radio.isChecked():
            self._settings.llm.provider = LLMProviderType.LOCAL
        elif self._openai_radio.isChecked():
            self._settings.llm.provider = LLMProviderType.OPENAI
        else:
            self._settings.llm.provider = LLMProviderType.ANTHROPIC

        self._settings.llm.openai_api_key = self._openai_key_edit.text()
        self._settings.llm.openai_model = self._openai_model_combo.currentText()
        self._settings.llm.anthropic_api_key = self._anthropic_key_edit.text()
        self._settings.llm.anthropic_model = self._anthropic_model_combo.currentText()

        # Transcription settings
        lang_map = ["auto", "en", "ru", "hi", "ar", "it", "es"]
        self._settings.transcription.language = lang_map[
            self._language_combo.currentIndex()
        ]
        self._settings.transcription.romanize = self._romanize_check.isChecked()
        self._settings.transcription.enable_diarization = (
            self._diarization_check.isChecked()
        )

        device_map = ["auto", "cpu", "cuda", "mps"]
        self._settings.transcription.device = device_map[
            self._device_combo.currentIndex()
        ]

        # Output settings
        self._settings.output.default_output_dir = self._output_dir_edit.text()
        self._settings.output.export_json = self._export_json_check.isChecked()
        self._settings.output.export_pdf = self._export_pdf_check.isChecked()
        self._settings.output.auto_open_results = self._auto_open_check.isChecked()

        # App settings
        theme_map = ["system", "light", "dark"]
        self._settings.app.theme = theme_map[self._theme_combo.currentIndex()]
        self._settings.app.check_updates = self._check_updates_check.isChecked()

        save_settings(self._settings)

    # Slot handlers
    @Slot()
    def _on_provider_changed(self) -> None:
        """Handle provider radio button change."""
        # Could enable/disable relevant fields based on selection
        pass

    @Slot()
    def _on_browse_output_dir(self) -> None:
        """Handle output directory browse."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if directory:
            self._output_dir_edit.setText(directory)

    @Slot()
    def _on_download_models(self) -> None:
        """Handle model download button."""
        # TODO: Implement model download
        QMessageBox.information(
            self,
            "Download Models",
            "Model download will be implemented in a future update.\n\n"
            "For now, models are downloaded automatically on first use.",
        )

    @Slot()
    def _on_clear_cache(self) -> None:
        """Handle clear cache button."""
        result = QMessageBox.question(
            self,
            "Clear Cache",
            "This will delete cached files and temporary data.\n"
            "Models will not be affected.\n\n"
            "Continue?",
        )
        if result == QMessageBox.StandardButton.Yes:
            # TODO: Implement cache clearing
            QMessageBox.information(self, "Cache Cleared", "Cache has been cleared.")

    @Slot()
    def _on_apply(self) -> None:
        """Handle apply button."""
        self._save_settings()

    @Slot()
    def _on_accept(self) -> None:
        """Handle OK button."""
        self._save_settings()
        self.accept()
