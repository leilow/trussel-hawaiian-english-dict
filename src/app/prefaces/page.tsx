import Link from "next/link";
import { getPrefaces } from "@/lib/queries";

export default async function PrefacesPage() {
  const prefaces = await getPrefaces();

  return (
    <>
      <h1>Prefaces</h1>
      <p className="muted">{prefaces.length} prefaces from preface table</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Title</th>
            <th>Subtitle</th>
            <th>Year/Edition</th>
          </tr>
        </thead>
        <tbody>
          {prefaces.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td className="mono small">{p.filename}</td>
              <td><Link href={`/prefaces/${p.id}`}><strong>{p.title}</strong></Link></td>
              <td className="small">{p.subtitle || "—"}</td>
              <td>{p.year_edition || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {prefaces.length === 0 && <p className="muted">No prefaces found.</p>}
    </>
  );
}
