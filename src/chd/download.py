"""Download raw HTML pages from trussel2.com/HAW/.

Features:
- Page manifest covering all page types
- Dynamic discovery of topical and concordance overflow pages
- Rate limiting (1.5s delay between requests)
- Skip-if-exists (unless --force)
- manifest.json log of all downloads
- CLI with --category filter
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://trussel2.com/HAW/"
RAW_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
DELAY = 1.5  # seconds between requests

# Hawaiian letters (core 12 + 11 loan letters)
HAW_CORE_LETTERS = list("aehiklmnopuw")
LOAN_LETTERS = list("bcdfgjrstvz")
ALL_HAW_LETTERS = HAW_CORE_LETTERS + LOAN_LETTERS

ENG_LETTERS = list("abcdefghijklmnopqrstuvwxyz")
REV_VOWELS = list("aeiou")


def _build_manifest() -> dict[str, list[str]]:
    """Build the complete page manifest by category."""
    return {
        "haw_eng": [f"haw-{l}.htm" for l in ALL_HAW_LETTERS],
        "eng_haw": [f"eng-{l}.htm" for l in ENG_LETTERS],
        "concordance": [f"haw-conc-{l}.htm" for l in ALL_HAW_LETTERS],
        "index": [f"index-{l}.htm" for l in ALL_HAW_LETTERS],
        "reverse_index": [f"rev-{v}.htm" for v in REV_VOWELS],
        "support": [
            "counts.htm",
            "refs.htm",
            "intro.htm",
            "texts.htm",
            "glossrefs.htm",
            "topical.htm",
        ],
    }


def download_page(filename: str, raw_dir: Path = RAW_DIR, force: bool = False) -> dict:
    """Download a single page and save to raw_dir."""
    filepath = raw_dir / filename
    url = BASE_URL + filename

    entry = {
        "filename": filename,
        "url": url,
        "status": "unknown",
        "timestamp": None,
        "size_bytes": 0,
    }

    if filepath.exists() and not force:
        entry["status"] = "skipped"
        entry["size_bytes"] = filepath.stat().st_size
        return entry

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(resp.content)
        entry["status"] = "downloaded"
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["size_bytes"] = len(resp.content)
        entry["http_status"] = resp.status_code
    except requests.RequestException as e:
        entry["status"] = "error"
        entry["error"] = str(e)

    return entry


def discover_topical_pages(raw_dir: Path = RAW_DIR) -> list[str]:
    """Parse topical.htm to discover all topical page filenames."""
    topical_path = raw_dir / "topical.htm"
    if not topical_path.exists():
        return []

    EXCLUDE_PREFIXES = ("eng-", "haw-conc-", "index-", "rev-")
    EXCLUDE_FILES = {"intro.htm", "counts.htm", "refs.htm", "texts.htm", "glossrefs.htm", "topical.htm"}

    soup = BeautifulSoup(topical_path.read_bytes(), "lxml")
    pages = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if not href.endswith(".htm") or href in pages:
            continue
        if any(href == f"haw-{l}.htm" for l in ALL_HAW_LETTERS):
            continue
        if href in EXCLUDE_FILES or any(href.startswith(p) for p in EXCLUDE_PREFIXES):
            continue
        pages.append(href)
    return pages


def discover_concordance_overflow(raw_dir: Path = RAW_DIR) -> list[str]:
    """Parse concordance pages for <a class="more"> overflow links."""
    overflow = []
    for f in sorted(raw_dir.glob("haw-conc-*.htm")):
        soup = BeautifulSoup(f.read_bytes(), "lxml")
        for a_tag in soup.find_all("a", class_="more"):
            href = a_tag.get("href", "")
            if href and href not in overflow:
                overflow.append(href)
    return overflow


def download_all(
    raw_dir: Path = RAW_DIR,
    categories: list[str] | None = None,
    force: bool = False,
    include_dynamic: bool = True,
) -> list[dict]:
    """Download all pages in the manifest."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest = _build_manifest()
    results = []

    if categories:
        manifest = {k: v for k, v in manifest.items() if k in categories}

    total = sum(len(v) for v in manifest.values())
    downloaded = 0

    for category, pages in manifest.items():
        print(f"\n{'=' * 60}")
        print(f"Category: {category} ({len(pages)} pages)")
        print(f"{'=' * 60}")

        for filename in pages:
            downloaded += 1
            entry = download_page(filename, raw_dir, force)
            results.append(entry)

            status_icon = {"downloaded": "+", "skipped": ".", "error": "X"}.get(entry["status"], "?")
            print(f"  [{downloaded}/{total}] {status_icon} {filename} ({entry['status']})")

            if entry["status"] == "downloaded":
                time.sleep(DELAY)

    if include_dynamic:
        if not categories or "topical" in categories:
            topical_pages = discover_topical_pages(raw_dir)
            if topical_pages:
                print(f"\n{'=' * 60}")
                print(f"Discovered {len(topical_pages)} topical pages")
                print(f"{'=' * 60}")
                for filename in topical_pages:
                    entry = download_page(filename, raw_dir, force)
                    results.append(entry)
                    icon = "+" if entry["status"] == "downloaded" else "."
                    print(f"  {icon} {filename} ({entry['status']})")
                    if entry["status"] == "downloaded":
                        time.sleep(DELAY)

        if not categories or "concordance" in categories:
            overflow = discover_concordance_overflow(raw_dir)
            if overflow:
                print(f"\n{'=' * 60}")
                print(f"Discovered {len(overflow)} concordance overflow pages")
                print(f"{'=' * 60}")
                for filename in overflow:
                    entry = download_page(filename, raw_dir, force)
                    results.append(entry)
                    icon = "+" if entry["status"] == "downloaded" else "."
                    print(f"  {icon} {filename} ({entry['status']})")
                    if entry["status"] == "downloaded":
                        time.sleep(DELAY)

    manifest_path = raw_dir / "manifest.json"
    manifest_data = {
        "download_date": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "total_pages": len(results),
        "downloaded": sum(1 for r in results if r["status"] == "downloaded"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "pages": results,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"Download Summary")
    print(f"{'=' * 60}")
    print(f"  Total:      {len(results)}")
    print(f"  Downloaded: {manifest_data['downloaded']}")
    print(f"  Skipped:    {manifest_data['skipped']}")
    print(f"  Errors:     {manifest_data['errors']}")
    print(f"  Manifest:   {manifest_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Download raw HTML pages from trussel2.com/HAW/")
    parser.add_argument(
        "--category",
        choices=["haw_eng", "eng_haw", "concordance", "index", "reverse_index", "support", "topical"],
        nargs="+",
        help="Download only specific categories",
    )
    parser.add_argument("--force", action="store_true", help="Re-download even if files already exist")
    parser.add_argument("--no-dynamic", action="store_true", help="Skip dynamic discovery of topical/overflow pages")

    args = parser.parse_args()
    download_all(
        categories=args.category,
        force=args.force,
        include_dynamic=not args.no_dynamic,
    )


if __name__ == "__main__":
    main()
