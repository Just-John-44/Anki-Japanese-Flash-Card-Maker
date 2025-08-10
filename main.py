import flashcard
import card_file_manager as fm
import sys
import os

def main():
    argv = sys.argv
    if len(argv) != 2:
        print("usage: main.py 'filename.txt'")
        exit(1)
    else:
        filename = argv[1]

    card_file_manager = fm.CardFileManager()
    vocab = tuple(card_file_manager.readWords(filename)) # vocab is a tuple of tuples


    
main()

def fileSearchDirPrompt(default_dir):
    ok_dir = False
    while not ok_dir:
        print(f"The default search directory for your vocab list is"
              f" {default_dir}.")
        input("press enter to continue with this directory."
              " Otherwise press any")
