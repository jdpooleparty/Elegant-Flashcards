class Flashcard:
    def __init__(self, question, answer, category="General"):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = 1  # 1-5 scale, 1 being easiest

    def __repr__(self):
        return f'Q: {self.question}, A: {self.answer}, Category: {self.category}, Difficulty: {self.difficulty}'