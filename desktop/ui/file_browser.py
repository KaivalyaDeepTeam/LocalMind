"""
VLC-like File Browser Panel

A file browser component for selecting audio files, similar to VLC's interface.
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeView,
    QFileSystemModel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QFrame,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, Slot, QDir, QModelIndex
from PySide6.QtGui import QIcon


# Supported audio formats
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm", ".aac", ".wma"}


class FileBrowserPanel(QWidget):
    """VLC-like file browser panel."""

    # Signals
    file_selected = Signal(str)  # Emitted when a file is selected
    file_double_clicked = Signal(str)  # Emitted when a file is double-clicked
    directory_changed = Signal(str)  # Emitted when directory changes

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_directory = Path.home()
        self._selected_file: Optional[Path] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the file browser UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header with title
        header = QLabel("Audio Files")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Path bar
        path_layout = QHBoxLayout()

        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Enter path or drag files here...")
        self._path_edit.setText(str(self._current_directory))
        path_layout.addWidget(self._path_edit)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._on_browse_clicked)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        # Quick access locations
        locations_layout = QHBoxLayout()

        home_btn = QPushButton("Home")
        home_btn.clicked.connect(lambda: self.set_directory(str(Path.home())))
        locations_layout.addWidget(home_btn)

        desktop_btn = QPushButton("Desktop")
        desktop_btn.clicked.connect(
            lambda: self.set_directory(str(Path.home() / "Desktop"))
        )
        locations_layout.addWidget(desktop_btn)

        downloads_btn = QPushButton("Downloads")
        downloads_btn.clicked.connect(
            lambda: self.set_directory(str(Path.home() / "Downloads"))
        )
        locations_layout.addWidget(downloads_btn)

        locations_layout.addStretch()

        layout.addLayout(locations_layout)

        # Splitter for tree and file list
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Directory tree
        self._tree_frame = QFrame()
        self._tree_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        tree_layout = QVBoxLayout(self._tree_frame)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        self._dir_model = QFileSystemModel()
        self._dir_model.setRootPath("")
        self._dir_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)

        self._tree_view = QTreeView()
        self._tree_view.setModel(self._dir_model)
        self._tree_view.setRootIndex(self._dir_model.index(""))
        self._tree_view.setHeaderHidden(True)
        # Hide columns except name
        for i in range(1, self._dir_model.columnCount()):
            self._tree_view.hideColumn(i)
        self._tree_view.setAnimated(True)

        tree_layout.addWidget(self._tree_view)
        splitter.addWidget(self._tree_frame)

        # Audio file list
        self._file_frame = QFrame()
        self._file_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        file_layout = QVBoxLayout(self._file_frame)
        file_layout.setContentsMargins(0, 0, 0, 0)

        file_header = QLabel("Audio Files in Directory")
        file_header.setStyleSheet("padding: 4px;")
        file_layout.addWidget(file_header)

        self._file_list = QListWidget()
        self._file_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._file_list.setAlternatingRowColors(True)
        file_layout.addWidget(self._file_list)

        splitter.addWidget(self._file_frame)

        # Set initial splitter sizes
        splitter.setSizes([200, 300])

        layout.addWidget(splitter, stretch=1)

        # File info panel
        self._info_frame = QFrame()
        self._info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(self._info_frame)
        info_layout.setContentsMargins(8, 8, 8, 8)

        self._file_info_label = QLabel("No file selected")
        self._file_info_label.setWordWrap(True)
        info_layout.addWidget(self._file_info_label)

        layout.addWidget(self._info_frame)

        # Load initial directory
        self._load_directory(self._current_directory)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self._path_edit.returnPressed.connect(self._on_path_entered)
        self._tree_view.clicked.connect(self._on_tree_clicked)
        self._file_list.itemClicked.connect(self._on_file_clicked)
        self._file_list.itemDoubleClicked.connect(self._on_file_double_clicked)

    def _load_directory(self, directory: Path) -> None:
        """Load audio files from the specified directory."""
        self._file_list.clear()

        if not directory.exists():
            return

        # Find audio files
        audio_files = []
        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix.lower() in AUDIO_EXTENSIONS:
                    audio_files.append(item)
        except PermissionError:
            pass

        # Sort by name
        audio_files.sort(key=lambda x: x.name.lower())

        # Add to list
        for audio_file in audio_files:
            item = QListWidgetItem(audio_file.name)
            item.setData(Qt.ItemDataRole.UserRole, str(audio_file))

            # Format file size
            size = audio_file.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"

            item.setToolTip(f"{audio_file.name}\nSize: {size_str}")
            self._file_list.addItem(item)

        # Update header
        count = len(audio_files)
        if count == 0:
            self._file_frame.findChild(QLabel).setText("No audio files found")
        else:
            self._file_frame.findChild(QLabel).setText(
                f"Audio Files ({count} file{'s' if count != 1 else ''})"
            )

    def _update_file_info(self, filepath: Path) -> None:
        """Update the file info panel."""
        if not filepath.exists():
            self._file_info_label.setText("File not found")
            return

        stat = filepath.stat()

        # Format size
        size = stat.st_size
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{size / (1024 * 1024 * 1024):.2f} GB"

        # Format modification time
        from datetime import datetime
        mtime = datetime.fromtimestamp(stat.st_mtime)
        time_str = mtime.strftime("%Y-%m-%d %H:%M")

        info_text = (
            f"<b>{filepath.name}</b><br>"
            f"Size: {size_str}<br>"
            f"Modified: {time_str}<br>"
            f"Format: {filepath.suffix.upper()[1:]}"
        )
        self._file_info_label.setText(info_text)

    # Public methods
    def set_directory(self, directory: str) -> None:
        """Set the current directory."""
        path = Path(directory)
        if path.exists() and path.is_dir():
            self._current_directory = path
            self._path_edit.setText(str(path))
            self._load_directory(path)

            # Expand tree to show directory
            index = self._dir_model.index(str(path))
            self._tree_view.setCurrentIndex(index)
            self._tree_view.scrollTo(index)

            self.directory_changed.emit(str(path))

    def select_file(self, filepath: str) -> None:
        """Select a specific file."""
        path = Path(filepath)
        if path.exists():
            # Set directory if different
            if path.parent != self._current_directory:
                self.set_directory(str(path.parent))

            # Find and select in list
            for i in range(self._file_list.count()):
                item = self._file_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == str(path):
                    self._file_list.setCurrentItem(item)
                    self._selected_file = path
                    self._update_file_info(path)
                    break

    def get_selected_file(self) -> Optional[str]:
        """Get the currently selected file path."""
        if self._selected_file:
            return str(self._selected_file)
        return None

    # Slot handlers
    @Slot()
    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        from PySide6.QtWidgets import QFileDialog

        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", str(self._current_directory)
        )
        if directory:
            self.set_directory(directory)

    @Slot()
    def _on_path_entered(self) -> None:
        """Handle path entered in text field."""
        path = self._path_edit.text().strip()
        if path:
            self.set_directory(path)

    @Slot(QModelIndex)
    def _on_tree_clicked(self, index: QModelIndex) -> None:
        """Handle directory tree click."""
        path = self._dir_model.filePath(index)
        if path:
            self.set_directory(path)

    @Slot(QListWidgetItem)
    def _on_file_clicked(self, item: QListWidgetItem) -> None:
        """Handle file list click."""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath:
            self._selected_file = Path(filepath)
            self._update_file_info(self._selected_file)
            self.file_selected.emit(filepath)

    @Slot(QListWidgetItem)
    def _on_file_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle file list double-click."""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath:
            self._selected_file = Path(filepath)
            self._update_file_info(self._selected_file)
            self.file_double_clicked.emit(filepath)
