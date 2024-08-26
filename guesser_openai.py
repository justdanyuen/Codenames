from players.guesser import Guesser
from dotenv import load_dotenv
import openai
import os

class AIGuesser(Guesser):
    def __init__(self, brown_ic=None, glove_vecs=None, word_vectors=None):
        super().__init__()
        load_dotenv()
        self.openai_key = os.getenv('OPENAI_KEY')
        openai.api_key = self.openai_key
        self.guesses = []
    
    def set_board(self, words):
        self.words = words
    
    def set_clue(self, clue, num):
        self.new_clue = True
        self.clue = clue
        self.num = num
        print("The clue is:", clue, num)
        li = [clue, num]
        return li

    def keep_guessing(self):
        return len(self.guesses) > 0
    
    def get_answer(self):
        guesser_prompt = f"""
        You are playing as a guesser in the game Codenames. Your task is to identify words from a given list that are most likely associated with a provided clue. Here's how you should proceed:

        First, you will be given a list of 25 words:
        <word_list>
        {self.words}
        </word_list>

        Then, you will receive a clue consisting of a word and a number:
        <clue>
        {self.clue}, {self.num}
        </clue>

        Your task is to analyze the clue and the remaining unguessed words on the board. The clue word is semantically related to one or more words in the list, and the number indicates how many words it is related to.

        To complete this task:

        1. Carefully consider the semantic relationship between the clue word and each unguessed word on the board.
        2. Identify the words that you believe are most strongly related to the clue.
        3. Create a sorted list of words from the word list. The list should contain a number of words equal to the number given in the clue.
        4. Sort this list based on the strength of their semantic relationship to the clue, with the most strongly related word at the end of the list.

        Provide your thoughts and reasoning in the following format:
        <thoughts>
        [Your thought process and reasoning for each word in the provided list]
        </thoughts>

        Your response should be formatted as follows:

        <guesses>
        [Least related word]
        [...]
        [More related word]
        [Most related word]
        </guesses>

        REMINDERS:
        - Only include unguessed words in your list
        - If a word has been guessed it will contain a * and should not be included in your guesses
        - Make sure the number of words in your list of guesses matches exactly the number given in the clue
        - Ensure that all words you return are in the provided word list and are spelled exactly as they appear in the list
        - Words that contain a * are placeholders and should not be guessed
        """
        if self.new_clue:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": guesser_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            self.new_clue = False
            message_content = response['choices'][0]['message']['content']
            print(message_content)
            self.guesses = parse_guesses(message_content)
            print(f'guesses: {self.guesses}')
        
        guess = self.guesses.pop()
        print(f'guess: {guess}')
        return guess


def parse_guesses(text):
    # Find the content within <guesses> tags
    start = text.find("<guesses>") + len("<guesses>")
    end = text.find("</guesses>")
    guesses_content = text[start:end].strip()

    # Split the content by newlines and remove any empty strings
    guesses = [word.strip() for word in guesses_content.split('\n') if word.strip()]

    return guesses
