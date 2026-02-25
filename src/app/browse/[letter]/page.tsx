import Link from "next/link";
import { getEntriesByLetter } from "@/lib/queries";
import { HawaiianLetterNav, SourceBadges, Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 100;

export default async function BrowseLetterPage({
  params,
  searchParams,
}: {
  params: Promise<{ letter: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { letter } = await params;
  const sp = await searchParams;
  const decoded = decodeURIComponent(letter);
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  const { entries, total } = await getEntriesByLetter(decoded, page, ITEMS_PER_PAGE);

  return (
    <>
      <h1>Hawaiian-English: {decoded.toUpperCase()}</h1>
      <HawaiianLetterNav basePath="/browse" activeLetter={decoded} />
      <p className="small muted">{total.toLocaleString()} entries</p>

      <table>
        <thead>
          <tr>
            <th>Headword</th>
            <th>Sources</th>
            <th>First Definition</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.id}>
              <td>
                <Link href={`/entry/${e.id}`}>
                  {e.headword_display || e.headword}
                  {e.subscript && <sub>{e.subscript}</sub>}
                </Link>
              </td>
              <td>
                <SourceBadges in_pe={e.in_pe} in_mk={e.in_mk} in_andrews={e.in_andrews} is_from_eh_only={e.is_from_eh_only} />
              </td>
              <td className="small">{e.sense?.[0]?.definition_text?.slice(0, 120) || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {entries.length === 0 && <p className="muted">No entries found.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath={`/browse/${encodeURIComponent(decoded)}`}
      />
    </>
  );
}
