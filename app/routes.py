from flask import render_template, request, jsonify, session, redirect, url_for
from app import app
from app.resume.generator import generate_custom_resume
import tiktoken
from config.config import Config
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

config = Config()

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

cred = credentials.Certificate(config.FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()  # Initialize Firestore client

@app.route("/")
def index():
    # Check if the user is logged in using the session variable
    if session.get('logged_in'):
        # If the user is logged in, redirect them to the dashboard
        return redirect(url_for('dashboard'))

    # If the user is not logged in, render the index.html template
    return render_template("index.html")

@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    resume_text = request.form.get("resume")
    job_description = request.form.get("job_description")

    # Check the length of both texts
    total_length = len(encoding.encode(job_description)) + len(encoding.encode(resume_text))

    if total_length > 3500:
        return jsonify({"error": "Combined length of resume and job description is too long."})

    # Call your function to generate custom resume
    generated_resume = generate_custom_resume(job_description, resume_text)

    if session.get('user_info').data['id']:
        user_id = session.get('user_info').data['id']
        save_resume_to_firestore_and_session(user_id, generated_resume)

    return jsonify(generated_resume)

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in using the session variable
    if not session.get('logged_in'):
        return 'Access denied: You are not logged in'

    # Retrieve the User Info dictionary from the session
    user_info = session.get('user_info')

    if user_info:
        # Access user data fields like 'given_name' and 'email' directly
        given_name = user_info.data['given_name']
        email = user_info.data['email']
        # Add other user data fields as needed

        # Store user data in Firestore
        user_id = user_info.data['id']
        user_ref = db.collection('users').document(user_id)

        existing_data = user_ref.get().to_dict()

        if existing_data:
            # Merge existing data with new data
            updated_data = {**existing_data, 'given_name': given_name, 'email': email}
            user_ref.update(updated_data)
        else:
            # Create a new document
            user_ref.set({'given_name': given_name, 'email': email})
        
        return render_template("dashboard.html", user_info=user_info)
    else:
        return 'Failed to fetch user info from OAuth response'
    
@app.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    # Optionally, redirect to a login page or another appropriate route
    return redirect(url_for('index')) 

# Function to save the generated resume to Firestore and session
def save_resume_to_firestore_and_session(user_id, generated_resume):
    # Get the current timestamp using Python's datetime
    timestamp = datetime.now()
    # Save the generated resume to Firestore
    resume_ref = db.collection('users').document(user_id).collection('resumes').document()
    resume_ref.set({
        'content': generated_resume,
        'timestamp': timestamp  # Optional: Add a timestamp
    })

    # Retrieve the user's stored resumes from the session
    user_resumes = session.get('user_resumes', [])

    # Append the generated resume to the list
    user_resumes.append(generated_resume)

    # Ensure that only the latest 10 resumes are stored
    if len(user_resumes) > 10:
        user_resumes = user_resumes[-10:]

    # Store the list of resumes in the user's session
    session['user_resumes'] = user_resumes

