# Speaker Diarization Status

## Current Implementation ❌

**The current "dual-channel" mode is NOT real speaker diarization!**

### What it does:
- Splits stereo audio into left/right channels
- Assumes: Left = Agent, Right = Customer
- **Problem**: Most call recordings are MONO (single channel)
- **Result**: Mono audio gets duplicated → same text transcribed twice → very bad quality

### When it works:
- Only if you have stereo files with speakers already separated
- Example: Professional call center systems that record each speaker on separate channels
- This is RARE in practice

## What's Needed for Real Diarization ✅

### 1. Install pyannote.audio
```bash
pip install pyannote.audio
```

### 2. Get Hugging Face Token
1. Create account at https://huggingface.co
2. Accept terms at https://huggingface.co/pyannote/speaker-diarization-3.1
3. Get token from https://huggingface.co/settings/tokens
4. Set environment variable:
   ```bash
   export HF_TOKEN=your_token_here
   ```

### 3. How Real Diarization Works
- Works with **mono audio** (most common)
- Detects speaker changes using voice characteristics
- Segments based on who is speaking when
- Assigns speaker labels: SPEAKER_00, SPEAKER_01, etc.

## Implementation Status

### ✅ Completed
- [x] Added `DiarizationWorker` class
- [x] Added `pyannote.audio>=3.1.0` to requirements
- [x] Created `combine_diarization_with_transcription()` helper

### 🚧 To Do
- [ ] Integrate diarization into Hindi workers
- [ ] Auto-detect mono vs stereo audio
- [ ] Use single-channel worker for mono
- [ ] Add UI option to enable/disable diarization
- [ ] Map SPEAKER_00/01 to Agent/Customer labels

## Quick Fix for Now

### For Mono Audio (Recommended)
The app will automatically use single-channel mode which:
- Transcribes all audio as one stream
- No speaker labels (or all labeled as "Unknown")
- Much better accuracy than broken dual-channel

### For Stereo Audio
Only use if your audio truly has:
- Left channel = one speaker
- Right channel = other speaker

## Future Enhancement

We can add a "Smart Diarization" mode that:
1. Checks if audio is mono or stereo
2. For mono: Uses pyannote.audio for speaker detection
3. For stereo: Uses current channel separation
4. Intelligently assigns Agent/Customer labels based on patterns

This requires user testing and feedback to get right.
