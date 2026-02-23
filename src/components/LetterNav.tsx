import Link from "next/link";

const HAWAIIAN_LETTERS = [
  "a", "e", "h", "i", "k", "l", "m", "n", "o", "p", "u", "w",
  "ʻa", "ʻe", "ʻi", "ʻo", "ʻu",
];

export function LetterNav({ activeLetter }: { activeLetter?: string }) {
  return (
    <nav className="flex flex-wrap gap-1 justify-center">
      {HAWAIIAN_LETTERS.map((letter) => (
        <Link
          key={letter}
          href={`/browse/${encodeURIComponent(letter)}`}
          className={`letter-link ${activeLetter === letter ? "active" : ""}`}
        >
          {letter.toUpperCase()}
        </Link>
      ))}
    </nav>
  );
}
