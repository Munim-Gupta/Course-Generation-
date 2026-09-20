"""
Register.py
===========
Purpose:
    Handles new user account registration, including input validation,
    email format verification, duplicate email checks, secure password hashing
    using Werkzeug, and database persistence.

Viva Talking Points:
    - Implements the Registration flow in the Model-View-Controller pattern.
    - Security: Passwords are NEVER stored in plain text. Uses PBKDF2/SHA256 via Werkzeug.
    - Input sanitization: Strips whitespace and verifies regex email format.
    - Database integrity: Validates uniqueness against the 'users' table before insertion.
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from Database_Connection import query_db, execute_db

register_bp = Blueprint("register", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    """Renders the registration form and processes new user submissions."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # 1. Validation: Ensure all fields are filled
        if not name or not email or not password or not confirm_password:
            flash("All fields are required. Please fill out the entire form.", "danger")
            return render_template("register.html", name=name, email=email)

        # 2. Validation: Email format check
        if not re.match(EMAIL_REGEX, email):
            flash("Invalid email format. Please enter a valid email address.", "danger")
            return render_template("register.html", name=name, email=email)

        # 3. Validation: Password confirmation check
        if password != confirm_password:
            flash("Passwords do not match. Please verify and try again.", "danger")
            return render_template("register.html", name=name, email=email)

        # 4. Validation: Minimum password length check
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template("register.html", name=name, email=email)

        # 5. Database check: Verify if email already exists
        existing_user = query_db("SELECT id FROM users WHERE email = ?", (email,), one=True)
        if existing_user:
            flash("An account with this email already exists. Please log in.", "info")
            return redirect(url_for("login.login"))

        # 6. Secure Hashing & Storage
        hashed_password = generate_password_hash(password)
        execute_db(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )

        flash("Registration successful! You may now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")
