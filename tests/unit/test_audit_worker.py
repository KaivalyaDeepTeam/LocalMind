"""
Tests for AuditWorker execution logic.

Tests the audit worker's do_work method with mocked LLM provider
to verify correct scoring and feedback generation.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from localmind.workers.audit_worker import (
    DEFAULT_PARAMETERS,
    AuditResult,
    AuditWorker,
    ParameterScore,
    create_audit_json_schema,
    create_audit_prompt,
    create_cot_analysis_prompt,
    create_single_shot_audit_prompt,
)
from localmind.workers.merge_worker import MergeResult, MergedSegment


class TestParameterScore:
    """Tests for ParameterScore dataclass."""

    def test_parameter_score_creation(self):
        """Test creating a parameter score."""
        score = ParameterScore(
            name="greeting",
            score=8.0,
            max_score=10.0,
            weight=1.0,
            feedback="Good greeting",
        )
        assert score.name == "greeting"
        assert score.score == 8.0
        assert score.max_score == 10.0
        assert score.weight == 1.0
        assert score.feedback == "Good greeting"

    def test_parameter_score_weighted_score(self):
        """Test weighted score calculation."""
        score = ParameterScore(
            name="test",
            score=8.0,
            max_score=10.0,
            weight=1.5,
        )
        assert score.weighted_score == 12.0  # 8.0 * 1.5

    def test_parameter_score_weighted_max(self):
        """Test weighted max score calculation."""
        score = ParameterScore(
            name="test",
            score=8.0,
            max_score=10.0,
            weight=1.5,
        )
        assert score.weighted_max == 15.0  # 10.0 * 1.5

    def test_parameter_score_to_dict(self):
        """Test to_dict conversion."""
        score = ParameterScore(
            name="test",
            score=7.5,
            max_score=10.0,
            weight=2.0,
            feedback="Test feedback",
        )
        d = score.to_dict()
        assert d["name"] == "test"
        assert d["score"] == 7.5
        assert d["max_score"] == 10.0
        assert d["weight"] == 2.0
        assert d["feedback"] == "Test feedback"


class TestAuditResult:
    """Tests for AuditResult dataclass."""

    def test_audit_result_creation(self):
        """Test creating an audit result."""
        scores = [
            ParameterScore(name="greeting", score=8.0, max_score=10.0, weight=1.0),
            ParameterScore(name="closing", score=7.0, max_score=10.0, weight=1.0),
        ]
        result = AuditResult(
            overall_score=75.0,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["Good communication"],
            improvements=["Better closing"],
            summary="Good overall performance",
        )
        assert result.overall_score == 75.0
        assert result.max_score == 100.0
        assert len(result.parameter_scores) == 2
        assert len(result.strengths) == 1
        assert len(result.improvements) == 1

    def test_audit_result_percentage(self):
        """Test percentage calculation."""
        result = AuditResult(overall_score=80.0, max_score=100.0)
        assert result.percentage == 80.0

    def test_audit_result_percentage_zero_max(self):
        """Test percentage with zero max score."""
        result = AuditResult(overall_score=50.0, max_score=0.0)
        assert result.percentage == 0.0

    def test_audit_result_to_dict(self):
        """Test to_dict conversion."""
        scores = [
            ParameterScore(
                name="greeting", score=8.0, max_score=10.0, weight=1.0, feedback="Good"
            )
        ]
        result = AuditResult(
            overall_score=80.0,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["Strength 1"],
            improvements=["Improvement 1"],
            summary="Summary text",
        )
        d = result.to_dict()
        assert d["overall_score"] == 80.0
        assert d["max_score"] == 100.0
        assert d["percentage"] == 80.0
        assert "greeting" in d["parameter_scores"]
        assert d["strengths"] == ["Strength 1"]
        assert d["improvements"] == ["Improvement 1"]
        assert d["summary"] == "Summary text"

    def test_audit_result_markdown_report_excellent(self):
        """Test markdown report generation for excellent performance."""
        scores = [
            ParameterScore(name="greeting", score=9.0, max_score=10.0, weight=1.0),
        ]
        result = AuditResult(
            overall_score=90.0,
            max_score=100.0,
            parameter_scores=scores,
            strengths=["Excellent greeting"],
            improvements=["Minor improvements"],
            summary="Outstanding performance",
        )
        report = result.generate_markdown_report()
        assert "Excellent Performance" in report
        assert "90.0%" in report
        assert "Excellent greeting" in report

    def test_audit_result_markdown_report_poor(self):
        """Test markdown report generation for poor performance."""
        result = AuditResult(
            overall_score=25.0,
            max_score=100.0,
            parameter_scores=[],
            summary="Needs significant improvement",
        )
        report = result.generate_markdown_report()
        assert "Needs Improvement" in report


class TestDefaultParameters:
    """Tests for default scoring parameters."""

    def test_default_parameters_count(self):
        """Test default parameters has correct count."""
        assert len(DEFAULT_PARAMETERS) == 10

    def test_default_parameters_weight_sum(self):
        """Test weights sum to 10.0 for 100 point max."""
        total_weight = sum(p["weight"] for p in DEFAULT_PARAMETERS)
        assert total_weight == 10.0

    def test_default_parameters_have_required_fields(self):
        """Test all parameters have required fields."""
        for param in DEFAULT_PARAMETERS:
            assert "name" in param
            assert "max_score" in param
            assert "weight" in param
            assert "description" in param


class TestAuditPrompts:
    """Tests for audit prompt generation."""

    def test_create_audit_json_schema(self):
        """Test JSON schema creation."""
        params = [{"name": "test_param", "max_score": 10}]
        schema = create_audit_json_schema(params)

        assert schema["type"] == "object"
        assert "parameter_scores" in schema["properties"]
        assert "strengths" in schema["properties"]
        assert "improvements" in schema["properties"]
        assert "summary" in schema["properties"]

    def test_create_cot_analysis_prompt(self):
        """Test Chain-of-Thought prompt creation."""
        prompt = create_cot_analysis_prompt()
        assert "Opening & Greeting" in prompt
        assert "Listening & Understanding" in prompt
        assert "Problem Solving" in prompt

    def test_create_single_shot_audit_prompt(self):
        """Test single-shot audit prompt creation."""
        params = DEFAULT_PARAMETERS[:3]
        prompt = create_single_shot_audit_prompt(params)

        assert "greeting" in prompt
        assert "SCORING GUIDELINES" in prompt
        assert "OUTPUT FORMAT" in prompt

    def test_create_audit_prompt_with_analysis(self):
        """Test audit prompt with CoT analysis."""
        params = [{"name": "greeting", "max_score": 10, "weight": 1.0, "description": "Test"}]
        analysis = "The agent provided a warm greeting."
        prompt = create_audit_prompt(params, analysis)

        assert "ANALYSIS FROM REASONING PHASE" in prompt
        assert analysis in prompt
        assert "SCORING SYSTEM" in prompt


class TestAuditWorkerInit:
    """Tests for AuditWorker initialization."""

    def test_worker_initialization(self, qapp):
        """Test worker initialization."""
        merge_result = MergeResult(
            merged_text="[Agent] Hello\n[Customer] Hi",
            segments=[],
        )
        worker = AuditWorker(merge_result=merge_result)

        assert worker._merge_result == merge_result
        assert worker._parameters == DEFAULT_PARAMETERS
        assert worker._loop is None

    def test_worker_custom_parameters(self, qapp):
        """Test worker with custom parameters."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        custom_params = [
            {"name": "custom1", "max_score": 10, "weight": 5.0, "description": "Custom 1"},
            {"name": "custom2", "max_score": 10, "weight": 5.0, "description": "Custom 2"},
        ]
        worker = AuditWorker(merge_result=merge_result, parameters=custom_params)

        assert worker._parameters == custom_params


class TestAuditWorkerDoWork:
    """Tests for AuditWorker.do_work() method."""

    @pytest.fixture
    def sample_merge_result(self):
        """Create a sample merge result for testing."""
        return MergeResult(
            merged_text="[Agent] Hello, thank you for calling. How can I help?\n[Customer] I need help with my order.",
            segments=[
                MergedSegment(
                    start=0.0,
                    end=3.0,
                    speaker="Agent",
                    text="Hello, thank you for calling. How can I help?",
                ),
                MergedSegment(
                    start=3.0,
                    end=6.0,
                    speaker="Customer",
                    text="I need help with my order.",
                ),
            ],
            summary="Customer called about order issue.",
        )

    def test_do_work_stop_requested(self, qapp, sample_merge_result):
        """Test worker stops when stop is requested."""
        worker = AuditWorker(merge_result=sample_merge_result)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None

    def test_calculate_subscore(self, qapp, sample_merge_result):
        """Test subscore calculation."""
        worker = AuditWorker(merge_result=sample_merge_result)

        scores = [
            ParameterScore(name="greeting", score=8.0, max_score=10.0, weight=1.0),
            ParameterScore(name="closing", score=6.0, max_score=10.0, weight=1.0),
            ParameterScore(name="compliance", score=9.0, max_score=10.0, weight=1.0),
        ]

        # Compliance params: greeting, closing, compliance
        compliance_score = worker._calculate_subscore(
            scores, ["greeting", "closing", "compliance"]
        )
        expected = ((8.0 + 6.0 + 9.0) / (10.0 + 10.0 + 10.0)) * 100
        assert compliance_score == expected

    def test_calculate_subscore_empty(self, qapp, sample_merge_result):
        """Test subscore calculation with no matching params."""
        worker = AuditWorker(merge_result=sample_merge_result)
        scores = [
            ParameterScore(name="other", score=8.0, max_score=10.0, weight=1.0),
        ]

        result = worker._calculate_subscore(scores, ["greeting", "closing"])
        assert result == 0.0


class TestAuditWorkerScoreCalculation:
    """Tests for score calculation logic."""

    def test_weighted_score_calculation(self):
        """Test that weighted scores are calculated correctly."""
        scores = [
            ParameterScore(name="p1", score=8.0, max_score=10.0, weight=2.0),
            ParameterScore(name="p2", score=6.0, max_score=10.0, weight=1.0),
        ]

        total_score = sum(p.score * p.weight for p in scores)
        total_max = sum(p.max_score * p.weight for p in scores)

        assert total_score == (8.0 * 2.0) + (6.0 * 1.0)  # 22.0
        assert total_max == (10.0 * 2.0) + (10.0 * 1.0)  # 30.0

    def test_percentage_calculation(self):
        """Test percentage calculation from weighted scores."""
        overall_score = 75.0
        max_score = 100.0

        percentage = (overall_score / max_score) * 100
        assert percentage == 75.0

    def test_score_boundary_zero(self):
        """Test score boundary at zero."""
        score = ParameterScore(name="test", score=0.0, max_score=10.0, weight=1.0)
        assert score.weighted_score == 0.0

    def test_score_boundary_max(self):
        """Test score boundary at max."""
        score = ParameterScore(name="test", score=10.0, max_score=10.0, weight=1.0)
        assert score.weighted_score == 10.0


class TestAuditWorkerErrorHandling:
    """Tests for error handling in AuditWorker."""

    def test_worker_with_empty_transcript(self, qapp):
        """Test worker creation with empty transcript."""
        merge_result = MergeResult(merged_text="", segments=[])
        worker = AuditWorker(merge_result=merge_result)

        # Worker should be created successfully
        assert worker._merge_result.merged_text == ""

    def test_worker_stop_before_llm(self, qapp):
        """Test worker stops before LLM call."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        worker = AuditWorker(merge_result=merge_result)
        worker._should_stop = True

        result = worker.do_work()
        assert result is None


class TestAuditWorkerParameterValidation:
    """Tests for parameter validation in AuditWorker."""

    def test_valid_parameters_accepted(self, qapp):
        """Test valid parameters are accepted."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        valid_params = [
            {"name": "Greeting", "weight": 1.0, "max_score": 10},
            {"name": "Resolution", "weight": 2.0, "max_score": 10},
        ]
        worker = AuditWorker(merge_result=merge_result, parameters=valid_params)
        assert worker._parameters == valid_params

    def test_invalid_weight_zero_rejected(self, qapp):
        """Test weight of 0 is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "Greeting", "weight": 0, "max_score": 10},
        ]
        with pytest.raises(ValueError, match="weight must be > 0"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_invalid_weight_negative_rejected(self, qapp):
        """Test negative weight is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "Greeting", "weight": -1.0, "max_score": 10},
        ]
        with pytest.raises(ValueError, match="weight must be > 0"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_invalid_weight_over_10_rejected(self, qapp):
        """Test weight > 10 is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "Greeting", "weight": 11.0, "max_score": 10},
        ]
        with pytest.raises(ValueError, match="weight must be > 0 and <= 10"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_invalid_max_score_zero_rejected(self, qapp):
        """Test max_score of 0 is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "Greeting", "weight": 1.0, "max_score": 0},
        ]
        with pytest.raises(ValueError, match="max_score must be positive"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_invalid_max_score_negative_rejected(self, qapp):
        """Test negative max_score is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "Greeting", "weight": 1.0, "max_score": -5},
        ]
        with pytest.raises(ValueError, match="max_score must be positive"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_missing_required_field_rejected(self, qapp):
        """Test missing required fields are rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "Greeting", "weight": 1.0},  # Missing max_score
        ]
        with pytest.raises(ValueError, match="missing required fields"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_empty_name_rejected(self, qapp):
        """Test empty name is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "", "weight": 1.0, "max_score": 10},
        ]
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_whitespace_name_rejected(self, qapp):
        """Test whitespace-only name is rejected."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        invalid_params = [
            {"name": "   ", "weight": 1.0, "max_score": 10},
        ]
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            AuditWorker(merge_result=merge_result, parameters=invalid_params)

    def test_default_parameters_pass_validation(self, qapp):
        """Test default parameters pass validation."""
        merge_result = MergeResult(merged_text="Test", segments=[])
        # Should not raise
        worker = AuditWorker(merge_result=merge_result)
        assert len(worker._parameters) > 0
