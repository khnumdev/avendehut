from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from typing import List


MAX_JSON_BYTES = 5 * 1024 * 1024  # 5 MB


def _ensure_dir(path: Path) -> None:
  path.mkdir(parents=True, exist_ok=True)


def _copy_template(dst: Path, template_dir: Path) -> None:
  _ensure_dir(dst)
  for name in ("index.html", "style.css", "script.js"):
    shutil.copy2(template_dir / name, dst / name)


def _write_json_atomic(path: Path, data: object) -> None:
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
  tmp.replace(path)


def copy_template_and_write_data(out: Path, catalog: List[dict]) -> None:
  template_dir = Path(__file__).resolve().parents[2] / "html_template"
  _copy_template(out, template_dir)

  # Write data.json or chunk
  data_json = out / "data.json"
  serialized = json.dumps(catalog, ensure_ascii=False)
  if len(serialized.encode("utf-8")) <= MAX_JSON_BYTES:
    _write_json_atomic(data_json, catalog)
    # Remove previous chunked directory if exists
    chunk_dir = out / "data"
    if chunk_dir.exists():
      shutil.rmtree(chunk_dir)
    return

  # Chunking
  chunk_dir = out / "data"
  if chunk_dir.exists():
    shutil.rmtree(chunk_dir)
  _ensure_dir(chunk_dir)

  # naive even split by count so each chunk is below limit
  items_per_chunk = max(1, math.floor(len(catalog) / max(1, math.ceil(len(serialized.encode('utf-8')) / MAX_JSON_BYTES))))
  chunks = []
  for idx in range(0, len(catalog), items_per_chunk):
    part = catalog[idx: idx + items_per_chunk]
    chunk_name = f"data-{idx // items_per_chunk + 1:04d}.json"
    _write_json_atomic(chunk_dir / chunk_name, part)
    chunks.append(f"data/{chunk_name}")

  _write_json_atomic(chunk_dir / "index.json", {"chunks": chunks})

