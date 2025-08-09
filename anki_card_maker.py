# John Wesley Thompson
# Created: 6/30/2025
# Last Edited: 7/10/2025
# anki_card_creator.py

# This program will help me make anki cards just a little bit faster.
# It will read a text file that contains flash card information and create
# a tab separated value file that can be easily imported into anki.

import sys
import re
from datetime import date

DEF_KEY_WORDS = ["Godan", "Ichidan", "Noun", "Suru", "Na-adjective", "I-adjective", "Transitive", "Intransitive", "Adverb", "Place"]

def main():

	argc = len(sys.argv)
	if (argc != 2):
		print("---no file name entered---")
		return

	filename = sys.argv[1]
	
	infile = find_file(filename)

	words, defs, sentences = read_file(infile)

	process_lists(words, defs, sentences)	

	create_tsv_file(words, defs, sentences)

	return

	
# find_file finds a file or doesn't and prints a message accordingly
# input: the name of a file to be opened
# output: a file object if the file was found
def find_file(filename):
	
	default_dir = "../../単語/"
	filename = default_dir + filename	
	
	print(filename)

	try:
		infile = open(filename, "r")
		print("---------file-found----------")

	except FileNotFoundError:
		print("---The specified file was not found.---")
		exit(1)

	return infile


# read_file reads the file given by the user and returns 3 lists containing
# all of the word, definitions, and example sentences respectively
# input: a file object to read from
# output: a list of words, a list of definitions, and a list of sentences
def read_file(infile):

	word_header = "WORDS\n"
	def_header = "DEFINITIONS\n"
	sentence_header = "SENTENCES\n"

	file_contents = infile.readlines()
	infile.close()

	words = []
	definitions = []
	sentences = []

	last_header = word_header
	for i in range(len(file_contents)):

		if file_contents[i] == word_header:
			last_header = word_header
			continue
		elif file_contents[i] == def_header:
			last_header = def_header
			continue
		elif file_contents[i] == sentence_header:
			last_header = sentence_header
			continue

		if last_header == word_header:
			words.append(file_contents[i])
		elif last_header == def_header:
			definitions.append(file_contents[i])
		else: # last header == sentence_header
			sentences.append(file_contents[i])


	return words, definitions, sentences


# process_lists formats all of the information in the lists to something easily
# readable on an anki card
# input: a list of words, a list of definitions, and a list of sentences
# output: the three lists but modified
def process_lists(words, defs, sentences):

	# Words
	for i in range(len(words)):
		words[i] = words[i].rstrip()
	words[:] = [x for x in words if x != ""]

	# Definitions	
	new_defs = []

	# "Godan", "Ichidan", "Noun", "Suru", "Na-adjective", "I-adjective, Transitive, Intransitive, Adverb"

	for i in range(len(defs)):
		
		godan = ichidan = tra = intra = suru_v = adv = False
		# check if the line is before a definition line
		if any(x in defs[i] for x in DEF_KEY_WORDS):
			if "Godan" in defs[i]:
				godan = True
			if "Ichidan" in defs[i]:
				ichidan = True
			if "Transitive" in defs[i]:
				tra = True
			if "Intransitive" in defs[i]:
				intra = True	
			if "Suru" in defs[i]:
				suru_v = True
			if "Adverb" in defs[i]:
				adv = True

			new_defs.append(defs[i + 1])

		if "--" in defs[i] or "[no definition found]" in defs[i]:
			new_defs.append(defs[i])

		# add information gathered from the pre definition line in a readable
		# format
		word_type_str = ""
		if suru_v:
			word_type_str += "[suru_v]"
		if godan:
			word_type_str += "[go]"
		if ichidan:
			word_type_str += "[ichi]"
		if tra:
			word_type_str += "[tra]"
		if intra:
			word_type_str += "[intra]"
		if adv:
			word_type_str += "[adv]"			

		if word_type_str != "":
			new_defs.append(word_type_str + '\n')


	defs[:] = new_defs[:]


	curr_def = ""
	defs_captured = 0
	new_defs = []
	for i in defs:

		# only gather 3 definitions per word
		if defs_captured == 3 and "--" not in i:
			continue

		curr_def += "<br>" + i.rstrip()
		if "--" in curr_def:
			curr_def = curr_def.rstrip("\n-")
			new_defs.append(curr_def)
			defs_captured = 0
			curr_def = ""

		# checks if the first thing in a line is a number
		elif i.split()[0].rstrip(".").isdigit():
			defs_captured += 1	
		

	defs[:] = new_defs[:]

	#Sentences
	new_sentences = []
	for i in range(len(sentences)):
		if re.search(r"\d+\.", sentences[i]): 
			new_sentences.append(sentences[i + 1] + sentences[i + 2] + sentences[i + 3])
			new_sentences[-1] = new_sentences[-1].replace("\n", "<br>")

	sentences[:] = new_sentences[:]
	

# create_tsv_file creates a tsv file from all of the lists treated in previous
# functions to be imported into anki
# input: a list of words, a list of definitions, and a list of sentences
# output: a tsv file
def create_tsv_file(words, defs, sentences):
	curr_date = date.today()
	
	if len(words) != len(defs) or len(words) != len(sentences):
		print("data does not match. file not created")
		exit(1)

	filename = "../../単語/単語" + curr_date.strftime("%Y-%m-%d") + ".tsv"
	try:
		outfile = open(filename, "w")
		print("file created")
	except FileExistsError:
		print("tsv file could not be created")
		exit(1)

	curr_card = ""
	for i in range(len(words)):
		curr_card = words[i] + '\t' + sentences[i] + '\t' + defs[i] + "\n"
		outfile.write(curr_card)
		curr_card = ""
	
	outfile.close()
	
main()
