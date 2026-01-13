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
    speaker: Optional[str] = None
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
        parent=None,
    ):
        """Initialize transcription worker.

        Args:
            audio_path: Path to audio file.
            model_name: Whisper model name.
            language: Language code or None for auto-detect.
            use_gpu: Whether to use GPU acceleration.
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._model_name = model_name
        self._language = language
        self._use_gpu = use_gpu
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
        audio = self._load_audio()

        self.report_progress(20, "Transcribing audio...")
        self.check_pause()

        if self.check_stop():
            return None

        # Transcribe
        result = self._transcribe(audio)

        self.report_progress(90, "Processing results...")

        # Build result
        segments = []
        for seg in result.get("segments", []):
            segments.append(TranscriptionSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
            ))

        transcription = TranscriptionResult(
            text=result["text"].strip(),
            segments=segments,
            language=result.get("language"),
            duration=audio.shape[-1] / 16000 if hasattr(audio, "shape") else 0,
        )

        self.report_progress(100, "Transcription complete")
        return transcription

    def _load_model(self) -> None:
        """Load the Whisper model."""
        try:
            import whisper
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. Install with: pip install openai-whisper"
            )

        device = "cuda" if self._use_gpu else "cpu"

        # Check for MPS (Apple Silicon)
        try:
            import torch
            if torch.backends.mps.is_available() and self._use_gpu:
                device = "mps"
        except (ImportError, AttributeError):
            pass

        self._model = whisper.load_model(self._model_name, device=device)

    def _load_audio(self):
        """Load audio file."""
        import whisper
        return whisper.load_audio(str(self._audio_path))

    def _transcribe(self, audio) -> Dict[str, Any]:
        """Transcribe audio with progress updates."""
        options = {}
        if self._language and self._language != "auto":
            options["language"] = self._language

        # Transcribe with verbose=False to avoid cluttering output
        result = self._model.transcribe(
            audio,
            verbose=False,
            **options,
        )

        return result


class DualChannelTranscriptionWorker(BaseWorker):
    """Worker for transcribing dual-channel (stereo) audio with speaker diarization."""

    def __init__(
        self,
        audio_path: str,
        model_name: str = "large-v3",
        language: Optional[str] = None,
        use_gpu: bool = True,
        agent_channel: int = 0,
        customer_channel: int = 1,
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
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._model_name = model_name
        self._language = language
        self._use_gpu = use_gpu
        self._agent_channel = agent_channel
        self._customer_channel = customer_channel
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
                speaker="Agent",
            ))

        for seg in customer_result.get("segments", []):
            all_segments.append(TranscriptionSegment(
                start=seg["start"],
                end=seg["end"],
                text=seg["text"].strip(),
                speaker="Customer",
            ))

        # Sort by start time
        all_segments.sort(key=lambda s: s.start)

        # Build full text
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
        try:
            import whisper
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. Install with: pip install openai-whisper"
            )

        device = "cuda" if self._use_gpu else "cpu"

        try:
            import torch
            if torch.backends.mps.is_available() and self._use_gpu:
                device = "mps"
        except (ImportError, AttributeError):
            pass

        self._model = whisper.load_model(self._model_name, device=device)

    def _load_channels(self):
        """Load separate audio channels."""
        try:
            import librosa
            import numpy as np
        except ImportError:
            raise ImportError(
                "librosa not installed. Install with: pip install librosa"
            )

        # Load stereo audio
        audio, sr = librosa.load(str(self._audio_path), sr=16000, mono=False)

        if audio.ndim == 1:
            # Mono audio - duplicate to both channels
            return audio, audio

        # Extract channels
        agent_audio = audio[self._agent_channel]
        customer_audio = audio[self._customer_channel]

        return agent_audio, customer_audio

    def _transcribe_channel(self, audio, speaker: str) -> Dict[str, Any]:
        """Transcribe a single channel."""
        import whisper

        options = {}
        if self._language and self._language != "auto":
            options["language"] = self._language

        # Pad/trim audio for Whisper
        audio = whisper.pad_or_trim(audio)

        result = self._model.transcribe(
            audio,
            verbose=False,
            **options,
        )

        return result
