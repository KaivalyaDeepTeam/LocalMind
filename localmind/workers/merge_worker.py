"""
LocalMind Merge Worker

Background worker for merging dual-channel transcripts using LLM.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any

from localmind.workers.base import BaseWorker
from localmind.workers.transcription_worker import TranscriptionResult


@dataclass
class MergedSegment:
    """A segment in the merged transcript."""

    start: float
    end: float
    speaker: str
    text: str
    original_segments: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start": self.start,
            "end": self.end,
            "speaker": self.speaker,
            "text": self.text,
        }


@dataclass
class MergeResult:
    """Result of transcript merging."""

    merged_text: str
    segments: list[MergedSegment] = field(default_factory=list)
    summary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "merged_text": self.merged_text,
            "segments": [s.to_dict() for s in self.segments],
            "summary": self.summary,
            "metadata": self.metadata,
        }


MERGE_SYSTEM_PROMPT = """You are an expert at merging dual-channel call transcripts.

Given transcripts from two channels (Agent and Customer), merge them into a coherent conversation.

Rules:
1. Maintain chronological order based on timestamps
2. Combine overlapping speech naturally
3. Remove duplicate content from cross-talk
4. Keep speaker labels accurate
5. Preserve the meaning and intent of both speakers
6. Clean up transcription artifacts (repeated words, filler sounds)

Output the merged transcript as a JSON object with this structure:
{
  "merged_text": "Full merged transcript as plain text with speaker labels",
  "segments": [
    {"start": 0.0, "end": 2.5, "speaker": "Agent", "text": "..."},
    {"start": 2.3, "end": 5.1, "speaker": "Customer", "text": "..."}
  ],
  "summary": "Brief 1-2 sentence summary of the conversation"
}"""


class MergeWorker(BaseWorker):
    """Worker for merging dual-channel transcripts."""

    def __init__(
        self,
        transcription: TranscriptionResult,
        parent=None,
    ):
        """Initialize merge worker.

        Args:
            transcription: Dual-channel transcription result.
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._transcription = transcription
        self._loop: asyncio.AbstractEventLoop | None = None

    def do_work(self) -> MergeResult:
        """Perform transcript merging."""
        self.report_progress(0, "Preparing transcript for merging...")

        if self.check_stop():
            return None

        # If single channel, just return as-is
        if self._transcription.channels == 1:
            self.report_progress(100, "Single channel - no merge needed")
            return self._single_channel_result()

        # Check if segments need LLM merging
        if self._is_simple_merge():
            self.report_progress(50, "Performing simple merge...")
            return self._simple_merge()

        # Use LLM for complex merging
        self.report_progress(20, "Initializing LLM for merge...")
        self.check_pause()

        if self.check_stop():
            return None

        # Run async LLM call in sync context
        self._loop = asyncio.new_event_loop()
        try:
            result = self._loop.run_until_complete(self._llm_merge())
        finally:
            self._loop.close()
            self._loop = None

        self.report_progress(100, "Merge complete")
        return result

    def _single_channel_result(self) -> MergeResult:
        """Create result for single-channel transcript."""
        segments = [
            MergedSegment(
                start=s.start,
                end=s.end,
                speaker=s.speaker or "Speaker",  # Use speaker from segment or default
                text=s.text,
            )
            for s in self._transcription.segments
        ]

        return MergeResult(
            merged_text=self._transcription.text,
            segments=segments,
        )

    def _is_simple_merge(self) -> bool:
        """Check if segments can be simply concatenated without LLM."""
        # Simple merge if no overlapping segments
        segments = sorted(self._transcription.segments, key=lambda s: s.start)

        for i in range(len(segments) - 1):
            current = segments[i]
            next_seg = segments[i + 1]
            # Check for significant overlap (more than 0.5 seconds)
            if current.end > next_seg.start + 0.5:
                return False

        return True

    def _simple_merge(self) -> MergeResult:
        """Perform simple chronological merge without LLM."""
        segments = sorted(self._transcription.segments, key=lambda s: s.start)

        merged_segments = [
            MergedSegment(
                start=s.start,
                end=s.end,
                speaker=s.speaker or "Speaker",  # Use speaker from segment or default
                text=s.text,
            )
            for s in segments
        ]

        merged_text = "\n".join(f"[{s.speaker}] {s.text}" for s in merged_segments)

        return MergeResult(
            merged_text=merged_text,
            segments=merged_segments,
        )

    async def _llm_merge(self) -> MergeResult:
        """Use LLM to merge overlapping segments."""
        from localmind.llm import LLMConfig, create_provider

        self.report_progress(30, "Loading LLM provider...")

        provider = create_provider()
        await provider.initialize()

        try:
            # Prepare transcript for LLM
            transcript_text = self._format_for_llm()

            self.report_progress(50, "Merging with LLM...")

            messages = [
                provider.create_system_message(MERGE_SYSTEM_PROMPT),
                provider.create_user_message(
                    f"Please merge this dual-channel transcript:\n\n{transcript_text}"
                ),
            ]

            config = LLMConfig(temperature=0.3, json_mode=True)
            response_data = await provider.generate_json(messages, config)

            self.report_progress(80, "Processing merge result...")

            # Parse response
            segments = [
                MergedSegment(
                    start=s["start"],
                    end=s["end"],
                    speaker=s["speaker"],
                    text=s["text"],
                )
                for s in response_data.get("segments", [])
            ]

            return MergeResult(
                merged_text=response_data.get("merged_text", ""),
                segments=segments,
                summary=response_data.get("summary"),
            )

        finally:
            await provider.close()

    def _format_for_llm(self) -> str:
        """Format transcript for LLM input."""
        lines = []
        for seg in self._transcription.segments:
            speaker = seg.speaker or "Speaker"
            lines.append(f"[{seg.start:.1f}s - {seg.end:.1f}s] [{speaker}]: {seg.text}")
        return "\n".join(lines)
