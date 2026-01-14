#!/usr/bin/env python3
"""
LocalMind Build Script

Cross-platform build orchestrator for creating distributable packages.

Usage:
    python packaging/scripts/build.py [platform] [options]

Platforms:
    macos   - Build macOS .app and .dmg
    windows - Build Windows .exe and installer
    linux   - Build Linux AppImage and .deb
    all     - Build for current platform

Options:
    --clean     Clean build directories before building
    --no-dmg    Skip DMG creation (macOS only)
    --no-installer  Skip installer creation
    --version VERSION  Set version number
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# Project paths
SCRIPT_DIR = Path(__file__).parent
PACKAGING_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PACKAGING_DIR.parent

# Build directories
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

# App info
APP_NAME = "LocalMind"
DEFAULT_VERSION = "1.0.0"


def get_version() -> str:
    """Get version from package."""
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from localmind import __version__
        return __version__
    except ImportError:
        return DEFAULT_VERSION


def run_command(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and handle errors."""
    print(f"  Running: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, capture_output=False)
    if check and result.returncode != 0:
        print(f"  Command failed with code {result.returncode}")
        sys.exit(1)
    return result


def clean_build():
    """Clean build directories."""
    print("Cleaning build directories...")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_path}")


def check_dependencies():
    """Check if required build tools are installed."""
    print("Checking build dependencies...")

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"  PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("  PyInstaller not found. Installing...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])

    return True


def build_pyinstaller():
    """Build with PyInstaller."""
    print("Building with PyInstaller...")
    spec_file = PACKAGING_DIR / "localmind.spec"

    run_command([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file),
    ])

    print("  PyInstaller build complete")


def build_macos(create_dmg: bool = True, version: str = DEFAULT_VERSION):
    """Build macOS package."""
    print("\n=== Building macOS Package ===\n")

    # Build with PyInstaller
    build_pyinstaller()

    app_path = DIST_DIR / f"{APP_NAME}.app"
    if not app_path.exists():
        print(f"  Error: App bundle not found at {app_path}")
        sys.exit(1)

    print(f"  App bundle created: {app_path}")

    if create_dmg:
        print("\nCreating DMG...")
        dmg_path = DIST_DIR / f"{APP_NAME}-{version}-macOS.dmg"

        # Check for create-dmg
        if shutil.which("create-dmg"):
            run_command([
                "create-dmg",
                "--volname", APP_NAME,
                "--volicon", str(PACKAGING_DIR / "macos" / "icon.icns"),
                "--window-pos", "200", "120",
                "--window-size", "600", "400",
                "--icon-size", "100",
                "--icon", f"{APP_NAME}.app", "150", "190",
                "--hide-extension", f"{APP_NAME}.app",
                "--app-drop-link", "450", "190",
                "--no-internet-enable",
                str(dmg_path),
                str(app_path),
            ], check=False)
        else:
            # Fallback to hdiutil
            print("  create-dmg not found, using hdiutil...")
            temp_dmg = DIST_DIR / "temp.dmg"

            run_command([
                "hdiutil", "create",
                "-volname", APP_NAME,
                "-srcfolder", str(app_path),
                "-ov", "-format", "UDZO",
                str(dmg_path),
            ])

        if dmg_path.exists():
            print(f"  DMG created: {dmg_path}")
        else:
            print("  Warning: DMG creation failed")

    print("\nmacOS build complete!")


def build_windows(create_installer: bool = True, version: str = DEFAULT_VERSION):
    """Build Windows package."""
    print("\n=== Building Windows Package ===\n")

    # Build with PyInstaller
    build_pyinstaller()

    exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    if not exe_path.exists():
        print(f"  Error: Executable not found at {exe_path}")
        sys.exit(1)

    print(f"  Executable created: {exe_path}")

    if create_installer:
        print("\nCreating installer...")

        # Check for Inno Setup
        inno_path = None
        possible_paths = [
            Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        ]

        for p in possible_paths:
            if p.exists():
                inno_path = p
                break

        if inno_path:
            iss_file = PACKAGING_DIR / "windows" / "installer.iss"
            if iss_file.exists():
                run_command([str(inno_path), str(iss_file)])
                print("  Installer created")
            else:
                print(f"  Warning: Inno Setup script not found: {iss_file}")
        else:
            print("  Warning: Inno Setup not found, skipping installer creation")

    print("\nWindows build complete!")


def build_linux(create_deb: bool = True, create_appimage: bool = True, version: str = DEFAULT_VERSION):
    """Build Linux package."""
    print("\n=== Building Linux Package ===\n")

    # Build with PyInstaller
    build_pyinstaller()

    exe_path = DIST_DIR / APP_NAME / APP_NAME
    if not exe_path.exists():
        print(f"  Error: Executable not found at {exe_path}")
        sys.exit(1)

    print(f"  Executable created: {exe_path}")

    if create_deb:
        print("\nCreating .deb package...")

        # Create deb structure
        deb_root = BUILD_DIR / "deb"
        deb_root.mkdir(parents=True, exist_ok=True)

        # DEBIAN control directory
        debian_dir = deb_root / "DEBIAN"
        debian_dir.mkdir(exist_ok=True)

        # Control file
        control_content = f"""Package: localmind
Version: {version}
Section: audio
Priority: optional
Architecture: amd64
Depends: libgtk-3-0, libwebkit2gtk-4.0-37
Maintainer: Kaivalya Anand Pandey <kaivalyaanandpandey666@gmail.com>
Description: Free, open-source AI for audio transcription and quality auditing
 LocalMind is a desktop application for transcribing audio files and
 performing quality audits using AI. It works 100% offline after
 downloading the required models.
Homepage: https://github.com/KaivalyaDeepTeam/LocalMind
"""
        (debian_dir / "control").write_text(control_content)

        # Install directories
        opt_dir = deb_root / "opt" / "localmind"
        opt_dir.mkdir(parents=True, exist_ok=True)

        # Copy application
        shutil.copytree(DIST_DIR / APP_NAME, opt_dir, dirs_exist_ok=True)

        # Desktop entry
        apps_dir = deb_root / "usr" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)

        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=LocalMind
Comment=AI Audio Transcription and Quality Auditing
Exec=/opt/localmind/{APP_NAME}
Icon=/opt/localmind/icon.png
Terminal=false
Categories=Audio;AudioVideo;Utility;
MimeType=audio/mpeg;audio/x-wav;audio/ogg;audio/flac;
"""
        (apps_dir / "localmind.desktop").write_text(desktop_content)

        # Symlink in /usr/bin
        bin_dir = deb_root / "usr" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        # Build deb
        deb_file = DIST_DIR / f"localmind_{version}_amd64.deb"
        run_command(["dpkg-deb", "--build", str(deb_root), str(deb_file)], check=False)

        if deb_file.exists():
            print(f"  .deb package created: {deb_file}")
        else:
            print("  Warning: .deb creation failed")

    if create_appimage:
        print("\nCreating AppImage...")
        build_appimage(version)

    print("\nLinux build complete!")


def build_appimage(version: str = DEFAULT_VERSION):
    """Build AppImage using appimagetool or appimage-builder."""
    appimage_file = DIST_DIR / f"LocalMind-{version}-x86_64.AppImage"

    # Check for appimage-builder
    if shutil.which("appimage-builder"):
        print("  Using appimage-builder...")
        recipe_file = PACKAGING_DIR / "linux" / "AppImageBuilder.yml"

        if recipe_file.exists():
            env = os.environ.copy()
            env["VERSION"] = version
            subprocess.run(
                ["appimage-builder", "--recipe", str(recipe_file), "--skip-test"],
                cwd=PROJECT_ROOT,
                env=env,
            )
        else:
            print(f"  Warning: AppImageBuilder.yml not found at {recipe_file}")
            return

    # Fallback: Create AppImage manually using appimagetool
    elif shutil.which("appimagetool"):
        print("  Using appimagetool...")

        # Create AppDir structure
        appdir = BUILD_DIR / "AppDir"
        if appdir.exists():
            shutil.rmtree(appdir)
        appdir.mkdir(parents=True)

        # Create directory structure
        (appdir / "usr" / "bin").mkdir(parents=True)
        (appdir / "usr" / "share" / "applications").mkdir(parents=True)
        (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(parents=True)

        # Copy application files
        app_src = DIST_DIR / APP_NAME
        app_dst = appdir / "usr" / "bin"
        for item in app_src.iterdir():
            if item.is_file():
                shutil.copy2(item, app_dst)
            else:
                shutil.copytree(item, app_dst / item.name, dirs_exist_ok=True)

        # Create AppRun script
        apprun_content = f"""#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
exec "$APPDIR/usr/bin/{APP_NAME}" "$@"
"""
        apprun_file = appdir / "AppRun"
        apprun_file.write_text(apprun_content)
        apprun_file.chmod(0o755)

        # Copy desktop file
        desktop_src = PACKAGING_DIR / "linux" / "localmind.desktop"
        if desktop_src.exists():
            desktop_content = desktop_src.read_text()
            # Update Exec path for AppImage
            desktop_content = desktop_content.replace(
                "Exec=/opt/localmind/LocalMind",
                "Exec=localmind"
            )
            desktop_content = desktop_content.replace(
                "Icon=/opt/localmind/icon.png",
                "Icon=localmind"
            )
            (appdir / "localmind.desktop").write_text(desktop_content)
            (appdir / "usr" / "share" / "applications" / "localmind.desktop").write_text(desktop_content)

        # Copy icon (use placeholder if not exists)
        icon_src = PACKAGING_DIR / "linux" / "icon.png"
        if icon_src.exists():
            shutil.copy2(icon_src, appdir / "localmind.png")
            shutil.copy2(icon_src, appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "localmind.png")
        else:
            print("  Warning: icon.png not found, AppImage may not have an icon")

        # Build AppImage
        run_command([
            "appimagetool",
            "--no-appstream",
            str(appdir),
            str(appimage_file),
        ], check=False)
    else:
        print("  Warning: Neither appimage-builder nor appimagetool found")
        print("  Install with: pip install appimage-builder")
        print("  Or download appimagetool from https://github.com/AppImage/AppImageKit")
        return

    if appimage_file.exists():
        print(f"  AppImage created: {appimage_file}")
    else:
        print("  Warning: AppImage creation failed")


def main():
    parser = argparse.ArgumentParser(description="LocalMind Build Script")
    parser.add_argument(
        "platform",
        nargs="?",
        default="all",
        choices=["macos", "windows", "linux", "all"],
        help="Target platform (default: current platform)",
    )
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument("--no-dmg", action="store_true", help="Skip DMG creation")
    parser.add_argument("--no-installer", action="store_true", help="Skip installer creation")
    parser.add_argument("--no-appimage", action="store_true", help="Skip AppImage creation")
    parser.add_argument("--no-deb", action="store_true", help="Skip .deb creation")
    parser.add_argument(
        "--format",
        choices=["deb", "appimage", "all"],
        default="all",
        help="Linux package format (default: all)",
    )
    parser.add_argument("--version", default=None, help="Version number")

    args = parser.parse_args()

    version = args.version or get_version()
    print(f"\n{'='*50}")
    print(f"  LocalMind Build Script v{version}")
    print(f"{'='*50}\n")

    if args.clean:
        clean_build()

    check_dependencies()

    # Determine platform
    platform = args.platform
    if platform == "all":
        if sys.platform == "darwin":
            platform = "macos"
        elif sys.platform == "win32":
            platform = "windows"
        else:
            platform = "linux"

    # Build
    if platform == "macos":
        if sys.platform != "darwin":
            print("Error: macOS builds must be done on macOS")
            sys.exit(1)
        build_macos(create_dmg=not args.no_dmg, version=version)

    elif platform == "windows":
        if sys.platform != "win32":
            print("Error: Windows builds must be done on Windows")
            sys.exit(1)
        build_windows(create_installer=not args.no_installer, version=version)

    elif platform == "linux":
        if not sys.platform.startswith("linux"):
            print("Error: Linux builds must be done on Linux")
            sys.exit(1)

        # Determine which formats to build
        create_deb = args.format in ["deb", "all"] and not args.no_deb
        create_appimage = args.format in ["appimage", "all"] and not args.no_appimage

        build_linux(
            create_deb=create_deb,
            create_appimage=create_appimage,
            version=version,
        )

    print(f"\n{'='*50}")
    print(f"  Build Complete!")
    print(f"  Output: {DIST_DIR}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
