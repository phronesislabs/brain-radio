"""Tests for YouTube transcript retrieval script."""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from youtube_transcript import (
    extract_video_id,
    format_transcript,
    get_transcript,
    save_transcript,
)


class TestExtractVideoId:
    """Tests for extract_video_id function."""

    def test_standard_watch_url(self):
        """Test extraction from standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_youtube_url(self):
        """Test extraction from youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        """Test extraction from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_mobile_url(self):
        """Test extraction from mobile YouTube URL."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_additional_params(self):
        """Test extraction from URL with additional query parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_v_in_query_but_different_path(self):
        """Test extraction from URL with v= in query but different path."""
        url = "https://www.youtube.com/something?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_v_path_format(self):
        """Test extraction from /v/ path format."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_v_path_format_with_params(self):
        """Test extraction from /v/ path format with query params."""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ?t=42"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_just_video_id(self):
        """Test that video ID alone is returned as-is."""
        video_id = "dQw4w9WgXcQ"
        assert extract_video_id(video_id) == "dQw4w9WgXcQ"

    def test_invalid_url_raises_value_error(self):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract video ID"):
            extract_video_id("https://example.com/video")


class TestGetTranscript:
    """Tests for get_transcript function."""

    @patch("youtube_transcript.YouTubeTranscriptApi")
    def test_get_transcript_success(self, mock_api_class):
        """Test successful transcript retrieval."""
        # Mock transcript list and transcript
        mock_transcript = Mock()
        mock_transcript.fetch.return_value = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "world", "start": 1.0, "duration": 1.0},
        ]

        mock_transcript_list = Mock()
        mock_transcript_list.find_transcript.return_value = mock_transcript
        mock_api_class.list_transcripts.return_value = mock_transcript_list

        result = get_transcript("dQw4w9WgXcQ", languages=["en"])

        assert len(result) == 2
        assert result[0]["text"] == "Hello"
        assert result[1]["text"] == "world"
        mock_transcript.fetch.assert_called_once()

    @patch("youtube_transcript.YouTubeTranscriptApi")
    def test_get_transcript_fallback_to_generated(self, mock_api_class):
        """Test fallback to auto-generated transcript when preferred language not available."""
        from youtube_transcript_api._errors import NoTranscriptFound

        mock_transcript = Mock()
        mock_transcript.fetch.return_value = [{"text": "Test", "start": 0.0, "duration": 1.0}]

        mock_transcript_list = Mock()
        # First language fails - create exception with required args (video_id, requested_language_codes, transcript_data)
        exception = NoTranscriptFound("dQw4w9WgXcQ", ["en"], mock_transcript_list)
        mock_transcript_list.find_transcript.side_effect = exception
        # Fallback to generated works
        mock_transcript_list.find_generated_transcript.return_value = mock_transcript
        mock_api_class.list_transcripts.return_value = mock_transcript_list

        result = get_transcript("dQw4w9WgXcQ", languages=["en"])

        assert len(result) == 1
        assert result[0]["text"] == "Test"

    @patch("youtube_transcript.YouTubeTranscriptApi")
    def test_get_transcript_video_unavailable(self, mock_api_class):
        """Test handling of unavailable video."""
        from youtube_transcript_api._errors import VideoUnavailable

        mock_api_class.list_transcripts.side_effect = VideoUnavailable("dQw4w9WgXcQ")

        with pytest.raises(VideoUnavailable):
            get_transcript("dQw4w9WgXcQ")

    @patch("youtube_transcript.YouTubeTranscriptApi")
    def test_get_transcript_disabled(self, mock_api_class):
        """Test handling of disabled transcripts."""
        from youtube_transcript_api._errors import TranscriptsDisabled

        mock_api_class.list_transcripts.side_effect = TranscriptsDisabled("dQw4w9WgXcQ")

        with pytest.raises(TranscriptsDisabled):
            get_transcript("dQw4w9WgXcQ")

    @patch("youtube_transcript.YouTubeTranscriptApi")
    def test_get_transcript_fallback_to_any_available(self, mock_api_class):
        """Test fallback to any available transcript when all else fails."""
        from youtube_transcript_api._errors import NoTranscriptFound

        mock_transcript = Mock()
        mock_transcript.fetch.return_value = [
            {"text": "Any transcript", "start": 0.0, "duration": 1.0}
        ]

        mock_transcript_list = Mock()
        # All language attempts fail
        mock_transcript_list.find_transcript.side_effect = NoTranscriptFound(
            "dQw4w9WgXcQ", ["en"], mock_transcript_list
        )
        # Generated transcript also fails
        mock_transcript_list.find_generated_transcript.side_effect = NoTranscriptFound(
            "dQw4w9WgXcQ", ["en"], mock_transcript_list
        )
        # But list() returns available transcripts
        mock_transcript_list.__iter__ = Mock(return_value=iter([mock_transcript]))
        mock_api_class.list_transcripts.return_value = mock_transcript_list

        result = get_transcript("dQw4w9WgXcQ", languages=["en"])

        assert len(result) == 1
        assert result[0]["text"] == "Any transcript"

    @patch("youtube_transcript.YouTubeTranscriptApi")
    def test_get_transcript_no_transcript_found_raises(self, mock_api_class):
        """Test that NoTranscriptFound is raised when no transcript available."""
        from youtube_transcript_api._errors import NoTranscriptFound

        mock_transcript_list = Mock()
        # All language attempts fail
        mock_transcript_list.find_transcript.side_effect = NoTranscriptFound(
            "dQw4w9WgXcQ", ["en"], mock_transcript_list
        )
        # Generated transcript also fails
        mock_transcript_list.find_generated_transcript.side_effect = NoTranscriptFound(
            "dQw4w9WgXcQ", ["en"], mock_transcript_list
        )
        # And no transcripts available
        mock_transcript_list.__iter__ = Mock(return_value=iter([]))
        # Mock list_transcripts to return the same list for error context
        mock_api_class.list_transcripts.return_value = mock_transcript_list

        with pytest.raises(NoTranscriptFound):
            get_transcript("dQw4w9WgXcQ", languages=["en"])


class TestFormatTranscript:
    """Tests for format_transcript function."""

    def test_format_text(self):
        """Test text format output."""
        transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "world", "start": 1.0, "duration": 1.0},
        ]
        result = format_transcript(transcript, format_type="text")
        assert result == "Hello world"

    def test_format_json(self):
        """Test JSON format output."""
        transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
        ]
        result = format_transcript(transcript, format_type="json")
        parsed = json.loads(result)
        assert parsed == transcript

    def test_format_markdown(self):
        """Test markdown format output."""
        transcript = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
            {"text": "world", "start": 1.5, "duration": 1.0},
        ]
        result = format_transcript(transcript, format_type="markdown")
        assert "# YouTube Transcript" in result
        assert "[0.00s]" in result
        assert "Hello" in result
        assert "[1.50s]" in result
        assert "world" in result

    def test_format_default_text(self):
        """Test that default format is text."""
        transcript = [{"text": "Test", "start": 0.0, "duration": 1.0}]
        result = format_transcript(transcript)
        assert result == "Test"


class TestSaveTranscript:
    """Tests for save_transcript function."""

    def test_save_transcript_creates_file(self, tmp_path):
        """Test that save_transcript creates file with content."""
        output_file = tmp_path / "transcript.txt"
        content = "Test transcript content"

        save_transcript(content, output_file)

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == content

    def test_save_transcript_creates_parent_dirs(self, tmp_path):
        """Test that save_transcript creates parent directories if needed."""
        output_file = tmp_path / "nested" / "dir" / "transcript.txt"
        content = "Test content"

        save_transcript(content, output_file)

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == content


class TestMainCLI:
    """Tests for main CLI function."""

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "https://youtube.com/watch?v=test"])
    def test_main_success(self, mock_extract, mock_get_transcript, capsys):
        """Test successful main execution."""
        from youtube_transcript import main

        mock_extract.return_value = "test_id"
        mock_get_transcript.return_value = [
            {"text": "Hello", "start": 0.0, "duration": 1.0},
        ]

        result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "Hello" in captured.out

    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "invalid-url"])
    def test_main_invalid_url(self, mock_extract, capsys):
        """Test main with invalid URL."""
        from youtube_transcript import main

        mock_extract.side_effect = ValueError("Invalid URL")

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "https://youtube.com/watch?v=test"])
    def test_main_generate_rules_flag(self, mock_extract, mock_get_transcript, capsys):
        """Test main with --generate-rules flag."""
        from youtube_transcript import main

        mock_extract.return_value = "test_id"
        mock_get_transcript.return_value = [{"text": "Test", "start": 0.0, "duration": 1.0}]

        # Mock sys.argv with --generate-rules
        with patch("sys.argv", ["youtube_transcript.py", "test", "--generate-rules"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        # Check for rule generation markers in stderr
        assert "CURSOR_RULE_GENERATION_REQUEST" in captured.err
        assert "TRANSCRIPT_START" in captured.err
        assert "TRANSCRIPT_END" in captured.err

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "test"])
    def test_main_video_unavailable_error(self, mock_extract, mock_get_transcript, capsys):
        """Test main with VideoUnavailable error."""
        from youtube_transcript import main
        from youtube_transcript_api._errors import VideoUnavailable

        mock_extract.return_value = "test_id"
        mock_get_transcript.side_effect = VideoUnavailable("test_id")

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "unavailable" in captured.err.lower()

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "test"])
    def test_main_transcripts_disabled_error(self, mock_extract, mock_get_transcript, capsys):
        """Test main with TranscriptsDisabled error."""
        from youtube_transcript import main
        from youtube_transcript_api._errors import TranscriptsDisabled

        mock_extract.return_value = "test_id"
        mock_get_transcript.side_effect = TranscriptsDisabled("test_id")

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "disabled" in captured.err.lower()

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "test", "--languages", "fr", "de"])
    def test_main_no_transcript_found_error(self, mock_extract, mock_get_transcript, capsys):
        """Test main with NoTranscriptFound error."""
        from youtube_transcript import main
        from youtube_transcript_api._errors import NoTranscriptFound

        mock_extract.return_value = "test_id"
        mock_transcript_list = Mock()
        mock_get_transcript.side_effect = NoTranscriptFound(
            "test_id", ["fr", "de"], mock_transcript_list
        )

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "No transcript found" in captured.err

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("sys.argv", ["youtube_transcript.py", "test"])
    def test_main_unexpected_error(self, mock_extract, mock_get_transcript, capsys):
        """Test main with unexpected error."""
        from youtube_transcript import main

        mock_extract.return_value = "test_id"
        mock_get_transcript.side_effect = RuntimeError("Unexpected error")

        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err

    @patch("youtube_transcript.get_transcript")
    @patch("youtube_transcript.extract_video_id")
    @patch("youtube_transcript.format_transcript")
    @patch("youtube_transcript.save_transcript")
    @patch("sys.argv", ["youtube_transcript.py", "test", "--output", "test.txt"])
    def test_main_with_output_file(
        self, mock_save, mock_format, mock_extract, mock_get_transcript, capsys
    ):
        """Test main with output file specified."""
        from youtube_transcript import main

        mock_extract.return_value = "test_id"
        mock_get_transcript.return_value = [{"text": "Test", "start": 0.0, "duration": 1.0}]
        mock_format.return_value = "Test transcript"

        result = main()

        assert result == 0
        mock_save.assert_called_once_with("Test transcript", "test.txt")

    @patch("sys.argv", ["youtube_transcript.py", "test", "--propose-only"])
    def test_main_propose_only_without_generate_rules(self, capsys):
        """Test that --propose-only without --generate-rules raises parser error."""
        from youtube_transcript import main

        # argparse.error() calls sys.exit(2), so we need to catch SystemExit
        with pytest.raises(SystemExit) as exc_info:
            main()

        # argparse.error exits with code 2
        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "--propose-only requires --generate-rules" in captured.err
