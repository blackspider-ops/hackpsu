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
AUTHORIZATION_BASE_URL = "https://www.linkedin.com/oauth/v2/authorizatiotern"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# LinkedIn Profile API URLs
PROFILE_API_URL = "https://api.linkedin.com/v2/me"
EMAIL_API_URL = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"

# Bearer token
BEARER_TOKEN = "AQVAC4EyVnQzU92khhWOKFmqjL9_o4r545qz8C-5Rh1r6tTmOgpPnb1Ft5xUmQppNi8D0vAD4krAXmDdnv_3Y6HnysveYNbbh4VvQqUA6dlacCG3OgLip7GXipirP7nbSxOdmRh-vGXqM24R6caUvJJUgzZq9Xlktp0ATMTW3BdrZxI_wPsDCOWMCiXPPab3h3ZDIqaNq-EwNbknwLBOk0JutcSXnR6ySiDfQ-lNWf9NzcCMl9aWc6NdHW9nnnUNvmbaPLSTnCyoOY8XkZ97qUNKH5gf51-IJZcNMhP8zjzvAmUFYS8IuhHOYo9Cqvd1EBUH2DrjIDcxguOYMrfBVRKU8LbPVQ"

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Define the allowed scopes in the order LinkedIn expects
SCOPES = "profile email w_member_social"

# Create OAuth2 Session with Bearer Token
def make_linkedin_session(token=None, state=None):
    if token is None:
        token = {'access_token': BEARER_TOKEN, 'token_type': 'Bearer'}
    
    return OAuth2Session(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        token=token,
        state=state,
        scope=SCOPES.split()
    )

@app.route('/')
def index():
    return 'Welcome to LinkedIn OAuth! Go to /login to authenticate.'

@app.route('/login')
def login():
    linkedin = make_linkedin_session()
    authorization_url, state = linkedin.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # No need to fetch a new token, bearer token is already set
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    linkedin = make_linkedin_session()
    
    # Fetch the user's basic LinkedIn profile
    response = linkedin.get(PROFILE_API_URL)
    profile_data = response.json()
    
    # Fetch email address
    email_response = linkedin.get(EMAIL_API_URL)
    email_data = email_response.json()
    
    # Safely access the email address
    email_address = 'No email found'
    if 'elements' in email_data:
        elements = email_data['elements']
        if elements:
            for element in elements:
                if 'handle~' in element:
                    email_address = element['handle~'].get('emailAddress', 'No email found')
                    break
    
    return {
        'basic_profile': profile_data,
        'email': email_address
    }

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7896)
