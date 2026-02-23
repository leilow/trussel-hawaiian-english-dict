"""Per-page fidelity tests for haw-e.htm (smaller page, regression baseline)."""

import pytest
from pathlib import Path
from chd.parsers.haw_eng import parse_haw_eng_page

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@pytest.fixture(scope="module")
def entries():
    filepath = RAW_DIR / "haw-e.htm"
    if not filepath.exists():
        pytest.skip("haw-e.htm not found")
    entries, ctx = parse_haw_eng_page(filepath)
    return {e.id: e for e in entries}, entries, ctx


def test_entry_count(entries):
    _, entry_list, _ = entries
    assert 500 < len(entry_list) < 1500


def test_zero_errors(entries):
    _, _, ctx = entries
    assert len(ctx.errors) == 0


def test_has_main_and_sub(entries):
    _, entry_list, _ = entries
    main = sum(1 for e in entry_list if e.trussel_display_type == "main")
    sub = sum(1 for e in entry_list if e.trussel_display_type == "sub")
    assert main > 0
    assert sub > 0


def test_has_examples(entries):
    _, entry_list, _ = entries
    total_ex = sum(len(e.examples) for e in entry_list)
    assert total_ex > 50


def test_has_etymologies(entries):
    _, entry_list, _ = entries
    with_etym = sum(1 for e in entry_list if e.etymology)
    assert with_etym > 10
