"""
Quiz.py
=======
Purpose:
    Renders the 15-question Final Course Certification Quiz (100% MCQs with options A, B, C, D),
    processes student submissions, evaluates multiple choice selections, records exam attempts,
    and unlocks the course Certificate upon achieving a passing score (>= 60%).

Viva Talking Points:
    - 100% Multiple Choice Questions: Every question presents 4 distinct options (A, B, C, D).
    - Certification Gate: A single comprehensive exam right before the certificate verifies
      holistic understanding of the entire course.
    - Instant Evaluation & Feedback: Compares chosen options against the answer key and
      provides a question-by-question review with explanations.
    - Database Consistency: Records attempts in 'quiz_attempts' with course_id and pass status.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from Database_Connection import query_db, execute_db
from Login import login_required
from Progress import get_or_create_progress, update_module_status, calculate_course_progress
from Quiz_Generator import generate_final_certification_quiz, generate_module_questions

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/course/<int:course_id>/final_quiz", methods=["GET", "POST"])
@login_required
def take_final_quiz(course_id):
    """
    Renders the 15-question Final Course Certification Exam (100% MCQs with options A, B, C, D)
    or evaluates submitted answers and unlocks the certificate if score >= 60%.
    """
    user_id = session["user_id"]

    course = query_db(
        "SELECT * FROM courses WHERE id = ? AND user_id = ?",
        (course_id, user_id),
        one=True
    )
    if not course:
        flash("Course not found or unauthorized access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Fetch existing questions for this course
    questions = query_db(
        "SELECT * FROM questions WHERE course_id = ? ORDER BY id ASC",
        (course_id,)
    )

    # Generate if not already present
    if len(questions) < 15:
        modules = query_db("SELECT title FROM modules WHERE course_id = ?", (course_id,))
        module_titles = [m["title"] for m in modules]
        generate_final_certification_quiz(course_id, course["topic"], course["difficulty"], module_titles)
        questions = query_db(
            "SELECT * FROM questions WHERE course_id = ? ORDER BY id ASC",
            (course_id,)
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

            is_correct = (user_ans.lower() == correct_ans.lower()) if user_ans else False
            if is_correct:
                score += 1

            results.append({
                "question": q["question"],
                "type": "mcq",
                "option_a": q["option_a"],
                "option_b": q["option_b"],
                "option_c": q["option_c"],
                "option_d": q["option_d"],
                "user_answer": user_ans if user_ans else "(No Option Selected)",
                "correct_answer": correct_ans,
                "is_correct": is_correct
            })

        pct = int((score / total_questions) * 100) if total_questions > 0 else 0
        passed = 1 if pct >= 60 else 0

        # Retrieve valid module_id from this course to satisfy foreign key constraint
        first_mod = query_db("SELECT id FROM modules WHERE course_id = ? ORDER BY module_number ASC LIMIT 1", (course_id,), one=True)
        mod_id = first_mod["id"] if first_mod else None

        # Save attempt in database
        execute_db("""
            INSERT INTO quiz_attempts (user_id, course_id, module_id, score, total_questions, passed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, course_id, mod_id, score, total_questions, passed))

        if passed:
            badge_class = "success"
            remarks = "Congratulations! You passed the Final Certification Exam. Your Certificate is now unlocked!"
        else:
            badge_class = "warning"
            remarks = "You scored below the 60% passing mark. Please review the course notes and try again!"

        return render_template(
            "quiz_result.html",
            course=course,
            score=score,
            total_questions=total_questions,
            percentage=pct,
            passed=passed,
            badge_class=badge_class,
            remarks=remarks,
            results=results,
            is_final_quiz=True
        )

    return render_template(
        "quiz.html",
        course=course,
        questions=questions,
        total_count=len(questions),
        is_final_quiz=True
    )


@quiz_bp.route("/quiz/<int:module_id>", methods=["GET", "POST"])
@login_required
def take_quiz(module_id):
    """
    Renders or evaluates a module quiz (100% 4-option MCQs).
    """
    user_id = session["user_id"]

    module_data = query_db("""
        SELECT m.*, c.title as course_title, c.user_id, c.id as course_id, c.topic, c.difficulty
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,), one=True)

    if not module_data or module_data["user_id"] != user_id:
        flash("Unauthorized quiz access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    course_id = module_data["course_id"]

    # Fetch questions for this module
    questions = query_db(
        "SELECT * FROM questions WHERE module_id = ? ORDER BY id ASC",
        (module_id,)
    )

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

            is_correct = (user_ans.lower() == correct_ans.lower()) if user_ans else False
            if is_correct:
                score += 1

            results.append({
                "question": q["question"],
                "type": "mcq",
                "option_a": q["option_a"],
                "option_b": q["option_b"],
                "option_c": q["option_c"],
                "option_d": q["option_d"],
                "user_answer": user_ans if user_ans else "(No Option Selected)",
                "correct_answer": correct_ans,
                "is_correct": is_correct
            })

        # Save quiz attempt
        execute_db("""
            INSERT INTO quiz_attempts (user_id, course_id, module_id, score, total_questions, passed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, course_id, module_id, score, total_questions, 1 if score >= 9 else 0))

        # Update progress table: mark module as completed
        get_or_create_progress(user_id, module_id)
        execute_db(
            "UPDATE progress SET quiz_completed = 1, module_completed = 1 WHERE user_id = ? AND module_id = ?",
            (user_id, module_id)
        )
        update_module_status(user_id, module_id)

        pct = int((score / total_questions) * 100) if total_questions > 0 else 0
        passed = 1 if pct >= 60 else 0

        badge_class = "success" if passed else "warning"
        remarks = "Great job completing the module questions!" if passed else "Keep practicing and review notes!"

        return render_template(
            "quiz_result.html",
            module=module_data,
            course={"id": course_id, "title": module_data["course_title"]},
            score=score,
            total_questions=total_questions,
            percentage=pct,
            passed=passed,
            badge_class=badge_class,
            remarks=remarks,
            results=results,
            is_final_quiz=False
        )

    return render_template(
        "quiz.html",
        module=module_data,
        course={"id": course_id, "title": module_data["course_title"]},
        questions=questions,
        total_count=len(questions),
        is_final_quiz=False
    )
