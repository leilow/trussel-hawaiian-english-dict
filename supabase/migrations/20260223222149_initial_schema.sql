-- CHD (Combined Hawaiian Dictionary) Schema
-- Source: trussel2.com/HAW/ parsed by chd-scraper v2

-- ─── Enums ──────────────────────────────────────────────────────────────────

CREATE TYPE dict_source AS ENUM ('PE', 'MK', 'Andrews', 'EH', 'Other');
CREATE TYPE cross_ref_type AS ENUM (
  'same as', 'redup. of', 'var. of', 'pas/imp. of', 'var. spelling of',
  'short for', 'similar to', 'plural of', 'a variety of',
  'cf.', 'see also', 'see', 'also'
);
CREATE TYPE display_type AS ENUM ('main', 'sub', 'comb1', 'comb2');

-- ─── Core Entry ─────────────────────────────────────────────────────────────

CREATE TABLE entry (
  id              TEXT PRIMARY KEY,  -- anchor ID from HTML (e.g. "57179")
  headword        TEXT NOT NULL,     -- normalized with diacriticals
  headword_display TEXT NOT NULL,    -- as shown on page
  headword_ascii  TEXT NOT NULL DEFAULT '',  -- ASCII fallback for search
  subscript       TEXT NOT NULL DEFAULT '',
  letter_page     TEXT NOT NULL DEFAULT '',
  display_type    display_type NOT NULL DEFAULT 'main',
  parent_entry_id TEXT REFERENCES entry(id),
  pdf_page        TEXT NOT NULL DEFAULT '',
  in_pe           BOOLEAN NOT NULL DEFAULT FALSE,
  in_mk           BOOLEAN NOT NULL DEFAULT FALSE,
  in_mk_addendum  BOOLEAN NOT NULL DEFAULT FALSE,
  in_andrews      BOOLEAN NOT NULL DEFAULT FALSE,
  in_placenames   BOOLEAN NOT NULL DEFAULT FALSE,
  is_from_eh_only BOOLEAN NOT NULL DEFAULT FALSE,
  syllable_breakdown TEXT NOT NULL DEFAULT '',
  is_basic_vocab  BOOLEAN NOT NULL DEFAULT FALSE,
  dialect         TEXT NOT NULL DEFAULT '',
  usage_register  TEXT NOT NULL DEFAULT '',
  is_loanword     BOOLEAN NOT NULL DEFAULT FALSE,
  loan_source     TEXT NOT NULL DEFAULT '',
  loan_language   TEXT NOT NULL DEFAULT '',
  source_tag      TEXT NOT NULL DEFAULT '',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_entry_headword ON entry(headword);
CREATE INDEX idx_entry_headword_ascii ON entry(headword_ascii);
CREATE INDEX idx_entry_letter_page ON entry(letter_page);
CREATE INDEX idx_entry_parent ON entry(parent_entry_id);

-- Full-text search on headword
ALTER TABLE entry ADD COLUMN headword_search tsvector
  GENERATED ALWAYS AS (to_tsvector('simple', headword || ' ' || headword_ascii)) STORED;
CREATE INDEX idx_entry_fts ON entry USING GIN(headword_search);

-- ─── Senses ─────────────────────────────────────────────────────────────────

CREATE TABLE sense (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  sense_num       INT NOT NULL DEFAULT 0,
  source_dict     dict_source NOT NULL DEFAULT 'PE',
  pos_raw         TEXT NOT NULL DEFAULT '',
  pos_hawaiian    TEXT NOT NULL DEFAULT '',  -- pepeke system
  pos_english     TEXT NOT NULL DEFAULT '',  -- English-familiar tag
  definition_text TEXT NOT NULL DEFAULT '',
  definition_html TEXT NOT NULL DEFAULT '',
  hawaiian_gloss  TEXT NOT NULL DEFAULT '',
  gloss_source_num TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_sense_entry ON sense(entry_id);

-- ─── Sub-Definitions (bullet points within a sense) ─────────────────────────

CREATE TABLE sub_definition (
  id              SERIAL PRIMARY KEY,
  sense_id        INT NOT NULL REFERENCES sense(id) ON DELETE CASCADE,
  text            TEXT NOT NULL DEFAULT '',
  is_figurative   BOOLEAN NOT NULL DEFAULT FALSE,
  is_rare         BOOLEAN NOT NULL DEFAULT FALSE,
  is_archaic      BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_subdef_sense ON sub_definition(sense_id);

-- ─── Domain codes on sub-definitions ────────────────────────────────────────

CREATE TABLE sub_definition_domain (
  id              SERIAL PRIMARY KEY,
  sub_definition_id INT NOT NULL REFERENCES sub_definition(id) ON DELETE CASCADE,
  code            TEXT NOT NULL  -- e.g. 'Bot', 'Mus', 'Med'
);

CREATE INDEX idx_subdef_domain ON sub_definition_domain(sub_definition_id);

-- ─── Linked Words (hyperlinks in definitions) ───────────────────────────────

CREATE TABLE linked_word (
  id              SERIAL PRIMARY KEY,
  sense_id        INT REFERENCES sense(id) ON DELETE CASCADE,
  sub_definition_id INT REFERENCES sub_definition(id) ON DELETE CASCADE,
  surface         TEXT NOT NULL DEFAULT '',
  target_anchor   TEXT NOT NULL DEFAULT '',  -- target entry ID
  target_page     TEXT NOT NULL DEFAULT '',
  link_class      TEXT NOT NULL DEFAULT '',
  CONSTRAINT linked_word_parent CHECK (sense_id IS NOT NULL OR sub_definition_id IS NOT NULL)
);

CREATE INDEX idx_linked_word_sense ON linked_word(sense_id);
CREATE INDEX idx_linked_word_subdef ON linked_word(sub_definition_id);
CREATE INDEX idx_linked_word_target ON linked_word(target_anchor);

-- ─── Examples ───────────────────────────────────────────────────────────────

CREATE TABLE example (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  hawaiian_text   TEXT NOT NULL DEFAULT '',
  english_text    TEXT NOT NULL DEFAULT '',
  note            TEXT NOT NULL DEFAULT '',
  olelo_noeau_num TEXT NOT NULL DEFAULT '',
  bible_ref       TEXT NOT NULL DEFAULT '',
  is_causative    BOOLEAN NOT NULL DEFAULT FALSE,
  source_dict     dict_source NOT NULL DEFAULT 'PE',
  source_ref_type TEXT NOT NULL DEFAULT '',  -- e.g. 'ON', 'Bible', 'Kep'
  source_ref_id   TEXT NOT NULL DEFAULT '',  -- e.g. '123', 'Luk.4.8'
  source_ref_url  TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_example_entry ON example(entry_id);

-- ─── Word Tokens (hyperlinked words in examples/concordance) ────────────────

CREATE TABLE word_token (
  id              SERIAL PRIMARY KEY,
  example_id      INT REFERENCES example(id) ON DELETE CASCADE,
  concordance_id  INT,  -- FK added after concordance table created
  surface         TEXT NOT NULL DEFAULT '',
  anchor          TEXT NOT NULL DEFAULT '',  -- target entry ID
  target_entry    TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_word_token_example ON word_token(example_id);

-- ─── Etymology ──────────────────────────────────────────────────────────────

CREATE TABLE etymology (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL UNIQUE REFERENCES entry(id) ON DELETE CASCADE,
  raw_text        TEXT NOT NULL DEFAULT '',
  proto_form      TEXT NOT NULL DEFAULT '',
  proto_language  TEXT NOT NULL DEFAULT '',
  qualifier       TEXT NOT NULL DEFAULT '',
  meaning         TEXT NOT NULL DEFAULT '',
  pollex_url      TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_etymology_entry ON etymology(entry_id);

-- ─── Cross-References ───────────────────────────────────────────────────────

CREATE TABLE cross_ref (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  ref_type        TEXT NOT NULL DEFAULT '',
  target_headword TEXT NOT NULL DEFAULT '',
  target_anchor   TEXT NOT NULL DEFAULT '',  -- target entry ID
  target_page     TEXT NOT NULL DEFAULT '',
  source_dict     dict_source NOT NULL DEFAULT 'PE'
);

CREATE INDEX idx_cross_ref_entry ON cross_ref(entry_id);
CREATE INDEX idx_cross_ref_target ON cross_ref(target_anchor);

-- ─── Grammar References ─────────────────────────────────────────────────────

CREATE TABLE grammar_ref (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  section         TEXT NOT NULL DEFAULT '',
  label           TEXT NOT NULL DEFAULT '',
  pdf_url         TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_grammar_ref_entry ON grammar_ref(entry_id);

-- ─── Hawaiian Glosses ───────────────────────────────────────────────────────

CREATE TABLE hawaiian_gloss (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  gloss           TEXT NOT NULL DEFAULT '',
  source_text_id  TEXT NOT NULL DEFAULT '',
  source_ref      TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_hawaiian_gloss_entry ON hawaiian_gloss(entry_id);

-- ─── Images ─────────────────────────────────────────────────────────────────

CREATE TABLE image (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  thumbnail_url   TEXT NOT NULL DEFAULT '',
  full_image_url  TEXT NOT NULL DEFAULT '',
  source_url      TEXT NOT NULL DEFAULT '',
  alt_text        TEXT NOT NULL DEFAULT '',
  height          INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_image_entry ON image(entry_id);

-- ─── Alt Spellings ──────────────────────────────────────────────────────────

CREATE TABLE alt_spelling (
  id              SERIAL PRIMARY KEY,
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  spelling        TEXT NOT NULL
);

CREATE INDEX idx_alt_spelling_entry ON alt_spelling(entry_id);

-- ─── Topics ─────────────────────────────────────────────────────────────────

CREATE TABLE topic (
  id              SERIAL PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE  -- e.g. 'fish', 'birds', 'plants'
);

CREATE TABLE entry_topic (
  entry_id        TEXT NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
  topic_id        INT NOT NULL REFERENCES topic(id) ON DELETE CASCADE,
  PRIMARY KEY (entry_id, topic_id)
);

CREATE INDEX idx_entry_topic_topic ON entry_topic(topic_id);

-- ─── English-Hawaiian ───────────────────────────────────────────────────────

CREATE TABLE eng_haw_entry (
  id              SERIAL PRIMARY KEY,
  english_word    TEXT NOT NULL,
  source          dict_source NOT NULL DEFAULT 'PE',
  letter_page     TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_eng_haw_word ON eng_haw_entry(english_word);

-- Full-text search on english word
ALTER TABLE eng_haw_entry ADD COLUMN word_search tsvector
  GENERATED ALWAYS AS (to_tsvector('english', english_word)) STORED;
CREATE INDEX idx_eng_haw_fts ON eng_haw_entry USING GIN(word_search);

CREATE TABLE eng_haw_translation (
  id              SERIAL PRIMARY KEY,
  eng_haw_entry_id INT NOT NULL REFERENCES eng_haw_entry(id) ON DELETE CASCADE,
  hawaiian_word   TEXT NOT NULL DEFAULT '',
  target_anchor   TEXT NOT NULL DEFAULT '',  -- haw-eng entry ID
  target_page     TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_eng_haw_trans_entry ON eng_haw_translation(eng_haw_entry_id);
CREATE INDEX idx_eng_haw_trans_target ON eng_haw_translation(target_anchor);

-- ─── Concordance ────────────────────────────────────────────────────────────

CREATE TABLE concordance (
  id              SERIAL PRIMARY KEY,
  word            TEXT NOT NULL,
  word_anchor     TEXT NOT NULL DEFAULT '',  -- haw-eng entry ID
  hawaiian_text   TEXT NOT NULL DEFAULT '',
  english_text    TEXT NOT NULL DEFAULT '',
  note            TEXT NOT NULL DEFAULT '',
  parent_entry_anchor TEXT NOT NULL DEFAULT '',  -- haw-eng entry ID
  parent_entry_page   TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_concordance_word ON concordance(word);
CREATE INDEX idx_concordance_word_anchor ON concordance(word_anchor);
CREATE INDEX idx_concordance_parent ON concordance(parent_entry_anchor);

-- Add FK for word_token.concordance_id now that concordance exists
ALTER TABLE word_token
  ADD CONSTRAINT fk_word_token_concordance
  FOREIGN KEY (concordance_id) REFERENCES concordance(id) ON DELETE CASCADE;

CREATE INDEX idx_word_token_concordance ON word_token(concordance_id);

-- ─── References (source abbreviation definitions) ───────────────────────────

CREATE TABLE reference (
  id              SERIAL PRIMARY KEY,
  abbreviation    TEXT NOT NULL,
  anchor          TEXT NOT NULL DEFAULT '',
  full_text       TEXT NOT NULL DEFAULT '',
  url             TEXT NOT NULL DEFAULT ''
);

CREATE INDEX idx_reference_abbrev ON reference(abbreviation);

-- ─── Row-Level Security ─────────────────────────────────────────────────────
-- Public read access, no write access via API

ALTER TABLE entry ENABLE ROW LEVEL SECURITY;
ALTER TABLE sense ENABLE ROW LEVEL SECURITY;
ALTER TABLE sub_definition ENABLE ROW LEVEL SECURITY;
ALTER TABLE sub_definition_domain ENABLE ROW LEVEL SECURITY;
ALTER TABLE linked_word ENABLE ROW LEVEL SECURITY;
ALTER TABLE example ENABLE ROW LEVEL SECURITY;
ALTER TABLE word_token ENABLE ROW LEVEL SECURITY;
ALTER TABLE etymology ENABLE ROW LEVEL SECURITY;
ALTER TABLE cross_ref ENABLE ROW LEVEL SECURITY;
ALTER TABLE grammar_ref ENABLE ROW LEVEL SECURITY;
ALTER TABLE hawaiian_gloss ENABLE ROW LEVEL SECURITY;
ALTER TABLE image ENABLE ROW LEVEL SECURITY;
ALTER TABLE alt_spelling ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic ENABLE ROW LEVEL SECURITY;
ALTER TABLE entry_topic ENABLE ROW LEVEL SECURITY;
ALTER TABLE eng_haw_entry ENABLE ROW LEVEL SECURITY;
ALTER TABLE eng_haw_translation ENABLE ROW LEVEL SECURITY;
ALTER TABLE concordance ENABLE ROW LEVEL SECURITY;
ALTER TABLE reference ENABLE ROW LEVEL SECURITY;

-- Public read policies
CREATE POLICY "Public read" ON entry FOR SELECT USING (true);
CREATE POLICY "Public read" ON sense FOR SELECT USING (true);
CREATE POLICY "Public read" ON sub_definition FOR SELECT USING (true);
CREATE POLICY "Public read" ON sub_definition_domain FOR SELECT USING (true);
CREATE POLICY "Public read" ON linked_word FOR SELECT USING (true);
CREATE POLICY "Public read" ON example FOR SELECT USING (true);
CREATE POLICY "Public read" ON word_token FOR SELECT USING (true);
CREATE POLICY "Public read" ON etymology FOR SELECT USING (true);
CREATE POLICY "Public read" ON cross_ref FOR SELECT USING (true);
CREATE POLICY "Public read" ON grammar_ref FOR SELECT USING (true);
CREATE POLICY "Public read" ON hawaiian_gloss FOR SELECT USING (true);
CREATE POLICY "Public read" ON image FOR SELECT USING (true);
CREATE POLICY "Public read" ON alt_spelling FOR SELECT USING (true);
CREATE POLICY "Public read" ON topic FOR SELECT USING (true);
CREATE POLICY "Public read" ON entry_topic FOR SELECT USING (true);
CREATE POLICY "Public read" ON eng_haw_entry FOR SELECT USING (true);
CREATE POLICY "Public read" ON eng_haw_translation FOR SELECT USING (true);
CREATE POLICY "Public read" ON concordance FOR SELECT USING (true);
CREATE POLICY "Public read" ON reference FOR SELECT USING (true);
