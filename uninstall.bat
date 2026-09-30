@echo off
REM Aria2c Manager Uninstaller for Windows
REM Removes application components and cleans up

setlocal enabledelayedexpansion

echo ========================================
echo   Aria2c Manager Uninstaller
echo ========================================
echo.

REM Define installation directory
set "INSTALL_DIR=%USERPROFILE%\Aria2cManager"

echo WARNING: This will remove Aria2c Manager from your system.
echo Installation location: %INSTALL_DIR%
echo.
set /p confirm="Are you sure you want to uninstall? (yes/no): "
if /i not "!confirm!"=="yes" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo [1/6] Stopping running processes...
tasklist | findstr aria2c >nul 2>&1
if %errorLevel% equ 0 (
    echo Stopping aria2c processes...
    taskkill /F /IM aria2c.exe >nul 2>&1
    taskkill /F /IM pythonw.exe >nul 2>&1
    taskkill /F /IM python.exe >nul 2>&1
    echo [OK] Processes stopped
) else (
    echo [INFO] No running processes found
)

echo.
echo [2/6] Removing Start Menu shortcut...
set "startMenuPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Aria2c Manager.lnk"
if exist "!startMenuPath!" (
    del "!startMenuPath!"
    echo [OK] Start Menu shortcut removed
) else (
    echo [INFO] No Start Menu shortcut found
)

echo.
echo [3/6] Removing auto-start shortcut...
set "startupPath=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Aria2c Manager.lnk"
if exist "!startupPath!" (
    del "!startupPath!"
    echo [OK] Auto-start shortcut removed
) else (
    echo [INFO] No auto-start shortcut found
)

echo.
echo [4/6] Removing browser extension...
echo Please manually remove the extension:
echo 1. Open Chrome or Edge
echo 2. Navigate to chrome://extensions/ or edge://extensions/
echo 3. Find "Aria2 Download Manager"
echo 4. Click "Remove"
echo.
pause

echo.
echo [5/6] Uninstalling Python dependencies...
cd /d "%INSTALL_DIR%" 2>nul
if %errorLevel% equ 0 (
    pip uninstall -y PyQt6 requests Flask >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] Python dependencies removed
    ) else (
        echo [WARNING] Failed to remove Python dependencies
        echo You may need to remove them manually: pip uninstall PyQt6 requests Flask
    )
) else (
    echo [INFO] Installation directory not found, skipping dependency removal
)

echo.
echo [6/7] Removing aria2c (optional)...
set /p remove_aria2c="Do you want to remove aria2c as well? (yes/no): "
if /i "!remove_aria2c!"=="yes" (
    echo Removing aria2c...
    winget uninstall aria2 >nul 2>&1
    if %errorLevel% equ 0 (
        echo [OK] aria2c removed via winget
    ) else (
        echo [INFO] winget removal failed or not available
        echo Please remove aria2c manually if desired
    )
) else (
    echo [INFO] aria2c kept installed
)

echo.
echo [7/7] Removing application files...
set /p remove_files="Do you want to remove application files from %INSTALL_DIR%? (yes/no): "
if /i "!remove_files!"=="yes" (
    echo Removing application directory...
    if exist "%INSTALL_DIR%" (
        rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
        if %errorLevel% equ 0 (
            echo [OK] Application files removed
        ) else (
            echo [WARNING] Failed to remove some files
            echo Please manually delete: %INSTALL_DIR%
        )
    ) else (
        echo [INFO] Installation directory not found
    )
) else (
    echo [INFO] Application files kept
)

echo.
echo ========================================
echo   Uninstallation Complete!
echo ========================================
echo.
echo Thank you for using Aria2c Manager!
echo.
pause
