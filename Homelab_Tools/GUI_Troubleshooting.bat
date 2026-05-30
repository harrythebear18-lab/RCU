@echo off
setlocal enabledelayedexpansion
title GUI Troubleshooting
echo="==============================================="
echo    RAM SHARING GUI TROUBLESHOOTING
echo="==============================================="
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Python found: python
set PYTHON_CMD="python"
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Python found: py
set PYTHON_CMD="py"
    ) else (
        echo ❌ Python not found
        echo Please install Python 3.7+ from python.org
        goto :end
    )
)

echo.
echo [2/5] Checking GUI files...
if exist "RAM_Sharing_GUI.py" (
    echo ✅ Original GUI file found
) else (
    echo ❌ Original GUI file missing
)

if exist "RAM_Sharing_Simple_GUI.py" (
    echo ✅ Simple GUI file found
) else (
    echo ❌ Simple GUI file missing
)

echo.
echo [3/5] Testing tkinter availability...
%PYTHON_CMD% -c "import tkinter; print('tkinter available')" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ tkinter available (original GUI should work)
) else (
    echo ❌ tkinter not available (use simple GUI)
)

echo.
echo [4/5] Testing PowerShell execution...
powershell -Command "Get-ExecutionPolicy" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ PowerShell execution working
) else (
    echo ❌ PowerShell execution issues
    echo Run Fix_Windows_Compatibility.bat as Administrator
)

echo.
echo [5/5] Testing required scripts...
if exist "Robust_RAM_Sharing.ps1" (
    echo ✅ RAM sharing script found
) else (
    echo ❌ RAM sharing script missing
)

if exist "Windows_Compatibility_Fix.ps1" (
    echo ✅ Compatibility fix script found
) else (
    echo ❌ Compatibility fix script missing
)

echo.
echo="======================================="
echo RECOMMENDATIONS:
echo="======================================="
echo.

if exist "RAM_Sharing_Simple_GUI.py" (
    echo Use: Launch_Simple_GUI.bat
    echo (No tkinter required, works on all systems)
) else (
    echo Install missing files or use batch scripts directly
)

echo.
echo Alternative methods:
echo 1. Setup_RAM_Sharing.bat (server setup)
echo 2. Map_RAM_Sharing.bat (client connection)
echo 3. Cross_Version_Setup.bat (complete setup)

:end
echo.
pause
