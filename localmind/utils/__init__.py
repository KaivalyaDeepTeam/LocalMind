"""LocalMind utilities."""

from .error_handler import (
    ErrorHandler,
    ErrorInfo,
    ErrorSeverity,
    ErrorMessages,
    ErrorContext,
    get_error_handler,
    safe_call,
)

__all__ = [
    "ErrorHandler",
    "ErrorInfo",
    "ErrorSeverity",
    "ErrorMessages",
    "ErrorContext",
    "get_error_handler",
    "safe_call",
]
