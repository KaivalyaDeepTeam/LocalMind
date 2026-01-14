#!/usr/bin/env python3
"""
Icon Generator for LocalMind

Generates platform-specific icons from SVG source:
- macOS: icon.icns (16, 32, 64, 128, 256, 512, 1024px)
- Windows: icon.ico (16, 24, 32, 48, 64, 128, 256px)
- Linux: icon.png (512px)

Requirements:
    pip install cairosvg Pillow

Usage:
    python packaging/scripts/generate_icons.py
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List

# Check for required libraries
try:
    import cairosvg
    from PIL import Image
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


SCRIPT_DIR = Path(__file__).parent
PACKAGING_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PACKAGING_DIR.parent

SVG_SOURCE = PACKAGING_DIR / "icon.svg"

# Output paths
MACOS_ICON = PACKAGING_DIR / "macos" / "icon.icns"
WINDOWS_ICON = PACKAGING_DIR / "windows" / "icon.ico"
LINUX_ICON = PACKAGING_DIR / "linux" / "icon.png"

# Icon sizes for each platform
MACOS_SIZES = [16, 32, 64, 128, 256, 512, 1024]
WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]
LINUX_SIZE = 512


def svg_to_png(svg_path: Path, png_path: Path, size: int) -> bool:
    """Convert SVG to PNG at specified size."""
    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=size,
            output_height=size,
        )
        return True
    except Exception as e:
        print(f"  Error converting SVG to PNG: {e}")
        return False


def create_icns(png_files: List[Path], output_path: Path) -> bool:
    """Create macOS .icns file from PNG files."""
    # Create iconset directory
    iconset_dir = output_path.parent / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # macOS iconset naming convention
    size_names = {
        16: ["icon_16x16.png"],
        32: ["icon_16x16@2x.png", "icon_32x32.png"],
        64: ["icon_32x32@2x.png"],
        128: ["icon_128x128.png"],
        256: ["icon_128x128@2x.png", "icon_256x256.png"],
        512: ["icon_256x256@2x.png", "icon_512x512.png"],
        1024: ["icon_512x512@2x.png"],
    }

    # Copy PNGs to iconset with correct names
    for png_path in png_files:
        size = int(png_path.stem.split("_")[-1])
        if size in size_names:
            for name in size_names[size]:
                dest = iconset_dir / name
                import shutil
                shutil.copy(png_path, dest)

    # Use iconutil to create icns (macOS only)
    if sys.platform == "darwin":
        try:
            subprocess.run(
                ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)],
                check=True,
                capture_output=True,
            )
            # Clean up iconset
            import shutil
            shutil.rmtree(iconset_dir)
            return True
        except subprocess.CalledProcessError as e:
            print(f"  Error creating icns: {e}")
            return False
    else:
        print("  Note: .icns creation requires macOS. Keeping iconset directory.")
        return False


def create_ico(png_files: List[Path], output_path: Path) -> bool:
    """Create Windows .ico file from PNG files."""
    try:
        # Find the largest PNG
        largest_png = max(png_files, key=lambda p: int(p.stem.split("_")[-1]))
        img = Image.open(largest_png)

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Save with all required sizes - Pillow will resize internally
        img.save(
            str(output_path),
            format="ICO",
            sizes=[(s, s) for s in WINDOWS_SIZES],
        )
        return True
    except Exception as e:
        print(f"  Error creating ico: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 50)
    print("  LocalMind Icon Generator")
    print("=" * 50 + "\n")

    if not HAVE_DEPS:
        print("Missing dependencies. Install with:")
        print("  pip install cairosvg Pillow")
        sys.exit(1)

    if not SVG_SOURCE.exists():
        print(f"Error: SVG source not found: {SVG_SOURCE}")
        sys.exit(1)

    # Create output directories
    for path in [MACOS_ICON, WINDOWS_ICON, LINUX_ICON]:
        path.parent.mkdir(parents=True, exist_ok=True)

    # Temporary directory for intermediate PNGs
    temp_dir = PACKAGING_DIR / "temp_icons"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Generate macOS icons
        print("Generating macOS icons...")
        macos_pngs = []
        for size in MACOS_SIZES:
            png_path = temp_dir / f"icon_{size}.png"
            if svg_to_png(SVG_SOURCE, png_path, size):
                macos_pngs.append(png_path)
                print(f"  Created {size}x{size}")

        if macos_pngs:
            if create_icns(macos_pngs, MACOS_ICON):
                print(f"  -> {MACOS_ICON}")
            else:
                print("  -> icns creation skipped (not on macOS or failed)")

        # Generate Windows icons
        print("\nGenerating Windows icons...")
        windows_pngs = []
        for size in WINDOWS_SIZES:
            png_path = temp_dir / f"win_icon_{size}.png"
            if svg_to_png(SVG_SOURCE, png_path, size):
                windows_pngs.append(png_path)
                print(f"  Created {size}x{size}")

        if windows_pngs:
            if create_ico(windows_pngs, WINDOWS_ICON):
                print(f"  -> {WINDOWS_ICON}")

        # Generate Linux icon
        print("\nGenerating Linux icon...")
        if svg_to_png(SVG_SOURCE, LINUX_ICON, LINUX_SIZE):
            print(f"  -> {LINUX_ICON}")

        print("\n" + "=" * 50)
        print("  Icon generation complete!")
        print("=" * 50 + "\n")

    finally:
        # Clean up temp directory
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
