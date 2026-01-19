# LocalMind Technical Guide
## Version 1.2.0

---

**Transform Audio into Intelligence**

Professional-grade transcription with AI-powered quality analysis.
100% offline. Zero cost. Complete privacy.

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation & First Launch](#installation--first-launch)
4. [Section A: Transcription (Speech-to-Text)](#section-a-transcription-speech-to-text)
   - [What is Transcription?](#what-is-transcription)
   - [Whisper Models Explained](#whisper-models-explained)
   - [Language Support](#transcription-language-support)
   - [Transcription Settings](#transcription-settings)
5. [Section B: LLM Quality Analysis](#section-b-llm-quality-analysis)
   - [What is LLM Analysis?](#what-is-llm-analysis)
   - [LLM Provider Options](#llm-provider-options)
   - [Local LLM Models](#local-llm-models)
   - [Cloud LLM Providers](#cloud-llm-providers)
   - [Quality Scoring Parameters](#quality-scoring-parameters)
6. [Export Options](#export-options)
7. [Settings Reference](#settings-reference)
8. [Troubleshooting](#troubleshooting)
9. [Privacy & Security](#privacy--security)

---

## Introduction

LocalMind is a desktop application that performs two distinct AI tasks:

| Task | Technology | Purpose |
|------|------------|---------|
| **Transcription** | OpenAI Whisper | Convert speech to text |
| **Quality Analysis** | Local/Cloud LLM | Score and analyze conversations |

These are **separate systems** that work together but can be used independently.

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | macOS 12 (Monterey) or later |
| RAM | 8 GB |
| Storage | 10 GB free space |
| Processor | Intel or Apple Silicon |

### Recommended Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | macOS 14 (Sonoma) or later |
| RAM | 16 GB or more |
| Storage | 20 GB free space |
| Processor | Apple M1/M2/M3 chip |

### First Run Downloads

On first launch, LocalMind downloads AI models:

| Model Type | Size | When Downloaded |
|------------|------|-----------------|
| Whisper (transcription) | ~1.5 GB | First transcription |
| Local LLM (analysis) | ~4 GB | First quality analysis |

**Internet required only for initial model downloads.**

---

## Installation & First Launch

### Step 1: Download

Download `LocalMind-1.2.0-macOS.dmg` from:
[github.com/KaivalyaDeepTeam/LocalMind/releases](https://github.com/KaivalyaDeepTeam/LocalMind/releases)

### Step 2: Install

1. Open the downloaded DMG file
2. Drag LocalMind to your Applications folder
3. Eject the DMG

### Step 3: First Launch

**Important:** macOS may block the app because it's not from the App Store.

**To open LocalMind:**

1. Right-click on LocalMind.app
2. Select "Open" from the menu
3. Click "Open" in the security dialog

This is a one-time step. After this, you can open normally.

### Step 4: Model Download

On first use:
- **Transcription models** download when you process your first audio file
- **LLM models** download when you enable quality scoring

Progress is shown in the status bar. This may take 5-15 minutes depending on your internet speed.

---

# Section A: Transcription (Speech-to-Text)

This section covers **converting audio to text** using OpenAI's Whisper technology.

---

## What is Transcription?

Transcription converts spoken words in audio files into written text. LocalMind uses **OpenAI Whisper**, one of the most accurate speech recognition systems available.

### How It Works

```
Audio File → Whisper AI → Written Transcript
   (MP3)       (Local)        (Text)
```

### Key Features

- **50+ languages** supported
- **Automatic language detection**
- **Speaker identification** (diarization)
- **Timestamps** for each segment
- **Works completely offline** after model download

### Supported Audio Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| MP3 | .mp3 | Most common format |
| WAV | .wav | Uncompressed, high quality |
| M4A | .m4a | Apple/iTunes format |
| FLAC | .flac | Lossless compression |
| OGG | .ogg | Open source format |
| WebM | .webm | Web audio format |

**Maximum file size:** 2 GB per file

---

## Whisper Models Explained

Whisper comes in different sizes. Larger models are more accurate but slower.

### Available Models

| Model | Size | Accuracy | Speed | Best For |
|-------|------|----------|-------|----------|
| **Large V3** | 1.5 GB | 97-99% | Slow | Professional use, critical accuracy |
| **Medium** | 750 MB | 95-97% | Medium | Daily use, good balance |
| **Small** | 250 MB | 92-95% | Fast | Quick transcriptions |
| **Base** | 150 MB | 88-92% | Very Fast | Testing, drafts |
| **Tiny** | 75 MB | 80-88% | Fastest | Real-time, low accuracy OK |

### Model Recommendation

| Your Priority | Recommended Model |
|---------------|-------------------|
| Best accuracy | Large V3 |
| Balanced performance | Medium |
| Fast processing | Small |
| Limited disk space | Base |

### How to Change Model

1. Go to **Settings** (Cmd + ,)
2. Select **Transcription** tab
3. Choose model from dropdown
4. Model downloads automatically if not present

---

## Transcription Language Support

### Automatic Detection

By default, LocalMind automatically detects the spoken language. This works well for:
- Single-language recordings
- Clear audio quality

### Manual Selection

For best results, manually select the language when:
- Audio has background noise
- Multiple languages are mixed
- Accuracy is critical

### Supported Languages (50+)

**European:** English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Russian, Ukrainian, Czech, Greek, Swedish, Danish, Norwegian, Finnish

**Asian:** Chinese (Mandarin), Japanese, Korean, Hindi, Bengali, Tamil, Telugu, Thai, Vietnamese, Indonesian, Malay

**Middle Eastern:** Arabic, Hebrew, Turkish, Persian, Urdu

**And many more...**

---

## Transcription Settings

Access via **Settings → Transcription**

### Basic Settings

| Setting | Options | Description |
|---------|---------|-------------|
| Model | Tiny → Large V3 | Accuracy vs speed tradeoff |
| Language | Auto / Specific | Audio language selection |
| GPU Acceleration | On / Off | Use Apple Silicon GPU |

### Advanced Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Chunk Length | 30 sec | Audio segments for processing |
| Batch Size | 16 | Parallel chunks (RAM dependent) |
| Compute Type | float16 | Precision (float32 for CPU) |

### Performance Tips

**For faster processing:**
- Enable GPU Acceleration (M1/M2/M3 Macs)
- Use Medium or Small model
- Increase Batch Size if you have 16GB+ RAM

**For better accuracy:**
- Use Large V3 model
- Select specific language (don't use auto-detect)
- Use high-quality audio source

---

# Section B: LLM Quality Analysis

This section covers **AI-powered conversation analysis** using Large Language Models.

---

## What is LLM Analysis?

LLM (Large Language Model) analysis reads your transcript and evaluates conversation quality. It provides:

- **Overall score** (0-100%)
- **Parameter scores** (customizable criteria)
- **Strengths** identified in the conversation
- **Areas for improvement**
- **Detailed feedback** for each parameter

### How It Works

```
Transcript → LLM Analysis → Quality Report
  (Text)       (AI)         (Scores + Feedback)
```

### Key Difference from Transcription

| Aspect | Transcription | LLM Analysis |
|--------|---------------|--------------|
| **Input** | Audio file | Text transcript |
| **Output** | Written text | Scores & feedback |
| **Technology** | Whisper | LLM (Phi/Qwen/GPT) |
| **Purpose** | Convert speech | Evaluate quality |
| **Required?** | Yes | Optional |

**LLM Analysis requires transcription to be completed first.**

---

## LLM Provider Options

LocalMind supports three ways to run LLM analysis:

### 1. Local LLM (Recommended)

**Runs entirely on your computer.**

| Pros | Cons |
|------|------|
| 100% free | Slower than cloud |
| Complete privacy | Requires 8GB+ RAM |
| No internet needed | Large model download |
| No API limits | |

### 2. OpenAI API

**Uses OpenAI's GPT models via internet.**

| Pros | Cons |
|------|------|
| Very fast | Costs money (per use) |
| High quality | Requires internet |
| No local resources | Data sent to cloud |

### 3. Anthropic API

**Uses Anthropic's Claude models via internet.**

| Pros | Cons |
|------|------|
| Excellent reasoning | Costs money (per use) |
| Great for analysis | Requires internet |
| Detailed feedback | Data sent to cloud |

### How to Choose

| Your Situation | Recommended Provider |
|----------------|---------------------|
| Privacy is critical | Local LLM |
| No internet available | Local LLM |
| Need fastest results | OpenAI API |
| Budget available | OpenAI or Anthropic |
| Best analysis quality | Anthropic API |

---

## Local LLM Models

When using Local LLM, you can choose from several models:

### Available Local Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **Phi-3.5 Mini** | 2.4 GB | Fast | Good | Default, balanced |
| **Qwen 2.5 3B** | 2.0 GB | Very Fast | Good | Quick analysis |
| **Qwen 2.5 7B** | 4.4 GB | Medium | Excellent | Professional use |
| **Mistral 7B** | 4.1 GB | Medium | Excellent | Detailed feedback |
| **Gemma 2 2B** | 1.6 GB | Fastest | Moderate | Speed priority |

### Model Recommendation

| Priority | Recommended Model |
|----------|-------------------|
| Best quality | Qwen 2.5 7B or Mistral 7B |
| Balanced | Phi-3.5 Mini (default) |
| Fastest | Gemma 2 2B |
| Low RAM (8GB) | Qwen 2.5 3B |

### How to Change Local Model

1. Go to **Settings → LLM Provider**
2. Select **Local LLM**
3. Click **Model** dropdown
4. Choose your preferred model
5. Model downloads automatically

---

## Cloud LLM Providers

### Setting Up OpenAI

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Go to **Settings → LLM Provider**
3. Select **OpenAI API**
4. Paste your API key
5. Click **Verify** to test connection

**Recommended model:** GPT-4o Mini (best value)

**Approximate cost:** $0.01-0.05 per audio file

### Setting Up Anthropic

1. Get API key from [console.anthropic.com](https://console.anthropic.com)
2. Go to **Settings → LLM Provider**
3. Select **Anthropic API**
4. Paste your API key
5. Click **Verify** to test connection

**Recommended model:** Claude 3.5 Haiku (best value)

**Approximate cost:** $0.01-0.03 per audio file

---

## Quality Scoring Parameters

LocalMind evaluates conversations using customizable parameters.

### Default Parameters

| Parameter | Weight | What It Measures |
|-----------|--------|------------------|
| Greeting & Introduction | 1.0x | Professional opening |
| Active Listening | 1.0x | Attention and engagement |
| Problem Identification | 1.0x | Understanding the issue |
| Solution Provided | 1.0x | Helpful resolution |
| Product Knowledge | 1.0x | Accuracy of information |
| Communication Clarity | 1.0x | Clear explanations |
| Empathy & Rapport | 1.0x | Emotional connection |
| Call Control | 1.0x | Managing conversation flow |
| Call Closing | 1.0x | Professional ending |
| Script Compliance | 1.0x | Following guidelines |

### Understanding Weights

Weights range from **0.1x to 3.0x**:

| Weight | Meaning | Impact on Score |
|--------|---------|-----------------|
| 0.1x - 0.5x | Low priority | Minor impact |
| 1.0x | Standard | Normal impact |
| 1.5x - 2.0x | High priority | Significant impact |
| 2.5x - 3.0x | Critical | Major impact |

### Custom Scoring Profiles

Create profiles for different use cases:

**Sales Calls:**
- Product Knowledge: 2.5x
- Call Closing: 2.0x
- Communication Clarity: 2.0x

**Support Calls:**
- Empathy & Rapport: 2.5x
- Problem Identification: 2.0x
- Solution Provided: 2.5x

**Compliance Audits:**
- Script Compliance: 3.0x
- Greeting & Introduction: 2.0x

### How to Customize

1. Go to **Edit → Scoring Parameters** (Cmd + Shift + S)
2. Adjust weight sliders
3. Add/remove parameters as needed
4. Save as new profile
5. Select profile when processing

---

## Export Options

LocalMind offers four export formats:

### PDF Report (Recommended)

**Keyboard:** Cmd + Shift + P

**Includes:**
- Circular score gauge with overall percentage
- Bar chart visualization of all parameters
- Detailed scores table with ratings
- AI feedback (summary, strengths, improvements)
- Full transcript (optional)

**Best for:** Sharing with management, clients, or stakeholders

### Markdown Report

**Keyboard:** Cmd + Shift + M

**Includes:**
- Formatted text with scores
- Strengths and improvements
- Easy to view in any text editor

**Best for:** Quick sharing, documentation, version control

### JSON Export

**Keyboard:** Cmd + Shift + J

**Includes:**
- Complete structured data
- All scores and metadata
- Machine-readable format

**Best for:** Integration with other systems, batch processing

### Text Transcript

**Keyboard:** Cmd + Shift + T

**Includes:**
- Plain text transcript
- Speaker labels
- Timestamps

**Best for:** Simple archival, text processing

---

## Settings Reference

### Transcription Tab

| Setting | Description |
|---------|-------------|
| Whisper Model | Speech recognition model size |
| Language | Audio language (Auto or specific) |
| GPU Acceleration | Use Apple Silicon for speed |
| Chunk Length | Audio segment size (advanced) |
| Batch Size | Parallel processing (advanced) |

### LLM Provider Tab

| Setting | Description |
|---------|-------------|
| Provider | Local LLM, OpenAI, or Anthropic |
| Model | Specific model to use |
| API Key | Required for cloud providers |
| Temperature | Creativity (0.0-1.0, lower = consistent) |

### Output Tab

| Setting | Description |
|---------|-------------|
| Output Directory | Where to save files |
| Auto-export JSON | Save JSON after processing |
| Auto-export PDF | Save PDF after processing |
| Include Transcript | Add transcript to PDF |

### Appearance Tab

| Setting | Description |
|---------|-------------|
| Theme | Light, Dark, or System |
| Language | UI language (8 available) |
| Colorblind Mode | Accessible color scheme |

---

## Troubleshooting

### Transcription Issues

**Problem: Transcription is very slow**

Solutions:
- Enable GPU Acceleration in Settings
- Use a smaller Whisper model (Medium or Small)
- Close other applications to free RAM
- Process shorter audio files

**Problem: Poor transcription accuracy**

Solutions:
- Use Large V3 model
- Select specific language instead of Auto-detect
- Use higher quality audio source
- Enable audio preprocessing

**Problem: Wrong language detected**

Solution:
- Manually select the correct language in Settings

### LLM Analysis Issues

**Problem: Quality scoring not working**

Solutions:
- Ensure LLM provider is configured in Settings
- Check if Local LLM model is downloaded
- Verify API key if using cloud provider
- Enable "Quality Scoring" checkbox before processing

**Problem: Local LLM is slow**

Solutions:
- Use a smaller model (Phi-3.5 or Gemma 2)
- Close other applications
- Consider using cloud provider for speed

**Problem: API error with cloud provider**

Solutions:
- Check API key is correct
- Verify account has credits/balance
- Check internet connection
- Try again later (rate limits)

### General Issues

**Problem: App won't open**

Solution (macOS):
1. Right-click LocalMind.app
2. Select "Open"
3. Click "Open" in dialog

**Problem: Models not downloading**

Solutions:
- Check internet connection
- Ensure sufficient disk space (10GB+)
- Check firewall/VPN settings
- Try restarting the app

**Problem: Out of memory error**

Solutions:
- Close other applications
- Use smaller models
- Restart the app
- Process shorter audio files

---

## Privacy & Security

### Data Handling

| Mode | Audio Data | Transcript |
|------|------------|------------|
| **Local LLM** | Stays on device | Stays on device |
| **OpenAI API** | Stays on device | Sent to OpenAI |
| **Anthropic API** | Stays on device | Sent to Anthropic |

**Your audio files are NEVER uploaded to the cloud.**

Only text transcripts are sent when using cloud LLM providers.

### What LocalMind Collects

**Nothing.**

- No telemetry
- No analytics
- No crash reports
- No usage tracking
- No account required

### Data Storage Locations

| Data | Location |
|------|----------|
| Transcripts | Your chosen output folder |
| Whisper models | `~/.cache/whisper/` |
| LLM models | `~/.cache/localmind/models/` |
| Settings | `~/Library/Application Support/LocalMind/` |

### Deleting All Data

To completely remove LocalMind data:

```bash
# Remove app
rm -rf /Applications/LocalMind.app

# Remove models
rm -rf ~/.cache/whisper/
rm -rf ~/.cache/localmind/

# Remove settings
rm -rf ~/Library/Application\ Support/LocalMind/
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Audio File | Cmd + O |
| Start Processing | Cmd + Return |
| Stop Processing | Escape |
| Export PDF | Cmd + Shift + P |
| Export Markdown | Cmd + Shift + M |
| Export JSON | Cmd + Shift + J |
| Export Transcript | Cmd + Shift + T |
| Scoring Parameters | Cmd + Shift + S |
| Settings | Cmd + , |
| Show Shortcuts | Cmd + / |
| Quit | Cmd + Q |

---

## Getting Help

### Resources

- **Documentation:** [github.com/KaivalyaDeepTeam/LocalMind](https://github.com/KaivalyaDeepTeam/LocalMind)
- **Issues:** [github.com/KaivalyaDeepTeam/LocalMind/issues](https://github.com/KaivalyaDeepTeam/LocalMind/issues)
- **Discussions:** [github.com/KaivalyaDeepTeam/LocalMind/discussions](https://github.com/KaivalyaDeepTeam/LocalMind/discussions)

### Reporting Bugs

When reporting an issue, include:
1. What you were trying to do
2. What happened instead
3. Your macOS version
4. LocalMind version (1.2.0)
5. Any error messages

---

## About LocalMind

LocalMind is free, open-source software built to provide professional-grade audio analysis while respecting your privacy.

### Our Principles

- **Free Forever** - No subscriptions, no hidden costs
- **Privacy First** - Your data stays on your device
- **Open Source** - Transparent, auditable code
- **Offline Capable** - Works without internet

### Credits

- **Whisper** by OpenAI - Speech recognition
- **Phi-3.5** by Microsoft - Local language model
- **llama.cpp** - Efficient local inference
- **PySide6** - Cross-platform UI
- **ReportLab** - PDF generation

---

**Version:** 1.2.0
**Last Updated:** January 2026
**License:** MIT (Free for any use)

---

© 2026 LocalMind Team. Made with care for everyone who values privacy.
