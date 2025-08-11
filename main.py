import flashcard
import card_file_manager as fm
import sys


def main():

    argv = sys.argv
    if len(argv) != 2:
        print("usage: main.py 'filename.txt'")
        exit(1)
    else:
        filename = argv[1]

    fm.initConfigFile()
    card_file_manager = fm.CardFileManager()
    vocab = tuple(card_file_manager.readWords(filename)) # vocab is a tuple of tuples


main()