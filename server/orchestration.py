"""Orchestration module for lesson and mode management.

This module handles:
- Intent detection from user input
- Mode switching logic
- Dynamic context generation for different modes
"""

from curriculum import LESSONS


def detect_mode(user_text, lesson_state):
    """Detect user intent and update lesson state accordingly.

    Analyzes user input to determine the appropriate tutoring mode:
    - quiz: User wants to be tested
    - teaching: User wants to learn new content
    - conversation: User wants practice dialogue
    - doubt: User has a question or clarification need

    Args:
        user_text: The user's spoken/typed input
        lesson_state: Current LessonState instance to update

    Returns:
        str: The detected/current mode
    """
    text = user_text.lower()

    # Quiz mode triggers
    if any(keyword in text for keyword in ["quiz", "test me", "ask me questions"]):
        lesson_state.set_mode("quiz")

    # Teaching mode triggers
    elif any(keyword in text for keyword in ["teach", "lesson", "learn", "show me"]):
        lesson_state.set_mode("teaching")

    # Conversation practice triggers
    elif any(
        keyword in text
        for keyword in [
            "practice",
            "conversation",
            "talk",
            "chat",
            "roleplay",
            "role play",
        ]
    ):
        lesson_state.set_mode("conversation")

    # Doubt/clarification triggers
    elif any(
        keyword in text
        for keyword in [
            "why",
            "what does",
            "meaning",
            "explain",
            "how do you",
        ]
    ):
        lesson_state.enter_doubt_mode()

    return lesson_state.current_mode


def get_mode_instruction(lesson_state):
    """Generate mode-specific instruction to inject into Gemini context.

    Creates tailored guidance for the LLM based on current mode,
    ensuring behavior matches user expectations.

    Args:
        lesson_state: Current LessonState instance

    Returns:
        str: Context instruction to inject, or empty string if no lesson active
    """
    if not lesson_state.current_lesson:
        return ""

    current_lesson = LESSONS.get(lesson_state.current_lesson)
    if not current_lesson:
        return ""

    mode_templates = {
        "teaching": f"""
MODE SWITCH: You are now in TEACHING mode.

Current lesson: {lesson_state.current_lesson}
Objective: {current_lesson['objective']}

Vocabulary to teach:
{chr(10).join(f"- {v['spanish']} ({v['english']})" for v in current_lesson['vocabulary'])}

TEACHING STRATEGY:
1. Introduce ONE word at a time
2. Say the Spanish word clearly
3. Ask the learner to repeat it
4. Give encouraging feedback
5. Move to the next word

Keep responses under 15 words. The learner should speak more than you.
""",

        "quiz": f"""
MODE SWITCH: You are now in QUIZ mode.

Current lesson: {lesson_state.current_lesson}

Ask ONE question at a time from this list:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(current_lesson['practice_questions']))}

QUIZ FLOW:
1. Ask the question
2. Wait for their answer
3. Give specific feedback (correct/incorrect)
4. Move to next question

Keep questions short. Accept semantically correct answers even if wording differs.
""",

        "conversation": f"""
MODE SWITCH: You are now in CONVERSATION PRACTICE mode.

Current lesson: {lesson_state.current_lesson}

Vocabulary they should use:
{', '.join(v['spanish'] for v in current_lesson['vocabulary'])}

CONVERSATION STRATEGY:
1. Start a realistic dialogue using the vocabulary
2. Encourage them to respond in Spanish
3. Gently correct pronunciation or grammar mistakes
4. Keep it natural and fun

Respond in Spanish primarily. Keep responses under 10 words to encourage their participation.
""",

        "doubt": """
MODE SWITCH: You are now in DOUBT RESOLUTION mode.

The learner has a question or needs clarification.

APPROACH:
1. Answer their question briefly in English
2. Give a simple example if helpful
3. Ask if they understand
4. Smoothly return to the lesson

Keep explanations under 20 words. Then resume the previous activity.
""",
    }

    return mode_templates.get(lesson_state.current_mode, "")


def detect_lesson_switch(user_text, lesson_state):
    """Detect if user wants to switch to a different lesson topic.

    Args:
        user_text: The user's input
        lesson_state: Current LessonState instance

    Returns:
        str: New lesson name if detected, None otherwise
    """
    text = user_text.lower()

    # Map common phrases to lesson names
    lesson_triggers = {
        "greetings": ["greet", "hello", "hi", "goodbye"],

        "numbers": [
            "number",
            "count",
            "uno",
            "dos",
            "tres",
        ],

        "ordering_food": [
            "food",
            "restaurant",
            "coffee",
            "menu",
            "water",
            "order food",
        ],
    }

    for lesson_name, keywords in lesson_triggers.items():
        if any(keyword in text for keyword in keywords):
            if lesson_state.current_lesson != lesson_name:
                return lesson_name

    return None


def track_mistake(user_text, expected_answer, lesson_state):
    user_text = user_text.lower()

    expected_answer = expected_answer.lower()

    if expected_answer not in user_text:
        lesson_state.mistakes.append(expected_answer)

        return True

    return False