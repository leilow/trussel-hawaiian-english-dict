import Link from "next/link";
import { getConcordanceByWord } from "@/lib/queries";
import { Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 100;

export default async function ConcordanceWordPage({
  params,
  searchParams,
}: {
  params: Promise<{ word: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { word } = await params;
  const sp = await searchParams;
  const decoded = decodeURIComponent(word);
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  const { sentences, total } = await getConcordanceByWord(decoded, page, ITEMS_PER_PAGE);

  return (
    <>
      <p><Link href="/concordance">&larr; Back to concordance</Link></p>
      <h1>Concordance: {decoded}</h1>
      <p className="small muted">{total.toLocaleString()} occurrences</p>

      <table>
        <thead>
          <tr>
            <th>Hawaiian</th>
            <th>English</th>
            <th style={{ width: 100 }}>Source</th>
          </tr>
        </thead>
        <tbody>
          {sentences.map((s) => (
            <tr key={s.id}>
              <td><em>{s.hawaiian_text}</em></td>
              <td className="small muted">{s.english_text}</td>
              <td className="small">
                {s.parent_entry_anchor && (
                  <Link href={`/entry/${s.parent_entry_anchor}`}>{s.parent_entry_anchor}</Link>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {sentences.length === 0 && <p className="muted">No entries found for &ldquo;{decoded}&rdquo;.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath={`/concordance/${encodeURIComponent(decoded)}`}
      />
    </>
  );
}
