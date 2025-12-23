"""Pydantic models for Brain-Radio data structures."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Mode(str, Enum):
    """Neuro-protocol modes."""

    FOCUS = "focus"
    RELAX = "relax"
    SLEEP = "sleep"
    MEDITATION = "meditation"


class ProtocolConstraints(BaseModel):
    """Machine-readable constraints for a neuro-protocol mode."""

    mode: Mode
    tempo_min: Optional[float] = Field(None, description="Minimum BPM")
    tempo_max: Optional[float] = Field(None, description="Maximum BPM")
    energy_min: Optional[float] = Field(None, description="Minimum energy (0.0-1.0)")
    energy_max: Optional[float] = Field(None, description="Maximum energy (0.0-1.0)")
    no_vocals: bool = Field(False, description="Hard ban on vocals")
    avoid_live: bool = Field(False, description="Avoid live versions")
    avoid_remaster: bool = Field(False, description="Avoid remastered versions")
    avoid_feat: bool = Field(False, description="Avoid tracks with featured artists")
    genres: list[str] = Field(default_factory=list, description="Preferred genres")
    key_preference: Optional[str] = Field(None, description="Preferred key (Major/Minor)")


class TrackMetadata(BaseModel):
    """Track metadata from Spotify or external sources."""

    spotify_id: str = Field(..., description="Spotify track ID")
    spotify_uri: str = Field(..., description="Spotify track URI")
    name: str = Field(..., description="Track name")
    artist: str = Field(..., description="Primary artist")
    album: Optional[str] = Field(None, description="Album name")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    bpm: Optional[float] = Field(None, description="Tempo in BPM")
    key: Optional[str] = Field(None, description="Musical key")
    is_instrumental: Optional[bool] = Field(None, description="Whether track is instrumental")
    energy: Optional[float] = Field(None, description="Energy level (0.0-1.0)")
    speechiness: Optional[float] = Field(None, description="Speechiness (0.0-1.0)")
    instrumentalness: Optional[float] = Field(None, description="Instrumentalness (0.0-1.0)")
    explicit: bool = Field(False, description="Whether track is explicit")
    is_live: bool = Field(False, description="Whether track is a live version")
    is_remaster: bool = Field(False, description="Whether track is remastered")
    has_feat: bool = Field(False, description="Whether track has featured artists")
    source: str = Field(..., description="Data source: 'spotify_features' or 'external_fallback'")


class VerificationResult(BaseModel):
    """Result of track verification by Researcher agent."""

    track: TrackMetadata
    approved: bool = Field(..., description="Whether track passes protocol constraints")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in verification")
    reasons: list[str] = Field(default_factory=list, description="Accept/reject reasons")
    distraction_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Distraction score (lower is better)"
    )


class PlaylistRequest(BaseModel):
    """User request for playlist generation."""

    mode: Mode
    genre: Optional[str] = Field(None, description="User-specified genre preference")
    duration_minutes: Optional[int] = Field(60, description="Target playlist duration")


class PlaylistResult(BaseModel):
    """Generated playlist result."""

    mode: Mode
    tracks: list[TrackMetadata] = Field(default_factory=list)
    total_duration_ms: int = Field(0, description="Total duration in milliseconds")
    verification_summary: dict[str, int] = Field(
        default_factory=dict, description="Summary of verification results"
    )
