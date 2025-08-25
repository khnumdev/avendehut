from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ebooklib import epub  # type: ignore
from pypdf import PdfReader  # type: ignore


def _stable_id(path: Path) -> str:
  stat = path.stat()
  h = hashlib.sha256()
  h.update(str(path.resolve()).encode())
  h.update(str(stat.st_size).encode())
  h.update(str(stat.st_mtime_ns).encode())
  return h.hexdigest()


def _iso(ts: float) -> str:
  return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _extract_epub(path: Path) -> tuple[str, List[str], Optional[int], Optional[str]]:
  book = epub.read_epub(str(path))
  title = (book.get_metadata("DC", "title") or [["", {}]])[0][0] or path.stem
  authors = [a[0] for a in (book.get_metadata("DC", "creator") or []) if a and a[0]] or []
  lang = (book.get_metadata("DC", "language") or [[None, {}]])[0][0]
  pubdate_raw = (book.get_metadata("DC", "date") or [[None, {}]])[0][0]
  year = None
  if pubdate_raw:
    try:
      year = int(str(pubdate_raw)[:4])
    except Exception:
      year = None
  return str(title), authors, year, (str(lang) if lang else None)


def _extract_pdf(path: Path) -> tuple[str, List[str], Optional[int], Optional[str]]:
  reader = PdfReader(str(path))
  info = reader.metadata or {}
  title = (getattr(info, "title", None) or path.stem)
  author = getattr(info, "author", None)
  authors = [author] if author else []
  year = None
  try:
    if getattr(info, "creation_date", None):
      # format like D:YYYYMMDDHHmmSS
      year = int(str(info.creation_date)[2:6])
  except Exception:
    year = None
  return str(title), authors, year, None


def _extract_mobi(path: Path) -> tuple[str, List[str], Optional[int], Optional[str]]:
  # Best-effort: try to import mobi, else fallback to filename
  try:
    import mobi  # type: ignore

    with open(path, "rb") as f:
      book = mobi.Mobi(f)
      meta = getattr(book, "header", None)
      title = getattr(meta, "title", None) or path.stem
      author = getattr(meta, "author", None)
      authors = [author] if author else []
      return str(title), authors, None, None
  except Exception:
    return path.stem, [], None, None


def _generate_tags(extension: str, title: str, authors: List[str], year: Optional[int], language: Optional[str]) -> List[str]:
  tags = set()
  tags.add(extension.lstrip(".").lower())
  for a in authors:
    if a:
      tags.add(a.lower())
  if language:
    tags.add(language.lower())
  if year:
    tags.add(str(year))
  return sorted(tags)


def extract_catalog_item(src_root: Path, path: Path) -> dict:
  """Extract metadata for a supported file and return a catalog item dict.

  The function is light-weight and avoids heavy NLP; it relies on embedded metadata.
  """
  extension = path.suffix.lower()
  title: str
  authors: List[str]
  year: Optional[int]
  language: Optional[str]
  if extension == ".epub":
    title, authors, year, language = _extract_epub(path)
  elif extension == ".pdf":
    title, authors, year, language = _extract_pdf(path)
  elif extension == ".mobi":
    title, authors, year, language = _extract_mobi(path)
  else:
    raise ValueError(f"Unsupported extension: {extension}")

  stat = path.stat()
  item = {
    "id": _stable_id(path),
    "path_rel": str(path.relative_to(src_root)),
    "filename": path.name,
    "extension": extension.lstrip("."),
    "title": title or path.stem,
    "authors": authors,
    "published_year": year,
    "language": language,
    "size_bytes": stat.st_size,
    "tags": _generate_tags(extension, title, authors, year, language),
    "created_at": _iso(stat.st_ctime),
    "modified_at": _iso(stat.st_mtime),
  }
  return item

