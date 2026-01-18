#!/usr/bin/env python3
"""
Automated Screenshot Tool for LocalMind User Guide
Takes screenshots of the app in all supported languages
"""
import sys
import time
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def take_screenshot(filename, description):
    """Take a screenshot using macOS screencapture"""
    output_dir = Path(__file__).parent.parent / "docs" / "user-guides" / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    print(f"\n{'='*60}")
    print(f"📸 Taking screenshot: {filename}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    print("\nCLICK ON THE LOCALMIND WINDOW NOW!")
    print("Screenshot will be taken in 3 seconds...")

    time.sleep(3)

    # Use screencapture with window selection
    try:
        subprocess.run([
            "screencapture",
            "-w",  # Window mode - click to select window
            "-o",  # Don't capture window shadow
            str(output_path)
        ], check=True)

        print(f"✅ Screenshot saved: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to take screenshot: {e}")
        return False


def main():
    """Main screenshot capture workflow"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     LocalMind Screenshot Tool for User Guide                 ║
║     Press Ctrl+C at any time to stop                         ║
╚══════════════════════════════════════════════════════════════╝

INSTRUCTIONS:
1. Keep LocalMind window visible on screen
2. When prompted, click on the LocalMind window
3. Screenshot will be taken after 3 seconds
4. Repeat for each screenshot

IMPORTANT: Have a test audio file ready for processing screenshots!

Press ENTER to start...
""")

    input()

    # Define all screenshots to take
    screenshots = [
        # English screenshots
        ("01-main-window-en.png", "Main window - English UI, no file loaded"),
        ("02-file-loaded-en.png", "Audio file loaded, ready to process - English UI"),
        ("03-model-selection-en.png", "Model selection dropdown open - English UI"),
        ("04-language-selector-en.png", "Language selector dropdown open - English UI"),
        ("05-processing-en.png", "Processing in progress with progress bar - English UI"),
        ("06-transcription-results-en.png", "Transcription results with speaker labels - English UI"),
        ("07-quality-scores-en.png", "Quality scoring results and feedback - English UI"),
        ("08-export-menu-en.png", "Export options menu - English UI"),
        ("09-settings-en.png", "Settings/Preferences window - English UI"),
        ("10-scoring-parameters-en.png", "Scoring parameters customization - English UI"),

        # Now repeat for other languages
        ("11-main-window-es.png", "Main window - Spanish UI"),
        ("12-main-window-ja.png", "Main window - Japanese UI"),
        ("13-main-window-ar.png", "Main window - Arabic UI (RTL layout)"),
        ("14-main-window-hi.png", "Main window - Hindi UI"),
        ("15-main-window-ru.png", "Main window - Russian UI"),
        ("16-main-window-fr.png", "Main window - French UI"),
        ("17-main-window-zh.png", "Main window - Chinese UI"),

        # Key features in different languages
        ("18-transcription-es.png", "Transcription results - Spanish UI"),
        ("19-transcription-hi.png", "Transcription results - Hindi UI"),
        ("20-quality-scores-ru.png", "Quality scores - Russian UI"),
    ]

    print(f"\nTotal screenshots to take: {len(screenshots)}")
    print("\nStarting screenshot capture...\n")

    successful = 0
    failed = 0

    for i, (filename, description) in enumerate(screenshots, 1):
        print(f"\n[{i}/{len(screenshots)}]")

        if take_screenshot(filename, description):
            successful += 1
        else:
            failed += 1

        if i < len(screenshots):
            print("\nReady for next screenshot...")
            time.sleep(2)

    # Summary
    print(f"\n{'='*60}")
    print(f"Screenshot Capture Complete!")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Location: docs/user-guides/screenshots/")
    print(f"{'='*60}\n")

    # List all captured screenshots
    output_dir = Path(__file__).parent.parent / "docs" / "user-guides" / "screenshots"
    screenshots_taken = list(output_dir.glob("*.png"))

    if screenshots_taken:
        print("\n📸 Screenshots captured:")
        for screenshot in sorted(screenshots_taken):
            size_mb = screenshot.stat().st_size / (1024 * 1024)
            print(f"  - {screenshot.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Screenshot capture interrupted by user")
        sys.exit(0)
