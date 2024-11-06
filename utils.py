import sqlite3

from flask import redirect, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_db():
    # Open the database connection within a context manager
    connection = sqlite3.connect("adventure.db")
    connection.row_factory = sqlite3.Row  # Optional: to return rows as dictionaries
    return connection
