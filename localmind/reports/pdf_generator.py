"""
LocalMind PDF Report Generator

Generates professional PDF audit reports using ReportLab (pure Python).
Features: Score gauges, bar charts, detailed tables, and clean layout.
"""

import io
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
import math

# ReportLab imports
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable, KeepTogether, ListFlowable, ListItem
    )
    from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge, Line
    from reportlab.graphics.charts.barcharts import HorizontalBarChart
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics import renderPDF
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    colors = None


# Color palette - Modern, professional colors
COLORS = {}
if HAS_REPORTLAB:
    COLORS = {
        # Brand colors
        'primary': colors.HexColor('#4F46E5'),       # Indigo
        'primary_light': colors.HexColor('#818CF8'), # Light indigo
        'primary_dark': colors.HexColor('#3730A3'),  # Dark indigo

        # Score colors
        'excellent': colors.HexColor('#10B981'),     # Emerald green
        'good': colors.HexColor('#22C55E'),          # Green
        'average': colors.HexColor('#F59E0B'),       # Amber
        'below_avg': colors.HexColor('#F97316'),     # Orange
        'poor': colors.HexColor('#EF4444'),          # Red

        # Neutral colors
        'text_dark': colors.HexColor('#111827'),     # Gray 900
        'text': colors.HexColor('#374151'),          # Gray 700
        'text_light': colors.HexColor('#6B7280'),    # Gray 500
        'text_muted': colors.HexColor('#9CA3AF'),    # Gray 400
        'border': colors.HexColor('#E5E7EB'),        # Gray 200
        'background': colors.HexColor('#F9FAFB'),    # Gray 50
        'background_alt': colors.HexColor('#F3F4F6'), # Gray 100
        'white': colors.white,
    }


def get_score_color(percentage: float) -> 'colors.Color':
    """Get color based on score percentage."""
    if not HAS_REPORTLAB:
        return None
    if percentage >= 85:
        return COLORS['excellent']
    elif percentage >= 70:
        return COLORS['good']
    elif percentage >= 55:
        return COLORS['average']
    elif percentage >= 40:
        return COLORS['below_avg']
    else:
        return COLORS['poor']


def get_rating_text(percentage: float) -> str:
    """Get rating text based on percentage."""
    if percentage >= 85:
        return "Excellent"
    elif percentage >= 70:
        return "Good"
    elif percentage >= 55:
        return "Average"
    elif percentage >= 40:
        return "Below Average"
    else:
        return "Needs Improvement"


@dataclass
class ReportOptions:
    """Options for PDF report generation."""
    include_transcript: bool = True
    include_chart: bool = True
    include_details: bool = True
    company_name: Optional[str] = None
    logo_path: Optional[str] = None
    page_size: str = "letter"  # "letter" or "a4"


class ScoreChartGenerator:
    """Generates score visualization charts using ReportLab."""

    @staticmethod
    def create_score_gauge(
        score: float,
        max_score: float = 100,
        size: float = 120
    ) -> Drawing:
        """Create a circular score gauge."""
        if not HAS_REPORTLAB:
            return None

        percentage = (score / max_score * 100) if max_score > 0 else 0
        color = get_score_color(percentage)

        drawing = Drawing(size, size + 20)
        center_x = size / 2
        center_y = size / 2 + 10
        radius = size / 2 - 10

        # Background circle (gray track)
        drawing.add(Wedge(
            center_x, center_y, radius,
            0, 360,
            fillColor=COLORS['background_alt'],
            strokeColor=None,
            strokeWidth=0
        ))

        # Score arc (colored portion)
        if percentage > 0:
            # Convert percentage to angle (starting from top, going clockwise)
            angle = percentage * 3.6  # 360 degrees = 100%
            start_angle = 90  # Start from top
            end_angle = 90 - angle

            drawing.add(Wedge(
                center_x, center_y, radius,
                end_angle, start_angle,
                fillColor=color,
                strokeColor=None,
                strokeWidth=0
            ))

        # Inner white circle to create donut effect
        inner_radius = radius * 0.65
        drawing.add(Circle(
            center_x, center_y, inner_radius,
            fillColor=COLORS['white'],
            strokeColor=None
        ))

        # Score text in center
        drawing.add(String(
            center_x, center_y + 5,
            f"{percentage:.0f}%",
            fontName='Helvetica-Bold',
            fontSize=24,
            fillColor=color,
            textAnchor='middle'
        ))

        # "Score" label below
        drawing.add(String(
            center_x, center_y - 15,
            "Overall",
            fontName='Helvetica',
            fontSize=10,
            fillColor=COLORS['text_light'],
            textAnchor='middle'
        ))

        return drawing

    @staticmethod
    def create_horizontal_bar_chart(
        parameters: List[Dict[str, Any]],
        width: float = 480,
        bar_height: float = 22
    ) -> Drawing:
        """Create a horizontal bar chart with score labels."""
        if not HAS_REPORTLAB or not parameters:
            return None

        num_params = len(parameters)
        chart_height = num_params * (bar_height + 12) + 40

        drawing = Drawing(width, chart_height)

        # Chart dimensions
        label_width = 150
        bar_width = width - label_width - 60
        start_x = label_width + 10
        start_y = chart_height - 30

        for i, param in enumerate(parameters):
            name = param.get("parameter", param.get("name", f"Parameter {i+1}"))
            # Truncate long names
            if len(name) > 25:
                name = name[:22] + "..."

            score = param.get("score", 0)
            max_score = param.get("max_score", param.get("max", 10))
            percentage = (score / max_score * 100) if max_score > 0 else 0
            color = get_score_color(percentage)

            y_pos = start_y - (i * (bar_height + 12))

            # Parameter label (left aligned)
            drawing.add(String(
                5, y_pos + bar_height/2 - 4,
                name,
                fontName='Helvetica',
                fontSize=10,
                fillColor=COLORS['text'],
                textAnchor='start'
            ))

            # Background bar (gray track)
            drawing.add(Rect(
                start_x, y_pos,
                bar_width, bar_height,
                fillColor=COLORS['background_alt'],
                strokeColor=None,
                rx=4, ry=4
            ))

            # Score bar (colored portion)
            score_width = (percentage / 100) * bar_width
            if score_width > 0:
                drawing.add(Rect(
                    start_x, y_pos,
                    max(score_width, 8), bar_height,  # Minimum width for visibility
                    fillColor=color,
                    strokeColor=None,
                    rx=4, ry=4
                ))

            # Score label (right of bar)
            drawing.add(String(
                start_x + bar_width + 8, y_pos + bar_height/2 - 4,
                f"{score:.1f}/{max_score:.0f}",
                fontName='Helvetica-Bold',
                fontSize=9,
                fillColor=COLORS['text'],
                textAnchor='start'
            ))

        return drawing

    @staticmethod
    def create_mini_bar(
        percentage: float,
        width: float = 60,
        height: float = 8
    ) -> Drawing:
        """Create a mini progress bar for table cells."""
        if not HAS_REPORTLAB:
            return None

        drawing = Drawing(width, height)
        color = get_score_color(percentage)

        # Background
        drawing.add(Rect(0, 0, width, height,
                        fillColor=COLORS['background_alt'],
                        strokeColor=None, rx=2, ry=2))

        # Fill
        fill_width = (percentage / 100) * width
        if fill_width > 0:
            drawing.add(Rect(0, 0, max(fill_width, 4), height,
                            fillColor=color,
                            strokeColor=None, rx=2, ry=2))

        return drawing


class PDFReportGenerator:
    """Generates professional PDF audit reports."""

    def __init__(self, options: Optional[ReportOptions] = None):
        """Initialize PDF generator."""
        self._options = options or ReportOptions()
        self._styles = self._create_styles() if HAS_REPORTLAB else {}

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles."""
        if not HAS_REPORTLAB:
            return {}

        styles = getSampleStyleSheet()

        return {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=COLORS['primary'],
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
            ),
            'Subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=COLORS['text_light'],
                spaceAfter=20,
                alignment=TA_CENTER,
            ),
            'SectionHeading': ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=COLORS['primary_dark'],
                spaceBefore=25,
                spaceAfter=12,
                fontName='Helvetica-Bold',
                borderPadding=(0, 0, 5, 0),
                borderWidth=0,
                borderColor=COLORS['primary'],
            ),
            'SubHeading': ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=COLORS['text_dark'],
                spaceBefore=15,
                spaceAfter=8,
                fontName='Helvetica-Bold',
            ),
            'Body': ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=10,
                textColor=COLORS['text'],
                spaceAfter=8,
                leading=14,
                alignment=TA_JUSTIFY,
            ),
            'BodyCentered': ParagraphStyle(
                'BodyCentered',
                parent=styles['Normal'],
                fontSize=10,
                textColor=COLORS['text'],
                spaceAfter=8,
                alignment=TA_CENTER,
            ),
            'Strength': ParagraphStyle(
                'Strength',
                parent=styles['Normal'],
                fontSize=10,
                textColor=COLORS['excellent'],
                leftIndent=15,
                spaceAfter=6,
                leading=14,
            ),
            'Improvement': ParagraphStyle(
                'Improvement',
                parent=styles['Normal'],
                fontSize=10,
                textColor=COLORS['below_avg'],
                leftIndent=15,
                spaceAfter=6,
                leading=14,
            ),
            'Transcript': ParagraphStyle(
                'Transcript',
                parent=styles['Normal'],
                fontSize=9,
                textColor=COLORS['text'],
                spaceAfter=6,
                leading=13,
                leftIndent=10,
            ),
            'TranscriptSpeaker': ParagraphStyle(
                'TranscriptSpeaker',
                parent=styles['Normal'],
                fontSize=9,
                textColor=COLORS['primary'],
                fontName='Helvetica-Bold',
                spaceAfter=2,
            ),
            'Footer': ParagraphStyle(
                'Footer',
                fontSize=8,
                textColor=COLORS['text_muted'],
                alignment=TA_CENTER,
            ),
        }

    def can_generate(self) -> bool:
        """Check if PDF generation is possible."""
        return HAS_REPORTLAB

    def _build_header(self, file_name: str) -> List:
        """Build report header with title and metadata."""
        elements = []

        # Main title
        elements.append(Paragraph(
            "Audio Quality Audit Report",
            self._styles['Title']
        ))

        # Subtitle with file and date
        date_str = datetime.now().strftime("%B %d, %Y at %H:%M")
        elements.append(Paragraph(
            f"<b>File:</b> {file_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Generated:</b> {date_str}",
            self._styles['Subtitle']
        ))

        # Divider line
        elements.append(HRFlowable(
            width="100%", thickness=2,
            color=COLORS['primary'], spaceAfter=20
        ))

        return elements

    def _build_score_overview(self, audit_result: Dict[str, Any]) -> List:
        """Build score overview section with gauge and summary."""
        elements = []

        # Get score data
        score_summary = audit_result.get("score_summary", {})
        total_score = score_summary.get("total_score", 0)
        max_score = score_summary.get("max_possible_score", 100)
        percentage = score_summary.get("percentage", 0)

        if max_score == 0 and total_score == 0:
            # Try alternative keys
            total_score = audit_result.get("overall_score", 0)
            max_score = audit_result.get("max_score", 100)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0

        rating = get_rating_text(percentage)
        rating_color = get_score_color(percentage)

        # Create gauge
        gauge = ScoreChartGenerator.create_score_gauge(percentage, 100, 130)

        # Build overview table with gauge on left, summary on right
        summary_data = [
            ["Total Score:", f"{total_score:.1f} / {max_score:.0f}"],
            ["Percentage:", f"{percentage:.1f}%"],
            ["Rating:", rating],
        ]

        summary_table = Table(summary_data, colWidths=[100, 120])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), COLORS['text_light']),
            ('TEXTCOLOR', (1, 0), (1, 1), COLORS['text_dark']),
            ('TEXTCOLOR', (1, 2), (1, 2), rating_color),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 2), (1, 2), 13),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        # Main overview table
        overview_data = [[gauge, summary_table]]
        overview_table = Table(overview_data, colWidths=[150, 300])
        overview_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (1, 0), (1, 0), 30),
        ]))

        # Wrap in a styled container
        container_data = [[overview_table]]
        container = Table(container_data, colWidths=[480])
        container.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['background']),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))

        elements.append(container)
        elements.append(Spacer(1, 20))

        return elements

    def _build_score_chart(self, audit_result: Dict[str, Any]) -> List:
        """Build the score breakdown bar chart."""
        elements = []

        if not self._options.include_chart:
            return elements

        scoring_details = audit_result.get("scoring_details", [])
        if not scoring_details:
            return elements

        elements.append(Paragraph("Score Breakdown", self._styles['SectionHeading']))

        # Create bar chart
        chart = ScoreChartGenerator.create_horizontal_bar_chart(scoring_details, width=490)
        if chart:
            elements.append(chart)

        elements.append(Spacer(1, 15))

        return elements

    def _build_detailed_scores_table(self, audit_result: Dict[str, Any]) -> List:
        """Build detailed scores table."""
        elements = []

        if not self._options.include_details:
            return elements

        scoring_details = audit_result.get("scoring_details", [])
        if not scoring_details:
            return elements

        elements.append(Paragraph("Detailed Scores", self._styles['SectionHeading']))

        # Table header
        table_data = [['Parameter', 'Score', 'Max', 'Percentage', 'Rating']]

        for param in scoring_details:
            name = param.get("parameter", param.get("name", "Unknown"))
            score = param.get("score", 0)
            max_score = param.get("max_score", param.get("max", 10))
            percentage = param.get("percentage", (score / max_score * 100) if max_score > 0 else 0)
            rating = param.get("rating", get_rating_text(percentage))

            # Truncate long names
            if len(name) > 30:
                name = name[:27] + "..."

            table_data.append([
                name,
                f"{score:.1f}",
                f"{max_score:.0f}",
                f"{percentage:.0f}%",
                rating
            ])

        # Create table
        col_widths = [180, 60, 50, 80, 100]
        table = Table(table_data, colWidths=col_widths)

        # Style the table
        style_commands = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['white'], COLORS['background']]),

            # Borders
            ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['primary']),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, COLORS['border']),

            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]

        # Color-code the rating column
        for i, param in enumerate(scoring_details, start=1):
            percentage = param.get("percentage", 0)
            if percentage == 0:
                score = param.get("score", 0)
                max_score = param.get("max_score", 10)
                percentage = (score / max_score * 100) if max_score > 0 else 0
            rating_color = get_score_color(percentage)
            style_commands.append(('TEXTCOLOR', (4, i), (4, i), rating_color))
            style_commands.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))

        table.setStyle(TableStyle(style_commands))
        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_ai_feedback(self, audit_result: Dict[str, Any]) -> List:
        """Build AI feedback section with strengths and improvements."""
        elements = []

        ai_feedback = audit_result.get("ai_feedback", {})
        if not ai_feedback:
            return elements

        elements.append(Paragraph("AI Analysis & Feedback", self._styles['SectionHeading']))

        # Summary
        summary = ai_feedback.get("summary", "")
        if summary:
            # Create summary box
            summary_data = [[Paragraph(f"<b>Summary:</b> {summary}", self._styles['Body'])]]
            summary_table = Table(summary_data, colWidths=[470])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['background']),
                ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 15))

        # Two-column layout for strengths and improvements
        strengths = ai_feedback.get("strengths", [])
        improvements = ai_feedback.get("improvements", [])

        if strengths or improvements:
            # Strengths column
            strengths_content = []
            if strengths:
                strengths_content.append(Paragraph(
                    "<font color='#10B981'><b>Strengths</b></font>",
                    self._styles['SubHeading']
                ))
                for s in strengths[:5]:  # Limit to 5 items
                    strengths_content.append(Paragraph(
                        f"<font color='#10B981'>&#10003;</font> {s}",
                        self._styles['Strength']
                    ))

            # Improvements column
            improvements_content = []
            if improvements:
                improvements_content.append(Paragraph(
                    "<font color='#F97316'><b>Areas for Improvement</b></font>",
                    self._styles['SubHeading']
                ))
                for imp in improvements[:5]:  # Limit to 5 items
                    improvements_content.append(Paragraph(
                        f"<font color='#F97316'>&#10148;</font> {imp}",
                        self._styles['Improvement']
                    ))

            # Create two-column table
            if strengths_content and improvements_content:
                col_data = [[strengths_content, improvements_content]]
                col_table = Table(col_data, colWidths=[235, 235])
                col_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ]))
                elements.append(col_table)
            elif strengths_content:
                for item in strengths_content:
                    elements.append(item)
            elif improvements_content:
                for item in improvements_content:
                    elements.append(item)

        elements.append(Spacer(1, 15))

        return elements

    def _build_transcript(self, audit_result: Dict[str, Any]) -> List:
        """Build transcript section."""
        elements = []

        if not self._options.include_transcript:
            return elements

        transcript = audit_result.get("transcript", "")
        if not transcript:
            return elements

        elements.append(PageBreak())
        elements.append(Paragraph("Full Transcript", self._styles['SectionHeading']))

        # Parse transcript into speaker turns
        lines = transcript.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to extract speaker
            speaker = None
            text = line

            # Check for common speaker patterns
            if ':' in line:
                parts = line.split(':', 1)
                potential_speaker = parts[0].strip()
                # Check if it looks like a speaker label
                if len(potential_speaker) < 30 and not potential_speaker[0].isdigit():
                    speaker = potential_speaker
                    text = parts[1].strip()

            if speaker:
                elements.append(Paragraph(
                    f"<b>{speaker}:</b> {text}",
                    self._styles['Transcript']
                ))
            else:
                elements.append(Paragraph(text, self._styles['Transcript']))

        return elements

    def _build_footer(self) -> List:
        """Build report footer."""
        elements = []

        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(
            width="100%", thickness=1,
            color=COLORS['border'], spaceBefore=10
        ))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "Generated by <b>LocalMind</b> - Free, Private, Open Source AI Audio Analysis<br/>"
            "<font color='#4F46E5'>https://localmind.ai</font>",
            self._styles['Footer']
        ))

        return elements

    def generate_pdf(
        self,
        audit_result: Dict[str, Any],
        output_path: str,
        file_name: str = "audio_file",
    ) -> None:
        """Generate PDF report and save to file."""
        if not self.can_generate():
            raise ImportError(
                "ReportLab is required for PDF generation. "
                "Install with: pip install reportlab"
            )

        # Select page size
        page_size = A4 if self._options.page_size == "a4" else letter

        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            rightMargin=55,
            leftMargin=55,
            topMargin=50,
            bottomMargin=50,
        )

        # Build content
        elements = []
        elements.extend(self._build_header(file_name))
        elements.extend(self._build_score_overview(audit_result))
        elements.extend(self._build_score_chart(audit_result))
        elements.extend(self._build_detailed_scores_table(audit_result))
        elements.extend(self._build_ai_feedback(audit_result))
        elements.extend(self._build_transcript(audit_result))
        elements.extend(self._build_footer())

        # Build PDF
        doc.build(elements)

    def generate_pdf_bytes(
        self,
        audit_result: Dict[str, Any],
        file_name: str = "audio_file",
    ) -> bytes:
        """Generate PDF report and return as bytes."""
        if not self.can_generate():
            raise ImportError("ReportLab is required for PDF generation")

        buffer = io.BytesIO()
        page_size = A4 if self._options.page_size == "a4" else letter

        doc = SimpleDocTemplate(
            buffer,
            pagesize=page_size,
            rightMargin=55,
            leftMargin=55,
            topMargin=50,
            bottomMargin=50,
        )

        elements = []
        elements.extend(self._build_header(file_name))
        elements.extend(self._build_score_overview(audit_result))
        elements.extend(self._build_score_chart(audit_result))
        elements.extend(self._build_detailed_scores_table(audit_result))
        elements.extend(self._build_ai_feedback(audit_result))
        elements.extend(self._build_transcript(audit_result))
        elements.extend(self._build_footer())

        doc.build(elements)

        return buffer.getvalue()
