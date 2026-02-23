"""Integration test: full pipeline parse → validate → export → verify."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chd.models import Entry, EngHawEntry, ConcordanceInstance
from chd.export import export_all, PROCESSED_DIR
from chd.parsers.haw_eng import parse_all_haw_eng, RAW_DIR


# Skip if raw data not available
pytestmark = pytest.mark.skipif(
    not (RAW_DIR / "haw-a.htm").exists(),
    reason="Raw HTML data not available",
)


@pytest.fixture(scope="module")
def export_result(tmp_path_factory):
    """Run the full export pipeline once for the module."""
    out_dir = tmp_path_factory.mktemp("processed")
    result = export_all(raw_dir=RAW_DIR, out_dir=out_dir)
    return result, out_dir


class TestFullPipeline:
    """End-to-end pipeline tests."""

    def test_export_returns_summary(self, export_result):
        summary, _ = export_result
        assert isinstance(summary, dict)
        assert "total_haw_eng" in summary
        assert "total_eng_haw" in summary
        assert "total_concordance" in summary

    def test_haw_eng_count_sanity(self, export_result):
        """Total deduplicated entries ~59K+ (core + topical-only merged)."""
        summary, _ = export_result
        total = summary["total_haw_eng"]
        assert total > 59_000, f"Too few entries: {total}"
        assert total < 65_000, f"Too many entries: {total}"

    def test_eng_haw_exists(self, export_result):
        summary, _ = export_result
        assert summary["total_eng_haw"] > 10_000

    def test_concordance_exists(self, export_result):
        summary, _ = export_result
        assert summary["total_concordance"] > 5_000

    def test_examples_extracted(self, export_result):
        summary, _ = export_result
        assert summary["total_examples"] > 10_000

    def test_cross_refs_extracted(self, export_result):
        summary, _ = export_result
        assert summary["total_cross_refs"] > 5_000

    def test_etymologies_extracted(self, export_result):
        summary, _ = export_result
        assert summary["total_etymologies"] > 1_000

    def test_images_extracted(self, export_result):
        summary, _ = export_result
        assert summary["total_images"] > 100


class TestJsonOutput:
    """Verify JSON files are written correctly."""

    def test_haw_eng_json_files(self, export_result):
        _, out_dir = export_result
        haw_eng_dir = out_dir / "haw_eng"
        json_files = list(haw_eng_dir.glob("*.json"))
        assert len(json_files) >= 20, f"Only {len(json_files)} haw-eng JSON files"

    def test_eng_haw_json_files(self, export_result):
        _, out_dir = export_result
        eng_haw_dir = out_dir / "eng_haw"
        json_files = list(eng_haw_dir.glob("*.json"))
        assert len(json_files) >= 20

    def test_concordance_json_files(self, export_result):
        _, out_dir = export_result
        conc_dir = out_dir / "concordance"
        json_files = list(conc_dir.glob("*.json"))
        assert len(json_files) >= 5

    def test_summary_json(self, export_result):
        _, out_dir = export_result
        summary_path = out_dir / "summary.json"
        assert summary_path.exists()
        data = json.loads(summary_path.read_text())
        assert data["total_haw_eng"] > 59_000

    def test_validation_report_json(self, export_result):
        _, out_dir = export_result
        report_path = out_dir / "validation_report.json"
        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert "link_resolution" in data
        assert "entry_validation" in data

    def test_haw_eng_a_json_roundtrip(self, export_result):
        """Verify entries can round-trip through JSON."""
        _, out_dir = export_result
        a_path = out_dir / "haw_eng" / "a.json"
        assert a_path.exists()
        data = json.loads(a_path.read_text())
        assert len(data) > 4_000
        # Validate first 100 entries round-trip
        for entry_data in data[:100]:
            entry = Entry.model_validate(entry_data)
            roundtrip = entry.model_dump(exclude_defaults=True)
            Entry.model_validate(roundtrip)


class TestValidation:
    """Verify validation results meet quality thresholds."""

    def test_cross_ref_resolution_rate(self, export_result):
        """Cross-ref resolution should be >80%."""
        _, out_dir = export_result
        report = json.loads((out_dir / "validation_report.json").read_text())
        rate = report["link_resolution"]["cross_refs"]["resolution_rate"]
        assert rate > 90, f"Cross-ref resolution only {rate}%"

    def test_linked_word_resolution_rate(self, export_result):
        _, out_dir = export_result
        report = json.loads((out_dir / "validation_report.json").read_text())
        rate = report["link_resolution"]["linked_words"]["resolution_rate"]
        assert rate > 70, f"Linked word resolution only {rate}%"

    def test_few_duplicate_ids(self, export_result):
        _, out_dir = export_result
        report = json.loads((out_dir / "validation_report.json").read_text())
        dupes = report["entry_validation"]["duplicate_ids"]
        total = report["entry_validation"]["total_entries"]
        dupe_rate = dupes / total * 100 if total else 0
        assert dupe_rate < 1, f"Duplicate ID rate {dupe_rate:.1f}% too high"

    def test_few_issues(self, export_result):
        _, out_dir = export_result
        report = json.loads((out_dir / "validation_report.json").read_text())
        issues = len(report["entry_validation"]["issues"])
        total = report["entry_validation"]["total_entries"]
        issue_rate = issues / total * 100 if total else 0
        assert issue_rate < 5, f"Issue rate {issue_rate:.1f}% too high"
