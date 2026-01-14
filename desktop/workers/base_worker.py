"""
Base Worker Classes for CallScore Desktop

Provides thread-safe worker base classes for background processing operations.
"""

from typing import Any, Optional
from enum import Enum

from PySide6.QtCore import QObject, QRunnable, Signal, QMutex, QMutexLocker


class ProcessingStage(Enum):
    """Processing pipeline stages with progress percentages."""
    IDLE = ("idle", 0)
    LOADING_MODELS = ("loading_models", 0)
    PREPROCESSING = ("preprocessing", 10)
    DIARIZATION = ("diarization", 20)
    TRANSCRIPTION_V3 = ("transcription_v3", 30)
    TRANSCRIPTION_H2H = ("transcription_h2h", 50)
    MERGING = ("merging", 70)
    AUDITING = ("auditing", 85)
    GENERATING_REPORT = ("generating_report", 95)
    COMPLETE = ("complete", 100)
    ERROR = ("error", -1)
    CANCELLED = ("cancelled", -1)

    def __init__(self, stage_id: str, progress: int):
        self.stage_id = stage_id
        self.base_progress = progress

    @property
    def label(self) -> str:
        """Human-readable label for this stage."""
        labels = {
            "idle": "Ready",
            "loading_models": "Loading AI models...",
            "preprocessing": "Preprocessing audio...",
            "diarization": "Identifying speakers...",
            "transcription_v3": "Transcribing (Whisper V3)...",
            "transcription_h2h": "Transcribing (Hindi2Hinglish)...",
            "merging": "Merging transcripts...",
            "auditing": "Auditing call quality...",
            "generating_report": "Generating report...",
            "complete": "Complete",
            "error": "Error occurred",
            "cancelled": "Cancelled",
        }
        return labels.get(self.stage_id, "Processing...")


class WorkerSignals(QObject):
    """
    Standard signals emitted by all workers.

    Signals:
        started: Emitted when worker begins processing
        progress: (percentage: int, message: str) Progress update
        stage_changed: (stage: ProcessingStage) Processing stage changed
        finished: (result: Any) Worker completed successfully with result
        error: (error_type: str, message: str) Error occurred
        cancelled: Worker was cancelled
    """
    started = Signal()
    progress = Signal(int, str)
    stage_changed = Signal(object)  # ProcessingStage
    finished = Signal(object)
    error = Signal(str, str)
    cancelled = Signal()


class BaseWorker(QRunnable):
    """
    Base class for all background processing workers.

    Subclasses should override the `run()` method to implement
    their processing logic. Use `is_cancelled()` to check for
    cancellation requests and emit appropriate signals.

    Example:
        class MyWorker(BaseWorker):
            def run(self):
                try:
                    self.signals.started.emit()
                    self._set_stage(ProcessingStage.LOADING_MODELS)

                    # Do work...
                    if self.is_cancelled():
                        self.signals.cancelled.emit()
                        return

                    self._set_stage(ProcessingStage.COMPLETE)
                    self.signals.finished.emit(result)
                except Exception as e:
                    self.signals.error.emit(type(e).__name__, str(e))
    """

    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self._is_cancelled = False
        self._mutex = QMutex()
        self._current_stage = ProcessingStage.IDLE

        # Enable auto-delete after completion
        self.setAutoDelete(True)

    def cancel(self) -> None:
        """
        Request cancellation of the worker.

        The worker should check `is_cancelled()` periodically
        and stop processing gracefully when True.
        """
        with QMutexLocker(self._mutex):
            self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """
        Check if cancellation has been requested.

        Returns:
            True if cancel() has been called, False otherwise.
        """
        with QMutexLocker(self._mutex):
            return self._is_cancelled

    def _set_stage(self, stage: ProcessingStage, detail: str = "") -> None:
        """
        Update the current processing stage.

        Args:
            stage: The new processing stage
            detail: Optional detail message for progress
        """
        self._current_stage = stage
        self.signals.stage_changed.emit(stage)

        if stage.base_progress >= 0:
            message = detail if detail else stage.label
            self.signals.progress.emit(stage.base_progress, message)

    def _emit_progress(self, percentage: int, message: str) -> None:
        """
        Emit a progress update.

        Args:
            percentage: Progress percentage (0-100)
            message: Progress message to display
        """
        self.signals.progress.emit(max(0, min(100, percentage)), message)

    @property
    def current_stage(self) -> ProcessingStage:
        """Get the current processing stage."""
        return self._current_stage

    def run(self) -> None:
        """
        Execute the worker's task.

        Subclasses must override this method to implement their
        processing logic. Should emit appropriate signals:
        - started: When beginning work
        - progress: For progress updates
        - stage_changed: When moving to a new stage
        - finished: When complete (with result)
        - error: When an error occurs
        - cancelled: When cancelled
        """
        raise NotImplementedError("Subclasses must implement run()")


class SimpleWorker(BaseWorker):
    """
    Simple worker that executes a callable function.

    Useful for one-off background tasks that don't need
    complex stage tracking.

    Example:
        def download_file(url):
            # ... download logic
            return filepath

        worker = SimpleWorker(download_file, "https://example.com/file.zip")
        worker.signals.finished.connect(on_download_complete)
        thread_pool.start(worker)
    """

    def __init__(self, fn: callable, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        """Execute the function and emit result."""
        try:
            self.signals.started.emit()
            result = self._fn(*self._args, **self._kwargs)

            if self.is_cancelled():
                self.signals.cancelled.emit()
            else:
                self.signals.finished.emit(result)

        except Exception as e:
            self.signals.error.emit(type(e).__name__, str(e))
