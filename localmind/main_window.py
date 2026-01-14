"""
LocalMind Main Window

The main application window with menu bar, file browser, and results panels.
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStatusBar, QToolBar, QFileDialog, QMessageBox, QLabel,
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QAction, QKeySequence

from localmind import __app_name__, __version__
from localmind.config import get_settings_manager, get_settings, save_settings
from localmind.ui.file_browser import FileBrowserPanel
from localmind.ui.progress_panel import ProgressPanel, ProcessingStage
from localmind.ui.results_viewer import ResultsViewer
from localmind.ui.settings_dialog import SettingsDialog
from localmind.ui.scoring_editor import ScoringEditorDialog
from localmind.ui.setup_wizard import SetupWizard
from localmind.ui.toast import ToastManager, ToastType, init_toast_manager
from localmind.workers import ProcessingOrchestrator, ProcessingResult
from localmind.config import get_profile_manager
from localmind.utils import get_error_handler, ErrorContext, ErrorMessages


class MainWindow(QMainWindow):
    """Main application window."""

    file_selected = Signal(str)
    processing_started = Signal()
    processing_finished = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._settings_manager = get_settings_manager()
        self._current_file: Optional[Path] = None
        self._recent_files: List[str] = []

        # Processing orchestrator
        self._orchestrator = ProcessingOrchestrator(self)

        # Initialize error handler with this window as parent
        self._error_handler = get_error_handler()
        self._error_handler.set_parent_widget(self)

        # Initialize toast notification manager
        self._toast_manager = init_toast_manager(self)

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._connect_signals()
        self._configure_orchestrator()

    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        self.setWindowTitle(__app_name__)
        self.setMinimumSize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: File browser
        self._file_browser = FileBrowserPanel()
        splitter.addWidget(self._file_browser)

        # Right: Progress and Results
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)

        self._progress_panel = ProgressPanel()
        right_layout.addWidget(self._progress_panel)

        self._results_viewer = ResultsViewer()
        right_layout.addWidget(self._results_viewer, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Audio File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_json = QAction("Export as &JSON...", self)
        export_json.setShortcut("Ctrl+Shift+J")
        export_json.triggered.connect(self._on_export_json)
        file_menu.addAction(export_json)

        export_pdf = QAction("Export as &PDF...", self)
        export_pdf.setShortcut("Ctrl+Shift+P")
        export_pdf.triggered.connect(self._on_export_pdf)
        file_menu.addAction(export_pdf)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        scoring_action = QAction("&Scoring Parameters...", self)
        scoring_action.setShortcut("Ctrl+Shift+S")
        scoring_action.triggered.connect(self._on_edit_scoring)
        edit_menu.addAction(scoring_action)

        edit_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self._on_open_settings)
        edit_menu.addAction(settings_action)

        # Process menu
        process_menu = menubar.addMenu("&Process")

        process_action = QAction("&Process Audio", self)
        process_action.setShortcut("Ctrl+Return")
        process_action.triggered.connect(self._on_process)
        process_menu.addAction(process_action)

        process_menu.addSeparator()

        stop_action = QAction("&Stop", self)
        stop_action.setShortcut("Escape")
        stop_action.triggered.connect(self._on_stop)
        process_menu.addAction(stop_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("Ctrl+/")
        shortcuts_action.triggered.connect(self._on_show_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        about_action = QAction("&About LocalMind", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        process_action = QAction("Process", self)
        process_action.triggered.connect(self._on_process)
        toolbar.addAction(process_action)

        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self._on_stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._on_open_settings)
        toolbar.addAction(settings_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._status_label = QLabel("Ready")
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
        """Configure the processing orchestrator from settings."""
        settings = get_settings()

        # Get scoring parameters from profile
        profile_manager = get_profile_manager()
        profile = profile_manager.get_current_profile()
        scoring_parameters = [
            {
                "name": p.name,
                "max_score": p.max_score,
                "weight": p.weight,
                "description": p.description,
            }
            for p in profile.get_enabled_parameters()
        ]

        self._orchestrator.configure(
            whisper_model=settings.transcription.whisper_model,
            language=settings.transcription.language if settings.transcription.language != "auto" else None,
            use_gpu=settings.transcription.use_gpu,
            dual_channel=True,
            scoring_parameters=scoring_parameters,
        )

    @Slot()
    def _on_open_file(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", str(Path.home()),
            "Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac *.webm);;All Files (*.*)"
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

    @Slot()
    def _on_process(self) -> None:
        if not self._current_file:
            QMessageBox.information(self, "No File", "Please select an audio file first.")
            return

        if self._orchestrator.is_processing:
            QMessageBox.information(self, "Processing", "Processing is already in progress.")
            return

        # Clear previous results
        self._results_viewer.clear()
        self._progress_panel.reset()

        # Start processing
        self._status_label.setText(f"Processing: {self._current_file.name}")
        self._progress_panel.start_full_process()
        self.processing_started.emit()

        self._orchestrator.start(str(self._current_file))

    @Slot()
    def _on_stop(self) -> None:
        self._orchestrator.stop()
        self._progress_panel.stop()
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
        self._status_label.setText("Processing complete")
        self.processing_finished.emit()

        # Load results into viewer
        if result.audit:
            self._results_viewer.load_results(result.to_dict())

        # Show success toast
        score = result.audit.overall_score if result.audit else 0
        self._toast_manager.show_success(
            f"Processing complete! Score: {score:.1f}%",
            action_text="View Results",
            action_callback=lambda: self._results_viewer.setCurrentIndex(0),
        )

        # Auto-export if configured
        settings = get_settings()
        if settings.output.auto_export_json and settings.output.output_directory:
            output_path = Path(settings.output.output_directory) / f"{self._current_file.stem}_result.json"
            self._results_viewer.export_json(str(output_path))
            self._toast_manager.show_info(f"Results exported to {output_path.name}")

    @Slot(str)
    def _on_processing_error(self, error: str) -> None:
        """Handle processing error."""
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
    def _on_export_json(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", str(Path.home() / "result.json"), "JSON (*.json)"
        )
        if filepath:
            self._results_viewer.export_json(filepath)

    @Slot()
    def _on_export_pdf(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", str(Path.home() / "report.pdf"), "PDF (*.pdf)"
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
        parameters = [
            {
                "name": p.name,
                "max_score": p.max_score,
                "weight": p.weight,
                "description": p.description,
            }
            for p in profile.get_enabled_parameters()
        ]
        self._orchestrator.configure(scoring_parameters=parameters)
        self._status_label.setText(f"Scoring profile '{profile_name}' loaded")

    @Slot()
    def _on_open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            settings = get_settings()
            self._provider_label.setText(f"LLM: {settings.llm.provider.value.title()}")
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
            <tr><td><b>Ctrl+Shift+J</b></td><td>Export as JSON</td></tr>
            <tr><td><b>Ctrl+Shift+P</b></td><td>Export as PDF</td></tr>
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
            self, f"About {__app_name__}",
            f"<h3>{__app_name__}</h3>"
            f"<p>Version {__version__}</p>"
            "<p>Free, open-source AI for audio transcription and quality auditing.</p>"
            "<p>Works 100% offline with local models.</p>"
            "<p>MIT License</p>"
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
