export default async function WordListDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const parts = slug.split("-");
  const year = parts.pop();
  const author = parts.map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");

  const mockRows = [
    { num: 1, original: "Aroha", modern: "aloha", gloss: "love, greeting", notes: "Common across Polynesia" },
    { num: 2, original: "Taboo", modern: "kapu", gloss: "forbidden, sacred", notes: "T/K correspondence" },
    { num: 3, original: "Taro", modern: "kalo", gloss: "taro plant", notes: "Staple food" },
    { num: 4, original: "Waheine", modern: "wahine", gloss: "woman", notes: "Spelling variation" },
    { num: 5, original: "Kanaka", modern: "kanaka", gloss: "person, human", notes: "Pan-Polynesian" },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">
        {author} ({year})
      </h1>
      <p className="text-muted leading-relaxed mb-8 max-w-3xl">
        A vocabulary list recorded by {author} during their visit to the Hawaiian Islands
        in {year}. These early word lists provide valuable evidence of Hawaiian pronunciation
        and vocabulary as perceived by Western visitors prior to the standardization of
        Hawaiian orthography.
      </p>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-card-border">
                <th className="text-left font-mono text-xs uppercase tracking-wider text-muted p-3 w-12">#</th>
                <th className="text-left font-mono text-xs uppercase tracking-wider text-muted p-3">Original Form</th>
                <th className="text-left font-mono text-xs uppercase tracking-wider text-muted p-3">Modern Hawaiian</th>
                <th className="text-left font-mono text-xs uppercase tracking-wider text-muted p-3">English Gloss</th>
                <th className="text-left font-mono text-xs uppercase tracking-wider text-muted p-3">Notes</th>
              </tr>
            </thead>
            <tbody>
              {mockRows.map((row) => (
                <tr key={row.num} className="border-b border-card-border/50 hover:bg-card/80 transition-colors">
                  <td className="p-3 font-mono text-muted">{row.num}</td>
                  <td className="p-3 italic">{row.original}</td>
                  <td className="p-3 font-semibold text-accent">{row.modern}</td>
                  <td className="p-3 text-muted">{row.gloss}</td>
                  <td className="p-3 text-xs text-muted">{row.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
