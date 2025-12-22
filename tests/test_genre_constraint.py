"""
Test: The "Vibe" Alignment

Goal: Ensure user taste is respected.
"""

from brain_radio.agents.neuro_composer import NeuroComposerAgent
from brain_radio.models import Mode


def test_genre_constraint():
    """
    Test: User requests "Focus" but specifies "Genre: Jazz".

    Acceptance Criteria: Resulting playlist must contain tracks that are BOTH
    Jazz AND comply with Focus rules (Instrumental, steady rhythm).
    """
    composer = NeuroComposerAgent()
    constraints = composer.compose_constraints(Mode.FOCUS, genre="Jazz")

    # Verify genre is set
    assert "Jazz" in constraints.genres

    # Verify Focus rules are still enforced
    assert constraints.no_vocals is True
    assert constraints.tempo_min == 120.0
    assert constraints.tempo_max == 140.0

    # Should NOT return high-energy Techno (default genre)
    assert "Techno" not in constraints.genres
