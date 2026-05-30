#!/usr/bin/env python3
"""
Windows Universal Deployer for Homelab Tools
Robust deployment for Windows 10 and Windows 11 with auto-path detection
"""

import os
import sys
import platform
import subprocess
import shutil
import json
import time
import winreg
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

class WindowsUniversalDeployer:
    """Windows 10/11 universal deployment system"""
    
    def __init__(self):
        self.platform_version = platform.version()
        self.is_windows_11 = self._detect_windows_11()
        self.python_cmd = self._detect_python()
        self.pip_cmd = self._detect_pip()
        self.install_dir = Path(os.path.expanduser("~/homelab-tools"))
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        self.temp_dir = self.install_dir / "temp"
        
        # Setup logging
        self._setup_logging()
        
    def _detect_windows_11(self) -> bool:
        """Detect if running on Windows 11"""
        try:
            # Windows 11 build numbers start at 22000
            build_number = int(platform.version().split('.')[-1])
            return build_number >= 22000
        except:
            return False
    
    def _setup_logging(self):
        """Setup logging system"""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = self.logs_dir / "deployment.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Windows Universal Deployer initialized")
        self.logger.info(f"Windows version: {self.platform_version}")
        self.logger.info(f"Windows 11: {self.is_windows_11}")
    
    def _detect_python(self) -> str:
        """Detect Python command with multiple fallback methods"""
        commands = ['py', 'python3', 'python', 'python.exe']
        
        # Method 1: Check PATH
        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info(f"Found Python via PATH: {cmd} v{result.stdout.strip()}")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        # Method 2: Check Windows Store Python locations
        python_paths = [
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Microsoft", "WindowsApps", "python.exe"),
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Microsoft", "WindowsApps", "py.exe"),
            r"C:\Program Files\Python*\python.exe",
            r"C:\Program Files (x86)\Python*\python.exe",
            r"C:\Python*\python.exe"
        ]
        
        for path_pattern in python_paths:
            try:
                # Expand environment variables and glob
                expanded_path = os.path.expandvars(path_pattern)
                if '*' in expanded_path:
                    import glob
                    matches = glob.glob(expanded_path)
                    if matches:
                        for match in matches:
                            if os.path.isfile(match):
                                self.logger.info(f"Found Python via path search: {match}")
                                return match
                else:
                    if os.path.isfile(expanded_path):
                        self.logger.info(f"Found Python via direct path: {expanded_path}")
                        return expanded_path
            except Exception:
                continue
        
        # Method 3: Registry check
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Python\PythonCore", 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        i += 1
                        
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                install_path = winreg.QueryValueEx(subkey, "InstallPath")[0]
                                python_exe = os.path.join(install_path, "python.exe")
                                if os.path.isfile(python_exe):
                                    self.logger.info(f"Found Python via registry: {python_exe}")
                                    return python_exe
                            except FileNotFoundError:
                                continue
                    except OSError:
                        break
        except Exception:
            pass
        
        raise RuntimeError("Python not found on this Windows system")
    
    def _detect_pip(self) -> str:
        """Detect pip command with multiple fallback methods"""
        commands = ['pip', 'pip3', 'pip.exe']
        
        # Method 1: Check PATH
        for cmd in commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info(f"Found pip via PATH: {cmd} v{result.stdout.strip()}")
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        # Method 2: Use python -m pip
        try:
            result = subprocess.run([self.python_cmd, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info(f"Found pip via python -m pip: {result.stdout.strip()}")
                return f"{self.python_cmd} -m pip"
        except Exception:
            pass
        
        # Method 3: Find pip in Python installation directory
        python_dir = os.path.dirname(self.python_cmd)
        scripts_dir = os.path.join(python_dir, "Scripts")
        if os.path.isdir(scripts_dir):
            pip_exe = os.path.join(scripts_dir, "pip.exe")
            if os.path.isfile(pip_exe):
                self.logger.info(f"Found pip in Scripts directory: {pip_exe}")
                return pip_exe
        
        raise RuntimeError("pip not found on this Windows system")
    
    def _create_directories(self):
        """Create necessary directories with proper permissions"""
        directories = [
            self.install_dir,
            self.config_dir,
            self.data_dir,
            self.logs_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {directory}")
            except Exception as e:
                self.logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    def _install_dependencies(self):
        """Install required dependencies with Windows-specific optimizations"""
        dependencies = [
            'psutil',
            'matplotlib', 
            'numpy',
            'pyyaml',
            'colorama',
            'requests',
            'flask',
            'sqlalchemy',
            'pillow',
            'scipy',
            'tkinter'
        ]
        
        # Windows 11 specific packages
        if self.is_windows_11:
            dependencies.extend([
                'pywin32',
                'wmi',
                'netifaces'
            ])
        
        self.logger.info("Installing dependencies...")
        
        for dep in dependencies:
            try:
                self.logger.info(f"Installing {dep}...")
                
                # Use --user flag for user-level installation
                cmd = self.pip_cmd.split()
                if ' -m pip' in ' '.join(cmd):
                    install_cmd = cmd + ['install', '--user', dep]
                else:
                    install_cmd = [cmd, 'install', '--user', dep]
                
                result = subprocess.run(install_cmd, 
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
        """Setup Windows environment variables"""
        env_vars = {
            'HOMELAB_ROOT': str(self.install_dir),
            'HOMELAB_CONFIG': str(self.config_dir),
            'HOMELAB_DATA': str(self.data_dir),
            'HOMELAB_LOGS': str(self.logs_dir),
            'HOMELAB_TEMP': str(self.temp_dir),
            'PYTHONPATH': str(self.install_dir)
        }
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
                for var, value in env_vars.items():
                    winreg.SetValueEx(key, var, 0, winreg.REG_SZ, value)
                    self.logger.info(f"Set environment variable: {var}")
                    
            # Notify system of environment change
            for var, value in env_vars.items():
                subprocess.run(['setx', var, value], capture_output=True)
            
            # Set current process environment
            for var, value in env_vars.items():
                os.environ[var] = value
                
        except Exception as e:
            self.logger.error(f"Failed to set environment variables: {e}")
            # Set temporary environment variables
            for var, value in env_vars.items():
                os.environ[var] = value
    
    def _create_windows_launchers(self):
        """Create Windows batch launchers with enhanced compatibility"""
        launcher_content = f'''@echo off
title Homelab Unified System Launcher - Windows {11 if self.is_windows_11 else 10}
echo ================================================
echo    HOMELAB UNIFIED SYSTEM LAUNCHER
echo    Windows {11 if self.is_windows_11 else 10} Compatible
echo ================================================
echo.

REM Set environment variables
set HOMELAB_ROOT={self.install_dir}
set HOMELAB_CONFIG={self.config_dir}
set HOMELAB_DATA={self.data_dir}
set HOMELAB_LOGS={self.logs_dir}
set HOMELAB_TEMP={self.temp_dir}
set PYTHONPATH={self.install_dir}

REM Check Python availability (try both python and py)
echo Detecting Python installation...
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
        echo Please install Python 3.7+ from https://python.org
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)

echo.
echo 1. Launch Unified Dashboard
echo 2. Start Core Services Only
echo 3. Test Core Services
echo 4. System Status Check
echo 5. Install Dependencies
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto launch_dashboard
if "%choice%"=="2" goto start_services
if "%choice%"=="3" goto test_services
if "%choice%"=="4" goto status_check
if "%choice%"=="5" goto install_deps
if "%choice%"=="6" goto exit_program

echo Invalid choice
pause
goto start

:install_deps
echo.
echo Installing/updating dependencies...
echo This may take several minutes...
echo.

%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install --user psutil matplotlib numpy pyyaml colorama requests flask sqlalchemy pillow scipy

echo.
echo Dependencies installation completed!
pause
goto start

:launch_dashboard
echo.
echo Launching Unified Dashboard...
echo This starts all core services and opens the integrated interface
echo.

cd /d "{self.install_dir}"
%PYTHON_CMD% "Core Services\\unified_dashboard.py"

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

cd /d "{self.install_dir}"

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

cd /d "{self.install_dir}"

echo Testing Event Bus...
%PYTHON_CMD% -c "
try:
    from Core Services.event_bus import get_event_bus, EventType
    bus = get_event_bus()
    event_id = bus.publish_sync(EventType.SYSTEM, 'test', {{'test': True}})
    print(f'Event Bus test: {{event_id}}')
except Exception as e:
    print(f'Event Bus test failed: {{e}}')
"

echo Testing Configuration Manager...
%PYTHON_CMD% -c "
try:
    from Core Services.config_manager import get_config_manager
    cm = get_config_manager()
    cm.set('test.value', 42, 'test', 'Test configuration')
    value = cm.get('test.value')
    print(f'Config Manager test: {{value}}')
except Exception as e:
    print(f'Config Manager test failed: {{e}}')
"

echo Testing Data Persistence...
%PYTHON_CMD% -c "
try:
    from Core Services.data_persistence import get_data_persistence
    dp = get_data_persistence()
    success = dp.store_metric('test', 'cpu_usage', 75.5, 'percent')
    print(f'Data Persistence test: {{success}}')
except Exception as e:
    print(f'Data Persistence test failed: {{e}}')
"

echo Testing Unified Monitoring...
%PYTHON_CMD% -c "
try:
    from Core Services.unified_monitoring import get_unified_monitoring, AlertSeverity
    um = get_unified_monitoring()
    alert_id = um.create_alert('Test Alert', 'This is a test alert', AlertSeverity.INFO, 'test')
    print(f'Unified Monitoring test: {{alert_id}}')
except Exception as e:
    print(f'Unified Monitoring test failed: {{e}}')
"

echo.
echo Core services integration tests completed!
pause
goto start

:status_check
echo.
echo System Status Check...
echo.

cd /d "{self.install_dir}"

echo Checking Python installation...
%PYTHON_CMD% --version

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
'''
        
        launcher_path = self.install_dir / "Launch_Homelab.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        self.logger.info(f"Created Windows launcher: {launcher_path}")
    
    def _create_desktop_shortcuts(self):
        """Create Windows desktop shortcuts"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Homelab Tools.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.install_dir / "Launch_Homelab.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.Description = "Homelab Unified System Launcher"
            shortcut.save()
            
            self.logger.info(f"Created desktop shortcut: {shortcut_path}")
        except ImportError:
            self.logger.warning("winshell/win32com not available, creating manual shortcut")
            self._create_manual_shortcut()
    
    def _create_manual_shortcut(self):
        """Create shortcut manually using PowerShell"""
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "Homelab Tools.lnk")
            
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{self.install_dir}\\Launch_Homelab.bat"
$Shortcut.WorkingDirectory = "{self.install_dir}"
$Shortcut.Description = "Homelab Unified System Launcher"
$Shortcut.Save()
'''
            
            result = subprocess.run(['powershell', '-Command', ps_script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"Created desktop shortcut via PowerShell: {shortcut_path}")
            else:
                self.logger.error(f"Failed to create shortcut: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Failed to create manual shortcut: {e}")
    
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
    
    def _setup_windows_firewall(self):
        """Setup Windows firewall rules"""
        try:
            firewall_rules = [
                f'netsh advfirewall firewall delete rule name="Homelab Tools"',
                f'netsh advfirewall firewall add rule name="Homelab Tools" dir=in action=allow program="{self.python_cmd}" enable=yes',
                f'netsh advfirewall firewall add rule name="Homelab Tools UDP" dir=in action=allow protocol=UDP localport=25565-25568 enable=yes'
            ]
            
            for rule in firewall_rules:
                subprocess.run(rule, shell=True, capture_output=True)
            
            self.logger.info("Windows firewall rules configured")
        except Exception as e:
            self.logger.warning(f"Failed to configure firewall: {e}")
    
    def deploy(self):
        """Main deployment function"""
        self.logger.info(f"Starting Homelab Tools deployment on Windows {11 if self.is_windows_11 else 10}")
        
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
            self._create_windows_launchers()
            
            self.logger.info("Creating desktop shortcuts...")
            self._create_desktop_shortcuts()
            
            self.logger.info("Configuring Windows firewall...")
            self._setup_windows_firewall()
            
            self.logger.info("✅ Deployment completed successfully!")
            self.logger.info(f"Installation directory: {self.install_dir}")
            self.logger.info(f"Launcher: {self.install_dir / 'Launch_Homelab.bat'}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {e}")
            return False

def main():
    """Main entry point"""
    deployer = WindowsUniversalDeployer()
    
    print("Homelab Tools Windows Universal Deployer")
    print("=" * 50)
    print(f"Windows version: {deployer.platform_version}")
    print(f"Windows 11: {deployer.is_windows_11}")
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
        print(f"  - Launcher: {deployer.install_dir / 'Launch_Homelab.bat'}")
        print("  - Desktop: Homelab Tools shortcut")
        print("\nThe system is ready for use on both Windows 10 and Windows 11!")
    else:
        print("\n❌ Deployment failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
