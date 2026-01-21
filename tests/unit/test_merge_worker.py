"""
Tests for MergeWorker execution logic.

Tests the merge worker's do_work method including simple merge
and LLM-based merge scenarios.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from localmind.workers.merge_worker import (
    MERGE_SYSTEM_PROMPT,
    MergedSegment,
    MergeResult,
    MergeWorker,
)
from localmind.workers.transcription_worker import TranscriptionResult, TranscriptionSegment


class TestMergedSegment:
    """Tests for MergedSegment dataclass."""

    def test_segment_creation(self):
        """Test creating a merged segment."""
        segment = MergedSegment(
            start=0.0,
            end=5.0,
            speaker="Agent",
            text="Hello, how can I help you?",
        )
        assert segment.start == 0.0
        assert segment.end == 5.0
        assert segment.speaker == "Agent"
        assert segment.text == "Hello, how can I help you?"

    def test_segment_to_dict(self):
        """Test segment to_dict conversion."""
        segment = MergedSegment(
            start=1.0,
            end=3.5,
            speaker="Customer",
            text="I need help",
        )
        result = segment.to_dict()
        assert result["start"] == 1.0
        assert result["end"] == 3.5
        assert result["speaker"] == "Customer"
        assert result["text"] == "I need help"

    def test_segment_with_original_segments(self):
        """Test segment with original segments tracking."""
        original = [{"start": 1.0, "end": 2.0, "text": "Original"}]
        segment = MergedSegment(
            start=1.0,
            end=3.0,
            speaker="Agent",
            text="Merged text",
            original_segments=original,
        )
        assert len(segment.original_segments) == 1


class TestMergeResult:
    """Tests for MergeResult dataclass."""

    def test_result_creation(self):
        """Test creating a merge result."""
        segments = [
            MergedSegment(start=0.0, end=2.0, speaker="Agent", text="Hello"),
            MergedSegment(start=2.0, end=4.0, speaker="Customer", text="Hi"),
        ]
        result = MergeResult(
            merged_text="[Agent] Hello\n[Customer] Hi",
            segments=segments,
            summary="Brief conversation",
        )
        assert "[Agent] Hello" in result.merged_text
        assert len(result.segments) == 2
        assert result.summary == "Brief conversation"

    def test_result_to_dict(self):
        """Test result to_dict conversion."""
        segments = [MergedSegment(start=0.0, end=1.0, speaker="Agent", text="Test")]
        result = MergeResult(
            merged_text="[Agent] Test",
            segments=segments,
            summary="Test summary",
            metadata={"key": "value"},
        )
        d = result.to_dict()
        assert d["merged_text"] == "[Agent] Test"
        assert len(d["segments"]) == 1
        assert d["summary"] == "Test summary"
        assert d["metadata"] == {"key": "value"}

    def test_result_default_values(self):
        """Test result default values."""
        result = MergeResult(merged_text="Test")
        assert result.segments == []
        assert result.summary is None
        assert result.metadata == {}


class TestMergeSystemPrompt:
    """Tests for merge system prompt."""

    def test_system_prompt_content(self):
        """Test that system prompt has required instructions."""
        assert "dual-channel call transcripts" in MERGE_SYSTEM_PROMPT
        assert "chronological order" in MERGE_SYSTEM_PROMPT
        assert "speaker labels" in MERGE_SYSTEM_PROMPT
        assert "JSON" in MERGE_SYSTEM_PROMPT


class TestMergeWorkerInit:
    """Tests for MergeWorker initialization."""

    def test_worker_initialization(self, qapp):
        """Test worker initialization."""
        transcription = TranscriptionResult(
            text="Test text",
            segments=[],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)

        assert worker._transcription == transcription
        assert worker._loop is None

    def test_worker_single_channel(self, qapp):
        """Test worker with single channel transcription."""
        transcription = TranscriptionResult(
            text="Test text",
            segments=[],
            channels=1,
        )
        worker = MergeWorker(transcription=transcription)
        assert worker._transcription.channels == 1


class TestMergeWorkerDoWork:
    """Tests for MergeWorker.do_work() method."""

    @pytest.fixture
    def single_channel_transcription(self):
        """Create single channel transcription."""
        return TranscriptionResult(
            text="Hello, thank you for calling.",
            segments=[
                TranscriptionSegment(
                    start=0.0,
                    end=3.0,
                    text="Hello, thank you for calling.",
                    speaker="Agent",
                )
            ],
            language="en",
            duration=3.0,
            channels=1,
        )

    @pytest.fixture
    def dual_channel_transcription(self):
        """Create dual channel transcription without overlap."""
        return TranscriptionResult(
            text="[Agent] Hello\n[Customer] Hi",
            segments=[
                TranscriptionSegment(
                    start=0.0,
                    end=2.0,
                    text="Hello, how can I help?",
                    speaker="Agent",
                ),
                TranscriptionSegment(
                    start=2.5,
                    end=4.0,
                    text="I need help with my order.",
                    speaker="Customer",
                ),
                TranscriptionSegment(
                    start=4.5,
                    end=6.0,
                    text="Sure, let me check that.",
                    speaker="Agent",
                ),
            ],
            language="en",
            duration=6.0,
            channels=2,
        )

    @pytest.fixture
    def overlapping_transcription(self):
        """Create dual channel transcription with overlap."""
        return TranscriptionResult(
            text="Overlapping segments",
            segments=[
                TranscriptionSegment(
                    start=0.0,
                    end=3.0,
                    text="Hello, how can I help you today?",
                    speaker="Agent",
                ),
                TranscriptionSegment(
                    start=2.0,  # Overlaps with previous segment
                    end=5.0,
                    text="I'm calling about my order that...",
                    speaker="Customer",
                ),
            ],
            language="en",
            duration=5.0,
            channels=2,
        )

    def test_do_work_single_channel(self, qapp, single_channel_transcription):
        """Test merge with single channel returns as-is."""
        worker = MergeWorker(transcription=single_channel_transcription)
        result = worker.do_work()

        assert result is not None
        assert isinstance(result, MergeResult)
        assert result.merged_text == single_channel_transcription.text
        assert len(result.segments) == 1

    def test_do_work_stop_requested(self, qapp, dual_channel_transcription):
        """Test worker stops when stop is requested."""
        worker = MergeWorker(transcription=dual_channel_transcription)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_do_work_simple_merge(self, qapp, dual_channel_transcription):
        """Test simple merge without LLM (no overlap)."""
        worker = MergeWorker(transcription=dual_channel_transcription)
        result = worker.do_work()

        assert result is not None
        assert isinstance(result, MergeResult)
        assert len(result.segments) == 3
        # Segments should be sorted by start time
        assert result.segments[0].speaker == "Agent"
        assert result.segments[1].speaker == "Customer"
        assert result.segments[2].speaker == "Agent"

    def test_overlapping_segments_detected(self, qapp, overlapping_transcription):
        """Test that overlapping segments are detected correctly."""
        worker = MergeWorker(transcription=overlapping_transcription)
        # Overlapping segments should require LLM merge
        assert worker._is_simple_merge() is False


class TestMergeWorkerHelpers:
    """Tests for MergeWorker helper methods."""

    def test_single_channel_result(self, qapp):
        """Test _single_channel_result method."""
        transcription = TranscriptionResult(
            text="Test text",
            segments=[
                TranscriptionSegment(start=0.0, end=2.0, text="Hello", speaker="Agent"),
            ],
            channels=1,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._single_channel_result()

        assert result.merged_text == "Test text"
        assert len(result.segments) == 1
        assert result.segments[0].speaker == "Agent"

    def test_single_channel_result_no_speaker(self, qapp):
        """Test _single_channel_result with no speaker label."""
        transcription = TranscriptionResult(
            text="Test text",
            segments=[
                TranscriptionSegment(start=0.0, end=2.0, text="Hello", speaker=None),
            ],
            channels=1,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._single_channel_result()

        # Should default to "Speaker"
        assert result.segments[0].speaker == "Speaker"

    def test_is_simple_merge_true(self, qapp):
        """Test _is_simple_merge returns True for non-overlapping."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=2.0, text="First", speaker="Agent"),
                TranscriptionSegment(start=3.0, end=5.0, text="Second", speaker="Customer"),
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        assert worker._is_simple_merge() is True

    def test_is_simple_merge_false(self, qapp):
        """Test _is_simple_merge returns False for overlapping."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=3.0, text="First", speaker="Agent"),
                TranscriptionSegment(
                    start=2.0, end=5.0, text="Second", speaker="Customer"
                ),  # Overlaps
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        assert worker._is_simple_merge() is False

    def test_simple_merge(self, qapp):
        """Test _simple_merge method."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=2.0, end=4.0, text="Second", speaker="Customer"),
                TranscriptionSegment(
                    start=0.0, end=2.0, text="First", speaker="Agent"
                ),  # Out of order
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._simple_merge()

        # Should be sorted by start time
        assert result.segments[0].text == "First"
        assert result.segments[1].text == "Second"

    def test_format_for_llm(self, qapp):
        """Test _format_for_llm method."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=2.5, text="Hello there", speaker="Agent"),
                TranscriptionSegment(
                    start=2.5, end=5.0, text="Hi, I need help", speaker="Customer"
                ),
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        formatted = worker._format_for_llm()

        assert "[0.0s - 2.5s] [Agent]: Hello there" in formatted
        assert "[2.5s - 5.0s] [Customer]: Hi, I need help" in formatted


class TestMergeWorkerTimestampHandling:
    """Tests for timestamp handling in merge."""

    def test_chronological_ordering(self, qapp):
        """Test that segments are ordered chronologically."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=5.0, end=7.0, text="Third", speaker="Agent"),
                TranscriptionSegment(start=0.0, end=2.0, text="First", speaker="Agent"),
                TranscriptionSegment(start=2.5, end=4.5, text="Second", speaker="Customer"),
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._simple_merge()

        assert result.segments[0].text == "First"
        assert result.segments[1].text == "Second"
        assert result.segments[2].text == "Third"

    def test_speaker_labels_preserved(self, qapp):
        """Test that speaker labels are preserved after merge."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=2.0, text="Agent text", speaker="Agent"),
                TranscriptionSegment(
                    start=2.5, end=4.5, text="Customer text", speaker="Customer"
                ),
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._simple_merge()

        assert result.segments[0].speaker == "Agent"
        assert result.segments[1].speaker == "Customer"

    def test_merged_text_format(self, qapp):
        """Test that merged text has correct format."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=2.0, text="Hello", speaker="Agent"),
                TranscriptionSegment(start=2.5, end=4.5, text="Hi there", speaker="Customer"),
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._simple_merge()

        assert "[Agent] Hello" in result.merged_text
        assert "[Customer] Hi there" in result.merged_text


class TestMergeWorkerEdgeCases:
    """Tests for edge cases in MergeWorker."""

    def test_empty_segments(self, qapp):
        """Test merge with empty segments list."""
        transcription = TranscriptionResult(
            text="",
            segments=[],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        # Should handle simple merge case
        assert worker._is_simple_merge() is True

    def test_single_segment(self, qapp):
        """Test merge with single segment."""
        transcription = TranscriptionResult(
            text="Single segment",
            segments=[
                TranscriptionSegment(
                    start=0.0, end=2.0, text="Single segment", speaker="Agent"
                ),
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        result = worker._simple_merge()

        assert len(result.segments) == 1
        assert result.segments[0].text == "Single segment"

    def test_adjacent_segments(self, qapp):
        """Test merge with exactly adjacent segments (no gap)."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=2.0, text="First", speaker="Agent"),
                TranscriptionSegment(
                    start=2.0, end=4.0, text="Second", speaker="Customer"
                ),  # Starts exactly where first ends
            ],
            channels=2,
        )
        worker = MergeWorker(transcription=transcription)
        # Adjacent but not overlapping (< 0.5s overlap threshold)
        assert worker._is_simple_merge() is True
