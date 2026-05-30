@echo off
setlocal enabledelayedexpansion
title Homelab Tools Universal Installer - Windows 10/11
echo="==============================================="
echo    HOMELAB TOOLS UNIVERSAL INSTALLER
echo    Compatible with Windows 10 and Windows 11
echo="==============================================="
echo.

REM Check for administrator privileges
net session >nul 2>&1
if !errorlevel! equ 0 (
    echo Running with administrator privileges
) else (
    echo Note: Running without administrator privileges
    echo Some features may require elevated access
)
echo.

REM Detect Windows version
ver | findstr /i "10\.0" > nul
if !errorlevel! equ 0 (
    ver | find "22000" > nul
    if !errorlevel! equ 0 (
        echo Detected: Windows 11
set "WINDOWS_VERSION="11""
    ) else (
        echo Detected: Windows 10
set "WINDOWS_VERSION="10""
    )
) else (
    echo Warning: Unsupported Windows version
    echo This installer is designed for Windows 10 and 11
    pause
    exit /b 1
)

echo.
echo Checking Python installation...

REM Check Python availability (try multiple methods)
echo Method 1: Checking PATH for python...
python --version >nul 2>&1
if !errorlevel! equ 0 (
set "PYTHON_CMD="python""
    echo Found Python: python
    goto python_found
)

echo Method 2: Checking PATH for py...
py --version >nul 2>&1
if !errorlevel! equ 0 (
set "PYTHON_CMD="py""
    echo Found Python: py
    goto python_found
)

echo Method 3: Checking Windows Apps...
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
set "PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe""
    echo Found Python: Windows Apps python
    goto python_found
)

if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\py.exe" (
set "PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\py.exe""
    echo Found Python: Windows Apps py
    goto python_found
)

echo Method 4: Checking common installation paths...
if exist "%PROGRAMFILES%\Python*\python.exe" (
    for %%f in ("%PROGRAMFILES%\Python*\python.exe") do (
set "PYTHON_CMD="%%f""
        echo Found Python: %%f
        goto python_found
    )
)

if exist "%PROGRAMFILES% (x86)\Python*\python.exe" (
    for %%f in ("%PROGRAMFILES% (x86)\Python*\python.exe") do (
set "PYTHON_CMD="%%f""
        echo Found Python: %%f
        goto python_found
    )
)

echo ERROR: Python not found!
echo.
echo Please install Python 3.7+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation
echo.
echo After installing Python, run this installer again.
pause
exit /b 1

:python_found
echo.
echo Python version:
%PYTHON_CMD% --version

echo.
echo Setting up installation directories...
set INSTALL_DIR="%USERPROFILE%\homelab-tools"
set CONFIG_DIR="%INSTALL_DIR%\config"
set DATA_DIR="%INSTALL_DIR%\data"
set LOGS_DIR="%INSTALL_DIR%\logs"
set TEMP_DIR="%INSTALL_DIR%\temp"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo Installation directories created.

echo.
echo Installing Python dependencies...
echo This may take several minutes depending on your internet connection...
echo.

%PYTHON_CMD% -m pip install --upgrade pip
if !errorlevel! neq 0 (
    echo Warning: pip upgrade failed, continuing...
)

echo Installing core dependencies...
%PYTHON_CMD% -m pip install --user psutil
if !errorlevel! neq 0 (
    echo Warning: psutil failed to install
) else (
    echo psutil installed successfully
)

%PYTHON_CMD% -m pip install --user matplotlib
if !errorlevel! neq 0 (
    echo Warning: matplotlib failed to install
) else (
    echo matplotlib installed successfully
)

%PYTHON_CMD% -m pip install --user numpy
if !errorlevel! neq 0 (
    echo Warning: numpy failed to install
) else (
    echo numpy installed successfully
)

%PYTHON_CMD% -m pip install --user pyyaml
if !errorlevel! neq 0 (
    echo Warning: pyyaml failed to install
) else (
    echo pyyaml installed successfully
)

%PYTHON_CMD% -m pip install --user colorama
if !errorlevel! neq 0 (
    echo Warning: colorama failed to install
) else (
    echo colorama installed successfully
)

%PYTHON_CMD% -m pip install --user requests
if !errorlevel! neq 0 (
    echo Warning: requests failed to install
) else (
    echo requests installed successfully
)

%PYTHON_CMD% -m pip install --user flask
if !errorlevel! neq 0 (
    echo Warning: flask failed to install
) else (
    echo flask installed successfully
)

%PYTHON_CMD% -m pip install --user sqlalchemy
if !errorlevel! neq 0 (
    echo Warning: sqlalchemy failed to install
) else (
    echo sqlalchemy installed successfully
)

%PYTHON_CMD% -m pip install --user pillow
if !errorlevel! neq 0 (
    echo Warning: pillow failed to install
) else (
    echo pillow installed successfully
)

%PYTHON_CMD% -m pip install --user scipy
if !errorlevel! neq 0 (
    echo Warning: scipy failed to install
) else (
    echo scipy installed successfully
)

echo Core dependencies installation completed

if "%WINDOWS_VERSION%"="="11" ("
    echo Installing Windows 11 specific packages...
    %PYTHON_CMD% -m pip install --user pywin32
    if !errorlevel! neq 0 (
        echo Warning: pywin32 failed to install
    ) else (
        echo pywin32 installed successfully
    )
    
    %PYTHON_CMD% -m pip install --user wmi
    if !errorlevel! neq 0 (
        echo Warning: wmi failed to install
    ) else (
        echo wmi installed successfully
    )
    
    %PYTHON_CMD% -m pip install --user netifaces
    if !errorlevel! neq 0 (
        echo Warning: netifaces failed to install
    ) else (
        echo netifaces installed successfully
    )
    
    echo Windows 11 packages installation completed
)

echo.
echo Setting up environment variables...
setx HOMELAB_ROOT "%INSTALL_DIR%" >nul 2>&1
setx HOMELAB_CONFIG "%CONFIG_DIR%" >nul 2>&1
setx HOMELAB_DATA "%DATA_DIR%" >nul 2>&1
setx HOMELAB_LOGS "%LOGS_DIR%" >nul 2>&1
setx HOMELAB_TEMP "%TEMP_DIR%" >nul 2>&1
setx PYTHONPATH "%INSTALL_DIR%" >nul 2>&1

REM Set current session environment
set HOMELAB_ROOT="%INSTALL_DIR%"
set HOMELAB_CONFIG="%CONFIG_DIR%"
set HOMELAB_DATA="%DATA_DIR%"
set HOMELAB_LOGS="%LOGS_DIR%"
set HOMELAB_TEMP="%TEMP_DIR%"
set PYTHONPATH="%INSTALL_DIR%"

echo Environment variables set.

echo.
echo Copying core files...
xcopy /E /I /Y "Core Services" "%INSTALL_DIR%\Core Services" >nul 2>&1
if exist "Integration_Examples" xcopy /E /I /Y "Integration_Examples" "%INSTALL_DIR%\Integration_Examples" >nul 2>&1

echo Core files copied.

echo.
echo Creating launcher script...
set LAUNCHER_CONTENT="@echo off^"
title Homelab Unified System Launcher - Windows %WINDOWS_VERSION%^
echo="===============================================^"
echo    HOMELAB UNIFIED SYSTEM LAUNCHER^
echo    Windows %WINDOWS_VERSION% Compatible^
echo="===============================================^"
echo.^
^
REM Set environment variables^
set HOMELAB_ROOT="%INSTALL_DIR%^"
set HOMELAB_CONFIG="%CONFIG_DIR%^"
set HOMELAB_DATA="%DATA_DIR%^"
set HOMELAB_LOGS="%LOGS_DIR%^"
set HOMELAB_TEMP="%TEMP_DIR%^"
set PYTHONPATH="%INSTALL_DIR%^"
^
REM Check Python availability^
echo Detecting Python installation...^
%PYTHON_CMD% --version ^>nul 2^>^&1^
if %!errorlevel!% equ 0 (^
set PYTHON_CMD="%PYTHON_CMD%^"
    echo Found Python: %PYTHON_CMD%^
) else (^
    py --version ^>nul 2^>^&1^
    if %!errorlevel!% equ 0 (^
set PYTHON_CMD="py^"
        echo Found Python: py^
    ) else (^
        echo ERROR: Python not found^
        pause^
        exit /b 1^
    )^
)^
^
echo.^
echo 1. Launch Unified Dashboard^
echo 2. Start Core Services Only^
echo 3. Test Core Services^
echo 4. System Status Check^
echo 5. Exit^
echo.^
^
set /p choice="Enter choice (1-5): "^
^
if "%%choice%%"="="1" goto launch_dashboard^"
if "%%choice%%"="="2" goto start_services^"
if "%%choice%%"="="3" goto test_services^"
if "%%choice%%"="="4" goto status_check^"
if "%%choice%%"="="5" goto exit_program^"
^
echo Invalid choice^
pause^
goto start^
^
:launch_dashboard^
echo.^
echo Launching Unified Dashboard...^
cd /d "%INSTALL_DIR%"^
%%PYTHON_CMD%% "Core Services\\unified_dashboard.py"^
goto start^
^
:start_services^
echo Starting Core Services...^
cd /d "%INSTALL_DIR%"^
^
echo Starting Event Bus...^
%%PYTHON_CMD%% -c "from Core Services.event_bus import get_event_bus; bus="get_event_bus(); print('Event Bus started')"^"
^
echo Starting Configuration Manager...^
%%PYTHON_CMD%% -c "from Core Services.config_manager import get_config_manager; cm="get_config_manager(); print('Configuration Manager started')"^"
^
echo Starting Authentication Service...^
%%PYTHON_CMD%% -c "from Core Services.auth_service import get_auth_service; auth="get_auth_service(); print('Authentication Service started')"^"
^
echo Starting Data Persistence...^
%%PYTHON_CMD%% -c "from Core Services.data_persistence import get_data_persistence; dp="get_data_persistence(); print('Data Persistence started')"^"
^
echo Starting Unified Monitoring...^
%%PYTHON_CMD%% -c "from Core Services.unified_monitoring import get_unified_monitoring; um="get_unified_monitoring(); print('Unified Monitoring started')"^"
^
echo.^
echo All core services started successfully!^
pause^
goto start^
^
:test_services^
echo.^
echo Testing Core Services Integration...^
cd /d "%INSTALL_DIR%"^
^
echo Testing Event Bus...^
%%PYTHON_CMD%% -c "from Core Services.event_bus import get_event_bus, EventType; bus="get_event_bus(); event_id = bus.publish_sync(EventType.SYSTEM, 'test', {'test': True}); print(f'Event Bus test: {event_id}')"^"
^
echo Testing Configuration Manager...^
%%PYTHON_CMD%% -c "from Core Services.config_manager import get_config_manager; cm="get_config_manager(); cm.set('test.value', 42, 'test', 'Test configuration'); value = cm.get('test.value'); print(f'Config Manager test: {value}')"^"
^
echo Testing Data Persistence...^
%%PYTHON_CMD%% -c "from Core Services.data_persistence import get_data_persistence; dp="get_data_persistence(); success = dp.store_metric('test', 'cpu_usage', 75.5, 'percent'); print(f'Data Persistence test: {success}')"^"
^
echo Testing Unified Monitoring...^
%%PYTHON_CMD%% -c "from Core Services.unified_monitoring import get_unified_monitoring, AlertSeverity; um="get_unified_monitoring(); alert_id = um.create_alert('Test Alert', 'This is a test alert', AlertSeverity.INFO, 'test'); print(f'Unified Monitoring test: {alert_id}')"^"
^
echo.^
echo Core services integration tests completed!^
pause^
goto start^
^
:status_check^
echo.^
echo System Status Check...^
cd /d "%INSTALL_DIR%"^
^
echo Checking Python installation...^
%%PYTHON_CMD%% --version^
^
echo Checking Core Services availability...^
^
echo Event Bus Status:^
%%PYTHON_CMD%% -c "try: from Core Services.event_bus import get_event_bus; bus="get_event_bus(); stats = bus.get_statistics(); print(f'Active - {stats[\"total_events\"]} events processed'); except Exception as e: print(f'Error: {e}')"^"
^
echo Configuration Manager Status:^
%%PYTHON_CMD%% -c "try: from Core Services.config_manager import get_config_manager; cm="get_config_manager(); validation = cm.validate_config(); print(f'Active - Valid: {validation[\"valid\"]}'); except Exception as e: print(f'Error: {e}')"^"
^
echo Data Persistence Status:^
%%PYTHON_CMD%% -c "try: from Core Services.data_persistence import get_data_persistence; dp="get_data_persistence(); stats = dp.get_database_stats(); print(f'Active - {stats[\"metrics_count\"]} metrics stored'); except Exception as e: print(f'Error: {e}')"^"
^
echo Unified Monitoring Status:^
%%PYTHON_CMD%% -c "try: from Core Services.unified_monitoring import get_unified_monitoring; um="get_unified_monitoring(); stats = um.get_monitoring_stats(); print(f'Active - {stats[\"active_alerts\"]} active alerts'); except Exception as e: print(f'Error: {e}')"^"
^
echo.^
pause^
goto start^
^
:exit_program^
echo.^
echo Goodbye!^
exit /b 0

echo %LAUNCHER_CONTENT% > "%INSTALL_DIR%\Launch_Homelab.bat"

echo Launcher created: %INSTALL_DIR%\Launch_Homelab.bat

echo.
echo Creating desktop shortcut...
powershell -Command "$WshShell="New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Homelab Tools.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\Launch_Homelab.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Homelab Unified System Launcher'; $Shortcut.Save()""

echo Desktop shortcut created.

echo.
echo Configuring Windows firewall...
netsh advfirewall firewall delete rule name="Homelab Tools" >nul 2>&1
netsh advfirewall firewall add rule name="Homelab Tools" dir=in action=allow program="%PYTHON_CMD%" enable=yes >nul 2>&1

echo Firewall rules configured.

echo.
echo="==============================================="
echo    INSTALLATION COMPLETED SUCCESSFULLY!
echo="==============================================="
echo.
echo Installation directory: %INSTALL_DIR%
echo Launcher: %INSTALL_DIR%\Launch_Homelab.bat
echo Desktop shortcut: Homelab Tools
echo.
echo You can now launch Homelab Tools from:
echo   - Double-click the desktop shortcut
echo   - Run: %INSTALL_DIR%\Launch_Homelab.bat
echo.
echo The system is ready for use on Windows %WINDOWS_VERSION%!
echo.
pause
