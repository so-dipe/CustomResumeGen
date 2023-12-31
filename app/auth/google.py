from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    session,
    # make_response,
    # render_template,
)
from flask_oauthlib.client import OAuth
from config.config import Config
from app.db import get_resumes_from_firestore

config = Config()

google_auth_bp = Blueprint("google_auth", __name__, url_prefix="/auth")

oauth = OAuth()
google = oauth.remote_app(
    "google",
    consumer_key=config.GOOGLE_CLIENT_ID,
    consumer_secret=config.GOOGLE_CLIENT_SECRET,
    request_token_params={
        "scope": "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email",
    },
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
)


@google_auth_bp.route("/google")
def login_google():
    print(url_for(".authorized_google", _external=True))
    if config.FLASK_ENV == "DEV":
        if config.CODESPACE:
            return google.authorize(
                callback="https://shiny-space-spoon-wq9jrxx96jpc5jx9-5000.app.github.dev/auth/google/authorized"
            )
        else:
            return google.authorize(
                callback=url_for(".authorized_google", _external=True)
            )
    else:
        return google.authorize(callback=url_for(".authorized_google", _external=True))


@google_auth_bp.route("/google/authorized")
def authorized_google():
    response = google.authorized_response()
    if response is None or response.get("access_token") is None:
        return "Access denied: reason={} error={}".format(
            request.args["error_reason"], request.args["error_description"]
        )

    # Store only necessary information from the OAuth response in the session
    session["google_token"] = response.get("access_token")
    session["logged_in"] = True

    # Retrieve the User Info from Google
    user_info = google.get("userinfo")
    if user_info:
        session["user_info"] = user_info.data
        print(session["user_info"])

        # Retrieve the user's ID
        user_id = user_info.data["id"]

        # Store the last 10 resumes in the session
        # session["user_resumes"] = get_resumes_from_firestore(user_id, limit=3)

        # Redirect the user to the dashboard
        return redirect(url_for("dashboard"))
    else:
        return "Failed to fetch user info from Google"


@google.tokengetter
def get_google_oauth_token():
    return session.get("google_token")
