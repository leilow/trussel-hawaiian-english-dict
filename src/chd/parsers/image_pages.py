"""Parse image detail pages (e.g. aalii.htm, nene.htm).

Each page has a consistent structure:
  <img src="images/{name}.jpg">
  <b><font size="+2">{headword}</font></b>
  <p align=center>{source attribution with optional link}</p>
"""

from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup

from chd.models import ImageDetailPage

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"


def parse_image_detail_page(filepath: Path) -> ImageDetailPage:
    """Parse a single image detail page."""
    soup = BeautifulSoup(filepath.read_bytes(), "lxml")

    result = ImageDetailPage(filename=filepath.name)

    # Image URL: <img src="images/aalii.jpg">
    img_tag = soup.find("img")
    if img_tag:
        result.image_url = img_tag.get("src", "")

    # Headword: <b><font size="+2">ʻaʻaliʻi</font></b>
    font_tag = soup.find("font", attrs={"size": "+2"})
    if font_tag:
        result.headword_display = font_tag.get_text(strip=True)

    # Source/caption: the <p align=center> or last <p> in the <td>
    td = soup.find("td")
    if td:
        # Find all <p> tags in the td
        p_tags = td.find_all("p")
        for p in p_tags:
            align = p.get("align", "")
            if align == "center" or (not result.source_credit and p != p_tags[0] if p_tags else False):
                # This is the source/credit line
                full_text = p.get_text(" ", strip=True)
                result.source_credit = full_text

                # Extract link if present
                a_tag = p.find("a", href=True)
                if a_tag:
                    result.source_link_url = a_tag.get("href", "")
                    result.source_link_text = a_tag.get_text(strip=True)

                # Caption is the text around the link
                result.caption = full_text
                break

    return result


def parse_all_image_detail_pages(
    raw_dir: Path = RAW_DIR,
    manifest_path: Path | None = None,
) -> list[ImageDetailPage]:
    """Parse all image detail pages listed in the manifest.

    If no manifest_path given, uses data/processed/images_manifest.json.
    """
    if manifest_path is None:
        manifest_path = raw_dir.parent / "processed" / "images_manifest.json"

    if not manifest_path.exists():
        return []

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = []

    for img_record in manifest.get("images", []):
        detail_page = img_record.get("detail_page", "")
        if not detail_page:
            continue

        filepath = raw_dir / detail_page
        if not filepath.exists():
            continue

        page = parse_image_detail_page(filepath)
        results.append(page)

    return results
