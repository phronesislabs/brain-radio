"""CLI entry point for Brain-Radio."""

from __future__ import annotations

from typing import Optional

import typer

from brain_radio.agents.neuro_composer import Mode, NeuroComposer

app = typer.Typer(add_completion=False)


@app.command()
def compose(
    mode: Mode = typer.Option(..., "--mode", help="Protocol mode."),
    genre: Optional[str] = typer.Option(None, "--genre", help="Preferred genre(s)."),
) -> None:
    """Emit protocol constraints for the requested mode."""
    composer = NeuroComposer()
    genres = [value.strip() for value in (genre or "").split(",") if value.strip()]
    constraints = composer.compose(mode, genres=genres)
    typer.echo(constraints.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
