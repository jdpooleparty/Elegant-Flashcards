import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

FLASHCARDS_DIR = "Flashcards"

class Flashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __repr__(self):
        return f'Q: {self.question}, A: {self.answer}'

class FlashcardDeck:
    def __init__(self):
        self.cards = []

    def load_from_files(self, files):
        """Load flashcards from selected JSON files."""
        self.cards = []
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        if 'question' in item and 'answer' in item:
                            self.cards.append(Flashcard(item['question'], item['answer']))
            except Exception as e:
                messagebox.showerror("Error", f"Could not load flashcards from {file}: {e}")

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

        # Ensure Flashcards directory exists
        if not os.path.exists(FLASHCARDS_DIR):
            os.makedirs(FLASHCARDS_DIR)

        # Set up the main window (increased size)
        self.root.title("Flashcard App")
        self.root.geometry("600x400")

        # Add buttons to the main window
        self.add_button = tk.Button(self.root, text="Load Flashcards", command=self.load_flashcards)
        self.add_button.pack(pady=10)

        self.view_button = tk.Button(self.root, text="View Flashcards", command=self.view_flashcards_window)
        self.view_button.pack(pady=10)

        self.quiz_button = tk.Button(self.root, text="Quiz Yourself", command=self.quiz_options_window)
        self.quiz_button.pack(pady=10)

        self.reload_button = tk.Button(self.root, text="Reload Flashcards", command=self.reload_flashcards)
        self.reload_button.pack(pady=10)

    def load_flashcards(self):
        """Allow the user to select one or more JSON files from the Flashcards directory."""
        files = filedialog.askopenfilenames(
            title="Select Flashcards",
            filetypes=[("JSON files", "*.json")],
            initialdir=FLASHCARDS_DIR
        )

        if files:
            self.deck.load_from_files(files)
            messagebox.showinfo("Success", f"Loaded {len(self.deck.cards)} flashcards.")
        else:
            messagebox.showwarning("No Files", "No flashcards were selected.")

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

        # Static button container
        button_frame = tk.Frame(self.quiz_window)
        button_frame.pack(pady=10)

        self.show_question_or_answer()

        self.next_button = tk.Button(button_frame, text="Next", command=self.next_card)
        self.next_button.grid(row=0, column=1, padx=10)

        self.show_answer_button = tk.Button(button_frame, text="Show Answer", command=self.show_answer_or_question)
        self.show_answer_button.grid(row=0, column=0)

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
        if hasattr(self, 'label'):
            self.label.config(text=display_text)
        else:
            self.label = tk.Label(self.quiz_window, text=display_text)
            self.label.pack(pady=10)

    def show_answer_or_question(self):
        """Display the answer (or question if in AtoQ mode)."""
        self.label.config(text=f"Answer: {self.next_text}" if self.mode == 'QtoA' else f"Question: {self.next_text}")
        self.show_answer_button.config(state='disabled')

    def next_card(self):
        """Move to the next flashcard."""
        self.current_card_idx += 1
        if self.current_card_idx < len(self.quiz_cards):
            self.show_answer_button.config(state='normal', text="Show Answer" if self.mode == 'QtoA' else "Show Question")
            self.show_question_or_answer()  # Show the next card
        else:
            messagebox.showinfo("Quiz Completed", "You've gone through all the flashcards!")
            self.quiz_window.destroy()

    def reload_flashcards(self):
        """Reload flashcards from the selected JSON files."""
        self.load_flashcards()



# Uncomment the following to run the app in a Python environment
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
