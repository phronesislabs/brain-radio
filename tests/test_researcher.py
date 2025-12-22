"""Tests for the Researcher agent's hybrid verification."""

from brain_radio.agents.neuro_composer import Mode, NeuroComposer
from brain_radio.agents.researcher import (
    AudioFeatures,
    Researcher,
    SearchResult,
    TrackCandidate,
)


class FakeSearchClient:
    def __init__(self, results: list[SearchResult]) -> None:
        self._results = results

    def search(self, query: str):
        return self._results


def test_focus_protocol_rejects_vocals():
    composer = NeuroComposer()
    constraints = composer.compose(Mode.focus)
    researcher = Researcher()

    vocal_track = TrackCandidate(
        title="Bohemian Rhapsody",
        artist="Queen",
        spotify_uri="spotify:track:vocal",
        audio_features=AudioFeatures(tempo=72.0, speechiness=0.8, instrumentalness=0.1),
    )
    instrumental_track = TrackCandidate(
        title="Awake",
        artist="Tycho",
        spotify_uri="spotify:track:instrumental",
        audio_features=AudioFeatures(
            tempo=128.0, speechiness=0.05, instrumentalness=0.9
        ),
    )

    vocal_decision = researcher.verify(vocal_track, constraints)
    instrumental_decision = researcher.verify(instrumental_track, constraints)

    assert not vocal_decision.accepted
    assert any("vocals" in reason.lower() for reason in vocal_decision.reasons)
    assert instrumental_decision.accepted
    assert instrumental_decision.vocal_source == "spotify_features"


def test_bpm_retrieval_accuracy():
    search_client = FakeSearchClient(
        results=[
            SearchResult(
                title="Sandstorm - BPM 136",
                snippet="Darude classic at 136 bpm.",
            )
        ]
    )
    researcher = Researcher(search_client=search_client)
    composer = NeuroComposer()
    constraints = composer.compose(Mode.focus)

    candidate = TrackCandidate(
        title="Sandstorm",
        artist="Darude",
        spotify_uri="spotify:track:sandstorm",
        audio_features=None,
    )

    decision = researcher.verify(candidate, constraints)

    assert decision.bpm_source == "external_fallback"
    assert decision.bpm is not None
    assert 131 <= decision.bpm <= 141
