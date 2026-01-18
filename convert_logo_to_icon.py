#!/usr/bin/env python3
"""
Convert LocalMind website logo (SVG) to macOS app icon (.icns).
Uses the existing logo from website/assets/logo.svg
"""

from pathlib import Path
import sys
import subprocess
import shutil

def check_dependencies():
    """Check and install required dependencies."""
    try:
        import cairosvg
        return True
    except ImportError:
        print("[*] Installing cairosvg for SVG conversion...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
        import cairosvg
        return True

def convert_svg_to_png(svg_path, png_path, size):
    """Convert SVG to PNG at specified size."""
    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=size,
            output_height=size
        )
        return True
    except Exception as e:
        print(f"[!]  cairosvg failed: {e}")
        # Try rsvg-convert as fallback
        try:
            subprocess.run(
                ["rsvg-convert", "-w", str(size), "-h", str(size), str(svg_path), "-o", str(png_path)],
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[!]  rsvg-convert also not available")
            return False

def create_iconset(svg_path, base_output_dir):
    """Create macOS iconset from SVG."""
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    iconset_dir = Path("LocalMind.iconset")
    iconset_dir.mkdir(exist_ok=True)

    print(f"[*] Creating iconset with {len(sizes)} sizes...")
    for size, filename in sizes:
        output_path = iconset_dir / filename
        if convert_svg_to_png(svg_path, output_path, size):
            print(f"  [+] {filename} ({size}x{size})")
        else:
            print(f"  [-] Failed to create {filename}")
            return None

    return iconset_dir

def main():
    """Convert logo to icon."""
    print("[*] Converting LocalMind Logo to App Icon")
    print("=" * 50)
    print()

    # Check dependencies
    check_dependencies()

    # Paths
    svg_path = Path("website/assets/logo.svg")
    output_dir = Path("localmind/resources/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not svg_path.exists():
        print(f"[!] Logo not found: {svg_path}")
        return 1

    print(f"[*] Source: {svg_path}")
    print(f"[*] Output: {output_dir}/")
    print()

    # Create high-res PNG (1024x1024)
    print("[*] Creating high-resolution PNG (1024x1024)...")
    png_path = output_dir / "icon.png"
    if convert_svg_to_png(svg_path, png_path, 1024):
        print(f"[+] Created: {png_path}")
    else:
        print(f"[!] Failed to create PNG")
        return 1
    print()

    # Create iconset
    iconset_dir = create_iconset(svg_path, output_dir)
    if not iconset_dir:
        print("[!] Failed to create iconset")
        return 1

    print(f"[+] Iconset created: {iconset_dir}/")
    print()

    # Convert to .icns using iconutil (macOS only)
    print("[*] Converting to .icns format...")
    icns_path = output_dir / "icon.icns"

    try:
        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"[+] Created: {icns_path}")
        print()

        # Clean up iconset directory
        shutil.rmtree(iconset_dir)
        print("[*] Cleaned up temporary iconset")

    except FileNotFoundError:
        print("[!]  iconutil not found (not on macOS?)")
        print(f"   Iconset kept at: {iconset_dir}/")
        print(f"   Convert manually: iconutil -c icns {iconset_dir} -o {icns_path}")
    except subprocess.CalledProcessError as e:
        print(f"[!]  iconutil failed: {e.stderr}")
        print(f"   Iconset kept at: {iconset_dir}/")

    print()
    print("[+] Icon conversion complete!")
    print(f"[*] High-res PNG: {png_path}")
    if icns_path.exists():
        print(f"[*] macOS icon: {icns_path}")
        print(f"[*] Size: {icns_path.stat().st_size / 1024:.1f} KB")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
