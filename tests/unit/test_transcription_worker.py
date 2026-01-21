"""
Tests for TranscriptionWorker execution logic.

Tests the transcription worker's do_work method with mocked Whisper model
to verify correct behavior without requiring actual model downloads.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from localmind.workers.transcription_worker import (
    DualChannelTranscriptionWorker,
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWorker,
)


class TestTranscriptionSegment:
    """Tests for TranscriptionSegment dataclass."""

    def test_segment_creation(self):
        """Test creating a transcription segment."""
        segment = TranscriptionSegment(
            start=0.0,
            end=5.0,
            text="Hello world",
            speaker="Agent",
            confidence=0.95,
        )
        assert segment.start == 0.0
        assert segment.end == 5.0
        assert segment.text == "Hello world"
        assert segment.speaker == "Agent"
        assert segment.confidence == 0.95

    def test_segment_to_dict(self):
        """Test segment to_dict conversion."""
        segment = TranscriptionSegment(
            start=1.0,
            end=3.5,
            text="Test text",
            speaker="Customer",
            confidence=0.9,
        )
        result = segment.to_dict()
        assert result["start"] == 1.0
        assert result["end"] == 3.5
        assert result["text"] == "Test text"
        assert result["speaker"] == "Customer"
        assert result["confidence"] == 0.9

    def test_segment_default_values(self):
        """Test segment default values."""
        segment = TranscriptionSegment(start=0.0, end=1.0, text="Test")
        assert segment.speaker is None
        assert segment.confidence == 1.0


class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""

    def test_result_creation(self):
        """Test creating a transcription result."""
        segments = [
            TranscriptionSegment(start=0.0, end=2.0, text="Hello"),
            TranscriptionSegment(start=2.0, end=4.0, text="World"),
        ]
        result = TranscriptionResult(
            text="Hello World",
            segments=segments,
            language="en",
            duration=4.0,
            channels=1,
        )
        assert result.text == "Hello World"
        assert len(result.segments) == 2
        assert result.language == "en"
        assert result.duration == 4.0
        assert result.channels == 1

    def test_result_to_dict(self):
        """Test result to_dict conversion."""
        segments = [TranscriptionSegment(start=0.0, end=1.0, text="Test")]
        result = TranscriptionResult(
            text="Test",
            segments=segments,
            language="en",
            duration=1.0,
        )
        d = result.to_dict()
        assert d["text"] == "Test"
        assert len(d["segments"]) == 1
        assert d["language"] == "en"
        assert d["duration"] == 1.0
        assert d["channels"] == 1

    def test_result_default_values(self):
        """Test result default values."""
        result = TranscriptionResult(text="Test")
        assert result.segments == []
        assert result.language is None
        assert result.duration == 0.0
        assert result.channels == 1


class TestTranscriptionWorkerInit:
    """Tests for TranscriptionWorker initialization."""

    def test_worker_initialization(self, qapp):
        """Test worker initialization with parameters."""
        worker = TranscriptionWorker(
            audio_path="/path/to/audio.wav",
            model_name="large-v3",
            language="en",
            use_gpu=True,
            use_preprocessing=True,
        )
        assert worker._audio_path == Path("/path/to/audio.wav")
        assert worker._model_name == "large-v3"
        assert worker._language == "en"
        assert worker._use_gpu is True
        assert worker._use_preprocessing is True
        assert worker._model is None

    def test_worker_default_values(self, qapp):
        """Test worker default initialization values."""
        worker = TranscriptionWorker(audio_path="/test.wav")
        assert worker._model_name == "large-v3"
        assert worker._language is None
        assert worker._use_gpu is True
        assert worker._use_preprocessing is True


class TestTranscriptionWorkerDoWork:
    """Tests for TranscriptionWorker.do_work() method."""

    @pytest.fixture
    def mock_audio_file(self, temp_dir):
        """Create a mock audio file for testing."""
        audio_path = temp_dir / "test_audio.wav"
        # Create a minimal WAV file
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            # 1 second of silence
            wav.writeframes(b"\x00" * 32000)
        return audio_path

    def test_do_work_stop_requested(self, qapp, mock_audio_file):
        """Test worker stops when stop is requested."""
        worker = TranscriptionWorker(
            audio_path=str(mock_audio_file),
            use_gpu=False,
        )
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_worker_check_stop(self, qapp):
        """Test check_stop method."""
        worker = TranscriptionWorker(audio_path="/test.wav")
        assert worker.check_stop() is False

        worker._should_stop = True
        assert worker.check_stop() is True

    def test_worker_report_progress(self, qapp):
        """Test report_progress method emits signal."""
        worker = TranscriptionWorker(audio_path="/test.wav")
        progress_values = []

        worker.progress.connect(lambda p, m: progress_values.append((p, m)))
        worker.report_progress(50, "Testing")

        assert len(progress_values) == 1
        assert progress_values[0] == (50, "Testing")


class TestDualChannelTranscriptionWorker:
    """Tests for DualChannelTranscriptionWorker."""

    def test_dual_channel_init(self, qapp):
        """Test dual-channel worker initialization."""
        worker = DualChannelTranscriptionWorker(
            audio_path="/path/to/stereo.wav",
            model_name="large-v3",
            language="en",
            use_gpu=True,
            agent_channel=0,
            customer_channel=1,
        )
        assert worker._agent_channel == 0
        assert worker._customer_channel == 1
        assert worker._model_name == "large-v3"

    def test_dual_channel_stop_requested(self, qapp, temp_dir):
        """Test dual-channel worker stops when requested."""
        audio_path = temp_dir / "test.wav"
        audio_path.touch()

        worker = DualChannelTranscriptionWorker(
            audio_path=str(audio_path),
            use_gpu=False,
        )
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_dual_channel_default_channels(self, qapp):
        """Test dual-channel default channel assignment."""
        worker = DualChannelTranscriptionWorker(audio_path="/test.wav")
        assert worker._agent_channel == 0
        assert worker._customer_channel == 1


class TestTranscriptionWorkerState:
    """Tests for worker state management."""

    def test_worker_initial_state(self, qapp):
        """Test worker initial state."""
        from localmind.workers.base import WorkerState

        worker = TranscriptionWorker(audio_path="/test.wav")
        assert worker.state == WorkerState.IDLE

    def test_worker_stop_method(self, qapp):
        """Test worker stop method."""
        from localmind.workers.base import WorkerState

        worker = TranscriptionWorker(audio_path="/test.wav")
        worker.stop()

        assert worker._should_stop is True
        assert worker.state == WorkerState.STOPPING

    def test_worker_pause_resume(self, qapp):
        """Test worker pause and resume."""
        from localmind.workers.base import WorkerState

        worker = TranscriptionWorker(audio_path="/test.wav")

        worker.pause()
        assert worker._is_paused is True
        assert worker.state == WorkerState.PAUSED

        worker.resume()
        assert worker._is_paused is False
        assert worker.state == WorkerState.RUNNING


class TestTranscriptionSegmentEdgeCases:
    """Tests for edge cases in TranscriptionSegment."""

    def test_empty_text(self):
        """Test segment with empty text."""
        segment = TranscriptionSegment(start=0.0, end=1.0, text="")
        assert segment.text == ""
        assert segment.to_dict()["text"] == ""

    def test_unicode_text(self):
        """Test segment with Unicode text."""
        segment = TranscriptionSegment(
            start=0.0, end=2.0, text="नमस्ते, मैं आपकी मदद कर सकता हूं"  # Hindi
        )
        assert "नमस्ते" in segment.text
        d = segment.to_dict()
        assert "नमस्ते" in d["text"]

    def test_very_long_segment(self):
        """Test segment with long text."""
        long_text = "word " * 1000
        segment = TranscriptionSegment(start=0.0, end=100.0, text=long_text)
        assert len(segment.text) > 4000

    def test_negative_timestamps(self):
        """Test segment creation doesn't validate timestamps."""
        # Dataclass doesn't validate - this tests current behavior
        segment = TranscriptionSegment(start=-1.0, end=-0.5, text="Test")
        assert segment.start == -1.0


class TestTranscriptionResultEdgeCases:
    """Tests for edge cases in TranscriptionResult."""

    def test_empty_segments_list(self):
        """Test result with empty segments."""
        result = TranscriptionResult(text="Test", segments=[])
        assert len(result.segments) == 0
        assert len(result.to_dict()["segments"]) == 0

    def test_multichannel_result(self):
        """Test result with multiple channels."""
        result = TranscriptionResult(text="Test", channels=4)
        assert result.channels == 4

    def test_long_duration(self):
        """Test result with long duration."""
        result = TranscriptionResult(text="Test", duration=3600.0)  # 1 hour
        assert result.duration == 3600.0


class TestTranscriptionWorkerModelLoading:
    """Tests for TranscriptionWorker._load_model() method."""

    def test_load_model_cuda_device(self, qapp):
        """Test model loading with CUDA device available."""
        worker = TranscriptionWorker(audio_path="/test.wav", use_gpu=True)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.device = MagicMock(return_value="cuda")

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"torch": mock_torch, "whisper": mock_whisper}):
            worker._load_model()

        mock_whisper.load_model.assert_called_once()
        assert worker._model is mock_model
        assert worker._device == "cuda"

    def test_load_model_mps_device(self, qapp):
        """Test model loading with MPS (Apple Silicon) device."""
        worker = TranscriptionWorker(audio_path="/test.wav", use_gpu=True)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True
        mock_torch.device = MagicMock()

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"torch": mock_torch, "whisper": mock_whisper}):
            worker._load_model()

        assert worker._device == "mps"
        assert worker._model is mock_model

    def test_load_model_cpu_fallback(self, qapp):
        """Test model loading falls back to CPU when no GPU available."""
        worker = TranscriptionWorker(audio_path="/test.wav", use_gpu=True)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.device = MagicMock()

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"torch": mock_torch, "whisper": mock_whisper}):
            worker._load_model()

        assert worker._device == "cpu"

    def test_load_model_use_gpu_false(self, qapp):
        """Test model loading with use_gpu=False forces CPU."""
        worker = TranscriptionWorker(audio_path="/test.wav", use_gpu=False)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True  # Would use GPU if enabled
        mock_torch.device = MagicMock()

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"torch": mock_torch, "whisper": mock_whisper}):
            worker._load_model()

        assert worker._device == "cpu"

    def test_load_model_import_error(self, qapp):
        """Test model loading handles import error."""
        worker = TranscriptionWorker(audio_path="/test.wav")

        with patch.dict("sys.modules", {"torch": None, "whisper": None}):
            with pytest.raises(ImportError, match="openai-whisper not installed"):
                worker._load_model()


class TestTranscriptionWorkerAudioLoading:
    """Tests for TranscriptionWorker._load_audio() method."""

    def test_load_audio_with_preprocessing(self, qapp, temp_dir):
        """Test audio loading with preprocessing enabled."""
        audio_path = temp_dir / "test.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = TranscriptionWorker(
            audio_path=str(audio_path),
            use_preprocessing=True,
        )

        mock_preprocess = MagicMock(return_value=(np.zeros(16000, dtype=np.float32), 16000))

        # Patch at the audio.preprocessing module level
        with patch(
            "localmind.audio.preprocessing.preprocess_audio_for_transcription",
            mock_preprocess,
        ):
            audio, sr = worker._load_audio()

        assert sr == 16000
        mock_preprocess.assert_called_once()

    def test_load_audio_preprocessing_fallback(self, qapp, temp_dir):
        """Test audio loading falls back when preprocessing fails."""
        audio_path = temp_dir / "test.wav"
        # Create a minimal WAV file
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = TranscriptionWorker(
            audio_path=str(audio_path),
            use_preprocessing=True,
        )

        # Mock preprocessing to fail
        mock_preprocess = MagicMock(side_effect=Exception("Preprocessing failed"))
        mock_librosa = MagicMock()
        mock_librosa.load.return_value = (np.zeros(16000), 16000)

        with patch(
            "localmind.audio.preprocessing.preprocess_audio_for_transcription",
            mock_preprocess,
        ):
            with patch("librosa.load", mock_librosa.load):
                audio, sr = worker._load_audio()

        assert sr == 16000

    def test_load_audio_no_preprocessing(self, qapp, temp_dir):
        """Test audio loading without preprocessing."""
        audio_path = temp_dir / "test.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = TranscriptionWorker(
            audio_path=str(audio_path),
            use_preprocessing=False,
        )

        mock_librosa = MagicMock()
        mock_librosa.load.return_value = (np.zeros(16000, dtype=np.float32), 16000)

        with patch("librosa.load", mock_librosa.load):
            audio, sr = worker._load_audio()

        assert sr == 16000
        mock_librosa.load.assert_called_once()


class TestTranscriptionWorkerTranscribe:
    """Tests for TranscriptionWorker._transcribe() method."""

    def test_transcribe_short_audio(self, qapp, temp_dir):
        """Test transcribing short audio (single chunk)."""
        worker = TranscriptionWorker(audio_path="/test.wav")

        # Create mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Hello world",
            "language": "en",
        }
        worker._model = mock_model
        worker._device = "cpu"

        # Short audio (10 seconds)
        audio = np.zeros(16000 * 10, dtype=np.float32)
        sr = 16000

        result = worker._transcribe(audio, sr)

        assert result["text"] == "Hello world"
        assert result["language"] == "en"

    def test_transcribe_long_audio_multiple_chunks(self, qapp):
        """Test transcribing long audio (multiple chunks)."""
        worker = TranscriptionWorker(audio_path="/test.wav")

        # Create mock model that returns different text for each chunk
        call_count = [0]

        def mock_transcribe(audio_chunk, **kwargs):
            call_count[0] += 1
            return {
                "text": f"Chunk {call_count[0]} text",
                "language": "en",
            }

        mock_model = MagicMock()
        mock_model.transcribe.side_effect = mock_transcribe
        worker._model = mock_model
        worker._device = "cpu"

        # Long audio (60 seconds - should create multiple chunks)
        audio = np.zeros(16000 * 60, dtype=np.float32)
        sr = 16000

        result = worker._transcribe(audio, sr)

        # Should have processed multiple chunks
        assert call_count[0] > 1
        assert "Chunk" in result["text"]

    def test_transcribe_with_language_setting(self, qapp):
        """Test transcription respects language setting."""
        worker = TranscriptionWorker(audio_path="/test.wav", language="hi")

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "नमस्ते",
            "language": "hi",
        }
        worker._model = mock_model
        worker._device = "cpu"

        audio = np.zeros(16000 * 10, dtype=np.float32)

        worker._transcribe(audio, 16000)  # Result not needed, checking call_args

        # Verify language was passed to transcribe
        call_args = mock_model.transcribe.call_args
        assert call_args[1].get("language") == "hi"

    def test_transcribe_chunk_exception_continues(self, qapp):
        """Test transcription continues when a chunk fails."""
        worker = TranscriptionWorker(audio_path="/test.wav")

        call_count = [0]

        def mock_transcribe(audio_chunk, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Chunk 1 failed")
            return {"text": f"Chunk {call_count[0]}", "language": "en"}

        mock_model = MagicMock()
        mock_model.transcribe.side_effect = mock_transcribe
        worker._model = mock_model
        worker._device = "cpu"

        # Long audio to generate multiple chunks
        audio = np.zeros(16000 * 60, dtype=np.float32)

        result = worker._transcribe(audio, 16000)

        # Should still have result from successful chunks
        assert call_count[0] > 1
        assert result["text"]  # Should not be empty

    def test_transcribe_auto_language_detection(self, qapp):
        """Test transcription with auto language detection."""
        worker = TranscriptionWorker(audio_path="/test.wav", language="auto")

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Bonjour",
            "language": "fr",
        }
        worker._model = mock_model
        worker._device = "cpu"

        audio = np.zeros(16000 * 10, dtype=np.float32)

        result = worker._transcribe(audio, 16000)

        # Language should be detected from transcription
        assert result["language"] == "fr"
        # Language param should not be passed for "auto"
        call_args = mock_model.transcribe.call_args
        assert "language" not in call_args[1]


class TestDualChannelWorkerModelLoading:
    """Tests for DualChannelTranscriptionWorker._load_model()."""

    def test_dual_channel_load_model(self, qapp):
        """Test dual-channel worker loads model correctly."""
        worker = DualChannelTranscriptionWorker(audio_path="/test.wav", use_gpu=False)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.device = MagicMock()

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        with patch.dict("sys.modules", {"torch": mock_torch, "whisper": mock_whisper}):
            worker._load_model()

        assert worker._model is mock_model


class TestDualChannelWorkerChannelLoading:
    """Tests for DualChannelTranscriptionWorker._load_channels()."""

    def test_load_channels_stereo(self, qapp, temp_dir):
        """Test loading stereo audio channels."""
        audio_path = temp_dir / "test_stereo.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(2)  # Stereo
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 64000)  # 1 second stereo

        worker = DualChannelTranscriptionWorker(
            audio_path=str(audio_path),
            use_preprocessing=False,
        )

        mock_librosa = MagicMock()
        # Return 2D array for stereo
        stereo_audio = np.zeros((2, 16000), dtype=np.float32)
        stereo_audio[0] = np.ones(16000) * 0.5  # Agent channel
        stereo_audio[1] = np.ones(16000) * 0.3  # Customer channel
        mock_librosa.load.return_value = (stereo_audio, 16000)

        with patch("librosa.load", mock_librosa.load):
            agent_audio, customer_audio = worker._load_channels()

        # Verify channels were separated
        assert np.allclose(agent_audio, stereo_audio[0])
        assert np.allclose(customer_audio, stereo_audio[1])

    def test_load_channels_mono_fallback(self, qapp, temp_dir):
        """Test loading mono audio duplicates to both channels."""
        audio_path = temp_dir / "test_mono.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = DualChannelTranscriptionWorker(
            audio_path=str(audio_path),
            use_preprocessing=False,
        )

        mock_librosa = MagicMock()
        mono_audio = np.zeros(16000, dtype=np.float32)
        mock_librosa.load.return_value = (mono_audio, 16000)

        with patch("librosa.load", mock_librosa.load):
            agent_audio, customer_audio = worker._load_channels()

        # Mono should be duplicated to both channels
        assert np.array_equal(agent_audio, customer_audio)


class TestDualChannelWorkerTranscription:
    """Tests for DualChannelTranscriptionWorker._transcribe_channel()."""

    def test_transcribe_channel(self, qapp):
        """Test transcribing a single channel."""
        worker = DualChannelTranscriptionWorker(audio_path="/test.wav")

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Hello from agent",
            "segments": [{"start": 0.0, "end": 2.0, "text": "Hello from agent"}],
            "language": "en",
        }
        mock_whisper.pad_or_trim.return_value = np.zeros(16000 * 30)
        worker._model = mock_model

        with patch.dict("sys.modules", {"whisper": mock_whisper}):
            with patch("whisper.pad_or_trim", mock_whisper.pad_or_trim):
                audio = np.zeros(16000 * 10, dtype=np.float32)
                result = worker._transcribe_channel(audio, "Agent")

        assert result["text"] == "Hello from agent"
        assert len(result["segments"]) == 1

    def test_transcribe_channel_with_language(self, qapp):
        """Test channel transcription respects language setting."""
        worker = DualChannelTranscriptionWorker(audio_path="/test.wav", language="es")

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Hola",
            "segments": [],
            "language": "es",
        }
        mock_whisper.pad_or_trim.return_value = np.zeros(16000 * 30)
        worker._model = mock_model

        with patch.dict("sys.modules", {"whisper": mock_whisper}):
            with patch("whisper.pad_or_trim", mock_whisper.pad_or_trim):
                audio = np.zeros(16000 * 10, dtype=np.float32)
                worker._transcribe_channel(audio, "Agent")  # Result not needed

        # Verify language was passed
        call_args = mock_model.transcribe.call_args
        assert call_args[1].get("language") == "es"


class TestDualChannelWorkerDoWork:
    """Tests for DualChannelTranscriptionWorker.do_work()."""

    def test_dual_channel_do_work_merges_segments(self, qapp, temp_dir):
        """Test do_work correctly merges segments from both channels."""
        audio_path = temp_dir / "test.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 64000)

        worker = DualChannelTranscriptionWorker(
            audio_path=str(audio_path),
            use_preprocessing=False,
        )

        # Mock model loading
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.device = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        mock_whisper = MagicMock()
        mock_model = MagicMock()

        # Agent transcription
        agent_result = {
            "text": "Hello from agent",
            "segments": [{"start": 0.0, "end": 2.0, "text": "Hello from agent"}],
            "language": "en",
        }
        # Customer transcription
        customer_result = {
            "text": "Hello from customer",
            "segments": [{"start": 1.0, "end": 3.0, "text": "Hello from customer"}],
            "language": "en",
        }
        mock_model.transcribe.side_effect = [agent_result, customer_result]
        mock_whisper.load_model.return_value = mock_model
        mock_whisper.pad_or_trim.return_value = np.zeros(16000 * 30)

        mock_librosa = MagicMock()
        stereo_audio = np.zeros((2, 16000), dtype=np.float32)
        mock_librosa.load.return_value = (stereo_audio, 16000)

        with patch.dict("sys.modules", {"torch": mock_torch, "whisper": mock_whisper}):
            with patch("librosa.load", mock_librosa.load):
                with patch("whisper.pad_or_trim", mock_whisper.pad_or_trim):
                    result = worker.do_work()

        assert result is not None
        assert result.channels == 2
        assert len(result.segments) == 2
        # Segments should be sorted by start time
        assert result.segments[0].start <= result.segments[1].start
        # Speakers should be assigned
        assert any(s.speaker == "Agent" for s in result.segments)
        assert any(s.speaker == "Customer" for s in result.segments)
