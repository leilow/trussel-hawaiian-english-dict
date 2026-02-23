"""Parse English-Hawaiian dictionary pages (eng-*.htm)."""

from __future__ import annotations

from pathlib import Path

from bs4 import Tag

from chd.enums import DictSource
from chd.models import EngHawEntry, EngHawTranslation
from chd.preprocess import parse_html

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"


def _parse_eng_haw_entry(p_tag: Tag, letter_page: str) -> EngHawEntry | None:
    eng_word_span = p_tag.find("span", class_="EngWord")
    eng_word_mk_span = p_tag.find("span", class_="EngWordMK")

    if eng_word_span:
        english_word = eng_word_span.get_text(strip=True)
        source = DictSource.PE
    elif eng_word_mk_span:
        english_word = eng_word_mk_span.get_text(strip=True)
        source = DictSource.MK
    else:
        return None

    entry = EngHawEntry(english_word=english_word, source=source, letter_page=letter_page)

    for def_span in p_tag.find_all("span", class_=["engdef", "engdefMK"]):
        for a_tag in def_span.find_all("a", class_="ex2"):
            href = a_tag.get("href", "") or ""
            target_page, target_anchor = "", ""
            if "#" in href:
                parts = href.rsplit("#", 1)
                target_page = parts[0]
                target_anchor = parts[1]
            entry.translations.append(EngHawTranslation(
                hawaiian_word=a_tag.get_text(strip=True),
                target_anchor=target_anchor,
                target_page=target_page,
            ))

    return entry


def parse_eng_haw_page(filepath: Path) -> list[EngHawEntry]:
    html = filepath.read_bytes()
    soup = parse_html(html, fix_p_tags=True)
    letter_page = filepath.stem.replace("eng-", "")
    entries = []
    body = soup.find("body")
    if not body:
        return entries
    for p_tag in body.find_all("p", class_="hw"):
        entry = _parse_eng_haw_entry(p_tag, letter_page)
        if entry:
            entries.append(entry)
    return entries


def parse_all_eng_haw(raw_dir: Path = RAW_DIR) -> dict[str, list[EngHawEntry]]:
    results = {}
    for f in sorted(raw_dir.glob("eng-*.htm")):
        letter = f.stem.replace("eng-", "")
        entries = parse_eng_haw_page(f)
        results[letter] = entries
    return results
