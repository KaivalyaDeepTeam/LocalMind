# Speaker Diarization Setup Guide

## ⚠️ Important: Python Version Requirement

**Speaker diarization requires Python 3.10** (not compatible with Python 3.11+)

If you're using Python 3.11+ (like Anaconda default), you have **two options**:

### Option A: Use Without Diarization (Recommended)
The app works great without diarization! You'll get high-quality transcripts, just without automatic Agent/Customer labels.

**Skip diarization setup and use the app as-is.**

### Option B: Install Diarization (Python 3.10 Required)

## Quick Start (One-Time Setup)

Speaker diarization automatically detects **who speaks when** in your audio files. It works with mono audio (most call recordings).

### Step 1: Create Python 3.10 Environment

**Using Conda (Recommended):**
```bash
# Create new environment with Python 3.10
conda create -n localmind python=3.10
conda activate localmind

# Navigate to project
cd /Users/prepladder/localmind/localmind

# Install main dependencies
pip install -r requirements.txt

# Install diarization (separate file)
pip install -r requirements-diarization.txt
```

**Using venv:**
```bash
# Install Python 3.10 first, then:
python3.10 -m venv venv310
source venv310/bin/activate
pip install -r requirements.txt
pip install -r requirements-diarization.txt
```

### Step 2: Authenticate with HuggingFace (One-Time)

The diarization model requires accepting terms on HuggingFace (free).

**Option A: Using CLI (Recommended)**
```bash
# Install HuggingFace CLI (if not installed)
pip install huggingface_hub

# Login (opens browser, then caches credentials)
huggingface-cli login
```

When prompted:
1. Create account at https://huggingface.co (if needed)
2. Get token from https://huggingface.co/settings/tokens (Create "Read" token)
3. Paste token in terminal
4. Accept terms at https://huggingface.co/pyannote/speaker-diarization-3.1

**Option B: Using Environment Variable**
```bash
# Set token in environment
export HF_TOKEN=hf_your_token_here

# Add to your ~/.zshrc or ~/.bash_profile for persistence
echo 'export HF_TOKEN=hf_your_token_here' >> ~/.zshrc
```

### Step 3: Run the App

```bash
python -m localmind
```

### Step 4: Enable Diarization in UI

1. Select **"Offline"** mode (top left)
2. Choose **"🇮🇳 Hindi-English (HindiSTT)"** language
3. Check ✅ **"Enable Speaker Diarization (Auto-detect Agent/Customer)"**
4. Process your audio file

**First run**: Diarization model downloads (~300MB, one-time)
**Subsequent runs**: Uses cached model (offline)

## How It Works

### Without Diarization (Default):
```
Transcript: all text together, no speaker labels
```

### With Diarization (Enabled):
```
[Agent] Hello, how can I help you?
[Customer] I need help with my account.
[Agent] I'd be happy to help with that.
```

## Features

- ✅ **Works with mono audio** (most call recordings)
- ✅ **Auto-detects speakers** (uses voice characteristics)
- ✅ **Caches model** (downloads once, works offline)
- ✅ **Smart mapping** (SPEAKER_00 → Agent, SPEAKER_01 → Customer)
- ✅ **Graceful fallback** (if diarization fails, continues without labels)

## Troubleshooting

### "401 Authentication Error"
- You haven't accepted terms or logged in
- Run: `huggingface-cli login`
- Accept terms at: https://huggingface.co/pyannote/speaker-diarization-3.1

### "Cannot install on Python version 3.11"
- **This is expected!** Diarization requires Python 3.10
- Either use Python 3.10 environment (see setup above)
- OR use the app without diarization (works great!)

### "Model not found"
- Check internet connection on first run
- Token might be invalid - create new one at https://huggingface.co/settings/tokens

### Diarization checkbox is disabled/grayed out
- `pyannote.audio` is not installed
- Hover over checkbox to see installation instructions
- You can still use the app without diarization!

### Slow processing
- Diarization adds ~30-60 seconds to processing
- Worth it for accurate speaker labels!
- Use only when you need speaker identification

### Poor speaker detection
- Works best with 2 speakers (Agent + Customer)
- Clear audio gives better results
- Noisy environments may confuse speaker changes

## Performance

| Audio Length | Processing Time (with diarization) |
|--------------|-----------------------------------|
| 5 minutes    | ~2-3 minutes (M3 Pro)            |
| 15 minutes   | ~5-7 minutes                      |
| 30 minutes   | ~10-15 minutes                    |

*Add ~1-2 minutes for first-time model download*

## Technical Details

- **Model**: pyannote/speaker-diarization-3.1
- **Size**: ~300MB
- **Cache Location**: `~/.cache/huggingface/hub/`
- **Device Support**: CPU, CUDA, Apple Silicon (MPS)
- **Works with**: Mono and stereo audio

## When to Use

✅ **Use Diarization When:**
- You have mono audio files (most common)
- You need to know who said what
- You want Agent/Customer labels automatically
- Audio quality is good enough for voice distinction

❌ **Skip Diarization When:**
- Processing speed is critical
- You only need the transcript, not speaker labels
- Audio quality is too poor (lots of noise/overlap)
- You already have stereo with separated channels

## FAQ

**Q: Do I need to be online?**
A: Only for first-time setup and download. After that, it works 100% offline.

**Q: Is my data sent anywhere?**
A: No! Everything runs locally on your machine. HuggingFace is only for model download.

**Q: Can I use my own HuggingFace account?**
A: Yes! Use your personal or company account. The token is only for authentication.

**Q: What if I don't want to create an account?**
A: Diarization is optional. Leave the checkbox unchecked for regular transcription.

## Summary

```bash
# One-time setup (2 minutes)
pip install -r requirements.txt
huggingface-cli login
# Accept terms at huggingface.co/pyannote/speaker-diarization-3.1

# Run app
python -m localmind

# Enable in UI: Offline > Hindi-English > ✅ Enable Diarization
```

That's it! Speaker labels will appear automatically.
