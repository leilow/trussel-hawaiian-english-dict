"""Unicode utilities for Hawaiian text processing."""

from __future__ import annotations

import re

SUBSCRIPT_DIGITS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
SUBSCRIPT_RE = re.compile(r"[₀₁₂₃₄₅₆₇₈₉]+$")

OKINA_VARIANTS = ["\u2018", "\u2019", "\u0060", "\u00B4", "\u0027"]

KAHAKO_MAP = {
    "ā": "a", "ē": "e", "ī": "i", "ō": "o", "ū": "u",
    "Ā": "A", "Ē": "E", "Ī": "I", "Ō": "O", "Ū": "U",
}


def strip_subscript(text: str) -> str:
    """Remove trailing Unicode subscript digits. 'ā₁' → 'ā'"""
    return SUBSCRIPT_RE.sub("", text).rstrip()


def extract_subscript(text: str) -> str:
    """Extract trailing subscript as plain string. 'ā₁' → '1'"""
    match = SUBSCRIPT_RE.search(text)
    return match.group().translate(SUBSCRIPT_DIGITS) if match else ""


def normalize_okina(text: str) -> str:
    """Normalize ʻokina variants to U+02BB."""
    for variant in OKINA_VARIANTS:
        text = text.replace(variant, "\u02BB")
    return text


def to_ascii(text: str) -> str:
    """Strip all Hawaiian diacriticals for URL/anchor matching."""
    result = text.replace("\u02BB", "")
    for accented, plain in KAHAKO_MAP.items():
        result = result.replace(accented, plain)
    return result


def subscript_to_display(num: int | str) -> str:
    """Convert plain number to Unicode subscript. 1 → '₁'"""
    return str(num).translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉"))
