import Link from "next/link";
import { getConcordanceByLetter } from "@/lib/queries";
import { Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 100;

export default async function ConcordancePage({
  searchParams,
}: {
  searchParams: Promise<{ letter?: string; page?: string }>;
}) {
  const sp = await searchParams;
  const letter = sp.letter || "a";
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  const { sentences, total } = await getConcordanceByLetter(letter, page, ITEMS_PER_PAGE);

  let lastWord = "";

  return (
    <>
      <h1>Concordance</h1>
      <p className="muted">Example sentences indexed by keyword</p>

      <div className="letter-nav">
        {["a","e","h","i","k","l","m","n","o","p","u","w"].map((l) => (
          <Link key={l} href={`/concordance?letter=${l}`} className={letter === l ? "active" : ""}>
            {l.toUpperCase()}
          </Link>
        ))}
      </div>

      <p className="small muted">{total.toLocaleString()} entries for &ldquo;{letter}&rdquo;</p>

      <table>
        <thead>
          <tr>
            <th style={{ width: 120 }}>Word</th>
            <th>Hawaiian</th>
            <th>English</th>
            <th style={{ width: 100 }}>Source</th>
          </tr>
        </thead>
        <tbody>
          {sentences.map((s) => {
            const showWord = s.word !== lastWord;
            lastWord = s.word;
            return (
              <tr key={s.id}>
                <td>
                  {showWord && (
                    <Link href={`/concordance/${encodeURIComponent(s.word)}`}>
                      <strong>{s.word}</strong>
                    </Link>
                  )}
                </td>
                <td><em>{s.hawaiian_text}</em></td>
                <td className="small muted">{s.english_text}</td>
                <td className="small">
                  {s.parent_entry_anchor && (
                    <Link href={`/entry/${s.parent_entry_anchor}`}>{s.parent_entry_anchor}</Link>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {sentences.length === 0 && <p className="muted">No concordance entries found.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath="/concordance"
        searchParams={{ letter }}
      />
    </>
  );
}
