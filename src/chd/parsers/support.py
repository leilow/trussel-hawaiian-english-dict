"""Parse support pages: counts.htm, refs.htm, topical.htm."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from chd.models import CountsData, Reference
from chd.preprocess import parse_html

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

HAW_CORE_LETTERS = list("aehiklmnopuw")
LOAN_LETTERS = list("bcdfgjrstvz")
ALL_HAW_LETTERS = HAW_CORE_LETTERS + LOAN_LETTERS


def parse_counts(filepath: Path | None = None) -> CountsData:
    if filepath is None:
        filepath = RAW_DIR / "counts.htm"
    html = filepath.read_bytes()
    soup = parse_html(html, fix_p_tags=False)
    counts = CountsData()
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            counts.raw_tables.append({"rows": rows})
    for td in counts.raw_tables:
        for row in td["rows"]:
            if len(row) >= 2:
                letter = row[0].strip().lower()
                count_str = row[1].strip().replace(",", "")
                if len(letter) <= 2 and count_str.isdigit():
                    counts.entries_by_letter[letter] = int(count_str)
    return counts


def parse_refs(filepath: Path | None = None) -> list[Reference]:
    if filepath is None:
        filepath = RAW_DIR / "refs.htm"
    html = filepath.read_bytes()
    soup = parse_html(html, fix_p_tags=False)
    refs = []
    for a_tag in soup.find_all("a", attrs={"name": True}):
        anchor = a_tag.get("name", "")
        if not anchor:
            continue
        parent = a_tag.parent
        if parent:
            full_text = parent.get_text(strip=True)
            b_tag = parent.find("b")
            abbreviation = b_tag.get_text(strip=True) if b_tag else anchor
            refs.append(Reference(abbreviation=abbreviation, anchor=anchor, full_text=full_text))
    return refs


def discover_topical_pages(filepath: Path | None = None) -> list[dict[str, str]]:
    if filepath is None:
        filepath = RAW_DIR / "topical.htm"
    if not filepath.exists():
        return []
    html = filepath.read_bytes()
    soup = parse_html(html, fix_p_tags=False)
    EXCLUDE_PREFIXES = ("eng-", "haw-conc-", "index-", "rev-")
    EXCLUDE_FILES = {"intro.htm", "counts.htm", "refs.htm", "texts.htm", "glossrefs.htm", "topical.htm"}
    pages = []
    seen = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if not href.endswith(".htm") or href in seen:
            continue
        if any(href == f"haw-{l}.htm" for l in ALL_HAW_LETTERS):
            continue
        if href in EXCLUDE_FILES or any(href.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        seen.add(href)
        pages.append({"filename": href, "name": a_tag.get_text(strip=True)})
    return pages
