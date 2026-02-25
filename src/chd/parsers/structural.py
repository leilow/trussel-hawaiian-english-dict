"""Parse index, reverse index, and structural pages.

Covers:
  - Index pages: index-{letter}.htm (23 pages, 36K entries)
  - Reverse index pages: rev-{vowel}.htm (5 pages, 38K entries)
  - Structural pages: intro.htm, texts.htm, reversehelp.htm, concord.htm
"""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup

from chd.models import IndexEntry, IndexPage, StructuralPage
from chd.parsers.reference import ASSET_EXTENSIONS, _extract_assets

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

HAW_CORE_LETTERS = list("aehiklmnopuw")
LOAN_LETTERS = list("bcdfgjrstvz")
ALL_LETTERS = HAW_CORE_LETTERS + LOAN_LETTERS
VOWELS = list("aeiou")


# ─── Index Pages ────────────────────────────────────────────────────────────


def parse_index_page(filepath: Path) -> IndexPage:
    """Parse an index-{letter}.htm page.

    Each entry is a <p class="hw"> with:
      - Headword link: <a class="HwNew"> or <a class="MkHw">
      - POS: <span class="pos"> or <span class="MKpos">
      - Definition: <span class="def"> or <span class="MKdef">
    """
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    letter = filepath.stem.replace("index-", "")
    result = IndexPage(filename=filepath.name, page_type="index", letter=letter)

    # Updated date
    updated_div = soup.find("div", class_="updated")
    if updated_div:
        result.updated = updated_div.get_text(strip=True).replace("updated:", "").strip()

    # Two-letter combo anchors
    for a_tag in soup.find_all("a", class_="indexline2let"):
        href = a_tag.get("href", "")
        if href.startswith("#"):
            combo = href[1:]
            if combo and combo not in result.two_letter_combos:
                result.two_letter_combos.append(combo)

    # Entries
    for p in soup.find_all("p", class_="hw"):
        entry = IndexEntry()

        # Headword link
        hw_link = p.find("a", class_="HwNew") or p.find("a", class_="MkHw")
        if hw_link:
            entry.headword = hw_link.get_text(strip=True)
            href = hw_link.get("href", "")
            if "#" in href:
                entry.target_page, entry.target_anchor = href.split("#", 1)
            else:
                entry.target_page = href

            # Source: MkHw = Māmaka Kaiao, HwNew = PE/Andrews
            if hw_link.get("class") and "MkHw" in hw_link.get("class", []):
                entry.source = "MK"
            else:
                entry.source = "PE"

        # Anchor
        anchor_tag = p.find("a", attrs={"name": True})
        if anchor_tag:
            entry.anchor = anchor_tag.get("name", "")

        # POS
        pos_span = p.find("span", class_="pos") or p.find("span", class_="MKpos")
        if pos_span:
            entry.pos = pos_span.get_text(strip=True)

        # Definition
        def_span = p.find("span", class_="def") or p.find("span", class_="MKdef")
        if def_span:
            entry.definition = def_span.get_text(" ", strip=True)

        if entry.headword:
            result.entries.append(entry)

    result.entry_count = len(result.entries)
    result.referenced_assets = _extract_assets(soup)
    return result


def parse_all_index_pages(raw_dir: Path = RAW_DIR) -> list[IndexPage]:
    """Parse all 23 index pages."""
    results = []
    for letter in ALL_LETTERS:
        fp = raw_dir / f"index-{letter}.htm"
        if fp.exists():
            results.append(parse_index_page(fp))
    return results


# ─── Reverse Index Pages ───────────────────────────────────────────────────


def parse_reverse_index_page(filepath: Path) -> IndexPage:
    """Parse a rev-{vowel}.htm page.

    Each entry is a <tr valign=top> with:
      - td[0]: headword in <span class="Rev"> with <a class="HwNew">
      - td[2]: definition text (may include POS in <i>)
    """
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    letter = filepath.stem.replace("rev-", "")
    result = IndexPage(filename=filepath.name, page_type="reverse", letter=letter)

    # Updated date
    updated_div = soup.find("div", class_="updated")
    if updated_div:
        result.updated = updated_div.get_text(strip=True).replace("updated:", "").strip()

    # Two-letter combo sections
    for a_tag in soup.find_all("a", attrs={"name": True}):
        name = a_tag.get("name", "")
        if name.startswith("-") and len(name) >= 2:
            combo = name[1:]  # strip leading dash
            if combo and combo not in result.two_letter_combos:
                result.two_letter_combos.append(combo)

    # Entries: <tr valign=top> with <span class="Rev">
    for tr in soup.find_all("tr", valign="top"):
        rev_span = tr.find("span", class_="Rev")
        if not rev_span:
            continue

        entry = IndexEntry()

        # Headword link (HwNew for PE, MkHw for Māmaka Kaiao)
        hw_link = rev_span.find("a", class_="HwNew") or rev_span.find("a", class_="MkHw")
        if hw_link:
            entry.headword = hw_link.get_text(strip=True)
            href = hw_link.get("href", "")
            if "#" in href:
                entry.target_page, entry.target_anchor = href.split("#", 1)
            else:
                entry.target_page = href
            if hw_link.get("class") and "MkHw" in hw_link.get("class", []):
                entry.source = "MK"

        # Anchor
        anchor_tag = tr.find("a", attrs={"name": True})
        if anchor_tag:
            entry.anchor = anchor_tag.get("name", "")

        # Definition: third <td> (index 2)
        tds = tr.find_all("td")
        if len(tds) >= 3:
            def_td = tds[2]
            def_text = def_td.get_text(" ", strip=True)
            # Extract POS from leading <i>
            first_i = def_td.find("i")
            if first_i and def_text.startswith(first_i.get_text(strip=True)):
                entry.pos = first_i.get_text(strip=True).rstrip(".")
                entry.definition = def_text[len(first_i.get_text(strip=True)):].strip()
            else:
                entry.definition = def_text

        if not entry.source:
            entry.source = "PE"
        if entry.headword:
            result.entries.append(entry)

    result.entry_count = len(result.entries)
    result.referenced_assets = _extract_assets(soup)
    return result


def parse_all_reverse_index_pages(raw_dir: Path = RAW_DIR) -> list[IndexPage]:
    """Parse all 5 reverse index pages."""
    results = []
    for vowel in VOWELS:
        fp = raw_dir / f"rev-{vowel}.htm"
        if fp.exists():
            results.append(parse_reverse_index_page(fp))
    return results


# ─── Structural Pages ──────────────────────────────────────────────────────


def parse_structural_page(filepath: Path) -> StructuralPage:
    """Parse a structural page (intro.htm, texts.htm, reversehelp.htm, etc.).

    These are primarily navigational/prose pages. We extract:
      - Title, updated date
      - Named sections (<a name=...> anchors)
      - All internal and external links
      - Referenced assets (PDFs, images, etc.)
    """
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    result = StructuralPage(filename=filepath.name)

    # Title
    title_tag = soup.find("title")
    if title_tag:
        result.title = title_tag.get_text(strip=True)

    # Updated date
    updated_div = soup.find("div", class_="updated")
    if updated_div:
        result.updated = updated_div.get_text(strip=True).replace("updated:", "").strip()

    # Named sections
    for a_tag in soup.find_all("a", attrs={"name": True}):
        name = a_tag.get("name", "")
        if not name or name == "Top" or name == "top":
            continue
        # Get section heading text from next sibling or parent
        heading = ""
        next_h = a_tag.find_next(["h1", "h2", "h3", "span"])
        if next_h:
            heading = next_h.get_text(strip=True)[:100]
        result.sections.append({"anchor": name, "heading": heading})

    # All links
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        if not href or href.startswith("#"):
            continue
        if href.startswith(("http://", "https://")):
            if href not in result.external_links:
                result.external_links.append(href)
        elif not href.startswith("mailto"):
            if href not in result.internal_links:
                result.internal_links.append(href)

    result.referenced_assets = _extract_assets(soup)
    return result


STRUCTURAL_PAGES = [
    "intro.htm", "texts.htm", "reversehelp.htm", "concord.htm",
    "recon.htm",
]


def parse_all_structural_pages(raw_dir: Path = RAW_DIR) -> list[StructuralPage]:
    """Parse all structural pages."""
    results = []
    for fn in STRUCTURAL_PAGES:
        fp = raw_dir / fn
        if fp.exists():
            results.append(parse_structural_page(fp))
    return results
