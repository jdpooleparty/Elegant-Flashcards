import tkinter as tk
from tkinter import messagebox, filedialog
import csv
import json

class Flashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __repr__(self):
        return f'Q: {self.question}, A: {self.answer}'

class FlashcardDeck:
    def __init__(self):
        self.cards = []

    def add_flashcard(self, question, answer):
        card = Flashcard(question, answer)
        self.cards.append(card)

    def view_flashcards(self):
        return self.cards

    def quiz(self):
        return self.cards

    def import_from_csv(self, filepath):
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 2:
                        self.add_flashcard(row[0], row[1])
            return True
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return False

    def import_from_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
                for item in data:
                    if 'question' in item and 'answer' in item:
                        self.add_flashcard(item['question'], item['answer'])
            return True
        except Exception as e:
            print(f"Error importing JSON: {e}")
            return False

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

        self.quiz_button = tk.Button(self.root, text="Quiz Yourself", command=self.quiz_window)
        self.quiz_button.pack(pady=10)

        self.import_button = tk.Button(self.root, text="Import Flashcards", command=self.import_flashcards)
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
        """Add a flashcard to the deck."""
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

    def quiz_window(self):
        """Open a window to quiz the user."""
        cards = self.deck.quiz()
        if not cards:
            messagebox.showinfo("No Cards", "No flashcards available to quiz.")
            return

        self.quiz_window = tk.Toplevel(self.root)
        self.quiz_window.title("Quiz")

        self.current_card_idx = 0
        self.correct_answers = 0
        self.total_questions = len(cards)
        self.quiz_cards = cards

        self.question_label = tk.Label(self.quiz_window, text=f"Question: {self.quiz_cards[self.current_card_idx].question}")
        self.question_label.pack(pady=10)

        self.answer_entry = tk.Entry(self.quiz_window, width=50)
        self.answer_entry.pack(pady=5)

        submit_button = tk.Button(self.quiz_window, text="Submit Answer", command=self.check_answer)
        submit_button.pack(pady=10)

    def check_answer(self):
        user_answer = self.answer_entry.get().strip().lower()
        correct_answer = self.quiz_cards[self.current_card_idx].answer.strip().lower()

        if user_answer == correct_answer:
            self.correct_answers += 1

        self.current_card_idx += 1
        if self.current_card_idx < self.total_questions:
            self.question_label.config(text=f"Question: {self.quiz_cards[self.current_card_idx].question}")
            self.answer_entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Quiz Completed", f"You got {self.correct_answers}/{self.total_questions} correct!")
            self.quiz_window.destroy()

    def import_flashcards(self):
        """Prompt the user to import flashcards from CSV or JSON."""
        filetypes = [("CSV files", "*.csv"), ("JSON files", "*.json")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)

        if filepath.endswith(".csv"):
            success = self.deck.import_from_csv(filepath)
        elif filepath.endswith(".json"):
            success = self.deck.import_from_json(filepath)
        else:
            messagebox.showerror("File Error", "Unsupported file type.")
            return

        if success:
            messagebox.showinfo("Success", "Flashcards imported successfully!")
        else:
            messagebox.showerror("Error", "Failed to import flashcards.")

# Uncomment the following to run the app in a Python environment
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
