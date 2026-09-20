"""
Module.py
=========
Purpose:
    Handles individual module and course view routing. Renders notes, code examples,
    embedded educational videos, navigation between sequential modules, and
    progress status indicators.

Viva Talking Points:
    - Authorization & Data Privacy: Verifies multi-tier ownership (courses.user_id == session.user_id)
      before serving course/module data, preventing IDOR (Insecure Direct Object Reference).
    - Sequential Navigation: Dynamically queries adjacent modules (prev/next) based on module_number.
    - Integration: Shows interactive progress state, video status, and direct links to 15-question quizzes.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash
import markdown
from Database_Connection import query_db
from Login import login_required
from Progress import calculate_course_progress, get_or_create_progress, is_course_final_quiz_passed

module_bp = Blueprint("module", __name__)


@module_bp.route("/course/<int:course_id>")
@login_required
def view_course(course_id):
    """Renders the comprehensive course syllabus, module list, and progress overview."""
    user_id = session["user_id"]

    # 1. Fetch course ensuring ownership
    course = query_db(
        "SELECT * FROM courses WHERE id = ? AND user_id = ?",
        (course_id, user_id),
        one=True
    )
    if not course:
        flash("Course not found or unauthorized access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # 2. Fetch all modules for this course
    modules = query_db(
        "SELECT * FROM modules WHERE course_id = ? ORDER BY module_number ASC",
        (course_id,)
    )

    # 3. Fetch progress for each module
    modules_with_progress = []
    for m in modules:
        prog = get_or_create_progress(user_id, m["id"])
        # Fetch best quiz score if attempted
        attempt = query_db(
            "SELECT MAX(score) as best_score, total_questions FROM quiz_attempts WHERE user_id = ? AND module_id = ?",
            (user_id, m["id"]),
            one=True
        )
        modules_with_progress.append({
            "module": m,
            "progress": prog,
            "quiz_score": attempt["best_score"] if attempt and attempt["best_score"] is not None else None,
            "total_questions": attempt["total_questions"] if attempt and attempt["total_questions"] else 15
        })

    progress_pct, completed_count, total_count = calculate_course_progress(user_id, course_id)

    # Final certification quiz status
    final_quiz_passed = is_course_final_quiz_passed(user_id, course_id)
    final_attempt = query_db(
        "SELECT MAX(score) as best_score, total_questions, passed FROM quiz_attempts WHERE user_id = ? AND course_id = ?",
        (user_id, course_id),
        one=True
    )

    return render_template(
        "course.html",
        course=course,
        modules=modules_with_progress,
        progress_pct=progress_pct,
        completed_count=completed_count,
        total_count=total_count,
        final_quiz_passed=final_quiz_passed,
        final_attempt=final_attempt
    )


@module_bp.route("/module/<int:module_id>")
@login_required
def view_module(module_id):
    """Renders specific module learning view with notes, video, and quiz launch."""
    user_id = session["user_id"]

    # Fetch module and verify user ownership via course relationship
    module_data = query_db("""
        SELECT m.*, c.title as course_title, c.user_id, c.id as course_id, c.module_count
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,), one=True)

    if not module_data or module_data["user_id"] != user_id:
        flash("Module not found or unauthorized access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    course_id = module_data["course_id"]
    current_num = module_data["module_number"]

    # Find previous and next module IDs
    prev_mod = query_db(
        "SELECT id FROM modules WHERE course_id = ? AND module_number = ?",
        (course_id, current_num - 1),
        one=True
    )
    next_mod = query_db(
        "SELECT id FROM modules WHERE course_id = ? AND module_number = ?",
        (course_id, current_num + 1),
        one=True
    )

    # Get current progress
    prog = get_or_create_progress(user_id, module_id)
    progress_pct, _, _ = calculate_course_progress(user_id, course_id)

    raw_notes = module_data["notes"] or ""
    notes_html = markdown.markdown(
        raw_notes,
        extensions=["fenced_code", "tables", "nl2br"]
    )

    return render_template(
        "module.html",
        module=module_data,
        notes_html=notes_html,
        prev_mod=prev_mod,
        next_mod=next_mod,
        progress=prog,
        progress_pct=progress_pct
    )
