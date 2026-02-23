"""Per-page fidelity tests for haw-h.htm (heavy hwdotted, hoʻo- causatives)."""

import pytest
from pathlib import Path
from chd.parsers.haw_eng import parse_haw_eng_page

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@pytest.fixture(scope="module")
def entries():
    filepath = RAW_DIR / "haw-h.htm"
    if not filepath.exists():
        pytest.skip("haw-h.htm not found")
    entries, ctx = parse_haw_eng_page(filepath)
    return {e.id: e for e in entries}, entries, ctx


def test_entry_count(entries):
    _, entry_list, _ = entries
    assert 7000 < len(entry_list) < 14000


def test_zero_errors(entries):
    _, _, ctx = entries
    assert len(ctx.errors) == 0


def test_has_syllable_breakdowns(entries):
    _, entry_list, _ = entries
    with_syl = sum(1 for e in entry_list if e.syllable_breakdown)
    assert with_syl > 50


def test_has_causative_examples(entries):
    _, entry_list, _ = entries
    causative = sum(1 for e in entry_list for ex in e.examples if ex.is_causative)
    assert causative > 100


def test_has_etymologies(entries):
    _, entry_list, _ = entries
    with_etym = sum(1 for e in entry_list if e.etymology)
    assert with_etym > 100
