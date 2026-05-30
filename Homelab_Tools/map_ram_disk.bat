@echo off
setlocal enabledelayedexpansion
echo Mapping network RAM disk from 192.168.1.186...
echo.

REM Map the shared RAM disk as drive Z:
net use Z: \\192.168.1.186\RamDisk /persistent:yes

if %ERRORLEVEL% EQU 0 (
    echo ✅ Successfully mapped RAM disk as Z: drive
    echo.
    echo You can now use Z: as high-speed storage
    echo This is actually using RAM from the other PC!
) else (
    echo ❌ Failed to map RAM disk
    echo Make sure:
    echo 1. RAM disk is created and shared on 192.168.1.186
    echo 2. Both PCs are on the same network
    echo 3. Network discovery is enabled
)

pause
