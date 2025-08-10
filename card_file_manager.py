# John Wesley Thompson
# Created: 8/9/2025
# card_file_manager.py

import os


class CardFileManager:

    def __init__(self):
        self.search_dirs = [os.path.expanduser('~/Documents/')]
        self._initSearchDirs() # test this before doing anything else

    def _initSearchDirs(self):
        try:
            infile = open(".card_maker_config", "r")
        except Exception as e:
            print(f"error accessing config file: {e}")
            exit(1)

        file_lines = infile.readlines()
        for line in file_lines:
            if "SEARCH_DIRS" in line:
                search_dirs = line.split(';')

        if not search_dirs:
            print("no specified search directories")
            exit(1)
        
        
        for dir in search_dirs:
            self.search_dirs.append(dir)


    def readWords(self, filename):
        # if user enters an invalid filetype
        if len(filename.split('.')) == 1 or filename.split('.')[1] != "txt":
            print("file must be a .txt file")
            exit(1)

        abs_filename = self.input_search_dir + filename

        try:
            infile = open(abs_filename, "r", encoding='utf-8')
        except FileNotFoundError:
            print(f"file '{abs_filename}' not found")
            exit(1)

        words = infile.readlines()
        infile.close()

        return ([tuple(word.split()) if len(word.split()) == 2 else ("", word.strip()) 
                 for word in words])




if __name__ == "__main__":
    filename = "2025-08-09_vocab.txt"
    fm = CardFileManager()
    words = fm.readWords(filename)
    print(words)