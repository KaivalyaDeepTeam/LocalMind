"""
Report Preview Dialog

Preview PDF reports before exporting.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Qt


class ReportPreviewDialog(QDialog):
    """Dialog for previewing PDF reports before export."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowTitle("Report Preview")
        self.setMinimumSize(800, 600)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Preview area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self._preview_widget = QWidget()
        self._preview_layout = QVBoxLayout(self._preview_widget)

        placeholder = QLabel("PDF preview will be shown here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-size: 14px;")
        self._preview_layout.addWidget(placeholder)

        scroll.setWidget(self._preview_widget)
        layout.addWidget(scroll, stretch=1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        export_btn = QPushButton("Export PDF")
        export_btn.clicked.connect(self.accept)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)

    def set_content(self, html_content: str) -> None:
        """Set the preview content from HTML."""
        # TODO: Render HTML preview
        pass
