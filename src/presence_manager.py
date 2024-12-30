import pypresence
import time
import threading
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

class PresenceManager:
    def __init__(self):
        self.client_id = '1320713470395551774'  # Your Client ID is already set here
        self.presence = None
        self.connected = False
        self.current_activity = None
        self.connect_lock = threading.Lock()
        self.loop = asyncio.new_event_loop()
        
    def set_token(self, token):
        with self.connect_lock:
            try:
                if self.presence:
                    try:
                        self.presence.close()
                    except:
                        pass
                
                # Set the event loop for this thread
                asyncio.set_event_loop(self.loop)
                
                self.presence = pypresence.Presence(self.client_id)
                self.presence.connect()
                self.connected = True
                
                # Start update loop in separate thread
                update_thread = threading.Thread(target=self._update_loop)
                update_thread.daemon = True
                update_thread.start()
                
                return True
                
            except Exception as e:
                print(f"Failed to connect to Discord: {e}")
                self.connected = False
                return False
            
    def _update_loop(self):
        # Set the event loop for this thread
        asyncio.set_event_loop(self.loop)
        
        while self.connected:
            try:
                if self.current_activity:
                    self.presence.update(**self.current_activity)
                time.sleep(15)  # Update every 15 seconds
            except Exception as e:
                print(f"Failed to update presence: {e}")
                with self.connect_lock:
                    self.connected = False
                break
                
    def update_activity(self, activity_data):
        self.current_activity = activity_data
        if self.connected and self.presence:
            try:
                if activity_data is None:
                    self.presence.clear()  # Clear the presence if activity_data is None
                else:
                    self.presence.update(**activity_data)
            except Exception as e:
                print(f"Failed to update presence: {e}")
        
    def is_connected(self):
        return self.connected and self.presence is not None
        
    def get_current_activity(self):
        if self.current_activity:
            return self.current_activity.get('details', 'No activity')
        return None 