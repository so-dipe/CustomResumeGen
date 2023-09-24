from flask import Flask
from flask_session import Session
from config.config import Config
from .auth.linkedin import auth_bp
from .auth.google import google_auth_bp


# Create the Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Register the auth_bp Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(google_auth_bp)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Initialize Flask-Session extension
Session(app)

from app import routes  # Import your route handlers
