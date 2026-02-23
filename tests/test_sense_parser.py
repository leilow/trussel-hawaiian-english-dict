"""Tests for chd.parsers.sense_parser."""

from pathlib import Path
from chd.enums import DictSource
from chd.parsers.sense_parser import parse_senses
from chd.preprocess import parse_html

FIXTURES = Path(__file__).parent / "fixtures"

def _load_p(filename):
    html = (FIXTURES / filename).read_text()
    soup = parse_html(html)
    return soup.find("p")

def test_pe_basic_sense():
    p = _load_p("entry_pe_basic.html")
    senses = parse_senses(p, DictSource.PE, "haw-a.htm", "57167")
    assert len(senses) >= 1
    assert senses[0].pos_raw == "prep."
    assert "of, acquired by" in senses[0].text
    assert len(senses[0].linked_words) >= 2

def test_bullet_sub_definitions():
    p = _load_p("entry_bullets.html")
    senses = parse_senses(p, DictSource.PE, "haw-a.htm", "57170")
    assert len(senses) >= 1
    s = senses[0]
    assert s.pos_raw == "nvi."
    assert len(s.sub_definitions) >= 2
    assert "jaw" in s.sub_definitions[0].text
    assert s.sub_definitions[1].is_figurative

def test_bullet_hawaiian_gloss():
    p = _load_p("entry_bullets.html")
    senses = parse_senses(p, DictSource.PE, "haw-a.htm", "57170")
    last = senses[-1]
    assert "māhele" in last.hawaiian_gloss or "mahele" in last.hawaiian_gloss

def test_andrews_multi_pos():
    p = _load_p("entry_andrews.html")
    senses = parse_senses(p, DictSource.ANDREWS, "haw-a.htm", "106357")
    assert len(senses) >= 3
    assert senses[0].pos_raw == "s."
    assert "jawbone" in senses[0].text
    assert senses[1].pos_raw == "v."
    assert senses[2].pos_raw == "adj."

def test_mk_sense():
    p = _load_p("entry_niihau.html")
    senses = parse_senses(p, DictSource.MK, "haw-a.htm", "75478")
    assert len(senses) >= 1
    assert "sentence" in senses[0].text

def test_domain_codes():
    p = _load_p("entry_bullets.html")
    senses = parse_senses(p, DictSource.PE, "haw-a.htm", "57170")
    has_bod = any("BOD" in sub.domain_codes for s in senses for sub in s.sub_definitions)
    assert has_bod
