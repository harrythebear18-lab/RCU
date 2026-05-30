@echo off
echo ========================================
echo Homelab Bidirectional Integration Launcher
echo ========================================
echo.

REM Check Python installation
echo Checking for Python installation...

REM Try python command first
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python found: 
    python --version
    set PYTHON_CMD=python
    goto :python_found
)

REM Try py command
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python found: 
    py --version
    set PYTHON_CMD=py
    goto :python_found
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python found: 
    python3 --version
    set PYTHON_CMD=python3
    goto :python_found
)

REM Python not found
echo Error: Python not found. Please install Python 3.9 or higher.
echo.
echo You can download Python from: https://www.python.org/downloads/
echo.
echo After installing Python, please run this launcher again.
pause
exit /b 1

:python_found
echo Python command set to: %PYTHON_CMD%

echo.
echo Checking dependencies...

REM Check required packages
%PYTHON_CMD% -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests...
    %PYTHON_CMD% -m pip install requests
)

%PYTHON_CMD% -c "import psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing psutil...
    %PYTHON_CMD% -m pip install psutil
)

%PYTHON_CMD% -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Pillow...
    %PYTHON_CMD% -m pip install Pillow
)

%PYTHON_CMD% -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask...
    %PYTHON_CMD% -m pip install flask
)

%PYTHON_CMD% -c "import flask_cors" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask-CORS...
    %PYTHON_CMD% -m pip install flask-cors
)

echo.
echo Dependencies check complete!
echo.

REM Configure Windows Firewall
echo Configuring Windows Firewall for Homelab services...
netsh advfirewall firewall add rule name="Homelab Portal" dir=in action=allow protocol=TCP localport=8080 >nul 2>&1
netsh advfirewall firewall add rule name="Homelab Discovery" dir=in action=allow protocol=UDP localport=30001 >nul 2>&1
netsh advfirewall firewall add rule name="Homelab API" dir=in action=allow protocol=TCP localport=8080 >nul 2>&1

echo Firewall rules configured.
echo.

REM Launch bidirectional launcher
echo Starting Homelab Bidirectional Launcher...
echo.
echo This launcher provides:
echo - Bidirectional integration between Windows Assistant and Homelab Portal
echo - Unified dark theme across all tools
echo - Real-time status monitoring
echo - Easy tool management
echo.

%PYTHON_CMD% "%~dp0Homelab_Bidirectional_Launcher.py"

echo.
echo Homelab Bidirectional Launcher closed.
pause
