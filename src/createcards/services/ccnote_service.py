# flash_card_service.py
# Created: 6/25/2026
# Last Edited: 7/28/2026
# Author: John Wesley Thompson

from createcards.ccnote import CCNote, Sense, Word, CCNoteField
from createcards.sentence_generator import OpenAISentenceGenerator
from createcards.temp_file_manager import TempFileManager

import json
from gtts import gTTS
import sqlite3
import genanki
import hashlib


DICT_ENTRY_QUERY = """
SELECT 
(
    SELECT json_group_array(DISTINCT spelling)
    FROM spellings
    WHERE entry_id = ?1
) AS spellings,

(
    SELECT json_group_array(DISTINCT reading)
    FROM readings
    WHERE entry_id = ?1
) AS readings,

(
    SELECT json_group_array(
        json_object(
            'sense_id', sense_id,
            'glosses', json(glosses)
        )
    )
    FROM 
    (
        SELECT
            sense_id,
            json_group_array(DISTINCT gloss) AS glosses
        FROM glosses
        WHERE entry_id = ?1
        GROUP BY sense_id
        ORDER BY sense_id
    )
) AS senses
"""

MODEL_NAME = "Createcards | Front + Back v1"

MODEL_ID = int.from_bytes(
    hashlib.blake2b(MODEL_NAME.encode(), digest_size=4).digest(),
    byteorder="big"
)

MODEL_TEMPLATE_FRONT = "{{Spellings}} | {{Readings}} {{Readings_Audio_Tag}}<br> \
        {{Sentences}}<br> \
        {{Sentences_Audio_Tag}}"

MODEL_TEMPLATE_BACK = "{{Senses}}"

CREATECARDS_MODEL = genanki.Model(
    model_id=MODEL_ID,
    name=MODEL_NAME,
    fields=[
        {"name": "Spellings"},
        {"name": "Readings"},
        {"name": "Readings_Audio_Tag"},
        {"name": "Sentences"},
        {"name": "Sentences_Audio_Tag"},
        {"name": "Senses"},
    ],
    templates=[
        {
            "name": "Createcards Forward v1",
            "qfmt": MODEL_TEMPLATE_FRONT,
            "afmt": "{{FrontSide}}<hr id='answer'>" + MODEL_TEMPLATE_BACK
        },
        {
            "name": "Createcards Reversed v1",
            "qfmt": MODEL_TEMPLATE_BACK,
            "afmt": MODEL_TEMPLATE_FRONT + "<hr id='answer'>{{FrontSide}}"
        }
    ]
)


class CCNoteService:
    '''Constructs CCNote objects from different sources.'''

    def __init__(
        self,
        db_conn: sqlite3.Connection,
        sentence_generator: OpenAISentenceGenerator,
        tmp_file_manager: TempFileManager,
    ):
        self.db_conn = db_conn
        self.sentence_generator = sentence_generator
        self.tmp_file_manager = tmp_file_manager

    def create_flash_cards(self, words: list[Word], print_progress: bool = True) -> list[CCNote]:
        '''Creates of a list of FlashCard objects, querying the dictionary 
        database, generating sentences, and generating audio.'''

        notes = [CCNote(model=CREATECARDS_MODEL) for _ in range(len(words))]

        # Database querying ---------------------------------------------------
        if print_progress:
            print("-----------Gathering entries from database-----------")

        self._populate_dict_entry_data(words, notes)

        # openai sentence generation ------------------------------------------
        if print_progress:
            print("----------Generating sentences with OpenAI-----------")

        self._generate_sentences(words, notes)

        # gTTs audio generation -----------------------------------------------
        if print_progress:
            print("-----Generating audio with Google Text-to-Speech-----")


        self._generate_audio(words, notes)

        return notes

    def _populate_dict_entry_data(self, words: list[Word], notes: list[CCNote]) -> None:
        '''Gathers word spellings, readings, and senses, and then populates those fields.'''

        db_cursor = self.db_conn.cursor()

        for i, word in enumerate(words):
            if not word.spelling and not word.reading: 
                raise ValueError("Empty lines in the input file are not allowed.")

            elif not word.spelling:
                db_cursor.execute(
                    "SELECT readings.entry_id FROM readings WHERE readings.reading = ?",
                    (word.reading,)
                )

            elif not word.reading:
                db_cursor.execute(
                    "SELECT spellings.entry_id FROM spellings WHERE spellings.spelling = ?",
                    (word.spelling,)
                )

            # both reading and spelling is given
            else: 
                db_cursor.execute(
                    """
                    SELECT spellings.entry_id FROM spellings 
                    JOIN readings USING (entry_id)
                    WHERE spellings.spelling = ? AND readings.reading = ?
                    """,
                    (word.spelling, word.reading)
                )

            # No result was found
            row = db_cursor.fetchone()
            if row is None:
                notes[i].entry_id = None
                notes[i].fields = []
                print(f"-!!!----- No entry found for {word.spelling or word.reading}")
                continue

            # In the case the user enters an ambiguous vocab word, the first 
            # match will be chosen. This should only happen when the user 
            entry_id = row['entry_id']

            # One big query with subqueries to gather information for one card
            db_cursor.execute(DICT_ENTRY_QUERY, (entry_id,))

            row = db_cursor.fetchone()

            notes[i].entry_id = entry_id
            notes[i].fields[CCNoteField.SPELLINGS] = "、".join(json.loads(row['spellings']))
            notes[i].fields[CCNoteField.READINGS] = "、".join(json.loads(row['readings']))
            notes[i].fields[CCNoteField.SENSES] =  "<br>".join(
                str(Sense(sense['sense_id'], sense['glosses'])) 
                for sense in json.loads(row['senses'])
            )

    def _generate_sentences(self, words: list[Word], notes: list[CCNote]) -> None:
        '''Generates sentences and populates the sentences field of a CCNote'''

        sentences = self.sentence_generator.generate_sentences(words)

        for i in range(len(words)):
            notes[i].fields[CCNoteField.SENTENCES] = sentences[i]

    def _generate_audio(self, words: list[Word], notes: list[CCNote]) -> None:
        '''Generates audio and populates the audio fields of a CCNote'''

        for i, word in enumerate(words):
            gtts_obj = gTTS(text=(word.reading or word.spelling), lang='ja', slow=False)
            readings_filename = self.tmp_file_manager.write_gtts_obj_to_temp_file(gtts_obj)

            if isinstance(sentences_text := notes[i].fields[CCNoteField.SENTENCES], str):
                sentences_text = sentences_text.replace("<br>", '')
                gtts_obj = gTTS(text=sentences_text, lang='ja', slow=False)
                sentences_filename = self.tmp_file_manager.write_gtts_obj_to_temp_file(gtts_obj)

            notes[i].readings_audio_file = str(readings_filename)
            notes[i].sentences_audio_file = str(sentences_filename)
            notes[i].fields[CCNoteField.READINGS_AUDIO_TAG] = f"[sound:{readings_filename}]"
            notes[i].fields[CCNoteField.SENTENCES_AUDIO_TAG] = f"[sound:{sentences_filename}]"
