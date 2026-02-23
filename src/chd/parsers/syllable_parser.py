"""Parse syllable breakdowns from hwdotted/MKhwdotted spans."""

from __future__ import annotations

from bs4 import Tag


def extract_syllable_breakdown(p_tag: Tag) -> str:
    """Extract syllable breakdown from <span class="hwdotted"> or <span class="MKhwdotted">.

    Returns a string like "ʻaʻa·liʻi" or "" if not present.
    """
    for cls in ("hwdotted", "MKhwdotted"):
        span = p_tag.find("span", class_=cls)
        if span:
            text = span.get_text(strip=True).strip("[] ")
            return text
    return ""
