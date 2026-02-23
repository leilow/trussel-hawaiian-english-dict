"""Seed Supabase database from exported JSON files via REST API.

Usage:
    python -m chd.seed [--dir data/processed]

Uses SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars, or falls back to
hardcoded project values.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

PROCESSED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

# Project defaults
DEFAULT_URL = "https://oldmeegmnudyosbztast.supabase.co"
BATCH = 500  # rows per REST API call


def get_config() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", DEFAULT_URL)
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        print("ERROR: Set SUPABASE_SERVICE_ROLE_KEY environment variable")
        print("  Get it from: supabase projects api-keys")
        sys.exit(1)
    return url, key


def load_json(filepath: Path):
    return json.loads(filepath.read_text(encoding="utf-8"))


class SupabaseSeeder:
    def __init__(self, url: str, key: str):
        self.base = url + "/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        self.headers_returning = {
            **self.headers,
            "Prefer": "return=representation",
        }

    def _post(self, table: str, rows: list[dict], upsert: bool = False) -> int:
        """Insert rows in batches. Returns total inserted."""
        if not rows:
            return 0
        headers = {**self.headers}
        if upsert:
            headers["Prefer"] = "return=minimal,resolution=merge-duplicates"
        total = 0
        for i in range(0, len(rows), BATCH):
            batch = rows[i:i + BATCH]
            resp = requests.post(f"{self.base}/{table}", headers=headers, json=batch)
            if resp.status_code not in (200, 201):
                print(f"  ERROR inserting into {table} (batch {i//BATCH}): {resp.status_code}")
                print(f"  {resp.text[:300]}")
                sys.exit(1)
            total += len(batch)
        return total

    def _post_returning(self, table: str, rows: list[dict]) -> list[dict]:
        """Insert rows and return the created records (with server-generated IDs)."""
        if not rows:
            return []
        results = []
        for i in range(0, len(rows), BATCH):
            batch = rows[i:i + BATCH]
            resp = requests.post(f"{self.base}/{table}", headers=self.headers_returning, json=batch)
            if resp.status_code not in (200, 201):
                print(f"  ERROR inserting into {table} (batch {i//BATCH}): {resp.status_code}")
                print(f"  {resp.text[:300]}")
                sys.exit(1)
            results.extend(resp.json())
        return results

    def _delete_all(self, table: str):
        """Delete all rows from a table."""
        # Use a filter that matches everything
        resp = requests.delete(
            f"{self.base}/{table}?id=gt.0",
            headers=self.headers,
        )
        if resp.status_code not in (200, 204):
            # Try text PK tables
            resp = requests.delete(
                f"{self.base}/{table}?id=neq.",
                headers=self.headers,
            )

    def truncate_all(self):
        """Clear all tables via RPC or sequential deletes."""
        # Order matters: child tables first
        tables = [
            "word_token", "linked_word", "sub_definition_domain", "sub_definition",
            "sense", "example", "etymology", "cross_ref", "grammar_ref",
            "hawaiian_gloss", "image", "alt_spelling", "entry_topic", "topic",
            "eng_haw_translation", "eng_haw_entry", "concordance", "reference", "entry",
        ]
        for t in tables:
            # Delete all with a broad filter
            for col in ["id", "entry_id", "sense_id", "topic_id", "eng_haw_entry_id",
                         "concordance_id", "sub_definition_id", "example_id"]:
                resp = requests.delete(
                    f"{self.base}/{t}?select=*",
                    headers={**self.headers, "Prefer": "return=minimal"},
                )
                if resp.status_code in (200, 204):
                    break
                # Try with different filter
                resp = requests.delete(
                    f"{self.base}/{t}",
                    headers={**self.headers, "Prefer": "return=minimal"},
                    params={"id": "not.is.null"} if t != "entry_topic" else {"entry_id": "not.is.null"},
                )
                if resp.status_code in (200, 204):
                    break

    def seed_entries(self, data_dir: Path) -> int:
        haw_dir = data_dir / "haw_eng"
        seen_ids = set()
        count = 0
        for jf in sorted(haw_dir.glob("*.json")):
            entries = load_json(jf)
            rows = []
            for e in entries:
                eid = e.get("id", "")
                if not eid or eid in seen_ids:
                    continue
                seen_ids.add(eid)
                rows.append({
                    "id": eid,
                    "headword": e.get("headword", ""),
                    "headword_display": e.get("headword_display", ""),
                    "headword_ascii": e.get("headword_ascii", ""),
                    "subscript": e.get("subscript", ""),
                    "letter_page": e.get("letter_page", ""),
                    "display_type": e.get("trussel_display_type", "main"),
                    "pdf_page": e.get("pdf_page", ""),
                    "in_pe": e.get("in_pe", False),
                    "in_mk": e.get("in_mk", False),
                    "in_mk_addendum": e.get("in_mk_addendum", False),
                    "in_andrews": e.get("in_andrews", False),
                    "in_placenames": e.get("in_placenames", False),
                    "is_from_eh_only": e.get("is_from_eh_only", False),
                    "syllable_breakdown": e.get("syllable_breakdown", ""),
                    "is_basic_vocab": e.get("is_basic_vocab", False),
                    "dialect": e.get("dialect", ""),
                    "usage_register": e.get("usage_register", ""),
                    "is_loanword": e.get("is_loanword", False),
                    "loan_source": e.get("loan_source", ""),
                    "loan_language": e.get("loan_language", ""),
                    "source_tag": e.get("source_tag", ""),
                })
            count += self._post("entry", rows, upsert=True)
        return count

    def seed_senses(self, data_dir: Path) -> int:
        haw_dir = data_dir / "haw_eng"
        sense_count = 0
        for jf in sorted(haw_dir.glob("*.json")):
            letter = jf.stem
            entries = load_json(jf)
            # Collect all senses for this file
            sense_rows = []
            for e in entries:
                eid = e.get("id", "")
                if not eid:
                    continue
                for sense in e.get("senses", []):
                    sense_rows.append({
                        "_entry": e,
                        "_sense": sense,
                        "entry_id": eid,
                        "sense_num": sense.get("sense_num", 0),
                        "source_dict": sense.get("source_dict", "PE"),
                        "pos_raw": sense.get("pos_raw", ""),
                        "pos_hawaiian": sense.get("pos_hawaiian", ""),
                        "pos_english": sense.get("pos_english", ""),
                        "definition_text": sense.get("text", ""),
                        "definition_html": sense.get("html", ""),
                        "hawaiian_gloss": sense.get("hawaiian_gloss", ""),
                        "gloss_source_num": sense.get("gloss_source_num", ""),
                    })

            # Insert senses in batches and get IDs back
            for i in range(0, len(sense_rows), BATCH):
                batch = sense_rows[i:i + BATCH]
                clean_batch = [{k: v for k, v in r.items() if not k.startswith("_")} for r in batch]
                created = self._post_returning("sense", clean_batch)
                sense_count += len(created)

                # Now insert linked_words and sub_definitions for each sense
                lw_rows = []
                sd_to_insert = []
                for j, sense_rec in enumerate(batch):
                    sense_id = created[j]["id"]
                    sense_data = sense_rec["_sense"]

                    for lw in sense_data.get("linked_words", []):
                        lw_rows.append({
                            "sense_id": sense_id,
                            "surface": lw.get("surface", ""),
                            "target_anchor": lw.get("target_anchor", ""),
                            "target_page": lw.get("target_page", ""),
                            "link_class": lw.get("link_class", ""),
                        })

                    for sd in sense_data.get("sub_definitions", []):
                        sd_to_insert.append({
                            "sense_id": sense_id,
                            "text": sd.get("text", ""),
                            "is_figurative": sd.get("is_figurative", False),
                            "is_rare": sd.get("is_rare", False),
                            "is_archaic": sd.get("is_archaic", False),
                            "_domain_codes": sd.get("domain_codes", []),
                            "_linked_words": sd.get("linked_words", []),
                        })

                self._post("linked_word", lw_rows)

                # Insert sub_definitions and their children
                if sd_to_insert:
                    clean_sd = [{k: v for k, v in r.items() if not k.startswith("_")} for r in sd_to_insert]
                    created_sds = self._post_returning("sub_definition", clean_sd)

                    domain_rows = []
                    sd_lw_rows = []
                    for k, sd_rec in enumerate(sd_to_insert):
                        sd_id = created_sds[k]["id"]
                        for code in sd_rec["_domain_codes"]:
                            domain_rows.append({"sub_definition_id": sd_id, "code": code})
                        for lw in sd_rec["_linked_words"]:
                            sd_lw_rows.append({
                                "sub_definition_id": sd_id,
                                "surface": lw.get("surface", ""),
                                "target_anchor": lw.get("target_anchor", ""),
                                "target_page": lw.get("target_page", ""),
                                "link_class": lw.get("link_class", ""),
                            })

                    self._post("sub_definition_domain", domain_rows)
                    self._post("linked_word", sd_lw_rows)

            print(f"    {letter}: {len(sense_rows)} senses")
        return sense_count

    def seed_examples(self, data_dir: Path) -> int:
        haw_dir = data_dir / "haw_eng"
        count = 0
        for jf in sorted(haw_dir.glob("*.json")):
            letter = jf.stem
            entries = load_json(jf)
            ex_rows = []
            for e in entries:
                eid = e.get("id", "")
                if not eid:
                    continue
                for ex in e.get("examples", []):
                    src_ref = ex.get("source_ref") or {}
                    ex_rows.append({
                        "_word_tokens": ex.get("word_tokens", []),
                        "entry_id": eid,
                        "hawaiian_text": ex.get("hawaiian_text", ""),
                        "english_text": ex.get("english_text", ""),
                        "note": ex.get("note", ""),
                        "olelo_noeau_num": ex.get("olelo_noeau_num", ""),
                        "bible_ref": ex.get("bible_ref", ""),
                        "is_causative": ex.get("is_causative", False),
                        "source_dict": ex.get("source_dict", "PE"),
                        "source_ref_type": src_ref.get("type", ""),
                        "source_ref_id": src_ref.get("id", ""),
                        "source_ref_url": src_ref.get("url", ""),
                    })

            for i in range(0, len(ex_rows), BATCH):
                batch = ex_rows[i:i + BATCH]
                clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in batch]
                created = self._post_returning("example", clean)
                count += len(created)

                wt_rows = []
                for j, ex_rec in enumerate(batch):
                    ex_id = created[j]["id"]
                    for wt in ex_rec["_word_tokens"]:
                        wt_rows.append({
                            "example_id": ex_id,
                            "surface": wt.get("surface", ""),
                            "anchor": wt.get("anchor", ""),
                            "target_entry": wt.get("target_entry", ""),
                        })
                self._post("word_token", wt_rows)

            if ex_rows:
                print(f"    {letter}: {len(ex_rows)} examples")
        return count

    def seed_bulk_table(self, data_dir: Path, table: str, extract_fn) -> int:
        """Generic bulk seeder for simple child tables."""
        haw_dir = data_dir / "haw_eng"
        rows = []
        for jf in sorted(haw_dir.glob("*.json")):
            entries = load_json(jf)
            for e in entries:
                eid = e.get("id", "")
                if not eid:
                    continue
                rows.extend(extract_fn(eid, e))
        return self._post(table, rows)

    def seed_etymologies(self, data_dir: Path) -> int:
        def extract(eid, e):
            ety = e.get("etymology")
            if not ety:
                return []
            return [{"entry_id": eid, "raw_text": ety.get("raw_text", ""),
                     "proto_form": ety.get("proto_form", ""), "proto_language": ety.get("proto_language", ""),
                     "qualifier": ety.get("qualifier", ""), "meaning": ety.get("meaning", ""),
                     "pollex_url": ety.get("pollex_url", "")}]
        return self.seed_bulk_table(data_dir, "etymology", extract)

    def seed_cross_refs(self, data_dir: Path) -> int:
        def extract(eid, e):
            return [{"entry_id": eid, "ref_type": xr.get("ref_type", ""),
                     "target_headword": xr.get("target_headword", ""),
                     "target_anchor": xr.get("target_anchor", ""),
                     "target_page": xr.get("target_page", ""),
                     "source_dict": xr.get("source_dict", "PE")}
                    for xr in e.get("cross_refs", [])]
        return self.seed_bulk_table(data_dir, "cross_ref", extract)

    def seed_grammar_refs(self, data_dir: Path) -> int:
        def extract(eid, e):
            return [{"entry_id": eid, "section": gr.get("section", ""),
                     "label": gr.get("label", ""), "pdf_url": gr.get("pdf_url", "")}
                    for gr in e.get("grammar_refs", [])]
        return self.seed_bulk_table(data_dir, "grammar_ref", extract)

    def seed_hawaiian_glosses(self, data_dir: Path) -> int:
        def extract(eid, e):
            return [{"entry_id": eid, "gloss": hg.get("gloss", ""),
                     "source_text_id": hg.get("source_text_id", ""),
                     "source_ref": hg.get("source_ref", "")}
                    for hg in e.get("hawaiian_glosses", [])]
        return self.seed_bulk_table(data_dir, "hawaiian_gloss", extract)

    def seed_images(self, data_dir: Path) -> int:
        def extract(eid, e):
            return [{"entry_id": eid, "thumbnail_url": img.get("thumbnail_url", ""),
                     "full_image_url": img.get("full_image_url", ""),
                     "source_url": img.get("source_url", ""),
                     "alt_text": img.get("alt_text", ""), "height": img.get("height", 0)}
                    for img in e.get("images", [])]
        return self.seed_bulk_table(data_dir, "image", extract)

    def seed_alt_spellings(self, data_dir: Path) -> int:
        def extract(eid, e):
            return [{"entry_id": eid, "spelling": sp} for sp in e.get("alt_spellings", [])]
        return self.seed_bulk_table(data_dir, "alt_spelling", extract)

    def seed_topics(self, data_dir: Path) -> int:
        haw_dir = data_dir / "haw_eng"
        topic_entries: dict[str, list[str]] = {}
        for jf in sorted(haw_dir.glob("*.json")):
            entries = load_json(jf)
            for e in entries:
                eid = e.get("id", "")
                if not eid:
                    continue
                for t in e.get("topics", []):
                    topic_entries.setdefault(t, []).append(eid)

        # Insert topics one by one to get IDs
        topic_ids = {}
        for name in sorted(topic_entries):
            created = self._post_returning("topic", [{"name": name}])
            if created:
                topic_ids[name] = created[0]["id"]

        # Insert entry_topic (dedup within each batch)
        seen = set()
        rows = []
        for name, eids in topic_entries.items():
            tid = topic_ids.get(name)
            if not tid:
                continue
            for eid in eids:
                key = (eid, tid)
                if key not in seen:
                    seen.add(key)
                    rows.append({"entry_id": eid, "topic_id": tid})
        self._post("entry_topic", rows)
        return len(topic_ids)

    def seed_eng_haw(self, data_dir: Path) -> tuple[int, int]:
        eng_dir = data_dir / "eng_haw"
        entry_count = 0
        trans_count = 0
        for jf in sorted(eng_dir.glob("*.json")):
            letter = jf.stem
            entries = load_json(jf)

            ehe_rows = []
            for e in entries:
                ehe_rows.append({
                    "_translations": e.get("translations", []),
                    "english_word": e.get("english_word", ""),
                    "source": e.get("source", "PE"),
                    "letter_page": e.get("letter_page", ""),
                })

            for i in range(0, len(ehe_rows), BATCH):
                batch = ehe_rows[i:i + BATCH]
                clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in batch]
                created = self._post_returning("eng_haw_entry", clean)
                entry_count += len(created)

                trans_rows = []
                for j, rec in enumerate(batch):
                    ehe_id = created[j]["id"]
                    for t in rec["_translations"]:
                        trans_rows.append({
                            "eng_haw_entry_id": ehe_id,
                            "hawaiian_word": t.get("hawaiian_word", ""),
                            "target_anchor": t.get("target_anchor", ""),
                            "target_page": t.get("target_page", ""),
                        })
                trans_count += self._post("eng_haw_translation", trans_rows)

            print(f"    {letter}: {len(ehe_rows)} entries")
        return entry_count, trans_count

    def seed_concordance(self, data_dir: Path) -> int:
        conc_dir = data_dir / "concordance"
        count = 0
        for jf in sorted(conc_dir.glob("*.json")):
            letter = jf.stem
            instances = load_json(jf)

            conc_rows = []
            for inst in instances:
                conc_rows.append({
                    "_word_tokens": inst.get("word_tokens", []),
                    "word": inst.get("word", ""),
                    "word_anchor": inst.get("word_anchor", ""),
                    "hawaiian_text": inst.get("hawaiian_text", ""),
                    "english_text": inst.get("english_text", ""),
                    "note": inst.get("note", ""),
                    "parent_entry_anchor": inst.get("parent_entry_anchor", ""),
                    "parent_entry_page": inst.get("parent_entry_page", ""),
                })

            for i in range(0, len(conc_rows), BATCH):
                batch = conc_rows[i:i + BATCH]
                clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in batch]
                created = self._post_returning("concordance", clean)
                count += len(created)

                wt_rows = []
                for j, rec in enumerate(batch):
                    conc_id = created[j]["id"]
                    for wt in rec["_word_tokens"]:
                        wt_rows.append({
                            "concordance_id": conc_id,
                            "surface": wt.get("surface", ""),
                            "anchor": wt.get("anchor", ""),
                            "target_entry": wt.get("target_entry", ""),
                        })
                self._post("word_token", wt_rows)

            print(f"    {letter}: {len(conc_rows)} instances")
        return count

    def seed_references(self, data_dir: Path) -> int:
        refs_path = data_dir / "support" / "refs.json"
        if not refs_path.exists():
            return 0
        refs = load_json(refs_path)
        rows = [{"abbreviation": r.get("abbreviation", ""), "anchor": r.get("anchor", ""),
                 "full_text": r.get("full_text", ""), "url": r.get("url", "")} for r in refs]
        return self._post("reference", rows)

    def verify_counts(self):
        """Check row counts via REST API."""
        tables = [
            "entry", "sense", "sub_definition", "sub_definition_domain",
            "linked_word", "example", "word_token", "etymology", "cross_ref",
            "grammar_ref", "hawaiian_gloss", "image", "alt_spelling",
            "topic", "entry_topic", "eng_haw_entry", "eng_haw_translation",
            "concordance", "reference",
        ]
        total = 0
        for t in tables:
            resp = requests.head(
                f"{self.base}/{t}?select=count",
                headers={**self.headers, "Prefer": "count=exact"},
            )
            count = int(resp.headers.get("content-range", "*/0").split("/")[1])
            total += count
            print(f"  {t:30s} {count:>10,}")
        print(f"  {'TOTAL':30s} {total:>10,}")


def seed_all(data_dir: Path = PROCESSED_DIR):
    url, key = get_config()
    seeder = SupabaseSeeder(url, key)

    print("=" * 60)
    print("CHD Database Seed (via REST API)")
    print("=" * 60)

    print("\nClearing existing data...")
    seeder.truncate_all()

    print("\nSeeding entries...")
    n = seeder.seed_entries(data_dir)
    print(f"  entries: {n:,}")

    print("\nSeeding senses + sub-definitions + linked words...")
    n = seeder.seed_senses(data_dir)
    print(f"  senses: {n:,}")

    print("\nSeeding examples + word tokens...")
    n = seeder.seed_examples(data_dir)
    print(f"  examples: {n:,}")

    print("\nSeeding etymologies...")
    n = seeder.seed_etymologies(data_dir)
    print(f"  etymologies: {n:,}")

    print("\nSeeding cross-references...")
    n = seeder.seed_cross_refs(data_dir)
    print(f"  cross_refs: {n:,}")

    print("\nSeeding grammar references...")
    n = seeder.seed_grammar_refs(data_dir)
    print(f"  grammar_refs: {n:,}")

    print("\nSeeding hawaiian glosses...")
    n = seeder.seed_hawaiian_glosses(data_dir)
    print(f"  hawaiian_glosses: {n:,}")

    print("\nSeeding images...")
    n = seeder.seed_images(data_dir)
    print(f"  images: {n:,}")

    print("\nSeeding alt spellings...")
    n = seeder.seed_alt_spellings(data_dir)
    print(f"  alt_spellings: {n:,}")

    print("\nSeeding topics...")
    n = seeder.seed_topics(data_dir)
    print(f"  topics: {n:,}")

    print("\nSeeding English-Hawaiian...")
    ne, nt = seeder.seed_eng_haw(data_dir)
    print(f"  eng_haw_entries: {ne:,}, translations: {nt:,}")

    print("\nSeeding concordance...")
    n = seeder.seed_concordance(data_dir)
    print(f"  concordance: {n:,}")

    print("\nSeeding references...")
    n = seeder.seed_references(data_dir)
    print(f"  references: {n:,}")

    print(f"\n{'=' * 60}")
    print("Verifying row counts...")
    seeder.verify_counts()
    print(f"{'=' * 60}")
    print("Seed complete!")


def main():
    parser = argparse.ArgumentParser(description="Seed Supabase database from exported JSON")
    parser.add_argument("--dir", type=Path, default=PROCESSED_DIR, help="Path to processed JSON directory")
    args = parser.parse_args()
    seed_all(args.dir)


if __name__ == "__main__":
    main()
