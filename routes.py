import sqlite3

from flask import render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from utils import get_db, login_required

def init_routes(app):
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
            db = get_db()
            cursor = db.cursor()
                
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (request.form.get("username"), request.form.get("email")))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Username or email already exists", "error")
                return render_template("register.html")
            
            # Insert the new user into the database
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?);", 
                (request.form.get("username"), request.form.get("email"), generate_password_hash(request.form.get("password")))
            )

            # Commit the insert
            db.commit()

            flash("Registration successful, please log in!", "success")
            # Redirect to a login page or home after registration
            return redirect(url_for("login"))

        return render_template("register.html")


    # Log in route
    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Forget any user_id
        session.clear()

        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            db = get_db()
            db.row_factory = sqlite3.Row  # Enable dictionary-like row access
            cursor = db.cursor()
                
            # Check if user and password exists
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?;", (username, )
            )
            user = cursor.fetchone()

            # Check if the user exists
            if not user:
                flash("User does not exist", "error")
                return redirect(url_for("login"))
            
            # Check if the password is correct
            elif not check_password_hash(user["password_hash"], password):
                flash("Password is incorrect", "error")
                return redirect(url_for("login"))

            # Log in the user by storing their id in the session
            session["user_id"] = user["id"]

            # Close the connection once finished
            db.close()

            # Render dashboard template after successful login
            return render_template("dashboard.html")

        return render_template("login.html")

    # Dashboard route
    @app.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        # Fetch the username for the logged-in user based on session user_id
        cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
        user = cursor.fetchone()  # Fetch the first result (single row)
        
        # If user is not found, redirect to login (optional safety check)
        if not user:
            return redirect("/login")
        
        # Pass the username to the template
        return render_template("dashboard.html", username=user["username"])

    # Planner route
    @app.route("/planner")
    @login_required
    def planner():
        #TODO create planner section
        return render_template("planner.html")

    # Explore route
    @app.route("/explore")
    @login_required
    def explore():
        #TODO create explore section
        return render_template("explore.html")

    # Settings route
    @app.route("/settings")
    @login_required
    def favourites():
        #TODO create settings section
        return render_template("settings.html")

    # Log out route
    @app.route("/logout")
    @login_required
    def logout():
        session.clear()
        #Logs user out to the home page
        return redirect("/")