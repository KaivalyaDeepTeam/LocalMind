"""
LocalMind Application Entry Point

This is the main entry point for the LocalMind application.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication

from localmind import __app_name__, __version__
from localmind.main_window import MainWindow
from localmind.config.settings import get_settings_manager, get_settings
from localmind.ui.theme_manager import init_theme_manager


def setup_application() -> QApplication:
    """Configure and create the Qt application."""
    QCoreApplication.setApplicationName(__app_name__)
    QCoreApplication.setApplicationVersion(__version__)
    QCoreApplication.setOrganizationName("LocalMind")
    QCoreApplication.setOrganizationDomain("localmind.ai")

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
    app = setup_application()

    settings_manager = get_settings_manager()
    settings = settings_manager.settings

    # Create main window
    window = MainWindow()

    # Restore or center window
    if settings.app.first_run_complete:
        window.resize(settings.app.window_width, settings.app.window_height)
        window.move(settings.app.window_x, settings.app.window_y)
    else:
        screen = app.primaryScreen().geometry()
        window.resize(1200, 800)
        window.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )

    window.show()

    # First run wizard
    if not settings.app.first_run_complete:
        window.show_first_run_wizard()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
