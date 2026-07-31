# ccnote.py
# Created: 8/9/2025
# Last Edited: 7/28/2026
# Author: John Wesley Thompson

from typing import NamedTuple
from enum import IntEnum
import genanki


class CCNoteField(IntEnum):
    SPELLINGS           = 0
    READINGS            = 1
    READINGS_AUDIO_TAG  = 2
    SENTENCES           = 3
    SENTENCES_AUDIO_TAG = 4
    SENSES              = 5
    TAGS                = 6


class Word(NamedTuple):
    spelling: str
    reading: str


class Sense:
    '''Represents a meaning of a word (a sense)'''

    def __init__(self, sense_id: int, glosses: list[str]):
        self.sense_id = sense_id    # The id of the sense in the JMdict database
        self.glosses = glosses      # different ways a sense is expressed with language

    def __eq__(self, other) -> bool:
        if not isinstance(other, Sense):
            return NotImplemented

        return (
            self.sense_id == other.sense_id and self.glosses == other.glosses
        )

    def __str__(self):
        return ", ".join(self.glosses)

    # a sense may contain more information in the future like part of 
    # speech or a context that the sense is used in


class CCNote(genanki.Note):
    '''Object representing all of the data needed for an Anki flash card,
    inheriting from genanki's Note class'''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields: list [str | None] = [None] * len(CCNoteField)
        self.readings_audio_file: str = ""
        self.sentences_audio_file: str = ""
        self.entry_id: int | None = None

    def is_invalid(self) -> bool:
        '''Returns false if there are no fields in the note or if there is no entry id.'''

        if [f for f in self.fields] or not self.entry_id:
            return False

        return True
