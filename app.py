import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from utils import get_db, login_required

# initialises the app
app = Flask(__name__)

# Session automatically is ended when the browser is closed
app.config["SESSION_PERMANENT"] = False

# Configure session to use server side filesystem (instead of client signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Prevent caching
@app.after_request
def after_request(response):
    """Ensure responses are not cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Home route
@app.route("/")
def index():

    #TODO implement a proper home page

    return render_template("index.html")

# Registering route
@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        
        password_hash = generate_password_hash(password)
        print(password_hash)

        db = get_db()
        cursor = db.cursor()
            
        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Username or email already exists", "error")
            return render_template("register.html")
        
        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?);", (username, email, password_hash)
        )

        # Commit the insert
        db.commit()
            
        # Close the connection once finished
        db.close()

        flash("Registration successful, please log in!", "success")
        # Redirect to a login page or home after registration
        return redirect("/login")

    return render_template("register.html")


# Log in route
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # TODO impliment log in system

    return render_template("login.html")

# Log out route
@app.route("/logout")
@login_required
def logout():
    session.clear()

    #Logs user out to the home page
    return redirect("/")
