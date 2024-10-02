import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import random
import json
from tkinter import Menu

class FlashcardUI(tk.Tk):
    def __init__(self, flashcard_deck):
        super().__init__()
        self.title("Elegant Flashcard App")
        self.geometry("1000x600")  # Increased window size
        self.deck = flashcard_deck

        # Define color scheme
        self.bg_color = "#F0F4F8"
        self.accent_color = "#4A90E2"
        self.text_color = "#333333"
        self.known_color = "blue"
        self.unknown_color = "black"

        self.configure(bg=self.bg_color)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.map('TButton', background=[('active', '#3A7AC2')])
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)

        self.known_cards = set()
        self.load_known_cards()

        self.is_dark_mode = False
        self.is_random_order = True  # New attribute for quiz order
        self.setup_toolbar()
        self.setup_ui()
        self.bind_hotkeys()

    def setup_toolbar(self):
        toolbar = Menu(self)
        self.config(menu=toolbar)

        # View menu
        view_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)

        # Tools menu
        tools_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Remove Duplicates", command=self.remove_duplicates)

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.bg_color = "#2E3440"
            self.accent_color = "#88C0D0"
            self.text_color = "#ECEFF4"
            self.known_color = "#A3BE8C"
            self.unknown_color = "#D08770"
        else:
            self.bg_color = "#F0F4F8"
            self.accent_color = "#4A90E2"
            self.text_color = "#333333"
            self.known_color = "blue"
            self.unknown_color = "black"

        self.configure(bg=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', background=self.accent_color, foreground=self.text_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('Treeview', background=self.bg_color, foreground=self.text_color, fieldbackground=self.bg_color)
        self.style.configure('Treeview.Heading', background=self.accent_color, foreground=self.text_color)

        # Update the quiz label color
        self.show_current_card()

    def remove_duplicates(self):
        if not self.deck.cards:
            messagebox.showinfo("Info", "No deck loaded. Please load a deck first.")
            return

        original_count = len(self.deck.cards)
        unique_cards = []
        seen = set()

        for card in self.deck.cards:
            card_tuple = (card.question.lower(), card.answer.lower())
            if card_tuple not in seen:
                seen.add(card_tuple)
                unique_cards.append(card)

        removed_count = original_count - len(unique_cards)

        if removed_count > 0:
            # Update the JSON file
            try:
                with open(self.current_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                new_data = []
                seen = set()
                for card in data:
                    card_tuple = (card['question'].lower(), card['answer'].lower())
                    if card_tuple not in seen:
                        seen.add(card_tuple)
                        new_data.append(card)
                
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, indent=2, ensure_ascii=False)

                self.deck.cards = unique_cards
                messagebox.showinfo("Duplicates Removed", f"Removed {removed_count} duplicate card(s) from the file.")
                self.update_file_treeview(self.current_file_path)
                self.start_quiz()  # Refresh the quiz with the updated deck
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update file: {str(e)}")
        else:
            messagebox.showinfo("No Duplicates", "No duplicate cards found in the deck.")

    def setup_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.file_label = ttk.Label(main_frame, text="Select a quiz deck:", font=("Arial", 12))
        self.file_label.pack(pady=10)

        file_frame = ttk.Frame(main_frame)
        file_frame.pack(pady=10)

        # Create a Treeview widget instead of Listbox
        self.file_treeview = ttk.Treeview(file_frame, columns=("File Name", "Card Count", "Known", "Unknown"), show="headings", height=10)
        self.file_treeview.heading("File Name", text="File Name")
        self.file_treeview.heading("Card Count", text="Card Count")
        self.file_treeview.heading("Known", text="Known")
        self.file_treeview.heading("Unknown", text="Unknown")
        self.file_treeview.column("File Name", width=400)
        self.file_treeview.column("Card Count", width=100, anchor="center")
        self.file_treeview.column("Known", width=100, anchor="center")
        self.file_treeview.column("Unknown", width=100, anchor="center")
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

        self.toggle_order_button = ttk.Button(button_frame, text="Toggle Order", command=self.toggle_quiz_order)
        self.toggle_order_button.pack(side=tk.LEFT, padx=5)

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
        self.bind('<Up>', lambda event: self.toggle_known())
        self.bind('<Down>', lambda event: self.flip_card())
        self.bind('<Control-q>', lambda event: self.quit())

    def populate_file_treeview(self):
        flashcards_dir = os.path.join(os.path.dirname(__file__), 'Flashcards')
        if os.path.exists(flashcards_dir):
            json_files = [f for f in os.listdir(flashcards_dir) if f.endswith('.json')]
            for file in json_files:
                file_path = os.path.join(flashcards_dir, file)
                card_count = self.get_card_count(file_path)
                known_count = self.get_known_count(file_path)
                unknown_count = card_count - known_count
                item = self.file_treeview.insert("", "end", values=(file, card_count, known_count, unknown_count))
        self.file_treeview.tag_configure('treeview', foreground='black')
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_select_file)

    def get_card_count(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data)
        except Exception:
            return "N/A"

    def get_known_count(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return sum(1 for card in data if card['question'] in self.known_cards)
        except Exception:
            return 0

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
                self.current_file_path = file_path  # Store the current file path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_file_treeview(self, new_file):
        new_file_name = os.path.basename(new_file)
        card_count = self.get_card_count(new_file)
        known_count = self.get_known_count(new_file)
        unknown_count = card_count - known_count
        for item in self.file_treeview.get_children():
            if self.file_treeview.item(item)['values'][0] == new_file_name:
                self.file_treeview.item(item, values=(new_file_name, card_count, known_count, unknown_count))
                return
        item = self.file_treeview.insert("", "end", values=(new_file_name, card_count, known_count, unknown_count))

    def start_quiz(self):
        self.quiz_cards = self.deck.cards.copy()
        if not self.show_known_cards.get():
            self.quiz_cards = [card for card in self.quiz_cards if card.question not in self.known_cards]
        if self.is_random_order:
            random.shuffle(self.quiz_cards)
        self.current_card_idx = 0
        self.showing_question = self.show_question_first.get()
        self.show_current_card()

    def show_current_card(self):
        if self.quiz_cards:
            card = self.quiz_cards[self.current_card_idx]
            card_number = self.deck.cards.index(card) + 1
            if self.showing_question:
                self.quiz_label.config(text=f"Card {card_number}\nQuestion: {card.question}", foreground=self.known_color if card.question in self.known_cards else self.unknown_color)
            else:
                self.quiz_label.config(text=f"Card {card_number}\nAnswer: {card.answer}", foreground=self.known_color if card.question in self.known_cards else self.unknown_color)
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

    def toggle_known(self):
        if self.quiz_cards:
            card = self.quiz_cards[self.current_card_idx]
            if card.question in self.known_cards:
                self.known_cards.remove(card.question)
            else:
                self.known_cards.add(card.question)
            self.save_known_cards()
            self.update_file_treeview(os.path.join(os.path.dirname(__file__), 'Flashcards', self.file_label.cget("text").split(": ")[1]))
            self.show_current_card()

    def toggle_show_known(self):
        self.start_quiz()

    def toggle_quiz_order(self):
        self.is_random_order = not self.is_random_order
        self.start_quiz()
        order_text = "Random" if self.is_random_order else "Sequential"
        self.toggle_order_button.config(text=f"Toggle Order ({order_text})")

    def load_known_cards(self):
        try:
            with open('known_cards.json', 'r') as f:
                self.known_cards = set(json.load(f))
        except FileNotFoundError:
            self.known_cards = set()

    def save_known_cards(self):
        with open('known_cards.json', 'w') as f:
            json.dump(list(self.known_cards), f)