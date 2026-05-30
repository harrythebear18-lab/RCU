@echo off
setlocal enabledelayedexpansion
title Auto RAM Connection Launcher
echo="==============================================="
echo    AUTO RAM CONNECTION LAUNCHER
echo="==============================================="
echo.
echo This script automatically:
echo - Detects if this PC is server or client
echo - Configures RAM sharing settings
echo - Connects both systems together
echo - Starts real-time monitoring
echo.
echo Choose launch mode:
echo 1. Auto-Connect All (Recommended)
echo 2. GUI Mode with Real-time Display
echo 3. Console Mode
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"="="1" goto auto_connect"
if "%choice%"="="2" goto gui_mode"
if "%choice%"="="3" goto console_mode"
if "%choice%"="="4" goto exit_program"

echo Invalid choice
pause
goto start

:auto_connect
echo.
echo Starting auto-connection...
echo This will configure everything automatically
echo.

REM Check Python availability
python --version >nul 2>&1
if !errorlevel! equ 0 (
set "PYTHON_CMD="python""
    echo Found Python: python
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
set "PYTHON_CMD="py""
        echo Found Python: py
    ) else (
        echo Python not found, using console mode...
        goto console_auto
    )
)

echo Launching auto-connection script...
%PYTHON_CMD% Auto_RAM_Connect.py
pause
goto start

:gui_mode
echo.
echo Starting GUI mode with real-time display...
echo.

REM Check Python availability
python --version >nul 2>&1
if !errorlevel! equ 0 (
set "PYTHON_CMD="python""
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
set "PYTHON_CMD="py""
    ) else (
        echo ERROR: Python required for GUI mode
        echo Use console mode instead
        pause
        goto start
    )
)

echo Launching GUI...
%PYTHON_CMD% Auto_RAM_Connect.py --gui
pause
goto start

:console_mode
echo.
echo Starting console mode...
echo.

REM Check Python availability
python --version >nul 2>&1
if !errorlevel! equ 0 (
set "PYTHON_CMD="python""
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
set "PYTHON_CMD="py""
    ) else (
        echo ERROR: Python required
        pause
        goto start
    )
)

echo Launching console mode...
%PYTHON_CMD% Auto_RAM_Connect.py --console
pause
goto start

:console_auto
echo.
echo Running auto-connection in console mode...
echo.

REM Use batch files for auto-connection
echo Step 1: Fixing Windows compatibility...
call Fix_Windows_Compatibility.bat

echo.
echo Step 2: Auto-detecting system role...
REM Simple detection based on available RAM
for /f "tokens="2 delims==" %%a in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do set "RAM_BYTES=%%a""
set /a "RAM_GB="!RAM_BYTES:~0,-9! / 1073741824""

echo Detected RAM: %RAM_GB%GB
if %RAM_GB% GEQ 16 (
    echo Detected as SERVER system
    echo.
    echo Step 3: Configuring server...
    call Setup_RAM_Sharing.bat
) else (
    echo Detected as CLIENT system
    echo.
    echo Step 3: Connecting to server...
    call Map_RAM_Sharing.bat
)

echo.
echo Auto-connection completed!
pause
goto start

:exit_program
echo.
echo Goodbye!
exit /b 0
