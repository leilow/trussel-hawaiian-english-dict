"""Detect dialect markers (Niʻihau) and register (rare, archaic, obsolete)."""

from __future__ import annotations

import re

from bs4 import Tag


def detect_dialect(p_tag: Tag) -> str:
    """Detect dialect from place-name links or text patterns.

    Returns dialect name (e.g., "Niʻihau") or "".
    """
    # Check <a class="pn"> links for Niihau
    for a_tag in p_tag.find_all("a", class_="pn"):
        text = a_tag.get_text(strip=True).rstrip(".")
        if "ni" in text.lower() and "ihau" in text.lower():
            return "Niʻihau"

    # Check text patterns
    full_text = p_tag.get_text()
    if re.search(r"Ni.?ihau\.?", full_text):
        return "Niʻihau"

    return ""


def detect_register(p_tag: Tag) -> str:
    """Detect usage register markers.

    Returns "rare", "archaic", "obsolete", or "".
    """
    full_text = p_tag.get_text()

    # Check for <i>rare</i>, (rare), etc.
    for i_tag in p_tag.find_all("i"):
        i_text = i_tag.get_text(strip=True).lower()
        if i_text in ("rare", "rare."):
            return "rare"
        if i_text in ("archaic", "archaic."):
            return "archaic"
        if i_text in ("obs.", "obs", "obsolete"):
            return "obsolete"

    # Check parenthetical patterns
    if re.search(r"\(rare\)", full_text, re.IGNORECASE):
        return "rare"
    if re.search(r"\(archaic\)", full_text, re.IGNORECASE):
        return "archaic"
    if re.search(r"\(obs(?:olete)?\.?\)", full_text, re.IGNORECASE):
        return "obsolete"

    return ""
