from flashcard_deck import FlashcardDeck
from flashcard_ui import FlashcardUI

def main():
    deck = FlashcardDeck()
    app = FlashcardUI(deck)
    app.mainloop()

if __name__ == "__main__":
    main()