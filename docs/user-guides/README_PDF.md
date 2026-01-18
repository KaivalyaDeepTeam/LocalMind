# Generating PDF User Guides

## Quick Method (macOS)

### Option 1: Using pandoc with BasicTeX (Recommended)

```bash
# Install BasicTeX (smaller than full MacTeX, ~100MB)
brew install --cask basictex

# Update PATH (add to ~/.zshrc or ~/.bash_profile)
eval "$(/usr/libexec/path_helper)"

# Install required packages
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended

# Generate PDFs
python scripts/generate_pdfs.py
```

### Option 2: Using Markdown Editors

**Typora** (Paid, but excellent):
1. Open any `TECHNICAL_GUIDE_*.md` file in Typora
2. File → Export → PDF
3. Repeat for all 8 languages

**MacDown** (Free):
1. Open markdown file
2. File → Export → PDF
3. Repeat for all languages

### Option 3: Online Conversion

1. Visit https://www.markdowntopdf.com/
2. Upload each `TECHNICAL_GUIDE_*.md` file
3. Download generated PDF
4. Rename to `LocalMind_Technical_Guide_{LANG}.pdf`

## Files Ready for PDF Conversion

- `TECHNICAL_GUIDE_EN.md` → English
- `TECHNICAL_GUIDE_ES.md` → Spanish (Español)
- `TECHNICAL_GUIDE_RU.md` → Russian (Русский)
- `TECHNICAL_GUIDE_HI.md` → Hindi (हिन्दी)
- `TECHNICAL_GUIDE_FR.md` → French (Français)
- `TECHNICAL_GUIDE_JA.md` → Japanese (日本語)
- `TECHNICAL_GUIDE_AR.md` → Arabic (العربية)
- `TECHNICAL_GUIDE_ZH.md` → Chinese (中文)

## Recommended PDF Settings

- **Page Size:** A4 or Letter
- **Margins:** 1 inch all sides
- **Font Size:** 11pt
- **Include:** Table of Contents
- **Images:** Embed screenshots

## Screenshot Paths

Screenshots are relative paths in markdown:
- `screenshots/01-main-window-en.png`
- `screenshots/11-main-window-ru.png`
- etc.

Make sure to convert from the `docs/user-guides/` directory so images are found correctly.

## Future: Automated CI/CD

Consider setting up GitHub Actions to auto-generate PDFs on every commit:

```yaml
name: Generate PDFs
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install pandoc
        run: sudo apt-get install -y pandoc texlive-xelatex
      - name: Generate PDFs
        run: python scripts/generate_pdfs.py
      - name: Upload PDFs
        uses: actions/upload-artifact@v2
        with:
          name: user-guides-pdf
          path: docs/user-guides/pdf/
```
