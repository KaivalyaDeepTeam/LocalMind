"""
LocalMind Speaker Diarization Worker

Real speaker diarization using pyannote.audio for detecting who speaks when.
Works with both mono and stereo audio files.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

from localmind.workers.base import BaseWorker


@dataclass
class SpeakerSegment:
    """A segment with speaker label."""
    start: float
    end: float
    speaker: str  # "SPEAKER_00", "SPEAKER_01", etc.


class DiarizationResult:
    """Result of speaker diarization."""
    def __init__(self, segments: List[SpeakerSegment], num_speakers: int):
        self.segments = segments
        self.num_speakers = num_speakers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segments": [
                {"start": s.start, "end": s.end, "speaker": s.speaker}
                for s in self.segments
            ],
            "num_speakers": self.num_speakers,
        }


class DiarizationWorker(BaseWorker):
    """Worker for speaker diarization using pyannote.audio."""

    def __init__(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
        min_speakers: int = 1,
        max_speakers: int = 10,
        use_gpu: bool = True,
        parent=None,
    ):
        """Initialize diarization worker.

        Args:
            audio_path: Path to audio file.
            num_speakers: Fixed number of speakers (None for auto-detection).
            min_speakers: Minimum number of speakers for auto-detection.
            max_speakers: Maximum number of speakers for auto-detection.
            use_gpu: Whether to use GPU acceleration.
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._audio_path = Path(audio_path)
        self._num_speakers = num_speakers
        self._min_speakers = min_speakers
        self._max_speakers = max_speakers
        self._use_gpu = use_gpu
        self._pipeline = None

    def do_work(self) -> DiarizationResult:
        """Perform speaker diarization."""
        self.report_progress(0, "Loading diarization model...")

        if self.check_stop():
            return None

        # Load pipeline
        self._load_pipeline()

        self.report_progress(20, "Detecting speakers...")
        self.check_pause()

        if self.check_stop():
            return None

        # Run diarization
        diarization = self._pipeline(
            str(self._audio_path),
            num_speakers=self._num_speakers,
            min_speakers=self._min_speakers,
            max_speakers=self._max_speakers,
        )

        self.report_progress(80, "Processing speaker segments...")

        # Convert to our format
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(SpeakerSegment(
                start=turn.start,
                end=turn.end,
                speaker=speaker,
            ))

        num_speakers = len(set(seg.speaker for seg in segments))

        self.report_progress(100, "Diarization complete")
        return DiarizationResult(segments=segments, num_speakers=num_speakers)

    def _load_pipeline(self) -> None:
        """Load the pyannote.audio pipeline with auto-download and caching."""
        try:
            from pyannote.audio import Pipeline
        except ImportError:
            raise ImportError(
                "pyannote.audio not installed. Install with: "
                "pip install pyannote.audio"
            )

        try:
            import torch
        except ImportError:
            raise ImportError("torch not installed")

        import os
        from pathlib import Path

        # Determine device
        if self._use_gpu:
            if torch.cuda.is_available():
                device = torch.device("cuda")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = torch.device("mps")
            else:
                device = torch.device("cpu")
        else:
            device = torch.device("cpu")

        self.report_progress(5, "Checking diarization model...")

        # Check for HuggingFace token
        hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

        # Try to use cached model first, then download if needed
        try:
            self.report_progress(10, f"Loading diarization model on {device}...")

            # Use token if available, otherwise rely on cached login
            auth_token = hf_token if hf_token else True  # True uses cached credentials

            self._pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=auth_token,
            )

            self._pipeline.to(device)
            self.report_progress(18, "Diarization model loaded")

        except Exception as e:
            error_msg = str(e)

            # Provide helpful error message if authentication fails
            if "401" in error_msg or "authentication" in error_msg.lower() or "token" in error_msg.lower():
                raise RuntimeError(
                    "Diarization model requires HuggingFace authentication.\n\n"
                    "One-time setup:\n"
                    "1. Create account at https://huggingface.co (free)\n"
                    "2. Accept terms at https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                    "3. Get token from https://huggingface.co/settings/tokens\n"
                    "4. Login with: huggingface-cli login\n"
                    "   OR set environment variable: export HF_TOKEN=your_token_here\n\n"
                    "After first login, the model will be cached for offline use."
                )
            else:
                raise RuntimeError(f"Failed to load diarization model: {error_msg}")


def combine_diarization_with_transcription(
    transcription_segments: List[Dict[str, Any]],
    diarization_segments: List[SpeakerSegment],
) -> List[Dict[str, Any]]:
    """
    Combine transcription segments with speaker labels from diarization.

    Args:
        transcription_segments: List of transcription segments with start, end, text.
        diarization_segments: List of speaker segments from diarization.

    Returns:
        List of segments with speaker labels assigned.
    """
    result = []

    for trans_seg in transcription_segments:
        start = trans_seg["start"]
        end = trans_seg["end"]
        text = trans_seg["text"]

        # Find the most overlapping speaker for this segment
        best_speaker = "Unknown"
        max_overlap = 0

        for diar_seg in diarization_segments:
            # Calculate overlap
            overlap_start = max(start, diar_seg.start)
            overlap_end = min(end, diar_seg.end)
            overlap = max(0, overlap_end - overlap_start)

            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = diar_seg.speaker

        result.append({
            "start": start,
            "end": end,
            "text": text,
            "speaker": best_speaker,
        })

    return result
