import os
from flask import Flask, redirect, request, session, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# Allow HTTP during development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI')
AUTHORIZATION_BASE_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# LinkedIn Profile API URLs
PROFILE_API_URL = "https://api.linkedin.com/v2/me"
DETAILED_PROFILE_URL = ("https://api.linkedin.com/v2/me?projection="
                        "(id,firstName,lastName,profilePicture(displayImage~:playableStreams),"
                        "headline,summary,positions,education)")

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Create OAuth2 Session
def make_linkedin_session(token=None, state=None):
    return OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        token=token,
        state=state
    )

@app.route('/')
def index():
    return 'Welcome to LinkedIn OAuth! Go to /login to authenticate.'

@app.route('/login')
def login():
    # Define the scopes
    scopes = ["r_liteprofile", "r_emailaddress", "w_member_social"]
    linkedin = make_linkedin_session()

    # Generate the authorization URL
    authorization_url, state = linkedin.authorization_url(
        AUTHORIZATION_BASE_URL,
        scope=' '.join(scopes)  # Join scopes with a space
    )

    # Save the state in the session for security
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    linkedin = make_linkedin_session(state=session.get('oauth_state'))

    # Fetch the token
    token = linkedin.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=request.url
    )

    # Save the token in the session
    session['oauth_token'] = token

    # Now you can use the token to access LinkedIn's API
    # Example: getting user profile data
    user_info = linkedin.get('https://api.linkedin.com/v2/me').json()
    print(user_info)  # Or handle the user data as needed

    return f'Logged in as: {user_info.get("localizedFirstName")} {user_info.get("localizedLastName")}'

@app.route('/profile')
def profile():
    linkedin = make_linkedin_session(token=session.get('oauth_token'))

    # Fetch the user's basic LinkedIn profile
    response = linkedin.get(PROFILE_API_URL)
    profile_data = response.json()

    # Fetch detailed profile information (including education and experience)
    detailed_response = linkedin.get(DETAILED_PROFILE_URL)
    detailed_profile_data = detailed_response.json()

    return {
        'basic_profile': profile_data,
        'detailed_profile': detailed_profile_data
    }

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7896)
    