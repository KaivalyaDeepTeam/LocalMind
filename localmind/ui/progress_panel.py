"""
LocalMind Progress Panel

Displays processing progress for transcription, merge, and audit stages.
"""

from typing import Optional
from enum import Enum, auto

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer


class ProcessingStage(Enum):
    """Processing stages."""
    IDLE = auto()
    TRANSCRIBING = auto()
    MERGING = auto()
    AUDITING = auto()
    GENERATING_REPORT = auto()
    COMPLETE = auto()
    ERROR = auto()


class StageProgressWidget(QFrame):
    """Widget showing progress for a single stage."""

    def __init__(self, name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._name = name
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # Stage name and status
        header = QHBoxLayout()
        self._name_label = QLabel(self._name)
        self._name_label.setStyleSheet("font-weight: bold;")
        header.addWidget(self._name_label)

        self._status_label = QLabel("Waiting")
        self._status_label.setStyleSheet("color: gray;")
        header.addWidget(self._status_label)
        header.addStretch()

        layout.addLayout(header)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.setFixedHeight(16)
        layout.addWidget(self._progress)

    def set_waiting(self) -> None:
        """Set stage to waiting state."""
        self._status_label.setText("Waiting")
        self._status_label.setStyleSheet("color: gray;")
        self._progress.setValue(0)

    def set_active(self) -> None:
        """Set stage to active state."""
        self._status_label.setText("Processing...")
        self._status_label.setStyleSheet("color: #2196F3;")

    def set_progress(self, value: int) -> None:
        """Set progress value (0-100)."""
        self._progress.setValue(value)

    def set_complete(self) -> None:
        """Set stage to complete state."""
        self._status_label.setText("Complete")
        self._status_label.setStyleSheet("color: #4CAF50;")
        self._progress.setValue(100)

    def set_error(self, message: str = "Error") -> None:
        """Set stage to error state."""
        self._status_label.setText(message)
        self._status_label.setStyleSheet("color: #F44336;")

    def reset(self) -> None:
        """Reset the stage."""
        self.set_waiting()


class ProgressPanel(QWidget):
    """Panel showing overall processing progress."""

    stage_changed = Signal(ProcessingStage)
    processing_complete = Signal()
    processing_error = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_stage = ProcessingStage.IDLE
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        # Header
        self._header = QLabel("Processing Pipeline")
        self._header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._header)

        # Stage widgets
        self._transcribe_stage = StageProgressWidget("1. Transcription")
        layout.addWidget(self._transcribe_stage)

        self._merge_stage = StageProgressWidget("2. Merge Channels")
        layout.addWidget(self._merge_stage)

        self._audit_stage = StageProgressWidget("3. Quality Audit")
        layout.addWidget(self._audit_stage)

        self._report_stage = StageProgressWidget("4. Generate Report")
        layout.addWidget(self._report_stage)

        # Overall status
        self._overall_status = QLabel("Ready")
        self._overall_status.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self._overall_status)

    def start_full_process(self) -> None:
        """Start the full processing pipeline."""
        self.reset()
        self._set_stage(ProcessingStage.TRANSCRIBING)
        self._transcribe_stage.set_active()
        self._overall_status.setText("Processing audio file...")
        self._overall_status.setStyleSheet("color: #2196F3;")

    def start_transcription(self) -> None:
        """Start transcription stage."""
        self._set_stage(ProcessingStage.TRANSCRIBING)
        self._transcribe_stage.set_active()

    def update_transcription_progress(self, progress: int) -> None:
        """Update transcription progress."""
        self._transcribe_stage.set_progress(progress)

    def complete_transcription(self) -> None:
        """Mark transcription as complete."""
        self._transcribe_stage.set_complete()
        self._set_stage(ProcessingStage.MERGING)
        self._merge_stage.set_active()

    def update_merge_progress(self, progress: int) -> None:
        """Update merge progress."""
        self._merge_stage.set_progress(progress)

    def complete_merge(self) -> None:
        """Mark merge as complete."""
        self._merge_stage.set_complete()
        self._set_stage(ProcessingStage.AUDITING)
        self._audit_stage.set_active()

    def update_audit_progress(self, progress: int) -> None:
        """Update audit progress."""
        self._audit_stage.set_progress(progress)

    def complete_audit(self) -> None:
        """Mark audit as complete."""
        self._audit_stage.set_complete()
        self._set_stage(ProcessingStage.GENERATING_REPORT)
        self._report_stage.set_active()

    def update_report_progress(self, progress: int) -> None:
        """Update report progress."""
        self._report_stage.set_progress(progress)

    def complete_all(self) -> None:
        """Mark all stages as complete."""
        self._report_stage.set_complete()
        self._set_stage(ProcessingStage.COMPLETE)
        self._overall_status.setText("Processing complete!")
        self._overall_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.processing_complete.emit()

    def set_error(self, stage: ProcessingStage, message: str) -> None:
        """Set error state for a stage."""
        self._set_stage(ProcessingStage.ERROR)
        stage_widget = {
            ProcessingStage.TRANSCRIBING: self._transcribe_stage,
            ProcessingStage.MERGING: self._merge_stage,
            ProcessingStage.AUDITING: self._audit_stage,
            ProcessingStage.GENERATING_REPORT: self._report_stage,
        }.get(stage)

        if stage_widget:
            stage_widget.set_error(message)

        self._overall_status.setText(f"Error: {message}")
        self._overall_status.setStyleSheet("color: #F44336;")
        self.processing_error.emit(message)

    def stop(self) -> None:
        """Stop processing."""
        self._set_stage(ProcessingStage.IDLE)
        self._overall_status.setText("Stopped")
        self._overall_status.setStyleSheet("color: #FF9800;")

    def reset(self) -> None:
        """Reset all stages."""
        self._transcribe_stage.reset()
        self._merge_stage.reset()
        self._audit_stage.reset()
        self._report_stage.reset()
        self._set_stage(ProcessingStage.IDLE)
        self._overall_status.setText("Ready")
        self._overall_status.setStyleSheet("color: gray; font-style: italic;")

    def _set_stage(self, stage: ProcessingStage) -> None:
        """Set the current stage."""
        self._current_stage = stage
        self.stage_changed.emit(stage)

    @property
    def current_stage(self) -> ProcessingStage:
        """Get the current processing stage."""
        return self._current_stage
