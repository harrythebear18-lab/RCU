@echo off
setlocal enabledelayedexpansion
title Quick Auto RAM Connect
echo="==============================================="
echo    QUICK AUTO RAM CONNECT
echo="==============================================="
echo.
echo One-click RAM sharing setup and connection
echo Automatically detects server/client and configures
echo.

REM Quick auto-detection and setup
echo Detecting system role...

REM Simple RAM-based detection
for /f "tokens="2 delims==" %%a in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do set RAM_BYTES=%%a"
set /a RAM_GB="%RAM_BYTES:~0,-9% / 1073741824"

echo System RAM: %RAM_GB%GB

if %RAM_GB% GEQ 16 (
    echo.
    echo 🖥️  CONFIGURING AS SERVER
echo="========================="
    echo.
    echo Step 1: Fixing compatibility...
    call Fix_Windows_Compatibility.bat >nul 2>&1
    
    echo Step 2: Setting up RAM sharing...
    call Setup_RAM_Sharing.bat
    
    echo.
    echo ✅ Server setup complete!
    echo RAM disk is now shared and ready for client connection
    
) else (
    echo.
    echo 🔗 CONFIGURING AS CLIENT
echo="======================="
    echo.
    echo Step 1: Testing server connection...
    ping -n 2 192.168.1.186 >nul
    if !errorlevel! neq 0 (
        echo ❌ Cannot reach server at 192.168.1.186
        echo Make sure server is running first
        pause
        exit /b 1
    )
    
    echo Step 2: Connecting to server...
    call Map_RAM_Sharing.bat
    
    echo.
    echo ✅ Client connection complete!
    echo RAM disk from server is now available
)

echo.
echo 🎉 Auto-connection completed successfully!
echo.
echo Next steps:
echo - Use the RAM disk as high-speed storage
echo - Monitor performance with RAM sharing tools
echo - Both systems now share RAM resources
echo.
pause
