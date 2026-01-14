"""
CallScore Desktop Main Window

The main application window with menu bar, file browser, and results panels.
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QMenuBar,
    QMenu,
    QStatusBar,
    QToolBar,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QLabel,
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QThreadPool
from PySide6.QtGui import QAction, QKeySequence, QIcon

from desktop import __app_name__, __version__
from desktop.config.user_settings import (
    get_settings_manager,
    get_settings,
    save_settings,
    SettingsManager,
)
from desktop.ui.file_browser import FileBrowserPanel
from desktop.ui.progress_panel import ProgressPanel, ProcessingStage
from desktop.ui.results_viewer import ResultsViewer
from desktop.ui.settings_dialog import SettingsDialog
from desktop.workers import ProcessingWorker, TranscriptionOnlyWorker


class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    file_selected = Signal(str)  # Emitted when an audio file is selected
    processing_started = Signal()
    processing_finished = Signal()
    processing_error = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._settings_manager = get_settings_manager()
        self._current_file: Optional[Path] = None
        self._recent_files: List[str] = []
        self._current_worker: Optional[ProcessingWorker] = None

        # Thread pool for background processing
        self._thread_pool = QThreadPool.globalInstance()
        self._thread_pool.setMaxThreadCount(1)  # Process one file at a time

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        self.setWindowTitle(__app_name__)
        self.setMinimumSize(800, 600)

        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main splitter for resizable panels
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: File browser
        self._file_browser = FileBrowserPanel()
        self._splitter.addWidget(self._file_browser)

        # Right panel: Progress and Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)

        # Progress panel
        self._progress_panel = ProgressPanel()
        right_layout.addWidget(self._progress_panel)

        # Results viewer
        self._results_viewer = ResultsViewer()
        right_layout.addWidget(self._results_viewer, stretch=1)

        self._splitter.addWidget(right_panel)

        # Set initial splitter sizes (30% file browser, 70% results)
        self._splitter.setSizes([300, 700])

        main_layout.addWidget(self._splitter)

    def _setup_menu_bar(self) -> None:
        """Set up the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Audio File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self._on_open_folder)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        # Recent files submenu
        self._recent_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()

        file_menu.addSeparator()

        export_json_action = QAction("Export as &JSON...", self)
        export_json_action.setShortcut("Ctrl+E")
        export_json_action.triggered.connect(self._on_export_json)
        file_menu.addAction(export_json_action)

        export_pdf_action = QAction("Export as &PDF...", self)
        export_pdf_action.setShortcut("Ctrl+P")
        export_pdf_action.triggered.connect(self._on_export_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        scoring_action = QAction("&Scoring Parameters...", self)
        scoring_action.triggered.connect(self._on_edit_scoring)
        edit_menu.addAction(scoring_action)

        edit_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self._on_open_settings)
        edit_menu.addAction(settings_action)

        # Process menu
        process_menu = menubar.addMenu("&Process")

        transcribe_action = QAction("&Transcribe", self)
        transcribe_action.setShortcut("Ctrl+T")
        transcribe_action.triggered.connect(self._on_transcribe)
        process_menu.addAction(transcribe_action)

        audit_action = QAction("&Audit Call", self)
        audit_action.setShortcut("Ctrl+A")
        audit_action.triggered.connect(self._on_audit)
        process_menu.addAction(audit_action)

        process_menu.addSeparator()

        full_process_action = QAction("&Full Process (Transcribe + Audit)", self)
        full_process_action.setShortcut("Ctrl+Return")
        full_process_action.triggered.connect(self._on_full_process)
        process_menu.addAction(full_process_action)

        process_menu.addSeparator()

        stop_action = QAction("&Stop Processing", self)
        stop_action.setShortcut("Escape")
        stop_action.triggered.connect(self._on_stop_processing)
        process_menu.addAction(stop_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(self._on_open_docs)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QAction("&About CallScore", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Open file button
        open_action = QAction("Open", self)
        open_action.setToolTip("Open audio file (Ctrl+O)")
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Process button
        process_action = QAction("Process", self)
        process_action.setToolTip("Full process: Transcribe + Audit (Ctrl+Return)")
        process_action.triggered.connect(self._on_full_process)
        toolbar.addAction(process_action)

        # Stop button
        stop_action = QAction("Stop", self)
        stop_action.setToolTip("Stop processing (Escape)")
        stop_action.triggered.connect(self._on_stop_processing)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # Export buttons
        export_json_action = QAction("JSON", self)
        export_json_action.setToolTip("Export results as JSON")
        export_json_action.triggered.connect(self._on_export_json)
        toolbar.addAction(export_json_action)

        export_pdf_action = QAction("PDF", self)
        export_pdf_action.setToolTip("Export results as PDF")
        export_pdf_action.triggered.connect(self._on_export_pdf)
        toolbar.addAction(export_pdf_action)

        toolbar.addSeparator()

        # Settings button
        settings_action = QAction("Settings", self)
        settings_action.setToolTip("Open settings")
        settings_action.triggered.connect(self._on_open_settings)
        toolbar.addAction(settings_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        # Status label
        self._status_label = QLabel("Ready")
        self._status_bar.addWidget(self._status_label, stretch=1)

        # LLM provider indicator
        settings = get_settings()
        provider_text = f"LLM: {settings.llm.provider.value.title()}"
        self._provider_label = QLabel(provider_text)
        self._status_bar.addPermanentWidget(self._provider_label)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._file_browser.file_selected.connect(self._on_file_selected)
        self._file_browser.file_double_clicked.connect(self._on_file_double_clicked)

    def _update_recent_files_menu(self) -> None:
        """Update the recent files menu."""
        self._recent_menu.clear()

        if not self._recent_files:
            no_recent = QAction("No recent files", self)
            no_recent.setEnabled(False)
            self._recent_menu.addAction(no_recent)
            return

        for filepath in self._recent_files[:10]:
            action = QAction(Path(filepath).name, self)
            action.setData(filepath)
            action.triggered.connect(lambda checked, p=filepath: self._open_file(p))
            self._recent_menu.addAction(action)

    def _add_to_recent_files(self, filepath: str) -> None:
        """Add a file to the recent files list."""
        if filepath in self._recent_files:
            self._recent_files.remove(filepath)
        self._recent_files.insert(0, filepath)
        self._recent_files = self._recent_files[:10]
        self._update_recent_files_menu()

    def _open_file(self, filepath: str) -> None:
        """Open and select an audio file."""
        path = Path(filepath)
        if path.exists():
            self._current_file = path
            self._file_browser.select_file(str(path))
            self._add_to_recent_files(str(path))
            self._status_label.setText(f"Selected: {path.name}")
            self.file_selected.emit(str(path))
        else:
            QMessageBox.warning(self, "File Not Found", f"Could not find file:\n{filepath}")

    # Slot handlers
    @Slot()
    def _on_open_file(self) -> None:
        """Handle open file action."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Audio File",
            str(Path.home()),
            "Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac *.webm);;All Files (*.*)"
        )
        if filepath:
            self._open_file(filepath)

    @Slot()
    def _on_open_folder(self) -> None:
        """Handle open folder action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            str(Path.home())
        )
        if folder:
            self._file_browser.set_directory(folder)

    @Slot(str)
    def _on_file_selected(self, filepath: str) -> None:
        """Handle file selection in browser."""
        self._current_file = Path(filepath)
        self._status_label.setText(f"Selected: {self._current_file.name}")

    @Slot(str)
    def _on_file_double_clicked(self, filepath: str) -> None:
        """Handle file double-click - start processing."""
        self._open_file(filepath)
        self._on_full_process()

    @Slot()
    def _on_transcribe(self) -> None:
        """Handle transcribe action."""
        if not self._current_file:
            QMessageBox.information(self, "No File Selected", "Please select an audio file first.")
            return

        if self._current_worker is not None:
            QMessageBox.warning(self, "Processing", "A file is already being processed.")
            return

        self._status_label.setText(f"Transcribing: {self._current_file.name}")
        self._progress_panel.start_transcription()

        # Create and start transcription-only worker
        settings = get_settings()
        self._current_worker = TranscriptionOnlyWorker(
            audio_path=str(self._current_file),
            settings=settings,
        )

        # Connect worker signals
        self._connect_worker_signals(self._current_worker)

        # Start processing
        self._thread_pool.start(self._current_worker)
        self.processing_started.emit()

    @Slot()
    def _on_audit(self) -> None:
        """Handle audit action."""
        if not self._current_file:
            QMessageBox.information(self, "No File Selected", "Please select an audio file first.")
            return

        # Audit requires transcript first - run full process
        QMessageBox.information(
            self,
            "Audit",
            "Audit requires transcription. Starting full process (Transcribe + Audit)."
        )
        self._on_full_process()

    @Slot()
    def _on_full_process(self) -> None:
        """Handle full process (transcribe + audit) action."""
        if not self._current_file:
            QMessageBox.information(self, "No File Selected", "Please select an audio file first.")
            return

        if self._current_worker is not None:
            QMessageBox.warning(self, "Processing", "A file is already being processed.")
            return

        self._status_label.setText(f"Processing: {self._current_file.name}")
        self._add_to_recent_files(str(self._current_file))
        self._progress_panel.start_full_process()

        # Create and start full processing worker
        settings = get_settings()
        self._current_worker = ProcessingWorker(
            audio_path=str(self._current_file),
            settings=settings,
            run_audit=True,
        )

        # Connect worker signals
        self._connect_worker_signals(self._current_worker)

        # Start processing
        self._thread_pool.start(self._current_worker)
        self.processing_started.emit()

    def _connect_worker_signals(self, worker) -> None:
        """Connect worker signals to UI handlers."""
        worker.signals.progress.connect(self._on_worker_progress)
        worker.signals.stage_changed.connect(self._on_worker_stage_changed)
        worker.signals.finished.connect(self._on_worker_finished)
        worker.signals.error.connect(self._on_worker_error)
        worker.signals.cancelled.connect(self._on_worker_cancelled)

    @Slot(int, str)
    def _on_worker_progress(self, percentage: int, message: str) -> None:
        """Handle worker progress update."""
        self._progress_panel.set_progress(percentage)
        self._progress_panel.set_detail(message)

    @Slot(object)
    def _on_worker_stage_changed(self, stage) -> None:
        """Handle worker stage change."""
        # Map worker stage to UI stage
        stage_map = {
            "loading_models": ProcessingStage.LOADING_MODELS,
            "preprocessing": ProcessingStage.PREPROCESSING,
            "diarization": ProcessingStage.DIARIZATION,
            "transcription_v3": ProcessingStage.TRANSCRIPTION,
            "transcription_h2h": ProcessingStage.TRANSCRIPTION,
            "merging": ProcessingStage.MERGING,
            "auditing": ProcessingStage.AUDITING,
            "complete": ProcessingStage.COMPLETE,
        }
        ui_stage = stage_map.get(stage.stage_id, ProcessingStage.TRANSCRIPTION)
        self._progress_panel.set_stage(ui_stage)

    @Slot(object)
    def _on_worker_finished(self, result: dict) -> None:
        """Handle worker completion."""
        self._current_worker = None
        self._progress_panel.complete(success=True)
        self._status_label.setText("Processing complete")

        # Display results
        self._results_viewer.set_results(result)

        self.processing_finished.emit()

    @Slot(str, str)
    def _on_worker_error(self, error_type: str, message: str) -> None:
        """Handle worker error."""
        self._current_worker = None
        self._progress_panel.error(message)
        self._status_label.setText(f"Error: {error_type}")

        QMessageBox.critical(
            self,
            f"Processing Error: {error_type}",
            f"An error occurred while processing:\n\n{message}"
        )

        self.processing_error.emit(message)

    @Slot()
    def _on_worker_cancelled(self) -> None:
        """Handle worker cancellation."""
        self._current_worker = None
        self._progress_panel.stop()
        self._status_label.setText("Processing cancelled")

    @Slot()
    def _on_stop_processing(self) -> None:
        """Handle stop processing action."""
        if self._current_worker is not None:
            self._current_worker.cancel()
            self._status_label.setText("Cancelling...")
        else:
            self._status_label.setText("No processing to stop")
            self._progress_panel.reset()

    @Slot()
    def _on_export_json(self) -> None:
        """Handle export as JSON action."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export as JSON",
            str(Path.home() / "callscore_result.json"),
            "JSON Files (*.json)"
        )
        if filepath:
            self._results_viewer.export_json(filepath)
            self._status_label.setText(f"Exported to: {Path(filepath).name}")

    @Slot()
    def _on_export_pdf(self) -> None:
        """Handle export as PDF action."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export as PDF",
            str(Path.home() / "callscore_report.pdf"),
            "PDF Files (*.pdf)"
        )
        if filepath:
            self._results_viewer.export_pdf(filepath)
            self._status_label.setText(f"Exported to: {Path(filepath).name}")

    @Slot()
    def _on_edit_scoring(self) -> None:
        """Handle edit scoring parameters action."""
        # TODO: Open scoring editor dialog
        QMessageBox.information(self, "Coming Soon", "Scoring parameter editor will be available soon.")

    @Slot()
    def _on_open_settings(self) -> None:
        """Handle open settings action."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Settings were saved, update UI
            settings = get_settings()
            provider_text = f"LLM: {settings.llm.provider.value.title()}"
            self._provider_label.setText(provider_text)

    @Slot()
    def _on_open_docs(self) -> None:
        """Handle open documentation action."""
        import webbrowser
        webbrowser.open("https://github.com/KaivalyaDeepTeam/callscore")

    @Slot()
    def _on_about(self) -> None:
        """Handle about action."""
        QMessageBox.about(
            self,
            f"About {__app_name__}",
            f"<h3>{__app_name__}</h3>"
            f"<p>Version {__version__}</p>"
            "<p>Free, open-source AI-powered call transcription and quality auditing.</p>"
            "<p>Works 100% offline with local models.</p>"
            '<p><a href="https://github.com/KaivalyaDeepTeam/callscore">GitHub Repository</a></p>'
            "<p>Licensed under MIT License</p>"
        )

    def show_first_run_wizard(self) -> None:
        """Show the first-run setup wizard."""
        # TODO: Implement first-run wizard for model downloads
        settings = get_settings()
        if not settings.app.whisper_models_downloaded:
            result = QMessageBox.question(
                self,
                "Welcome to CallScore",
                "This appears to be your first time running CallScore.\n\n"
                "Before you can transcribe audio, you need to download the AI models "
                "(approximately 4.5 GB).\n\n"
                "Would you like to download the models now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                # TODO: Start model download
                pass

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Save window geometry
        settings = get_settings()
        settings.app.window_width = self.width()
        settings.app.window_height = self.height()
        settings.app.window_x = self.x()
        settings.app.window_y = self.y()
        settings.app.first_run_complete = True
        save_settings(settings)

        event.accept()
