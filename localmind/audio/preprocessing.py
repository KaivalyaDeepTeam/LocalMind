"""
Professional Audio Preprocessing for Call Center Transcription

Handles critical issues in call recordings:
- Uneven speaker volumes (one quiet, one loud)
- Telephone bandwidth limitations (300-3400 Hz)
- Background noise and interference
- Compression artifacts
- AGC (Automatic Gain Control) variations

Optimized for Whisper and Hindi transcription models.
"""

import tempfile
from pathlib import Path

import numpy as np


def apply_telephone_bandpass(audio: np.ndarray, sr: int) -> np.ndarray:
    """
    Apply telephone bandwidth filter (300-3400 Hz).

    Call recordings are typically limited to telephone bandwidth.
    Filtering to this range removes out-of-band noise and focuses
    on the speech frequency range.

    Args:
        audio: Audio samples
        sr: Sample rate

    Returns:
        Bandpass-filtered audio
    """
    try:
        from scipy import signal

        # Telephone bandwidth: 300 Hz to 3400 Hz
        low_cutoff = 300
        high_cutoff = 3400

        # Design Butterworth bandpass filter
        sos = signal.butter(
            N=4, Wn=[low_cutoff, high_cutoff], btype="bandpass", fs=sr, output="sos"
        )

        # Apply filter
        filtered = signal.sosfilt(sos, audio)
        return filtered.astype(np.float32)

    except ImportError:
        # scipy not available, return original
        return audio


def apply_dynamic_range_compression(
    audio: np.ndarray,
    threshold: float = -20.0,
    ratio: float = 4.0,
    attack: float = 0.005,
    release: float = 0.1,
    sr: int = 16000,
) -> np.ndarray:
    """
    Apply dynamic range compression (DRC) to even out volume levels.

    Critical for call recordings where speakers have very different volumes.
    Brings quiet speakers up and loud speakers down.

    Args:
        audio: Audio samples
        threshold: Compression threshold in dB (default: -20 dB)
        ratio: Compression ratio (default: 4:1)
        attack: Attack time in seconds (default: 5ms)
        release: Release time in seconds (default: 100ms)
        sr: Sample rate

    Returns:
        Compressed audio
    """
    # Convert to dB
    audio_db = 20 * np.log10(np.abs(audio) + 1e-8)

    # Calculate envelope
    attack_samples = int(attack * sr)
    release_samples = int(release * sr)

    envelope = np.zeros_like(audio_db)
    envelope[0] = audio_db[0]

    for i in range(1, len(audio_db)):
        if audio_db[i] > envelope[i - 1]:
            # Attack
            alpha = 1.0 / attack_samples
        else:
            # Release
            alpha = 1.0 / release_samples

        envelope[i] = alpha * audio_db[i] + (1 - alpha) * envelope[i - 1]

    # Apply compression
    gain_db = np.zeros_like(envelope)
    mask = envelope > threshold
    gain_db[mask] = (threshold - envelope[mask]) * (1 - 1 / ratio)

    # Convert gain back to linear
    gain_linear = 10 ** (gain_db / 20)

    # Apply gain
    compressed = audio * gain_linear

    return compressed.astype(np.float32)


def rms_normalize(audio: np.ndarray, target_rms_db: float = -20.0) -> np.ndarray:
    """
    RMS normalization for consistent loudness.

    Args:
        audio: Audio samples
        target_rms_db: Target RMS level in dB (default: -20 dBFS)

    Returns:
        RMS-normalized audio
    """
    # Calculate current RMS
    current_rms = np.sqrt(np.mean(audio**2))

    if current_rms < 1e-8:  # Silence
        return audio

    # Convert target dB to linear
    target_rms_linear = 10 ** (target_rms_db / 20.0)

    # Calculate gain
    gain = target_rms_linear / current_rms

    # Limit gain to prevent over-amplification (max 20 dB boost)
    max_gain = 10.0  # 20 dB
    gain = min(gain, max_gain)

    # Apply gain
    normalized = audio * gain

    # Hard clip to [-1, 1] instead of tanh (tanh can distort speech)
    normalized = np.clip(normalized, -0.95, 0.95)

    return normalized.astype(np.float32)


def apply_noise_gate(
    audio: np.ndarray,
    threshold_db: float = -40.0,
    sr: int = 16000,
    attack: float = 0.001,
    release: float = 0.05,
) -> np.ndarray:
    """
    Apply noise gate to remove background noise during silence.

    Args:
        audio: Audio samples
        threshold_db: Gate threshold in dB
        sr: Sample rate
        attack: Attack time in seconds
        release: Release time in seconds

    Returns:
        Gated audio
    """
    # Convert to dB
    audio_db = 20 * np.log10(np.abs(audio) + 1e-8)

    # Calculate envelope
    attack_samples = int(attack * sr)
    release_samples = int(release * sr)

    envelope = np.zeros_like(audio_db)
    envelope[0] = audio_db[0]

    for i in range(1, len(audio_db)):
        if audio_db[i] > envelope[i - 1]:
            alpha = 1.0 / max(1, attack_samples)
        else:
            alpha = 1.0 / max(1, release_samples)

        envelope[i] = alpha * audio_db[i] + (1 - alpha) * envelope[i - 1]

    # Calculate gate gain
    gate_gain = np.zeros_like(envelope)
    gate_gain[envelope > threshold_db] = 1.0

    # Smooth transitions
    for i in range(1, len(gate_gain)):
        if gate_gain[i] != gate_gain[i - 1]:
            # Fade in/out over 5ms
            fade_samples = int(0.005 * sr)
            if i + fade_samples < len(gate_gain):
                if gate_gain[i] == 1.0:  # Fade in
                    gate_gain[i : i + fade_samples] = np.linspace(0, 1, fade_samples)
                else:  # Fade out
                    gate_gain[i : i + fade_samples] = np.linspace(1, 0, fade_samples)

    # Apply gate
    gated = audio * gate_gain

    return gated.astype(np.float32)


def apply_deemphasis(audio: np.ndarray, sr: int, alpha: float = 0.97) -> np.ndarray:
    """
    Apply de-emphasis filter to reduce high-frequency noise.

    Telephone systems often use pre-emphasis, this reverses it.

    Args:
        audio: Audio samples
        sr: Sample rate
        alpha: De-emphasis coefficient

    Returns:
        De-emphasized audio
    """
    # De-emphasis filter: y[n] = x[n] + alpha * y[n-1]
    deemphasized = np.zeros_like(audio)
    deemphasized[0] = audio[0]

    for i in range(1, len(audio)):
        deemphasized[i] = audio[i] + alpha * deemphasized[i - 1]

    # Normalize to prevent DC offset buildup
    deemphasized = deemphasized - np.mean(deemphasized)

    return deemphasized.astype(np.float32)


def preprocess_audio_for_transcription(
    audio_path: str,
    target_sr: int = 16000,
    apply_compression: bool = True,
    apply_gate: bool = True,
    telephone_filter: bool = False,  # Changed to False by default - too aggressive for MP3
) -> tuple[np.ndarray, int]:
    """
    Complete professional audio preprocessing pipeline for call recordings.

    Pipeline:
    1. Load and resample to 16kHz
    2. Apply telephone bandpass filter (300-3400 Hz) - OPTIONAL
    3. Apply noise gate (remove silence/noise)
    4. Apply dynamic range compression (even out volumes)
    5. RMS normalization (consistent loudness)

    Args:
        audio_path: Path to audio file
        target_sr: Target sample rate (16000 for Whisper)
        apply_compression: Enable dynamic range compression
        apply_gate: Enable noise gate
        telephone_filter: Enable telephone bandwidth filter (use for raw phone recordings only)

    Returns:
        Tuple of (processed_audio, sample_rate)
    """
    import librosa

    print("\nAudio Preprocessing Pipeline:")
    print(f"   Input: {Path(audio_path).name}")

    # 1. Load audio at target sample rate
    audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)
    duration = len(audio) / sr
    print(f"   [OK] Loaded: {duration:.1f}s @ {sr} Hz")

    # Check if audio is valid
    if len(audio) == 0 or np.max(np.abs(audio)) < 1e-6:
        print("   [WARNING] Audio is silent or empty!")
        return audio, sr

    # 2. Telephone bandpass filter (OPTIONAL - can be too aggressive for compressed audio)
    if telephone_filter:
        audio = apply_telephone_bandpass(audio, sr)
        print("   [OK] Telephone filter: 300-3400 Hz")

    # 3. Noise gate (remove background noise)
    if apply_gate:
        audio = apply_noise_gate(audio, threshold_db=-45.0, sr=sr)  # Gentler threshold
        print("   [OK] Noise gate: -45 dB threshold")

    # 4. Dynamic range compression (CRITICAL for uneven volumes)
    if apply_compression:
        audio = apply_dynamic_range_compression(
            audio, threshold=-20.0, ratio=3.0, sr=sr  # Gentler ratio (was 4.0)
        )
        print("   [OK] Compression: 3:1 ratio @ -20 dB")

    # 5. RMS normalization (final level adjustment)
    audio = rms_normalize(audio, target_rms_db=-16.0)  # Slightly louder target
    print("   [OK] RMS normalized: -16 dBFS")

    # Validate output
    final_rms_db = 20 * np.log10(np.sqrt(np.mean(audio**2)) + 1e-8)
    final_peak_db = 20 * np.log10(np.max(np.abs(audio)) + 1e-8)
    print(f"   [INFO] Final RMS: {final_rms_db:.1f} dB")
    print(f"   [INFO] Final Peak: {final_peak_db:.1f} dB")

    if np.isnan(audio).any() or np.isinf(audio).any():
        print("   [ERROR] Preprocessed audio contains NaN or Inf values!")
        # Return original audio
        audio, sr = librosa.load(audio_path, sr=target_sr, mono=True)
        return audio, sr

    print()
    return audio, sr


def preprocess_dual_channel_audio(
    audio_path: str,
    agent_channel: int = 0,
    customer_channel: int = 1,
    target_sr: int = 16000,
) -> tuple[str, str]:
    """
    Preprocess stereo audio with independent normalization per channel.

    CRITICAL: Each speaker needs separate processing because they often
    have vastly different volume levels in call recordings.

    Args:
        audio_path: Path to stereo audio file
        agent_channel: Channel for agent (0=left, 1=right)
        customer_channel: Channel for customer
        target_sr: Target sample rate

    Returns:
        Tuple of (agent_audio_path, customer_audio_path)
    """
    import librosa
    import soundfile as sf

    print("\nDual-Channel Preprocessing:")

    # Load stereo audio
    audio, sr = librosa.load(audio_path, sr=target_sr, mono=False)

    if audio.ndim == 1:
        # Mono audio - process once and duplicate
        print("   ⚠️  Mono audio detected, processing as single channel")
        processed, sr = preprocess_audio_for_transcription(audio_path, target_sr)

        temp_dir = tempfile.gettempdir()
        path = str(Path(temp_dir) / "preprocessed_mono.wav")
        sf.write(path, processed, sr)

        return path, path

    # Extract channels
    agent_audio = audio[agent_channel]
    customer_audio = audio[customer_channel]

    print(f"   Agent: Channel {agent_channel}")
    print(f"   Customer: Channel {customer_channel}")

    # Process each channel INDEPENDENTLY
    print("\n   Processing Agent Channel:")
    agent_audio = apply_telephone_bandpass(agent_audio, sr)
    agent_audio = apply_noise_gate(agent_audio, threshold_db=-40.0, sr=sr)
    agent_audio = apply_dynamic_range_compression(agent_audio, threshold=-20.0, ratio=4.0, sr=sr)
    agent_audio = apply_deemphasis(agent_audio, sr)
    agent_audio = rms_normalize(agent_audio, target_rms_db=-20.0)
    print(f"   [OK] Agent RMS: {20*np.log10(np.sqrt(np.mean(agent_audio**2)) + 1e-8):.1f} dB")

    print("\n   Processing Customer Channel:")
    customer_audio = apply_telephone_bandpass(customer_audio, sr)
    customer_audio = apply_noise_gate(customer_audio, threshold_db=-40.0, sr=sr)
    customer_audio = apply_dynamic_range_compression(
        customer_audio, threshold=-20.0, ratio=4.0, sr=sr
    )
    customer_audio = apply_deemphasis(customer_audio, sr)
    customer_audio = rms_normalize(customer_audio, target_rms_db=-20.0)
    print(
        f"   [OK] Customer RMS: {20*np.log10(np.sqrt(np.mean(customer_audio**2)) + 1e-8):.1f} dB\n"
    )

    # Save to temp files
    temp_dir = tempfile.gettempdir()
    agent_path = str(Path(temp_dir) / "agent_preprocessed.wav")
    customer_path = str(Path(temp_dir) / "customer_preprocessed.wav")

    # Ensure audio is float32 and in valid range [-1, 1]
    agent_audio = np.clip(agent_audio, -1.0, 1.0).astype(np.float32)
    customer_audio = np.clip(customer_audio, -1.0, 1.0).astype(np.float32)

    sf.write(agent_path, agent_audio, sr, subtype="FLOAT")
    sf.write(customer_path, customer_audio, sr, subtype="FLOAT")

    return agent_path, customer_path


def save_preprocessed_audio(audio: np.ndarray, sr: int, output_path: str | None = None) -> str:
    """
    Save preprocessed audio to file.

    Args:
        audio: Preprocessed audio samples
        sr: Sample rate
        output_path: Output file path (None for temp file)

    Returns:
        Path to saved file
    """
    import soundfile as sf

    if output_path is None:
        temp_dir = tempfile.gettempdir()
        output_path = str(Path(temp_dir) / "preprocessed_audio.wav")

    # Ensure audio is float32 and in valid range [-1, 1]
    audio = np.clip(audio, -1.0, 1.0).astype(np.float32)
    sf.write(output_path, audio, sr, subtype="FLOAT")
    return output_path
