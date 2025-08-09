# John Wesley Thompson
# Created: 7/10/2025
# Last Edited: 7/10/2025
# pitch_accent_adder.py

# This program makes ading pitch accent to my cards much easier.
# It should be able to send me a comma separated list of the words
# on my list via email so i can easily paste the words into the 
# shirabe jisho phone app. (the only one i trust for pitch accents)
# after that it will be an interface for adding the pitch accent marks

import sys
import smtplib
from email.mime.text import MIMEText

DEFAULT_FILE_PATH = "../../単語/"

def main():

	argc = len(sys.argv)
	if argc != 2:
		print("---enter only a file name---")
		exit(1)

	filename = DEFAULT_FILE_PATH + sys.argv[1]

	try:
		infile = open(filename, "r")
	except FileNotFoundError:
		print(f"---file '{filename}' not found---")
		exit(1)

	file_contents = infile.readlines()
	if file_contents[0] != "WORDS\n":
		print("---expected 'WORDS' at beginning of file---")
		exit(1)

	words = ""
	while i in file_contents != "DEFINITIONS\n":
		words += i + ','

	print(words)
	sender_email = "jwthompson121@gmail.com"
	receiver_email = "jwthompson121@gmail.com"
	password = "$n00py20"
	subject = "todays vocab"

main()
