# test_ccnote_service.py
# Created: Jul 28 2026
# Last Edited: Jul 28 2026
# Author: John Wesley Thompson

from createcards.services.ccnote_service import CREATECARDS_MODEL, CCNoteService
from createcards.ccnote import CCNote, CCNoteField, Word
import sqlite3
from pathlib import Path
from gtts.tts import gTTS
import pytest


class StubAIContentGenerator:
    def __init__(self, sentences, tags) -> None:
        self.sentences = sentences
        self.tags = tags

    def generate_content(self, vocab: list[Word]) -> tuple[list[str], list[str]]:
        return (self.sentences, self.tags)


class StubTempFileManager:
    def write_gtts_obj_to_temp_file(self, gtts_obj: gTTS) -> Path:
        return Path("/dev/null")

@pytest.mark.parameterize(
    ("sentences", "tags"),
    [
        ()
    ]
)
def test_generate_ai_content():
    db_conn = sqlite3.connect(":memory:")
    api_client = StubAIContentGenerator(
        [
            "猫が好きです。<br>猫はかわいいです。",
            "犬が走っています。<br>犬を飼っています。"
        ],
        [
            "Common・Daily Life",
            "Common・Daily Life",
        ],
    )
    tmp_file_manager = StubTempFileManager()
    service = CCNoteService(db_conn, api_client, tmp_file_manager)

    words = [
        Word("猫", "ねこ"),
        Word("犬", "いぬ"),
    ]

    notes = [
        CCNote(model=CREATECARDS_MODEL)
        for _ in words
    ]

    service._generate_AI_content(words=words, notes=notes)

    assert notes[0].fields[CCNoteField.SENTENCES] == (
        "猫が好きです。<br>猫はかわいいです。"
    )
    assert notes[0].fields[CCNoteField.TAGS] == "Common・Daily Life"

    assert notes[1].fields[CCNoteField.SENTENCES] == (
        "犬が走っています。<br>犬を飼っています。"
    )
    assert notes[1].fields[CCNoteField.TAGS] == "Common・Daily Life"

