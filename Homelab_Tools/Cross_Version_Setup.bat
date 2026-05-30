@echo off
setlocal enabledelayedexpansion
title Complete Cross-Version Setup
echo="==============================================="
echo    COMPLETE WINDOWS 10/11 SETUP
echo="==============================================="
echo.
echo This script performs the complete setup for
echo Windows 10 to Windows 11 RAM sharing
echo.
echo Current PC: Windows 11 (Build 26200)
echo Target PC: Windows 10 (192.168.1.132)
echo.
echo This will:
echo 1. Fix Windows compatibility issues
echo 2. Install required components
echo 3. Configure network settings
echo 4. Set up RAM sharing
echo 5. Test connectivity
echo.
echo IMPORTANT: Run as Administrator
echo.
pause

echo.
echo="======================================="
echo STEP 1: WINDOWS COMPATIBILITY FIXES
echo="======================================="
echo.

call Fix_Windows_Compatibility.bat

echo.
echo="======================================="
echo STEP 2: RAM SHARING SETUP
echo="======================================="
echo.

echo Setting up RAM sharing on this PC...
call Setup_RAM_Sharing.bat

echo.
echo="======================================="
echo STEP 3: FINAL VERIFICATION
echo="======================================="
echo.

echo Verifying setup completion...
powershell -ExecutionPolicy Bypass -File "Windows_Compatibility_Fix.ps1" -Action test

echo.
echo="======================================="
echo SETUP COMPLETED!
echo="======================================="
echo.
echo Your Windows 11 PC is now configured to share RAM
echo with the Windows 10 PC at 192.168.1.132
echo.
echo On the Windows 10 PC (192.168.1.132):
echo 1. Run Fix_Windows_Compatibility.bat (as Admin)
echo 2. Run Map_RAM_Sharing.bat (as Admin)
echo.
echo For easy management, use:
echo - Launch_RAM_Sharing.bat (GUI interface)
echo - Create_Desktop_Shortcut.bat (desktop access)
echo.
echo Troubleshooting:
echo - If connection fails, check Windows Firewall
echo - Ensure both PCs are on same network
echo - Verify SMB sharing is enabled
echo - Run as Administrator on both PCs
echo.

pause
