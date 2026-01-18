# LocalMind Screenshot Guide

**Quick guide to capturing screenshots for the User Guide in all 8 languages**

---

## Preparation

1. **Launch LocalMind**: `python -m localmind`
2. **Have a test audio file ready**: Any MP3/WAV file (10-15 minutes recommended)
3. **Clean desktop**: Remove clutter from background
4. **Full screen** (optional): For better screenshots

---

## Taking Screenshots (macOS)

### Method: Using Cmd+Shift+4 + Spacebar

1. Press `Cmd + Shift + 4`
2. Press `Spacebar` (cursor becomes a camera)
3. Click on the LocalMind window
4. Screenshot saves to Desktop

### Rename and Move

After taking each screenshot:
```bash
# Move from Desktop to screenshots folder
mv ~/Desktop/Screen\ Shot*.png docs/user-guides/screenshots/01-main-window-en.png
```

---

## Screenshots Needed (20 total)

### Part 1: English UI (10 screenshots)

#### 1. Main Window - Clean State
**Filename:** `01-main-window-en.png`
**What to show:**
- LocalMind open, no file loaded
- Clean UI showing drag-drop area
- Top menu bar visible
- Language selector showing "English"

**Steps:**
1. Launch LocalMind
2. Ensure UI is in English
3. Take screenshot: `Cmd+Shift+4` → `Space` → Click window
4. Save as: `01-main-window-en.png`

---

####  Audio File Loaded
**Filename:** `02-file-loaded-en.png`
**What to show:**
- Audio file loaded and ready
- File name and duration visible
- "Process" button ready
- Model selection visible

**Steps:**
1. Drag audio file into LocalMind
2. Wait for file to load
3. Take screenshot
4. Save as: `02-file-loaded-en.png`

---

#### 3. Model Selection Dropdown
**Filename:** `03-model-selection-en.png`
**What to show:**
- Model dropdown expanded
- All 3 options visible (Base, Medium, Large)
- Model descriptions showing

**Steps:**
1. Click on Model dropdown
2. Take screenshot while open
3. Save as: `03-model-selection-en.png`

---

#### 4. Language Selector Open
**Filename:** `04-language-selector-en.png`
**What to show:**
- Language selector dropdown expanded
- All 8 languages visible with flags
- Current language highlighted

**Steps:**
1. Click on language selector (top-right)
2. Take screenshot while dropdown open
3. Save as: `04-language-selector-en.png`

---

#### 5. Processing in Progress
**Filename:** `05-processing-en.png`
**What to show:**
- Progress bar showing percentage
- Current processing stage
- Estimated time remaining

**Steps:**
1. Click "Process" button
2. Wait 5-10 seconds for processing to start
3. Take screenshot during processing
4. Save as: `05-processing-en.png`
5. **Don't stop processing!** Continue to next step...

---

#### 6. Transcription Results
**Filename:** `06-transcription-results-en.png`
**What to show:**
- Full transcript displayed
- Speaker labels (Speaker 1, Speaker 2)
- Timestamps visible
- Transcript text clear and readable

**Steps:**
1. Wait for processing to complete
2. View transcription results
3. Take screenshot
4. Save as: `06-transcription-results-en.png`

---

#### 7. Quality Scores
**Filename:** `07-quality-scores-en.png`
**What to show:**
- Overall quality score (big number)
- Category breakdowns with scores
- Feedback/recommendations section
- Charts or visualizations

**Steps:**
1. Click on "Quality" tab (if separate)
2. Ensure scores are visible
3. Take screenshot
4. Save as: `07-quality-scores-en.png`

---

#### 8. Export Menu
**Filename:** `08-export-menu-en.png`
**What to show:**
- Export menu or dialog open
- PDF, JSON, TXT options visible
- Export settings if any

**Steps:**
1. Click File → Export (or Export button)
2. Take screenshot of export options
3. Save as: `08-export-menu-en.png`
4. Press ESC to close without exporting

---

#### 9. Settings Window
**Filename:** `09-settings-en.png`
**What to show:**
- Settings/Preferences window
- Multiple setting categories
- Configuration options visible

**Steps:**
1. Click Edit → Settings (or `Cmd+,`)
2. Ensure settings window is centered
3. Take screenshot
4. Save as: `09-settings-en.png`
5. Close settings

---

#### 10. Scoring Parameters
**Filename:** `10-scoring-parameters-en.png`
**What to show:**
- Scoring parameters customization window
- Parameter weights (sliders or numbers)
- Custom parameter options

**Steps:**
1. Open Edit → Scoring Parameters
2. Take screenshot of customization interface
3. Save as: `10-scoring-parameters-en.png`
4. Close parameters window

---

### Part 2: Other Languages (7 screenshots)

**For each language, capture the main window to show the translated UI**

#### Change Language Process:
1. Click language selector (top-right)
2. Select new language
3. UI updates immediately
4. Take screenshot of main window

#### 11. Spanish UI
**Filename:** `11-main-window-es.png`
**Steps:**
1. Change to Español 🇪🇸
2. Take screenshot of main window
3. Save as: `11-main-window-es.png`

#### 12. Japanese UI
**Filename:** `12-main-window-ja.png`
**Steps:**
1. Change to 日本語 🇯🇵
2. Take screenshot
3. Save as: `12-main-window-ja.png`

#### 13. Arabic UI (RTL)
**Filename:** `13-main-window-ar.png`
**Steps:**
1. Change to العربية 🇦🇪
2. Note: UI flips to right-to-left
3. Take screenshot
4. Save as: `13-main-window-ar.png`

#### 14. Hindi UI
**Filename:** `14-main-window-hi.png`
**Steps:**
1. Change to हिन्दी 🇮🇳
2. Take screenshot
3. Save as: `14-main-window-hi.png`

#### 15. Russian UI
**Filename:** `15-main-window-ru.png`
**Steps:**
1. Change to Русский 🇷🇺
2. Take screenshot
3. Save as: `15-main-window-ru.png`

#### 16. French UI
**Filename:** `16-main-window-fr.png`
**Steps:**
1. Change to Français 🇫🇷
2. Take screenshot
3. Save as: `16-main-window-fr.png`

#### 17. Chinese UI
**Filename:** `17-main-window-zh.png`
**Steps:**
1. Change to 中文 🇨🇳
2. Take screenshot
3. Save as: `17-main-window-zh.png`

---

### Part 3: Bonus Screenshots (Optional)

#### 18. Transcription in Spanish
**Filename:** `18-transcription-es.png`
**Steps:**
1. Keep UI in Spanish
2. Show transcription results
3. Save as: `18-transcription-es.png`

#### 19. Transcription in Hindi
**Filename:** `19-transcription-hi.png`
**Steps:**
1. Change UI to Hindi
2. Show transcription results
3. Save as: `19-transcription-hi.png`

#### 20. Quality Scores in Russian
**Filename:** `20-quality-scores-ru.png`
**Steps:**
1. Change UI to Russian
2. Show quality scoring section
3. Save as: `20-quality-scores-ru.png`

---

## Batch Rename Script

After taking screenshots on Desktop, use this script to move and rename them all at once:

```bash
#!/bin/bash
# Move screenshots from Desktop to proper location

cd ~/Desktop

# English screenshots
mv "Screen Shot 2026-01-* at *.*.* AM.png" ../localmind/localmind/docs/user-guides/screenshots/01-main-window-en.png
# ... repeat for each screenshot

# Or use numbered naming:
i=1
for file in Screen\ Shot*.png; do
    mv "$file" "../localmind/localmind/docs/user-guides/screenshots/$(printf "%02d" $i)-screenshot.png"
    ((i++))
done
```

---

## Quality Checklist

Before finishing, verify:

- ✅ All 20 screenshots taken
- ✅ Each screenshot is clear and readable
- ✅ No personal/sensitive information visible
- ✅ File names match exactly (01-main-window-en.png, etc.)
- ✅ Screenshots are in PNG format
- ✅ Minimum resolution: 1200x800px for full windows
- ✅ All saved to: `docs/user-guides/screenshots/`

---

## Next Steps

After screenshots are captured:

1. **Review quality** - Open each file and check clarity
2. **Run guide generator** - `python scripts/generate_user_guides.py`
3. **Generate PDFs** - Creates guides with embedded screenshots
4. **Translate guides** - Automated translation to all 8 languages
5. **Upload to website** - Add download links

---

**Estimated Time:** 30-40 minutes for all screenshots

**Tips:**
- Take breaks between language switches
- Keep LocalMind window at consistent size
- Use good lighting (not required but helps)
- Don't rush - quality matters for user guides!
