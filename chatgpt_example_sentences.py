# John Wesley Thompson
# Created: 7/7/2025
# Last Edited: 7/9/2025
# chatgpt_example_sentences

# This program doesn't work unless you pay for a quota for gpt. I wasted an hour
# doing this. 

# Nevermind its really cheap and i decided to temorarily cancel my crunchyroll 
# subscription

from openai import OpenAI
import os


PROMPT = '''Hello! I'm going to provide you with a list of words in Japanese.\n
            For each word, please generate 2 example sentences and tell me the\n 
            formality level of the word. For the formality, I want to know if\n
            the word is 丁寧語, 尊敬語, casual, etc. Please do this in the\n
            following format: \n\n
            1. word (the second word would be "2. word", and so on)\n
            sentence 1\n
            sentence 2\n
            (formality)\n\n
            please do not stop generating sentences until you have made them\n
            for every word. I'm certain that this is the desired format.\n\n
            Here is the list, and thank you!:\n'''

def main():

    # get words from a file that contains words and their definitions
    filepath = "../../単語/"

    filename = input("enter file name: ")
    filename = filepath + filename

    words = read_words_file(filename)
    
    # set up chat gpt message
    try:
        client = OpenAI(
            api_key = os.getenv("OPENAI_API_KEY")
        )   
    except Exception as e:
        print(f"Error initializing gpt client: {e}")
        exit(1)

    todays_prompt = PROMPT + words    

    print("---generating example sentences via chat gpt---")

    chat_completion = client.chat.completions.create(
        messages = [{
            "role":"user",
            "content":todays_prompt
        }],
        model = "gpt-4o-mini"
    )

    example_sentences = chat_completion.choices[0].message.content

    append_sentences_to_file(filename, example_sentences)

    return


# read_words_file reads the words list from a file containing words and their
# definitions. 
# input: the name of the file to be read
# output: a string of words from the file
def read_words_file(filename):
    
    try:
        infile = open(filename, "r")
    except FileNotFoundError:
        print(f"---file {filename} not found---")
        exit(1)

    file_lines = infile.readlines()
    infile.close()

    if file_lines[0] != "WORDS\n":
        print("---Expected 'WORDS' at beginning of file---")
    else:
        file_lines.pop(0)

    line = 0
    words_str = ""
    while file_lines[line] != "DEFINITIONS\n":
        words_str += file_lines[line]
        line += 1

    return words_str


# append_sentences_to_file appends the sentences created by chat gpt to the
# the file containing definitions and words and adds a sentences header
# input: the name of the file to be opened and a string of sentences to be 
#        appended
def append_sentences_to_file(filename, sentences):

    try:
        outfile = open(filename, "a")
    except FileNotFoundError:
        print("---could not append sentences to file---")
        exit(1)

    outfile.write("\nSENTENCES\n")
    outfile.write(sentences)
    print("---sentences appended to file---")
    outfile.close()


main()