"""Link extraction, classification, and resolution for the CHD scraper."""

from __future__ import annotations

import re
from urllib.parse import unquote, urljoin, urlparse

from bs4 import Tag

from chd.enums import CrossRefType, LinkTarget
from chd.models import Link, LinkedWord, WordToken
from chd.preprocess import get_css_class

BASE_URL = "https://trussel2.com/HAW/"

LINK_CLASS_MAP: dict[str, LinkTarget] = {
    "hawinentry": LinkTarget.INTERNAL_ENTRY,
    "ex": LinkTarget.CONCORDANCE,
    "hw": LinkTarget.PDF,
    "hwb": LinkTarget.PDF,
    "proto": LinkTarget.POLLEX,
    "refs": LinkTarget.REFERENCE,
    "bc": LinkTarget.BIBLE_CONC,
    "MkHw": LinkTarget.SELF_LINK,
    "lalink": LinkTarget.SELF_LINK,
    "pn": LinkTarget.PLACE_NAME,
    "t": LinkTarget.TOPICAL,
    "fw": LinkTarget.INTERNAL_ENTRY,
    "cf": LinkTarget.INTERNAL_ENTRY,
    "ex2": LinkTarget.INTERNAL_ENTRY,
    "more": LinkTarget.CONCORDANCE,
    "dot": LinkTarget.INTERNAL_ENTRY,
    "dotMK": LinkTarget.INTERNAL_ENTRY,
}

CROSS_REF_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"same\s+as\b", re.IGNORECASE), CrossRefType.SAME_AS),
    (re.compile(r"redup(?:lication|\.)\s+of\b", re.IGNORECASE), CrossRefType.REDUP_OF),
    (re.compile(r"var(?:iant|\.)\s+of\b", re.IGNORECASE), CrossRefType.VAR_OF),
    (re.compile(r"pas(?:sive)?/imp(?:erative)?(?:\.)?\s+of\b", re.IGNORECASE), CrossRefType.PAS_IMP_OF),
    (re.compile(r"var(?:iant|\.)\s+spelling\s+(?:of\b)?", re.IGNORECASE), CrossRefType.VAR_SPELLING_OF),
    (re.compile(r"short\s+for\b", re.IGNORECASE), CrossRefType.SHORT_FOR),
    (re.compile(r"similar\s+to\b", re.IGNORECASE), CrossRefType.SIMILAR_TO),
    (re.compile(r"plural\s+of\b", re.IGNORECASE), CrossRefType.PLURAL_OF),
    (re.compile(r"a\s+variety\s+of\b", re.IGNORECASE), CrossRefType.A_VARIETY_OF),
    (re.compile(r"\bcf\.?\s*", re.IGNORECASE), CrossRefType.CF),
    (re.compile(r"\bsee\s+also\b", re.IGNORECASE), CrossRefType.SEE_ALSO),
    (re.compile(r"\bsee\b", re.IGNORECASE), CrossRefType.SEE),
    (re.compile(r"\balso\b", re.IGNORECASE), CrossRefType.ALSO),
]


def resolve_cross_ref_type(text: str) -> str:
    """Determine cross-reference type from text preceding a link."""
    text = text.strip()
    for pattern, ref_type in CROSS_REF_PATTERNS:
        if pattern.search(text):
            return ref_type.value
    return ""


def _classify_by_heuristic(href: str, resolved: str) -> LinkTarget:
    if not href:
        return LinkTarget.UNKNOWN
    parsed = urlparse(resolved)
    host = parsed.hostname or ""
    path = parsed.path.lower()
    if "pollex.org" in host:
        return LinkTarget.POLLEX
    if "ulukau.org" in host and "grammar" in path:
        return LinkTarget.GRAMMAR
    if "ulukau.org" in host and "pepn" in path:
        return LinkTarget.PLACE_NAME
    if "baibala" in href.lower():
        return LinkTarget.BIBLE_CONC
    if href.endswith(".pdf"):
        return LinkTarget.PDF
    if "glossrefs" in href.lower():
        return LinkTarget.GLOSSREFS
    if "refs.htm" in href.lower():
        return LinkTarget.REFERENCE
    if "conc-" in href.lower() or "conc_" in href.lower():
        return LinkTarget.CONCORDANCE
    if re.match(r"haw-\w+\.htm", href) or re.match(r"eng-\w+\.htm", href):
        return LinkTarget.INTERNAL_ENTRY
    base_host = urlparse(BASE_URL).hostname
    if host and host != base_host:
        return LinkTarget.EXTERNAL
    return LinkTarget.UNKNOWN


def _parse_target(href: str, resolved: str) -> tuple[str, str]:
    if not href:
        return "", ""
    for url in (resolved, href):
        if "#" in url:
            page_part, anchor = url.rsplit("#", 1)
            page = page_part.rsplit("/", 1)[-1] if "/" in page_part else page_part
            return page, unquote(anchor)
    page = resolved.rsplit("/", 1)[-1] if "/" in resolved else resolved
    return page, ""


def classify_link(
    a_tag: Tag, from_page: str = "", from_anchor: str = "", from_context: str = "",
) -> Link:
    """Classify an <a> tag into a full Link record."""
    href = a_tag.get("href", "") or ""
    text = a_tag.get_text(strip=True)
    link_class = get_css_class(a_tag)
    resolved = urljoin(BASE_URL + from_page, href) if href else ""

    if link_class in LINK_CLASS_MAP:
        target_type = LINK_CLASS_MAP[link_class]
        if link_class == "refs" and href:
            if "grammar" in href.lower() or "ulukau" in href.lower():
                target_type = LinkTarget.GRAMMAR
            elif "baibala" in href.lower():
                target_type = LinkTarget.BIBLE_CONC
    else:
        target_type = _classify_by_heuristic(href, resolved)

    target_page, target_anchor = _parse_target(href, resolved)
    return Link(
        link_class=link_class, href=href, text=text, resolved_url=resolved,
        from_page=from_page, from_entry_anchor=from_anchor, from_context=from_context,
        target_type=target_type, target_page=target_page, target_anchor=target_anchor,
    )


def extract_all_links(
    element: Tag, from_page: str = "", from_anchor: str = "", from_context: str = "",
) -> list[Link]:
    return [classify_link(a, from_page, from_anchor, from_context) for a in element.find_all("a", href=True)]


def extract_linked_words(element: Tag) -> list[LinkedWord]:
    """Extract all <a class="hawinentry"> as LinkedWord records."""
    words = []
    for a_tag in element.find_all("a", class_="hawinentry"):
        href = a_tag.get("href", "") or ""
        target_page, target_anchor = _parse_target(href, urljoin(BASE_URL, href))
        words.append(LinkedWord(
            surface=a_tag.get_text(strip=True),
            target_anchor=target_anchor, target_page=target_page, link_class="hawinentry",
        ))
    return words


def extract_word_tokens(element: Tag) -> list[WordToken]:
    """Extract all <a class="ex"> as WordToken records."""
    tokens = []
    for a_tag in element.find_all("a", class_="ex"):
        href = a_tag.get("href", "") or ""
        _, anchor = _parse_target(href, urljoin(BASE_URL, href))
        tokens.append(WordToken(surface=a_tag.get_text(strip=True), anchor=anchor))
    return tokens
