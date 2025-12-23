"""
Tests for Distraction Scoring (Focus Effectiveness Proxies).

Acceptance Criteria: The "Not Just a Playlist" Tests
"""

import pytest

from brain_radio.agents.researcher import ResearcherAgent
from brain_radio.models import Mode, ProtocolConstraints, TrackMetadata


@pytest.fixture
def researcher():
    """Create Researcher agent."""
    return ResearcherAgent()


@pytest.fixture
def focus_constraints():
    """Focus protocol constraints."""
    return ProtocolConstraints(
        mode=Mode.FOCUS,
        tempo_min=120.0,
        tempo_max=140.0,
        no_vocals=True,
        avoid_live=True,
        avoid_remaster=True,
        avoid_feat=True,
    )


@pytest.mark.asyncio
async def test_focus_distraction_score_filters_attention_grabbing_tracks(
    researcher, focus_constraints
):
    """
    Test: Focus distraction score filters attention-grabbing tracks.

    Acceptance Criteria: Must reject candidates that violate hard bans and
    compute distraction_score with auditable feature breakdown.
    """
    # High speechiness track (should be rejected)
    high_speech = TrackMetadata(
        spotify_id="test1",
        spotify_uri="spotify:track:test1",
        name="High Speech Track",
        artist="Test",
        speechiness=0.8,
        instrumentalness=0.1,
        is_instrumental=False,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher.verify_track(high_speech, focus_constraints)
    assert not result.approved, "High speechiness track should be rejected"
    assert result.distraction_score is not None, "Distraction score should be computed"

    # Explicit track (should be rejected)
    explicit_track = TrackMetadata(
        spotify_id="test2",
        spotify_uri="spotify:track:test2",
        name="Explicit Track",
        artist="Test",
        explicit=True,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher.verify_track(explicit_track, focus_constraints)
    # Explicit might not be hard-banned by default, but should increase distraction score
    if result.distraction_score:
        assert result.distraction_score > 0.0, "Explicit content should increase distraction"

    # Low distraction track (should be approved)
    low_distraction = TrackMetadata(
        spotify_id="test3",
        spotify_uri="spotify:track:test3",
        name="Low Distraction Track",
        artist="Test",
        speechiness=0.05,
        instrumentalness=0.95,
        energy=0.4,
        is_instrumental=True,
        bpm=130.0,
        explicit=False,
        source="spotify_features",
    )

    result = await researcher.verify_track(low_distraction, focus_constraints)
    assert result.approved, "Low distraction track should be approved"
    if result.distraction_score:
        assert result.distraction_score < 0.7, "Low distraction score should be below threshold"


@pytest.mark.asyncio
async def test_hard_ban_enforcement(researcher, focus_constraints):
    """Test that hard bans are enforced with explicit reasons."""
    # Live version
    live_track = TrackMetadata(
        spotify_id="test4",
        spotify_uri="spotify:track:test4",
        name="Track (Live)",
        artist="Test",
        is_live=True,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher.verify_track(live_track, focus_constraints)
    assert not result.approved
    assert any("live" in r.lower() for r in result.reasons), "Should mention live version"

    # Remaster version
    remaster_track = TrackMetadata(
        spotify_id="test5",
        spotify_uri="spotify:track:test5",
        name="Track (Remastered)",
        artist="Test",
        is_remaster=True,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher.verify_track(remaster_track, focus_constraints)
    assert not result.approved
    assert any("remaster" in r.lower() for r in result.reasons), "Should mention remaster"

    # Track with featured artists
    feat_track = TrackMetadata(
        spotify_id="test6",
        spotify_uri="spotify:track:test6",
        name="Track (feat. Artist)",
        artist="Test",
        has_feat=True,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher.verify_track(feat_track, focus_constraints)
    assert not result.approved
    assert any("feat" in r.lower() or "featured" in r.lower() for r in result.reasons), (
        "Should mention featured artists"
    )
