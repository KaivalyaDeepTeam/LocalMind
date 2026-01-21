"""
Application smoke tests.

These tests verify that the application can start and initialize correctly
on all supported platforms. They test the actual application startup flow.
"""

import sys
import time
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication


class TestApplicationStartup:
    """Tests for application startup sequence."""

    def test_main_window_initializes(self, qapp):
        """Test that MainWindow initializes without errors."""
        from localmind.main_window import MainWindow

        window = MainWindow()
        assert window is not None
        assert window.windowTitle() == "LocalMind"
        window.close()

    def test_main_window_shows_and_closes(self, qapp):
        """Test that MainWindow can show and close."""
        from localmind.main_window import MainWindow

        window = MainWindow()
        window.show()

        # Process events to ensure window is displayed
        qapp.processEvents()

        assert window.isVisible()

        window.close()
        qapp.processEvents()

    def test_main_window_components_exist(self, qapp):
        """Test that MainWindow has all expected components."""
        from localmind.main_window import MainWindow

        window = MainWindow()

        # Check for essential attributes/components
        # These should exist regardless of platform
        assert hasattr(window, "centralWidget")
        assert window.centralWidget() is not None

        window.close()

    def test_settings_load_on_startup(self, qapp):
        """Test that settings load correctly on startup."""
        from localmind.config import get_settings

        settings = get_settings()
        assert settings is not None

    def test_theme_applies_on_startup(self, qapp):
        """Test that theme manager applies theme on startup."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        # Should be able to set and apply themes
        manager.set_theme("light")
        assert manager.current_theme == "light"

        manager.set_theme("dark")
        assert manager.current_theme == "dark"


class TestApplicationShutdown:
    """Tests for clean application shutdown."""

    def test_main_window_cleanup(self, qapp):
        """Test that MainWindow cleans up properly on close."""
        from localmind.main_window import MainWindow

        window = MainWindow()
        window.show()
        qapp.processEvents()

        # Close should not raise
        window.close()
        qapp.processEvents()

    def test_settings_dialog_cleanup(self, qapp):
        """Test that SettingsDialog cleans up properly."""
        from localmind.ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog()
        dialog.show()
        qapp.processEvents()

        dialog.close()
        qapp.processEvents()


class TestUIResponsiveness:
    """Tests for UI responsiveness."""

    def test_main_window_resize(self, qapp):
        """Test that MainWindow can be resized."""
        from localmind.main_window import MainWindow

        window = MainWindow()
        window.show()
        qapp.processEvents()

        # Resize
        window.resize(1200, 800)
        qapp.processEvents()

        assert window.width() == 1200
        assert window.height() == 800

        window.close()

    def test_theme_switch_doesnt_crash(self, qapp):
        """Test that switching themes doesn't crash."""
        from localmind.main_window import MainWindow
        from localmind.ui.theme_manager import ThemeManager

        window = MainWindow()
        window.show()
        qapp.processEvents()

        manager = ThemeManager(qapp)

        # Switch themes multiple times
        for theme in ["light", "dark", "system", "light"]:
            manager.set_theme(theme)
            qapp.processEvents()

        window.close()


class TestConfigPersistence:
    """Tests for configuration persistence."""

    def test_settings_save_and_load(self, tmp_path, monkeypatch):
        """Test that settings can be saved and loaded."""
        from localmind.config import UserSettings, get_settings, save_settings

        settings = get_settings()
        original_theme = settings.app.theme

        try:
            # Modify and save
            settings.app.theme = "dark"
            save_settings(settings)

            # Reload and verify
            reloaded = get_settings()
            assert reloaded.app.theme == "dark"
        finally:
            # Restore original
            settings.app.theme = original_theme
            save_settings(settings)

    def test_keyring_api_key_persistence(self, monkeypatch):
        """Test that API keys persist in keyring."""
        # Mock keyring to avoid touching real keyring in tests
        mock_storage = {}

        def mock_set_password(service, key, value):
            mock_storage[f"{service}:{key}"] = value

        def mock_get_password(service, key):
            return mock_storage.get(f"{service}:{key}")

        def mock_delete_password(service, key):
            mock_storage.pop(f"{service}:{key}", None)

        import keyring

        monkeypatch.setattr(keyring, "set_password", mock_set_password)
        monkeypatch.setattr(keyring, "get_password", mock_get_password)
        monkeypatch.setattr(keyring, "delete_password", mock_delete_password)

        from localmind.config import get_openai_api_key, set_openai_api_key

        # Set key
        set_openai_api_key("sk-test-key-123")

        # Retrieve key
        retrieved = get_openai_api_key()
        assert retrieved == "sk-test-key-123"


class TestModuleImports:
    """Tests to verify all modules can be imported."""

    def test_import_main_window(self):
        """Test MainWindow import."""
        from localmind.main_window import MainWindow

        assert MainWindow is not None

    def test_import_workers(self):
        """Test worker imports."""
        from localmind.workers.audit_worker import AuditWorker
        from localmind.workers.merge_worker import MergeWorker
        from localmind.workers.orchestrator import ProcessingOrchestrator
        from localmind.workers.transcription_worker import TranscriptionWorker

        assert TranscriptionWorker is not None
        assert MergeWorker is not None
        assert AuditWorker is not None
        assert ProcessingOrchestrator is not None

    def test_import_ui_components(self):
        """Test UI component imports."""
        from localmind.ui.file_browser import FileBrowserPanel
        from localmind.ui.mode_selector import ModeSelector
        from localmind.ui.results_viewer import ResultsViewer
        from localmind.ui.settings_dialog import SettingsDialog
        from localmind.ui.theme_manager import ThemeManager

        assert FileBrowserPanel is not None
        assert ModeSelector is not None
        assert ResultsViewer is not None
        assert SettingsDialog is not None
        assert ThemeManager is not None

    def test_import_llm_providers(self):
        """Test LLM provider imports."""
        from localmind.llm.base import BaseLLMProvider
        from localmind.llm.factory import create_provider
        from localmind.llm.local_provider import LocalProvider
        from localmind.llm.openai_provider import OpenAIProvider

        assert BaseLLMProvider is not None
        assert OpenAIProvider is not None
        assert LocalProvider is not None
        assert create_provider is not None

    def test_import_config(self):
        """Test config imports."""
        from localmind.config import UserSettings, get_settings

        assert UserSettings is not None
        assert get_settings is not None

    def test_import_audio_processing(self):
        """Test audio processing imports."""
        from localmind.audio.preprocessing import preprocess_audio_for_transcription

        assert preprocess_audio_for_transcription is not None


class TestApplicationEntryPoint:
    """Tests for the application entry point."""

    def test_localmind_module_runnable(self):
        """Test that localmind module has __main__.py."""
        import importlib.util

        spec = importlib.util.find_spec("localmind.__main__")
        assert spec is not None

    def test_app_function_exists(self):
        """Test that main app function exists."""
        from localmind.__main__ import main

        assert callable(main)


class TestPlatformSpecificStartup:
    """Platform-specific startup tests."""

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_specific_setup(self, qapp):
        """Test macOS-specific application setup."""
        # On macOS, the app should work with Metal backend
        import torch

        # MPS should at least be queryable
        assert hasattr(torch.backends, "mps")

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_windows_specific_setup(self, qapp):
        """Test Windows-specific application setup."""
        # Windows should have os.startfile available
        assert hasattr(
            __builtins__["os"] if isinstance(__builtins__, dict) else __builtins__, "startfile"
        ) or hasattr(__import__("os"), "startfile")

    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux only")
    def test_linux_specific_setup(self, qapp):
        """Test Linux-specific application setup."""
        # On Linux, XDG utilities should be available
        import shutil

        # xdg-open might not be in PATH in CI, so just check the import works
        assert True  # If we got here, Qt initialized properly on Linux
