"""Parse support pages: counts.htm, refs.htm, topical.htm."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from chd.links import classify_link
from chd.models import CountsData, Reference, TopicalPage, TopicalTopic
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
    """Legacy wrapper — returns list of {filename, name} dicts."""
    page = parse_topical(filepath)
    return [{"filename": t.filename, "name": t.name} for t in page.topics]


def parse_topical(filepath: Path | None = None) -> TopicalPage:
    """Parse topical.htm into a full TopicalPage with counts and descriptions."""
    if filepath is None:
        filepath = RAW_DIR / "topical.htm"
    if not filepath.exists():
        return TopicalPage()
    html = filepath.read_bytes()
    soup = parse_html(html, fix_p_tags=False)

    # Extract title (h2)
    title = ""
    h2 = soup.find("h2")
    if h2:
        title = h2.get_text(strip=True)

    # The topic list is in the inner table (rows with 3 cells: name+link, count, description)
    topics = []
    for tr in soup.find_all("tr", valign="top"):
        cells = tr.find_all("td")
        if len(cells) < 3:
            continue

        # Cell 0: topic name + link
        a_tag = cells[0].find("a", href=True)
        if not a_tag:
            continue
        name = a_tag.get_text(strip=True)
        filename = a_tag.get("href", "")

        # Cell 1: entry count
        count_text = cells[1].get_text(strip=True).replace(",", "")
        entry_count = int(count_text) if count_text.isdigit() else 0

        # Cell 2: description (may contain links)
        description = cells[2].get_text(" ", strip=True)
        desc_links = []
        for desc_a in cells[2].find_all("a", href=True):
            desc_links.append(classify_link(desc_a, from_page="topical.htm"))

        topics.append(TopicalTopic(
            name=name,
            filename=filename,
            entry_count=entry_count,
            description=description,
            description_links=desc_links,
        ))

    return TopicalPage(
        title=title,
        topic_count=len(topics),
        topics=topics,
    )
