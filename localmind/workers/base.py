"""
LocalMind Base Worker

Base class for background worker threads using Qt's QThread.
"""

from typing import Optional, Any
from enum import Enum, auto

from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition


class WorkerState(Enum):
    """Worker state enumeration."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    FINISHED = auto()
    ERROR = auto()


class BaseWorker(QThread):
    """Base class for background workers.

    Signals:
        started_work: Emitted when work begins.
        progress: Emitted with progress updates (0-100, message).
        finished_work: Emitted when work completes successfully with result.
        error: Emitted when an error occurs with error message.
        status_changed: Emitted when worker state changes.
    """

    started_work = Signal()
    progress = Signal(int, str)  # percent, message
    finished_work = Signal(object)  # result
    error = Signal(str)  # error message
    status_changed = Signal(WorkerState)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = WorkerState.IDLE
        self._mutex = QMutex()
        self._pause_condition = QWaitCondition()
        self._should_stop = False
        self._is_paused = False
        self._result: Any = None
        self._error_message: Optional[str] = None

    @property
    def state(self) -> WorkerState:
        """Get current worker state."""
        return self._state

    @property
    def result(self) -> Any:
        """Get the result after completion."""
        return self._result

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if any."""
        return self._error_message

    def _set_state(self, state: WorkerState) -> None:
        """Set worker state and emit signal."""
        self._state = state
        self.status_changed.emit(state)

    def run(self) -> None:
        """Main thread execution - calls do_work()."""
        self._should_stop = False
        self._is_paused = False
        self._error_message = None
        self._result = None

        self._set_state(WorkerState.RUNNING)
        self.started_work.emit()

        try:
            self._result = self.do_work()
            if not self._should_stop:
                self._set_state(WorkerState.FINISHED)
                self.finished_work.emit(self._result)
        except Exception as e:
            self._error_message = str(e)
            self._set_state(WorkerState.ERROR)
            self.error.emit(self._error_message)

    def do_work(self) -> Any:
        """Override this method to perform actual work.

        Returns:
            Result of the work.

        Raises:
            Exception: If work fails.
        """
        raise NotImplementedError("Subclasses must implement do_work()")

    def stop(self) -> None:
        """Request the worker to stop."""
        self._mutex.lock()
        self._should_stop = True
        if self._is_paused:
            self._is_paused = False
            self._pause_condition.wakeAll()
        self._mutex.unlock()
        self._set_state(WorkerState.STOPPING)

    def pause(self) -> None:
        """Pause the worker."""
        self._mutex.lock()
        self._is_paused = True
        self._mutex.unlock()
        self._set_state(WorkerState.PAUSED)

    def resume(self) -> None:
        """Resume a paused worker."""
        self._mutex.lock()
        self._is_paused = False
        self._pause_condition.wakeAll()
        self._mutex.unlock()
        self._set_state(WorkerState.RUNNING)

    def check_stop(self) -> bool:
        """Check if stop was requested. Call periodically in do_work()."""
        return self._should_stop

    def check_pause(self) -> None:
        """Check and handle pause state. Call periodically in do_work()."""
        self._mutex.lock()
        while self._is_paused and not self._should_stop:
            self._pause_condition.wait(self._mutex)
        self._mutex.unlock()

    def report_progress(self, percent: int, message: str = "") -> None:
        """Report progress from do_work().

        Args:
            percent: Progress percentage (0-100).
            message: Optional status message.
        """
        self.progress.emit(percent, message)
