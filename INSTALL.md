# Installation Guide

This guide provides detailed installation instructions for Aria2c Manager on different platforms.

## System Requirements

- **Python**: 3.8 or higher
- **aria2c**: Latest stable version
- **Operating System**: Windows 10+, Linux, macOS
- **Browser**: Chrome 88+ or Edge 88+ (for extension)
- **Memory**: 512MB minimum, 1GB recommended
- **Disk Space**: 100MB for application, additional space for downloads

## Platform-Specific Installation

### Windows

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
cd C:\Users\vatsa\OneDrive\Desktop\aria2c-manager
pip install -r requirements.txt
```

#### Step 4: Load Browser Extension
1. Open Chrome or Edge
2. Navigate to `chrome://extensions/` or `edge://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `extension` folder from the project directory

#### Step 5: Configure and Run
```bash
# Quick start with system tray
.\start_manager.bat

# Or manual start
python start_aria2.py
python app.pyw --minimized
```

### Linux (Ubuntu/Debian)

#### Step 1: Install Python
```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### Step 2: Install aria2c
```bash
sudo apt install aria2
```

#### Step 3: Install Python Dependencies
```bash
cd ~/aria2c-manager
pip3 install -r requirements.txt
```

#### Step 4: Load Browser Extension
1. Open Chrome or Chromium
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select the `extension` folder

#### Step 5: Configure and Run
```bash
# Start aria2c daemon
python3 start_aria2.py &

# Start GUI in system tray
python3 app.pyw --minimized
```

### macOS

#### Step 1: Install Python
```bash
brew install python@3.9
```

#### Step 2: Install aria2c
```bash
brew install aria2
```

#### Step 3: Install Python Dependencies
```bash
cd ~/aria2c-manager
pip3 install -r requirements.txt
```

#### Step 4: Load Browser Extension
1. Open Chrome
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select the `extension` folder

#### Step 5: Configure and Run
```bash
# Start aria2c daemon
python3 start_aria2.py &

# Start GUI in system tray
python3 app.pyw --minimized
```

## Verification

### Test aria2c Installation
```bash
aria2c --version
# Should output version information
```

### Test Python Dependencies
```bash
python -c "import PyQt6; import requests; print('Dependencies OK')"
```

### Test RPC Connection
```bash
# Start aria2c first
python start_aria2.py

# In another terminal, test connection
curl -X POST http://localhost:6800/jsonrpc -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":"test","method":"aria2.getVersion","params":["token:MyCustomSecret123"]}'
```

### Test Extension
1. Navigate to any website
2. Right-click a download link → "Save link as"
3. Verify the extension intercepts the download
4. Check that aria2c GUI shows the download

## Configuration

### aria2c RPC Settings
Edit `start_aria2.py` to customize:
- **Port**: Change `--rpc-listen-port=6800`
- **Secret**: Change `--rpc-secret=MyCustomSecret123`
- **Connections**: Change `--max-connection-per-server=16`
- **Splits**: Change `--split=16`

### Download Location
**Default**: User's Downloads folder

**Custom Location**:
1. Right-click extension → Options
2. Enter your preferred directory
3. Click "Save Settings"

**GUI Location**: Edit `start_aria2.py` to change the Downloads path:
```python
downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
# Change "Downloads" to your preferred folder
```

## Troubleshooting

### Python Not Found
**Windows**: Ensure Python is added to PATH during installation
**Linux**: Install python3 and pip3
**macOS**: Use Homebrew to install Python

### aria2c Not Found
**Windows**: Add aria2c directory to system PATH
**Linux**: `sudo apt install aria2`
**macOS**: `brew install aria2`

### Permission Denied
**Linux/macOS**: Make scripts executable:
```bash
chmod +x start_aria2.py
chmod +x app.pyw
```

### Extension Won't Load
- Ensure you're loading the `extension` folder, not individual files
- Check browser console for errors
- Verify manifest.json is valid JSON
- Try reloading the extension

### GUI Won't Connect
- Verify aria2c is running: `netstat -an | grep 6800` (Linux/macOS) or `netstat -an | findstr 6800` (Windows)
- Check RPC secret matches
- Ensure no firewall blocking port 6800

### Downloads Going to Wrong Location
- Kill old aria2c processes and restart
- Check extension options for custom directory
- Verify `start_aria2.py` has correct Downloads path

## Uninstallation

### Remove Application Files
```bash
# Delete project directory
rm -rf aria2c-manager
```

### Remove Browser Extension
1. Navigate to `chrome://extensions/`
2. Find "Aria2 Download Manager"
3. Click "Remove"

### Remove aria2c
**Windows**: Uninstall via Control Panel or delete aria2c folder
**Linux**: `sudo apt remove aria2`
**macOS**: `brew uninstall aria2`

### Remove Python Dependencies
```bash
pip uninstall PyQt6 requests
```

## Advanced Configuration

### Performance Tuning
For maximum download speed, adjust these settings in `start_aria2.py`:
```python
"--max-connection-per-server=32",  # Increase connections
"--split=32",                      # Increase splits
"--min-split-size=1M",            # Minimum split size
"--max-overall-download-limit=0",  # No overall limit
```

### Bandwidth Limiting
Add to `start_aria2.py`:
```python
"--max-download-limit=10M",       # 10MB per download
"--max-overall-download-limit=50M" # 50MB total
```

### Proxy Support
Add to `start_aria2.py`:
```python
"--http-proxy=http://proxy:8080",
"--https-proxy=http://proxy:8080",
```

## Security Considerations

- **RPC Secret**: Change the default secret in production
- **Firewall**: Consider firewall rules for port 6800
- **File Permissions**: Ensure download directory has appropriate permissions
- **HTTPS**: aria2c supports HTTPS, ensure certificates are valid

## Updates

### Update aria2c
**Windows**: Download latest from aria2.github.io
**Linux**: `sudo apt update && sudo apt upgrade aria2`
**macOS**: `brew upgrade aria2`

### Update Python Dependencies
```bash
pip install --upgrade PyQt6 requests
```

### Update Extension
1. Navigate to `chrome://extensions/`
2. Click "Reload" on the extension
3. Clear browser cache if needed

## Support

For additional help:
- Check the main [README.md](README.md)
- Open an issue on GitHub
- Review troubleshooting section
- Check aria2c documentation at [aria2.github.io](https://aria2.github.io/)
