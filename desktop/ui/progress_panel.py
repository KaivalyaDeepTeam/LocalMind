"""
Progress Panel

Displays processing progress for transcription, merging, and auditing.
"""

from typing import Optional
from enum import Enum

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QLabel,
    QFrame,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal, Slot


class ProcessingStage(Enum):
    """Processing stages."""
    IDLE = "idle"
    LOADING_MODELS = "loading_models"
    PREPROCESSING = "preprocessing"
    DIARIZATION = "diarization"
    TRANSCRIPTION = "transcription"
    MERGING = "merging"
    AUDITING = "auditing"
    GENERATING_REPORT = "generating_report"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


STAGE_LABELS = {
    ProcessingStage.IDLE: "Ready",
    ProcessingStage.LOADING_MODELS: "Loading AI models...",
    ProcessingStage.PREPROCESSING: "Preprocessing audio...",
    ProcessingStage.DIARIZATION: "Identifying speakers...",
    ProcessingStage.TRANSCRIPTION: "Transcribing audio...",
    ProcessingStage.MERGING: "Merging transcripts...",
    ProcessingStage.AUDITING: "Auditing call quality...",
    ProcessingStage.GENERATING_REPORT: "Generating report...",
    ProcessingStage.COMPLETE: "Complete",
    ProcessingStage.ERROR: "Error occurred",
    ProcessingStage.CANCELLED: "Cancelled",
}


class ProgressPanel(QWidget):
    """Panel showing processing progress."""

    # Signals
    cancel_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._stage = ProcessingStage.IDLE
        self._is_processing = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the progress panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(8)

        # Main frame
        self._frame = QFrame()
        self._frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(self._frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)

        # Stage label
        self._stage_label = QLabel("Ready")
        self._stage_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        frame_layout.addWidget(self._stage_label)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        frame_layout.addWidget(self._progress_bar)

        # Detail label
        self._detail_label = QLabel("")
        self._detail_label.setStyleSheet("color: #666; font-size: 11px;")
        self._detail_label.setWordWrap(True)
        frame_layout.addWidget(self._detail_label)

        # Time estimate
        self._time_label = QLabel("")
        self._time_label.setStyleSheet("color: #888; font-size: 11px;")
        frame_layout.addWidget(self._time_label)

        # Cancel button (hidden by default)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self._on_cancel_clicked)
        self._cancel_button.setVisible(False)
        button_layout.addWidget(self._cancel_button)

        frame_layout.addLayout(button_layout)

        layout.addWidget(self._frame)

        # Initially hide the panel
        self._frame.setVisible(False)

    def _update_display(self) -> None:
        """Update the display based on current state."""
        self._stage_label.setText(STAGE_LABELS.get(self._stage, "Unknown"))

        if self._stage == ProcessingStage.IDLE:
            self._frame.setVisible(False)
        else:
            self._frame.setVisible(True)

        # Show cancel button only when processing
        self._cancel_button.setVisible(self._is_processing)

        # Set progress bar style based on stage
        if self._stage == ProcessingStage.ERROR:
            self._progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #e74c3c; }"
            )
        elif self._stage == ProcessingStage.COMPLETE:
            self._progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #27ae60; }"
            )
        elif self._stage == ProcessingStage.CANCELLED:
            self._progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #f39c12; }"
            )
        else:
            self._progress_bar.setStyleSheet("")  # Default style

    # Public methods
    def start_transcription(self) -> None:
        """Start transcription-only progress."""
        self._is_processing = True
        self._stage = ProcessingStage.LOADING_MODELS
        self._progress_bar.setValue(0)
        self._detail_label.setText("Preparing transcription models...")
        self._time_label.setText("")
        self._update_display()

    def start_full_process(self) -> None:
        """Start full processing progress."""
        self._is_processing = True
        self._stage = ProcessingStage.LOADING_MODELS
        self._progress_bar.setValue(0)
        self._detail_label.setText("Preparing AI models...")
        self._time_label.setText("Estimated time: 2-5 minutes depending on audio length")
        self._update_display()

    def stop(self) -> None:
        """Stop and reset progress."""
        self._is_processing = False
        if self._stage not in (ProcessingStage.COMPLETE, ProcessingStage.ERROR):
            self._stage = ProcessingStage.CANCELLED
        self._update_display()

    def reset(self) -> None:
        """Reset to idle state."""
        self._is_processing = False
        self._stage = ProcessingStage.IDLE
        self._progress_bar.setValue(0)
        self._detail_label.setText("")
        self._time_label.setText("")
        self._update_display()

    def set_stage(self, stage: ProcessingStage) -> None:
        """Set the current processing stage."""
        self._stage = stage
        self._update_display()

    def set_progress(self, value: int) -> None:
        """Set progress value (0-100)."""
        self._progress_bar.setValue(max(0, min(100, value)))

    def set_detail(self, text: str) -> None:
        """Set detail text."""
        self._detail_label.setText(text)

    def set_time_estimate(self, text: str) -> None:
        """Set time estimate text."""
        self._time_label.setText(text)

    def complete(self, success: bool = True) -> None:
        """Mark processing as complete."""
        self._is_processing = False
        if success:
            self._stage = ProcessingStage.COMPLETE
            self._progress_bar.setValue(100)
            self._detail_label.setText("Processing completed successfully")
        else:
            self._stage = ProcessingStage.ERROR
        self._time_label.setText("")
        self._update_display()

    def error(self, message: str) -> None:
        """Show error state."""
        self._is_processing = False
        self._stage = ProcessingStage.ERROR
        self._detail_label.setText(f"Error: {message}")
        self._time_label.setText("")
        self._update_display()

    @property
    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self._is_processing

    # Slot handlers
    @Slot()
    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self.cancel_requested.emit()
