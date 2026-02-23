export default async function ConcordanceWordPage({
  params,
}: {
  params: Promise<{ word: string }>;
}) {
  const { word } = await params;
  const decodedWord = decodeURIComponent(word);

  const mockSentences = [
    { id: 1, hawaiian: `Ua ${decodedWord} aku nei au iā ia.`, english: `I ${decodedWord} to them.` },
    { id: 2, hawaiian: `He mea nui ka ${decodedWord} i ka nohona Hawaiʻi.`, english: `The ${decodedWord} is important in Hawaiian life.` },
    { id: 3, hawaiian: `E ${decodedWord} mai, e ke keiki.`, english: `Please ${decodedWord}, child.` },
    { id: 4, hawaiian: `ʻO ka ${decodedWord} ka mea maikaʻi loa.`, english: `The ${decodedWord} is the best thing.` },
    { id: 5, hawaiian: `Ua loaʻa ka ${decodedWord} ma ka moʻolelo kahiko.`, english: `The ${decodedWord} was found in the ancient story.` },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-3xl font-bold mb-2">
        Concordance: <span className="text-accent">{decodedWord}</span>
      </h1>
      <p className="text-sm text-muted font-mono mb-8">5 occurrences</p>

      <div className="space-y-3">
        {mockSentences.map((s) => (
          <div key={s.id} className="card p-4">
            <p className="text-foreground leading-relaxed mb-1">
              {s.hawaiian.split(new RegExp(`(${decodedWord})`, "gi")).map((part, i) =>
                part.toLowerCase() === decodedWord.toLowerCase() ? (
                  <mark key={i} className="bg-accent/20 text-foreground px-0.5 rounded">
                    {part}
                  </mark>
                ) : (
                  <span key={i}>{part}</span>
                )
              )}
            </p>
            <p className="text-sm text-muted">{s.english}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
