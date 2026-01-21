"""
Tests for ProcessingOrchestrator.

Tests the pipeline coordination: transcription -> merge -> audit.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from localmind.workers.orchestrator import ProcessingOrchestrator, ProcessingResult


class TestProcessingResult:
    """Tests for ProcessingResult dataclass."""

    def test_processing_result_defaults(self):
        """Test default values."""
        result = ProcessingResult()
        assert result.transcription is None
        assert result.merge is None
        assert result.audit is None
        assert result.error is None

    def test_processing_result_to_dict_empty(self):
        """Test to_dict with no data."""
        result = ProcessingResult()
        d = result.to_dict()
        assert d == {}

    def test_processing_result_to_dict_with_error(self):
        """Test to_dict with error."""
        result = ProcessingResult(error="Test error")
        d = result.to_dict()
        assert d["error"] == "Test error"

    def test_processing_result_to_dict_with_transcription(self):
        """Test to_dict includes transcription."""
        from localmind.workers.transcription_worker import TranscriptionResult

        transcription = TranscriptionResult(text="Test text")
        result = ProcessingResult(transcription=transcription)
        d = result.to_dict()

        assert "transcription" in d
        assert d["transcription"]["text"] == "Test text"


class TestProcessingOrchestratorInit:
    """Tests for ProcessingOrchestrator initialization."""

    def test_orchestrator_initialization(self, qapp):
        """Test orchestrator initializes with correct defaults."""
        orchestrator = ProcessingOrchestrator()

        assert orchestrator._audio_path is None
        assert orchestrator._is_processing is False
        assert orchestrator._should_stop is False
        assert orchestrator._whisper_model == "large-v3"
        assert orchestrator._language is None
        assert orchestrator._use_gpu is True
        assert orchestrator._dual_channel is True
        assert orchestrator._use_hindi_stt is False
        assert orchestrator._hindi_model_variant == "apex"
        assert orchestrator._use_preprocessing is True
        assert orchestrator._transcription_only is False

    def test_orchestrator_is_processing_property(self, qapp):
        """Test is_processing property."""
        orchestrator = ProcessingOrchestrator()
        assert orchestrator.is_processing is False

        orchestrator._is_processing = True
        assert orchestrator.is_processing is True


class TestProcessingOrchestratorConfigure:
    """Tests for ProcessingOrchestrator.configure() method."""

    def test_configure_all_parameters(self, qapp):
        """Test configure sets all parameters."""
        orchestrator = ProcessingOrchestrator()

        orchestrator.configure(
            whisper_model="medium",
            language="en",
            use_gpu=False,
            dual_channel=False,
            use_hindi_stt=True,
            hindi_model_variant="prime",
            use_preprocessing=False,
            scoring_parameters=[{"name": "test"}],
            transcription_only=True,
        )

        assert orchestrator._whisper_model == "medium"
        assert orchestrator._language == "en"
        assert orchestrator._use_gpu is False
        assert orchestrator._dual_channel is False
        assert orchestrator._use_hindi_stt is True
        assert orchestrator._hindi_model_variant == "prime"
        assert orchestrator._use_preprocessing is False
        assert orchestrator._parameters == [{"name": "test"}]
        assert orchestrator._transcription_only is True

    def test_configure_partial_parameters(self, qapp):
        """Test configure with partial parameters."""
        orchestrator = ProcessingOrchestrator()
        orchestrator.configure(language="hi")

        assert orchestrator._language == "hi"
        # Defaults should remain
        assert orchestrator._whisper_model == "large-v3"
        assert orchestrator._use_gpu is True


class TestProcessingOrchestratorStart:
    """Tests for ProcessingOrchestrator.start() method."""

    def test_start_file_not_found(self, qapp):
        """Test start with non-existent file."""
        orchestrator = ProcessingOrchestrator()
        error_emitted = []
        orchestrator.processing_error.connect(lambda e: error_emitted.append(e))

        orchestrator.start("/non/existent/file.wav")

        assert len(error_emitted) == 1
        assert "File not found" in error_emitted[0]
        assert orchestrator._is_processing is False

    def test_start_already_processing(self, qapp, temp_dir):
        """Test start ignores when already processing."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator._is_processing = True

        # Should return without doing anything
        orchestrator.start(str(audio_file))

        # Still in same state
        assert orchestrator._is_processing is True
        assert orchestrator._audio_path is None  # Not updated

    def test_start_sets_audio_path(self, qapp, temp_dir):
        """Test start sets audio path correctly."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()

        with patch.object(orchestrator, "_start_transcription"):
            orchestrator.start(str(audio_file))

        assert orchestrator._audio_path == audio_file
        assert orchestrator._is_processing is True
        assert orchestrator._should_stop is False


class TestProcessingOrchestratorStop:
    """Tests for ProcessingOrchestrator.stop() method."""

    def test_stop_sets_flags(self, qapp):
        """Test stop sets correct flags."""
        orchestrator = ProcessingOrchestrator()
        orchestrator._is_processing = True
        orchestrator._should_stop = False

        orchestrator.stop()

        assert orchestrator._should_stop is True
        assert orchestrator._is_processing is False

    def test_stop_with_running_workers(self, qapp):
        """Test stop calls stop on all running workers."""
        orchestrator = ProcessingOrchestrator()

        # Create mock workers
        mock_transcription = MagicMock()
        mock_transcription.isRunning.return_value = True
        mock_merge = MagicMock()
        mock_merge.isRunning.return_value = True
        mock_audit = MagicMock()
        mock_audit.isRunning.return_value = True

        orchestrator._transcription_worker = mock_transcription
        orchestrator._merge_worker = mock_merge
        orchestrator._audit_worker = mock_audit
        orchestrator._is_processing = True

        orchestrator.stop()

        mock_transcription.stop.assert_called_once()
        mock_transcription.wait.assert_called_once()
        mock_merge.stop.assert_called_once()
        mock_merge.wait.assert_called_once()
        mock_audit.stop.assert_called_once()
        mock_audit.wait.assert_called_once()

    def test_stop_with_no_workers(self, qapp):
        """Test stop works when no workers exist."""
        orchestrator = ProcessingOrchestrator()
        orchestrator._is_processing = True

        # Should not raise
        orchestrator.stop()
        assert orchestrator._is_processing is False


class TestProcessingOrchestratorStereoDetection:
    """Tests for stereo audio detection."""

    def test_check_if_stereo_mono(self, qapp, temp_dir):
        """Test stereo detection with mono audio."""
        import numpy as np

        audio_file = temp_dir / "mono.wav"

        # Create mock mono audio
        with patch("librosa.load") as mock_load:
            mock_load.return_value = (np.zeros(16000), 16000)  # 1D array = mono

            orchestrator = ProcessingOrchestrator()
            result = orchestrator._check_if_stereo(audio_file)

            assert result is False

    def test_check_if_stereo_stereo(self, qapp, temp_dir):
        """Test stereo detection with stereo audio."""
        import numpy as np

        audio_file = temp_dir / "stereo.wav"

        # Create mock stereo audio
        with patch("librosa.load") as mock_load:
            mock_load.return_value = (np.zeros((2, 16000)), 16000)  # 2D array = stereo

            orchestrator = ProcessingOrchestrator()
            result = orchestrator._check_if_stereo(audio_file)

            assert result is True

    def test_check_if_stereo_error_fallback(self, qapp, temp_dir):
        """Test stereo detection falls back to mono on error."""
        audio_file = temp_dir / "bad.wav"

        with patch("librosa.load", side_effect=Exception("Load failed")):
            orchestrator = ProcessingOrchestrator()
            result = orchestrator._check_if_stereo(audio_file)

            # Should return False (mono) on error
            assert result is False


class TestProcessingOrchestratorWorkerSelection:
    """Tests for worker selection logic."""

    def test_whisper_mono_worker_selection(self, qapp, temp_dir):
        """Test Whisper mono worker is selected for mono audio."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator.configure(use_hindi_stt=False, dual_channel=True)
        orchestrator._audio_path = audio_file

        with patch.object(orchestrator, "_check_if_stereo", return_value=False):
            with patch("localmind.workers.orchestrator.TranscriptionWorker") as mock_worker:
                mock_instance = MagicMock()
                mock_worker.return_value = mock_instance

                orchestrator._start_transcription()

                mock_worker.assert_called_once()
                assert "model_name" in str(mock_worker.call_args)

    def test_whisper_stereo_worker_selection(self, qapp, temp_dir):
        """Test DualChannel Whisper worker is selected for stereo audio."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator.configure(use_hindi_stt=False, dual_channel=True)
        orchestrator._audio_path = audio_file

        with patch.object(orchestrator, "_check_if_stereo", return_value=True):
            with patch(
                "localmind.workers.orchestrator.DualChannelTranscriptionWorker"
            ) as mock_worker:
                mock_instance = MagicMock()
                mock_worker.return_value = mock_instance

                orchestrator._start_transcription()

                mock_worker.assert_called_once()

    def test_hindi_stt_mono_worker_selection(self, qapp, temp_dir):
        """Test HindiSTT mono worker is selected."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator.configure(use_hindi_stt=True, dual_channel=True)
        orchestrator._audio_path = audio_file

        with patch.object(orchestrator, "_check_if_stereo", return_value=False):
            with patch("localmind.workers.orchestrator.HindiSTTWorker") as mock_worker:
                mock_instance = MagicMock()
                mock_worker.return_value = mock_instance

                orchestrator._start_transcription()

                mock_worker.assert_called_once()
                # Check num_speakers is passed
                call_kwargs = mock_worker.call_args[1]
                assert call_kwargs.get("num_speakers") == 2

    def test_hindi_stt_stereo_worker_selection(self, qapp, temp_dir):
        """Test DualChannel HindiSTT worker is selected for stereo."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator.configure(use_hindi_stt=True, dual_channel=True)
        orchestrator._audio_path = audio_file

        with patch.object(orchestrator, "_check_if_stereo", return_value=True):
            with patch("localmind.workers.orchestrator.DualChannelHindiSTTWorker") as mock_worker:
                mock_instance = MagicMock()
                mock_worker.return_value = mock_instance

                orchestrator._start_transcription()

                mock_worker.assert_called_once()


class TestProcessingOrchestratorStageTransitions:
    """Tests for stage transition handling."""

    def test_on_transcription_complete_starts_merge(self, qapp):
        """Test transcription completion starts merge stage."""
        from localmind.workers.transcription_worker import TranscriptionResult

        orchestrator = ProcessingOrchestrator()
        orchestrator._should_stop = False
        orchestrator._transcription_only = False

        completed_signal = []
        orchestrator.stage_completed.connect(lambda s: completed_signal.append(s))

        transcription = TranscriptionResult(text="Test")

        with patch.object(orchestrator, "_start_merge") as mock_start_merge:
            orchestrator._on_transcription_complete(transcription)

            assert orchestrator._result.transcription == transcription
            assert "transcription" in completed_signal
            mock_start_merge.assert_called_once()

    def test_on_transcription_complete_transcription_only(self, qapp):
        """Test transcription-only mode skips merge and audit."""
        from localmind.workers.transcription_worker import TranscriptionResult

        orchestrator = ProcessingOrchestrator()
        orchestrator._should_stop = False
        orchestrator._transcription_only = True
        orchestrator._is_processing = True

        complete_signal = []
        orchestrator.processing_complete.connect(lambda r: complete_signal.append(r))

        transcription = TranscriptionResult(text="Test")

        with patch.object(orchestrator, "_start_merge") as mock_start_merge:
            orchestrator._on_transcription_complete(transcription)

            # Should not start merge
            mock_start_merge.assert_not_called()
            # Should emit processing_complete
            assert len(complete_signal) == 1
            assert orchestrator._is_processing is False

    def test_on_transcription_complete_stop_requested(self, qapp):
        """Test transcription completion respects stop flag."""
        from localmind.workers.transcription_worker import TranscriptionResult

        orchestrator = ProcessingOrchestrator()
        orchestrator._should_stop = True
        orchestrator._is_processing = True

        transcription = TranscriptionResult(text="Test")

        with patch.object(orchestrator, "_start_merge") as mock_start_merge:
            orchestrator._on_transcription_complete(transcription)

            mock_start_merge.assert_not_called()
            assert orchestrator._is_processing is False

    def test_on_merge_complete_starts_audit(self, qapp):
        """Test merge completion starts audit stage."""
        from localmind.workers.merge_worker import MergeResult

        orchestrator = ProcessingOrchestrator()
        orchestrator._should_stop = False

        completed_signal = []
        orchestrator.stage_completed.connect(lambda s: completed_signal.append(s))

        merge_result = MergeResult(merged_text="Test")

        with patch.object(orchestrator, "_start_audit") as mock_start_audit:
            orchestrator._on_merge_complete(merge_result)

            assert orchestrator._result.merge == merge_result
            assert "merge" in completed_signal
            mock_start_audit.assert_called_once()

    def test_on_audit_complete_emits_processing_complete(self, qapp):
        """Test audit completion emits processing_complete."""
        from localmind.workers.audit_worker import AuditResult

        orchestrator = ProcessingOrchestrator()
        orchestrator._should_stop = False
        orchestrator._is_processing = True

        completed_signal = []
        processing_complete_signal = []
        orchestrator.stage_completed.connect(lambda s: completed_signal.append(s))
        orchestrator.processing_complete.connect(lambda r: processing_complete_signal.append(r))

        audit_result = AuditResult(overall_score=80.0, max_score=100.0)

        orchestrator._on_audit_complete(audit_result)

        assert orchestrator._result.audit == audit_result
        assert "audit" in completed_signal
        assert len(processing_complete_signal) == 1
        assert orchestrator._is_processing is False


class TestProcessingOrchestratorErrorHandling:
    """Tests for error handling."""

    def test_on_stage_error_emits_signals(self, qapp):
        """Test stage error emits correct signals."""
        orchestrator = ProcessingOrchestrator()
        orchestrator._is_processing = True

        stage_error_signal = []
        processing_error_signal = []
        orchestrator.stage_error.connect(lambda s, e: stage_error_signal.append((s, e)))
        orchestrator.processing_error.connect(lambda e: processing_error_signal.append(e))

        orchestrator._on_stage_error("transcription", "Test error message")

        assert orchestrator._result.error == "transcription: Test error message"
        assert orchestrator._is_processing is False
        assert len(stage_error_signal) == 1
        assert stage_error_signal[0] == ("transcription", "Test error message")
        assert len(processing_error_signal) == 1
        assert processing_error_signal[0] == "Test error message"


class TestProcessingOrchestratorSignals:
    """Tests for signal emissions."""

    def test_stage_started_signal_emitted(self, qapp, temp_dir):
        """Test stage_started signal is emitted."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator._audio_path = audio_file

        started_signal = []
        orchestrator.stage_started.connect(lambda s: started_signal.append(s))

        with patch.object(orchestrator, "_check_if_stereo", return_value=False):
            with patch("localmind.workers.orchestrator.TranscriptionWorker") as mock_worker:
                mock_instance = MagicMock()
                mock_worker.return_value = mock_instance

                orchestrator._start_transcription()

        assert "transcription" in started_signal

    def test_stage_progress_signal_forwarded(self, qapp, temp_dir):
        """Test progress signals are forwarded from workers."""
        audio_file = temp_dir / "test.wav"
        audio_file.touch()

        orchestrator = ProcessingOrchestrator()
        orchestrator._audio_path = audio_file

        progress_signals = []
        orchestrator.stage_progress.connect(lambda s, p, m: progress_signals.append((s, p, m)))

        with patch.object(orchestrator, "_check_if_stereo", return_value=False):
            with patch("localmind.workers.orchestrator.TranscriptionWorker") as mock_worker:
                mock_instance = MagicMock()
                mock_worker.return_value = mock_instance

                orchestrator._start_transcription()

                # Simulate progress signal from worker
                # Get the lambda connected to progress
                progress_connect_call = mock_instance.progress.connect.call_args
                progress_callback = progress_connect_call[0][0]

                # Call the callback
                progress_callback(50, "Testing")

        assert ("transcription", 50, "Testing") in progress_signals
