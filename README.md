# Anki-Flash-Card-Maker
This program makes it much easier to make anki cards. It will create a csv file containing a card for each word in the entered list. Each card will have example sentences, jisho definitions, and tts audio.  

## Dependencies
The dependencies used for text to speech functionality are the kokoro tts model and it's dependencies. Do the following to get them downloaded:

```bash
pip install -r requirements.txt
```

## Make it Run!
Add your openai api key to your system environment. In your shell config, add this line:

Linux/macOS: `export OPENAI_API_KEY="insert your api key here"`

Windows: `set OPENAI_API_KEY="your api key"`
