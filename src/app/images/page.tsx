import { getImageDetails } from "@/lib/queries";
import { Pagination, trusselUrl } from "@/components/shared";

const ITEMS_PER_PAGE = 50;

export default async function ImagesPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const sp = await searchParams;
  const page = Math.max(1, parseInt(sp.page || "1", 10));

  const { images, total } = await getImageDetails(page, ITEMS_PER_PAGE);

  return (
    <>
      <h1>Image Details</h1>
      <p className="muted">{total} images from image_detail table</p>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Filename</th>
            <th>Headword</th>
            <th>Caption</th>
            <th>Credit</th>
            <th>Preview</th>
          </tr>
        </thead>
        <tbody>
          {images.map((img) => (
            <tr key={img.id}>
              <td>{img.id}</td>
              <td className="mono small">{img.filename}</td>
              <td>{img.headword_display || "—"}</td>
              <td className="small">{img.caption?.slice(0, 100) || "—"}</td>
              <td className="small">{img.source_credit || "—"}</td>
              <td>
                {img.image_url && (
                  <a href={trusselUrl(img.image_url)} target="_blank" rel="noopener noreferrer">
                    <img src={trusselUrl(img.image_url)} alt={img.caption || img.filename} style={{ maxHeight: 50, border: "1px solid #ccc" }} />
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {images.length === 0 && <p className="muted">No images found.</p>}

      <Pagination
        currentPage={page}
        totalItems={total}
        itemsPerPage={ITEMS_PER_PAGE}
        basePath="/images"
      />
    </>
  );
}
