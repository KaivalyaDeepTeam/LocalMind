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
from localmind.ui.progress_panel import ProgressPanel
from localmind.ui.results_viewer import ResultsViewer
from localmind.ui.settings_dialog import SettingsDialog


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

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._connect_signals()

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
        export_json.triggered.connect(self._on_export_json)
        file_menu.addAction(export_json)

        export_pdf = QAction("Export as &PDF...", self)
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
        self._file_browser.file_selected.connect(self._on_file_selected)
        self._file_browser.file_double_clicked.connect(self._on_file_double_clicked)

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
        self._status_label.setText(f"Processing: {self._current_file.name}")
        self._progress_panel.start_full_process()
        # TODO: Start processing worker

    @Slot()
    def _on_stop(self) -> None:
        self._progress_panel.stop()
        self._status_label.setText("Stopped")

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
        QMessageBox.information(self, "Coming Soon", "Scoring editor coming soon.")

    @Slot()
    def _on_open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            settings = get_settings()
            self._provider_label.setText(f"LLM: {settings.llm.provider.value.title()}")

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
        """Show first-run setup."""
        settings = get_settings()
        if not settings.app.whisper_models_downloaded:
            result = QMessageBox.question(
                self, "Welcome to LocalMind",
                "Download AI models (4.5 GB) to get started?\n\n"
                "This is required for transcription.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                pass  # TODO: Start download

    def closeEvent(self, event) -> None:
        """Save window state on close."""
        settings = get_settings()
        settings.app.window_width = self.width()
        settings.app.window_height = self.height()
        settings.app.window_x = self.x()
        settings.app.window_y = self.y()
        settings.app.first_run_complete = True
        save_settings(settings)
        event.accept()
