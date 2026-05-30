@echo off
title Homelab Tools - Comprehensive System Audit
color 0B
echo ========================================
echo HOMELAB TOOLS - COMPREHENSIVE SYSTEM AUDIT
echo ========================================
echo.
echo This will run the COMPLETE comprehensive audit
echo with accurate component counting and functionality analysis.
echo.
echo The audit processes in 10 manageable chunks to prevent hanging.
echo.
echo Finding Python installation...

REM Try to find Python - Comprehensive Windows 10/11 detection
echo Checking Python installations...

REM Check py launcher first (Windows 10/11 standard)
where py >nul 2>&1
if %errorlevel% == 0 (
    echo Found py launcher
    set PYTHON_CMD=py
    goto :python_found
)

REM Check python command
where python >nul 2>&1
if %errorlevel% == 0 (
    echo Found python command
    set PYTHON_CMD=python
    goto :python_found
)

REM Check Windows Store Python (Windows 10/11)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    echo Found Windows Store Python
    set PYTHON_CMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
    goto :python_found
)

REM Check standard Python installations
if exist "C:\Python312\python.exe" (
    echo Found Python 3.12
    set PYTHON_CMD=C:\Python312\python.exe
    goto :python_found
)

if exist "C:\Python311\python.exe" (
    echo Found Python 3.11
    set PYTHON_CMD=C:\Python311\python.exe
    goto :python_found
)

if exist "C:\Python310\python.exe" (
    echo Found Python 3.10
    set PYTHON_CMD=C:\Python310\python.exe
    goto :python_found
)

if exist "C:\Python39\python.exe" (
    echo Found Python 3.9
    set PYTHON_CMD=C:\Python39\python.exe
    goto :python_found
)

REM Check AppData Python installations
if exist "%APPDATA%\Python\Python312\python.exe" (
    echo Found Python 3.12 in AppData
    set PYTHON_CMD=%APPDATA%\Python\Python312\python.exe
    goto :python_found
)

if exist "%APPDATA%\Python\Python311\python.exe" (
    echo Found Python 3.11 in AppData
    set PYTHON_CMD=%APPDATA%\Python\Python311\python.exe
    goto :python_found
)

if exist "%APPDATA%\Python\Python310\python.exe" (
    echo Found Python 3.10 in AppData
    set PYTHON_CMD=%APPDATA%\Python\Python310\python.exe
    goto :python_found
)

REM Check Program Files Python
if exist "C:\Program Files\Python312\python.exe" (
    echo Found Python 3.12 in Program Files
    set PYTHON_CMD=C:\Program Files\Python312\python.exe
    goto :python_found
)

if exist "C:\Program Files\Python311\python.exe" (
    echo Found Python 3.11 in Program Files
    set PYTHON_CMD=C:\Program Files\Python311\python.exe
    goto :python_found
)

if exist "C:\Program Files\Python310\python.exe" (
    echo Found Python 3.10 in Program Files
    set PYTHON_CMD=C:\Program Files\Python310\python.exe
    goto :python_found
)

REM Check Program Files (x86) Python
if exist "C:\Program Files (x86)\Python312\python.exe" (
    echo Found Python 3.12 in Program Files (x86)
    set PYTHON_CMD=C:\Program Files (x86)\Python312\python.exe
    goto :python_found
)

if exist "C:\Program Files (x86)\Python311\python.exe" (
    echo Found Python 3.11 in Program Files (x86)
    set PYTHON_CMD=C:\Program Files (x86)\Python311\python.exe
    goto :python_found
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    echo Found Python 3.10 in Program Files (x86)
    set PYTHON_CMD=C:\Program Files (x86)\Python310\python.exe
    goto :python_found
)

echo ERROR: Python not found on this system!
echo.
echo Please install Python from https://python.org
echo Or ensure Python is added to your PATH
echo.
echo Press any key to close...
pause > nul
exit /b 1

:python_found

echo Using: %PYTHON_CMD%
echo.
echo ========================================
echo COMPREHENSIVE AUDIT CHUNKS:
echo ========================================
echo 1. Complete File Discovery
echo 2. Python Applications Analysis  
echo 3. Batch Files & Launchers Analysis
echo 4. Core System Components
echo 5. Mesh VPN System Analysis
echo 6. Network & Monitoring Tools
echo 7. Resource Management Tools
echo 8. Core Services Integration
echo 9. Setup & Installation Tools
echo 10. Advanced & Experimental Components
echo.
echo This will provide ACCURATE counts for:
echo - All Python files (.py)
echo - All Batch files (.bat) 
echo - All C/C++ files (.cpp, .c, .h)
echo - Component functionality analysis
echo - System health assessment
echo.
echo Press any key to start the COMPREHENSIVE audit...
pause > nul
echo.
echo Starting COMPREHENSIVE chunked audit...
echo ========================================
echo.

%PYTHON_CMD% comprehensive_chunked_audit.py

echo.
echo.
echo ========================================
echo COMPREHENSIVE AUDIT COMPLETED!
echo ========================================
echo.
echo Results saved to: comprehensive_system_audit_results.json
echo.
echo This audit provides:
echo - Accurate component counts
echo - Functionality analysis
echo - System health assessment
echo - Detailed breakdown by category
echo.
echo Press any key to close this window...
pause > nul
