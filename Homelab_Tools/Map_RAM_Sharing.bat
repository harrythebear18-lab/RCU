@echo off
setlocal enabledelayedexpansion
title Map RAM Disk from Other PC
echo="==============================================="
echo    MAP RAM DISK FROM OTHER PC - HOMELAB
echo="==============================================="
echo.
echo This script will connect to RAM disk shared from:
echo Source PC: 192.168.1.186
echo Target PC: 192.168.1.132
echo.
echo It will try multiple connection methods automatically:
echo 1. iSCSI Target (better performance)
echo 2. SMB Share (more compatible)
echo.
pause

echo.
echo [1/3] Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: This script requires administrator privileges
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)
echo SUCCESS: Administrator privileges confirmed

echo.
echo [2/3] Connecting to RAM disk from 192.168.1.186...
powershell -ExecutionPolicy Bypass -File "Robust_RAM_Sharing.ps1" -Action map -TargetIP 192.168.1.186

if !errorlevel! equ 0 (
    echo.
    echo SUCCESS: RAM disk mapped successfully!
    echo.
    echo Check your "This PC" for new drives:
    echo - Drive Z: (SMB share) or
    echo - Drive with highest letter (iSCSI)
    echo.
    echo You can now use this as high-speed storage!
    echo This is actually using RAM from the other PC.
) else (
    echo.
    echo ERROR: Failed to map RAM disk
    echo Make sure:
    echo 1. RAM sharing is set up on 192.168.1.186
    echo 2. Both PCs are on the same network
    echo 3. Windows Firewall allows file sharing
)

echo.
echo [3/3] Testing performance...
powershell -ExecutionPolicy Bypass -File "Robust_RAM_Sharing.ps1" -Action test

echo.
pause
