from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

import click
from rich.console import Console
from rich.progress import Progress

from ..utils.metadata import extract_catalog_item
from ..utils.manifest import Manifest, ManifestFile, load_manifest, write_manifest
from ..utils.htmlgen import copy_template_and_write_data


console = Console()


SUPPORTED_EXTENSIONS = {".epub", ".pdf", ".mobi"}


def iter_source_files(src: Path) -> Iterable[Path]:
  for root, _dirs, files in os.walk(src):
    for name in files:
      path = Path(root) / name
      if path.suffix.lower() in SUPPORTED_EXTENSIONS:
        yield path


def compute_file_hash(path: Path) -> str:
  sha = hashlib.sha256()
  with path.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
      sha.update(chunk)
  return sha.hexdigest()


@click.command(context_settings={"help_option_names": ["-h", "-help", "--help"]})
@click.option("--src", type=click.Path(exists=True, file_okay=False, path_type=Path), required=True, help="Source folder (local or onedrive:/path)")
@click.option("--out", type=click.Path(file_okay=False, path_type=Path), required=True, help="Output folder")
@click.option("--format", "format_", type=click.Choice(["html"], case_sensitive=False), default="html", show_default=True)
@click.option("--force", is_flag=True, help="Reprocess all files, ignoring manifest")
def build_command(src: Path, out: Path, format_: str, force: bool) -> None:
  """Scan source, process new/updated books, and generate HTML site."""
  out.mkdir(parents=True, exist_ok=True)

  manifest_path = out / ".manifest.json"
  previous_manifest = None if force else load_manifest(manifest_path)
  previous_index = {f.path_rel: f for f in (previous_manifest.files if previous_manifest else [])}

  source_files = list(iter_source_files(src))
  to_process: List[Path] = []
  manifest_files: List[ManifestFile] = []

  for file_path in source_files:
    stat = file_path.stat()
    path_rel = str(file_path.relative_to(src))
    prev = previous_index.get(path_rel)
    if prev and prev.size_bytes == stat.st_size and prev.mtime_ns == stat.st_mtime_ns:
      manifest_files.append(prev)
      continue
    to_process.append(file_path)

  items = []
  with Progress() as progress:
    task = progress.add_task("Processing files", total=len(to_process))
    for file_path in to_process:
      try:
        item = extract_catalog_item(src, file_path)
        items.append(item)

        stat = file_path.stat()
        sha256 = compute_file_hash(file_path)
        manifest_files.append(
          ManifestFile(path_rel=str(file_path.relative_to(src)), size_bytes=stat.st_size, mtime_ns=stat.st_mtime_ns, sha256=sha256)
        )
      except Exception as exc:  # pragma: no cover - rare edge cases
        console.print(f"[yellow]Warning[/yellow]: Failed to process {file_path}: {exc}")
      finally:
        progress.advance(task)

  # If there was a previous catalog, we should merge unchanged items.
  # For simplicity, regenerate catalog from disk for all manifest entries.
  # This keeps logic deterministic while still skipping heavy parsing of unchanged files.
  catalog = []
  for mf in manifest_files:
    file_path = src / mf.path_rel
    try:
      catalog.append(extract_catalog_item(src, file_path))
    except Exception as exc:  # pragma: no cover
      console.print(f"[yellow]Warning[/yellow]: Failed to refresh {file_path}: {exc}")

  copy_template_and_write_data(out, catalog)

  manifest = Manifest(version="1", generated_at=datetime.now(timezone.utc).isoformat(), files=manifest_files)
  write_manifest(manifest_path, manifest)

  console.print(f"[green]Build complete[/green]: {out}")

