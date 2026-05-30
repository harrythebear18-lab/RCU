@echo off
echo ========================================
echo Homelab Tools - WireGuard Installer
echo ========================================
echo.

echo Checking system requirements...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Starting WireGuard installation...
python setup\wireguard_installer.py

if errorlevel 1 (
    echo.
    echo Installation failed. Check logs\wireguard_installer.log for details.
    pause
    exit /b 1
)

echo.
echo WireGuard installation completed successfully!
echo.
echo Next steps:
echo 1. Run: python "Network Management\bidirectional_mesh_setup.py"
echo 2. Follow the deployment instructions
echo 3. Start the mesh VPN using the provided scripts
echo.
pause
