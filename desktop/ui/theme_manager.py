"""
Theme Manager for CallScore Desktop

Handles loading and switching between light/dark themes,
including automatic system theme detection.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Callable, List

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor

logger = logging.getLogger(__name__)


class ThemeManager(QObject):
    """
    Manages application themes.

    Supports light, dark, and system-automatic themes.
    Loads QSS stylesheets from resources/styles/.
    """

    # Signal emitted when theme changes
    theme_changed = Signal(str)  # theme name

    THEMES = ["light", "dark", "system"]

    def __init__(self, app: QApplication):
        super().__init__()
        self._app = app
        self._current_theme = "system"
        self._resolved_theme = "light"  # Actual theme after resolving "system"
        self._watchers: List[Callable[[str], None]] = []

        # Path to stylesheets
        self._styles_dir = self._find_styles_dir()

    def _find_styles_dir(self) -> Path:
        """Find the styles directory."""
        # Try relative to this file
        current_dir = Path(__file__).parent.parent / "resources" / "styles"
        if current_dir.exists():
            return current_dir

        # Try from package root
        import desktop
        pkg_dir = Path(desktop.__file__).parent / "resources" / "styles"
        if pkg_dir.exists():
            return pkg_dir

        # Fallback
        logger.warning("Styles directory not found, using fallback")
        return Path(__file__).parent.parent / "resources" / "styles"

    @property
    def current_theme(self) -> str:
        """Get the currently set theme preference."""
        return self._current_theme

    @property
    def resolved_theme(self) -> str:
        """Get the actual theme being displayed (after resolving 'system')."""
        return self._resolved_theme

    @property
    def is_dark(self) -> bool:
        """Check if currently using dark theme."""
        return self._resolved_theme == "dark"

    def set_theme(self, theme: str) -> None:
        """
        Set and apply a theme.

        Args:
            theme: Theme name ("light", "dark", or "system")
        """
        if theme not in self.THEMES:
            logger.warning(f"Unknown theme: {theme}, using 'system'")
            theme = "system"

        self._current_theme = theme

        # Resolve system theme
        if theme == "system":
            resolved = self._detect_system_theme()
        else:
            resolved = theme

        self._resolved_theme = resolved
        self._apply_theme(resolved)
        self.theme_changed.emit(resolved)

        logger.info(f"Theme set to: {theme} (resolved: {resolved})")

    def _apply_theme(self, theme: str) -> None:
        """Load and apply the QSS stylesheet."""
        stylesheet_path = self._styles_dir / f"theme_{theme}.qss"

        if not stylesheet_path.exists():
            logger.warning(f"Stylesheet not found: {stylesheet_path}")
            # Apply basic palette instead
            self._apply_fallback_palette(theme)
            return

        try:
            with open(stylesheet_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()

            self._app.setStyleSheet(stylesheet)
            logger.debug(f"Applied stylesheet: {stylesheet_path}")

        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")
            self._apply_fallback_palette(theme)

    def _apply_fallback_palette(self, theme: str) -> None:
        """Apply a basic color palette when stylesheet is unavailable."""
        palette = QPalette()

        if theme == "dark":
            # Dark theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor("#1A1A1A"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#FAFAFA"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#242424"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2D2D2D"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#FAFAFA"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#2D2D2D"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FAFAFA"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#6366F1"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#818CF8"))
        else:
            # Light theme colors
            palette.setColor(QPalette.ColorRole.Window, QColor("#FAFAFA"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#1A1A1A"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F9FAFB"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#1A1A1A"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1A1A1A"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#6366F1"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#6366F1"))

        self._app.setPalette(palette)
        self._app.setStyleSheet("")  # Clear any existing stylesheet

    def _detect_system_theme(self) -> str:
        """Detect the system's color scheme preference."""
        # macOS
        if sys.platform == "darwin":
            try:
                from subprocess import run, DEVNULL
                result = run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True,
                    stderr=DEVNULL,
                )
                if "Dark" in result.stdout:
                    return "dark"
            except Exception:
                pass
            return "light"

        # Windows
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return "light" if value else "dark"
            except Exception:
                pass
            return "light"

        # Linux - check various environment hints
        if sys.platform.startswith("linux"):
            # Check GTK theme
            import os
            gtk_theme = os.environ.get("GTK_THEME", "").lower()
            if "dark" in gtk_theme:
                return "dark"

            # Check color scheme via Qt
            try:
                palette = self._app.palette()
                bg_color = palette.color(QPalette.ColorRole.Window)
                # If background is darker than mid-gray, assume dark theme
                if bg_color.lightness() < 128:
                    return "dark"
            except Exception:
                pass

        return "light"

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self._resolved_theme == "light":
            self.set_theme("dark")
        else:
            self.set_theme("light")

    def add_watcher(self, callback: Callable[[str], None]) -> None:
        """Add a callback to be notified of theme changes."""
        self._watchers.append(callback)
        self.theme_changed.connect(callback)

    def remove_watcher(self, callback: Callable[[str], None]) -> None:
        """Remove a theme change callback."""
        if callback in self._watchers:
            self._watchers.remove(callback)
            self.theme_changed.disconnect(callback)


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> Optional[ThemeManager]:
    """Get the global theme manager instance."""
    return _theme_manager


def init_theme_manager(app: QApplication) -> ThemeManager:
    """
    Initialize the global theme manager.

    Should be called once during application startup.

    Args:
        app: The QApplication instance

    Returns:
        The initialized ThemeManager
    """
    global _theme_manager
    _theme_manager = ThemeManager(app)
    return _theme_manager


def apply_theme_from_settings() -> None:
    """Apply theme based on user settings."""
    from desktop.config.user_settings import get_settings

    manager = get_theme_manager()
    if manager is None:
        logger.warning("Theme manager not initialized")
        return

    settings = get_settings()
    manager.set_theme(settings.app.theme)
