# cli.py
# Last Edited: 7/6/2026
# Author: John Wesley Thompson

from createcards.ccnote import Word
from createcards.sentence_generator import OpenAISentenceGenerator
from createcards.services.setup_service import SetupService
from createcards.services.ccnote_service import CCNoteService, CCNoteField

import sqlite3
from pathlib import Path
import argparse
import hashlib
import genanki
import sys

DATABASE_PATH = "data/jmdict.db"

DECK_NAME = "Createcards Deck v1"

DECK_ID = int.from_bytes(
    hashlib.blake2b(DECK_NAME.encode(), digest_size=4).digest(),
    byteorder="big"
)

COMPLETION_MESSAGE = """

apkg file created. Don't forget to add any missing values for
definitions that were listed as issues. Possible reasons for
issues:

- Provided a spelling for a word but no reading
  example: 猫 (not followed by a space and ねこ)
- Provided a word that is not in the database or is misspelled
"""

def main():
    args = parse_cli_args()

    if args.command == "setup":
        SetupService().run()
        return

    if not Path(DATABASE_PATH).is_file():
        print("Database not found. Run 'createcards setup' to set up the database.")
        sys.exit(1)

    try:
        vocab = read_vocab_file(args.input_file)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        sys.exit(1)

    # FlashCardService setup
    db_conn = sqlite3.connect(DATABASE_PATH)
    db_conn.row_factory = sqlite3.Row
    sentence_generator = OpenAISentenceGenerator()
    fc_service = CCNoteService(db_conn, sentence_generator)

    notes = fc_service.create_flash_cards(vocab)

    db_conn.close()

    # create Anki deck and package with genanki
    deck = genanki.Deck(
        deck_id=DECK_ID,
        name=DECK_NAME
    )
    for note in notes:
        deck.add_note(note)

    package = genanki.Package(deck)

    for note in notes:
        package.media_files.append(
            note.fields[CCNoteField.READINGS_AUDIO_TAG],
            note.fields[CCNoteField.SENTENCES_AUDIO_TAG]
        )

    # write to file and show completion
    package.write_to_file(args.output_file)

    print(COMPLETION_MESSAGE)


def text_file(path_str: str) -> Path:
    '''Argparse .text and .txt file type validation function'''
    path = Path(path_str)

    if path.suffix != ".txt" and path.suffix != ".text":
        raise argparse.ArgumentTypeError("Input file must be a text file.")

    return path


def apkg_file(path_str: str) -> Path:
    '''Argparse .apkg file type validation function'''
    path = Path(path_str)

    if path.suffix != ".apkg":
        raise argparse.ArgumentTypeError("Output file must be an apkg file.")

    return path


def parse_cli_args() -> argparse.Namespace:
    '''Parses CLI arguments and returns a dictionary of them'''
    cli_parser = argparse.ArgumentParser()
    cli_subparsers = cli_parser.add_subparsers(dest="command", required=True)

    cli_setup_parser = cli_subparsers.add_parser("setup")

    cli_generate_parser = cli_subparsers.add_parser("generate")
    cli_generate_parser.add_argument("input_file", type=text_file)
    cli_generate_parser.add_argument("output_file", type=apkg_file)

    return cli_parser.parse_args()



def read_vocab_file(filename: Path) -> list[Word]:
    '''Verifies file contences and returns a list of the vocabulary words'''
    try:
        with filename.open("r", encoding='utf-8') as vocab_file:
            lines = vocab_file.readlines()

    except FileNotFoundError:
        raise FileNotFoundError(f"file '{filename}' not found.")

    for i, line in enumerate(lines):
        line = line.strip().split()

        if len(line) > 2:
            raise ValueError(f"line {line} is invalid input. Only 2 fields should be provided")

        elif len(line) == 1:
            line.insert(0, "")

        lines[i] = Word(line[0], line[1])

    return lines


if __name__ == "__main__":
    main()
