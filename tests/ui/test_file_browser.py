"""
Tests for File Browser module.

Tests the file browser components including utility functions,
drop zone, file card, and file browser panel.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGetFileSizeStr:
    """Tests for get_file_size_str utility function."""

    def test_file_size_bytes(self, temp_dir):
        """Test file size display for bytes."""
        from localmind.ui.file_browser import get_file_size_str

        # Create a small file
        filepath = temp_dir / "small.txt"
        filepath.write_bytes(b"x" * 500)

        result = get_file_size_str(str(filepath))
        assert result == "500 B"

    def test_file_size_kilobytes(self, temp_dir):
        """Test file size display for kilobytes."""
        from localmind.ui.file_browser import get_file_size_str

        # Create a ~2KB file
        filepath = temp_dir / "kb.txt"
        filepath.write_bytes(b"x" * 2048)

        result = get_file_size_str(str(filepath))
        assert result == "2.0 KB"

    def test_file_size_megabytes(self, temp_dir):
        """Test file size display for megabytes."""
        from localmind.ui.file_browser import get_file_size_str

        # Create a ~1.5MB file
        filepath = temp_dir / "mb.txt"
        filepath.write_bytes(b"x" * (1024 * 1024 + 512 * 1024))

        result = get_file_size_str(str(filepath))
        assert result == "1.5 MB"

    def test_file_size_gigabytes(self):
        """Test file size display for gigabytes (mocked)."""
        from localmind.ui.file_browser import get_file_size_str

        # Mock os.path.getsize to return 2.5GB
        with patch("os.path.getsize", return_value=int(2.5 * 1024 * 1024 * 1024)):
            result = get_file_size_str("/fake/path")
            assert result == "2.5 GB"

    def test_file_size_zero_bytes(self, temp_dir):
        """Test file size display for empty file."""
        from localmind.ui.file_browser import get_file_size_str

        filepath = temp_dir / "empty.txt"
        filepath.touch()

        result = get_file_size_str(str(filepath))
        assert result == "0 B"

    def test_file_size_exactly_1kb(self):
        """Test file size at exactly 1KB boundary."""
        from localmind.ui.file_browser import get_file_size_str

        with patch("os.path.getsize", return_value=1024):
            result = get_file_size_str("/fake/path")
            assert result == "1.0 KB"

    def test_file_size_exactly_1mb(self):
        """Test file size at exactly 1MB boundary."""
        from localmind.ui.file_browser import get_file_size_str

        with patch("os.path.getsize", return_value=1024 * 1024):
            result = get_file_size_str("/fake/path")
            assert result == "1.0 MB"

    def test_file_size_exactly_1gb(self):
        """Test file size at exactly 1GB boundary."""
        from localmind.ui.file_browser import get_file_size_str

        with patch("os.path.getsize", return_value=1024 * 1024 * 1024):
            result = get_file_size_str("/fake/path")
            assert result == "1.0 GB"

    def test_file_size_nonexistent_file(self):
        """Test file size for nonexistent file returns empty string."""
        from localmind.ui.file_browser import get_file_size_str

        result = get_file_size_str("/nonexistent/path/file.txt")
        assert result == ""

    def test_file_size_exception_returns_empty(self):
        """Test exception handling returns empty string."""
        from localmind.ui.file_browser import get_file_size_str

        with patch("os.path.getsize", side_effect=PermissionError("denied")):
            result = get_file_size_str("/fake/path")
            assert result == ""


class TestDropZoneAudioExtensions:
    """Tests for DropZoneWidget audio extensions."""

    def test_audio_extensions_contains_wav(self, qapp):
        """Test AUDIO_EXTENSIONS contains .wav."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".wav" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_mp3(self, qapp):
        """Test AUDIO_EXTENSIONS contains .mp3."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".mp3" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_m4a(self, qapp):
        """Test AUDIO_EXTENSIONS contains .m4a."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".m4a" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_ogg(self, qapp):
        """Test AUDIO_EXTENSIONS contains .ogg."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".ogg" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_flac(self, qapp):
        """Test AUDIO_EXTENSIONS contains .flac."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".flac" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_webm(self, qapp):
        """Test AUDIO_EXTENSIONS contains .webm."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".webm" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_aac(self, qapp):
        """Test AUDIO_EXTENSIONS contains .aac."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".aac" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_wma(self, qapp):
        """Test AUDIO_EXTENSIONS contains .wma."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".wma" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_contains_opus(self, qapp):
        """Test AUDIO_EXTENSIONS contains .opus."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".opus" in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_does_not_contain_txt(self, qapp):
        """Test AUDIO_EXTENSIONS does not contain .txt."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".txt" not in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_does_not_contain_pdf(self, qapp):
        """Test AUDIO_EXTENSIONS does not contain .pdf."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert ".pdf" not in widget.AUDIO_EXTENSIONS

    def test_audio_extensions_is_set(self, qapp):
        """Test AUDIO_EXTENSIONS is a set for O(1) lookup."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert isinstance(widget.AUDIO_EXTENSIONS, set)


class TestDropZoneWidget:
    """Tests for DropZoneWidget initialization and behavior."""

    def test_drop_zone_accepts_drops(self, qapp):
        """Test drop zone accepts drops."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert widget.acceptDrops() is True

    def test_drop_zone_object_name(self, qapp):
        """Test drop zone has correct object name."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert widget.objectName() == "dropZoneEmpty"

    def test_drop_zone_minimum_height(self, qapp):
        """Test drop zone has minimum height set."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        assert widget.minimumHeight() == 280

    def test_drop_zone_browse_clicked_signal(self, qapp):
        """Test browse_clicked signal is emitted on mouse press."""
        from localmind.ui.file_browser import DropZoneWidget

        widget = DropZoneWidget()
        signal_received = []
        widget.browse_clicked.connect(lambda: signal_received.append(True))

        # Simulate mouse press
        from PySide6.QtCore import QEvent, QPoint
        from PySide6.QtGui import QMouseEvent

        event = MagicMock()
        widget.mousePressEvent(event)

        assert len(signal_received) == 1


class TestFileCardWidget:
    """Tests for FileCardWidget."""

    def test_file_card_initial_state(self, qapp):
        """Test file card initializes with no file."""
        from localmind.ui.file_browser import FileCardWidget

        widget = FileCardWidget()
        assert widget.get_file() is None

    def test_file_card_object_name(self, qapp):
        """Test file card has correct object name."""
        from localmind.ui.file_browser import FileCardWidget

        widget = FileCardWidget()
        assert widget.objectName() == "fileCard"

    def test_file_card_set_file(self, qapp, temp_dir):
        """Test setting a file on the card."""
        from localmind.ui.file_browser import FileCardWidget

        # Create test file
        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        widget = FileCardWidget()
        widget.set_file(str(filepath))

        assert widget.get_file() == str(filepath)

    def test_file_card_displays_filename(self, qapp, temp_dir):
        """Test file card displays the filename."""
        from localmind.ui.file_browser import FileCardWidget

        filepath = temp_dir / "my_audio.mp3"
        filepath.write_bytes(b"x" * 1024)

        widget = FileCardWidget()
        widget.set_file(str(filepath))

        assert widget._filename_label.text() == "my_audio.mp3"

    def test_file_card_displays_extension(self, qapp, temp_dir):
        """Test file card displays file extension."""
        from localmind.ui.file_browser import FileCardWidget

        filepath = temp_dir / "audio.flac"
        filepath.write_bytes(b"x" * 1024)

        widget = FileCardWidget()
        widget.set_file(str(filepath))

        assert "FLAC" in widget._file_info_label.text()

    def test_file_card_process_signal(self, qapp):
        """Test process_clicked signal can be connected."""
        from localmind.ui.file_browser import FileCardWidget

        widget = FileCardWidget()
        signal_received = []
        widget.process_clicked.connect(lambda: signal_received.append(True))

        # Signal should be connectable
        widget.process_clicked.emit()
        assert len(signal_received) == 1

    def test_file_card_change_file_signal(self, qapp):
        """Test change_file_clicked signal can be connected."""
        from localmind.ui.file_browser import FileCardWidget

        widget = FileCardWidget()
        signal_received = []
        widget.change_file_clicked.connect(lambda: signal_received.append(True))

        widget.change_file_clicked.emit()
        assert len(signal_received) == 1


class TestFileBrowserPanel:
    """Tests for FileBrowserPanel."""

    def test_browser_panel_initial_state(self, qapp):
        """Test browser panel initializes with no file."""
        from localmind.ui.file_browser import FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            panel = FileBrowserPanel()

            assert panel.get_selected_file() is None

    def test_browser_panel_audio_extensions_match(self, qapp):
        """Test panel AUDIO_EXTENSIONS matches drop zone."""
        from localmind.ui.file_browser import DropZoneWidget, FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            panel = FileBrowserPanel()
            drop_zone = DropZoneWidget()

            assert panel.AUDIO_EXTENSIONS == drop_zone.AUDIO_EXTENSIONS

    def test_browser_panel_select_file(self, qapp, temp_dir):
        """Test programmatic file selection."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()
                panel.select_file(str(filepath))

                assert panel.get_selected_file() == str(filepath)

    def test_browser_panel_file_selected_signal(self, qapp, temp_dir):
        """Test file_selected signal is emitted."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()

                received_files = []
                panel.file_selected.connect(lambda f: received_files.append(f))

                panel.select_file(str(filepath))

                assert len(received_files) == 1
                assert received_files[0] == str(filepath)

    def test_browser_panel_reset(self, qapp, temp_dir):
        """Test reset clears selected file."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()
                panel.select_file(str(filepath))

                assert panel.get_selected_file() is not None

                panel.reset()

                assert panel.get_selected_file() is None

    def test_browser_panel_stack_index_changes(self, qapp, temp_dir):
        """Test stack index changes when file is selected."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()

                # Initially at drop zone (index 0)
                assert panel._stack.currentIndex() == 0

                panel.select_file(str(filepath))

                # After selection, at file card (index 1)
                assert panel._stack.currentIndex() == 1

    def test_browser_panel_reset_returns_to_drop_zone(self, qapp, temp_dir):
        """Test reset returns to drop zone state."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()
                panel.select_file(str(filepath))
                panel.reset()

                assert panel._stack.currentIndex() == 0


class TestFileBrowserRecentFiles:
    """Tests for recent files functionality."""

    def test_add_to_recent_limits_to_five(self, qapp, temp_dir):
        """Test recent files list is limited to 5 items."""
        from localmind.ui.file_browser import FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()

                # Add 7 files
                for i in range(7):
                    filepath = temp_dir / f"test{i}.wav"
                    filepath.write_bytes(b"x" * 1024)
                    panel.select_file(str(filepath))

                assert len(panel._recent_files) == 5

    def test_add_to_recent_moves_existing_to_front(self, qapp, temp_dir):
        """Test selecting existing file moves it to front."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath1 = temp_dir / "test1.wav"
        filepath1.write_bytes(b"x" * 1024)
        filepath2 = temp_dir / "test2.wav"
        filepath2.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            with patch("localmind.ui.file_browser.save_settings"):
                panel = FileBrowserPanel()

                panel.select_file(str(filepath1))
                panel.select_file(str(filepath2))
                panel.select_file(str(filepath1))

                assert panel._recent_files[0] == str(filepath1)

    def test_load_recent_files_from_settings(self, qapp, temp_dir):
        """Test loading recent files from settings."""
        from localmind.ui.file_browser import FileBrowserPanel

        filepath = temp_dir / "test.wav"
        filepath.write_bytes(b"x" * 1024)

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = [str(filepath)]
            panel = FileBrowserPanel()

            assert str(filepath) in panel._recent_files


class TestFileBrowserValidation:
    """Tests for file validation in the browser."""

    def test_valid_wav_extension_in_panel(self, qapp):
        """Test .wav is valid in panel."""
        from localmind.ui.file_browser import FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            panel = FileBrowserPanel()

            assert ".wav" in panel.AUDIO_EXTENSIONS

    def test_valid_mp3_extension_in_panel(self, qapp):
        """Test .mp3 is valid in panel."""
        from localmind.ui.file_browser import FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            panel = FileBrowserPanel()

            assert ".mp3" in panel.AUDIO_EXTENSIONS

    def test_invalid_extension_not_in_panel(self, qapp):
        """Test .exe is invalid in panel."""
        from localmind.ui.file_browser import FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            panel = FileBrowserPanel()

            assert ".exe" not in panel.AUDIO_EXTENSIONS

    def test_all_extensions_are_lowercase(self, qapp):
        """Test all extensions are lowercase."""
        from localmind.ui.file_browser import FileBrowserPanel

        with patch("localmind.ui.file_browser.get_settings") as mock_settings:
            mock_settings.return_value.app.recent_files = []
            panel = FileBrowserPanel()

            for ext in panel.AUDIO_EXTENSIONS:
                assert ext == ext.lower()
                assert ext.startswith(".")
