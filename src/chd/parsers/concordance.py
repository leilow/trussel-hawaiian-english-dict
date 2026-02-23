"""Parse Concordance pages (haw-conc-*.htm and overflow con-*.htm pages)."""

from __future__ import annotations

from pathlib import Path

from bs4 import Tag

from chd.links import extract_word_tokens
from chd.models import ConcordanceInstance, WordToken
from chd.preprocess import parse_html

RAW_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"


def parse_concordance_page(filepath: Path) -> list[ConcordanceInstance]:
    html = filepath.read_bytes()
    soup = parse_html(html, fix_p_tags=False)
    instances = []

    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue
            if tds[0].get("colspan"):
                continue

            inst = ConcordanceInstance()

            # Cell 0: headword
            fw_link = tds[0].find("a", class_="fw")
            if fw_link:
                inst.word = fw_link.get_text(strip=True)
                href = fw_link.get("href", "") or ""
                if "#" in href:
                    inst.word_anchor = href.rsplit("#", 1)[1]
            else:
                inst.word = tds[0].get_text(strip=True)

            # Cell 1: Hawaiian sentence with word tokens
            inst.hawaiian_text = tds[1].get_text()
            inst.word_tokens = extract_word_tokens(tds[1])

            # Cell 2: English translation + note
            eng_span = tds[2].find("span", class_="EngEx")
            inst.english_text = eng_span.get_text(strip=True) if eng_span else tds[2].get_text(strip=True)
            xn_span = tds[2].find("span", class_="xn")
            if xn_span:
                inst.note = xn_span.get_text(strip=True).strip("[] ")

            # Cell 3: parent entry link
            cf_link = tds[3].find("a", class_="cf")
            if cf_link:
                href = cf_link.get("href", "") or ""
                if "#" in href:
                    parts = href.rsplit("#", 1)
                    inst.parent_entry_page = parts[0]
                    inst.parent_entry_anchor = parts[1]

            if inst.word:
                instances.append(inst)

    return instances


def parse_all_concordance(raw_dir: Path = RAW_DIR) -> dict[str, list[ConcordanceInstance]]:
    results = {}
    for f in sorted(raw_dir.glob("haw-conc-*.htm")):
        letter = f.stem.replace("haw-conc-", "")
        instances = parse_concordance_page(f)
        results[letter] = results.get(letter, []) + instances
    for f in sorted(raw_dir.glob("con-*.htm")):
        instances = parse_concordance_page(f)
        letter = f.stem.replace("con-", "").split("-")[0][:1]
        results[letter] = results.get(letter, []) + instances
    return results
