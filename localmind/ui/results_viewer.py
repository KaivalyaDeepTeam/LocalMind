"""
LocalMind Results Viewer

Displays audit results with transcript, scores, and feedback.
Features animated circular score gauges and modern UI.
"""

import json
import math
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QFrame,
    QScrollArea, QSplitter, QMessageBox, QPushButton, QSizePolicy,
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, Property,
    QRectF, QPointF,
)
from PySide6.QtGui import (
    QColor, QPainter, QPen, QFont, QBrush, QPainterPath,
    QLinearGradient, QConicalGradient, QSyntaxHighlighter, QTextCharFormat,
)
import re


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Simple JSON syntax highlighter for the raw JSON viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Define formats for different JSON elements
        self._key_format = QTextCharFormat()
        self._key_format.setForeground(QColor("#7C3AED"))  # Purple for keys
        self._key_format.setFontWeight(QFont.Weight.Bold)

        self._string_format = QTextCharFormat()
        self._string_format.setForeground(QColor("#059669"))  # Green for strings

        self._number_format = QTextCharFormat()
        self._number_format.setForeground(QColor("#D97706"))  # Amber for numbers

        self._keyword_format = QTextCharFormat()
        self._keyword_format.setForeground(QColor("#DC2626"))  # Red for keywords

        self._bracket_format = QTextCharFormat()
        self._bracket_format.setForeground(QColor("#64748B"))  # Gray for brackets

        # Patterns for highlighting
        self._patterns = [
            # JSON keys (before colon)
            (r'"([^"\\]|\\.)*"\s*:', self._key_format),
            # String values
            (r':\s*"([^"\\]|\\.)*"', self._string_format),
            # Numbers
            (r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b', self._number_format),
            # Keywords (true, false, null)
            (r'\b(true|false|null)\b', self._keyword_format),
            # Brackets and braces
            (r'[\[\]{}]', self._bracket_format),
        ]

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to a block of text."""
        for pattern, fmt in self._patterns:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)


class CircularScoreGauge(QWidget):
    """
    Animated circular gauge showing a score with arc visualization.

    Features:
    - Animated arc drawing (0 to score%)
    - Color gradient based on score
    - Inner text with score and grade letter
    - Smooth animation on value change
    - Colorblind-friendly mode
    """

    # Standard colors (red-orange-green)
    COLORS_STANDARD = {
        "high": "#059669",    # Green - Emerald-600
        "medium": "#D97706",  # Orange - Amber-600
        "low": "#DC2626",     # Red
    }

    # Colorblind-friendly colors (blue-purple-orange)
    COLORS_COLORBLIND = {
        "high": "#2563EB",    # Blue
        "medium": "#7C3AED",  # Purple
        "low": "#EA580C",     # Orange (instead of red)
    }

    # Class-level colorblind mode setting
    _colorblind_mode = False

    @classmethod
    def set_colorblind_mode(cls, enabled: bool) -> None:
        """Set colorblind mode for all score gauges."""
        cls._colorblind_mode = enabled

    @classmethod
    def is_colorblind_mode(cls) -> bool:
        """Check if colorblind mode is enabled."""
        return cls._colorblind_mode

    def __init__(
        self,
        label: str = "",
        size: int = 120,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._label = label
        self._size = size
        self._score: float = 0.0
        self._animated_score: float = 0.0
        self._max_score: float = 100.0

        # Animation
        self._animation = QPropertyAnimation(self, b"animatedScore")
        self._animation.setDuration(800)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setMinimumSize(size, size + 30)
        self.setMaximumSize(size + 40, size + 50)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def get_animated_score(self) -> float:
        return self._animated_score

    def set_animated_score(self, value: float) -> None:
        self._animated_score = value
        self.update()

    animatedScore = Property(float, get_animated_score, set_animated_score)

    def set_score(self, score: float, max_score: float = 100.0) -> None:
        """Set the score with animation."""
        self._score = score
        self._max_score = max_score

        # Animate to new value
        self._animation.stop()
        self._animation.setStartValue(self._animated_score)
        self._animation.setEndValue(score)
        self._animation.start()

    def set_score_instant(self, score: float, max_score: float = 100.0) -> None:
        """Set score without animation."""
        self._score = score
        self._max_score = max_score
        self._animated_score = score
        self.update()

    def _get_color_for_score(self, pct: float) -> QColor:
        """Get color based on score percentage (colorblind-aware)."""
        colors = self.COLORS_COLORBLIND if self._colorblind_mode else self.COLORS_STANDARD
        if pct >= 80:
            return QColor(colors["high"])
        elif pct >= 60:
            return QColor(colors["medium"])
        else:
            return QColor(colors["low"])

    def _get_grade(self, pct: float) -> str:
        """Get letter grade for percentage."""
        if pct >= 90:
            return "A"
        elif pct >= 80:
            return "B"
        elif pct >= 70:
            return "C"
        elif pct >= 60:
            return "D"
        else:
            return "F"

    def paintEvent(self, event) -> None:
        """Paint the circular gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        width = self.width()
        height = self.height()
        gauge_size = min(width, height - 30) - 10
        center_x = width / 2
        center_y = (height - 30) / 2 + 5

        # Draw background arc
        pen = QPen(QColor("#E2E8F0"), 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rect = QRectF(
            center_x - gauge_size / 2,
            center_y - gauge_size / 2,
            gauge_size,
            gauge_size,
        )

        # Background arc (270 degrees, starting from bottom-left)
        start_angle = 225 * 16  # Qt uses 1/16th of a degree
        span_angle = -270 * 16

        painter.drawArc(rect, start_angle, span_angle)

        # Draw progress arc
        pct = (self._animated_score / self._max_score) * 100 if self._max_score > 0 else 0
        color = self._get_color_for_score(pct)

        pen = QPen(color, 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        progress_span = int(-270 * 16 * (pct / 100))
        painter.drawArc(rect, start_angle, progress_span)

        # Draw center text (score)
        painter.setPen(QColor("#0F172A"))
        font = QFont("", 22, QFont.Weight.Bold)
        painter.setFont(font)

        score_text = f"{self._animated_score:.0f}"
        text_rect = QRectF(
            center_x - gauge_size / 2,
            center_y - 15,
            gauge_size,
            30,
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, score_text)

        # Draw grade letter below score
        grade = self._get_grade(pct)
        font = QFont("", 12, QFont.Weight.Medium)
        painter.setFont(font)
        painter.setPen(color)

        grade_rect = QRectF(
            center_x - gauge_size / 2,
            center_y + 10,
            gauge_size,
            20,
        )
        painter.drawText(grade_rect, Qt.AlignmentFlag.AlignCenter, grade)

        # Draw label at bottom
        if self._label:
            painter.setPen(QColor("#64748B"))
            font = QFont("", 11, QFont.Weight.Medium)
            painter.setFont(font)

            label_rect = QRectF(0, height - 25, width, 20)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self._label)


class ScoreGaugeWidget(QFrame):
    """Widget showing a score with visual gauge (legacy compatibility)."""

    def __init__(self, label: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._label = label
        self._score: float = 0.0
        self._max_score: float = 100.0
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setObjectName("scoreGaugeCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Circular gauge with grade explanation tooltip
        self._gauge = CircularScoreGauge(self._label, size=100)
        self._gauge.setToolTip(
            "Grade Scale:\n"
            "A = 90-100% (Excellent)\n"
            "B = 80-89% (Good)\n"
            "C = 70-79% (Average)\n"
            "D = 60-69% (Below Average)\n"
            "F = Below 60% (Needs Improvement)"
        )
        layout.addWidget(self._gauge, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_score(self, score: float, max_score: float = 100.0) -> None:
        """Set the score value."""
        self._score = score
        self._max_score = max_score
        self._gauge.set_score(score, max_score)


class TranscriptViewer(QWidget):
    """Widget for viewing transcript with speaker labels."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setObjectName("transcriptViewer")
        layout.addWidget(self._text_edit)

    def set_transcript(self, transcript: str) -> None:
        """Set the transcript text."""
        self._text_edit.setPlainText(transcript)

    def set_segments(self, segments: list) -> None:
        """Set transcript from segments with speaker labels."""
        html = []
        for seg in segments:
            speaker = seg.get("speaker", "Unknown")
            text = seg.get("text", "")
            start = seg.get("start", 0)
            end = seg.get("end", 0)

            # Use theme-aware colors
            speaker_class = "agent" if speaker.lower() == "agent" else "customer"
            html.append(
                f'<p style="margin: 8px 0;">'
                f'<span class="{speaker_class}" style="font-weight: 600;">'
                f'[{start:.1f}s - {end:.1f}s] {speaker}:</span> {text}</p>'
            )

        self._text_edit.setHtml(
            '<style>'
            '.agent { color: #4F46E5; }'
            '.customer { color: #7C3AED; }'
            '</style>'
            + "".join(html)
        )

    def clear(self) -> None:
        """Clear the transcript."""
        self._text_edit.clear()


class ScoreDetailsTable(QWidget):
    """Widget showing detailed scoring breakdown."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setObjectName("scoreDetailsTable")
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Parameter", "Score", "Max", "Weight"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def set_scores(self, scores: Dict[str, Any]) -> None:
        """Set the scoring data."""
        self._table.setRowCount(0)

        for param, data in scores.items():
            row = self._table.rowCount()
            self._table.insertRow(row)

            # Parameter name
            name_item = QTableWidgetItem(param.replace("_", " ").title())
            self._table.setItem(row, 0, name_item)

            # Score
            score = data.get("score", 0) if isinstance(data, dict) else data
            score_item = QTableWidgetItem(f"{score:.1f}")
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, score_item)

            # Max score
            max_score = data.get("max", 10) if isinstance(data, dict) else 10
            max_item = QTableWidgetItem(f"{max_score}")
            max_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, max_item)

            # Weight
            weight = data.get("weight", 1.0) if isinstance(data, dict) else 1.0
            weight_item = QTableWidgetItem(f"{weight:.1f}")
            weight_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, weight_item)

    def clear(self) -> None:
        """Clear the table."""
        self._table.setRowCount(0)


class FeedbackViewer(QWidget):
    """Widget for viewing AI feedback."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setObjectName("feedbackViewer")
        layout.addWidget(self._text_edit)

    def set_feedback(self, feedback: str) -> None:
        """Set the feedback text."""
        self._text_edit.setPlainText(feedback)

    def set_structured_feedback(self, feedback: Dict[str, Any]) -> None:
        """Set structured feedback with sections."""
        html = ['<style>h3 { color: #4F46E5; margin-top: 16px; } li { margin: 4px 0; }</style>']

        if "summary" in feedback:
            html.append(f"<h3>Summary</h3><p>{feedback['summary']}</p>")

        if "strengths" in feedback:
            html.append("<h3>Strengths</h3><ul>")
            for item in feedback["strengths"]:
                html.append(f"<li>{item}</li>")
            html.append("</ul>")

        if "improvements" in feedback:
            html.append("<h3>Areas for Improvement</h3><ul>")
            for item in feedback["improvements"]:
                html.append(f"<li>{item}</li>")
            html.append("</ul>")

        if "recommendations" in feedback:
            html.append("<h3>Recommendations</h3><ul>")
            for item in feedback["recommendations"]:
                html.append(f"<li>{item}</li>")
            html.append("</ul>")

        self._text_edit.setHtml("".join(html))

    def clear(self) -> None:
        """Clear the feedback."""
        self._text_edit.clear()


class EmptyStateWidget(QWidget):
    """Widget shown when no results are loaded."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon placeholder (text-based)
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Title
        title = QLabel("No Results Yet")
        title.setObjectName("emptyStateTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #64748B;")
        layout.addWidget(title)

        # Description
        desc = QLabel("Process an audio file to see results here")
        desc.setObjectName("emptyStateDesc")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 13px; color: #94A3B8;")
        layout.addWidget(desc)


class ResultsViewer(QWidget):
    """Main results viewer with tabs for different views."""

    results_loaded = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._results: Optional[Dict[str, Any]] = None
        self._scroll_positions: Dict[int, int] = {}  # Track scroll position per tab
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Score summary at top
        self._scores_container = QFrame()
        self._scores_container.setObjectName("scoresContainer")
        scores_layout = QHBoxLayout(self._scores_container)
        scores_layout.setContentsMargins(0, 0, 0, 0)
        scores_layout.setSpacing(16)

        self._overall_gauge = ScoreGaugeWidget("Overall Score")
        scores_layout.addWidget(self._overall_gauge)

        self._compliance_gauge = ScoreGaugeWidget("Compliance")
        scores_layout.addWidget(self._compliance_gauge)

        self._quality_gauge = ScoreGaugeWidget("Quality")
        scores_layout.addWidget(self._quality_gauge)

        scores_layout.addStretch()

        layout.addWidget(self._scores_container)

        # Tab widget for detailed views
        self._tabs = QTabWidget()
        self._tabs.setObjectName("resultsTabWidget")

        # Transcript tab
        self._transcript_viewer = TranscriptViewer()
        self._tabs.addTab(self._transcript_viewer, "Transcript")

        # Scores tab
        self._scores_table = ScoreDetailsTable()
        self._tabs.addTab(self._scores_table, "Score Details")

        # Feedback tab
        self._feedback_viewer = FeedbackViewer()
        self._tabs.addTab(self._feedback_viewer, "AI Feedback")

        # Raw JSON tab with syntax highlighting
        self._raw_json = QTextEdit()
        self._raw_json.setReadOnly(True)
        self._raw_json.setObjectName("rawJsonViewer")
        self._raw_json.setFont(QFont("Menlo", 10))
        self._json_highlighter = JsonSyntaxHighlighter(self._raw_json.document())
        self._tabs.addTab(self._raw_json, "Raw JSON")

        # Connect tab change to preserve scroll position
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._previous_tab = 0

        layout.addWidget(self._tabs)

        # Empty state (shown when no results)
        self._empty_state = EmptyStateWidget()
        layout.addWidget(self._empty_state)

        # Initially show empty state
        self._update_visibility(has_results=False)

    def _update_visibility(self, has_results: bool, transcription_only: bool = False) -> None:
        """Update visibility of components based on results state."""
        # Hide score gauges for transcription-only mode
        self._scores_container.setVisible(has_results and not transcription_only)
        self._tabs.setVisible(has_results)
        self._empty_state.setVisible(not has_results)

    def _on_tab_changed(self, new_index: int) -> None:
        """Handle tab change - save and restore scroll positions."""
        # Save scroll position of previous tab
        prev_widget = self._tabs.widget(self._previous_tab)
        if prev_widget:
            scrollable = self._get_scrollable_widget(prev_widget)
            if scrollable and hasattr(scrollable, 'verticalScrollBar'):
                self._scroll_positions[self._previous_tab] = scrollable.verticalScrollBar().value()

        # Restore scroll position of new tab
        new_widget = self._tabs.widget(new_index)
        if new_widget and new_index in self._scroll_positions:
            scrollable = self._get_scrollable_widget(new_widget)
            if scrollable and hasattr(scrollable, 'verticalScrollBar'):
                # Use timer to ensure widget is ready
                QTimer.singleShot(0, lambda: scrollable.verticalScrollBar().setValue(
                    self._scroll_positions.get(new_index, 0)
                ))

        self._previous_tab = new_index

    def _get_scrollable_widget(self, widget: QWidget) -> Optional[QWidget]:
        """Get the scrollable widget from a tab widget."""
        # Direct QTextEdit widgets
        if isinstance(widget, QTextEdit):
            return widget
        # For custom viewer widgets, find the QTextEdit child
        text_edit = widget.findChild(QTextEdit)
        if text_edit:
            return text_edit
        # For table widgets
        table = widget.findChild(QTableWidget)
        if table:
            return table
        return widget

    def load_results(self, results: Dict[str, Any]) -> None:
        """Load audit results."""
        self._results = results

        # Detect transcription-only mode (has transcript but no meaningful scores)
        is_transcription_only = (
            results.get("overall_score", 0) == 0 and
            "transcript" in results and
            not results.get("scores") and
            not results.get("parameter_scores")
        )

        self._update_visibility(has_results=True, transcription_only=is_transcription_only)

        # Update gauges with actual max_score from results (only if not transcription-only)
        if not is_transcription_only:
            max_score = results.get("max_score", 100.0)

            overall = results.get("overall_score", 0)
            self._overall_gauge.set_score(overall, max_score)

            compliance = results.get("compliance_score", 0)
            self._compliance_gauge.set_score(compliance, max_score)

            quality = results.get("quality_score", 0)
            self._quality_gauge.set_score(quality, max_score)

        # Update transcript
        if "transcript" in results:
            self._transcript_viewer.set_transcript(results["transcript"])
        elif "segments" in results:
            self._transcript_viewer.set_segments(results["segments"])

        # Update scores table
        if "scores" in results:
            self._scores_table.set_scores(results["scores"])
        elif "parameter_scores" in results:
            self._scores_table.set_scores(results["parameter_scores"])

        # Update feedback
        if "feedback" in results:
            if isinstance(results["feedback"], dict):
                self._feedback_viewer.set_structured_feedback(results["feedback"])
            else:
                self._feedback_viewer.set_feedback(results["feedback"])

        # Update raw JSON
        self._raw_json.setPlainText(json.dumps(results, indent=2, ensure_ascii=False))

        self.results_loaded.emit(results)

    def clear(self) -> None:
        """Clear all results."""
        self._results = None
        self._update_visibility(has_results=False)
        self._overall_gauge.set_score(0)
        self._compliance_gauge.set_score(0)
        self._quality_gauge.set_score(0)
        self._transcript_viewer.clear()
        self._scores_table.clear()
        self._feedback_viewer.clear()
        self._raw_json.clear()

    def setCurrentIndex(self, index: int) -> None:
        """Set the current tab index."""
        self._tabs.setCurrentIndex(index)

    def export_json(self, filepath: str) -> None:
        """Export results to JSON file."""
        if not self._results:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return

        try:
            with open(filepath, "w") as f:
                json.dump(self._results, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")

    def export_transcript(self, filepath: str) -> None:
        """Export transcript to text file."""
        if not self._results:
            QMessageBox.warning(self, "No Results", "No transcript to export.")
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                # Write header
                file_name = self._results.get("file_name", "audio")
                language = self._results.get("language", "unknown")
                f.write(f"Transcript: {file_name}\n")
                f.write(f"Language: {language}\n")
                f.write("=" * 50 + "\n\n")

                # Write segments with speaker labels if available
                if "segments" in self._results and self._results["segments"]:
                    for seg in self._results["segments"]:
                        speaker = seg.get("speaker", "Unknown")
                        text = seg.get("text", "")
                        start = seg.get("start", 0)
                        end = seg.get("end", 0)
                        f.write(f"[{start:.1f}s - {end:.1f}s] {speaker}: {text}\n\n")
                elif "transcript" in self._results:
                    # Plain transcript without segments
                    f.write(self._results["transcript"])

            QMessageBox.information(
                self, "Export Complete",
                f"Transcript exported to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export transcript: {e}")

    def export_pdf(self, filepath: str) -> None:
        """Export results to PDF file."""
        if not self._results:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return

        try:
            from localmind.reports import PDFReportGenerator, ReportOptions

            options = ReportOptions(
                include_transcript=True,
                include_chart=True,
                include_scores=True,
            )
            generator = PDFReportGenerator(options)

            if not generator.can_generate():
                QMessageBox.warning(
                    self, "Missing Dependencies",
                    "PDF export requires Jinja2 and WeasyPrint.\n\n"
                    "Install with: pip install jinja2 weasyprint"
                )
                return

            # Get file name from results or use default
            file_name = self._results.get("file_name", "audio_file")
            generator.generate_pdf(self._results, filepath, file_name)

            QMessageBox.information(
                self, "Export Complete",
                f"PDF report exported to:\n{filepath}"
            )

        except ImportError as e:
            QMessageBox.warning(
                self, "Missing Dependencies",
                f"PDF export requires additional packages:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n\n{e}")

    def get_results(self) -> Optional[Dict[str, Any]]:
        """Get the current results."""
        return self._results
