import { supabase } from "./supabase";
import type {
  EntryWithRelations,
  EntryBrief,
  TopicWithCount,
  ConcordanceWithTokens,
  EngHawEntryWithTranslations,
  Reference,
  Entry,
  DictionarySource,
  Preface,
  Wordlist,
  WordlistEntryWithLinks,
  GlossSourceText,
  ImageDetail,
  StructuralPage,
} from "./types";

// ── Entry detail select fragment ─────────────────────────────
const ENTRY_DETAIL_SELECT = `
  *,
  sense (
    *,
    sub_definition (
      *,
      sub_definition_domain (*),
      linked_word (*)
    ),
    linked_word (*)
  ),
  example (
    *,
    word_token (*)
  ),
  etymology (*),
  cross_ref (*),
  grammar_ref (*),
  hawaiian_gloss (*),
  image (*),
  alt_spelling (*),
  entry_topic (
    topic (*)
  )
`;

// ── Entry detail (the big joined query) ─────────────────────
// Resolves both numeric IDs ("58645") and headword_ascii anchors ("aloha")

export async function getEntry(id: string): Promise<EntryWithRelations | null> {
  const isNumeric = /^\d+$/.test(id);

  if (isNumeric) {
    // Direct lookup by numeric ID
    const { data, error } = await supabase
      .from("entry")
      .select(ENTRY_DETAIL_SELECT)
      .eq("id", id)
      .single();

    if (!error && data) {
      if (data.sense) {
        data.sense.sort((a: { sense_num: number }, b: { sense_num: number }) => a.sense_num - b.sense_num);
      }
      return data as EntryWithRelations;
    }
  }

  // Fallback: lookup by headword_ascii (used by cross-refs, word tokens, linked words)
  const decoded = decodeURIComponent(id);
  const { data: matches, error: matchError } = await supabase
    .from("entry")
    .select(ENTRY_DETAIL_SELECT)
    .eq("headword_ascii", decoded)
    .eq("is_from_eh_only", false)
    .order("in_pe", { ascending: false })   // PE entries first
    .order("in_mk", { ascending: false })   // then MK
    .order("in_andrews", { ascending: false }); // then Andrews

  if (matchError || !matches?.length) return null;

  // Pick the first (highest priority) entry
  const data = matches[0];
  if (data.sense) {
    data.sense.sort((a: { sense_num: number }, b: { sense_num: number }) => a.sense_num - b.sense_num);
  }
  return data as EntryWithRelations;
}

// ── Resolve anchor to entry ID (for redirects) ──────────────
// Returns all matching entries for a headword_ascii, for disambiguation

export async function getEntriesByAnchor(anchor: string): Promise<EntryBrief[]> {
  const decoded = decodeURIComponent(anchor);
  const { data, error } = await supabase
    .from("entry")
    .select(`
      id, headword, headword_display, headword_ascii, subscript,
      in_pe, in_mk, in_andrews, is_from_eh_only,
      sense ( definition_text, pos_raw )
    `)
    .eq("headword_ascii", decoded)
    .eq("is_from_eh_only", false)
    .order("in_pe", { ascending: false })
    .order("subscript");

  if (error) return [];
  return (data ?? []) as EntryBrief[];
}

// ── Sub-entries (children of a parent entry) ────────────────

export async function getSubEntries(parentId: string): Promise<EntryBrief[]> {
  const { data, error } = await supabase
    .from("entry")
    .select(`
      id, headword, headword_display, subscript,
      in_pe, in_mk, in_andrews, is_from_eh_only,
      sense ( definition_text, pos_raw )
    `)
    .eq("parent_entry_id", parentId)
    .order("headword");

  if (error) return [];
  return (data ?? []) as EntryBrief[];
}

// ── Browse by letter (paginated) ────────────────────────────

interface BrowseFilters {
  source?: string[];
  pos?: string;
  prefix?: string;
  hasEtymology?: boolean;
  hasExamples?: boolean;
  isLoanword?: boolean;
}

export async function getEntriesByLetter(
  letter: string,
  page: number = 1,
  limit: number = 50,
  filters?: BrowseFilters
) {
  let query = supabase
    .from("entry")
    .select(
      `id, headword, headword_display, subscript,
       in_pe, in_mk, in_andrews, is_from_eh_only, is_loanword,
       sense ( definition_text, pos_raw )`,
      { count: "exact" }
    )
    .eq("letter_page", letter)
    .eq("is_from_eh_only", false)   // Exclude reverse-index-only entries
    .neq("headword", "");           // Exclude empty headwords

  // Apply filters
  if (filters?.source?.length) {
    for (const src of filters.source) {
      if (src === "PE") query = query.eq("in_pe", true);
      if (src === "MK") query = query.eq("in_mk", true);
      if (src === "Andrews") query = query.eq("in_andrews", true);
    }
  }
  if (filters?.prefix) {
    query = query.ilike("headword", `${filters.prefix}%`);
  }
  if (filters?.isLoanword) {
    query = query.eq("is_loanword", true);
  }

  const offset = (page - 1) * limit;
  query = query.order("headword").range(offset, offset + limit - 1);

  const { data, count, error } = await query;
  if (error) return { entries: [], total: 0 };
  return { entries: (data ?? []) as EntryBrief[], total: count ?? 0 };
}

// ── Full-text search (Hawaiian-English) ─────────────────────

export async function searchEntries(query: string, page: number = 1, limit: number = 50) {
  // Try prefix match on headword first for better UX, fall back to FTS
  const offset = (page - 1) * limit;

  // Use FTS with prefix matching
  const tsQuery = query.trim().replace(/\s+/g, " & ") + ":*";

  const { data, count, error } = await supabase
    .from("entry")
    .select(
      `id, headword, headword_display, subscript,
       in_pe, in_mk, in_andrews, is_from_eh_only,
       sense ( definition_text, pos_raw )`,
      { count: "exact" }
    )
    .textSearch("headword_search", tsQuery, { type: "plain", config: "simple" })
    .eq("is_from_eh_only", false)
    .order("headword")
    .range(offset, offset + limit - 1);

  if (error || !data?.length) {
    // Fallback: ilike search
    const { data: fallback, count: fbCount } = await supabase
      .from("entry")
      .select(
        `id, headword, headword_display, subscript,
         in_pe, in_mk, in_andrews, is_from_eh_only,
         sense ( definition_text, pos_raw )`,
        { count: "exact" }
      )
      .ilike("headword", `%${query}%`)
      .eq("is_from_eh_only", false)
      .order("headword")
      .range(offset, offset + limit - 1);

    return { entries: (fallback ?? []) as EntryBrief[], total: fbCount ?? 0 };
  }

  return { entries: data as EntryBrief[], total: count ?? 0 };
}

// ── Full-text search (English-Hawaiian) ─────────────────────

export async function searchEngHaw(query: string, page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;
  const tsQuery = query.trim().replace(/\s+/g, " & ") + ":*";

  const { data, count, error } = await supabase
    .from("eng_haw_entry")
    .select(
      `id, english_word, source, letter_page,
       eng_haw_translation ( id, hawaiian_word, target_anchor, target_page )`,
      { count: "exact" }
    )
    .textSearch("word_search", tsQuery, { type: "plain", config: "english" })
    .order("english_word")
    .range(offset, offset + limit - 1);

  if (error || !data?.length) {
    // Fallback: ilike
    const { data: fallback, count: fbCount } = await supabase
      .from("eng_haw_entry")
      .select(
        `id, english_word, source, letter_page,
         eng_haw_translation ( id, hawaiian_word, target_anchor, target_page )`,
        { count: "exact" }
      )
      .ilike("english_word", `%${query}%`)
      .order("english_word")
      .range(offset, offset + limit - 1);

    return { entries: (fallback ?? []) as EngHawEntryWithTranslations[], total: fbCount ?? 0 };
  }

  return { entries: data as EngHawEntryWithTranslations[], total: count ?? 0 };
}

// ── Topics ──────────────────────────────────────────────────

export async function getTopics(): Promise<TopicWithCount[]> {
  // Get topics with entry count via entry_topic join
  const { data, error } = await supabase
    .from("topic")
    .select("id, name, entry_topic ( count )")
    .order("name");

  if (error || !data) return [];

  return data.map((t) => ({
    id: t.id,
    name: t.name,
    entry_count: (t.entry_topic as { count: number }[])?.[0]?.count ?? 0,
  }));
}

export async function getEntriesByTopic(topicId: number, page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;

  // Get entry IDs for this topic
  const { data: junctionData, count, error: jError } = await supabase
    .from("entry_topic")
    .select("entry_id", { count: "exact" })
    .eq("topic_id", topicId)
    .range(offset, offset + limit - 1);

  if (jError || !junctionData?.length) return { entries: [], total: 0 };

  const entryIds = junctionData.map((j) => j.entry_id);

  const { data, error } = await supabase
    .from("entry")
    .select(`
      id, headword, headword_display, subscript,
      in_pe, in_mk, in_andrews, is_from_eh_only,
      sense ( definition_text, pos_raw )
    `)
    .in("id", entryIds)
    .order("headword");

  if (error) return { entries: [], total: 0 };
  return { entries: (data ?? []) as EntryBrief[], total: count ?? 0 };
}

export async function getTopicByName(name: string) {
  const { data, error } = await supabase
    .from("topic")
    .select("id, name")
    .ilike("name", name)
    .single();

  if (error) return null;
  return data as { id: number; name: string };
}

// ── Concordance ─────────────────────────────────────────────

export async function getConcordanceByWord(word: string, page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;

  const { data, count, error } = await supabase
    .from("concordance")
    .select(
      `id, word, word_anchor, hawaiian_text, english_text, note,
       parent_entry_anchor, parent_entry_page`,
      { count: "exact" }
    )
    .eq("word", word)
    .range(offset, offset + limit - 1);

  if (error) return { sentences: [], total: 0 };
  return { sentences: (data ?? []) as ConcordanceWithTokens[], total: count ?? 0 };
}

export async function getConcordanceLetterWords(letter: string, page: number = 1, limit: number = 100) {
  const offset = (page - 1) * limit;

  // Get distinct words starting with this letter
  const { data, count, error } = await supabase
    .from("concordance")
    .select("word", { count: "exact", head: false })
    .ilike("word", `${letter}%`)
    .order("word")
    .range(offset, offset + limit - 1);

  if (error) return { words: [], total: 0 };

  // Deduplicate
  const seen = new Set<string>();
  const unique = (data ?? []).filter((d) => {
    if (seen.has(d.word)) return false;
    seen.add(d.word);
    return true;
  });

  return { words: unique.map((d) => d.word), total: count ?? 0 };
}

// ── English-Hawaiian browse by letter ────────────────────────

export async function getEngHawByLetter(letter: string, page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;

  const { data, count, error } = await supabase
    .from("eng_haw_entry")
    .select(
      `id, english_word, source, letter_page,
       eng_haw_translation ( id, hawaiian_word, target_anchor, target_page )`,
      { count: "exact" }
    )
    .eq("letter_page", letter)
    .order("english_word")
    .range(offset, offset + limit - 1);

  if (error) return { entries: [], total: 0 };
  return { entries: (data ?? []) as EngHawEntryWithTranslations[], total: count ?? 0 };
}

// ── Concordance by letter (paginated KWIC view) ─────────────

export async function getConcordanceByLetter(letter: string, page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;

  const { data, count, error } = await supabase
    .from("concordance")
    .select(
      `id, word, word_anchor, hawaiian_text, english_text, note,
       parent_entry_anchor, parent_entry_page`,
      { count: "exact" }
    )
    .ilike("word", `${letter}%`)
    .order("word")
    .range(offset, offset + limit - 1);

  if (error) return { sentences: [], total: 0 };
  return { sentences: (data ?? []) as ConcordanceWithTokens[], total: count ?? 0 };
}

// ── References ──────────────────────────────────────────────

export async function getReferences(): Promise<Reference[]> {
  const { data, error } = await supabase
    .from("reference")
    .select("*")
    .order("abbreviation");

  if (error) return [];
  return (data ?? []) as Reference[];
}

// ── Statistics ──────────────────────────────────────────────

export async function getStats() {
  const [entries, senses, examples, concordance, crossRefs, etymologies, engHaw, references] =
    await Promise.all([
      supabase.from("entry").select("*", { count: "exact", head: true }),
      supabase.from("sense").select("*", { count: "exact", head: true }),
      supabase.from("example").select("*", { count: "exact", head: true }),
      supabase.from("concordance").select("*", { count: "exact", head: true }),
      supabase.from("cross_ref").select("*", { count: "exact", head: true }),
      supabase.from("etymology").select("*", { count: "exact", head: true }),
      supabase.from("eng_haw_entry").select("*", { count: "exact", head: true }),
      supabase.from("reference").select("*", { count: "exact", head: true }),
    ]);

  return {
    entries: entries.count ?? 0,
    senses: senses.count ?? 0,
    examples: examples.count ?? 0,
    concordance: concordance.count ?? 0,
    crossRefs: crossRefs.count ?? 0,
    etymologies: etymologies.count ?? 0,
    engHaw: engHaw.count ?? 0,
    references: references.count ?? 0,
  };
}

export async function getEntriesBySource() {
  // Count entries per source using boolean flags
  const [pe, mk, andrews, ehOnly] = await Promise.all([
    supabase.from("entry").select("*", { count: "exact", head: true }).eq("in_pe", true),
    supabase.from("entry").select("*", { count: "exact", head: true }).eq("in_mk", true),
    supabase.from("entry").select("*", { count: "exact", head: true }).eq("in_andrews", true),
    supabase.from("entry").select("*", { count: "exact", head: true }).eq("is_from_eh_only", true),
  ]);

  return [
    { source: "PE", entries: pe.count ?? 0 },
    { source: "MK", entries: mk.count ?? 0 },
    { source: "Andrews", entries: andrews.count ?? 0 },
    { source: "EH only", entries: ehOnly.count ?? 0 },
  ];
}

export async function getEntriesByLetter_stats() {
  const letters = ["a", "e", "h", "i", "k", "l", "m", "n", "o", "p", "u", "w"];
  const results = await Promise.all(
    letters.map(async (letter) => {
      const { count } = await supabase
        .from("entry")
        .select("*", { count: "exact", head: true })
        .eq("letter_page", letter);
      return { letter: letter.toUpperCase(), entries: count ?? 0 };
    })
  );
  return results;
}

// ── Random entry (deterministic by date) ────────────────────

export async function getRandomEntry(): Promise<EntryBrief | null> {
  // Use today's date as seed for deterministic pick
  const today = new Date();
  const dateStr = `${today.getFullYear()}-${today.getMonth()}-${today.getDate()}`;
  // Simple hash
  let hash = 0;
  for (let i = 0; i < dateStr.length; i++) {
    hash = ((hash << 5) - hash + dateStr.charCodeAt(i)) | 0;
  }
  const offset = Math.abs(hash) % 50000;

  const { data, error } = await supabase
    .from("entry")
    .select(`
      id, headword, headword_display, subscript,
      in_pe, in_mk, in_andrews, is_from_eh_only,
      sense ( definition_text, pos_raw )
    `)
    .eq("in_pe", true)
    .eq("display_type", "main")
    .not("sense", "is", null)
    .order("headword")
    .range(offset, offset)
    .single();

  if (error || !data) {
    // Fallback: just get first entry
    const { data: fallback } = await supabase
      .from("entry")
      .select(`
        id, headword, headword_display, subscript,
        in_pe, in_mk, in_andrews, is_from_eh_only,
        sense ( definition_text, pos_raw )
      `)
      .eq("in_pe", true)
      .limit(1)
      .single();

    return (fallback as EntryBrief) ?? null;
  }

  return data as EntryBrief;
}

// ── Dictionary Sources ───────────────────────────────────────

export async function getDictionarySources(): Promise<DictionarySource[]> {
  const { data, error } = await supabase
    .from("dictionary_source")
    .select("*")
    .order("source_page")
    .order("anchor");

  if (error) return [];
  return (data ?? []) as DictionarySource[];
}

// ── Prefaces ─────────────────────────────────────────────────

export async function getPrefaces(): Promise<Preface[]> {
  const { data, error } = await supabase
    .from("preface")
    .select("id, filename, title, subtitle, year_edition")
    .order("year_edition");

  if (error) return [];
  return (data ?? []) as Preface[];
}

export async function getPreface(id: number): Promise<Preface | null> {
  const { data, error } = await supabase
    .from("preface")
    .select("*")
    .eq("id", id)
    .single();

  if (error) return null;
  return data as Preface;
}

// ── Wordlists ────────────────────────────────────────────────

export async function getWordlists(): Promise<Wordlist[]> {
  const { data, error } = await supabase
    .from("wordlist")
    .select("*")
    .order("title");

  if (error) return [];
  return (data ?? []) as Wordlist[];
}

export async function getWordlist(id: number): Promise<Wordlist | null> {
  const { data, error } = await supabase
    .from("wordlist")
    .select("*")
    .eq("id", id)
    .single();

  if (error) return null;
  return data as Wordlist;
}

export async function getWordlistEntries(
  wordlistId: number,
  page: number = 1,
  limit: number = 100
) {
  const offset = (page - 1) * limit;

  const { data, count, error } = await supabase
    .from("wordlist_entry")
    .select(
      `*, wordlist_entry_link (*)`,
      { count: "exact" }
    )
    .eq("wordlist_id", wordlistId)
    .order("entry_number")
    .range(offset, offset + limit - 1);

  if (error) return { entries: [], total: 0 };
  return { entries: (data ?? []) as WordlistEntryWithLinks[], total: count ?? 0 };
}

// ── Gloss Source Texts ───────────────────────────────────────

export async function getGlossSources(): Promise<GlossSourceText[]> {
  const { data, error } = await supabase
    .from("gloss_source_text")
    .select("*")
    .order("source_number");

  if (error) return [];
  return (data ?? []) as GlossSourceText[];
}

// ── Image Details ────────────────────────────────────────────

export async function getImageDetails(page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;

  const { data, count, error } = await supabase
    .from("image_detail")
    .select("*", { count: "exact" })
    .order("filename")
    .range(offset, offset + limit - 1);

  if (error) return { images: [], total: 0 };
  return { images: (data ?? []) as ImageDetail[], total: count ?? 0 };
}

// ── Structural Pages ─────────────────────────────────────────

export async function getStructuralPages(): Promise<StructuralPage[]> {
  const { data, error } = await supabase
    .from("structural_page")
    .select("id, filename, title, updated")
    .order("filename");

  if (error) return [];
  return (data ?? []) as StructuralPage[];
}

export async function getStructuralPage(id: number): Promise<StructuralPage | null> {
  const { data, error } = await supabase
    .from("structural_page")
    .select("*")
    .eq("id", id)
    .single();

  if (error) return null;
  return data as StructuralPage;
}

// ── All Table Stats (27 tables) ──────────────────────────────

export async function getAllTableStats() {
  const tables = [
    "entry", "sense", "sub_definition", "sub_definition_domain",
    "linked_word", "example", "word_token", "etymology",
    "cross_ref", "grammar_ref", "hawaiian_gloss", "image",
    "alt_spelling", "topic", "entry_topic",
    "eng_haw_entry", "eng_haw_translation",
    "concordance", "reference",
    "dictionary_source", "preface", "wordlist", "wordlist_entry",
    "wordlist_entry_link", "gloss_source_text", "image_detail",
    "structural_page",
  ];

  const results = await Promise.all(
    tables.map(async (table) => {
      const { count, error } = await supabase
        .from(table)
        .select("*", { count: "exact", head: true });
      return { table, count: error ? 0 : (count ?? 0) };
    })
  );

  return results;
}
