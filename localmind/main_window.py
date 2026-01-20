"""
LocalMind Main Window

The main application window with menu bar, file browser, and results panels.
"""

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from localmind import __app_name__, __version__
from localmind.config import get_profile_manager, get_settings, get_settings_manager, save_settings
from localmind.ui.file_browser import FileBrowserPanel
from localmind.ui.loading_indicator import SpinnerWidget
from localmind.ui.mode_selector import ModeSelector, ProcessingMode
from localmind.ui.progress_panel import ProcessingStage, ProgressPanel
from localmind.ui.results_viewer import CircularScoreGauge, ResultsViewer
from localmind.ui.scoring_editor import ScoringEditorDialog
from localmind.ui.settings_dialog import SettingsDialog
from localmind.ui.setup_wizard import SetupWizard
from localmind.ui.toast import init_toast_manager
from localmind.utils import get_error_handler
from localmind.workers import ProcessingOrchestrator, ProcessingResult


class MainWindow(QMainWindow):
    """Main application window."""

    file_selected = Signal(str)
    processing_started = Signal()
    processing_finished = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._settings_manager = get_settings_manager()
        self._current_file: Path | None = None
        self._recent_files: list[str] = []

        # Processing orchestrator
        self._orchestrator = ProcessingOrchestrator(self)

        # Initialize error handler with this window as parent
        self._error_handler = get_error_handler()
        self._error_handler.set_parent_widget(self)

        # Initialize toast notification manager
        self._toast_manager = init_toast_manager(self)

        # Apply colorblind mode from settings
        settings = get_settings()
        CircularScoreGauge.set_colorblind_mode(settings.app.colorblind_mode)

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._connect_signals()
        self._configure_orchestrator()

    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        self.setWindowTitle(__app_name__)
        self.setMinimumSize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Mode selector + File browser
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Mode selector at top
        self._mode_selector = ModeSelector()
        self._mode_selector.mode_changed.connect(self._on_mode_changed)
        self._mode_selector.settings_changed.connect(self._on_mode_settings_changed)
        left_layout.addWidget(self._mode_selector)

        # File browser below
        self._file_browser = FileBrowserPanel()
        left_layout.addWidget(self._file_browser, stretch=1)

        splitter.addWidget(left_panel)

        # Right: Progress and Results
        right = QWidget()
        right.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(16)

        self._progress_panel = ProgressPanel()
        right_layout.addWidget(self._progress_panel)

        self._results_viewer = ResultsViewer()
        right_layout.addWidget(self._results_viewer, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([350, 650])

        layout.addWidget(splitter)

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu(self.tr("&File"))

        open_action = QAction(self.tr("&Open Audio File..."), self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_transcript = QAction(self.tr("Export &Transcript..."), self)
        export_transcript.setShortcut("Ctrl+Shift+T")
        export_transcript.triggered.connect(self._on_export_transcript)
        file_menu.addAction(export_transcript)

        export_json = QAction(self.tr("Export as &JSON..."), self)
        export_json.setShortcut("Ctrl+Shift+J")
        export_json.triggered.connect(self._on_export_json)
        file_menu.addAction(export_json)

        export_markdown = QAction(self.tr("Export &Markdown Report..."), self)
        export_markdown.setShortcut("Ctrl+Shift+M")
        export_markdown.triggered.connect(self._on_export_markdown_report)
        file_menu.addAction(export_markdown)

        export_pdf = QAction(self.tr("Export &PDF Report..."), self)
        export_pdf.setShortcut("Ctrl+Shift+P")
        export_pdf.triggered.connect(self._on_export_pdf)
        file_menu.addAction(export_pdf)

        file_menu.addSeparator()

        quit_action = QAction(self.tr("&Quit"), self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu(self.tr("&Edit"))

        scoring_action = QAction(self.tr("&Scoring Parameters..."), self)
        scoring_action.setShortcut("Ctrl+Shift+S")
        scoring_action.triggered.connect(self._on_edit_scoring)
        edit_menu.addAction(scoring_action)

        edit_menu.addSeparator()

        settings_action = QAction(self.tr("&Settings..."), self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self._on_open_settings)
        edit_menu.addAction(settings_action)

        # Process menu
        process_menu = menubar.addMenu(self.tr("&Process"))

        process_action = QAction(self.tr("&Process Audio"), self)
        process_action.setShortcut("Ctrl+Return")
        process_action.triggered.connect(self._on_process)
        process_menu.addAction(process_action)

        process_menu.addSeparator()

        stop_action = QAction(self.tr("&Stop"), self)
        stop_action.setShortcut("Escape")
        stop_action.triggered.connect(self._on_stop)
        process_menu.addAction(stop_action)

        # Help menu
        help_menu = menubar.addMenu(self.tr("&Help"))

        shortcuts_action = QAction(self.tr("&Keyboard Shortcuts"), self)
        shortcuts_action.setShortcut("Ctrl+/")
        shortcuts_action.triggered.connect(self._on_show_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        about_action = QAction(self.tr("&About LocalMind"), self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = QToolBar(self.tr("Main"))
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        open_action = QAction(self.tr("Open"), self)
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        process_action = QAction(self.tr("Process"), self)
        process_action.triggered.connect(self._on_process)
        toolbar.addAction(process_action)

        stop_action = QAction(self.tr("Stop"), self)
        stop_action.triggered.connect(self._on_stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        settings_action = QAction(self.tr("Settings"), self)
        settings_action.triggered.connect(self._on_open_settings)
        toolbar.addAction(settings_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        # Processing spinner (hidden by default)
        self._status_spinner = SpinnerWidget(16)
        self._status_spinner.hide()
        self._status_bar.addWidget(self._status_spinner)

        self._status_label = QLabel(self.tr("Ready"))
        self._status_bar.addWidget(self._status_label, stretch=1)

        settings = get_settings()
        self._provider_label = QLabel(f"LLM: {settings.llm.provider.value.title()}")
        self._status_bar.addPermanentWidget(self._provider_label)

    def _connect_signals(self) -> None:
        """Connect signals."""
        # File browser signals
        self._file_browser.file_selected.connect(self._on_file_selected)
        self._file_browser.file_double_clicked.connect(self._on_file_double_clicked)

        # Orchestrator signals
        self._orchestrator.stage_started.connect(self._on_stage_started)
        self._orchestrator.stage_progress.connect(self._on_stage_progress)
        self._orchestrator.stage_completed.connect(self._on_stage_completed)
        self._orchestrator.stage_error.connect(self._on_stage_error)
        self._orchestrator.processing_complete.connect(self._on_processing_complete)
        self._orchestrator.processing_error.connect(self._on_processing_error)

    def _configure_orchestrator(self) -> None:
        """Configure the processing orchestrator from settings and mode selector."""
        settings = get_settings()

        # Get scoring parameters from profile
        profile_manager = get_profile_manager()
        profile = profile_manager.get_current_profile()
        enabled_params = profile.get_enabled_parameters()

        # Pass parameters with max_score and weight directly
        # The audit worker will apply weights during calculation
        scoring_parameters = []
        for p in enabled_params:
            scoring_parameters.append(
                {
                    "name": p.name,
                    "max_score": p.max_score,
                    "weight": p.weight,
                    "description": p.description,
                }
            )

        # Language mode mapping
        LANGUAGE_CODE_MAP = {
            "auto": None,  # Auto-detect
            "english": "en",
            "hindi-english": "hi",  # Special: uses HindiSTT
            "spanish": "es",
            "french": "fr",
            "german": "de",
            "italian": "it",
            "portuguese": "pt",
            "russian": "ru",
            "japanese": "ja",
            "korean": "ko",
            "chinese": "zh",
            "arabic": "ar",
            "turkish": "tr",
            "dutch": "nl",
        }

        # Check if Hindi mode is enabled from mode selector
        use_hindi_stt = False
        hindi_model_variant = "apex"  # Default
        use_preprocessing = True  # Default ON
        language_code = None  # Default to auto-detect

        if self._mode_selector.get_mode() == ProcessingMode.OFFLINE:
            language_mode = self._mode_selector.get_language_mode()
            use_hindi_stt = language_mode == "hindi-english"

            if use_hindi_stt:
                hindi_model_variant = self._mode_selector.get_hindi_model_variant()

            # Map language mode to Whisper language code
            language_code = LANGUAGE_CODE_MAP.get(language_mode, None)

            # Get audio preprocessing setting (applies to all modes)
            use_preprocessing = self._mode_selector.is_preprocessing_enabled()

        # Get whisper model from mode selector (for offline mode)
        whisper_model = self._mode_selector.get_whisper_model()

        self._orchestrator.configure(
            whisper_model=whisper_model,
            language=language_code,
            use_gpu=settings.transcription.use_gpu,
            dual_channel=True,
            use_hindi_stt=use_hindi_stt,
            hindi_model_variant=hindi_model_variant,
            use_preprocessing=use_preprocessing,
            scoring_parameters=scoring_parameters,
            transcription_only=not self._mode_selector.is_scoring_enabled(),
        )

    @Slot()
    def _on_open_file(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Audio File",
            str(Path.home()),
            "Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac *.webm);;All Files (*.*)",
        )
        if filepath:
            self._current_file = Path(filepath)
            self._file_browser.select_file(filepath)
            self._status_label.setText(f"Selected: {self._current_file.name}")

    @Slot(str)
    def _on_file_selected(self, filepath: str) -> None:
        self._current_file = Path(filepath)
        self._status_label.setText(f"Selected: {self._current_file.name}")

    @Slot(str)
    def _on_file_double_clicked(self, filepath: str) -> None:
        self._current_file = Path(filepath)
        self._on_process()

    @Slot(ProcessingMode)
    def _on_mode_changed(self, mode: ProcessingMode) -> None:
        """Handle processing mode change."""
        if mode == ProcessingMode.ONLINE:
            provider = self._mode_selector.get_provider()
            self._status_label.setText(f"Online mode - {provider}")
            self._provider_label.setText(f"Provider: {provider}")
        else:
            self._status_label.setText("Offline mode - 100% private")
            self._provider_label.setText("Mode: Offline")

    @Slot()
    def _on_mode_settings_changed(self) -> None:
        """Handle mode settings change."""
        mode = self._mode_selector.get_mode()
        if mode == ProcessingMode.ONLINE:
            provider = self._mode_selector.get_provider()
            model = self._mode_selector.get_model()
            self._provider_label.setText(f"{provider}: {model}")
        else:
            whisper_model = self._mode_selector.get_whisper_model()
            self._provider_label.setText(f"Whisper: {whisper_model}")

    @Slot()
    def _on_process(self) -> None:
        if not self._current_file:
            QMessageBox.information(self, "No File", "Please select an audio file first.")
            return

        if self._orchestrator.is_processing:
            QMessageBox.information(self, "Processing", "Processing is already in progress.")
            return

        # Reconfigure orchestrator with current settings
        self._configure_orchestrator()

        # Clear previous results
        self._results_viewer.clear()
        self._progress_panel.reset()

        # Start processing
        mode = self._mode_selector.get_mode()
        if mode == ProcessingMode.OFFLINE and self._mode_selector.is_hindi_mode():
            variant = self._mode_selector.get_hindi_model_variant()
            variant_name = "Apex" if variant == "apex" else "Prime"
            self._status_label.setText(
                f"Processing (Hindi {variant_name}): {self._current_file.name}"
            )
        else:
            self._status_label.setText(f"Processing: {self._current_file.name}")

        # Show status spinner
        self._status_spinner.start()

        self._progress_panel.start_full_process()
        self.processing_started.emit()

        self._orchestrator.start(str(self._current_file))

    @Slot()
    def _on_stop(self) -> None:
        self._orchestrator.stop()
        self._progress_panel.stop()
        self._status_spinner.stop()
        self._status_label.setText("Stopped")

    @Slot(str)
    def _on_stage_started(self, stage: str) -> None:
        """Handle stage start."""
        stage_map = {
            "transcription": "Transcribing audio...",
            "merge": "Merging transcript...",
            "audit": "Auditing quality...",
        }
        message = stage_map.get(stage, f"Processing {stage}...")
        self._status_label.setText(message)

    @Slot(str, int, str)
    def _on_stage_progress(self, stage: str, percent: int, message: str) -> None:
        """Handle stage progress update."""
        if stage == "transcription":
            self._progress_panel.update_transcription_progress(percent)
        elif stage == "merge":
            self._progress_panel.update_merge_progress(percent)
        elif stage == "audit":
            self._progress_panel.update_audit_progress(percent)

        if message:
            self._status_label.setText(message)

    @Slot(str)
    def _on_stage_completed(self, stage: str) -> None:
        """Handle stage completion."""
        if stage == "transcription":
            self._progress_panel.complete_transcription()
        elif stage == "merge":
            self._progress_panel.complete_merge()
        elif stage == "audit":
            self._progress_panel.complete_audit()

    @Slot(str, str)
    def _on_stage_error(self, stage: str, error: str) -> None:
        """Handle stage error."""
        stage_enum = {
            "transcription": ProcessingStage.TRANSCRIBING,
            "merge": ProcessingStage.MERGING,
            "audit": ProcessingStage.AUDITING,
        }.get(stage, ProcessingStage.ERROR)

        self._progress_panel.set_error(stage_enum, error)

    @Slot(object)
    def _on_processing_complete(self, result: ProcessingResult) -> None:
        """Handle processing completion."""
        self._progress_panel.complete_all()
        self._status_spinner.stop()
        self._status_label.setText("Processing complete")
        self.processing_finished.emit()

        # Build display data
        display_data = result.to_dict()

        # For transcription-only mode, format the data for the viewer
        if result.transcription and not result.audit:
            display_data["transcript"] = result.transcription.text
            display_data["segments"] = (
                [
                    {
                        "speaker": s.speaker or "Speaker",
                        "text": s.text,
                        "start": s.start,
                        "end": s.end,
                    }
                    for s in result.transcription.segments
                ]
                if result.transcription.segments
                else []
            )
            display_data["language"] = result.transcription.language
            display_data["file_name"] = self._current_file.name if self._current_file else "audio"
            # Add placeholder scores for transcription-only
            display_data["overall_score"] = 0
            display_data["max_score"] = 100

        # Load results into viewer
        has_transcript = (
            display_data.get("transcript") and len(display_data.get("transcript", "").strip()) > 0
        )

        if has_transcript or result.audit:
            self._results_viewer.load_results(display_data)
            # Force show the Transcript tab for transcription-only mode
            if not result.audit:
                self._results_viewer.setCurrentIndex(0)
        elif result.transcription is not None:
            # Transcription completed but returned empty - likely model limitation
            self._toast_manager.show_warning(
                "Transcription returned empty. Try a larger model (e.g., 'small' or 'medium') for better results with non-English audio.",
                duration=8000,
            )
            self._status_label.setText("Transcription empty - try larger model")
            return

        # Show success toast
        if result.audit:
            score = result.audit.overall_score
            self._toast_manager.show_success(
                f"Processing complete! Score: {score:.1f}%",
                action_text="View Results",
                action_callback=lambda: self._results_viewer.setCurrentIndex(0),
            )
        else:
            # Transcription-only mode
            self._toast_manager.show_success(
                "Transcription complete!",
                action_text="View Transcript",
                action_callback=lambda: self._results_viewer.setCurrentIndex(0),
            )

        # Auto-save transcript for transcription-only mode
        if result.transcription and not result.audit and self._current_file:
            transcript_path = (
                self._current_file.parent / f"{self._current_file.stem}_transcript.txt"
            )
            try:
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(f"Transcript: {self._current_file.name}\n")
                    f.write(f"Language: {result.transcription.language or 'unknown'}\n")
                    f.write("=" * 50 + "\n\n")
                    if result.transcription.segments:
                        for seg in result.transcription.segments:
                            speaker_label = f"[{seg.speaker}] " if seg.speaker else ""
                            f.write(
                                f"[{seg.start:.1f}s - {seg.end:.1f}s] {speaker_label}{seg.text}\n\n"
                            )
                    else:
                        f.write(result.transcription.text)
                self._toast_manager.show_info(f"Transcript saved: {transcript_path.name}")
            except Exception as e:
                print(f"Failed to auto-save transcript: {e}")

        # Auto-export if configured
        settings = get_settings()
        if settings.output.auto_export_json and settings.output.output_directory:
            output_path = (
                Path(settings.output.output_directory) / f"{self._current_file.stem}_result.json"
            )
            self._results_viewer.export_json(str(output_path))
            self._toast_manager.show_info(f"Results exported to {output_path.name}")

    @Slot(str)
    def _on_processing_error(self, error: str) -> None:
        """Handle processing error."""
        self._status_spinner.stop()
        self._status_label.setText(f"Error: {error}")

        # Show error toast
        self._toast_manager.show_error(
            f"Processing failed: {error[:100]}...",
            duration=6000,
        )

        self._error_handler.handle_error(
            Exception(error),
            title="Processing Error",
            message=f"An error occurred during processing:\n\n{error}",
            show_dialog=True,
        )

    @Slot()
    def _on_export_transcript(self) -> None:
        """Export transcript as text file."""
        default_name = "transcript.txt"
        if self._current_file:
            default_name = f"{self._current_file.stem}_transcript.txt"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Transcript", str(Path.home() / default_name), "Text Files (*.txt)"
        )
        if filepath:
            self._results_viewer.export_transcript(filepath)

    @Slot()
    def _on_export_json(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", str(Path.home() / "result.json"), "JSON (*.json)"
        )
        if filepath:
            self._results_viewer.export_json(filepath)

    @Slot()
    def _on_export_markdown_report(self) -> None:
        """Export audit report as markdown file for skill improvement."""
        default_name = "audit_report.md"
        if self._current_file:
            default_name = f"{self._current_file.stem}_audit_report.md"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown Report", str(Path.home() / default_name), "Markdown Files (*.md)"
        )
        if filepath:
            self._results_viewer.export_markdown_report(filepath)

    @Slot()
    def _on_export_pdf(self) -> None:
        """Export audit report as PDF file."""
        default_name = "audit_report.pdf"
        if self._current_file:
            default_name = f"{self._current_file.stem}_audit_report.pdf"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export PDF Report", str(Path.home() / default_name), "PDF Files (*.pdf)"
        )
        if filepath:
            self._results_viewer.export_pdf(filepath)

    @Slot()
    def _on_edit_scoring(self) -> None:
        """Open the scoring parameters editor."""
        dialog = ScoringEditorDialog(self)
        dialog.profile_saved.connect(self._on_scoring_profile_saved)
        dialog.exec()

    @Slot(str)
    def _on_scoring_profile_saved(self, profile_name: str) -> None:
        """Handle scoring profile save."""
        # Update orchestrator with new parameters
        profile_manager = get_profile_manager()
        profile = profile_manager.get_current_profile()
        enabled_params = profile.get_enabled_parameters()

        # Convert weighted parameters to point allocation out of 100
        total_weighted = sum(p.max_score * p.weight for p in enabled_params)

        parameters = []
        for p in enabled_params:
            # Calculate points: (max_score * weight / total_weighted) * 100
            if total_weighted > 0:
                points = (p.max_score * p.weight / total_weighted) * 100
            else:
                points = 0

            parameters.append(
                {
                    "name": p.name,
                    "points": points,  # Use new points format
                    "max_score": p.max_score,  # Keep for backward compatibility
                    "weight": p.weight,  # Keep for backward compatibility
                    "description": p.description,
                }
            )

        self._orchestrator.configure(scoring_parameters=parameters)
        self._status_label.setText(f"Scoring profile '{profile_name}' loaded")

    @Slot()
    def _on_open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            settings = get_settings()
            provider = settings.llm.provider
            provider_name = provider.value if hasattr(provider, "value") else str(provider)
            self._provider_label.setText(f"LLM: {provider_name.title()}")
            self._configure_orchestrator()

    @Slot()
    def _on_show_shortcuts(self) -> None:
        """Show keyboard shortcuts dialog."""
        shortcuts_html = """
        <h3>Keyboard Shortcuts</h3>
        <table style="margin: 10px;">
            <tr><td><b>Ctrl+O</b></td><td>Open audio file</td></tr>
            <tr><td><b>Ctrl+Return</b></td><td>Process audio</td></tr>
            <tr><td><b>Escape</b></td><td>Stop processing</td></tr>
            <tr><td><b>Ctrl+Shift+T</b></td><td>Export transcript</td></tr>
            <tr><td><b>Ctrl+Shift+J</b></td><td>Export as JSON</td></tr>
            <tr><td><b>Ctrl+Shift+P</b></td><td>Export PDF report</td></tr>
            <tr><td><b>Ctrl+Shift+S</b></td><td>Edit scoring parameters</td></tr>
            <tr><td><b>Ctrl+,</b></td><td>Open settings</td></tr>
            <tr><td><b>Ctrl+/</b></td><td>Show shortcuts</td></tr>
            <tr><td><b>Ctrl+Q</b></td><td>Quit application</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_html)

    @Slot()
    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {__app_name__}",
            f"<h3>{__app_name__}</h3>"
            f"<p>Version {__version__}</p>"
            "<p>Free, open-source AI for audio transcription and quality auditing.</p>"
            "<p>Works 100% offline with local models.</p>"
            "<p>MIT License</p>",
        )

    def show_first_run_wizard(self) -> None:
        """Show first-run setup wizard."""
        settings = get_settings()
        if not settings.app.first_run_complete:
            wizard = SetupWizard(self)
            wizard.setup_complete.connect(self._on_setup_complete)
            wizard.exec()

    @Slot()
    def _on_setup_complete(self) -> None:
        """Handle setup wizard completion."""
        self._status_label.setText("Setup complete - ready to process audio")
        self._configure_orchestrator()

    def closeEvent(self, event) -> None:
        """Save window state on close."""
        # Stop any running processing
        if self._orchestrator.is_processing:
            self._orchestrator.stop()

        settings = get_settings()
        settings.app.window_width = self.width()
        settings.app.window_height = self.height()
        settings.app.window_x = self.x()
        settings.app.window_y = self.y()
        settings.app.first_run_complete = True
        save_settings(settings)
        event.accept()
