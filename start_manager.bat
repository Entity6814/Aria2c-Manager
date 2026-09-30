@echo off
REM Start the Aria2 Download Manager in system tray mode
REM This script uses pyw for background operation without console window

echo Starting Aria2 Download Manager in system tray...

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Start aria2c daemon in background using pyw (no console window)
REM This will check if daemon is already running and skip if so
start /MIN pyw "%SCRIPT_DIR%start_aria2.py"

REM Wait a moment for aria2c to start
ping 127.0.0.1 -n 3 >nul

REM Start the GUI in minimized mode using pyw
REM This will check if GUI is already running and show it instead
start /MIN pyw "%SCRIPT_DIR%app.pyw" --minimized

echo Manager started in system tray. Use the tray icon to access the interface.
echo Downloads will be saved to: %USERPROFILE%\Downloads



