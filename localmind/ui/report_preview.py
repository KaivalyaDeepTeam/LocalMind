"""
LocalMind Report Preview Dialog

Preview and export PDF audit reports.
"""

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from localmind.reports.pdf_generator import PDFReportGenerator, ReportOptions


class PDFGenerationWorker(QThread):
    """Worker thread for PDF generation."""

    finished = Signal(bool, str)  # success, message/path
    progress = Signal(str)

    def __init__(
        self,
        generator: PDFReportGenerator,
        audit_result: dict[str, Any],
        output_path: str,
        file_name: str,
        parent=None,
    ):
        super().__init__(parent)
        self._generator = generator
        self._audit_result = audit_result
        self._output_path = output_path
        self._file_name = file_name

    def run(self):
        """Generate PDF in background."""
        try:
            self.progress.emit("Generating HTML...")
            self._generator.generate_pdf(
                self._audit_result,
                self._output_path,
                self._file_name,
            )
            self.finished.emit(True, self._output_path)
        except Exception as e:
            self.finished.emit(False, str(e))


class ReportPreviewDialog(QDialog):
    """Dialog for previewing and exporting PDF reports."""

    report_exported = Signal(str)

    def __init__(
        self,
        audit_result: dict[str, Any],
        file_name: str = "audio_file",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._audit_result = audit_result
        self._file_name = file_name
        self._options = ReportOptions()
        self._generator: PDFReportGenerator | None = None
        self._worker: PDFGenerationWorker | None = None

        self._setup_ui()
        self._check_dependencies()
        self._update_preview()

    def _setup_ui(self) -> None:
        """Set up the UI."""
        self.setWindowTitle("Report Preview")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Options
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 10, 0)

        # Options group
        options_group = QGroupBox("Report Options")
        options_group_layout = QVBoxLayout(options_group)

        self._include_transcript = QCheckBox("Include full transcript")
        self._include_transcript.setChecked(True)
        self._include_transcript.stateChanged.connect(self._on_option_changed)
        options_group_layout.addWidget(self._include_transcript)

        self._include_chart = QCheckBox("Include score chart")
        self._include_chart.setChecked(True)
        self._include_chart.stateChanged.connect(self._on_option_changed)
        options_group_layout.addWidget(self._include_chart)

        self._include_scores = QCheckBox("Include detailed scores")
        self._include_scores.setChecked(True)
        self._include_scores.stateChanged.connect(self._on_option_changed)
        options_group_layout.addWidget(self._include_scores)

        options_layout.addWidget(options_group)

        # Dependencies status
        deps_group = QGroupBox("Dependencies")
        deps_layout = QVBoxLayout(deps_group)

        self._jinja_status = QLabel()
        deps_layout.addWidget(self._jinja_status)

        self._weasyprint_status = QLabel()
        deps_layout.addWidget(self._weasyprint_status)

        self._matplotlib_status = QLabel()
        deps_layout.addWidget(self._matplotlib_status)

        options_layout.addWidget(deps_group)

        # Summary
        summary_group = QGroupBox("Report Summary")
        summary_layout = QVBoxLayout(summary_group)

        self._score_label = QLabel()
        self._score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        summary_layout.addWidget(self._score_label)

        self._params_label = QLabel()
        summary_layout.addWidget(self._params_label)

        options_layout.addWidget(summary_group)

        options_layout.addStretch()

        splitter.addWidget(options_widget)

        # Right: Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(10, 0, 0, 0)

        preview_label = QLabel("HTML Preview:")
        preview_layout.addWidget(preview_label)

        self._preview_browser = QTextBrowser()
        self._preview_browser.setOpenExternalLinks(False)
        preview_layout.addWidget(self._preview_browser)

        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        preview_layout.addWidget(self._progress_bar)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: gray;")
        preview_layout.addWidget(self._status_label)

        splitter.addWidget(preview_widget)
        splitter.setSizes([250, 550])

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()

        self._refresh_btn = QPushButton("Refresh Preview")
        self._refresh_btn.clicked.connect(self._update_preview)
        button_layout.addWidget(self._refresh_btn)

        button_layout.addStretch()

        self._export_btn = QPushButton("Export PDF...")
        self._export_btn.clicked.connect(self._on_export)
        button_layout.addWidget(self._export_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _check_dependencies(self) -> None:
        """Check and display dependency status."""
        self._generator = PDFReportGenerator(self._options)
        deps = self._generator.check_dependencies()

        def status_text(available: bool, name: str) -> str:
            if available:
                return f"<span style='color: green;'>✓ {name} available</span>"
            else:
                return f"<span style='color: red;'>✗ {name} not installed</span>"

        self._jinja_status.setText(status_text(deps["jinja2"], "Jinja2"))
        self._weasyprint_status.setText(status_text(deps["weasyprint"], "WeasyPrint"))
        self._matplotlib_status.setText(status_text(deps["matplotlib"], "Matplotlib (charts)"))

        # Enable/disable export based on core dependencies
        can_export = deps["jinja2"] and deps["weasyprint"]
        self._export_btn.setEnabled(can_export)

        if not can_export:
            self._status_label.setText(
                "Install missing dependencies: pip install jinja2 weasyprint"
            )
            self._status_label.setStyleSheet("color: red;")

    def _update_options(self) -> None:
        """Update options from UI."""
        self._options.include_transcript = self._include_transcript.isChecked()
        self._options.include_chart = self._include_chart.isChecked()
        self._options.include_scores = self._include_scores.isChecked()

    @Slot()
    def _on_option_changed(self) -> None:
        """Handle option change."""
        self._update_options()
        self._update_preview()

    def _update_preview(self) -> None:
        """Update the HTML preview."""
        self._update_options()
        self._generator = PDFReportGenerator(self._options)

        # Update summary
        overall = self._audit_result.get("overall_score", 0)
        max_score = self._audit_result.get("max_score", 100)
        self._score_label.setText(f"Overall: {overall:.1f} / {max_score:.1f}")

        params = self._audit_result.get("parameter_scores", {})
        self._params_label.setText(f"Parameters: {len(params)}")

        # Generate preview
        if not self._generator.check_dependencies()["jinja2"]:
            self._preview_browser.setHtml(
                "<html><body><p style='color: red;'>"
                "Jinja2 is required for preview. Install with: pip install jinja2"
                "</p></body></html>"
            )
            return

        try:
            html = self._generator.generate_html(self._audit_result, self._file_name)
            self._preview_browser.setHtml(html)
            self._status_label.setText("Preview updated")
            self._status_label.setStyleSheet("color: green;")
        except Exception as e:
            self._preview_browser.setHtml(
                f"<html><body><p style='color: red;'>Error: {e}</p></body></html>"
            )
            self._status_label.setText(f"Preview error: {e}")
            self._status_label.setStyleSheet("color: red;")

    @Slot()
    def _on_export(self) -> None:
        """Export to PDF."""
        if not self._generator.can_generate():
            QMessageBox.warning(
                self,
                "Cannot Export",
                "PDF export requires Jinja2 and WeasyPrint.\n\n"
                "Install with: pip install jinja2 weasyprint",
            )
            return

        # Get output path
        default_name = f"{Path(self._file_name).stem}_report.pdf"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export PDF Report", str(Path.home() / default_name), "PDF Files (*.pdf)"
        )

        if not filepath:
            return

        # Start generation
        self._progress_bar.setVisible(True)
        self._progress_bar.setRange(0, 0)  # Indeterminate
        self._export_btn.setEnabled(False)
        self._status_label.setText("Generating PDF...")
        self._status_label.setStyleSheet("color: blue;")

        self._update_options()
        self._generator = PDFReportGenerator(self._options)

        self._worker = PDFGenerationWorker(
            self._generator,
            self._audit_result,
            filepath,
            self._file_name,
        )
        self._worker.progress.connect(self._on_generation_progress)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.start()

    @Slot(str)
    def _on_generation_progress(self, message: str) -> None:
        """Handle generation progress."""
        self._status_label.setText(message)

    @Slot(bool, str)
    def _on_generation_finished(self, success: bool, message: str) -> None:
        """Handle generation completion."""
        self._progress_bar.setVisible(False)
        self._export_btn.setEnabled(True)

        if success:
            self._status_label.setText(f"Exported to: {message}")
            self._status_label.setStyleSheet("color: green;")
            self.report_exported.emit(message)

            # Ask to open
            result = QMessageBox.question(
                self,
                "Export Complete",
                f"PDF exported successfully!\n\n{message}\n\nOpen the file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result == QMessageBox.StandardButton.Yes:
                import subprocess
                import sys

                if sys.platform == "darwin":
                    subprocess.run(["open", message])
                elif sys.platform == "win32":
                    subprocess.run(["start", "", message], shell=True)
                else:
                    subprocess.run(["xdg-open", message])
        else:
            self._status_label.setText(f"Export failed: {message}")
            self._status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Export Failed", f"Failed to generate PDF:\n\n{message}")
