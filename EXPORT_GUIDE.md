# Export Guide - JSON and TXT Formats

## Overview

LocalMind exports call quality audits in two formats:
1. **JSON** - Complete data for integration and processing
2. **TXT** - Human-readable transcripts for review

---

## JSON Export

### How to Export
- **Menu**: File → Export as JSON...
- **Keyboard**: `Ctrl+Shift+J`

### What's Included
```json
{
  "file_name": "call_recording.wav",
  "language": "en",
  "duration": 123.45,
  "transcript": "Full conversation text...",
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "speaker": "Agent",
      "text": "Hello, how can I help you?"
    }
  ],
  "audit": {
    "overall_score": 85.5,
    "compliance_score": 90.0,
    "quality_score": 82.5,
    "parameter_scores": [
      {
        "name": "greeting",
        "display_name": "Greeting & Introduction",
        "score": 9.0,
        "max_score": 10.0,
        "weight": 1.5,
        "feedback": "Excellent professional greeting..."
      }
    ],
    "strengths": [
      "Professional greeting",
      "Clear communication"
    ],
    "improvements": [
      "Could improve active listening",
      "More empathy needed"
    ],
    "summary": "Overall good call quality..."
  }
}
```

### Use Cases
- **Integration**: Import into your CRM or QA system
- **Analysis**: Process with scripts or analytics tools
- **Backup**: Store complete audit data
- **API**: Send to external services
- **Reporting**: Generate custom reports programmatically

---

## TXT Export

### How to Export
- **Menu**: File → Export Transcript...
- **Keyboard**: `Ctrl+Shift+T`

### What's Included
```
Transcript: call_recording.wav
Language: en
Duration: 123.4s
==================================================

[0.0s - 5.2s] Agent: Hello, how can I help you?

[5.2s - 10.8s] Customer: I need help with my account.

[10.8s - 15.3s] Agent: I'd be happy to help with that.

[15.3s - 25.1s] Customer: I can't login to the portal.

[25.1s - 35.7s] Agent: Let me help you reset your password.
```

### Use Cases
- **Review**: Quick human-readable review
- **Training**: Use for agent coaching
- **Documentation**: Attach to support tickets
- **Sharing**: Email to team members
- **Archival**: Simple text-based storage

---

## Features

### Automatic Handling

| Feature | Description |
|---------|-------------|
| **Auto Extensions** | Adds `.json` or `.txt` if you forget |
| **Auto Directories** | Creates folders if they don't exist |
| **Unicode Support** | Handles Hindi, Arabic, Russian, etc. |
| **Empty Segment Skip** | Removes blank entries automatically |
| **Data Validation** | Checks for required data before export |

### Error Handling

| Error | What You'll See |
|-------|----------------|
| **No Results** | "No results to export. Please process an audio file first." |
| **Missing Transcript** | "No transcript data available to export." |
| **Permission Denied** | "Cannot write to: [path]. Please check file permissions." |
| **Disk Full** | "Not enough disk space. Please free up some space." |
| **Invalid Path** | "Please provide a valid file path." |

---

## Examples

### Example 1: Svetozar Technologies Export

**Scenario**: Export audit results for Svetozar's custom scoring profile

1. Process a call with Svetozar scoring profile loaded
2. Export as JSON: `svetozar_call_001.json`
3. Results include custom parameters:
   - Data Privacy Compliance (3.0x weight)
   - Technical Accuracy (2.5x weight)
   - Brand Messaging (1.5x weight)

**JSON Output**:
```json
{
  "file_name": "svetozar_call_001.wav",
  "audit": {
    "overall_score": 87.3,
    "parameter_scores": [
      {
        "name": "data_privacy",
        "display_name": "Data Privacy Compliance",
        "score": 10.0,
        "max_score": 10.0,
        "weight": 3.0,
        "feedback": "Excellent GDPR compliance..."
      },
      {
        "name": "technical_accuracy",
        "display_name": "Technical Accuracy",
        "score": 8.5,
        "max_score": 10.0,
        "weight": 2.5,
        "feedback": "Mostly accurate technical info..."
      }
    ]
  }
}
```

### Example 2: Multilingual Call Export

**Scenario**: Hindi-English customer service call

1. Process call in Hindi mode
2. Export transcript: `hindi_call_transcript.txt`

**TXT Output**:
```
Transcript: customer_support_hindi.wav
Language: hi
Duration: 245.3s
==================================================

[0.0s - 4.2s] Agent: नमस्ते, मैं आपकी कैसे मदद कर सकता हूं?

[4.2s - 8.5s] Customer: Hi, I need help with my order.

[8.5s - 15.7s] Agent: Sure, let me check your order details.

[15.7s - 22.3s] Customer: मेरा ऑर्डर नंबर 12345 है।
```

---

## Integration Examples

### Python Integration

```python
import json

# Read JSON export
with open('audit_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Extract overall score
score = results['audit']['overall_score']
print(f"Call score: {score}%")

# Get failing parameters (score < 7.0)
failing = [
    p for p in results['audit']['parameter_scores']
    if p['score'] < 7.0
]

# Print areas for improvement
for param in failing:
    print(f"- {param['display_name']}: {param['score']}/{param['max_score']}")
    print(f"  Feedback: {param['feedback']}")
```

### Excel/Google Sheets

1. Export as JSON
2. Use online JSON to CSV converter: https://json-csv.com
3. Import CSV into Excel/Sheets
4. Create pivot tables and charts

### CRM Integration

```python
import requests
import json

# Read audit results
with open('audit_results.json', 'r') as f:
    audit_data = json.load(f)

# Send to your CRM
response = requests.post(
    'https://your-crm.com/api/call-audits',
    json={
        'call_id': audit_data['file_name'],
        'score': audit_data['audit']['overall_score'],
        'compliance': audit_data['audit']['compliance_score'],
        'quality': audit_data['audit']['quality_score'],
        'transcript': audit_data['transcript'],
        'strengths': audit_data['audit']['strengths'],
        'improvements': audit_data['audit']['improvements']
    },
    headers={'Authorization': 'Bearer YOUR_API_KEY'}
)
```

---

## Best Practices

### For Call Center Managers

1. **Daily Exports**: Export all day's audits at end of shift
2. **Naming Convention**: Use `YYYYMMDD_agentname_callnumber.json`
3. **Backup**: Store JSON files in cloud storage (Dropbox, Google Drive)
4. **Review**: Use TXT files for quick agent coaching sessions

### For QA Teams

1. **Batch Processing**: Export all calls in a folder
2. **Analysis**: Use Python/Excel to analyze trends
3. **Reporting**: Create weekly/monthly summary reports
4. **Archival**: Keep JSON for complete audit trail

### For Trainers

1. **Examples**: Export excellent calls as TXT for training materials
2. **Coaching**: Share TXT transcripts with agents for review
3. **Comparison**: Export before/after training to show improvement

---

## Troubleshooting

### "Cannot write to file"
- **Cause**: File is open in another program or folder is read-only
- **Solution**: Close the file or choose a different location

### "No results to export"
- **Cause**: No audio has been processed yet
- **Solution**: Process an audio file first (File → Open Audio or Ctrl+O)

### "Unicode characters not showing"
- **Cause**: Wrong encoding in text editor
- **Solution**: Open with UTF-8 encoding (most modern editors default to this)

### "JSON file too large"
- **Cause**: Very long audio files create large JSON
- **Solution**: Normal for long calls; use compression (zip) for storage

---

## File Size Guide

| Audio Length | JSON Size | TXT Size |
|--------------|-----------|----------|
| 5 minutes | ~50 KB | ~10 KB |
| 15 minutes | ~150 KB | ~30 KB |
| 30 minutes | ~300 KB | ~60 KB |
| 1 hour | ~600 KB | ~120 KB |

*Sizes are approximate and depend on speech density and language*

---

## Summary

**JSON Export**:
- Complete audit data
- Machine-readable
- Best for integration and analysis

**TXT Export**:
- Human-readable transcript
- Simple text format
- Best for review and coaching

**Both formats**:
- UTF-8 encoding (all languages supported)
- Automatic error handling
- Auto-create directories
- Auto-add file extensions

---

For more information, see:
- [Scoring Parameters Guide](SCORING_GUIDE.md)
- [Changes - PDF Removal](CHANGES_PDF_REMOVAL.md)
