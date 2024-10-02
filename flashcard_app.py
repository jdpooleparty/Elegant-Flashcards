import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

FLASHCARD_FILE = "flashcards.json"

class Flashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __repr__(self):
        return f'Q: {self.question}, A: {self.answer}'

class FlashcardDeck:
    def __init__(self, json_file=FLASHCARD_FILE):
        self.cards = []
        self.json_file = json_file
        self.load_flashcards()

    def load_flashcards(self):
        """Load flashcards from the JSON file."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.cards = [Flashcard(item['question'], item['answer']) for item in data]
            except Exception as e:
                messagebox.showerror("Error", f"Could not load flashcards: {e}")
        else:
            # If the file doesn't exist, initialize an empty file
            with open(self.json_file, 'w') as file:
                json.dump([], file)

    def save_flashcards(self):
        """Save all flashcards to the JSON file."""
        with open(self.json_file, 'w', encoding='utf-8') as file:
            data = [{'question': card.question, 'answer': card.answer} for card in self.cards]
            json.dump(data, file, indent=4)

    def add_flashcard(self, question, answer):
        """Add a new flashcard to the deck and save it to the JSON file."""
        card = Flashcard(question, answer)
        self.cards.append(card)
        self.save_flashcards()

    def view_flashcards(self):
        """Return all flashcards."""
        return self.cards

    def quiz(self):
        """Return all flashcards for quizzing."""
        return self.cards

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.deck = FlashcardDeck()

        # Set up the main window
        self.root.title("Flashcard App")
        self.root.geometry("400x300")

        # Add buttons to the main window
        self.add_button = tk.Button(self.root, text="Add Flashcard", command=self.add_flashcard_window)
        self.add_button.pack(pady=10)

        self.view_button = tk.Button(self.root, text="View Flashcards", command=self.view_flashcards_window)
        self.view_button.pack(pady=10)

        self.quiz_button = tk.Button(self.root, text="Quiz Yourself", command=self.quiz_options_window)
        self.quiz_button.pack(pady=10)

        self.import_button = tk.Button(self.root, text="Reload Flashcards", command=self.reload_flashcards)
        self.import_button.pack(pady=10)

    def add_flashcard_window(self):
        """Open a window to add a new flashcard."""
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Add Flashcard")

        question_label = tk.Label(self.new_window, text="Question:")
        question_label.pack(pady=5)
        self.question_entry = tk.Entry(self.new_window, width=50)
        self.question_entry.pack(pady=5)

        answer_label = tk.Label(self.new_window, text="Answer:")
        answer_label.pack(pady=5)
        self.answer_entry = tk.Entry(self.new_window, width=50)
        self.answer_entry.pack(pady=5)

        add_button = tk.Button(self.new_window, text="Add", command=self.add_flashcard)
        add_button.pack(pady=10)

    def add_flashcard(self):
        """Add a flashcard to the deck and save it to the JSON file."""
        question = self.question_entry.get()
        answer = self.answer_entry.get()

        if question and answer:
            self.deck.add_flashcard(question, answer)
            messagebox.showinfo("Success", "Flashcard added successfully!")
            self.new_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Please enter both a question and an answer.")

    def view_flashcards_window(self):
        """Open a window to view all flashcards."""
        self.view_window = tk.Toplevel(self.root)
        self.view_window.title("View Flashcards")

        cards = self.deck.view_flashcards()
        if not cards:
            messagebox.showinfo("No Cards", "No flashcards to display.")
            self.view_window.destroy()
            return

        for idx, card in enumerate(cards, start=1):
            label = tk.Label(self.view_window, text=f"{idx}. Q: {card.question}, A: {card.answer}")
            label.pack(pady=2)

    def quiz_options_window(self):
        """Open a window to select quiz options (Question → Answer or Answer → Question)."""
        self.option_window = tk.Toplevel(self.root)
        self.option_window.title("Quiz Options")

        label = tk.Label(self.option_window, text="Select quiz type:")
        label.pack(pady=10)

        question_to_answer_button = tk.Button(self.option_window, text="Question → Answer", command=lambda: self.quiz_window('QtoA'))
        question_to_answer_button.pack(pady=5)

        answer_to_question_button = tk.Button(self.option_window, text="Answer → Question", command=lambda: self.quiz_window('AtoQ'))
        answer_to_question_button.pack(pady=5)

    def quiz_window(self, mode):
        """Open a window to quiz the user. Mode determines if it's Q->A or A->Q."""
        cards = self.deck.quiz()
        if not cards:
            messagebox.showinfo("No Cards", "No flashcards available to quiz.")
            return

        self.quiz_window = tk.Toplevel(self.root)
        self.quiz_window.title("Quiz")

        self.current_card_idx = 0
        self.quiz_cards = cards
        self.mode = mode  # QtoA or AtoQ

        self.show_question_or_answer()

        self.next_button = tk.Button(self.quiz_window, text="Next", command=self.next_card)
        self.next_button.pack(pady=10)

    def show_question_or_answer(self):
        """Display either the question or the answer based on the mode and current card."""
        card = self.quiz_cards[self.current_card_idx]
        if self.mode == 'QtoA':
            self.current_text = card.question
            self.next_text = card.answer
            display_text = f"Question: {self.current_text}"
        else:
            self.current_text = card.answer
            self.next_text = card.question
            display_text = f"Answer: {self.current_text}"

        # Show the current question/answer
        self.label = tk.Label(self.quiz_window, text=display_text)
        self.label.pack(pady=10)

        self.show_answer_button = tk.Button(self.quiz_window, text="Show Answer" if self.mode == 'QtoA' else "Show Question", command=self.show_answer_or_question)
        self.show_answer_button.pack(pady=10)

    def show_answer_or_question(self):
        """Display the answer (or question if in AtoQ mode)."""
        self.label.config(text=f"Answer: {self.next_text}" if self.mode == 'QtoA' else f"Question: {self.next_text}")
        self.show_answer_button.destroy()  # Remove the "Show Answer/Question" button after it's clicked

    def next_card(self):
        """Move to the next flashcard."""
        self.current_card_idx += 1
        if self.current_card_idx < len(self.quiz_cards):
            self.label.destroy()  # Remove the previous question/answer label
            self.show_question_or_answer()  # Show the next card
        else:
            messagebox.showinfo("Quiz Completed", "You've gone through all the flashcards!")
            self.quiz_window.destroy()

    def reload_flashcards(self):
        """Reload flashcards from the JSON file."""
        self.deck.load_flashcards()
        messagebox.showinfo("Reloaded", "Flashcards reloaded from JSON file.")



# Uncomment the following to run the app in a Python environment
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
