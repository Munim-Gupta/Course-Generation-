"""
Database_Connection.py
======================
Purpose:
    Manages SQLite database connection, table initialization, and helper functions
    for safe SQL query execution across the application.

Viva Talking Points:
    - Uses SQLite, a lightweight serverless relational database stored as a local file.
    - Foreign keys are enabled explicitly using 'PRAGMA foreign_keys = ON'.
    - Implements parameterized queries to prevent SQL Injection attacks.
    - Uses sqlite3.Row so query results can be accessed like Python dictionaries.
"""

import os
import sqlite3

# Define the path to the database file inside the 'instance' folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DB_PATH = os.path.join(INSTANCE_DIR, "course_generator.db")


def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Sets row_factory to sqlite3.Row for dictionary-like column access.
    """
    # Ensure the instance directory exists
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Creates all required tables automatically if they do not already exist.
    Called once during application startup in main.py.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            duration TEXT NOT NULL,
            module_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 3. modules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            module_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            notes TEXT NOT NULL,
            video_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
        );
    """)

    # 4. questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            question_type TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT NOT NULL,
            FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
        );
    """)

    # 5. quiz_attempts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
        );
    """)

    # 6. progress table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            video_watched INTEGER DEFAULT 0,
            quiz_completed INTEGER DEFAULT 0,
            module_completed INTEGER DEFAULT 0,
            UNIQUE(user_id, module_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
        );
    """)

    # Dynamic migrations for Final Certification Quiz
    for migration in [
        "ALTER TABLE questions ADD COLUMN course_id INTEGER DEFAULT 0;",
        "ALTER TABLE quiz_attempts ADD COLUMN course_id INTEGER DEFAULT 0;",
        "ALTER TABLE quiz_attempts ADD COLUMN passed INTEGER DEFAULT 0;"
    ]:
        try:
            cursor.execute(migration)
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def query_db(query, args=(), one=False):
    """
    Helper function to query the database.
    Returns a single Row if one=True, else a list of Rows.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query, args=()):
    """
    Helper function to execute INSERT, UPDATE, or DELETE queries.
    Returns the last inserted row ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id
