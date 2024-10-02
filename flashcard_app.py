class Flashcard:
    def __init__(self, question, answer):
        """
        Initialize a flashcard with a question and answer.
        """
        self.question = question
        self.answer = answer

    def __repr__(self):
        """
        Representation of a flashcard, showing question and answer.
        """
        return f'Q: {self.question}, A: {self.answer}'


class FlashcardDeck:
    def __init__(self):
        """
        Initialize an empty deck of flashcards.
        """
        self.cards = []

    def add_flashcard(self, question, answer):
        """
        Add a new flashcard to the deck.
        """
        card = Flashcard(question, answer)
        self.cards.append(card)

    def view_flashcards(self):
        """
        View all flashcards in the deck.
        """
        if not self.cards:
            print("No flashcards in the deck.")
        else:
            for idx, card in enumerate(self.cards, 1):
                print(f"{idx}. {card}")

    def quiz(self):
        """
        Quiz the user with flashcards.
        """
        if not self.cards:
            print("No flashcards available to quiz.")
            return

        correct = 0
        for card in self.cards:
            print(f"Question: {card.question}")
            user_answer = input("Your Answer: ")
            if user_answer.strip().lower() == card.answer.strip().lower():
                print("Correct!")
                correct += 1
            else:
                print(f"Wrong! The correct answer is: {card.answer}")
        
        print(f"Quiz Complete! You answered {correct}/{len(self.cards)} correctly.")

def main_menu():
    """
    Main menu to interact with the flashcard app.
    """
    deck = FlashcardDeck()
    
    while True:
        print("\nFlashcard App Menu:")
        print("1. Add Flashcard")
        print("2. View Flashcards")
        print("3. Quiz Yourself")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            question = input("Enter the question: ")
            answer = input("Enter the answer: ")
            deck.add_flashcard(question, answer)
            print("Flashcard added!")
        elif choice == "2":
            deck.view_flashcards()
        elif choice == "3":
            deck.quiz()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please choose again.")

# Uncomment the following line to run the flashcard app in a Python environment
# main_menu()
