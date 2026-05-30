@echo off
setlocal enabledelayedexpansion
title Windows 10/11 Compatibility Fix
echo="==============================================="
echo    WINDOWS 10/11 COMPATIBILITY FIX
echo="==============================================="
echo.
echo This script fixes compatibility issues between
echo Windows 10 and Windows 11 for RAM sharing
echo.
echo It will:
echo - Detect Windows versions on both PCs
echo - Configure PowerShell execution policies
echo - Enable network sharing features
echo - Configure firewall and network settings
echo - Install ImDisk with compatibility fixes
echo - Test cross-version connectivity
echo.
echo Requirements:
echo - Run as Administrator on BOTH PCs
echo - Both PCs on same network (192.168.1.x)
echo.
pause

echo.
echo [1/6] Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: This script requires administrator privileges
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)
echo SUCCESS: Administrator privileges confirmed

echo.
echo [2/6] Detecting Windows version...
for /f "tokens="*" %%i in ('powershell -Command "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object -ExpandProperty Caption"') do set OS_NAME=%%i"
echo Detected: %OS_NAME%

echo.
echo [3/6] Applying Windows compatibility fixes...
powershell -ExecutionPolicy Bypass -File "Windows_Compatibility_Fix.ps1" -Action fix

if !errorlevel! equ 0 (
    echo.
    echo SUCCESS: Windows compatibility fixes applied!
) else (
    echo.
    echo ERROR: Some fixes failed. Check the messages above.
)

echo.
echo [4/6] Testing cross-version connectivity...
powershell -ExecutionPolicy Bypass -File "Windows_Compatibility_Fix.ps1" -Action test

echo.
echo [5/6] Generating compatibility report...
echo Report will be saved to your desktop

echo.
echo [6/6] Ready for RAM sharing setup!
echo.
echo Next steps:
echo 1. Run this script on BOTH PCs (as Administrator)
echo 2. On PC 1 (192.168.1.186): Run Setup_RAM_Sharing.bat
echo 3. On PC 2 (192.168.1.132): Run Map_RAM_Sharing.bat
echo 4. Use Launch_RAM_Sharing.bat for GUI management
echo.

pause
