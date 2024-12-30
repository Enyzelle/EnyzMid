import psutil
import win32gui
import win32process
import time
import threading
import re
from settings import Settings

class ActivityMonitor:
    def __init__(self, presence_manager):
        self.presence_manager = presence_manager
        self.running = False
        self.start_timestamp = int(time.time())
        self.last_title = ""
        self.settings = Settings()
        
    def start(self):
        if not self.running:
            self.running = True
            monitor_thread = threading.Thread(target=self._monitor_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
        
    def stop(self):
        self.running = False
        
    def _monitor_loop(self):
        while self.running:
            try:
                window = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
                process_name = process.name().lower()
                title = win32gui.GetWindowText(window)
                
                self._handle_window_change(title, process_name)
                
            except Exception as e:
                print(f"Error monitoring activity: {e}")
                
            time.sleep(1)  # Check every second
            
    def _handle_window_change(self, title, process_name):
        # Browser-based activities (for Chrome/Edge/Firefox)
        if ("chrome" in process_name or "msedge" in process_name or "firefox" in process_name):
            title_lower = title.lower()
            
            # YouTube
            if "youtube" in title_lower:
                if self.settings.is_activity_enabled('youtube'):
                    if "- youtube" in title_lower or "youtube -" in title_lower:
                        video_info = self._parse_youtube_title(title)
                        if video_info:
                            self._update_youtube_presence(video_info, True)
                        else:
                            self._update_youtube_presence(None, False)
                else:
                    self._clear_presence()
            
            # Facebook
            elif "facebook" in title_lower:
                if self.settings.is_activity_enabled('facebook'):
                    self._update_facebook_presence(title)
                else:
                    self._clear_presence()
            
            # Instagram
            elif "instagram" in title_lower:
                if self.settings.is_activity_enabled('instagram'):
                    self._update_instagram_presence(title)
                else:
                    self._clear_presence()
            
            # Twitter/X
            elif any(x in title_lower for x in ["twitter.com", "x.com"]):
                if self.settings.is_activity_enabled('twitter'):
                    self._update_twitter_presence(title)
                else:
                    self._clear_presence()
            
            # GitHub
            elif "github" in title_lower:
                if self.settings.is_activity_enabled('github'):
                    self._update_github_presence(title)
                else:
                    self._clear_presence()
        
        # Netflix
        elif "netflix" in title.lower():
            if self.settings.is_activity_enabled('netflix'):
                show_name = self._parse_netflix_title(title)
                self._update_netflix_presence(show_name, bool(show_name))
            else:
                self._clear_presence()
        
        # Spotify
        elif "spotify" in process_name:
            if self.settings.is_activity_enabled('spotify'):
                self._update_spotify_presence(title, "Spotify" in title)
            else:
                self._clear_presence()
            
    def _parse_youtube_title(self, title):
        """Better YouTube title parsing"""
        # Common patterns for YouTube titles in different browsers
        patterns = [
            r'(.*?) - YouTube',  # Chrome/Edge pattern
            r'YouTube - (.*)',    # Alternative pattern
            r'(.*?) \| YouTube'   # Another possible pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                full_title = match.group(1).strip()
                
                # Remove notification counts
                full_title = re.sub(r'^\(\d+\)\s*', '', full_title)
                
                # Try to extract artist and song title
                # Pattern for "ARTIST - SONG TITLE" format
                artist_song_match = re.match(r'^(.+?)\s*-\s*(.+)$', full_title)
                
                if artist_song_match:
                    artist = artist_song_match.group(1).strip()
                    song = artist_song_match.group(2).strip()
                    
                    # Remove common suffixes like "(OFFICIAL MUSIC VIDEO)"
                    song = re.sub(r'\s*\([^)]*VIDEO[^)]*\)\s*$', '', song, flags=re.IGNORECASE)
                    
                    return {
                        'video_title': song,
                        'channel': artist
                    }
                else:
                    return {
                        'video_title': full_title,
                        'channel': 'YouTube'
                    }
        
        return None
    
    def _parse_netflix_title(self, title):
        if " - " in title:
            parts = title.split(" - ")
            if len(parts) >= 2 and "Netflix" in parts[-1]:
                return parts[0].strip()
        return None
            
    def _update_youtube_presence(self, parsed_title, is_watching):
        if is_watching and parsed_title:
            self.presence_manager.update_activity({
                "details": parsed_title['video_title'][:128],  # Song title
                "state": f"by {parsed_title['channel']}"[:128],  # Artist/Channel
                "large_image": "youtube",
                "large_text": "YouTube",
                "small_image": "playing",
                "small_text": "Playing",
                "start": self.start_timestamp
            })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing YouTube",
                "state": "Looking for videos",
                "large_image": "youtube",
                "large_text": "YouTube",
                "small_image": "browsing",
                "small_text": "Browsing"
            })
        
    def _update_netflix_presence(self, title, is_watching):
        if is_watching and title:
            self.presence_manager.update_activity({
                "details": title[:128],
                "state": "Watching on Netflix",
                "large_image": "netflix",
                "large_text": "Netflix",
                "small_image": "watching",
                "small_text": "Watching",
                "start": self.start_timestamp
            })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing Netflix",
                "state": "Looking for something to watch",
                "large_image": "netflix",
                "large_text": "Netflix",
                "small_image": "browsing",
                "small_text": "Browsing"
            })
        
    def _update_spotify_presence(self, title, is_playing):
        if is_playing and " - " in title:
            parts = title.split(' - ')
            song = parts[0].strip()
            artist = parts[1].replace("Spotify", "").strip()
            
            self.presence_manager.update_activity({
                "details": song[:128],
                "state": f"by {artist}"[:128],
                "large_image": "spotify",
                "large_text": "Spotify",
                "small_image": "playing",
                "small_text": "Playing",
                "start": self.start_timestamp
            })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing Spotify",
                "state": "Looking for music",
                "large_image": "spotify",
                "large_text": "Spotify",
                "small_image": "browsing",
                "small_text": "Browsing"
            })  

    def _clear_presence(self):
        """Clear the current Discord presence"""
        self.presence_manager.update_activity(None)  

    def _update_facebook_presence(self, title):
        self.presence_manager.update_activity({
            "details": "Browsing Facebook",
            "state": "Staying connected",
            "large_image": "facebook",  # Add this asset to Discord
            "large_text": "Facebook",
            "small_image": "browsing",
            "small_text": "Browsing"
        })

    def _update_instagram_presence(self, title):
        self.presence_manager.update_activity({
            "details": "Browsing Instagram",
            "state": "Checking posts",
            "large_image": "instagram",  # Add this asset to Discord
            "large_text": "Instagram",
            "small_image": "browsing",
            "small_text": "Browsing"
        })

    def _update_twitter_presence(self, title):
        self.presence_manager.update_activity({
            "details": "On Twitter",
            "state": "Reading tweets",
            "large_image": "twitter",  # Add this asset to Discord
            "large_text": "Twitter",
            "small_image": "browsing",
            "small_text": "Browsing"
        })

    def _update_github_presence(self, title):
        # Try to extract repository name
        repo_match = re.search(r'([^/]+/[^/]+) (?:·|:) GitHub', title)
        if repo_match:
            repo = repo_match.group(1)
            self.presence_manager.update_activity({
                "details": "Working on GitHub",
                "state": f"Repository: {repo}",
                "large_image": "github",  # Add this asset to Discord
                "large_text": "GitHub",
                "small_image": "coding",  # Add this asset to Discord
                "small_text": "Coding"
            })
        else:
            self.presence_manager.update_activity({
                "details": "Browsing GitHub",
                "state": "Looking at repositories",
                "large_image": "github",
                "large_text": "GitHub",
                "small_image": "browsing",
                "small_text": "Browsing"
            })  