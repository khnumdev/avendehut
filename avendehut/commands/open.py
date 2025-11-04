from __future__ import annotations

import webbrowser
from pathlib import Path

import click
from rich.console import Console


console = Console()


@click.command(context_settings={"help_option_names": ["-h", "-help", "--help"]})
@click.option("--out", type=click.Path(file_okay=False, path_type=Path), required=True)
def open_command(out: Path) -> None:
    """Open generated HTML in default browser."""
    index = out / "index.html"
    if not index.exists():
        raise click.ClickException(f"index.html not found in {out}")
    webbrowser.open_new_tab(index.resolve().as_uri())
    console.print(f"Opened {index}")
