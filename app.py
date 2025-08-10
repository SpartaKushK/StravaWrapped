import os
from flask import Flask, request, jsonify, redirect, session
import requests
import dotenv

dotenv.load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_AUTHORIZATION_URL = 'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = 'https://www.strava.com/oauth/token'


@app.route('/login')
def login():
    '''
    Redirects to user to Strava's authorization page
    '''
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://localhost:5000/strava-callback",
        "approval_prompt": "auto",
        "scope": "activity:read_all",
    }

    auth_url = f"{STRAVA_AUTHORIZATION_URL}?" + \
        "&".join([f"{k}={v}" for k, v in params.items()])

    print("Redirecting to: ", auth_url)

    return redirect(auth_url)


@app.route('/strava-callback')
def strava_callback():
    '''
    Handles the callback from Strava
    '''
    auth_code = request.args.get('code')

    if not auth_code:
        return "Error: No authorization code received", 400

    print("Received code: ", auth_code)

    token_payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
    }

    print("Requesting tokens from Strava...")

    try:
        response = requests.post(STRAVA_TOKEN_URL, data=token_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to get access token: {e}", 500

    token_data = response.json()
    print("Received tokens: ", token_data)

    session['token_data'] = token_data

    return redirect('http://localhost:3000/dashboard')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
