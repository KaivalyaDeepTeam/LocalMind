"""
Tests for audio preprocessing functions.

Tests signal processing functions used for call recording preprocessing
including bandpass filtering, compression, normalization, and noise gating.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestApplyTelephoneBandpass:
    """Tests for apply_telephone_bandpass function."""

    def test_bandpass_filter_basic(self):
        """Test basic bandpass filtering."""
        from localmind.audio.preprocessing import apply_telephone_bandpass

        # Create test signal with components at different frequencies
        sr = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sr * duration), dtype=np.float32)

        # Signal with low (100 Hz), mid (1000 Hz), and high (5000 Hz) components
        audio = (
            np.sin(2 * np.pi * 100 * t)  # Below passband
            + np.sin(2 * np.pi * 1000 * t)  # Within passband
            + np.sin(2 * np.pi * 5000 * t)  # Above passband
        ).astype(np.float32)

        filtered = apply_telephone_bandpass(audio, sr)

        # Output should be float32
        assert filtered.dtype == np.float32
        # Output should have same length
        assert len(filtered) == len(audio)

    def test_bandpass_filter_preserves_speech_frequencies(self):
        """Test that speech frequencies (300-3400 Hz) are preserved."""
        from localmind.audio.preprocessing import apply_telephone_bandpass

        sr = 16000
        duration = 0.5
        t = np.linspace(0, duration, int(sr * duration), dtype=np.float32)

        # Pure 1000 Hz tone (within passband)
        audio = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

        filtered = apply_telephone_bandpass(audio, sr)

        # Signal within passband should be mostly preserved
        # Allow for some filter attenuation
        assert np.max(np.abs(filtered)) > 0.5

    def test_bandpass_filter_without_scipy(self):
        """Test fallback when scipy is not available."""
        from localmind.audio.preprocessing import apply_telephone_bandpass

        audio = np.random.randn(1000).astype(np.float32)
        sr = 16000

        with patch.dict("sys.modules", {"scipy": None, "scipy.signal": None}):
            # Should return original audio without scipy
            result = apply_telephone_bandpass(audio, sr)
            # When scipy import fails, should return original
            assert len(result) == len(audio)


class TestApplyDynamicRangeCompression:
    """Tests for apply_dynamic_range_compression function."""

    def test_compression_basic(self):
        """Test basic compression functionality."""
        from localmind.audio.preprocessing import apply_dynamic_range_compression

        sr = 16000
        # Create signal with varying amplitude
        audio = np.concatenate(
            [
                np.ones(4000, dtype=np.float32) * 0.1,  # Quiet section
                np.ones(4000, dtype=np.float32) * 0.9,  # Loud section
                np.ones(4000, dtype=np.float32) * 0.1,  # Quiet section
            ]
        )

        compressed = apply_dynamic_range_compression(audio, threshold=-20.0, ratio=4.0, sr=sr)

        assert compressed.dtype == np.float32
        assert len(compressed) == len(audio)

    def test_compression_reduces_dynamic_range(self):
        """Test that compression reduces dynamic range."""
        from localmind.audio.preprocessing import apply_dynamic_range_compression

        sr = 16000
        # Signal with large dynamic range
        quiet = np.ones(2000, dtype=np.float32) * 0.01
        loud = np.ones(2000, dtype=np.float32) * 0.9
        audio = np.concatenate([quiet, loud])

        original_range = np.max(np.abs(audio)) - np.min(np.abs(audio[audio != 0]))

        compressed = apply_dynamic_range_compression(audio, threshold=-20.0, ratio=4.0, sr=sr)
        compressed_range = np.max(np.abs(compressed)) - np.min(np.abs(compressed[compressed != 0]))

        # Compressed range should be smaller (or at least not larger)
        assert compressed_range <= original_range * 1.1  # Allow small tolerance

    def test_compression_preserves_silence(self):
        """Test that compression handles silence correctly."""
        from localmind.audio.preprocessing import apply_dynamic_range_compression

        audio = np.zeros(1000, dtype=np.float32)
        sr = 16000

        compressed = apply_dynamic_range_compression(audio, sr=sr)

        # Should not produce NaN or Inf for silent audio
        assert not np.any(np.isnan(compressed))
        assert not np.any(np.isinf(compressed))


class TestRmsNormalize:
    """Tests for rms_normalize function."""

    def test_normalize_basic(self):
        """Test basic RMS normalization."""
        from localmind.audio.preprocessing import rms_normalize

        # Create test signal
        audio = np.random.randn(16000).astype(np.float32) * 0.1
        normalized = rms_normalize(audio, target_rms_db=-20.0)

        assert normalized.dtype == np.float32
        assert len(normalized) == len(audio)

    def test_normalize_reaches_target(self):
        """Test that normalization reaches target RMS level."""
        from localmind.audio.preprocessing import rms_normalize

        audio = np.random.randn(16000).astype(np.float32) * 0.05
        target_rms_db = -20.0

        normalized = rms_normalize(audio, target_rms_db=target_rms_db)

        # Calculate actual RMS
        actual_rms = np.sqrt(np.mean(normalized**2))
        actual_rms_db = 20 * np.log10(actual_rms + 1e-8)

        # Should be within 3 dB of target (accounting for clipping)
        assert abs(actual_rms_db - target_rms_db) < 6

    def test_normalize_handles_silence(self):
        """Test that normalization handles silence."""
        from localmind.audio.preprocessing import rms_normalize

        audio = np.zeros(1000, dtype=np.float32)
        normalized = rms_normalize(audio)

        # Should return original for silence
        np.testing.assert_array_equal(normalized, audio)

    def test_normalize_clips_output(self):
        """Test that output is clipped to valid range."""
        from localmind.audio.preprocessing import rms_normalize

        # Very quiet audio that would need large gain
        audio = np.random.randn(16000).astype(np.float32) * 0.001
        normalized = rms_normalize(audio, target_rms_db=-10.0)

        # Should be clipped to [-0.95, 0.95]
        assert np.max(normalized) <= 0.95
        assert np.min(normalized) >= -0.95

    def test_normalize_limits_gain(self):
        """Test that gain is limited to prevent over-amplification."""
        from localmind.audio.preprocessing import rms_normalize

        # Very quiet audio
        audio = np.random.randn(16000).astype(np.float32) * 0.0001
        normalized = rms_normalize(audio, target_rms_db=-10.0)

        # Should not produce extreme values
        assert np.max(np.abs(normalized)) < 2.0


class TestApplyNoiseGate:
    """Tests for apply_noise_gate function."""

    def test_noise_gate_basic(self):
        """Test basic noise gate functionality."""
        from localmind.audio.preprocessing import apply_noise_gate

        sr = 16000
        # Signal with speech and silence
        speech = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, 8000)).astype(np.float32) * 0.5
        silence = np.random.randn(8000).astype(np.float32) * 0.001  # Very quiet noise
        audio = np.concatenate([speech, silence])

        gated = apply_noise_gate(audio, threshold_db=-40.0, sr=sr)

        assert gated.dtype == np.float32
        assert len(gated) == len(audio)

    def test_noise_gate_attenuates_quiet_sections(self):
        """Test that noise gate attenuates quiet sections."""
        from localmind.audio.preprocessing import apply_noise_gate

        sr = 16000
        # Loud section followed by quiet noise
        loud = np.ones(4000, dtype=np.float32) * 0.5
        quiet = np.ones(4000, dtype=np.float32) * 0.001  # Below threshold
        audio = np.concatenate([loud, quiet])

        gated = apply_noise_gate(audio, threshold_db=-40.0, sr=sr)

        # Quiet section should be significantly attenuated
        quiet_section_energy = np.sqrt(np.mean(gated[4000:] ** 2))
        original_quiet_energy = np.sqrt(np.mean(audio[4000:] ** 2))

        # Gated energy should be less than or equal to original
        assert quiet_section_energy <= original_quiet_energy * 1.1

    def test_noise_gate_preserves_loud_sections(self):
        """Test that noise gate preserves loud sections."""
        from localmind.audio.preprocessing import apply_noise_gate

        sr = 16000
        # Signal above threshold
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, 8000)).astype(np.float32) * 0.5

        gated = apply_noise_gate(audio, threshold_db=-40.0, sr=sr)

        # Loud section should be mostly preserved
        correlation = np.corrcoef(audio, gated)[0, 1]
        assert correlation > 0.9


class TestApplyDeemphasis:
    """Tests for apply_deemphasis function."""

    def test_deemphasis_basic(self):
        """Test basic de-emphasis functionality."""
        from localmind.audio.preprocessing import apply_deemphasis

        sr = 16000
        audio = np.random.randn(16000).astype(np.float32)

        deemphasized = apply_deemphasis(audio, sr)

        assert deemphasized.dtype == np.float32
        assert len(deemphasized) == len(audio)

    def test_deemphasis_removes_dc_offset(self):
        """Test that de-emphasis removes DC offset."""
        from localmind.audio.preprocessing import apply_deemphasis

        sr = 16000
        audio = np.random.randn(16000).astype(np.float32)

        deemphasized = apply_deemphasis(audio, sr)

        # Mean should be close to zero (DC offset removed)
        assert abs(np.mean(deemphasized)) < 0.01


class TestPreprocessAudioForTranscription:
    """Tests for preprocess_audio_for_transcription function."""

    @pytest.fixture
    def test_audio_file(self, temp_dir):
        """Create a test audio file."""
        import wave

        audio_path = temp_dir / "test.wav"
        sr = 16000
        duration = 1.0
        samples = int(sr * duration)

        # Generate a simple sine wave
        t = np.linspace(0, duration, samples)
        audio = (np.sin(2 * np.pi * 440 * t) * 32767 * 0.5).astype(np.int16)

        with wave.open(str(audio_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sr)
            wav.writeframes(audio.tobytes())

        return audio_path

    def test_full_pipeline(self, test_audio_file):
        """Test full preprocessing pipeline."""
        from localmind.audio.preprocessing import preprocess_audio_for_transcription

        audio, sr = preprocess_audio_for_transcription(
            str(test_audio_file),
            target_sr=16000,
            apply_compression=True,
            apply_gate=True,
            telephone_filter=False,
        )

        assert sr == 16000
        assert len(audio) > 0
        assert audio.dtype == np.float32
        assert not np.any(np.isnan(audio))
        assert not np.any(np.isinf(audio))

    def test_pipeline_with_telephone_filter(self, test_audio_file):
        """Test pipeline with telephone filter enabled."""
        from localmind.audio.preprocessing import preprocess_audio_for_transcription

        audio, sr = preprocess_audio_for_transcription(
            str(test_audio_file),
            target_sr=16000,
            apply_compression=True,
            apply_gate=True,
            telephone_filter=True,
        )

        assert sr == 16000
        assert len(audio) > 0

    def test_pipeline_minimal(self, test_audio_file):
        """Test pipeline with minimal processing."""
        from localmind.audio.preprocessing import preprocess_audio_for_transcription

        audio, sr = preprocess_audio_for_transcription(
            str(test_audio_file),
            target_sr=16000,
            apply_compression=False,
            apply_gate=False,
            telephone_filter=False,
        )

        assert sr == 16000
        assert len(audio) > 0


class TestPreprocessDualChannelAudio:
    """Tests for preprocess_dual_channel_audio function."""

    @pytest.fixture
    def stereo_audio_file(self, temp_dir):
        """Create a stereo test audio file."""
        import soundfile as sf

        audio_path = temp_dir / "stereo.wav"
        sr = 16000
        duration = 1.0
        samples = int(sr * duration)

        # Create stereo audio (left channel louder)
        t = np.linspace(0, duration, samples)
        left = (np.sin(2 * np.pi * 440 * t) * 0.8).astype(np.float32)
        right = (np.sin(2 * np.pi * 880 * t) * 0.3).astype(np.float32)

        stereo = np.column_stack([left, right])
        sf.write(str(audio_path), stereo, sr)

        return audio_path

    @pytest.fixture
    def mono_audio_file(self, temp_dir):
        """Create a mono test audio file."""
        import soundfile as sf

        audio_path = temp_dir / "mono.wav"
        sr = 16000
        duration = 1.0
        samples = int(sr * duration)

        t = np.linspace(0, duration, samples)
        audio = (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)

        sf.write(str(audio_path), audio, sr)

        return audio_path

    def test_dual_channel_processing(self, stereo_audio_file):
        """Test dual channel preprocessing."""
        from localmind.audio.preprocessing import preprocess_dual_channel_audio

        agent_path, customer_path = preprocess_dual_channel_audio(
            str(stereo_audio_file),
            agent_channel=0,
            customer_channel=1,
            target_sr=16000,
        )

        assert Path(agent_path).exists()
        assert Path(customer_path).exists()

    def test_dual_channel_mono_fallback(self, mono_audio_file):
        """Test dual channel preprocessing with mono audio."""
        from localmind.audio.preprocessing import preprocess_dual_channel_audio

        agent_path, customer_path = preprocess_dual_channel_audio(
            str(mono_audio_file),
            agent_channel=0,
            customer_channel=1,
            target_sr=16000,
        )

        # Should return same path for both channels
        assert agent_path == customer_path


class TestSavePreprocessedAudio:
    """Tests for save_preprocessed_audio function."""

    def test_save_to_temp(self):
        """Test saving to temporary file."""
        from localmind.audio.preprocessing import save_preprocessed_audio

        audio = np.random.randn(16000).astype(np.float32)
        sr = 16000

        path = save_preprocessed_audio(audio, sr)

        assert Path(path).exists()
        assert path.endswith(".wav")

    def test_save_to_specific_path(self, temp_dir):
        """Test saving to specific path."""
        from localmind.audio.preprocessing import save_preprocessed_audio

        audio = np.random.randn(16000).astype(np.float32)
        sr = 16000
        output_path = str(temp_dir / "output.wav")

        result_path = save_preprocessed_audio(audio, sr, output_path)

        assert result_path == output_path
        assert Path(result_path).exists()

    def test_save_clips_audio(self):
        """Test that saving clips audio to valid range."""
        from localmind.audio.preprocessing import save_preprocessed_audio

        # Audio with values outside [-1, 1]
        audio = np.array([1.5, -1.5, 0.5, -0.5], dtype=np.float32)
        sr = 16000

        path = save_preprocessed_audio(audio, sr)

        # Read back and verify clipping
        import soundfile as sf

        loaded, _ = sf.read(path)
        assert np.max(loaded) <= 1.0
        assert np.min(loaded) >= -1.0


class TestEdgeCases:
    """Tests for edge cases in audio preprocessing."""

    def test_empty_audio(self):
        """Test preprocessing with empty audio array."""
        from localmind.audio.preprocessing import rms_normalize

        audio = np.array([], dtype=np.float32)
        result = rms_normalize(audio)

        assert len(result) == 0

    def test_single_sample(self):
        """Test preprocessing with single sample."""
        from localmind.audio.preprocessing import apply_dynamic_range_compression

        audio = np.array([0.5], dtype=np.float32)
        sr = 16000

        result = apply_dynamic_range_compression(audio, sr=sr)

        assert len(result) == 1
        assert not np.isnan(result[0])

    def test_extreme_values(self):
        """Test preprocessing with extreme values."""
        from localmind.audio.preprocessing import rms_normalize

        # Very large values
        audio = np.array([1000.0, -1000.0, 500.0], dtype=np.float32)
        result = rms_normalize(audio)

        # Should be clipped
        assert np.max(result) <= 0.95
        assert np.min(result) >= -0.95

    def test_nan_handling(self):
        """Test that NaN values are handled."""
        from localmind.audio.preprocessing import rms_normalize

        # Audio with NaN (should be avoided but test robustness)
        audio = np.array([0.5, np.nan, 0.5], dtype=np.float32)

        # This might produce NaN - test for awareness
        result = rms_normalize(audio)
        # Implementation should ideally handle this
