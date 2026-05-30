@echo off
title Homelab Tools System Audit
color 0A
echo ========================================
echo Homelab Tools - Chunked System Audit
echo ========================================
echo.
echo Finding Python installation...

REM Try to find Python
where python >nul 2>&1
if %errorlevel% == 0 (
    echo Found python command
    set PYTHON_CMD=python
) else (
    where py >nul 2>&1
    if %errorlevel% == 0 (
        echo Found py command
        set PYTHON_CMD=py
    ) else (
        echo Trying default Python paths...
        if exist "C:\Python39\python.exe" (
            set PYTHON_CMD=C:\Python39\python.exe
        ) else if exist "C:\Python310\python.exe" (
            set PYTHON_CMD=C:\Python310\python.exe
        ) else if exist "C:\Python311\python.exe" (
            set PYTHON_CMD=C:\Python311\python.exe
        ) else if exist "C:\Python312\python.exe" (
            set PYTHON_CMD=C:\Python312\python.exe
        ) else (
            echo ERROR: Python not found! Please install Python or add it to PATH.
            echo.
            echo Press any key to close...
            pause > nul
            exit /b 1
        )
    )
)

echo Using: %PYTHON_CMD%
echo.
echo This will run the system audit in this window
echo so you can see the progress in real-time.
echo.
echo Press any key to start the audit...
pause > nul
echo.
echo Starting chunked audit...
echo.

%PYTHON_CMD% chunked_system_audit.py

echo.
echo.
echo ========================================
echo Audit completed!
echo ========================================
echo.
echo Results saved to: comprehensive_system_audit_results.json
echo.
echo Press any key to close this window...
pause > nul
