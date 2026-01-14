"""
LocalMind Setup Wizard

First-run setup wizard for downloading models and configuring the app.
"""

from typing import Optional, List, Tuple

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QCheckBox, QRadioButton, QButtonGroup, QProgressBar,
    QGroupBox, QTextEdit, QPushButton, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

import shutil

from localmind.workers.model_download_worker import (
    ModelDownloadWorker, ModelInfo, SetupWizardData,
    AVAILABLE_MODELS, ModelType, is_model_downloaded,
    get_required_download_size, get_optional_download_size,
)
from localmind.config import SettingsManager


class WelcomePage(QWizardPage):
    """Welcome page of the setup wizard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to LocalMind")
        self.setSubTitle("Free, open-source AI for audio transcription and quality auditing")

        layout = QVBoxLayout(self)

        # Welcome message
        welcome_label = QLabel(
            "<h2>Welcome!</h2>"
            "<p>LocalMind helps you transcribe audio files and perform quality audits "
            "using AI - all running locally on your computer.</p>"
            "<p>This wizard will help you set up the required AI models.</p>"
        )
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)

        layout.addSpacing(20)

        # Features
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)

        features = [
            "100% offline operation after setup",
            "Local audio transcription with Whisper",
            "Quality auditing with customizable parameters",
            "Support for multiple LLM backends",
            "Professional PDF report generation",
        ]

        for feature in features:
            label = QLabel(f"✓ {feature}")
            label.setStyleSheet("color: #4CAF50;")
            features_layout.addWidget(label)

        layout.addWidget(features_group)

        layout.addStretch()

        # Download size info
        required_size = get_required_download_size()
        if required_size > 0:
            size_label = QLabel(
                f"<p><b>Required download:</b> ~{required_size:.1f} GB</p>"
                "<p>Models will be downloaded from Hugging Face.</p>"
            )
            size_label.setStyleSheet("color: #666;")
            layout.addWidget(size_label)


class ModelSelectionPage(QWizardPage):
    """Page for selecting which models to download."""

    def __init__(self, wizard_data: SetupWizardData, parent=None):
        super().__init__(parent)
        self._wizard_data = wizard_data

        self.setTitle("Select AI Models")
        self.setSubTitle("Choose which models to download")

        layout = QVBoxLayout(self)

        # Whisper model selection
        whisper_group = QGroupBox("Transcription Model (Required)")
        whisper_layout = QVBoxLayout(whisper_group)

        self._whisper_group = QButtonGroup(self)

        whisper_models = [m for m in AVAILABLE_MODELS if m.model_type == ModelType.WHISPER]
        for model in whisper_models:
            downloaded = is_model_downloaded(model)
            status = " ✓ Downloaded" if downloaded else f" ({model.size_gb:.1f} GB)"

            radio = QRadioButton(f"{model.display_name}{status}")
            radio.setProperty("model_name", model.name)
            if model.name == "whisper-large-v3":
                radio.setChecked(True)
            self._whisper_group.addButton(radio)
            whisper_layout.addWidget(radio)

            desc = QLabel(f"    {model.description}")
            desc.setStyleSheet("color: #666; margin-left: 20px;")
            whisper_layout.addWidget(desc)

        layout.addWidget(whisper_group)

        # Local LLM selection
        llm_group = QGroupBox("Local LLM (Optional - for offline auditing)")
        llm_layout = QVBoxLayout(llm_group)

        self._download_llm_check = QCheckBox("Download local LLM for offline auditing")
        self._download_llm_check.stateChanged.connect(self._on_llm_check_changed)
        llm_layout.addWidget(self._download_llm_check)

        self._llm_group = QButtonGroup(self)
        self._llm_radios = []

        llm_models = [m for m in AVAILABLE_MODELS if m.model_type == ModelType.LOCAL_LLM]
        for model in llm_models:
            downloaded = is_model_downloaded(model)
            status = " ✓ Downloaded" if downloaded else f" ({model.size_gb:.1f} GB)"

            radio = QRadioButton(f"{model.display_name}{status}")
            radio.setProperty("model_name", model.name)
            radio.setEnabled(False)
            if model.name == "phi-3.5-mini":
                radio.setChecked(True)
            self._llm_group.addButton(radio)
            self._llm_radios.append(radio)
            llm_layout.addWidget(radio)

            desc = QLabel(f"    {model.description}")
            desc.setStyleSheet("color: #666; margin-left: 20px;")
            llm_layout.addWidget(desc)

        layout.addWidget(llm_group)

        layout.addStretch()

        # Total download size
        self._size_label = QLabel()
        self._size_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._size_label)

        self._update_size_label()

    def _on_llm_check_changed(self) -> None:
        """Handle LLM checkbox change."""
        enabled = self._download_llm_check.isChecked()
        for radio in self._llm_radios:
            radio.setEnabled(enabled)
        self._update_size_label()

    def _update_size_label(self) -> None:
        """Update the total download size label."""
        total = 0.0

        # Get selected Whisper model size
        for button in self._whisper_group.buttons():
            if button.isChecked():
                model_name = button.property("model_name")
                for model in AVAILABLE_MODELS:
                    if model.name == model_name and not is_model_downloaded(model):
                        total += model.size_gb
                break

        # Get selected LLM size if enabled
        if self._download_llm_check.isChecked():
            for button in self._llm_group.buttons():
                if button.isChecked():
                    model_name = button.property("model_name")
                    for model in AVAILABLE_MODELS:
                        if model.name == model_name and not is_model_downloaded(model):
                            total += model.size_gb
                    break

        if total > 0:
            self._size_label.setText(f"Total download: ~{total:.1f} GB")
        else:
            self._size_label.setText("All selected models already downloaded!")

    def validatePage(self) -> bool:
        """Save selections when leaving page."""
        # Save Whisper selection
        for button in self._whisper_group.buttons():
            if button.isChecked():
                self._wizard_data.whisper_model = button.property("model_name")
                break

        # Save LLM selection
        self._wizard_data.download_local_llm = self._download_llm_check.isChecked()
        if self._wizard_data.download_local_llm:
            for button in self._llm_group.buttons():
                if button.isChecked():
                    self._wizard_data.local_llm_model = button.property("model_name")
                    break

        return True


class DownloadPage(QWizardPage):
    """Page for downloading selected models."""

    def __init__(self, wizard_data: SetupWizardData, parent=None):
        super().__init__(parent)
        self._wizard_data = wizard_data
        self._worker: Optional[ModelDownloadWorker] = None
        self._download_complete = False

        self.setTitle("Downloading Models")
        self.setSubTitle("Please wait while models are downloaded")

        layout = QVBoxLayout(self)

        # Current model
        self._current_label = QLabel("Preparing...")
        self._current_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self._current_label)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        layout.addWidget(self._progress_bar)

        # Status
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #666;")
        layout.addWidget(self._status_label)

        layout.addSpacing(20)

        # Log
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(150)
        layout.addWidget(self._log)

        layout.addStretch()

        # Skip button
        self._skip_button = QPushButton("Skip Downloads")
        self._skip_button.clicked.connect(self._on_skip)
        layout.addWidget(self._skip_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _check_disk_space(self, required_gb: float) -> Tuple[bool, float]:
        """Check if there's enough disk space for downloads.

        Args:
            required_gb: Required space in GB

        Returns:
            Tuple of (has_enough_space, available_gb)
        """
        models_dir = SettingsManager.get_models_dir()
        try:
            # Get disk usage for the models directory (or its parent if it doesn't exist)
            check_path = models_dir if models_dir.exists() else models_dir.parent
            usage = shutil.disk_usage(check_path)
            available_gb = usage.free / (1024 ** 3)  # Convert to GB
            # Add 10% buffer for safety
            return available_gb >= (required_gb * 1.1), available_gb
        except Exception:
            # If we can't check, assume enough space
            return True, 0.0

    def initializePage(self) -> None:
        """Start downloads when page is shown."""
        self._download_complete = False
        self._log.clear()
        self._log.append("Starting downloads...")

        # Get models to download
        models = self._wizard_data.get_models_to_download()

        # Filter out already downloaded
        models_to_download = [m for m in models if not is_model_downloaded(m)]

        if not models_to_download:
            self._log.append("All models already downloaded!")
            self._current_label.setText("Complete!")
            self._progress_bar.setValue(100)
            self._download_complete = True
            self.completeChanged.emit()
            return

        # Calculate total required space
        total_required_gb = sum(m.size_gb for m in models_to_download)

        # Check disk space before starting
        has_space, available_gb = self._check_disk_space(total_required_gb)
        if not has_space:
            result = QMessageBox.warning(
                self,
                "Insufficient Disk Space",
                f"Not enough disk space for downloads.\n\n"
                f"Required: ~{total_required_gb:.1f} GB\n"
                f"Available: ~{available_gb:.1f} GB\n\n"
                f"Free up some disk space or choose smaller models.\n\n"
                f"Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                self._log.append(f"Insufficient disk space. Need {total_required_gb:.1f} GB, have {available_gb:.1f} GB")
                self._current_label.setText("Waiting for disk space...")
                return
            self._log.append(f"Warning: Low disk space ({available_gb:.1f} GB available)")

        # Start download worker
        self._worker = ModelDownloadWorker(models_to_download)
        self._worker.started_download.connect(self._on_started)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_download.connect(self._on_finished)
        self._worker.all_complete.connect(self._on_all_complete)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def cleanupPage(self) -> None:
        """Stop downloads if going back."""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()

    def isComplete(self) -> bool:
        """Check if page is complete."""
        return self._download_complete

    @Slot(str)
    def _on_started(self, model_name: str) -> None:
        """Handle download start."""
        self._current_label.setText(f"Downloading: {model_name}")
        self._progress_bar.setValue(0)
        self._log.append(f"\nDownloading {model_name}...")

    @Slot(str, int, float)
    def _on_progress(self, model_name: str, percent: int, speed: float) -> None:
        """Handle progress update."""
        self._progress_bar.setValue(percent)
        self._status_label.setText(f"{percent}% - {speed:.1f} MB/s")

    @Slot(str, bool, str)
    def _on_finished(self, model_name: str, success: bool, message: str) -> None:
        """Handle download completion."""
        if success:
            self._log.append(f"✓ {model_name} downloaded successfully")
        else:
            self._log.append(f"✗ {model_name} failed: {message}")

    @Slot()
    def _on_all_complete(self) -> None:
        """Handle all downloads complete."""
        self._current_label.setText("Downloads Complete!")
        self._progress_bar.setValue(100)
        self._status_label.setText("All models downloaded")
        self._download_complete = True
        self._skip_button.setVisible(False)
        self.completeChanged.emit()

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error."""
        self._log.append(f"Error: {message}")

    @Slot()
    def _on_skip(self) -> None:
        """Skip remaining downloads with warning."""
        # Show warning dialog
        result = QMessageBox.warning(
            self,
            "Skip Downloads?",
            "LocalMind requires AI models to function properly.\n\n"
            "Without downloading models:\n"
            "• Transcription will not work\n"
            "• Quality auditing will be limited\n\n"
            "You can download models later from Settings.\n\n"
            "Are you sure you want to skip?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()

        self._current_label.setText("Downloads Skipped")
        self._log.append("\nDownloads skipped by user.")
        self._download_complete = True
        self.completeChanged.emit()


class CompletePage(QWizardPage):
    """Completion page of the setup wizard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Setup Complete!")
        self.setSubTitle("LocalMind is ready to use")

        layout = QVBoxLayout(self)

        # Success message
        success_label = QLabel(
            "<h2>You're all set!</h2>"
            "<p>LocalMind is now configured and ready to transcribe audio files.</p>"
        )
        success_label.setWordWrap(True)
        layout.addWidget(success_label)

        layout.addSpacing(20)

        # Quick start guide
        guide_group = QGroupBox("Quick Start")
        guide_layout = QVBoxLayout(guide_group)

        steps = [
            "1. Select an audio file from the file browser",
            "2. Click 'Process' to start transcription and auditing",
            "3. View results in the Results panel",
            "4. Export as JSON or PDF report",
        ]

        for step in steps:
            label = QLabel(step)
            guide_layout.addWidget(label)

        layout.addWidget(guide_group)

        layout.addSpacing(20)

        # Tips
        tips_label = QLabel(
            "<p><b>Tips:</b></p>"
            "<ul>"
            "<li>Use Edit → Settings to configure LLM providers</li>"
            "<li>Use Edit → Scoring Parameters to customize audit criteria</li>"
            "<li>Supported formats: WAV, MP3, M4A, OGG, FLAC, WebM</li>"
            "</ul>"
        )
        tips_label.setWordWrap(True)
        layout.addWidget(tips_label)

        layout.addStretch()


class SetupWizard(QWizard):
    """First-run setup wizard."""

    setup_complete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._wizard_data = SetupWizardData()

        self.setWindowTitle("LocalMind Setup")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)

        # Add pages
        self.addPage(WelcomePage())
        self.addPage(ModelSelectionPage(self._wizard_data))
        self.addPage(DownloadPage(self._wizard_data))
        self.addPage(CompletePage())

        # Connect finish
        self.finished.connect(self._on_finished)

    @Slot(int)
    def _on_finished(self, result: int) -> None:
        """Handle wizard completion."""
        if result == QWizard.DialogCode.Accepted:
            # Save settings
            from localmind.config import get_settings, save_settings
            settings = get_settings()
            settings.app.whisper_models_downloaded = True
            settings.app.first_run_complete = True
            settings.transcription.use_gpu = self._wizard_data.use_gpu
            save_settings(settings)

            self.setup_complete.emit()
