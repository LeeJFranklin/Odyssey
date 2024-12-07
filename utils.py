import re
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

        exclude_phrases = [
            "This is an accepted version of this page", 
            "Cork or CORK may refer to:",
            "d)",
            "ˈheɾɑ] ⓘ) ",
            "ʒɐˈneɾu] ⓘ)",
            "Z-goh, GLASS- ; Scottish Gaelic: Glaschu ) "
            ]

        # Extract and return the first non-empty paragraph
        result = []

        # Compile a regex pattern for exclusion based on the list of phrases
        exclude_pattern = re.compile("|".join(re.escape(phrase) for phrase in exclude_phrases), re.IGNORECASE)

        for paragraph in paragraphs:
            # Clean the text (remove references like [1] or (1))
            text = re.sub(r"\[.*?\]|\(.*?\)", "", paragraph.text).strip()

            # Skip paragraphs that match any of the excluded phrases
            if text and not exclude_pattern.search(text):
                result.append(text)  # Add meaningful paragraph to the result
            if len(result) == 2:  # Stop after collecting the first 2 valid paragraphs
                break
        
        return " ".join(result)  # Combine the first two paragraphs into one string
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Wikipedia: {e}")
        return "Could not retrieve data due to a network error."
