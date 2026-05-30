#!/usr/bin/env python3
"""
Cross-Platform Homelab Tools Deployer
Robust auto-path detection and deployment for Windows and Linux systems
"""

import os
import sys
import platform
import subprocess
import shutil
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

class CrossPlatformDeployer:
    """Robust cross-platform deployment system"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.python_cmd = self._detect_python()
        self.pip_cmd = self._detect_pip()
        self.install_dir = Path.home() / "homelab-tools" if self.platform != "windows" else Path(os.path.expanduser("~/homelab-tools"))
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.install_dir / "deployment.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _detect_python(self) -> str:
        """Detect Python command on current platform"""
        commands = ['python3', 'python', 'py'] if self.platform == 'windows' else ['python3', 'python']
        
        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info(f"Found Python: {cmd} v{result.stdout.strip()}")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
                
        raise RuntimeError("Python not found on this system")
    
    def _detect_pip(self) -> str:
        """Detect pip command on current platform"""
        commands = ['pip3', 'pip'] if self.platform != 'windows' else ['pip', 'pip3']
        
        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info(f"Found pip: {cmd} v{result.stdout.strip()}")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
                
        raise RuntimeError("pip not found on this system")
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [self.install_dir, self.config_dir, self.data_dir, self.logs_dir]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {directory}")
            except Exception as e:
                self.logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    def _install_dependencies(self):
        """Install required dependencies"""
        dependencies = [
            'psutil',
            'matplotlib', 
            'numpy',
            'tkinter',
            'pyyaml',
            'colorama',
            'requests',
            'flask',
            'sqlalchemy'
        ]
        
        self.logger.info("Installing dependencies...")
        
        for dep in dependencies:
            try:
                self.logger.info(f"Installing {dep}...")
                result = subprocess.run([self.pip_cmd, 'install', dep], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.logger.info(f"✓ {dep} installed successfully")
                else:
                    self.logger.warning(f"⚠ {dep} installation failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.logger.error(f"✗ {dep} installation timed out")
            except Exception as e:
                self.logger.error(f"✗ {dep} installation failed: {e}")
    
    def _setup_environment_variables(self):
        """Setup platform-specific environment variables"""
        env_vars = {
            'HOMELAB_ROOT': str(self.install_dir),
            'HOMELAB_CONFIG': str(self.config_dir),
            'HOMELAB_DATA': str(self.data_dir),
            'HOMELAB_LOGS': str(self.logs_dir),
            'PYTHONPATH': str(self.install_dir)
        }
        
        if self.platform == 'windows':
            self._setup_windows_env(env_vars)
        else:
            self._setup_linux_env(env_vars)
    
    def _setup_windows_env(self, env_vars: Dict[str, str]):
        """Setup Windows environment variables"""
        try:
            import winreg
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
                for var, value in env_vars.items():
                    winreg.SetValueEx(key, var, 0, winreg.REG_SZ, value)
                    self.logger.info(f"Set Windows environment variable: {var}")
                    
            # Notify system of environment change
            subprocess.run(['setx', var, value], capture_output=True)
            
        except ImportError:
            self.logger.warning("winreg not available, using temporary environment")
            for var, value in env_vars.items():
                os.environ[var] = value
    
    def _setup_linux_env(self, env_vars: Dict[str, str]):
        """Setup Linux environment variables"""
        bashrc_path = Path.home() / ".bashrc"
        
        env_lines = []
        for var, value in env_vars.items():
            env_lines.append(f'export {var}="{value}"')
            os.environ[var] = value
        
        try:
            with open(bashrc_path, 'a') as f:
                f.write("\n# Homelab Tools Environment\n")
                f.write("\n".join(env_lines) + "\n")
            self.logger.info("Added environment variables to ~/.bashrc")
        except Exception as e:
            self.logger.error(f"Failed to update ~/.bashrc: {e}")
    
    def _create_launchers(self):
        """Create platform-specific launchers"""
        if self.platform == 'windows':
            self._create_windows_launchers()
        else:
            self._create_linux_launchers()
    
    def _create_windows_launchers(self):
        """Create Windows batch launchers"""
        launcher_content = f"""@echo off
title Homelab Unified System Launcher
echo ================================================
echo    HOMELAB UNIFIED SYSTEM LAUNCHER
echo ================================================
echo.

REM Check Python availability (try both python and py)
{self.python_cmd} --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD={self.python_cmd}
    echo Found Python: {self.python_cmd}
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
        echo Found Python: py
    ) else (
        echo ERROR: Python not found
        echo Please install Python 3.7+ to use the unified system
        pause
        exit /b 1
    )
)

echo.
echo 1. Launch Unified Dashboard
echo 2. Start Core Services Only
echo 3. Test Core Services
echo 4. System Status Check
echo 5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto launch_dashboard
if "%choice%"=="2" goto start_services
if "%choice%"=="3" goto test_services
if "%choice%"=="4" goto status_check
if "%choice%"=="5" goto exit_program

echo Invalid choice
pause
goto start

:launch_dashboard
echo.
echo Launching Unified Dashboard...
echo This starts all core services and opens the integrated interface
echo.

%PYTHON_CMD% "{self.install_dir}\\Core Services\\unified_dashboard.py"

if %errorlevel% neq 0 (
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
%PYTHON_CMD% -c "from Core Services.event_bus import get_event_bus; bus = get_event_bus(); print('Event Bus started')"

echo Starting Configuration Manager...
%PYTHON_CMD% -c "from Core Services.config_manager import get_config_manager; cm = get_config_manager(); print('Configuration Manager started')"

echo Starting Authentication Service...
%PYTHON_CMD% -c "from Core Services.auth_service import get_auth_service; auth = get_auth_service(); print('Authentication Service started')"

echo Starting Data Persistence...
%PYTHON_CMD% -c "from Core Services.data_persistence import get_data_persistence; dp = get_data_persistence(); print('Data Persistence started')"

echo Starting Unified Monitoring...
%PYTHON_CMD% -c "from Core Services.unified_monitoring import get_unified_monitoring; um = get_unified_monitoring(); print('Unified Monitoring started')"

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

echo Testing Event Bus...
%PYTHON_CMD% -c "
from Core Services.event_bus import get_event_bus, EventType
bus = get_event_bus()
event_id = bus.publish_sync(EventType.SYSTEM, 'test', {{'test': True}})
print(f'Event Bus test: {{event_id}}')
"

echo Testing Configuration Manager...
%PYTHON_CMD% -c "
from Core Services.config_manager import get_config_manager
cm = get_config_manager()
cm.set('test.value', 42, 'test', 'Test configuration')
value = cm.get('test.value')
print(f'Config Manager test: {{value}}')
"

echo Testing Data Persistence...
%PYTHON_CMD% -c "
from Core Services.data_persistence import get_data_persistence
dp = get_data_persistence()
success = dp.store_metric('test', 'cpu_usage', 75.5, 'percent')
print(f'Data Persistence test: {{success}}')
"

echo Testing Unified Monitoring...
%PYTHON_CMD% -c "
from Core Services.unified_monitoring import get_unified_monitoring, AlertSeverity
um = get_unified_monitoring()
alert_id = um.create_alert('Test Alert', 'This is a test alert', AlertSeverity.INFO, 'test')
print(f'Unified Monitoring test: {{alert_id}}')
"

echo.
echo All core services integration tests passed!
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
    bus = get_event_bus()
    stats = bus.get_statistics()
    print(f'Active - {{stats[\"total_events\"]}} events processed')
except Exception as e:
    print(f'Error: {{e}}')
"

echo.
echo Configuration Manager Status:
%PYTHON_CMD% -c "
try:
    from Core Services.config_manager import get_config_manager
    cm = get_config_manager()
    validation = cm.validate_config()
    print(f'Active - Valid: {{validation[\"valid\"]}}')
except Exception as e:
    print(f'Error: {{e}}')
"

echo.
echo Data Persistence Status:
%PYTHON_CMD% -c "
try:
    from Core Services.data_persistence import get_data_persistence
    dp = get_data_persistence()
    stats = dp.get_database_stats()
    print(f'Active - {{stats[\"metrics_count\"]}} metrics stored')
except Exception as e:
    print(f'Error: {{e}}')
"

echo.
echo Unified Monitoring Status:
%PYTHON_CMD% -c "
try:
    from Core Services.unified_monitoring import get_unified_monitoring
    um = get_unified_monitoring()
    stats = um.get_monitoring_stats()
    print(f'Active - {{stats[\"active_alerts\"]}} active alerts')
except Exception as e:
    print(f'Error: {{e}}')
"

echo.
pause
goto start

:exit_program
echo.
echo Goodbye!
exit /b 0
"""
        
        launcher_path = self.install_dir / "Launch_Homelab.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        self.logger.info(f"Created Windows launcher: {launcher_path}")
    
    def _create_linux_launchers(self):
        """Create Linux shell launchers"""
        launcher_content = f"""#!/bin/bash
# Homelab Unified System Launcher

echo "==============================================="
echo "   HOMELAB UNIFIED SYSTEM LAUNCHER"
echo "==============================================="
echo

# Check Python availability
if command -v {self.python_cmd} &> /dev/null; then
    PYTHON_CMD="{self.python_cmd}"
    echo "Found Python: $PYTHON_CMD"
else
    echo "ERROR: Python not found"
    echo "Please install Python 3.7+ to use the unified system"
    exit 1
fi

echo
echo "1. Launch Unified Dashboard"
echo "2. Start Core Services Only"
echo "3. Test Core Services"
echo "4. System Status Check"
echo "5. Exit"
echo

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo
        echo "Launching Unified Dashboard..."
        echo "This starts all core services and opens the integrated interface"
        echo
        
        $PYTHON_CMD "{self.install_dir}/Core Services/unified_dashboard.py"
        
        if [ $? -ne 0 ]; then
            echo
            echo "ERROR: Failed to launch unified dashboard"
            echo "Check that all core services are available"
            read -p "Press Enter to continue..."
        fi
        ;;
    2)
        echo "Starting Core Services..."
        echo "This initializes the unified backend architecture"
        echo
        
        echo "Starting Event Bus..."
        $PYTHON_CMD -c "from Core Services.event_bus import get_event_bus; bus = get_event_bus(); print('Event Bus started')"
        
        echo "Starting Configuration Manager..."
        $PYTHON_CMD -c "from Core Services.config_manager import get_config_manager; cm = get_config_manager(); print('Configuration Manager started')"
        
        echo "Starting Authentication Service..."
        $PYTHON_CMD -c "from Core Services.auth_service import get_auth_service; auth = get_auth_service(); print('Authentication Service started')"
        
        echo "Starting Data Persistence..."
        $PYTHON_CMD -c "from Core Services.data_persistence import get_data_persistence; dp = get_data_persistence(); print('Data Persistence started')"
        
        echo "Starting Unified Monitoring..."
        $PYTHON_CMD -c "from Core Services.unified_monitoring import get_unified_monitoring; um = get_unified_monitoring(); print('Unified Monitoring started')"
        
        echo
        echo "All core services started successfully!"
        echo
        echo "Services are now running and available for integration"
        read -p "Press Enter to continue..."
        ;;
    3)
        echo
        echo "Testing Core Services Integration..."
        echo
        
        echo "Testing Event Bus..."
        $PYTHON_CMD -c "
from Core Services.event_bus import get_event_bus, EventType
bus = get_event_bus()
event_id = bus.publish_sync(EventType.SYSTEM, 'test', {'test': True})
print(f'Event Bus test: {event_id}')
"
        
        echo "Testing Configuration Manager..."
        $PYTHON_CMD -c "
from Core Services.config_manager import get_config_manager
cm = get_config_manager()
cm.set('test.value', 42, 'test', 'Test configuration')
value = cm.get('test.value')
print(f'Config Manager test: {value}')
"
        
        echo "Testing Data Persistence..."
        $PYTHON_CMD -c "
from Core Services.data_persistence import get_data_persistence
dp = get_data_persistence()
success = dp.store_metric('test', 'cpu_usage', 75.5, 'percent')
print(f'Data Persistence test: {success}')
"
        
        echo "Testing Unified Monitoring..."
        $PYTHON_CMD -c "
from Core Services.unified_monitoring import get_unified_monitoring, AlertSeverity
um = get_unified_monitoring()
alert_id = um.create_alert('Test Alert', 'This is a test alert', AlertSeverity.INFO, 'test')
print(f'Unified Monitoring test: {alert_id}')
"
        
        echo
        echo "All core services integration tests passed!"
        read -p "Press Enter to continue..."
        ;;
    4)
        echo
        echo "System Status Check..."
        echo
        
        echo "Checking Core Services availability..."
        echo
        
        echo "Event Bus Status:"
        $PYTHON_CMD -c "
try:
    from Core Services.event_bus import get_event_bus
    bus = get_event_bus()
    stats = bus.get_statistics()
    print(f'Active - {stats["total_events"]} events processed')
except Exception as e:
    print(f'Error: {e}')
"
        
        echo
        echo "Configuration Manager Status:"
        $PYTHON_CMD -c "
try:
    from Core Services.config_manager import get_config_manager
    cm = get_config_manager()
    validation = cm.validate_config()
    print(f'Active - Valid: {validation["valid"]}')
except Exception as e:
    print(f'Error: {e}')
"
        
        echo
        echo "Data Persistence Status:"
        $PYTHON_CMD -c "
try:
    from Core Services.data_persistence import get_data_persistence
    dp = get_data_persistence()
    stats = dp.get_database_stats()
    print(f'Active - {stats["metrics_count"]} metrics stored')
except Exception as e:
    print(f'Error: {e}')
"
        
        echo
        echo "Unified Monitoring Status:"
        $PYTHON_CMD -c "
try:
    from Core Services.unified_monitoring import get_unified_monitoring
    um = get_unified_monitoring()
    stats = um.get_monitoring_stats()
    print(f'Active - {stats["active_alerts"]} active alerts')
except Exception as e:
    print(f'Error: {e}')
"
        
        echo
        read -p "Press Enter to continue..."
        ;;
    5)
        echo
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        read -p "Press Enter to continue..."
        ;;
esac

# Restart launcher
exec "$0"
"""
        
        launcher_path = self.install_dir / "launch_homelab.sh"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        # Make executable
        os.chmod(launcher_path, 0o755)
        
        self.logger.info(f"Created Linux launcher: {launcher_path}")
    
    def _create_desktop_shortcuts(self):
        """Create desktop shortcuts"""
        if self.platform == 'windows':
            self._create_windows_shortcut()
        else:
            self._create_linux_shortcut()
    
    def _create_windows_shortcut(self):
        """Create Windows desktop shortcut"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Homelab Tools.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.install_dir / "Launch_Homelab.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "icon.ico")
            shortcut.save()
            
            self.logger.info(f"Created Windows desktop shortcut: {shortcut_path}")
        except ImportError:
            self.logger.warning("winshell/win32com not available, skipping desktop shortcut")
    
    def _create_linux_shortcut(self):
        """Create Linux desktop shortcut"""
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path.home() / "desktop"
        
        shortcut_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Homelab Tools
Comment=Homelab Unified System Launcher
Exec={self.install_dir}/launch_homelab.sh
Icon={self.install_dir}/icon.png
Terminal=true
Categories=System;Development;
"""
        
        shortcut_path = desktop_dir / "Homelab Tools.desktop"
        with open(shortcut_path, 'w') as f:
            f.write(shortcut_content)
        
        os.chmod(shortcut_path, 0o755)
        self.logger.info(f"Created Linux desktop shortcut: {shortcut_path}")
    
    def _copy_core_files(self):
        """Copy core files to installation directory"""
        current_dir = Path.cwd()
        
        # Copy Core Services
        core_services_src = current_dir / "Core Services"
        if core_services_src.exists():
            core_services_dst = self.install_dir / "Core Services"
            if core_services_dst.exists():
                shutil.rmtree(core_services_dst)
            shutil.copytree(core_services_src, core_services_dst)
            self.logger.info("Copied Core Services")
        
        # Copy Integration Examples
        integration_src = current_dir / "Integration_Examples"
        if integration_src.exists():
            integration_dst = self.install_dir / "Integration_Examples"
            if integration_dst.exists():
                shutil.rmtree(integration_dst)
            shutil.copytree(integration_src, integration_dst)
            self.logger.info("Copied Integration Examples")
    
    def deploy(self):
        """Main deployment function"""
        self.logger.info(f"Starting Homelab Tools deployment on {self.platform}")
        
        try:
            self.logger.info("Creating directories...")
            self._create_directories()
            
            self.logger.info("Installing dependencies...")
            self._install_dependencies()
            
            self.logger.info("Setting up environment variables...")
            self._setup_environment_variables()
            
            self.logger.info("Copying core files...")
            self._copy_core_files()
            
            self.logger.info("Creating launchers...")
            self._create_launchers()
            
            self.logger.info("Creating desktop shortcuts...")
            self._create_desktop_shortcuts()
            
            self.logger.info("✅ Deployment completed successfully!")
            self.logger.info(f"Installation directory: {self.install_dir}")
            
            if self.platform == 'windows':
                self.logger.info(f"Run: {self.install_dir / 'Launch_Homelab.bat'}")
            else:
                self.logger.info(f"Run: {self.install_dir / 'launch_homelab.sh'}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {e}")
            return False

def main():
    """Main entry point"""
    deployer = CrossPlatformDeployer()
    
    print("Homelab Tools Cross-Platform Deployer")
    print("=" * 50)
    print(f"Platform: {deployer.platform}")
    print(f"Python: {deployer.python_cmd}")
    print(f"Installation directory: {deployer.install_dir}")
    print()
    
    confirm = input("Proceed with deployment? (y/N): ").lower().strip()
    if confirm != 'y':
        print("Deployment cancelled.")
        return
    
    success = deployer.deploy()
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("You can now launch Homelab Tools from:")
        print(f"  - Launcher: {deployer.install_dir / ('Launch_Homelab.bat' if deployer.platform == 'windows' else 'launch_homelab.sh')}")
        print(f"  - Desktop: Homelab Tools shortcut")
    else:
        print("\n❌ Deployment failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
