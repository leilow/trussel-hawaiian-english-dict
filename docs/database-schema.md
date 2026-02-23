# CHD Database Schema

```mermaid
erDiagram
    Entry {
        string id PK "anchor ID from HTML"
        string headword "normalized (with diacriticals)"
        string headword_display "as shown on page"
        string headword_ascii "ASCII fallback"
        string subscript "e.g. 1, 2"
        string letter_page "e.g. a, k, h"
        string trussel_display_type "main | sub | comb1 | comb2"
        string trussel_subentry_of FK "parent entry ID"
        string pdf_page
        bool in_pe
        bool in_mk
        bool in_mk_addendum
        bool in_andrews
        bool in_placenames
        bool is_from_eh_only
        string syllable_breakdown
        bool is_basic_vocab
        string dialect "e.g. Niihau"
        string usage_register "e.g. rare, archaic"
        bool is_loanword
        string loan_source
        string loan_language
        string source_tag
    }

    Sense {
        int sense_num
        string source_dict "PE | MK | Andrews | EH | Other"
        string pos_raw "e.g. nvs."
        string pos_hawaiian "e.g. kikino + haina aano"
        string pos_english "e.g. noun, stative"
        string text "full definition text"
        string html "raw HTML"
        string hawaiian_gloss
        string gloss_source_num
    }

    SubDefinition {
        string text "bullet-point definition"
        bool is_figurative
        bool is_rare
        bool is_archaic
    }

    LinkedWord {
        string surface "display text"
        string target_anchor FK "target entry ID"
        string target_page
        string link_class "CSS class"
    }

    Example {
        string hawaiian_text
        string english_text
        string note
        string olelo_noeau_num
        string bible_ref
        bool is_causative
        string source_dict
    }

    WordToken {
        string surface "display text"
        string anchor FK "target entry ID"
        string target_entry
    }

    SourceRef {
        string type "e.g. ON, Bible, Kep"
        string id "e.g. 123, Luk.4.8"
        string url
    }

    Etymology {
        string raw_text
        string proto_form "e.g. *kalo"
        string proto_language "e.g. PPN"
        string qualifier
        string meaning
        string pollex_url
    }

    CrossRef {
        string ref_type "same as | redup. of | var. of | ..."
        string target_headword
        string target_anchor FK "target entry ID"
        string target_page
        string source_dict
    }

    GrammarRef {
        string section
        string label
        string pdf_url
    }

    HawaiianGloss {
        string gloss
        string source_text_id
        string source_ref
    }

    ImageInfo {
        string thumbnail_url
        string full_image_url
        string source_url
        string alt_text
        int height
    }

    DomainCode {
        string code "e.g. Bot, Mus, Med"
    }

    AltSpelling {
        string spelling
    }

    Topic {
        string name "e.g. fish, birds, plants"
    }

    EngHawEntry {
        string english_word PK
        string source "PE | MK | Andrews | EH | Other"
        string letter_page
    }

    EngHawTranslation {
        string hawaiian_word
        string target_anchor FK "haw-eng entry ID"
        string target_page
    }

    ConcordanceInstance {
        string word
        string word_anchor FK "haw-eng entry ID"
        string hawaiian_text
        string english_text
        string note
        string parent_entry_anchor FK "haw-eng entry ID"
        string parent_entry_page
    }

    Reference {
        string abbreviation PK "e.g. PE, MK, And."
        string anchor
        string full_text
        string url
    }

    %% ─── Relationships ───

    Entry ||--o{ Sense : "has"
    Entry ||--o{ Example : "has"
    Entry ||--o{ CrossRef : "references"
    Entry ||--o| Etymology : "has"
    Entry ||--o{ GrammarRef : "has"
    Entry ||--o{ HawaiianGloss : "has"
    Entry ||--o{ ImageInfo : "has"
    Entry ||--o{ AltSpelling : "has"
    Entry ||--o{ Topic : "tagged with"
    Entry ||--o{ Entry : "subentry of"

    Sense ||--o{ SubDefinition : "has"
    Sense ||--o{ LinkedWord : "contains"

    SubDefinition ||--o{ LinkedWord : "contains"
    SubDefinition ||--o{ DomainCode : "tagged with"

    Example ||--o{ WordToken : "contains"
    Example ||--o| SourceRef : "cites"

    CrossRef }o--o| Entry : "points to"

    EngHawEntry ||--o{ EngHawTranslation : "has"
    EngHawTranslation }o--o| Entry : "points to"

    ConcordanceInstance }o--o| Entry : "word links to"
    ConcordanceInstance }o--o| Entry : "parent entry"
    ConcordanceInstance ||--o{ WordToken : "contains"

    LinkedWord }o--o| Entry : "points to"
    WordToken }o--o| Entry : "points to"
```

## Summary

| Table | Rows | Description |
|-------|------|-------------|
| **Entry** | 59,715 | Hawaiian-English dictionary entries (deduplicated + topical-only) |
| **Sense** | ~90K | POS + definition per source dictionary |
| **SubDefinition** | ~30K | Bullet-point sub-definitions within senses |
| **Example** | ~27K | Hawaiian/English sentence pairs |
| **CrossRef** | ~16K | Cross-references between entries |
| **Etymology** | ~2.6K | Proto-Polynesian reconstructions |
| **ImageInfo** | ~200 | Illustrated entry images |
| **EngHawEntry** | 20,712 | English-Hawaiian reverse lookup |
| **EngHawTranslation** | 76,859 | English→Hawaiian word mappings |
| **ConcordanceInstance** | 133,684 | Word-in-context sentence examples |
| **Reference** | 705 | Source abbreviation definitions |

## Enum Types

| Enum | Values |
|------|--------|
| **DictSource** | PE, MK, Andrews, EH, Other |
| **LinkTarget** | internal_entry, concordance, pdf, pollex, grammar, bible_conc, place_name, topical, reference, external, glossrefs, self_link, unknown |
| **CrossRefType** | same as, redup. of, var. of, pas/imp. of, var. spelling of, short for, similar to, plural of, a variety of, cf., see also, see, also |
