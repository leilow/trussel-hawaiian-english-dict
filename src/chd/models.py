"""Pydantic v2 data models for the CHD scraper."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from chd.enums import CrossRefType, DictSource, LinkTarget


class CHDModel(BaseModel):
    """Base model with shared config."""
    model_config = ConfigDict(use_enum_values=True)


# ─── Link Models ──────────────────────────────────────────────────────────────


class LinkedWord(CHDModel):
    """A hyperlinked word in a definition — <a class="hawinentry">."""
    surface: str = ""
    target_anchor: str = ""
    target_page: str = ""
    link_class: str = ""


class WordToken(CHDModel):
    """A hyperlinked word in an example sentence — <a class="ex">."""
    surface: str = ""
    anchor: str = ""
    target_entry: str = ""


class Link(CHDModel):
    """Universal link record for every <a href>."""
    link_class: str = ""
    href: str = ""
    text: str = ""
    resolved_url: str = ""
    from_page: str = ""
    from_entry_anchor: str = ""
    from_context: str = ""
    target_type: LinkTarget = LinkTarget.UNKNOWN
    target_page: str = ""
    target_anchor: str = ""


# ─── Entry Component Models ──────────────────────────────────────────────────


class SubDefinition(CHDModel):
    """A single bullet-point sub-definition within a sense."""
    text: str = ""
    is_figurative: bool = False
    is_rare: bool = False
    is_archaic: bool = False
    domain_codes: list[str] = []
    linked_words: list[LinkedWord] = []


class SourceRef(CHDModel):
    """Structured source citation on an example."""
    type: str = ""
    id: str = ""
    url: str = ""


class Sense(CHDModel):
    """A single POS + definition sense."""
    sense_num: int = 0
    source_dict: DictSource = DictSource.PE
    pos_raw: str = ""
    pos_hawaiian: str = ""
    pos_english: str = ""
    sub_definitions: list[SubDefinition] = []
    text: str = ""
    html: str = ""
    linked_words: list[LinkedWord] = []
    hawaiian_gloss: str = ""
    gloss_source_num: str = ""


class Example(CHDModel):
    """An example sentence or phrase."""
    hawaiian_text: str = ""
    english_text: str = ""
    note: str = ""
    word_tokens: list[WordToken] = []
    source_ref: SourceRef | None = None
    olelo_noeau_num: str = ""
    bible_ref: str = ""
    is_causative: bool = False
    source_dict: DictSource = DictSource.PE


class Etymology(CHDModel):
    """Proto-language reconstruction data."""
    raw_text: str = ""
    proto_form: str = ""
    proto_language: str = ""
    qualifier: str = ""
    meaning: str = ""
    pollex_url: str = ""


class CrossRef(CHDModel):
    """A cross-reference to another entry."""
    ref_type: str = ""
    target_headword: str = ""
    target_anchor: str = ""
    target_page: str = ""
    source_dict: DictSource = DictSource.PE


class GrammarRef(CHDModel):
    """A grammar reference link."""
    section: str = ""
    label: str = ""
    pdf_url: str = ""


class HawaiianGloss(CHDModel):
    """A Hawaiian language gloss with source reference."""
    gloss: str = ""
    source_text_id: str = ""
    source_ref: str = ""


class ImageInfo(CHDModel):
    """Image metadata for illustrated entries."""
    thumbnail_url: str = ""
    full_image_url: str = ""
    source_url: str = ""
    alt_text: str = ""
    height: int = 0


# ─── Main Entry Model ────────────────────────────────────────────────────────


class Entry(CHDModel):
    """A complete dictionary entry."""
    id: str = ""
    headword: str = ""
    headword_display: str = ""
    headword_ascii: str = ""
    subscript: str = ""
    letter_page: str = ""
    trussel_display_type: str = "main"
    trussel_subentry_of: str = ""
    pdf_page: str = ""
    in_pe: bool = False
    in_mk: bool = False
    in_mk_addendum: bool = False
    in_andrews: bool = False
    in_placenames: bool = False
    is_from_eh_only: bool = False
    senses: list[Sense] = []
    syllable_breakdown: str = ""
    examples: list[Example] = []
    cross_refs: list[CrossRef] = []
    etymology: Etymology | None = None
    grammar_refs: list[GrammarRef] = []
    hawaiian_glosses: list[HawaiianGloss] = []
    topics: list[str] = []
    is_basic_vocab: bool = False
    dialect: str = ""
    usage_register: str = ""
    images: list[ImageInfo] = []
    is_loanword: bool = False
    loan_source: str = ""
    loan_language: str = ""
    alt_spellings: list[str] = []
    source_tag: str = ""


# ─── English-Hawaiian Models ─────────────────────────────────────────────────


class EngHawTranslation(CHDModel):
    hawaiian_word: str = ""
    target_anchor: str = ""
    target_page: str = ""


class EngHawEntry(CHDModel):
    english_word: str = ""
    source: DictSource = DictSource.PE
    letter_page: str = ""
    translations: list[EngHawTranslation] = []


# ─── Concordance Models ──────────────────────────────────────────────────────


class ConcordanceInstance(CHDModel):
    word: str = ""
    word_anchor: str = ""
    hawaiian_text: str = ""
    english_text: str = ""
    note: str = ""
    parent_entry_anchor: str = ""
    parent_entry_page: str = ""
    word_tokens: list[WordToken] = []


# ─── Support Models ──────────────────────────────────────────────────────────


class Reference(CHDModel):
    abbreviation: str = ""
    anchor: str = ""
    full_text: str = ""
    url: str = ""


class CountsData(CHDModel):
    entries_by_letter: dict[str, int] = {}
    entries_by_source: dict[str, int] = {}
    total_entries: int = 0
    raw_tables: list[dict] = []
