"""HTML preprocessing for CHD pages."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag


def fix_unclosed_p_tags(html: str) -> str:
    """Insert </p> before every <p to force flat sibling structure."""
    return re.sub(r"(?=<p[\s>])", "</p>", html)


def parse_html(html: str | bytes, fix_p_tags: bool = True) -> BeautifulSoup:
    """Parse HTML with lxml, optionally fixing unclosed <p> tags."""
    if isinstance(html, bytes):
        html = html.decode("utf-8", errors="replace")
    if fix_p_tags:
        html = fix_unclosed_p_tags(html)
    return BeautifulSoup(html, "lxml")


def find_content_area(soup: BeautifulSoup) -> Tag | None:
    """Find the main content <body> tag."""
    return soup.find("body")


def is_inside_seeword_table(element: Tag) -> bool:
    """Check if an element is inside a seeword navigation box (cornsilk table)."""
    parent = element.parent
    while parent:
        if parent.name == "table":
            bg = (parent.get("bgcolor") or "").lower()
            return bg == "cornsilk"
        parent = parent.parent
    return False


def get_css_class(tag: Tag) -> str:
    """Get the first CSS class of a tag, or empty string."""
    classes = tag.get("class", [])
    if isinstance(classes, list) and classes:
        return classes[0]
    if isinstance(classes, str):
        return classes
    return ""
