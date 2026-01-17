"""
LocalMind Transcription Worker

Background worker for audio transcription using Whisper.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from localmind.workers.base import BaseWorker


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio."""
    start: float
    end: float
    text: str
    speaker: Optional[str] = None  # Populated from channel info for dual-channel audio
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "speaker": self.speaker,
            "confidence": self.confidence,
        }


@dataclass
class TranscriptionResult:
    """Result of transcription."""
    text: str
    segments: List[TranscriptionSegment] = field(default_factory=list)
    language: Optional[str] = None
    duration: float = 0.0
    channels: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "segments": [s.to_dict() for s in self.segments],
            "language": self.language,
            "duration": self.duration,
            "channels": self.channels,
        }


class TranscriptionWorker(BaseWorker):
    """Worker for transcribing audio files."""

    def __init__(
        self,
        audio_path: str,
        model_name: str = "large-v3",
        language: Optional[str] = None,
        use_gpu: bool = True,
        use_preprocessing: bool = True,
        parent=None,
    ):
        """Initialize transcription worker.

        Args:
            audio_path: Path to audio file.
            model_name: Whisper model name.
            language: Language code or None for auto-detect.
            use_gpu: Whether to use GPU acceleration.
            use_preprocessing: Apply audio preprocessing (volume leveling, noise reduction).
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._model_name = model_name
        self._language = language
        self._use_gpu = use_gpu
        self._use_preprocessing = use_preprocessing
        self._model = None

    def do_work(self) -> TranscriptionResult:
        """Perform transcription."""
        self.report_progress(0, "Loading Whisper model...")

        if self.check_stop():
            return None

        # Load model
        self._load_model()

        self.report_progress(10, "Loading audio file...")
        self.check_pause()

        if self.check_stop():
            return None

        # Load and preprocess audio
        audio, sr = self._load_audio()

        self.report_progress(15, "Transcribing audio...")
        self.check_pause()

        if self.check_stop():
            return None

        # Transcribe with chunking
        result = self._transcribe(audio, sr)

        self.report_progress(90, "Processing results...")

        # Build single segment from chunked transcription
        full_text = result.get("text", "").strip()
        segments = []

        if full_text:
            segments.append(TranscriptionSegment(
                start=0.0,
                end=len(audio) / sr,
                text=full_text,
            ))

        transcription = TranscriptionResult(
            text=full_text,
            segments=segments,
            language=result.get("language"),
            duration=len(audio) / sr,
        )

        self.report_progress(100, "Transcription complete")
        return transcription

    def _load_model(self) -> None:
        """Load the Whisper model."""
        import os

        try:
            import torch
            import whisper
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. Install with: pip install openai-whisper"
            )

        self._device = "cpu"  # Default to CPU

        # Check for GPU availability
        if self._use_gpu:
            if torch.cuda.is_available():
                self._device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self._device = "mps"  # Apple Silicon GPU
            else:
                self._device = "cpu"

        # Patch torch.load to handle CUDA-saved models on non-CUDA devices
        original_load = torch.load
        def patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = torch.device(self._device)
            return original_load(*args, **kwargs)
        torch.load = patched_load

        try:
            self._model = whisper.load_model(self._model_name, device=self._device)
        finally:
            torch.load = original_load

    def _load_audio(self):
        """Load and optionally preprocess audio file."""
        import numpy as np

        # Apply preprocessing if enabled
        if self._use_preprocessing:
            from localmind.audio.preprocessing import preprocess_audio_for_transcription

            try:
                processed_audio, sr = preprocess_audio_for_transcription(
                    str(self._audio_path),
                    target_sr=16000,
                    apply_compression=True,  # Critical for volume leveling
                    apply_gate=True,
                    telephone_filter=False,  # Disabled - too aggressive for MP3/compressed audio
                )
                return processed_audio.astype(np.float32), sr
            except Exception as e:
                print(f"Warning: Audio preprocessing failed ({e}), using original audio")

        # No preprocessing or preprocessing failed - use original audio
        import librosa
        audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=True)
        return audio, sr

    def _transcribe(self, audio, sr) -> Dict[str, Any]:
        """Transcribe audio with chunking and optimized parameters."""
        import numpy as np
        import torch
        import whisper

        # Chunk audio with 5-second overlap for better boundary handling
        chunk_duration = 25  # seconds (< 30s limit)
        overlap_duration = 5  # seconds overlap
        stride_duration = chunk_duration - overlap_duration  # 20 seconds

        chunk_samples = chunk_duration * sr
        stride_samples = stride_duration * sr
        total_samples = len(audio)

        # Calculate number of chunks with overlap
        num_chunks = max(1, int(np.ceil((total_samples - chunk_samples) / stride_samples)) + 1)

        print(f"Processing audio in {num_chunks} chunks (25s each, 5s overlap)...")

        all_text = []
        previous_text_end = ""  # Store end of previous chunk for deduplication
        detected_lang = None  # Will be set from first successful chunk

        for i in range(num_chunks):
            # Calculate chunk boundaries with overlap
            start_sample = i * stride_samples
            end_sample = min(start_sample + chunk_samples, total_samples)

            # For the last chunk, make sure we get all remaining audio
            if i == num_chunks - 1:
                end_sample = total_samples

            chunk = audio[start_sample:end_sample]

            # Pad chunk to 30 seconds (Whisper requirement)
            target_length = 30 * sr
            if len(chunk) < target_length:
                padding = target_length - len(chunk)
                chunk = np.pad(chunk, (0, padding), mode='constant', constant_values=0)

            # Transcribe chunk with optimized parameters
            progress = 20 + int((i / num_chunks) * 70)
            self.report_progress(progress, f"Transcribing chunk {i+1}/{num_chunks}...")

            try:
                # Transcribe options with optimized parameters
                transcribe_options = {
                    "verbose": False,
                    "fp16": self._device == "cuda",  # Only use fp16 on CUDA, not MPS (causes NaN errors)
                    # CRITICAL parameters for maximum word capture
                    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                    "no_speech_threshold": 0.3,  # CRITICAL for quiet speakers
                    "compression_ratio_threshold": 2.4,
                    "logprob_threshold": -1.0,
                    "condition_on_previous_text": False,
                }

                # Add language if specified
                if self._language and self._language != "auto":
                    transcribe_options["language"] = self._language

                # Transcribe chunk
                with torch.no_grad():
                    result = self._model.transcribe(chunk, **transcribe_options)

                text = result["text"].strip()

                # Store detected language from first successful chunk
                if detected_lang is None and "language" in result:
                    detected_lang = result["language"]

                if text:
                    if i == 0:
                        # First chunk - keep everything
                        all_text.append(text)
                        words = text.split()
                        previous_text_end = " ".join(words[-10:]) if len(words) > 10 else text
                    else:
                        # Subsequent chunks - deduplicate overlap
                        words = text.split()
                        deduplicated = False

                        # Try to find overlap by checking first N words against previous chunk's end
                        for overlap_words in range(min(15, len(words)), 0, -1):
                            chunk_start = " ".join(words[:overlap_words])
                            if chunk_start in previous_text_end:
                                # Found overlap - skip these words
                                remaining_text = " ".join(words[overlap_words:])
                                if remaining_text:
                                    all_text.append(remaining_text)
                                    remaining_words = remaining_text.split()
                                    previous_text_end = " ".join(remaining_words[-10:]) if len(remaining_words) > 10 else remaining_text
                                deduplicated = True
                                break

                        if not deduplicated:
                            # No clear overlap found - keep all
                            all_text.append(text)
                            previous_text_end = " ".join(words[-10:]) if len(words) > 10 else text

            except Exception as e:
                print(f"Warning: Chunk {i} failed ({e}), skipping")

        # Combine all chunks
        full_text = " ".join(all_text)

        # Determine language (from detection or user setting)
        final_lang = detected_lang if detected_lang else self._language

        return {
            "text": full_text,
            "language": final_lang,
        }


class DualChannelTranscriptionWorker(BaseWorker):
    """Worker for transcribing dual-channel (stereo) audio with separate channel processing."""

    def __init__(
        self,
        audio_path: str,
        model_name: str = "large-v3",
        language: Optional[str] = None,
        use_gpu: bool = True,
        agent_channel: int = 0,
        customer_channel: int = 1,
        use_preprocessing: bool = True,
        parent=None,
    ):
        """Initialize dual-channel transcription worker.

        Args:
            audio_path: Path to audio file.
            model_name: Whisper model name.
            language: Language code or None for auto-detect.
            use_gpu: Whether to use GPU acceleration.
            agent_channel: Channel index for agent audio.
            customer_channel: Channel index for customer audio.
            use_preprocessing: Apply audio preprocessing (volume leveling, noise reduction).
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._model_name = model_name
        self._language = language
        self._use_gpu = use_gpu
        self._agent_channel = agent_channel
        self._customer_channel = customer_channel
        self._use_preprocessing = use_preprocessing
        self._model = None

    def do_work(self) -> TranscriptionResult:
        """Perform dual-channel transcription."""
        self.report_progress(0, "Loading Whisper model...")

        if self.check_stop():
            return None

        # Load model
        self._load_model()

        self.report_progress(10, "Loading audio channels...")
        self.check_pause()

        if self.check_stop():
            return None

        # Load audio channels
        agent_audio, customer_audio = self._load_channels()

        # Transcribe agent channel
        self.report_progress(20, "Transcribing agent channel...")
        self.check_pause()

        if self.check_stop():
            return None

        agent_result = self._transcribe_channel(agent_audio, "Agent")

        # Transcribe customer channel
        self.report_progress(50, "Transcribing customer channel...")
        self.check_pause()

        if self.check_stop():
            return None

        customer_result = self._transcribe_channel(customer_audio, "Customer")

        # Merge and sort segments
        self.report_progress(80, "Merging transcripts...")

        all_segments = []
        for seg in agent_result.get("segments", []):
            all_segments.append(TranscriptionSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
                speaker="Agent",  # Assigned from channel 0
            ))

        for seg in customer_result.get("segments", []):
            all_segments.append(TranscriptionSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
                speaker="Customer",  # Assigned from channel 1
            ))

        # Sort by start time
        all_segments.sort(key=lambda s: s.start)

        # Build full text - chronological with speaker labels
        full_text = "\n".join(
            f"[{s.speaker}] {s.text}" for s in all_segments
        )

        transcription = TranscriptionResult(
            text=full_text,
            segments=all_segments,
            language=agent_result.get("language"),
            channels=2,
        )

        self.report_progress(100, "Dual-channel transcription complete")
        return transcription

    def _load_model(self) -> None:
        """Load the Whisper model."""
        import os

        try:
            import torch
            import whisper
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. Install with: pip install openai-whisper"
            )

        device = "cpu"  # Default to CPU

        # Check for GPU availability
        if self._use_gpu:
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"  # Apple Silicon GPU
            else:
                device = "cpu"

        # Patch torch.load to handle CUDA-saved models on non-CUDA devices
        original_load = torch.load
        def patched_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = torch.device(device)
            return original_load(*args, **kwargs)
        torch.load = patched_load

        try:
            self._model = whisper.load_model(self._model_name, device=device)
        finally:
            torch.load = original_load

    def _load_channels(self):
        """Load and optionally preprocess separate audio channels with independent normalization."""
        import librosa
        import numpy as np

        try:
            # Check if audio is stereo
            audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=False)
            is_stereo = audio.ndim == 2
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {e}")

        # Apply preprocessing if enabled
        if self._use_preprocessing:
            from localmind.audio.preprocessing import (
                preprocess_dual_channel_audio,
                preprocess_audio_for_transcription,
            )
            import soundfile as sf
            import tempfile
            from pathlib import Path

            if not is_stereo:
                # Mono audio - preprocess once and return for both channels
                try:
                    processed_audio, sr = preprocess_audio_for_transcription(
                        str(self._audio_path),
                        target_sr=16000,
                        apply_compression=True,
                        apply_gate=True,
                        telephone_filter=False,  # Disabled - too aggressive for MP3/compressed audio
                    )
                    return processed_audio, processed_audio
                except Exception as e:
                    print(f"Warning: Audio preprocessing failed ({e}), using original audio")

            else:
                # Stereo audio - preprocess each channel independently (CRITICAL for uneven volumes)
                try:
                    agent_path, customer_path = preprocess_dual_channel_audio(
                        str(self._audio_path),
                        agent_channel=self._agent_channel,
                        customer_channel=self._customer_channel,
                        target_sr=16000,
                    )

                    # Load preprocessed audio
                    agent_audio, _ = sf.read(agent_path)
                    customer_audio, _ = sf.read(customer_path)
                    return agent_audio, customer_audio

                except Exception as e:
                    print(f"Warning: Dual-channel preprocessing failed ({e}), using basic channel split")

        # No preprocessing or preprocessing failed - basic channel extraction
        if not is_stereo:
            # Mono audio - duplicate to both channels
            return audio, audio

        # Stereo - extract channels
        agent_audio = audio[self._agent_channel]
        customer_audio = audio[self._customer_channel]
        return agent_audio, customer_audio

    def _transcribe_channel(self, audio, speaker: str) -> Dict[str, Any]:
        """Transcribe a single channel."""
        import torch
        import whisper

        # Determine device for fp16 setting
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"

        options = {
            "verbose": False,
            "fp16": device == "cuda",  # Only use fp16 on CUDA, not MPS (causes NaN errors)
        }

        if self._language and self._language != "auto":
            options["language"] = self._language

        # Pad/trim audio for Whisper
        audio = whisper.pad_or_trim(audio)

        result = self._model.transcribe(audio, **options)

        return result
