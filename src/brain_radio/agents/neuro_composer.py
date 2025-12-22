"""Neuro-Composer agent: translates modes into protocol constraints."""

from __future__ import annotations

from enum import Enum
from typing import Iterable, Optional

from pydantic import BaseModel, Field


class Mode(str, Enum):
    """Supported neuro-protocol modes."""

    focus = "focus"
    relax = "relax"
    sleep = "sleep"
    meditation = "meditation"


class ProtocolConstraints(BaseModel):
    """Machine-readable protocol constraints for verification."""

    mode: Mode
    bpm_min: Optional[int] = Field(default=None, description="Minimum BPM inclusive.")
    bpm_max: Optional[int] = Field(default=None, description="Maximum BPM inclusive.")
    allow_vocals: bool = Field(default=False, description="Whether vocals are allowed.")
    preferred_genres: list[str] = Field(default_factory=list)


class NeuroComposer:
    """Translate user intent into strict protocol constraints."""

    def compose(
        self, mode: Mode, genres: Optional[Iterable[str]] = None
    ) -> ProtocolConstraints:
        genres_list = [genre.strip() for genre in (genres or []) if genre.strip()]

        if mode == Mode.focus:
            return ProtocolConstraints(
                mode=mode,
                bpm_min=120,
                bpm_max=140,
                allow_vocals=False,
                preferred_genres=genres_list,
            )

        if mode == Mode.relax:
            return ProtocolConstraints(
                mode=mode,
                bpm_min=60,
                bpm_max=90,
                allow_vocals=True,
                preferred_genres=genres_list,
            )

        if mode == Mode.sleep:
            return ProtocolConstraints(
                mode=mode,
                bpm_min=None,
                bpm_max=60,
                allow_vocals=False,
                preferred_genres=genres_list,
            )

        return ProtocolConstraints(
            mode=mode,
            bpm_min=None,
            bpm_max=80,
            allow_vocals=False,
            preferred_genres=genres_list,
        )
