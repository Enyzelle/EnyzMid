class AppState:
    def __init__(self):
        self.app_instance = None

    def set_app(self, app):
        self.app_instance = app

    def get_app(self):
        return self.app_instance

app_state = AppState() 