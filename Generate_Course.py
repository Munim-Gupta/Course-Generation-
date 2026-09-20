"""
Generate_Course.py
==================
Purpose:
    Handles course creation requests, validates parameters, coordinates with
    Course_Generator_Engine and Quiz_Generator to create modules, notes, and 15-question
    quizzes, and stores the records in the SQLite database.

Viva Talking Points:
    - Transactional Course Creation: Generates course entity, nested modules, and automated
      15 questions for each module in a single cohesive flow.
    - Zero External API overhead: 100% locally driven through predefined curricula and local question bank.
    - User Ownership: Ensures the new course is permanently linked to the authenticated user's ID.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from Database_Connection import execute_db, query_db
from Login import login_required
from Course_Generator_Engine import generate_course_modules
from Quiz_Generator import generate_module_questions
from Progress import get_or_create_progress

generate_course_bp = Blueprint("generate_course", __name__)

VALID_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]
VALID_MODULE_COUNTS = [3, 5, 8, 12]


@generate_course_bp.route("/generate_course", methods=["GET", "POST"])
@login_required
def generate_course():
    """Renders the course generation form and builds the full course upon submission."""
    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        difficulty = request.form.get("difficulty", "Beginner").capitalize()
        duration = request.form.get("duration", "4 Weeks").strip()
        module_count_raw = request.form.get("module_count", "5")

        # 1. Validation
        if not topic:
            flash("Please enter a valid course topic (e.g., Python, HTML, CSS, JavaScript).", "danger")
            return render_template("generate_course.html")

        if difficulty not in VALID_DIFFICULTIES:
            difficulty = "Beginner"

        try:
            module_count = int(module_count_raw)
            if module_count not in VALID_MODULE_COUNTS:
                module_count = 5
        except ValueError:
            module_count = 5

        user_id = session["user_id"]
        course_title = f"{topic.capitalize()} - {difficulty} Masterclass"

        # 2. Insert Course record
        course_id = execute_db("""
            INSERT INTO courses (user_id, title, topic, difficulty, duration, module_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, course_title, topic, difficulty, duration, module_count))

        # 3. Generate module outlines, student notes, and educational videos
        modules_data = generate_course_modules(topic, difficulty, module_count)

        for mod_info in modules_data:
            # Insert each module into the database
            module_id = execute_db("""
                INSERT INTO modules (course_id, module_number, title, notes, video_url)
                VALUES (?, ?, ?, ?, ?)
            """, (
                course_id,
                mod_info["module_number"],
                mod_info["title"],
                mod_info["notes"],
                mod_info["video_url"]
            ))

            # Automatically generate exactly 15 questions for each module
            generate_module_questions(module_id, topic, difficulty, mod_info["title"])

            # Initialize progress tracking entry for the user
            get_or_create_progress(user_id, module_id)

        flash(f"'{course_title}' generated successfully with {module_count} modules and automated quizzes!", "success")
        return redirect(url_for("module.view_course", course_id=course_id))

    return render_template("generate_course.html")
