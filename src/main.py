import flashcard
import jisho_scraper as jscrape
import sentence_generator as sgenerator
from datetime import date

import sys
# tts related includes 
from gtts import gTTS

AUDIO_DIR = "../ttsAudio/"


def main():

    argv = sys.argv
    if len(argv) != 2:
        print("usage: main.py 'filename.txt'")
        exit(1)
    else:
        filename = argv[1]

    print("jello") # I like jello.

    vocab = tuple(readWords(filename)) # vocab is a tuple of tuples (kanji, word), (..., ...)
    flashcards = [flashcard.FlashCard(word) for word in vocab]

    # generate sentences
    gpt_model = "gpt-4o-mini"
    gpt_client = sgenerator.initGPTClient()

    print("---generating example sentences via chat gpt---")
    sentences = sgenerator.promptChatGPT(gpt_client, gpt_model, vocab)
    gpt_client.close()

    # scrape definitions
    print("------scraping jisho.org for definitions-------")
    definitions = jscrape.gatherDefinitions(vocab)

    # generate tts audio
    print("-------generating audio with google tts--------")
    word_filepaths, sentence_filepaths = generateTTSMp3(vocab, sentences)

    # add data to the flashcards
    for i in range(len(flashcards)):
        flashcards[i].sentences = sentences[i]
        flashcards[i].definition = definitions[i]
        flashcards[i].word_audio_filepath = word_filepaths[i]
        flashcards[i].sentence_audio_filepath = sentence_filepaths[i]

    # print(flashcards)

    # create csv file
    with open(f"単語_{date.today().strftime('%Y-%m-%d')}.csv", "w") as outfile:
        for card in flashcards:
            print(card.csv_string(), file=outfile)



def generateTTSMp3(vocab, sentences):

    word_filenames = []
    sentence_filenames = []
    for word, sentence in zip(vocab, sentences):
        nonempty_word = word[0] if word[0] else word[1]

        word_out_filename = f"{AUDIO_DIR}{nonempty_word}.mp3"
        sentence_out_filename = f"{AUDIO_DIR}{nonempty_word}_sentences.mp3"

        gtts_obj = gTTS(text=nonempty_word, lang='ja', slow=False)
        gtts_obj.save(word_out_filename)

        sentence = sentence.split("(")[0]
        gtts_obj = gTTS(text=sentence, lang='ja', slow=False)
        gtts_obj.save(sentence_out_filename)

        word_filenames.append(word_out_filename)
        sentence_filenames.append(sentence_out_filename)

    return word_filenames, sentence_filenames


def readWords(filename: str):
        if filename.split('.')[1] != "txt" and filename.split('.')[1] != "text":
            print("file must be a text file")
            exit(1)

        try:
            infile = open(filename, "r", encoding='utf-8')
            words = infile.readlines()
            infile.close()
        except FileNotFoundError:
            print(f"file '{filename}' not found.")
            exit(1)

        return ([tuple(word.split()) if len(word.split()) == 2 else 
                 ("", word.strip()) for word in words])


main()