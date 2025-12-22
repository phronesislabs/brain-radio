# YouTube Transcript Script

A modular, portable Python script for retrieving YouTube video transcripts. Can be used as a CLI tool or imported as a module.

## Installation

```bash
# Using uv (recommended)
uv pip install youtube-transcript-api

# Or using pip
pip install youtube-transcript-api
```

## Usage

### As a CLI Tool

```bash
# Basic usage
python scripts/youtube_transcript.py <youtube_url>

# Save to file
python scripts/youtube_transcript.py <youtube_url> --output transcript.txt

# Different formats
python scripts/youtube_transcript.py <youtube_url> --format json
python scripts/youtube_transcript.py <youtube_url> --format markdown

# Generate rules flag (for Cursor integration)
python scripts/youtube_transcript.py <youtube_url> --generate-rules
python scripts/youtube_transcript.py <youtube_url> --generate-rules --propose-only
```

### As a Python Module

```python
from scripts.youtube_transcript import get_transcript, extract_video_id, format_transcript

# Extract video ID from URL
video_id = extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Get transcript
transcript = get_transcript(video_id, languages=["en"])

# Format transcript
formatted = format_transcript(transcript, format_type="text")
```

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (just the ID)

## Output Formats

- **text** (default): Plain text, words joined with spaces
- **json**: JSON array with full transcript entries (text, start, duration)
- **markdown**: Markdown formatted with timestamps

## Error Handling

The script handles common errors:

- `ValueError`: Invalid URL format
- `VideoUnavailable`: Video doesn't exist or is private
- `TranscriptsDisabled`: Transcripts disabled for the video
- `NoTranscriptFound`: No transcript in requested languages

## Portability

This script is designed to be portable and can be:

- Copied to other projects
- Used as a standalone tool
- Integrated into CI/CD pipelines
- Imported in other Python scripts

The only dependency is `youtube-transcript-api`, which can be installed independently.

## Cursor Integration

When used with the `--generate-rules` flag, the script outputs special markers that Cursor agents can detect to automatically generate rules or commands from transcript content. See `.cursor/commands/youtube_transcript.md` for details.

