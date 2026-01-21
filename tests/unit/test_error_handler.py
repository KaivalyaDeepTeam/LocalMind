"""
Tests for Error Handler utilities.

Tests centralized error handling, logging, and user notification.
"""

from unittest.mock import MagicMock, patch

import pytest

from localmind.utils.error_handler import (
    ErrorContext,
    ErrorHandler,
    ErrorInfo,
    ErrorMessages,
    ErrorSeverity,
    get_error_handler,
    safe_call,
)


class TestErrorSeverity:
    """Tests for ErrorSeverity enum."""

    def test_error_severity_values(self):
        """Test all severity levels exist with correct values."""
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_error_severity_count(self):
        """Test we have exactly 4 severity levels."""
        assert len(ErrorSeverity) == 4


class TestErrorInfo:
    """Tests for ErrorInfo dataclass."""

    def test_error_info_creation(self):
        """Test creating an ErrorInfo."""
        error_info = ErrorInfo(
            title="Test Error",
            message="Something went wrong",
            severity=ErrorSeverity.ERROR,
        )

        assert error_info.title == "Test Error"
        assert error_info.message == "Something went wrong"
        assert error_info.severity == ErrorSeverity.ERROR
        assert error_info.details is None
        assert error_info.exception is None

    def test_error_info_with_all_fields(self):
        """Test ErrorInfo with all fields populated."""
        exc = ValueError("Test exception")
        error_info = ErrorInfo(
            title="Test Error",
            message="Something went wrong",
            severity=ErrorSeverity.CRITICAL,
            details="Traceback details here",
            exception=exc,
        )

        assert error_info.details == "Traceback details here"
        assert error_info.exception == exc

    def test_error_info_default_values(self):
        """Test ErrorInfo default values."""
        error_info = ErrorInfo(
            title="Error",
            message="Message",
            severity=ErrorSeverity.INFO,
        )

        assert error_info.details is None
        assert error_info.exception is None


class TestErrorHandlerSingleton:
    """Tests for ErrorHandler singleton pattern."""

    def test_singleton_returns_same_instance(self, qapp):
        """Test ErrorHandler returns same instance."""
        # Reset singleton for clean test
        ErrorHandler._instance = None

        handler1 = ErrorHandler()
        handler2 = ErrorHandler()

        assert handler1 is handler2

    def test_get_error_handler_returns_singleton(self, qapp):
        """Test get_error_handler returns singleton."""
        # Reset singleton
        ErrorHandler._instance = None

        handler1 = get_error_handler()
        handler2 = get_error_handler()

        assert handler1 is handler2

    def test_singleton_initialization_once(self, qapp):
        """Test singleton only initializes once."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        assert handler._initialized is True

        # Second instantiation should not re-initialize
        handler2 = ErrorHandler()
        assert handler2._initialized is True
        assert handler is handler2


class TestErrorHandlerSetParent:
    """Tests for ErrorHandler.set_parent_widget()."""

    def test_set_parent_widget(self, qapp):
        """Test setting parent widget."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        mock_widget = MagicMock()

        handler.set_parent_widget(mock_widget)

        assert handler._parent_widget == mock_widget

    def test_parent_widget_default_none(self, qapp):
        """Test parent widget defaults to None."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()

        assert handler._parent_widget is None


class TestErrorHandlerHandleError:
    """Tests for ErrorHandler.handle_error()."""

    def test_handle_error_returns_error_info(self, qapp):
        """Test handle_error returns ErrorInfo."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Test error")

        with patch.object(handler, "_show_error_dialog"):
            result = handler.handle_error(exc, show_dialog=False)

        assert isinstance(result, ErrorInfo)
        assert result.message == "Test error"
        assert result.severity == ErrorSeverity.ERROR

    def test_handle_error_custom_message(self, qapp):
        """Test handle_error with custom message."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Original error")

        with patch.object(handler, "_show_error_dialog"):
            result = handler.handle_error(exc, message="Custom user message", show_dialog=False)

        assert result.message == "Custom user message"

    def test_handle_error_custom_title(self, qapp):
        """Test handle_error with custom title."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Test")

        with patch.object(handler, "_show_error_dialog"):
            result = handler.handle_error(exc, title="Custom Title", show_dialog=False)

        assert result.title == "Custom Title"

    def test_handle_error_emits_signal(self, qapp):
        """Test handle_error emits error_occurred signal."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Test")

        signal_received = []
        handler.error_occurred.connect(lambda ei: signal_received.append(ei))

        with patch.object(handler, "_show_error_dialog"):
            handler.handle_error(exc, show_dialog=False)

        assert len(signal_received) == 1
        assert signal_received[0].message == "Test"

    def test_handle_error_includes_traceback(self, qapp):
        """Test handle_error captures traceback."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()

        try:
            raise ValueError("Test error")
        except ValueError as exc:
            with patch.object(handler, "_show_error_dialog"):
                result = handler.handle_error(exc, show_dialog=False)

        assert result.details is not None
        assert "ValueError" in result.details

    def test_handle_error_severity_levels(self, qapp):
        """Test handle_error with different severity levels."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Test")

        for severity in [
            ErrorSeverity.INFO,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL,
        ]:
            with patch.object(handler, "_show_error_dialog"):
                result = handler.handle_error(exc, severity=severity, show_dialog=False)
                assert result.severity == severity

    def test_handle_error_shows_dialog_when_requested(self, qapp):
        """Test handle_error shows dialog when show_dialog=True."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Test")

        with patch.object(handler, "_show_error_dialog") as mock_dialog:
            handler.handle_error(exc, show_dialog=True)
            mock_dialog.assert_called_once()

    def test_handle_error_no_dialog_when_disabled(self, qapp):
        """Test handle_error skips dialog when show_dialog=False."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()
        exc = ValueError("Test")

        with patch.object(handler, "_show_error_dialog") as mock_dialog:
            handler.handle_error(exc, show_dialog=False)
            mock_dialog.assert_not_called()


class TestErrorHandlerHandleWarning:
    """Tests for ErrorHandler.handle_warning()."""

    def test_handle_warning_returns_error_info(self, qapp):
        """Test handle_warning returns ErrorInfo."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()

        with patch.object(handler, "_show_warning_dialog"):
            result = handler.handle_warning("Warning message", show_dialog=False)

        assert isinstance(result, ErrorInfo)
        assert result.message == "Warning message"
        assert result.severity == ErrorSeverity.WARNING

    def test_handle_warning_custom_title(self, qapp):
        """Test handle_warning with custom title."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()

        with patch.object(handler, "_show_warning_dialog"):
            result = handler.handle_warning("Message", title="Custom Warning", show_dialog=False)

        assert result.title == "Custom Warning"

    def test_handle_warning_emits_signal(self, qapp):
        """Test handle_warning emits error_occurred signal."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()

        signal_received = []
        handler.error_occurred.connect(lambda ei: signal_received.append(ei))

        with patch.object(handler, "_show_warning_dialog"):
            handler.handle_warning("Warning", show_dialog=False)

        assert len(signal_received) == 1
        assert signal_received[0].severity == ErrorSeverity.WARNING

    def test_handle_warning_shows_dialog_when_requested(self, qapp):
        """Test handle_warning shows dialog when show_dialog=True."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = ErrorHandler()

        with patch.object(handler, "_show_warning_dialog") as mock_dialog:
            handler.handle_warning("Warning", show_dialog=True)
            mock_dialog.assert_called_once()


class TestSafeCall:
    """Tests for safe_call utility function."""

    def test_safe_call_success(self, qapp):
        """Test safe_call returns result on success."""
        # Reset singleton
        ErrorHandler._instance = None

        def successful_func(x, y):
            return x + y

        result = safe_call(successful_func, 2, 3, show_dialog=False)
        assert result == 5

    def test_safe_call_with_kwargs(self, qapp):
        """Test safe_call passes kwargs correctly."""
        # Reset singleton
        ErrorHandler._instance = None

        def func_with_kwargs(a, b=10):
            return a * b

        result = safe_call(func_with_kwargs, 5, b=20, show_dialog=False)
        assert result == 100

    def test_safe_call_exception_returns_default(self, qapp):
        """Test safe_call returns default on exception."""
        # Reset singleton
        ErrorHandler._instance = None

        def failing_func():
            raise ValueError("Intentional failure")

        result = safe_call(failing_func, default_return="default_value", show_dialog=False)
        assert result == "default_value"

    def test_safe_call_exception_returns_none_by_default(self, qapp):
        """Test safe_call returns None by default on exception."""
        # Reset singleton
        ErrorHandler._instance = None

        def failing_func():
            raise ValueError("Intentional failure")

        result = safe_call(failing_func, show_dialog=False)
        assert result is None

    def test_safe_call_handles_error(self, qapp):
        """Test safe_call calls error handler on exception."""
        # Reset singleton
        ErrorHandler._instance = None

        def failing_func():
            raise ValueError("Test error")

        handler = get_error_handler()
        signal_received = []
        handler.error_occurred.connect(lambda ei: signal_received.append(ei))

        safe_call(failing_func, show_dialog=False)

        assert len(signal_received) == 1


class TestErrorContext:
    """Tests for ErrorContext context manager."""

    def test_error_context_no_exception(self, qapp):
        """Test ErrorContext with no exception."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(show_dialog=False)

        with ctx:
            result = 1 + 1

        assert ctx.error_info is None
        assert result == 2

    def test_error_context_captures_exception(self, qapp):
        """Test ErrorContext captures exception."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(show_dialog=False)

        with ctx:
            raise ValueError("Test exception")

        assert ctx.error_info is not None
        assert "Test exception" in ctx.error_info.message

    def test_error_context_suppresses_exception(self, qapp):
        """Test ErrorContext suppresses exception by default."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(reraise=False, show_dialog=False)

        # Should not raise
        with ctx:
            raise ValueError("Should be suppressed")

        assert ctx.error_info is not None

    def test_error_context_reraises_when_requested(self, qapp):
        """Test ErrorContext reraises exception when reraise=True."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(reraise=True, show_dialog=False)

        with pytest.raises(ValueError, match="Should reraise"):
            with ctx:
                raise ValueError("Should reraise")

    def test_error_context_custom_title(self, qapp):
        """Test ErrorContext with custom title."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(title="Custom Title", show_dialog=False)

        with ctx:
            raise ValueError("Test")

        assert ctx.error_info.title == "Custom Title"

    def test_error_context_custom_message(self, qapp):
        """Test ErrorContext with custom message."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(message="Custom message", show_dialog=False)

        with ctx:
            raise ValueError("Original")

        assert ctx.error_info.message == "Custom message"

    def test_error_context_custom_severity(self, qapp):
        """Test ErrorContext with custom severity."""
        # Reset singleton
        ErrorHandler._instance = None

        ctx = ErrorContext(severity=ErrorSeverity.CRITICAL, show_dialog=False)

        with ctx:
            raise ValueError("Test")

        assert ctx.error_info.severity == ErrorSeverity.CRITICAL

    def test_error_context_emits_signal(self, qapp):
        """Test ErrorContext emits signal on error."""
        # Reset singleton
        ErrorHandler._instance = None

        handler = get_error_handler()
        signal_received = []
        handler.error_occurred.connect(lambda ei: signal_received.append(ei))

        ctx = ErrorContext(show_dialog=False)

        with ctx:
            raise ValueError("Test")

        assert len(signal_received) == 1


class TestErrorMessages:
    """Tests for ErrorMessages constants."""

    def test_file_error_messages_exist(self):
        """Test file-related error messages exist."""
        assert ErrorMessages.FILE_NOT_FOUND
        assert ErrorMessages.FILE_READ_ERROR
        assert ErrorMessages.FILE_WRITE_ERROR
        assert ErrorMessages.INVALID_AUDIO_FORMAT

    def test_model_error_messages_exist(self):
        """Test model-related error messages exist."""
        assert ErrorMessages.MODEL_NOT_FOUND
        assert ErrorMessages.MODEL_LOAD_ERROR
        assert ErrorMessages.MODEL_DOWNLOAD_ERROR

    def test_llm_error_messages_exist(self):
        """Test LLM-related error messages exist."""
        assert ErrorMessages.LLM_CONNECTION_ERROR
        assert ErrorMessages.LLM_API_KEY_INVALID
        assert ErrorMessages.LLM_RATE_LIMIT
        assert ErrorMessages.LLM_RESPONSE_ERROR

    def test_processing_error_messages_exist(self):
        """Test processing-related error messages exist."""
        assert ErrorMessages.TRANSCRIPTION_ERROR
        assert ErrorMessages.MERGE_ERROR
        assert ErrorMessages.AUDIT_ERROR

    def test_report_error_messages_exist(self):
        """Test report-related error messages exist."""
        assert ErrorMessages.PDF_GENERATION_ERROR
        assert ErrorMessages.MISSING_DEPENDENCIES

    def test_error_messages_are_strings(self):
        """Test all error messages are non-empty strings."""
        for attr_name in dir(ErrorMessages):
            if not attr_name.startswith("_"):
                attr = getattr(ErrorMessages, attr_name)
                assert isinstance(attr, str)
                assert len(attr) > 0
