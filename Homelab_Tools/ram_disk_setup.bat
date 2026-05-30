@echo off
setlocal enabledelayedexpansion
echo Setting up RAM Disk for network sharing...
echo.

REM Download and install ImDisk (if not already installed)
REM This creates a virtual RAM disk that can be shared over network

echo Creating 4GB RAM disk as drive R:
imdisk -a -s 4G -m R: -p "/fs:ntfs /q /y"

if %ERRORLEVEL% EQU 0 (
    echo ✅ RAM disk created successfully as R:
    echo.
    echo Setting up network share...
net share RamDisk="R:\ /grant:Everyone,FULL"
    
    echo ✅ RAM disk shared as \\192.168.1.186\RamDisk
    echo.
    echo You can now map this on the other PC as network drive
) else (
    echo ❌ Failed to create RAM disk
    echo Please install ImDisk first: https://sourceforge.net/projects/imdisk-toolkit/
)

pause
