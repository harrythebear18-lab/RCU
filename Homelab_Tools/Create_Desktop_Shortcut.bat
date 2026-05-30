@echo off
setlocal enabledelayedexpansion
title Create Desktop Shortcut
echo="==============================================="
echo    CREATE RAM SHARING DESKTOP SHORTCUT
echo="==============================================="
echo.

REM Get current directory
set SCRIPT_DIR="%~dp0"
set SCRIPT_DIR="%SCRIPT_DIR:~0,-1%"

REM Create VBScript to make shortcut
echo Set oWS="WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs""
echo sLinkFile = "%USERPROFILE%\Desktop\RAM Sharing Manager.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink="oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs""
echo oLink.TargetPath = "%SCRIPT_DIR%\Launch_RAM_Sharing.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Homelab RAM Sharing Manager" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,13" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

REM Execute VBScript
cscript //nologo "%TEMP%\CreateShortcut.vbs"

REM Cleanup
del "%TEMP%\CreateShortcut.vbs"

if exist "%USERPROFILE%\Desktop\RAM Sharing Manager.lnk" (
    echo SUCCESS: Desktop shortcut created!
    echo.
    echo You can now launch RAM Sharing Manager from your desktop
) else (
    echo ERROR: Failed to create desktop shortcut
)

echo.
pause
