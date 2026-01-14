"""
LocalMind File Browser Panel

Modern drag-and-drop file selector with quick access locations.
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QFileDialog,
    QSizePolicy, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, Slot, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont


class DropZone(QFrame):
    """Drag and drop zone for audio files."""

    file_dropped = Signal(str)
    files_dropped = Signal(list)  # For batch processing

    AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm', '.aac', '.wma', '.opus'}

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("dropZone")
        self.setMinimumHeight(180)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel("🎵")
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Main text
        title = QLabel("Drop audio file here")
        title.setObjectName("dropZoneTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("or click to browse")
        subtitle.setObjectName("dropZoneSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Supported formats
        formats = QLabel("MP3, WAV, M4A, FLAC, OGG, WebM")
        formats.setObjectName("dropZoneFormats")
        formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(formats)

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

        # Collect all valid audio files
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.suffix.lower() in self.AUDIO_EXTENSIONS:
                    files.append(str(path))

        # Emit first file (for single file processing)
        if files:
            self.file_dropped.emit(files[0])
            # Also emit all files for batch processing
            if hasattr(self, 'files_dropped'):
                self.files_dropped.emit(files)

    def mousePressEvent(self, event) -> None:
        # Open file dialog on click - supports multiple selection
        filepaths, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files",
            str(Path.home()),
            "Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac *.webm *.aac);;All Files (*.*)"
        )
        if filepaths:
            self.file_dropped.emit(filepaths[0])
            # Emit all files for batch processing
            if len(filepaths) > 1 and hasattr(self, 'files_dropped'):
                self.files_dropped.emit(filepaths)


class QuickAccessItem(QFrame):
    """Quick access location button."""

    clicked = Signal(str)

    def __init__(self, name: str, path: str, icon: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._path = path
        self._setup_ui(name, icon)

    def _setup_ui(self, name: str, icon: str) -> None:
        self.setObjectName("quickAccessItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px; background: transparent;")
        layout.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setObjectName("quickAccessName")
        layout.addWidget(name_label)

        layout.addStretch()

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._path)


class RecentFileItem(QFrame):
    """Recent file item."""

    clicked = Signal(str)
    remove_clicked = Signal(str)

    def __init__(self, filepath: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._filepath = filepath
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("recentFileItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Icon
        icon_label = QLabel("🎵")
        icon_label.setStyleSheet("font-size: 16px; background: transparent;")
        layout.addWidget(icon_label)

        # File info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        path = Path(self._filepath)
        name_label = QLabel(path.name)
        name_label.setObjectName("recentFileName")
        info_layout.addWidget(name_label)

        folder_label = QLabel(str(path.parent.name))
        folder_label.setObjectName("recentFileFolder")
        info_layout.addWidget(folder_label)

        layout.addLayout(info_layout, stretch=1)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._filepath)


class FileBrowserPanel(QWidget):
    """Modern file browser with drag-drop and quick access."""

    file_selected = Signal(str)
    file_double_clicked = Signal(str)
    process_clicked = Signal()
    batch_process_clicked = Signal(list)  # For batch processing

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._recent_files: List[str] = []
        self._current_file: Optional[str] = None
        self._batch_queue: List[str] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Drop zone
        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._on_file_dropped)
        layout.addWidget(self._drop_zone)

        # Selected file display
        self._selected_container = QFrame()
        self._selected_container.setObjectName("selectedFileContainer")
        self._selected_container.setVisible(False)
        selected_layout = QVBoxLayout(self._selected_container)
        selected_layout.setContentsMargins(12, 12, 12, 12)
        selected_layout.setSpacing(8)

        file_row = QHBoxLayout()
        file_icon = QLabel("🎵")
        file_icon.setStyleSheet("font-size: 18px; background: transparent;")
        file_row.addWidget(file_icon)

        self._selected_file_label = QLabel("")
        self._selected_file_label.setObjectName("selectedFileName")
        self._selected_file_label.setWordWrap(True)
        file_row.addWidget(self._selected_file_label, stretch=1)
        selected_layout.addLayout(file_row)

        # Process buttons row
        btn_row = QHBoxLayout()

        self._process_btn = QPushButton("Process")
        self._process_btn.setObjectName("processButton")
        self._process_btn.clicked.connect(self._on_process_clicked)
        btn_row.addWidget(self._process_btn)

        self._add_to_queue_btn = QPushButton("Add to Queue")
        self._add_to_queue_btn.setObjectName("queueButton")
        self._add_to_queue_btn.clicked.connect(self._on_add_to_queue)
        btn_row.addWidget(self._add_to_queue_btn)

        selected_layout.addLayout(btn_row)

        layout.addWidget(self._selected_container)

        # Batch Queue section
        self._queue_header = QLabel("Batch Queue")
        self._queue_header.setObjectName("sectionHeader")
        self._queue_header.setVisible(False)
        layout.addWidget(self._queue_header)

        self._queue_container = QFrame()
        self._queue_container.setObjectName("batchQueueContainer")
        self._queue_container.setVisible(False)
        queue_layout = QVBoxLayout(self._queue_container)
        queue_layout.setContentsMargins(12, 12, 12, 12)
        queue_layout.setSpacing(8)

        self._queue_list = QListWidget()
        self._queue_list.setObjectName("batchQueueList")
        self._queue_list.setMaximumHeight(120)
        queue_layout.addWidget(self._queue_list)

        queue_btn_row = QHBoxLayout()
        self._process_queue_btn = QPushButton("Process All")
        self._process_queue_btn.setObjectName("processButton")
        self._process_queue_btn.clicked.connect(self._on_process_queue)
        queue_btn_row.addWidget(self._process_queue_btn)

        self._clear_queue_btn = QPushButton("Clear")
        self._clear_queue_btn.clicked.connect(self._on_clear_queue)
        queue_btn_row.addWidget(self._clear_queue_btn)

        queue_layout.addLayout(queue_btn_row)
        layout.addWidget(self._queue_container)

        # Quick Access section
        quick_access_header = QLabel("Quick Access")
        quick_access_header.setObjectName("sectionHeader")
        layout.addWidget(quick_access_header)

        # Quick access locations
        home = str(Path.home())
        locations = [
            ("Desktop", str(Path.home() / "Desktop"), "🖥️"),
            ("Documents", str(Path.home() / "Documents"), "📁"),
            ("Downloads", str(Path.home() / "Downloads"), "⬇️"),
            ("Music", str(Path.home() / "Music"), "🎵"),
        ]

        for name, path, icon in locations:
            if Path(path).exists():
                item = QuickAccessItem(name, path, icon)
                item.clicked.connect(self._on_quick_access_clicked)
                layout.addWidget(item)

        # Recent Files section
        self._recent_header = QLabel("Recent Files")
        self._recent_header.setObjectName("sectionHeader")
        self._recent_header.setVisible(False)
        layout.addWidget(self._recent_header)

        self._recent_container = QWidget()
        self._recent_layout = QVBoxLayout(self._recent_container)
        self._recent_layout.setContentsMargins(0, 0, 0, 0)
        self._recent_layout.setSpacing(4)
        self._recent_container.setVisible(False)
        layout.addWidget(self._recent_container)

        layout.addStretch()

    @Slot(str)
    def _on_file_dropped(self, filepath: str) -> None:
        self._set_selected_file(filepath)
        self._add_to_recent(filepath)
        self.file_selected.emit(filepath)
        # Auto-start processing on drop
        self.file_double_clicked.emit(filepath)

    @Slot(str)
    def _on_quick_access_clicked(self, path: str) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", path,
            "Audio Files (*.wav *.mp3 *.m4a *.ogg *.flac *.webm *.aac);;All Files (*.*)"
        )
        if filepath:
            self._set_selected_file(filepath)
            self._add_to_recent(filepath)
            self.file_selected.emit(filepath)

    @Slot(str)
    def _on_recent_clicked(self, filepath: str) -> None:
        if Path(filepath).exists():
            self._set_selected_file(filepath)
            self.file_selected.emit(filepath)
        else:
            self._remove_from_recent(filepath)

    @Slot()
    def _on_process_clicked(self) -> None:
        if self._current_file:
            self.file_double_clicked.emit(self._current_file)
            self.process_clicked.emit()

    @Slot()
    def _on_add_to_queue(self) -> None:
        """Add current file to batch queue."""
        if self._current_file and self._current_file not in self._batch_queue:
            self._batch_queue.append(self._current_file)
            self._update_queue_ui()

    @Slot()
    def _on_process_queue(self) -> None:
        """Process all files in the queue."""
        if self._batch_queue:
            self.batch_process_clicked.emit(self._batch_queue.copy())

    @Slot()
    def _on_clear_queue(self) -> None:
        """Clear the batch queue."""
        self._batch_queue.clear()
        self._update_queue_ui()

    def _update_queue_ui(self) -> None:
        """Update the batch queue display."""
        self._queue_list.clear()
        for filepath in self._batch_queue:
            filename = Path(filepath).name
            self._queue_list.addItem(f"🎵 {filename}")

        has_queue = len(self._batch_queue) > 0
        self._queue_header.setVisible(has_queue)
        self._queue_container.setVisible(has_queue)

    def add_files_to_queue(self, filepaths: List[str]) -> None:
        """Add multiple files to the batch queue."""
        for filepath in filepaths:
            if filepath not in self._batch_queue:
                self._batch_queue.append(filepath)
        self._update_queue_ui()

    def get_queue(self) -> List[str]:
        """Get the current batch queue."""
        return self._batch_queue.copy()

    def clear_queue(self) -> None:
        """Clear the batch queue."""
        self._batch_queue.clear()
        self._update_queue_ui()

    def remove_from_queue(self, filepath: str) -> None:
        """Remove a file from the queue."""
        if filepath in self._batch_queue:
            self._batch_queue.remove(filepath)
            self._update_queue_ui()

    def _set_selected_file(self, filepath: str) -> None:
        """Update the selected file display."""
        self._current_file = filepath
        filename = Path(filepath).name
        self._selected_file_label.setText(filename)
        self._selected_container.setVisible(True)

    def _add_to_recent(self, filepath: str) -> None:
        if filepath in self._recent_files:
            self._recent_files.remove(filepath)
        self._recent_files.insert(0, filepath)
        self._recent_files = self._recent_files[:5]  # Keep only 5 recent
        self._update_recent_ui()

    def _remove_from_recent(self, filepath: str) -> None:
        if filepath in self._recent_files:
            self._recent_files.remove(filepath)
            self._update_recent_ui()

    def _update_recent_ui(self) -> None:
        # Clear existing items
        while self._recent_layout.count():
            child = self._recent_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new items
        for filepath in self._recent_files:
            if Path(filepath).exists():
                item = RecentFileItem(filepath)
                item.clicked.connect(self._on_recent_clicked)
                self._recent_layout.addWidget(item)

        # Show/hide section
        has_recent = len(self._recent_files) > 0
        self._recent_header.setVisible(has_recent)
        self._recent_container.setVisible(has_recent)

    def select_file(self, filepath: str) -> None:
        """Programmatically select a file."""
        self._add_to_recent(filepath)
        self.file_selected.emit(filepath)

    def get_selected_file(self) -> Optional[str]:
        """Get the currently selected file."""
        return self._current_file
