from __future__ import annotations

from pathlib import Path

from avendehut.utils.metadata import extract_catalog_item


def test_extract_pdf_minimal(tmp_path: Path) -> None:
    # Create a tiny PDF using pypdf writer to ensure metadata exists
    from pypdf import PdfWriter

    pdf_path = tmp_path / "test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/Title": "Sample PDF", "/Author": "Alice"})
    with open(pdf_path, "wb") as f:
        writer.write(f)

    item = extract_catalog_item(tmp_path, pdf_path)
    assert item["title"] == "Sample PDF"
    assert "alice" in [t.lower() for t in item["tags"]]
    assert item["extension"] == "pdf"
