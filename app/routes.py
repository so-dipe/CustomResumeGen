from flask import render_template, request, jsonify, session, redirect, url_for
from app import app
from app.resume.generator import generate_custom_resume
import tiktoken
from config.config import Config
from datetime import datetime
from .db import (
    save_resume_to_firestore_and_session,
    update_or_create_user_data,
    get_next_resume_id,
    get_user_resumes_from_firestore,
    get_last_10_user_resumes,
)

config = Config()

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# db = firestore.client()  # Initialize Firestore client


@app.route("/")
def index():
    # Check if the user is logged in using the session variable
    if session.get("logged_in"):
        # If the user is logged in, redirect them to the dashboard
        return redirect(url_for("dashboard"))

    # If the user is not logged in, render the index.html template
    return render_template("index.html")


@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    resume_text = request.form.get("resume")
    job_description = request.form.get("job_description")

    # Check the length of both texts
    total_length = len(encoding.encode(job_description)) + len(
        encoding.encode(resume_text)
    )

    if total_length > 3500:
        return jsonify(
            {"error": "Combined length of resume and job description is too long."}
        )

    # Call your function to generate a custom resume
    generated_resume = generate_custom_resume(job_description, resume_text)

    # Check if the user is logged in using the session variable
    if "user_info" not in session or "id" not in session["user_info"].data:
        return jsonify({"error": "User is not logged in."})

    user_id = session["user_info"].data["id"]

    resume_id = get_next_resume_id(user_id)

    # Save the generated resume to Firestore and session
    save_resume_to_firestore_and_session(user_id, generated_resume, resume_id)

    return jsonify(generated_resume)


@app.route("/dashboard")
def dashboard():
    # Check if the user is logged in using the session variable
    if not session.get("logged_in"):
        return "Access denied: You are not logged in"

    # Retrieve the User Info dictionary from the session
    user_info = session.get("user_info")

    if user_info:
        # Call the function to update or create user data in Firestore
        update_or_create_user_data(user_info)

        # Retrieve the last 10 user resumes from the session
        user_resumes = session.get("user_resumes", {})

        return render_template(
            "dashboard.html", user_info=user_info, user_resumes=user_resumes
        )
    else:
        return "Failed to fetch user info from OAuth response"


@app.route("/show_more_resumes")
def show_more_resumes():
    # Retrieve the user's ID from the session
    user_id = session.get("user_info").data["id"]

    # Get the current page number from the query parameters (default to 1)
    page = int(request.args.get("page", 1))

    # Define the number of resumes to display per page
    resumes_per_page = 10

    # Retrieve resumes from Firestore with pagination
    user_resumes = get_user_resumes_from_firestore(user_id, page, resumes_per_page)

    # Determine if there are more pages
    has_more = len(user_resumes) > (page * resumes_per_page)

    return render_template(
        "show_more_resumes.html", resumes=user_resumes, page=page, has_more=has_more
    )


@app.route("/logout")
def logout():
    # Clear the user's session
    session.clear()
    # Optionally, redirect to a login page or another appropriate route
    return redirect(url_for("index"))
