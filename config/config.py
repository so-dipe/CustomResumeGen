import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    DEBUG = True

    # Firebase configuration
    FIREBASE_API_KEY = "your-firebase-api-key"
    FIREBASE_AUTH_DOMAIN = "your-firebase-auth-domain"
    FIREBASE_PROJECT_ID = "your-firebase-project-id"
    # Add other Firebase configuration variables here as needed

    # Database configuration (if you're using one)
    SQLALCHEMY_DATABASE_URI = "your-database-uri"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OPEN AI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # LINKEDIN LOGIN
    LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_ACCESS_TOKEN = os.environ.get("INKEDIN_ACCESS_TOKEN")

    # GOOGLE LOGIN
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    # FIREBASE CREDIENTIALS
    FIREBASE_CRED_PATH = "config/data/serviceAccountKey.json"
