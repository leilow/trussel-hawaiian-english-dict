#!/usr/bin/env python3
"""Extract navigation scaffolding from Trussel's haw-*.htm files.

Parses three layers of navigation from the raw HTML:
  Layer 1: Main letter links with entry counts (a:3318, e:630, ...)
  Layer 2: Loanword letter links (b, c, d, f, g, j, r, s, t, v, z)
  Layer 3: Two-letter combo anchors within each page (aa, ab, ac, ...)

Compares Layer 1 counts against:
  - Parsed entry counts from data/processed/haw_eng/{letter}.json
  - Counts from data/processed/support/counts.json

Outputs: reports/scaffolding_report.json
"""

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

PROJECT_ROOT = Path("/Users/leimomi/trussel-hawaiian-english-dict")
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_HAW_ENG = PROJECT_ROOT / "data" / "processed" / "haw_eng"
COUNTS_JSON = PROJECT_ROOT / "data" / "processed" / "support" / "counts.json"
REPORT_PATH = PROJECT_ROOT / "reports" / "scaffolding_report.json"

HAWAIIAN_LETTERS = list("aehiklmnopuw")
LOAN_LETTERS = list("bcdfgjrstvz")
ALL_LETTERS = HAWAIIAN_LETTERS + LOAN_LETTERS


def parse_nav_from_file(filepath: Path) -> dict:
    """Parse Layer 1, 2, and 3 from a single haw-*.htm file."""
    html = filepath.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    result = {
        "layer1": {},       # letter -> count (from nav table)
        "layer2": [],       # loanword letters found
        "layer3_combos": [],  # two-letter anchor combos
    }

    # --- Layer 1: Main letter links with counts ---
    # Structure: <td ...><a href="haw-X.htm">&nbsp;<font size="+2">X</font>
    #            <br><font size="-2">COUNT</font></a></td>
    # These are in a table with bgcolor="floralwhite" cells
    for td in soup.find_all("td", attrs={"bgcolor": "floralwhite"}):
        link = td.find("a", href=re.compile(r"^haw-[a-z]\.htm$"))
        if not link:
            continue
        # Extract letter from the large font
        big_font = link.find("font", attrs={"size": "+2"})
        small_font = link.find("font", attrs={"size": "-2"})
        if big_font and small_font:
            letter = big_font.get_text(strip=True)
            try:
                count = int(small_font.get_text(strip=True))
                result["layer1"][letter] = count
            except ValueError:
                pass

    # --- Layer 2: Loanword letter links ---
    # Structure: <a class="MKindexlink" href="haw-b.htm">&nbsp;b&nbsp;&nbsp;</a>
    for link in soup.find_all("a", class_="MKindexlink"):
        href = link.get("href", "")
        m = re.match(r"haw-([a-z])\.htm$", href)
        if m:
            letter = m.group(1)
            if letter not in result["layer2"]:
                result["layer2"].append(letter)

    # --- Layer 3: Two-letter combo anchors (jump links within the page) ---
    # Structure: <p class="indexline"><a href="#aa">aa</a> ...
    # These are internal fragment links with 2-letter text
    indexline = soup.find("p", class_="indexline")
    if indexline:
        for link in indexline.find_all("a", href=re.compile(r"^#")):
            text = link.get_text(strip=True)
            if len(text) >= 2 and text.isalpha():
                result["layer3_combos"].append(text)

    return result


def load_parsed_entry_count(letter: str) -> int | None:
    """Count entries in data/processed/haw_eng/{letter}.json."""
    path = PROCESSED_HAW_ENG / f"{letter}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return len(data)
    elif isinstance(data, dict):
        # Could be a dict with entries key or just a mapping
        if "entries" in data:
            return len(data["entries"])
        return len(data)
    return None


def load_counts_json() -> dict[str, int]:
    """Load entries_by_letter from counts.json."""
    if not COUNTS_JSON.exists():
        return {}
    data = json.loads(COUNTS_JSON.read_text(encoding="utf-8"))
    return data.get("entries_by_letter", {})


def main():
    print("Extracting scaffolding from raw HTML files...")

    # Load comparison data
    counts_by_letter = load_counts_json()
    print(f"  counts.json has {len(counts_by_letter)} letters")

    # Parse each file
    per_letter = {}
    all_layer2 = set()
    layer3_by_letter = {}

    # We only need to parse Layer 1 once (it's the same nav on every page),
    # but we parse each file for its own Layer 3 combos.
    layer1_counts = {}  # Trussel nav counts (same across all pages)

    for letter in ALL_LETTERS:
        filepath = RAW_DIR / f"haw-{letter}.htm"
        if not filepath.exists():
            print(f"  WARNING: {filepath.name} not found, skipping")
            continue

        nav = parse_nav_from_file(filepath)

        # Layer 1: grab from first file that has it (they're all the same)
        if not layer1_counts and nav["layer1"]:
            layer1_counts = nav["layer1"]

        # Layer 2: accumulate
        all_layer2.update(nav["layer2"])

        # Layer 3: per-letter combos
        if nav["layer3_combos"]:
            layer3_by_letter[letter] = nav["layer3_combos"]

    # Build per-letter report
    total_discrepancies = 0
    for letter in ALL_LETTERS:
        trussel_count = layer1_counts.get(letter)
        parsed_count = load_parsed_entry_count(letter)
        counts_page_count = counts_by_letter.get(letter)

        discrepancies = []
        if trussel_count is not None and parsed_count is not None:
            if trussel_count != parsed_count:
                discrepancies.append(
                    f"trussel_nav({trussel_count}) != parsed({parsed_count}), "
                    f"diff={trussel_count - parsed_count}"
                )
        if trussel_count is not None and counts_page_count is not None:
            if trussel_count != counts_page_count:
                discrepancies.append(
                    f"trussel_nav({trussel_count}) != counts_json({counts_page_count}), "
                    f"diff={trussel_count - counts_page_count}"
                )
        if parsed_count is not None and counts_page_count is not None:
            if parsed_count != counts_page_count:
                discrepancies.append(
                    f"parsed({parsed_count}) != counts_json({counts_page_count}), "
                    f"diff={parsed_count - counts_page_count}"
                )

        total_discrepancies += len(discrepancies)

        entry = {
            "trussel_nav_count": trussel_count,
            "parsed_count": parsed_count,
            "counts_page_count": counts_page_count,
        }
        if discrepancies:
            entry["discrepancies"] = discrepancies
        per_letter[letter] = entry

    # Build report
    report = {
        "per_letter": per_letter,
        "layer2_letters": sorted(all_layer2),
        "layer3_combos": layer3_by_letter,
        "summary": {
            "total_letters_checked": len(per_letter),
            "hawaiian_letters": len([l for l in HAWAIIAN_LETTERS if l in per_letter]),
            "loan_letters": len([l for l in LOAN_LETTERS if l in per_letter]),
            "total_discrepancies": total_discrepancies,
            "letters_with_discrepancies": [
                l for l in ALL_LETTERS
                if per_letter.get(l, {}).get("discrepancies")
            ],
            "trussel_nav_total": sum(
                v for v in layer1_counts.values() if v is not None
            ),
        },
    }

    # Write report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nReport written to {REPORT_PATH}")

    # Print summary
    print(f"\n--- Summary ---")
    print(f"Trussel nav total: {report['summary']['trussel_nav_total']}")
    print(f"Layer 2 (loanword) letters: {report['layer2_letters']}")
    print(f"Layer 3 combos found for {len(layer3_by_letter)} letters")
    print(f"Total discrepancies: {total_discrepancies}")
    if report["summary"]["letters_with_discrepancies"]:
        print(f"Letters with discrepancies: {report['summary']['letters_with_discrepancies']}")

    # Print per-letter comparison table
    print(f"\n{'Letter':>6}  {'Trussel':>8}  {'Parsed':>8}  {'counts.json':>12}  Notes")
    print("-" * 60)
    for letter in ALL_LETTERS:
        entry = per_letter.get(letter, {})
        tn = entry.get("trussel_nav_count")
        pc = entry.get("parsed_count")
        cc = entry.get("counts_page_count")
        tn_s = str(tn) if tn is not None else "-"
        pc_s = str(pc) if pc is not None else "-"
        cc_s = str(cc) if cc is not None else "-"
        flag = " *" if entry.get("discrepancies") else ""
        print(f"{letter:>6}  {tn_s:>8}  {pc_s:>8}  {cc_s:>12}{flag}")

    return 0 if total_discrepancies == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
