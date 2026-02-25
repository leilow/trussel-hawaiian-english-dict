import Link from "next/link";

// ── Trussel Base URL ─────────────────────────────────────────
// All image/PDF URLs in the DB are relative (e.g. "images/aalii.jpg").
// Prepend the base URL to make them absolute.

const TRUSSEL_BASE = "https://trussel2.com/HAW/";

export function trusselUrl(relativePath: string | null | undefined): string {
  if (!relativePath) return "";
  // Already absolute
  if (relativePath.startsWith("http://") || relativePath.startsWith("https://")) {
    return relativePath;
  }
  return `${TRUSSEL_BASE}${relativePath}`;
}

// ── Source Badges ────────────────────────────────────────────

export function SourceBadges({
  in_pe,
  in_mk,
  in_andrews,
  is_from_eh_only,
  source,
}: {
  in_pe?: boolean;
  in_mk?: boolean;
  in_andrews?: boolean;
  is_from_eh_only?: boolean;
  source?: string;
}) {
  // Single source mode (for eng-haw entries)
  if (source) {
    const cls =
      source === "PE" ? "badge-pe" :
      source === "MK" ? "badge-mk" :
      source === "Andrews" ? "badge-andrews" :
      source === "EH" ? "badge-eh" : "badge-other";
    return <span className={`badge ${cls}`}>{source}</span>;
  }

  return (
    <span>
      {in_pe && <span className="badge badge-pe">PE</span>}
      {in_mk && <span className="badge badge-mk">MK</span>}
      {in_andrews && <span className="badge badge-andrews">And</span>}
      {is_from_eh_only && <span className="badge badge-eh">EH</span>}
    </span>
  );
}

// ── Hawaiian Letter Nav ──────────────────────────────────────

const HAWAIIAN_LETTERS = ["a", "e", "h", "i", "k", "l", "m", "n", "o", "p", "u", "w"];

export function HawaiianLetterNav({
  basePath,
  activeLetter,
}: {
  basePath: string;
  activeLetter?: string;
}) {
  return (
    <div className="letter-nav">
      {HAWAIIAN_LETTERS.map((l) => (
        <Link
          key={l}
          href={`${basePath}/${l}`}
          className={activeLetter === l ? "active" : ""}
        >
          {l.toUpperCase()}
        </Link>
      ))}
    </div>
  );
}

// ── English Letter Nav ───────────────────────────────────────

const ENGLISH_LETTERS = "abcdefghijklmnopqrstuvwxyz".split("");

export function EnglishLetterNav({
  basePath,
  activeLetter,
}: {
  basePath: string;
  activeLetter?: string;
}) {
  return (
    <div className="letter-nav">
      {ENGLISH_LETTERS.map((l) => (
        <Link
          key={l}
          href={`${basePath}/${l}`}
          className={activeLetter === l ? "active" : ""}
        >
          {l.toUpperCase()}
        </Link>
      ))}
    </div>
  );
}

// ── Pagination ───────────────────────────────────────────────

export function Pagination({
  currentPage,
  totalItems,
  itemsPerPage,
  basePath,
  searchParams,
}: {
  currentPage: number;
  totalItems: number;
  itemsPerPage: number;
  basePath: string;
  searchParams?: Record<string, string>;
}) {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  if (totalPages <= 1) return null;

  function pageUrl(page: number) {
    const params = new URLSearchParams(searchParams);
    params.set("page", String(page));
    return `${basePath}?${params.toString()}`;
  }

  // Show window of pages around current
  const pages: number[] = [];
  const start = Math.max(1, currentPage - 3);
  const end = Math.min(totalPages, currentPage + 3);
  for (let i = start; i <= end; i++) pages.push(i);

  return (
    <div className="pagination">
      {currentPage > 1 && <Link href={pageUrl(currentPage - 1)}>&laquo; Prev</Link>}
      {start > 1 && <Link href={pageUrl(1)}>1</Link>}
      {start > 2 && <span>...</span>}
      {pages.map((p) =>
        p === currentPage ? (
          <span key={p} className="current">{p}</span>
        ) : (
          <Link key={p} href={pageUrl(p)}>{p}</Link>
        )
      )}
      {end < totalPages - 1 && <span>...</span>}
      {end < totalPages && <Link href={pageUrl(totalPages)}>{totalPages}</Link>}
      {currentPage < totalPages && <Link href={pageUrl(currentPage + 1)}>Next &raquo;</Link>}
    </div>
  );
}
