class LessonState:
    def __init__(self):
        self.current_mode = "idle"
        self.current_lesson = None
        self.lesson_step = 0
        self.current_question = None
        self.previous_mode = None

        self.mistakes = []
        self.learned_vocab = []

    def start_lesson(self, lesson_name):
        self.current_mode = "teaching"
        self.current_lesson = lesson_name
        self.lesson_step = 0

    def start_quiz(self, lesson_name):
        self.current_mode = "quiz"
        self.current_lesson = lesson_name
        self.lesson_step = 0

    def enter_doubt_mode(self):
        self.previous_mode = self.current_mode
        self.current_mode = "doubt"

    def exit_doubt_mode(self):
        if self.previous_mode:
            self.current_mode = self.previous_mode

    def next_step(self):
        self.lesson_step += 1

    def set_mode(self, mode):
        self.current_mode = mode