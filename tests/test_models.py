"""Tests for chd.models module."""

import json
from chd.models import Entry, EngHawEntry, EngHawTranslation, ConcordanceInstance, Example, Etymology, Sense, SubDefinition, SourceRef, LinkedWord, WordToken, HawaiianGloss, ImageInfo


def test_entry_round_trip():
    entry = Entry(
        id="57179", headword="ʻā", headword_display="ʻā₁", headword_ascii="a",
        subscript="1", letter_page="a", in_pe=True, pdf_page="p001",
        senses=[Sense(sense_num=1, pos_raw="nvi.", text="fiery, burning.",
                      linked_words=[LinkedWord(surface="ahi", target_anchor="ahi")])],
        examples=[Example(hawaiian_text="ʻā akaaka", english_text="to shine brightly",
                         word_tokens=[WordToken(surface="ʻā", anchor="a")])],
        etymology=Etymology(raw_text="PPn *kaha", proto_form="*kaha", proto_language="PPn"),
        hawaiian_glosses=[HawaiianGloss(gloss="Ka hana a ke ahi", source_text_id="14")],
        images=[ImageInfo(thumbnail_url="images/aalii.jpg", height=45)],
    )
    restored = Entry.model_validate(entry.model_dump())
    assert restored.id == "57179"
    assert restored.headword == "ʻā"
    assert restored.senses[0].pos_raw == "nvi."
    assert restored.etymology.proto_form == "*kaha"

def test_entry_json_preserves_diacriticals():
    entry = Entry(headword="ʻōlelo")
    j = json.loads(entry.model_dump_json())
    assert j["headword"] == "ʻōlelo"

def test_eng_haw_round_trip():
    entry = EngHawEntry(english_word="abandon", translations=[EngHawTranslation(hawaiian_word="haʻalele")])
    restored = EngHawEntry.model_validate(entry.model_dump())
    assert restored.translations[0].hawaiian_word == "haʻalele"

def test_sub_definition():
    sub = SubDefinition(text="jaw, cheekbone.", domain_codes=["BOD"])
    assert sub.model_dump()["domain_codes"] == ["BOD"]

def test_source_ref():
    ref = SourceRef(type="ON", id="1681")
    assert ref.model_dump()["type"] == "ON"
