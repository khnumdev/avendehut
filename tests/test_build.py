from __future__ import annotations

import json
from pathlib import Path
from click.testing import CliRunner

from avendehut.cli import main


def create_sample_pdf(dir_path: Path, name: str = "a.pdf") -> Path:
  from pypdf import PdfWriter

  pdf = dir_path / name
  writer = PdfWriter()
  writer.add_blank_page(width=72, height=72)
  writer.add_metadata({"/Title": name, "/Author": "Author"})
  with open(pdf, "wb") as f:
    writer.write(f)
  return pdf


def test_build_and_manifest(tmp_path: Path) -> None:
  src = tmp_path / "src"
  out = tmp_path / "out"
  src.mkdir()
  create_sample_pdf(src, "a.pdf")

  runner = CliRunner()
  result = runner.invoke(main, ["build", "--src", str(src), "--out", str(out)])
  assert result.exit_code == 0, result.output

  assert (out / "index.html").exists()
  assert (out / ".manifest.json").exists()

  # Data should exist
  data_json = out / "data.json"
  assert data_json.exists()
  data = json.loads(data_json.read_text(encoding="utf-8"))
  assert isinstance(data, list) and len(data) >= 1

  # Re-run without changes should be fast and still succeed
  result2 = runner.invoke(main, ["build", "--src", str(src), "--out", str(out)])
  assert result2.exit_code == 0, result2.output

