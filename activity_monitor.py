import psutil
import win32gui
import win32process
import time
import threading
import re

class ActivityMonitor:
    def __init__(self, presence_manager):
        self.presence_manager = presence_manager
        self.running = False
        self.start_timestamp = int(time.time())
        self.last_title = ""
        
    def start(self):
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def _monitor_loop(self):
        while self.running:
            try:
                window = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
                process_name = process.name().lower()
                title = win32gui.GetWindowText(window)
                
                if title != self.last_title:  # Only update if title changed
                    self.last_title = title
                    
                    # YouTube detection
                    if "- YouTube" in title:  # Video playing
                        self._update_youtube_presence(self._parse_youtube_title(title), True)
                    elif "YouTube" in title:  # Just browsing
                        self._update_youtube_presence(None, False)
                    
                    # Netflix detection
                    elif "netflix" in title.lower():
                        show_name = None
                        # Try to extract show name from title
                        if " - " in title:
                            parts = title.split(" - ")
                            if len(parts) >= 2 and "Netflix" in parts[-1]:
                                show_name = parts[0].strip()
                        self._update_netflix_presence(show_name, True if show_name else False)
                    
                    # Spotify detection
                    elif "spotify" in process_name:
                        if " - " in title and "Spotify" in title:
                            self._update_spotify_presence(title, True)
                        else:
                            self._update_spotify_presence(None, False)
                    
            except Exception as e:
                print(f"Error monitoring activity: {e}")
                
            time.sleep(1)
    
    def _parse_youtube_title(self, title):
        # Remove notification numbers and clean up title
        title = re.sub(r'\(\d+\)', '', title)
        title = title.replace('- YouTube', '').strip()
        
        # Split into video title and channel
        parts = title.split(' - ')
        video_title = parts[0].strip() if parts else ""
        channel = parts[1].strip() if len(parts) > 1 else "YouTube"
        
        return {
            'video_title': video_title,
            'channel': channel
        }
            
    def _update_youtube_presence(self, parsed_title, is_watching):
        if is_watching and parsed_title:
            self.presence_manager.update_activity({
                "details": parsed_title['video_title'][:128],  # Discord limit
                "state": f"Watching on Youtube",
                "large_image": "mp:https://i.imgur.com/3QfIvLf.png",  # YouTube logo
                "large_text": "YouTube",
                "small_image": "mp:https://i.imgur.com/Mw6qmkp.png",  # Play icon
                "small_text": "Watching",
                "start": self.start_timestamp
            })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing YouTube",
                "state": "Looking for videos",
                "large_image": "mp:https://i.imgur.com/3QfIvLf.png",  # YouTube logo
                "large_text": "YouTube",
                "small_image": "mp:https://i.imgur.com/ZeYHCJX.png",  # Browse icon
                "small_text": "Browsing"
            })
        
    def _update_netflix_presence(self, title, is_watching):
        if is_watching and title:
            self.presence_manager.update_activity({
                "details": title[:128],
                "state": "Watching on Netflix",
                "large_image": "mp:https://i.imgur.com/4tf6x2F.png",  # Netflix logo
                "large_text": "Netflix",
                "small_image": "mp:https://i.imgur.com/Mw6qmkp.png",  # Play icon
                "small_text": "Watching",
                "start": self.start_timestamp
            })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing Netflix",
                "state": "Looking for something to watch",
                "large_image": "mp:https://i.imgur.com/4tf6x2F.png",  # Netflix logo
                "large_text": "Netflix",
                "small_image": "mp:https://i.imgur.com/ZeYHCJX.png",  # Browse icon
                "small_text": "Browsing"
            })
        
    def _update_spotify_presence(self, title, is_playing):
        if is_playing and title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                song = parts[0].strip()
                artist = parts[1].strip()
                if "Spotify" in artist:
                    artist = artist.replace("Spotify", "").strip()
                
                self.presence_manager.update_activity({
                    "details": song[:128],
                    "state": f"by {artist}"[:128],
                    "large_image": "mp:https://i.imgur.com/OWKWjBz.png",  # Spotify logo
                    "large_text": "Spotify",
                    "small_image": "mp:https://i.imgur.com/Mw6qmkp.png",  # Play icon
                    "small_text": "Playing",
                    "start": self.start_timestamp
                })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing Spotify",
                "state": "Looking for music",
                "large_image": "mp:https://i.imgur.com/OWKWjBz.png",  # Spotify logo
                "large_text": "Spotify",
                "small_image": "mp:https://i.imgur.com/ZeYHCJX.png",  # Browse icon
                "small_text": "Browsing"
            }) 