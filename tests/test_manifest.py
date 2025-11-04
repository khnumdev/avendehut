from __future__ import annotations

from pathlib import Path
from avendehut.utils.manifest import Manifest, ManifestFile, write_manifest, load_manifest


def test_manifest_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / ".manifest.json"
    m = Manifest(
        version="1",
        generated_at="2020-01-01T00:00:00Z",
        files=[
            ManifestFile(path_rel="a.epub", size_bytes=123, mtime_ns=456, sha256="deadbeef"),
        ],
    )
    write_manifest(path, m)
    loaded = load_manifest(path)
    assert loaded is not None
    assert loaded.version == "1"
    assert loaded.files[0].path_rel == "a.epub"
