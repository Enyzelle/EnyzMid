# EnyzMid - Discord Rich Presence Manager
# Author: Enyz
# Version: 1.0.0
# Date: 2024-12-28 

# This is a simple Discord Rich Presence manager that allows you to connect to Discord and display your current activity.
# It uses the pypresence library to interact with the Discord API and the PyQt5 library to create the GUI.
# The application is designed to run in the background and will automatically connect to Discord when the user logs in.
# The application will also display the user's current activity and allow them to disconnect from Discord.  

# This is not a fully functional application and is only a proof of concept.
# It is not intended to be used in a production environment.
# It is intended to be used as a reference for how to interact with the Discord API and how to create a GUI in PyQt5.

import sys
import webbrowser
import pystray
from PIL import Image
import threading
import json
import os
from presence_manager import PresenceManager
from web_server import start_server
from activity_monitor import ActivityMonitor
from app_state import app_state

app = None

class EnyzMid:
    def __init__(self):
        global app
        app = self
        self.presence_manager = PresenceManager()
        self.activity_monitor = ActivityMonitor(self.presence_manager)
        app_state.set_app(self)
        self.setup_tray()
        
    def setup_tray(self):
        # Load icon image (you'll need to provide an icon.png file)
        icon_image = Image.open('icon.png')
        
        # Create system tray menu
        menu_items = [
            pystray.MenuItem("Connect to Discord", self.start_auth),
            pystray.MenuItem("Manage Activities", self.open_management),
            pystray.MenuItem("Exit", self.quit_application)
        ]
        
        # Create system tray icon
        self.icon = pystray.Icon(
            "EnyzMid",
            icon_image,
            "EnyzMid - Discord Rich Presence",
            menu=pystray.Menu(*menu_items)
        )
        
        # Auto-connect on startup if config exists
        if os.path.exists('config.json'):
            self.start_auth()
    
    def start(self):
        # Start activity monitor
        self.activity_monitor.start()
        
        # Run the icon
        self.icon.run()
    
    def start_auth(self):
        # Reset the connection event
        from web_server import connection_successful
        connection_successful.clear()
        
        # Start the local web server in a separate thread
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Open the Discord OAuth2 URL
        webbrowser.open('http://localhost:5000/login')
        
        # Wait for successful connection
        def wait_for_connection():
            if connection_successful.wait(timeout=60):
                self.load_config()
        
        connection_thread = threading.Thread(target=wait_for_connection)
        connection_thread.daemon = True
        connection_thread.start()
    
    def open_management(self):
        webbrowser.open('http://localhost:5000/manage')
    
    def load_config(self):
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if config.get('token'):
                        self.presence_manager.set_token(config['token'])
            except Exception as e:
                print(f'Error loading config: {str(e)}')
    
    def quit_application(self):
        self.icon.stop()
        sys.exit(0)

def main():
    app = EnyzMid()
    app.start()

if __name__ == '__main__':
    main() 