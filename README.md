# Anki Japanese Flash Card Generator
A CLI tool that generates Anki packages files containing vocabulary and example sentence audio, ready for Anki. Built to automate manual Anki card creation and to support intense vocabulary study workflows.

### Bookmarks
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Technical Decisions](#design-decisions)
- [Future Improvements](#future-improvements)

## **Features**
- Provides easily usable CLI interface for generating cards
- Generates apkg files ready for Anki import
- Automatically gathers dictionary definitions from JMdict (the same data jisho.org uses)
- Generates example sentences using the OpenAI API
- Generates audio for vocabulary and example sentences
- Uses a custom SQLite database for fast dictionary lookups
- Supports both standard Python and Docker workflows

### Overview
```text
Input:

単語 たんご
言葉 ことば
語彙 ごい
リンゴ

Command:
createcards generate input.txt output.apkg

Output:
- output.apkg
- word audio files
- sentence audio files
```

## **Tech Stack**
<img align="left" height="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" />
<img align="left" height="35px" src="attachments/openai.png"/>
<img align="left" height="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/sqlite/sqlite-original.svg" />
<img align="left" height="40px" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/docker/docker-original-wordmark.svg" />

<br><br>

Languages: Python, SQLite

APIs: gTTS (Google Text-to-Speech), OpenAI API

DevOps: Docker

## Architecture
The application is organized into several stages:

1. **Input Processing**
    - Reads user-provided text file
    - Validates file formats and command-line arguments

2. **Data Gathering**
    - SQLite reading, spelling, and definition lookups
    - OpenAI sentence generation
    - Google TTS generates audio for words and sentences

3. **Card Compilation**
    - Creates a list of flash card objects with previously gathered data

4. **Output**
    - Anki package file containing the compiled notes
    - Google TTS output audio mp3 files

## **Installation & Setup**

### Standard Install
Download it straight from git using pip:
```bash
pip install git+https://github.com/Just-John-44/Anki-Japanese-Flash-Card-Generator.git
```

Create the SQLite database for card generation with this command:
```bash
# ! This will download a large dictionary file as an intermediate step via ftp.
createcards setup
```

Next, add your OpenAI API key to your system environment as the following variable:

```bash
OPENAI_API_KEY="insert your api key here"
```

### Docker
Pull the container and setup the program with the following commands:

```bash
docker pull justjohn44/createcards:latest
```

```bash
# sets up the database for all generate commands
docker run -it \
-v $(pwd)/data:/app/data \
justjohn/createcards:latest setup
```

## **Usage**

### For Standard Install
The createcards script takes two possible commands, one of which you have already run (`setup`). The other command is `generate` and it takes a text (.text or .txt) file and an apkg file as arguments. This is how it's used:

```bash
createcards generate inputfile.txt outputfile.apkg
```

### For Docker Container
Run the container with the following command:

```bash
# Generates an apkg file and mp3 files from the words in example.text
docker run -it \
  -e OPENAI_API_KEY=sk-xxxxx \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/test.txt:/app/test.txt \
  -v $(pwd)/myfile.apkg:/app/myfile.apkg \
  justjohn44/createcards:latest generate example.text myfile.apkg
```
### Input & Output
The expected format for input is a text file containing entries of a word's spelling and a word's reading. If the word doesn't have a spelling, then the reading should only be written once. There should be no case where a spelling exists without a reading, and the program will ask the user to fix any entries that do. Each entry should be on its own line with the spelling and reading separated by whitespace. Empty lines are not allowed. Here is an example:

**inputfile.txt**
```
単語　たんご
言葉　ことば
語彙　ごい
リンゴ
```

After the `generate` command is run, the createcards will display on the terminal what its current process is, and it will generate am apkg file and two mp3 files for each entry in inputfile.txt. One for sentences and one for the word itself. After that, they can be imported into anki and used to populate any kind of note that the user likes.

## **Technical Decisions**
- With storage and efficiency in mind, createcards is designed with a SQLite database that is created once during setup. The files that the database are built from are quite large, so they're deleted after the database is built to save storage.

- Data is gathered from multiple sources, so the service classes FlashCardService and SetupService were implemented as a separate layer to handle data flow. This solved the "Who handles this data?", and class dependency issues that were apparent beforehand and enforced better separation of concerns.

## **Future Improvements**
Though the program is functional as is, I would like to add the following features to improve user experience:

- Addition of command line arguments and a personal config that allow the user to specify what data they want inlcuded in their flash cards

- Implementation of the genanki Python module to bundle flash card data and audio files into a single package, using Anki's native structure

- Usage of the tags that the OpenAI client generate for cards (at the moment, they are discarded)

<br>

[Back to top](#anki-flash-card-generator)