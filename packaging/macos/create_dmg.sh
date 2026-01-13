#!/bin/bash
# LocalMind macOS DMG Creation Script
#
# Requirements:
#   - create-dmg (brew install create-dmg)
#   - App bundle already built in dist/
#
# Usage: ./create_dmg.sh [version]

set -e

VERSION="${1:-1.0.0}"
APP_NAME="LocalMind"
DMG_NAME="${APP_NAME}-${VERSION}-macOS.dmg"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DIST_DIR="${PROJECT_ROOT}/dist"
APP_PATH="${DIST_DIR}/${APP_NAME}.app"

echo "==================================="
echo "  LocalMind DMG Creator"
echo "  Version: ${VERSION}"
echo "==================================="

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: App bundle not found at ${APP_PATH}"
    echo "Run the build script first: python packaging/scripts/build.py"
    exit 1
fi

# Check for create-dmg
if ! command -v create-dmg &> /dev/null; then
    echo "create-dmg not found. Installing via Homebrew..."
    brew install create-dmg
fi

# Remove existing DMG
rm -f "${DIST_DIR}/${DMG_NAME}"

echo ""
echo "Creating DMG..."

create-dmg \
    --volname "${APP_NAME}" \
    --volicon "${SCRIPT_DIR}/icon.icns" \
    --background "${SCRIPT_DIR}/dmg_background.png" \
    --window-pos 200 120 \
    --window-size 660 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 180 190 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 480 190 \
    --no-internet-enable \
    "${DIST_DIR}/${DMG_NAME}" \
    "${APP_PATH}" \
    || {
        # Fallback if background image doesn't exist
        echo "Retrying without background image..."
        create-dmg \
            --volname "${APP_NAME}" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --icon "${APP_NAME}.app" 150 190 \
            --hide-extension "${APP_NAME}.app" \
            --app-drop-link 450 190 \
            --no-internet-enable \
            "${DIST_DIR}/${DMG_NAME}" \
            "${APP_PATH}"
    }

echo ""
echo "==================================="
echo "  DMG created successfully!"
echo "  Output: ${DIST_DIR}/${DMG_NAME}"
echo "==================================="

# Show file size
ls -lh "${DIST_DIR}/${DMG_NAME}"
