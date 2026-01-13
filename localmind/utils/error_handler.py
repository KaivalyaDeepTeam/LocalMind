"""
LocalMind Error Handling Utilities

Centralized error handling for consistent user feedback and logging.
"""

import logging
import sys
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any

from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QObject, Signal


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """Container for error information."""
    title: str
    message: str
    severity: ErrorSeverity
    details: Optional[str] = None
    exception: Optional[Exception] = None


class ErrorHandler(QObject):
    """Centralized error handler for the application."""

    error_occurred = Signal(ErrorInfo)

    _instance: Optional["ErrorHandler"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        super().__init__()
        self._initialized = True
        self._parent_widget: Optional[QWidget] = None
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def set_parent_widget(self, widget: QWidget):
        """Set the parent widget for dialogs."""
        self._parent_widget = widget

    def handle_error(
        self,
        error: Exception,
        title: str = "Error",
        message: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        show_dialog: bool = True,
    ) -> ErrorInfo:
        """
        Handle an error with logging and optional user notification.

        Args:
            error: The exception that occurred
            title: Dialog title
            message: User-friendly message (defaults to str(error))
            severity: Error severity level
            show_dialog: Whether to show a dialog to the user

        Returns:
            ErrorInfo object with error details
        """
        if message is None:
            message = str(error)

        details = traceback.format_exc()

        error_info = ErrorInfo(
            title=title,
            message=message,
            severity=severity,
            details=details,
            exception=error,
        )

        # Log the error
        log_method = {
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical,
        }.get(severity, logger.error)

        log_method(f"{title}: {message}\n{details}")

        # Emit signal
        self.error_occurred.emit(error_info)

        # Show dialog if requested
        if show_dialog:
            self._show_error_dialog(error_info)

        return error_info

    def handle_warning(
        self,
        message: str,
        title: str = "Warning",
        show_dialog: bool = True,
    ) -> ErrorInfo:
        """Handle a warning with optional user notification."""
        error_info = ErrorInfo(
            title=title,
            message=message,
            severity=ErrorSeverity.WARNING,
        )

        logger.warning(f"{title}: {message}")
        self.error_occurred.emit(error_info)

        if show_dialog:
            self._show_warning_dialog(error_info)

        return error_info

    def _show_error_dialog(self, error_info: ErrorInfo):
        """Show an error dialog to the user."""
        icon = {
            ErrorSeverity.INFO: QMessageBox.Icon.Information,
            ErrorSeverity.WARNING: QMessageBox.Icon.Warning,
            ErrorSeverity.ERROR: QMessageBox.Icon.Critical,
            ErrorSeverity.CRITICAL: QMessageBox.Icon.Critical,
        }.get(error_info.severity, QMessageBox.Icon.Critical)

        dialog = QMessageBox(self._parent_widget)
        dialog.setIcon(icon)
        dialog.setWindowTitle(error_info.title)
        dialog.setText(error_info.message)

        if error_info.details:
            dialog.setDetailedText(error_info.details)

        dialog.exec()

    def _show_warning_dialog(self, error_info: ErrorInfo):
        """Show a warning dialog to the user."""
        dialog = QMessageBox(self._parent_widget)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(error_info.title)
        dialog.setText(error_info.message)
        dialog.exec()


def get_error_handler() -> ErrorHandler:
    """Get the singleton error handler instance."""
    return ErrorHandler()


def safe_call(
    func: Callable,
    *args,
    error_title: str = "Error",
    error_message: Optional[str] = None,
    show_dialog: bool = True,
    default_return: Any = None,
    **kwargs,
) -> Any:
    """
    Safely call a function with error handling.

    Args:
        func: Function to call
        *args: Positional arguments for the function
        error_title: Title for error dialog
        error_message: Custom error message
        show_dialog: Whether to show error dialog
        default_return: Value to return on error
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        get_error_handler().handle_error(
            error=e,
            title=error_title,
            message=error_message,
            show_dialog=show_dialog,
        )
        return default_return


class ErrorContext:
    """Context manager for error handling."""

    def __init__(
        self,
        title: str = "Error",
        message: Optional[str] = None,
        show_dialog: bool = True,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        reraise: bool = False,
    ):
        self.title = title
        self.message = message
        self.show_dialog = show_dialog
        self.severity = severity
        self.reraise = reraise
        self.error_info: Optional[ErrorInfo] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.error_info = get_error_handler().handle_error(
                error=exc_val,
                title=self.title,
                message=self.message,
                severity=self.severity,
                show_dialog=self.show_dialog,
            )
            return not self.reraise
        return False


# Common error messages
class ErrorMessages:
    """Common error messages for the application."""

    # File errors
    FILE_NOT_FOUND = "The specified file could not be found."
    FILE_READ_ERROR = "An error occurred while reading the file."
    FILE_WRITE_ERROR = "An error occurred while writing the file."
    INVALID_AUDIO_FORMAT = "The audio file format is not supported."

    # Model errors
    MODEL_NOT_FOUND = "The required model is not installed."
    MODEL_LOAD_ERROR = "Failed to load the AI model."
    MODEL_DOWNLOAD_ERROR = "Failed to download the model."

    # LLM errors
    LLM_CONNECTION_ERROR = "Failed to connect to the LLM provider."
    LLM_API_KEY_INVALID = "The API key is invalid or expired."
    LLM_RATE_LIMIT = "Rate limit exceeded. Please try again later."
    LLM_RESPONSE_ERROR = "Failed to parse the LLM response."

    # Processing errors
    TRANSCRIPTION_ERROR = "An error occurred during transcription."
    MERGE_ERROR = "An error occurred while merging transcripts."
    AUDIT_ERROR = "An error occurred during the audit process."

    # Report errors
    PDF_GENERATION_ERROR = "Failed to generate the PDF report."
    MISSING_DEPENDENCIES = "Required dependencies are not installed."
