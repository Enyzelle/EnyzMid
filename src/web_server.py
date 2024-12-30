from flask import Flask, request, redirect, render_template_string, jsonify
import json
import requests
from threading import Event
import os
from settings import Settings
from app_state import app_state

app = Flask(__name__)
settings = Settings()

# Load config from environment variables or use defaults
DISCORD_CLIENT_ID = 'DISCORD_CLIENT_ID' # Replace with your discord client id
DISCORD_CLIENT_SECRET = 'DISCORD_CLIENT_SECRET' # Replace with your discord secret id
REDIRECT_URI = 'http://localhost:5000/callback' # This is the default callback

# Event to signal successful connection
connection_successful = Event()

# HTML template with improved design and user profile
MANAGEMENT_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>EnyzMid - Activity Management</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #36393f;
            color: white;
            min-height: 100vh;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: #2f3136;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 4px solid #7289da;
        }
        
        .user-info h2 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .user-info p {
            color: #b9bbbe;
            font-size: 14px;
        }
        
        .title {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 25px;
            color: #fff;
        }
        
        .activities {
            display: grid;
            gap: 15px;
        }
        
        .activity {
            background: #2f3136;
            padding: 20px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .activity:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .activity-name {
            font-size: 16px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .activity-icon {
            width: 24px;
            height: 24px;
        }
        
        .switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 28px;
        }
        
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #4f545c;
            transition: .4s;
            border-radius: 34px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background-color: #7289da;
        }
        
        input:checked + .slider:before {
            transform: translateX(22px);
        }
        
        .status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 5px;
            background: #43b581;
            color: white;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .status.show {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{{ user_data.avatar_url }}" alt="Avatar" class="avatar">
            <div class="user-info">
                <h2>{{ user_data.username }}</h2>
                <p>Discord Rich Presence Manager</p>
            </div>
        </div>
        
        <h1 class="title">Activity Management</h1>
        
        <div class="activities">
            <div class="activity">
                <span class="activity-name">
                    <img src="https://imgur.com/GdjY8tH.png" class="activity-icon" alt="YouTube">
                    YouTube Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="youtube" onchange="updateActivity('youtube', this.checked)" 
                           {{ 'checked' if youtube else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="activity">
                <span class="activity-name">
                    <img src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/227_Netflix_logo-512.png" class="activity-icon" alt="Netflix">
                    Netflix Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="netflix" onchange="updateActivity('netflix', this.checked)"
                           {{ 'checked' if netflix else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="activity">
                <span class="activity-name">
                    <img src="https://imgur.com/Et5AJpz.png" class="activity-icon" alt="Spotify">
                    Spotify Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="spotify" onchange="updateActivity('spotify', this.checked)"
                           {{ 'checked' if spotify else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="activity">
                <span class="activity-name">
                    <img src="https://imgur.com/nIiaG46.png" class="activity-icon" alt="Facebook">
                    Facebook Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="facebook" onchange="updateActivity('facebook', this.checked)"
                           {{ 'checked' if facebook else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="activity">
                <span class="activity-name">
                    <img src="https://cdn2.iconfinder.com/data/icons/social-icons-33/128/Instagram-512.png" class="activity-icon" alt="Instagram">
                    Instagram Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="instagram" onchange="updateActivity('instagram', this.checked)"
                           {{ 'checked' if instagram else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="activity">
                <span class="activity-name">
                    <img src="https://imgur.com/LS08Auh.png" class="activity-icon" alt="Twitter">
                    Twitter Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="twitter" onchange="updateActivity('twitter', this.checked)"
                           {{ 'checked' if twitter else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="activity">
                <span class="activity-name">
                    <img src="https://imgur.com/bx8Rxta.png" class="activity-icon" alt="GitHub">
                    GitHub Activity
                </span>
                <label class="switch">
                    <input type="checkbox" id="github" onchange="updateActivity('github', this.checked)"
                           {{ 'checked' if github else '' }}>
                    <span class="slider"></span>
                </label>
            </div>
        </div>
    </div>
    
    <div id="status" class="status">Settings saved!</div>
    
    <script>
        function updateActivity(activity, enabled) {
            fetch('/api/settings/activity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    activity: activity,
                    enabled: enabled
                })
            }).then(() => {
                const status = document.getElementById('status');
                status.classList.add('show');
                setTimeout(() => {
                    status.classList.remove('show');
                }, 2000);
            });
        }
    </script>
</body>
</html>
'''

# Add user data storage
user_data = {
    'username': 'Not Connected',
    'avatar_url': 'https://i.imgur.com/tdi3NGa.png'  # Default avatar
}

@app.route('/manage')
def manage():
    return render_template_string(MANAGEMENT_PAGE,
        user_data=user_data,
        youtube=settings.is_activity_enabled('youtube'),
        netflix=settings.is_activity_enabled('netflix'),
        spotify=settings.is_activity_enabled('spotify'),
        facebook=settings.is_activity_enabled('facebook'),
        instagram=settings.is_activity_enabled('instagram'),
        twitter=settings.is_activity_enabled('twitter'),
        github=settings.is_activity_enabled('github')
    )

@app.route('/api/settings/activity', methods=['POST'])
def update_activity():
    data = request.json
    activity = data.get('activity')
    enabled = data.get('enabled')
    
    if activity in ['youtube', 'netflix', 'spotify', 'facebook', 'instagram', 'twitter', 'github']:
        settings.set_activity_enabled(activity, enabled)
        if not enabled:
            # Get the activity monitor from app_state
            main_app = app_state.get_app()
            if main_app and main_app.activity_monitor:
                main_app.activity_monitor._clear_presence()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

@app.route('/login')
def login():
    auth_url = (
        f'https://discord.com/api/oauth2/authorize'
        f'?client_id={DISCORD_CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&response_type=code'
        f'&scope=rpc%20identify'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization code not received.', 400
    
    try:
        # Exchange code for token
        token_response = requests.post(
            'https://discord.com/api/oauth2/token',
            data={
                'client_id': DISCORD_CLIENT_ID,
                'client_secret': DISCORD_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'scope': 'identify'  # Add identify scope
            }
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            
            # Fetch user data
            user_response = requests.get(
                'https://discord.com/api/users/@me',
                headers={
                    'Authorization': f"Bearer {token_data['access_token']}"
                }
            )
            
            if user_response.status_code == 200:
                user_info = user_response.json()
                user_data['username'] = f"{user_info['username']}#{user_info['discriminator']}"
                user_data['avatar_url'] = f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"
            
            # Save token to config file
            with open('config.json', 'w') as f:
                json.dump({'token': token_data['access_token']}, f)
            
            connection_successful.set()
            
            return '''
                <script>
                    setTimeout(function() {
                        window.close();
                    }, 3000);
                </script>
                <h2>Successfully connected!</h2>
                <p>This window will close automatically in 3 seconds.</p>
            '''
        else:
            return f'Failed to authenticate with Discord. Status code: {token_response.status_code}', 400
            
    except Exception as e:
        return f'Error during authentication: {str(e)}', 500

def start_server():
    try:
        app.run(port=5000, use_reloader=False)
    except Exception as e:
        print(f"Failed to start web server: {e}")
