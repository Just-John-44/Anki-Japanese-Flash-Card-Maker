import flashcard
import jisho_scraper as jscrape
import card_file_manager as fm
import sys


def main():
    
    argv = sys.argv
    if len(argv) != 2:
        print("usage: main.py 'filename.txt'")
        exit(1)
    else:
        filename = argv[1]

    print("jello")

    fm.initConfigFile()
    card_file_manager = fm.CardFileManager()
    vocab = tuple(card_file_manager.readWords(filename)) # vocab is a tuple of tuples
    
    flashcards = [flashcard.FlashCard(word) for word in vocab]

    # scrape jisho.org for word definitions
    for i in range(len(vocab)):
        writing_page, kana_page = jscrape.wordHtmlPages(vocab[i])
        if not writing_page and not kana_page:
            print(f"no pages found for {vocab[i][0]} or {vocab[i][1]}")
            continue

        word_block = jscrape.scrapeWordBlock(writing_page, vocab[i])
        if not word_block:
            word_block = jscrape.scrapeWordBlock(kana_page, vocab[i]) 
            if not word_block:
                print(f"no word block found for {vocab[i][0]} or {vocab[i][1]}")
                continue

        flashcards[i].definition = jscrape.scrapeDefinition(word_block)
    
    print(flashcards)





main()