from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import click
from rich.console import Console
from rich.table import Table


console = Console()


def iter_catalog(out: Path) -> Iterable[dict]:
    data_json = out / "data.json"
    data_index = out / "data" / "index.json"
    if data_json.exists():
        data = json.loads(data_json.read_text(encoding="utf-8"))
        for item in data:
            yield item
    elif data_index.exists():
        index = json.loads(data_index.read_text(encoding="utf-8"))
        for chunk in index.get("chunks", []):
            chunk_path = out / chunk
            arr = json.loads(chunk_path.read_text(encoding="utf-8"))
            for item in arr:
                yield item
    else:
        raise click.ClickException("No catalog found. Run 'avendehut build' first.")


@click.command(context_settings={"help_option_names": ["-h", "-help", "--help"]})
@click.option("--out", type=click.Path(file_okay=False, path_type=Path), required=True)
@click.option("--query", type=str, default="", help="Search text")
@click.option("--tags", type=str, default="", help="Comma-separated tags to filter")
def search_command(out: Path, query: str, tags: str) -> None:
    """Search the local catalog index from the CLI."""
    query_lower = query.lower().strip()
    tag_filters = [t.strip().lower() for t in tags.split(",") if t.strip()]

    results: List[dict] = []
    for item in iter_catalog(out):
        haystack = " ".join(
            [
                item.get("title", ""),
                ", ".join(item.get("authors", []) or []),
                " ".join(item.get("tags", []) or []),
            ]
        ).lower()
        if query_lower and query_lower not in haystack:
            continue
        if tag_filters:
            item_tags = {t.lower() for t in (item.get("tags", []) or [])}
            if not set(tag_filters).issubset(item_tags):
                continue
        results.append(item)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Title")
    table.add_column("Authors")
    table.add_column("Year")
    table.add_column("Path")
    for it in results[:50]:
        table.add_row(
            it.get("title", ""),
            ", ".join(it.get("authors", []) or []),
            str(it.get("published_year", "") or ""),
            it.get("path_rel", ""),
        )
    console.print(table)
    console.print(f"[green]{len(results)}[/green] result(s)")
