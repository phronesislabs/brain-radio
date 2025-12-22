"""Tests for Researcher Agent (Hybrid Verifier)."""

import pytest

from brain_radio.agents.researcher import ResearcherAgent
from brain_radio.models import Mode, ProtocolConstraints, TrackMetadata


@pytest.fixture
def researcher_agent():
    """Create a Researcher agent instance."""
    return ResearcherAgent()


@pytest.fixture
def focus_constraints():
    """Create Focus protocol constraints."""
    return ProtocolConstraints(
        mode=Mode.FOCUS,
        tempo_min=120.0,
        tempo_max=140.0,
        no_vocals=True,
        avoid_live=True,
        avoid_remaster=True,
        avoid_feat=True,
    )


@pytest.fixture
def vocal_track():
    """Create a track with vocals (Bohemian Rhapsody)."""
    return TrackMetadata(
        spotify_id="4u7EnebtmKWrUHhmAwpZw1",
        spotify_uri="spotify:track:4u7EnebtmKWrUHhmAwpZw1",
        name="Bohemian Rhapsody",
        artist="Queen",
        speechiness=0.3,
        instrumentalness=0.0,
        is_instrumental=False,
        source="spotify_features",
    )


@pytest.fixture
def instrumental_track():
    """Create an instrumental track (Tycho - Awake)."""
    return TrackMetadata(
        spotify_id="5YQwhbh8d1N3AlBqGyWHbG",
        spotify_uri="spotify:track:5YQwhbh8d1N3AlBqGyWHbG",
        name="Awake",
        artist="Tycho",
        speechiness=0.05,
        instrumentalness=0.95,
        is_instrumental=True,
        source="spotify_features",
    )


@pytest.mark.asyncio
async def test_focus_protocol_rejects_vocals(
    researcher_agent, focus_constraints, vocal_track, instrumental_track
):
    """
    Test: Focus protocol rejects vocal tracks and accepts instrumental tracks.

    Acceptance Criteria: The "Silence" Test
    """
    # Test vocal track rejection
    result_vocal = await researcher_agent.verify_track(vocal_track, focus_constraints)
    assert not result_vocal.approved, "Vocal track should be rejected"
    assert any("vocals" in reason.lower() for reason in result_vocal.reasons), (
        "Rejection reason should mention vocals"
    )

    # Test instrumental track acceptance
    result_instrumental = await researcher_agent.verify_track(instrumental_track, focus_constraints)
    assert result_instrumental.approved, "Instrumental track should be approved"
    assert result_instrumental.track.source in [
        "spotify_features",
        "external_fallback",
    ], "Source should be recorded"


@pytest.mark.asyncio
async def test_bpm_retrieval_accuracy(researcher_agent, focus_constraints):
    """
    Test: BPM retrieval accuracy with tolerance.

    Acceptance Criteria: The "Tempo" Check
    """
    # Create a track with known BPM (Sandstorm ~136 BPM)
    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Sandstorm",
        artist="Darude",
        bpm=None,  # Missing BPM - will trigger web research
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track, focus_constraints)

    # If BPM was found, it should be in the expected range
    if result.track.bpm is not None:
        assert 131 <= result.track.bpm <= 141, f"BPM {result.track.bpm} should be ~136 ±5"
        # Check source annotation
        if result.track.bpm != track.bpm:
            assert result.track.source == "external_fallback", (
                "Should use external_fallback when BPM is researched"
            )


@pytest.mark.asyncio
async def test_rejects_live_versions(researcher_agent, focus_constraints):
    """Test that live versions are rejected for Focus mode."""
    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Test Track (Live)",
        artist="Test Artist",
        is_live=True,
        is_instrumental=True,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track, focus_constraints)
    assert not result.approved, "Live version should be rejected"
    assert any("live" in reason.lower() for reason in result.reasons), (
        "Rejection reason should mention live version"
    )


@pytest.mark.asyncio
async def test_rejects_remaster_versions(researcher_agent, focus_constraints):
    """Test that remastered versions are rejected for Focus mode."""
    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Test Track (Remastered)",
        artist="Test Artist",
        is_remaster=True,
        is_instrumental=True,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track, focus_constraints)
    assert not result.approved, "Remastered version should be rejected"
    assert any("remaster" in reason.lower() for reason in result.reasons), (
        "Rejection reason should mention remaster"
    )


@pytest.mark.asyncio
async def test_bpm_range_enforcement(researcher_agent, focus_constraints):
    """Test that BPM outside range is rejected."""
    # Track with BPM too low
    track_low = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Slow Track",
        artist="Test Artist",
        bpm=100.0,  # Below 120 minimum
        is_instrumental=True,
        source="spotify_features",
    )

    result_low = await researcher_agent.verify_track(track_low, focus_constraints)
    assert not result_low.approved, "Track with BPM below minimum should be rejected"
    assert any("below minimum" in reason.lower() for reason in result_low.reasons), (
        "Rejection reason should mention BPM below minimum"
    )

    # Track with BPM too high
    track_high = TrackMetadata(
        spotify_id="test456",
        spotify_uri="spotify:track:test456",
        name="Fast Track",
        artist="Test Artist",
        bpm=150.0,  # Above 140 maximum
        is_instrumental=True,
        source="spotify_features",
    )

    result_high = await researcher_agent.verify_track(track_high, focus_constraints)
    assert not result_high.approved, "Track with BPM above maximum should be rejected"
    assert any("above maximum" in reason.lower() for reason in result_high.reasons), (
        "Rejection reason should mention BPM above maximum"
    )

    # Track with BPM in range
    track_good = TrackMetadata(
        spotify_id="test789",
        spotify_uri="spotify:track:test789",
        name="Good Track",
        artist="Test Artist",
        bpm=130.0,  # Within 120-140 range
        is_instrumental=True,
        source="spotify_features",
    )

    result_good = await researcher_agent.verify_track(track_good, focus_constraints)
    assert result_good.approved, "Track with BPM in range should be approved"
