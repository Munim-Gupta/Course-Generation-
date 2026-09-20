"""
Quiz.py
=======
Purpose:
    Renders the 15-question module quiz, processes student answers, performs
    string-normalized and exact-match answer evaluations, updates database records
    for quiz attempts and module progress, and renders a detailed feedback page.

Viva Talking Points:
    - Multi-format Evaluation:
        * MCQ & True/False: Direct comparison with normalized casing and spacing.
        * Short Answer: Natural string normalization (lowercasing, trimming, punctuation removal).
    - Database Consistency: Records every attempt in 'quiz_attempts' and updates 'progress'.
    - Instant Feedback: Renders question-by-question analysis showing user submission vs correct answer.
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from Database_Connection import query_db, execute_db
from Login import login_required
from Progress import get_or_create_progress, update_module_status, calculate_course_progress
from Quiz_Generator import generate_module_questions

quiz_bp = Blueprint("quiz", __name__)


def normalize_answer(text):
    """Normalizes answer string by lowercasing, stripping, and removing punctuation."""
    if not text:
        return ""
    cleaned = re.sub(r"[^\w\s]", "", text.strip().lower())
    return " ".join(cleaned.split())


@quiz_bp.route("/quiz/<int:module_id>", methods=["GET", "POST"])
@login_required
def take_quiz(module_id):
    """Renders the 15-question quiz interface or evaluates submitted answers."""
    user_id = session["user_id"]

    # Verify ownership through the course hierarchy
    module_data = query_db("""
        SELECT m.*, c.title as course_title, c.user_id, c.id as course_id, c.topic, c.difficulty
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,), one=True)

    if not module_data or module_data["user_id"] != user_id:
        flash("Unauthorized quiz access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Fetch questions for this module
    questions = query_db(
        "SELECT * FROM questions WHERE module_id = ? ORDER BY id ASC",
        (module_id,)
    )

    # If questions do not exist yet, generate them dynamically
    if len(questions) < 15:
        generate_module_questions(
            module_id,
            module_data["topic"],
            module_data["difficulty"],
            module_data["title"]
        )
        questions = query_db(
            "SELECT * FROM questions WHERE module_id = ? ORDER BY id ASC",
            (module_id,)
        )

    if request.method == "POST":
        score = 0
        total_questions = len(questions)
        results = []

        for q in questions:
            q_id = q["id"]
            field_name = f"question_{q_id}"
            user_ans = request.form.get(field_name, "").strip()
            correct_ans = q["correct_answer"].strip()
            q_type = q["question_type"]

            is_correct = False
            if q_type in ["mcq", "true_false"]:
                if user_ans.lower() == correct_ans.lower():
                    is_correct = True
            else:  # short_answer
                norm_user = normalize_answer(user_ans)
                norm_correct = normalize_answer(correct_ans)
                # Check exact normalized match or containment of essential token
                if norm_user == norm_correct or (len(norm_correct) > 2 and norm_correct in norm_user):
                    is_correct = True

            if is_correct:
                score += 1

            results.append({
                "question": q["question"],
                "type": q_type,
                "option_a": q["option_a"],
                "option_b": q["option_b"],
                "option_c": q["option_c"],
                "option_d": q["option_d"],
                "user_answer": user_ans if user_ans else "(No Answer Provided)",
                "correct_answer": correct_ans,
                "is_correct": is_correct
            })

        # Save quiz attempt
        execute_db("""
            INSERT INTO quiz_attempts (user_id, module_id, score, total_questions)
            VALUES (?, ?, ?, ?)
        """, (user_id, module_id, score, total_questions))

        # Update progress table: mark quiz as completed
        get_or_create_progress(user_id, module_id)
        execute_db(
            "UPDATE progress SET quiz_completed = 1 WHERE user_id = ? AND module_id = ?",
            (user_id, module_id)
        )

        # Check if entire module is completed (video + quiz)
        update_module_status(user_id, module_id)

        pct = int((score / total_questions) * 100) if total_questions > 0 else 0

        # Performance remarks
        if pct >= 80:
            badge_class = "success"
            remarks = "Excellent work! You demonstrated strong mastery of this topic."
        elif pct >= 60:
            badge_class = "info"
            remarks = "Good job! You have a solid grasp, with room for minor revision."
        else:
            badge_class = "warning"
            remarks = "Keep practicing! Review the module notes and retake the quiz to improve."

        # Fetch adjacent modules for quick navigation
        next_mod = query_db(
            "SELECT id FROM modules WHERE course_id = ? AND module_number = ?",
            (module_data["course_id"], module_data["module_number"] + 1),
            one=True
        )

        course_pct, _, _ = calculate_course_progress(user_id, module_data["course_id"])

        return render_template(
            "quiz_result.html",
            module=module_data,
            score=score,
            total=total_questions,
            percentage=pct,
            badge_class=badge_class,
            remarks=remarks,
            results=results,
            next_mod=next_mod,
            course_pct=course_pct
        )

    # GET: Render the interactive quiz
    return render_template(
        "quiz.html",
        module=module_data,
        questions=questions,
        total_questions=len(questions)
    )
