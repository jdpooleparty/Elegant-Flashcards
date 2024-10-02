import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import random
import json
import csv
from tkinter import Menu
import configparser
import pygame
from flashcard import Flashcard

class FlashcardUI(tk.Tk):
    def __init__(self, flashcard_deck):
        super().__init__()
        self.title("Elegant Flashcards")
        self.geometry("1000x600")  # Increased window size
        self.deck = flashcard_deck

        # Initialize quiz_cards here
        self.quiz_cards = []

        # Load configuration
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read('config.ini')
        
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

        self.known_cards = set()  # Store known cards as a set
        self.load_known_cards()

        self.is_dark_mode = self.config_parser.getboolean('View', 'dark_mode', fallback=False)
        self.color_mode = self.config_parser.get('View', 'color_mode', fallback='light')
        self.is_random_order = self.config_parser.getboolean('Quiz', 'random_order', fallback=True)
        self.sound_enabled = self.config_parser.getboolean('Sound', 'enabled', fallback=True)
        self.sound_option = self.config_parser.get('Sound', 'option', fallback='success.wav')
        self.show_question_first = tk.BooleanVar(value=self.config_parser.getboolean('CardOptions', 'show_question_first', fallback=True))
        self.show_known_cards = tk.BooleanVar(value=self.config_parser.getboolean('CardOptions', 'show_known_cards', fallback=True))
        self.setup_toolbar()
        self.setup_ui()
        self.bind_hotkeys()
        
        self.apply_color_mode()

        # Initialize pygame mixer for sound
        pygame.mixer.init()

    def setup_toolbar(self):
        toolbar = Menu(self)
        self.configure(menu=toolbar)

        # View menu
        view_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="View", menu=view_menu)
        
        self.color_mode_var = tk.StringVar(value=self.color_mode)
        view_menu.add_radiobutton(label="Light Mode", variable=self.color_mode_var, value="light", command=self.change_color_mode)
        view_menu.add_radiobutton(label="Dark Mode", variable=self.color_mode_var, value="dark", command=self.change_color_mode)
        view_menu.add_radiobutton(label="System", variable=self.color_mode_var, value="system", command=self.change_color_mode)

        # Tools menu
        tools_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Remove Duplicates", command=self.remove_duplicates)
        tools_menu.add_command(label="Browse Removed Flashcards", command=self.browse_removed_flashcards)
        tools_menu.add_command(label="Import from CSV", command=self.import_from_csv)

        # Sound menu
        sound_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="Sound", menu=sound_menu)
        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        sound_menu.add_checkbutton(label="Enable Sound", variable=self.sound_var, command=self.toggle_sound)
        
        # Sound options submenu
        sound_options_menu = Menu(sound_menu, tearoff=0)
        sound_menu.add_cascade(label="Sound Options", menu=sound_options_menu)
        
        self.sound_option_var = tk.StringVar(value=self.sound_option)
        sound_options_menu.add_radiobutton(label="Success Sound", variable=self.sound_option_var, value="success.wav", command=self.change_sound_option)
        sound_options_menu.add_radiobutton(label="Chime Sound", variable=self.sound_option_var, value="chime.wav", command=self.change_sound_option)
        sound_options_menu.add_radiobutton(label="Bell Sound", variable=self.sound_option_var, value="bell.wav", command=self.change_sound_option)

        # Card Options menu
        card_options_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="Card Options", menu=card_options_menu)
        card_options_menu.add_checkbutton(label="Show Question First", variable=self.show_question_first, command=self.toggle_question_first)
        card_options_menu.add_checkbutton(label="Show Known Cards", variable=self.show_known_cards, command=self.toggle_show_known)

        # About menu
        about_menu = Menu(toolbar, tearoff=0)
        toolbar.add_cascade(label="About", menu=about_menu)
        about_menu.add_command(label="About Elegant Flashcards", command=self.show_about)

    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("About Elegant Flashcards")
        about_window.geometry("400x300")

        logo_label = ttk.Label(about_window, text="Elegant Flashcards", font=("Arial", 16, "bold"))
        logo_label.pack(pady=10)

        license_text = "This program is free software: you can redistribute it and/or modify\n" \
                       "it under the terms of the GNU General Public License as published by\n" \
                       "the Free Software Foundation, either version 3 of the License, or\n" \
                       "(at your option) any later version."
        license_label = ttk.Label(about_window, text=license_text, wraplength=380, justify="center")
        license_label.pack(pady=10)

        developer_label = ttk.Label(about_window, text="Developed by Jonathan Poole in 2024")
        developer_label.pack(pady=10)

    def toggle_sound(self):
        self.sound_enabled = self.sound_var.get()
        self.save_config()

    def change_sound_option(self):
        self.sound_option = self.sound_option_var.get()
        self.save_config()

    def change_color_mode(self):
        self.color_mode = self.color_mode_var.get()
        self.apply_color_mode()
        self.save_config()

    def apply_color_mode(self):
        if self.color_mode == "system":
            # You might need to implement a way to detect system color mode
            # For now, we'll default to light mode
            self.is_dark_mode = False
        elif self.color_mode == "dark":
            self.is_dark_mode = True
        else:
            self.is_dark_mode = False
        
        self.toggle_dark_mode()

    def toggle_dark_mode(self):
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
        if not hasattr(self, 'current_file_path'):
            messagebox.showinfo("Info", "Please select a deck first.")
            return

        try:
            with open(self.current_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Create a set to store unique questions
            unique_questions = set()
            unique_cards = []

            for card in data:
                question = card['question']
                if question not in unique_questions:
                    unique_questions.add(question)
                    unique_cards.append(card)

            removed_count = len(data) - len(unique_cards)

            # Write the unique cards back to the file
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                json.dump(unique_cards, f, indent=2, ensure_ascii=False)

            # Update the deck
            self.deck.cards = [Flashcard(card['question'], card['answer'], card.get('category', 'General')) for card in unique_cards]
            self.update_file_treeview(self.current_file_path)
            self.start_quiz()

            messagebox.showinfo("Success", f"Removed {removed_count} duplicate cards.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove duplicates: {str(e)}")

    def add_to_removed_flashcards(self, card):
        removed_file = os.path.join(os.path.dirname(__file__), 'Flashcards', 'Removed_Flashcards.json')
        try:
            with open(removed_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data.append(card)
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.truncate()
        except FileNotFoundError:
            with open(removed_file, 'w', encoding='utf-8') as f:
                json.dump([card], f, indent=2, ensure_ascii=False)

    def browse_removed_flashcards(self):
        removed_file = os.path.join(os.path.dirname(__file__), 'Flashcards', 'Removed_Flashcards.json')
        try:
            with open(removed_file, 'r', encoding='utf-8') as f:
                removed_cards = json.load(f)
        except FileNotFoundError:
            messagebox.showinfo("Info", "No removed flashcards found.")
            return

        if not removed_cards:
            messagebox.showinfo("Info", "No removed flashcards found.")
            return

        browse_window = tk.Toplevel(self)
        browse_window.title("Browse Removed Flashcards")
        browse_window.geometry("600x400")

        treeview = ttk.Treeview(browse_window, columns=("Question", "Answer"), show="headings")
        treeview.heading("Question", text="Question")
        treeview.heading("Answer", text="Answer")
        treeview.pack(expand=True, fill="both")

        for card in removed_cards:
            treeview.insert("", "end", values=(card['question'], card['answer']))

        def add_to_current_deck():
            selected_item = treeview.selection()
            if not selected_item:
                messagebox.showinfo("Info", "Please select a flashcard to add.")
                return

            item = treeview.item(selected_item[0])
            card = {'question': item['values'][0], 'answer': item['values'][1]}

            if not hasattr(self, 'current_file_path'):
                messagebox.showinfo("Info", "Please select a deck first.")
                return

            try:
                if self.current_file_path.endswith('.json'):
                    with open(self.current_file_path, 'r+', encoding='utf-8') as f:
                        data = json.load(f)
                        data.append(card)
                        f.seek(0)
                        json.dump(data, f, indent=2, ensure_ascii=False)
                        f.truncate()
                elif self.current_file_path.endswith('.csv'):
                    with open(self.current_file_path, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=['question', 'answer'])
                        writer.writerow(card)

                # Remove the card from Removed_Flashcards.json
                removed_cards.remove(card)
                with open(removed_file, 'w', encoding='utf-8') as f:
                    json.dump(removed_cards, f, indent=2, ensure_ascii=False)

                treeview.delete(selected_item[0])
                self.deck.cards.append(Flashcard(card['question'], card['answer']))
                self.update_file_treeview(self.current_file_path)
                messagebox.showinfo("Success", "Flashcard added to the current deck.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add flashcard: {str(e)}")

        add_button = ttk.Button(browse_window, text="Add to Current Deck", command=add_to_current_deck)
        add_button.pack(pady=10)

    def import_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header row
                    imported_cards = [{'question': row[0], 'answer': row[1]} for row in reader]

                if not imported_cards:
                    messagebox.showinfo("Info", "No cards found in the CSV file.")
                    return

                # Add imported cards to the current deck
                if hasattr(self, 'current_file_path'):
                    if self.current_file_path.endswith('.json'):
                        with open(self.current_file_path, 'r+', encoding='utf-8') as f:
                            data = json.load(f)
                            data.extend(imported_cards)
                            f.seek(0)
                            json.dump(data, f, indent=2, ensure_ascii=False)
                            f.truncate()
                    elif self.current_file_path.endswith('.csv'):
                        with open(self.current_file_path, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=['question', 'answer'])
                            writer.writerows(imported_cards)

                    for card in imported_cards:
                        self.deck.cards.append(Flashcard(card['question'], card['answer']))

                    self.update_file_treeview(self.current_file_path)
                    messagebox.showinfo("Success", f"Imported {len(imported_cards)} cards from CSV.")
                    self.start_quiz()  # Refresh the quiz with the updated deck
                else:
                    messagebox.showinfo("Info", "Please select a deck first before importing.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")

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

        select_file_button = ttk.Button(button_frame, text="Select File", command=self.load_file)
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

        self.toggle_known_button = ttk.Button(control_frame, text="Toggle Known (↑)", command=self.toggle_known)
        self.toggle_known_button.grid(row=0, column=1, padx=5)

        self.flip_button = ttk.Button(control_frame, text="Flip (↓)", command=self.flip_card)
        self.flip_button.grid(row=0, column=2, padx=5)

        self.next_button = ttk.Button(control_frame, text="Next (→)", command=self.next_card)
        self.next_button.grid(row=0, column=3, padx=5)

        # Populate file treeview with JSON and CSV files from Flashcards directory
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
            files = [f for f in os.listdir(flashcards_dir) if f.endswith(('.json', '.csv'))]
            for file in files:
                file_path = os.path.join(flashcards_dir, file)
                card_count = self.get_card_count(file_path)
                known_count = len(self.known_cards.intersection(self.get_questions(file_path)))
                unknown_count = card_count - known_count
                item = self.file_treeview.insert("", "end", values=(file, card_count, known_count, unknown_count))
        self.file_treeview.tag_configure('treeview', foreground='black')
        self.file_treeview.bind('<<TreeviewSelect>>', self.on_select_file)

    def get_card_count(self, file_path):
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return len(data)
            elif file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    return sum(1 for row in reader) - 1  # Subtract 1 for header row
        except Exception:
            return "N/A"

    def get_questions(self, file_path):
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [card['question'] for card in data]
            elif file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    return [row['question'] for row in reader]
        except Exception:
            return []

    def on_select_file(self, event):
        selection = self.file_treeview.selection()
        if selection:
            item = self.file_treeview.item(selection[0])
            file_name = item['values'][0]
            flashcards_dir = os.path.join(os.path.dirname(__file__), 'Flashcards')
            file_path = os.path.join(flashcards_dir, file_name)
            self.load_file(file_path)

    def load_file(self, file_path=None):
        if file_path is None:
            flashcards_dir = os.path.join(os.path.dirname(__file__), 'Flashcards')
            file_path = filedialog.askopenfilename(initialdir=flashcards_dir, filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")])
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self.deck.load_from_file(file_path)
                elif file_path.endswith('.csv'):
                    self.deck.load_from_csv(file_path)
                self.file_label.config(text=f"Selected deck: {os.path.basename(file_path)}")
                self.start_quiz_button.config(state="normal")
                self.update_file_treeview(file_path)
                self.current_file_path = file_path  # Store the current file path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def update_file_treeview(self, new_file):
        new_file_name = os.path.basename(new_file)
        card_count = self.get_card_count(new_file)
        known_count = len(self.known_cards.intersection(self.get_questions(new_file)))
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
        self.save_config()

    def toggle_known(self):
        if self.quiz_cards:
            card = self.quiz_cards[self.current_card_idx]
            if card.question in self.known_cards:
                self.known_cards.remove(card.question)
            else:
                self.known_cards.add(card.question)
                if self.sound_enabled:
                    self.play_sound()
            self.save_known_cards()
            self.update_file_treeview(self.current_file_path)
            self.show_current_card()

    def play_sound(self):
        try:
            sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
            sound_file = os.path.join(sound_dir, self.sound_option)
            if os.path.exists(sound_file):
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            else:
                print(f"Error: Sound file not found: {sound_file}")
        except pygame.error as e:
            print(f"Error: Unable to play sound file {self.sound_option}: {str(e)}")

    def toggle_show_known(self):
        self.start_quiz()
        self.save_config()

    def toggle_quiz_order(self):
        self.is_random_order = not self.is_random_order
        self.start_quiz()
        order_text = "Random" if self.is_random_order else "Sequential"
        self.toggle_order_button.config(text=f"Toggle Order ({order_text})")
        self.save_config()

    def load_known_cards(self):
        try:
            with open('known_cards.json', 'r') as f:
                self.known_cards = set(json.load(f))
        except FileNotFoundError:
            self.known_cards = set()

    def save_known_cards(self):
        with open('known_cards.json', 'w') as f:
            json.dump(list(self.known_cards), f)

    def save_config(self):
        if not self.config_parser.has_section('View'):
            self.config_parser.add_section('View')
        self.config_parser.set('View', 'color_mode', self.color_mode)
        self.config_parser.set('View', 'dark_mode', str(self.is_dark_mode))
        
        if not self.config_parser.has_section('Quiz'):
            self.config_parser.add_section('Quiz')
        self.config_parser.set('Quiz', 'random_order', str(self.is_random_order))
        
        if not self.config_parser.has_section('Sound'):
            self.config_parser.add_section('Sound')
        self.config_parser.set('Sound', 'enabled', str(self.sound_enabled))
        self.config_parser.set('Sound', 'option', self.sound_option)
        
        if not self.config_parser.has_section('CardOptions'):
            self.config_parser.add_section('CardOptions')
        self.config_parser.set('CardOptions', 'show_question_first', str(self.show_question_first.get()))
        self.config_parser.set('CardOptions', 'show_known_cards', str(self.show_known_cards.get()))
        
        with open('config.ini', 'w') as configfile:
            self.config_parser.write(configfile)

    def quit(self):
        self.save_config()
        super().quit()