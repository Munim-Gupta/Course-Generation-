"""
scratch/test_flask_app.py
=========================
Comprehensive Flask test client script verifying all HTTP routes,
authentication sessions, course generation, quiz submissions, and PDF downloads.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from Database_Connection import query_db, execute_db


def test_flask_routes():
    print("=== Testing Flask Application End-to-End ===")
    app.config["TESTING"] = True
    client = app.test_client()

    # 1. Homepage
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200 for /, got {res.status_code}"
    assert b"Generate Structured Courses" in res.data
    print("[OK] GET / renders index.html")

    # 2. Registration Page
    res = client.get("/register")
    assert res.status_code == 200
    assert b"Create an Account" in res.data
    print("[OK] GET /register renders register.html")

    # 3. Post Registration
    test_email = "alex_student@college.edu"
    execute_db("DELETE FROM users WHERE email = ?", (test_email,))
    res = client.post("/register", data={
        "name": "Alex Student",
        "email": test_email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Registration successful" in res.data
    print("[OK] POST /register successfully registered user and redirected to login")

    # 4. Login Page
    res = client.get("/login")
    assert res.status_code == 200
    assert b"Welcome Back" in res.data
    print("[OK] GET /login renders login.html")

    # 5. Post Login
    res = client.post("/login", data={
        "email": test_email,
        "password": "Password123!"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Hello, Alex Student" in res.data
    print("[OK] POST /login logged in and redirected to dashboard")

    # 6. Dashboard
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"Student Dashboard" in res.data
    print("[OK] GET /dashboard renders dashboard metrics")

    # 7. Generate Course Form
    res = client.get("/generate_course")
    assert res.status_code == 200
    assert b"Generate a New Course" in res.data
    print("[OK] GET /generate_course renders course generator form")

    # 8. Post Course Generation (Python Beginner 5 Modules)
    res = client.post("/generate_course", data={
        "topic": "Python",
        "difficulty": "Beginner",
        "duration": "4 Weeks",
        "module_count": "5"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Python - Beginner Masterclass" in res.data
    print("[OK] POST /generate_course generated course, 5 modules, and redirected to syllabus")

    # Grab the course and first module
    user_row = query_db("SELECT id FROM users WHERE email = ?", (test_email,), one=True)
    user_id = user_row["id"]
    course_row = query_db("SELECT * FROM courses WHERE user_id = ? ORDER BY id DESC", (user_id,), one=True)
    course_id = course_row["id"]

    modules = query_db("SELECT * FROM modules WHERE course_id = ? ORDER BY module_number ASC", (course_id,))
    assert len(modules) == 5
    mod_1 = modules[0]
    mod_1_id = mod_1["id"]

    # 9. View Course Syllabus
    res = client.get(f"/course/{course_id}")
    assert res.status_code == 200
    assert b"Curriculum Modules" in res.data
    print(f"[OK] GET /course/{course_id} displays course syllabus")

    # 10. View Module
    res = client.get(f"/module/{mod_1_id}")
    assert res.status_code == 200
    assert mod_1["title"].replace("&", "&amp;").encode() in res.data or mod_1["title"].encode() in res.data
    print(f"[OK] GET /module/{mod_1_id} displays module notes and video player")

    # 11. Mark Video Watched
    res = client.post(f"/mark_video_watched/{mod_1_id}", follow_redirects=True)
    assert res.status_code == 200
    assert b"Video marked as watched" in res.data
    print(f"[OK] POST /mark_video_watched/{mod_1_id} updated video watched state")

    # 12. View 15-Question Quiz
    res = client.get(f"/quiz/{mod_1_id}")
    assert res.status_code == 200
    assert b"Question 15 of 15" in res.data
    print(f"[OK] GET /quiz/{mod_1_id} renders exactly 15 questions")

    # 13. Submit Quiz with answers
    questions = query_db("SELECT * FROM questions WHERE module_id = ? ORDER BY id ASC", (mod_1_id,))
    assert len(questions) == 15
    quiz_data = {}
    for q in questions:
        quiz_data[f"question_{q['id']}"] = q["correct_answer"]

    res = client.post(f"/quiz/{mod_1_id}", data=quiz_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Quiz Completed!" in res.data
    assert b"/ 15" in res.data
    assert b"100%" in res.data
    print(f"[OK] POST /quiz/{mod_1_id} evaluated 15 answers, saved attempt, and rendered results (15/15, 100%)")

    # 14. Download Module Notes PDF
    res = client.get(f"/download_module_pdf/{mod_1_id}")
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert res.data.startswith(b"%PDF")
    print(f"[OK] GET /download_module_pdf/{mod_1_id} returns valid PDF")

    # 15. Download Course Syllabus PDF
    res = client.get(f"/download_course_pdf/{course_id}")
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert res.data.startswith(b"%PDF")
    print(f"[OK] GET /download_course_pdf/{course_id} returns valid full course PDF")

    # 16. Verify Certificate is locked before 100% completion
    res = client.get(f"/certificate/{course_id}", follow_redirects=True)
    assert res.status_code == 200
    assert b"You must complete all" in res.data
    print(f"[OK] GET /certificate/{course_id} properly locks certificate before 100% completion")

    # 17. Complete remaining 4 modules to reach 100%
    for m in modules[1:]:
        execute_db("UPDATE progress SET video_watched = 1, quiz_completed = 1, module_completed = 1 WHERE user_id = ? AND module_id = ?", (user_id, m["id"]))

    # 18. View Certificate now that it is unlocked!
    res = client.get(f"/certificate/{course_id}")
    assert res.status_code == 200
    assert b"CERTIFICATE OF ACHIEVEMENT" in res.data
    assert b"Alex Student" in res.data
    print(f"[OK] GET /certificate/{course_id} unlocks certificate upon 100% completion")

    # 19. Download Certificate PDF
    res = client.get(f"/certificate/download/{course_id}")
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert res.data.startswith(b"%PDF")
    print(f"[OK] GET /certificate/download/{course_id} downloads official landscape PDF certificate")

    # 20. Logout
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    assert b"logged out" in res.data
    print("[OK] GET /logout cleared session and redirected to login")

    print("\n=======================================================")
    print(" ALL 20 FLASK HTTP ROUTE TESTS PASSED WITH 100% SUCCESS! ")
    print("=======================================================")


if __name__ == "__main__":
    test_flask_routes()
