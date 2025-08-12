import flashcard
import jisho_scraper as jscrape
import sentence_generator as sgenerator
import card_file_manager as fmanager
import sys


def main():
    
    argv = sys.argv
    if len(argv) != 2:
        print("usage: main.py 'filename.txt'")
        exit(1)
    else:
        filename = argv[1]

    print("jello")

    fmanager.initConfigFile()
    card_file_manager = fmanager.CardFileManager()
    vocab = tuple(card_file_manager.readWords(filename)) # vocab is a tuple of tuples
    
    flashcards = [flashcard.FlashCard(word) for word in vocab]

    # # scrape jisho.org for word definitions and prompt chatgpt for sentence examples
    # for i in range(len(vocab)):
    #     writing_page, kana_page = jscrape.wordHtmlPages(vocab[i])
    #     if not writing_page and not kana_page:
    #         print(f"no pages found for {vocab[i][0]} or {vocab[i][1]}")
    #         continue

    #     word_block = jscrape.scrapeWordBlock(writing_page, vocab[i])
    #     if not word_block:
    #         word_block = jscrape.scrapeWordBlock(kana_page, vocab[i]) 
    #         if not word_block:
    #             print(f"no word block found for {vocab[i][0]} or {vocab[i][1]}")
    #             continue

    #     flashcards[i].definition = jscrape.scrapeDefinition(word_block)
    
    # print(flashcards)

    card_file_manager.addConfig("OPENAI_MODEL", "gpt-4o-mini")
    gpt_model = card_file_manager.getConfig("OPENAI_MODEL")
    gpt_client = sgenerator.initGPTClient()
    print("---generating example sentences via chat gpt---")
    sentences = sgenerator.promptChatGPT(gpt_client, gpt_model, vocab)
    print(sentences)

    for i in range(len(vocab)):
        flashcards[i].sentences = sentences[i]

    print(flashcards)





main()