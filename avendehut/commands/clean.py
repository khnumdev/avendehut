from __future__ import annotations

import shutil
from pathlib import Path

import click
from rich.console import Console


console = Console()


@click.command(context_settings={"help_option_names": ["-h", "-help", "--help"]})
@click.option("--out", type=click.Path(file_okay=False, path_type=Path), required=True)
def clean_command(out: Path) -> None:
  """Delete generated output and manifest."""
  if not out.exists():
    console.print(f"[yellow]Nothing to clean:[/yellow] {out}")
    return
  for child in out.iterdir():
    if child.name == ".gitkeep":
      continue
    if child.is_dir():
      shutil.rmtree(child)
    else:
      child.unlink(missing_ok=True)
  console.print(f"[green]Cleaned:[/green] {out}")

