import Link from "next/link";
import { getStructuralPages } from "@/lib/queries";

export default async function StructuralPagesPage() {
  const pages = await getStructuralPages();

  return (
    <>
      <h1>Structural Pages</h1>
      <p className="muted">{pages.length} pages from structural_page table</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Title</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {pages.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td className="mono small">{p.filename}</td>
              <td><Link href={`/pages/${p.id}`}><strong>{p.title || p.filename}</strong></Link></td>
              <td className="small">{p.updated || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {pages.length === 0 && <p className="muted">No structural pages found.</p>}
    </>
  );
}
