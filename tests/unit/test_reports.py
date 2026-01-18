"""
Unit tests for LocalMind reports module.
"""

import pytest
from pathlib import Path

from localmind.reports.pdf_generator import (
    PDFReportGenerator,
    ReportOptions,
    ScoreChartGenerator,
    get_score_class,
    get_bar_class,
)


class TestReportOptions:
    """Tests for ReportOptions."""

    def test_default_options(self):
        """Test default report options."""
        options = ReportOptions()

        assert options.include_transcript is True
        assert options.include_chart is True
        assert options.include_scores is True
        assert options.company_name is None

    def test_custom_options(self):
        """Test custom report options."""
        options = ReportOptions(
            include_transcript=False,
            include_chart=False,
            company_name="Test Corp",
        )

        assert options.include_transcript is False
        assert options.include_chart is False
        assert options.company_name == "Test Corp"


class TestScoreClasses:
    """Tests for score CSS class functions."""

    def test_score_class_excellent(self):
        """Test excellent score class."""
        assert get_score_class(95) == "score-excellent"
        assert get_score_class(80) == "score-excellent"

    def test_score_class_good(self):
        """Test good score class."""
        assert get_score_class(75) == "score-good"
        assert get_score_class(60) == "score-good"

    def test_score_class_average(self):
        """Test average score class."""
        assert get_score_class(55) == "score-average"
        assert get_score_class(40) == "score-average"

    def test_score_class_poor(self):
        """Test poor score class."""
        assert get_score_class(35) == "score-poor"
        assert get_score_class(0) == "score-poor"

    def test_bar_class_excellent(self):
        """Test excellent bar class."""
        assert get_bar_class(85) == "bar-excellent"

    def test_bar_class_good(self):
        """Test good bar class."""
        assert get_bar_class(65) == "bar-good"

    def test_bar_class_average(self):
        """Test average bar class."""
        assert get_bar_class(45) == "bar-average"

    def test_bar_class_poor(self):
        """Test poor bar class."""
        assert get_bar_class(25) == "bar-poor"


class TestPDFReportGenerator:
    """Tests for PDFReportGenerator."""

    def test_create_generator(self):
        """Test creating a PDF generator."""
        generator = PDFReportGenerator()

        assert generator._options.include_transcript is True
        assert generator._options.include_chart is True

    def test_create_with_options(self):
        """Test creating generator with custom options."""
        options = ReportOptions(include_transcript=False)
        generator = PDFReportGenerator(options)

        assert generator._options.include_transcript is False

    def test_check_dependencies(self):
        """Test checking dependencies."""
        generator = PDFReportGenerator()
        deps = generator.check_dependencies()

        assert "jinja2" in deps
        assert "weasyprint" in deps
        assert "matplotlib" in deps

        # All should be boolean
        for key, value in deps.items():
            assert isinstance(value, bool)

    def test_can_generate(self):
        """Test can_generate method."""
        generator = PDFReportGenerator()
        result = generator.can_generate()

        # Result depends on installed packages
        assert isinstance(result, bool)

    def test_generate_html(self, sample_audit_result):
        """Test generating HTML report."""
        generator = PDFReportGenerator()

        # Skip if jinja2 not available
        if not generator.check_dependencies()["jinja2"]:
            pytest.skip("Jinja2 not installed")

        html = generator.generate_html(sample_audit_result, "test_audio.wav")

        assert "<!DOCTYPE html>" in html
        assert "Call Quality Audit Report" in html
        assert "test_audio.wav" in html
        assert "75.5" in html  # Overall score

    def test_generate_html_with_no_transcript(self, sample_audit_result):
        """Test generating HTML without transcript."""
        options = ReportOptions(include_transcript=False)
        generator = PDFReportGenerator(options)

        if not generator.check_dependencies()["jinja2"]:
            pytest.skip("Jinja2 not installed")

        html = generator.generate_html(sample_audit_result, "test.wav")

        # Should not include full transcript section
        assert "Full Transcript" not in html or "include_transcript" in html


class TestScoreChartGenerator:
    """Tests for ScoreChartGenerator."""

    def test_generate_bar_chart(self):
        """Test generating bar chart."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("Matplotlib not installed")

        parameters = [
            {"name": "greeting", "display_name": "Greeting", "score": 8.0, "max": 10.0},
            {"name": "empathy", "display_name": "Empathy", "score": 7.0, "max": 10.0},
            {"name": "solution", "display_name": "Solution", "score": 9.0, "max": 10.0},
        ]

        chart = ScoreChartGenerator.generate_bar_chart(parameters)

        assert chart is not None
        assert chart.startswith("data:image/png;base64,")

    def test_generate_radar_chart(self):
        """Test generating radar chart."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("Matplotlib not installed")

        parameters = [
            {"name": "p1", "display_name": "Param 1", "score": 8.0, "max": 10.0},
            {"name": "p2", "display_name": "Param 2", "score": 7.0, "max": 10.0},
            {"name": "p3", "display_name": "Param 3", "score": 9.0, "max": 10.0},
            {"name": "p4", "display_name": "Param 4", "score": 6.0, "max": 10.0},
        ]

        chart = ScoreChartGenerator.generate_radar_chart(parameters)

        assert chart is not None
        assert chart.startswith("data:image/png;base64,")

    def test_radar_chart_requires_minimum_points(self):
        """Test radar chart requires at least 3 points."""
        try:
            import matplotlib
        except ImportError:
            pytest.skip("Matplotlib not installed")

        parameters = [
            {"name": "p1", "display_name": "P1", "score": 8.0, "max": 10.0},
            {"name": "p2", "display_name": "P2", "score": 7.0, "max": 10.0},
        ]

        chart = ScoreChartGenerator.generate_radar_chart(parameters)

        assert chart is None  # Not enough points

    def test_empty_parameters(self):
        """Test with empty parameters."""
        bar_chart = ScoreChartGenerator.generate_bar_chart([])
        radar_chart = ScoreChartGenerator.generate_radar_chart([])

        assert bar_chart is None
        assert radar_chart is None
