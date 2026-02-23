"""Three-layer POS mapping: PE raw → Hawaiian pepeke → English.

Layer 1: PE raw label (preserved exactly)
Layer 2: Hawaiian grammatical category (pepeke system)
Layer 3: English-familiar tag
"""

from __future__ import annotations

# (pos_raw) → (pos_hawaiian, pos_english)
POS_MAP: dict[str, tuple[str, str]] = {
    "n.": ("kikino", "noun"),
    "v.": ("painu", "verb"),
    "vi.": ("painu hehele", "verb intransitive"),
    "vt.": ("painu hamani", "verb transitive"),
    "vs.": ("haina aano", "stative"),
    "nvs.": ("kikino + haina aano", "noun, stative"),
    "nvt.": ("kikino + painu hamani", "noun, verb transitive"),
    "nvi.": ("kikino + painu hehele", "noun, verb intransitive"),
    "adj.": ("kahulu", "adjective"),
    "adv.": ("kahulu", "adverb"),
    "conj.": ("huaolelo hoohui", "conjunction"),
    "prep.": ("ami", "preposition"),
    "pron.": ("papani", "pronoun"),
    "interj.": ("huaolelo hoike", "interjection"),
    "part.": ("ami", "particle"),
    "dem.": ("kai kuhikuhi", "demonstrative"),
    "s.": ("kikino", "noun"),  # Andrews "substantive"
    "conj., prep.": ("huaolelo hoohui + ami", "conjunction, preposition"),
    "gram.": ("", "grammar term"),
    "placename.": ("ioa wahi", "place name"),
    "idiom.": ("", "idiom"),
    "caus.": ("painu hoo-", "causative"),
    "caus/sim.": ("painu hoo-", "causative/simulative"),
    "nv.": ("kikino + painu", "noun, verb"),
    "nvs., vt.": ("kikino + haina aano + painu hamani", "noun, stative, verb transitive"),
}


def map_pos(pos_raw: str) -> tuple[str, str]:
    """Map a PE raw POS label to Hawaiian and English categories.

    Returns (pos_hawaiian, pos_english). Unknown labels return ("", "").
    """
    # Normalize whitespace
    key = pos_raw.strip()
    if key in POS_MAP:
        return POS_MAP[key]

    # Try lowercase
    key_lower = key.lower()
    for k, v in POS_MAP.items():
        if k.lower() == key_lower:
            return v

    return ("", "")
