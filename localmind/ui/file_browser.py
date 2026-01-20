"""
LocalMind File Browser Panel

Commercial-quality audio file selector with drag-and-drop support.
"""

import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from localmind.config import get_settings, save_settings


def get_file_size_str(filepath: str) -> str:
    """Get human-readable file size."""
    try:
        size = os.path.getsize(filepath)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    except:
        return ""


class DropZoneWidget(QFrame):
    """Clean drop zone for empty state."""

    file_dropped = Signal(str)
    browse_clicked = Signal()

    AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm", ".aac", ".wma", ".opus"}

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("dropZoneEmpty")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(280)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Large upload icon
        icon_label = QLabel()
        icon_label.setObjectName("uploadIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("↑")  # Will be styled with CSS
        layout.addWidget(icon_label)

        # Main text
        title = QLabel(self.tr("Drop your audio file here"))
        title.setObjectName("dropTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(self.tr("or click anywhere to browse"))
        subtitle.setObjectName("dropSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Supported formats
        formats = QLabel(self.tr("MP3, WAV, M4A, FLAC, OGG, WebM"))
        formats.setObjectName("dropFormats")
        formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(formats)

    def mousePressEvent(self, event) -> None:
        self.browse_clicked.emit()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = Path(url.toLocalFile())
                    if path.suffix.lower() in self.AUDIO_EXTENSIONS:
                        event.acceptProposedAction()
                        self.setProperty("dragOver", True)
                        self.style().unpolish(self)
                        self.style().polish(self)
                        return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)

        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.suffix.lower() in self.AUDIO_EXTENSIONS:
                    self.file_dropped.emit(str(path))
                    return


class FileCardWidget(QFrame):
    """Selected file display card."""

    process_clicked = Signal()
    change_file_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._filepath: str | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("fileCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # File info section
        file_section = QFrame()
        file_section.setObjectName("fileInfoSection")
        file_layout = QHBoxLayout(file_section)
        file_layout.setContentsMargins(16, 16, 16, 16)
        file_layout.setSpacing(16)

        # Audio icon
        icon_frame = QFrame()
        icon_frame.setObjectName("audioIconFrame")
        icon_frame.setFixedSize(64, 64)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("♪")
        icon_label.setObjectName("audioIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        file_layout.addWidget(icon_frame)

        # File details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)

        self._filename_label = QLabel(self.tr("No file selected"))
        self._filename_label.setObjectName("fileName")
        self._filename_label.setWordWrap(True)
        details_layout.addWidget(self._filename_label)

        self._file_info_label = QLabel("")
        self._file_info_label.setObjectName("fileInfo")
        details_layout.addWidget(self._file_info_label)

        file_layout.addLayout(details_layout, stretch=1)

        # Change file button
        change_btn = QPushButton(self.tr("Change"))
        change_btn.setObjectName("changeFileBtn")
        change_btn.setFixedWidth(80)
        change_btn.clicked.connect(self.change_file_clicked.emit)
        file_layout.addWidget(change_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addWidget(file_section)

        # Process button - prominent and centered
        self._process_btn = QPushButton(self.tr("Start Processing"))
        self._process_btn.setObjectName("primaryProcessBtn")
        self._process_btn.setMinimumHeight(48)
        self._process_btn.clicked.connect(self.process_clicked.emit)
        layout.addWidget(self._process_btn)

        # Hint text
        hint = QLabel(self.tr("Press Enter or click to start transcription"))
        hint.setObjectName("processHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

    def set_file(self, filepath: str) -> None:
        """Set the displayed file."""
        self._filepath = filepath
        path = Path(filepath)

        self._filename_label.setText(path.name)

        # Build info string
        info_parts = []
        size_str = get_file_size_str(filepath)
        if size_str:
            info_parts.append(size_str)

        ext = path.suffix.upper().replace(".", "")
        if ext:
            info_parts.append(f"{ext} audio")

        info_parts.append(str(path.parent))

        self._file_info_label.setText(" • ".join(info_parts))

    def get_file(self) -> str | None:
        return self._filepath


class FileBrowserPanel(QWidget):
    """Commercial-quality file browser with state management."""

    file_selected = Signal(str)
    file_double_clicked = Signal(str)
    process_clicked = Signal()

    AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm", ".aac", ".wma", ".opus"}

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_file: str | None = None
        self._recent_files: list[str] = []
        self._setup_ui()
        self._load_recent_files()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header = QLabel(self.tr("Audio File"))
        header.setObjectName("panelHeader")
        layout.addWidget(header)

        # Stacked widget for state management
        self._stack = QStackedWidget()

        # State 0: Empty - Drop zone
        self._drop_zone = DropZoneWidget()
        self._drop_zone.file_dropped.connect(self._on_file_selected)
        self._drop_zone.browse_clicked.connect(self._open_file_dialog)
        self._stack.addWidget(self._drop_zone)

        # State 1: File selected - File card
        self._file_card = FileCardWidget()
        self._file_card.process_clicked.connect(self._on_process)
        self._file_card.change_file_clicked.connect(self._open_file_dialog)
        self._stack.addWidget(self._file_card)

        layout.addWidget(self._stack, stretch=1)

        # Recent files section (compact)
        self._recent_section = QFrame()
        self._recent_section.setObjectName("recentSection")
        recent_layout = QVBoxLayout(self._recent_section)
        recent_layout.setContentsMargins(0, 8, 0, 0)
        recent_layout.setSpacing(8)

        recent_header = QLabel(self.tr("Recent"))
        recent_header.setObjectName("recentHeader")
        recent_layout.addWidget(recent_header)

        self._recent_buttons_layout = QHBoxLayout()
        self._recent_buttons_layout.setSpacing(8)
        recent_layout.addLayout(self._recent_buttons_layout)

        self._recent_section.setVisible(False)
        layout.addWidget(self._recent_section)

    def _open_file_dialog(self) -> None:
        """Open file selection dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Audio File"),
            str(Path.home()),
            self.tr("Audio Files")
            + " (*.wav *.mp3 *.m4a *.ogg *.flac *.webm *.aac);;"
            + self.tr("All Files")
            + " (*.*)",
        )
        if filepath:
            self._on_file_selected(filepath)

    @Slot(str)
    def _on_file_selected(self, filepath: str) -> None:
        """Handle file selection."""
        self._current_file = filepath
        self._file_card.set_file(filepath)
        self._stack.setCurrentIndex(1)  # Show file card
        self._add_to_recent(filepath)
        self.file_selected.emit(filepath)

    @Slot()
    def _on_process(self) -> None:
        """Handle process button click."""
        if self._current_file:
            self.file_double_clicked.emit(self._current_file)
            self.process_clicked.emit()

    def _add_to_recent(self, filepath: str) -> None:
        """Add file to recent list."""
        if filepath in self._recent_files:
            self._recent_files.remove(filepath)
        self._recent_files.insert(0, filepath)
        self._recent_files = self._recent_files[:5]
        self._update_recent_ui()
        self._save_recent_files()

    def _update_recent_ui(self) -> None:
        """Update recent files buttons."""
        # Clear existing buttons
        while self._recent_buttons_layout.count():
            child = self._recent_buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add recent file buttons (show max 3)
        shown = 0
        for filepath in self._recent_files:
            if Path(filepath).exists() and filepath != self._current_file:
                btn = QPushButton(Path(filepath).name)
                btn.setObjectName("recentFileBtn")
                btn.setToolTip(filepath)
                btn.setMaximumWidth(120)
                btn.clicked.connect(lambda checked, f=filepath: self._on_file_selected(f))
                self._recent_buttons_layout.addWidget(btn)
                shown += 1
                if shown >= 3:
                    break

        self._recent_buttons_layout.addStretch()
        self._recent_section.setVisible(shown > 0)

    def _load_recent_files(self) -> None:
        """Load recent files from settings."""
        try:
            settings = get_settings()
            self._recent_files = list(settings.app.recent_files)[:5]
            self._update_recent_ui()
        except:
            pass

    def _save_recent_files(self) -> None:
        """Save recent files to settings."""
        try:
            settings = get_settings()
            settings.app.recent_files = self._recent_files[:5]
            save_settings(settings)
        except:
            pass

    def select_file(self, filepath: str) -> None:
        """Programmatically select a file."""
        self._on_file_selected(filepath)

    def get_selected_file(self) -> str | None:
        """Get currently selected file."""
        return self._current_file

    def reset(self) -> None:
        """Reset to empty state."""
        self._current_file = None
        self._stack.setCurrentIndex(0)
        self._update_recent_ui()
