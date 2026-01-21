"""
Tests for Hindi STT Worker.

Tests Hindi-English (Hinglish) transcription workers.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from localmind.workers.hindi_transcription_worker import (
    HINDI_MODELS,
    DualChannelHindiSTTWorker,
    HindiSTTWorker,
)
from localmind.workers.transcription_worker import TranscriptionResult, TranscriptionSegment


class TestHindiModels:
    """Tests for HINDI_MODELS configuration."""

    def test_hindi_models_exist(self):
        """Test Hindi models are defined."""
        assert "apex" in HINDI_MODELS
        assert "prime" in HINDI_MODELS

    def test_hindi_models_have_correct_ids(self):
        """Test Hindi models have correct HuggingFace IDs."""
        assert "Oriserve" in HINDI_MODELS["apex"]
        assert "Oriserve" in HINDI_MODELS["prime"]
        assert "Apex" in HINDI_MODELS["apex"]
        assert "Prime" in HINDI_MODELS["prime"]


class TestHindiSTTWorkerInit:
    """Tests for HindiSTTWorker initialization."""

    def test_worker_initialization_defaults(self, qapp):
        """Test worker initializes with correct defaults."""
        worker = HindiSTTWorker(audio_path="/test/audio.wav")

        assert worker._audio_path == Path("/test/audio.wav")
        assert worker._use_gpu is True
        assert worker._use_flash_attention is False
        assert worker._model_variant == "apex"
        assert worker._num_speakers == 2
        assert worker._use_preprocessing is True
        assert worker._pipe is None

    def test_worker_initialization_custom_values(self, qapp):
        """Test worker with custom initialization values."""
        worker = HindiSTTWorker(
            audio_path="/test/audio.wav",
            use_gpu=False,
            use_flash_attention=True,
            model_variant="prime",
            num_speakers=3,
            use_preprocessing=False,
        )

        assert worker._use_gpu is False
        assert worker._use_flash_attention is True
        assert worker._model_variant == "prime"
        assert worker._model_id == HINDI_MODELS["prime"]
        assert worker._num_speakers == 3
        assert worker._use_preprocessing is False

    def test_worker_model_id_apex(self, qapp):
        """Test apex model ID is set correctly."""
        worker = HindiSTTWorker(audio_path="/test.wav", model_variant="apex")
        assert worker._model_id == HINDI_MODELS["apex"]

    def test_worker_model_id_prime(self, qapp):
        """Test prime model ID is set correctly."""
        worker = HindiSTTWorker(audio_path="/test.wav", model_variant="prime")
        assert worker._model_id == HINDI_MODELS["prime"]


class TestHindiSTTWorkerDoWork:
    """Tests for HindiSTTWorker.do_work() method."""

    def test_do_work_stop_requested(self, qapp, temp_dir):
        """Test worker stops when stop is requested."""
        audio_path = temp_dir / "test.wav"
        audio_path.touch()

        worker = HindiSTTWorker(audio_path=str(audio_path), use_gpu=False)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_do_work_reports_progress(self, qapp):
        """Test worker reports progress."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_gpu=False)

        progress_values = []
        worker.progress.connect(lambda p, m: progress_values.append((p, m)))

        # Stop immediately to test initial progress
        worker._should_stop = True
        worker.do_work()

        # Should have reported initial progress
        assert len(progress_values) >= 1
        assert progress_values[0][0] == 0  # First progress is 0


class TestHindiSTTWorkerState:
    """Tests for HindiSTTWorker state management."""

    def test_worker_initial_state(self, qapp):
        """Test worker initial state."""
        from localmind.workers.base import WorkerState

        worker = HindiSTTWorker(audio_path="/test.wav")
        assert worker.state == WorkerState.IDLE

    def test_worker_stop_method(self, qapp):
        """Test worker stop method."""
        from localmind.workers.base import WorkerState

        worker = HindiSTTWorker(audio_path="/test.wav")
        worker.stop()

        assert worker._should_stop is True
        assert worker.state == WorkerState.STOPPING

    def test_worker_pause_resume(self, qapp):
        """Test worker pause and resume."""
        from localmind.workers.base import WorkerState

        worker = HindiSTTWorker(audio_path="/test.wav")

        worker.pause()
        assert worker._is_paused is True
        assert worker.state == WorkerState.PAUSED

        worker.resume()
        assert worker._is_paused is False
        assert worker.state == WorkerState.RUNNING


class TestDualChannelHindiSTTWorkerInit:
    """Tests for DualChannelHindiSTTWorker initialization."""

    def test_dual_channel_init_defaults(self, qapp):
        """Test dual-channel worker initialization defaults."""
        worker = DualChannelHindiSTTWorker(audio_path="/test/stereo.wav")

        assert worker._audio_path == Path("/test/stereo.wav")
        assert worker._use_gpu is True
        assert worker._use_flash_attention is False
        assert worker._model_variant == "apex"
        assert worker._agent_channel == 0
        assert worker._customer_channel == 1
        assert worker._use_preprocessing is True
        assert worker._model is None
        assert worker._processor is None

    def test_dual_channel_init_custom_channels(self, qapp):
        """Test dual-channel worker with custom channel assignment."""
        worker = DualChannelHindiSTTWorker(
            audio_path="/test/stereo.wav",
            agent_channel=1,
            customer_channel=0,
        )

        assert worker._agent_channel == 1
        assert worker._customer_channel == 0

    def test_dual_channel_init_prime_model(self, qapp):
        """Test dual-channel worker with prime model."""
        worker = DualChannelHindiSTTWorker(
            audio_path="/test/stereo.wav",
            model_variant="prime",
        )

        assert worker._model_variant == "prime"
        assert worker._model_id == HINDI_MODELS["prime"]


class TestDualChannelHindiSTTWorkerDoWork:
    """Tests for DualChannelHindiSTTWorker.do_work() method."""

    def test_dual_channel_stop_requested(self, qapp, temp_dir):
        """Test dual-channel worker stops when requested."""
        audio_path = temp_dir / "test.wav"
        audio_path.touch()

        worker = DualChannelHindiSTTWorker(audio_path=str(audio_path), use_gpu=False)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_dual_channel_reports_progress(self, qapp):
        """Test dual-channel worker reports progress."""
        worker = DualChannelHindiSTTWorker(audio_path="/test.wav", use_gpu=False)

        progress_values = []
        worker.progress.connect(lambda p, m: progress_values.append((p, m)))

        # Stop immediately to test initial progress
        worker._should_stop = True
        worker.do_work()

        # Should have reported initial progress
        assert len(progress_values) >= 1


class TestDualChannelHindiSTTWorkerState:
    """Tests for DualChannelHindiSTTWorker state management."""

    def test_dual_channel_initial_state(self, qapp):
        """Test dual-channel worker initial state."""
        from localmind.workers.base import WorkerState

        worker = DualChannelHindiSTTWorker(audio_path="/test.wav")
        assert worker.state == WorkerState.IDLE

    def test_dual_channel_stop(self, qapp):
        """Test dual-channel worker stop."""
        from localmind.workers.base import WorkerState

        worker = DualChannelHindiSTTWorker(audio_path="/test.wav")
        worker.stop()

        assert worker._should_stop is True
        assert worker.state == WorkerState.STOPPING


class TestTranscriptionResultFormat:
    """Tests for Hindi transcription result format."""

    def test_transcription_result_language(self):
        """Test transcription result has correct language."""
        # Simulate expected result format from HindiSTTWorker
        result = TranscriptionResult(
            text="Test Hindi-English text",
            segments=[],
            language="hi-en",
        )

        assert result.language == "hi-en"

    def test_dual_channel_result_channels(self):
        """Test dual-channel result has correct channels."""
        # Simulate expected result format from DualChannelHindiSTTWorker
        result = TranscriptionResult(
            text="[Agent] Hello\n[Customer] Hi",
            segments=[
                TranscriptionSegment(start=0.0, end=0.0, text="Hello", speaker="Agent"),
                TranscriptionSegment(start=0.0, end=0.0, text="Hi", speaker="Customer"),
            ],
            language="hi-en",
            channels=2,
        )

        assert result.channels == 2
        assert len(result.segments) == 2
        assert result.segments[0].speaker == "Agent"
        assert result.segments[1].speaker == "Customer"


class TestHindiWorkerDeviceSelection:
    """Tests for device selection logic."""

    def test_cpu_when_gpu_disabled(self, qapp):
        """Test CPU is used when GPU is disabled."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_gpu=False)
        # Device is set during _load_model, but we can verify the flag
        assert worker._use_gpu is False

    def test_gpu_flag_enabled(self, qapp):
        """Test GPU flag is set when enabled."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_gpu=True)
        assert worker._use_gpu is True


class TestHindiWorkerPreprocessing:
    """Tests for audio preprocessing option."""

    def test_preprocessing_enabled_by_default(self, qapp):
        """Test preprocessing is enabled by default."""
        worker = HindiSTTWorker(audio_path="/test.wav")
        assert worker._use_preprocessing is True

    def test_preprocessing_can_be_disabled(self, qapp):
        """Test preprocessing can be disabled."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_preprocessing=False)
        assert worker._use_preprocessing is False

    def test_dual_channel_preprocessing_enabled(self, qapp):
        """Test dual-channel preprocessing is enabled by default."""
        worker = DualChannelHindiSTTWorker(audio_path="/test.wav")
        assert worker._use_preprocessing is True


class TestHindiWorkerFlashAttention:
    """Tests for Flash Attention option."""

    def test_flash_attention_disabled_by_default(self, qapp):
        """Test Flash Attention is disabled by default."""
        worker = HindiSTTWorker(audio_path="/test.wav")
        assert worker._use_flash_attention is False

    def test_flash_attention_can_be_enabled(self, qapp):
        """Test Flash Attention can be enabled."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_flash_attention=True)
        assert worker._use_flash_attention is True

    def test_dual_channel_flash_attention(self, qapp):
        """Test dual-channel Flash Attention option."""
        worker = DualChannelHindiSTTWorker(audio_path="/test.wav", use_flash_attention=True)
        assert worker._use_flash_attention is True


class TestHindiWorkerEdgeCases:
    """Tests for edge cases in Hindi workers."""

    def test_empty_audio_path(self, qapp):
        """Test worker creation with empty path."""
        worker = HindiSTTWorker(audio_path="")
        assert worker._audio_path == Path("")

    def test_unicode_path(self, qapp):
        """Test worker with Unicode path."""
        worker = HindiSTTWorker(audio_path="/test/हिंदी_audio.wav")
        assert "हिंदी" in str(worker._audio_path)

    def test_num_speakers_none(self, qapp):
        """Test worker with None num_speakers (auto-detection)."""
        worker = HindiSTTWorker(audio_path="/test.wav", num_speakers=None)
        assert worker._num_speakers is None

    def test_num_speakers_custom(self, qapp):
        """Test worker with custom num_speakers."""
        worker = HindiSTTWorker(audio_path="/test.wav", num_speakers=5)
        assert worker._num_speakers == 5


class TestHindiSTTWorkerModelLoading:
    """Tests for HindiSTTWorker._load_model() method."""

    def test_load_model_cuda_device(self, qapp):
        """Test model loading with CUDA device available."""
        import numpy as np

        worker = HindiSTTWorker(audio_path="/test.wav", use_gpu=True)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = MagicMock()
        mock_torch.float32 = MagicMock()
        mock_torch.device = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        mock_model = MagicMock()
        mock_model.to.return_value = mock_model
        mock_processor = MagicMock()

        mock_transformers = MagicMock()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.return_value = mock_model
        mock_transformers.AutoProcessor.from_pretrained.return_value = mock_processor

        with patch.dict("sys.modules", {"torch": mock_torch, "transformers": mock_transformers}):
            worker._load_model()

        assert worker._device == "cuda:0"
        assert worker._model is mock_model
        assert worker._processor is mock_processor

    def test_load_model_mps_device_no_flash_attention(self, qapp):
        """Test model loading with MPS device (flash attention disabled)."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_gpu=True, use_flash_attention=True)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True
        mock_torch.float16 = MagicMock()
        mock_torch.float32 = MagicMock()
        mock_torch.device = MagicMock()

        mock_model = MagicMock()
        mock_model.to.return_value = mock_model
        mock_processor = MagicMock()

        mock_transformers = MagicMock()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.return_value = mock_model
        mock_transformers.AutoProcessor.from_pretrained.return_value = mock_processor

        with patch.dict("sys.modules", {"torch": mock_torch, "transformers": mock_transformers}):
            worker._load_model()

        # On MPS, flash attention should not be used
        assert worker._device == "mps"
        # Model should use float32 on MPS to avoid NaN errors
        assert worker._dtype == mock_torch.float32

    def test_load_model_cpu_fallback(self, qapp):
        """Test model loading falls back to CPU when no GPU available."""
        worker = HindiSTTWorker(audio_path="/test.wav", use_gpu=True)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False
        mock_torch.float32 = MagicMock()
        mock_torch.device = MagicMock()

        mock_model = MagicMock()
        mock_model.to.return_value = mock_model
        mock_processor = MagicMock()

        mock_transformers = MagicMock()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.return_value = mock_model
        mock_transformers.AutoProcessor.from_pretrained.return_value = mock_processor

        with patch.dict("sys.modules", {"torch": mock_torch, "transformers": mock_transformers}):
            worker._load_model()

        assert worker._device == "cpu"

    def test_load_model_import_error(self, qapp):
        """Test model loading handles import error."""
        worker = HindiSTTWorker(audio_path="/test.wav")

        with patch.dict("sys.modules", {"torch": None, "transformers": None}):
            with pytest.raises(ImportError, match="transformers not installed"):
                worker._load_model()


class TestHindiSTTWorkerTranscribe:
    """Tests for HindiSTTWorker._transcribe() method."""

    def test_transcribe_with_preprocessing(self, qapp, temp_dir):
        """Test transcription with preprocessing enabled."""
        import numpy as np

        audio_path = temp_dir / "test.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = HindiSTTWorker(
            audio_path=str(audio_path),
            use_preprocessing=True,
        )

        # Setup mocks
        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_processor.return_value = MagicMock(
            input_features=MagicMock(to=MagicMock(return_value=MagicMock()))
        )
        mock_processor.batch_decode.return_value = ["नमस्ते Hello"]

        worker._model = mock_model
        worker._processor = mock_processor
        worker._device = "cpu"
        worker._dtype = MagicMock()

        mock_preprocess = MagicMock(return_value=(np.zeros(16000, dtype=np.float32), 16000))

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        with patch(
            "localmind.audio.preprocessing.preprocess_audio_for_transcription",
            mock_preprocess,
        ):
            with patch("torch.no_grad", mock_torch.no_grad):
                result = worker._transcribe()

        assert "text" in result
        mock_preprocess.assert_called_once()

    def test_transcribe_preprocessing_fallback(self, qapp, temp_dir):
        """Test transcription falls back when preprocessing fails."""
        import numpy as np

        audio_path = temp_dir / "test.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = HindiSTTWorker(
            audio_path=str(audio_path),
            use_preprocessing=True,
        )

        # Setup mocks
        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_processor.return_value = MagicMock(
            input_features=MagicMock(to=MagicMock(return_value=MagicMock()))
        )
        mock_processor.batch_decode.return_value = ["Hello"]

        worker._model = mock_model
        worker._processor = mock_processor
        worker._device = "cpu"
        worker._dtype = MagicMock()

        mock_preprocess = MagicMock(side_effect=Exception("Preprocessing failed"))
        mock_librosa = MagicMock()
        mock_librosa.load.return_value = (np.zeros(16000, dtype=np.float32), 16000)

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        with patch(
            "localmind.audio.preprocessing.preprocess_audio_for_transcription",
            mock_preprocess,
        ):
            with patch("librosa.load", mock_librosa.load):
                with patch("torch.no_grad", mock_torch.no_grad):
                    result = worker._transcribe()

        assert "text" in result
        mock_librosa.load.assert_called_once()

    def test_transcribe_multiple_chunks(self, qapp, temp_dir):
        """Test transcription with multiple chunks."""
        import numpy as np

        worker = HindiSTTWorker(audio_path="/test.wav", use_preprocessing=False)

        # Create mock model that returns different text for chunks
        call_count = [0]

        def mock_generate(*args, **kwargs):
            call_count[0] += 1
            return MagicMock()

        mock_model = MagicMock()
        mock_model.generate.side_effect = mock_generate

        mock_processor = MagicMock()
        mock_processor.return_value = MagicMock(
            input_features=MagicMock(to=MagicMock(return_value=MagicMock()))
        )
        mock_processor.batch_decode.return_value = [f"Chunk text"]

        worker._model = mock_model
        worker._processor = mock_processor
        worker._device = "cpu"
        worker._dtype = MagicMock()

        # Long audio to generate multiple chunks (60 seconds)
        mock_librosa = MagicMock()
        mock_librosa.load.return_value = (np.zeros(16000 * 60, dtype=np.float32), 16000)

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        with patch("librosa.load", mock_librosa.load):
            with patch("torch.no_grad", mock_torch.no_grad):
                result = worker._transcribe()

        # Should have processed multiple chunks
        assert call_count[0] > 1


class TestDualChannelHindiSTTWorkerModelLoading:
    """Tests for DualChannelHindiSTTWorker._load_model()."""

    def test_dual_channel_load_model_cpu(self, qapp):
        """Test dual-channel worker loads model on CPU correctly."""
        worker = DualChannelHindiSTTWorker(audio_path="/test.wav", use_gpu=False)

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.float32 = MagicMock()
        mock_torch.device = MagicMock()

        mock_model = MagicMock()
        mock_model.to.return_value = mock_model
        mock_processor = MagicMock()

        mock_transformers = MagicMock()
        mock_transformers.AutoModelForSpeechSeq2Seq.from_pretrained.return_value = mock_model
        mock_transformers.AutoProcessor.from_pretrained.return_value = mock_processor

        with patch.dict("sys.modules", {"torch": mock_torch, "transformers": mock_transformers}):
            worker._load_model()

        assert worker._device == "cpu"
        assert worker._model is mock_model


class TestDualChannelHindiSTTWorkerChannelLoading:
    """Tests for DualChannelHindiSTTWorker._load_channels()."""

    def test_load_channels_stereo_no_preprocessing(self, qapp, temp_dir):
        """Test loading stereo channels without preprocessing."""
        import numpy as np

        audio_path = temp_dir / "test_stereo.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 64000)

        worker = DualChannelHindiSTTWorker(
            audio_path=str(audio_path),
            use_preprocessing=False,
        )

        mock_librosa = MagicMock()
        stereo_audio = np.zeros((2, 16000), dtype=np.float32)
        stereo_audio[0] = np.ones(16000) * 0.5
        stereo_audio[1] = np.ones(16000) * 0.3
        mock_librosa.load.return_value = (stereo_audio, 16000)

        mock_sf = MagicMock()

        with patch("librosa.load", mock_librosa.load):
            with patch("soundfile.write", mock_sf):
                agent_path, customer_path = worker._load_channels()

        # Should return temp file paths
        assert agent_path is not None
        assert customer_path is not None

    def test_load_channels_mono_no_preprocessing(self, qapp, temp_dir):
        """Test loading mono audio duplicates to both channels."""
        import numpy as np

        audio_path = temp_dir / "test_mono.wav"
        import wave

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(b"\x00" * 32000)

        worker = DualChannelHindiSTTWorker(
            audio_path=str(audio_path),
            use_preprocessing=False,
        )

        mock_librosa = MagicMock()
        mono_audio = np.zeros(16000, dtype=np.float32)
        mock_librosa.load.return_value = (mono_audio, 16000)

        with patch("librosa.load", mock_librosa.load):
            agent_path, customer_path = worker._load_channels()

        # Mono returns same path for both
        assert agent_path == customer_path


class TestDualChannelHindiSTTWorkerTranscription:
    """Tests for DualChannelHindiSTTWorker._transcribe_audio()."""

    def test_transcribe_audio(self, qapp, temp_dir):
        """Test transcribing audio from a channel."""
        import numpy as np

        # Create a temp audio file
        audio_path = temp_dir / "test_channel.wav"
        import soundfile as sf

        sf.write(str(audio_path), np.zeros(16000, dtype=np.float32), 16000)

        worker = DualChannelHindiSTTWorker(audio_path="/test.wav")

        mock_model = MagicMock()
        mock_processor = MagicMock()
        mock_processor.return_value = MagicMock(
            input_features=MagicMock(to=MagicMock(return_value=MagicMock()))
        )
        mock_processor.batch_decode.return_value = ["Agent speaking Hindi"]

        worker._model = mock_model
        worker._processor = mock_processor
        worker._device = "cpu"
        worker._dtype = MagicMock()

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        with patch("torch.no_grad", mock_torch.no_grad):
            result = worker._transcribe_audio(str(audio_path))

        assert "text" in result
        assert result["text"] == "Agent speaking Hindi"

    def test_transcribe_audio_chunk_error_continues(self, qapp, temp_dir):
        """Test transcription continues when a chunk fails."""
        import numpy as np

        # Create a longer audio file to generate multiple chunks
        audio_path = temp_dir / "test_long.wav"
        import soundfile as sf

        sf.write(str(audio_path), np.zeros(16000 * 60, dtype=np.float32), 16000)  # 60 seconds

        worker = DualChannelHindiSTTWorker(audio_path="/test.wav")

        call_count = [0]

        def mock_generate(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("First chunk failed")
            return MagicMock()

        mock_model = MagicMock()
        mock_model.generate.side_effect = mock_generate

        mock_processor = MagicMock()
        mock_processor.return_value = MagicMock(
            input_features=MagicMock(to=MagicMock(return_value=MagicMock()))
        )
        mock_processor.batch_decode.return_value = ["Text from chunk"]

        worker._model = mock_model
        worker._processor = mock_processor
        worker._device = "cpu"
        worker._dtype = MagicMock()

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock()
        mock_torch.no_grad.return_value.__exit__ = MagicMock()

        with patch("torch.no_grad", mock_torch.no_grad):
            result = worker._transcribe_audio(str(audio_path))

        # Should have processed multiple chunks and continued after error
        assert call_count[0] > 1
        assert "text" in result
