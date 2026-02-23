"""Export parsed dictionary data to structured JSON."""

from __future__ import annotations

import json
from pathlib import Path

from chd.models import Entry, EngHawEntry, ConcordanceInstance
from chd.parsers.haw_eng import parse_all_haw_eng, RAW_DIR
from chd.parsers.eng_haw import parse_all_eng_haw
from chd.parsers.concordance import parse_all_concordance
from chd.parsers.support import parse_counts, parse_refs, discover_topical_pages
from chd.pos_mapper import map_pos
from chd.validate import validate_link_resolution, validate_entries

PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"


def _write_json(data, filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def _apply_pos_mapping(entries: list[Entry]) -> None:
    """Apply three-layer POS mapping to all senses in place."""
    for entry in entries:
        for sense in entry.senses:
            if sense.pos_raw and not sense.pos_hawaiian:
                haw, eng = map_pos(sense.pos_raw)
                sense.pos_hawaiian = haw
                sense.pos_english = eng


def export_haw_eng(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> list[Entry]:
    """Parse and export all Hawaiian-English entries (deduped, with topical-only merged)."""
    print("Parsing Hawaiian-English pages...")
    results = parse_all_haw_eng(raw_dir)

    haw_eng_dir = out_dir / "haw_eng"
    all_entries: list[Entry] = []

    # Phase 1: Core letter pages
    core_ids: set[str] = set()
    for letter, (entries, ctx) in sorted(results.items()):
        if len(letter) > 1 and letter not in ("aa",):
            continue
        _apply_pos_mapping(entries)
        for e in entries:
            if e.id:
                core_ids.add(e.id)
        data = [e.model_dump(exclude_defaults=True) for e in entries]
        _write_json(data, haw_eng_dir / f"{letter}.json")
        all_entries.extend(entries)
        errors = len(ctx.errors)
        print(f"  {letter}: {len(entries)} entries" + (f" ({errors} errors)" if errors else ""))

    # Phase 2: Merge topical-only entries (not in core pages)
    topical_only: list[Entry] = []
    topical_pages: list[str] = []
    for letter, (entries, ctx) in sorted(results.items()):
        if len(letter) <= 1 or letter == "aa":
            continue
        topical_pages.append(letter)
        for e in entries:
            if e.id and e.id not in core_ids:
                # Tag with topic and add to core
                if letter not in e.topics:
                    e.topics.append(letter)
                _apply_pos_mapping([e])
                topical_only.append(e)
                core_ids.add(e.id)

    if topical_only:
        data = [e.model_dump(exclude_defaults=True) for e in topical_only]
        _write_json(data, haw_eng_dir / "topical_only.json")
        all_entries.extend(topical_only)
        print(f"  topical-only: {len(topical_only)} unique entries from {len(topical_pages)} pages")

    print(f"  Total: {len(all_entries)} entries")
    return all_entries


def export_eng_haw(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> list[EngHawEntry]:
    print("\nParsing English-Hawaiian pages...")
    results = parse_all_eng_haw(raw_dir)
    eng_haw_dir = out_dir / "eng_haw"
    all_entries = []
    for letter, entries in sorted(results.items()):
        data = [e.model_dump(exclude_defaults=True) for e in entries]
        _write_json(data, eng_haw_dir / f"{letter}.json")
        all_entries.extend(entries)
    total_trans = sum(len(e.translations) for e in all_entries)
    print(f"  Total: {len(all_entries)} entries, {total_trans} translations")
    return all_entries


def export_concordance(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> list[ConcordanceInstance]:
    print("\nParsing Concordance pages...")
    results = parse_all_concordance(raw_dir)
    conc_dir = out_dir / "concordance"
    all_instances = []
    for letter, instances in sorted(results.items()):
        data = [i.model_dump(exclude_defaults=True) for i in instances]
        _write_json(data, conc_dir / f"{letter}.json")
        all_instances.extend(instances)
    print(f"  Total: {len(all_instances)} instances")
    return all_instances


def export_support(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR):
    print("\nParsing support pages...")
    support_dir = out_dir / "support"
    counts_path = raw_dir / "counts.htm"
    if counts_path.exists():
        counts = parse_counts(counts_path)
        _write_json(counts.model_dump(), support_dir / "counts.json")
    refs_path = raw_dir / "refs.htm"
    if refs_path.exists():
        refs = parse_refs(refs_path)
        _write_json([r.model_dump(exclude_defaults=True) for r in refs], support_dir / "refs.json")
        print(f"  Refs: {len(refs)}")
    topics = discover_topical_pages(raw_dir / "topical.htm")
    _write_json(topics, support_dir / "topical_pages.json")
    print(f"  Topical: {len(topics)} pages")


def export_all(raw_dir: Path = RAW_DIR, out_dir: Path = PROCESSED_DIR) -> dict:
    """Run the full export pipeline with validation."""
    print("=" * 60)
    print("CHD Scraper v2 — Full Export")
    print("=" * 60)

    entries = export_haw_eng(raw_dir, out_dir)
    eng_entries = export_eng_haw(raw_dir, out_dir)
    conc_instances = export_concordance(raw_dir, out_dir)
    export_support(raw_dir, out_dir)

    # Validation
    print("\nRunning validation...")
    link_report = validate_link_resolution(entries)
    entry_report = validate_entries(entries)

    report = {
        "haw_eng_entries": len(entries),
        "eng_haw_entries": len(eng_entries),
        "concordance_instances": len(conc_instances),
        "link_resolution": link_report,
        "entry_validation": entry_report,
    }
    _write_json(report, out_dir / "validation_report.json")

    print(f"\n  Cross-ref resolution: {link_report['cross_refs']['resolution_rate']}%")
    print(f"  Linked word resolution: {link_report['linked_words']['resolution_rate']}%")
    print(f"  Entry issues: {len(entry_report['issues'])}")
    print(f"  Duplicate IDs: {entry_report['duplicate_ids']}")

    # Summary
    summary = {
        "total_haw_eng": len(entries),
        "total_eng_haw": len(eng_entries),
        "total_concordance": len(conc_instances),
        "total_examples": sum(len(e.examples) for e in entries),
        "total_cross_refs": sum(len(e.cross_refs) for e in entries),
        "total_etymologies": sum(1 for e in entries if e.etymology),
        "total_images": sum(len(e.images) for e in entries),
    }
    _write_json(summary, out_dir / "summary.json")

    print(f"\n{'=' * 60}")
    print(f"Export complete! → {out_dir}")
    print(f"{'=' * 60}")
    return summary
