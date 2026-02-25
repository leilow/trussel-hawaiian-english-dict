import Link from "next/link";
import { notFound } from "next/navigation";
import { getStructuralPage } from "@/lib/queries";

export default async function StructuralPageDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const page = await getStructuralPage(parseInt(id, 10));
  if (!page) notFound();

  return (
    <>
      <p><Link href="/pages">&larr; Back to pages</Link></p>
      <h1>{page.title || page.filename}</h1>

      <table>
        <tbody>
          <tr><td><strong>Filename</strong></td><td className="mono">{page.filename}</td></tr>
          <tr><td><strong>Updated</strong></td><td>{page.updated || "—"}</td></tr>
          <tr><td><strong>Internal Links</strong></td><td className="small">{page.internal_links?.length || 0}</td></tr>
          <tr><td><strong>External Links</strong></td><td className="small">{page.external_links?.length || 0}</td></tr>
          <tr><td><strong>Referenced Assets</strong></td><td className="small">{page.referenced_assets?.length || 0}</td></tr>
        </tbody>
      </table>

      {/* Sections (JSONB) */}
      {page.sections && (
        <div className="detail-section">
          <h2>Sections</h2>
          <pre style={{ background: "#f5f0e0", padding: 12, overflow: "auto", fontSize: "0.8rem", border: "1px solid #ccc" }}>
            {JSON.stringify(page.sections, null, 2)}
          </pre>
        </div>
      )}

      {/* Internal links */}
      {page.internal_links && page.internal_links.length > 0 && (
        <div className="detail-section">
          <h2>Internal Links</h2>
          <ul>
            {page.internal_links.map((link, i) => (
              <li key={i} className="mono small">{link}</li>
            ))}
          </ul>
        </div>
      )}

      {/* External links */}
      {page.external_links && page.external_links.length > 0 && (
        <div className="detail-section">
          <h2>External Links</h2>
          <ul>
            {page.external_links.map((link, i) => (
              <li key={i} className="small">
                <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
