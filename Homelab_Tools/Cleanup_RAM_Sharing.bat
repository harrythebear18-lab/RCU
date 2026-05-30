@echo off
setlocal enabledelayedexpansion
title Cleanup RAM Sharing Setup
echo="==============================================="
echo    CLEANUP RAM SHARING SETUP - HOMELAB
echo="==============================================="
echo.
echo This script will remove all RAM sharing components:
echo - RAM disk
echo - SMB shares
echo - iSCSI targets
echo.
echo WARNING: This will disconnect any active RAM sharing!
echo.
pause

echo.
echo Removing RAM sharing setup...
powershell -ExecutionPolicy Bypass -File "Robust_RAM_Sharing.ps1" -Action cleanup

if !errorlevel! equ 0 (
    echo.
    echo SUCCESS: RAM sharing cleanup completed!
) else (
    echo.
    echo ERROR: Cleanup failed. Check error messages above.
)

echo.
pause
