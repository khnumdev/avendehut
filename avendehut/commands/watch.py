from __future__ import annotations

import time
from pathlib import Path

import click
from rich.console import Console

from .build import build_command


console = Console()


@click.command(context_settings={"help_option_names": ["-h", "-help", "--help"]})
@click.option("--src", type=str, required=True, help="Source folder (local path or onedrive:/path)")
@click.option(
    "--out", type=click.Path(file_okay=False, path_type=Path), required=True, help="Output folder"
)
@click.option(
    "--interval", type=float, default=2.0, show_default=True, help="Polling interval in seconds"
)
def watch_command(src: str, out: Path, interval: float) -> None:
    """Watch a source folder for changes and auto-rebuild HTML."""
    console.print(f"Watching {src} for changes. Press Ctrl+C to stop.")
    last_snapshot = None
    try:
        while True:
            # For OneDrive paths, we'll always rebuild (no local file watching)
            # For local paths, watch file changes
            from ..utils.onedrive import is_onedrive_path

            if is_onedrive_path(src):
                # For OneDrive, just rebuild at intervals (no file watching available)
                console.print("Rebuilding from OneDrive...")
                build_command.main(  # type: ignore[attr-defined]
                    args=["--src", src, "--out", str(out)],
                    prog_name="avendehut build",
                    standalone_mode=False,
                )
            else:
                src_path = Path(src)
                snapshot = tuple(
                    (p, p.stat().st_mtime_ns) for p in sorted(src_path.rglob("*")) if p.is_file()
                )
                if snapshot != last_snapshot:
                    # Trigger a build
                    console.print("Change detected. Rebuilding...")
                    build_command.main(  # type: ignore[attr-defined]
                        args=["--src", src, "--out", str(out)],
                        prog_name="avendehut build",
                        standalone_mode=False,
                    )
                    last_snapshot = snapshot
            time.sleep(interval)
    except KeyboardInterrupt:  # pragma: no cover
        console.print("Stopped watching.")
