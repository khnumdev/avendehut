from __future__ import annotations

from pathlib import Path
from click.testing import CliRunner

from avendehut.cli import main


def test_cli_help() -> None:
  runner = CliRunner()
  result = runner.invoke(main, ["--help"])
  assert result.exit_code == 0
  assert "Usage" in result.output


def test_cli_search_and_export(tmp_path: Path) -> None:
  from pypdf import PdfWriter

  src = tmp_path / "src"; src.mkdir()
  out = tmp_path / "out"
  writer = PdfWriter(); writer.add_blank_page(width=72, height=72); writer.add_metadata({"/Title": "Hello", "/Author": "Bob"})
  with open(src / "doc.pdf", "wb") as f:
    writer.write(f)

  runner = CliRunner()
  assert runner.invoke(main, ["build", "--src", str(src), "--out", str(out)]).exit_code == 0

  # search
  result = runner.invoke(main, ["search", "--out", str(out), "--query", "hello"]) 
  assert result.exit_code == 0
  assert "result(s)" in result.output

  # export json
  json_out = tmp_path / "export.json"
  result = runner.invoke(main, ["export", "--out", str(json_out), "--format", "json", "--src-out", str(out)])
  assert result.exit_code == 0
  assert json_out.exists()

  # export csv
  csv_out = tmp_path / "export.csv"
  result = runner.invoke(main, ["export", "--out", str(csv_out), "--format", "csv", "--src-out", str(out)])
  assert result.exit_code == 0
  assert csv_out.exists()

