#!/usr/bin/env python3
"""Batch-parse all 48 topical pages and compare entry counts to Trussel's stated counts.

Run from project root with venv active:
    python scripts/batch_topical.py
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

# Add project src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from chd.parsers.support import parse_topical
from chd.parsers.haw_eng import parse_haw_eng_page

RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_PATH = PROJECT_ROOT / "reports" / "topical_parse_report.json"


def main() -> None:
    # Step 1: Parse topical.htm to get Trussel's stated entry counts per topic
    topical_page = parse_topical(RAW_DIR / "topical.htm")
    trussel_counts: dict[str, int] = {}
    topic_names: dict[str, str] = {}
    for topic in topical_page.topics:
        trussel_counts[topic.filename] = topic.entry_count
        topic_names[topic.filename] = topic.name

    # Step 2: Read the topical_pages.json list
    pages_json_path = PROJECT_ROOT / "data" / "processed" / "support" / "topical_pages.json"
    with open(pages_json_path) as f:
        topical_pages = json.load(f)

    # Step 3: Parse each topical page and compare counts
    results = []
    total_entries = 0
    pages_with_discrepancies = 0
    pages_with_errors = 0

    for page in topical_pages:
        filename = page["filename"]
        name = page["name"]
        filepath = RAW_DIR / filename
        trussel_count = trussel_counts.get(filename, -1)

        record: dict = {
            "filename": filename,
            "name": topic_names.get(filename, name),
            "trussel_count": trussel_count,
            "parsed_total": 0,
            "parsed_main_only": 0,
            "discrepancy": 0,
            "errors": [],
        }

        if not filepath.exists():
            record["errors"].append(f"File not found: {filepath}")
            pages_with_errors += 1
            results.append(record)
            continue

        try:
            entries, ctx = parse_haw_eng_page(filepath)
            parsed_total = len(entries)
            parsed_main = sum(
                1 for e in entries if e.trussel_display_type == "main"
            )

            record["parsed_total"] = parsed_total
            record["parsed_main_only"] = parsed_main
            record["discrepancy"] = parsed_main - trussel_count if trussel_count >= 0 else 0

            if ctx.errors:
                record["errors"] = [str(e) for e in ctx.errors]

            total_entries += parsed_total

            if record["discrepancy"] != 0:
                pages_with_discrepancies += 1
            if record["errors"]:
                pages_with_errors += 1

        except Exception:
            record["errors"].append(traceback.format_exc())
            pages_with_errors += 1

        results.append(record)

    # Step 4: Build summary and write report
    summary = {
        "total_pages": len(results),
        "total_entries": total_entries,
        "pages_with_discrepancies": pages_with_discrepancies,
        "pages_with_errors": pages_with_errors,
    }

    report = {"pages": results, "summary": summary}

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary to stdout
    print(f"Topical Parse Report")
    print(f"{'='*60}")
    print(f"Total pages:              {summary['total_pages']}")
    print(f"Total entries parsed:     {summary['total_entries']}")
    print(f"Pages with discrepancies: {summary['pages_with_discrepancies']}")
    print(f"Pages with errors:        {summary['pages_with_errors']}")
    print()

    # Show discrepancies
    discrepant = [r for r in results if r["discrepancy"] != 0]
    if discrepant:
        print(f"Discrepancies ({len(discrepant)}):")
        print(f"  {'Filename':<30} {'Trussel':>8} {'Parsed':>8} {'Diff':>6}")
        print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*6}")
        for r in discrepant:
            diff = r["discrepancy"]
            sign = "+" if diff > 0 else ""
            print(
                f"  {r['filename']:<30} {r['trussel_count']:>8} "
                f"{r['parsed_main_only']:>8} {sign}{diff:>5}"
            )
        print()

    # Show errors
    errored = [r for r in results if r["errors"]]
    if errored:
        print(f"Pages with errors ({len(errored)}):")
        for r in errored:
            print(f"  {r['filename']}: {len(r['errors'])} error(s)")
        print()

    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
