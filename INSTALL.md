# Installing LocalMind on macOS

LocalMind is free, open-source AI software for audio transcription and quality auditing that runs completely offline on your Mac.

## 📦 System Requirements

- **macOS**: 10.15 (Catalina) or later
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 3-15GB (app + models)
- **Internet**: Required only for initial model downloads

## 🚀 Installation

### Step 1: Download

Download `LocalMind-macOS.dmg` from [GitHub Releases](https://github.com/KaivalyaDeepTeam/LocalMind/releases)

### Step 2: Install

1. Open the DMG file
2. Drag `LocalMind.app` to Applications folder

### Step 3: First Launch (Important!)

**You will see a security warning** because the app is not signed with an Apple certificate (we're open-source and don't pay $99/year for that).

**To open LocalMind:**

**Method 1 (Easiest):**
1. **Right-click** on LocalMind.app in Applications
2. Select **"Open"**
3. Click **"Open"** in the dialog

**Method 2 (Terminal):**
```bash
xattr -cr /Applications/LocalMind.app
open /Applications/LocalMind.app
```

**Method 3 (System Preferences):**
1. Try to open normally (will be blocked)
2. Go to System Preferences → Security & Privacy
3. Click "Open Anyway"

**This is a one-time step!** After first launch, you can open normally.

## ✅ Why is LocalMind Safe?

- **100% Open Source**: All code is public on GitHub
- **No Telemetry**: Zero tracking or analytics
- **Fully Offline**: Works without internet (after model download)
- **Community Verified**: Transparent development

The security warning is only because we don't have an Apple Developer certificate, not because of any security issue.

## 🎯 First Time Setup

1. **Select Language**: Choose your language mode
2. **Download Models**: AI models download automatically (5-15 minutes)
3. **Configure LLM** (optional): Choose local or cloud for auditing
4. **Start Using**: Drag & drop audio files to process!

## 📝 Usage

1. Open audio file (drag & drop or File menu)
2. Select transcription or scoring mode
3. Click Process
4. View results and export (JSON/Text/Markdown)

## 🗑️ Uninstall

Delete the app:
```bash
rm -rf /Applications/LocalMind.app
```

Remove data (optional):
```bash
rm -rf ~/Library/Application\ Support/LocalMind/
```

## 🆘 Need Help?

- **Issues**: https://github.com/KaivalyaDeepTeam/LocalMind/issues
- **Docs**: https://github.com/KaivalyaDeepTeam/LocalMind#readme

---

**Free & Open Source** • MIT License • Made with ❤️ by LocalMind Team
