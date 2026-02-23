import Link from "next/link";

const wordLists = [
  { author: "Anderson", year: 1778, slug: "anderson-1778", count: 229 },
  { author: "Samwell", year: 1779, slug: "samwell-1779", count: 185 },
  { author: "Beresford", year: 1787, slug: "beresford-1787", count: 142 },
  { author: "Martinez", year: 1789, slug: "martinez-1789", count: 97 },
  { author: "Santeliz", year: 1791, slug: "santeliz-1791", count: 113 },
  { author: "Quimper", year: 1791, slug: "quimper-1791", count: 68 },
  { author: "Lisiansky", year: 1804, slug: "lisiansky-1804", count: 201 },
  { author: "Campbell", year: 1809, slug: "campbell-1809", count: 156 },
  { author: "Gaimard", year: 1819, slug: "gaimard-1819", count: 310 },
  { author: "Bishop", year: 1825, slug: "bishop-1825", count: 178 },
  { author: "Botta", year: 1828, slug: "botta-1828", count: 245 },
  { author: "Dumont", year: 1834, slug: "dumont-1834", count: 192 },
];

export default function WordListsPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">Historical Word Lists</h1>
      <p className="text-muted mb-8">
        Vocabulary recorded by early Western visitors to the Hawaiian Islands
      </p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {wordLists.map((list) => (
          <Link key={list.slug} href={`/word-lists/${list.slug}`} className="block">
            <div className="card p-5 hover:shadow-md transition-shadow h-full">
              <h2 className="text-lg font-semibold text-foreground mb-1">
                {list.author}
              </h2>
              <div className="flex items-center gap-3 text-sm text-muted">
                <span className="font-mono">{list.year}</span>
                <span>&middot;</span>
                <span className="font-mono">{list.count} entries</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
