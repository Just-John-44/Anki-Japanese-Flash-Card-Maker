# John Wesley Thompson
# Created: 8/9/2025
# flashcard.py

class FlashCard:
    def __init__(self, word):
        self.writing = word[0]
        self.kana = word[1]
        self.definition = ""
        self.sentences = ""
        self.audio_filepath = ""
        

    def __repr__(self):
        if self.writing:
            word = f"{self.writing}\u3000{self.kana}"
        else:
            word = f"{self.kana}"

        return ("--------------------\n"
            f"{word}\n"
            f"{self.definition}\n"
            f"{self.sentences}\n"
            f"{self.audio_filepath}\n"
            "--------------------\n")
    

    # I thought I could use this in the missingFields function but it's not helpful
    # because the function requires a more in depth check
    # def __iter__(self):
    #     yield self.kanji
    #     yield self.kana
    #     yield self.definition
    #     yield self.sentences
    #     yield self.audio_filepath


    def csv_string(self):
        word = f"{self.writing}\u3000{self.kana}" if self.writing else self.kana

        return (f"{word},{self.definition},"
            f"{self.sentences},{self.audio_filepath}\n")


    def missingFields(self):
        # card can have no kanji if it has kana
        if (self.writing == "" and self.kana == "" or 
            self.kana == "" or
            self.definition == "" or
            self.sentences == "" or
            self.audio_filepath == ""):
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