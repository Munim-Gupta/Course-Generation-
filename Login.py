"""
Login.py
========
Purpose:
    Handles user authentication, credentials verification using secure password
    hashing, Flask session creation, and provides the login_required decorator
    to protect private pages from unauthorized access.

Viva Talking Points:
    - Session-based authentication: Stores user_id and user_name in cryptographically signed cookies.
    - Security: Uses werkzeug.security.check_password_hash to protect against timing attacks.
    - Route protection: Uses a custom Python decorator (@login_required) using functools.wraps.
    - Authorization check: Prevents unauthenticated users from accessing courses, quizzes, or certificates.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from Database_Connection import query_db

login_bp = Blueprint("login", __name__)


def login_required(f):
    """
    Decorator to protect routes requiring authentication.
    Redirects unauthenticated users to the login page with a flash warning.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    """Renders login form and verifies user credentials."""
    # If user is already logged in, send them straight to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", email=email)

        # Lookup user by email
        user = query_db("SELECT * FROM users WHERE email = ?", (email,), one=True)

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html", email=email)

        # Set session state
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        flash(f"Welcome back, {user['name']}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.dashboard"))

    return render_template("login.html")
