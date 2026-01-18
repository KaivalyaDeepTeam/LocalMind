# DMG Build Readiness Checklist for LocalMind

## ✅ READY - What's Working

### 1. Build Configuration
- ✅ PyInstaller spec file exists (`LocalMind.spec`)
- ✅ GitHub Actions workflow configured (`release.yml`)
- ✅ DMG creation command: `hdiutil create -volname "LocalMind" -srcfolder dist/LocalMind.app -ov -format UDZO LocalMind-macOS.dmg`
- ✅ App bundle identifier: `ai.localmind.desktop`
- ✅ Minimum macOS version: 10.15 (Catalina)

### 2. Dependencies Management
- ✅ All Python dependencies in `pyproject.toml`
- ✅ Models are downloaded on-demand (not bundled)
- ✅ Model storage uses standard paths:
  - macOS: `~/Library/Application Support/LocalMind/models`
  - Creates directory automatically if missing

### 3. App Structure
- ✅ Console disabled (proper GUI app)
- ✅ File associations configured (wav, mp3, m4a, ogg, flac, webm)
- ✅ High resolution support enabled
- ✅ Dark mode support enabled

## ⚠️ CRITICAL ISSUES - Must Fix Before Release

### 1. **Missing App Icon**
```python
# In LocalMind.spec line 91:
icon=None,  # ❌ No icon specified!
```
**Impact:** DMG will work but app will show generic icon
**Fix:** Create icon.icns and update spec:
```python
icon='localmind/resources/images/icon.icns',
```

### 2. **Large Dependencies Not Optimized**
Heavy packages included:
- `torch` + `torchaudio` (~2GB)
- `transformers` (~500MB)
- `llama-cpp-python` (compiled binaries)

**Impact:** DMG will be 2-3GB in size
**Fix:** Consider:
- Using `--onefile` mode
- Excluding unnecessary torch backends
- Using UPX compression (already enabled)

### 3. **No Code Signing**
```python
codesign_identity=None,  # ❌ Not signed
```
**Impact:** macOS Gatekeeper will block on first run
- Users will see: "LocalMind cannot be opened because it is from an unidentified developer"
- Workaround required: Right-click > Open (first time only)

**Fix Options:**
- Sign with Apple Developer ID ($99/year)
- OR document workaround clearly in README
- OR use `--deep` flag with ad-hoc signing

### 4. **No Notarization**
**Impact:** macOS 10.15+ will show extra security warnings
**Fix:** Requires:
1. Apple Developer account
2. Code signing certificate
3. Notarization process via Apple

### 5. **Python Runtime Dependencies**
The DMG bundles Python interpreter and all libraries, but:
- ❌ No verification that bundled Python is self-contained
- ❌ Might rely on system Python in some edge cases

**Test Required:** Install on COMPLETELY FRESH Mac (no Python, no Homebrew)

## 🔧 RECOMMENDED FIXES BEFORE RELEASE

### Fix 1: Add App Icon
```bash
# Create icon from PNG (need ImageMagick or iconutil)
mkdir LocalMind.iconset
sips -z 16 16     icon.png --out LocalMind.iconset/icon_16x16.png
sips -z 32 32     icon.png --out LocalMind.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out LocalMind.iconset/icon_32x32.png
sips -z 64 64     icon.png --out LocalMind.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out LocalMind.iconset/icon_128x128.png
sips -z 256 256   icon.png --out LocalMind.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out LocalMind.iconset/icon_256x256.png
sips -z 512 512   icon.png --out LocalMind.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out LocalMind.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out LocalMind.iconset/icon_512x512@2x.png
iconutil -c icns LocalMind.iconset -o localmind/resources/images/icon.icns
```

### Fix 2: Optimize PyInstaller Spec
```python
# Add to excludes in LocalMind.spec:
excludes=[
    'tkinter',
    'matplotlib',  # If not used directly
    'IPython',
    'notebook',
    'pytest',
],

# Add PyTorch optimization:
hiddenimports=[
    ...
    'torch.nn.functional',  # Explicit instead of full torch
]

# Reduce torch size:
a = Analysis(
    ...
    excludes=['torch.distributions'],  # If not needed
)
```

### Fix 3: Add Gatekeeper Bypass Instructions
Create `README_DMG_INSTALL.md`:
```markdown
# Installing LocalMind on macOS

## First-Time Installation

1. Download `LocalMind-macOS.dmg`
2. Open the DMG file
3. Drag LocalMind.app to Applications folder

## ⚠️ Security Warning Workaround

If you see "LocalMind cannot be opened":

**Method 1 (Recommended):**
1. Right-click LocalMind.app
2. Select "Open"
3. Click "Open" in the dialog

**Method 2 (Command Line):**
```bash
xattr -cr /Applications/LocalMind.app
```

This is a one-time step. After this, you can open normally.
```

### Fix 4: Create Standalone Build Script
```bash
#!/bin/bash
# build_dmg.sh

echo "🔨 Building LocalMind DMG..."

# Clean previous builds
rm -rf build dist *.dmg

# Install dependencies
pip install -e ".[dev]"
pip install pyinstaller

# Build with PyInstaller
pyinstaller LocalMind.spec

# Create DMG
hdiutil create \
  -volname "LocalMind" \
  -srcfolder dist/LocalMind.app \
  -ov \
  -format UDZO \
  LocalMind-macOS.dmg

echo "✅ DMG created: LocalMind-macOS.dmg"
echo "📦 Size: $(du -h LocalMind-macOS.dmg | cut -f1)"
```

## 🧪 TESTING CHECKLIST (Fresh Mac)

Before releasing, test on a Mac with:
- ✅ No Python installed
- ✅ No Homebrew
- ✅ No Xcode Command Line Tools
- ✅ Fresh macOS install (VM recommended)

**Test Steps:**
1. Mount DMG
2. Copy to Applications
3. Launch app (use right-click > Open)
4. Select language
5. Download Whisper model (test internet connection)
6. Process a test audio file
7. Export results (JSON, transcript, markdown)
8. Change settings
9. Close and reopen (test persistence)

**Expected Behavior:**
- ✅ App launches without errors
- ✅ Models download automatically
- ✅ Audio processing works
- ✅ Settings persist
- ✅ No Python errors in Console.app

## 🚨 SHOW STOPPERS (Will NOT work on fresh Mac)

### None Currently Detected ✅

The app SHOULD work because:
- ✅ PyInstaller bundles Python interpreter
- ✅ All dependencies are bundled
- ✅ Models download on-demand
- ✅ No system Python required

### Potential Issues to Watch:

1. **llama-cpp-python compiled binaries**
   - May have architecture dependencies
   - Test on both Intel and Apple Silicon

2. **PyTorch Metal acceleration**
   - May need macOS 12.3+ for M1/M2
   - Falls back to CPU if not available

3. **Audio codecs**
   - MP3/M4A might need system codecs
   - Test all supported formats

## 📋 BUILD COMMAND SUMMARY

### Quick Build (Local Testing)
```bash
# 1. Clean
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. Build
pyinstaller LocalMind.spec

# 3. Create DMG
hdiutil create -volname "LocalMind" -srcfolder dist/LocalMind.app -ov -format UDZO LocalMind-macOS.dmg

# 4. Test
open LocalMind-macOS.dmg
```

### Production Build (GitHub Actions)
```bash
# Trigger workflow
gh workflow run release.yml --ref main -f tag=v1.1.0
```

## 📊 FINAL READINESS SCORE

| Category | Status | Score |
|----------|--------|-------|
| Build Config | ✅ Working | 10/10 |
| Dependencies | ✅ Bundled | 10/10 |
| Models | ✅ Download on-demand | 10/10 |
| App Icon | ⚠️ Missing | 5/10 |
| Code Signing | ❌ None | 0/10 |
| Documentation | ⚠️ Needs install guide | 5/10 |
| Testing | ⚠️ Not verified on fresh Mac | 0/10 |

**Overall: 40/70 (57%)**

## 🎯 MINIMUM VIABLE RELEASE

To ship NOW with acceptable UX:

1. ✅ Keep current build (works but unsigned)
2. ⚠️ Add app icon (5 min fix)
3. ✅ Add installation instructions with Gatekeeper bypass
4. ⚠️ Test on one fresh Mac VM
5. ✅ Document "first run may take time to download models"

**This will produce a working DMG that requires user to bypass Gatekeeper.**

## 🚀 PRODUCTION READY RELEASE

For professional release:

1. Get Apple Developer account ($99/year)
2. Code sign the app
3. Notarize with Apple
4. Add app icon
5. Test on multiple fresh Macs (Intel + Apple Silicon)
6. Create professional installer DMG with background image
7. Add auto-updater (Sparkle framework)

**Timeline: 1-2 weeks + Apple Developer setup**
