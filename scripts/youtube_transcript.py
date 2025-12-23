#!/usr/bin/env python3
"""
YouTube Transcript Retrieval Script

A modular script to retrieve full transcripts from YouTube videos.
Can be used as a CLI tool or imported as a module in other scripts.

Usage:
    python youtube_transcript.py <youtube_url> [--generate-rules] [--output OUTPUT]
    python youtube_transcript.py <youtube_url> --generate-rules --propose-only
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )
except ImportError:
    print(
        "Error: youtube-transcript-api not installed. "
        "Install with: uv pip install youtube-transcript-api",
        file=sys.stderr,
    )
    sys.exit(1)


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - VIDEO_ID (if already just an ID)

    Args:
        url: YouTube URL or video ID

    Returns:
        Video ID string

    Raises:
        ValueError: If video ID cannot be extracted
    """
    # If it's already just an ID (no URL structure)
    if len(url) == 11 and url.replace("-", "").replace("_", "").isalnum():
        return url

    parsed = urlparse(url)
    video_id = None

    # Standard watch URL: ?v=VIDEO_ID
    if parsed.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            query_params = parse_qs(parsed.query)
            video_id = query_params.get("v", [None])[0]
        # Short URL: /watch?v=VIDEO_ID (path might be different)
        elif "v=" in parsed.query:
            query_params = parse_qs(parsed.query)
            video_id = query_params.get("v", [None])[0]
        # Embed URL: /embed/VIDEO_ID
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[1].split("?")[0]
        # Short URL format: /v/VIDEO_ID
        elif parsed.path.startswith("/v/"):
            video_id = parsed.path.split("/v/")[1].split("?")[0]

    # youtu.be short URL: https://youtu.be/VIDEO_ID
    elif parsed.netloc in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/").split("?")[0]

    if not video_id:
        raise ValueError(
            f"Could not extract video ID from URL: {url}\n"
            "Supported formats: https://www.youtube.com/watch?v=VIDEO_ID, "
            "https://youtu.be/VIDEO_ID, or just VIDEO_ID"
        )

    return video_id


def get_transcript(video_id: str, languages: list[str] | None = None) -> list[dict[str, Any]]:
    """
    Retrieve transcript for a YouTube video.

    Args:
        video_id: YouTube video ID
        languages: Preferred language codes (e.g., ['en', 'en-US']). If None, tries auto-generated.

    Returns:
        List of transcript entries, each with 'text', 'start', and 'duration' keys

    Raises:
        VideoUnavailable: If video doesn't exist or is unavailable
        TranscriptsDisabled: If transcripts are disabled for this video
        NoTranscriptFound: If no transcript found in requested languages
    """
    if languages is None:
        languages = ["en", "en-US", "en-GB"]

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None

        # Try to get transcript in preferred languages
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except NoTranscriptFound:
                continue

        # If no preferred language found, try auto-generated
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(["en"])
            except NoTranscriptFound:
                # Try any available transcript
                available = list(transcript_list)
                if available:
                    transcript = available[0]
                else:
                    # Re-fetch transcript list for error context
                    transcript_list_for_error = YouTubeTranscriptApi.list_transcripts(video_id)
                    raise NoTranscriptFound(video_id, languages, transcript_list_for_error)

        return transcript.fetch()

    except VideoUnavailable:
        raise
    except TranscriptsDisabled:
        raise
    except NoTranscriptFound:
        raise


def format_transcript(transcript: list[dict[str, Any]], format_type: str = "text") -> str:
    """
    Format transcript in different output formats.

    Args:
        transcript: List of transcript entries
        format_type: Output format - 'text', 'json', or 'markdown'

    Returns:
        Formatted transcript string
    """
    if format_type == "json":
        return json.dumps(transcript, indent=2)

    if format_type == "markdown":
        lines = ["# YouTube Transcript\n"]
        for entry in transcript:
            timestamp = f"{entry['start']:.2f}"
            lines.append(f"**[{timestamp}s]** {entry['text']}\n")
        return "".join(lines)

    # Default: plain text
    lines = []
    for entry in transcript:
        lines.append(entry["text"])
    return " ".join(lines)


def save_transcript(transcript_text: str, output_path: str | Path) -> None:
    """
    Save transcript to file.

    Args:
        transcript_text: Formatted transcript text
        output_path: Path to output file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(transcript_text, encoding="utf-8")
    print(f"Transcript saved to: {output_path}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Retrieve YouTube video transcripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python youtube_transcript.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
  python youtube_transcript.py dQw4w9WgXcQ --output transcript.txt
  python youtube_transcript.py https://youtu.be/dQw4w9WgXcQ --format json
  python youtube_transcript.py <url> --generate-rules
  python youtube_transcript.py <url> --generate-rules --propose-only
        """,
    )
    parser.add_argument(
        "url",
        help="YouTube URL or video ID",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: print to stdout)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--languages",
        "-l",
        nargs="+",
        default=["en", "en-US", "en-GB"],
        help="Preferred language codes (default: en en-US en-GB)",
    )
    parser.add_argument(
        "--generate-rules",
        action="store_true",
        help="Generate Cursor rules/commands from transcript (requires AI agent)",
    )
    parser.add_argument(
        "--propose-only",
        action="store_true",
        help="Only propose rules/commands, don't write them (requires --generate-rules)",
    )

    args = parser.parse_args()

    # Validate propose-only requires generate-rules
    if args.propose_only and not args.generate_rules:
        parser.error("--propose-only requires --generate-rules")

    try:
        # Extract video ID
        video_id = extract_video_id(args.url)
        print(f"Video ID: {video_id}", file=sys.stderr)

        # Get transcript
        print("Fetching transcript...", file=sys.stderr)
        transcript = get_transcript(video_id, args.languages)

        # Format transcript
        transcript_text = format_transcript(transcript, args.format)

        # Save or print
        if args.output:
            save_transcript(transcript_text, args.output)
        else:
            print(transcript_text)

        # Handle rule generation flag
        if args.generate_rules:
            # Output a special marker that the Cursor agent can detect
            # The agent will then process the transcript and propose rules
            print(
                "\n---CURSOR_RULE_GENERATION_REQUEST---",
                file=sys.stderr,
            )
            print(
                json.dumps(
                    {
                        "action": "generate_rules",
                        "propose_only": args.propose_only,
                        "transcript_length": len(transcript),
                        "video_id": video_id,
                    }
                ),
                file=sys.stderr,
            )
            # Also output the transcript in a structured way for the agent
            print("\n---TRANSCRIPT_START---", file=sys.stderr)
            print(transcript_text, file=sys.stderr)
            print("---TRANSCRIPT_END---", file=sys.stderr)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except VideoUnavailable:
        print(f"Error: Video {args.url} is unavailable or doesn't exist", file=sys.stderr)
        return 1
    except TranscriptsDisabled:
        print(f"Error: Transcripts are disabled for video {args.url}", file=sys.stderr)
        return 1
    except NoTranscriptFound:
        print(
            f"Error: No transcript found for video {args.url} in languages: {args.languages}",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
