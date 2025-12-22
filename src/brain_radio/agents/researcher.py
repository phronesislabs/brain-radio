"""Researcher agent: hybrid verifier for tempo and vocal content."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

from pydantic import BaseModel, Field

from brain_radio.agents.neuro_composer import ProtocolConstraints


class AudioFeatures(BaseModel):
    """Subset of audio features relevant to protocol checks."""

    tempo: Optional[float] = Field(default=None, description="Tempo in BPM.")
    speechiness: Optional[float] = Field(
        default=None, description="Speechiness estimate (0-1)."
    )
    instrumentalness: Optional[float] = Field(
        default=None, description="Instrumentalness estimate (0-1)."
    )


class TrackCandidate(BaseModel):
    """Track metadata input to the researcher."""

    title: str
    artist: str
    spotify_uri: str
    audio_features: Optional[AudioFeatures] = None


@dataclass(frozen=True)
class SearchResult:
    title: str
    snippet: str


class SearchClient(Protocol):
    """Search interface for external BPM/vocal research."""

    def search(self, query: str) -> Iterable[SearchResult]:
        """Return search results for the query."""


class VerificationDecision(BaseModel):
    """Structured audit record for acceptance/rejection decisions."""

    accepted: bool
    spotify_uri: str
    reasons: list[str]
    bpm: Optional[float] = None
    bpm_source: Optional[str] = None
    vocal_source: Optional[str] = None


class Researcher:
    """Hybrid verifier for tempo and vocal content."""

    def __init__(self, search_client: Optional[SearchClient] = None) -> None:
        self._search_client = search_client

    def verify(
        self, candidate: TrackCandidate, constraints: ProtocolConstraints
    ) -> VerificationDecision:
        reasons: list[str] = []
        bpm, bpm_source = self._resolve_bpm(candidate)
        if bpm is None:
            reasons.append("Insufficient BPM data")
        elif not self._bpm_in_range(bpm, constraints):
            reasons.append("Tempo out of range")

        vocals_ok, vocal_source = self._resolve_vocals(candidate, constraints)
        if not vocals_ok:
            reasons.append("Contains vocals")

        accepted = not reasons
        return VerificationDecision(
            accepted=accepted,
            spotify_uri=candidate.spotify_uri,
            reasons=reasons,
            bpm=bpm,
            bpm_source=bpm_source,
            vocal_source=vocal_source,
        )

    def _resolve_bpm(
        self, candidate: TrackCandidate
    ) -> tuple[Optional[float], Optional[str]]:
        if candidate.audio_features and candidate.audio_features.tempo:
            return candidate.audio_features.tempo, "spotify_features"

        if not self._search_client:
            return None, None

        query = f"{candidate.title} {candidate.artist} bpm"
        bpm = self._parse_bpm_from_search(self._search_client.search(query))
        if bpm is None:
            return None, "external_fallback"
        return bpm, "external_fallback"

    def _resolve_vocals(
        self, candidate: TrackCandidate, constraints: ProtocolConstraints
    ) -> tuple[bool, Optional[str]]:
        if constraints.allow_vocals:
            return True, "protocol_allows_vocals"

        features = candidate.audio_features
        if features:
            speechiness = features.speechiness
            instrumentalness = features.instrumentalness
            if speechiness is not None and speechiness >= 0.33:
                return False, "spotify_features"
            if instrumentalness is not None and instrumentalness < 0.5:
                return False, "spotify_features"
            if speechiness is not None or instrumentalness is not None:
                return True, "spotify_features"

        return False, "insufficient_data"

    @staticmethod
    def _parse_bpm_from_search(results: Iterable[SearchResult]) -> Optional[float]:
        bpm_pattern = re.compile(
            r"\b(\d{2,3})\s*(?:bpm|beats per minute)\b", re.IGNORECASE
        )
        for result in results:
            for text in (result.title, result.snippet):
                match = bpm_pattern.search(text)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue
        return None

    @staticmethod
    def _bpm_in_range(bpm: float, constraints: ProtocolConstraints) -> bool:
        if constraints.bpm_min is not None and bpm < constraints.bpm_min:
            return False
        if constraints.bpm_max is not None and bpm > constraints.bpm_max:
            return False
        return True
