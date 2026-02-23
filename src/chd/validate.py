"""Post-parse validation: link resolution, entry integrity checks."""

from __future__ import annotations

from collections import defaultdict

from chd.models import Entry
from chd.unicode import to_ascii


def validate_link_resolution(entries: list[Entry]) -> dict:
    """Check how many cross-refs and linked words resolve to actual entries.

    Returns a report dict with resolution rates and unresolved links.
    """
    # Build anchor index
    anchor_set = set()
    headword_set = set()
    for e in entries:
        if e.id:
            anchor_set.add(e.id)
        headword_set.add(e.headword)
        headword_set.add(to_ascii(e.headword))
        headword_set.add(e.headword_display)

    # Check cross-refs
    xref_total = 0
    xref_resolved = 0
    xref_unresolved = []
    for e in entries:
        for xref in e.cross_refs:
            xref_total += 1
            target = xref.target_anchor or xref.target_headword
            if target in anchor_set or target in headword_set or to_ascii(target) in headword_set:
                xref_resolved += 1
            else:
                xref_unresolved.append({
                    "from_entry": e.id,
                    "from_headword": e.headword_display,
                    "ref_type": xref.ref_type,
                    "target": xref.target_headword,
                    "target_anchor": xref.target_anchor,
                })

    # Check linked words in senses
    link_total = 0
    link_resolved = 0
    for e in entries:
        for sense in e.senses:
            for lw in sense.linked_words:
                link_total += 1
                target = lw.target_anchor or lw.surface
                if target in anchor_set or target in headword_set or to_ascii(target) in headword_set:
                    link_resolved += 1

    xref_rate = (xref_resolved / xref_total * 100) if xref_total else 0
    link_rate = (link_resolved / link_total * 100) if link_total else 0

    return {
        "cross_refs": {
            "total": xref_total,
            "resolved": xref_resolved,
            "resolution_rate": round(xref_rate, 1),
            "unresolved_sample": xref_unresolved[:50],
        },
        "linked_words": {
            "total": link_total,
            "resolved": link_resolved,
            "resolution_rate": round(link_rate, 1),
        },
    }


def validate_entries(entries: list[Entry]) -> dict:
    """Run integrity checks on parsed entries."""
    issues = []

    for e in entries:
        if not e.id:
            issues.append({"entry": e.headword_display, "issue": "missing anchor ID"})
        if not e.headword:
            issues.append({"entry": e.id, "issue": "missing headword"})
        if not e.senses and e.trussel_display_type == "main":
            issues.append({"entry": f"{e.id} ({e.headword_display})", "issue": "main entry with no senses"})

    # Duplicate anchor check
    seen_ids = defaultdict(int)
    for e in entries:
        if e.id:
            seen_ids[e.id] += 1
    duplicates = {k: v for k, v in seen_ids.items() if v > 1}

    return {
        "total_entries": len(entries),
        "issues": issues[:100],
        "duplicate_ids": len(duplicates),
        "duplicate_id_sample": dict(list(duplicates.items())[:20]),
    }
