import { LetterNav } from "@/components/LetterNav";
import { EntryCard } from "@/components/EntryCard";

const mockEntriesByLetter: Record<string, Array<{ id: string; headword: string; source: string; definition: string }>> = {
  a: [
    { id: "1", headword: "aloha", source: "PE", definition: "Love, affection, compassion, mercy, sympathy, pity, kindness." },
    { id: "2", headword: "aloha ʻāina", source: "PE", definition: "Love of the land, patriotism." },
    { id: "7", headword: "ahi", source: "PE", definition: "Fire; to burn." },
    { id: "8", headword: "ahupuaʻa", source: "PE", definition: "Land division usually extending from the uplands to the sea." },
    { id: "9", headword: "ʻai", source: "PE", definition: "Food, especially vegetable food as distinguished from iʻa; to eat." },
    { id: "10", headword: "aikāne", source: "PE", definition: "Friend, friendly." },
    { id: "11", headword: "ʻaina", source: "PE", definition: "Meal, to eat." },
    { id: "12", headword: "akua", source: "PE", definition: "God, goddess, spirit, ghost, devil, image, idol." },
    { id: "13", headword: "ala", source: "PE", definition: "Path, road, trail; to wake up, to rise." },
    { id: "14", headword: "aliʻi", source: "PE", definition: "Chief, chiefess, ruler, monarch, queen, king." },
  ],
};

function getMockEntries(letter: string) {
  if (mockEntriesByLetter[letter]) return mockEntriesByLetter[letter];
  // Generate plausible entries for other letters
  const letterUpper = letter.replace("ʻ", "").toUpperCase();
  return Array.from({ length: 10 }, (_, i) => ({
    id: `${letter}-${i}`,
    headword: `${letter}${["ala", "ele", "iki", "oku", "ulu", "ane", "imo", "ope", "una", "ahi"][i]}`,
    source: ["PE", "MK", "Andrews", "PE", "PE", "MK", "PE", "Andrews", "PE", "PE"][i],
    definition: `Definition for ${letter}-word ${i + 1}. A common Hawaiian word starting with ${letterUpper}.`,
  }));
}

export default async function BrowseLetterPage({
  params,
}: {
  params: Promise<{ letter: string }>;
}) {
  const { letter } = await params;
  const decodedLetter = decodeURIComponent(letter);
  const entries = getMockEntries(decodedLetter);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <LetterNav activeLetter={decodedLetter} />
      </div>

      <h1 className="text-3xl font-bold mb-6">
        Entries starting with <span className="text-accent">{decodedLetter.toUpperCase()}</span>
      </h1>

      <div className="space-y-3 mb-8">
        {entries.map((entry) => (
          <EntryCard
            key={entry.id}
            id={entry.id}
            headword={entry.headword}
            source={entry.source}
            definition={entry.definition}
          />
        ))}
      </div>

      {/* Pagination placeholder */}
      <div className="text-center text-sm text-muted font-mono">
        Showing 1&ndash;10 of 3,241
      </div>
    </div>
  );
}
