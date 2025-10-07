# John Wesley Thompson
# Created: 8/9/2025
# flashcard.py

class FlashCard:
    def __init__(self, word):
        self.writing = word[0]
        self.kana = word[1]
        self.definition = ""
        self.sentences = ""
        self.word_audio_filepath = ""
        self.sentence_audio_filepath = ""


    def __repr__(self):
        if self.writing:
            word = f"{self.writing}\u3000{self.kana}"
        else:
            word = f"{self.kana}"

        return ("--------------------\n"
            f"{word}\n"
            f"{self.definition}\n"
            f"{self.sentences}\n"
            f"{self.word_audio_filepath}\n"
            f"{self.sentence_audio_filepath}\n"
            "--------------------\n")


    def csv_string(self):
        word = f"{self.writing}\u3000{self.kana}" if self.writing else self.kana

        csv_string = (f"{word},{self.definition},"
            f"{self.sentences},[sound:{self.word_audio_filepath}],"
            f"{self.sentence_audio_filepath}\n")

        return csv_string.replace('\n', "<br>")

    def missingFields(self):
        # card can have no kanji if it has kana
        if (self.writing == "" and self.kana == "" or 
            self.kana == "" or
            self.definition == "" or
            self.sentences == "" or
            self.word_audio_filepath == "" or
            self.sentence_audio_filepath == ""):
            return True

        return False


    def addPitch(self):
        pass


if __name__ == "__main__":

    both = FlashCard(("図書館", "としょかん"))
    nokanji = FlashCard(("", "こんにちは"))


    print(f"both: \n{both}")
    print(f"nokanji: \n{nokanji}")
    print("csv:")
    print(both.csv_string())
    print(nokanji.csv_string())

    print(f"'both' missing fields: {both.missingFields()}")
    print(f"'nokanji' missing fields: {nokanji.missingFields()}")

    both.definition = "library"
    both.sentences = "これはテストだ"
    both.audio_filepath = "ttsSounds/notreal/filepath"

    nokanji.definition = "hello"
    nokanji.sentences = "これもテスト"
    nokanji.audio_filepath = "ttsSounds/fake/filepath"

    print("with other members")
    print(f"both: \n{both}")
    print(f"nokanji: \n{nokanji}")
    print("csv:")
    print(both.csv_string())
    print(nokanji.csv_string())

    print(f"'both' missing fields: {both.missingFields()}")
    print(f"'nokanji' missing fields: {nokanji.missingFields()}")