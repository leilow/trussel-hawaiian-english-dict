#!/usr/bin/env python3
"""Cross-verify headwords across multiple Hawaiian dictionary sources.

Compares headwords from:
1. Main project (Trussel haw-eng processed data)
2. Experiment Trussel2 scrape
3. ManoMano
4. Wehewiki (wehe.hilo.hawaii.edu)

Outputs a JSON report to reports/cross_verification_report.json.
"""

import json
import os
import sys
import unicodedata
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/leimomi/trussel-hawaiian-english-dict")
EXPERIMENTS = Path("/Users/leimomi/experiments/dictionary/data/raw")

# Source paths
MAIN_HAW_ENG_DIR = PROJECT_ROOT / "data" / "processed" / "haw_eng"
EXPERIMENT_TRUSSEL = EXPERIMENTS / "trussel2" / "all_entries.json"
MANOMANO_FILE = EXPERIMENTS / "manomano" / "all_entries.json"
WEHEWIKI_FILE = EXPERIMENTS / "wehewiki" / "all_entries.json"

REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORT_DIR / "cross_verification_report.json"


def normalize_headword(hw: str) -> str:
    """Normalize headword for comparison: lowercase, strip, remove subscript digits."""
    hw = hw.strip().lower()
    # Remove subscript-style homograph markers like ₁, ₂ etc.
    # Also remove trailing ASCII digit markers preceded by underscore
    import re
    hw = re.sub(r'[₀₁₂₃₄₅₆₇₈₉]+$', '', hw)
    hw = re.sub(r'_\d+$', '', hw)
    # Strip leading hyphens (some wehewiki entries start with -)
    hw = hw.lstrip('-')
    return hw.strip()


def load_main_headwords() -> tuple[set[str], dict[str, str]]:
    """Load headwords from main project haw_eng JSON files.

    Returns:
        (normalized_set, {normalized: display_form})
    """
    normalized = set()
    display_map = {}
    count = 0

    for json_file in sorted(MAIN_HAW_ENG_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            hw = entry.get("headword", "")
            if not hw:
                continue
            count += 1
            norm = normalize_headword(hw)
            if norm:
                normalized.add(norm)
                if norm not in display_map:
                    display_map[norm] = hw

    print(f"  Main project: {count} entries, {len(normalized)} unique normalized headwords")
    return normalized, display_map


def load_experiment_trussel_headwords() -> tuple[set[str], dict[str, str], int]:
    """Load headwords from the experiment trussel2 file (potentially very large).

    Returns:
        (normalized_set, {normalized: display_form}, raw_count)
    """
    file_size_mb = EXPERIMENT_TRUSSEL.stat().st_size / (1024 * 1024)
    print(f"  Experiment Trussel2 file: {file_size_mb:.0f} MB")

    normalized = set()
    display_map = {}
    count = 0

    # File is ~953MB. Try loading directly; catch MemoryError.
    try:
        with open(EXPERIMENT_TRUSSEL, "r", encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            hw = entry.get("headword", "")
            if not hw:
                continue
            count += 1
            norm = normalize_headword(hw)
            if norm:
                normalized.add(norm)
                if norm not in display_map:
                    display_map[norm] = hw
        print(f"  Experiment Trussel2: {count} entries, {len(normalized)} unique normalized headwords")
    except (MemoryError, Exception) as e:
        print(f"  WARNING: Could not load experiment Trussel2 ({type(e).__name__}: {e})")
        print("  Attempting streaming parse with json.JSONDecoder...")
        # Fallback: stream through line by line extracting "headword" values
        try:
            import re
            hw_pattern = re.compile(r'"headword"\s*:\s*"([^"]*)"')
            with open(EXPERIMENT_TRUSSEL, "r", encoding="utf-8") as f:
                for line in f:
                    for match in hw_pattern.finditer(line):
                        hw = match.group(1)
                        count += 1
                        norm = normalize_headword(hw)
                        if norm:
                            normalized.add(norm)
                            if norm not in display_map:
                                display_map[norm] = hw
            print(f"  Experiment Trussel2 (streamed): {count} entries, {len(normalized)} unique normalized headwords")
        except Exception as e2:
            print(f"  FAILED to load experiment Trussel2: {e2}")
            return set(), {}, 0

    return normalized, display_map, count


def load_manomano_headwords() -> tuple[set[str], dict[str, str], int, list[dict]]:
    """Load headwords from ManoMano.

    ManoMano uses "word" as the headword key.

    Returns:
        (normalized_set, {normalized: display_form}, raw_count, raw_entries)
    """
    with open(MANOMANO_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    normalized = set()
    display_map = {}
    count = 0

    for entry in entries:
        hw = entry.get("word", "")
        if not hw:
            continue
        count += 1
        norm = normalize_headword(hw)
        if norm:
            normalized.add(norm)
            if norm not in display_map:
                display_map[norm] = hw

    print(f"  ManoMano: {count} entries, {len(normalized)} unique normalized headwords")
    return normalized, display_map, count, entries


def load_wehewiki_headwords() -> tuple[set[str], dict[str, str], int, list[dict]]:
    """Load headwords from Wehewiki.

    Wehewiki uses "headword" as the key. Also tracks source_dict for Parker/Clark detection.

    Returns:
        (normalized_set, {normalized: display_form}, raw_count, raw_entries)
    """
    with open(WEHEWIKI_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    normalized = set()
    display_map = {}
    count = 0

    for entry in entries:
        hw = entry.get("headword", "")
        if not hw:
            continue
        count += 1
        norm = normalize_headword(hw)
        if norm:
            normalized.add(norm)
            if norm not in display_map:
                display_map[norm] = hw

    print(f"  Wehewiki: {count} entries, {len(normalized)} unique normalized headwords")
    return normalized, display_map, count, entries


def find_parker_clark_entries(wehewiki_entries: list[dict]) -> dict:
    """Find Wehewiki entries attributed to Parker or Clark dictionaries.

    Parker = source_dict 'P1' or source_dict_raw containing 'Parker'
    Clark = source_dict_raw containing 'Clark'
    """
    parker_entries = []
    clark_entries = []

    for entry in wehewiki_entries:
        src = entry.get("source_dict", "")
        src_raw = entry.get("source_dict_raw", "").lower()
        hw = entry.get("headword", "")

        if src == "P1" or "parker" in src_raw:
            parker_entries.append(hw)
        if "clark" in src_raw:
            clark_entries.append(hw)

    return {
        "parker_count": len(parker_entries),
        "parker_sample": sorted(set(parker_entries))[:50],
        "clark_count": len(clark_entries),
        "clark_sample": sorted(set(clark_entries))[:50],
    }


def main():
    print("=" * 60)
    print("Hawaiian Dictionary Cross-Verification")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    # Load all sources
    print("\nLoading sources...")
    main_set, main_display = load_main_headwords()

    exp_set, exp_display, exp_count = load_experiment_trussel_headwords()

    mm_set, mm_display, mm_count, mm_entries = load_manomano_headwords()

    ww_set, ww_display, ww_count, ww_entries = load_wehewiki_headwords()

    # Compute overlaps
    print("\nComputing overlaps...")
    main_mm = main_set & mm_set
    main_ww = main_set & ww_set
    mm_ww = mm_set & ww_set
    all_three = main_set & mm_set & ww_set

    # Include experiment trussel overlaps if available
    main_exp = main_set & exp_set if exp_set else set()

    print(f"  Main ∩ ManoMano: {len(main_mm)}")
    print(f"  Main ∩ Wehewiki: {len(main_ww)}")
    print(f"  ManoMano ∩ Wehewiki: {len(mm_ww)}")
    print(f"  All three: {len(all_three)}")
    if exp_set:
        print(f"  Main ∩ Experiment Trussel: {len(main_exp)}")

    # Unique to each source (not in main)
    unique_mm = mm_set - main_set
    unique_ww = ww_set - main_set

    print(f"\n  Unique to ManoMano (not in main): {len(unique_mm)}")
    print(f"  Unique to Wehewiki (not in main): {len(unique_ww)}")

    # Parker/Clark analysis
    print("\nAnalyzing Parker/Clark entries in Wehewiki...")
    pc = find_parker_clark_entries(ww_entries)
    print(f"  Parker entries: {pc['parker_count']}")
    print(f"  Clark entries: {pc['clark_count']}")

    # Parker entries unique to Wehewiki (not in main project)
    parker_headwords_norm = set()
    for entry in ww_entries:
        src = entry.get("source_dict", "")
        src_raw = entry.get("source_dict_raw", "").lower()
        if src == "P1" or "parker" in src_raw:
            norm = normalize_headword(entry.get("headword", ""))
            if norm:
                parker_headwords_norm.add(norm)
    parker_unique = parker_headwords_norm - main_set
    print(f"  Parker entries NOT in main project: {len(parker_unique)}")

    # Build summary
    summary_lines = [
        f"Cross-verification of {len(main_set)} main project headwords against {len(mm_set)} ManoMano "
        f"and {len(ww_set)} Wehewiki unique headwords.",
        f"",
        f"Overlap: {len(main_mm)} headwords shared between main and ManoMano "
        f"({len(main_mm)/len(main_set)*100:.1f}% of main).",
        f"Overlap: {len(main_ww)} headwords shared between main and Wehewiki "
        f"({len(main_ww)/len(main_set)*100:.1f}% of main).",
        f"All three sources share {len(all_three)} headwords.",
        f"",
        f"ManoMano has {len(unique_mm)} headwords not in main project (potential additions).",
        f"Wehewiki has {len(unique_ww)} headwords not in main project (potential additions).",
        f"",
        f"Wehewiki contains {pc['parker_count']} Parker (1922) entries, of which "
        f"{len(parker_unique)} headwords are not in the main project.",
        f"Wehewiki contains {pc['clark_count']} Clark entries.",
    ]
    if exp_set:
        summary_lines.append(
            f"Experiment Trussel2 has {len(exp_set)} unique headwords, "
            f"{len(main_exp)} overlap with main project."
        )

    summary = "\n".join(summary_lines)
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    print(summary)

    # Build report
    report = {
        "generated_at": datetime.now().isoformat(),
        "source_counts": {
            "main_project": {
                "total_entries": len(main_display),  # approximate from display_map
                "unique_normalized_headwords": len(main_set),
            },
            "experiment_trussel": {
                "total_entries": exp_count,
                "unique_normalized_headwords": len(exp_set),
                "note": "953MB file" if exp_set else "Could not load (too large)",
            },
            "manomano": {
                "total_entries": mm_count,
                "unique_normalized_headwords": len(mm_set),
            },
            "wehewiki": {
                "total_entries": ww_count,
                "unique_normalized_headwords": len(ww_set),
            },
        },
        "overlaps": {
            "main_manomano": len(main_mm),
            "main_wehewiki": len(main_ww),
            "manomano_wehewiki": len(mm_ww),
            "all_three": len(all_three),
            "main_experiment_trussel": len(main_exp) if exp_set else None,
        },
        "unique_to_manomano": {
            "count": len(unique_mm),
            "sample": sorted(unique_mm)[:50],
            "sample_display": [mm_display.get(hw, hw) for hw in sorted(unique_mm)[:50]],
        },
        "unique_to_wehewiki": {
            "count": len(unique_ww),
            "sample": sorted(unique_ww)[:50],
            "sample_display": [ww_display.get(hw, hw) for hw in sorted(unique_ww)[:50]],
        },
        "parker_clark_entries": {
            "parker_total": pc["parker_count"],
            "parker_unique_headwords_not_in_main": len(parker_unique),
            "parker_sample": pc["parker_sample"],
            "clark_total": pc["clark_count"],
            "clark_sample": pc["clark_sample"],
        },
        "summary": summary,
    }

    # Write report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nReport written to: {REPORT_FILE}")
    print("Done.")


if __name__ == "__main__":
    main()
