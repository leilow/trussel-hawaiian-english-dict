"""Parse headword, etymology, cross-refs, grammar refs from entry <p> tags."""

from __future__ import annotations

import re

from bs4 import NavigableString, Tag

from chd.enums import DictSource
from chd.links import classify_link, resolve_cross_ref_type
from chd.models import CrossRef, Etymology, GrammarRef, HawaiianGloss
from chd.preprocess import get_css_class
from chd.unicode import extract_subscript, strip_subscript

# Headword span class → source mapping
HEADWORD_CLASS_TO_SOURCE: dict[str, DictSource] = {
    "HwNew": DictSource.PE,
    "HwNewA": DictSource.PE,
    "MK": DictSource.MK,
    "MKA": DictSource.MK,
    "LA": DictSource.ANDREWS,
    "HIE": DictSource.EH,
    "OTH": DictSource.OTHER,
    "PN": DictSource.PE,
}

NUMERIC_ANCHOR_RE = re.compile(r"^\d+$")


def detect_source(p_tag: Tag) -> DictSource:
    """Detect the source dictionary from headword span classes."""
    for cls, source in HEADWORD_CLASS_TO_SOURCE.items():
        if p_tag.find("span", class_=cls):
            return source
    if p_tag.find("span", class_="MKcolor"):
        return DictSource.MK
    return DictSource.PE


def extract_headword(p_tag: Tag) -> tuple[str, str, str, str]:
    """Extract headword info from an entry <p> tag.

    Returns (headword_display, headword_base, subscript, pdf_page).
    """
    pdf_page = ""

    for cls in HEADWORD_CLASS_TO_SOURCE:
        hw_span = p_tag.find("span", class_=cls)
        if hw_span:
            hw_link = hw_span.find("a", class_=["hw", "hwb", "MkHw", "lalink"])
            if hw_link:
                display = hw_link.get_text(strip=True)
                href = hw_link.get("href", "")
                if href and href.endswith(".pdf"):
                    pdf_page = href.replace(".pdf", "")
            else:
                display = hw_span.get_text(strip=True)

            base = strip_subscript(display)
            subscript = extract_subscript(display)
            return display, base, subscript, pdf_page

    # Fallback
    display = p_tag.get_text(strip=True)[:50]
    return display, strip_subscript(display), extract_subscript(display), pdf_page


def extract_etymology(p_tag: Tag, from_page: str, from_anchor: str) -> Etymology | None:
    """Extract etymology from <span class="proto">."""
    proto_span = p_tag.find("span", class_="proto")
    if not proto_span:
        return None

    raw_text = proto_span.get_text(strip=True)
    etym = Etymology(raw_text=raw_text)

    # Extract POLLEX link
    pollex_link = proto_span.find("a", class_="proto")
    if pollex_link:
        etym.pollex_url = pollex_link.get("href", "")
        etym.proto_form = "*" + pollex_link.get_text(strip=True)

    # Parse proto language and qualifier from text
    text = raw_text.strip("[] ")

    # Qualifier in parentheses
    qual_match = re.match(r"\(([^)]+)\)\s*", text)
    if qual_match:
        etym.qualifier = qual_match.group(1)
        text = text[qual_match.end():]

    # Proto language (2-6 letters starting with uppercase)
    lang_match = re.match(r"([A-Z][A-Za-z()]{1,10})\s+", text)
    if lang_match:
        etym.proto_language = lang_match.group(1)
        text = text[lang_match.end():]

    # Proto form if not already from link
    if not etym.proto_form:
        form_match = re.match(r"\*(\S+)", text)
        if form_match:
            etym.proto_form = "*" + form_match.group(1).rstrip(",.")
            text = text[form_match.end():]

    # Meaning from <i> tags or remaining text
    meaning_parts = [i.get_text(strip=True) for i in proto_span.find_all("i")]
    if meaning_parts:
        etym.meaning = " ".join(meaning_parts)
    elif text.strip(",. "):
        etym.meaning = text.strip(",. ")

    return etym


def extract_cross_refs(
    p_tag: Tag,
    source: DictSource,
    from_page: str,
    from_anchor: str,
) -> list[CrossRef]:
    """Extract cross-references from See/seeMK spans and hawinentry links."""
    refs = []

    # From See/seeMK spans
    for see_span in p_tag.find_all("span", class_=["See", "seeMK"]):
        see_text = see_span.get_text(strip=True)
        ref_type = resolve_cross_ref_type(see_text) or "see"

        next_link = see_span.find_next("a", class_="hawinentry")
        if next_link and next_link.find_parent("p") == p_tag:
            href = next_link.get("href", "") or ""
            target_page = ""
            target_anchor = ""
            if "#" in href:
                parts = href.rsplit("#", 1)
                target_page = parts[0]
                target_anchor = parts[1]

            refs.append(CrossRef(
                ref_type=ref_type,
                target_headword=next_link.get_text(strip=True),
                target_anchor=target_anchor,
                target_page=target_page,
                source_dict=source,
            ))

    # Inline cross-refs from preceding text
    for a_tag in p_tag.find_all("a", class_="hawinentry"):
        hw_text = a_tag.get_text(strip=True)
        already = any(r.target_headword == hw_text for r in refs)
        if already:
            continue

        preceding_text = ""
        prev = a_tag.previous_sibling
        if prev and isinstance(prev, NavigableString):
            preceding_text = str(prev).strip()
        elif prev and isinstance(prev, Tag):
            preceding_text = prev.get_text(strip=True)

        ref_type = resolve_cross_ref_type(preceding_text)
        if ref_type:
            href = a_tag.get("href", "") or ""
            target_page = ""
            target_anchor = ""
            if "#" in href:
                parts = href.rsplit("#", 1)
                target_page = parts[0]
                target_anchor = parts[1]

            refs.append(CrossRef(
                ref_type=ref_type,
                target_headword=hw_text,
                target_anchor=target_anchor,
                target_page=target_page,
                source_dict=source,
            ))

    return refs


def extract_grammar_refs(p_tag: Tag, from_page: str, from_anchor: str) -> list[GrammarRef]:
    """Extract grammar references from <span class="gram">."""
    refs = []
    for gram_span in p_tag.find_all("span", class_="gram"):
        label = gram_span.get_text(strip=True)
        pdf_url = ""

        # Find the PDF link (usually ulukau)
        for a_tag in gram_span.find_all("a"):
            href = a_tag.get("href", "")
            if "ulukau" in href or href.endswith(".pdf"):
                pdf_url = href
                if not label:
                    label = a_tag.get_text(strip=True)
                break

        # Extract section number
        section_match = re.search(r"(\d+(?:\.\d+)+)", label)
        section = section_match.group(1) if section_match else ""

        if label or pdf_url:
            refs.append(GrammarRef(
                section=section,
                label=label.strip("() "),
                pdf_url=pdf_url,
            ))
    return refs


def extract_hawaiian_glosses(p_tag: Tag) -> list[HawaiianGloss]:
    """Extract Hawaiian language glosses from hawdef spans."""
    glosses = []
    gloss_parts = []
    gloss_num = ""

    for hs in p_tag.find_all("span", class_="hawdef"):
        text = hs.get_text(strip=True)
        parent_a = hs.find_parent("a", href=lambda h: h and "glossrefs" in h)
        if parent_a:
            gloss_num = text
        else:
            gloss_parts.append(text)

    if gloss_parts:
        glosses.append(HawaiianGloss(
            gloss=" ".join(gloss_parts).strip("[] "),
            source_text_id=gloss_num,
        ))

    return glosses


def find_preceding_anchor(p_tag: Tag) -> str:
    """Find the nearest preceding numeric anchor for a <p> tag."""
    # Check inside the <p> tag itself first
    for a in p_tag.find_all("a", attrs={"name": NUMERIC_ANCHOR_RE}):
        return a.get("name", "")

    # Check previous siblings
    node = p_tag.previous_sibling
    while node:
        if isinstance(node, Tag):
            if node.name == "a" and NUMERIC_ANCHOR_RE.match(node.get("name", "")):
                return node.get("name", "")
            anchors = node.find_all("a", attrs={"name": NUMERIC_ANCHOR_RE})
            if anchors:
                return anchors[-1].get("name", "")
        node = node.previous_sibling

    # Check parent's previous siblings
    parent = p_tag.parent
    if parent:
        node = parent.previous_sibling
        while node:
            if isinstance(node, Tag):
                if node.name == "a" and NUMERIC_ANCHOR_RE.match(node.get("name", "")):
                    return node.get("name", "")
                anchors = node.find_all("a", attrs={"name": NUMERIC_ANCHOR_RE})
                if anchors:
                    return anchors[-1].get("name", "")
            node = node.previous_sibling

    return ""
