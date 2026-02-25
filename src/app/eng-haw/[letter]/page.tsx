import Link from "next/link";
import { getEngHawByLetter } from "@/lib/queries";
import { EnglishLetterNav, SourceBadges, Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 100;

export default async function EngHawLetterPage({
  params,
  searchParams,
}: {
  params: Promise<{ letter: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { letter } = await params;
  const sp = await searchParams;
  const decoded = decodeURIComponent(letter).toLowerCase();
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  const { entries, total } = await getEngHawByLetter(decoded, page, ITEMS_PER_PAGE);

  return (
    <>
      <h1>English-Hawaiian: {decoded.toUpperCase()}</h1>
      <EnglishLetterNav basePath="/eng-haw" activeLetter={decoded} />
      <p className="small muted">{total.toLocaleString()} entries</p>

      <table>
        <thead>
          <tr>
            <th>English</th>
            <th>Source</th>
            <th>Hawaiian Translations</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.id}>
              <td><strong>{e.english_word}</strong></td>
              <td><SourceBadges source={e.source} /></td>
              <td>
                {e.eng_haw_translation.map((t, i) => (
                  <span key={t.id}>
                    {i > 0 && ", "}
                    {t.target_anchor ? (
                      <Link href={`/entry/${t.target_anchor}`}>{t.hawaiian_word || t.target_anchor}</Link>
                    ) : (
                      t.hawaiian_word || "?"
                    )}
                  </span>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {entries.length === 0 && <p className="muted">No entries found.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath={`/eng-haw/${decoded}`}
      />
    </>
  );
}
