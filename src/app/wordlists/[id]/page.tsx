import Link from "next/link";
import { notFound } from "next/navigation";
import { getWordlist, getWordlistEntries } from "@/lib/queries";
import { Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 100;

export default async function WordlistDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ page?: string }>;
}) {
  const { id } = await params;
  const sp = await searchParams;
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  const wordlist = await getWordlist(parseInt(id, 10));
  if (!wordlist) notFound();

  const { entries, total } = await getWordlistEntries(wordlist.id, page, ITEMS_PER_PAGE);

  return (
    <>
      <p><Link href="/wordlists">&larr; Back to wordlists</Link></p>
      <h1>{wordlist.title}</h1>

      <table>
        <tbody>
          <tr><td><strong>Filename</strong></td><td className="mono">{wordlist.filename}</td></tr>
          <tr><td><strong>Author</strong></td><td>{wordlist.author || "—"}</td></tr>
          <tr><td><strong>Year</strong></td><td>{wordlist.year || "—"}</td></tr>
          <tr><td><strong>Entry Count</strong></td><td>{wordlist.entry_count}</td></tr>
        </tbody>
      </table>

      {wordlist.intro_text && (
        <div className="detail-section">
          <h2>Introduction</h2>
          <p className="small">{wordlist.intro_text}</p>
        </div>
      )}

      <h2>Entries ({total})</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>List Word</th>
            <th>Modern Hawaiian</th>
            <th>Gloss</th>
            <th>Links</th>
            <th>Footnote</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.id}>
              <td>{e.entry_number ?? "—"}</td>
              <td><strong>{e.list_word}</strong></td>
              <td>{e.modern_hawaiian || "—"}</td>
              <td className="small">{e.gloss || "—"}</td>
              <td className="small">
                {e.wordlist_entry_link?.map((lk, i) => (
                  <span key={lk.id}>
                    {i > 0 && ", "}
                    {lk.target_anchor ? (
                      <Link href={`/entry/${lk.target_anchor}`}>{lk.surface}</Link>
                    ) : (
                      lk.surface
                    )}
                  </span>
                ))}
              </td>
              <td className="small muted">{e.footnote || ""}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {entries.length === 0 && <p className="muted">No entries found.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath={`/wordlists/${id}`}
      />
    </>
  );
}
