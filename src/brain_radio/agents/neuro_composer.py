"""Neuro-Composer Agent: Translates cognitive goals into strict constraints."""

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
                tempo_min=120.0,
                tempo_max=140.0,
                energy_min=None,
                energy_max=0.7,  # Avoid high-intensity for Focus
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
                tempo_min=60.0,
                tempo_max=90.0,
                energy_min=None,
                energy_max=0.6,
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
                tempo_max=60.0,
                energy_min=None,
                energy_max=0.3,
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
                tempo_max=70.0,
                energy_min=None,
                energy_max=0.4,
                no_vocals=True,  # Meditation avoids guided speech by default
                avoid_live=True,
                avoid_remaster=False,
                avoid_feat=False,
                genres=["Ambient", "Drone", "Nature Sounds"] if genre is None else [genre],
                key_preference=None,
            )

        else:
            raise ValueError(f"Unknown mode: {mode}")
