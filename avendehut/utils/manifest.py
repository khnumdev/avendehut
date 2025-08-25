from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


from pydantic import BaseModel


class ManifestFile(BaseModel):
  path_rel: str
  size_bytes: int
  mtime_ns: int
  sha256: str


class Manifest(BaseModel):
  version: str
  generated_at: str
  files: List[ManifestFile]


def load_manifest(path: Path) -> Optional[Manifest]:
  if not path.exists():
    return None
  data = json.loads(path.read_text(encoding="utf-8"))
  return Manifest.model_validate(data)


def write_manifest(path: Path, manifest: Manifest) -> None:
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
  tmp.replace(path)

