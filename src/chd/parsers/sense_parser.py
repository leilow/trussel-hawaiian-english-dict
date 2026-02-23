"""Parse POS + definitions with bullet sub-senses."""

from __future__ import annotations

import re

from bs4 import Tag

from chd.enums import DictSource
from chd.links import extract_linked_words
from chd.models import Sense, SubDefinition
from chd.preprocess import get_css_class

POS_CLASSES = {
    "pos": DictSource.PE, "MKpos": DictSource.MK,
    "LApos": DictSource.ANDREWS, "Otherpos": DictSource.OTHER, "HIEpos": DictSource.EH,
}
DEF_CLASSES = {
    "def": DictSource.PE, "MKdef": DictSource.MK,
    "LAdef": DictSource.ANDREWS, "Otherdef": DictSource.OTHER, "HIEdef": DictSource.EH,
}

BULLET_RE = re.compile(r"•|·")
FIG_RE = re.compile(r"\bfig\b\.?", re.IGNORECASE)


def _parse_sub_definitions(text: str, html: str, element: Tag) -> list[SubDefinition]:
    parts = BULLET_RE.split(text)
    if len(parts) <= 1:
        return []
    subs = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        sub = SubDefinition(text=part)
        if FIG_RE.search(part):
            sub.is_figurative = True
        if re.search(r"\brare\b", part, re.IGNORECASE):
            sub.is_rare = True
        if re.search(r"\barchaic\b", part, re.IGNORECASE):
            sub.is_archaic = True
        subs.append(sub)
    return subs


def _extract_hawaiian_gloss(p_tag: Tag) -> tuple[str, str]:
    gloss_parts, gloss_num = [], ""
    for hs in p_tag.find_all("span", class_="hawdef"):
        text = hs.get_text(strip=True)
        if hs.find_parent("a", href=lambda h: h and "glossrefs" in h):
            gloss_num = text
        else:
            gloss_parts.append(text)
    return " ".join(gloss_parts).strip("[] ") if gloss_parts else "", gloss_num


def _extract_domain_codes(p_tag: Tag) -> list[str]:
    semcode = p_tag.find("span", class_="semcode")
    return semcode.get_text(strip=True).split() if semcode else []


def parse_senses(p_tag: Tag, source: DictSource, from_page: str, from_anchor: str) -> list[Sense]:
    if source == DictSource.ANDREWS:
        return _parse_andrews_senses(p_tag, from_page, from_anchor)
    return _parse_standard_senses(p_tag, source, from_page, from_anchor)


def _parse_standard_senses(p_tag: Tag, source: DictSource, from_page: str, from_anchor: str) -> list[Sense]:
    senses = []
    current_pos = ""
    sense_num = 0
    domain_codes = _extract_domain_codes(p_tag)
    hawaiian_gloss, gloss_num = _extract_hawaiian_gloss(p_tag)

    for child in p_tag.children:
        if not isinstance(child, Tag) or child.name != "span":
            continue
        cls = get_css_class(child)
        if cls in POS_CLASSES:
            pos_text = child.get_text(strip=True)
            if pos_text:
                current_pos = pos_text
        elif cls in DEF_CLASSES:
            def_text = child.get_text()
            sense_num += 1
            sense = Sense(
                sense_num=sense_num, source_dict=DEF_CLASSES[cls], pos_raw=current_pos,
                text=def_text.strip(), html=str(child), linked_words=extract_linked_words(child),
            )
            subs = _parse_sub_definitions(def_text, str(child), child)
            if subs:
                sense.sub_definitions = subs
            senses.append(sense)

    if senses:
        if domain_codes:
            for s in senses:
                if s.sub_definitions:
                    for sub in s.sub_definitions:
                        sub.domain_codes = domain_codes
        last = senses[-1]
        if hawaiian_gloss:
            last.hawaiian_gloss = hawaiian_gloss
        if gloss_num:
            last.gloss_source_num = gloss_num

    if not senses:
        for cls, src in DEF_CLASSES.items():
            span = p_tag.find("span", class_=cls)
            if span:
                sense_num += 1
                senses.append(Sense(
                    sense_num=sense_num, source_dict=src, pos_raw=current_pos,
                    text=span.get_text(strip=True), html=str(span),
                    linked_words=extract_linked_words(span),
                ))
                break

    return senses


def _parse_andrews_senses(p_tag: Tag, from_page: str, from_anchor: str) -> list[Sense]:
    senses = []
    current_pos = ""
    sense_num = 0
    for child in p_tag.children:
        if not isinstance(child, Tag) or child.name != "span":
            continue
        cls = get_css_class(child)
        if cls == "LApos":
            pos_text = child.get_text(strip=True)
            if pos_text:
                current_pos = pos_text
        elif cls == "LAdef":
            sense_num += 1
            senses.append(Sense(
                sense_num=sense_num, source_dict=DictSource.ANDREWS, pos_raw=current_pos,
                text=child.get_text().strip(), html=str(child),
                linked_words=extract_linked_words(child),
            ))
    return senses
