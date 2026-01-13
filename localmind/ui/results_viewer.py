"""
LocalMind Results Viewer

Displays audit results with transcript, scores, and feedback.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QFrame,
    QScrollArea, QSplitter, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class ScoreGaugeWidget(QFrame):
    """Widget showing a score with visual gauge."""

    def __init__(self, label: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._label = label
        self._score: float = 0.0
        self._max_score: float = 100.0
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self._label_widget = QLabel(self._label)
        self._label_widget.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._label_widget)

        self._score_label = QLabel("--")
        self._score_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self._score_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_score(self, score: float, max_score: float = 100.0) -> None:
        """Set the score value."""
        self._score = score
        self._max_score = max_score
        self._score_label.setText(f"{score:.1f}")

        # Color based on percentage
        pct = (score / max_score) * 100 if max_score > 0 else 0
        if pct >= 80:
            color = "#4CAF50"  # Green
        elif pct >= 60:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red

        self._score_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")


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
        self._text_edit.setStyleSheet("font-family: monospace;")
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

            color = "#2196F3" if speaker == "Agent" else "#9C27B0"
            html.append(
                f'<p><span style="color: {color}; font-weight: bold;">'
                f'[{start:.1f}s - {end:.1f}s] {speaker}:</span> {text}</p>'
            )

        self._text_edit.setHtml("".join(html))

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
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Parameter", "Score", "Max", "Weight"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setAlternatingRowColors(True)
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
        layout.addWidget(self._text_edit)

    def set_feedback(self, feedback: str) -> None:
        """Set the feedback text."""
        self._text_edit.setPlainText(feedback)

    def set_structured_feedback(self, feedback: Dict[str, Any]) -> None:
        """Set structured feedback with sections."""
        html = []

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


class ResultsViewer(QWidget):
    """Main results viewer with tabs for different views."""

    results_loaded = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._results: Optional[Dict[str, Any]] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Score summary at top
        scores_layout = QHBoxLayout()
        self._overall_gauge = ScoreGaugeWidget("Overall Score")
        scores_layout.addWidget(self._overall_gauge)

        self._compliance_gauge = ScoreGaugeWidget("Compliance")
        scores_layout.addWidget(self._compliance_gauge)

        self._quality_gauge = ScoreGaugeWidget("Quality")
        scores_layout.addWidget(self._quality_gauge)

        layout.addLayout(scores_layout)

        # Tab widget for detailed views
        self._tabs = QTabWidget()

        # Transcript tab
        self._transcript_viewer = TranscriptViewer()
        self._tabs.addTab(self._transcript_viewer, "Transcript")

        # Scores tab
        self._scores_table = ScoreDetailsTable()
        self._tabs.addTab(self._scores_table, "Score Details")

        # Feedback tab
        self._feedback_viewer = FeedbackViewer()
        self._tabs.addTab(self._feedback_viewer, "AI Feedback")

        # Raw JSON tab
        self._raw_json = QTextEdit()
        self._raw_json.setReadOnly(True)
        self._raw_json.setStyleSheet("font-family: monospace; font-size: 11px;")
        self._tabs.addTab(self._raw_json, "Raw JSON")

        layout.addWidget(self._tabs)

    def load_results(self, results: Dict[str, Any]) -> None:
        """Load audit results."""
        self._results = results

        # Update gauges
        overall = results.get("overall_score", 0)
        self._overall_gauge.set_score(overall)

        compliance = results.get("compliance_score", 0)
        self._compliance_gauge.set_score(compliance)

        quality = results.get("quality_score", 0)
        self._quality_gauge.set_score(quality)

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
        self._raw_json.setPlainText(json.dumps(results, indent=2))

        self.results_loaded.emit(results)

    def clear(self) -> None:
        """Clear all results."""
        self._results = None
        self._overall_gauge.set_score(0)
        self._compliance_gauge.set_score(0)
        self._quality_gauge.set_score(0)
        self._transcript_viewer.clear()
        self._scores_table.clear()
        self._feedback_viewer.clear()
        self._raw_json.clear()

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

    def export_pdf(self, filepath: str) -> None:
        """Export results to PDF file."""
        if not self._results:
            QMessageBox.warning(self, "No Results", "No results to export.")
            return

        # TODO: Implement PDF export with WeasyPrint
        QMessageBox.information(self, "Coming Soon", "PDF export coming soon.")

    def get_results(self) -> Optional[Dict[str, Any]]:
        """Get the current results."""
        return self._results
