@echo off
setlocal enabledelayedexpansion
title RAM Sharing Manager - Batch GUI Launcher
echo="==============================================="
echo    RAM SHARING MANAGER - BATCH GUI
echo="==============================================="
echo.
echo Starting pure batch file GUI interface...
echo (No Python or tkinter required)
echo.
echo This works on ANY Windows system!
echo.

REM Check if main menu script exists
if not exist "RAM_Sharing_Menu.bat" (
    echo ERROR: RAM_Sharing_Menu.bat not found
    echo Make sure you're in the Homelab Tools directory
    pause
    exit /b 1
)

REM Launch the batch GUI
echo Launching RAM Sharing Manager...
call RAM_Sharing_Menu.bat

echo.
echo RAM Sharing Manager closed
