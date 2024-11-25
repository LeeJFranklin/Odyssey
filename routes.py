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

    # Suprise location planning route
    @app.route("/plan_trip_here", methods=["GET", "POST"])
    @login_required
    def plan_trip_here():
        
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        if request.method == "POST":
            city = request.form.get("hidden-city-input")
            country = request.form.get("hidden-country-input")

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
        
        cursor.execute(
            "SELECT * FROM itinerary WHERE trip_id = ? AND user_id = ? ORDER BY entry_date ASC, entry_time ASC;",
            (trip_id, session["user_id"])
        )
        itinerary = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM packing_list WHERE trip_id = ? AND user_id = ?;",
            (trip_id, session["user_id"])
        )

        packing_list = cursor.fetchall()

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

        return render_template("planner.html", trip=trip, itinerary=itinerary, packing_list=packing_list)
    
    # Planner page itinerary section
    @app.route("/itinerary/<int:trip_id>", methods=["GET", "POST"])
    @login_required
    def itinerary(trip_id):
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        if request.method == "POST":
            # Extract fields from the form
            itinerary_date = request.form.get("itinerary-date")
            itinerary_time = request.form.get("itinerary-time")
            itinerary_info = request.form.get("itinerary-info")
            itinerary_cost = request.form.get("itinerary-cost")

            # Check if these fields are blank (e.g., triggered by the delete button)
            if not itinerary_date and not itinerary_time and not itinerary_info and not itinerary_cost:
                # Likely a misrouted delete form submission; ignore this POST
                flash("Invalid entry data. Action ignored.", "error")
            else:
                # Enter entry into the itinerary table
                cursor.execute(
                    "INSERT INTO itinerary (trip_id, user_id, entry_date, entry_time, entry_info, entry_cost) VALUES (?, ?, ?, ?, ?, ?);",
                    (trip_id, session["user_id"], itinerary_date, itinerary_time, itinerary_info, itinerary_cost)
                )

                db.commit()

                return redirect(url_for("planner", trip_id=trip_id))

        return render_template("planner.html")
    
    @app.route("/delete_itinerary_entry/<int:entry_id>", methods=["POST"])
    @login_required
    def delete_itinerary_entry(entry_id):
        db = get_db()
        cursor = db.cursor()

        # Retrieve trip_id from the form
        trip_id = request.form.get("delete-entry-value")

        if not trip_id:
            flash("Trip ID is missing. Cannot delete entry.", "error")
            return redirect(url_for("home"))

        # Ensure the entry belongs to the user and is part of the specified trip
        cursor.execute(
            "SELECT * FROM itinerary WHERE id = ? AND trip_id = ? AND user_id = ?;",
            (entry_id, trip_id, session["user_id"])
        )
        entry = cursor.fetchone()

        if not entry:
            flash("Entry not found or you don't have permission to delete it.", "error")
            return redirect(url_for("planner", trip_id=trip_id))

        # Delete the entry
        cursor.execute(
            "DELETE FROM itinerary WHERE id = ? AND trip_id = ? AND user_id = ?;",
            (entry_id, trip_id, session["user_id"])
        )
        db.commit()

        flash("Entry deleted successfully.", "success")
        return redirect(url_for("planner", trip_id=trip_id))


    
    # Planner page packing_list section
    @app.route("/packing_list/<int:trip_id>", methods=["GET", "POST"])
    @login_required
    def packing_list(trip_id):
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        if request.method == "POST":
            # Extract fields from the form
            item = request.form.get("packing-item")
            amount = request.form.get("packing-amount")
            packed = request.form.get("packing-packed")

            # Enter entry into the packing_list table
            cursor.execute(
                "INSERT INTO packing_list (trip_id, user_id, item, amount, packed) VALUES (?, ?, ?, ?, ?);",
                (trip_id, session["user_id"], item, amount, packed)
            )

            db.commit()

            return redirect(url_for("planner", trip_id=trip_id))

        return render_template("planner.html")
    
    # Planner page delete trip route
    @app.route("/delete_trip/<int:trip_id>", methods=["POST"])
    @login_required
    def delete_trip(trip_id):
        db = get_db()
        db.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = db.cursor()

        if request.method == "POST":
            cursor.execute(
                "DELETE FROM trips WHERE id = ? AND user_id = ?;", (trip_id, session["user_id"])
            )
            db.commit()

            return redirect(url_for("home"))


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
    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        
        if request.method == "POST":
            db = get_db()
            db.row_factory = sqlite3.Row  # Enable dictionary-like row access
            cursor = db.cursor()

            password = request.form.get("current-password")
            new_password = request.form.get("new-password")
            confirm_password = request.form.get("confirm-password")

            cursor.execute(
                "SELECT password_hash FROM users WHERE id = ?;", (session["user_id"],)
            )
            user = cursor.fetchone()

            if not check_password_hash(user["password_hash"], password):
                flash("Password is incorrect", "error")
                return redirect(url_for("login"))
            elif new_password != confirm_password:
                flash("Passwords do not match", "error")
                return redirect(url_for("login"))
            else:
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?;", (generate_password_hash(new_password), session["user_id"])
                )
                db.commit()
                
                return redirect(url_for("home"))

        return render_template("settings.html")
    
    # Delete account route
    @app.route("/delete_account", methods=["GET", "POST"])
    @login_required
    def delete_account():
        if request.method == "POST":
            db = get_db()
            db.row_factory = sqlite3.Row  # Enable dictionary-like row access
            cursor = db.cursor()

            cursor.execute(
                "DELETE FROM users WHERE id = ?;", (session["user_id"],)
            )
            db.commit()
            session.clear()
            return redirect("/")
        
        return render_template("settings.html")

    # Log out route
    @app.route("/logout")
    @login_required
    def logout():
        session.clear()
        # Logs user out to the home page
        return redirect("/")