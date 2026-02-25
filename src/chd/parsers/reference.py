"""Parse reference and scholarly pages.

Covers:
  - Dictionary source pages: sources-pe.htm, sources-mk.htm, sources-an.htm
  - Dictionary preface pages: prefs-57.htm, prefs-65.htm, etc.
  - Gloss source texts: glossrefs.htm
  - Historical wordlists: anderson.htm, samwell.htm, etc.
"""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from chd.models import (
    DictionaryEdition,
    DictionarySourcePage,
    GlossRefsPage,
    GlossSourceText,
    LinkedWord,
    PrefacePage,
    WordlistEntry,
    WordlistPage,
)

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

ASSET_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".gif", ".png", ".js", ".css", ".ico"}


def _extract_assets(soup: BeautifulSoup) -> list[str]:
    """Extract all non-HTML asset references (PDFs, images, JS, CSS) from a page."""
    assets: list[str] = []
    seen: set[str] = set()
    for tag in soup.find_all(["a", "img", "link", "script"]):
        for attr in ("href", "src"):
            val = tag.get(attr, "")
            if not val or val.startswith(("http", "#", "mailto")):
                continue
            clean = val.split("#")[0]
            ext = Path(clean).suffix.lower()
            if ext in ASSET_EXTENSIONS and clean not in seen:
                seen.add(clean)
                assets.append(clean)
    return sorted(assets)


# ─── Dictionary Source Pages ────────────────────────────────────────────────


def parse_source_page(filepath: Path) -> DictionarySourcePage:
    """Parse a dictionary source page (sources-pe.htm, etc.)."""
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    result = DictionarySourcePage(filename=filepath.name)

    # Title from <h1>
    h1 = soup.find("h1")
    if h1:
        result.title = h1.get_text(strip=True)

    # Updated date
    updated_div = soup.find("div", class_="updated")
    if updated_div:
        result.updated = updated_div.get_text(strip=True).replace("updated:", "").strip()

    # Author images (top section photos)
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and src not in result.author_images:
            # Separate author images from edition cover images
            # Author images are in the top section before editions
            pass  # collected below with editions

    # Preface links
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        if href.startswith("prefs-"):
            if href not in result.preface_links:
                result.preface_links.append(href)

    # Editions: each has an <a name="XX"> anchor.
    # The anchor may be inside a <tr> or standalone before a <table>.
    # Strategy: find all named anchors, then look for the nearest <h2>.
    edition_anchors = {"57", "64", "73", "81", "86", "96", "98", "03", "65", "10", "74"}
    for anchor_tag in soup.find_all("a", attrs={"name": True}):
        anchor = anchor_tag.get("name", "")
        if anchor not in edition_anchors:
            continue

        edition = DictionaryEdition(anchor=anchor)

        # Find the containing <tr> or the next sibling table's first <tr>
        container = anchor_tag.find_parent("tr")
        if not container:
            # Anchor is standalone — find the next <tr> with an <h2>
            next_table = anchor_tag.find_next("table")
            if next_table:
                container = next_table.find("tr")

        if not container:
            continue

        # Title from <h2>
        h2 = container.find("h2")
        if h2:
            edition.title = h2.get_text(" ", strip=True)

        # Year from h2 text
        year_match = re.search(r"\b(1[89]\d{2}|20\d{2})\b", edition.title)
        if year_match:
            edition.year = year_match.group(1)

        # Full description from the text cell (bgcolor=lightblue or floralwhite, or has h2)
        tds = container.find_all("td")
        for td in tds:
            bg = td.get("bgcolor", "")
            if bg in ("lightblue", "floralwhite") or td.find("h2"):
                edition.description = td.get_text(" ", strip=True)
                break

        # Cover images in this row
        for img in container.find_all("img"):
            src = img.get("src", "")
            if src:
                edition.cover_images.append(src)

        # Intro PDF link
        for a_tag in container.find_all("a", href=True):
            href = a_tag.get("href", "")
            if href.endswith(".pdf"):
                edition.intro_pdf_url = href
                break

        result.editions.append(edition)

    # Collect author-level images (not in edition rows)
    all_edition_images = set()
    for ed in result.editions:
        all_edition_images.update(ed.cover_images)
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and src not in all_edition_images and "statcounter" not in src:
            if src not in result.author_images:
                result.author_images.append(src)

    result.referenced_assets = _extract_assets(soup)
    return result


def parse_all_source_pages(raw_dir: Path = RAW_DIR) -> list[DictionarySourcePage]:
    """Parse all three dictionary source pages."""
    filenames = ["sources-pe.htm", "sources-mk.htm", "sources-an.htm"]
    results = []
    for fn in filenames:
        fp = raw_dir / fn
        if fp.exists():
            results.append(parse_source_page(fp))
    return results


# ─── Preface Pages ──────────────────────────────────────────────────────────


def parse_preface_page(filepath: Path) -> PrefacePage:
    """Parse a dictionary preface page (prefs-57.htm, etc.)."""
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    result = PrefacePage(filename=filepath.name)

    # Title from <h2>
    h2 = soup.find("h2")
    if h2:
        result.title = h2.get_text(" ", strip=True)

    # Subtitle from <h3> (e.g., Hawaiian proverb)
    h3 = soup.find("h3")
    if h3:
        result.subtitle = h3.get_text(" ", strip=True)

    # Year/edition from title
    year_match = re.search(r"\b(1957|1961|1965|1971|1986)\b", result.title)
    if year_match:
        result.year_edition = year_match.group(1)

    # Navigation links to other preface pages
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        if href.startswith("prefs-") and href != filepath.name:
            if href not in result.preface_nav_links:
                result.preface_nav_links.append(href)

    # Images
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and "statcounter" not in src:
            result.images.append(src)

    # Prose content: the main <td> with the preface text
    # Find the large content table
    content_td = None
    for table in soup.find_all("table"):
        width = table.get("width", "")
        if "75%" in str(width):
            td = table.find("td")
            if td:
                content_td = td
                break

    if content_td:
        # Get the inner HTML of the content, stripping nav and scripts
        # Remove the nav links at the top (preface links)
        result.prose_html = str(content_td)

    result.referenced_assets = _extract_assets(soup)
    return result


def parse_all_preface_pages(raw_dir: Path = RAW_DIR) -> list[PrefacePage]:
    """Parse all preface pages."""
    filenames = ["prefs-57.htm", "prefs-65.htm", "prefs-71.htm", "prefs-86.htm", "prefs-and.htm"]
    results = []
    for fn in filenames:
        fp = raw_dir / fn
        if fp.exists():
            results.append(parse_preface_page(fp))
    return results


# ─── Gloss Source Texts ─────────────────────────────────────────────────────


def parse_glossrefs(filepath: Path | None = None) -> GlossRefsPage:
    """Parse glossrefs.htm — source texts for Hawaiian glosses."""
    if filepath is None:
        filepath = RAW_DIR / "glossrefs.htm"
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    result = GlossRefsPage()

    # Title
    h2 = soup.find("h2")
    if h2:
        result.title = h2.get_text(strip=True)

    # Updated date
    updated_div = soup.find("div", class_="updated")
    if updated_div:
        result.updated = updated_div.get_text(strip=True).replace("updated:", "").strip()

    # Each source text is in a section starting with <a name=N>
    # followed by a <table> with cover image and text
    for anchor_tag in soup.find_all("a", attrs={"name": True}):
        anchor_name = anchor_tag.get("name", "")
        if not anchor_name.isdigit():
            continue

        source = GlossSourceText(number=int(anchor_name))

        # The table immediately following the anchor
        table = anchor_tag.find_next("table")
        if not table:
            continue

        # Cover image
        img = table.find("img")
        if img:
            source.cover_image_url = img.get("src", "")

        # Text cell (second <td>)
        tds = table.find_all("td")
        text_td = tds[1] if len(tds) > 1 else tds[0] if tds else None
        if not text_td:
            continue

        # Hawaiian title from <span class="hawfont">
        haw_span = text_td.find("span", class_="hawfont")
        if haw_span:
            source.hawaiian_title = haw_span.get_text(strip=True)

        # Ulukau URL from the link wrapping the hawfont span
        title_link = text_td.find("a", href=True)
        if title_link:
            href = title_link.get("href", "")
            if "ulukau" in href:
                source.ulukau_url = href

        # Author info from <span class="authorfont">
        author_span = text_td.find("span", class_="authorfont")
        if author_span:
            source.author_info = author_span.get_text(" ", strip=True)

        # Publisher, year, pages from remaining text
        full_text = text_td.get_text("\n", strip=True)
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]

        # Look for publisher line (e.g., "Hale Kuamoʻo, 1996")
        for line in lines:
            if re.search(r"(Hale Kuamo|ʻAha Pūnana|Island Heritage)", line):
                source.publisher = line
                year_match = re.search(r"\b(19\d{2}|20\d{2})\b", line)
                if year_match:
                    source.year = year_match.group(1)

        # Page count
        for line in lines:
            pages_match = re.search(r"(\d+)\s*pp", line)
            if pages_match:
                source.page_count = pages_match.group(0)
                break

        result.source_texts.append(source)

    result.source_count = len(result.source_texts)
    result.referenced_assets = _extract_assets(soup)
    return result


# ─── Historical Wordlist Pages ──────────────────────────────────────────────


def parse_wordlist_page(filepath: Path) -> WordlistPage:
    """Parse a historical wordlist page (anderson.htm, samwell.htm, etc.).

    These pages have a consistent structure:
      - Navigation header
      - Cross-links to other wordlist pages
      - Title: <h2>Author's List<br>(Year)</h2>
      - Intro prose in a bordered table
      - Vocabulary table with columns: num, list_word, modern_hawaiian, gloss
      - Footnotes interspersed as rows with colspan=4
    """
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")
    result = WordlistPage(filename=filepath.name)

    # Title from <h2> — e.g., "William Anderson's List\n(1778)"
    # Skip the cross-nav h2 ("The earliest Hawaiian word lists"), look for the author-specific one
    h2_tags = soup.find_all("h2")
    for h2 in h2_tags:
        text = h2.get_text(" ", strip=True)
        if re.search(r"\(\d{4}\)", text):
            result.title = text
            year_match = re.search(r"\((\d{4})\)", text)
            if year_match:
                result.year = year_match.group(1)
            # Author is text before "'s List" or "'s Vocabulary" or "(year)"
            author_match = re.match(r"(.+?)(?:'s\s+List|'s\s+Vocabulary|\s*\()", text)
            if author_match:
                result.author = author_match.group(1).strip()
            break

    # Sort links (alternative sort orders)
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        if filepath.stem in href or re.match(r"anderson[ahg]?\.htm", href):
            text = a_tag.get_text(strip=True)
            if text and href not in result.sort_links:
                result.sort_links.append(href)

    # Intro text: the bordered table with prose
    for table in soup.find_all("table"):
        border = table.get("border", "")
        cellpadding = table.get("cellpadding", "")
        if border == "1" and cellpadding == "20":
            td = table.find("td")
            if td:
                result.intro_text = td.get_text(" ", strip=True)
            break

    # Vocabulary table: the table with cellpadding=10 and bgcolor=floralwhite
    vocab_table = None
    for table in soup.find_all("table"):
        bg = table.get("bgcolor", "")
        cellpadding = table.get("cellpadding", "")
        if bg == "floralwhite" or (cellpadding == "10" and table.find("span", class_="word")):
            vocab_table = table
            break

    if not vocab_table:
        # Fallback: find a table that contains <span class="word">
        for table in soup.find_all("table"):
            if table.find("span", class_="word"):
                vocab_table = table
                break

    if vocab_table:
        current_footnote = ""
        entries = []

        for tr in vocab_table.find_all("tr", recursive=False):
            # Check if this is a footnote row (has colspan)
            colspan_td = tr.find("td", attrs={"colspan": True})
            if colspan_td:
                footnote_span = colspan_td.find("span", class_="footnote")
                if footnote_span:
                    current_footnote = footnote_span.get_text(" ", strip=True)
                    # Attach to the previous entry
                    if entries:
                        entries[-1].footnote = current_footnote
                continue

            # Skip header row
            if tr.find("th"):
                continue

            tds = tr.find_all("td", recursive=False)
            if len(tds) < 4:
                continue

            # Column 0: number
            num_text = tds[0].get_text(strip=True).rstrip(".")
            try:
                num = int(num_text)
            except ValueError:
                continue

            # Column 1: list word
            word_span = tds[1].find("span", class_="word")
            list_word = word_span.get_text(" ", strip=True) if word_span else tds[1].get_text(strip=True)

            # Column 2: modern Hawaiian (with links)
            haw_span = tds[2].find("span", class_="Haw")
            modern_haw = haw_span.get_text(" ", strip=True) if haw_span else tds[2].get_text(strip=True)

            # Extract linked words
            linked_words = []
            search_in = haw_span if haw_span else tds[2]
            for a_tag in search_in.find_all("a", class_="hawinentry"):
                href = a_tag.get("href", "")
                surface = a_tag.get_text(strip=True)
                target_page = ""
                target_anchor = ""
                if "#" in href:
                    target_page, target_anchor = href.split("#", 1)
                else:
                    target_page = href
                linked_words.append(LinkedWord(
                    surface=surface,
                    target_page=target_page,
                    target_anchor=target_anchor,
                    link_class="hawinentry",
                ))

            # Column 3: gloss
            gloss_span = tds[3].find("span", class_="gloss")
            gloss = gloss_span.get_text(" ", strip=True) if gloss_span else tds[3].get_text(strip=True)

            entries.append(WordlistEntry(
                number=num,
                list_word=list_word,
                modern_hawaiian=modern_haw,
                modern_hawaiian_links=linked_words,
                gloss=gloss,
            ))

        result.entries = entries
        result.entry_count = len(entries)

    return result


WORDLIST_PAGES = [
    "anderson.htm", "samwell.htm", "beresford.htm", "martinez.htm",
    "spanish1.htm", "quimper.htm", "lisiansky.htm", "campbell.htm",
    "arago.htm", "bishop.htm", "botta.htm", "dumont.htm",
]


def parse_all_wordlist_pages(raw_dir: Path = RAW_DIR) -> list[WordlistPage]:
    """Parse all 12 historical wordlist pages."""
    results = []
    for fn in WORDLIST_PAGES:
        fp = raw_dir / fn
        if fp.exists():
            results.append(parse_wordlist_page(fp))
    return results
