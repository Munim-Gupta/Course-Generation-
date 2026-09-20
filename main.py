"""
main.py
=======
Purpose:
    Primary entry point for the Course Generator application. Configures the Flask
    runtime, initializes the SQLite database schema on startup, registers all feature
    blueprints, and provides global error handlers.

Viva Talking Points:
    - Modular Architecture: Each feature is encapsulated in a dedicated Blueprint
      (Authentication, Course Generation, Engine, Quizzes, Progress, PDF, Certificates).
    - Lifecycle Hooks: Automatically invokes init_db() on startup to ensure database tables
      are initialized without manual intervention.
    - Zero External AI/API: Generates dynamic courses and quizzes completely locally.
    - Defensive Programming: Catches HTTP 404 and 500 errors with friendly user notifications.
"""

import os
from flask import Flask, render_template, session, redirect, url_for

# Import database initialization
from Database_Connection import init_db

# Import feature blueprints
from Login import login_bp
from Register import register_bp
from Logout import logout_bp
from Dashboard import dashboard_bp
from Generate_Course import generate_course_bp
from Module import module_bp
from Quiz import quiz_bp
from Progress import progress_bp
from PDF_Generator import pdf_bp
from Certificate import certificate_bp


def create_app():
    """Application factory pattern to configure and bootstrap the Flask application."""
    app = Flask(__name__)

    # Cryptographic secret key for signing session cookies
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "course-generator-secret-key-college-2026")

    # Initialize SQLite database and tables automatically
    with app.app_context():
        init_db()

    # Register blueprints for modular routing
    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(generate_course_bp)
    app.register_blueprint(module_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(certificate_bp)

    # Home route
    @app.route("/")
    def index():
        """Redirects authenticated users to the dashboard or renders the homepage."""
        if "user_id" in session:
            return redirect(url_for("dashboard.dashboard"))
        return render_template("index.html")

    # Global context processor for session details
    @app.context_processor
    def inject_user():
        return {
            "current_user_id": session.get("user_id"),
            "current_user_name": session.get("user_name"),
            "current_user_email": session.get("user_email")
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("base.html", custom_error="The requested page could not be found. (404)"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("base.html", custom_error="An unexpected server error occurred. Please try again later. (500)"), 500

    return app


app = create_app()

if __name__ == "__main__":
    print("==================================================================")
    print(" Course Generation Website Starting...")
    print(" Zero AI API / Local Python Engine & 15-Question Quiz Generator")
    print(" Running at: http://127.0.0.1:5000")
    print("==================================================================")
    app.run(debug=True, host="127.0.0.1", port=5000)
