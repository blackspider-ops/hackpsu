import requests
from flask import Flask, request, redirect

# LinkedIn API details
CLIENT_ID = "78iqnqgmretbyi"
CLIENT_SECRET = "WPL_AP1.9qt0lG4YYbIYtvAu.RFcNJg=="
REDIRECT_URI = "http://localhost:7898/callback"
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = "openid profile email w_member_social"
import requests
from flask import Flask, request, redirect


# Flask app to handle OAuth2 callback
app = Flask(__name__)

# Step 1: Redirect user to LinkedIn for authorization
@app.route('/')
def linkedin_login():
    auth_url = (
        f"{AUTHORIZATION_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES.replace(' ', '%20')}"
    )
    return redirect(auth_url)

# Step 2: LinkedIn redirects back with an authorization code
@app.route('/callback')
def linkedin_callback():
    code = request.args.get('code')
    
    # Step 3: Exchange authorization code for access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    token_response = requests.post(TOKEN_URL, data=token_data)
    token_json = token_response.json()
    
    access_token = token_json.get('access_token')
    
    if access_token:
        # Step 4: Use the access token to get the user's profile
        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': 'application/json'
        }
        
        # Get basic profile information
        profile_response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        )
        
        # Get user's email address
        email_response = requests.get(
            'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
            headers=headers
        )
        
        return f"Profile: {profile_response.json()}<br>Email: {email_response.json()}"
    
    return "Error: Unable to get access token"

if __name__ == "__main__":
    app.run(debug=True, port=7898)
