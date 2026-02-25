import { getReferences } from "@/lib/queries";

export default async function ReferencesPage() {
  const refs = await getReferences();

  return (
    <>
      <h1>References</h1>
      <p className="muted">{refs.length} references from database</p>

      <table>
        <thead>
          <tr>
            <th>Abbrev</th>
            <th>Anchor</th>
            <th>Full Text</th>
            <th>URL</th>
          </tr>
        </thead>
        <tbody>
          {refs.map((r) => (
            <tr key={r.id}>
              <td className="mono"><strong>{r.abbreviation}</strong></td>
              <td className="mono small">{r.anchor}</td>
              <td className="small">{r.full_text}</td>
              <td className="small">
                {r.url && <a href={r.url} target="_blank" rel="noopener noreferrer">link</a>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {refs.length === 0 && <p className="muted">No references found.</p>}
    </>
  );
}
