"""
Quiz_Generator.py
=================
Purpose:
    Generates an automated, balanced 15-question Multiple Choice Quiz (100% MCQs with
    options A, B, C, D) for the Final Course Certification Exam without using paid APIs.
    Pulls from a local JSON question bank with an algorithmic MCQ template generator
    that guarantees every question has 4 selectable options.

Viva Talking Points:
    - 100% Multiple Choice Questions: Every question contains 4 distinct options (A, B, C, D).
    - Randomized Option Placement: Shuffles option positions (A, B, C, D) to prevent positional bias.
    - Tiered Selection Architecture:
        Tier 1: High-quality topic matches from question_bank.json
        Tier 2: Algorithmic domain-parameterized MCQs derived from course curriculum concepts
    - Final Certification Exam Integration: Associates questions directly with the course entity (course_id).
"""

import json
import os
import random
from Database_Connection import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTION_BANK_FILE = os.path.join(BASE_DIR, "question_bank.json")


def load_question_bank():
    """Loads all predefined questions from question_bank.json."""
    if not os.path.exists(QUESTION_BANK_FILE):
        return []
    try:
        with open(QUESTION_BANK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading question bank: {e}")
        return []


def generate_rich_mcq(topic, concept, index):
    """
    Generates an authentic 4-option Multiple Choice Question (MCQ)
    where options are shuffled so the correct answer varies between A, B, C, and D.
    """
    c = concept.strip()
    templates = [
        {
            "q": f"In {topic}, what is the primary role or significance of '{c}'?",
            "a": f"To implement core operations and structure program logic around {c}",
            "b": f"To automatically terminate the program execution whenever {c} is called",
            "c": f"To reset operating system network sockets and cache buffers",
            "d": f"To bypass runtime type checks and memory safety validations"
        },
        {
            "q": f"Which of the following is considered a standard best practice when working with '{c}' in {topic}?",
            "a": f"Validate boundary conditions and follow clean syntax conventions for {c}",
            "b": f"Never use {c} inside loops, functions, or conditional structures",
            "c": f"Define {c} strictly as a global variable across all modules",
            "d": f"Disable error handling and exception logging when implementing {c}"
        },
        {
            "q": f"What is the expected outcome if '{c}' is improperly configured or uninitialized in {topic}?",
            "a": f"The runtime engine raises an exception or produces incorrect logical results",
            "b": f"The host machine immediately restarts without warning",
            "c": f"All source code files are permanently removed from disk",
            "d": f"The compiler silently skips all remaining functions in the file"
        },
        {
            "q": f"How does mastering '{c}' benefit real-world software development in {topic}?",
            "a": f"It improves code maintainability, algorithmic efficiency, and modular design",
            "b": f"It eliminates the need for RAM and CPU resources in production",
            "c": f"It converts backend logic automatically into client-side cookies",
            "d": f"It restricts the application to run only on legacy 32-bit platforms"
        }
    ]

    t = templates[index % len(templates)]
    options_raw = [
        (t["a"], True),
        (t["b"], False),
        (t["c"], False),
        (t["d"], False)
    ]
    random.shuffle(options_raw)

    correct_answer = ""
    for opt_text, is_correct in options_raw:
        if is_correct:
            correct_answer = opt_text

    return {
        "topic": topic.lower(),
        "difficulty": "beginner",
        "type": "mcq",
        "question": t["q"],
        "option_a": options_raw[0][0],
        "option_b": options_raw[1][0],
        "option_c": options_raw[2][0],
        "option_d": options_raw[3][0],
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "explanation": f"Understanding {c} is essential for writing efficient, production-grade code in {topic}."
    }


def generate_final_certification_quiz(course_id, topic, difficulty, module_titles=None):
    """
    Generates exactly 15 comprehensive Multiple Choice Questions (100% MCQs with options A, B, C, D)
    for the Final Course Certification Exam. Saves questions in SQLite under course_id.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if questions already exist for this course
    existing = cur.execute(
        "SELECT * FROM questions WHERE course_id = ? ORDER BY id ASC",
        (course_id,)
    ).fetchall()

    if len(existing) >= 15:
        conn.close()
        return [dict(q) for q in existing]

    bank = load_question_bank()
    topic_normalized = topic.strip().lower()

    # Filter bank for MCQs that have all 4 options populated
    topic_mcqs = [
        q for q in bank
        if q.get("type") == "mcq"
        and q.get("option_a") and q.get("option_b") and q.get("option_c") and q.get("option_d")
        and (q.get("topic", "").lower() in topic_normalized or topic_normalized in q.get("topic", "").lower())
    ]
    random.shuffle(topic_mcqs)

    TARGET_COUNT = 15
    selected_questions = list(topic_mcqs[:TARGET_COUNT])

    # Extract concepts from curriculum module titles
    concepts = []
    if module_titles:
        for t in module_titles:
            words = [w for w in t.replace(":", " ").replace("-", " ").replace("&", " ").split() if len(w) > 3]
            concepts.extend(words)

    if not concepts:
        concepts = [topic, "Syntax", "Variables", "Functions", "Data Structures", "Logic Flow", "Debugging", "Optimization", "Architecture"]

    # Fill up to 15 with 4-option MCQs
    while len(selected_questions) < TARGET_COUNT:
        idx = len(selected_questions)
        concept = concepts[idx % len(concepts)]
        selected_questions.append(generate_rich_mcq(topic, concept, idx))

    assert len(selected_questions) == TARGET_COUNT

    # Save to SQLite database
    cur.execute("DELETE FROM questions WHERE course_id = ?", (course_id,))

    # Retrieve valid module_id from this course to satisfy foreign key constraint
    first_mod = cur.execute("SELECT id FROM modules WHERE course_id = ? ORDER BY module_number ASC LIMIT 1", (course_id,)).fetchone()
    mod_id = first_mod["id"] if first_mod else (cur.execute("SELECT id FROM modules LIMIT 1").fetchone() or {"id": 1})["id"]

    for q in selected_questions:
        cur.execute("""
            INSERT INTO questions (course_id, module_id, question, question_type, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_id,
            mod_id,
            q["question"],
            "mcq",
            q["option_a"],
            q["option_b"],
            q["option_c"],
            q["option_d"],
            q["answer"]
        ))

    conn.commit()
    conn.close()

    return selected_questions


def generate_module_questions(module_id, topic, difficulty, module_title=""):
    """
    Backwards-compatible helper that generates 15 MCQs with all 4 options (A, B, C, D)
    for a specific module if accessed directly.
    """
    bank = load_question_bank()
    topic_normalized = topic.strip().lower()

    topic_mcqs = [
        q for q in bank
        if q.get("type") == "mcq"
        and q.get("option_a") and q.get("option_b") and q.get("option_c") and q.get("option_d")
        and (q.get("topic", "").lower() in topic_normalized or topic_normalized in q.get("topic", "").lower())
    ]
    random.shuffle(topic_mcqs)

    TARGET_COUNT = 15
    selected_questions = list(topic_mcqs[:TARGET_COUNT])

    concepts = [w for w in module_title.replace(":", " ").replace("-", " ").split() if len(w) > 3]
    if not concepts:
        concepts = [topic, "Syntax", "Variables", "Functions", "Data Structures", "Logic Flow", "Debugging"]

    while len(selected_questions) < TARGET_COUNT:
        idx = len(selected_questions)
        c = concepts[idx % len(concepts)]
        selected_questions.append(generate_rich_mcq(topic, c, idx))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE module_id = ?", (module_id,))

    for q in selected_questions:
        cur.execute("""
            INSERT INTO questions (course_id, module_id, question, question_type, option_a, option_b, option_c, option_d, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            0,
            module_id,
            q["question"],
            "mcq",
            q["option_a"],
            q["option_b"],
            q["option_c"],
            q["option_d"],
            q["answer"]
        ))

    conn.commit()
    conn.close()

    return selected_questions
