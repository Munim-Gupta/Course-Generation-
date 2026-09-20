"""
app.py
======
Deployment entry point alias for WSGI servers (like Gunicorn on Render/Railway).
Exposes the Flask 'app' instance from main.py so both 'gunicorn main:app'
and 'gunicorn app:app' work seamlessly.
"""

from main import app

if __name__ == "__main__":
    app.run()
