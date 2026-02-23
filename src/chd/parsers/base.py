"""Base parser with error handling."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from bs4 import Tag

logger = logging.getLogger(__name__)


@dataclass
class ParseError:
    page: str = ""
    anchor_id: str = ""
    component: str = ""
    message: str = ""
    html_snippet: str = ""


@dataclass
class ParseContext:
    page_filename: str = ""
    letter_page: str = ""
    errors: list[ParseError] = field(default_factory=list)

    def log_error(self, anchor_id: str, component: str, message: str, element: Tag | None = None):
        snippet = str(element)[:200] if element else ""
        self.errors.append(ParseError(
            page=self.page_filename, anchor_id=anchor_id,
            component=component, message=message, html_snippet=snippet,
        ))
        logger.warning(f"[{self.page_filename}#{anchor_id}] {component}: {message}")
