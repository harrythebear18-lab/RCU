@echo off
echo ========================================
echo Homelab Simple Launcher
echo ========================================
echo.

REM Try to find and run Python
echo Attempting to start Homelab Bidirectional Launcher...
echo.

REM Method 1: Try python
python "%~dp0Homelab_Bidirectional_Launcher.py" 2>nul
if %errorlevel% equ 0 goto :success

REM Method 2: Try py
py "%~dp0Homelab_Bidirectional_Launcher.py" 2>nul
if %errorlevel% equ 0 goto :success

REM Method 3: Try python3
python3 "%~dp0Homelab_Bidirectional_Launcher.py" 2>nul
if %errorlevel% equ 0 goto :success

REM Method 4: Try test script first
echo Python not found. Running diagnostic test...
echo.
python "%~dp0test_python.py" 2>nul
if %errorlevel% equ 0 goto :success

py "%~dp0test_python.py" 2>nul
if %errorlevel% equ 0 goto :success

python3 "%~dp0test_python.py" 2>nul
if %errorlevel% equ 0 goto :success

REM All methods failed
echo.
echo ERROR: Python not found or not working properly.
echo.
echo Please install Python 3.9 or higher from:
echo https://www.python.org/downloads/
echo.
echo After installation, make sure to check "Add Python to PATH" during setup.
echo.
echo Current directory: %~dp0
echo.
echo Files in directory:
dir /b "%~dp0*.py"
echo.
echo Press any key to open Python download page...
pause >nul
start https://www.python.org/downloads/
goto :end

:success
echo.
echo Homelab launcher started successfully!

:end
pause
