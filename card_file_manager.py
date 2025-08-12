# John Wesley Thompson
# Created: 8/9/2025
# card_file_manager.py

import os

CONFIG_FILE = ".card_maker_config"


class CardFileManager:

    search_dirs = []

    def __init__(self):
        self._initSearchDirs()


    def _initSearchDirs(self):
        try:
            infile = open(CONFIG_FILE, "r")
        except Exception as e:
            print(f"error accessing config file: {e}")
            exit(1)

        file_lines = infile.readlines()
        for line in file_lines:
            if "SEARCH_DIRS" in line:
                search_dirs = line.replace("SEARCH_DIRS=", "").split(';')
                search_dirs = [dir.strip() for dir in search_dirs]

        if not search_dirs:
            print("no specified search directories")
            exit(1)
        
        for dir in search_dirs:
            self.search_dirs.append(dir)


    def readWords(self, filename):
        if len(filename.split('.')) == 1 or filename.split('.')[1] != "txt":
            print("file must be a .txt file")
            exit(1)

        abs_filename = filename
        for dir in self.search_dirs:
            if os.path.isfile(dir + filename):
                abs_filename = dir + filename
                break

        try:
            infile = open(abs_filename, "r", encoding='utf-8')
            words = infile.readlines()
            infile.close()
        except FileNotFoundError:
            print(f"file '{abs_filename}' not found.")
            exit(1)

        return ([tuple(word.split()) if len(word.split()) == 2 else 
                 ("", word.strip()) for word in words])
    

    def getConfig(self, config_name):
        try:
            infile = open(CONFIG_FILE, "r",  encoding='utf-8')
        except Exception:
            print("issue opening config file")

        config = [line for line in infile.readlines() if config_name in line]
        infile.close()

        if not config:
            print(f"no config named {config_name} found in config file")
            return

        return config[0].replace(config_name + '=', "").strip()
    

    def addConfig(self, config_name, config_val):
        try:
            infile = open(CONFIG_FILE, "r+",  encoding='utf-8')
        except Exception:
            print("issue opening config file")

        configs = infile.readlines()
        for config in configs:
            if config_name in config:
                infile.close()
                return

        infile.write('\n' + config_name + '=' + config_val)
        infile.close()


def initConfigFile():
    try:
        # at the moment this block code assumes that if there is a 
        # .card_maker_config file, then there is a valid search directory
        # inside
        if not os.path.isfile(CONFIG_FILE):
            infile = open(CONFIG_FILE, "w")
            infile.write(f"SEARCH_DIRS={os.path.expanduser('~/Documents/')}")
            infile.close()

    except Exception as e:
        print(f"error initializing config file: {e}")
        exit(1)



if __name__ == "__main__":
    filename = "2025-08-09_vocab.txt"
    filem = CardFileManager()
    words = filem.readWords(filename)
    print(f"readWordsOutput: {words}")
    print(f"search_dirs: {filem.search_dirs}")