# Course Generation Website

A complete, modular, beginner-friendly **Course Generation Web Application** built using **Python, Flask, SQLite, Bootstrap 5, and ReportLab**.

This project is tailored specifically for college academic submissions and viva presentations. It runs **100% locally with zero external or paid AI APIs**, using a Python rule engine, structured knowledge templates, and a curated question bank.

---

## 🌟 Key Features

1. **User Authentication & Security**:
   - Secure registration with email validation and duplicate checking.
   - Industry-standard password hashing using `werkzeug.security`.
   - Flask session management with protected routes (`@login_required`).

2. **Automated Course & Notes Generation (Zero AI API)**:
   - Topic knowledge engine supporting Python, HTML, CSS, JavaScript, SQL, Java, C++, and DBMS.
   - Dynamic algorithmic fallback for any custom or novel topic.
   - Multi-section student-friendly notes with syntax, practical code snippets, expected outputs, and viva takeaways.
   - Verified educational video tutorials embedded into every module.

3. **Automated 15-Question Quiz Generator**:
   - Every module automatically generates **exactly 15 questions**.
   - Balanced distribution: **8 Multiple Choice (MCQ)**, **4 True/False**, and **3 Short Answer**.
   - Random sampling from `question_bank.json` with cascading fallback templates to guarantee no duplicates and a 15-question quota.

4. **Progress Tracking**:
   - Tracks **Video Watched** and **Quiz Completed** states per module.
   - Modules reach complete status only when both requirements are met.
   - Interactive progress bars on dashboard, course views, and module pages.
   - One-click "Continue Course" to jump straight to the first incomplete module.

5. **In-Memory PDF Generation & Academic Certificate**:
   - Export full course syllabus or individual module notes as PDF.
   - Gated **Certificate of Achievement** unlocked strictly upon 100% course completion.
   - Generated with ReportLab with dual borders, student name, unique verification hash, and signature blocks.

---

## 🏗️ Project Architecture

```text
Project College/
│
├── main.py                     # Entry point, app factory, blueprint registration
│
├── Login.py                    # User login route & session management
├── Register.py                 # Registration, validation, Werkzeug password hashing
├── Database_Connection.py      # SQLite connection & auto-table creation
├── Dashboard.py                # Student dashboard & aggregate analytics
├── Generate_Course.py          # Course generation route handler
├── Course_Generator_Engine.py  # Local knowledge engine & notes generator
├── Module.py                   # Module viewer, video embed, pagination
├── Quiz.py                     # 15-question quiz taking & evaluation logic
├── Quiz_Generator.py           # 15-question generator (8 MCQ, 4 T/F, 3 Short) + fallbacks
├── Progress.py                 # Progress tracking helpers & mark-watched route
├── Logout.py                   # Session termination
├── PDF_Generator.py            # ReportLab PDF notes & syllabus export
├── Certificate.py              # ReportLab landscape certificate generator
│
├── question_bank.json          # Predefined question bank for CS & IT topics
├── requirements.txt            # Minimal dependencies (Flask, Werkzeug, reportlab)
├── README.md                   # Project documentation & viva guide
├── .gitignore                  # Git ignore rules
│
├── templates/
│   ├── base.html               # Base layout, navbar, flash alerts, footer
│   ├── index.html              # Homepage with feature showcases
│   ├── login.html              # User login form
│   ├── register.html           # User registration form
│   ├── dashboard.html          # Student learning dashboard & course cards
│   ├── generate_course.html    # Course creation form with topic quick-picks
│   ├── course.html             # Full course syllabus & module list
│   ├── module.html             # Module study page with notes & video player
│   ├── quiz.html               # 15-question quiz interface
│   ├── quiz_result.html        # Score review & question-by-question breakdown
│   └── certificate.html        # Web preview of completion certificate
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom styling complementing Bootstrap 5
│   ├── js/
│   │   └── script.js           # Interactive validation & quiz answer tracker
│   └── images/                 # Image assets
│
└── instance/
    └── course_generator.db     # SQLite database (auto-created on first run)
```

---

## 💻 Installation & Running (Windows / VS Code)

### 1. Open Terminal in VS Code
Open the project folder `Project College` in VS Code, then open a PowerShell terminal:

### 2. Create Virtual Environment (Optional but recommended)
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
```bash
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 5. Run the Application
```bash
python main.py
```

### 6. Open in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🗄️ Database Schema

The application automatically creates `instance/course_generator.db` on startup with 6 normalized tables:

1. **`users`**: `id`, `name`, `email`, `password` (hashed), `created_at`
2. **`courses`**: `id`, `user_id`, `title`, `topic`, `difficulty`, `duration`, `module_count`, `created_at`
3. **`modules`**: `id`, `course_id`, `module_number`, `title`, `notes`, `video_url`, `created_at`
4. **`questions`**: `id`, `module_id`, `question`, `question_type`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_answer`
5. **`quiz_attempts`**: `id`, `user_id`, `module_id`, `score`, `total_questions`, `attempted_at`
6. **`progress`**: `id`, `user_id`, `module_id`, `video_watched`, `quiz_completed`, `module_completed` (Unique constraint on `user_id, module_id`)

---

## 🎓 College Viva Preparation Guide

### Q1: Why does this project not use an external AI API (like OpenAI or Gemini)?
> **Answer**: External AI APIs require paid subscriptions, API keys, and internet connectivity, which can fail, run out of credits, or suffer from latency. This system is designed as an autonomous, 100% deterministic academic platform using pure Python logic, templates, and a curated JSON question bank.

### Q2: How does the Quiz Generator guarantee exactly 15 questions?
> **Answer**: The algorithm in `Quiz_Generator.py` employs a 3-tier cascade:
> 1. Filters `question_bank.json` by matching the requested topic and difficulty.
> 2. Partitions questions into MCQ, True/False, and Short Answer pools.
> 3. If any pool has fewer than its target (8 MCQ, 4 T/F, 3 Short Answer), it invokes dynamic algorithmic template functions (`generate_template_mcq`, `generate_template_tf`, `generate_template_short`) based on module concepts to fulfill the exact 15-question quota.

### Q3: How is student progress computed?
> **Answer**: In `Progress.py`, a module is only marked completed when `video_watched == 1` AND `quiz_completed == 1`. The course progress is then calculated as `(completed_modules / total_modules) * 100`.

### Q4: How is security handled?
> **Answer**: Passwords are never stored in plain text; they are hashed using PBKDF2/SHA-256 via `werkzeug.security.generate_password_hash`. All database queries use parameterized SQL inputs (`?`) to prevent SQL Injection, and route decorators (`@login_required`) prevent unauthorized access.

### Q5: How are PDFs generated without third-party web services?
> **Answer**: We use Python's open-source `ReportLab` library. In `PDF_Generator.py` and `Certificate.py`, the documents are rendered using vector drawing and Flowable objects directly in an in-memory `io.BytesIO` buffer, served to the client via Flask's `send_file`.
