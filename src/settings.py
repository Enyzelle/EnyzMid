import json
import os

DEFAULT_SETTINGS = {
    "activities": {
        "youtube": True,
        "netflix": True,
        "spotify": True,
        "facebook": False,
        "instagram": False,
        "twitter": False,
        "github": False
    }
}

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Merge saved settings with defaults to ensure all activities exist
                    self.settings = DEFAULT_SETTINGS.copy()
                    self.settings["activities"].update(saved_settings.get("activities", {}))
            except:
                self.settings = DEFAULT_SETTINGS
        else:
            self.settings = DEFAULT_SETTINGS
            self.save_settings()
    
    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def is_activity_enabled(self, activity):
        return self.settings["activities"].get(activity, True)
    
    def set_activity_enabled(self, activity, enabled):
        self.settings["activities"][activity] = enabled
        self.save_settings() 