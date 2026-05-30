@echo off
setlocal enabledelayedexpansion
echo Homelab Tools - Windows 10 Setup Script
echo="======================================="
echo.

echo Checking Python installation...
REM Check Python availability (try both python and py)
python --version >nul 2>&1
if !errorlevel! equ 0 (
set PYTHON_CMD="python"
    echo Found Python: python
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
set PYTHON_CMD="py"
        echo Found Python: py
    ) else (
        echo ERROR: Python not found! Please install Python 3.8+ from https://python.org
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)

echo Python found
echo.

echo Installing required dependencies...
echo This may take several minutes...
echo.

%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
%PYTHON_CMD% -m pip install pywin32 wmi netifaces scapy colorama pyyaml jinja2

if errorlevel 1 (
    echo.
    echo ERROR: Some packages failed to install
    echo Try running this script as Administrator
    echo Or run: %PYTHON_CMD% install_dependencies.py
    pause
    exit /b 1
)

echo Dependencies installed successfully!
echo.
echo Testing homelab launcher...
%PYTHON_CMD% homelab_launcher.py

if errorlevel 1 (
    echo.
    echo ERROR: Launcher test failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo Setup completed successfully!
echo You can now run the launcher using:
echo    - Double-click: launch_homelab.bat
echo    - Command: %PYTHON_CMD% homelab_launcher.py
echo.
pause
