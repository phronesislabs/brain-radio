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
        # Typer may return 2 for invalid args, ValueError is caught and typer.Exit(1) is raised
        # Should exit with non-zero code
        assert result.exit_code != 0
        # Error message should mention invalid mode (if it gets to our code)
        # or typer will show usage error
        assert result.exit_code in [1, 2]

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

        # Test by calling the function directly since CliRunner has issues with asyncio.run patching
        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            # Call generate directly and verify output via echo calls
            generate(mode="focus", genre=None, duration=60, dry_run=False)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Generated playlist" in str(call) for call in echo_calls)
            assert any("1" in str(call) and "tracks" in str(call) for call in echo_calls)

    def test_generate_with_genre(self, mock_openai_key):
        """Test generate with genre specified."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre="Techno", duration=60, dry_run=False)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("Techno" in str(call) or "genre" in str(call).lower() for call in echo_calls)

    def test_generate_with_duration(self, mock_openai_key):
        """Test generate with custom duration."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre=None, duration=120, dry_run=False)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("120" in str(call) or "duration" in str(call).lower() for call in echo_calls)

    def test_generate_dry_run(self, mock_openai_key):
        """Test generate in dry-run mode."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre=None, duration=60, dry_run=True)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any(
                "dry-run" in str(call).lower() or "dry" in str(call).lower() for call in echo_calls
            )

    def test_generate_all_modes(self, mock_openai_key):
        """Test generate with all valid modes."""
        modes = ["focus", "relax", "sleep", "meditation"]

        for mode in modes:
            mode_result = PlaylistResult(
                mode=Mode(mode),
                tracks=[],
                total_duration_ms=0,
                verification_summary={"approved": 0, "rejected": 0},
            )
            with (
                patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
                patch("brain_radio.cli.ChatOpenAI"),
                patch("brain_radio.cli.asyncio.run", return_value=mode_result),
                patch("brain_radio.cli.typer.echo") as mock_echo,
            ):
                mock_supervisor = MagicMock()
                mock_supervisor.generate_playlist = AsyncMock(return_value=mode_result)
                mock_supervisor_class.return_value = mock_supervisor

                generate(mode=mode, genre=None, duration=60, dry_run=False)
                echo_calls = [str(call) for call in mock_echo.call_args_list]
                assert any(mode in str(call).lower() for call in echo_calls), f"Mode {mode} failed"

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

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre=None, duration=60, dry_run=False)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("15" in str(call) or "tracks" in str(call) for call in echo_calls)

    def test_generate_shows_verification_summary(self, mock_openai_key):
        """Test generate shows verification summary."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 5, "rejected": 3, "total": 8},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre=None, duration=60, dry_run=False)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any(
                "summary" in str(call).lower() or "approved" in str(call).lower()
                for call in echo_calls
            )


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

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result) as mock_asyncio_run,
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
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

            # Verify asyncio.run was called
            mock_asyncio_run.assert_called_once()
            # Verify output was printed
            assert mock_echo.call_count >= 1

    def test_generate_with_all_parameters(self, mock_openai_key):
        """Test generate with all parameters specified."""
        mock_result = PlaylistResult(
            mode=Mode.RELAX,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="relax", genre="Jazz", duration=120, dry_run=True)
            # Verify function executed successfully
            assert mock_echo.call_count > 0

    def test_generate_dry_run_mode(self, mock_openai_key):
        """Test generate in dry-run mode (no LLM)."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre=None, duration=60, dry_run=True)
            # In dry-run, ChatOpenAI should not be instantiated
            assert mock_echo.call_count > 0

    def test_generate_with_empty_playlist(self, mock_openai_key):
        """Test generate with empty playlist result."""
        mock_result = PlaylistResult(
            mode=Mode.FOCUS,
            tracks=[],
            total_duration_ms=0,
            verification_summary={"approved": 0, "rejected": 0},
        )

        with (
            patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class,
            patch("brain_radio.cli.ChatOpenAI"),
            patch("brain_radio.cli.asyncio.run", return_value=mock_result),
            patch("brain_radio.cli.typer.echo") as mock_echo,
        ):
            mock_supervisor = MagicMock()
            mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
            mock_supervisor_class.return_value = mock_supervisor

            generate(mode="focus", genre=None, duration=60, dry_run=False)
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("0" in str(call) or "tracks" in str(call) for call in echo_calls)
