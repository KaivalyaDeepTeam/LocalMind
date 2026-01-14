"""
LocalMind Loading Indicator

Animated loading spinner for use during operations.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QSizePolicy,
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, Signal,
)
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class SpinnerWidget(QWidget):
    """Animated spinner widget."""

    def __init__(self, size: int = 20, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._size = size
        self._angle = 0
        self._color = QColor("#6366F1")  # Indigo

        self.setFixedSize(size, size)

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)

    def start(self) -> None:
        """Start the spinner animation."""
        self._timer.start(50)  # 20 FPS
        self.show()

    def stop(self) -> None:
        """Stop the spinner animation."""
        self._timer.stop()
        self.hide()

    def _rotate(self) -> None:
        """Rotate the spinner."""
        self._angle = (self._angle + 30) % 360
        self.update()

    def set_color(self, color: QColor) -> None:
        """Set the spinner color."""
        self._color = color

    def paintEvent(self, event) -> None:
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate center and radius
        center = self.rect().center()
        radius = (self._size - 4) / 2

        # Draw arc segments with varying opacity
        pen = QPen(self._color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        for i in range(8):
            # Calculate opacity based on position
            opacity = 0.15 + (i / 8.0) * 0.85
            color = QColor(self._color)
            color.setAlphaF(opacity)
            pen.setColor(color)
            painter.setPen(pen)

            # Calculate angle for this segment
            segment_angle = self._angle + (i * 45)
            start_angle = segment_angle * 16  # Qt uses 1/16 degree
            span_angle = 30 * 16

            rect = self.rect().adjusted(2, 2, -2, -2)
            painter.drawArc(rect, start_angle, span_angle)


class LoadingButton(QPushButton):
    """Button with built-in loading state."""

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._original_text = text
        self._loading = False

        # Create spinner
        self._spinner = SpinnerWidget(16, self)
        self._spinner.hide()

    def set_loading(self, loading: bool, text: Optional[str] = None) -> None:
        """Set the loading state."""
        self._loading = loading

        if loading:
            self.setEnabled(False)
            if text:
                self.setText(f"  {text}")
            else:
                self.setText(f"  {self._original_text}...")
            self._position_spinner()
            self._spinner.start()
        else:
            self.setEnabled(True)
            self.setText(self._original_text)
            self._spinner.stop()

    def _position_spinner(self) -> None:
        """Position the spinner inside the button."""
        # Position spinner at left side of button
        x = 8
        y = (self.height() - self._spinner.height()) // 2
        self._spinner.move(x, y)

    def resizeEvent(self, event) -> None:
        """Handle resize to reposition spinner."""
        super().resizeEvent(event)
        if self._loading:
            self._position_spinner()

    def is_loading(self) -> bool:
        """Check if button is in loading state."""
        return self._loading


class LoadingOverlay(QFrame):
    """Loading overlay with spinner and message."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self.hide()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setObjectName("loadingOverlay")
        self.setStyleSheet("""
            #loadingOverlay {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spinner
        self._spinner = SpinnerWidget(32)
        layout.addWidget(self._spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        # Message
        self._message = QLabel("Loading...")
        self._message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message.setStyleSheet("color: #374151; font-size: 13px;")
        layout.addWidget(self._message)

    def show_loading(self, message: str = "Loading...") -> None:
        """Show the loading overlay."""
        self._message.setText(message)
        self._spinner.start()

        # Resize to parent
        if self.parent():
            self.setGeometry(self.parent().rect())

        self.show()
        self.raise_()

    def hide_loading(self) -> None:
        """Hide the loading overlay."""
        self._spinner.stop()
        self.hide()


class InlineLoadingIndicator(QWidget):
    """Inline loading indicator with text."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self.hide()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Spinner
        self._spinner = SpinnerWidget(16)
        layout.addWidget(self._spinner)

        # Message
        self._message = QLabel("Loading...")
        self._message.setStyleSheet("color: #6B7280; font-size: 12px;")
        layout.addWidget(self._message)

        layout.addStretch()

    def show_loading(self, message: str = "Loading...") -> None:
        """Show the loading indicator."""
        self._message.setText(message)
        self._spinner.start()
        self.show()

    def hide_loading(self) -> None:
        """Hide the loading indicator."""
        self._spinner.stop()
        self.hide()
