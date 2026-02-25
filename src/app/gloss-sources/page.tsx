import { getGlossSources } from "@/lib/queries";
import { trusselUrl } from "@/components/shared";

export default async function GlossSourcesPage() {
  const sources = await getGlossSources();

  return (
    <>
      <h1>Gloss Source Texts</h1>
      <p className="muted">{sources.length} sources from gloss_source_text table</p>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Hawaiian Title</th>
            <th>Author</th>
            <th>Publisher</th>
            <th>Year</th>
            <th>Pages</th>
            <th>Cover</th>
            <th>Ulukau</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((s) => (
            <tr key={s.id}>
              <td>{s.source_number}</td>
              <td><strong>{s.hawaiian_title}</strong></td>
              <td className="small">{s.author_info || "—"}</td>
              <td className="small">{s.publisher || "—"}</td>
              <td>{s.year || "—"}</td>
              <td>{s.page_count || "—"}</td>
              <td className="small">
                {s.cover_image_url && (
                  <a href={trusselUrl(s.cover_image_url)} target="_blank" rel="noopener noreferrer">
                    <img src={trusselUrl(s.cover_image_url)} alt={s.hawaiian_title} style={{ maxHeight: 40, border: "1px solid #ccc" }} />
                  </a>
                )}
              </td>
              <td className="small">
                {s.ulukau_url && <a href={s.ulukau_url} target="_blank" rel="noopener noreferrer">link</a>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {sources.length === 0 && <p className="muted">No gloss sources found.</p>}
    </>
  );
}
