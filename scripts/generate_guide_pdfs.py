#!/usr/bin/env python3
"""
Generate PDF versions of technical guides from Markdown using ReportLab.
Supports multiple languages including non-Latin scripts.
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Guide configurations
GUIDES = [
    ("EN", "English", "Technical Guide"),
    ("ES", "Español", "Guía Técnica"),
    ("FR", "Français", "Guide Technique"),
    ("HI", "हिन्दी", "तकनीकी गाइड"),
    ("AR", "العربية", "الدليل التقني"),
    ("RU", "Русский", "Техническое руководство"),
    ("JA", "日本語", "テクニカルガイド"),
    ("ZH", "中文", "技术指南"),
]

# Colors
PRIMARY_COLOR = HexColor('#2563eb')
SECONDARY_COLOR = HexColor('#64748b')
HEADER_BG = HexColor('#f1f5f9')


def register_fonts():
    """Register fonts for Unicode support."""
    import platform

    # Try to find system fonts that support Unicode
    if platform.system() == 'Darwin':  # macOS
        font_paths = [
            # macOS system fonts with good Unicode coverage
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]

        for path in font_paths:
            if Path(path).exists():
                try:
                    pdfmetrics.registerFont(TTFont('Unicode', path))
                    return 'Unicode'
                except:
                    continue

    # Fallback to Helvetica (basic Latin only)
    return 'Helvetica'


def create_styles(font_name='Helvetica'):
    """Create paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    # Title style
    styles.add(ParagraphStyle(
        name='GuideTitle',
        fontName=font_name,
        fontSize=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=12,
        alignment=TA_CENTER,
    ))

    # Subtitle
    styles.add(ParagraphStyle(
        name='GuideSubtitle',
        fontName=font_name,
        fontSize=14,
        textColor=SECONDARY_COLOR,
        spaceAfter=24,
        alignment=TA_CENTER,
    ))

    # Section header (H1)
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName=font_name,
        fontSize=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=24,
        spaceAfter=12,
        borderPadding=8,
    ))

    # Subsection header (H2)
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        fontName=font_name,
        fontSize=14,
        textColor=HexColor('#1e40af'),
        spaceBefore=18,
        spaceAfter=8,
    ))

    # H3 header
    styles.add(ParagraphStyle(
        name='H3Header',
        fontName=font_name,
        fontSize=12,
        textColor=HexColor('#334155'),
        spaceBefore=12,
        spaceAfter=6,
    ))

    # Body text
    styles.add(ParagraphStyle(
        name='GuideBody',
        fontName=font_name,
        fontSize=10,
        textColor=HexColor('#334155'),
        spaceAfter=8,
        leading=14,
    ))

    # Code style
    styles.add(ParagraphStyle(
        name='GuideCode',
        fontName='Courier',
        fontSize=9,
        textColor=HexColor('#1e293b'),
        backColor=HexColor('#f8fafc'),
        spaceBefore=6,
        spaceAfter=6,
        leftIndent=12,
        borderPadding=8,
    ))

    # List item
    styles.add(ParagraphStyle(
        name='ListItem',
        fontName=font_name,
        fontSize=10,
        textColor=HexColor('#334155'),
        leftIndent=20,
        spaceAfter=4,
    ))

    return styles


def parse_markdown(md_content):
    """Parse markdown content into structured elements."""
    elements = []
    lines = md_content.split('\n')
    i = 0

    in_code_block = False
    code_content = []
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                elements.append(('code', '\n'.join(code_content)))
                code_content = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_content.append(line)
            i += 1
            continue

        # Tables
        if '|' in line and not line.strip().startswith('```'):
            # Check if it's a table separator line
            if re.match(r'^[\s|:-]+$', line):
                i += 1
                continue

            # Parse table row
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells:
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            elements.append(('table', table_rows))
            table_rows = []
            in_table = False

        # Headers
        if line.startswith('# '):
            elements.append(('h1', line[2:].strip()))
        elif line.startswith('## '):
            elements.append(('h2', line[3:].strip()))
        elif line.startswith('### '):
            elements.append(('h3', line[4:].strip()))
        # Horizontal rule
        elif line.strip() == '---':
            elements.append(('hr', None))
        # List items
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            elements.append(('list', line.strip()[2:]))
        elif re.match(r'^\d+\.\s', line.strip()):
            elements.append(('list', re.sub(r'^\d+\.\s', '', line.strip())))
        # Bold text paragraph
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            elements.append(('bold', line.strip()[2:-2]))
        # Regular paragraph
        elif line.strip():
            elements.append(('p', line.strip()))

        i += 1

    # Handle remaining table
    if in_table and table_rows:
        elements.append(('table', table_rows))

    return elements


def escape_xml(text):
    """Escape special XML characters."""
    if not text:
        return ''
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def format_text(text):
    """Format text with basic markdown styling."""
    text = escape_xml(text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9">\1</font>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'<u>\1</u>', text)
    return text


def build_pdf(md_content, output_path, title, styles):
    """Build PDF from markdown content."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    story = []
    elements = parse_markdown(md_content)

    for elem_type, content in elements:
        try:
            if elem_type == 'h1':
                # Check if it's the main title
                if content.startswith('LocalMind'):
                    story.append(Paragraph(format_text(content), styles['GuideTitle']))
                else:
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(format_text(content), styles['SectionHeader']))

            elif elem_type == 'h2':
                story.append(Paragraph(format_text(content), styles['SubsectionHeader']))

            elif elem_type == 'h3':
                story.append(Paragraph(format_text(content), styles['H3Header']))

            elif elem_type == 'p':
                story.append(Paragraph(format_text(content), styles['GuideBody']))

            elif elem_type == 'bold':
                story.append(Paragraph(f'<b>{escape_xml(content)}</b>', styles['GuideBody']))

            elif elem_type == 'list':
                story.append(Paragraph(f'• {format_text(content)}', styles['ListItem']))

            elif elem_type == 'code':
                # Format code block
                code_lines = content.split('\n')
                for line in code_lines:
                    if line.strip():
                        story.append(Paragraph(escape_xml(line), styles['GuideCode']))

            elif elem_type == 'table':
                if content and len(content) > 0:
                    # Create table
                    table_data = []
                    for row in content:
                        formatted_row = [Paragraph(format_text(cell), styles['GuideBody']) for cell in row]
                        table_data.append(formatted_row)

                    if table_data:
                        col_count = len(table_data[0])
                        col_width = (doc.width) / col_count

                        table = Table(table_data, colWidths=[col_width] * col_count)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
                            ('TEXTCOLOR', (0, 0), (-1, 0), PRIMARY_COLOR),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('TOPPADDING', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e2e8f0')),
                        ]))
                        story.append(Spacer(1, 6))
                        story.append(table)
                        story.append(Spacer(1, 6))

            elif elem_type == 'hr':
                story.append(Spacer(1, 12))

        except Exception as e:
            # Skip problematic elements
            print(f"    Warning: Skipped element due to: {e}")
            continue

    doc.build(story)


def main():
    """Generate PDFs for all guides."""
    print("LocalMind PDF Generator (ReportLab)")
    print("=" * 60)

    # Register fonts
    font_name = register_fonts()
    print(f"Using font: {font_name}")

    # Create styles
    styles = create_styles(font_name)

    docs_dir = Path(__file__).parent.parent / "docs" / "user-guides"
    pdf_dir = docs_dir / "pdf"
    pdf_dir.mkdir(exist_ok=True)

    print(f"Input directory: {docs_dir}")
    print(f"Output directory: {pdf_dir}\n")

    success_count = 0
    fail_count = 0

    for code, lang, title in GUIDES:
        md_file = docs_dir / f"TECHNICAL_GUIDE_{code}.md"
        pdf_file = pdf_dir / f"LocalMind_Technical_Guide_{code}.pdf"

        if not md_file.exists():
            print(f"Skipping {code}: {md_file.name} not found")
            fail_count += 1
            continue

        print(f"Generating {code} ({lang})...")

        try:
            md_content = md_file.read_text(encoding='utf-8')
            build_pdf(md_content, pdf_file, f"LocalMind {title}", styles)

            size_kb = pdf_file.stat().st_size / 1024
            print(f"   Success: {pdf_file.name} ({size_kb:.1f} KB)")
            success_count += 1
        except Exception as e:
            print(f"   Failed: {e}")
            fail_count += 1

    print(f"\n{'=' * 60}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Location: {pdf_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
