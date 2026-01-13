"""
LocalMind PDF Report Generator

Generates professional PDF audit reports using WeasyPrint and Jinja2.
"""

import io
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

# Template rendering
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

# PDF generation
try:
    from weasyprint import HTML, CSS
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False

# Chart generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def get_templates_dir() -> Path:
    """Get the templates directory."""
    return Path(__file__).parent / "templates"


def get_score_class(percentage: float) -> str:
    """Get CSS class based on score percentage."""
    if percentage >= 80:
        return "score-excellent"
    elif percentage >= 60:
        return "score-good"
    elif percentage >= 40:
        return "score-average"
    else:
        return "score-poor"


def get_bar_class(percentage: float) -> str:
    """Get bar CSS class based on score percentage."""
    if percentage >= 80:
        return "bar-excellent"
    elif percentage >= 60:
        return "bar-good"
    elif percentage >= 40:
        return "bar-average"
    else:
        return "bar-poor"


@dataclass
class ReportOptions:
    """Options for PDF report generation."""
    include_transcript: bool = True
    include_chart: bool = True
    include_scores: bool = True
    company_name: Optional[str] = None
    logo_path: Optional[str] = None


class ScoreChartGenerator:
    """Generates score visualization charts."""

    @staticmethod
    def generate_radar_chart(
        parameters: List[Dict[str, Any]],
        width: int = 6,
        height: int = 6,
    ) -> Optional[str]:
        """Generate a radar chart of scores.

        Args:
            parameters: List of parameter dicts with name, score, max.
            width: Chart width in inches.
            height: Chart height in inches.

        Returns:
            Base64-encoded PNG image data URI, or None if matplotlib unavailable.
        """
        if not HAS_MATPLOTLIB or not parameters:
            return None

        # Prepare data
        labels = [p.get("display_name", p["name"])[:15] for p in parameters]
        scores = [p["score"] / p["max"] * 100 for p in parameters]

        # Number of variables
        num_vars = len(labels)
        if num_vars < 3:
            return None  # Radar chart needs at least 3 points

        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the loop
        scores += scores[:1]

        # Create figure
        fig, ax = plt.subplots(figsize=(width, height), subplot_kw=dict(polar=True))

        # Draw the chart
        ax.fill(angles, scores, color='#2196F3', alpha=0.25)
        ax.plot(angles, scores, color='#1976D2', linewidth=2)

        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=9)

        # Set y-axis
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], size=8, color='gray')

        # Style
        ax.spines['polar'].set_color('#ddd')
        ax.grid(color='#eee', linewidth=0.5)

        plt.tight_layout()

        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)

        # Convert to base64 data URI
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_data}"

    @staticmethod
    def generate_bar_chart(
        parameters: List[Dict[str, Any]],
        width: int = 8,
        height: int = 4,
    ) -> Optional[str]:
        """Generate a horizontal bar chart of scores.

        Args:
            parameters: List of parameter dicts with name, score, max.
            width: Chart width in inches.
            height: Chart height in inches.

        Returns:
            Base64-encoded PNG image data URI, or None if matplotlib unavailable.
        """
        if not HAS_MATPLOTLIB or not parameters:
            return None

        # Prepare data
        labels = [p.get("display_name", p["name"]) for p in parameters]
        percentages = [p["score"] / p["max"] * 100 for p in parameters]

        # Colors based on score
        colors = []
        for pct in percentages:
            if pct >= 80:
                colors.append('#4CAF50')
            elif pct >= 60:
                colors.append('#8BC34A')
            elif pct >= 40:
                colors.append('#FF9800')
            else:
                colors.append('#F44336')

        # Create figure
        fig, ax = plt.subplots(figsize=(width, height))

        # Create bars
        y_pos = np.arange(len(labels))
        bars = ax.barh(y_pos, percentages, color=colors, height=0.6)

        # Customize
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, size=10)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Score (%)', size=10)

        # Add value labels
        for bar, pct in zip(bars, percentages):
            ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                   f'{pct:.0f}%', va='center', size=9, color='#666')

        # Style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#ddd')
        ax.spines['left'].set_color('#ddd')
        ax.tick_params(colors='#666')

        # Add grid
        ax.xaxis.grid(True, color='#eee', linewidth=0.5)
        ax.set_axisbelow(True)

        plt.tight_layout()

        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close(fig)

        # Convert to base64 data URI
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_data}"


class PDFReportGenerator:
    """Generates PDF audit reports."""

    def __init__(self, options: Optional[ReportOptions] = None):
        """Initialize PDF generator.

        Args:
            options: Report generation options.
        """
        self._options = options or ReportOptions()
        self._templates_dir = get_templates_dir()
        self._chart_generator = ScoreChartGenerator()

        if HAS_JINJA2:
            self._env = Environment(
                loader=FileSystemLoader(str(self._templates_dir)),
                autoescape=select_autoescape(['html', 'xml']),
            )
        else:
            self._env = None

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available.

        Returns:
            Dict mapping dependency name to availability.
        """
        return {
            "jinja2": HAS_JINJA2,
            "weasyprint": HAS_WEASYPRINT,
            "matplotlib": HAS_MATPLOTLIB,
        }

    def can_generate(self) -> bool:
        """Check if PDF generation is possible."""
        return HAS_JINJA2 and HAS_WEASYPRINT

    def generate_html(
        self,
        audit_result: Dict[str, Any],
        file_name: str = "audio_file",
    ) -> str:
        """Generate HTML report from audit results.

        Args:
            audit_result: Audit result dictionary.
            file_name: Name of the audio file.

        Returns:
            Rendered HTML string.
        """
        if not HAS_JINJA2:
            raise ImportError("Jinja2 is required for report generation. Install with: pip install jinja2")

        # Prepare template data
        overall_score = audit_result.get("overall_score", 0)
        max_score = audit_result.get("max_score", 100)
        overall_pct = (overall_score / max_score * 100) if max_score > 0 else 0

        compliance_score = audit_result.get("compliance_score", 0)
        quality_score = audit_result.get("quality_score", 0)

        # Process parameters
        parameters = []
        param_scores = audit_result.get("parameter_scores", {})

        if isinstance(param_scores, dict):
            for name, data in param_scores.items():
                if isinstance(data, dict):
                    score = data.get("score", 0)
                    max_s = data.get("max", 10)
                    weight = data.get("weight", 1.0)
                else:
                    score = data
                    max_s = 10
                    weight = 1.0

                pct = (score / max_s * 100) if max_s > 0 else 0
                parameters.append({
                    "name": name.replace("_", " ").title(),
                    "score": f"{score:.1f}",
                    "max": f"{max_s:.0f}",
                    "weight": f"{weight:.1f}",
                    "percentage": pct,
                    "bar_class": get_bar_class(pct),
                })

        # Generate chart
        chart_image = None
        if self._options.include_chart and HAS_MATPLOTLIB and parameters:
            chart_params = [
                {
                    "name": p["name"],
                    "display_name": p["name"],
                    "score": float(p["score"]),
                    "max": float(p["max"]),
                }
                for p in parameters
            ]
            chart_image = self._chart_generator.generate_bar_chart(chart_params)

        # Process transcript
        transcript_lines = []
        if self._options.include_transcript:
            transcript = audit_result.get("transcript", "")
            if transcript:
                for line in transcript.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    speaker = "Unknown"
                    text = line

                    if line.startswith("[Agent]"):
                        speaker = "Agent"
                        text = line[7:].strip()
                    elif line.startswith("[Customer]"):
                        speaker = "Customer"
                        text = line[10:].strip()
                    elif "]" in line and line.startswith("["):
                        bracket_end = line.index("]")
                        speaker = line[1:bracket_end]
                        text = line[bracket_end + 1:].strip()

                    transcript_lines.append({
                        "speaker": speaker,
                        "text": text,
                    })

        # Get feedback
        feedback = audit_result.get("feedback", {})
        if isinstance(feedback, dict):
            summary = feedback.get("summary", audit_result.get("summary", ""))
            strengths = feedback.get("strengths", audit_result.get("strengths", []))
            improvements = feedback.get("improvements", audit_result.get("improvements", []))
        else:
            summary = str(feedback) if feedback else ""
            strengths = audit_result.get("strengths", [])
            improvements = audit_result.get("improvements", [])

        # Render template
        template = self._env.get_template("audit_report.html")
        html = template.render(
            file_name=file_name,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            overall_score=f"{overall_score:.1f}",
            max_score=f"{max_score:.1f}",
            overall_score_class=get_score_class(overall_pct),
            compliance_score=f"{compliance_score:.0f}",
            compliance_score_class=get_score_class(compliance_score),
            quality_score=f"{quality_score:.0f}",
            quality_score_class=get_score_class(quality_score),
            parameters=parameters,
            chart_image=chart_image,
            summary=summary,
            strengths=strengths,
            improvements=improvements,
            include_transcript=self._options.include_transcript,
            transcript_lines=transcript_lines,
        )

        return html

    def generate_pdf(
        self,
        audit_result: Dict[str, Any],
        output_path: str,
        file_name: str = "audio_file",
    ) -> None:
        """Generate PDF report and save to file.

        Args:
            audit_result: Audit result dictionary.
            output_path: Path to save the PDF.
            file_name: Name of the audio file.
        """
        if not self.can_generate():
            missing = []
            deps = self.check_dependencies()
            if not deps["jinja2"]:
                missing.append("jinja2")
            if not deps["weasyprint"]:
                missing.append("weasyprint")
            raise ImportError(
                f"Missing required dependencies: {', '.join(missing)}. "
                f"Install with: pip install {' '.join(missing)}"
            )

        # Generate HTML
        html_content = self.generate_html(audit_result, file_name)

        # Convert to PDF
        html = HTML(string=html_content, base_url=str(self._templates_dir))
        html.write_pdf(output_path)

    def generate_pdf_bytes(
        self,
        audit_result: Dict[str, Any],
        file_name: str = "audio_file",
    ) -> bytes:
        """Generate PDF report and return as bytes.

        Args:
            audit_result: Audit result dictionary.
            file_name: Name of the audio file.

        Returns:
            PDF file as bytes.
        """
        if not self.can_generate():
            raise ImportError("Missing required dependencies for PDF generation")

        html_content = self.generate_html(audit_result, file_name)
        html = HTML(string=html_content, base_url=str(self._templates_dir))
        return html.write_pdf()


def generate_report(
    audit_result: Dict[str, Any],
    output_path: str,
    file_name: str = "audio_file",
    include_transcript: bool = True,
    include_chart: bool = True,
) -> None:
    """Convenience function to generate a PDF report.

    Args:
        audit_result: Audit result dictionary.
        output_path: Path to save the PDF.
        file_name: Name of the audio file.
        include_transcript: Whether to include transcript.
        include_chart: Whether to include score chart.
    """
    options = ReportOptions(
        include_transcript=include_transcript,
        include_chart=include_chart,
    )
    generator = PDFReportGenerator(options)
    generator.generate_pdf(audit_result, output_path, file_name)
