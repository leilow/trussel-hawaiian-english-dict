import { getAllTableStats, getEntriesBySource, getEntriesByLetter_stats } from "@/lib/queries";

export default async function StatisticsPage() {
  const [tableStats, sourceData, letterData] = await Promise.all([
    getAllTableStats(),
    getEntriesBySource(),
    getEntriesByLetter_stats(),
  ]);

  const grandTotal = tableStats.reduce((sum, t) => sum + t.count, 0);

  return (
    <>
      <h1>Statistics — All 27 Tables</h1>
      <p className="muted">Grand total: {grandTotal.toLocaleString()} rows</p>

      <h2>Table Row Counts</h2>
      <table>
        <thead>
          <tr>
            <th>Table</th>
            <th>Rows</th>
          </tr>
        </thead>
        <tbody>
          {tableStats.map((t) => (
            <tr key={t.table}>
              <td className="mono">{t.table}</td>
              <td>{t.count.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Entries by Source</h2>
      <table>
        <thead>
          <tr><th>Source</th><th>Entries</th></tr>
        </thead>
        <tbody>
          {sourceData.map((s) => (
            <tr key={s.source}>
              <td>{s.source}</td>
              <td>{s.entries.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Entries by Letter</h2>
      <table>
        <thead>
          <tr><th>Letter</th><th>Entries</th></tr>
        </thead>
        <tbody>
          {letterData.map((l) => (
            <tr key={l.letter}>
              <td>{l.letter}</td>
              <td>{l.entries.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
