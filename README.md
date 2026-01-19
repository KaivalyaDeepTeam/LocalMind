# LocalMind

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**The First Free, Open Source AI That Runs 100% On Your Machine**

LocalMind is a revolutionary desktop application that brings enterprise-grade AI capabilities to everyone - completely free, completely offline, completely private.

## Why LocalMind?

- **100% Free Forever** - No subscriptions, no API costs, no hidden fees
- **100% Offline** - Works without internet after initial setup
- **100% Private** - Your data never leaves your machine
- **100% Open Source** - Inspect, modify, and contribute

## Features

### Audio Transcription
- Multi-language support (English, Russian, Hindi, Arabic, Italian, Spanish)
- Automatic language detection
- Script romanization for non-Latin languages

### Quality Auditing
- AI-powered call quality scoring
- **Fully customizable scoring parameters** - Create profiles for your organization
- Visual drag-and-drop weight editor (no technical skills needed)
- Import/export scoring profiles to share with your team
- Compliance violation detection
- Strengths and improvement suggestions
- [**→ Customization Guide**](SCORING_GUIDE.md) - Step-by-step instructions for non-technical users

### Flexible AI Backend
- **Local LLM** - Bundled AI model, works offline (recommended)
- **OpenAI API** - Use your own API key
- **Anthropic API** - Use your own API key

### Export Options
- **PDF reports** with charts and visualizations
- **Markdown reports** for easy sharing
- JSON export for integration
- TXT transcript export
- Copy to clipboard

## Quick Start

### Download

| Platform | Download | Size |
|----------|----------|------|
| macOS | [LocalMind-macOS.dmg](https://github.com/KaivalyaDeepTeam/LocalMind/releases/latest) | ~300 MB |
| Windows | Coming Soon | ~300 MB |
| Linux | Coming Soon | ~300 MB |

> **Note:** AI models (~1.5 GB) download automatically on first run.

### First Run

1. Download and install LocalMind for your platform
2. Launch the application
3. Select an audio file and click "Process"
4. Whisper model downloads automatically on first use

That's it! No accounts, no API keys, no configuration needed.

## Customization for Organizations

LocalMind is designed for **easy customization by non-technical users**. Organizations can create custom scoring profiles that match their specific audit requirements.

### Creating Your Own Scoring Profile

1. Open **Edit → Scoring Parameters** (Ctrl+Shift+S)
2. Click **New** to create a profile for your organization
3. Add custom parameters using the visual editor
4. Adjust weights with the drag-and-drop slider
5. Save and share with your team

### Real-World Example

**Svetozar Technologies** might create a custom profile with:
- Data Privacy Compliance (3.0x weight - critical)
- Technical Accuracy (2.5x weight - high)
- Brand Messaging (1.5x weight - important)
- Custom company-specific requirements

**No coding required!** The visual editor makes it easy for call center managers, QA teams, and trainers to customize scoring without technical knowledge.

📖 **[Read the Complete Customization Guide](SCORING_GUIDE.md)**

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Storage | 10 GB | 15 GB |
| GPU | None | NVIDIA/Apple Silicon |
| OS | macOS 12+, Windows 10+, Ubuntu 22.04+ | Latest |

## Performance

| Hardware | 10 min Audio | Real-time Factor |
|----------|--------------|------------------|
| M3 Pro Mac | ~4-5 min | 0.4-0.5x |
| RTX 4090 | ~1-2 min | 0.1-0.2x |
| RTX 3080 | ~3-4 min | 0.3-0.4x |
| CPU Only | ~15-20 min | 1.5-2.0x |

## For Developers

### Install from Source

**macOS:**
```bash
# Clone repository
git clone https://github.com/KaivalyaDeepTeam/localmind.git
cd localmind

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m localmind
```

**Linux (Ubuntu/Debian):**
```bash
# Clone repository
git clone https://github.com/KaivalyaDeepTeam/localmind.git
cd localmind

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m localmind
```

**Windows:**
```bash
# Clone repository
git clone https://github.com/KaivalyaDeepTeam/localmind.git
cd localmind

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m localmind
```

### Build Installers

Build must be done on the target platform.

**macOS:**
```bash
# Build
pip install pyinstaller
pyinstaller LocalMind.spec
hdiutil create -volname "LocalMind" -srcfolder dist/LocalMind.app -ov -format UDZO LocalMind-macOS.dmg
```

**Windows:**
```bash
pip install pyinstaller
pyinstaller LocalMind.spec
# Creates dist\LocalMind\ - compress to ZIP
```

**Linux (Ubuntu/Debian):**
```bash
# Build
pip install pyinstaller
pyinstaller LocalMind.spec
# Creates dist/LocalMind/ - compress to tar.gz
tar -czvf LocalMind-Linux.tar.gz -C dist LocalMind
```

## Technology

LocalMind is built with:

- **PySide6** - Cross-platform native UI
- **Whisper** - State-of-the-art speech recognition
- **Phi-3.5** - Efficient local language model
- **llama.cpp** - Optimized local inference

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - Use it however you want, free forever.

## Support

- **Issues**: [GitHub Issues](https://github.com/KaivalyaDeepTeam/localmind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KaivalyaDeepTeam/localmind/discussions)

---

**LocalMind** - AI that respects your privacy and your wallet.
