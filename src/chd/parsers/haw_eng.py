"""Parse Hawaiian-English dictionary pages (haw-*.htm).

State machine iterating flat <p> siblings in document order.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from bs4 import Tag

from chd.enums import DictSource
from chd.links import extract_word_tokens
from chd.models import Entry, Example
from chd.parsers.base import ParseContext
from chd.parsers.dialect_detector import detect_dialect, detect_register
from chd.parsers.entry_components import (
    detect_source,
    extract_cross_refs,
    extract_etymology,
    extract_grammar_refs,
    extract_hawaiian_glosses,
    extract_headword,
    find_preceding_anchor,
)
from chd.parsers.image_parser import extract_images
from chd.parsers.sense_parser import parse_senses
from chd.parsers.source_ref_parser import extract_example_source_ref
from chd.parsers.syllable_parser import extract_syllable_breakdown
from chd.preprocess import get_css_class, is_inside_seeword_table, parse_html
from chd.unicode import to_ascii

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

NUMERIC_ANCHOR_RE = re.compile(r"^\d+$")

# Loan language abbreviation map
LOAN_LANG_MAP = {
    "Eng.": "English", "Eng": "English",
    "Gr.": "Greek", "Gr": "Greek",
    "Lat.": "Latin", "Lat": "Latin",
    "Heb.": "Hebrew", "Heb": "Hebrew",
    "Sp.": "Spanish", "Sp": "Spanish",
    "Port.": "Portuguese",
    "Fr.": "French",
    "Chin.": "Chinese",
    "Jap.": "Japanese",
}


def _parse_loan_info(p_tag: Tag) -> tuple[bool, str, str]:
    """Extract loanword info from <span class="loan"> and <span class="Eng">."""
    is_loanword = False
    loan_language = ""
    loan_source = ""

    # Check for Eng marker
    if p_tag.find("span", class_="Eng"):
        is_loanword = True
        loan_language = "English"

    # Check for loan span with language info
    loan_span = p_tag.find("span", class_="loan")
    if loan_span:
        is_loanword = True
        text = loan_span.get_text(strip=True)
        # Pattern: "Gr. aetos." or "Eng."
        for abbrev, lang in LOAN_LANG_MAP.items():
            if abbrev in text:
                loan_language = lang
                # Extract source word after the abbreviation
                remainder = text.split(abbrev, 1)[-1].strip().rstrip(".")
                if remainder:
                    loan_source = remainder
                break

    return is_loanword, loan_language, loan_source


def _parse_alt_spellings(p_tag: Tag) -> list[str]:
    """Extract alternate spellings from altspell* spans."""
    spellings = []
    for cls in ("altspell", "altspellB", "altspellEH", "altspellLA", "altspellMK", "altspellOTH"):
        for span in p_tag.find_all("span", class_=cls):
            text = span.get_text(strip=True)
            if text:
                spellings.append(text)
    return spellings


def _parse_example(p_tag: Tag, from_page: str, from_anchor: str) -> Example:
    """Parse a <p class="ex"> example sentence."""
    ex = Example()

    # Detect source
    if p_tag.find("span", class_="hawexMK") or p_tag.find("span", class_="engexMK"):
        ex.source_dict = DictSource.MK

    # Hawaiian text + word tokens
    haw_span = p_tag.find("span", class_=["hawex", "hawexMK"])
    if haw_span:
        ex.hawaiian_text = haw_span.get_text()
        ex.word_tokens = extract_word_tokens(haw_span)

        # Detect causative: bold hawinentry link
        b_tag = haw_span.find("b")
        if b_tag and b_tag.find("a", class_="hawinentry"):
            ex.is_causative = True

    # English text
    eng_span = p_tag.find("span", class_=["engex", "engexMK"])
    if eng_span:
        ex.english_text = eng_span.get_text(strip=True)

    # Note
    xn_span = p_tag.find("span", class_="xn")
    if xn_span:
        ex.note = xn_span.get_text(strip=True).strip("[] ")

    # Source reference
    ref, on_num, bible_ref = extract_example_source_ref(p_tag)
    if ref:
        ex.source_ref = ref
        ex.olelo_noeau_num = on_num
        ex.bible_ref = bible_ref

    return ex


def _build_entry(
    p_tag: Tag,
    entry_type: str,
    anchor_id: str,
    letter_page: str,
    from_page: str,
    current_main: Entry | None,
    ctx: ParseContext,
) -> Entry:
    """Parse a single <p class="hw"> or <p class="hwSub"> into an Entry."""
    try:
        source = detect_source(p_tag)
        display, base, subscript, pdf_page = extract_headword(p_tag)

        entry = Entry(
            id=anchor_id,
            headword=base,
            headword_display=display,
            headword_ascii=to_ascii(base),
            subscript=subscript,
            letter_page=letter_page,
            trussel_display_type=entry_type,
            pdf_page=pdf_page,
        )

        if entry_type == "sub" and current_main:
            entry.trussel_subentry_of = current_main.id

        # Source flags
        if source == DictSource.PE:
            entry.in_pe = True
        elif source == DictSource.MK:
            entry.in_mk = True
            if p_tag.find("span", class_="addend"):
                entry.in_mk_addendum = True
        elif source == DictSource.ANDREWS:
            entry.in_andrews = True
        elif source == DictSource.EH:
            entry.is_from_eh_only = True

        # Place name
        if p_tag.find("span", class_="PN") or p_tag.find("span", class_="pn"):
            entry.in_placenames = True

        # Senses
        entry.senses = parse_senses(p_tag, source, from_page, anchor_id)

        # Etymology
        entry.etymology = extract_etymology(p_tag, from_page, anchor_id)

        # Cross-references
        entry.cross_refs = extract_cross_refs(p_tag, source, from_page, anchor_id)

        # Grammar references
        entry.grammar_refs = extract_grammar_refs(p_tag, from_page, anchor_id)

        # Hawaiian glosses
        entry.hawaiian_glosses = extract_hawaiian_glosses(p_tag)

        # Images
        entry.images = extract_images(p_tag)

        # Syllable breakdown
        entry.syllable_breakdown = extract_syllable_breakdown(p_tag)

        # Dialect & register
        entry.dialect = detect_dialect(p_tag)
        entry.usage_register = detect_register(p_tag)

        # Loanword
        is_loan, loan_lang, loan_src = _parse_loan_info(p_tag)
        entry.is_loanword = is_loan
        entry.loan_language = loan_lang
        entry.loan_source = loan_src

        # Alt spellings
        entry.alt_spellings = _parse_alt_spellings(p_tag)

        # Source tag
        entry_span = p_tag.find("span", class_="entry")
        if entry_span:
            entry.source_tag = entry_span.get_text(strip=True).strip("() ")

        # Topics from semcode
        semcode = p_tag.find("span", class_="semcode")
        if semcode:
            entry.topics = semcode.get_text(strip=True).split()

        return entry

    except Exception as e:
        ctx.log_error(anchor_id, "entry", str(e), p_tag)
        return Entry(id=anchor_id, headword="[PARSE ERROR]", letter_page=letter_page)


def parse_haw_eng_page(filepath: Path) -> tuple[list[Entry], ParseContext]:
    """Parse a single Hawaiian-English page into entries.

    Returns (entries, context_with_errors).
    """
    html = filepath.read_bytes()
    soup = parse_html(html)

    letter_page = filepath.stem.replace("haw-", "")
    from_page = filepath.name
    ctx = ParseContext(page_filename=from_page, letter_page=letter_page)

    entries: list[Entry] = []
    current_main: Entry | None = None
    current_entry: Entry | None = None

    body = soup.find("body")
    if not body:
        return entries, ctx

    for p_tag in body.find_all("p", class_=["hw", "hwSub", "ex"]):
        p_class = get_css_class(p_tag)

        if is_inside_seeword_table(p_tag):
            continue

        if p_class == "hw":
            anchor_id = find_preceding_anchor(p_tag)
            entry = _build_entry(p_tag, "main", anchor_id, letter_page, from_page, current_main, ctx)
            entries.append(entry)
            current_main = entry
            current_entry = entry

        elif p_class == "hwSub":
            anchor_id = find_preceding_anchor(p_tag)
            entry = _build_entry(p_tag, "sub", anchor_id, letter_page, from_page, current_main, ctx)
            entries.append(entry)
            current_entry = entry

        elif p_class == "ex":
            if current_entry:
                try:
                    ex = _parse_example(p_tag, from_page, current_entry.id)
                    current_entry.examples.append(ex)
                except Exception as e:
                    ctx.log_error(current_entry.id, "example", str(e), p_tag)

    return entries, ctx


def parse_all_haw_eng(raw_dir: Path = RAW_DIR) -> dict[str, tuple[list[Entry], ParseContext]]:
    """Parse all Hawaiian-English pages. Returns dict of letter → (entries, ctx)."""
    results = {}
    for f in sorted(raw_dir.glob("haw-*.htm")):
        # Skip concordance and topical pages
        if "conc" in f.name or f.name.count("-") > 1:
            continue
        letter = f.stem.replace("haw-", "")
        entries, ctx = parse_haw_eng_page(f)
        results[letter] = (entries, ctx)
    return results
