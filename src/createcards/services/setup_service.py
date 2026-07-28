# setup_service.py
# Created: 6/24/2026
# Last Edited: 6/28/2026
# Author: John Wesley Thompson

import gzip
import shutil
from pathlib import Path
from ftplib import FTP
import sqlite3
import xml.etree.ElementTree as ET

DICT_GZ_PATH = Path("data/JMdict_e.gz")
DICT_XML_PATH = Path("data/JMdict_e.xml")


class SetupService:

    def run(self):
        self._downloadJMdict()
        self._buildDatabase()

        DICT_GZ_PATH.unlink()
        DICT_XML_PATH.unlink()

    def _downloadJMdict(self):
        print("Downloading JMdict...")

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        gz_path = data_dir / "JMdict_e.gz"
        xml_path = data_dir / "JMdict_e.xml"

        with FTP("ftp.edrdg.org") as ftp:
            ftp.login()

            remote_path = "/pub/Nihongo/JMdict_e.gz"

            with open(gz_path, "wb") as gz_file:
                ftp.retrbinary(f"RETR {remote_path}", gz_file.write)

        print("Extracting JMdict...")

        with gzip.open(gz_path, "rb") as src:
            with open(xml_path, "wb") as dst:
                shutil.copyfileobj(src, dst)

    def _buildDatabase(self):
        print("Building Database...")

        db_path = Path("data/jmdict.db")

        db_connection = sqlite3.connect(db_path)
        cursor = db_connection.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS spellings (
                spelling_id INTEGER PRIMARY KEY,
                entry_id INTEGER NOT NULL,
                spelling TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS readings (
                reading_id INTEGER PRIMARY KEY,
                entry_id INTEGER NOT NULL,
                reading TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS senses (
                sense_id INTEGER PRIMARY KEY,
                entry_id INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS glosses (
                gloss_id INTEGER PRIMARY KEY,
                entry_id INTEGER NOT NULL,
                sense_id INTEGER NOT NULL,
                gloss TEXT NOT NULL,
                FOREIGN KEY(sense_id) REFERENCES senses(sense_id)
            );
            """
        )

        tree = ET.parse(DICT_XML_PATH)
        root = tree.getroot()

        db_connection.execute("BEGIN")

        for entry in root.findall("entry"):
            entry_id = entry.findtext("ent_seq")
            if entry_id is None:
                return Exception("Error finding entry id for database entry")

            entry_id = int(entry_id)

            # insert spelling
            for keb in entry.findall("k_ele/keb"):
                cursor.execute (
                    "INSERT INTO spellings (entry_id, spelling) VALUES (?, ?)",
                    (entry_id, keb.text)
                )

            # insert readings
            for reb in entry.findall("r_ele/reb"):
                cursor.execute(
                    "INSERT INTO readings (entry_id, reading) VALUES (?, ?)",
                    (entry_id, reb.text)
                )

            # establish sense and glosses
            for sense in entry.findall("sense"):
                cursor.execute(
                    "INSERT INTO senses (entry_id) VALUES (?)",
                    (entry_id,)
                )

                sense_id = cursor.lastrowid

                for gloss in sense.findall("gloss"):
                    cursor.execute(
                        "INSERT INTO glosses (entry_id, sense_id, gloss) VALUES (?, ?, ?)",
                        (entry_id, sense_id, gloss.text)
                    )

        db_connection.commit()
        db_connection.close()
