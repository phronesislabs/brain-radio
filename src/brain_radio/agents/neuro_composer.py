"""Neuro-Composer Agent: Translates cognitive goals into strict constraints."""

from brain_radio.agents.constants import (
    FOCUS_MODE_MAX_ENERGY,
    FOCUS_MODE_TEMPO_MAX,
    FOCUS_MODE_TEMPO_MIN,
    MEDITATION_MODE_MAX_ENERGY,
    MEDITATION_MODE_TEMPO_MAX,
    RELAX_MODE_MAX_ENERGY,
    RELAX_MODE_TEMPO_MAX,
    RELAX_MODE_TEMPO_MIN,
    SLEEP_MODE_MAX_ENERGY,
    SLEEP_MODE_TEMPO_MAX,
)
from brain_radio.models import Mode, ProtocolConstraints


class NeuroComposerAgent:
    """
    Neuro-Composer Agent (The "Scientist").

    Translates abstract cognitive goals into strict, machine-readable constraints.
    """

    def compose_constraints(self, mode: Mode, genre: str | None = None) -> ProtocolConstraints:
        """
        Generate protocol constraints for a given mode.

        Args:
            mode: The neuro-protocol mode (Focus, Relax, Sleep, Meditation)
            genre: Optional user-specified genre preference

        Returns:
            ProtocolConstraints with strict ranges and bans
        """
        if mode == Mode.FOCUS:
            return ProtocolConstraints(
                mode=mode,
                tempo_min=FOCUS_MODE_TEMPO_MIN,
                tempo_max=FOCUS_MODE_TEMPO_MAX,
                energy_min=None,
                energy_max=FOCUS_MODE_MAX_ENERGY,
                no_vocals=True,
                avoid_live=True,
                avoid_remaster=True,
                avoid_feat=True,
                genres=["Techno", "Baroque", "Post-Rock"] if genre is None else [genre],
                key_preference=None,
            )

        elif mode == Mode.RELAX:
            return ProtocolConstraints(
                mode=mode,
                tempo_min=RELAX_MODE_TEMPO_MIN,
                tempo_max=RELAX_MODE_TEMPO_MAX,
                energy_min=None,
                energy_max=RELAX_MODE_MAX_ENERGY,
                no_vocals=False,  # Relax allows vocals
                avoid_live=False,
                avoid_remaster=False,
                avoid_feat=False,
                genres=["Acoustic", "Ambient", "Jazz"] if genre is None else [genre],
                key_preference="Major",
            )

        elif mode == Mode.SLEEP:
            return ProtocolConstraints(
                mode=mode,
                tempo_min=None,
                tempo_max=SLEEP_MODE_TEMPO_MAX,
                energy_min=None,
                energy_max=SLEEP_MODE_MAX_ENERGY,
                no_vocals=False,  # Sleep can have soft vocals
                avoid_live=True,
                avoid_remaster=False,
                avoid_feat=False,
                genres=["Ambient", "Drone", "Nature Sounds"] if genre is None else [genre],
                key_preference=None,
            )

        elif mode == Mode.MEDITATION:
            return ProtocolConstraints(
                mode=mode,
                tempo_min=None,
                tempo_max=MEDITATION_MODE_TEMPO_MAX,
                energy_min=None,
                energy_max=MEDITATION_MODE_MAX_ENERGY,
                no_vocals=True,  # Meditation avoids guided speech by default
                avoid_live=True,
                avoid_remaster=False,
                avoid_feat=False,
                genres=["Ambient", "Drone", "Nature Sounds"] if genre is None else [genre],
                key_preference=None,
            )

        else:
            raise ValueError(f"Unknown mode: {mode}")
