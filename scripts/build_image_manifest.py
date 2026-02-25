#!/usr/bin/env python3
"""Build a deduplicated image manifest from all haw_eng JSON files.

Scans data/processed/haw_eng/*.json, extracts image metadata,
deduplicates by image filename, and writes data/processed/images_manifest.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path("/Users/leimomi/trussel-hawaiian-english-dict")
HAW_ENG_DIR = PROJECT_ROOT / "data" / "processed" / "haw_eng"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "images_manifest.json"


def derive_image_filename(thumbnail_url: str, full_image_url: str) -> str:
    """Derive a canonical image filename for deduplication.

    The thumbnail_url is typically like "images/aalii.jpg" — we use the
    basename of that as the dedup key.  If thumbnail_url is missing or
    has no recognisable image extension, fall back to full_image_url.
    """
    for url in (thumbnail_url, full_image_url):
        if not url:
            continue
        basename = os.path.basename(url)
        if "." in basename:
            return basename
    # Should not happen, but return whatever we have
    return thumbnail_url or full_image_url


def derive_detail_page(full_image_url: str, thumbnail_url: str) -> str:
    """Derive the Trussel detail page URL.

    In the scraped data, full_image_url is already the detail page
    (e.g. "aalii.htm").  If it looks like an .htm(l) page, use it directly.
    Otherwise, derive from the image filename: "images/foo.jpg" -> "foo.htm".
    """
    if full_image_url and full_image_url.endswith((".htm", ".html")):
        return full_image_url

    # Fall back: derive from thumbnail
    basename = os.path.basename(thumbnail_url or full_image_url or "")
    name, _ = os.path.splitext(basename)
    if name:
        return f"{name}.htm"
    return ""


def build_manifest() -> dict:
    """Scan all JSON files and build the image manifest."""
    # image_filename -> manifest record
    images: dict[str, dict] = {}

    json_files = sorted(HAW_ENG_DIR.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {HAW_ENG_DIR}")
        return {"total_images": 0, "images": []}

    entries_scanned = 0
    entries_with_images = 0

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        if not isinstance(data, list):
            continue

        for entry in data:
            entries_scanned += 1
            entry_images = entry.get("images")
            if not entry_images:
                continue

            entries_with_images += 1
            headword = entry.get("headword", "")
            entry_id = entry.get("id", "")
            letter_page = entry.get("letter_page", "")

            entry_ref = {
                "headword": headword,
                "entry_id": entry_id,
                "letter_page": letter_page,
            }

            for img in entry_images:
                thumbnail_url = img.get("thumbnail_url", "")
                full_image_url = img.get("full_image_url", "")
                alt_text = img.get("alt_text", "")

                filename = derive_image_filename(thumbnail_url, full_image_url)
                detail_page = derive_detail_page(full_image_url, thumbnail_url)

                if filename in images:
                    # Add this entry as another reference
                    existing_entries = images[filename]["entries"]
                    if entry_ref not in existing_entries:
                        existing_entries.append(entry_ref)
                else:
                    images[filename] = {
                        "image_filename": filename,
                        "thumbnail_url": thumbnail_url,
                        "full_image_url": full_image_url,
                        "alt_text": alt_text,
                        "detail_page": detail_page,
                        "entries": [entry_ref],
                    }

    # Sort by filename for stable output
    sorted_images = sorted(images.values(), key=lambda x: x["image_filename"])

    manifest = {
        "total_images": len(sorted_images),
        "entries_scanned": entries_scanned,
        "entries_with_images": entries_with_images,
        "images": sorted_images,
    }
    return manifest


def main() -> None:
    print(f"Scanning {HAW_ENG_DIR} ...")
    manifest = build_manifest()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"Entries scanned: {manifest['entries_scanned']}")
    print(f"Entries with images: {manifest['entries_with_images']}")
    print(f"Unique images: {manifest['total_images']}")
    print(f"Manifest written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
