import requests
import webbrowser
import urllib.parse

# Replace with your actual LinkedIn credentials
CLIENT_ID = '869ineym5l39jr'
CLIENT_SECRET = 'WPL_AP1.kCUDOzeKJUpRacqV.1ka8mA=='
REDIRECT_URI = 'http://127.0.0.1:8000/callback'
AUTHORIZATION_BASE_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
SCOPE = ['r_liteprofile', 'r_emailaddress']

# Step 1: Manually Direct User to LinkedIn for Authorization
def get_authorization_code():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPE)
    }
    authorization_url = AUTHORIZATION_BASE_URL + '?' + urllib.parse.urlencode(params)
    
    # Open the authorization URL in the user's default browser
    print("Opening LinkedIn authorization URL in browser...")
    webbrowser.open(authorization_url)
    
    # Ask the user to copy the authorization code from the redirect URL
    redirect_response = input("Paste the full redirect URL here: ")
    
    # Parse the URL and extract the authorization code
    parsed_url = urllib.parse.urlparse(redirect_response)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    print(f"Parsed URL: {parsed_url}")
    print(f"Query Parameters: {query_params}")
    
    # Check if the 'code' parameter is present in the query
    if 'code' in query_params:
        authorization_code = query_params['code'][0]
        return authorization_code
    else:
        raise Exception("Authorization code not found in the URL. Please make sure you paste the correct URL.")

# Step 2: Exchange Authorization Code for Access Token
def get_access_token(authorization_code):
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(TOKEN_URL, data=data)
    response_data = response.json()
    
    print(f"Token Response: {response_data}")
    
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        raise Exception(f"Error fetching access token: {response_data}")

# Step 3: Fetch User's Profile Information
def fetch_user_profile(access_token):
    profile_url = 'https://api.linkedin.com/v2/me'
    email_url = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Fetch profile information
    profile_response = requests.get(profile_url, headers=headers)
    email_response = requests.get(email_url, headers=headers)
    
    if profile_response.status_code == 200:
        profile_info = profile_response.json()
        email_info = email_response.json()
        return profile_info, email_info
    else:
        raise Exception(f"Error fetching profile: {profile_response.status_code}, {profile_response.text}")

if __name__ == "__main__":
    try:
        # Step 1: Get the authorization code
        authorization_code = get_authorization_code()
        
        # Step 2: Exchange the authorization code for an access token
        access_token = get_access_token(authorization_code)
        print(f"Access Token: {access_token}")
        
        # Step 3: Fetch the user's LinkedIn profile and email
        profile_info, email_info = fetch_user_profile(access_token)
        print(f"Profile Info: {profile_info}")
        print(f"Email Info: {email_info}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
