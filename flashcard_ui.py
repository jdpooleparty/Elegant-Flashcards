import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import random
import json

class FlashcardUI(tk.Tk):
    def __init__(self, flashcard_deck):
        super().__init__()
        self.title("Elegant Flashcard App")
        self.geometry("800x600")  # Increased window size
        self.deck = flashcard_deck

        # Define color scheme
        self.bg_color = "#F0F4F8"
        self.accent_color = "#4A90E2"
        self.text_color = "#333333"

        self.configure(bg=self.bg_color)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.map('TButton', background=[('active', '#3A7AC2')])
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)

        self.known_cards = set()
        self.load_known_cards()

        self.setup_ui()
        self.bind_hotkeys()

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.file_label = ttk.Label(main_frame, text="Select a quiz deck:", font=("Arial", 12))
        self.file_label.pack(pady=10)

        file_frame = ttk.Frame(main_frame)
        file_frame.pack(pady=10)

        # Create a Treeview widget instead of Listbox
        self.file_treeview = ttk.Treeview(file_frame, columns=("File Name", "Card Count"), show="headings", height=10)
        self.file_treeview.heading("File Name", text="File Name")
        self.file_treeview.heading("Card Count", text="Card Count")
        self.file_treeview.column("File Name", width=400)
        self.file_treeview.column("Card Count", width=100, anchor="center")
        self.file_treeview.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_treeview.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        select_file_button = ttk.Button(button_frame, text="Select JSON File", command=self.load_json_file)
        select_file_button.pack(side=tk.LEFT, padx=5)

        self.start_quiz_button = ttk.Button(button_frame, text="Start Quiz", command=self.start_quiz, state="disabled")
        self.start_quiz_button.pack(side=tk.LEFT, padx=5)

        self.quiz_label = ttk.Label(main_frame, text="", wraplength=700, font=("Arial", 14))
        self.quiz_label.pack(expand=True, fill="both", pady=20)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)

        self.prev_button = ttk.Button(control_frame, text="Previous (←)", command=self.prev_card)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.flip_button = ttk.Button(control_frame, text="Flip (↓)", command=self.flip_card)
        self.flip_button.grid(row=0, column=1, padx=5)

        self.next_button = ttk.Button(control_frame, text="Next (→)", command=self.next_card)
        self.next_button.grid(row=0, column=2, padx=5)

        self.show_question_first = tk.BooleanVar(value=True)
        self.question_first_toggle = ttk.Checkbutton(main_frame, text="Show Question First", 
                                                     variable=self.show_question_first, 
                                                     command=self.toggle_question_first)
        self.question_first_toggle.pack(pady=5)

        self.show_known_cards = tk.BooleanVar(value=True)
        self.show_known_toggle = ttk.Checkbutton(main_frame, text="Show Known Cards", 
                                                 variable=self.show_known_cards, 
                                                 command=self.toggle_show_known)
        self.show_known_toggle.pack(pady=5)

        # Populate file treeview with JSON files from Flashcards directory
        self.populate_file_treeview()

        # Bind button click events to remove focus
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.bind('<Button-1>', lambda e: self.focus_set())

    def bind_hotkeys(self):
        self.bind('<Left>', lambda event: self.prev_card())
        self.bind('<Right>', lambda event: self.next_card())
        self.bind('<Up>', lambda event: self.mark_known())
        self.bind('<Down>', lambda event: self.flip_card())
        self.bind('<Control-q>', lambda event: self.quit())

    def populate_file_treeview(self):
        flashcards_dir = os.path.join(os.path.dirname(__file__), 'Flashcards')
        if os.path.exists(flashcards_dir):
            json_files = [f for f in os.listdir(flashcards_dir) if f.endswith('.json')]
            for file in json_files:
                file_path = os.path.join(flashcards_dir, file)
                card_count = self.get_card_count(file_path)
                self.file_treeview.insert("", "end", values=(file, card_count))
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_select_file)

    def get_card_count(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data)
        except Exception:
            return "N/A"

    def on_select_file(self, event):
        selection = self.file_treeview.selection()
        if selection:
            item = self.file_treeview.item(selection[0])
            file_name = item['values'][0]
            flashcards_dir = os.path.join(os.path.dirname(__file__), 'Flashcards')
            file_path = os.path.join(flashcards_dir, file_name)
            self.load_json_file(file_path)

    def load_json_file(self, file_path=None):
        if file_path is None:
            flashcards_dir = os.path.join(os.path.dirname(__file__), 'Flashcards')
            file_path = filedialog.askopenfilename(initialdir=flashcards_dir, filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.deck.load_from_file(file_path)
                self.file_label.config(text=f"Selected deck: {os.path.basename(file_path)}")
                self.start_quiz_button.config(state="normal")
                self.update_file_treeview(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_file_treeview(self, new_file):
        new_file_name = os.path.basename(new_file)
        card_count = self.get_card_count(new_file)
        for item in self.file_treeview.get_children():
            if self.file_treeview.item(item)['values'][0] == new_file_name:
                return
        self.file_treeview.insert("", "end", values=(new_file_name, card_count))

    def start_quiz(self):
        self.quiz_cards = self.deck.cards.copy()
        if not self.show_known_cards.get():
            self.quiz_cards = [card for card in self.quiz_cards if card.question not in self.known_cards]
        random.shuffle(self.quiz_cards)
        self.current_card_idx = 0
        self.showing_question = self.show_question_first.get()
        self.show_current_card()

    def show_current_card(self):
        if self.quiz_cards:
            card = self.quiz_cards[self.current_card_idx]
            if self.showing_question:
                self.quiz_label.config(text=f"Question: {card.question}", foreground=self.accent_color)
            else:
                self.quiz_label.config(text=f"Answer: {card.answer}", foreground=self.text_color)
        else:
            self.quiz_label.config(text="No flashcards loaded for the quiz.", foreground=self.text_color)

    def flip_card(self):
        self.showing_question = not self.showing_question
        self.show_current_card()

    def next_card(self):
        if self.quiz_cards:
            self.current_card_idx = (self.current_card_idx + 1) % len(self.quiz_cards)
            self.showing_question = self.show_question_first.get()
            self.show_current_card()

    def prev_card(self):
        if self.quiz_cards:
            self.current_card_idx = (self.current_card_idx - 1) % len(self.quiz_cards)
            self.showing_question = self.show_question_first.get()
            self.show_current_card()

    def toggle_question_first(self):
        if self.quiz_cards:
            self.showing_question = self.show_question_first.get()
            self.show_current_card()

    def mark_known(self):
        if self.quiz_cards:
            card = self.quiz_cards[self.current_card_idx]
            self.known_cards.add(card.question)
            self.save_known_cards()
            if not self.show_known_cards.get():
                self.quiz_cards.pop(self.current_card_idx)
                if not self.quiz_cards:
                    self.quiz_label.config(text="All cards are known!", foreground=self.text_color)
                else:
                    self.current_card_idx %= len(self.quiz_cards)
                    self.show_current_card()
            else:
                self.next_card()

    def toggle_show_known(self):
        self.start_quiz()

    def load_known_cards(self):
        try:
            with open('known_cards.json', 'r') as f:
                self.known_cards = set(json.load(f))
        except FileNotFoundError:
            self.known_cards = set()

    def save_known_cards(self):
        with open('known_cards.json', 'w') as f:
            json.dump(list(self.known_cards), f)