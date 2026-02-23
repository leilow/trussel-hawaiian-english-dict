"""Per-page fidelity tests for haw-a.htm.

These assertions are verified by visual inspection of the rendered HTML page.
"""

import pytest
from pathlib import Path
from chd.parsers.haw_eng import parse_haw_eng_page

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@pytest.fixture(scope="module")
def entries():
    filepath = RAW_DIR / "haw-a.htm"
    if not filepath.exists():
        pytest.skip("haw-a.htm not found")
    entries, ctx = parse_haw_eng_page(filepath)
    return {e.id: e for e in entries}, entries


def _by_id(entries_tuple, anchor_id):
    entries_map, _ = entries_tuple
    return entries_map.get(anchor_id)


# ─── Entry Count ──────────────────────────────────────────────────────────────

def test_entry_count(entries):
    _, entry_list = entries
    assert 3000 < len(entry_list) < 6000


# ─── a₁ (PE prep.) ───────────────────────────────────────────────────────────

def test_a1_headword(entries):
    e = _by_id(entries, "57167")
    assert e is not None
    assert e.headword_display == "a₁"
    assert e.subscript == "1"
    assert e.pdf_page == "p001"
    assert e.in_pe is True

def test_a1_senses(entries):
    e = _by_id(entries, "57167")
    assert len(e.senses) >= 1
    assert e.senses[0].pos_raw == "prep."
    assert "of, acquired by" in e.senses[0].text

def test_a1_linked_words(entries):
    e = _by_id(entries, "57167")
    assert len(e.senses[0].linked_words) >= 2  # a, kaʻu, kāna

def test_a1_grammar_refs(entries):
    e = _by_id(entries, "57167")
    assert len(e.grammar_refs) >= 1


# ─── ā₁ (PE nvi. with bullets) ───────────────────────────────────────────────

def test_aa1_headword(entries):
    e = _by_id(entries, "57170")
    assert e is not None
    assert "ā" in e.headword
    assert e.senses[0].pos_raw == "nvi."

def test_aa1_bullets(entries):
    e = _by_id(entries, "57170")
    s = e.senses[0]
    assert len(s.sub_definitions) >= 2
    assert "jaw" in s.sub_definitions[0].text

def test_aa1_etymology(entries):
    e = _by_id(entries, "57170")
    assert e.etymology is not None
    assert "PCP" in e.etymology.proto_language

def test_aa1_hawaiian_gloss(entries):
    e = _by_id(entries, "57170")
    assert len(e.hawaiian_glosses) >= 1
    assert "māhele" in e.hawaiian_glosses[0].gloss or "mahele" in e.hawaiian_glosses[0].gloss

def test_aa1_topics(entries):
    e = _by_id(entries, "57170")
    assert "BOD" in e.topics

def test_aa1_examples(entries):
    e = _by_id(entries, "57170")
    assert len(e.examples) >= 2
    # Should have a causative example
    assert any(ex.is_causative for ex in e.examples)


# ─── MK sub-entry ────────────────────────────────────────────────────────────

def test_mk_subentry(entries):
    e = _by_id(entries, "75479")
    assert e is not None
    assert e.in_mk is True
    assert e.trussel_display_type == "sub"

def test_mk_subentry_parent(entries):
    e = _by_id(entries, "75479")
    assert e.trussel_subentry_of != ""


# ─── Andrews multi-POS ───────────────────────────────────────────────────────

def test_andrews_multi_pos(entries):
    e = _by_id(entries, "106352")
    assert e is not None
    assert e.in_andrews is True
    assert len(e.senses) >= 3


# ─── Niʻihau dialect ─────────────────────────────────────────────────────────

def test_niihau_dialect(entries):
    e = _by_id(entries, "75478")
    assert e is not None
    assert e.dialect == "Niʻihau"


# ─── ʻaʻaliʻi (image entry) ──────────────────────────────────────────────────

def test_aalii_image(entries):
    e = _by_id(entries, "57266")
    assert e is not None
    assert len(e.images) >= 1
    assert "aalii.jpg" in e.images[0].thumbnail_url

def test_aalii_syllable(entries):
    e = _by_id(entries, "57266")
    assert "·" in e.syllable_breakdown


# ─── Loanword ─────────────────────────────────────────────────────────────────

def test_loanword(entries):
    e = _by_id(entries, "57356")
    assert e is not None
    assert e.is_loanword is True
    assert e.loan_language == "Greek"
    assert e.loan_source == "aetos"


# ─── Example with ON source ref ──────────────────────────────────────────────

def test_example_source_ref(entries):
    """Find an entry with an ON source reference in its examples."""
    _, entry_list = entries
    found = False
    for e in entry_list:
        for ex in e.examples:
            if ex.olelo_noeau_num:
                found = True
                assert ex.source_ref is not None
                assert ex.source_ref.type == "ON"
                break
        if found:
            break
    assert found, "No example with ON source ref found"


# ─── Word tokens in examples ─────────────────────────────────────────────────

def test_word_tokens_populated(entries):
    """At least some examples should have word tokens."""
    _, entry_list = entries
    with_tokens = sum(
        1 for e in entry_list for ex in e.examples if ex.word_tokens
    )
    assert with_tokens > 100
