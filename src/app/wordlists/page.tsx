import Link from "next/link";
import { getWordlists } from "@/lib/queries";

export default async function WordlistsPage() {
  const wordlists = await getWordlists();

  return (
    <>
      <h1>Wordlists</h1>
      <p className="muted">{wordlists.length} wordlists from wordlist table</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Title</th>
            <th>Author</th>
            <th>Year</th>
            <th>Entries</th>
          </tr>
        </thead>
        <tbody>
          {wordlists.map((w) => (
            <tr key={w.id}>
              <td>{w.id}</td>
              <td className="mono small">{w.filename}</td>
              <td><Link href={`/wordlists/${w.id}`}><strong>{w.title}</strong></Link></td>
              <td className="small">{w.author || "—"}</td>
              <td>{w.year || "—"}</td>
              <td>{w.entry_count}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {wordlists.length === 0 && <p className="muted">No wordlists found.</p>}
    </>
  );
}
