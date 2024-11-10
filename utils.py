import sqlite3

from flask import g, redirect, session
from functools import wraps

# Prevent caching
def after_request(response):
    """Ensure responses are not cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Database connection
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("odyssey.db")
        g.db.row_factory = sqlite3.Row
    return g.db

# Database teardown
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

