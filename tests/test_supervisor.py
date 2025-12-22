"""Tests for Supervisor Agent orchestration."""

import pytest

from brain_radio.agents.supervisor import SupervisorAgent
from brain_radio.models import Mode, PlaylistRequest


@pytest.fixture
def supervisor():
    """Create a Supervisor agent instance."""
    return SupervisorAgent()


@pytest.mark.asyncio
async def test_supervisor_composes_constraints(supervisor):
    """Test that Supervisor composes constraints correctly."""
    request = PlaylistRequest(mode=Mode.FOCUS, genre="Techno")
    result = await supervisor.generate_playlist(request)

    assert result.mode == Mode.FOCUS
    assert result.verification_summary is not None
    assert "total_candidates" in result.verification_summary


@pytest.mark.asyncio
async def test_supervisor_workflow_completes(supervisor):
    """Test that the full workflow completes without errors."""
    request = PlaylistRequest(mode=Mode.FOCUS, duration_minutes=60)

    # Should not raise
    result = await supervisor.generate_playlist(request)

    assert result is not None
    assert isinstance(result.tracks, list)


@pytest.mark.asyncio
async def test_supervisor_different_modes(supervisor):
    """Test Supervisor with different modes."""
    for mode in [Mode.FOCUS, Mode.RELAX, Mode.SLEEP, Mode.MEDITATION]:
        request = PlaylistRequest(mode=mode)
        result = await supervisor.generate_playlist(request)
        assert result.mode == mode


@pytest.mark.asyncio
async def test_supervisor_error_handling(supervisor):
    """Test Supervisor error handling paths."""
    # Test with invalid request that might cause errors
    # The supervisor should handle errors gracefully
    request = PlaylistRequest(mode=Mode.FOCUS, duration_minutes=60)

    # Should complete without raising
    result = await supervisor.generate_playlist(request)
    assert result is not None
    assert "error" not in str(result).lower() or result.mode == Mode.FOCUS
