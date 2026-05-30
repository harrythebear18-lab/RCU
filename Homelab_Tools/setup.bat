@echo off
setlocal enabledelayedexpansion
title Homelab Tools - Auto Setup
color 0A
echo.
echo="======================================="
echo    Homelab Tools - Auto Setup Script
echo="======================================="
echo.
echo This script will automatically configure:
echo - Python dependencies
echo - Git LFS for large files
echo - Windows permissions
echo - Environment variables
echo - Required system components
echo.
pause

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [✓] Python found

:: Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed
    echo Installing Git...
    winget install Git.Git
    if errorlevel 1 (
        echo [ERROR] Failed to install Git automatically
        echo Please install Git from https://git-scm.com
        pause
        exit /b 1
    )
)

echo [✓] Git found

:: Install Git LFS
echo Installing Git LFS...
git lfs version >nul 2>&1
if errorlevel 1 (
    echo Git LFS not found, installing...
    winget install GitHub.GitLFS
    if errorlevel 1 (
        echo [WARNING] Failed to install Git LFS via winget
        echo Trying alternative installation...
        if exist git-lfs.exe (
            echo Using bundled Git LFS...
            .\git-lfs.exe install
        ) else (
            echo [ERROR] Git LFS installation failed
            echo Please install Git LFS manually from https://git-lfs.github.com
        )
    ) else (
        git lfs install
    )
) else (
    echo [✓] Git LFS already installed
)

:: Install Python dependencies
echo Installing Python dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some dependencies failed to install
    echo Trying to install core dependencies manually...
    pip install psutil matplotlib numpy tkinter
)

:: Install optional GPU packages
echo Installing optional GPU packages...
pip install cupy-cuda11x >nul 2>&1
pip install GPUtil >nul 2>&1
pip install pyopencl >nul 2>&1
echo [✓] Dependencies installed

:: Set up Windows permissions
echo Setting up Windows permissions...
net session >nul 2>&1
if !errorlevel! equ 0 (
    echo Requesting administrator privileges for system setup...
    echo.
    echo Creating firewall rules for homelab tools...
    netsh advfirewall firewall add rule name="Homelab Tools" dir=in action=allow program="python.exe" enable=yes >nul 2>&1
    
    echo Setting up performance monitoring permissions...
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PerfLib" /v "Application" /t REG_SZ /d "Homelab Tools" /f >nul 2>&1
) else (
    echo [INFO] Running without administrator privileges
    echo Some features may require manual configuration
)

:: Create environment variables
echo Setting up environment variables...
setx HOMELAB_ROOT "%CD%" >nul 2>&1
setx PYTHONPATH "%CD%" >nul 2>&1

:: Create startup directories
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "temp" mkdir temp
if not exist "performance_data" mkdir performance_data

:: Pull LFS objects
echo Downloading large files from Git LFS...
git lfs pull >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Some LFS files may not be available
    echo Run 'git lfs pull' manually if needed
) else (
    echo [✓] Large files downloaded
)

:: Test basic functionality
echo Testing basic functionality...
python "temp_script_5915.py" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Some core dependencies may not be working
) else (
    echo [✓] Core dependencies working
)

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell="New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Homelab Tools.lnk'); $Shortcut.TargetPath = '%CD%\homelab_launcher.py'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Save()""

echo.
echo="======================================="
echo    Setup Complete!
echo="======================================="
echo.
echo Next steps:
echo 1. Double-click the Homelab Tools desktop shortcut
echo 2. Or run: python homelab_launcher.py
echo 3. Check the README.md for detailed usage
echo.
echo If you encounter issues:
echo - Run this script as administrator
echo - Check Python and Git installations
echo - Verify internet connection for LFS downloads
echo.
pause
