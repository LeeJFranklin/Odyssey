import requests
import sqlite3

from bs4 import BeautifulSoup
from flask import g, redirect, session
from functools import wraps
from urllib.parse import quote

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

# Wiki scraping tool
def info_scraper(loc):
    # Safely encode the location to handle special characters
    encoded_location = quote(loc.replace(" ", "_"))
    url = f"https://en.wikipedia.org/wiki/{encoded_location}"
    
    try:
        # Send a request to the Wikipedia page
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP issues
        
        # Parse the page content
        soup = BeautifulSoup(response.text, "html.parser")
        
        paragraphs = soup.find_all("p")
        
        # Check if we are getting any paragraphs at all
        if not paragraphs:
            return "No paragraphs found on this page."

        # Extract and return the first non-empty paragraph
        for paragraph in paragraphs:
            text = paragraph.text.strip()
            if text:
                return text  # Return the first meaningful paragraph found
        
        # In case all paragraphs are empty
        return "No meaningful content found in the paragraphs."
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Wikipedia: {e}")
        return "Could not retrieve data due to a network error."
