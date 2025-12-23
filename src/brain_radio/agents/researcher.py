"""Researcher Agent: Hybrid verifier that validates tracks using web research."""

import re
from typing import Any

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI

from brain_radio.agents.constants import (
    DISTRACTION_SCORE_ENERGY_WEIGHT,
    DISTRACTION_SCORE_EXPLICIT_PENALTY,
    DISTRACTION_SCORE_INSTRUMENTALNESS_WEIGHT,
    DISTRACTION_SCORE_REJECTION_THRESHOLD,
    DISTRACTION_SCORE_SPEECHINESS_WEIGHT,
    INSTRUMENTALNESS_THRESHOLD,
    MAX_VALID_BPM,
    MIN_VALID_BPM,
    SPEECHINESS_THRESHOLD,
)
from brain_radio.models import Mode, ProtocolConstraints, TrackMetadata, VerificationResult


class ResearcherAgent:
    """
    Hybrid Verifier Agent.

    Verifies that a specific Spotify track satisfies protocol constraints.
    Uses web research to find BPM, key, and instrumental status when Spotify
    audio features are unavailable.
    """

    def __init__(self, llm: ChatOpenAI | None = None, search_tool: Any = None):
        """Initialize Researcher agent."""
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.search_tool = search_tool or DuckDuckGoSearchRun()

    async def verify_track(
        self, track: TrackMetadata, constraints: ProtocolConstraints
    ) -> VerificationResult:
        """
        Verify a track against protocol constraints.

        Uses web research to find missing metadata (BPM, instrumental status).
        """
        reasons: list[str] = []
        confidence = 1.0

        # Calculate distraction score for Focus mode (even for rejected tracks)
        distraction_score = None
        if constraints.mode == Mode.FOCUS:
            distraction_score = self._calculate_distraction_score(track)

        # Check hard bans first
        if constraints.no_vocals and not self._is_instrumental(track):
            return VerificationResult(
                track=track,
                approved=False,
                confidence=1.0,
                reasons=["Contains vocals - violates protocol constraint"],
                distraction_score=distraction_score,
            )

        if constraints.avoid_live and track.is_live:
            return VerificationResult(
                track=track,
                approved=False,
                confidence=1.0,
                reasons=["Live version - violates protocol constraint"],
                distraction_score=distraction_score,
            )

        if constraints.avoid_remaster and track.is_remaster:
            return VerificationResult(
                track=track,
                approved=False,
                confidence=1.0,
                reasons=["Remastered version - violates protocol constraint"],
                distraction_score=distraction_score,
            )

        if constraints.avoid_feat and track.has_feat:
            return VerificationResult(
                track=track,
                approved=False,
                confidence=1.0,
                reasons=["Featured artists - violates protocol constraint"],
                distraction_score=distraction_score,
            )

        # Verify BPM if required
        if constraints.tempo_min is not None or constraints.tempo_max is not None:
            bpm = track.bpm
            if bpm is None:
                # Use web research to find BPM
                bpm = await self._research_bpm(track)
                if bpm is None:
                    return VerificationResult(
                        track=track,
                        approved=False,
                        confidence=0.0,
                        reasons=["Could not determine BPM - insufficient confidence"],
                    )
                track.bpm = bpm
                track.source = "external_fallback"

            # Check BPM range
            if constraints.tempo_min is not None and bpm < constraints.tempo_min:
                return VerificationResult(
                    track=track,
                    approved=False,
                    confidence=1.0,
                    reasons=[f"BPM {bpm} below minimum {constraints.tempo_min}"],
                )

            if constraints.tempo_max is not None and bpm > constraints.tempo_max:
                return VerificationResult(
                    track=track,
                    approved=False,
                    confidence=1.0,
                    reasons=[f"BPM {bpm} above maximum {constraints.tempo_max}"],
                )

            reasons.append(f"BPM {bpm} within range")

        # Check energy if required
        if constraints.energy_min is not None and track.energy is not None:
            if track.energy < constraints.energy_min:
                return VerificationResult(
                    track=track,
                    approved=False,
                    confidence=1.0,
                    reasons=[f"Energy {track.energy} below minimum {constraints.energy_min}"],
                )

        if constraints.energy_max is not None and track.energy is not None:
            if track.energy > constraints.energy_max:
                return VerificationResult(
                    track=track,
                    approved=False,
                    confidence=1.0,
                    reasons=[f"Energy {track.energy} above maximum {constraints.energy_max}"],
                )

        # Check distraction score threshold for Focus mode
        if constraints.mode == Mode.FOCUS and distraction_score is not None:
            if distraction_score > DISTRACTION_SCORE_REJECTION_THRESHOLD:
                return VerificationResult(
                    track=track,
                    approved=False,
                    confidence=0.9,
                    reasons=[f"Distraction score {distraction_score:.2f} too high"],
                    distraction_score=distraction_score,
                )

        reasons.append("All protocol constraints satisfied")
        return VerificationResult(
            track=track,
            approved=True,
            confidence=confidence,
            reasons=reasons,
            distraction_score=distraction_score,
        )

    def _is_instrumental(self, track: TrackMetadata) -> bool:
        """Check if track is instrumental."""
        # Use Spotify data if available
        if track.is_instrumental is not None:
            return track.is_instrumental

        # Use speechiness/instrumentalness as proxy
        if track.instrumentalness is not None:
            return track.instrumentalness > INSTRUMENTALNESS_THRESHOLD

        if track.speechiness is not None:
            return track.speechiness < SPEECHINESS_THRESHOLD

        # Default to unknown (will need web research)
        return False

    async def _research_bpm(self, track: TrackMetadata) -> float | None:
        """
        Research BPM using web search.

        Searches for track BPM and extracts numeric value from results.
        """
        query = f"{track.name} {track.artist} BPM tempo"
        try:
            # DuckDuckGoSearchRun may not have ainvoke, use invoke in async context
            if hasattr(self.search_tool, "ainvoke"):
                result = await self.search_tool.ainvoke(query)
            else:
                # Run sync tool in executor if needed
                import asyncio

                result = await asyncio.to_thread(self.search_tool.invoke, query)
            # Extract BPM from search results
            bpm = self._extract_bpm_from_text(result)
            return bpm
        except Exception:
            # Log error but continue (fallback will be used)
            pass
            return None

    def _extract_bpm_from_text(self, text: str) -> float | None:
        """Extract BPM value from text using regex."""
        # Look for patterns like "120 BPM", "BPM: 140", "tempo: 130"
        patterns = [
            r"\b(\d{2,3})\s*BPM\b",
            r"BPM[:\s]+(\d{2,3})",
            r"tempo[:\s]+(\d{2,3})",
            r"(\d{2,3})\s*bpm",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    bpm = float(matches[0])
                    # Sanity check: BPM should be within valid range
                    if MIN_VALID_BPM <= bpm <= MAX_VALID_BPM:
                        return bpm
                except ValueError:
                    continue

        return None

    def _calculate_distraction_score(self, track: TrackMetadata) -> float:
        """
        Calculate distraction score for Focus mode.

        Lower is better. Factors:
        - Speechiness (higher = more distracting)
        - Low instrumentalness (higher = more distracting)
        - High energy (higher = more distracting)
        - Explicit content
        """
        score = 0.0

        # Speechiness penalty
        if track.speechiness is not None:
            score += track.speechiness * DISTRACTION_SCORE_SPEECHINESS_WEIGHT

        # Instrumentalness (inverse - low instrumentalness = high distraction)
        if track.instrumentalness is not None:
            score += (1.0 - track.instrumentalness) * DISTRACTION_SCORE_INSTRUMENTALNESS_WEIGHT

        # Energy penalty
        if track.energy is not None:
            score += track.energy * DISTRACTION_SCORE_ENERGY_WEIGHT

        # Explicit penalty
        if track.explicit:
            score += DISTRACTION_SCORE_EXPLICIT_PENALTY

        return min(score, 1.0)
