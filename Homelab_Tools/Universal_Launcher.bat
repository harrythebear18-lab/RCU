@echo off
setlocal enabledelayedexpansion
title Universal RAM Sharing Launcher
echo="==============================================="
echo    UNIVERSAL RAM SHARING LAUNCHER
echo="==============================================="
echo.
echo This launcher works with ANY Python installation
echo Supports both 'python' and 'py' commands
echo.

REM Check if Python is available (try both python and py)
python --version >nul 2>&1
if !errorlevel! equ 0 (
set PYTHON_CMD="python"
    echo Found Python: python
    goto check_gui_files
)

py --version >nul 2>&1
if !errorlevel! equ 0 (
set PYTHON_CMD="py"
    echo Found Python: py
    goto check_gui_files
)

echo Python not found - using batch-only mode
echo.
goto batch_menu

:check_gui_files
echo Python detected - checking GUI files...

if exist "RAM_Sharing_GUI.py" (
    echo Found: GUI with tkinter support
set GUI_TYPE="gui"
) else if exist "RAM_Sharing_Simple_GUI.py" (
    echo Found: Simple GUI (no tkinter)
set GUI_TYPE="simple"
) else (
    echo No GUI files found - using batch-only mode
    goto batch_menu
)

echo.
echo Choose launch method:
echo 1. GUI Interface (recommended)
echo 2. Batch Menu (no Python needed)
echo 3. Exit
echo.

set /p launch_choice="Enter choice (1-3): "

if "%launch_choice%"="="1" goto launch_gui"
if "%launch_choice%"="="2" goto batch_menu"
if "%launch_choice%"="="3" goto exit_program"

echo Invalid choice
pause
goto check_gui_files

:launch_gui
echo.
echo Launching GUI interface...
if "%GUI_TYPE%"="="gui" ("
    echo Using tkinter GUI...
    %PYTHON_CMD% RAM_Sharing_GUI.py
) else (
    echo Using simple GUI...
    %PYTHON_CMD% RAM_Sharing_Simple_GUI.py
)

if !errorlevel! neq 0 (
    echo.
    echo GUI launch failed - falling back to batch menu
    pause
    goto batch_menu
)

goto exit_program

:batch_menu
cls
echo="==============================================="
echo    RAM SHARING - BATCH MENU
echo="==============================================="
echo.
echo Choose what you want to do:
echo.
echo 1. START RAM SHARING SERVER (PC 1 - 192.168.1.186)
echo 2. CONNECT TO RAM SERVER (PC 2 - 192.168.1.132)
echo 3. STOP SERVER / CLEANUP
echo 4. FIX WINDOWS COMPATIBILITY
echo 5. TEST NETWORK CONNECTION
echo 6. EXIT
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"="="1" goto start_server"
if "%choice%"="="2" goto connect_server"
if "%choice%"="="3" goto cleanup"
if "%choice%"="="4" goto fix_compat"
if "%choice%"="="5" goto test_network"
if "%choice%"="="6" goto exit_program"

echo Invalid choice. Please try again.
pause
goto batch_menu

:start_server
echo.
echo Starting RAM sharing server...
call Setup_RAM_Sharing.bat
pause
goto batch_menu

:connect_server
echo.
echo Connecting to RAM server...
call Map_RAM_Sharing.bat
pause
goto batch_menu

:cleanup
echo.
echo Stopping server and cleanup...
call Cleanup_RAM_Sharing.bat
pause
goto batch_menu

:fix_compat
echo.
echo Fixing Windows compatibility...
call Fix_Windows_Compatibility.bat
pause
goto batch_menu

:test_network
echo.
echo Testing network connection...
ping -n 3 192.168.1.132
pause
goto batch_menu

:exit_program
echo.
echo Goodbye!
exit /b 0
