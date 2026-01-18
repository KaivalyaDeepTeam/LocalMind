#!/usr/bin/env python3
"""
Generate PDF versions of technical guides from Markdown
Requires: pandoc or grip (markdown renderer)
"""

import subprocess
import sys
from pathlib import Path

# Guide configurations
GUIDES = [
    ("EN", "English", "Technical Guide"),
    ("ES", "Español", "Guía Técnica"),
    ("RU", "Русский", "Техническое руководство"),
    ("HI", "हिन्दी", "तकनीकी मार्गदर्शिका"),
    ("FR", "Français", "Guide Technique"),
    ("JA", "日本語", "テクニカルガイド"),
    ("AR", "العربية", "الدليل التقني"),
    ("ZH", "中文", "技术指南"),
]

def check_pandoc():
    """Check if pandoc is installed"""
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_pdf_pandoc(md_file, pdf_file, title):
    """Generate PDF using pandoc"""
    cmd = [
        "pandoc",
        str(md_file),
        "-o", str(pdf_file),
        "--pdf-engine=xelatex",  # Better Unicode support
        f"--metadata=title:{title}",
        "--metadata=author:LocalMind",
        "--toc",  # Table of contents
        "--toc-depth=2",
        "-V", "geometry:margin=1in",
        "-V", "fontsize=11pt",
        "-V", "documentclass=article",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr.decode()}")
        return False

def main():
    """Generate PDFs for all guides"""
    docs_dir = Path(__file__).parent.parent / "docs" / "user-guides"
    pdf_dir = docs_dir / "pdf"
    pdf_dir.mkdir(exist_ok=True)

    print("LocalMind PDF Generator")
    print("=" * 60)

    if not check_pandoc():
        print("\n❌ ERROR: pandoc is not installed")
        print("\nInstall pandoc:")
        print("  brew install pandoc")
        print("  brew install --cask mactex-no-gui  # For PDF support")
        print("\nOr download from: https://pandoc.org/installing.html")
        sys.exit(1)

    print(f"\n✓ pandoc found")
    print(f"✓ Input directory: {docs_dir}")
    print(f"✓ Output directory: {pdf_dir}\n")

    success_count = 0
    fail_count = 0

    for code, lang, title in GUIDES:
        md_file = docs_dir / f"TECHNICAL_GUIDE_{code}.md"
        pdf_file = pdf_dir / f"LocalMind_Technical_Guide_{code}.pdf"

        if not md_file.exists():
            print(f"⚠️  Skipping {code}: {md_file.name} not found")
            fail_count += 1
            continue

        print(f"📄 Generating {code} ({lang})...")

        if generate_pdf_pandoc(md_file, pdf_file, f"LocalMind {title}"):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"   ✓ Success: {pdf_file.name} ({size_mb:.2f} MB)")
            success_count += 1
        else:
            print(f"   ✗ Failed: {pdf_file.name}")
            fail_count += 1

    print(f"\n{'=' * 60}")
    print(f"PDF Generation Complete!")
    print(f"{'=' * 60}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📁 Location: {pdf_dir}")
    print(f"{'=' * 60}\n")

    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  PDF generation interrupted by user")
        sys.exit(0)
