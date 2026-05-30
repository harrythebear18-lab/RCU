@echo off
setlocal enabledelayedexpansion
title Homelab Portal - Windows 10/11 Unified Resource Sharing
echo="==============================================="
echo    HOMELAB PORTAL - WINDOWS 10/11
echo    Unified Resource Sharing System
echo="==============================================="
echo.
echo This portal provides:
echo - Screen sharing between Windows systems
echo - Sound sharing and audio streaming
echo - Drag-and-drop file transfer
echo - Resource sharing (RAM, CPU, GPU)
echo - Bidirectional communication
echo.
echo Compatible with Windows 10 and Windows 11
echo.

REM Check Windows version
ver | findstr /i "10\.0" > nul
if !errorlevel! equ 0 (
    ver | find "22000" > nul
    if !errorlevel! equ 0 (
        echo Detected: Windows 11
set WINDOWS_VERSION="11"
    ) else (
        echo Detected: Windows 10
set WINDOWS_VERSION="10"
    )
) else (
    echo ERROR: This portal requires Windows 10 or Windows 11
    pause
    exit /b 1
)

echo Detected Windows %WINDOWS_VERSION%
echo.

REM Detect Python command
set PYTHON_CMD=""
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    echo Found Python: python
    goto :python_found
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=py
        echo Found Python: py
        goto :python_found
    ) else (
        python3 --version >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_CMD=python3
            echo Found Python: python3
            goto :python_found
        ) else (
            echo ERROR: Python not found
            echo Please install Python 3.7 or higher
            echo Download from: https://www.python.org/downloads/
            echo.
            echo After installing, make sure "Add Python to PATH" is checked
            pause
            exit /b 1
        )
    )
)

:python_found

echo.
echo Checking dependencies...
%PYTHON_CMD% -c "import tkinter, PIL, socket" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installing required dependencies...
    %PYTHON_CMD% -m pip install --user Pillow
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Configuring Windows Firewall for portal...
echo Adding firewall rules for Homelab Portal...
netsh advfirewall firewall add rule name="Homelab Portal" dir=in action=allow protocol=TCP localport=30000 >nul 2>&1
netsh advfirewall firewall add rule name="Homelab Portal Discovery" dir=in action=allow protocol=UDP localport=30001 >nul 2>&1
if !errorlevel! equ 0 (
    echo Firewall rules configured successfully
) else (
    echo Warning: Could not configure firewall rules automatically
    echo You may need to manually allow Homelab Portal through Windows Firewall
)

echo.
echo Starting Homelab Portal...
echo The portal will start in a new window
echo.
echo Portal Features:
echo - Automatic discovery of other Windows systems
echo - Drag-and-drop file sharing
echo - Screen sharing with remote control
echo - Sound sharing and audio streaming
echo - Resource sharing (RAM, CPU, GPU)
echo - Bidirectional communication
echo.
echo Port Information:
echo - Portal Server: TCP 30000
echo - Discovery Service: UDP 30001
echo.
echo Note: Make sure port 30000 is open on your Windows Firewall
echo.

REM Start the portal
start "Homelab Portal" %PYTHON_CMD% "%~dp0Core Services\homelab_portal.py"

echo.
echo Homelab Portal is starting...
echo Please wait for the GUI window to appear
echo.
echo If the portal doesn't start:
echo 1. Check that Python is installed
echo 2. Verify Windows Firewall allows port 30000
echo 3. Make sure no other program is using port 30000
echo.
pause
