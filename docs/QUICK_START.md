# LocalMind Quick Start Guide

Get up and running in 5 minutes.

---

## Step 1: Download

Go to [GitHub Releases](https://github.com/KaivalyaDeepTeam/localmind/releases/latest) and download:

| Your Computer | Download |
|--------------|----------|
| Mac | `LocalMind-macOS.dmg` |
| Windows | `LocalMind-Windows.zip` |
| Linux | `LocalMind-Linux.tar.gz` |

---

## Step 2: Install

**Mac:**
1. Open the `.dmg` file
2. Drag LocalMind to Applications folder
3. Double-click to open
4. If blocked: Right-click → Open → Open

**Windows:**
1. Extract the `.zip` file
2. Open the folder
3. Double-click `LocalMind.exe`

**Linux:**
1. Extract the `.tar.gz` file
2. Open terminal in the folder
3. Run `./LocalMind`

---

## Step 3: First Use

```
┌────────────────────────────────────────────┐
│                                            │
│     Drop your audio file here              │
│                                            │
│         📁 Browse                          │
│                                            │
│     MP3, WAV, M4A, FLAC, OGG, WebM        │
│                                            │
└────────────────────────────────────────────┘
```

1. **Drop an audio file** onto the main window
   - Or click "Browse" to select a file

2. **Click "Start Processing"**
   - First run downloads AI models (~2 GB, takes 5-10 min)
   - Subsequent uses start immediately

3. **View your results**
   - Transcript appears on the right
   - Quality scores shown (if enabled)
   - Export as PDF or JSON

---

## Settings (Optional)

Access via **Settings** menu or gear icon:

### Language
Change the interface language:
- English, Russian, Spanish, Hindi, Arabic

### Theme
- Light mode
- Dark mode
- System (follows your computer)

### Quality Scoring
Toggle on/off. When ON:
- Requires an AI provider (Local, OpenAI, or Anthropic)
- Analyzes communication quality
- Provides scores and feedback

---

## Keyboard Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Open file | ⌘O | Ctrl+O |
| Start processing | ⌘Enter | Ctrl+Enter |
| Stop processing | ⌘. | Ctrl+. |
| Settings | ⌘, | Ctrl+, |
| Quit | ⌘Q | Alt+F4 |

---

## Tips

1. **Clear audio = better results**
   - Reduce background noise when possible
   - Higher quality recordings transcribe better

2. **Long files take time**
   - A 1-hour recording may take 20-30 minutes
   - Processing is done locally on your computer

3. **GPU speeds things up**
   - Macs with M1/M2/M3 chips are fast
   - Windows PCs with NVIDIA GPUs are fast
   - CPU-only works but is slower

4. **Auto-detect language**
   - Leave language on "Auto-detect" for mixed languages
   - Select specific language for best accuracy

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't open (Mac) | Right-click → Open → Open |
| First run is slow | Normal - downloading AI models |
| Processing stuck | Check if file is valid audio |
| Poor accuracy | Try clearer audio source |
| Out of memory | Close other applications |

---

## Need More Help?

- **Full User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **Report Issues**: [GitHub Issues](https://github.com/KaivalyaDeepTeam/localmind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KaivalyaDeepTeam/localmind/discussions)

---

**That's it! You're ready to use LocalMind.**
