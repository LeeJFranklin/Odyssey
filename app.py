from flask import Flask
from flask_session import Session

from routes import init_routes
from api import init_api_routes
from utils import after_request, close_db

# initialises the app
app = Flask(__name__)

# Session automatically is ended when the browser is closed
app.config["SESSION_PERMANENT"] = False

# Configure session to use server side filesystem (instead of client signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Prevent caching
app.after_request(after_request)

# Database teardown
app.teardown_appcontext(close_db)

# Register routes
init_routes(app)
init_api_routes(app)

if __name__ == "__main__":
    app.run(debug=True)