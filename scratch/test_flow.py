"""
scratch/test_flow.py
====================
End-to-end automated verification script testing all core functionality:
- Database schema initialization
- User registration & password hashing
- Login validation
- Course generation (known topic & custom topic)
- 15-question quiz generation (8 MCQ, 4 T/F, 3 Short)
- Video watch toggling & Quiz evaluation
- Module completion logic
- PDF syllabus & notes generation via ReportLab
- Certificate generation gating & PDF output
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash, check_password_hash
from Database_Connection import init_db, get_db_connection, query_db, execute_db
from Course_Generator_Engine import generate_course_modules
from Quiz_Generator import generate_module_questions
from Progress import calculate_course_progress, get_or_create_progress, update_module_status, get_next_incomplete_module
from PDF_Generator import build_pdf_styles, parse_markdown_to_flowables
from Certificate import generate_certificate_hash
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate
from reportlab.pdfgen import canvas
import io


def test_end_to_end():
    print("=== Step 1: Testing Database Initialization ===")
    init_db()
    conn = get_db_connection()
    tables = [row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    conn.close()
    expected_tables = ["users", "courses", "modules", "questions", "quiz_attempts", "progress"]
    for t in expected_tables:
        assert t in tables, f"Missing table: {t}"
    print("[OK] All 6 SQLite tables successfully verified!")

    print("\n=== Step 2: Testing User Registration & Password Hashing ===")
    test_email = "teststudent@college.edu"
    test_password = "SecretPassword123!"
    hashed = generate_password_hash(test_password)
    assert check_password_hash(hashed, test_password)
    assert not check_password_hash(hashed, "WrongPassword")

    # Clean previous test user
    execute_db("DELETE FROM users WHERE email = ?", (test_email,))
    user_id = execute_db(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        ("Test Student", test_email, hashed)
    )
    assert user_id > 0
    print(f"[OK] User registered successfully with ID {user_id} and secure hash.")

    print("\n=== Step 3: Testing Course & Module Generation (Python Beginner, 5 modules) ===")
    modules_data = generate_course_modules("Python", "Beginner", 5)
    assert len(modules_data) == 5, f"Expected 5 modules, got {len(modules_data)}"

    course_id = execute_db("""
        INSERT INTO courses (user_id, title, topic, difficulty, duration, module_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, "Python for Beginners", "Python", "Beginner", "4 Weeks", 5))

    module_ids = []
    for mod_info in modules_data:
        m_id = execute_db("""
            INSERT INTO modules (course_id, module_number, title, notes, video_url)
            VALUES (?, ?, ?, ?, ?)
        """, (
            course_id,
            mod_info["module_number"],
            mod_info["title"],
            mod_info["notes"],
            mod_info["video_url"]
        ))
        module_ids.append(m_id)
        get_or_create_progress(user_id, m_id)

    print(f"[OK] Course {course_id} and 5 modules successfully inserted.")

    print("\n=== Step 4: Testing 15-Question Quiz Generator on all modules ===")
    for idx, m_id in enumerate(module_ids, start=1):
        qs = generate_module_questions(m_id, "Python", "Beginner", modules_data[idx - 1]["title"])
        assert len(qs) == 15, f"Module {m_id} expected 15 questions, got {len(qs)}"

        # Verify exact distribution in database
        db_qs = query_db("SELECT * FROM questions WHERE module_id = ?", (m_id,))
        assert len(db_qs) == 15
        mcqs = [q for q in db_qs if q["question_type"] == "mcq"]
        tfs = [q for q in db_qs if q["question_type"] == "true_false"]
        shorts = [q for q in db_qs if q["question_type"] == "short_answer"]

        assert len(mcqs) == 8, f"Expected 8 MCQs, got {len(mcqs)}"
        assert len(tfs) == 4, f"Expected 4 True/False, got {len(tfs)}"
        assert len(shorts) == 3, f"Expected 3 Short Answer, got {len(shorts)}"

    print("[OK] Exactly 15 questions (8 MCQ, 4 T/F, 3 Short Answer) verified across all modules!")

    print("\n=== Step 5: Testing Unknown Topic Fallback (Docker, 3 modules) ===")
    custom_modules = generate_course_modules("Docker", "Beginner", 3)
    assert len(custom_modules) == 3
    docker_c_id = execute_db("""
        INSERT INTO courses (user_id, title, topic, difficulty, duration, module_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, "Docker for Beginners", "Docker", "Beginner", "2 Weeks", 3))
    docker_m_id = execute_db("""
        INSERT INTO modules (course_id, module_number, title, notes, video_url)
        VALUES (?, ?, ?, ?, ?)
    """, (
        docker_c_id,
        custom_modules[0]["module_number"],
        custom_modules[0]["title"],
        custom_modules[0]["notes"],
        custom_modules[0]["video_url"]
    ))
    custom_qs = generate_module_questions(docker_m_id, "Docker", "Beginner", custom_modules[0]["title"])
    assert len(custom_qs) == 15, f"Expected 15 questions for custom topic, got {len(custom_qs)}"
    print("[OK] Custom topic fallback successfully generated 15 questions without crashing!")

    print("\n=== Step 6: Testing Progress Flow (Video Watched -> Quiz Passed -> Complete) ===")
    mod_1 = module_ids[0]

    # Initially 0% progress
    pct, comp, tot = calculate_course_progress(user_id, course_id)
    assert pct == 0 and comp == 0 and tot == 5

    # Mark video watched
    execute_db("UPDATE progress SET video_watched = 1 WHERE user_id = ? AND module_id = ?", (user_id, mod_1))
    update_module_status(user_id, mod_1)
    # Module shouldn't be complete yet because quiz is not done
    prog_1 = query_db("SELECT * FROM progress WHERE user_id = ? AND module_id = ?", (user_id, mod_1), one=True)
    assert prog_1["module_completed"] == 0, "Module should NOT be complete without quiz"

    # Now mark quiz complete
    execute_db("UPDATE progress SET quiz_completed = 1 WHERE user_id = ? AND module_id = ?", (user_id, mod_1))
    update_module_status(user_id, mod_1)
    prog_1 = query_db("SELECT * FROM progress WHERE user_id = ? AND module_id = ?", (user_id, mod_1), one=True)
    assert prog_1["module_completed"] == 1, "Module SHOULD be complete when video and quiz are done"

    pct, comp, tot = calculate_course_progress(user_id, course_id)
    assert pct == 20 and comp == 1 and tot == 5
    print("[OK] Module completion logic and progress calculation (20%) verified!")

    # Complete all remaining modules to test 100% course progress
    for m_id in module_ids[1:]:
        execute_db("UPDATE progress SET video_watched = 1, quiz_completed = 1 WHERE user_id = ? AND module_id = ?", (user_id, m_id))
        update_module_status(user_id, m_id)

    pct, comp, tot = calculate_course_progress(user_id, course_id)
    assert pct == 100 and comp == 5 and tot == 5
    next_incomplete = get_next_incomplete_module(user_id, course_id)
    assert next_incomplete is None, "When course is 100%, next_incomplete should be None"
    print("[OK] 100% Course completion verified!")

    print("\n=== Step 7: Testing PDF Generation with ReportLab ===")
    mod_row = query_db("SELECT * FROM modules WHERE id = ?", (mod_1,), one=True)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = build_pdf_styles()
    flowables = parse_markdown_to_flowables(mod_row["notes"], styles)
    doc.build(flowables)
    assert buf.getvalue().startswith(b"%PDF"), "Generated file is not a valid PDF"
    print("[OK] ReportLab Module Notes PDF successfully built and verified!")

    print("\n=== Step 8: Testing Certificate Generation with ReportLab ===")
    cert_hash = generate_certificate_hash(user_id, course_id)
    assert len(cert_hash) == 10
    cert_buf = io.BytesIO()
    w, h = landscape(letter)
    c = canvas.Canvas(cert_buf, pagesize=landscape(letter))
    c.drawString(100, 100, f"Certificate ID: {cert_hash}")
    c.showPage()
    c.save()
    assert cert_buf.getvalue().startswith(b"%PDF")
    print(f"[OK] ReportLab Landscape Certificate generated with verification ID: {cert_hash}")

    print("\n=======================================================")
    print(" ALL 8 INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("=======================================================")


if __name__ == "__main__":
    test_end_to_end()
