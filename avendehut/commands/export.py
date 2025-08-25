from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

import click

from .search import iter_catalog


@click.command(context_settings={"help_option_names": ["-h", "-help", "--help"]})
@click.option("--out", type=click.Path(dir_okay=False, path_type=Path), required=True)
@click.option("--format", "format_", type=click.Choice(["csv", "json"], case_sensitive=False), required=True)
@click.option("--src-out", "out_dir", type=click.Path(file_okay=False, path_type=Path), required=True, help="Directory containing built catalog (for reading data)")
def export_command(out: Path, format_: str, out_dir: Path) -> None:
  """Export catalog to CSV or JSON."""
  items = list(iter_catalog(out_dir))
  if format_ == "json":
    # Write atomically to avoid partial files
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(out)
  else:
    fieldnames = [
      "id",
      "path_rel",
      "filename",
      "extension",
      "title",
      "authors",
      "published_year",
      "language",
      "size_bytes",
      "tags",
      "created_at",
      "modified_at",
    ]
    # Write atomically to avoid partial files
    tmp = out.with_suffix(out.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      for it in items:
        row = it.copy()
        row["authors"] = ", ".join(row.get("authors", []) or [])
        row["tags"] = ", ".join(row.get("tags", []) or [])
        writer.writerow(row)
    tmp.replace(out)

