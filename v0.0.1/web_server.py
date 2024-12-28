from flask import Flask, request, redirect
import json
import requests
from threading import Event

app = Flask(__name__)

DISCORD_CLIENT_ID = 'DISCORD_CLIENT_ID' # Replace with your Discord application client ID
DISCORD_CLIENT_SECRET = 'DISCORD_CLIENT_SECRET' # Replace with your Discord application client secret
REDIRECT_URI = 'http://localhost:5000/callback' # Replace with your redirect URI, this is the default

# Event to signal successful connection
connection_successful = Event()

@app.route('/login')
def login():
    return redirect(f'https://discord.com/api/oauth2/authorize'
                   f'?client_id={DISCORD_CLIENT_ID}'
                   f'&redirect_uri={REDIRECT_URI}'
                   f'&response_type=code'
                   f'&scope=rpc')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    # Exchange code for token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post('https://discord.com/api/oauth2/token', data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        
        # Save token to config file
        with open('config.json', 'w') as f:
            json.dump({'token': token_data['access_token']}, f)
        
        # Signal successful connection
        connection_successful.set()
            
        return '<script>window.close();</script>Successfully connected! You can close this window.'
    else:
        return 'Failed to authenticate with Discord.'

def start_server():
    app.run(port=5000, use_reloader=False)