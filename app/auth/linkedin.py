from flask import Blueprint, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
from config.config import Config

config = Config()
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

oauth = OAuth()
linkedin = oauth.remote_app(
    "linkedin",
    consumer_key=config.LINKEDIN_CLIENT_ID,  # 'YourLinkedInClientID',
    consumer_secret=config.LINKEDIN_CLIENT_SECRET,  # 'YourLinkedInClientSecret',
    request_token_params={
        # Define the LinkedIn permissions you need
        "scope": "r_emailaddress r_liteprofile",
    },
    base_url="https://api.linkedin.com/v2/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://www.linkedin.com/oauth/v2/accessToken",
    authorize_url="https://www.linkedin.com/oauth/v2/authorization",
)


@auth_bp.route("/linkedin")
def login():
    # print(url_for('.authorized', _external=True))
    return linkedin.authorize(callback=url_for(".authorized", _external=True))
    # return linkedin.authorize(callback="https://shiny-space-spoon-wq9jrxx96jpc5jx9-5000.app.github.dev/auth/linkedin/authorized")


@auth_bp.route("/linkedin/authorized")
def authorized():
    response = linkedin.authorized_response()
    if response is None or response.get("access_token") is None:
        return "Access denied: reason={} error={}".format(
            request.args["error_reason"], request.args["error_description"]
        )

    session["linkedin_token"] = (response["access_token"], "")
    user_info = linkedin.get("me")
    # Save user_info to your database or session as needed

    return "Logged in as: " + user_info.data["localizedFirstName"]


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get("linkedin_token")


# from flask import Blueprint, request, redirect, url_for, session, flash
# from config.config import Config
# import requests  # Import your User model

# config = Config()
# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# LINKEDIN_CLIENT_ID = config.LINKEDIN_CLIENT_ID
# LINKEDIN_CLIENT_SECRET = config.LINKEDIN_CLIENT_SECRET

# @auth_bp.route('/linkedin')
# def login():
#     # Redirect the user to LinkedIn for authorization
#     print(f"https://www.linkedin.com/oauth/v2/authorization?"
#                     f"response_type=code&"
#                     f"client_id={LINKEDIN_CLIENT_ID}&"
#                     # f"redirect_uri={url_for('.authorized', _external=True)}&"
#                     f"redirect_uri=https://shiny-space-spoon-wq9jrxx96jpc5jx9-5000.app.github.dev/auth/linkedin/authorized&"
#                     f"scope=r_liteprofile%20r_emailaddress")
#     return redirect(f"https://www.linkedin.com/oauth/v2/authorization?"
#                     f"response_type=code&"
#                     f"client_id={LINKEDIN_CLIENT_ID}&"
#                     # f"redirect_uri={url_for('.authorized', _external=True)}&"
#                     f"redirect_uri=https://shiny-space-spoon-wq9jrxx96jpc5jx9-5000.app.github.dev/auth/linkedin/authorized&"
#                     f"scope=r_liteprofile%20r_emailaddress")

# @auth_bp.route('/linkedin/authorized')
# def authorized():
#     # Handle the authorization callback from LinkedIn
#     code = request.args.get('code')
#     if not code:
#         return 'Access denied: No authorization code received.'

#     # Exchange the authorization code for an access token
#     token_url = "https://www.linkedin.com/oauth/v2/accessToken"
#     token_data = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': url_for('.authorized', _external=True),
#         'client_id': LINKEDIN_CLIENT_ID,
#         'client_secret': LINKEDIN_CLIENT_SECRET
#     }

#     response = requests.post(token_url, data=token_data)
#     if response.status_code != 200:
#         return 'Access denied: Unable to obtain access token.'

#     access_token = response.json().get('access_token')

#     # Use the access token to fetch the user's LinkedIn profile data
#     profile_url = "https://api.linkedin.com/v2/me"
#     headers = {'Authorization': f'Bearer {access_token}'}

#     profile_response = requests.get(profile_url, headers=headers)

#     if profile_response.status_code == 200:
#         profile_data = profile_response.json()
#         print(profile_data)
#     else:
#         return 'Access denied: Failed to fetch user info from LinkedIn.'
