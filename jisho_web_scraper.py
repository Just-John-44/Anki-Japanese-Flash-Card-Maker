# John Wesley Thompson
# Created: 7/3/2025
# Last Edited: 7/6/2025
# jisho_web_scraper.py

# This program is meant to search jisho for a list of words and find the
# definitions of each one. I don't like to copy and paste all of my 
# Japanese flash card information into anki, so this will be my new method.

import re
import requests
from bs4 import BeautifulSoup
import time
import os
import sys

URL_BASE = "https://jisho.org/search/"

def main():

	filepath = "../../単語/"

	argc = len(sys.argv)
	if (argc != 2):
		print("---no file name entered---")
		return

	filename = filepath + sys.argv[1]

	print("jello")
	search_terms_list = read_word_file(filename)
	search_output = []

	no_definitions_list = []	

	for search_terms in search_terms_list:
		
		print_progress(search_terms_list, search_terms)
		
		term1_page, term2_page = retrieve_html_page(search_terms)
		if term1_page.status_code != 200 and term2_page.status_code != 200:
			print("-------no search results-------")
			return

		word_info = search_for_word_info(term1_page, search_terms)
		if word_info == None and term2_page.status_code == 200:
			word_info = search_for_word_info(term2_page, search_terms)
			if word_info == None:
				#print(f"---no definition_found for {search_terms}---")
				no_definitions_list.append(search_terms)
				search_output.append("[no definition found]\n--\n")
				continue

		elif term2_page.status_code != 200:
			#print(f"---no definition found for {search_terms}---")
			no_definitions_list.append(search_terms)
			search_output.append("[no definition found]\n--\n")
			continue

		search_output.append(word_info)

	append_defs_to_file(filename, search_output)

	print("-----definitions appended to file-----")
	if no_definitions_list:
		print("-------no definitions found for-------")
		for i in no_definitions_list:
			print(i)

	return


# append_defs_to_file takes all of the information that was taken from the 
# jisho.org pages and appends it to a file, which should be the same as the
# file that the words were read from
# input: a filename to open and the information to be appended as a list of
# 		 strings
def append_defs_to_file(filename, defs):

	try:	
		outfile = open(filename, "a")
	except FileNotFoundError:
		print("-----failed to append definitions to file-----")
		exit(1)

	outfile.write("\nDEFINITIONS\n")
	for i in defs:
		outfile.write(i)

	outfile.close()


# read_word_file opens the file containing all of the search terms and 
# provides them in a list
# input: the file name of the file to be opened
# output: a list of paired search terms (the word's writing, and the word's)
#		  hiragana
def read_word_file(filename):
	try:
		infile = open(filename, "r")
	except FileNotFoundError:
		print("-------words file not found-------")
		exit(1)

	file_lines = infile.readlines()
	infile.close()	

	if file_lines[0] != "WORDS\n":
		print("---Expected 'WORDS' at beginning of file---")
		exit(1)
	else:
		file_lines.pop(0)

	words_list = [x.split() for x in file_lines]
	words_list = [x for x in words_list if x]
	for i in range(len(words_list)):
		if len(words_list[i]) == 1:
			words_list[i] = [""] + words_list[i]

		if "・" in words_list[i][1]:
			second_word = words_list[i][1].split("・")[0]
			words_list[i][1] = second_word
	

	return words_list


# print_progress prints the term that is currently being processed and a rough
# estimate of the completion of the search for the whole word list
# input: the list of all of the search term pairs, and the search term pair 
#		 currently being searched for
def print_progress(search_terms_list, search_terms):

	os.system('clear')
	print(f"Searching for {search_terms}")

	search_term_ct = len(search_terms_list)
	completed_searches = search_terms_list.index(search_terms)
	completed_percent = (completed_searches + 1) / search_term_ct * 100
	print(f"[ Searching | {completed_percent:.2f}% ]")


# retrieve_html_page finds the page that contains all of the definitions for a 
# search on jisho.org
# input: a list of a words writing and hiragana
# output: two page search results. one for the writing and one for the hiragana
#		  if a page isn't found, a message is displayed telling the user so
def retrieve_html_page(search_terms):
	term1_url = URL_BASE + search_terms[0]
	term2_url = URL_BASE + search_terms[1]

	time.sleep(1)
	term1_page = requests.get(term1_url)
	time.sleep(1)
	term2_page = requests.get(term2_url)
	if term1_page.status_code != 200:
		print("-----------page1 retrieval error------------")
	if term2_page.status_code != 200:
		print("-----------page2 retrieval error------------")
	if term1_page.status_code == 429 or term2_page.status_code == 429:
		print("----------too many requests error----------")

	return term1_page, term2_page


# gather_writing gathers the main writing of a word on jisho.org
# input: the html of the whole definition block
# output: a list where each element is a kanji or kana of the writing of a word
def gather_writing(def_block):
	
	writing = def_block.find('span', class_='text')
	
	if writing == None:
		return None

	writing_str = writing.text
	writing_str = writing_str.strip()
	writing_lst = []
	for i in writing_str:
		writing_lst.append(i)
		
	return writing_lst


# gather_furigana gathers the furigana that appears above the kanji in the 
# writing of the word on jisho.org
# input: the html of the whole definition block
# output: a list with each element containing the furigana for a kanji, or an
#		  empty string for kana that dont need furigana
def gather_furigana(def_block):
	
	furigana = def_block.find('span', class_='furigana')

	if furigana == None:
		return None

	furi = [] 
	for i in furigana:
		furi.append(i.text)
		
	furi.pop(0)
	furi.pop(-1)

	return furi


# sync_furi_and_writing combines the furigana and the kana in the writing to 
# create a whole hiragana-only word
# input: the furigana list and writing list both gathered from a dictionary 
# 		 block
# output: a hiragana word as a string
def sync_furi_and_writing(furi, writing):

	if furi == None or writing == None:
		return

	hiragana = ""
	for i in range(len(furi)):
		if furi[i] == "":
			hiragana += writing[i]
		else:
			hiragana += furi[i]

	return hiragana


# gather_def_data gathers the definitions of a word from a definition block
# input: a definition block
# output: a list of strings with numbered definitions for a word 
def gather_def_data(def_block):
	
	def_nums = def_block.find_all('span', class_='meaning-definition-section_divider')
	
	defs = def_block.find_all('span', class_='meaning-meaning')
	if defs != None:
		defs_lst = []
		for i in range(len(defs)):
			def_str = ""
			if i < len(def_nums):
				def_str += def_nums[i].text + defs[i].text
			else:
				def_str += defs[i].text 			

			defs_lst.append(def_str)
	
	else:
		return None	

	return defs_lst


# gather_def_metadata finds the part of speech, the type of word, and/or
# info such as "other forms" or "wikipedia meaning"
# input: a definition block
# output: a list of strings containing data about a word
def gather_def_metadata(def_block):

	def_metadata = def_block.find_all('div', class_='meaning-tags')
	if def_metadata == None:
		print("ITS NONE")
		return None

	def_metadata_lst = []
	for i in def_metadata:
		def_metadata_lst.append(i.text)
	
	return def_metadata_lst


# compile_word_into_string takes all of the data gathered from a definition
# block and puts it together in an easily readable string
# input: a words writing list, hiragana string, metadata list, and 
#		 definition list
# output: a single string containing info about a word
def compile_word_info_string(writing, hiragana, metadata, defs):
	word_info_str = ""
	if writing == hiragana:
		word_info_str += writing + '\n'
	else:
		word_info_str += writing + '　' + hiragana + '\n'

	for i in range(len(metadata)):
		word_info_str += metadata[i] + '\n' + defs[i] + '\n'

	word_info_str += "--\n"

	return word_info_str


# search_for_word_info searches a page and utilizes various functions to create
# an easily understandable interpretation of the information gathered from
# jisho.org. it finds the terms being searched for within a page and gathers 
# info about it
# input: an html page and a word's pair of search terms
# output: an easily understandable string containing the searches information
def search_for_word_info(page, search_terms):

	# get all definition blocks in a page
	page_contents = BeautifulSoup(page.text, 'html.parser')
	no_match = page_contents.find('div', id='no-matches')

	def_blocks = page_contents.find_all('div', class_='concept_light clearfix')

	def_block_num = 0
	for i in def_blocks:

		# gather needed info for word searching and result making
		writing = gather_writing(i)
		if writing == None:
			continue		

		furi = gather_furigana(i)

		hiragana = sync_furi_and_writing(furi, writing)
		
		def_metadata = gather_def_metadata(i)
		
		defs = gather_def_data(i)

		# deal with unwanted or special word information
		other_forms = ""
		other_forms_lst = []
		if def_metadata != None and defs != None:
			if "Wikipedia definition" in def_metadata:
				idx = def_metadata.index("Wikipedia definition")
				def_metadata.pop(idx)
				defs.pop(idx)

			if "Notes" in def_metadata:
				idx = def_metadata.index("Notes")
				def_metadata.pop(idx)

			if "Other forms" in def_metadata:
				idx = def_metadata.index("Other forms")
				other_forms = defs[idx]
				defs.pop(idx)
				def_metadata.pop(idx)
				
				other_forms_lst = re.split(r'[、 ]', other_forms)
				other_forms_lst = [i.strip("】【") for i in other_forms_lst]


		# search the gathered info for a match with the word being searched for
		writing = ''.join(writing)
		hiragana = ''.join(hiragana)

		if search_terms[0] == "":
			if search_terms[1] == writing or search_terms[1] == hiragana:
				result = compile_word_info_string(writing, hiragana, def_metadata, defs)
				return result
	
		else:
			if search_terms[1] == hiragana:
				if search_terms[0] == writing:
					result = compile_word_info_string(writing, hiragana, def_metadata, defs)
					return result
				elif other_forms_lst:
					if search_terms[0] in other_forms_lst:
						result = compile_word_info_string(writing, hiragana, def_metadata, defs)
						return result
					 

	return None
				
		

main()
