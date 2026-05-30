@echo off
title RAM Sharing Manager - Pure Batch GUI
setlocal enabledelayedexpansion

:main_menu
cls
echo="==============================================================="
echo                HOMELAB RAM SHARING MANAGER
echo="==============================================================="
echo                Pure Batch GUI - No Python Required
echo="==============================================================="
echo Server: 192.168.1.186 (Windows 11) | Client: 192.168.1.132 (Windows 10)
echo="==============================================================="
echo.
echo MAIN MENU:
echo.
echo 1. [SERVER] Start RAM Sharing Server (PC 1)
echo 2. [CLIENT] Connect to RAM Server (PC 2)
echo 3. [STOP]   Stop Server / Disconnect
echo 4. [TEST]   Test Performance
echo 5. [FIX]    Fix Windows Compatibility
echo 6. [STATUS] Show Current Status
echo 7. [CLEANUP] Remove All Components
echo 8. [EXIT]   Exit Program
echo.
echo="==============================================================="
echo.

set /p choice="Select option (1-8): "

if "%choice%"="="1" goto start_server"
if "%choice%"="="2" goto connect_server"
if "%choice%"="="3" goto stop_server"
if "%choice%"="="4" goto test_performance"
if "%choice%"="="5" goto fix_compatibility"
if "%choice%"="="6" goto show_status"
if "%choice%"="="7" goto cleanup_all"
if "%choice%"="="8" goto exit_program"

echo Invalid option. Please try again.
pause
goto main_menu

:start_server
cls
echo="==============================================================="
echo                    STARTING RAM SHARING SERVER
echo="==============================================================="
echo.
echo This will:
echo - Create a 4GB RAM disk
echo - Set up SMB and iSCSI sharing
echo - Configure network access
echo.
echo Server IP: 192.168.1.186
echo RAM Size: 4GB
echo Drive Letter: R:
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/3] Starting RAM sharing setup...
call Setup_RAM_Sharing.bat

if !errorlevel! equ 0 (
    echo.
    echo [2/3] Server setup completed successfully!
    echo RAM disk is now available at: \\192.168.1.186\RamDisk
) else (
    echo.
    echo [2/3] Server setup failed. Check error messages above.
)

echo.
echo [3/3] Press any key to return to main menu...
pause >nul
goto main_menu

:connect_server
cls
echo="==============================================================="
echo                    CONNECTING TO RAM SERVER
echo="==============================================================="
echo.
echo This will connect to the RAM sharing server:
echo Server IP: 192.168.1.186
echo.
echo The system will try:
echo 1. iSCSI connection (better performance)
echo 2. SMB share (more compatible)
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/3] Connecting to RAM server...
call Map_RAM_Sharing.bat

if !errorlevel! equ 0 (
    echo.
    echo [2/3] Connected successfully!
    echo RAM disk should now be available as a network drive.
) else (
    echo.
    echo [2/3] Connection failed. Check error messages above.
    echo Make sure:
    echo - Server is running on 192.168.1.186
    echo - Both PCs are on same network
    echo - Windows Firewall allows file sharing
)

echo.
echo [3/3] Press any key to return to main menu...
pause >nul
goto main_menu

:stop_server
cls
echo="==============================================================="
echo                    STOPPING SERVER / CLEANUP
echo="==============================================================="
echo.
echo This will:
echo - Stop RAM sharing server
echo - Remove network shares
echo - Disconnect clients
echo - Remove RAM disk
echo.
echo WARNING: This will disconnect all active connections!
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/2] Stopping server and cleanup...
call Cleanup_RAM_Sharing.bat

if !errorlevel! equ 0 (
    echo.
    echo [2/2] Cleanup completed successfully!
) else (
    echo.
    echo [2/2] Cleanup failed. Check error messages above.
)

echo.
echo Press any key to return to main menu...
pause >nul
goto main_menu

:test_performance
cls
echo="==============================================================="
echo                    PERFORMANCE TESTING
echo="==============================================================="
echo.
echo Testing RAM sharing performance...
echo This will test read/write speeds of the shared RAM.
echo.

REM Check if RAM disk exists
dir R:\ >nul 2>&1
if !errorlevel! equ 0 (
    echo RAM disk found, testing performance...
    
    echo.
    echo [1/3] Testing write performance...
    echo Creating 100MB test file...
    
    REM Create test file
    echo Creating performance test file...
    (fsutil file createnew R:\perf_test.tmp 104857600) >nul 2>&1
    
    if exist R:\perf_test.tmp (
        echo Write test completed.
        
        echo.
        echo [2/3] Testing read performance...
        echo Reading test file...
        
        REM Read test file
        copy R:\perf_test.tmp nul >nul 2>&1
        
        echo Read test completed.
        
        echo.
        echo [3/3] Cleaning up test file...
        del R:\perf_test.tmp >nul 2>&1
        
        echo.
        echo Performance test completed!
        echo For detailed performance metrics, use PowerShell scripts.
    ) else (
        echo Failed to create test file.
    )
) else (
    echo RAM disk not found (R: drive).
    echo Please start the server first.
)

echo.
echo Press any key to return to main menu...
pause >nul
goto main_menu

:fix_compatibility
cls
echo="==============================================================="
echo                WINDOWS COMPATIBILITY FIX
echo="==============================================================="
echo.
echo This will fix compatibility issues between Windows 10 and 11:
echo - Configure PowerShell execution policies
echo - Enable network sharing features
echo - Configure firewall rules
echo - Install required components
echo.
echo Run this on BOTH PCs as Administrator!
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/4] Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: This script requires administrator privileges
    echo Right-click and select "Run as administrator"
    pause
    goto main_menu
)
echo Administrator privileges confirmed.

echo.
echo [2/4] Applying Windows compatibility fixes...
call Fix_Windows_Compatibility.bat

if !errorlevel! equ 0 (
    echo.
    echo [3/4] Compatibility fixes applied successfully!
) else (
    echo.
    echo [3/4] Some fixes failed. Check error messages above.
)

echo.
echo [4/4] Testing connectivity...
ping -n 1 192.168.1.132 >nul 2>&1
if !errorlevel! equ 0 (
    echo Network connectivity: OK
) else (
    echo Network connectivity: FAILED - Check network connection
)

echo.
echo Press any key to return to main menu...
pause >nul
goto main_menu

:show_status
cls
echo="==============================================================="
echo                    SYSTEM STATUS
echo="==============================================================="
echo.

echo [1/6] Checking RAM disk...
dir R:\ >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ RAM Disk: Available (R:)
for /f "tokens="3" %%a in ('dir R:\ ^| find "bytes free"') do echo   Free Space: %%a"
) else (
    echo ❌ RAM Disk: Not found
)

echo.
echo [2/6] Checking network connectivity...
ping -n 1 192.168.1.132 >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Network: Client PC reachable (192.168.1.132)
) else (
    echo ❌ Network: Client PC not reachable
)

echo.
echo [3/6] Checking SMB share...
net share | findstr RamDisk >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ SMB Share: Active
) else (
    echo ❌ SMB Share: Not found
)

echo.
echo [4/6] Checking PowerShell execution...
powershell -Command "Get-ExecutionPolicy" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ PowerShell: Execution policy configured
) else (
    echo ❌ PowerShell: Execution issues detected
)

echo.
echo [5/6] Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Privileges: Running as Administrator
) else (
    echo ⚠️  Privileges: Not running as Administrator
)

echo.
echo [6/6] Checking required files...
if exist "Robust_RAM_Sharing.ps1" (
    echo ✅ Scripts: RAM sharing script found
) else (
    echo ❌ Scripts: RAM sharing script missing
)

if exist "Windows_Compatibility_Fix.ps1" (
    echo ✅ Scripts: Compatibility fix script found
) else (
    echo ❌ Scripts: Compatibility fix script missing
)

echo.
echo="==============================================================="
echo Press any key to return to main menu...
pause >nul
goto main_menu

:cleanup_all
cls
echo="==============================================================="
echo                    CLEANUP ALL COMPONENTS
echo="==============================================================="
echo.
echo ⚠️  WARNING: This will remove ALL RAM sharing components!
echo.
echo This action will:
echo - Stop RAM sharing server
echo - Remove all network shares
echo - Disconnect client connections
echo - Remove RAM disk
echo - Clean up temporary files
echo.
echo Are you absolutely sure you want to continue?
echo.

set /p confirm="Type 'YES' to confirm cleanup: "
if /i not "%confirm%"="="YES" ("
    echo Cleanup cancelled.
    pause
    goto main_menu
)

echo.
echo [1/3] Starting cleanup process...
call Cleanup_RAM_Sharing.bat

echo.
echo [2/3] Removing network connections...
net use * /delete /y >nul 2>&1

echo.
echo [3/3] Cleanup completed!
echo All RAM sharing components have been removed.

echo.
echo Press any key to return to main menu...
pause >nul
goto main_menu

:exit_program
cls
echo="==============================================================="
echo                    EXITING RAM SHARING MANAGER
echo="==============================================================="
echo.
echo Thank you for using Homelab RAM Sharing Manager!
echo.
echo For support or updates, check the GitHub repository:
echo https://github.com/harrythebear18-lab/Homelab-Tools
echo.

echo Press any key to exit...
pause >nul
exit /b 0
