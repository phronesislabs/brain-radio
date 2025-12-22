"""Tests for Brain-Radio CLI interface."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from brain_radio.cli import app, generate
from brain_radio.models import Mode, PlaylistResult, TrackMetadata

runner = CliRunner()


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Set a mock OpenAI API key in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")


class TestCLIGenerate:
    """Tests for CLI generate command."""

    def test_generate_invalid_mode(self):
        """Test generate with invalid mode."""
        result = runner.invoke(app, ["generate", "--mode", "invalid"])
        assert result.exit_code != 0  # Typer returns 2 for invalid args
        assert "Invalid mode" in result.stdout or "invalid" in result.stdout.lower()

    def test_generate_valid_mode_default(self, mock_openai_key):
        """Test generate with valid mode (default focus)."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[
                TrackMetadata(
                    spotify_id="test1",
                    spotify_uri="spotify:track:test1",
                    name="Test Track",
                    artist="Test Artist",
                    bpm=130.0,
                    source="spotify_features",
                )
            ],
            total_duration_ms=180000,
            verification_summary={"approved": 1, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate"])
            assert result.exit_code == 0
            assert "Generated playlist" in result.stdout
            assert "1 tracks" in result.stdout

    def test_generate_with_genre(self, mock_openai_key):
        """Test generate with genre specified."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate", "--mode", "focus", "--genre", "Techno"])
            assert result.exit_code == 0
            assert "Genre preference: Techno" in result.stdout

    def test_generate_with_duration(self, mock_openai_key):
        """Test generate with custom duration."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate", "--duration", "120"])
            assert result.exit_code == 0
            assert "Target duration: 120 minutes" in result.stdout

    def test_generate_dry_run(self, mock_openai_key):
        """Test generate in dry-run mode."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate", "--dry-run"])
            assert result.exit_code == 0
            assert "dry-run mode" in result.stdout

    def test_generate_all_modes(self, mock_openai_key):
        """Test generate with all valid modes."""
        modes = ["focus", "relax", "sleep", "meditation"]
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        for mode in modes:
            with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
                mock_supervisor = MagicMock()
                mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
                mock_supervisor_class.return_value = mock_supervisor

                result = runner.invoke(app, ["generate", "--mode", mode])
                assert result.exit_code == 0, f"Mode {mode} failed"
                assert mode in result.stdout.lower()

    def test_generate_with_multiple_tracks(self, mock_openai_key):
        """Test generate with multiple tracks (shows first 10)."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[
                TrackMetadata(
                    spotify_id=f"test{i}",
                    spotify_uri=f"spotify:track:test{i}",
                    name=f"Track {i}",
                    artist=f"Artist {i}",
                    bpm=130.0,
                    source="spotify_features",
                )
                for i in range(15)
            ],
            total_duration_ms=180000,
            verification_summary={"approved": 15, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate"])
            assert result.exit_code == 0
            assert "15 tracks" in result.stdout
            assert "... and 5 more" in result.stdout

    def test_generate_shows_verification_summary(self, mock_openai_key):
        """Test generate shows verification summary."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 5, "rejected": 3, "total": 8},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate"])
            assert result.exit_code == 0
            assert "Verification summary" in result.stdout
            assert "approved" in result.stdout or "5" in result.stdout


class TestCLIExecution:
    """Tests for CLI execution paths."""

    @pytest.mark.asyncio
    async def test_generate_function_direct_call(self, mock_openai_key):
        """Test generate function can be called directly."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[
                TrackMetadata(
                    spotify_id="test1",
                    spotify_uri="spotify:track:test1",
                    name="Test Track",
                    artist="Test Artist",
                    bpm=130.0,
                    source="spotify_features",
                )
            ],
            total_duration_ms=180000,
            verification_summary={"approved": 1, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ), patch("brain_radio.cli.typer.echo") as mock_echo:
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            # Call the function directly
            generate(
                mode="focus",
                genre=None,
                duration=60,
                dry_run=False,
            )

            # Verify supervisor was called
            mock_supervisor.generate_playlist.assert_called_once()
            # Verify output was printed
            assert mock_echo.call_count >= 3  # At least 3 echo calls

    def test_generate_with_all_parameters(self, mock_openai_key):
        """Test generate with all parameters specified."""
        mock_result = PlaylistResult(
            mode=Mode.RELAX,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(
                app,
                [
                    "generate",
                    "--mode",
                    "relax",
                    "--genre",
                    "Jazz",
                    "--duration",
                    "120",
                    "--dry-run",
                ],
            )
            assert result.exit_code == 0

    def test_generate_dry_run_mode(self, mock_openai_key):
        """Test generate in dry-run mode (no LLM)."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class:
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate", "--dry-run"])
            # In dry-run, ChatOpenAI should not be instantiated
            assert result.exit_code == 0
            assert "dry-run mode" in result.stdout

    def test_generate_with_empty_playlist(self, mock_openai_key):
        """Test generate with empty playlist result."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
            "brain_radio.cli.ChatOpenAI"
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            result = runner.invoke(app, ["generate"])
            assert result.exit_code == 0
            assert "0 tracks" in result.stdout

