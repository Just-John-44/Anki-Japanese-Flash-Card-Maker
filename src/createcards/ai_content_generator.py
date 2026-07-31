# ai_content_generator.py
# Created: 8/12/2025
# Last Edited: 7/30/2026
# Author: John Wesley Thompson

from createcards.ccnote import Word

import json
from openai import OpenAI
from dotenv import load_dotenv
import os


PROMPT_HEADER = '''
I'm going to provide you a list of words in Japanese.
For each word, please generate 2 example sentences and if applicable,
tell me if the word belongs to any of the following tags:

Register:
Casual, Neutral, Polite, Formal, Very Formal, Honorific, Humble, Business,
Literary, Old-fashioned, Slang, Masculine, Feminine, Childish, Vulgar

Context/Domain:
Academic, Professional, Legal, Medical, Technical, Scientific, Computing/IT,
Engineering, Financial, Government, Military, Religious, Historical, Educational,
News, Internet, Social Media, Gaming, Anime/Manga, Sports, Travel, Food, Family,
Romance, Daily Life

Frequency:
Common, Uncommon

Situational:
Mostly Spoken, Mostly Written, Conversational, Public Speaking, Customer Service,
Email, Texting, Telephone, Workplace, Classroom

please do so in the following json format:

Use the exact input word as the JSON key.
Do not normalize, modify, reorder, or omit any words.
Return one object entry for every word provided.

{
    "word1": {
        "s1": "insert first generated sentence here for word 1.",
        "s2": "insert second generated sentence here for word 1.",
        "tags": "tag1・tag2・tag3・..."
    },
    "word2": {
        ...
        ...
        ...
    },
    ...
}


'''

IDEOGRAPHIC_SPACE = '\u3000'

load_dotenv()

class OpenAIContentGenerator:
    def __init__(
        self, 
        client=None, 
        model: str="gpt-4o-mini"
    ):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY")

        self.model = model
        self.client = OpenAI(api_key=api_key) if client is None else client

    def generate_content(self, vocab: list[Word]) -> tuple[list[str], list[str]]:
        '''Generates sentences using the OpenAI API'''
        if not vocab:
            raise ValueError("No vocab provided")

        if (self.client is None):
            raise ValueError("Cannot generate sentences without a valid client")

        vocab_strings = [IDEOGRAPHIC_SPACE.join(word) if word[0] else word[1] for word in vocab]
        vocab_text = '\n'.join(vocab_strings)

        full_prompt = PROMPT_HEADER + vocab_text
        chat_completion = self.client.chat.completions.create(
            model = self.model,
            messages = [
            {
                "role": "system",
                "content": "Return output in json only. No explanation. No markdown"
            },
            {
                "role": "user",
                "content": full_prompt
            }]
        )

        response_text = chat_completion.choices[0].message.content

        try:
            if isinstance(response_text, str):
                data = json.loads(response_text)
            else:
                raise ValueError("OpenAI returned a value that's not a string")

        except json.JSONDecodeError:
            print("OpenAI returned an invalid response.")
            raise

        if not isinstance(data, dict):
            raise ValueError("OpenAI did not return json object (may have returned a list, etc.)")

        if len(data) != len(vocab):
            raise RuntimeError("OpenAI output inconsistent with input")

        sentences = []
        tags = []
        for word in vocab_strings:
            try:
                entry = data[word]
                sentences.append(entry["s1"] + "<br>" + entry["s2"])
                tags.append(entry["tags"])

            except KeyError:
                print("OpenAI returned incorrect schema")
                raise

        return sentences, tags
