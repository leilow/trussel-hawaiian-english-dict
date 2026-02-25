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


class ImageDetailPage(CHDModel):
    """Parsed image detail page (e.g. aalii.htm)."""
    filename: str = ""
    image_url: str = ""
    headword_display: str = ""
    caption: str = ""
    source_credit: str = ""
    source_link_url: str = ""
    source_link_text: str = ""


class ImageInfo(CHDModel):
    """Image metadata for illustrated entries."""
    thumbnail_url: str = ""
    full_image_url: str = ""
    source_url: str = ""
    alt_text: str = ""
    height: int = 0
    caption: str = ""
    source_credit: str = ""


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


class TopicalTopic(CHDModel):
    """A single topic from the topical page."""
    name: str = ""
    filename: str = ""
    entry_count: int = 0
    description: str = ""
    description_links: list[Link] = []


class TopicalPage(CHDModel):
    """Full parsed topical.htm page."""
    title: str = ""
    topic_count: int = 0
    topics: list[TopicalTopic] = []


class CountsData(CHDModel):
    entries_by_letter: dict[str, int] = {}
    entries_by_source: dict[str, int] = {}
    total_entries: int = 0
    raw_tables: list[dict] = []


# ─── Reference & Source Page Models ─────────────────────────────────────────


class DictionaryEdition(CHDModel):
    """A single edition of a dictionary source."""
    anchor: str = ""
    title: str = ""
    year: str = ""
    description: str = ""
    cover_images: list[str] = []
    intro_pdf_url: str = ""


class DictionarySourcePage(CHDModel):
    """Parsed sources-*.htm page."""
    filename: str = ""
    title: str = ""
    updated: str = ""
    editions: list[DictionaryEdition] = []
    preface_links: list[str] = []
    author_images: list[str] = []
    referenced_assets: list[str] = []


class WordlistEntry(CHDModel):
    """A single word in a historical wordlist."""
    number: int = 0
    list_word: str = ""
    modern_hawaiian: str = ""
    modern_hawaiian_links: list[LinkedWord] = []
    gloss: str = ""
    footnote: str = ""


class WordlistPage(CHDModel):
    """Parsed historical wordlist page."""
    filename: str = ""
    title: str = ""
    author: str = ""
    year: str = ""
    intro_text: str = ""
    sort_links: list[str] = []
    entries: list[WordlistEntry] = []
    entry_count: int = 0


class GlossSourceText(CHDModel):
    """A single source text entry from glossrefs.htm."""
    number: int = 0
    hawaiian_title: str = ""
    author_info: str = ""
    publisher: str = ""
    year: str = ""
    page_count: str = ""
    cover_image_url: str = ""
    ulukau_url: str = ""


class GlossRefsPage(CHDModel):
    """Parsed glossrefs.htm page."""
    title: str = ""
    updated: str = ""
    source_count: int = 0
    source_texts: list[GlossSourceText] = []
    referenced_assets: list[str] = []


class IndexEntry(CHDModel):
    """A single entry in the index or reverse index."""
    headword: str = ""
    anchor: str = ""
    target_page: str = ""
    target_anchor: str = ""
    pos: str = ""
    definition: str = ""
    source: str = ""  # "PE", "MK", "Andrews"


class IndexPage(CHDModel):
    """Parsed index-{letter}.htm or rev-{vowel}.htm page."""
    filename: str = ""
    page_type: str = ""  # "index" or "reverse"
    letter: str = ""
    updated: str = ""
    entry_count: int = 0
    entries: list[IndexEntry] = []
    two_letter_combos: list[str] = []
    referenced_assets: list[str] = []


class StructuralPage(CHDModel):
    """Parsed structural page (intro.htm, texts.htm, etc.)."""
    filename: str = ""
    title: str = ""
    updated: str = ""
    sections: list[dict] = []
    internal_links: list[str] = []
    external_links: list[str] = []
    referenced_assets: list[str] = []


class PrefacePage(CHDModel):
    """Parsed preface page."""
    filename: str = ""
    title: str = ""
    subtitle: str = ""
    year_edition: str = ""
    prose_html: str = ""
    preface_nav_links: list[str] = []
    images: list[str] = []
    referenced_assets: list[str] = []
