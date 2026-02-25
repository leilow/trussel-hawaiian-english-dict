import { getDictionarySources } from "@/lib/queries";
import { trusselUrl } from "@/components/shared";

export default async function SourcesPage() {
  const sources = await getDictionarySources();

  return (
    <>
      <h1>Dictionary Sources</h1>
      <p className="muted">{sources.length} sources from dictionary_source table</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Source Page</th>
            <th>Anchor</th>
            <th>Title</th>
            <th>Year</th>
            <th>Description</th>
            <th>Cover Images</th>
            <th>PDF</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((s) => (
            <tr key={s.id}>
              <td>{s.id}</td>
              <td className="mono small">{s.source_page}</td>
              <td className="mono">{s.anchor}</td>
              <td><strong>{s.title}</strong></td>
              <td>{s.year || "—"}</td>
              <td className="small">{s.description?.slice(0, 150) || "—"}</td>
              <td className="small">
                {s.cover_images?.map((img, i) => (
                  <a key={i} href={trusselUrl(img)} target="_blank" rel="noopener noreferrer" style={{ marginRight: 4 }}>
                    <img src={trusselUrl(img)} alt={`${s.title} cover ${i + 1}`} style={{ maxHeight: 40, border: "1px solid #ccc", verticalAlign: "middle" }} />
                  </a>
                ))}
                {(!s.cover_images || s.cover_images.length === 0) && "—"}
              </td>
              <td className="small">
                {s.intro_pdf_url && <a href={trusselUrl(s.intro_pdf_url)} target="_blank" rel="noopener noreferrer">PDF</a>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {sources.length === 0 && <p className="muted">No sources found.</p>}
    </>
  );
}
