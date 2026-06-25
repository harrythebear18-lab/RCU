#!/usr/bin/env python3
"""
System Data Connector
Connects portal to existing monitoring tools and system data
"""

import psutil
import platform
import subprocess
import socket
import logging
from typing import Dict, List, Any, Optional
import json

class SystemDataConnector:
    """Connects to existing monitoring tools and system data"""
    
    def __init__(self):
        self.logger = logging.getLogger("SystemDataConnector")
        
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information using psutil"""
        try:
            cpu_info = {
                'brand': platform.processor(),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'usage_percent': psutil.cpu_percent(interval=1),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'architecture': platform.architecture()[0],
                'machine': platform.machine()
            }
            return cpu_info
        except Exception as e:
            self.logger.error(f"Failed to get CPU info: {e}")
            return {}
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        try:
            gpu_info = {}
            
            # Try to get NVIDIA GPU info
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines):
                        if line.strip():
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 6:
                                gpu_info[f'nvidia_gpu_{i}'] = {
                                    'name': parts[0],
                                    'memory_total': int(parts[1]),
                                    'memory_used': int(parts[2]),
                                    'memory_free': int(parts[3]),
                                    'utilization': int(parts[4]),
                                    'temperature': int(parts[5]) if parts[5] != 'N/A' else None
                                }
            except:
                pass
            
            # Try to get AMD GPU info
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_info[f'amd_gpu_{i}'] = {
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal,
                        'memory_used': gpu.memoryUsed,
                        'memory_free': gpu.memoryFree,
                        'utilization': gpu.load * 100,
                        'temperature': gpu.temperature
                    }
            except:
                pass
            
            return gpu_info
        except Exception as e:
            self.logger.error(f"Failed to get GPU info: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
            return memory_info
        except Exception as e:
            self.logger.error(f"Failed to get memory info: {e}")
            return {}
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information"""
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addresses in net_if_addrs.items():
                stats = net_if_stats.get(interface_name)
                if stats:
                    interface_info = {
                        'name': interface_name,
                        'is_up': stats.isup,
                        'speed': stats.speed,
                        'mtu': stats.mtu,
                        'duplex': stats.duplex,
                        'addresses': []
                    }
                    
                    for addr in addresses:
                        address_info = {
                            'family': str(addr.family),
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        }
                        interface_info['addresses'].append(address_info)
                    
                    interfaces.append(interface_info)
            
            return interfaces
        except Exception as e:
            self.logger.error(f"Failed to get network interfaces: {e}")
            return []
    
    def get_disk_info(self) -> List[Dict[str, Any]]:
        """Get disk information"""
        try:
            disks = []
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                    disks.append(disk_info)
                except:
                    continue
            
            return disks
        except Exception as e:
            self.logger.error(f"Failed to get disk info: {e}")
            return []
    
    def get_process_info(self) -> List[Dict[str, Any]]:
        """Get running process information"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except:
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return processes[:20]  # Return top 20 processes
        except Exception as e:
            self.logger.error(f"Failed to get process info: {e}")
            return []
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get complete system information"""
        try:
            system_info = {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'hostname': socket.gethostname(),
                'boot_time': psutil.boot_time()
            }
            return system_info
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
    
    def check_ddr4_memory(self) -> bool:
        """Check if DDR4 memory is present"""
        try:
            # This is a simplified check - in reality, you'd need WMI or other tools
            # For now, we'll assume DDR4 is present on modern systems
            memory_info = self.get_memory_info()
            return memory_info.get('total', 0) > 0
        except:
            return False
    
    def detect_intel_cpu(self) -> bool:
        """Detect if Intel CPU is present"""
        try:
            return 'Intel' in platform.processor()
        except:
            return False
    
    def get_screen_info(self) -> Dict[str, Any]:
        """Get screen/display information"""
        try:
            screen_info = {}
            
            # Try to get screen resolution using Windows APIs
            try:
                import ctypes
                user32 = ctypes.windll.user32
                gdi32 = ctypes.windll.gdi32
                
                # Get screen dimensions
                width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
                
                screen_info = {
                    'width': width,
                    'height': height,
                    'bits_per_pixel': gdi32.GetDeviceCaps(gdi32.GetDC(0), 12)  # BITSPIXEL
                }
            except:
                pass
            
            return screen_info
        except Exception as e:
            self.logger.error(f"Failed to get screen info: {e}")
            return {}

# Global instance
_system_connector = None

def get_system_connector() -> SystemDataConnector:
    """Get global system connector instance"""
    global _system_connector
    if _system_connector is None:
        _system_connector = SystemDataConnector()
    return _system_connector
