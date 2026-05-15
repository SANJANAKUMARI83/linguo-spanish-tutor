import json
import os


MEMORY_FILE = "progress.json"


def load_progress():
    if not os.path.exists(MEMORY_FILE):
        return {
            "completed_lessons": [],
            "mistakes": [],
            "learned_vocab": [],
        }

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_progress(lesson_state):
    progress = {
        "completed_lessons": [],
        "mistakes": lesson_state.mistakes,
        "learned_vocab": lesson_state.learned_vocab,
    }

    if lesson_state.current_lesson:
        progress["completed_lessons"].append(
            lesson_state.current_lesson
        )

    with open(MEMORY_FILE, "w") as f:
        json.dump(progress, f, indent=2)