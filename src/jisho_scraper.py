# John Wesley Thompson
# Created: 8/10/2025
# jisho_scraper.py

import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://jisho.org/search/"


def wordHtmlPages(word):
    writing_url = BASE_URL + word[0]
    kana_url = BASE_URL + word[1]

    writing_page = requests.get(writing_url)
    time.sleep(1)
    kana_page = requests.get(kana_url)
    time.sleep(1)

    if writing_page.status_code != 200 and kana_page.status_code != 200:
        print(f"no search results for {word[0]} or {word[1]}")

    elif writing_page.status_code == 429 or kana_page.status_code == 429:
        print("too many requests.")

    return writing_page, kana_page


def scrapeWordBlock(page, word):
    pg_contents = BeautifulSoup(page.text, "html.parser")
    if pg_contents.find("div", id="no-matches"):
        print("no word info found.")
        return

    # get all definition blocks in a page
    word_blocks = pg_contents.find_all("div", class_="concept_light clearfix")

    for word_block in word_blocks:
        if (word[0] and word[0] in word_block.find("span", class_="text").text
            or word[1] and word[1] in word_block.text):
            return word_block

    return


def scrapeDefinition(word_block):

    if not word_block:
        return ""

    # gather information from html elements
    nums = word_block.find_all('span', class_="meaning-definition-section_divider")
    parts_of_speech = word_block.find_all('div', class_='meaning-tags')
    defs = word_block.find_all('span', class_='meaning-meaning')

    if not nums or len(parts_of_speech) < len(nums): # all defs are numbered, so return in the case where there are none
        print("issue finding definition information")
        return ""

    desired_pos = {
        "Godan":"[go.]", 
        "Ichidan":"[ichi.]", 
        "Noun":"[n.]", 
        "Suru verb":"[suru v.]", 
        "Na-adjective":"[na-adj.]", 
        "I-adjective":"[i-adj.]", 
        "Transitive":"[tra.]", 
        "Intransitive":"[intra.]", 
        "Adverb":"[adv.]", 
        "Place":"[Place]"
    }

    def_str = ""
    max_defs = 3
    for i in range(len(nums)):

        if i == max_defs:
            def_str += "...\n"
            break
        
        filtered_pos = []
        curr_def_pos = parts_of_speech[i].text.split(", ") # pos is short for part of speech
        for j in range(len(curr_def_pos)):
            for pos in desired_pos:
                if pos in curr_def_pos[j]:
                    filtered_pos.append(desired_pos[pos])

        if not filtered_pos:
            continue # don't want def lines for any other type of info

        for f_pos in filtered_pos:
            def_str += f_pos

        def_str += '\n' + nums[i].text + defs[i].text + '\n'

    if def_str:
        return def_str
    else:
        print("issue finding definition information")
        return ""


def gatherDefinitions(vocab):

    definitions = []
    for word in vocab:
        writing_page, kana_page = wordHtmlPages(word)
        if not writing_page and not kana_page:
            print(f"no pages found for {word[0]} or {word[1]}")
            continue

        word_block = scrapeWordBlock(writing_page, word)
        if not word_block:
            word_block = scrapeWordBlock(kana_page, word) 
            if not word_block:
                print(f"no word block found for {word[0]} or {word[1]}")

        definitions.append(scrapeDefinition(word_block))

    return definitions



if __name__ == "__main__":
    word = ("愛","あい")
    word = ("食べる", "たべる")
    word = ("図書館", "としょかん")
    word = ("昼ご飯", "ひるごはん")
    word = ("", "さきおととい")
    word = ("一昨昨日", "")
    word = ("極端", "きょくたん")
    word = ("開く", "あく")

    writing_page, kana_page = wordHtmlPages(word)
    if writing_page or kana_page:
        print("at least one page found for word")
    else:
        print("no pages found for word")
    word_block = scrapeWordBlock(writing_page, word)
    if word_block:
        print(f"word block:\n{word_block.text}")
    else:
        word_block = scrapeWordBlock(kana_page, word)
        if word_block:
            print(f"word block:\n{word_block.text}")
        else:
            print(f"no word block found")
    # kana = scrapeKana(word_block)
    # print(f"kana: {kana}")
    definition = scrapeDefinition(word_block)
    print(f"definition: {definition}")