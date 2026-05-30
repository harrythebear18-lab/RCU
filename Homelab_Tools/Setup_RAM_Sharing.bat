@echo off
setlocal enabledelayedexpansion
title Robust RAM Sharing Setup
echo="==============================================="
echo    ROBUST RAM SHARING SETUP - HOMELAB
echo="==============================================="
echo.
echo This script will set up multiple RAM sharing methods:
echo - RAM Disk + SMB Share (Simple, compatible)
echo - RAM Disk + iSCSI Target (Better performance)
echo.
echo Requirements:
echo - Windows 10/11 Pro/Enterprise/Server
echo - Administrator privileges
echo - Both PCs on same network (192.168.1.x)
echo.
echo Current PC IP: 192.168.1.186
echo Target PC IP: 192.168.1.132
echo.
pause

echo.
echo [1/4] Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: This script requires administrator privileges
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)
echo SUCCESS: Administrator privileges confirmed

echo.
echo [2/5] Installing required Windows features...
powershell -Command "Install-WindowsFeature -Name FS-FileServer,FS-iSCSITarget-Server -IncludeManagementTools -ErrorAction SilentlyContinue"

echo.
echo [3/5] Setting up RAM sharing with PowerShell...
powershell -ExecutionPolicy Bypass -File "Robust_RAM_Sharing.ps1" -Action setup -RAMSizeGB 4 -DriveLetter R

if !errorlevel! equ 0 (
    echo.
    echo SUCCESS: RAM sharing setup completed!
    echo.
    echo Available sharing methods:
    echo - SMB Share: \\192.168.1.186\RamDisk
    echo - iSCSI Target: RAMDiskTarget
    echo.
    echo On the other PC (192.168.1.132), run:
    echo powershell -ExecutionPolicy Bypass -File "Robust_RAM_Sharing.ps1" -Action map -TargetIP 192.168.1.186
) else (
    echo.
    echo ERROR: Setup failed. Check the error messages above.
)

echo.
pause
