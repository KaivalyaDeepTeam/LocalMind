"""
LocalMind File Browser Panel

VLC-like file browser for selecting audio files.
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QFileSystemModel,
    QLineEdit, QPushButton, QLabel, QComboBox, QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot, QDir, QModelIndex


class FileBrowserPanel(QWidget):
    """VLC-like file browser panel."""

    file_selected = Signal(str)
    file_double_clicked = Signal(str)

    # Supported audio formats
    AUDIO_EXTENSIONS = [
        "*.wav", "*.mp3", "*.m4a", "*.ogg", "*.flac", "*.webm",
        "*.aac", "*.wma", "*.opus",
    ]

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_path: Optional[Path] = None
        self._setup_ui()
        self._connect_signals()
        self._load_initial_directory()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel("Audio Files")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Path bar
        path_layout = QHBoxLayout()
        path_layout.setSpacing(4)

        self._path_combo = QComboBox()
        self._path_combo.setEditable(True)
        self._path_combo.setSizePolicy(
            self._path_combo.sizePolicy().horizontalPolicy(),
            self._path_combo.sizePolicy().verticalPolicy()
        )
        path_layout.addWidget(self._path_combo, stretch=1)

        self._up_button = QPushButton("↑")
        self._up_button.setFixedWidth(30)
        self._up_button.setToolTip("Go to parent directory")
        path_layout.addWidget(self._up_button)

        self._home_button = QPushButton("⌂")
        self._home_button.setFixedWidth(30)
        self._home_button.setToolTip("Go to home directory")
        path_layout.addWidget(self._home_button)

        layout.addLayout(path_layout)

        # File tree
        self._file_model = QFileSystemModel()
        self._file_model.setNameFilters(self.AUDIO_EXTENSIONS)
        self._file_model.setNameFilterDisables(False)

        self._tree_view = QTreeView()
        self._tree_view.setModel(self._file_model)
        self._tree_view.setRootIndex(self._file_model.index(str(Path.home())))
        self._tree_view.setColumnWidth(0, 250)
        self._tree_view.hideColumn(1)  # Size
        self._tree_view.hideColumn(2)  # Type
        self._tree_view.setHeaderHidden(False)
        self._tree_view.setSortingEnabled(True)
        self._tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        layout.addWidget(self._tree_view, stretch=1)

        # Info bar
        self._info_label = QLabel("Select an audio file")
        self._info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self._info_label)

    def _connect_signals(self) -> None:
        """Connect signals."""
        self._tree_view.clicked.connect(self._on_item_clicked)
        self._tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self._up_button.clicked.connect(self._go_up)
        self._home_button.clicked.connect(self._go_home)
        self._path_combo.lineEdit().returnPressed.connect(self._on_path_entered)

    def _load_initial_directory(self) -> None:
        """Load the initial directory."""
        home = str(Path.home())
        self._file_model.setRootPath(home)
        self._tree_view.setRootIndex(self._file_model.index(home))
        self._path_combo.setCurrentText(home)
        self._current_path = Path(home)

    @Slot(QModelIndex)
    def _on_item_clicked(self, index: QModelIndex) -> None:
        """Handle item click."""
        path = self._file_model.filePath(index)
        if path:
            file_path = Path(path)
            if file_path.is_file():
                self._current_path = file_path
                self._info_label.setText(f"{file_path.name} ({self._format_size(file_path.stat().st_size)})")
                self.file_selected.emit(str(file_path))
            elif file_path.is_dir():
                self._navigate_to(file_path)

    @Slot(QModelIndex)
    def _on_item_double_clicked(self, index: QModelIndex) -> None:
        """Handle item double-click."""
        path = self._file_model.filePath(index)
        if path:
            file_path = Path(path)
            if file_path.is_file():
                self.file_double_clicked.emit(str(file_path))
            elif file_path.is_dir():
                self._navigate_to(file_path)

    @Slot()
    def _go_up(self) -> None:
        """Navigate to parent directory."""
        current = self._tree_view.rootIndex()
        path = Path(self._file_model.filePath(current))
        if path.parent != path:
            self._navigate_to(path.parent)

    @Slot()
    def _go_home(self) -> None:
        """Navigate to home directory."""
        self._navigate_to(Path.home())

    @Slot()
    def _on_path_entered(self) -> None:
        """Handle path entry."""
        path_str = self._path_combo.currentText()
        path = Path(path_str).expanduser()
        if path.exists() and path.is_dir():
            self._navigate_to(path)

    def _navigate_to(self, path: Path) -> None:
        """Navigate to a directory."""
        if path.is_dir():
            self._file_model.setRootPath(str(path))
            self._tree_view.setRootIndex(self._file_model.index(str(path)))
            self._path_combo.setCurrentText(str(path))

    def select_file(self, filepath: str) -> None:
        """Programmatically select a file."""
        path = Path(filepath)
        if path.exists():
            # Navigate to parent directory
            self._navigate_to(path.parent)
            # Select the file
            index = self._file_model.index(str(path))
            self._tree_view.setCurrentIndex(index)
            self._tree_view.scrollTo(index)
            self._current_path = path
            self.file_selected.emit(str(path))

    def get_selected_file(self) -> Optional[str]:
        """Get the currently selected file."""
        if self._current_path and self._current_path.is_file():
            return str(self._current_path)
        return None

    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size for display."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
