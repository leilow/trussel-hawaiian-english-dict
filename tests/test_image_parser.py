"""Tests for component parsers: image, syllable, dialect, source_ref, entry_components."""

from pathlib import Path
from chd.enums import DictSource
from chd.parsers.dialect_detector import detect_dialect, detect_register
from chd.parsers.entry_components import detect_source, extract_etymology, extract_grammar_refs, extract_hawaiian_glosses, extract_headword
from chd.parsers.image_parser import extract_images
from chd.parsers.source_ref_parser import extract_example_source_ref, parse_source_ref
from chd.parsers.syllable_parser import extract_syllable_breakdown
from chd.preprocess import parse_html

FIXTURES = Path(__file__).parent / "fixtures"

def _load_p(filename):
    html = (FIXTURES / filename).read_text()
    soup = parse_html(html)
    return soup.find("p")

# Image
def test_extract_images():
    p = _load_p("entry_image.html")
    images = extract_images(p)
    assert len(images) == 1
    assert "aalii.jpg" in images[0].thumbnail_url
    assert images[0].full_image_url == "aalii.htm"
    assert images[0].height == 45

def test_no_images():
    assert len(extract_images(_load_p("entry_pe_basic.html"))) == 0

# Syllable
def test_extract_syllable_breakdown():
    syl = extract_syllable_breakdown(_load_p("entry_image.html"))
    assert "·" in syl

def test_no_syllable():
    assert extract_syllable_breakdown(_load_p("entry_pe_basic.html")) == ""

# Dialect
def test_detect_niihau():
    assert detect_dialect(_load_p("entry_niihau.html")) == "Niʻihau"

def test_no_dialect():
    assert detect_dialect(_load_p("entry_pe_basic.html")) == ""

# Source Ref
def test_parse_source_ref_on():
    ref = parse_source_ref("(ON 1681)")
    assert ref.type == "ON" and ref.id == "1681"

def test_parse_source_ref_bible():
    ref = parse_source_ref("Hal. 3:7")
    assert ref.type == "BIBLE" and ref.id == "3:7"

def test_extract_example_source_ref():
    ref, on_num, bible = extract_example_source_ref(_load_p("example_basic.html"))
    assert ref.type == "ON" and on_num == "1681"

# Entry Components
def test_detect_source_pe():
    assert detect_source(_load_p("entry_pe_basic.html")) == DictSource.PE

def test_detect_source_mk():
    assert detect_source(_load_p("entry_niihau.html")) == DictSource.MK

def test_detect_source_andrews():
    assert detect_source(_load_p("entry_andrews.html")) == DictSource.ANDREWS

def test_extract_headword_pe():
    display, base, subscript, pdf = extract_headword(_load_p("entry_pe_basic.html"))
    assert display == "a₁" and base == "a" and subscript == "1" and pdf == "p001"

def test_extract_headword_image():
    display, base, subscript, pdf = extract_headword(_load_p("entry_image.html"))
    assert "ʻaʻaliʻi" in display and pdf == "p003"

def test_extract_etymology():
    etym = extract_etymology(_load_p("entry_bullets.html"), "haw-a.htm", "57170")
    assert etym is not None and "PCP" in etym.proto_language and "*aa" in etym.proto_form

def test_extract_grammar_refs():
    refs = extract_grammar_refs(_load_p("entry_pe_basic.html"), "haw-a.htm", "57167")
    assert len(refs) >= 1 and "4.5.1" in refs[0].section and "ulukau" in refs[0].pdf_url

def test_extract_hawaiian_glosses():
    glosses = extract_hawaiian_glosses(_load_p("entry_bullets.html"))
    assert len(glosses) >= 1
    assert "māhele" in glosses[0].gloss or "mahele" in glosses[0].gloss
