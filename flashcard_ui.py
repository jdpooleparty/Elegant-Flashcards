import tkinter as tk
from tkinter import ttk
import os
import random
from tkinterdnd2 import DND_FILES, TkinterDnD

class FlashcardUI(TkinterDnD.Tk):
    def __init__(self, flashcard_deck):
        super().__init__()
        self.title("Advanced Flashcard App")
        self.geometry("800x600")
        self.deck = flashcard_deck

        # Define color scheme
        self.bg_color = "#E6F3FF"  # A lovely shade of light blue
        self.accent_color = "#4a90e2"
        self.text_color = "#333333"

        # Initialize category_colors dictionary
        self.category_colors = {}

        self.configure(bg=self.bg_color)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.map('TButton', background=[('active', '#3a7ac2')])
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TNotebook', background=self.bg_color)
        self.style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.text_color)

        self.setup_ui()
        self.bind_hotkeys()
        self.load_json_files()

        # Start scanning for new flashcards
        self.scan_for_new_flashcards()

        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.drop_file)

    def setup_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.main_frame = ttk.Frame(self.notebook)
        self.quiz_frame = ttk.Frame(self.notebook)
        self.stats_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text="Main")
        self.notebook.add(self.quiz_frame, text="Quiz")
        self.notebook.add(self.stats_frame, text="Stats")

        self.setup_main_frame()
        self.setup_quiz_frame()
        self.setup_stats_frame()

    def setup_main_frame(self):
        self.file_listbox = tk.Listbox(self.main_frame, width=70, height=10, bg=self.bg_color, fg=self.text_color)
        self.file_listbox.pack(pady=10)
        self.file_listbox.bind('<<ListboxSelect>>', self.load_selected_file)

        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.main_frame, textvariable=self.category_var, state="readonly")
        self.category_combobox.pack(pady=10)
        self.category_combobox.bind("<<ComboboxSelected>>", self.update_card_list)

        self.card_listbox = tk.Listbox(self.main_frame, width=70, height=20, bg=self.bg_color, fg=self.text_color)
        self.card_listbox.pack(pady=10)
        self.card_listbox.bind('<Return>', self.show_selected_card)

        add_button = ttk.Button(self.main_frame, text="Add New Card", command=self.add_new_card)
        add_button.pack(pady=10)

    def setup_quiz_frame(self):
        self.quiz_label = ttk.Label(self.quiz_frame, text="", wraplength=700, font=("Arial", 14))
        self.quiz_label.pack(expand=True, fill="both", padx=20, pady=20)

        button_frame = ttk.Frame(self.quiz_frame)
        button_frame.pack(pady=10)

        self.prev_button = ttk.Button(button_frame, text="Previous (←)", command=self.prev_card)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.flip_button = ttk.Button(button_frame, text="Flip (Space)", command=self.flip_card)
        self.flip_button.grid(row=0, column=1, padx=5)

        self.next_button = ttk.Button(button_frame, text="Next (→)", command=self.next_card)
        self.next_button.grid(row=0, column=2, padx=5)

        self.start_quiz_button = ttk.Button(self.quiz_frame, text="Start Quiz", command=self.start_quiz)
        self.start_quiz_button.pack(pady=10)

        self.continuous_var = tk.BooleanVar()
        self.continuous_check = ttk.Checkbutton(self.quiz_frame, text="Continuous Mode", variable=self.continuous_var)
        self.continuous_check.pack(pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.quiz_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=10)

        difficulty_frame = ttk.Frame(self.quiz_frame)
        difficulty_frame.pack(pady=10)
        
        for i in range(1, 6):
            btn = ttk.Button(difficulty_frame, text=str(i), width=3, command=lambda x=i: self.set_difficulty(x))
            btn.pack(side=tk.LEFT, padx=2)

    def setup_stats_frame(self):
        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD, width=70, height=20, bg=self.bg_color, fg=self.text_color)
        self.stats_text.pack(pady=10)

        refresh_button = ttk.Button(self.stats_frame, text="Refresh Stats", command=self.update_stats)
        refresh_button.pack(pady=10)

    def bind_hotkeys(self):
        self.bind('<Left>', lambda event: self.prev_card())
        self.bind('<Right>', lambda event: self.next_card())
        self.bind('<space>', lambda event: self.flip_card())
        self.bind('<Control-q>', lambda event: self.quit())

        # Unbind space from all buttons to prevent default behavior
        for child in self.winfo_children():
            if isinstance(child, ttk.Button):
                child.unbind('<space>')

    def load_json_files(self):
        self.file_listbox.delete(0, tk.END)
        for file in os.listdir("Flashcards"):
            if file.endswith('.json'):
                self.file_listbox.insert(tk.END, file)

    def load_selected_file(self, event):
        selected_indices = self.file_listbox.curselection()
        if selected_indices:
            selected_file = self.file_listbox.get(selected_indices[0])
            file_path = os.path.join("Flashcards", selected_file)
            self.deck.load_from_file(file_path)
            self.update_category_combobox()
            self.update_card_list()

    def update_category_combobox(self):
        categories = list(self.deck.categories)
        self.category_combobox['values'] = categories
        if categories:
            self.category_combobox.set(categories[0])
            self.generate_category_colors(categories)

    def generate_category_colors(self, categories):
        for category in categories:
            if category not in self.category_colors:
                self.category_colors[category] = f"#{random.randint(0, 0xFFFFFF):06x}"

    def update_card_list(self, event=None):
        selected_category = self.category_var.get()
        self.card_listbox.delete(0, tk.END)
        for card in self.deck.get_cards_by_category(selected_category):
            self.card_listbox.insert(tk.END, f"Q: {card.question}")
            self.card_listbox.itemconfigure(tk.END, {'bg': self.category_colors[selected_category]})

    def add_new_card(self):
        # Implement a new window to add a card
        pass

    def start_quiz(self):
        self.quiz_cards = self.deck.cards.copy()
        random.shuffle(self.quiz_cards)
        self.current_card_idx = 0
        self.showing_question = True
        self.show_current_card()

    def show_current_card(self):
        if self.quiz_cards:
            card = self.quiz_cards[self.current_card_idx]
            if self.showing_question:
                self.quiz_label.config(text=f"Question: {card.question}", foreground=self.accent_color)
            else:
                self.quiz_label.config(text=f"Answer: {card.answer}", foreground=self.text_color)
            progress = (self.current_card_idx + 1) / len(self.quiz_cards) * 100
            self.progress_var.set(progress)
        else:
            self.quiz_label.config(text="No flashcards loaded for the quiz.", foreground=self.text_color)

    def flip_card(self):
        self.showing_question = not self.showing_question
        self.show_current_card()

    def next_card(self):
        if self.current_card_idx < len(self.quiz_cards) - 1:
            self.current_card_idx += 1
        elif self.continuous_var.get():
            self.current_card_idx = 0
        else:
            return
        self.showing_question = True
        self.show_current_card()

    def prev_card(self):
        if self.current_card_idx > 0:
            self.current_card_idx -= 1
        elif self.continuous_var.get():
            self.current_card_idx = len(self.quiz_cards) - 1
        else:
            return
        self.showing_question = True
        self.show_current_card()

    def update_stats(self):
        stats = f"Total Cards: {len(self.deck.cards)}\n\n"
        stats += "Cards per Category:\n"
        for category in self.deck.categories:
            count = len(self.deck.get_cards_by_category(category))
            stats += f"{category}: {count}\n"
        
        stats += "\nCards per Difficulty:\n"
        for difficulty in range(1, 6):
            count = len(self.deck.get_cards_by_difficulty(difficulty))
            stats += f"Difficulty {difficulty}: {count}\n"

        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert(tk.END, stats)
        self.stats_text.tag_configure("bold", font=("Arial", 10, "bold"))
        self.stats_text.tag_add("bold", "1.0", "1.end")
        self.stats_text.tag_add("bold", "3.0", "3.end")
        self.stats_text.tag_add("bold", "1.0 + 4 lines", "1.0 + 4 lines lineend")

    def show_selected_card(self, event=None):
        selected_indices = self.card_listbox.curselection()
        if selected_indices:
            selected_card = self.deck.get_cards_by_category(self.category_var.get())[selected_indices[0]]
            self.show_card_details(selected_card)

    def show_card_details(self, card):
        details_window = tk.Toplevel(self)
        details_window.title("Card Details")
        details_window.geometry("400x300")
        
        question_label = ttk.Label(details_window, text=f"Question: {card.question}", wraplength=380)
        question_label.pack(pady=10)
        
        answer_label = ttk.Label(details_window, text=f"Answer: {card.answer}", wraplength=380)
        answer_label.pack(pady=10)
        
        category_label = ttk.Label(details_window, text=f"Category: {card.category}")
        category_label.pack(pady=5)
        
        difficulty_label = ttk.Label(details_window, text=f"Difficulty: {card.difficulty}")
        difficulty_label.pack(pady=5)

    def drop_file(self, event):
        file_path = event.data
        if file_path.endswith('.json'):
            self.deck.load_from_file(file_path)
            self.update_category_combobox()
            self.update_card_list()
            self.file_listbox.insert(tk.END, os.path.basename(file_path))

    def set_difficulty(self, difficulty):
        if self.quiz_cards:
            current_card = self.quiz_cards[self.current_card_idx]
            current_card.difficulty = difficulty
            self.next_card()

    def scan_for_new_flashcards(self):
        current_files = set(self.file_listbox.get(0, tk.END))
        flashcard_files = set(file for file in os.listdir("Flashcards") if file.endswith('.json'))
        
        new_files = flashcard_files - current_files
        for file in new_files:
            self.file_listbox.insert(tk.END, file)
        
        # Schedule the next scan
        self.after(5000, self.scan_for_new_flashcards)