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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QWidget, QFrame, QStatusBar, QSystemTrayIcon, 
                            QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from presence_manager import PresenceManager
from web_server import start_server
import threading
import json
import os
from activity_monitor import ActivityMonitor

class StyleSheet:
    MAIN_STYLE = """
    QMainWindow {
        background-color: #36393f;
    }
    QLabel {
        color: #ffffff;
        font-size: 14px;
    }
    QPushButton {
        background-color: #7289da;
        border: none;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 14px;
        min-width: 150px;
    }
    QPushButton:hover {
        background-color: #677bc4;
    }
    QPushButton:disabled {
        background-color: #4f5660;
    }
    QStatusBar {
        color: #ffffff;
        background-color: #2f3136;
    }
    """

class EnyzMid(QMainWindow):
    def __init__(self):
        super().__init__()
        self.presence_manager = PresenceManager()
        self.activity_monitor = ActivityMonitor(self.presence_manager)
        self.initUI()
        self.activity_monitor.start()
        
        # Setup status check timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_connection_status)
        self.status_timer.start(5000)  # Check every 5 seconds
        
        # Auto-connect on startup
        self.auto_connect()
        
    def initUI(self):
        self.setWindowTitle('EnyzMid - Discord Rich Presence')
        self.setFixedSize(500, 400)
        self.setStyleSheet(StyleSheet.MAIN_STYLE)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.png'))  # Make sure to have an icon.png file
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        connect_action = QAction("Connect to Discord", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        connect_action.triggered.connect(self.start_auth)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(connect_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double click tray icon to show window
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo/Title
        title_label = QLabel('EnyzMid')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel('Discord Rich Presence Manager')
        subtitle_label.setFont(QFont('Arial', 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #4f5660;")
        layout.addWidget(line)
        
        # Status display
        self.status_label = QLabel('Status: Not Connected')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; background-color: #2f3136; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        # Current activity display
        self.activity_label = QLabel('No activity detected')
        self.activity_label.setAlignment(Qt.AlignCenter)
        self.activity_label.setStyleSheet("padding: 10px; background-color: #2f3136; border-radius: 5px;")
        layout.addWidget(self.activity_label)
        
        # Connect button
        self.connect_button = QPushButton('Connect with Discord', self)
        self.connect_button.clicked.connect(self.start_auth)
        self.connect_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.connect_button)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Ready')
        
        # Add stretches for better spacing
        layout.addStretch()
        
    def auto_connect(self):
        """Attempt to connect automatically on startup"""
        if os.path.exists('config.json'):
            self.start_auth()
            self.hide()  # Hide window after auto-connecting
        
    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "EnyzMid",
            "Application minimized to tray",
            QSystemTrayIcon.Information,
            2000
        )
        
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            
    def quit_application(self):
        """Properly close the application"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def load_config(self):
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if config.get('token'):
                        self.presence_manager.set_token(config['token'])
                        self.update_connection_status(True)
            except Exception as e:
                self.statusBar.showMessage(f'Error loading config: {str(e)}')
    
    def start_auth(self):
        self.statusBar.showMessage('Starting authentication...')
        self.connect_button.setEnabled(False)
        
        # Reset the connection event
        from web_server import connection_successful
        connection_successful.clear()
        
        # Start the local web server in a separate thread
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Open the Discord OAuth2 URL
        webbrowser.open('http://localhost:5000/login')
        
        # Start a thread to wait for successful connection
        def wait_for_connection():
            if connection_successful.wait(timeout=60):  # Wait up to 60 seconds
                self.load_config()  # Reload config after successful connection
                self.check_connection_status()  # Update status immediately
        
        connection_thread = threading.Thread(target=wait_for_connection)
        connection_thread.daemon = True
        connection_thread.start()
        
    def check_connection_status(self):
        is_connected = self.presence_manager.is_connected()
        self.update_connection_status(is_connected)
        
        # Update activity label
        current_activity = self.presence_manager.get_current_activity()
        if current_activity:
            self.activity_label.setText(f"Current Activity: {current_activity}")
        
    def update_connection_status(self, is_connected):
        if is_connected:
            self.status_label.setText('Status: Connected')
            self.status_label.setStyleSheet("padding: 10px; background-color: #43b581; border-radius: 5px;")
            self.connect_button.setEnabled(False)
            self.statusBar.showMessage('Connected to Discord')
            self.tray_icon.setToolTip('EnyzMid - Connected')
        else:
            self.status_label.setText('Status: Not Connected')
            self.status_label.setStyleSheet("padding: 10px; background-color: #f04747; border-radius: 5px;")
            self.connect_button.setEnabled(True)
            self.statusBar.showMessage('Not connected to Discord')
            self.tray_icon.setToolTip('EnyzMid - Not Connected')

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Allow running in background
    window = EnyzMid()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 