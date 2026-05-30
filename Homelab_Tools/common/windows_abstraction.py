#!/usr/bin/env python3
"""
Windows 10 Abstraction Layer
Provides proper Windows 10 compatibility for all homelab tools and monitors
"""

import os
import sys
import platform
import subprocess
import psutil
import ctypes
import ctypes.wintypes
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging
import time

class WindowsAbstraction:
    """Windows 10 specific abstraction layer for system operations"""
    
    def __init__(self):
        self.system_info = self.get_system_info()
        self.logger = logging.getLogger(__name__)
        
        # Windows API constants
        self.kernel32 = ctypes.windll.kernel32
        self.user32 = ctypes.windll.user32
        
        # Initialize Windows-specific features
        self.initialize_windows_features()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive Windows system information"""
        return {
            'platform': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'is_windows_10': platform.release() == '10',
            'is_windows_11': platform.release() == '11',
            'is_admin': self.is_admin()
        }
    
    def is_admin(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def initialize_windows_features(self):
        """Initialize Windows-specific features and optimizations"""
        if self.system_info['is_windows_10'] or self.system_info['is_windows_11']:
            # Set high priority for better performance
            self.set_process_priority()
            
            # Enable Windows-specific optimizations
            self.enable_windows_optimizations()
    
    def set_process_priority(self):
        """Set process priority for better performance"""
        try:
            # Get current process handle
            HANDLE = ctypes.wintypes.HANDLE
            DWORD = ctypes.wintypes.DWORD
            BOOL = ctypes.wintypes.BOOL
            
            # Set priority class to HIGH_PRIORITY_CLASS
            HIGH_PRIORITY_CLASS = 0x00000080
            GetCurrentProcess = self.kernel32.GetCurrentProcess
            GetCurrentProcess.restype = HANDLE
            GetCurrentProcess.argtypes = []
            
            SetPriorityClass = self.kernel32.SetPriorityClass
            SetPriorityClass.restype = BOOL
            SetPriorityClass.argtypes = [HANDLE, DWORD]
            
            process_handle = GetCurrentProcess()
            SetPriorityClass(process_handle, HIGH_PRIORITY_CLASS)
            
            self.logger.info("Process priority set to HIGH")
            
        except Exception as e:
            self.logger.warning(f"Failed to set process priority: {e}")
    
    def enable_windows_optimizations(self):
        """Enable Windows-specific optimizations"""
        try:
            # Disable Windows Defender real-time monitoring for homelab directory
            self.configure_windows_defender()
            
            # Optimize power settings
            self.configure_power_settings()
            
            # Configure Windows Firewall
            self.configure_firewall()
            
        except Exception as e:
            self.logger.warning(f"Windows optimization setup failed: {e}")
    
    def configure_windows_defender(self):
        """Configure Windows Defender exclusions"""
        try:
            homelab_path = Path.cwd()
            
            # Add Windows Defender exclusions
            exclusions = [
                str(homelab_path),
                str(homelab_path / "*.py"),
                str(homelab_path / "*.exe"),
                str(homelab_path / "*.dll")
            ]
            
            for exclusion in exclusions:
                try:
                    # Run PowerShell command to add exclusion
                    cmd = [
                        'powershell', '-Command',
                        f'MpPreference.exe -AddExclusionPath "{exclusion}"'
                    ]
                    subprocess.run(cmd, capture_output=True, timeout=10)
                    
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Windows Defender exclusion timeout for: {exclusion}")
                except Exception as e:
                    self.logger.warning(f"Failed to add Windows Defender exclusion: {e}")
            
            self.logger.info("Windows Defender exclusions configured")
            
        except Exception as e:
            self.logger.warning(f"Windows Defender configuration failed: {e}")
    
    def configure_power_settings(self):
        """Configure Windows power settings for optimal performance"""
        try:
            # Set power plan to High Performance
            cmd = [
                'powercfg', '/setactive', 'scHEME_MIN'
            ]
            subprocess.run(cmd, capture_output=True, timeout=10)
            
            self.logger.info("Power plan set to High Performance")
            
        except Exception as e:
            self.logger.warning(f"Power configuration failed: {e}")
    
    def configure_firewall(self):
        """Configure Windows Firewall rules for homelab services"""
        try:
            homelab_path = Path.cwd()
            
            # Common ports used by homelab tools
            ports = [8080, 25565, 32400, 51820, 80, 443]
            
            for port in ports:
                try:
                    # Add firewall rule for each port
                    cmd = [
                        'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                        f'name=Homelab_Port_{port}',
                        'dir=in',
                        'action=allow',
                        'protocol=TCP',
                        f'localport={port}'
                    ]
                    subprocess.run(cmd, capture_output=True, timeout=10)
                    
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Firewall rule timeout for port {port}")
                except Exception as e:
                    self.logger.warning(f"Failed to add firewall rule for port {port}: {e}")
            
            self.logger.info("Windows Firewall rules configured")
            
        except Exception as e:
            self.logger.warning(f"Firewall configuration failed: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get enhanced Windows system metrics"""
        try:
            # CPU metrics with Windows-specific optimizations
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics with Windows-specific information
            disk_partitions = psutil.disk_partitions()
            disk_usage = {}
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100,
                        'filesystem': partition.fstype
                    }
                except Exception as e:
                    self.logger.warning(f"Failed to get disk usage for {partition.device}: {e}")
            
            # Network metrics with Windows-specific optimizations
            network_io = psutil.net_io_counters()
            network_interfaces = psutil.net_if_addrs()
            
            # Windows-specific metrics
            windows_metrics = self.get_windows_specific_metrics()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'disk': disk_usage,
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'interfaces': list(network_interfaces.keys())
                },
                'windows': windows_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def get_windows_specific_metrics(self) -> Dict[str, Any]:
        """Get Windows-specific system metrics"""
        try:
            metrics = {}
            
            # Get Windows performance counters
            try:
                # CPU temperature (if available)
                cpu_temp = self.get_cpu_temperature()
                if cpu_temp:
                    metrics['cpu_temperature'] = cpu_temp
                
                # GPU metrics
                gpu_metrics = self.get_gpu_metrics()
                if gpu_metrics:
                    metrics['gpu'] = gpu_metrics
                
                # System uptime
                uptime = self.get_system_uptime()
                metrics['uptime'] = uptime
                
                # Page file usage
                pagefile = self.get_pagefile_usage()
                metrics['pagefile'] = pagefile
                
            except Exception as e:
                self.logger.warning(f"Windows metrics collection failed: {e}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get Windows-specific metrics: {e}")
            return {}
    
    def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature using Windows WMI"""
        try:
            import wmi
            
            c = wmi.WMI()
            for temperature in c.Win32_TemperatureProbe():
                if temperature.CurrentReading:
                    return float(temperature.CurrentReading)
            
            return None
            
        except ImportError:
            # wmi not available, try alternative method
            return None
        except Exception as e:
            self.logger.warning(f"Failed to get CPU temperature: {e}")
            return None
    
    def get_gpu_metrics(self) -> Optional[Dict[str, Any]]:
        """Get GPU metrics using Windows WMI or NVIDIA tools"""
        try:
            gpu_info = {}
            
            # Try NVIDIA GPU monitoring
            try:
                import pynvml
                pynvml.nvmlInit()
                
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    gpu_info[f'gpu_{i}'] = {
                        'name': name,
                        'temperature': temp,
                        'utilization': util.gpu,
                        'memory_used': memory_info.used,
                        'memory_total': memory_info.total,
                        'memory_percent': (memory_info.used / memory_info.total) * 100
                    }
                
                pynvml.nvmlShutdown()
                
            except ImportError:
                # pynvml not available, try WMI
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    for gpu in c.Win32_VideoController():
                        gpu_info[gpu.Name] = {
                            'name': gpu.Name,
                            'adapter_ram': gpu.AdapterRAM,
                            'driver_version': gpu.DriverVersion
                        }
                        
                except ImportError:
                    return None
                except Exception as e:
                    self.logger.warning(f"WMI GPU query failed: {e}")
            
            return gpu_info if gpu_info else None
            
        except Exception as e:
            self.logger.warning(f"Failed to get GPU metrics: {e}")
            return None
    
    def get_system_uptime(self) -> Optional[int]:
        """Get system uptime in seconds"""
        try:
            kernel32 = ctypes.windll.kernel32
            
            # Get system uptime
            uptime = ctypes.c_ulong()
            kernel32.GetTickCount64(ctypes.byref(uptime))
            
            return uptime.value
            
        except Exception as e:
            self.logger.warning(f"Failed to get system uptime: {e}")
            return None
    
    def get_pagefile_usage(self) -> Optional[Dict[str, Any]]:
        """Get page file usage information"""
        try:
            pagefile = psutil.swap_memory()
            
            return {
                'total': pagefile.total,
                'used': pagefile.used,
                'free': pagefile.free,
                'percent': pagefile.percent
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get pagefile usage: {e}")
            return None
    
    def optimize_for_realtime(self):
        """Optimize system for real-time monitoring"""
        try:
            # Set thread priority
            import threading
            current_thread = threading.current_thread()
            
            # Windows-specific thread priority
            THREAD_PRIORITY_HIGHEST = 2
            handle = self.kernel32.GetCurrentThread()
            self.kernel32.SetThreadPriority(handle, THREAD_PRIORITY_HIGHEST)
            
            # Disable Windows power saving for monitoring
            self.set_thread_execution_state()
            
            self.logger.info("System optimized for real-time monitoring")
            
        except Exception as e:
            self.logger.warning(f"Real-time optimization failed: {e}")
    
    def set_thread_execution_state(self):
        """Set thread execution state to prevent sleep"""
        try:
            # Prevent system from sleeping during monitoring
            ES_CONTINUOUS = 0x80000000
            ES_SYSTEM_REQUIRED = 0x00000001
            
            self.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to set thread execution state: {e}")
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get enhanced process list with Windows-specific information"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    pinfo['status'] = proc.status()
                    pinfo['create_time'] = proc.create_time()
                    pinfo['exe'] = proc.exe() if proc.exe() else None
                    pinfo['cwd'] = proc.cwd() if proc.cwd() else None
                    
                    # Windows-specific process information
                    if self.system_info['is_windows_10'] or self.system_info['is_windows_11']:
                        pinfo['windows_info'] = self.get_process_windows_info(proc.pid)
                    
                    processes.append(pinfo)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Failed to get process list: {e}")
            return []
    
    def get_process_windows_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get Windows-specific process information"""
        try:
            import wmi
            c = wmi.WMI()
            
            for process in c.Win32_Process(ProcessId=pid):
                return {
                    'command_line': process.CommandLine,
                    'executable_path': process.ExecutablePath,
                    'working_set_size': process.WorkingSetSize,
                    'page_file_usage': process.PageFileUsage,
                    'thread_count': process.ThreadCount,
                    'handle_count': process.HandleCount
                }
            
            return None
            
        except ImportError:
            return None
        except Exception as e:
            self.logger.warning(f"Failed to get Windows process info for PID {pid}: {e}")
            return None
    
    def get_network_interfaces(self) -> Dict[str, Any]:
        """Get detailed network interface information"""
        try:
            interfaces = {}
            
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                interface_info = {
                    'name': interface_name,
                    'addresses': [],
                    'stats': {}
                }
                
                # Get addresses
                for addr in interface_addresses:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                # Get statistics
                try:
                    stats = psutil.net_if_stats()[interface_name]
                    interface_info['stats'] = {
                        'isup': stats.isup,
                        'duplex': stats.duplex,
                        'speed': stats.speed,
                        'mtu': stats.mtu
                    }
                except KeyError:
                    pass
                
                interfaces[interface_name] = interface_info
            
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get network interfaces: {e}")
            return {}
    
    def get_service_status(self, service_name: str) -> Optional[str]:
        """Get Windows service status"""
        try:
            import wmi
            c = wmi.WMI()
            
            for service in c.Win32_Service(Name=service_name):
                return service.State
            
            return None
            
        except ImportError:
            return None
        except Exception as e:
            self.logger.warning(f"Failed to get service status for {service_name}: {e}")
            return None
    
    def cleanup_resources(self):
        """Clean up Windows resources"""
        try:
            # Reset thread execution state
            self.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS
            
            # Reset process priority
            HANDLE = ctypes.wintypes.HANDLE
            DWORD = ctypes.wintypes.DWORD
            BOOL = ctypes.wintypes.BOOL
            
            NORMAL_PRIORITY_CLASS = 0x00000020
            GetCurrentProcess = self.kernel32.GetCurrentProcess
            GetCurrentProcess.restype = HANDLE
            GetCurrentProcess.argtypes = []
            
            SetPriorityClass = self.kernel32.SetPriorityClass
            SetPriorityClass.restype = BOOL
            SetPriorityClass.argtypes = [HANDLE, DWORD]
            
            process_handle = GetCurrentProcess()
            SetPriorityClass(process_handle, NORMAL_PRIORITY_CLASS)
            
            self.logger.info("Windows resources cleaned up")
            
        except Exception as e:
            self.logger.warning(f"Resource cleanup failed: {e}")

# Global Windows abstraction instance
windows_abstraction = WindowsAbstraction()

def get_windows_abstraction() -> WindowsAbstraction:
    """Get the global Windows abstraction instance"""
    return windows_abstraction

def is_windows_10() -> bool:
    """Check if running on Windows 10"""
    return windows_abstraction.system_info['is_windows_10']

def is_windows_11() -> bool:
    """Check if running on Windows 11"""
    return windows_abstraction.system_info['is_windows_11']

def is_admin() -> bool:
    """Check if running with administrator privileges"""
    return windows_abstraction.system_info['is_admin']

def optimize_for_realtime():
    """Optimize system for real-time monitoring"""
    windows_abstraction.optimize_for_realtime()

def cleanup_resources():
    """Clean up Windows resources"""
    windows_abstraction.cleanup_resources()

# Context manager for Windows optimization
class WindowsOptimization:
    """Context manager for Windows-specific optimizations"""
    
    def __enter__(self):
        optimize_for_realtime()
        return windows_abstraction
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        cleanup_resources()

# Export main functions
__all__ = [
    'WindowsAbstraction',
    'get_windows_abstraction',
    'is_windows_10',
    'is_windows_11', 
    'is_admin',
    'optimize_for_realtime',
    'cleanup_resources',
    'WindowsOptimization'
]
