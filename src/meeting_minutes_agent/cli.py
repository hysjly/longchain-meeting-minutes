from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from meeting_minutes_agent.service import generate_minutes


app = typer.Typer(help="Convert FunASR transcripts into structured meeting minutes.")


@app.callback()
def main() -> None:
    """Meeting minutes agent command group."""


@app.command()
def run(
    input_path: Annotated[Path, typer.Argument(help="Path to FunASR transcript JSON.")],
    output_path: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path to write Markdown minutes."),
    ] = None,
) -> None:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    try:
        markdown = generate_minutes(payload)
    except (RuntimeError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        if _is_provider_error(exc):
            typer.echo(f"LLM provider error: {exc}", err=True)
            raise typer.Exit(code=1) from exc
        raise
    if output_path is None:
        typer.echo(markdown)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def _is_provider_error(exc: Exception) -> bool:
    module_name = exc.__class__.__module__
    return module_name == "openai" or module_name.startswith("openai.")
