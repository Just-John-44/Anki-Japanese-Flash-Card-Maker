# temp_file_manager.py
# Created: Jul 28 2026
# Last Edited: Jul 28 2026
# Author: John Wesley Thompson

from gtts.tts import gTTS
from uuid import uuid4
from pathlib import Path
import tempfile


class TempFileManager:
    def __init__(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_dir_name = Path(self._tmp_dir.name)

    def write_gtts_obj_to_temp_file(self, gtts_obj: gTTS) -> Path:
        filename = Path(f"{uuid4().hex[:12]}.mp3")
        gtts_obj.save(self.tmp_dir_name / filename)
        return filename

    def remove_temp_files(self) -> None:
        self._tmp_dir.cleanup()