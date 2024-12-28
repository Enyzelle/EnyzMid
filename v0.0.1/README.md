# EnyzMid - Discord Rich Presence Manager

<div align="center">
  <img src="assets/logo.png" alt="EnyzMid Logo" width="200"/>
  <br>
  <p>A powerful Discord Rich Presence manager for YouTube, Netflix, and Spotify</p>
</div>

## 🌟 Features

- 🎵 Real-time activity detection for:
  - YouTube (videos and channels)
  - Netflix (shows and movies)
  - Spotify (songs and artists)
- 🔄 Automatic Discord connection
- 🔲 System tray integration
- 🚀 Auto-start capability
- 💻 Discord-themed UI
- 🎨 Custom status icons

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.8 or higher
- Windows OS
- Discord desktop application
- Git (for cloning the repository)

## 🚀 Installation

### For Users

1. Download the latest release from the [Releases](https://github.com/Enyzelle/EnyzMid/releases) page
2. Extract the ZIP file
3. Run `EnyzMid.exe`

### For Developers

1. Clone the repository:
```bash
git clone https://github.com/Enyzelle/EnyzMid.git
```
2. Navigate to the project directory:
```bash
cd EnyzMid
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
2. Create and activate a virtual environment:
### Windows
```bash
python -m venv venv
venv\Scripts\activate
```
### Linux
```bash
python -m venv venv
source venv/bin/activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Set up your Discord application:
- Go to [Discord Developer Portal](https://discord.com/developers/applications)
- Create a new application
- Copy the Client ID and Client Secret
- Under OAuth2 → Redirects, add: `http://localhost:5000/callback`
- Save changes
5. Configure the application:
- Update the following files with your Discord credentials:
     ```python
     # presence_manager.py
     self.client_id = 'YOUR_DISCORD_CLIENT_ID'
     
     # web_server.py
     DISCORD_CLIENT_ID = 'YOUR_DISCORD_CLIENT_ID'
     DISCORD_CLIENT_SECRET = 'YOUR_DISCORD_CLIENT_SECRET'
     ```
6. Run the application:
```bash
python main.py
```

## 🛠️ Building from Source

To create your own executable:
## Install PyInstaller
```bash
pip install pyinstaller
```
## Create the executable
```bash
pyinstaller --name EnyzMid --onefile --windowed --icon=assets/icon.ico main.py
```
The executable will be located in the `dist` folder.

## 📝 Configuration

### Discord Developer Portal Setup

1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name your application (e.g., "EnyzMid")
4. Go to "OAuth2" settings
5. Add redirect URL: `http://localhost:5000/callback`
6. Copy Client ID and Client Secret
7. Save all changes

## 🔧 Troubleshooting

Common issues and solutions:

1. **Connection Issues**
   - Ensure Discord is running
   - Check if your Client ID and Secret are correct
   - Try restarting both Discord and EnyzMid

2. **Activity Not Showing**
   - Make sure you're using a supported browser
   - Check if the media is playing in an active window
   - Verify that Discord is running

3. **Building Errors**
   - Ensure all requirements are installed
   - Use a compatible Python version (3.8+)
   - Check for any missing dependencies

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## ⚠️ Known Issues

Current version limitations:
1. YouTube detection needs improvement
2. Netflix title extraction can be inconsistent
3. Connection status might need manual reconnection
4. Media thumbnails may not always display

*These issues are being actively worked on.*

## 📞 Support

If you need help or want to report a bug:
1. Create a new issue with detailed information
2. Include your system information
3. Describe the steps to reproduce the issue

## 🔄 Project Structure
```
EnyzMid/
├── main.py # Main application file
├── presence_manager.py # Discord presence management
├── web_server.py # OAuth2 web server
├── activity_monitor.py # Activity detection
├── requirements.txt # Python dependencies
└── assets/ # Icons and images
```

## 📦 Dependencies

- PyQt5 - GUI framework
- pypresence - Discord Rich Presence API
- Flask - Web server for OAuth2
- psutil - Process and system monitoring
- pywin32 - Windows API access
- requests - HTTP client
- nest_asyncio - Asyncio support

## 🔒 Privacy

EnyzMid only monitors window titles for supported applications and does not:
- Collect personal information
- Store any user data
- Send data to external servers
- Access any content within applications

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [pypresence](https://github.com/qwertyquerty/pypresence) for Discord Rich Presence implementation
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- All contributors and supporters

---

<div align="center">
  Made with ❤️ by the EnyzMid Team
  <br>
  <sub>Not affiliated with Discord, YouTube, Netflix, or Spotify</sub>
</div>