import Link from "next/link";
import { notFound } from "next/navigation";
import { getPreface } from "@/lib/queries";

export default async function PrefaceDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const preface = await getPreface(parseInt(id, 10));
  if (!preface) notFound();

  return (
    <>
      <p><Link href="/prefaces">&larr; Back to prefaces</Link></p>
      <h1>{preface.title}</h1>
      {preface.subtitle && <h2>{preface.subtitle}</h2>}

      <table>
        <tbody>
          <tr><td><strong>Filename</strong></td><td className="mono">{preface.filename}</td></tr>
          <tr><td><strong>Year/Edition</strong></td><td>{preface.year_edition || "—"}</td></tr>
          <tr><td><strong>Nav Links</strong></td><td className="small">{preface.nav_links?.join(", ") || "—"}</td></tr>
          <tr><td><strong>Images</strong></td><td className="small">{preface.images?.length || 0} images</td></tr>
          <tr><td><strong>Referenced Assets</strong></td><td className="small">{preface.referenced_assets?.length || 0}</td></tr>
        </tbody>
      </table>

      {preface.prose_html && (
        <div className="detail-section">
          <h2>Prose Content</h2>
          <div
            style={{ border: "1px solid #ccc", padding: 16, background: "#fff", maxHeight: 600, overflow: "auto" }}
            dangerouslySetInnerHTML={{ __html: preface.prose_html }}
          />
        </div>
      )}
    </>
  );
}
