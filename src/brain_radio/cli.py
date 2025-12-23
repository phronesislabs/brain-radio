"""CLI interface for Brain-Radio."""

import asyncio
from typing import Annotated

import typer
from langchain_openai import ChatOpenAI

from brain_radio.agents.supervisor import SupervisorAgent
from brain_radio.cli_constants import (
    DEFAULT_DURATION_MINUTES,
    MAX_TRACKS_TO_DISPLAY,
    MILLISECONDS_PER_SECOND,
    SECONDS_PER_MINUTE,
)
from brain_radio.models import Mode, PlaylistRequest

app = typer.Typer(help="Brain-Radio: Generate scientifically-tuned Spotify playlists")


@app.command()
def generate(
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Neuro-protocol mode: focus, relax, sleep, meditation"),
    ] = "focus",
    genre: Annotated[
        str | None,
        typer.Option("--genre", "-g", help="Genre preference (e.g., Jazz, Techno)"),
    ] = None,
    duration: Annotated[
        int,
        typer.Option("--duration", "-d", help="Target playlist duration in minutes"),
    ] = DEFAULT_DURATION_MINUTES,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Run without actual Spotify API calls"),
    ] = False,
):
    """
    Generate a playlist for the specified mode.

    Example:
        brain-radio generate --mode focus --genre Techno --duration 120
    """
    try:
        mode_enum = Mode(mode.lower())
    except ValueError:
        typer.echo(f"Error: Invalid mode '{mode}'. Must be one of: focus, relax, sleep, meditation")
        raise typer.Exit(1)

    request = PlaylistRequest(mode=mode_enum, genre=genre, duration_minutes=duration)

    typer.echo(f"Generating {mode_enum.value} playlist...")
    if genre:
        typer.echo(f"Genre preference: {genre}")
    typer.echo(f"Target duration: {duration} minutes")
    if dry_run:
        typer.echo("Running in dry-run mode (no Spotify API calls)")

    # Initialize supervisor and generate playlist
    # Note: In dry-run mode, we still need LLM for Researcher agent's web search
    # but we won't make actual Spotify API calls (handled in generate_candidates)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) if not dry_run else None
    supervisor = SupervisorAgent(llm=llm)

    result = asyncio.run(supervisor.generate_playlist(request))

    typer.echo(f"\n[SUCCESS] Generated playlist with {len(result.tracks)} tracks")
    duration_minutes = result.total_duration_ms / MILLISECONDS_PER_SECOND / SECONDS_PER_MINUTE
    typer.echo(f"Total duration: {duration_minutes:.1f} minutes")
    typer.echo("\nVerification summary:")
    for key, value in result.verification_summary.items():
        typer.echo(f"  {key}: {value}")

    if result.tracks:
        typer.echo("\nTracks:")
        for i, track in enumerate(result.tracks[:MAX_TRACKS_TO_DISPLAY], 1):
            typer.echo(f"  {i}. {track.name} - {track.artist}")
        if len(result.tracks) > MAX_TRACKS_TO_DISPLAY:
            remaining_tracks = len(result.tracks) - MAX_TRACKS_TO_DISPLAY
            typer.echo(f"  ... and {remaining_tracks} more")


if __name__ == "__main__":
    app()
