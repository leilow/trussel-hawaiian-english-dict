"""Per-page fidelity tests for haw-k.htm (largest page, ~12K entries)."""

import pytest
from pathlib import Path
from chd.parsers.haw_eng import parse_haw_eng_page

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@pytest.fixture(scope="module")
def entries():
    filepath = RAW_DIR / "haw-k.htm"
    if not filepath.exists():
        pytest.skip("haw-k.htm not found")
    entries, ctx = parse_haw_eng_page(filepath)
    return {e.id: e for e in entries}, entries, ctx


def test_entry_count(entries):
    _, entry_list, _ = entries
    assert 8000 < len(entry_list) < 15000


def test_zero_errors(entries):
    _, _, ctx = entries
    assert len(ctx.errors) == 0


def test_has_images(entries):
    _, entry_list, _ = entries
    with_images = sum(1 for e in entry_list if e.images)
    assert with_images > 10


def test_has_loanwords(entries):
    _, entry_list, _ = entries
    loanwords = sum(1 for e in entry_list if e.is_loanword)
    assert loanwords > 20


def test_has_cross_refs(entries):
    _, entry_list, _ = entries
    total_xrefs = sum(len(e.cross_refs) for e in entry_list)
    assert total_xrefs > 500


def test_has_word_tokens(entries):
    _, entry_list, _ = entries
    with_tokens = sum(1 for e in entry_list for ex in e.examples if ex.word_tokens)
    assert with_tokens > 200


def test_variety_of_sources(entries):
    _, entry_list, _ = entries
    pe = sum(1 for e in entry_list if e.in_pe)
    mk = sum(1 for e in entry_list if e.in_mk)
    andrews = sum(1 for e in entry_list if e.in_andrews)
    assert pe > 3000
    assert mk > 500
    assert andrews > 500
