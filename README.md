# Aria2c Manager

A modern, professional download manager system built around aria2c with a browser extension for download interception and a PyQt6 desktop GUI for monitoring and control.

## Features

- **Multi-threaded Downloads**: Leverages aria2c's powerful multi-threading capabilities (customizable connections and splits)
- **Browser Integration**: Chrome/Edge extension with popup UI for download management
- **Modern GUI**: PyQt6-based desktop application with dark theme and modern browser-like interface
- **System Tray**: Runs in background as system tray icon with notifications
- **Crash Resistance**: Persistent download state that survives application crashes
- **Inline Controls**: Pause, resume, and cancel controls directly on each download
- **Smart Notifications**: Desktop notifications for download events with source tracking
- **Configurable Locations**: User-configurable download directories via extension settings
- **Real-time Monitoring**: Live progress updates, speed monitoring, and download statistics
- **Auto-Update**: Automatic update checking via GitHub integration
- **Professional Installer**: Automated installation with dependency checking
- **Advanced Mode**: Customizable parallel connections, split parts, and download location
- **Smart Installation**: Installs to user profile folder for better data management
- **On-Demand Launch**: Extension can launch the app when needed via Flask API
- **Single Instance**: Prevents multiple instances of GUI and daemon
- **Auto-Start**: Configurable auto-start on Windows boot (safe with single-instance protection)

## Screenshots

*Add screenshots here when available*

## Architecture

The system consists of three interconnected components:

### 1. Aria2c Daemon (`start_aria2.py`)
- Python script that launches aria2c as a background RPC daemon
- Configured for optimal multi-threaded performance
- Downloads saved to user's Downloads folder by default
- Runs without console window (pyw)

### 2. Browser Extension (`extension/`)
- Manifest V3 Chrome/Edge extension
- Intercepts browser download events
- Cancels native downloads and forwards to aria2c
- Provides download location configuration
- Shows desktop notifications for download events
- **Popup UI**: Click extension icon to manage downloads directly
- **Auto-Detection**: Checks if desktop app is running before intercepting downloads

### 3. Desktop GUI (`app.pyw`)
- PyQt6-based monitoring dashboard
- Real-time download status updates
- Manual URL input for direct downloads
- Download management controls (pause/resume/cancel)
- System tray integration with background operation
- Auto-update checking via GitHub

## Installation

### Prerequisites

- **Windows 10+**
- **Python 3.8+**
- **aria2c** - Download from [aria2.github.io](https://aria2.github.io/)
- **PyQt6** and **requests** Python packages

### Quick Installation

Run the provided installer:
```bash
install.bat
```

The installer will:
- Check for Python installation (install if needed)
- Check for aria2c installation (install via winget or guide manual installation)
- Install Python dependencies (PyQt6, requests, Flask)
- Copy application files to `%USERPROFILE%\Aria2cManager`
- Create Start Menu shortcut (runs app.pyw directly with icon)
- Create auto-start shortcut (runs app.pyw minimized on boot)

### Manual Installation

#### Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation: `python --version`

#### Step 2: Install aria2c
1. Download aria2c from [aria2.github.io](https://aria2.github.io/)
2. Extract to a folder (e.g., `C:\aria2`)
3. Add aria2c to PATH:
   - Search for "Environment Variables"
   - Edit system PATH
   - Add aria2c directory (e.g., `C:\aria2`)
4. Verify installation: `aria2c --version`

#### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Load Browser Extension
1. Open Chrome or Edge
2. Navigate to `chrome://extensions/` or `edge://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select the `extension/` folder from this project

#### Step 5: Configure Download Location (Optional)
Download location can be configured in two ways:
1. **Extension Popup Advanced Mode**: Click extension icon → Toggle "Advanced Mode" → Set download directory
2. **Extension Options Page**: Right-click extension → Options → Set download directory

Leave empty to use aria2c's default (Downloads folder).

Note: Advanced mode also allows customizing parallel connections and split parts.

## Usage

### Quick Start

**Using the installer:**
```bash
install.bat
```

**Manual start:**
```bash
start_manager.bat
```

### Manual Start Options

1. **Start aria2c daemon:**
   ```bash
   pyw start_aria2.py
   ```

2. **Launch GUI:**
   ```bash
   pyw app.pyw
   ```

3. **Start in system tray:**
   ```bash
   pyw app.pyw --minimized
   ```

### Browser Downloads

Once the extension is loaded:
- Any browser download will be automatically intercepted (if desktop app is running)
- Downloads are forwarded to aria2c for multi-threaded downloading
- Desktop notifications will indicate when downloads start
- **Extension Popup**: Click the extension icon to:
  - View all active, waiting, and completed downloads
  - Add new downloads via URL input
  - Pause, resume, or remove downloads
  - Check connection status to aria2c daemon
  - Launch the desktop app if not running
  - **Advanced Mode**: Customize download location, parallel connections, and split parts

### GUI Downloads

1. Launch the GUI application
2. Paste a URL in the input field
3. Click "Add Download"
4. Monitor progress in the download list
5. Use inline controls to pause/resume/cancel downloads

## Configuration

### aria2c RPC Settings

Default RPC configuration:
- **Port**: 6800
- **Secret**: `MyCustomSecret123`
- **Max Connections**: 16 per server
- **Splits**: 16 per file
- **Auto-resume**: Enabled

To modify these settings, edit `start_aria2.py`.

### Download Location

**Default**: User's Downloads folder

**Custom**: Configure via extension options
1. Right-click extension → Options
2. Set your preferred directory
3. Save settings

## Installation Location

By default, the installer places the application in:
```
%USERPROFILE%\Aria2cManager
```

For example: `C:\Users\YourName\Aria2cManager`

This keeps application data separated from your source files and allows for easier updates.

## Development

### Project Structure

```
aria2c-manager/
├── extension/
│   ├── manifest.json       # Extension manifest
│   ├── background.js       # Download interception logic
│   ├── popup.html          # Extension popup UI
│   ├── popup.js            # Popup functionality with advanced mode
│   ├── options.html        # Settings page
│   └── icon.png            # Extension icon (optional)
├── app.pyw                # PyQt6 GUI application (console-free)
├── start_aria2.py         # aria2c daemon launcher
├── start_manager.bat      # Windows startup script
├── install.bat            # Windows installer
├── uninstall.bat          # Windows uninstaller
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Running the Application

**Development mode:**
```bash
python app.pyw
```

**Production mode (background):**
```bash
pyw app.pyw --minimized
```

### Building

No build process required - pure Python/JavaScript implementation.

## Troubleshooting

### aria2c won't start
- Ensure aria2c is installed and in PATH
- Check for existing aria2c processes: `tasklist | findstr aria2`
- Kill existing processes: `taskkill /F /IM aria2c.exe`

### Extension not intercepting downloads
- Ensure aria2c daemon is running on port 6800
- The extension now checks if the desktop app is running before intercepting
- If the app is not running, the extension will show a notification
- You can click "Launch Desktop App" in the extension popup
- Check browser console for errors
- Verify extension permissions
- Reload the extension after changes

### GUI won't connect to aria2c
- Verify aria2c is running: `netstat -an | findstr 6800`
- Check RPC secret matches in both daemon and GUI
- Ensure no firewall blocking port 6800

### Downloads going to wrong location
- Kill old aria2c processes and restart
- Check extension popup advanced settings for custom directory
- Verify `start_aria2.py` has correct Downloads path
- Check extension options for custom directory

### Advanced mode settings not applying
- Make sure to click "Save Settings" in the extension popup
- Check that the settings are persisted (they save to Chrome storage)
- Restart downloads after changing settings

### Console window appears
- Ensure you're using `pyw` instead of `python` for background operation
- Use `start_manager.bat` for proper background startup

## Uninstallation

Run the provided uninstaller:
```bash
uninstall.bat
```

The uninstaller will:
- Stop running processes
- Remove Start Menu shortcut
- Remove auto-start shortcut
- Guide extension removal
- Remove Python dependencies (optional)
- Remove aria2c (optional)
- Remove application files from `%USERPROFILE%\Aria2cManager` (optional)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [aria2](https://aria2.github.io/) - The powerful multi-threaded download utility
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python GUI framework
- Chrome Extension API - For download interception

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

## Roadmap

- [ ] Add torrent support
- [ ] Implement download scheduling
- [ ] Add bandwidth limiting
- [ ] Add download categories
- [ ] Implement download queuing
- [ ] Add statistics and reporting

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
