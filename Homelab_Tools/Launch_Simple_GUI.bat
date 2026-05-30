@echo off
setlocal enabledelayedexpansion
title Simple RAM Sharing GUI
echo="==============================================="
echo    SIMPLE RAM SHARING GUI
echo="==============================================="
echo.
echo Starting console-based RAM sharing interface...
echo (No tkinter required)
echo.

REM Check if Python is available (try both python and py)
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
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.7+ to use the GUI
        echo.
        echo Alternative: Use the batch file scripts:
        echo - Setup_RAM_Sharing.bat (for server)
        echo - Map_RAM_Sharing.bat (for client)
        echo.
        pause
        exit /b 1
    )
)

REM Check if simple GUI script exists
if not exist "RAM_Sharing_Simple_GUI.py" (
    echo ERROR: RAM_Sharing_Simple_GUI.py not found
    echo Make sure you're in the Homelab Tools directory
    pause
    exit /b 1
)

REM Launch the simple GUI
echo Launching Simple RAM Sharing GUI...
%PYTHON_CMD% RAM_Sharing_Simple_GUI.py

if !errorlevel! neq 0 (
    echo.
    echo ERROR: Failed to launch Simple GUI
    echo Make sure all required files are present
    pause
)

echo Simple RAM Sharing GUI closed
