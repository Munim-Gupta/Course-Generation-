"""
Dashboard.py
============
Purpose:
    Renders the student learning dashboard, showing aggregate metrics (total courses,
    total modules, modules completed, videos watched, quiz scores) and cards for
    each course enrolled by the current user.

Viva Talking Points:
    - User isolation: All queries filter strictly by session['user_id'].
    - Real-time aggregation: Aggregates metrics dynamically from courses, modules,
      quiz_attempts, and progress tables.
    - Adaptive navigation: "Continue Course" dynamically resolves the first incomplete module.
"""

from flask import Blueprint, render_template, session
from Database_Connection import query_db
from Login import login_required
from Progress import calculate_course_progress, get_next_incomplete_module

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Aggregates user metrics and renders courses in responsive cards."""
    user_id = session["user_id"]
    user_name = session.get("user_name", "Student")

    # 1. Fetch user's courses
    courses = query_db(
        "SELECT * FROM courses WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )

    total_courses = len(courses)
    total_modules = 0
    total_completed_modules = 0
    total_videos_watched = 0

    course_cards = []

    for c in courses:
        c_id = c["id"]
        c_pct, c_completed, c_total = calculate_course_progress(user_id, c_id)
        total_modules += c_total
        total_completed_modules += c_completed

        # Check videos watched for this course
        mods = query_db("SELECT id FROM modules WHERE course_id = ?", (c_id,))
        if mods:
            m_ids = [m["id"] for m in mods]
            placeholders = ",".join(["?"] * len(m_ids))
            v_watched_rows = query_db(
                f"SELECT COUNT(*) as cnt FROM progress WHERE user_id = ? AND module_id IN ({placeholders}) AND video_watched = 1",
                [user_id] + m_ids,
                one=True
            )
            total_videos_watched += v_watched_rows["cnt"] if v_watched_rows else 0

        next_mod = get_next_incomplete_module(user_id, c_id)

        course_cards.append({
            "course": c,
            "progress_pct": c_pct,
            "completed_modules": c_completed,
            "total_modules": c_total,
            "next_module": next_mod,
            "is_complete": (c_pct == 100)
        })

    # 2. Compute Quiz stats
    quiz_stats = query_db("""
        SELECT COUNT(*) as total_attempts, AVG(score * 100.0 / total_questions) as avg_score
        FROM quiz_attempts
        WHERE user_id = ?
    """, (user_id,), one=True)

    avg_quiz_score = int(quiz_stats["avg_score"]) if quiz_stats and quiz_stats["avg_score"] is not None else 0
    total_quizzes_taken = quiz_stats["total_attempts"] if quiz_stats else 0

    # 3. Overall completion percentage across all courses
    overall_progress = int((total_completed_modules / total_modules) * 100) if total_modules > 0 else 0

    return render_template(
        "dashboard.html",
        user_name=user_name,
        total_courses=total_courses,
        total_modules=total_modules,
        completed_modules=total_completed_modules,
        videos_watched=total_videos_watched,
        avg_quiz_score=avg_quiz_score,
        quizzes_taken=total_quizzes_taken,
        overall_progress=overall_progress,
        courses=course_cards
    )
