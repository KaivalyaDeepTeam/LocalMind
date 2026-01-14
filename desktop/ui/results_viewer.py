"""
Results Viewer Panel

Displays transcription and audit results with tabs for different views.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QFrame,
    QScrollArea,
    QSplitter,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont


class ResultsViewer(QWidget):
    """Panel for viewing processing results."""

    # Signals
    export_requested = Signal(str)  # format: "json" or "pdf"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._results: Optional[Dict[str, Any]] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the results viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget for different views
        self._tabs = QTabWidget()

        # Transcript tab
        self._transcript_tab = self._create_transcript_tab()
        self._tabs.addTab(self._transcript_tab, "Transcript")

        # Audit tab
        self._audit_tab = self._create_audit_tab()
        self._tabs.addTab(self._audit_tab, "Audit Results")

        # Quality tab
        self._quality_tab = self._create_quality_tab()
        self._tabs.addTab(self._quality_tab, "Quality Scores")

        # Raw JSON tab
        self._json_tab = self._create_json_tab()
        self._tabs.addTab(self._json_tab, "Raw JSON")

        layout.addWidget(self._tabs)

        # Show placeholder
        self._show_placeholder()

    def _create_transcript_tab(self) -> QWidget:
        """Create the transcript view tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header_layout = QHBoxLayout()
        self._transcript_header = QLabel("Transcript")
        self._transcript_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self._transcript_header)
        header_layout.addStretch()

        # Duration label
        self._duration_label = QLabel("")
        self._duration_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self._duration_label)

        layout.addLayout(header_layout)

        # Transcript text
        self._transcript_text = QTextEdit()
        self._transcript_text.setReadOnly(True)
        self._transcript_text.setFont(QFont("Menlo", 11))
        self._transcript_text.setPlaceholderText(
            "Transcript will appear here after processing..."
        )
        layout.addWidget(self._transcript_text)

        return widget

    def _create_audit_tab(self) -> QWidget:
        """Create the audit results tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Summary frame
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_layout = QVBoxLayout(summary_frame)

        self._audit_summary_label = QLabel("Audit Summary")
        self._audit_summary_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        summary_layout.addWidget(self._audit_summary_label)

        # Score display
        score_layout = QHBoxLayout()

        self._score_label = QLabel("--")
        self._score_label.setStyleSheet(
            "font-size: 48px; font-weight: bold; color: #27ae60;"
        )
        score_layout.addWidget(self._score_label)

        self._grade_label = QLabel("")
        self._grade_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        score_layout.addWidget(self._grade_label)

        score_layout.addStretch()

        # Recommendation
        self._recommendation_label = QLabel("")
        self._recommendation_label.setStyleSheet("font-size: 16px;")
        score_layout.addWidget(self._recommendation_label)

        summary_layout.addLayout(score_layout)

        layout.addWidget(summary_frame)

        # RAZT Violations
        razt_frame = QFrame()
        razt_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        razt_layout = QVBoxLayout(razt_frame)

        self._razt_header = QLabel("RAZT Violations")
        self._razt_header.setStyleSheet("font-weight: bold;")
        razt_layout.addWidget(self._razt_header)

        self._razt_text = QTextEdit()
        self._razt_text.setReadOnly(True)
        self._razt_text.setMaximumHeight(150)
        self._razt_text.setPlaceholderText("No violations detected")
        razt_layout.addWidget(self._razt_text)

        layout.addWidget(razt_frame)

        # Strengths and Improvements
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Strengths
        strengths_widget = QWidget()
        strengths_layout = QVBoxLayout(strengths_widget)
        strengths_layout.setContentsMargins(0, 0, 0, 0)

        strengths_label = QLabel("Strengths")
        strengths_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        strengths_layout.addWidget(strengths_label)

        self._strengths_text = QTextEdit()
        self._strengths_text.setReadOnly(True)
        strengths_layout.addWidget(self._strengths_text)

        splitter.addWidget(strengths_widget)

        # Improvements
        improvements_widget = QWidget()
        improvements_layout = QVBoxLayout(improvements_widget)
        improvements_layout.setContentsMargins(0, 0, 0, 0)

        improvements_label = QLabel("Areas for Improvement")
        improvements_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        improvements_layout.addWidget(improvements_label)

        self._improvements_text = QTextEdit()
        self._improvements_text.setReadOnly(True)
        improvements_layout.addWidget(self._improvements_text)

        splitter.addWidget(improvements_widget)

        layout.addWidget(splitter, stretch=1)

        return widget

    def _create_quality_tab(self) -> QWidget:
        """Create the quality scores table tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel("Quality Parameter Scores")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        # Table
        self._quality_table = QTableWidget()
        self._quality_table.setColumnCount(5)
        self._quality_table.setHorizontalHeaderLabels(
            ["Parameter", "Score", "Max", "Verdict", "Feedback"]
        )
        self._quality_table.horizontalHeader().setStretchLastSection(True)
        self._quality_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._quality_table.setAlternatingRowColors(True)
        self._quality_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self._quality_table)

        return widget

    def _create_json_tab(self) -> QWidget:
        """Create the raw JSON view tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header with copy button
        header_layout = QHBoxLayout()

        header = QLabel("Raw JSON Output")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header)

        header_layout.addStretch()

        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self._copy_json_to_clipboard)
        header_layout.addWidget(copy_btn)

        layout.addLayout(header_layout)

        # JSON text
        self._json_text = QTextEdit()
        self._json_text.setReadOnly(True)
        self._json_text.setFont(QFont("Menlo", 10))
        self._json_text.setPlaceholderText("JSON output will appear here...")
        layout.addWidget(self._json_text)

        return widget

    def _show_placeholder(self) -> None:
        """Show placeholder content."""
        self._transcript_text.setPlainText("")
        self._score_label.setText("--")
        self._grade_label.setText("")
        self._recommendation_label.setText("")
        self._razt_text.setPlainText("")
        self._strengths_text.setPlainText("")
        self._improvements_text.setPlainText("")
        self._quality_table.setRowCount(0)
        self._json_text.setPlainText("")
        self._duration_label.setText("")

    def _copy_json_to_clipboard(self) -> None:
        """Copy JSON to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self._json_text.toPlainText())

    # Public methods
    def set_results(self, results: Dict[str, Any]) -> None:
        """Set and display results."""
        self._results = results
        self._update_display()

    def clear(self) -> None:
        """Clear all results."""
        self._results = None
        self._show_placeholder()

    def _update_display(self) -> None:
        """Update display with current results."""
        if not self._results:
            self._show_placeholder()
            return

        # Update transcript tab
        transcript = self._results.get("transcription", {})
        merged = transcript.get("merged_transcript", "")
        self._transcript_text.setPlainText(merged)

        duration = transcript.get("audio_duration_seconds", 0)
        if duration:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self._duration_label.setText(f"Duration: {minutes}m {seconds}s")

        # Update audit tab
        audit = self._results.get("audit", {})
        quality = audit.get("quality", {})

        total_score = quality.get("total_score", 0)
        grade = quality.get("grade", "")
        recommendation = audit.get("overall_recommendation", "")

        self._score_label.setText(str(total_score))
        self._grade_label.setText(grade)
        self._recommendation_label.setText(recommendation)

        # Color score based on value
        if total_score >= 80:
            self._score_label.setStyleSheet(
                "font-size: 48px; font-weight: bold; color: #27ae60;"
            )
        elif total_score >= 60:
            self._score_label.setStyleSheet(
                "font-size: 48px; font-weight: bold; color: #f39c12;"
            )
        else:
            self._score_label.setStyleSheet(
                "font-size: 48px; font-weight: bold; color: #e74c3c;"
            )

        # RAZT violations
        razt = audit.get("razt", {})
        has_zt = razt.get("has_zt_violation", False)
        has_ra = razt.get("has_ra_violation", False)

        if has_zt or has_ra:
            violations_text = razt.get("summary", "Violations detected")
            self._razt_text.setPlainText(violations_text)
            self._razt_text.setStyleSheet("background-color: #fdf2e9;")
        else:
            self._razt_text.setPlainText("No violations detected")
            self._razt_text.setStyleSheet("")

        # Strengths
        strengths = quality.get("strengths", [])
        if strengths:
            self._strengths_text.setPlainText("\n".join(f"• {s}" for s in strengths))

        # Improvements
        improvements = quality.get("improvements", [])
        if improvements:
            self._improvements_text.setPlainText(
                "\n".join(f"• {i}" for i in improvements)
            )

        # Quality table
        parameters = quality.get("parameters", [])
        self._quality_table.setRowCount(len(parameters))

        for row, param in enumerate(parameters):
            name_item = QTableWidgetItem(param.get("name", ""))
            score_item = QTableWidgetItem(str(param.get("score", 0)))
            max_item = QTableWidgetItem(str(param.get("max_score", 0)))
            verdict_item = QTableWidgetItem(param.get("verdict", ""))
            feedback_item = QTableWidgetItem(param.get("feedback", ""))

            # Color based on verdict
            verdict = param.get("verdict", "").upper()
            if verdict == "NO_MARKDOWN":
                score_item.setBackground(QColor("#d5f5e3"))
            elif "MARKDOWN" in verdict:
                score_item.setBackground(QColor("#fadbd8"))

            self._quality_table.setItem(row, 0, name_item)
            self._quality_table.setItem(row, 1, score_item)
            self._quality_table.setItem(row, 2, max_item)
            self._quality_table.setItem(row, 3, verdict_item)
            self._quality_table.setItem(row, 4, feedback_item)

        # JSON tab
        self._json_text.setPlainText(json.dumps(self._results, indent=2))

    def export_json(self, filepath: str) -> bool:
        """Export results as JSON."""
        if not self._results:
            QMessageBox.warning(
                self, "No Results", "No results to export. Process an audio file first."
            )
            return False

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._results, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export JSON:\n{e}")
            return False

    def export_pdf(self, filepath: str) -> bool:
        """Export results as PDF."""
        if not self._results:
            QMessageBox.warning(
                self, "No Results", "No results to export. Process an audio file first."
            )
            return False

        # TODO: Implement PDF export with WeasyPrint
        QMessageBox.information(
            self, "Coming Soon", "PDF export will be available in a future update."
        )
        return False

    def get_results(self) -> Optional[Dict[str, Any]]:
        """Get current results."""
        return self._results
