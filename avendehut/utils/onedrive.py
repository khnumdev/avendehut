from __future__ import annotations

"""OneDrive integration helpers (placeholder minimal interface).

This module provides stubs for authentication and listing files using Microsoft Graph.
For this initial version, local filesystem paths are supported. If a path starts with
"onedrive:/", callers should integrate with Graph to download files to a local cache
before processing. This file includes placeholders and clear exceptions to guide future work.
"""

import os
from pathlib import Path
from typing import Iterable


def is_onedrive_path(path: str) -> bool:
  return path.startswith("onedrive:/")


def ensure_onedrive_env() -> None:
  required = ["ONEDRIVE_CLIENT_ID", "ONEDRIVE_CLIENT_SECRET"]
  missing = [k for k in required if not os.getenv(k)]
  if missing:
    raise RuntimeError(f"Missing OneDrive environment variables: {', '.join(missing)}")


def list_onedrive_files(prefix_path: str) -> Iterable[Path]:  # pragma: no cover - stub
  raise NotImplementedError("OneDrive listing not implemented. Use local paths for now.")

