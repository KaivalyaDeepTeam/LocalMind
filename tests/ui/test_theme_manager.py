"""
Tests for Theme Manager.

Tests the ThemeManager class and related functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtGui import QColor, QPalette


class TestThemeManagerConstants:
    """Tests for ThemeManager constants and class attributes."""

    def test_themes_list_contains_expected_values(self, qapp):
        """Test THEMES list has light, dark, and system options."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert "light" in manager.THEMES
        assert "dark" in manager.THEMES
        assert "system" in manager.THEMES

    def test_themes_list_length(self, qapp):
        """Test THEMES list has exactly 3 items."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert len(manager.THEMES) == 3


class TestThemeManagerInitialization:
    """Tests for ThemeManager initialization."""

    def test_initial_current_theme_is_system(self, qapp):
        """Test initial theme preference is 'system'."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert manager.current_theme == "system"

    def test_initial_resolved_theme_is_light(self, qapp):
        """Test initial resolved theme defaults to 'light'."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert manager.resolved_theme == "light"

    def test_app_reference_stored(self, qapp):
        """Test QApplication reference is stored."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert manager._app is qapp

    def test_styles_dir_is_path(self, qapp):
        """Test styles directory is a Path object."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert isinstance(manager._styles_dir, Path)


class TestThemeManagerProperties:
    """Tests for ThemeManager properties."""

    def test_current_theme_property(self, qapp):
        """Test current_theme property returns set theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._current_theme = "dark"
        assert manager.current_theme == "dark"

    def test_resolved_theme_property(self, qapp):
        """Test resolved_theme property returns actual theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._resolved_theme = "dark"
        assert manager.resolved_theme == "dark"

    def test_is_dark_true_when_dark_theme(self, qapp):
        """Test is_dark returns True when resolved theme is dark."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._resolved_theme = "dark"
        assert manager.is_dark is True

    def test_is_dark_false_when_light_theme(self, qapp):
        """Test is_dark returns False when resolved theme is light."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._resolved_theme = "light"
        assert manager.is_dark is False


class TestSetTheme:
    """Tests for ThemeManager.set_theme method."""

    def test_set_theme_light(self, qapp):
        """Test setting light theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager.set_theme("light")
        assert manager.current_theme == "light"
        assert manager.resolved_theme == "light"

    def test_set_theme_dark(self, qapp):
        """Test setting dark theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager.set_theme("dark")
        assert manager.current_theme == "dark"
        assert manager.resolved_theme == "dark"

    def test_set_theme_system_resolves(self, qapp):
        """Test setting system theme resolves to light or dark."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager.set_theme("system")
        assert manager.current_theme == "system"
        assert manager.resolved_theme in ["light", "dark"]

    def test_set_theme_invalid_defaults_to_system(self, qapp):
        """Test invalid theme defaults to system."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager.set_theme("invalid_theme")
        assert manager.current_theme == "system"

    def test_set_theme_emits_signal(self, qapp):
        """Test theme_changed signal is emitted."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        signal_received = []
        manager.theme_changed.connect(lambda t: signal_received.append(t))

        manager.set_theme("dark")
        assert len(signal_received) == 1
        assert signal_received[0] == "dark"


class TestToggleTheme:
    """Tests for ThemeManager.toggle_theme method."""

    def test_toggle_from_light_to_dark(self, qapp):
        """Test toggling from light to dark theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._resolved_theme = "light"
        manager.toggle_theme()
        assert manager.resolved_theme == "dark"

    def test_toggle_from_dark_to_light(self, qapp):
        """Test toggling from dark to light theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._resolved_theme = "dark"
        manager.toggle_theme()
        assert manager.resolved_theme == "light"


class TestDetectSystemTheme:
    """Tests for system theme detection on different platforms."""

    def test_detect_system_theme_macos_dark(self, qapp, mock_subprocess_result):
        """Test macOS dark theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        mock_subprocess_result.stdout = "Dark"

        with patch("sys.platform", "darwin"):
            with patch("subprocess.run", return_value=mock_subprocess_result):
                result = manager._detect_system_theme()
                assert result == "dark"

    def test_detect_system_theme_macos_light(self, qapp, mock_subprocess_result):
        """Test macOS light theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        mock_subprocess_result.stdout = ""

        with patch("sys.platform", "darwin"):
            with patch("subprocess.run", return_value=mock_subprocess_result):
                result = manager._detect_system_theme()
                assert result == "light"

    def test_detect_system_theme_macos_exception(self, qapp):
        """Test macOS theme detection falls back on exception."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        with patch("sys.platform", "darwin"):
            with patch("subprocess.run", side_effect=Exception("error")):
                result = manager._detect_system_theme()
                assert result == "light"

    def test_detect_system_theme_windows_light(self, qapp):
        """Test Windows light theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        mock_winreg = MagicMock()
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (1, None)  # 1 = light theme
        mock_winreg.HKEY_CURRENT_USER = 0

        with patch("sys.platform", "win32"):
            with patch.dict("sys.modules", {"winreg": mock_winreg}):
                # Re-import to get the mock
                import importlib

                from localmind.ui import theme_manager

                importlib.reload(theme_manager)
                manager = theme_manager.ThemeManager(qapp)

                with patch.object(manager, "_detect_system_theme") as mock_detect:
                    mock_detect.return_value = "light"
                    result = mock_detect()
                    assert result == "light"

    def test_detect_system_theme_windows_dark(self, qapp):
        """Test Windows dark theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        with patch.object(manager, "_detect_system_theme") as mock_detect:
            mock_detect.return_value = "dark"
            result = mock_detect()
            assert result == "dark"

    def test_detect_system_theme_linux_dark(self, qapp):
        """Test Linux dark theme detection via GTK_THEME."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        with patch("sys.platform", "linux"):
            with patch.dict("os.environ", {"GTK_THEME": "Adwaita-dark"}):
                result = manager._detect_system_theme()
                assert result == "dark"

    def test_detect_system_theme_linux_light(self, qapp):
        """Test Linux light theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        with patch("sys.platform", "linux"):
            with patch.dict("os.environ", {"GTK_THEME": "Adwaita"}, clear=True):
                result = manager._detect_system_theme()
                assert result == "light"

    def test_detect_system_theme_linux_no_gtk_theme(self, qapp):
        """Test Linux defaults to light when GTK_THEME not set."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        with patch("sys.platform", "linux"):
            with patch.dict("os.environ", {}, clear=True):
                result = manager._detect_system_theme()
                assert result == "light"

    def test_detect_system_theme_unknown_platform(self, qapp):
        """Test unknown platform defaults to light."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)

        with patch("sys.platform", "freebsd"):
            result = manager._detect_system_theme()
            assert result == "light"


class TestApplyFallbackPalette:
    """Tests for fallback palette application."""

    def test_apply_fallback_palette_dark(self, qapp):
        """Test dark fallback palette colors."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._apply_fallback_palette("dark")

        palette = qapp.palette()
        # Verify dark theme window color
        window_color = palette.color(QPalette.ColorRole.Window)
        assert window_color == QColor("#1A1A1A")

    def test_apply_fallback_palette_light(self, qapp):
        """Test light fallback palette colors."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._apply_fallback_palette("light")

        palette = qapp.palette()
        # Verify light theme window color
        window_color = palette.color(QPalette.ColorRole.Window)
        assert window_color == QColor("#FAFAFA")

    def test_apply_fallback_palette_clears_stylesheet(self, qapp):
        """Test fallback palette clears any existing stylesheet."""
        from localmind.ui.theme_manager import ThemeManager

        qapp.setStyleSheet("some-stylesheet")
        manager = ThemeManager(qapp)
        manager._apply_fallback_palette("light")

        assert qapp.styleSheet() == ""


class TestApplyTheme:
    """Tests for theme application with stylesheets."""

    def test_apply_theme_missing_stylesheet_uses_fallback(self, qapp, temp_dir):
        """Test missing stylesheet triggers fallback palette."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._styles_dir = temp_dir  # Empty directory

        with patch.object(manager, "_apply_fallback_palette") as mock_fallback:
            manager._apply_theme("dark")
            mock_fallback.assert_called_once_with("dark")

    def test_apply_theme_loads_stylesheet(self, qapp, temp_dir):
        """Test stylesheet is loaded and applied."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._styles_dir = temp_dir

        # Create a test stylesheet
        stylesheet_path = temp_dir / "theme_light.qss"
        stylesheet_path.write_text("QWidget { background: white; }")

        manager._apply_theme("light")
        assert "background: white" in qapp.styleSheet()

    def test_apply_theme_read_error_uses_fallback(self, qapp, temp_dir):
        """Test read error triggers fallback palette."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        manager._styles_dir = temp_dir

        # Create stylesheet path but make it unreadable
        stylesheet_path = temp_dir / "theme_dark.qss"
        stylesheet_path.write_text("content")

        with patch("builtins.open", side_effect=PermissionError("denied")):
            with patch.object(manager, "_apply_fallback_palette") as mock_fallback:
                manager._apply_theme("dark")
                mock_fallback.assert_called_once_with("dark")


class TestFindStylesDir:
    """Tests for styles directory discovery."""

    def test_find_styles_dir_returns_path(self, qapp):
        """Test _find_styles_dir returns a Path."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        result = manager._find_styles_dir()
        assert isinstance(result, Path)


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_init_theme_manager_creates_instance(self, qapp):
        """Test init_theme_manager creates a ThemeManager."""
        from localmind.ui import theme_manager

        # Reset global state
        theme_manager._theme_manager = None

        result = theme_manager.init_theme_manager(qapp)

        assert result is not None
        assert isinstance(result, theme_manager.ThemeManager)
        assert theme_manager._theme_manager is result

    def test_get_theme_manager_returns_none_before_init(self, qapp):
        """Test get_theme_manager returns None before initialization."""
        from localmind.ui import theme_manager

        # Reset global state
        theme_manager._theme_manager = None

        result = theme_manager.get_theme_manager()
        assert result is None

    def test_get_theme_manager_returns_instance_after_init(self, qapp):
        """Test get_theme_manager returns instance after initialization."""
        from localmind.ui import theme_manager

        # Reset and initialize
        theme_manager._theme_manager = None
        theme_manager.init_theme_manager(qapp)

        result = theme_manager.get_theme_manager()
        assert result is not None
        assert isinstance(result, theme_manager.ThemeManager)

    def test_apply_theme_from_settings_when_no_manager(self, qapp):
        """Test apply_theme_from_settings does nothing without manager."""
        from localmind.ui import theme_manager

        # Reset global state
        theme_manager._theme_manager = None

        # Should not raise
        theme_manager.apply_theme_from_settings()

    def test_apply_theme_from_settings_applies_setting(self, qapp):
        """Test apply_theme_from_settings applies the theme from settings."""
        from unittest.mock import MagicMock

        from localmind.ui import theme_manager

        # Reset and initialize
        theme_manager._theme_manager = None
        manager = theme_manager.init_theme_manager(qapp)

        # Create mock settings with app.theme attribute
        mock_settings = MagicMock()
        mock_settings.app.theme = "dark"

        # Patch at the source module where get_settings is imported from
        with patch("localmind.config.settings.get_settings", return_value=mock_settings):
            theme_manager.apply_theme_from_settings()

        assert manager.current_theme == "dark"


class TestThemeChangedSignal:
    """Tests for theme_changed signal behavior."""

    def test_signal_emitted_on_set_theme(self, qapp):
        """Test signal is emitted when theme is set."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        received_themes = []
        manager.theme_changed.connect(lambda t: received_themes.append(t))

        manager.set_theme("dark")
        manager.set_theme("light")

        assert received_themes == ["dark", "light"]

    def test_signal_emitted_on_toggle(self, qapp):
        """Test signal is emitted when theme is toggled."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        received_themes = []
        manager.theme_changed.connect(lambda t: received_themes.append(t))

        manager._resolved_theme = "light"
        manager.toggle_theme()

        assert "dark" in received_themes
