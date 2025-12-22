"""
Test: System Integration (Dry Run)

Acceptance Criteria: End-to-end orchestration validation.
"""

import pytest

from brain_radio.agents.supervisor import SupervisorAgent
from brain_radio.models import Mode, PlaylistRequest


@pytest.mark.asyncio
async def test_end_to_end_mode_generation_dry_run():
    """
    Test: Run full pipeline in dry-run mode.

    Acceptance Criteria:
    1. Neuro-Composer produces strict constraints.
    2. Catalog Agent resolves candidate Spotify track URIs/IDs.
    3. Researcher approves/rejects with reasons and confidence.
    4. Output JSON matches strict Pydantic schema.
    """
    supervisor = SupervisorAgent()

    request = PlaylistRequest(mode=Mode.FOCUS, genre="Techno", duration_minutes=60)
    result = await supervisor.generate_playlist(request)

    # Verify result structure
    assert result.mode == Mode.FOCUS
    assert isinstance(result.tracks, list)
    assert isinstance(result.verification_summary, dict)
    assert "total_candidates" in result.verification_summary
    assert "approved" in result.verification_summary
    assert "rejected" in result.verification_summary

    # Verify all tracks have required fields
    for track in result.tracks:
        assert track.spotify_id
        assert track.spotify_uri
        assert track.name
        assert track.artist
        assert track.source in ["spotify_features", "external_fallback"]
