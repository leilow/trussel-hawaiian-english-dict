-- Phase 2-5 tables: dictionary sources, prefaces, wordlists, gloss sources,
-- image details, structural pages. Also extends the existing image table.

-- =============================================================================
-- dictionary_source: editions of the three source dictionaries
-- =============================================================================
CREATE TABLE dictionary_source (
    id              SERIAL PRIMARY KEY,
    source_page     TEXT NOT NULL,           -- 'sources-pe.htm', 'sources-mk.htm', 'sources-an.htm'
    anchor          TEXT NOT NULL,           -- '57', '64', '86', '96', etc.
    title           TEXT NOT NULL,
    year            TEXT,
    description     TEXT,
    cover_images    TEXT[] DEFAULT '{}',
    intro_pdf_url   TEXT,
    UNIQUE(source_page, anchor)
);

ALTER TABLE dictionary_source ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_dictionary_source" ON dictionary_source FOR SELECT USING (true);

-- =============================================================================
-- preface: dictionary preface prose
-- =============================================================================
CREATE TABLE preface (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL UNIQUE,     -- 'prefs-57.htm'
    title           TEXT NOT NULL,
    subtitle        TEXT,
    year_edition    TEXT,
    prose_html      TEXT,                     -- full HTML of preface text
    nav_links       TEXT[] DEFAULT '{}',
    images          TEXT[] DEFAULT '{}',
    referenced_assets TEXT[] DEFAULT '{}'
);

ALTER TABLE preface ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_preface" ON preface FOR SELECT USING (true);

-- =============================================================================
-- wordlist: historical wordlist pages (container)
-- =============================================================================
CREATE TABLE wordlist (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL UNIQUE,     -- 'anderson.htm'
    title           TEXT NOT NULL,            -- 'William Anderson''s List (1778)'
    author          TEXT,
    year            TEXT,
    intro_text      TEXT,
    entry_count     INT DEFAULT 0
);

ALTER TABLE wordlist ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_wordlist" ON wordlist FOR SELECT USING (true);

-- =============================================================================
-- wordlist_entry: individual words in historical wordlists
-- =============================================================================
CREATE TABLE wordlist_entry (
    id                  SERIAL PRIMARY KEY,
    wordlist_id         INT NOT NULL REFERENCES wordlist(id) ON DELETE CASCADE,
    entry_number        INT,
    list_word           TEXT NOT NULL,
    modern_hawaiian     TEXT,
    gloss               TEXT,
    footnote            TEXT
);

CREATE INDEX idx_wordlist_entry_wordlist ON wordlist_entry(wordlist_id);

ALTER TABLE wordlist_entry ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_wordlist_entry" ON wordlist_entry FOR SELECT USING (true);

-- =============================================================================
-- wordlist_entry_link: links from modern_hawaiian to dictionary entries
-- =============================================================================
CREATE TABLE wordlist_entry_link (
    id                  SERIAL PRIMARY KEY,
    wordlist_entry_id   INT NOT NULL REFERENCES wordlist_entry(id) ON DELETE CASCADE,
    surface             TEXT NOT NULL,
    target_anchor       TEXT,
    target_page         TEXT,
    link_class          TEXT
);

CREATE INDEX idx_wordlist_entry_link_entry ON wordlist_entry_link(wordlist_entry_id);

ALTER TABLE wordlist_entry_link ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_wordlist_entry_link" ON wordlist_entry_link FOR SELECT USING (true);

-- =============================================================================
-- gloss_source_text: Hawaiian source texts used for glosses
-- =============================================================================
CREATE TABLE gloss_source_text (
    id              SERIAL PRIMARY KEY,
    source_number   INT NOT NULL UNIQUE,
    hawaiian_title  TEXT NOT NULL,
    author_info     TEXT,
    publisher       TEXT,
    year            TEXT,
    page_count      TEXT,
    cover_image_url TEXT,
    ulukau_url      TEXT
);

ALTER TABLE gloss_source_text ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_gloss_source_text" ON gloss_source_text FOR SELECT USING (true);

-- =============================================================================
-- image_detail: image detail pages with captions and credits
-- =============================================================================
CREATE TABLE image_detail (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL UNIQUE,
    image_url       TEXT NOT NULL,
    headword_display TEXT,
    caption         TEXT,
    source_credit   TEXT,
    source_link_url TEXT,
    source_link_text TEXT
);

ALTER TABLE image_detail ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_image_detail" ON image_detail FOR SELECT USING (true);

-- =============================================================================
-- structural_page: intro, texts, reversehelp, etc.
-- =============================================================================
CREATE TABLE structural_page (
    id              SERIAL PRIMARY KEY,
    filename        TEXT NOT NULL UNIQUE,
    title           TEXT,
    updated         TEXT,
    sections        JSONB DEFAULT '[]',
    internal_links  TEXT[] DEFAULT '{}',
    external_links  TEXT[] DEFAULT '{}',
    referenced_assets TEXT[] DEFAULT '{}'
);

ALTER TABLE structural_page ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public_read_structural_page" ON structural_page FOR SELECT USING (true);

-- =============================================================================
-- Extend existing image table with caption and source_credit
-- =============================================================================
ALTER TABLE image ADD COLUMN caption TEXT;
ALTER TABLE image ADD COLUMN source_credit TEXT;
