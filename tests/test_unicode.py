"""Tests for chd.unicode module."""

from chd.unicode import extract_subscript, normalize_okina, strip_subscript, subscript_to_display, to_ascii


def test_strip_subscript_single():
    assert strip_subscript("ā₁") == "ā"

def test_strip_subscript_multi():
    assert strip_subscript("ā₁₂") == "ā"

def test_strip_subscript_none():
    assert strip_subscript("ā") == "ā"

def test_extract_subscript_single():
    assert extract_subscript("ā₁") == "1"

def test_extract_subscript_multi():
    assert extract_subscript("ā₁₂") == "12"

def test_extract_subscript_none():
    assert extract_subscript("ā") == ""

def test_normalize_okina_left_quote():
    assert normalize_okina("\u2018ōlelo") == "ʻōlelo"

def test_normalize_okina_right_quote():
    assert normalize_okina("\u2019ōlelo") == "ʻōlelo"

def test_to_ascii_okina():
    assert to_ascii("ʻōlelo") == "olelo"

def test_to_ascii_niihau():
    assert to_ascii("Niʻihau") == "Niihau"

def test_to_ascii_all_macrons():
    assert to_ascii("āēīōū") == "aeiou"

def test_subscript_to_display():
    assert subscript_to_display(1) == "₁"
    assert subscript_to_display(12) == "₁₂"
