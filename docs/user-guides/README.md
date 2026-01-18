# LocalMind User Guides

## Overview

Comprehensive technical guides for LocalMind in 8 languages with professional screenshots.

## Available Guides

### Markdown Versions (Ready Now)

All guides are available in Markdown format with embedded screenshots:

| Language | File | Native Name |
|----------|------|-------------|
| 🇬🇧 English | [TECHNICAL_GUIDE_EN.md](TECHNICAL_GUIDE_EN.md) | English |
| 🇪🇸 Spanish | [TECHNICAL_GUIDE_ES.md](TECHNICAL_GUIDE_ES.md) | Español |
| 🇷🇺 Russian | [TECHNICAL_GUIDE_RU.md](TECHNICAL_GUIDE_RU.md) | Русский |
| 🇮🇳 Hindi | [TECHNICAL_GUIDE_HI.md](TECHNICAL_GUIDE_HI.md) | हिन्दी |
| 🇫🇷 French | [TECHNICAL_GUIDE_FR.md](TECHNICAL_GUIDE_FR.md) | Français |
| 🇯🇵 Japanese | [TECHNICAL_GUIDE_JA.md](TECHNICAL_GUIDE_JA.md) | 日本語 |
| 🇦🇪 Arabic | [TECHNICAL_GUIDE_AR.md](TECHNICAL_GUIDE_AR.md) | العربية |
| 🇨🇳 Chinese | [TECHNICAL_GUIDE_ZH.md](TECHNICAL_GUIDE_ZH.md) | 中文 |

### PDF Versions

See [README_PDF.md](README_PDF.md) for instructions on generating professional PDF versions.

## Screenshots

**Total:** 14 screenshots organized in `screenshots/` folder

**English UI** (8 screenshots):
- 01-main-window-en.png - Main window with processing pipeline
- 02-scoring-parameters-en.png - Scoring parameters editor
- 03-settings-llm-en.png - LLM Provider settings
- 04-llm-provider-dropdown-en.png - Provider selection dropdown
- 05-model-selection-en.png - Model selection dropdown
- 06-settings-transcription-en.png - Whisper transcription settings
- 07-settings-output-en.png - Output and export settings
- 08-settings-appearance-en.png - Appearance and language settings

**Russian UI (Русский)** (6 screenshots):
- 11-main-window-ru.png - Main window in Russian
- 12-settings-llm-ru.png - LLM Provider settings in Russian
- 13-settings-transcription-ru.png - Transcription settings in Russian
- 14-settings-output-ru.png - Output settings in Russian
- 15-settings-appearance-ru.png - Appearance settings in Russian
- 16-language-dropdown-ru.png - Language dropdown showing all 8 languages

## Guide Structure

Each technical guide includes:

### 1. Quick Start
- System requirements
- Installation steps
- First launch instructions

### 2. Your First Transcription
- Step-by-step walkthrough
- Processing modes explained
- Model selection guidance

### 3. Understanding Quality Scoring
- Default parameters explained
- Customization options
- Chain-of-Thought (CoT) reasoning details

### 4. Choosing the Right Model
- Comparison of Qwen models
- Whisper model variants (Base, Medium, Large)
- Use case recommendations

### 5. Settings
- LLM Provider configuration
- Transcription settings
- Output settings
- Appearance customization

### 6. Export & Share
- Available formats (JSON, PDF, TXT)
- Export workflow

### 7. Multilingual Support
- 8 supported UI languages
- 50+ transcription languages
- How to change language

### 8. Troubleshooting
- Common issues and solutions
- Performance optimization tips
- Quality improvement guidance

### 9. Privacy & Security
- What LocalMind collects (nothing!)
- Data storage locations
- Open source transparency

### 10. Advanced Tips
- Speed optimization
- Accuracy improvement
- Batch processing
- Custom scoring profiles

## Professional Design

Guides follow premium product manual aesthetics:

✓ Minimalist, clean layout
✓ Generous white space
✓ Large, integrated screenshots
✓ User-centric language
✓ Short, punchy headlines
✓ Visual step-by-step workflows
✓ Clear troubleshooting sections

## Usage

### For Users

1. **Download**: Click the language you prefer
2. **Read**: View directly on GitHub or download markdown
3. **PDF**: Generate PDF using instructions in README_PDF.md

### For Developers

1. **Translate**: Use existing guides as templates for new languages
2. **Update**: Edit markdown files directly
3. **Screenshots**: Add new screenshots to `screenshots/` folder
4. **Generate PDFs**: Run `python ../scripts/generate_pdfs.py`

## Maintenance

### Adding New Screenshots

1. Take screenshot using macOS: `Cmd + Shift + 4` → `Spacebar` → Click window
2. Name using convention: `##-description-LANG.png`
3. Save to `screenshots/` folder
4. Reference in markdown: `![Description](screenshots/filename.png)`

### Adding New Languages

1. Copy `TECHNICAL_GUIDE_EN.md` to `TECHNICAL_GUIDE_{CODE}.md`
2. Translate all content
3. Update screenshot references if language-specific
4. Add to guides list in this README
5. Add to `scripts/generate_pdfs.py` GUIDES list

### Updating Content

1. Edit the English version first
2. Propagate changes to other languages
3. Update version number and date at bottom
4. Test all screenshot links
5. Regenerate PDFs if needed

## Technical Details

**Format:** GitHub Flavored Markdown
**Screenshots:** PNG format, optimized for web
**Image hosting:** Relative paths in same repository
**Encoding:** UTF-8 with BOM for RTL languages (Arabic)
**Line endings:** LF (Unix style)

## Statistics

- **Total Words (English):** ~2,500
- **Total Screenshots:** 14
- **Languages:** 8
- **Sections:** 10 main sections
- **File Sizes:** ~10-18KB per markdown file
- **Screenshot Sizes:** ~200-400KB per image

## Credits

**Created:** January 2026
**Style:** Premium technical manual
**Screenshots:** LocalMind v1.0.0
**Languages:** English, Spanish, Russian, Hindi, French, Japanese, Arabic, Chinese

## License

Documentation: MIT License
Screenshots: © 2026 LocalMind Project

---

**For PDF generation instructions, see:** [README_PDF.md](README_PDF.md)

**For screenshot capture guide, see:** [../SCREENSHOT_GUIDE.md](../SCREENSHOT_GUIDE.md)
