"""
CallScore Desktop Application Entry Point

This is the main entry point for the CallScore Desktop application.
Run this file to start the application.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon

from desktop import __app_name__, __version__
from desktop.main_window import MainWindow
from desktop.config.user_settings import get_settings_manager, get_settings
from desktop.ui.theme_manager import init_theme_manager


def setup_application() -> QApplication:
    """Configure and create the Qt application."""
    # Set application metadata before creating QApplication
    QCoreApplication.setApplicationName(__app_name__)
    QCoreApplication.setApplicationVersion(__version__)
    QCoreApplication.setOrganizationName("CallScore")
    QCoreApplication.setOrganizationDomain("callscore.io")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # Use Fusion style for consistent cross-platform appearance
    app.setStyle("Fusion")

    # Initialize theme manager and apply user's theme preference
    theme_manager = init_theme_manager(app)
    settings = get_settings()
    theme_manager.set_theme(settings.app.theme)

    return app


def main() -> int:
    """Main application entry point."""
    # Create application
    app = setup_application()

    # Initialize settings manager
    settings_manager = get_settings_manager()
    settings = settings_manager.settings

    # Create and show main window
    window = MainWindow()

    # Restore window geometry if available
    if settings.app.first_run_complete:
        window.resize(settings.app.window_width, settings.app.window_height)
        window.move(settings.app.window_x, settings.app.window_y)
    else:
        # Center window on screen for first run
        screen = app.primaryScreen().geometry()
        window.resize(1200, 800)
        window.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )

    window.show()

    # Check if first run - show setup wizard
    if not settings.app.first_run_complete:
        window.show_first_run_wizard()

    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
