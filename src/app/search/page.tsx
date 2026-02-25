import Link from "next/link";
import { searchEntries, searchEngHaw } from "@/lib/queries";
import { SourceBadges, Pagination } from "@/components/shared";

const ITEMS_PER_PAGE = 50;

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; type?: string; page?: string }>;
}) {
  const { q, type, page: pageStr } = await searchParams;
  const searchType = type || "haw-eng";
  const page = Math.max(1, parseInt(pageStr || "1", 10));

  let hawResults: Awaited<ReturnType<typeof searchEntries>> | null = null;
  let engResults: Awaited<ReturnType<typeof searchEngHaw>> | null = null;

  if (q) {
    if (searchType === "haw-eng") {
      hawResults = await searchEntries(q, page, ITEMS_PER_PAGE);
    } else {
      engResults = await searchEngHaw(q, page, ITEMS_PER_PAGE);
    }
  }

  const totalResults = searchType === "haw-eng" ? (hawResults?.total ?? 0) : (engResults?.total ?? 0);

  return (
    <>
      <h1>Search</h1>

      {/* Search form */}
      <form action="/search" method="get" style={{ marginBottom: 16 }}>
        <input
          type="text"
          name="q"
          defaultValue={q || ""}
          placeholder="Search..."
          style={{ padding: "6px 10px", fontSize: "1rem", width: 300, border: "1px solid #ccc", borderRadius: 3 }}
        />
        <input type="hidden" name="type" value={searchType} />
        <button type="submit" style={{ padding: "6px 16px", marginLeft: 4, cursor: "pointer" }}>Go</button>
      </form>

      {/* Tabs */}
      <p>
        <Link href={q ? `/search?q=${encodeURIComponent(q)}&type=haw-eng` : "/search?type=haw-eng"}>
          {searchType === "haw-eng" ? <strong>[Hawaiian-English]</strong> : "Hawaiian-English"}
        </Link>
        {" | "}
        <Link href={q ? `/search?q=${encodeURIComponent(q)}&type=eng-haw` : "/search?type=eng-haw"}>
          {searchType === "eng-haw" ? <strong>[English-Hawaiian]</strong> : "English-Hawaiian"}
        </Link>
      </p>

      {!q ? (
        <p className="muted">Enter a search term above.</p>
      ) : (
        <>
          <p className="small muted">{totalResults.toLocaleString()} results for &ldquo;{q}&rdquo;</p>

          {searchType === "haw-eng" && hawResults && (
            <table>
              <thead>
                <tr>
                  <th>Headword</th>
                  <th>Sources</th>
                  <th>Definition</th>
                </tr>
              </thead>
              <tbody>
                {hawResults.entries.map((e) => (
                  <tr key={e.id}>
                    <td>
                      <Link href={`/entry/${e.id}`}>
                        {e.headword_display || e.headword}
                        {e.subscript && <sub>{e.subscript}</sub>}
                      </Link>
                    </td>
                    <td><SourceBadges in_pe={e.in_pe} in_mk={e.in_mk} in_andrews={e.in_andrews} is_from_eh_only={e.is_from_eh_only} /></td>
                    <td className="small">{e.sense?.[0]?.definition_text?.slice(0, 120) || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {searchType === "eng-haw" && engResults && (
            <table>
              <thead>
                <tr>
                  <th>English</th>
                  <th>Source</th>
                  <th>Hawaiian Translations</th>
                </tr>
              </thead>
              <tbody>
                {engResults.entries.map((e) => (
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
          )}

          <Pagination
            currentPage={page}
            totalItems={totalResults}
            itemsPerPage={ITEMS_PER_PAGE}
            basePath="/search"
            searchParams={{ q: q || "", type: searchType }}
          />
        </>
      )}
    </>
  );
}
