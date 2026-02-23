"""Tests for chd.preprocess module."""

from chd.preprocess import fix_unclosed_p_tags, get_css_class, is_inside_seeword_table, parse_html

def test_fix_unclosed_p_tags():
    assert "</p><p" in fix_unclosed_p_tags('<p class="hw">e1<p class="ex">ex1')

def test_parse_html_unclosed_p():
    soup = parse_html('<html><body><p class="hw">e1<p class="ex">ex1<p class="hw">e2</body></html>')
    assert len(soup.find("body").find_all("p", class_="hw")) == 2

def test_get_css_class():
    soup = parse_html('<span class="pos">nvi.</span>')
    assert get_css_class(soup.find("span")) == "pos"

def test_is_inside_seeword_table():
    html = '<html><body><table bgcolor="cornsilk"><tr><td><p class="hw">skip</p></td></tr></table><p class="hw">keep</p></body></html>'
    soup = parse_html(html)
    ps = soup.find_all("p", class_="hw")
    assert is_inside_seeword_table(ps[0]) is True
    assert is_inside_seeword_table(ps[1]) is False
