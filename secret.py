from flask import Flask, request, session, redirect, url_for
from flask_session import Session
from config.config import Config
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Set your secret key here

Session(app)


@app.route("/")
def index():
    user_name = session.get("user_name")
    if user_name:
        return f'Hello, {user_name}! <a href="/logout">Logout</a>'
    else:
        return 'You are not logged in. <a href="/login">Login</a>'


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        if user_name:
            session["user_name"] = user_name
            return redirect(url_for("index"))

    return 'Enter your name: <form method="POST"><input type="text" name="user_name"><input type="submit" value="Login"></form>'


@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
