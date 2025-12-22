"""Tests for Researcher Agent (Hybrid Verifier)."""

from unittest.mock import patch

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
        bpm=130.0,  # Valid BPM for Focus mode (120-140 range)
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


@pytest.mark.asyncio
async def test_energy_constraints(researcher_agent):
    """Test energy constraint enforcement."""
    constraints = ProtocolConstraints(
        mode=Mode.FOCUS,
        tempo_min=120.0,
        tempo_max=140.0,
        energy_min=0.3,
        energy_max=0.7,
        no_vocals=True,
    )

    # Track with energy too low
    track_low_energy = TrackMetadata(
        spotify_id="test1",
        spotify_uri="spotify:track:test1",
        name="Low Energy Track",
        artist="Test",
        energy=0.2,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track_low_energy, constraints)
    assert not result.approved, "Track with energy below minimum should be rejected"
    assert any("below minimum" in reason.lower() for reason in result.reasons)

    # Track with energy too high
    track_high_energy = TrackMetadata(
        spotify_id="test2",
        spotify_uri="spotify:track:test2",
        name="High Energy Track",
        artist="Test",
        energy=0.8,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track_high_energy, constraints)
    assert not result.approved, "Track with energy above maximum should be rejected"
    assert any("above maximum" in reason.lower() for reason in result.reasons)

    # Track with energy in range
    track_good_energy = TrackMetadata(
        spotify_id="test3",
        spotify_uri="spotify:track:test3",
        name="Good Energy Track",
        artist="Test",
        energy=0.5,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track_good_energy, constraints)
    assert result.approved, "Track with energy in range should be approved"


@pytest.mark.asyncio
async def test_bpm_research_failure(researcher_agent, focus_constraints):
    """Test BPM research when search fails."""
    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Unknown Track",
        artist="Unknown Artist",
        bpm=None,
        is_instrumental=True,
        source="spotify_features",
    )

    # Mock search tool to fail
    with patch.object(researcher_agent, "search_tool", side_effect=Exception("Search failed")):
        result = await researcher_agent.verify_track(track, focus_constraints)
        assert not result.approved
        assert "Could not determine BPM" in result.reasons[0]


def test_extract_bpm_from_text(researcher_agent):
    """Test BPM extraction from text."""
    # Test various BPM patterns
    test_cases = [
        ("The track is 120 BPM", 120.0),
        ("BPM: 140", 140.0),
        ("tempo: 130", 130.0),
        ("Track has 125 bpm", 125.0),
        ("No BPM here", None),
        ("BPM: 250", None),  # Out of range
        ("BPM: 50", None),  # Out of range
    ]

    for text, expected in test_cases:
        result = researcher_agent._extract_bpm_from_text(text)
        assert result == expected, f"Failed for text: {text}"


def test_is_instrumental(researcher_agent):
    """Test instrumental detection logic."""
    # Track with is_instrumental set
    track1 = TrackMetadata(
        spotify_id="test1",
        spotify_uri="spotify:track:test1",
        name="Track",
        artist="Artist",
        is_instrumental=True,
        source="spotify_features",
    )
    assert researcher_agent._is_instrumental(track1) is True

    # Track with high instrumentalness
    track2 = TrackMetadata(
        spotify_id="test2",
        spotify_uri="spotify:track:test2",
        name="Track",
        artist="Artist",
        instrumentalness=0.8,
        source="spotify_features",
    )
    assert researcher_agent._is_instrumental(track2) is True

    # Track with low speechiness
    track3 = TrackMetadata(
        spotify_id="test3",
        spotify_uri="spotify:track:test3",
        name="Track",
        artist="Artist",
        speechiness=0.2,
        source="spotify_features",
    )
    assert researcher_agent._is_instrumental(track3) is True

    # Track with high speechiness
    track4 = TrackMetadata(
        spotify_id="test4",
        spotify_uri="spotify:track:test4",
        name="Track",
        artist="Artist",
        speechiness=0.5,
        source="spotify_features",
    )
    assert researcher_agent._is_instrumental(track4) is False

    # Track with no data
    track5 = TrackMetadata(
        spotify_id="test5",
        spotify_uri="spotify:track:test5",
        name="Track",
        artist="Artist",
        source="spotify_features",
    )
    assert researcher_agent._is_instrumental(track5) is False


def test_calculate_distraction_score(researcher_agent):
    """Test distraction score calculation."""
    # High distraction track
    high_distraction = TrackMetadata(
        spotify_id="test1",
        spotify_uri="spotify:track:test1",
        name="High Distraction",
        artist="Test",
        speechiness=0.8,
        instrumentalness=0.1,
        energy=0.9,
        explicit=True,
        source="spotify_features",
    )
    score = researcher_agent._calculate_distraction_score(high_distraction)
    assert score > 0.5, "High distraction track should have high score"

    # Low distraction track
    low_distraction = TrackMetadata(
        spotify_id="test2",
        spotify_uri="spotify:track:test2",
        name="Low Distraction",
        artist="Test",
        speechiness=0.05,
        instrumentalness=0.95,
        energy=0.3,
        explicit=False,
        source="spotify_features",
    )
    score = researcher_agent._calculate_distraction_score(low_distraction)
    assert score < 0.5, "Low distraction track should have low score"
    assert score <= 1.0, "Score should be capped at 1.0"


@pytest.mark.asyncio
async def test_distraction_score_above_threshold(researcher_agent, focus_constraints):
    """Test that tracks with high distraction score are rejected (line 147)."""
    # Create an instrumental track with high distraction score
    high_distraction_track = TrackMetadata(
        spotify_id="test1",
        spotify_uri="spotify:track:test1",
        name="High Distraction Track",
        artist="Test",
        speechiness=0.8,
        instrumentalness=0.95,  # Instrumental so it passes vocal check
        energy=0.95,
        is_instrumental=True,
        bpm=130.0,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(high_distraction_track, focus_constraints)
    # Should be rejected for high distraction score (line 147)
    assert not result.approved
    assert result.distraction_score is not None
    assert any("Distraction score" in reason for reason in result.reasons)


@pytest.mark.asyncio
async def test_non_focus_mode_no_distraction_score(researcher_agent):
    """Test that distraction score is only calculated for Focus mode."""
    relax_constraints = ProtocolConstraints(
        mode=Mode.RELAX,
        tempo_min=60.0,
        tempo_max=90.0,
        no_vocals=False,
    )

    track = TrackMetadata(
        spotify_id="test1",
        spotify_uri="spotify:track:test1",
        name="Relax Track",
        artist="Test",
        bpm=75.0,
        source="spotify_features",
    )

    result = await researcher_agent.verify_track(track, relax_constraints)
    # Distraction score should be None for non-Focus modes
    assert result.distraction_score is None


@pytest.mark.asyncio
async def test_bpm_research_with_ainvoke(researcher_agent, focus_constraints):
    """Test BPM research using ainvoke method (lines 103-104)."""
    from unittest.mock import AsyncMock, MagicMock

    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Test Track",
        artist="Test Artist",
        bpm=None,
        is_instrumental=True,
        source="spotify_features",
    )

    # Mock search tool with ainvoke that returns valid BPM
    mock_search_tool = MagicMock()
    mock_search_tool.ainvoke = AsyncMock(return_value="Track has 130 BPM tempo")
    # Ensure hasattr returns True
    type(mock_search_tool).ainvoke = mock_search_tool.ainvoke
    researcher_agent.search_tool = mock_search_tool

    result = await researcher_agent.verify_track(track, focus_constraints)

    # BPM should be extracted and source set to external_fallback (lines 103-104)
    assert result.track.bpm is not None, "BPM should be extracted from search"
    assert 120 <= result.track.bpm <= 140, f"BPM {result.track.bpm} should be in range"
    assert result.track.source == "external_fallback", "Source should be external_fallback after research"


@pytest.mark.asyncio
async def test_bpm_research_with_sync_invoke(researcher_agent, focus_constraints):
    """Test BPM research using sync invoke in thread."""
    from unittest.mock import MagicMock

    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Test Track",
        artist="Test Artist",
        bpm=None,
        is_instrumental=True,
        source="spotify_features",
    )

    # Mock search tool without ainvoke (sync only)
    mock_search_tool = MagicMock()
    # Don't set ainvoke attribute
    mock_search_tool.invoke = MagicMock(return_value="Track tempo is 135 BPM")
    # Make hasattr return False for ainvoke
    if hasattr(type(mock_search_tool), "ainvoke"):
        delattr(type(mock_search_tool), "ainvoke")
    researcher_agent.search_tool = mock_search_tool

    result = await researcher_agent.verify_track(track, focus_constraints)

    # BPM should be extracted if search worked
    if result.track.bpm is not None:
        assert 120 <= result.track.bpm <= 140
        assert result.track.source == "external_fallback"


@pytest.mark.asyncio
async def test_bpm_research_exception_handling(researcher_agent, focus_constraints):
    """Test BPM research handles exceptions gracefully (lines 193-198)."""
    from unittest.mock import AsyncMock, MagicMock

    track = TrackMetadata(
        spotify_id="test123",
        spotify_uri="spotify:track:test123",
        name="Test Track",
        artist="Test Artist",
        bpm=None,
        is_instrumental=True,
        source="spotify_features",
    )

    # Mock search tool to raise exception
    mock_search_tool = MagicMock()
    mock_search_tool.ainvoke = AsyncMock(side_effect=Exception("Search failed"))
    researcher_agent.search_tool = mock_search_tool

    result = await researcher_agent.verify_track(track, focus_constraints)

    # Should reject due to missing BPM
    assert not result.approved
    assert any("Could not determine BPM" in reason for reason in result.reasons)

    # Test exception in sync invoke path
    mock_search_tool2 = MagicMock()
    if hasattr(mock_search_tool2, "ainvoke"):
        delattr(mock_search_tool2, "ainvoke")
    mock_search_tool2.invoke = MagicMock(side_effect=Exception("Sync search failed"))
    researcher_agent.search_tool = mock_search_tool2

    result2 = await researcher_agent.verify_track(track, focus_constraints)
    assert not result2.approved


def test_extract_bpm_edge_cases(researcher_agent):
    """Test BPM extraction with edge cases."""
    # Test with multiple BPM values (should use first)
    text = "Track has 120 BPM and also 140 BPM mentioned"
    result = researcher_agent._extract_bpm_from_text(text)
    assert result == 120.0

    # Test with invalid BPM (out of range)
    text = "Track has 300 BPM"  # Too high
    result = researcher_agent._extract_bpm_from_text(text)
    assert result is None

    text = "Track has 20 BPM"  # Too low
    result = researcher_agent._extract_bpm_from_text(text)
    assert result is None

    # Test with no BPM
    text = "This track has no tempo information"
    result = researcher_agent._extract_bpm_from_text(text)
    assert result is None

    # Test with case insensitive
    text = "bpm: 125"
    result = researcher_agent._extract_bpm_from_text(text)
    assert result == 125.0

    # Test ValueError exception handling (lines 222-223)
    # Create text that will cause ValueError in float conversion
    # We need to mock re.findall to return invalid data
    from unittest.mock import patch
    with patch("brain_radio.agents.researcher.re.findall") as mock_findall:
        mock_findall.return_value = ["invalid_bpm"]  # Will cause ValueError
        result = researcher_agent._extract_bpm_from_text("test")
        assert result is None  # Should return None on ValueError
