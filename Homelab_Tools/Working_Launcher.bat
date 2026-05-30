@echo off
setlocal enabledelayedexpansion
title RAM Sharing Tools - Working Launcher
echo="==============================================="
echo    RAM SHARING TOOLS - WORKING LAUNCHER
echo="==============================================="
echo.
echo This launcher works on ANY Windows system
echo No Python required for basic functions
echo.

echo Choose what you want to do:
echo.
echo 1. START RAM SHARING SERVER (PC 1 - 192.168.1.186)
echo 2. CONNECT TO RAM SERVER (PC 2 - 192.168.1.132)
echo 3. STOP SERVER / CLEANUP
echo 4. FIX WINDOWS COMPATIBILITY ISSUES
echo 5. TEST NETWORK CONNECTION
echo 6. EXIT
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"="="1" goto start_server"
if "%choice%"="="2" goto connect_server"
if "%choice%"="="3" goto cleanup"
if "%choice%"="="4" goto fix_compat"
if "%choice%"="="5" goto test_network"
if "%choice%"="="6" goto exit_program"

echo Invalid choice. Please try again.
pause
goto start

:start_server
echo.
echo="======================================="
echo STARTING RAM SHARING SERVER
echo="======================================="
echo.
echo This will create a 4GB RAM disk and share it
echo Server IP: 192.168.1.186
echo.
pause

echo Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Please run as Administrator
    pause
    goto start
)

echo Starting server setup...
call Setup_RAM_Sharing.bat

echo.
echo Server setup completed!
pause
goto start

:connect_server
echo.
echo="======================================="
echo CONNECTING TO RAM SERVER
echo="======================================="
echo.
echo This will connect to the RAM sharing server
echo Server IP: 192.168.1.186
echo.
pause

echo Connecting to server...
call Map_RAM_Sharing.bat

echo.
echo Connection attempt completed!
pause
goto start

:cleanup
echo.
echo="======================================="
echo CLEANUP - STOP SERVER
echo="======================================="
echo.
echo This will stop the server and remove all components
echo.
pause

echo Starting cleanup...
call Cleanup_RAM_Sharing.bat

echo.
echo Cleanup completed!
pause
goto start

:fix_compat
echo.
echo="======================================="
echo FIXING WINDOWS COMPATIBILITY
echo="======================================="
echo.
echo This fixes issues between Windows 10 and 11
echo Run this on BOTH PCs as Administrator
echo.
pause

echo Checking administrator privileges...
net session >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Please run as Administrator
    pause
    goto start
)

echo Applying compatibility fixes...
call Fix_Windows_Compatibility.bat

echo.
echo Compatibility fixes applied!
pause
goto start

:test_network
echo.
echo="======================================="
echo TESTING NETWORK CONNECTION
echo="======================================="
echo.
echo Testing connection between PCs...
echo.

echo Pinging 192.168.1.132 (client PC)...
ping -n 3 192.168.1.132

if !errorlevel! equ 0 (
    echo.
    echo SUCCESS: Network connection is working!
) else (
    echo.
    echo FAILED: Network connection not working
    echo Check:
    echo - Both PCs are on same network
    echo - No firewall blocking
    echo - IP addresses are correct
)

echo.
pause
goto start

:exit_program
echo.
echo Goodbye!
exit /b 0
