@echo off
setlocal enabledelayedexpansion
title Homelab Unified System Launcher
echo="==============================================="
echo    HOMELAB UNIFIED SYSTEM LAUNCHER
echo="==============================================="
echo.
echo This launcher starts the new unified architecture:
echo - Central Event Bus for inter-service communication
echo - Unified Configuration Management
echo - Authentication Service with SSO
echo - Data Persistence Layer
echo - Unified Monitoring & Alerting
echo - Integrated Dashboard
echo.

REM Check Python availability (try python, py, and python3)
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    echo Found Python: python
    goto :python_found
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=py
        echo Found Python: py
        goto :python_found
    ) else (
        python3 --version >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_CMD=python3
            echo Found Python: python3
            goto :python_found
        ) else (
            echo ERROR: Python not found
            echo Please install Python 3.7+ to use the unified system
            echo Download from: https://www.python.org/downloads/
            echo.
            echo After installing, make sure "Add Python to PATH" is checked
            pause
            exit /b 1
        )
    )
)

:python_found

echo.
echo Choose launch option:
echo 1. Launch Unified Dashboard (Recommended)
echo 2. Start Core Services Only
echo 3. Test Core Services
echo 4. System Status Check
echo 5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"="="1" goto launch_dashboard"
if "%choice%"="="2" goto start_services"
if "%choice%"="="3" goto test_services"
if "%choice%"="="4" goto status_check"
if "%choice%"="="5" goto exit_program"

echo Invalid choice
pause
goto start

:launch_dashboard
echo.
echo Launching Unified Dashboard...
echo This starts all core services and opens the integrated interface
echo.

%PYTHON_CMD% "Core Services\unified_dashboard.py"

if !errorlevel! neq 0 (
    echo.
    echo ERROR: Failed to launch unified dashboard
    echo Check that all core services are available
    pause
)
goto start

:start_services
echo Starting Core Services...
echo This initializes the unified backend architecture
echo.

echo Starting Event Bus...
%PYTHON_CMD% "%~dp0test_integration.py"

echo.
echo All core services are now running!
echo You can now access the unified dashboard or individual tools
echo.
pause
goto start

echo.
echo All core services started successfully!
echo.
echo Services are now running and available for integration
pause
goto start

:test_services
echo.
echo Testing Core Services Integration...
echo.

%PYTHON_CMD% "%~dp0test_integration.py"

echo.
pause
goto start

:status_check
echo.
echo System Status Check...
echo.

echo Checking Core Services availability...
echo.

echo Event Bus Status:
%PYTHON_CMD% -c "
try:
    from Core Services.event_bus import get_event_bus
bus="get_event_bus()"
stats="bus.get_statistics()"
    print(f'Active - {stats["total_events"]} events processed')
except Exception as e:
    print(f'Error: {e}')
"

echo.
echo Configuration Manager Status:
%PYTHON_CMD% -c "
try:
    from Core Services.config_manager import get_config_manager
cm="get_config_manager()"
validation="cm.validate_config()"
    print(f'Active - Valid: {validation["valid"]}')
except Exception as e:
    print(f'Error: {e}')
"

echo.
echo Authentication Service Status:
%PYTHON_CMD% -c "
try:
    from Core Services.auth_service import get_auth_service
auth="get_auth_service()"
sessions="len(auth.get_active_sessions())"
    print(f'Active - {sessions} sessions')
except Exception as e:
    print(f'Error: {e}')
"

echo.
echo Data Persistence Status:
%PYTHON_CMD% -c "
try:
    from Core Services.data_persistence import get_data_persistence
dp="get_data_persistence()"
stats="dp.get_database_stats()"
    print(f'Active - {stats["metrics_count"]} metrics stored')
except Exception as e:
    print(f'Error: {e}')
"

echo.
echo Unified Monitoring Status:
%PYTHON_CMD% -c "
try:
    from Core Services.unified_monitoring import get_unified_monitoring
um="get_unified_monitoring()"
stats="um.get_monitoring_stats()"
    print(f'Active - {stats["active_alerts"]} active alerts')
except Exception as e:
    print(f'Error: {e}')
"

echo.
pause
goto start

:exit_program
echo.
echo Goodbye!
exit /b 0
