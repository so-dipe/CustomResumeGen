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

# Function to save the generated resume to Firestore and session


def save_resume_to_firestore_and_session(user_id, generated_resume):
    # Get the current timestamp using Python's datetime
    timestamp = datetime.now()
    print(timestamp)

    # Reference the "resumes" collection for the user and add a new document with auto-generated ID
    resume_ref = (
        db.collection("users")
        .document(user_id)
        .collection("resumes")
        .add({"content": generated_resume, "timestamp": timestamp})
    )

    # Get the auto-generated ID for the newly created document
    _, document_reference = resume_ref  # Unpack the tuple
    resume_id = document_reference.id
    print(resume_id)

    # Save the generated resume to the session
    # save_resume_to_session(generated_resume, resume_id, timestamp)

    # Limit the number of documents in Firestore to 100
    limit_documents_in_firestore(user_id, limit=100)

    return None


def save_resume_to_session(generated_resume, resume_id, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().replace(tzinfo=None)

    # Create a dictionary to store the resume data and its timestamp
    resume_data = {
        "content": generated_resume,
        "timestamp": timestamp.replace(tzinfo=None),
    }

    # Add the resume data to the session
    session["user_resumes"][resume_id] = resume_data

    # If the number of resumes exceeds your desired limit (e.g., 10), remove the oldest ones
    if len(session["user_resumes"]) > 3:
        remove_oldest_resumes(3)


def remove_oldest_resumes(limit):
    # Sort the resumes by timestamp in ascending order
    sorted_resumes = sorted(
        session["user_resumes"].items(), key=lambda x: x[1]["timestamp"]
    )

    # Get the IDs of the oldest resumes to be removed
    oldest_resume_ids = [
        resume[0] for resume in sorted_resumes[: len(session["user_resumes"]) - limit]
    ]

    # Remove the oldest resumes from the session
    for resume_id in oldest_resume_ids:
        del session["user_resumes"][resume_id]


# Function to store the generated resume in the user's session


def get_resumes_from_firestore(user_id, limit=None):
    user_resumes = {}

    # Query the "resumes" collection, order by timestamp in descending order
    resume_query = (
        db.collection("users")
        .document(user_id)
        .collection("resumes")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
    )

    # If a limit is specified, apply the limit to the query
    if limit is not None:
        resume_query = resume_query.limit(limit)

    # Retrieve the documents that match the query
    for doc in resume_query.stream():
        resume_id = doc.id
        resume_data = doc.to_dict()
        user_resumes[resume_id] = resume_data

    return user_resumes


def limit_documents_in_firestore(user_id, limit):
    # Query all resume documents for the user, ordered by timestamp
    resume_query = (
        db.collection("users")
        .document(user_id)
        .collection("resumes")
        .order_by("timestamp")
    )

    # Get the total number of documents
    total_documents = list(resume_query.stream())

    # If the total number of documents exceeds the limit, delete the oldest documents
    if len(total_documents) > limit:
        documents_to_delete = resume_query.limit(len(total_documents) - limit).stream()
        for doc in documents_to_delete:
            doc.reference.delete()


def update_or_create_user_data(user_info):
    # Access user data fields like 'given_name' and 'email' directly
    given_name = user_info["given_name"]
    email = user_info["email"]
    # Add other user data fields as needed

    # Get the user's ID from the user_info data
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
