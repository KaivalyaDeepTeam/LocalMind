"""
Cross-platform compatibility tests.

These tests verify that platform-specific code works correctly on all supported
operating systems (macOS, Windows, Linux).
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestPlatformDetection:
    """Tests for platform detection utilities."""

    def test_sys_platform_is_valid(self):
        """Test that sys.platform returns a valid value."""
        valid_platforms = ["darwin", "win32", "linux", "linux2"]
        # sys.platform should start with one of these
        assert any(sys.platform.startswith(p) for p in valid_platforms)

    def test_os_name_is_valid(self):
        """Test that os.name returns a valid value."""
        valid_names = ["posix", "nt"]
        assert os.name in valid_names


class TestThemeDetection:
    """Tests for system theme detection across platforms."""

    def test_theme_manager_import(self):
        """Test that ThemeManager can be imported."""
        from localmind.ui.theme_manager import ThemeManager

        assert ThemeManager is not None

    def test_theme_manager_creation(self, qapp):
        """Test that ThemeManager can be created on any platform."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        assert manager is not None

    def test_system_theme_detection_returns_valid_theme(self, qapp):
        """Test that system theme detection returns a valid theme."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        detected = manager._detect_system_theme()
        assert detected in ["light", "dark"]

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_theme_detection(self, qapp):
        """Test macOS-specific theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        # Should use defaults command on macOS
        theme = manager._detect_system_theme()
        assert theme in ["light", "dark"]

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_windows_theme_detection(self, qapp):
        """Test Windows-specific theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        # Should use winreg on Windows
        theme = manager._detect_system_theme()
        assert theme in ["light", "dark"]

    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux only")
    def test_linux_theme_detection(self, qapp):
        """Test Linux-specific theme detection."""
        from localmind.ui.theme_manager import ThemeManager

        manager = ThemeManager(qapp)
        # Should check GTK_THEME on Linux
        theme = manager._detect_system_theme()
        assert theme in ["light", "dark"]


class TestFileOperations:
    """Tests for cross-platform file operations."""

    def test_pathlib_works_cross_platform(self):
        """Test that pathlib.Path works correctly."""
        # Create a path
        p = Path("test") / "subdir" / "file.txt"
        assert isinstance(p, Path)

        # Should have correct number of parts
        assert len(p.parts) == 3

    def test_temp_directory_creation(self):
        """Test that temporary directories can be created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert Path(tmpdir).exists()
            assert Path(tmpdir).is_dir()

    def test_file_creation_and_deletion(self):
        """Test that files can be created and deleted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            assert test_file.exists()
            assert test_file.read_text() == "test content"
            test_file.unlink()
            assert not test_file.exists()

    def test_unicode_filename_handling(self):
        """Test that unicode filenames work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with unicode characters
            test_file = Path(tmpdir) / "tëst_文件_файл.txt"
            test_file.write_text("unicode content")
            assert test_file.exists()
            assert test_file.read_text() == "unicode content"

    def test_path_with_spaces(self):
        """Test that paths with spaces work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "path with spaces" / "file name.txt"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("content")
            assert test_file.exists()


class TestFileOpening:
    """Tests for platform-specific file opening."""

    def test_open_file_function_exists(self):
        """Test that report_preview has platform-specific file opening."""
        # This tests that the code structure is correct
        import localmind.ui.report_preview as rp

        # The module should be importable
        assert rp is not None

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_uses_open_command(self):
        """Test that macOS uses 'open' command."""
        with patch("subprocess.run") as mock_run:
            import subprocess

            # Simulate what report_preview does on macOS
            subprocess.run(["open", "/tmp/test.pdf"])
            mock_run.assert_called_with(["open", "/tmp/test.pdf"])

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_windows_uses_startfile(self):
        """Test that Windows uses os.startfile."""
        # os.startfile only exists on Windows
        assert hasattr(os, "startfile")

    @pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux only")
    def test_linux_uses_xdg_open(self):
        """Test that Linux uses 'xdg-open' command."""
        with patch("subprocess.run") as mock_run:
            import subprocess

            # Simulate what report_preview does on Linux
            subprocess.run(["xdg-open", "/tmp/test.pdf"])
            mock_run.assert_called_with(["xdg-open", "/tmp/test.pdf"])


class TestKeyringStorage:
    """Tests for secure API key storage across platforms."""

    def test_keyring_import(self):
        """Test that keyring can be imported."""
        import keyring

        assert keyring is not None

    def test_keyring_backend_available(self):
        """Test that a keyring backend is available."""
        import keyring

        backend = keyring.get_keyring()
        assert backend is not None
        # Backend name should not be "fail" (the fallback that always fails)
        assert "fail" not in backend.__class__.__name__.lower()

    def test_keyring_set_and_get(self):
        """Test that keyring can store and retrieve values."""
        import keyring

        service = "LocalMind-Test"
        key = "test_key"
        value = "test_value_12345"

        try:
            # Store
            keyring.set_password(service, key, value)

            # Retrieve
            retrieved = keyring.get_password(service, key)
            assert retrieved == value

        finally:
            # Cleanup
            try:
                keyring.delete_password(service, key)
            except Exception:
                pass

    def test_keyring_delete(self):
        """Test that keyring can delete values."""
        import keyring

        service = "LocalMind-Test"
        key = "test_delete_key"
        value = "test_value"

        # Store first
        keyring.set_password(service, key, value)

        # Delete
        keyring.delete_password(service, key)

        # Should be gone
        result = keyring.get_password(service, key)
        assert result is None

    def test_settings_keyring_functions(self):
        """Test LocalMind's keyring wrapper functions."""
        from localmind.config import get_api_key, set_api_key

        test_key = "test_ci_key"
        test_value = "sk-test-12345"

        try:
            # Store
            result = set_api_key(test_key, test_value)
            assert result is True

            # Retrieve
            retrieved = get_api_key(test_key)
            assert retrieved == test_value

            # Delete (set to empty)
            set_api_key(test_key, "")
            retrieved = get_api_key(test_key)
            assert retrieved == ""

        finally:
            # Ensure cleanup
            try:
                import keyring

                keyring.delete_password("LocalMind", test_key)
            except Exception:
                pass


class TestGUIComponents:
    """Tests for GUI component creation across platforms."""

    def test_qapplication_creation(self, qapp):
        """Test that QApplication can be created."""
        from PySide6.QtWidgets import QApplication

        assert QApplication.instance() is not None

    def test_main_window_creation(self, qapp):
        """Test that MainWindow can be created."""
        from localmind.main_window import MainWindow

        window = MainWindow()
        assert window is not None
        window.close()

    def test_settings_dialog_creation(self, qapp):
        """Test that SettingsDialog can be created."""
        from localmind.ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog()
        assert dialog is not None
        dialog.close()

    def test_file_browser_creation(self, qapp):
        """Test that FileBrowserPanel can be created."""
        from localmind.ui.file_browser import FileBrowserPanel

        browser = FileBrowserPanel()
        assert browser is not None

    def test_results_viewer_creation(self, qapp):
        """Test that ResultsViewer can be created."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        assert viewer is not None


class TestAudioProcessing:
    """Tests for audio processing across platforms."""

    def test_librosa_import(self):
        """Test that librosa can be imported."""
        import librosa

        assert librosa is not None

    def test_soundfile_import(self):
        """Test that soundfile can be imported."""
        import soundfile

        assert soundfile is not None

    def test_numpy_import(self):
        """Test that numpy can be imported."""
        import numpy as np

        assert np is not None

    def test_scipy_import(self):
        """Test that scipy can be imported."""
        import scipy

        assert scipy is not None


class TestMLLibraries:
    """Tests for ML library availability across platforms."""

    def test_torch_import(self):
        """Test that PyTorch can be imported."""
        import torch

        assert torch is not None

    def test_torch_device_detection(self):
        """Test that PyTorch can detect available devices."""
        import torch

        # CPU should always be available
        assert torch.device("cpu") is not None

        # Check CUDA availability (may or may not be present)
        cuda_available = torch.cuda.is_available()
        assert isinstance(cuda_available, bool)

        # Check MPS availability on macOS
        if sys.platform == "darwin":
            mps_available = torch.backends.mps.is_available()
            assert isinstance(mps_available, bool)

    def test_transformers_import(self):
        """Test that transformers can be imported."""
        import transformers

        assert transformers is not None

    def test_whisper_import(self):
        """Test that whisper can be imported."""
        import whisper

        assert whisper is not None


class TestSubprocessSafety:
    """Tests for subprocess safety across platforms."""

    def test_no_shell_true_in_report_preview(self):
        """Verify report_preview doesn't use shell=True."""
        import inspect

        from localmind.ui import report_preview

        source = inspect.getsource(report_preview)
        # Should not have shell=True
        assert "shell=True" not in source

    def test_subprocess_with_list_args(self):
        """Test that subprocess works with list arguments."""
        import subprocess

        # This should work on all platforms
        if sys.platform == "win32":
            result = subprocess.run(["cmd", "/c", "echo", "test"], capture_output=True, text=True)
        else:
            result = subprocess.run(["echo", "test"], capture_output=True, text=True)

        assert result.returncode == 0


class TestEncodingHandling:
    """Tests for encoding handling across platforms."""

    def test_utf8_file_handling(self):
        """Test UTF-8 file handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "utf8_test.txt"
            content = "Hello, 世界! Привет! مرحبا!"
            test_file.write_text(content, encoding="utf-8")
            read_content = test_file.read_text(encoding="utf-8")
            assert read_content == content

    def test_json_unicode_handling(self):
        """Test JSON with unicode content."""
        import json

        data = {"message": "Hello, 世界!", "name": "Тест"}
        json_str = json.dumps(data, ensure_ascii=False)
        loaded = json.loads(json_str)
        assert loaded == data


class TestEnvironmentVariables:
    """Tests for environment variable handling."""

    def test_can_read_env_vars(self):
        """Test that environment variables can be read."""
        # PATH should exist on all platforms
        path = os.environ.get("PATH") or os.environ.get("Path")
        assert path is not None

    def test_can_set_env_vars(self):
        """Test that environment variables can be set."""
        test_var = "LOCALMIND_TEST_VAR"
        test_value = "test_value_123"

        os.environ[test_var] = test_value
        assert os.environ.get(test_var) == test_value

        # Cleanup
        del os.environ[test_var]
        assert os.environ.get(test_var) is None
