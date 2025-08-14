# John Wesley Thompson
# Created: 8/12/2025
# sentence_generator.py

import card_file_manager as cfm
import re
from openai import OpenAI
import os

PROMPT_HEADER = '''
Hello! I'm going to provide you with a list of words in Japanese.\n
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
Here is the list, and thank you!:\n
'''


def initGPTClient():
    try:
        client = OpenAI(
            api_key = os.getenv("OPENAI_API_KEY")
        )   
    except Exception as e:
        print(f"Error initializing gpt client: {e}")
        exit(1)

    return client


def promptChatGPT(client, model, vocab):
    vocab = ['\u3000'.join(word) if word[0] else word[1] for word in vocab]
    vocab_text = '\n'.join(vocab)

    full_prompt = PROMPT_HEADER + vocab_text
    chat_completion = client.chat.completions.create(
        messages = [{
            "role":"user",
            "content":full_prompt
        }],
        model = model
    )

    sentences = chat_completion.choices[0].message.content.split('\n')

    # this makes a list of strings of 2 exampel sentences
    new_sentences = []
    for i in range(len(sentences)):
        if re.search(r"\d+\.", sentences[i]): 
            sentence_group = '\n'.join(sentences[i + 1: i + 4])
            new_sentences.append(sentence_group)

    return new_sentences


if __name__ == "__main__":

    gpt_client = initGPTClient()
    cfm.initConfigFile()
    file_manager = cfm.CardFileManager()
    model = file_manager.getConfig("OPENAI_MODEL")

    vocab = (("図書館", "としょかん"), ("割り勘", "わりかん"), ("", "テスト"))
    sentences = promptChatGPT(gpt_client, model, vocab)
    print(sentences)