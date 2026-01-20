"""
Unit tests for LocalMind reports module.
"""

import pytest

from localmind.reports.pdf_generator import (
    PDFReportGenerator,
    ReportOptions,
    ScoreChartGenerator,
    get_bar_class,
    get_score_class,
)


class TestReportOptions:
    """Tests for ReportOptions."""

    def test_default_options(self):
        """Test default report options."""
        options = ReportOptions()

        assert options.include_transcript is True
        assert options.include_chart is True
        assert options.include_details is True
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

    def test_can_generate(self):
        """Test can_generate method."""
        generator = PDFReportGenerator()
        result = generator.can_generate()

        # Result depends on whether ReportLab is installed
        assert isinstance(result, bool)

    def test_generate_pdf_bytes(self, sample_audit_result):
        """Test generating PDF bytes."""
        generator = PDFReportGenerator()

        if not generator.can_generate():
            pytest.skip("ReportLab not installed")

        pdf_bytes = generator.generate_pdf_bytes(sample_audit_result, "test_audio.wav")

        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        # PDF files start with %PDF
        assert pdf_bytes[:4] == b"%PDF"


class TestScoreChartGenerator:
    """Tests for ScoreChartGenerator."""

    def test_create_score_gauge(self):
        """Test creating a score gauge."""
        # This returns a ReportLab Drawing or None
        gauge = ScoreChartGenerator.create_score_gauge(75.0, 100.0)

        # Returns None if ReportLab not installed, otherwise a Drawing
        if gauge is not None:
            assert hasattr(gauge, "width")
            assert hasattr(gauge, "height")

    def test_create_horizontal_bar_chart(self):
        """Test creating horizontal bar chart."""
        parameters = [
            {"name": "greeting", "display_name": "Greeting", "score": 8.0, "max_score": 10.0},
            {"name": "empathy", "display_name": "Empathy", "score": 7.0, "max_score": 10.0},
            {"name": "solution", "display_name": "Solution", "score": 9.0, "max_score": 10.0},
        ]

        chart = ScoreChartGenerator.create_horizontal_bar_chart(parameters)

        # Returns None if ReportLab not installed, otherwise a Drawing
        if chart is not None:
            assert hasattr(chart, "width")
            assert hasattr(chart, "height")

    def test_create_mini_bar(self):
        """Test creating mini progress bar."""
        bar = ScoreChartGenerator.create_mini_bar(75.0)

        # Returns None if ReportLab not installed, otherwise a Drawing
        if bar is not None:
            assert hasattr(bar, "width")
            assert hasattr(bar, "height")

    def test_empty_parameters_bar_chart(self):
        """Test bar chart with empty parameters."""
        chart = ScoreChartGenerator.create_horizontal_bar_chart([])

        # Should return None for empty parameters
        assert chart is None

    def test_score_gauge_boundary_values(self):
        """Test score gauge with boundary values."""
        # Test 0%
        gauge_zero = ScoreChartGenerator.create_score_gauge(0, 100)
        # Test 100%
        gauge_full = ScoreChartGenerator.create_score_gauge(100, 100)
        # Test 50%
        gauge_half = ScoreChartGenerator.create_score_gauge(50, 100)

        # All should either be None (no ReportLab) or valid drawings
        for gauge in [gauge_zero, gauge_full, gauge_half]:
            if gauge is not None:
                assert hasattr(gauge, "width")
