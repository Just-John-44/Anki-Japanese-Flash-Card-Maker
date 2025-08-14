import flashcard
import jisho_scraper as jscrape
import sentence_generator as sgenerator
import card_file_manager as fmanager

import sys
import os
# tts related includes
from kokoro import KPipeline
import soundfile as sf


def main():

    argv = sys.argv
    if len(argv) != 2:
        print("usage: main.py 'filename.txt'")
        exit(1)
    else:
        filename = argv[1]

    print("jello") # I like jello.

    fmanager.initFileSystem()
    card_file_manager = fmanager.CardFileManager()
    vocab = tuple(card_file_manager.readWords(filename)) # vocab is a tuple of tuples
    
    flashcards = [flashcard.FlashCard(word) for word in vocab]

    # initialize gpt sentence generator
    card_file_manager.addConfig("OPENAI_MODEL", "gpt-4o-mini")
    gpt_model = card_file_manager.getConfig("OPENAI_MODEL")
    gpt_client = sgenerator.initGPTClient()

    # generate sentences
    print("---generating example sentences via chat gpt---")
    sentences = sgenerator.promptChatGPT(gpt_client, gpt_model, vocab)
    gpt_client.close()

    # initialize tts pipeline and generate audio
    pipeline = KPipeline(lang_code='j')

    # add data to the flashcards
    for i, word in enumerate(vocab):
        # scrape definitions
        print(f"---scraping jisho.org for {word}---")

        writing_page, kana_page = jscrape.wordHtmlPages(word)
        if not writing_page and not kana_page:
            print(f"no pages found for {word[0]} or {word[1]}")
            continue

        word_block = jscrape.scrapeWordBlock(writing_page, word)
        if not word_block:
            word_block = jscrape.scrapeWordBlock(kana_page, word) 
            if not word_block:
                print(f"no word block found for {word[0]} or {word[1]}")

        definition = jscrape.scrapeDefinition(word_block)

        # generate audio
        tts_word = word[0] if word[0] else word[1]
        print(f"----generating audio for {word}----")
        tts_sentences = sentences[i].split('(')[0]

        word_output_name = f"{fmanager.AUDIO_DIR}{tts_word}"
        sentences_output_name = f"{fmanager.AUDIO_DIR}{tts_word}_sentences"
        generateTTSMp3(tts_word, word_output_name, pipeline)
        generateTTSMp3(tts_sentences, sentences_output_name, pipeline)

        # add data to cards
        flashcards[i].definition = definition
        flashcards[i].sentences = sentences[i]
        if os.path.isfile(f"{word_output_name}.mp3"):
            flashcards[i].word_audio_filepath = f"{word_output_name}.mp3"
        if os.path.isfile(f"{sentences_output_name}.mp3"):
            flashcards[i].sentence_audio_filepath = f"{sentences_output_name}.mp3"


    print(flashcards)


def generateTTSMp3(text, output_name, pipeline):
    # The best voice that the kokoro tts model has for japanese according to
    # their documentation at the time of this program's creation:
    generator = pipeline(text, voice="jf_alpha")
    kHz = 24000 # Kokoro uses 24 kHz
    # The pipeline yields segments: (graphemes, phonemes, audio_np)
    for tts_dat in generator: # tts_dat is a tuple of (graphemes, phonemes, audio data)
        sf.write(f"{output_name}.wav", tts_dat[2], kHz)
        os.system(f"ffmpeg -loglevel quiet -y -i {output_name}.wav -vn -ar {kHz} -ac 2 -b:a 192k {output_name}.mp3")
        os.system(f"rm {output_name}.wav")



main()