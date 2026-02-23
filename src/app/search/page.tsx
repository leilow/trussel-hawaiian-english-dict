import Link from "next/link";
import { SearchBar } from "@/components/SearchBar";
import { EntryCard } from "@/components/EntryCard";

const mockResults = [
  { id: "1", headword: "aloha", source: "PE", pos: "n., v.t., interj.", definition: "Love, affection, compassion, mercy, sympathy, pity, kindness, sentiment, grace, charity; greeting, salutation, regards." },
  { id: "2", headword: "aloha ʻāina", source: "PE", pos: "n.", definition: "Love of the land, patriotism." },
  { id: "3", headword: "aloha ʻoe", source: "PE", pos: "interj.", definition: "Farewell to you, may you be loved. Title of a famous song composed by Queen Liliʻuokalani." },
  { id: "4", headword: "alohilani", source: "PE", pos: "n.", definition: "Bright sky, brightness." },
  { id: "5", headword: "alohi", source: "PE", pos: "v.i.", definition: "To shine, sparkle, glitter." },
];

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; type?: string }>;
}) {
  const { q, type } = await searchParams;
  const searchType = type || "haw-eng";

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <SearchBar defaultValue={q || ""} />
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1 mb-8 border-b border-card-border">
        <Link
          href={q ? `/search?q=${encodeURIComponent(q)}&type=haw-eng` : "/search?type=haw-eng"}
          className={`px-4 py-2 font-mono text-sm border-b-2 transition-colors ${
            searchType === "haw-eng"
              ? "border-accent text-foreground"
              : "border-transparent text-muted hover:text-foreground"
          }`}
        >
          Hawaiian-English
        </Link>
        <Link
          href={q ? `/search?q=${encodeURIComponent(q)}&type=eng-haw` : "/search?type=eng-haw"}
          className={`px-4 py-2 font-mono text-sm border-b-2 transition-colors ${
            searchType === "eng-haw"
              ? "border-accent text-foreground"
              : "border-transparent text-muted hover:text-foreground"
          }`}
        >
          English-Hawaiian
        </Link>
      </div>

      {/* Results */}
      {!q ? (
        <div className="text-center py-16">
          <p className="text-muted text-lg">Enter a search term above</p>
        </div>
      ) : (
        <div>
          <p className="text-sm text-muted mb-4">
            {mockResults.length} results for <span className="font-semibold text-foreground">&ldquo;{q}&rdquo;</span>
          </p>
          <div className="space-y-3">
            {mockResults.map((entry) => (
              <EntryCard
                key={entry.id}
                id={entry.id}
                headword={entry.headword}
                source={entry.source}
                definition={entry.definition}
                pos={entry.pos}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
