"""Enums for the CHD scraper."""

from enum import Enum


class DictSource(str, Enum):
    """Source dictionary identifier."""

    PE = "PE"  # Pukui & Elbert 1986
    MK = "MK"  # Māmaka Kaiao 2003/2010
    ANDREWS = "Andrews"  # Andrews 1865
    EH = "EH"  # PE English-Hawaiian section
    OTHER = "Other"  # NKE, Kaua, etc.


class LinkTarget(str, Enum):
    """Classification of where a link points."""

    INTERNAL_ENTRY = "internal_entry"
    CONCORDANCE = "concordance"
    PDF = "pdf"
    POLLEX = "pollex"
    GRAMMAR = "grammar"
    BIBLE_CONC = "bible_conc"
    PLACE_NAME = "place_name"
    TOPICAL = "topical"
    REFERENCE = "reference"
    EXTERNAL = "external"
    GLOSSREFS = "glossrefs"
    SELF_LINK = "self_link"
    UNKNOWN = "unknown"


class CrossRefType(str, Enum):
    """Types of cross-references between entries."""

    SAME_AS = "same as"
    REDUP_OF = "redup. of"
    VAR_OF = "var. of"
    PAS_IMP_OF = "pas/imp. of"
    VAR_SPELLING_OF = "var. spelling of"
    SHORT_FOR = "short for"
    SIMILAR_TO = "similar to"
    PLURAL_OF = "plural of"
    A_VARIETY_OF = "a variety of"
    CF = "cf."
    SEE_ALSO = "see also"
    SEE = "see"
    ALSO = "also"
