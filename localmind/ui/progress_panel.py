"""
LocalMind Progress Panel

Displays processing progress for transcription, merge, and audit stages
with smooth animations, ETA tracking, and expandable details.
"""

import time
from enum import Enum, auto

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ProcessingStage(Enum):
    """Processing stages."""

    IDLE = auto()
    TRANSCRIBING = auto()
    MERGING = auto()
    AUDITING = auto()
    GENERATING_REPORT = auto()
    COMPLETE = auto()
    ERROR = auto()


class AnimatedProgressBar(QProgressBar):
    """
    Progress bar with smooth value transitions.

    Features:
    - Animated value changes (300ms ease-out)
    - Indeterminate mode with animated striped pattern
    - Status property for theming (success, error, active)
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._animated_value = 0
        self._target_value = 0
        self._animation = QPropertyAnimation(self, b"animatedValue")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setRange(0, 100)
        self.setTextVisible(True)
        self.setFixedHeight(8)

    def get_animated_value(self) -> int:
        return self._animated_value

    def set_animated_value(self, value: int) -> None:
        self._animated_value = value
        super().setValue(value)

    animatedValue = Property(int, get_animated_value, set_animated_value)

    def setValue(self, value: int) -> None:
        """Animate to the new value."""
        if value == self._target_value:
            return

        self._target_value = value
        self._animation.stop()
        self._animation.setStartValue(self._animated_value)
        self._animation.setEndValue(value)
        self._animation.start()

    def setValueInstant(self, value: int) -> None:
        """Set value without animation."""
        self._target_value = value
        self._animated_value = value
        super().setValue(value)

    def setStatus(self, status: str) -> None:
        """Set status property for theming."""
        self.setProperty("status", status)
        self.style().unpolish(self)
        self.style().polish(self)


class StageProgressWidget(QFrame):
    """
    Widget showing progress for a single stage with animations.

    Features:
    - Smooth animated progress bar
    - ETA and elapsed time display
    - Pulsing indicator for active state
    - Expandable log panel
    """

    retry_requested = Signal()

    def __init__(self, name: str, number: int, parent: QWidget | None = None):
        super().__init__(parent)
        self._name = name
        self._number = number
        self._start_time: float | None = None
        self._current_progress: int = 0
        self._is_expanded = False
        self._logs: list[str] = []
        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setObjectName("stageWidget")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Header row
        header = QHBoxLayout()
        header.setSpacing(8)

        # Stage number indicator (pulsing circle)
        self._indicator = QLabel(str(self._number))
        self._indicator.setObjectName("stageIndicator")
        self._indicator.setFixedSize(24, 24)
        self._indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._indicator.setFont(QFont("", 11, QFont.Weight.Bold))
        header.addWidget(self._indicator)

        # Stage name
        self._name_label = QLabel(self._name)
        self._name_label.setObjectName("stageName")
        self._name_label.setFont(QFont("", 13, QFont.Weight.Medium))
        header.addWidget(self._name_label)

        header.addStretch()

        # Status label
        self._status_label = QLabel(self.tr("Waiting"))
        self._status_label.setObjectName("stageStatus")
        self._status_label.setProperty("state", "waiting")
        header.addWidget(self._status_label)

        # Time display (with ETA)
        self._time_label = QLabel("")
        self._time_label.setObjectName("stageTime")
        self._time_label.setMinimumWidth(150)  # Wider for ETA
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(self._time_label)

        # Expand button
        self._expand_btn = QPushButton(self.tr("Details"))
        self._expand_btn.setObjectName("expandButton")
        self._expand_btn.setProperty("ghost", "true")
        self._expand_btn.setFixedHeight(24)
        self._expand_btn.clicked.connect(self._toggle_expand)
        self._expand_btn.setVisible(False)
        header.addWidget(self._expand_btn)

        main_layout.addLayout(header)

        # Progress bar
        self._progress = AnimatedProgressBar()
        main_layout.addWidget(self._progress)

        # Expandable log panel
        self._log_panel = QTextEdit()
        self._log_panel.setObjectName("stageLogPanel")
        self._log_panel.setReadOnly(True)
        self._log_panel.setMaximumHeight(100)
        self._log_panel.setVisible(False)
        self._log_panel.setFont(QFont("Menlo", 10))
        main_layout.addWidget(self._log_panel)

        # Retry button (shown on error) - use primary style as retry is a positive action
        self._retry_btn = QPushButton(self.tr("Retry"))
        self._retry_btn.setProperty("primary", "true")
        self._retry_btn.setVisible(False)
        self._retry_btn.clicked.connect(self.retry_requested.emit)
        main_layout.addWidget(self._retry_btn)

        # Timer for updating elapsed time
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time_display)

    def _setup_animations(self) -> None:
        """Set up pulsing animation for active state."""
        # Opacity effect for pulsing
        self._opacity_effect = QGraphicsOpacityEffect(self._indicator)
        self._opacity_effect.setOpacity(1.0)
        self._indicator.setGraphicsEffect(self._opacity_effect)

        # Pulse animation
        self._pulse_animation = QSequentialAnimationGroup(self)

        fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_out.setDuration(500)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.5)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutSine)

        fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_in.setDuration(500)
        fade_in.setStartValue(0.5)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InOutSine)

        self._pulse_animation.addAnimation(fade_out)
        self._pulse_animation.addAnimation(fade_in)
        self._pulse_animation.setLoopCount(-1)  # Infinite

    def _toggle_expand(self) -> None:
        """Toggle the log panel expansion."""
        self._is_expanded = not self._is_expanded
        self._log_panel.setVisible(self._is_expanded)
        self._expand_btn.setText(self.tr("Hide") if self._is_expanded else self.tr("Details"))

    def _update_time_display(self) -> None:
        """Update the elapsed time display with ETA."""
        if self._start_time is None:
            return

        elapsed = time.time() - self._start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        # Format elapsed time
        if minutes > 0:
            elapsed_str = f"{minutes}m {seconds}s"
        else:
            elapsed_str = f"{seconds}s"

        # Calculate ETA if we have progress
        if self._current_progress > 5 and self._current_progress < 100:
            # Estimate remaining time based on current rate
            rate = elapsed / self._current_progress  # seconds per percent
            remaining_pct = 100 - self._current_progress
            eta_seconds = rate * remaining_pct

            eta_min = int(eta_seconds // 60)
            eta_sec = int(eta_seconds % 60)

            if eta_min > 0:
                eta_str = f"~{eta_min}m {eta_sec}s left"
            else:
                eta_str = f"~{eta_sec}s left"

            self._time_label.setText(f"{elapsed_str} ({eta_str})")
        else:
            self._time_label.setText(elapsed_str)

    def add_log(self, message: str) -> None:
        """Add a log message."""
        self._logs.append(message)
        self._log_panel.append(message)
        if len(self._logs) > 0:
            self._expand_btn.setVisible(True)

    def clear_logs(self) -> None:
        """Clear all log messages."""
        self._logs.clear()
        self._log_panel.clear()

    def set_waiting(self) -> None:
        """Set stage to waiting state."""
        self._pulse_animation.stop()
        self._opacity_effect.setOpacity(1.0)
        self._timer.stop()

        self._status_label.setText(self.tr("Waiting"))
        self._status_label.setProperty("state", "waiting")
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

        self._indicator.setProperty("state", "waiting")
        self._indicator.style().unpolish(self._indicator)
        self._indicator.style().polish(self._indicator)

        self._progress.setValueInstant(0)
        self._progress.setStatus("")
        self._time_label.setText("")
        self._retry_btn.setVisible(False)
        self._start_time = None

    def set_active(self) -> None:
        """Set stage to active state with pulsing animation."""
        self._start_time = time.time()
        self._timer.start(1000)
        self._pulse_animation.start()

        self._status_label.setText(self.tr("Processing..."))
        self._status_label.setProperty("state", "active")
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

        self._indicator.setProperty("state", "active")
        self._indicator.style().unpolish(self._indicator)
        self._indicator.style().polish(self._indicator)

        self._progress.setStatus("active")
        self._retry_btn.setVisible(False)

    def set_progress(self, value: int) -> None:
        """Set progress value (0-100) with animation."""
        self._current_progress = value
        self._progress.setValue(value)

    def set_complete(self) -> None:
        """Set stage to complete state."""
        self._pulse_animation.stop()
        self._opacity_effect.setOpacity(1.0)
        self._timer.stop()

        # Record final time
        if self._start_time:
            elapsed = time.time() - self._start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            if minutes > 0:
                self._time_label.setText(f"{minutes}m {seconds}s")
            else:
                self._time_label.setText(f"{seconds}s")

        self._status_label.setText(self.tr("Complete"))
        self._status_label.setProperty("state", "complete")
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

        self._indicator.setProperty("state", "complete")
        self._indicator.style().unpolish(self._indicator)
        self._indicator.style().polish(self._indicator)

        self._progress.setValue(100)
        self._progress.setStatus("success")
        self._retry_btn.setVisible(False)

    def set_error(self, message: str = "Error") -> None:
        """Set stage to error state."""
        self._pulse_animation.stop()
        self._opacity_effect.setOpacity(1.0)
        self._timer.stop()

        # Update final time before stopping
        if self._start_time is not None:
            elapsed = time.time() - self._start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            if minutes > 0:
                self._time_label.setText(f"{minutes}m {seconds}s (failed)")
            else:
                self._time_label.setText(f"{seconds}s (failed)")

        self._status_label.setText(message)
        self._status_label.setProperty("state", "error")
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

        self._indicator.setProperty("state", "error")
        self._indicator.style().unpolish(self._indicator)
        self._indicator.style().polish(self._indicator)

        self._progress.setStatus("error")
        self._retry_btn.setVisible(True)

        self.add_log(f"Error: {message}")

    def reset(self, preserve_expansion: bool = False) -> None:
        """Reset the stage.

        Args:
            preserve_expansion: If True, keep the current expansion state.
        """
        self.set_waiting()
        self.clear_logs()
        self._expand_btn.setVisible(False)
        if not preserve_expansion:
            self._log_panel.setVisible(False)
            self._is_expanded = False

    def get_expansion_state(self) -> bool:
        """Get the current expansion state."""
        return self._is_expanded

    def set_expansion_state(self, expanded: bool) -> None:
        """Set the expansion state without resetting logs."""
        self._is_expanded = expanded
        if self._logs:  # Only show if there are logs
            self._log_panel.setVisible(expanded)
            self._expand_btn.setText("Hide" if expanded else "Details")


class ProgressPanel(QWidget):
    """
    Panel showing overall processing progress with animations.

    Features:
    - Animated progress bars for each stage
    - Overall time tracking
    - Stage-specific logs
    - Error recovery with retry buttons
    """

    stage_changed = Signal(ProcessingStage)
    processing_complete = Signal()
    processing_error = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_stage = ProcessingStage.IDLE
        self._start_time: float | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(12)

        # Header with overall time
        header_layout = QHBoxLayout()

        self._header = QLabel(self.tr("Processing Pipeline"))
        self._header.setObjectName("progressHeader")
        self._header.setFont(QFont("", 16, QFont.Weight.DemiBold))
        header_layout.addWidget(self._header)

        header_layout.addStretch()

        self._total_time_label = QLabel("")
        self._total_time_label.setObjectName("totalTime")
        header_layout.addWidget(self._total_time_label)

        layout.addLayout(header_layout)

        # Stage widgets
        self._transcribe_stage = StageProgressWidget(self.tr("Transcription"), 1)
        self._transcribe_stage.retry_requested.connect(
            lambda: self._retry_stage(ProcessingStage.TRANSCRIBING)
        )
        layout.addWidget(self._transcribe_stage)

        self._merge_stage = StageProgressWidget(self.tr("Merge Channels"), 2)
        self._merge_stage.retry_requested.connect(
            lambda: self._retry_stage(ProcessingStage.MERGING)
        )
        layout.addWidget(self._merge_stage)

        self._audit_stage = StageProgressWidget(self.tr("Quality Audit"), 3)
        self._audit_stage.retry_requested.connect(
            lambda: self._retry_stage(ProcessingStage.AUDITING)
        )
        layout.addWidget(self._audit_stage)

        self._report_stage = StageProgressWidget(self.tr("Generate Report"), 4)
        self._report_stage.retry_requested.connect(
            lambda: self._retry_stage(ProcessingStage.GENERATING_REPORT)
        )
        layout.addWidget(self._report_stage)

        # Overall status
        self._overall_status = QLabel(self.tr("Ready to process"))
        self._overall_status.setObjectName("overallStatus")
        self._overall_status.setProperty("state", "idle")
        self._overall_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._overall_status)

        # Total time update timer
        self._total_timer = QTimer(self)
        self._total_timer.timeout.connect(self._update_total_time)

    def _update_total_time(self) -> None:
        """Update total elapsed time display."""
        if self._start_time is None:
            return

        elapsed = time.time() - self._start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        if minutes > 0:
            self._total_time_label.setText(f"Total: {minutes}m {seconds}s")
        else:
            self._total_time_label.setText(f"Total: {seconds}s")

    def _retry_stage(self, stage: ProcessingStage) -> None:
        """Handle retry request for a stage."""
        # Reset the stage and restart from there
        stage_widget = self._get_stage_widget(stage)
        if stage_widget:
            stage_widget.reset()
            stage_widget.set_active()
            self._set_stage(stage)

    def _get_stage_widget(self, stage: ProcessingStage) -> StageProgressWidget | None:
        """Get the widget for a stage."""
        return {
            ProcessingStage.TRANSCRIBING: self._transcribe_stage,
            ProcessingStage.MERGING: self._merge_stage,
            ProcessingStage.AUDITING: self._audit_stage,
            ProcessingStage.GENERATING_REPORT: self._report_stage,
        }.get(stage)

    def start_full_process(self) -> None:
        """Start the full processing pipeline."""
        self.reset()
        self._start_time = time.time()
        self._total_timer.start(1000)

        self._set_stage(ProcessingStage.TRANSCRIBING)
        self._transcribe_stage.set_active()

        self._overall_status.setText(self.tr("Processing audio file..."))
        self._overall_status.setProperty("state", "active")
        self._overall_status.style().unpolish(self._overall_status)
        self._overall_status.style().polish(self._overall_status)

    def start_transcription(self) -> None:
        """Start transcription stage."""
        self._set_stage(ProcessingStage.TRANSCRIBING)
        self._transcribe_stage.set_active()

    def update_transcription_progress(self, progress: int) -> None:
        """Update transcription progress."""
        self._transcribe_stage.set_progress(progress)

    def add_transcription_log(self, message: str) -> None:
        """Add a log message to transcription stage."""
        self._transcribe_stage.add_log(message)

    def complete_transcription(self) -> None:
        """Mark transcription as complete."""
        self._transcribe_stage.set_complete()
        self._set_stage(ProcessingStage.MERGING)
        self._merge_stage.set_active()

    def update_merge_progress(self, progress: int) -> None:
        """Update merge progress."""
        self._merge_stage.set_progress(progress)

    def add_merge_log(self, message: str) -> None:
        """Add a log message to merge stage."""
        self._merge_stage.add_log(message)

    def complete_merge(self) -> None:
        """Mark merge as complete."""
        self._merge_stage.set_complete()
        self._set_stage(ProcessingStage.AUDITING)
        self._audit_stage.set_active()

    def update_audit_progress(self, progress: int) -> None:
        """Update audit progress."""
        self._audit_stage.set_progress(progress)

    def add_audit_log(self, message: str) -> None:
        """Add a log message to audit stage."""
        self._audit_stage.add_log(message)

    def complete_audit(self) -> None:
        """Mark audit as complete."""
        self._audit_stage.set_complete()
        self._set_stage(ProcessingStage.GENERATING_REPORT)
        self._report_stage.set_active()

    def update_report_progress(self, progress: int) -> None:
        """Update report progress."""
        self._report_stage.set_progress(progress)

    def add_report_log(self, message: str) -> None:
        """Add a log message to report stage."""
        self._report_stage.add_log(message)

    def complete_all(self) -> None:
        """Mark all stages as complete."""
        self._total_timer.stop()
        self._report_stage.set_complete()
        self._set_stage(ProcessingStage.COMPLETE)

        # Show final time
        if self._start_time:
            elapsed = time.time() - self._start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            if minutes > 0:
                self._total_time_label.setText(f"Completed in {minutes}m {seconds}s")
            else:
                self._total_time_label.setText(f"Completed in {seconds}s")

        self._overall_status.setText(self.tr("Processing complete!"))
        self._overall_status.setProperty("state", "complete")
        self._overall_status.style().unpolish(self._overall_status)
        self._overall_status.style().polish(self._overall_status)

        self.processing_complete.emit()

    def set_error(self, stage: ProcessingStage, message: str) -> None:
        """Set error state for a stage."""
        self._total_timer.stop()
        self._set_stage(ProcessingStage.ERROR)

        stage_widget = self._get_stage_widget(stage)
        if stage_widget:
            stage_widget.set_error(message)

        self._overall_status.setText(f"Error: {message}")
        self._overall_status.setProperty("state", "error")
        self._overall_status.style().unpolish(self._overall_status)
        self._overall_status.style().polish(self._overall_status)

        self.processing_error.emit(message)

    def stop(self) -> None:
        """Stop processing."""
        self._total_timer.stop()
        self._set_stage(ProcessingStage.IDLE)

        self._overall_status.setText(self.tr("Stopped"))
        self._overall_status.setProperty("state", "warning")
        self._overall_status.style().unpolish(self._overall_status)
        self._overall_status.style().polish(self._overall_status)

    def reset(self) -> None:
        """Reset all stages."""
        self._total_timer.stop()
        self._start_time = None
        self._total_time_label.setText("")

        self._transcribe_stage.reset()
        self._merge_stage.reset()
        self._audit_stage.reset()
        self._report_stage.reset()

        self._set_stage(ProcessingStage.IDLE)

        self._overall_status.setText(self.tr("Ready to process"))
        self._overall_status.setProperty("state", "idle")
        self._overall_status.style().unpolish(self._overall_status)
        self._overall_status.style().polish(self._overall_status)

    def _set_stage(self, stage: ProcessingStage) -> None:
        """Set the current stage."""
        self._current_stage = stage
        self.stage_changed.emit(stage)

    @property
    def current_stage(self) -> ProcessingStage:
        """Get the current processing stage."""
        return self._current_stage
