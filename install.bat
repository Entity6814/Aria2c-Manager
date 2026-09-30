@echo off
REM Aria2c Manager Professional Installer for Windows
REM Downloads from GitHub and installs to user profile folder

setlocal enabledelayedexpansion

echo ========================================
echo   Aria2c Manager Installer
echo ========================================
echo.

REM Define installation directory
set "INSTALL_DIR=%USERPROFILE%\Aria2cManager"
set "GITHUB_REPO=https://github.com/Entity6814/Aria2c-Manager/archive/refs/heads/main.zip"
set "TEMP_ZIP=%TEMP%\aria2c-manager.zip"

echo [1/8] Checking for Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Python not found in PATH
    echo.
    echo Please install Python 3.8 or higher:
    echo - Visit: https://www.python.org/downloads/
    echo - Download and run the installer
    echo - IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    start https://www.python.org/downloads/
    echo.
    echo After installing Python, please run this installer again.
    pause
    exit /b 1
) else (
    echo [OK] Python is installed
    python --version
)

echo.
echo [2/8] Checking for aria2c installation...
aria2c --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] aria2c not found in PATH
    echo.
    echo Installation options:
    echo 1. Automatic installation using winget
    echo 2. Manual installation
    echo.
    set /p choice="Choose installation method (1 or 2): "
    
    if "!choice!"=="1" (
        echo.
        echo Installing aria2c using winget...
        winget install aria2
        if %errorLevel% neq 0 (
            echo [ERROR] winget installation failed
            echo Please install aria2c manually from: https://aria2.github.io/
            pause
            exit /b 1
        )
        echo [OK] aria2c installed via winget
    ) else (
        echo.
        echo Manual installation required:
        echo 1. Download aria2c from: https://aria2.github.io/
        echo 2. Extract to a folder (e.g., C:\aria2)
        echo 3. Add aria2c to system PATH
        echo.
        echo To add to PATH:
        echo - Search for "Environment Variables"
        echo - Edit system PATH
        echo - Add aria2c directory
        echo.
        echo After installation, please run this installer again.
        pause
        exit /b 1
    )
) else (
    echo [OK] aria2c is installed
    aria2c --version
)

echo.
echo [3/8] Downloading from GitHub...
echo Source: %GITHUB_REPO%
echo.

REM Download using PowerShell
powershell -Command "Invoke-WebRequest -Uri '%GITHUB_REPO%' -OutFile '%TEMP_ZIP%'"
if %errorLevel% neq 0 (
    echo [ERROR] Failed to download from GitHub
    echo Please check your internet connection
    pause
    exit /b 1
)
echo [OK] Downloaded successfully

echo.
echo [4/8] Extracting to installation directory...
echo Target directory: %INSTALL_DIR%

REM Create installation directory if it doesn't exist
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo [OK] Created installation directory
) else (
    echo [INFO] Installation directory already exists, clearing...
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
    mkdir "%INSTALL_DIR%"
)

REM Extract zip file
powershell -Command "Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP%\aria2c-temp' -Force"
if %errorLevel% neq 0 (
    echo [ERROR] Failed to extract zip file
    pause
    exit /b 1
)

REM Move files from extracted folder to installation directory
for /d %%d in ("%TEMP%\aria2c-temp\*") do (
    xcopy "%%d\*" "%INSTALL_DIR%\" /E /I /Y /H >nul 2>&1
)
if %errorLevel% neq 0 (
    echo [ERROR] Failed to copy files
    pause
    exit /b 1
)

REM Clean up temp files
rmdir /s /q "%TEMP%\aria2c-temp" >nul 2>&1
del "%TEMP_ZIP%" >nul 2>&1

echo [OK] Files extracted successfully

echo.
echo [5/8] Installing Python dependencies...
cd /d "%INSTALL_DIR%"
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

echo.
echo [6/8] Creating Start Menu shortcut...
set "startMenuPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Aria2c Manager.lnk"
set "targetPath=%INSTALL_DIR%\app.pyw"
set "iconPath=%INSTALL_DIR%\extension\icon.png"

REM Check if icon exists
if exist "%iconPath%" (
    REM Create Start Menu shortcut with icon
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%startMenuPath%'); $s.TargetPath = 'pyw'; $s.Arguments = '\"%INSTALL_DIR%\app.pyw\"'; $s.Description = 'Aria2c Download Manager'; $s.IconLocation = '%iconPath%'; $s.Save()"
) else (
    REM Create Start Menu shortcut without icon
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%startMenuPath%'); $s.TargetPath = 'pyw'; $s.Arguments = '\"%INSTALL_DIR%\app.pyw\"'; $s.Description = 'Aria2c Download Manager'; $s.Save()"
    echo [INFO] icon.png not found, creating shortcut without icon
)
if %errorLevel% neq 0 (
    echo [WARNING] Failed to create Start Menu shortcut
) else (
    echo [OK] Start Menu shortcut created
)

echo.
echo [7/8] Creating auto-start shortcut...
set "startupPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Aria2c Manager.lnk"

REM Check if icon exists
if exist "%iconPath%" (
    REM Create auto-start shortcut with icon and minimized flag
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%startupPath%'); $s.TargetPath = 'pyw'; $s.Arguments = '\"%INSTALL_DIR%\app.pyw\" --minimized'; $s.Description = 'Aria2c Download Manager - Auto Start'; $s.IconLocation = '%iconPath%'; $s.Save()"
) else (
    REM Create auto-start shortcut without icon
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%startupPath%'); $s.TargetPath = 'pyw'; $s.Arguments = '\"%INSTALL_DIR%\app.pyw\" --minimized'; $s.Description = 'Aria2c Download Manager - Auto Start'; $s.Save()"
)
if %errorLevel% neq 0 (
    echo [WARNING] Failed to create auto-start shortcut
) else (
    echo [OK] Auto-start shortcut created (Aria2c Manager will start on boot in system tray)
)

echo.
echo [8/8] Copying icon for shortcut use...
REM Copy icon to installation root for easier access
if exist "%INSTALL_DIR%\extension\icon.png" (
    copy "%INSTALL_DIR%\extension\icon.png" "%INSTALL_DIR%\app_icon.png" >nul 2>&1
    echo [OK] Icon copied to installation directory
) else (
    echo [INFO] No icon found in extension folder
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Installation location: %INSTALL_DIR%
echo.
echo Shortcuts created:
echo - Start Menu: Aria2c Manager
echo - Startup: Aria2c Manager (auto-start on boot in system tray)
echo.
echo To start Aria2c Manager:
echo - Open Start Menu and click "Aria2c Manager"
echo - Or run: pyw "%INSTALL_DIR%\app.pyw"
echo.
echo The GUI will automatically start the aria2c daemon if needed.
echo Single-instance protection prevents multiple instances.
echo.
echo The browser extension can also launch the app when needed.
echo.
echo To load the browser extension:
echo 1. Open Chrome or Edge
echo 2. Navigate to chrome://extensions/ or edge://extensions/
echo 3. Enable "Developer mode"
echo 4. Click "Load unpacked"
echo 5. Select the "extension" folder from: %INSTALL_DIR%\extension
echo.
echo For more information, see README.md
echo.
pause
