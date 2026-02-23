"""Parse source references on examples (ON nums, Bible refs, etc.)."""

from __future__ import annotations

import re

from bs4 import Tag

from chd.models import SourceRef

# Pattern: (ON 1681), (Kel. 33), (Malo 180), etc.
SOURCE_REF_RE = re.compile(r"\(?\s*(\w+)\.?\s+(\d+(?:[:.]\d+)?)\s*\)?")

# Known source types and their full names
SOURCE_TYPES = {
    "ON": "ON",  # Olelo Noeau
    "Kel": "KEP",  # Kepelino
    "Kep": "KEP",
    "FOR": "FOR",  # Fornander
    "Malo": "Malo",
    "Hal": "BIBLE",  # Psalms (Halelu)
    "Kin": "BIBLE",  # Genesis (Kinohi)
    "Oih": "BIBLE",  # Acts (Oihana)
    "Mat": "BIBLE",  # Matthew (Mataio)
    "Mar": "BIBLE",  # Mark (Mareko)
    "Luk": "BIBLE",  # Luke (Luka)
    "Ioa": "BIBLE",  # John (Ioane)
    "Rom": "BIBLE",  # Romans (Roma)
    "Isa": "BIBLE",  # Isaiah (Isaia)
    "Kan": "BIBLE",  # Numbers (Kanawailua)
    "Ier": "BIBLE",  # Jeremiah
    "Sol": "BIBLE",  # Song of Solomon
    "Puk": "BIBLE",  # Exodus (Pukaana)
    "Nah": "BIBLE",  # Nahum
    "Ios": "BIBLE",  # Joshua
    "Eset": "BIBLE",  # Esther
    "Dan": "BIBLE",  # Daniel
    "Epeso": "BIBLE",  # Ephesians
}

BIBLE_BOOKS = {k for k, v in SOURCE_TYPES.items() if v == "BIBLE"}


def parse_source_ref(text: str) -> SourceRef | None:
    """Parse a source reference string like '(ON 1681)' or '(Hal. 3:7)'."""
    text = text.strip("() ")
    match = SOURCE_REF_RE.match(text)
    if not match:
        return None

    abbrev = match.group(1)
    ref_id = match.group(2)
    ref_type = SOURCE_TYPES.get(abbrev, abbrev)

    return SourceRef(type=ref_type, id=ref_id)


def extract_example_source_ref(p_tag: Tag) -> tuple[SourceRef | None, str, str]:
    """Extract source ref from an example <p> tag.

    Returns (source_ref, olelo_noeau_num, bible_ref).
    """
    exsrc_span = p_tag.find("span", class_="exsource")
    if not exsrc_span:
        return None, "", ""

    text = exsrc_span.get_text(strip=True)
    ref = parse_source_ref(text)
    if not ref:
        return None, "", ""

    # Extract URL if present
    a_tag = exsrc_span.find("a")
    if a_tag:
        ref.url = a_tag.get("href", "")

    olelo_noeau_num = ""
    bible_ref = ""

    if ref.type == "ON":
        olelo_noeau_num = ref.id
    elif ref.type == "BIBLE":
        bible_ref = text.strip("() ")

    return ref, olelo_noeau_num, bible_ref
