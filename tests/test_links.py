"""Tests for chd.links module."""

from bs4 import BeautifulSoup
from chd.enums import LinkTarget
from chd.links import classify_link, extract_linked_words, extract_word_tokens, resolve_cross_ref_type

def _make_a(html):
    return BeautifulSoup(html, "lxml").find("a")

def test_classify_hawinentry():
    link = classify_link(_make_a('<a class="hawinentry" href="haw-k.htm#kau">kau</a>'), "haw-a.htm", "57179", "definition")
    assert link.target_type == LinkTarget.INTERNAL_ENTRY
    assert link.target_anchor == "kau"

def test_classify_concordance_ex():
    link = classify_link(_make_a('<a class="ex" href="haw-conc-a.htm#aloha">aloha</a>'))
    assert link.target_type == LinkTarget.CONCORDANCE

def test_classify_pdf():
    link = classify_link(_make_a('<a class="hw" href="p001.pdf">ʻā₁</a>'))
    assert link.target_type == LinkTarget.PDF

def test_classify_pollex():
    link = classify_link(_make_a('<a class="proto" href="http://pollex.org.nz/entry/kaha">kaha</a>'))
    assert link.target_type == LinkTarget.POLLEX

def test_classify_grammar():
    link = classify_link(_make_a('<a class="refs" href="http://www.ulukau.org/elib/grammar/doc89.pdf">(Gram. 6.6.3)</a>'))
    assert link.target_type == LinkTarget.GRAMMAR

def test_classify_bible_conc():
    link = classify_link(_make_a('<a class="bc" href="baibala/baibala-conc-a.htm#aloha">bc</a>'))
    assert link.target_type == LinkTarget.BIBLE_CONC

def test_classify_glossrefs_heuristic():
    link = classify_link(_make_a('<a href="glossrefs.htm#14">₁₄</a>'))
    assert link.target_type == LinkTarget.GLOSSREFS

def test_resolve_cross_ref_same_as():
    assert resolve_cross_ref_type("same as") == "same as"

def test_resolve_cross_ref_redup():
    assert resolve_cross_ref_type("redup. of") == "redup. of"

def test_resolve_cross_ref_see():
    assert resolve_cross_ref_type("see") == "see"

def test_resolve_cross_ref_no_match():
    assert resolve_cross_ref_type("random text") == ""

def test_extract_linked_words():
    html = '<span class="def">This <a class="hawinentry" href="haw-a.htm#a">a</a> and <a class="hawinentry" href="haw-k.htm#kau">kau</a></span>'
    span = BeautifulSoup(html, "lxml").find("span")
    words = extract_linked_words(span)
    assert len(words) == 2
    assert words[0].surface == "a"
    assert words[1].surface == "kau"

def test_extract_word_tokens():
    html = '<span class="hawex"><a class="ex" href="haw-conc-a.htm#a">a</a> <a class="ex" href="haw-conc-h.htm#hiki">hiki</a></span>'
    span = BeautifulSoup(html, "lxml").find("span")
    tokens = extract_word_tokens(span)
    assert len(tokens) == 2
    assert tokens[0].surface == "a"
    assert tokens[1].anchor == "hiki"
