"""Direct tests for CLI to increase coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from brain_radio.cli import generate
from brain_radio.models import Mode, PlaylistResult, TrackMetadata


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Set a mock OpenAI API key in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")


@pytest.mark.asyncio
async def test_generate_function_directly(mock_openai_key):
    """Test generate function called directly to cover lines 42-74."""
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
            for i in range(12)  # More than 10 to test line 74
        ],
        total_duration_ms=180000,
        verification_summary={"approved": 12, "rejected": 0},
    )

    with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
        "brain_radio.cli.ChatOpenAI"
    ), patch("brain_radio.cli.typer.echo") as mock_echo, patch(
        "brain_radio.cli.asyncio.run"
    ) as mock_asyncio_run:
        mock_supervisor = MagicMock()
        mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
        mock_supervisor_class.return_value = mock_supervisor
        mock_asyncio_run.return_value = mock_result

        # Call generate directly
        generate(
            mode="focus",
            genre="Techno",  # Test line 50
            duration=60,
            dry_run=False,
        )

        # Verify genre was echoed (line 50)
        echo_calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Techno" in str(call) for call in echo_calls)

        # Verify tracks were listed (lines 63-74)
        assert any("Track" in str(call) for call in echo_calls)
        assert any("more" in str(call).lower() for call in echo_calls)  # Line 74


def test_generate_with_dry_run_directly(mock_openai_key):
    """Test generate with dry_run to cover line 53."""
    mock_result = PlaylistResult(
        mode=Mode.FOCUS,
        tracks=[],
        total_duration_ms=0,
        verification_summary={"approved": 0, "rejected": 0},
    )

    with patch("brain_radio.cli.SupervisorAgent") as mock_supervisor_class, patch(
        "brain_radio.cli.typer.echo"
    ) as mock_echo, patch("brain_radio.cli.asyncio.run") as mock_asyncio_run:
        mock_supervisor = MagicMock()
        mock_supervisor.generate_playlist = AsyncMock(return_value=mock_result)
        mock_supervisor_class.return_value = mock_supervisor
        mock_asyncio_run.return_value = mock_result

        generate(mode="focus", genre=None, duration=60, dry_run=True)

        # Verify dry-run was echoed (line 53)
        echo_calls = [str(call) for call in mock_echo.call_args_list]
        assert any("dry-run" in str(call).lower() for call in echo_calls)


def test_generate_value_error_directly(mock_openai_key):
    """Test ValueError handling directly (lines 42-44)."""
    with patch("brain_radio.cli.typer.echo") as mock_echo, patch(
        "brain_radio.cli.typer.Exit"
    ) as mock_exit:
        mock_exit.side_effect = SystemExit(1)

        try:
            generate(mode="invalid_mode_xyz", genre=None, duration=60, dry_run=False)
            assert False, "Should have raised SystemExit"
        except SystemExit:
            pass  # Expected

        # Verify error was echoed
        echo_calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Invalid mode" in str(call) for call in echo_calls)

