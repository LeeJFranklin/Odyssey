import sqlite3

from flask import jsonify, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

from utils import get_db, info_scraper, login_required

def init_routes(app):
    # Landing page route
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
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?;", (request.form.get("username"), request.form.get("email")))
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

            # Redirect to home after successful login
            return redirect(url_for("home"))

        return render_template("login.html")

    # Home route
    @app.route("/home", methods=["GET", "POST"])
    @login_required
    def home():
        
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        if request.method == "POST":
            city = request.form.get("city")
            country = request.form.get("country")

            cursor.execute(
                "INSERT INTO trips (user_id, city, country) VALUES (?, ?, ?);",
                (session["user_id"], city.strip(), country.strip())
            )

            # Commit the insert
            db.commit()

            cursor.execute(
                "SELECT id FROM trips WHERE user_id = ? ORDER BY id DESC LIMIT 1;",
                (session["user_id"],)
            )

            trip_id = cursor.fetchone()["id"]  # Fetch the id from the result

            return redirect(url_for("planner", trip_id=trip_id))

        # Fetch the username for the logged-in user based on session user_id
        cursor.execute(
            "SELECT username FROM users WHERE id = ?;", (session["user_id"],)
            )
        user = cursor.fetchone()  # Fetch the first result (single row)
            
        # If user is not found, redirect to login (optional safety check)
        if not user:
            return redirect("/login")
            
        # Fetch previously created trips
        cursor.execute(
                "SELECT id, city, country FROM trips WHERE user_id = ? ORDER BY id ASC;", (session["user_id"],)
            )
        locations = cursor.fetchall()
        
        # Pass the username and locations to the template
        return render_template("home.html", username=user["username"], locations=locations)

    # Planner route
    @app.route("/planner/<int:trip_id>", methods=["GET", "POST"])
    @login_required
    def planner(trip_id):
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        today = date.today().strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD

        # Fetch trip information
        cursor.execute(
            "SELECT * FROM trips WHERE user_id = ? AND id = ?;", (session["user_id"], trip_id)
        )

        trip = cursor.fetchall()

        if not trip:
            # Handle case where trip is not found or unauthorized
            flash("Trip not found or access denied.", "error")
            return redirect(url_for("home"))  # Redirect to a safe route

        if request.method == "POST":
            # Extract fields
            startdate = request.form.get("startdate")
            enddate = request.form.get("enddate")
            transport = request.form.get("transport")
            accommodation = request.form.get("accommodation")
            budget = request.form.get("budget")

            # Update data into trips table
            cursor.execute(
                "UPDATE trips SET startdate = ?, enddate = ?, transport = ?, accommodation = ?, budget = ? WHERE id = ? AND user_id = ?;", 
                (startdate, enddate, transport, accommodation, budget, trip_id, session["user_id"])
            )

            db.commit()

            return redirect(url_for("planner", trip_id=trip_id, min_date=today))

        return render_template("planner.html", trip=trip)
    
    # Planner page itinerary section
    @app.route("/itinerary", methods=["GET", "POST"])
    @login_required
    def itinerary(trip_id):
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM itinerary WHERE trip_id = ? AND user_id = ?;",
            (trip_id, session["user_id"])
        )

        itinerary = cursor.fetchall()

        if request.method == "POST":
            # Extract fields fro the form
            itinerary_date = request.form.get("itinerary-date")
            itinerary_time = request.form.get("itinerary-time")
            itinerary_info = request.form.get("itinerary-info")
            itinerary_cost = request.form.get("itinerary-cost")

            # Enter entry into the itinerary table
            cursor.execute(
                "INSERT INTO itinerary (trip_id, user_id, entry_date, entry_time, entry_info, entry_cost) VALUES (?, ?, ?, ?, ?, ?);",
                (trip_id, session["user_id"], itinerary_date, itinerary_time, itinerary_info, itinerary_cost)
            )

            db.commit()

            return redirect(url_for("planner", trip_id=trip_id))

        return render_template("planner.html", itinerary=itinerary)

    # Home page explore section
    @app.route("/explore", methods=["GET", "POST"])
    @login_required
    def explore():
        location_info = None

        if request.method == "POST":
            if request.get_json():
                # Get the JSON data sent from the frontend
                data = request.get_json()

                # Extract the location from the JSON data
                location = data.get("location")

                if location:
                    # Pass the location to the scraper function
                    location_info = info_scraper(location)
                else:
                    location_info = "No information on this location."

                # Return a JSON response with the location information
                return jsonify({"location_info": location_info})

        # Handle GET requests and render the page
        return render_template("home.html")


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