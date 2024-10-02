import json
import csv
from flashcard import Flashcard

class FlashcardDeck:
    def __init__(self):
        self.cards = []
        self.categories = set()

    def load_from_file(self, file):
        """Load flashcards from a selected JSON file."""
        self.cards = []
        self.categories = set()
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if 'question' in item and 'answer' in item:
                        category = item.get('category', "General")
                        card = Flashcard(item['question'], item['answer'], category)
                        card.difficulty = item.get('difficulty', 1)
                        self.cards.append(card)
                        self.categories.add(category)
        except Exception as e:
            print(f"Could not load flashcards from {file}: {e}")

    def get_cards_by_category(self, category):
        """Return cards of a specific category."""
        return [card for card in self.cards if card.category == category]

    def get_cards_by_difficulty(self, difficulty):
        """Return cards of a specific difficulty."""
        return [card for card in self.cards if card.difficulty == difficulty]

    def load_from_csv(self, file):
        """Load flashcards from a selected CSV file."""
        self.cards = []
        self.categories = set()
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'question' in row and 'answer' in row:
                        category = row.get('category', "General")
                        card = Flashcard(row['question'], row['answer'], category)
                        card.difficulty = int(row.get('difficulty', 1))
                        self.cards.append(card)
                        self.categories.add(category)
        except Exception as e:
            print(f"Could not load flashcards from {file}: {e}")