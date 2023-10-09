import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from config.config import Config
from flask import session

config = Config()

# Initialize Firestore
cred = credentials.Certificate(config.FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


def save_resume_to_firestore_and_session(user_id, generated_resume, resume_id):
    # Store the generated resume in the user's session
    store_in_session(user_id, generated_resume)

    # Get the current timestamp using Python's datetime
    timestamp = datetime.now()

    # Save the generated resume to Firestore with the specified resume_id
    resume_ref = (
        db.collection("users")
        .document(user_id)
        .collection("resumes")
        .document(str(resume_id))
    )
    resume_ref.set({"content": generated_resume, "timestamp": timestamp})


# Function to store the generated resume in the user's session


def store_in_session(user_id, generated_resume):
    # Retrieve the user's stored resumes from Firestore
    user_resumes = get_user_resumes_from_firestore(user_id)

    # Ensure that only the latest 100 resumes are stored in Firestore
    if len(user_resumes) >= 100:
        # Remove the oldest resume(s) if the limit is exceeded
        oldest_resume_ids = sorted(user_resumes.keys())[: len(user_resumes) - 99]
        for resume_id in oldest_resume_ids:
            user_resumes.pop(resume_id)

    # Append the generated resume to the list in Firestore
    next_resume_id = str(len(user_resumes) + 1)
    user_resumes[next_resume_id] = generated_resume

    # Store the updated list of resumes in Firestore
    set_user_resumes_in_firestore(user_id, user_resumes)

    # Store the latest 10 resumes in the user's session
    latest_10_resumes = dict(list(user_resumes.items())[-10:])
    session["user_resumes"] = latest_10_resumes


# Function to retrieve user resumes from Firestore


def get_user_resumes_from_firestore(user_id):
    user_resumes = {}
    resume_ref = db.collection("users").document(user_id).collection("resumes").stream()
    for doc in resume_ref:
        resume_id = doc.id
        resume_data = doc.to_dict()
        user_resumes[resume_id] = resume_data["content"]
    return user_resumes


# Function to set user resumes in Firestore


def set_user_resumes_in_firestore(user_id, user_resumes):
    user_resume_ref = db.collection("users").document(user_id).collection("resumes")
    for resume_id, resume_content in user_resumes.items():
        user_resume_ref.document(resume_id).set({"content": resume_content})


def update_or_create_user_data(user_info):
    # Access user data fields like 'given_name' and 'email' directly
    given_name = user_info["given_name"]
    email = user_info["email"]
    # Add other user data fields as needed

    # Get the user's ID from the user_info dictionary
    user_id = user_info["id"]

    # Reference to the user's document in Firestore
    user_ref = db.collection("users").document(user_id)

    existing_data = user_ref.get().to_dict()

    if existing_data:
        # Merge existing data with new data
        updated_data = {**existing_data, "given_name": given_name, "email": email}
        user_ref.update(updated_data)
    else:
        # Create a new document
        user_ref.set({"given_name": given_name, "email": email})


# Implement a function to get the next resume ID for a user


def get_next_resume_id(user_id):
    # Reference to the user's resumes collection
    resumes_ref = db.collection("users").document(user_id).collection("resumes")

    # Query the existing resumes to find the maximum resume ID
    query = resumes_ref.stream()
    last_resume = list(query)  # Convert the generator to a list

    if last_resume:
        # Get the last used resume ID
        last_resume_id = len(last_resume)
        print(last_resume_id)
        # Increment the last used ID by 1 to create the next resume ID
        return last_resume_id + 1
    else:
        # If no resumes are found, start with ID 1
        return 1


# Implement a function to get the last used resume ID for a user


def get_last_resume_id(user_id):
    # Reference to the user's resumes collection
    resumes_ref = db.collection("users").document(user_id).collection("resumes")

    # Query the existing resumes to find the maximum resume ID
    query = resumes_ref.stream()
    last_resume = list(query)

    if last_resume:
        # Get the last used resume ID
        last_resume_id = len(last_resume)
        return last_resume_id
    else:
        # If no resumes are found, return 0 as the default
        return 0


# Modify get_user_resumes_from_firestore to support pagination


def get_user_resumes_from_firestore(user_id, page=1, per_page=10):
    user_resumes = {}
    resume_ref = db.collection("users").document(user_id).collection("resumes")

    # Calculate the starting index based on the current page and per_page
    start_index = (page - 1) * per_page

    # Retrieve resumes with pagination
    resume_query = (
        resume_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(per_page)
        .offset(start_index)
        .stream()
    )

    for doc in resume_query:
        resume_id = doc.id
        resume_data = doc.to_dict()
        user_resumes[resume_id] = resume_data["content"]

    return user_resumes


# Function to get the last 10 user resumes from Firestore.


def get_last_10_user_resumes(user_id):
    user_resumes = {}
    resume_ref = (
        db.collection("users")
        .document(user_id)
        .collection("resumes")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(10)
        .stream()
    )
    for doc in resume_ref:
        resume_id = doc.id
        resume_data = doc.to_dict()
        user_resumes[resume_id] = resume_data["content"]
    return user_resumes
