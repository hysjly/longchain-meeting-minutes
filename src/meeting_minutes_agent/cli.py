from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

from meeting_minutes_agent.service import generate_minutes


app = typer.Typer(help="Convert FunASR transcripts into structured meeting minutes.")
PROGRESS_EVENT_LABELS = {
    "speaker_inference_start": "说话人角色推断中",
    "speaker_inference_done": "说话人角色推断完成",
    "minutes_generation_start": "会议纪要生成中",
    "minutes_generation_done": "会议纪要生成完成",
}


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
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed:.0f}/{task.total:.0f}"),
            TimeElapsedColumn(),
            console=Console(stderr=True),
            transient=False,
        ) as progress:
            task_id = progress.add_task("准备处理逐字稿", total=2)
            markdown = generate_minutes(
                payload,
                progress_callback=_build_progress_callback(progress, task_id),
            )
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


def _build_progress_callback(progress: Progress, task_id: int):
    def update(event: str) -> None:
        label = PROGRESS_EVENT_LABELS.get(event)
        if label is None:
            return
        progress.update(task_id, description=label)
        if event.endswith("_done"):
            progress.advance(task_id)

    return update
