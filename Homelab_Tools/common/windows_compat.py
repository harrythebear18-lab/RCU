#!/usr/bin/env python3
"""
Windows Compatibility Utilities
Cross-platform compatibility helpers for Windows homelab tools
"""

import os
import platform
import subprocess
import ctypes
from pathlib import Path
from typing import Optional, Union, List
import logging

class WindowsCompat:
    """Windows-specific compatibility utilities"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.logger = logging.getLogger('WindowsCompat')
    
    def get_device_path(self, unix_path: str, windows_path: str = None) -> str:
        """Convert Unix device path to Windows-compatible path"""
        if not self.is_windows:
            return unix_path
        
        if windows_path:
            return windows_path
        
        # Common Unix to Windows device path mappings
        device_mappings = {
            '/dev/ultra_dma': r'\\.\UltraDMA',
            '/dev/rdma0': r'\\.\RDMA0',
            '/dev/mem': r'\\.\PhysicalMemory',
            '/dev/null': 'NUL' if self.is_windows else '/dev/null',
            '/dev/zero': 'NUL' if self.is_windows else '/dev/zero'
        }
        
        return device_mappings.get(unix_path, unix_path)
    
    def get_config_path(self, unix_path: str) -> str:
        """Convert Unix config path to Windows path"""
        if not self.is_windows:
            return unix_path
        
        # Convert forward slashes to backslashes
        windows_path = unix_path.replace('/', '\\')
        
        # Handle common Unix paths
        path_mappings = {
            '/etc/homelab/': os.path.expandvars('%PROGRAMDATA%\\Homelab\\'),
            '/var/log/homelab/': os.path.expandvars('%PROGRAMDATA%\\Homelab\\Logs\\'),
            '/tmp/homelab/': os.path.expandvars('%TEMP%\\Homelab\\'),
            '/home/': os.path.expandvars('%USERPROFILE%\\'),
            '/usr/local/bin/': os.path.expandvars('%PROGRAMFILES%\\Homelab\\bin\\')
        }
        
        for unix_prefix, windows_prefix in path_mappings.items():
            if unix_path.startswith(unix_prefix):
                return windows_prefix + unix_path[len(unix_prefix):]
        
        # If no mapping found, try to make it Windows-compatible
        if windows_path.startswith('\\'):
            # Absolute Unix path - convert to Windows absolute path
            if len(windows_path) > 1 and windows_path[1] == '\\':
                # Already in Windows format
                return windows_path
            else:
                # Convert to relative path
                return windows_path.lstrip('\\')
        
        return windows_path
    
    def get_executable_extension(self) -> str:
        """Get appropriate executable extension for the platform"""
        return '.exe' if self.is_windows else ''
    
    def get_python_executable(self) -> str:
        """Get appropriate Python executable command"""
        if self.is_windows:
            return 'py'  # Windows Python launcher
        return 'python3'
    
    def get_shell_command(self, command: str, use_shell: bool = True) -> Union[str, List[str]]:
        """Convert shell command for Windows compatibility"""
        if not self.is_windows:
            return command
        
        # Windows-specific command conversions
        command_mappings = {
            'rm -rf': 'rmdir /s /q',
            'rm -f': 'del /f',
            'cp': 'copy',
            'mv': 'move',
            'ls': 'dir',
            'cat': 'type',
            'grep': 'findstr',
            'chmod +x': 'icacls',  # Windows permissions are different
            'ps aux': 'tasklist',
            'kill': 'taskkill',
            'ping -c': 'ping -n'
        }
        
        for unix_cmd, windows_cmd in command_mappings.items():
            if command.startswith(unix_cmd):
                return command.replace(unix_cmd, windows_cmd, 1)
        
        return command
    
    def create_windows_service(self, service_name: str, executable_path: str, 
                             display_name: str = None, description: str = None) -> bool:
        """Create Windows service (requires admin privileges)"""
        if not self.is_windows:
            self.logger.warning("Service creation only supported on Windows")
            return False
        
        try:
            # Use sc.exe to create service
            cmd = ['sc', 'create', service_name, 'binPath=', f'"{executable_path}"']
            
            if display_name:
                cmd.extend(['DisplayName=', f'"{display_name}"'])
            
            if description:
                cmd.extend(['start=', 'auto'])  # Start automatically
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if description:
                    # Set description separately
                    desc_cmd = ['sc', 'description', service_name, f'"{description}"']
                    subprocess.run(desc_cmd, capture_output=True, timeout=10)
                
                self.logger.info(f"Windows service '{service_name}' created successfully")
                return True
            else:
                self.logger.error(f"Failed to create service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Service creation error: {e}")
            return False
    
    def check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges on Windows"""
        if not self.is_windows:
            return os.geteuid() == 0  # Unix root check
        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def get_environment_variable(self, var_name: str, default: str = None) -> str:
        """Get environment variable with Windows fallbacks"""
        value = os.getenv(var_name)
        if value:
            return value
        
        # Windows-specific environment variable mappings
        windows_mappings = {
            'HOME': 'USERPROFILE',
            'USER': 'USERNAME',
            'PATH': 'PATH',
            'TEMP': 'TEMP',
            'TMP': 'TMP'
        }
        
        if self.is_windows and var_name in windows_mappings:
            return os.getenv(windows_mappings[var_name], default or '')
        
        return default or ''
    
    def ensure_directory_exists(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists with Windows-compatible permissions"""
        path_obj = Path(path)
        
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
            
            # On Windows, set appropriate permissions
            if self.is_windows:
                try:
                    # Give full control to current user
                    import win32security
                    import ntsecuritycon
                    
                    user_sid = win32security.GetUserSid()
                    dacl = win32security.ACL()
                    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, 
                                           ntsecuritycon.FILE_ALL_ACCESS, user_sid)
                    
                    # Apply security descriptor
                    security = win32security.SECURITY_INFORMATION()
                    security.SetSecurityDescriptorDacl(1, dacl, 0)
                    
                    win32security.SetFileSecurity(str(path_obj), security)
                except ImportError:
                    # win32security not available - skip permission setting
                    pass
                except Exception as e:
                    self.logger.warning(f"Could not set Windows permissions: {e}")
            
            return path_obj
            
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {e}")
            raise
    
    def get_process_list(self) -> List[dict]:
        """Get process list with Windows compatibility"""
        if self.is_windows:
            try:
                # Use Windows tasklist command
                result = subprocess.run(['tasklist', '/fo', 'csv'], 
                                      capture_output=True, text=True, timeout=10)
                
                processes = []
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 5:
                            processes.append({
                                'pid': int(parts[1].strip('"')),
                                'name': parts[0].strip('"'),
                                'memory': parts[4].strip('"'),
                                'status': parts[4].strip('"') if len(parts) > 4 else 'Unknown'
                            })
                
                return processes
                
            except Exception as e:
                self.logger.error(f"Failed to get Windows process list: {e}")
                return []
        else:
            # Unix systems - use psutil or ps command
            try:
                import psutil
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory': str(proc.info['memory_info'].rss) if proc.info['memory_info'] else '0',
                            'status': 'running'
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return processes
            except ImportError:
                # Fallback to ps command
                try:
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    processes = []
                    for line in lines:
                        parts = line.split(None, 10)  # Split into max 11 parts
                        if len(parts) >= 11:
                            processes.append({
                                'pid': int(parts[1]),
                                'name': parts[10],
                                'memory': parts[5],
                                'status': parts[7]
                            })
                    return processes
                except Exception as e:
                    self.logger.error(f"Failed to get Unix process list: {e}")
                    return []
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill process with Windows compatibility"""
        if self.is_windows:
            try:
                cmd = ['taskkill', '/PID', str(pid)]
                if force:
                    cmd.append('/F')
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return result.returncode == 0
                
            except Exception as e:
                self.logger.error(f"Failed to kill Windows process {pid}: {e}")
                return False
        else:
            try:
                import psutil
                proc = psutil.Process(pid)
                proc.kill() if force else proc.terminate()
                return True
            except ImportError:
                # Fallback to kill command
                try:
                    signal = 9 if force else 15  # SIGKILL or SIGTERM
                    result = subprocess.run(['kill', str(signal), str(pid)], timeout=10)
                    return result.returncode == 0
                except Exception as e:
                    self.logger.error(f"Failed to kill Unix process {pid}: {e}")
                    return False
    
    def get_network_interfaces(self) -> List[dict]:
        """Get network interfaces with Windows compatibility"""
        if self.is_windows:
            try:
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=10)
                
                interfaces = []
                current_interface = {}
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('adapter '):
                        if current_interface:
                            interfaces.append(current_interface)
                        current_interface = {'name': line.split('adapter ')[1].rstrip(':')}
                    
                    elif 'IPv4 Address' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            current_interface['ipv4'] = parts[1].strip()
                    
                    elif 'Subnet Mask' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            current_interface['netmask'] = parts[1].strip()
                
                if current_interface:
                    interfaces.append(current_interface)
                
                return interfaces
                
            except Exception as e:
                self.logger.error(f"Failed to get Windows network interfaces: {e}")
                return []
        else:
            # Unix systems - use ip or ifconfig
            try:
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, timeout=10)
                # Parse Unix ip output (simplified)
                return []  # Implementation would go here
            except Exception:
                try:
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True, timeout=10)
                    # Parse Unix ifconfig output (simplified)
                    return []  # Implementation would go here
                except Exception as e:
                    self.logger.error(f"Failed to get Unix network interfaces: {e}")
                    return []

# Global compatibility instance
compat = WindowsCompat()

# Convenience functions
def get_device_path(unix_path: str, windows_path: str = None) -> str:
    """Get platform-appropriate device path"""
    return compat.get_device_path(unix_path, windows_path)

def is_admin() -> bool:
    """Check if running with admin/root privileges"""
    return compat.check_admin_privileges()

def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists with proper permissions"""
    return compat.ensure_directory_exists(path)

def get_python_cmd() -> str:
    """Get appropriate Python command for the platform"""
    return compat.get_python_executable()
