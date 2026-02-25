import Link from "next/link";
import { getStats, getRandomEntry } from "@/lib/queries";
import { SourceBadges } from "@/components/shared";

export default async function HomePage() {
  const [stats, wordOfDay] = await Promise.all([getStats(), getRandomEntry()]);

  return (
    <>
      <h1>Trussel Hawaiian-English Dictionary</h1>
      <p className="muted">Data validation browser — all 27 tables</p>

      <h2>Quick Stats</h2>
      <table>
        <tbody>
          <tr><td>Entries</td><td>{stats.entries.toLocaleString()}</td></tr>
          <tr><td>Senses</td><td>{stats.senses.toLocaleString()}</td></tr>
          <tr><td>Examples</td><td>{stats.examples.toLocaleString()}</td></tr>
          <tr><td>Concordance</td><td>{stats.concordance.toLocaleString()}</td></tr>
          <tr><td>Cross-refs</td><td>{stats.crossRefs.toLocaleString()}</td></tr>
          <tr><td>Etymologies</td><td>{stats.etymologies.toLocaleString()}</td></tr>
          <tr><td>Eng-Haw</td><td>{stats.engHaw.toLocaleString()}</td></tr>
          <tr><td>References</td><td>{stats.references.toLocaleString()}</td></tr>
        </tbody>
      </table>

      {wordOfDay && (
        <>
          <h2>Word of the Day</h2>
          <p>
            <Link href={`/entry/${wordOfDay.id}`}>
              <strong>{wordOfDay.headword}</strong>
              {wordOfDay.subscript && <sub>{wordOfDay.subscript}</sub>}
            </Link>{" "}
            <SourceBadges in_pe={wordOfDay.in_pe} in_mk={wordOfDay.in_mk} in_andrews={wordOfDay.in_andrews} is_from_eh_only={wordOfDay.is_from_eh_only} />
            {wordOfDay.sense?.[0]?.definition_text && (
              <> — {wordOfDay.sense[0].definition_text}</>
            )}
          </p>
        </>
      )}

      <h2>Browse</h2>
      <ul>
        <li><Link href="/browse">Hawaiian-English (by letter)</Link></li>
        <li><Link href="/eng-haw">English-Hawaiian (by letter)</Link></li>
        <li><Link href="/concordance">Concordance</Link></li>
        <li><Link href="/topics">Topics</Link></li>
        <li><Link href="/references">References</Link></li>
        <li><Link href="/search">Search</Link></li>
      </ul>

      <h2>Phase 2-5 Data</h2>
      <ul>
        <li><Link href="/sources">Dictionary Sources</Link></li>
        <li><Link href="/prefaces">Prefaces</Link></li>
        <li><Link href="/wordlists">Wordlists</Link></li>
        <li><Link href="/gloss-sources">Gloss Source Texts</Link></li>
        <li><Link href="/images">Image Details</Link></li>
        <li><Link href="/pages">Structural Pages</Link></li>
        <li><Link href="/statistics">All 27 Table Statistics</Link></li>
      </ul>
    </>
  );
}
