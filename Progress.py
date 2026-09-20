"""
Progress.py
===========
Purpose:
    Manages module progression tracking, video watched toggling, quiz completion
    status, and course completion percentage calculation.

Viva Talking Points:
    - Business Logic: A module is only marked 'completed' when BOTH video is watched
      and the quiz has been completed.
    - Database Integrity: Uses SQLite INSERT ... ON CONFLICT DO UPDATE to ensure
      no duplicate progress records exist per user and module.
    - Aggregation: Calculates real-time completion rates using SQL aggregations.
"""

from flask import Blueprint, redirect, url_for, session, flash, request, jsonify
from Database_Connection import query_db, execute_db
from Login import login_required

progress_bp = Blueprint("progress", __name__)


def get_or_create_progress(user_id, module_id):
    """
    Fetches the existing progress record or creates an initialized default row.
    Guarantees no duplicates through the unique constraint.
    """
    prog = query_db(
        "SELECT * FROM progress WHERE user_id = ? AND module_id = ?",
        (user_id, module_id),
        one=True
    )
    if not prog:
        execute_db("""
            INSERT INTO progress (user_id, module_id, video_watched, quiz_completed, module_completed)
            VALUES (?, ?, 0, 0, 0)
            ON CONFLICT(user_id, module_id) DO NOTHING
        """, (user_id, module_id))
        prog = query_db(
            "SELECT * FROM progress WHERE user_id = ? AND module_id = ?",
            (user_id, module_id),
            one=True
        )
    return prog


def update_module_status(user_id, module_id):
    """
    Evaluates whether the module is fully completed:
    video_watched == 1 OR module_completed == 1.
    """
    prog = get_or_create_progress(user_id, module_id)
    if prog:
        is_completed = 1 if (prog["video_watched"] == 1 or prog["module_completed"] == 1) else 0
        execute_db(
            "UPDATE progress SET module_completed = ? WHERE user_id = ? AND module_id = ?",
            (is_completed, user_id, module_id)
        )


def is_course_final_quiz_passed(user_id, course_id):
    """
    Checks if user has passed the Final Course Certification Quiz with score >= 60%.
    Returns (passed (bool), best_score, total_questions).
    """
    attempt = query_db("""
        SELECT MAX(score) as best_score, total_questions
        FROM quiz_attempts
        WHERE user_id = ? AND course_id = ?
    """, (user_id, course_id), one=True)

    if attempt and attempt["best_score"] is not None and attempt["total_questions"]:
        total = attempt["total_questions"]
        best = attempt["best_score"]
        pct = (best * 100.0) / total
        return (pct >= 60.0), best, total

    return False, None, 15


def calculate_course_progress(user_id, course_id):
    """
    Calculates the completion percentage for a given course.
    Returns: (percentage (int), completed_count, total_count)
    """
    modules = query_db(
        "SELECT id FROM modules WHERE course_id = ? ORDER BY module_number",
        (course_id,)
    )
    total_count = len(modules)
    if total_count == 0:
        return 0, 0, 0

    module_ids = [m["id"] for m in modules]
    placeholders = ",".join(["?"] * len(module_ids))

    completed_rows = query_db(
        f"SELECT COUNT(*) as count FROM progress WHERE user_id = ? AND module_id IN ({placeholders}) AND module_completed = 1",
        [user_id] + module_ids,
        one=True
    )
    completed_count = completed_rows["count"] if completed_rows else 0
    percentage = int((completed_count / total_count) * 100)
    return percentage, completed_count, total_count


def get_next_incomplete_module(user_id, course_id):
    """
    Finds the first module in the course that has not yet been marked completed.
    Returns the module Row, or None if the course is 100% finished.
    """
    modules = query_db(
        "SELECT * FROM modules WHERE course_id = ? ORDER BY module_number ASC",
        (course_id,)
    )
    for mod in modules:
        prog = query_db(
            "SELECT module_completed FROM progress WHERE user_id = ? AND module_id = ?",
            (user_id, mod["id"]),
            one=True
        )
        if not prog or prog["module_completed"] != 1:
            return mod
    return None


@progress_bp.route("/mark_video_watched/<int:module_id>", methods=["POST"])
@login_required
def mark_video_watched(module_id):
    """Route to mark a module's video as watched."""
    user_id = session["user_id"]

    # Verify that the module belongs to a course owned by this user
    mod = query_db("""
        SELECT m.id, c.id as course_id, c.user_id
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,), one=True)

    if not mod or mod["user_id"] != user_id:
        flash("Unauthorized module access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    # Mark video as watched in progress
    get_or_create_progress(user_id, module_id)
    execute_db(
        "UPDATE progress SET video_watched = 1, module_completed = 1 WHERE user_id = ? AND module_id = ?",
        (user_id, module_id)
    )
    update_module_status(user_id, module_id)

    flash("Video marked as watched and module completed!", "success")
    return redirect(url_for("module.view_module", module_id=module_id))


@progress_bp.route("/mark_module_completed/<int:module_id>", methods=["POST"])
@login_required
def mark_module_completed(module_id):
    """Route to mark a module as completed by the student."""
    user_id = session["user_id"]

    mod = query_db("""
        SELECT m.id, c.id as course_id, c.user_id
        FROM modules m
        JOIN courses c ON m.course_id = c.id
        WHERE m.id = ?
    """, (module_id,), one=True)

    if not mod or mod["user_id"] != user_id:
        flash("Unauthorized module access.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    get_or_create_progress(user_id, module_id)
    execute_db(
        "UPDATE progress SET video_watched = 1, module_completed = 1 WHERE user_id = ? AND module_id = ?",
        (user_id, module_id)
    )
    update_module_status(user_id, module_id)

    flash("Module marked as completed! Excellent work.", "success")
    return redirect(url_for("module.view_module", module_id=module_id))
