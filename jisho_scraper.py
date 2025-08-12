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


def scrapeKana(word_block):

	if not word_block:
		return

	writing = word_block.find("span", class_="text")
	furi = word_block.find("span", class_="furigana") # furi short for furigana

	if not writing or not furi:
		print(f"issue with bulding kana")
		return

	writing_chars = [ch.text.strip() for ch in writing]
	furi_chars = [ch.text.strip() for ch in furi]
	furi_chars = furi_chars[1:-1]

	kana = ""
	for i in range(len(furi_chars)):
		kana += writing_chars[i] if not furi_chars[i] else furi_chars[i]

	return kana


def scrapeDefinition(word_block):

	if not word_block:
		return

	def_num_css_class = "meaning-definition-section_divider"
	nums = word_block.find_all('span', class_=def_num_css_class)
	metadata = word_block.find_all('div', class_='meaning-tags')
	defs = word_block.find_all('span', class_='meaning-meaning')

	if not nums:
		print("issue finding definition information")
		return

	def_str = ""
	for i in range(len(nums)):
		if len(metadata) > i:
			def_str += metadata[i].text + '\n' 

		def_str += nums[i].text + defs[i].text

	return def_str



if __name__ == "__main__":
	word = ("愛","あい")
	word = ("食べる", "たべる")
	word = ("図書館", "としょかん")
	word = ("昼ご飯", "ひるごはん")
	word = ("", "さきおととい")
	word = ("一昨昨日", "")
	
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

	kana = scrapeKana(word_block)
	print(f"kana: {kana}")

	definition = scrapeDefinition(word_block)
	print(f"definition: {definition}")