"""
Integration tests for the complete processing pipeline.

Tests end-to-end workflow: transcription -> merge -> audit -> export
verifying data flow and worker interactions.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from localmind.workers.audit_worker import AuditResult, AuditWorker, ParameterScore
from localmind.workers.merge_worker import MergedSegment, MergeResult, MergeWorker
from localmind.workers.transcription_worker import (
    TranscriptionResult,
    TranscriptionSegment,
    TranscriptionWorker,
)


class TestDataFlowIntegration:
    """Tests for data flow through the pipeline."""

    @pytest.fixture
    def sample_transcription_result(self):
        """Create a sample transcription result."""
        return TranscriptionResult(
            text="[Agent] Hello, thank you for calling support. How can I help?\n[Customer] I need help with my account.",
            segments=[
                TranscriptionSegment(
                    start=0.0,
                    end=3.0,
                    text="Hello, thank you for calling support. How can I help?",
                    speaker="Agent",
                ),
                TranscriptionSegment(
                    start=3.5,
                    end=6.0,
                    text="I need help with my account.",
                    speaker="Customer",
                ),
            ],
            language="en",
            duration=6.0,
            channels=2,
        )

    @pytest.fixture
    def sample_merge_result(self):
        """Create a sample merge result."""
        return MergeResult(
            merged_text="[Agent] Hello, thank you for calling support. How can I help?\n[Customer] I need help with my account.",
            segments=[
                MergedSegment(
                    start=0.0,
                    end=3.0,
                    speaker="Agent",
                    text="Hello, thank you for calling support. How can I help?",
                ),
                MergedSegment(
                    start=3.5,
                    end=6.0,
                    speaker="Customer",
                    text="I need help with my account.",
                ),
            ],
            summary="Customer called for account assistance.",
        )

    @pytest.fixture
    def sample_audit_result(self):
        """Create a sample audit result."""
        scores = [
            ParameterScore(
                name="greeting", score=8.5, max_score=10.0, weight=0.7, feedback="Good greeting"
            ),
            ParameterScore(
                name="active_listening",
                score=8.0,
                max_score=10.0,
                weight=1.1,
                feedback="Shows engagement",
            ),
            ParameterScore(
                name="problem_identification",
                score=7.5,
                max_score=10.0,
                weight=1.1,
                feedback="Identified issue",
            ),
            ParameterScore(
                name="solution_provided",
                score=7.0,
                max_score=10.0,
                weight=1.5,
                feedback="Adequate solution",
            ),
            ParameterScore(
                name="product_knowledge",
                score=8.0,
                max_score=10.0,
                weight=1.1,
                feedback="Good knowledge",
            ),
            ParameterScore(
                name="communication_clarity",
                score=8.5,
                max_score=10.0,
                weight=0.8,
                feedback="Clear",
            ),
            ParameterScore(
                name="empathy", score=7.5, max_score=10.0, weight=0.8, feedback="Shows care"
            ),
            ParameterScore(
                name="call_control", score=8.0, max_score=10.0, weight=0.7, feedback="Good control"
            ),
            ParameterScore(
                name="closing", score=7.0, max_score=10.0, weight=0.7, feedback="Proper closing"
            ),
            ParameterScore(
                name="compliance",
                score=8.5,
                max_score=10.0,
                weight=1.5,
                feedback="Followed scripts",
            ),
        ]
        return AuditResult(
            overall_score=78.0,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["Professional greeting", "Clear communication"],
            improvements=["Could provide more details", "Better follow-up"],
            summary="Good overall performance.",
            compliance_score=80.0,
            quality_score=76.0,
        )

    def test_transcription_to_merge_flow(self, qapp, sample_transcription_result):
        """Test data flow from transcription to merge."""
        # Verify transcription structure
        assert sample_transcription_result.channels == 2
        assert len(sample_transcription_result.segments) == 2

        # Create merge worker with transcription
        merge_worker = MergeWorker(transcription=sample_transcription_result)
        merge_result = merge_worker.do_work()

        # Verify merge result
        assert merge_result is not None
        assert isinstance(merge_result, MergeResult)
        assert len(merge_result.segments) == 2

        # Verify speaker labels preserved
        speakers = [s.speaker for s in merge_result.segments]
        assert "Agent" in speakers
        assert "Customer" in speakers

    def test_merge_result_to_audit_input(self, sample_merge_result):
        """Test merge result can be used as audit input."""
        # Verify merge result has required fields for audit
        assert sample_merge_result.merged_text
        assert len(sample_merge_result.merged_text) > 0

        # Create audit worker
        audit_worker = AuditWorker(merge_result=sample_merge_result)
        assert audit_worker._merge_result == sample_merge_result

    def test_audit_result_structure(self, sample_audit_result):
        """Test audit result has complete structure."""
        # Verify overall scores
        assert sample_audit_result.overall_score > 0
        assert sample_audit_result.max_score == 100.0
        assert 0 <= sample_audit_result.percentage <= 100

        # Verify parameter scores
        assert len(sample_audit_result.parameter_scores) == 10
        for score in sample_audit_result.parameter_scores:
            assert score.name
            assert 0 <= score.score <= score.max_score
            assert score.weight > 0

        # Verify feedback sections
        assert len(sample_audit_result.strengths) > 0
        assert len(sample_audit_result.improvements) > 0
        assert sample_audit_result.summary


class TestPipelineCancellation:
    """Tests for pipeline cancellation at different stages."""

    def test_transcription_cancellation(self, qapp, temp_dir):
        """Test cancelling transcription worker."""
        audio_path = temp_dir / "test.wav"
        audio_path.touch()

        worker = TranscriptionWorker(
            audio_path=str(audio_path),
            use_gpu=False,
        )
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_merge_cancellation(self, qapp):
        """Test cancelling merge worker."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[],
            channels=2,
        )

        worker = MergeWorker(transcription=transcription)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_audit_cancellation(self, qapp):
        """Test cancelling audit worker."""
        merge_result = MergeResult(
            merged_text="Test transcript",
            segments=[],
        )

        worker = AuditWorker(merge_result=merge_result)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None


class TestExportIntegration:
    """Tests for export functionality after pipeline completion."""

    @pytest.fixture
    def complete_audit_result(self):
        """Create a complete audit result for export testing."""
        scores = [
            ParameterScore(name="greeting", score=8.0, max_score=10.0, weight=1.0, feedback="Good"),
            ParameterScore(
                name="closing", score=7.5, max_score=10.0, weight=1.0, feedback="Adequate"
            ),
        ]
        return AuditResult(
            overall_score=77.5,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["Professional tone", "Clear communication"],
            improvements=["Better closing"],
            summary="Good call overall.",
            compliance_score=80.0,
            quality_score=75.0,
            transcript="[Agent] Hello\n[Customer] Hi",
        )

    def test_export_to_json(self, complete_audit_result, temp_dir):
        """Test exporting audit result to JSON."""
        export_path = temp_dir / "export.json"

        # Convert to dict and save
        result_dict = complete_audit_result.to_dict()

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        # Verify file
        assert export_path.exists()

        with open(export_path, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["overall_score"] == 77.5
        assert "greeting" in loaded["parameter_scores"]

    def test_export_to_markdown(self, complete_audit_result, temp_dir):
        """Test exporting audit result to Markdown."""
        export_path = temp_dir / "export.md"

        markdown = complete_audit_result.generate_markdown_report()

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        assert export_path.exists()

        content = export_path.read_text()
        assert "Call Quality Audit Report" in content
        assert "77.5" in content
        assert "Professional tone" in content

    def test_export_unicode_content(self, temp_dir):
        """Test exporting with Unicode content (Hindi, Arabic)."""
        scores = [
            ParameterScore(
                name="greeting",
                score=8.0,
                max_score=10.0,
                weight=1.0,
                feedback="नमस्ते - Good Hindi greeting",  # Hindi
            ),
        ]
        result = AuditResult(
            overall_score=80.0,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["مرحبا - Arabic greeting"],  # Arabic
            improvements=["Привет - Russian word"],  # Russian
            summary="Multilingual test: 你好",  # Chinese
            transcript="[Agent] नमस्ते\n[Customer] السلام عليكم",
        )

        export_path = temp_dir / "unicode_export.json"
        result_dict = result.to_dict()

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        # Verify Unicode is preserved
        with open(export_path, encoding="utf-8") as f:
            content = f.read()

        assert "नमस्ते" in content  # Hindi
        assert "مرحبا" in content  # Arabic
        assert "Привет" in content  # Russian
        assert "你好" in content  # Chinese


class TestWorkerState:
    """Tests for worker state management."""

    def test_worker_initial_state(self, qapp):
        """Test workers start in IDLE state."""
        from localmind.workers.base import WorkerState

        transcription_worker = TranscriptionWorker(audio_path="/test.wav")
        assert transcription_worker.state == WorkerState.IDLE

    def test_worker_stop_state(self, qapp):
        """Test worker stop sets correct state."""
        from localmind.workers.base import WorkerState

        worker = TranscriptionWorker(audio_path="/test.wav")
        worker.stop()

        assert worker.state == WorkerState.STOPPING
        assert worker._should_stop is True

    def test_worker_pause_resume(self, qapp):
        """Test worker pause and resume."""
        from localmind.workers.base import WorkerState

        worker = TranscriptionWorker(audio_path="/test.wav")

        worker.pause()
        assert worker.state == WorkerState.PAUSED

        worker.resume()
        assert worker.state == WorkerState.RUNNING


class TestProgressReporting:
    """Tests for progress reporting through pipeline."""

    def test_merge_worker_progress(self, qapp):
        """Test merge worker reports progress."""
        transcription = TranscriptionResult(
            text="Test",
            segments=[
                TranscriptionSegment(start=0.0, end=1.0, text="Test", speaker="Agent"),
            ],
            channels=1,
        )

        progress_values = []
        worker = MergeWorker(transcription=transcription)
        worker.progress.connect(lambda p, m: progress_values.append(p))

        worker.do_work()

        # Should have at least start and end progress
        assert 100 in progress_values

    def test_audit_worker_initial_progress(self, qapp):
        """Test audit worker reports initial progress."""
        merge_result = MergeResult(merged_text="Test", segments=[])

        worker = AuditWorker(merge_result=merge_result)
        worker._should_stop = True  # Stop immediately

        progress_values = []
        worker.progress.connect(lambda p, m: progress_values.append(p))

        worker.do_work()

        # Should have reported initial progress
        assert 0 in progress_values
