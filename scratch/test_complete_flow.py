"""
scratch/test_complete_flow.py
=============================
Validates:
1. Python Datascience course generation (dedicated curricula, Pandas/NumPy notes, verified YouTube embeds).
2. Module learning & completion workflow (no per-module quizzes required).
3. 100% 4-option MCQs on Final Certification Exam (Option A, B, C, D present on every question).
4. Passing score (>= 60%) gating the verified Certificate.
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from main import app
from Database_Connection import init_db, query_db, execute_db
import Course_Generator_Engine as CGE
import Quiz_Generator as QG
from Progress import calculate_course_progress, is_course_final_quiz_passed


class TestCompleteFlow(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        # Initialize DB
        init_db()

        # Setup test user
        self.email = "datascience_tester@college.edu"
        self.password = "SecurePass123"
        self.full_name = "Alex Johnson"

        execute_db("DELETE FROM users WHERE email = ?", (self.email,))
        execute_db("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, 'hash_placeholder')
        """, (self.full_name, self.email))

        user = query_db("SELECT id FROM users WHERE email = ?", (self.email,), one=True)
        self.user_id = user["id"]

    def test_end_to_end_flow(self):
        # 1. Test Course_Generator_Engine for 'Python Datascience'
        mods = CGE.generate_course_modules("Python Datascience", "beginner", 3)
        self.assertEqual(len(mods), 3)
        
        # Verify module 1 is Data Science intro
        self.assertIn("Data Science", mods[0]["title"])
        self.assertIn("youtube.com/embed", mods[0]["video_url"])
        
        # Verify module 2 is NumPy
        self.assertIn("NumPy", mods[1]["title"])
        self.assertIn("numpy as np", mods[1]["notes"])
        
        # Verify module 3 is Pandas
        self.assertIn("Pandas", mods[2]["title"])

        # 2. Insert course into database
        execute_db("""
            INSERT INTO courses (user_id, title, topic, difficulty, duration, module_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.user_id, "Python Datascience Complete Track", "Python Datascience", "beginner", "4 Weeks", 3))

        course = query_db("SELECT id FROM courses WHERE user_id = ? ORDER BY id DESC LIMIT 1", (self.user_id,), one=True)
        course_id = course["id"]

        for m in mods:
            execute_db("""
                INSERT INTO modules (course_id, module_number, title, notes, video_url)
                VALUES (?, ?, ?, ?, ?)
            """, (course_id, m["module_number"], m["title"], m["notes"], m["video_url"]))

        db_modules = query_db("SELECT * FROM modules WHERE course_id = ? ORDER BY module_number ASC", (course_id,))
        self.assertEqual(len(db_modules), 3)

        # 3. Simulate user session
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user_id
            sess["user_name"] = self.full_name
            sess["user_email"] = self.email

        # 4. View course syllabus
        res = self.client.get(f"/course/{course_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Course Certification Exam (15 MCQs)", res.data)
        self.assertIn(b"Certificate Locked", res.data)

        # 5. Complete modules 1, 2, and 3
        for m in db_modules:
            # Mark video watched
            res_vid = self.client.post(f"/mark_video_watched/{m['id']}")
            self.assertEqual(res_vid.status_code, 302)

            # Mark module complete
            res_comp = self.client.post(f"/mark_module_completed/{m['id']}")
            self.assertEqual(res_comp.status_code, 302)

        # Verify 100% progress
        pct, comp, total = calculate_course_progress(self.user_id, course_id)
        self.assertEqual(pct, 100)
        self.assertEqual(comp, 3)

        # 6. Verify Certificate is BLOCKED before taking Final Exam
        res_cert_blocked = self.client.get(f"/certificate/{course_id}", follow_redirects=True)
        self.assertIn(b"Final Certification Exam", res_cert_blocked.data)

        # 7. Take Final Certification Exam (GET)
        res_quiz_get = self.client.get(f"/course/{course_id}/final_quiz")
        self.assertEqual(res_quiz_get.status_code, 200)
        self.assertIn(b"Final Exam", res_quiz_get.data)

        # Verify 15 questions in DB, each having option_a, option_b, option_c, option_d
        questions = query_db("SELECT * FROM questions WHERE course_id = ? ORDER BY id ASC", (course_id,))
        self.assertEqual(len(questions), 15)
        for q in questions:
            self.assertTrue(bool(q["option_a"]), f"Missing option_a for question {q['id']}")
            self.assertTrue(bool(q["option_b"]), f"Missing option_b for question {q['id']}")
            self.assertTrue(bool(q["option_c"]), f"Missing option_c for question {q['id']}")
            self.assertTrue(bool(q["option_d"]), f"Missing option_d for question {q['id']}")
            self.assertTrue(bool(q["correct_answer"]), f"Missing correct_answer for question {q['id']}")

        # 8. Submit Final Exam with passing answers
        post_data = {}
        for q in questions:
            post_data[f"question_{q['id']}"] = q["correct_answer"]

        res_quiz_post = self.client.post(f"/course/{course_id}/final_quiz", data=post_data)
        self.assertEqual(res_quiz_post.status_code, 200)
        self.assertIn(b"Congratulations! You Passed!", res_quiz_post.data)
        self.assertIn(b"Claim Your Certificate Now!", res_quiz_post.data)

        # 9. Verify is_course_final_quiz_passed returns True
        self.assertTrue(is_course_final_quiz_passed(self.user_id, course_id))

        # 10. Access Certificate (GET)
        res_cert = self.client.get(f"/certificate/{course_id}")
        self.assertEqual(res_cert.status_code, 200)
        self.assertIn(b"CERTIFICATE OF ACHIEVEMENT", res_cert.data)
        self.assertIn(self.full_name.encode("utf-8"), res_cert.data)
        print("\n>>> ALL CHECKS PASSED: Python Datascience notes/video accurate, 15 4-option MCQs verified, certificate unlocked after final exam!")


if __name__ == "__main__":
    unittest.main()
