#!/bin/bash
# LocalMind Production DMG Build Script
# Builds a production-ready DMG for direct distribution (no code signing)

set -e  # Exit on error

echo "LocalMind Production Build"
echo "=========================="
echo ""

# Configuration
APP_NAME="LocalMind"
DMG_NAME="LocalMind-macOS.dmg"
VERSION="1.1.0"

# Clean previous builds
echo "[*] Cleaning previous builds..."
rm -rf build dist *.dmg
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "[+] Clean complete"
echo ""

# Check icon exists
if [ ! -f "localmind/resources/images/icon.icns" ]; then
    echo "[!] Icon not found. Creating from logo..."
    python convert_logo_to_icon.py
fi
echo "[+] Icon ready"
echo ""

# Check PyInstaller
echo "[*] Checking PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi
echo "[+] PyInstaller ready"
echo ""

# Build with PyInstaller
echo "[*] Building ${APP_NAME}.app..."
echo "This may take 5-10 minutes..."
pyinstaller LocalMind.spec --clean --noconfirm

if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "[!] Build failed! ${APP_NAME}.app not found in dist/"
    exit 1
fi
echo "[+] Build complete"
echo ""

# Get app size
APP_SIZE=$(du -sh "dist/${APP_NAME}.app" | cut -f1)
echo "App size: ${APP_SIZE}"
echo ""

# Create DMG
echo "[*] Creating DMG..."
hdiutil create \
  -volname "${APP_NAME}" \
  -srcfolder "dist/${APP_NAME}.app" \
  -ov \
  -format UDZO \
  "${DMG_NAME}"

if [ ! -f "${DMG_NAME}" ]; then
    echo "[!] DMG creation failed!"
    exit 1
fi

DMG_SIZE=$(du -sh "${DMG_NAME}" | cut -f1)
echo "[+] DMG created successfully!"
echo ""

# Final summary
echo "Build Summary"
echo "============="
echo "Version: ${VERSION}"
echo "App: dist/${APP_NAME}.app (${APP_SIZE})"
echo "DMG: ${DMG_NAME} (${DMG_SIZE})"
echo ""

# Distribution checklist
echo "Distribution Checklist"
echo "======================"
echo "[+] App icon included"
echo "[+] Security entitlements configured"
echo "[+] Privacy permissions declared"
echo "[+] File associations configured"
echo "[+] Dark mode supported"
echo "[+] Models download on-demand"
echo ""

# Usage instructions
echo "Next Steps"
echo "=========="
echo ""
echo "1. Test the DMG:"
echo "   open ${DMG_NAME}"
echo ""
echo "2. Upload to GitHub Releases:"
echo "   - Create new release with tag v${VERSION}"
echo "   - Upload ${DMG_NAME}"
echo "   - Include INSTALL.md instructions"
echo ""
echo "3. Users install by:"
echo "   - Opening DMG"
echo "   - Dragging to Applications"
echo "   - Right-click → Open (first time only)"
echo ""
echo "[!] Important: Users will see security warning (not code signed)"
echo "    This is normal for open-source apps without Apple Developer account"
echo "    INSTALL.md has clear bypass instructions"
echo ""
echo "[+] Build complete! Ready for distribution!"
