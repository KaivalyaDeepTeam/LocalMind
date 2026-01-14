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
- Speaker diarization (identifies who said what)
- Automatic language detection
- Script romanization for non-Latin languages

### Quality Auditing
- AI-powered call quality scoring
- Customizable scoring parameters (drag-and-drop editor)
- Compliance violation detection
- Strengths and improvement suggestions

### Flexible AI Backend
- **Local LLM** - Bundled AI model, works offline (recommended)
- **OpenAI API** - Use your own API key
- **Anthropic API** - Use your own API key

### Export Options
- JSON export for integration
- Professional PDF reports
- Copy to clipboard

## Quick Start

### Download

| Platform | Download | Size |
|----------|----------|------|
| macOS | [LocalMind-macOS.dmg](https://github.com/KaivalyaDeepTeam/LocalMind/releases/latest) | ~800 MB |
| Windows | [LocalMind-Windows.zip](https://github.com/KaivalyaDeepTeam/LocalMind/releases/latest) | ~800 MB |
| Linux | [LocalMind-Linux.tar.gz](https://github.com/KaivalyaDeepTeam/LocalMind/releases/latest) | ~800 MB |

### First Run

1. Download and install LocalMind for your platform
2. Launch the application
3. Select an audio file and click "Process"
4. Whisper model downloads automatically on first use

That's it! No accounts, no API keys, no configuration needed.

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

```bash
# Clone repository
git clone https://github.com/KaivalyaDeepTeam/localmind.git
cd localmind

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m localmind
```

### Build Installers

Build must be done on the target platform.

**macOS:**
```bash
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
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libcairo2
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
- **WeasyPrint** - Professional PDF generation

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - Use it however you want, free forever.

## Support

- **Issues**: [GitHub Issues](https://github.com/KaivalyaDeepTeam/localmind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KaivalyaDeepTeam/localmind/discussions)

---

**LocalMind** - AI that respects your privacy and your wallet.
