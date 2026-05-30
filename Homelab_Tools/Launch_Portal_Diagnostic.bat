@echo off
setlocal enabledelayedexpansion
title Portal Diagnostic Launcher
echo ========================================
echo Homelab Portal Diagnostic Launcher
echo ========================================
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
            echo Please install Python 3.7+ from: https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
)

:python_found
echo.
echo Running portal diagnostic...
echo This will check for common issues preventing portal startup
echo.

%PYTHON_CMD% "%~dp0test_portal_startup.py"

echo.
echo If diagnostic shows issues, try these fixes:
echo 1. Install missing packages: pip install Pillow psutil
echo 2. Check Core Services directory exists
echo 3. Verify Python 3.9+ is installed
echo.
pause
