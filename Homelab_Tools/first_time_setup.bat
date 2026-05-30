@echo off
setlocal enabledelayedexpansion
title Homelab Tools - First Time Setup
color 0A
echo.
echo="======================================="
echo    Homelab Tools - First Time Setup
echo="======================================="
echo.
echo This will set up the basic configuration
echo for Homelab Tools on your system.
echo.
pause

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [✓] Python found

:: Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

echo [✓] Git found

:: Setup Git LFS
echo Setting up Git LFS...
if exist git-lfs.exe (
    echo Using bundled Git LFS...
    .\git-lfs.exe install
) else (
    git lfs install
)

:: Install basic dependencies
echo Installing basic dependencies...
pip install psutil matplotlib numpy requests wmi

:: Create directories
echo Creating directories...
if not exist logs mkdir logs
if not exist cache mkdir cache
if not exist temp mkdir temp

:: Download LFS files
echo Downloading large files...
git lfs pull

:: Create basic config
echo Creating configuration...
echo # Homelab Tools - Basic Configuration > homelab_config.ini
echo update_interval="1000 >> homelab_config.ini"
echo cache_size="100 >> homelab_config.ini"
echo log_level="INFO >> homelab_config.ini"
echo gpu_enabled="True >> homelab_config.ini"

echo.
echo="======================================="
echo    Setup Complete!
echo="======================================="
echo.
echo You can now run: python homelab_launcher.py
echo.
pause
commit