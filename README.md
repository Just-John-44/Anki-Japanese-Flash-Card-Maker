# Anki Flash Card Maker
A program that creates a tsv file and mp3 files ready to be imported into an Anki deck.

## **About the Project**
---
This project was created to help me create Anki flashcards faster than I could by manually inputting the data. It scrapes jisho.org for card definitions, prompts chat gpt for 2 example sentences, and uses Google text-to-speech for sentence and word audio. It's written entirely in Pyhton, and uses the beautifulsoup, requests, openai, and gtts libraries.
<br><br>

<!-- put icons of language usage here and links to the libraries used. basically the tech stack-->
<img align="left" height="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" />
<img align="left" height="40" src="attachments/beautifulsoup.png"/>
<img align="left" height="40" src="attachments/openai.png"/>
<img align="left" height="40" src="attachments/requests.png"/>
<br><br>


## **Features**
---
+ AI-generated sentences for each word
+ gTTS for each word and sentence
+ Word definitions stright from jisho.org 

## **Requirements and Build**
---

### **macOS/Linux:**
All dependencies are listed in requirements.txt. Do the following to get them downloaded:

```bash
pip install -r requirements.txt
```

Add your openai api key to your system environment. In your shell config, add this line:

```bash
export OPENAI_API_KEY="insert your api key here"
```

### **Docker:**
To create and run a docker container, do the following to build the the image:

```bash
docker build -t your-image-name build/directory/here
```

Next, create and run the container with the following command:

```bash
docker run --rm -it \
-e OPENAI_API_KEY="your api key in quotes" \
-v /directory/to/run/the/container:/app your-image-name /app/your_vocab_input_file.txt
```

- `--rm` deletes the container after its done running
- `-e` specifies the environment vaariables needed for the program
- `-v` mounts your filepath to the filepath in the container


## **How to Use**
---
To use the program after the set up steps, move to the directory that you want to create your flashcard tsv and media files in. I have my directory structure set up like so:
```bash
mainVocabDirectory
├── vocabDirectoryWithDate
│   └── todays_date_words.txt
└── tango_2025-10-10
    └── tango_2025-10-10.txt
```
In your directory, you should have `.txt` a file with a list of words. The format is one word per line, with the word's kanji first and its kana second, separated by a widespace character like so:
```bash
言葉　ことば
単語　たんご
語彙　ごい
```
If the word doesn't have kanji, you should only write its kana on that line (no widespaces).

Once you've moved to your directory that has your vocab list, run the script:
```bash
createcards mv_vocab_list.txt
```

The program will run, displaying what step it is on during the card making process, and will notify you if there are any issues finding definitions. The web scraper is not perfect, and you will have to enter the definitions manually for the ones that it can not find.

Your current directory will have a new tsv file and mp3 files for all of the words on your list. The only thing left to do now is to import them. All of your mp3 files need to be moved to Anki's collection.media folder before you import your tsv file. Find it, and copy or move your mp3 files into it. Lastly, import your tsv file into the Anki app and your done!

