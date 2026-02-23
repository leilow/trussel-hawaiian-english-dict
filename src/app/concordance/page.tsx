import Link from "next/link";
import { SearchBar } from "@/components/SearchBar";

const mockSentences = [
  { id: 1, hawaiian: "Aloha kākou, e nā hoaaloha.", english: "Greetings to us all, friends.", word: "aloha", wordHref: "/concordance/aloha" },
  { id: 2, hawaiian: "Ua hele au i ka hale kūʻai.", english: "I went to the store.", word: "hele", wordHref: "/concordance/hele" },
  { id: 3, hawaiian: "Nani ka moana i kēia lā.", english: "The ocean is beautiful today.", word: "moana", wordHref: "/concordance/moana" },
  { id: 4, hawaiian: "E ʻai kākou i ka paina.", english: "Let us eat at the feast.", word: "ʻai", wordHref: "/concordance/%CA%BBai" },
  { id: 5, hawaiian: "Ua hoʻi mai ka makua i ka hale.", english: "The parent returned home.", word: "makua", wordHref: "/concordance/makua" },
  { id: 6, hawaiian: "He mea nui ka ʻōlelo Hawaiʻi.", english: "The Hawaiian language is important.", word: "ʻōlelo", wordHref: "/concordance/%CA%BB%C5%8Dlelo" },
  { id: 7, hawaiian: "Mahalo nui loa iā ʻoe.", english: "Thank you very much.", word: "mahalo", wordHref: "/concordance/mahalo" },
  { id: 8, hawaiian: "E noho mai i ka noho.", english: "Sit down on the chair.", word: "noho", wordHref: "/concordance/noho" },
  { id: 9, hawaiian: "Ua hana mākou i ka lā āpau.", english: "We worked all day.", word: "hana", wordHref: "/concordance/hana" },
  { id: 10, hawaiian: "ʻO Maui ka mokupuni maikaʻi.", english: "Maui is the good island.", word: "mokupuni", wordHref: "/concordance/mokupuni" },
];

function highlightWord(sentence: string, word: string) {
  const regex = new RegExp(`(${word})`, "gi");
  const parts = sentence.split(regex);
  return parts.map((part, i) =>
    part.toLowerCase() === word.toLowerCase() ? (
      <mark key={i} className="bg-accent/20 text-foreground px-0.5 rounded">
        {part}
      </mark>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

export default function ConcordancePage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">Concordance</h1>
      <p className="text-muted mb-6">Browse 133,684 sentences from Hawaiian texts</p>

      <div className="mb-8">
        <SearchBar />
      </div>

      <div className="space-y-3">
        {mockSentences.map((s) => (
          <div key={s.id} className="card p-4">
            <p className="text-foreground leading-relaxed mb-1">
              {highlightWord(s.hawaiian, s.word)}
            </p>
            <p className="text-sm text-muted mb-2">{s.english}</p>
            <Link
              href={s.wordHref}
              className="font-mono text-xs text-accent hover:underline"
            >
              {s.word}
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
