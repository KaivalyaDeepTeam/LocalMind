"""
Toast Notification System for LocalMind

Google-style toast notifications with animations, auto-dismiss,
and action button support.
"""

from typing import Optional, Callable
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,
    QApplication
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    Property, Signal, QPoint, QSize
)
from PySide6.QtGui import QFont


class ToastType(Enum):
    """Toast notification types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Default durations per toast type (errors need more time to read)
DEFAULT_DURATIONS = {
    ToastType.SUCCESS: 4000,
    ToastType.INFO: 5000,
    ToastType.WARNING: 6000,
    ToastType.ERROR: 8000,
}


class ToastNotification(QFrame):
    """
    A single toast notification with slide-in animation.

    Features:
    - Slide-in from bottom-right
    - Auto-dismiss after configurable duration
    - Optional action button
    - Different types (success, error, warning, info)
    """

    closed = Signal()

    # Type-specific styling
    STYLES = {
        ToastType.SUCCESS: {
            "bg": "#D1FAE5",
            "border": "#059669",
            "text": "#065F46",
            "icon": "✓",
            "bg_dark": "#064E3B",
            "text_dark": "#A7F3D0",
        },
        ToastType.ERROR: {
            "bg": "#FEE2E2",
            "border": "#DC2626",
            "text": "#991B1B",
            "icon": "✕",
            "bg_dark": "#7F1D1D",
            "text_dark": "#FECACA",
        },
        ToastType.WARNING: {
            "bg": "#FEF3C7",
            "border": "#D97706",
            "text": "#92400E",
            "icon": "⚠",
            "bg_dark": "#78350F",
            "text_dark": "#FDE68A",
        },
        ToastType.INFO: {
            "bg": "#E0F2FE",
            "border": "#0284C7",
            "text": "#075985",
            "icon": "ℹ",
            "bg_dark": "#0C4A6E",
            "text_dark": "#BAE6FD",
        },
    }

    def __init__(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = 4000,
        action_text: Optional[str] = None,
        action_callback: Optional[Callable] = None,
        parent: Optional[QWidget] = None,
        dark_mode: bool = False,
    ):
        super().__init__(parent)

        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        self._action_text = action_text
        self._action_callback = action_callback
        self._dark_mode = dark_mode

        self._setup_ui()
        self._setup_animations()

        # Start auto-dismiss timer
        if duration > 0:
            QTimer.singleShot(duration, self._start_hide_animation)

    def _setup_ui(self) -> None:
        """Set up the toast UI."""
        style = self.STYLES[self._toast_type]

        # Choose colors based on dark mode
        if self._dark_mode:
            bg_color = style["bg_dark"]
            text_color = style["text_dark"]
            border_color = style["border"]
        else:
            bg_color = style["bg"]
            text_color = style["text"]
            border_color = style["border"]

        self.setObjectName("toast")
        self.setStyleSheet(f"""
            QFrame#toast {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 0px;
            }}
            QLabel {{
                background-color: transparent;
                color: {text_color};
            }}
            QPushButton {{
                background-color: transparent;
                color: {border_color};
                border: none;
                padding: 4px 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(style["icon"])
        icon_label.setFont(QFont("", 16))
        layout.addWidget(icon_label)

        # Message
        message_label = QLabel(self._message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("", 13))
        layout.addWidget(message_label, 1)

        # Action button (optional)
        if self._action_text and self._action_callback:
            action_btn = QPushButton(self._action_text)
            action_btn.clicked.connect(self._on_action_clicked)
            layout.addWidget(action_btn)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self._start_hide_animation)
        layout.addWidget(close_btn)

        # Responsive width based on parent size
        self.setMinimumWidth(280)
        # Calculate max width as percentage of parent (max 450px)
        if self.parent():
            parent_width = self.parent().width()
            # Use 40% of parent width, capped between 280-450px
            responsive_max = min(450, max(280, int(parent_width * 0.4)))
            self.setMaximumWidth(responsive_max)
        else:
            self.setMaximumWidth(450)
        self.adjustSize()

    def _setup_animations(self) -> None:
        """Set up slide and fade animations."""
        # Opacity effect for fade
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Fade in animation
        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out animation
        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out.setDuration(200)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self._on_hide_finished)

    def show_animated(self) -> None:
        """Show the toast with animation."""
        self.show()
        self._fade_in.start()

    def _start_hide_animation(self) -> None:
        """Start the hide animation."""
        self._fade_out.start()

    def _on_hide_finished(self) -> None:
        """Called when hide animation finishes."""
        self.hide()
        self.closed.emit()
        self.deleteLater()

    def _on_action_clicked(self) -> None:
        """Handle action button click."""
        if self._action_callback:
            self._action_callback()
        self._start_hide_animation()


class ToastManager(QWidget):
    """
    Manages toast notifications in a stack at the bottom-right of the window.

    Usage:
        manager = ToastManager(parent_window)
        manager.show_toast("File saved successfully!", ToastType.SUCCESS)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._toasts: list[ToastNotification] = []
        self._spacing = 12
        self._margin = 20
        self._dark_mode = False

        # Make this widget invisible and non-interactive
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Position at bottom-right of parent
        if parent:
            parent.installEventFilter(self)
            self._update_position()

    def set_dark_mode(self, dark: bool) -> None:
        """Set dark mode for new toasts."""
        self._dark_mode = dark

    def show_toast(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: Optional[int] = None,
        action_text: Optional[str] = None,
        action_callback: Optional[Callable] = None,
    ) -> ToastNotification:
        """
        Show a new toast notification.

        Args:
            message: The message to display
            toast_type: Type of toast (success, error, warning, info)
            duration: Auto-dismiss duration in ms (0 = no auto-dismiss)
            action_text: Optional action button text
            action_callback: Optional callback for action button

        Returns:
            The created ToastNotification
        """
        # Use type-specific default duration if not specified
        if duration is None:
            duration = DEFAULT_DURATIONS.get(toast_type, 5000)

        toast = ToastNotification(
            message=message,
            toast_type=toast_type,
            duration=duration,
            action_text=action_text,
            action_callback=action_callback,
            parent=self.parent(),
            dark_mode=self._dark_mode,
        )

        toast.closed.connect(lambda: self._on_toast_closed(toast))
        self._toasts.append(toast)

        self._update_toast_positions()
        toast.show_animated()

        return toast

    def show_success(self, message: str, **kwargs) -> ToastNotification:
        """Convenience method for success toast."""
        return self.show_toast(message, ToastType.SUCCESS, **kwargs)

    def show_error(self, message: str, **kwargs) -> ToastNotification:
        """Convenience method for error toast."""
        return self.show_toast(message, ToastType.ERROR, **kwargs)

    def show_warning(self, message: str, **kwargs) -> ToastNotification:
        """Convenience method for warning toast."""
        return self.show_toast(message, ToastType.WARNING, **kwargs)

    def show_info(self, message: str, **kwargs) -> ToastNotification:
        """Convenience method for info toast."""
        return self.show_toast(message, ToastType.INFO, **kwargs)

    def _on_toast_closed(self, toast: ToastNotification) -> None:
        """Handle toast close."""
        if toast in self._toasts:
            self._toasts.remove(toast)
            self._update_toast_positions()

    def _update_toast_positions(self) -> None:
        """Update positions of all toasts in the stack."""
        if not self.parent():
            return

        parent = self.parent()
        parent_rect = parent.rect()

        # Start from bottom-right
        y_offset = self._margin

        for toast in reversed(self._toasts):
            x = parent_rect.width() - toast.width() - self._margin
            y = parent_rect.height() - toast.height() - y_offset

            toast.move(x, y)
            y_offset += toast.height() + self._spacing

    def _update_position(self) -> None:
        """Update manager position when parent resizes."""
        self._update_toast_positions()

    def eventFilter(self, obj, event) -> bool:
        """Handle parent resize events."""
        if obj == self.parent() and event.type() == event.Type.Resize:
            self._update_toast_positions()
        return super().eventFilter(obj, event)

    def clear_all(self) -> None:
        """Clear all toasts."""
        for toast in self._toasts[:]:
            toast._start_hide_animation()


# Global toast manager instance
_toast_manager: Optional[ToastManager] = None


def get_toast_manager() -> Optional[ToastManager]:
    """Get the global toast manager."""
    return _toast_manager


def init_toast_manager(parent: QWidget) -> ToastManager:
    """Initialize the global toast manager."""
    global _toast_manager
    _toast_manager = ToastManager(parent)
    return _toast_manager


def show_toast(
    message: str,
    toast_type: ToastType = ToastType.INFO,
    **kwargs
) -> Optional[ToastNotification]:
    """
    Show a toast notification using the global manager.

    Convenience function for quick toast display.
    """
    manager = get_toast_manager()
    if manager:
        return manager.show_toast(message, toast_type, **kwargs)
    return None
