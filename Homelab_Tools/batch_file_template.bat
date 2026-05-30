@echo off
setlocal enabledelayedexpansion

REM Windows 10/11 Compatible Batch File Template
REM This template ensures compatibility across Windows versions

REM Check Windows version
ver | findstr /i "10\.0" > nul
if !errorlevel! equ 0 (
    ver | find "22000" > nul
    if !errorlevel! equ 0 (
set WINDOWS_VERSION="11"
    ) else (
set WINDOWS_VERSION="10"
    )
) else (
set WINDOWS_VERSION="UNKNOWN"
)

REM Detect Python command
set PYTHON_CMD=""
python --version >nul 2>&1
if !errorlevel! equ 0 (
set PYTHON_CMD="python"
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
set PYTHON_CMD="py"
    ) else (
        echo ERROR: Python not found
        pause
        exit /b 1
    )
)

echo Detected Windows %WINDOWS_VERSION%
echo Using Python command: %PYTHON_CMD%

REM Your batch file logic goes here
REM Example: Run a Python script
%PYTHON_CMD% your_script.py

pause
