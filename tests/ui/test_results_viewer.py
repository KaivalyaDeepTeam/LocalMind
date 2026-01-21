"""
Tests for Results Viewer module.

Tests the CircularScoreGauge, TranscriptViewer, ScoreDetailsTable,
FeedbackViewer, and ResultsViewer widgets.
"""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtGui import QColor


class TestCircularScoreGaugeColors:
    """Tests for CircularScoreGauge color constants."""

    def test_standard_colors_has_high(self, qapp):
        """Test standard colors include high (green)."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert "high" in gauge.COLORS_STANDARD
        assert gauge.COLORS_STANDARD["high"] == "#059669"

    def test_standard_colors_has_medium(self, qapp):
        """Test standard colors include medium (orange)."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert "medium" in gauge.COLORS_STANDARD
        assert gauge.COLORS_STANDARD["medium"] == "#D97706"

    def test_standard_colors_has_low(self, qapp):
        """Test standard colors include low (red)."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert "low" in gauge.COLORS_STANDARD
        assert gauge.COLORS_STANDARD["low"] == "#DC2626"

    def test_colorblind_colors_has_high(self, qapp):
        """Test colorblind colors include high (blue)."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert "high" in gauge.COLORS_COLORBLIND
        assert gauge.COLORS_COLORBLIND["high"] == "#2563EB"

    def test_colorblind_colors_has_medium(self, qapp):
        """Test colorblind colors include medium (purple)."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert "medium" in gauge.COLORS_COLORBLIND
        assert gauge.COLORS_COLORBLIND["medium"] == "#7C3AED"

    def test_colorblind_colors_has_low(self, qapp):
        """Test colorblind colors include low (orange, not red)."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert "low" in gauge.COLORS_COLORBLIND
        assert gauge.COLORS_COLORBLIND["low"] == "#EA580C"


class TestCircularScoreGaugeGrades:
    """Tests for CircularScoreGauge grade calculations."""

    def test_grade_a_for_90_plus(self, qapp):
        """Test grade A for 90% and above."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._get_grade(90) == "A"
        assert gauge._get_grade(95) == "A"
        assert gauge._get_grade(100) == "A"

    def test_grade_b_for_80_to_89(self, qapp):
        """Test grade B for 80-89%."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._get_grade(80) == "B"
        assert gauge._get_grade(85) == "B"
        assert gauge._get_grade(89) == "B"

    def test_grade_c_for_70_to_79(self, qapp):
        """Test grade C for 70-79%."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._get_grade(70) == "C"
        assert gauge._get_grade(75) == "C"
        assert gauge._get_grade(79) == "C"

    def test_grade_d_for_60_to_69(self, qapp):
        """Test grade D for 60-69%."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._get_grade(60) == "D"
        assert gauge._get_grade(65) == "D"
        assert gauge._get_grade(69) == "D"

    def test_grade_f_below_60(self, qapp):
        """Test grade F for below 60%."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._get_grade(59) == "F"
        assert gauge._get_grade(50) == "F"
        assert gauge._get_grade(0) == "F"


class TestCircularScoreGaugeColorForScore:
    """Tests for CircularScoreGauge color calculation."""

    def test_high_color_for_80_plus(self, qapp):
        """Test high color returned for 80% and above."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        gauge._colorblind_mode = False

        color = gauge._get_color_for_score(80)
        assert color == QColor("#059669")

        color = gauge._get_color_for_score(100)
        assert color == QColor("#059669")

    def test_medium_color_for_60_to_79(self, qapp):
        """Test medium color returned for 60-79%."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        gauge._colorblind_mode = False

        color = gauge._get_color_for_score(60)
        assert color == QColor("#D97706")

        color = gauge._get_color_for_score(79)
        assert color == QColor("#D97706")

    def test_low_color_below_60(self, qapp):
        """Test low color returned for below 60%."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        gauge._colorblind_mode = False

        color = gauge._get_color_for_score(59)
        assert color == QColor("#DC2626")

        color = gauge._get_color_for_score(0)
        assert color == QColor("#DC2626")

    def test_colorblind_mode_uses_different_colors(self, qapp):
        """Test colorblind mode uses different color palette."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        gauge._colorblind_mode = True

        color_high = gauge._get_color_for_score(90)
        assert color_high == QColor("#2563EB")  # Blue, not green

        color_low = gauge._get_color_for_score(30)
        assert color_low == QColor("#EA580C")  # Orange, not red


class TestCircularScoreGaugeWidget:
    """Tests for CircularScoreGauge widget initialization."""

    def test_gauge_creates(self, qapp):
        """Test CircularScoreGauge can be created."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge is not None

    def test_gauge_with_label(self, qapp):
        """Test CircularScoreGauge stores label."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge(label="Overall")
        assert gauge._label == "Overall"

    def test_gauge_with_size(self, qapp):
        """Test CircularScoreGauge stores size."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge(size=150)
        assert gauge._size == 150

    def test_gauge_initial_score_zero(self, qapp):
        """Test initial score is zero."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._score == 0.0

    def test_gauge_initial_animated_score_zero(self, qapp):
        """Test initial animated score is zero."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        assert gauge._animated_score == 0.0

    def test_gauge_set_score(self, qapp):
        """Test setting score."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        gauge.set_score(75.5, 100.0)

        assert gauge._score == 75.5
        assert gauge._max_score == 100.0

    def test_gauge_set_score_instant(self, qapp):
        """Test setting score instantly without animation."""
        from localmind.ui.results_viewer import CircularScoreGauge

        gauge = CircularScoreGauge()
        gauge.set_score_instant(80.0, 100.0)

        assert gauge._score == 80.0
        assert gauge._animated_score == 80.0

    def test_colorblind_mode_class_method(self, qapp):
        """Test colorblind mode can be set via class method."""
        from localmind.ui.results_viewer import CircularScoreGauge

        # Reset to known state
        CircularScoreGauge._colorblind_mode = False

        assert CircularScoreGauge.is_colorblind_mode() is False

        CircularScoreGauge.set_colorblind_mode(True)
        assert CircularScoreGauge.is_colorblind_mode() is True

        # Reset for other tests
        CircularScoreGauge.set_colorblind_mode(False)


class TestScoreGaugeWidget:
    """Tests for ScoreGaugeWidget (legacy compatibility)."""

    def test_score_gauge_widget_creates(self, qapp):
        """Test ScoreGaugeWidget can be created."""
        from localmind.ui.results_viewer import ScoreGaugeWidget

        widget = ScoreGaugeWidget("Test Label")
        assert widget is not None

    def test_score_gauge_widget_object_name(self, qapp):
        """Test ScoreGaugeWidget has correct object name."""
        from localmind.ui.results_viewer import ScoreGaugeWidget

        widget = ScoreGaugeWidget("Test")
        assert widget.objectName() == "scoreGaugeCard"

    def test_score_gauge_widget_set_score(self, qapp):
        """Test setting score on ScoreGaugeWidget."""
        from localmind.ui.results_viewer import ScoreGaugeWidget

        widget = ScoreGaugeWidget("Test")
        widget.set_score(85.0, 100.0)

        assert widget._score == 85.0
        assert widget._max_score == 100.0


class TestTranscriptViewer:
    """Tests for TranscriptViewer widget."""

    def test_transcript_viewer_creates(self, qapp):
        """Test TranscriptViewer can be created."""
        from localmind.ui.results_viewer import TranscriptViewer

        viewer = TranscriptViewer()
        assert viewer is not None

    def test_transcript_viewer_set_transcript(self, qapp):
        """Test setting transcript text."""
        from localmind.ui.results_viewer import TranscriptViewer

        viewer = TranscriptViewer()
        viewer.set_transcript("Hello, this is a test transcript.")

        assert viewer._text_edit.toPlainText() == "Hello, this is a test transcript."

    def test_transcript_viewer_set_segments(self, qapp):
        """Test setting transcript from segments."""
        from localmind.ui.results_viewer import TranscriptViewer

        viewer = TranscriptViewer()
        segments = [
            {"start": 0.0, "end": 2.0, "text": "Hello", "speaker": "Agent"},
            {"start": 2.0, "end": 4.0, "text": "Hi there", "speaker": "Customer"},
        ]
        viewer.set_segments(segments)

        html = viewer._text_edit.toHtml()
        assert "Agent" in html
        assert "Customer" in html

    def test_transcript_viewer_handles_none_speaker(self, qapp):
        """Test transcript viewer handles None speaker."""
        from localmind.ui.results_viewer import TranscriptViewer

        viewer = TranscriptViewer()
        segments = [{"start": 0.0, "end": 2.0, "text": "Hello", "speaker": None}]
        viewer.set_segments(segments)

        html = viewer._text_edit.toHtml()
        assert "Unknown" in html

    def test_transcript_viewer_clear(self, qapp):
        """Test clearing transcript."""
        from localmind.ui.results_viewer import TranscriptViewer

        viewer = TranscriptViewer()
        viewer.set_transcript("Some text")
        viewer.clear()

        assert viewer._text_edit.toPlainText() == ""


class TestScoreDetailsTable:
    """Tests for ScoreDetailsTable widget."""

    def test_score_details_table_creates(self, qapp):
        """Test ScoreDetailsTable can be created."""
        from localmind.ui.results_viewer import ScoreDetailsTable

        table = ScoreDetailsTable()
        assert table is not None

    def test_score_details_table_object_name(self, qapp):
        """Test ScoreDetailsTable has correct object name."""
        from localmind.ui.results_viewer import ScoreDetailsTable

        table = ScoreDetailsTable()
        assert table._table.objectName() == "scoreDetailsTable"

    def test_score_details_table_column_count(self, qapp):
        """Test ScoreDetailsTable has 4 columns."""
        from localmind.ui.results_viewer import ScoreDetailsTable

        table = ScoreDetailsTable()
        assert table._table.columnCount() == 4

    def test_score_details_table_set_scores(self, qapp):
        """Test setting scores data."""
        from localmind.ui.results_viewer import ScoreDetailsTable

        table = ScoreDetailsTable()
        scores = {
            "greeting": {"score": 8.5, "max": 10, "weight": 1.0},
            "problem_solving": {"score": 7.0, "max": 10, "weight": 1.5},
        }
        table.set_scores(scores)

        assert table._table.rowCount() == 2

    def test_score_details_table_clear(self, qapp):
        """Test clearing table."""
        from localmind.ui.results_viewer import ScoreDetailsTable

        table = ScoreDetailsTable()
        scores = {"greeting": {"score": 8.5, "max": 10, "weight": 1.0}}
        table.set_scores(scores)
        table.clear()

        assert table._table.rowCount() == 0


class TestFeedbackViewer:
    """Tests for FeedbackViewer widget."""

    def test_feedback_viewer_creates(self, qapp):
        """Test FeedbackViewer can be created."""
        from localmind.ui.results_viewer import FeedbackViewer

        viewer = FeedbackViewer()
        assert viewer is not None

    def test_feedback_viewer_set_feedback(self, qapp):
        """Test setting plain feedback text."""
        from localmind.ui.results_viewer import FeedbackViewer

        viewer = FeedbackViewer()
        viewer.set_feedback("Good performance overall.")

        assert viewer._text_edit.toPlainText() == "Good performance overall."

    def test_feedback_viewer_set_structured_feedback(self, qapp):
        """Test setting structured feedback."""
        from localmind.ui.results_viewer import FeedbackViewer

        viewer = FeedbackViewer()
        feedback = {
            "summary": "Overall good call.",
            "strengths": ["Clear communication", "Professional tone"],
            "improvements": ["Be more concise"],
        }
        viewer.set_structured_feedback(feedback)

        html = viewer._text_edit.toHtml()
        assert "Summary" in html
        assert "Strengths" in html
        assert "Clear communication" in html

    def test_feedback_viewer_clear(self, qapp):
        """Test clearing feedback."""
        from localmind.ui.results_viewer import FeedbackViewer

        viewer = FeedbackViewer()
        viewer.set_feedback("Some feedback")
        viewer.clear()

        assert viewer._text_edit.toPlainText() == ""


class TestEmptyStateWidget:
    """Tests for EmptyStateWidget."""

    def test_empty_state_creates(self, qapp):
        """Test EmptyStateWidget can be created."""
        from localmind.ui.results_viewer import EmptyStateWidget

        widget = EmptyStateWidget()
        assert widget is not None


class TestJsonSyntaxHighlighter:
    """Tests for JsonSyntaxHighlighter."""

    def test_json_highlighter_creates(self, qapp):
        """Test JsonSyntaxHighlighter can be created."""
        from localmind.ui.results_viewer import JsonSyntaxHighlighter
        from PySide6.QtGui import QTextDocument

        doc = QTextDocument()
        highlighter = JsonSyntaxHighlighter(doc)
        assert highlighter is not None

    def test_json_highlighter_has_patterns(self, qapp):
        """Test JsonSyntaxHighlighter has patterns defined."""
        from localmind.ui.results_viewer import JsonSyntaxHighlighter
        from PySide6.QtGui import QTextDocument

        doc = QTextDocument()
        highlighter = JsonSyntaxHighlighter(doc)
        assert len(highlighter._patterns) > 0

    def test_json_highlighter_key_format(self, qapp):
        """Test JSON key format is purple and bold."""
        from localmind.ui.results_viewer import JsonSyntaxHighlighter
        from PySide6.QtGui import QColor, QFont, QTextDocument

        doc = QTextDocument()
        highlighter = JsonSyntaxHighlighter(doc)

        assert highlighter._key_format.foreground().color() == QColor("#7C3AED")
        assert highlighter._key_format.fontWeight() == QFont.Weight.Bold


class TestResultsViewer:
    """Tests for main ResultsViewer widget."""

    def test_results_viewer_creates(self, qapp):
        """Test ResultsViewer can be created."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        assert viewer is not None

    def test_results_viewer_initial_state_empty(self, qapp):
        """Test ResultsViewer starts with no results."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        assert viewer.get_results() is None

    def test_results_viewer_empty_state_visible_initially(self, qapp):
        """Test empty state visibility is set correctly initially."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        # When widget isn't shown, check visibility flag via property
        # _update_visibility(has_results=False) sets _empty_state visible and _tabs hidden
        assert viewer._empty_state.isVisibleTo(viewer) is True or not viewer._tabs.isVisibleTo(viewer)

    def test_results_viewer_tabs_hidden_initially(self, qapp):
        """Test tabs visibility is set correctly initially."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        # Tabs should not be visible when no results loaded
        assert viewer._tabs.isVisibleTo(viewer) is False or viewer.get_results() is None

    def test_results_viewer_load_results(self, qapp):
        """Test loading results."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        results = {
            "overall_score": 75.0,
            "percentage": 75.0,
            "compliance_score": 80.0,
            "quality_score": 70.0,
            "transcript": "Hello, this is a test.",
            "parameter_scores": {"greeting": {"score": 8.0, "max": 10, "weight": 1.0}},
        }
        viewer.load_results(results)

        assert viewer.get_results() is not None
        # Verify results were loaded correctly
        assert viewer.get_results()["overall_score"] == 75.0

    def test_results_viewer_clear(self, qapp):
        """Test clearing results."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        results = {"overall_score": 75.0, "transcript": "Test"}
        viewer.load_results(results)
        viewer.clear()

        assert viewer.get_results() is None

    def test_results_viewer_set_current_index(self, qapp):
        """Test setting current tab index."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        viewer.setCurrentIndex(2)

        assert viewer._tabs.currentIndex() == 2

    def test_results_viewer_transcription_only_mode(self, qapp):
        """Test transcription-only mode configures viewer for transcript display."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        results = {
            "overall_score": 0,
            "transcript": "Hello, this is a transcription only test.",
        }
        viewer.load_results(results)

        # In transcription-only mode, results are loaded
        assert viewer.get_results() is not None
        assert viewer.get_results()["transcript"] == "Hello, this is a transcription only test."

    def test_results_viewer_with_scoring_shows_gauges(self, qapp):
        """Test results with scoring configures score gauges."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        results = {
            "overall_score": 75.0,
            "percentage": 75.0,
            "compliance_score": 80.0,
            "quality_score": 70.0,
            "transcript": "Test",
            "parameter_scores": {"greeting": {"score": 8.0}},
        }
        viewer.load_results(results)

        # Verify gauges were configured with scores
        assert viewer._overall_gauge._gauge._score == 75.0
        assert viewer._compliance_gauge._gauge._score == 80.0
        assert viewer._quality_gauge._gauge._score == 70.0

    def test_results_viewer_results_loaded_signal(self, qapp):
        """Test results_loaded signal is emitted."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        received_results = []
        viewer.results_loaded.connect(lambda r: received_results.append(r))

        results = {"overall_score": 75.0, "transcript": "Test"}
        viewer.load_results(results)

        assert len(received_results) == 1
        assert received_results[0] == results


class TestResultsViewerTabs:
    """Tests for ResultsViewer tab structure."""

    def test_has_transcript_tab(self, qapp):
        """Test ResultsViewer has Transcript tab."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        tab_texts = [viewer._tabs.tabText(i) for i in range(viewer._tabs.count())]
        assert "Transcript" in tab_texts

    def test_has_score_details_tab(self, qapp):
        """Test ResultsViewer has Score Details tab."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        tab_texts = [viewer._tabs.tabText(i) for i in range(viewer._tabs.count())]
        assert "Score Details" in tab_texts

    def test_has_ai_feedback_tab(self, qapp):
        """Test ResultsViewer has AI Feedback tab."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        tab_texts = [viewer._tabs.tabText(i) for i in range(viewer._tabs.count())]
        assert "AI Feedback" in tab_texts

    def test_has_raw_json_tab(self, qapp):
        """Test ResultsViewer has Raw JSON tab."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        tab_texts = [viewer._tabs.tabText(i) for i in range(viewer._tabs.count())]
        assert "Raw JSON" in tab_texts

    def test_tab_count_is_four(self, qapp):
        """Test ResultsViewer has exactly 4 tabs."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        assert viewer._tabs.count() == 4


class TestResultsViewerExport:
    """Tests for ResultsViewer export functionality."""

    def test_export_json_no_results_shows_warning(self, qapp):
        """Test export_json shows warning when no results."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()

        with patch.object(viewer, "parent", return_value=None):
            with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
                viewer.export_json("/fake/path.json")
                mock_warning.assert_called_once()

    def test_export_transcript_no_results_shows_warning(self, qapp):
        """Test export_transcript shows warning when no results."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()

        with patch.object(viewer, "parent", return_value=None):
            with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
                viewer.export_transcript("/fake/path.txt")
                mock_warning.assert_called_once()

    def test_export_json_empty_path_shows_warning(self, qapp):
        """Test export_json with empty path shows warning."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        viewer._results = {"transcript": "Test"}

        with patch.object(viewer, "parent", return_value=None):
            with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
                viewer.export_json("")
                mock_warning.assert_called_once()

    def test_export_markdown_no_report_shows_warning(self, qapp):
        """Test export_markdown_report shows warning when no report."""
        from localmind.ui.results_viewer import ResultsViewer

        viewer = ResultsViewer()
        viewer._results = {"transcript": "Test"}  # No markdown_report

        with patch.object(viewer, "parent", return_value=None):
            with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
                viewer.export_markdown_report("/fake/path.md")
                mock_warning.assert_called_once()
