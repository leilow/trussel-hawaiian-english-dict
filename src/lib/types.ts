// ── Core entry ──────────────────────────────────────────────

export interface Entry {
  id: string;
  headword: string;
  headword_display: string;
  headword_ascii: string;
  subscript: string | null;
  letter_page: string;
  display_type: "main" | "sub" | "comb1" | "comb2";
  parent_entry_id: string | null;
  pdf_page: string | null;
  in_pe: boolean;
  in_mk: boolean;
  in_mk_addendum: boolean;
  in_andrews: boolean;
  in_placenames: boolean;
  is_from_eh_only: boolean;
  syllable_breakdown: string | null;
  is_basic_vocab: boolean;
  dialect: string | null;
  usage_register: string | null;
  is_loanword: boolean;
  loan_source: string | null;
  loan_language: string | null;
  source_tag: string | null;
  created_at: string;
}

// ── Sense + sub-definitions ─────────────────────────────────

export interface Sense {
  id: number;
  entry_id: string;
  sense_num: number;
  source_dict: DictSource;
  pos_raw: string | null;
  pos_hawaiian: string | null;
  pos_english: string | null;
  definition_text: string | null;
  definition_html: string | null;
  hawaiian_gloss: string | null;
  gloss_source_num: string | null;
}

export interface SubDefinition {
  id: number;
  sense_id: number;
  text: string;
  is_figurative: boolean;
  is_rare: boolean;
  is_archaic: boolean;
}

export interface SubDefinitionDomain {
  id: number;
  sub_definition_id: number;
  code: string;
}

export interface LinkedWord {
  id: number;
  sense_id: number | null;
  sub_definition_id: number | null;
  surface: string;
  target_anchor: string | null;
  target_page: string | null;
  link_class: string | null;
}

// ── Examples + word tokens ──────────────────────────────────

export interface Example {
  id: number;
  entry_id: string;
  hawaiian_text: string | null;
  english_text: string | null;
  note: string | null;
  olelo_noeau_num: string | null;
  bible_ref: string | null;
  is_causative: boolean;
  source_dict: DictSource;
  source_ref_type: string | null;
  source_ref_id: string | null;
  source_ref_url: string | null;
}

export interface WordToken {
  id: number;
  example_id: number | null;
  concordance_id: number | null;
  surface: string;
  anchor: string | null;
  target_entry: string | null;
}

// ── Etymology ───────────────────────────────────────────────

export interface Etymology {
  id: number;
  entry_id: string;
  raw_text: string | null;
  proto_form: string | null;
  proto_language: string | null;
  qualifier: string | null;
  meaning: string | null;
  pollex_url: string | null;
}

// ── Cross-references ────────────────────────────────────────

export interface CrossRef {
  id: number;
  entry_id: string;
  ref_type: string | null;
  target_headword: string | null;
  target_anchor: string | null;
  target_page: string | null;
  source_dict: DictSource;
}

// ── Grammar references ──────────────────────────────────────

export interface GrammarRef {
  id: number;
  entry_id: string;
  section: string | null;
  label: string | null;
  pdf_url: string | null;
}

// ── Hawaiian glosses ────────────────────────────────────────

export interface HawaiianGloss {
  id: number;
  entry_id: string;
  gloss: string | null;
  source_text_id: string | null;
  source_ref: string | null;
}

// ── Images ──────────────────────────────────────────────────

export interface ImageInfo {
  id: number;
  entry_id: string;
  thumbnail_url: string | null;
  full_image_url: string | null;
  source_url: string | null;
  alt_text: string | null;
  height: number | null;
}

// ── Alt spellings ───────────────────────────────────────────

export interface AltSpelling {
  id: number;
  entry_id: string;
  spelling: string;
}

// ── Topics ──────────────────────────────────────────────────

export interface Topic {
  id: number;
  name: string;
}

export interface EntryTopic {
  entry_id: string;
  topic_id: number;
}

// ── English-Hawaiian ────────────────────────────────────────

export interface EngHawEntry {
  id: number;
  english_word: string;
  source: DictSource;
  letter_page: string | null;
}

export interface EngHawTranslation {
  id: number;
  eng_haw_entry_id: number;
  hawaiian_word: string | null;
  target_anchor: string | null;
  target_page: string | null;
}

// ── Concordance ─────────────────────────────────────────────

export interface Concordance {
  id: number;
  word: string;
  word_anchor: string | null;
  hawaiian_text: string | null;
  english_text: string | null;
  note: string | null;
  parent_entry_anchor: string | null;
  parent_entry_page: string | null;
}

// ── References ──────────────────────────────────────────────

export interface Reference {
  id: number;
  abbreviation: string | null;
  anchor: string | null;
  full_text: string | null;
  url: string | null;
}

// ── Enums ───────────────────────────────────────────────────

export type DictSource = "PE" | "MK" | "Andrews" | "EH" | "Other";

// ── Composite types for joined queries ──────────────────────

export interface SenseWithDetails extends Sense {
  sub_definition: SubDefinitionWithDomains[];
  linked_word: LinkedWord[];
}

export interface SubDefinitionWithDomains extends SubDefinition {
  sub_definition_domain: SubDefinitionDomain[];
  linked_word: LinkedWord[];
}

export interface ExampleWithTokens extends Example {
  word_token: WordToken[];
}

export interface EntryWithRelations extends Entry {
  sense: SenseWithDetails[];
  example: ExampleWithTokens[];
  etymology: Etymology[];
  cross_ref: CrossRef[];
  grammar_ref: GrammarRef[];
  hawaiian_gloss: HawaiianGloss[];
  image: ImageInfo[];
  alt_spelling: AltSpelling[];
  entry_topic: { topic: Topic }[];
  // Sub-entries (children)
  children?: EntryBrief[];
}

export interface EntryBrief {
  id: string;
  headword: string;
  headword_display: string;
  headword_ascii?: string;
  subscript: string | null;
  in_pe: boolean;
  in_mk: boolean;
  in_andrews: boolean;
  is_from_eh_only: boolean;
  sense: { definition_text: string | null; pos_raw: string | null }[];
}

export interface TopicWithCount extends Topic {
  entry_count: number;
}

export interface ConcordanceWithTokens extends Concordance {
  word_token: WordToken[];
}

export interface EngHawEntryWithTranslations extends EngHawEntry {
  eng_haw_translation: EngHawTranslation[];
}

// ── Phase 2-5 tables ──────────────────────────────────────────

export interface DictionarySource {
  id: number;
  source_page: string;
  anchor: string;
  title: string;
  year: string | null;
  description: string | null;
  cover_images: string[];
  intro_pdf_url: string | null;
}

export interface Preface {
  id: number;
  filename: string;
  title: string;
  subtitle: string | null;
  year_edition: string | null;
  prose_html: string | null;
  nav_links: string[];
  images: string[];
  referenced_assets: string[];
}

export interface Wordlist {
  id: number;
  filename: string;
  title: string;
  author: string | null;
  year: string | null;
  intro_text: string | null;
  entry_count: number;
}

export interface WordlistEntry {
  id: number;
  wordlist_id: number;
  entry_number: number | null;
  list_word: string;
  modern_hawaiian: string | null;
  gloss: string | null;
  footnote: string | null;
}

export interface WordlistEntryLink {
  id: number;
  wordlist_entry_id: number;
  surface: string;
  target_anchor: string | null;
  target_page: string | null;
  link_class: string | null;
}

export interface GlossSourceText {
  id: number;
  source_number: number;
  hawaiian_title: string;
  author_info: string | null;
  publisher: string | null;
  year: string | null;
  page_count: string | null;
  cover_image_url: string | null;
  ulukau_url: string | null;
}

export interface ImageDetail {
  id: number;
  filename: string;
  image_url: string;
  headword_display: string | null;
  caption: string | null;
  source_credit: string | null;
  source_link_url: string | null;
  source_link_text: string | null;
}

export interface StructuralPage {
  id: number;
  filename: string;
  title: string | null;
  updated: string | null;
  sections: unknown;
  internal_links: string[];
  external_links: string[];
  referenced_assets: string[];
}

export interface WordlistEntryWithLinks extends WordlistEntry {
  wordlist_entry_link: WordlistEntryLink[];
}
