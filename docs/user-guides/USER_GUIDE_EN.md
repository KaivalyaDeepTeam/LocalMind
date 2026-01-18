# LocalMind User Guide

**Version 1.2.0 | English**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Changing Language](#changing-language)
3. [Understanding AI Models](#understanding-ai-models)
4. [Step-by-Step Usage](#step-by-step-usage)
5. [Model Selection Guide](#model-selection-guide)
6. [Quality Scoring](#quality-scoring)
7. [Export Options](#export-options)
8. [Tips & Best Practices](#tips--best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is LocalMind?

LocalMind is a **100% free, offline AI transcription and quality analysis tool** that runs entirely on your computer. No internet connection needed after setup, no subscriptions, and complete privacy.

**Key Features:**
- ✅ Professional audio transcription powered by Whisper AI
- ✅ AI-powered quality scoring with Chain-of-Thought reasoning
- ✅ Multi-language support (99+ languages for transcription)
- ✅ Customizable scoring parameters
- ✅ 100% offline - works without internet
- ✅ No data ever leaves your device

###First Launch

When you first open LocalMind:

1. **Initial Model Download** (~2-3 GB)
   - LocalMind will automatically download the AI models
   - This happens only once
   - Takes 5-10 minutes depending on internet speed
   - Models are cached for future use

2. **Main Window Appears**
   - Clean, intuitive interface
   - Drag-and-drop area for audio files
   - Menu bar with settings and options
   - Language selector in the top-right corner

![Screenshot: Main Window - Clean interface with drag-drop area]

---

## Changing Language

LocalMind's user interface is available in **8 languages**:
- 🇬🇧 English
- 🇪🇸 Spanish (Español)
- 🇯🇵 Japanese (日本語)
- 🇦🇪 Arabic (العربية) - with RTL layout
- 🇮🇳 Hindi (हिन्दी)
- 🇷🇺 Russian (Русский)
- 🇫🇷 French (Français)
- 🇨🇳 Chinese Simplified (中文)

### How to Change Language:

**Method 1: Language Selector (Top-Right)**

1. Look for the **language dropdown** in the top-right corner
2. Click on the **flag icon** or current language
3. Select your preferred language from the dropdown
4. Interface instantly updates to the new language

![Screenshot: Language dropdown showing all 8 languages]

**Method 2: Settings Menu**

1. Go to **Menu → Settings** (or press `Ctrl+,` / `Cmd+,`)
2. Find **"Language" section**
3. Choose from the dropdown
4. Click **"Apply"**

![Screenshot: Settings window with language selection]

**Note:** Changing the UI language doesn't affect audio transcription language detection - that's automatic!

---

## Understanding AI Models

LocalMind uses **two types of AI models** to provide the best experience:

### 1. Whisper Models (Speech Recognition)

**What it does:** Converts audio speech into written text

LocalMind offers **3 Whisper model variants**:

#### Base Model (Default) ⚡
- **File Size:** ~140 MB
- **Speed:** Very Fast
- **Accuracy:** Good (90-92%)
- **Best for:** Quick transcriptions, clear audio, casual use
- **Processing:** 10-min audio ≈ 2-3 minutes on laptop

#### Medium Model (Balanced) ⭐ **Recommended**
- **File Size:** ~1.5 GB
- **Speed:** Moderate
- **Accuracy:** Excellent (95-97%)
- **Best for:** Professional use, important recordings
- **Processing:** 10-min audio ≈ 5-7 minutes on laptop

#### Large Model (Maximum Quality) 🎯
- **File Size:** ~3 GB
- **Speed:** Slower
- **Accuracy:** Best (97-99%)
- **Best for:** Critical transcriptions, legal/medical, noisy audio
- **Processing:** 10-min audio ≈ 10-15 minutes on laptop

**Which Model Should You Use?**
- **General use:** Medium Model (best balance)
- **Quick drafts:** Base Model
- **Critical accuracy:** Large Model
- **Poor audio quality:** Large Model (handles noise better)

![Screenshot: Model selection dropdown with descriptions]

### 2. Phi-3.5 Model (Quality Analysis)

**What it does:** Analyzes transcription for quality, compliance, and insights

**Model Details:**
- **Size:** ~2 GB (downloads automatically)
- **Purpose:** Understanding context, scoring quality, generating feedback
- **Technology:** Microsoft's Phi-3.5 Mini (3.8B parameters)
- **Speed:** Near real-time analysis
- **Accuracy:** Enhanced with Chain-of-Thought reasoning (20-30% better)

**What it analyzes:**
- Communication clarity
- Professional tone
- Compliance with guidelines
- Problem resolution
- Empathy and engagement
- Custom parameters you define

---

## Step-by-Step Usage

### Step 1: Load Audio File

**Three ways to load audio:**

**Method A: Drag & Drop** (Easiest)
1. Open LocalMind
2. Drag your audio file from Finder/Explorer
3. Drop it onto the main window
4. File loads automatically

**Method B: File Menu**
1. Click **File → Open Audio** (or `Ctrl+O` / `Cmd+O`)
2. Browse to your audio file
3. Select and click **"Open"**

**Method C: Recent Files**
1. Click **File → Recent Files**
2. Select from previously processed files

![Screenshot: Main window with audio file loaded, showing filename and duration]

**Supported Formats:**
- MP3, WAV, M4A, FLAC, OGG, WebM
- Any length (tested up to 4+ hours)
- Mono or stereo recordings

### Step 2: Select Model & Language

**Before processing, configure:**

**A. Whisper Model Selection**
1. Find **"Model"** dropdown (usually below file name)
2. Choose: **Base** / **Medium** / **Large**
3. See model description update with size and speed info

**B. Audio Language** (Optional)
1. Find **"Language"** dropdown
2. Options:
   - **Auto-detect** (Recommended) - Whisper automatically detects
   - **Specific language** - Choose if you know (e.g., Spanish, Hindi)
3. For best results with clear audio: Use Auto-detect

![Screenshot: Model and language selection dropdowns]

### Step 3: Enable Quality Scoring (Optional)

**Quality Analysis Options:**

1. Find **"Enable Quality Scoring"** checkbox
2. Check to enable AI quality analysis
3. Click **"Configure Scoring"** to customize parameters
4. Choose scoring profile:
   - **Default** - General communication quality
   - **Call Center** - Customer service metrics
   - **Legal** - Compliance and professionalism
   - **Custom** - Your own parameters

**Scoring Parameters:**
- Communication Clarity (Weight: 1.5x)
- Professionalism (Weight: 2.0x)
- Compliance (Weight: 1.8x)
- Problem Resolution (Weight: 1.5x)
- Empathy & Engagement (Weight: 1.2x)

![Screenshot: Quality scoring configuration panel]

### Step 4: Process Audio

**Start Transcription:**

1. Click the big **"Process"** button (or `Ctrl+P` / `Cmd+P`)
2. **Processing begins** - you'll see:
   - Progress bar showing percentage complete
   - Current stage (Loading model → Transcribing → Analyzing)
   - Estimated time remaining
   - Real-time transcription preview (if enabled)

3. **During processing:**
   - You can continue using your computer
   - Don't close LocalMind
   - Don't put computer to sleep (pauses processing)

![Screenshot: Processing in progress with progress bar and status]

**Processing Times:**

| Hardware | 10-Min Audio | 60-Min Audio |
|----------|--------------|--------------|
| M3 Pro Mac | 2-3 min | 15-20 min |
| RTX 4090 GPU | 1-2 min | 8-12 min |
| RTX 3080 GPU | 2-4 min | 15-25 min |
| Standard Laptop (CPU) | 8-12 min | 50-70 min |

### Step 5: Review Results

**After processing completes:**

**Transcription Tab:**
- **Full transcript** with timestamps
- **Speaker labels** (Speaker 1, Speaker 2, etc.)
- **Paragraphs** automatically detected
- **Search function** to find specific words

**Quality Tab** (if enabled):
- **Overall score** (0-100)
- **Category breakdowns** with individual scores
- **Strengths** - What went well
- **Areas for Improvement** - Specific suggestions
- **Compliance notes** - Flags or violations
- **Chain-of-Thought reasoning** - AI's detailed analysis

![Screenshot: Transcription results with speaker labels and timestamps]

![Screenshot: Quality scoring results with scores and feedback]

---

## Model Selection Guide

### Choose the Right Model for Your Use Case

#### Use Case 1: Customer Service Calls 📞

**Scenario:** Call center analyzing 100+ calls per day

**Recommended Setup:**
- **Whisper Model:** Medium (balance of speed & accuracy)
- **Quality Scoring:** Enabled with "Call Center" profile
- **Parameters:**
  - Greeting Quality (2.0x weight)
  - Problem Resolution (2.5x weight)
  - Empathy (2.0x weight)
  - Compliance (1.8x weight)

**Why:** Medium model processes fast enough for volume while maintaining professional accuracy. Quality scoring helps train agents.

**Expected Time:** 3-5 minutes per 10-minute call (M1/M2 Mac)

---

#### Use Case 2: Medical/Legal Transcription ⚖️

**Scenario:** Accurate transcription of patient interviews or depositions

**Recommended Setup:**
- **Whisper Model:** Large (maximum accuracy)
- **Quality Scoring:** Disabled (focus on accuracy, not analysis)
- **Language:** Auto-detect or specific if known

**Why:** Large model provides 97-99% accuracy critical for medical/legal documentation. HIPAA/compliance-safe (100% offline).

**Expected Time:** 10-15 minutes per 10-minute recording

---

#### Use Case 3: Podcast/Interview Transcription 🎙️

**Scenario:** Creating show notes, blog posts, or subtitles

**Recommended Setup:**
- **Whisper Model:** Medium (good balance)
- **Quality Scoring:** Disabled (not needed for content)
- **Export:** TXT or JSON format

**Why:** Medium provides excellent accuracy without the extra time of Large. Focus on transcript quality, not quality analysis.

**Expected Time:** 5-7 minutes per 10-minute episode

---

#### Use Case 4: Quick Meeting Notes 📝

**Scenario:** Fast turnaround for internal team meetings

**Recommended Setup:**
- **Whisper Model:** Base (fastest)
- **Quality Scoring:** Disabled
- **Export:** Copy to clipboard

**Why:** Base model is 3-4x faster for quick internal use. Acceptable accuracy for informal notes.

**Expected Time:** 2-3 minutes per 10-minute meeting

---

#### Use Case 5: Multi-Language Content 🌍

**Scenario:** Transcribing audio in Spanish, Hindi, Arabic, etc.

**Recommended Setup:**
- **Whisper Model:** Medium or Large
- **Language:** Auto-detect (works best for Whisper)
- **UI Language:** Match your preference

**Why:** Whisper excels at multi-language recognition. Medium/Large models handle accents and code-switching better.

**Supported Languages:** English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Arabic, Hindi, Chinese, Japanese, Korean, and 85+ more!

---

#### Use Case 6: Noisy Audio / Poor Quality 📢

**Scenario:** Street interviews, crowded locations, phone recordings

**Recommended Setup:**
- **Whisper Model:** Large (best noise handling)
- **Pre-processing:** Use audio cleanup tool if available
- **Expectations:** Accuracy will be lower with very noisy audio

**Why:** Large model has better noise resistance. Still, garbage-in = garbage-out. Consider cleaning audio first with tools like Audacity.

---

## Quality Scoring

### Understanding Scores

LocalMind's AI analyzes transcriptions across **5 key dimensions**:

#### 1. Communication Clarity (0-100)
**What it measures:**
- How clearly ideas were expressed
- Use of appropriate language
- Avoiding jargon or confusing terms
- Logical flow of conversation

**Good Example (95):**
> "I understand your concern. Let me explain our policy in simple terms. First, we'll process your refund within 3-5 business days. Second, you'll receive an email confirmation. Does that help?"

**Poor Example (55):**
> "Yeah so like, the thing is, um, we've got this process, you know, and it's like, complicated, but yeah we'll get to it eventually."

#### 2. Professionalism (0-100)
**What it measures:**
- Appropriate tone and language
- Respectful communication
- No inappropriate language
- Professional demeanor

**High Score:** Courteous, respectful, professional language
**Low Score:** Rude tone, interruptions, unprofessional words

#### 3. Compliance (0-100)
**What it measures:**
- Following required scripts/guidelines
- Mentioning required disclosures
- Avoiding prohibited statements
- Meeting regulatory requirements

**Customizable:** Add your company's specific compliance rules

#### 4. Problem Resolution (0-100)
**What it measures:**
- Addressing customer's actual issue
- Providing clear solutions
- Following up appropriately
- Reaching resolution

**High Score:** Issue fully resolved, customer satisfied
**Low Score:** Issue unresolved, customer frustrated

#### 5. Empathy & Engagement (0-100)
**What it measures:**
- Active listening cues
- Acknowledging customer emotions
- Using empathetic language
- Personal engagement

**Good Example:**
> "I completely understand how frustrating this must be for you. Let me personally ensure this gets resolved today."

### Customizing Scoring Parameters

**Create Your Own Scoring Profile:**

1. Go to **Edit → Scoring Parameters** (or `Ctrl+Shift+S`)
2. Click **"New Profile"**
3. Name your profile (e.g., "Tech Support Profile")
4. Add/modify parameters:
   - **Parameter Name:** What you're measuring
   - **Weight:** Importance (0.5x to 3.0x)
   - **Description:** What qualifies as good/bad
   - **Keywords:** Specific phrases to look for

**Example: Custom Tech Support Profile**

```
Profile Name: Tech Support Quality
Parameters:
- Greeting (1.5x): "Thank you for calling", "How may I help"
- Technical Accuracy (2.5x): Correct troubleshooting steps
- Patience (2.0x): Not rushing customer, explaining clearly
- Escalation Awareness (1.8x): Knowing when to escalate
- Closing (1.5x): "Is there anything else", confirming resolution
```

![Screenshot: Scoring parameters editor with weights and descriptions]

---

## Export Options

LocalMind offers **3 export formats** to suit different needs:

### 1. PDF Report (Professional)

**What's included:**
- Company logo/branding (customizable)
- Full transcript with timestamps
- Speaker identification
- Quality scores with visualizations
- Detailed feedback and recommendations
- Charts and graphs
- Customizable template

**Best for:**
- Sharing with managers/stakeholders
- Client presentations
- Performance reviews
- Documentation

**How to export:**
1. Click **File → Export → PDF Report**
2. Choose template (Standard / Detailed / Summary)
3. Add custom notes if needed
4. Click **"Generate PDF"**
5. Choose save location

![Screenshot: PDF export dialog with template options]

### 2. JSON Export (Technical)

**What's included:**
- Raw transcript data
- Speaker labels and timestamps
- Quality scores (if enabled)
- Metadata (file info, processing time)
- Custom parameters used
- AI reasoning (Chain-of-Thought)

**Best for:**
- Developers integrating with other systems
- Batch processing workflows
- Data analysis in Excel/Python
- Custom report generation

**How to export:**
1. Click **File → Export → JSON Data**
2. Choose save location
3. JSON file includes all data in structured format

**JSON Structure:**
```json
{
  "transcript": {
    "segments": [
      {
        "speaker": "Speaker 1",
        "text": "Hello, how can I help you today?",
        "timestamp": "00:00:05"
      }
    ]
  },
  "quality_scores": {
    "overall": 87,
    "categories": {
      "communication": 92,
      "professionalism": 85
    }
  }
}
```

### 3. Plain Text (Simple)

**What's included:**
- Clean transcript text
- Speaker labels
- Timestamps (optional)
- No formatting or scores

**Best for:**
- Copy-pasting into documents
- Quick sharing via email
- Text editing in other tools
- Creating blog posts from podcasts

**How to export:**
1. Click **File → Export → Text File**
2. Options:
   - Include timestamps: Yes/No
   - Include speaker labels: Yes/No
   - Include quality scores: Yes/No
3. Choose save location

### Quick Copy to Clipboard

**Fastest option for quick use:**

1. Click **Edit → Copy Transcript** (or `Ctrl+Shift+C`)
2. Transcript copies to clipboard
3. Paste anywhere you need it

---

## Tips & Best Practices

### For Best Transcription Accuracy

✅ **DO:**
- Use clear, high-quality audio recordings
- Minimize background noise if possible
- Speak clearly and at moderate pace
- Use Medium or Large model for important content
- Let speakers finish sentences (avoid talking over)

❌ **DON'T:**
- Process very noisy or distorted audio without cleanup
- Expect perfection from heavily accented/muffled audio
- Interrupt the app during processing
- Use Base model for critical transcriptions

### For Efficient Processing

✅ **DO:**
- Close other heavy applications during processing
- Use GPU if available (10x faster)
- Process multiple files overnight with batch mode
- Start with smaller files to test settings

❌ **DON'T:**
- Put computer to sleep during processing
- Run multiple LocalMind instances simultaneously
- Process 4+ hour files on old hardware

### For Quality Scoring

✅ **DO:**
- Customize parameters for your specific use case
- Review and adjust weights based on results
- Use scoring profiles for different scenarios
- Export results to track improvements over time

❌ **DON'T:**
- Use default parameters for specialized needs
- Ignore the AI's reasoning - it provides context
- Over-weight too many parameters (dilutes focus)

### Privacy & Security

✅ **DO:**
- Use LocalMind for sensitive recordings (100% offline)
- Verify no internet connection if needed (airplane mode works!)
- Trust that data never leaves your device
- Review exported files before sharing

❌ **DON'T:**
- Upload LocalMind transcripts to untrusted cloud services
- Share JSON exports containing sensitive data
- Assume cloud services are as private

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Model Download Failed"

**Symptoms:** Error message during first launch, models won't download

**Solutions:**
1. **Check internet connection** - Required for initial download
2. **Check disk space** - Need 5-10 GB free
3. **Retry download** - Click "Retry" or restart app
4. **Manual download** - Download models from GitHub releases
5. **Firewall** - Temporarily disable to test

---

#### Issue 2: "Transcription is Inaccurate"

**Symptoms:** Wrong words, missing sections, garbled text

**Solutions:**
1. **Upgrade model** - Use Medium or Large instead of Base
2. **Check audio quality** - Very noisy audio = poor results
3. **Specify language** - If auto-detect fails, manually select
4. **Clean audio first** - Use Audacity to remove noise
5. **Check audio format** - Try converting to WAV

---

#### Issue 3: "Processing is Very Slow"

**Symptoms:** Takes 30+ minutes for 10-minute audio

**Solutions:**
1. **Use smaller model** - Base processes 3x faster than Large
2. **Enable GPU** - Go to Settings → Performance → Enable GPU
3. **Close other apps** - Free up CPU/RAM
4. **Check hardware** - See system requirements
5. **Update drivers** - Especially GPU drivers

---

#### Issue 4: "App Crashes During Processing"

**Symptoms:** LocalMind closes unexpectedly mid-process

**Solutions:**
1. **Check RAM** - Need 8GB minimum, 16GB recommended
2. **Update LocalMind** - Get latest version
3. **Reduce file size** - Split long audio into smaller chunks
4. **Check logs** - Help → Show Logs for error details
5. **Reinstall app** - Clean install may fix corruption

---

#### Issue 5: "Quality Scores Seem Wrong"

**Symptoms:** Scores don't match your assessment of quality

**Solutions:**
1. **Review parameters** - Make sure they match your criteria
2. **Adjust weights** - Increase weight of important factors
3. **Add custom keywords** - Help AI recognize your specific terms
4. **Check reasoning** - Read AI's Chain-of-Thought explanation
5. **Refine over time** - Scoring improves as you customize

---

### Getting Help

**Still having issues?**

1. **Check documentation:** [https://github.com/KaivalyaDeepTeam/LocalMind/tree/main/docs](https://github.com/KaivalyaDeepTeam/LocalMind/tree/main/docs)

2. **Search existing issues:** [https://github.com/KaivalyaDeepTeam/LocalMind/issues](https://github.com/KaivalyaDeepTeam/LocalMind/issues)

3. **Ask the community:** [https://github.com/KaivalyaDeepTeam/LocalMind/discussions](https://github.com/KaivalyaDeepTeam/LocalMind/discussions)

4. **Report a bug:** [Create new issue](https://github.com/KaivalyaDeepTeam/LocalMind/issues/new)

**When reporting, include:**
- Operating system (macOS 13.4, Windows 11, etc.)
- LocalMind version (Help → About)
- Error message (exact wording)
- Steps to reproduce
- Audio file format/length

---

## Keyboard Shortcuts

### General
- `Ctrl+O` / `Cmd+O` - Open audio file
- `Ctrl+P` / `Cmd+P` - Start processing
- `Ctrl+,` / `Cmd+,` - Open settings
- `Ctrl+Q` / `Cmd+Q` - Quit application

### Editing
- `Ctrl+C` / `Cmd+C` - Copy selected text
- `Ctrl+Shift+C` / `Cmd+Shift+C` - Copy full transcript
- `Ctrl+F` / `Cmd+F` - Find in transcript

### Export
- `Ctrl+E` / `Cmd+E` - Export menu
- `Ctrl+S` / `Cmd+S` - Quick save as text

### View
- `Ctrl+1` - Show transcript tab
- `Ctrl+2` - Show quality tab
- `Ctrl+3` - Show settings tab

---

## About LocalMind

**LocalMind** is developed by **Svetozar Technologies** with a mission to democratize AI and protect user privacy.

### Our Principles

- **Free Forever** - No subscriptions, no trials, no paywalls
- **Privacy First** - Your data never leaves your device
- **Open Source** - Transparent, auditable code (MIT License)
- **Offline First** - Works without internet after setup

### Version Information

- **Current Version:** 1.2.0
- **Release Date:** January 2026
- **License:** MIT (Free for personal and commercial use)
- **Support:** Community-driven via GitHub

### Contributing

LocalMind is open source! Contribute at:
**https://github.com/KaivalyaDeepTeam/LocalMind**

---

**Thank you for using LocalMind!** 🎉

*Powerful AI. Complete Privacy. Zero Cost.*
