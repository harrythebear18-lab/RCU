@echo off
setlocal enabledelayedexpansion
title RAM Sharing Tools Launcher
echo="==============================================="
echo    RAM SHARING TOOLS LAUNCHER
echo="==============================================="
echo.
echo Choose an option:
echo.
echo 1. Start RAM Sharing Server
echo 2. Connect to RAM Server  
echo 3. Stop Server / Cleanup
echo 4. Fix Windows Compatibility
echo 5. Test Connection
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"="="1" goto start_server"
if "%choice%"="="2" goto connect_server"
if "%choice%"="="3" goto stop_server"
if "%choice%"="="4" goto fix_compatibility"
if "%choice%"="="5" goto test_connection"
if "%choice%"="="6" goto exit_program"

echo Invalid choice
pause
exit

:start_server
echo.
echo Starting RAM sharing server...
call Setup_RAM_Sharing.bat
pause
exit

:connect_server
echo.
echo Connecting to RAM server...
call Map_RAM_Sharing.bat
pause
exit

:stop_server
echo.
echo Stopping server and cleanup...
call Cleanup_RAM_Sharing.bat
pause
exit

:fix_compatibility
echo.
echo Fixing Windows compatibility...
call Fix_Windows_Compatibility.bat
pause
exit

:test_connection
echo.
echo Testing connection to 192.168.1.132...
ping -n 3 192.168.1.132
if !errorlevel! equ 0 (
    echo Connection successful!
) else (
    echo Connection failed!
)
pause
exit

:exit_program
echo Goodbye!
exit
