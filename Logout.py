"""
Logout.py
=========
Purpose:
    Handles user logout by completely clearing the session and redirecting
    to the login page.

Viva Talking Points:
    - Session management: session.clear() purges all session cookies on the server side.
    - Security: Prevents session fixation and stale authenticated access.
"""

from flask import Blueprint, redirect, url_for, session, flash

logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout")
def logout():
    """Clears the active session and redirects the user to the login screen."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("login.login"))
