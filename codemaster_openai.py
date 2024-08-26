from players.codemaster import Codemaster  # Import the Codemaster class
from dotenv import load_dotenv
import openai
import os
import time

class AICodemaster(Codemaster):
    def __init__(self, brown_ic=None, glove_vecs=None, word_vectors=None):
        super().__init__()
        load_dotenv()
        self.openai_key = os.getenv('OPENAI_KEY')  
        openai.api_key = self.openai_key

    def set_game_state(self, words, maps):
        self.words = words
        self.maps = maps

    def get_clue(self):
        codemaster_prompt = f"""
        You are a codemaster in the game Codenames. Your task is to provide a clue word that is semantically similar to as many 'Red' words as possible while avoiding words similar to 'Blue' and especially 'Assassin' words.

        Here is the list of 25 words on the board:
        <words>
        {self.words}
        </words>

        And here are their corresponding mappings:
        <mappings>
        {self.maps}
        </mappings>

        Your goal is to find a clue word that is semantically similar to as many 'Red' words as possible. The number of 'Red' words your clue relates to is your score. However, you must be careful:

        1. Avoid words similar to 'Blue', as they could help the opposing team.
        2. Absolutely avoid words similar to 'Assassin', as guessing this word results in an immediate loss.
        3. Words mapped to 'Civilian' are neutral, so they are less critical to avoid than 'Blue' or 'Assassin' words.

        Follow these steps:
        1. Analyze the words and their mappings.
        2. Identify the 'Red' words.
        3. Look for semantic connections between multiple 'Red' words.
        4. Consider potential clue words that relate to multiple 'Red' words.
        5. Evaluate each potential clue word to ensure it doesn't strongly relate to 'Blue' or 'Assassin' words.
        6. Choose the best clue word that maximizes the number of related 'Red' words while minimizing risk.

        Provide your response in the following format:
        <thinking>
        [Your thought process, including consideration of different options and why you chose your final clue word]
        </thinking>
        <answer>
        Clue word: [Your chosen clue word]
        Number: [The number of 'Red' words your clue relates to]
        Explanation: [Brief explanation of which 'Red' words your clue relates to and why you chose this clue]
        </answer>

        Important reminders:
        - Never include civilian words with red words in your count.
        - Ensure your clue word is not on the board or a variation of a word on the board.
        - Your clue must be a single word in English.
        - Avoid proper nouns unless they are common knowledge.
        - If a word contains a '*' character, it is a placeholder for a word that should not be guessed.
        - Never return a number higher than the number of unguessed red words (guessed red words are marked as *Red* in the word list).
        - Whenever you evaluate a potential clue word, always consider the risk of leading your team to 'Blue' or 'Assassin' words.
        """
        
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     max_tokens=1000,
        #     temperature=0,
        #     messages=[
        #         {"role": "system", "content": "This prompt will be used in a python script in a function whenever the AI Codemaster has get_clue called."},
        #         {"role": "user", "content": codemaster_prompt}
        #     ]
        # )

        response = self.get_openai_response(codemaster_prompt)


        # Extract the content from the response
        message_content = response['choices'][0]['message']['content']
        print(message_content)

        # Parse the message content to get the clue word and number
        clue_word, number = self.parse_answer(message_content)
        
        return clue_word, number

    def get_openai_response(self, prompt):
        """Handle OpenAI API rate limit by retrying after a delay."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Replace with the correct OpenAI model name
                max_tokens=1000,
                temperature=0,
                messages=[
                    {"role": "system", "content": "This prompt will be used in a python script in a function whenever the AI Codemaster has get_clue called."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response
        except openai.error.RateLimitError:
            print("Rate limit reached. Waiting for 20 seconds...")
            time.sleep(20)
            return self.get_openai_response(prompt)  # Retry after waiting

    def parse_answer(self, text):
        try:
            # Ensure that <answer> tags are present
            start = text.find("<answer>") + len("<answer>")
            end = text.find("</answer>")
            if start == -1 or end == -1:
                raise ValueError("Answer tags not found in the response.")

            # Extract the content within <answer> tags
            answer_content = text[start:end].strip()

            # Split the content by lines
            lines = answer_content.split("\n")
            if len(lines) < 2:
                raise ValueError("Expected at least two lines for clue and number.")

            # Extract Clue Word and Number
            clue_word = lines[0].split(": ")[1].strip().replace("[", "").replace("]", "")
            number = int(lines[1].split(": ")[1].strip())

            return clue_word, number
        except (IndexError, ValueError) as e:
            print(f"Error parsing the clue: {e}")
            print(f"Raw AI Response: {text}")
            return "Unknown", 0

# python run_game.py players.codemaster_openai.AICodemaster players.guesser_openai.AIGuesser --seed 3442
# to run script
