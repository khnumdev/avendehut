from __future__ import annotations

import sys
import webbrowser
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .commands.build import build_command
from .commands.watch import watch_command
from .commands.clean import clean_command
from .commands.open import open_command
from .commands.search import search_command
from .commands.export import export_command


console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="avendehut")
def main() -> None:
  """avendehut - build and search a local HTML catalog of books.

  Inspired by Juan Hispalense (Avendehut Hispanus).
  """


# Register subcommands
main.add_command(build_command, name="build")
main.add_command(watch_command, name="watch")
main.add_command(clean_command, name="clean")
main.add_command(open_command, name="open")
main.add_command(search_command, name="search")
main.add_command(export_command, name="export")


if __name__ == "__main__":  # pragma: no cover
  try:
    main()
  except click.ClickException as e:  # pragma: no cover
    console.print(f"[red]Error:[/red] {e}")
    sys.exit(e.exit_code if hasattr(e, "exit_code") else 1)

