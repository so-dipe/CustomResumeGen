from flask import Flask
from datetime import timedelta
from flask_session import Session
from config.config import Config
from .auth.linkedin import auth_bp
from .auth.google import google_auth_bp


# Create the Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Set the preferred URL scheme to 'https'
app.config["PREFERRED_URL_SCHEME"] = "https"

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "cookie"
app.permanent_session_lifetime = timedelta(days=7)

# # Initialize Flask-Session extension
# Session(app)

# Register the auth_bp Blueprint
# app.register_blueprint(auth_bp)
app.register_blueprint(google_auth_bp)

# autopep8: off
from app import routes

# autopep8: on
