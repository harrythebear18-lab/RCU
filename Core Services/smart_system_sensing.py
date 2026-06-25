#!/usr/bin/env python3
"""
Smart System Sensing
Automatically detects system type and applies appropriate optimizations
"""

import platform
import subprocess
import logging
import time
import ctypes
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import psutil
import re

class SystemType(Enum):
    """System types"""
    WINDOWS_10 = "Windows 10"
    WINDOWS_11 = "Windows 11"
    WINDOWS_SERVER = "Windows Server"
    LINUX = "Linux"
    MACOS = "macOS"
    UNKNOWN = "Unknown"

class HardwareProfile(Enum):
    """Hardware profiles"""
    INTEL_NVIDIA = "Intel+NVIDIA"
    AMD_AMD = "AMD+AMD"
    INTEL_INTEL = "Intel+Intel"
    MIXED = "Mixed"
    UNKNOWN = "Unknown"

class SystemCapability(Enum):
    """System capabilities"""
    GAMING = "gaming"
    PRODUCTIVITY = "productivity"
    DEVELOPMENT = "development"
    SERVER = "server"
    MULTIMEDIA = "multimedia"
    BASIC = "basic"

@dataclass
class SystemInfo:
    """System information"""
    system_type: SystemType
    hardware_profile: HardwareProfile
    capabilities: List[SystemCapability]
    cpu_info: Dict[str, Any]
    gpu_info: Dict[str, Any]
    memory_info: Dict[str, Any]
    disk_info: Dict[str, Any]
    network_info: Dict[str, Any]
    build_number: int
    version: str
    architecture: str
    total_score: float

@dataclass
class OptimizationProfile:
    """Optimization profile for system"""
    system_type: SystemType
    hardware_profile: HardwareProfile
    cpu_optimizations: Dict[str, Any]
    gpu_optimizations: Dict[str, Any]
    memory_optimizations: Dict[str, Any]
    network_optimizations: Dict[str, Any]
    ui_optimizations: Dict[str, Any]
    power_optimizations: Dict[str, Any]

class SmartSystemSensing:
    """Smart system sensing and optimization"""
    
    def __init__(self):
        self.logger = logging.getLogger("SmartSystemSensing")
        self.system_info = None
        self.optimization_profile = None
        self.detection_cache = {}
        self.last_detection_time = 0
        self.cache_timeout = 300  # 5 minutes
        
    def detect_system(self, force_refresh: bool = False) -> SystemInfo:
        """Detect system information"""
        current_time = time.time()
        
        # Check cache
        if not force_refresh and self.system_info and (current_time - self.last_detection_time) < self.cache_timeout:
            return self.system_info
        
        self.logger.info("Starting smart system detection...")
        
        # Detect system type
        system_type = self._detect_system_type()
        
        # Detect hardware profile
        hardware_profile = self._detect_hardware_profile()
        
        # Detect capabilities
        capabilities = self._detect_capabilities()
        
        # Gather hardware info
        cpu_info = self._get_cpu_info()
        gpu_info = self._get_gpu_info()
        memory_info = self._get_memory_info()
        disk_info = self._get_disk_info()
        network_info = self._get_network_info()
        
        # Get version info
        build_number = self._get_build_number()
        version = self._get_version_string()
        architecture = platform.architecture()[0]
        
        # Calculate system score
        total_score = self._calculate_system_score(cpu_info, gpu_info, memory_info)
        
        # Create system info
        self.system_info = SystemInfo(
            system_type=system_type,
            hardware_profile=hardware_profile,
            capabilities=capabilities,
            cpu_info=cpu_info,
            gpu_info=gpu_info,
            memory_info=memory_info,
            disk_info=disk_info,
            network_info=network_info,
            build_number=build_number,
            version=version,
            architecture=architecture,
            total_score=total_score
        )
        
        self.last_detection_time = current_time
        
        # Generate optimization profile
        self.optimization_profile = self._generate_optimization_profile()
        
        self.logger.info(f"System detected: {system_type.value} with {hardware_profile.value} profile")
        return self.system_info
    
    def _detect_system_type(self) -> SystemType:
        """Detect system type with enhanced Windows 11 detection"""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Enhanced Windows 11 detection
                version_info = platform.version()
                build_number = self._get_build_number()
                
                # Method 1: Build number detection (most reliable)
                if build_number >= 22000:
                    return SystemType.WINDOWS_11
                elif build_number >= 10240:
                    return SystemType.WINDOWS_10
                elif build_number >= 9200:
                    return SystemType.WINDOWS_SERVER
                
                # Method 2: Registry detection
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                        product_name = winreg.QueryValueEx(key, "ProductName")[0]
                        build_lab = winreg.QueryValueEx(key, "BuildLabEx")[0] if "BuildLabEx" in [name for name, _ in winreg.QueryInfoKey(key)] else ""
                        
                        if "Windows 11" in product_name:
                            return SystemType.WINDOWS_11
                        elif "Windows 10" in product_name:
                            return SystemType.WINDOWS_10
                        elif "Server" in product_name:
                            return SystemType.WINDOWS_SERVER
                except:
                    pass
                
                # Method 3: Feature detection
                if self._check_windows_11_features():
                    return SystemType.WINDOWS_11
                elif self._check_windows_10_features():
                    return SystemType.WINDOWS_10
                else:
                    return SystemType.WINDOWS_SERVER
            
            elif system == "Linux":
                return SystemType.LINUX
            elif system == "Darwin":
                return SystemType.MACOS
            else:
                return SystemType.UNKNOWN
                
        except Exception as e:
            self.logger.error(f"Failed to detect system type: {e}")
            return SystemType.UNKNOWN
    
    def _check_windows_11_features(self) -> bool:
        """Check for Windows 11 specific features"""
        try:
            # Check for Windows 11 specific features
            features_found = 0
            
            # Check for Windows Terminal (Windows 11 feature)
            try:
                result = subprocess.run(['wt', '--version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    features_found += 1
            except:
                pass
            
            # Check for Widgets (Windows 11 feature)
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
                    try:
                        widgets_enabled = winreg.QueryValueEx(key, "TaskbarDa")[0]
                        if widgets_enabled:
                            features_found += 1
                    except:
                        pass
            except:
                pass
            
            # Check for Snap Layouts (Windows 11 feature)
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
                    try:
                        snap_assist = winreg.QueryValueEx(key, "EnableSnapAssist")[0]
                        if snap_assist:
                            features_found += 1
                    except:
                        pass
            except:
                pass
            
            # Check for Centered Taskbar (Windows 11 default)
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
                    try:
                        taskbar_alignment = winreg.QueryValueEx(key, "TaskbarAl")[0]
                        if taskbar_alignment == 1:  # Centered
                            features_found += 1
                    except:
                        pass
            except:
                pass
            
            # If we found multiple Windows 11 features, it's likely Windows 11
            return features_found >= 2
            
        except Exception as e:
            self.logger.debug(f"Windows 11 feature check failed: {e}")
            return False
    
    def _check_windows_10_features(self) -> bool:
        """Check for Windows 10 specific features"""
        try:
            # Check for Windows 10 specific features
            features_found = 0
            
            # Check for Windows Store
            try:
                result = subprocess.run(['powershell', '-Command', 'Get-AppxPackage -Name "Microsoft.WindowsStore"'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0 and "Microsoft.WindowsStore" in result.stdout:
                    features_found += 1
            except:
                pass
            
            # Check for Cortana
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Cortana") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Action Center
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\ActionCenter") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Windows 10 Timeline
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Timeline") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Windows 10 Game Bar
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Windows 10 Focus Assist
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\FocusAssist") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Windows 10 Virtual Desktops
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Windows 10 Storage Sense
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense") as key:
                    features_found += 1
            except:
                pass
            
            # Check for Windows 10 Windows Defender Security Center
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Security Center") as key:
                    features_found += 1
            except:
                pass
            
            # If we found multiple Windows 10 features, it's likely Windows 10
            return features_found >= 3
            
        except Exception as e:
            self.logger.debug(f"Windows 10 feature check failed: {e}")
            return False
    
    def _detect_hardware_profile(self) -> HardwareProfile:
        """Detect hardware profile"""
        try:
            cpu_brand = self._get_cpu_brand()
            gpu_brands = self._get_gpu_brands()
            
            # Determine profile based on CPU and GPU brands
            if "Intel" in cpu_brand:
                if any("NVIDIA" in brand or "GeForce" in brand or "RTX" in brand for brand in gpu_brands):
                    return HardwareProfile.INTEL_NVIDIA
                elif any("Intel" in brand for brand in gpu_brands):
                    return HardwareProfile.INTEL_INTEL
                else:
                    return HardwareProfile.INTEL_NVIDIA  # Default to Intel+NVIDIA
            elif "AMD" in cpu_brand:
                if any("AMD" in brand or "Radeon" in brand for brand in gpu_brands):
                    return HardwareProfile.AMD_AMD
                else:
                    return HardwareProfile.AMD_AMD  # Default to AMD+AMD
            else:
                return HardwareProfile.MIXED
                
        except Exception as e:
            self.logger.error(f"Failed to detect hardware profile: {e}")
            return HardwareProfile.UNKNOWN
    
    def _detect_capabilities(self) -> List[SystemCapability]:
        """Detect system capabilities"""
        capabilities = []
        
        try:
            cpu_info = self._get_cpu_info()
            gpu_info = self._get_gpu_info()
            memory_info = self._get_memory_info()
            
            # Gaming capability
            if (cpu_info.get('cores', 0) >= 4 and 
                memory_info.get('total_gb', 0) >= 8 and
                len(gpu_info.get('gpus', [])) > 0):
                capabilities.append(SystemCapability.GAMING)
            
            # Productivity capability
            if (cpu_info.get('cores', 0) >= 2 and 
                memory_info.get('total_gb', 0) >= 4):
                capabilities.append(SystemCapability.PRODUCTIVITY)
            
            # Development capability
            if (cpu_info.get('cores', 0) >= 4 and 
                memory_info.get('total_gb', 0) >= 8):
                capabilities.append(SystemCapability.DEVELOPMENT)
            
            # Server capability
            if (cpu_info.get('cores', 0) >= 8 and 
                memory_info.get('total_gb', 0) >= 16):
                capabilities.append(SystemCapability.SERVER)
            
            # Multimedia capability
            if (len(gpu_info.get('gpus', [])) > 0 and
                memory_info.get('total_gb', 0) >= 8):
                capabilities.append(SystemCapability.MULTIMEDIA)
            
            # Basic capability (always available)
            capabilities.append(SystemCapability.BASIC)
            
        except Exception as e:
            self.logger.error(f"Failed to detect capabilities: {e}")
            capabilities.append(SystemCapability.BASIC)
        
        return capabilities
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'brand': self._get_cpu_brand(),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'frequency': cpu_freq._asdict() if cpu_freq else None,
                'usage_percent': cpu_percent,
                'architecture': platform.architecture()[0]
            }
        except Exception as e:
            self.logger.error(f"Failed to get CPU info: {e}")
            return {}
    
    def _get_cpu_brand(self) -> str:
        """Get CPU brand"""
        try:
            return platform.processor()
        except:
            return "Unknown"
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        gpu_info = {'gpus': []}
        
        try:
            # Try NVIDIA GPU detection
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip():
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 5:
                                gpu_info['gpus'].append({
                                    'brand': 'NVIDIA',
                                    'name': parts[0],
                                    'memory_total': int(parts[1]),
                                    'memory_used': int(parts[2]),
                                    'utilization': int(parts[3]),
                                    'temperature': int(parts[4]) if parts[4] != 'N/A' else None
                                })
            except:
                pass
            
            # Try AMD GPU detection
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_info['gpus'].append({
                        'brand': 'AMD',
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal,
                        'memory_used': gpu.memoryUsed,
                        'utilization': gpu.load * 100,
                        'temperature': gpu.temperature
                    })
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to get GPU info: {e}")
        
        return gpu_info
    
    def _get_gpu_brands(self) -> List[str]:
        """Get GPU brands"""
        gpu_info = self._get_gpu_info()
        return [gpu.get('brand', 'Unknown') for gpu in gpu_info.get('gpus', [])]
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory info: {e}")
            return {}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        try:
            disks = []
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except:
                    continue
            
            return {'disks': disks}
        except Exception as e:
            self.logger.error(f"Failed to get disk info: {e}")
            return {}
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for interface_name, addresses in net_if_addrs.items():
                stats = net_if_stats.get(interface_name)
                if stats:
                    interfaces.append({
                        'name': interface_name,
                        'is_up': stats.isup,
                        'speed': stats.speed,
                        'mtu': stats.mtu,
                        'duplex': stats.duplex
                    })
            
            return {'interfaces': interfaces}
        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
            return {}
    
    def _get_build_number(self) -> int:
        """Get Windows build number"""
        try:
            if platform.system() == "Windows":
                version_info = platform.version()
                if "10.0" in version_info:
                    parts = version_info.split('.')
                    if len(parts) >= 3:
                        return int(parts[2])
            return 0
        except:
            return 0
    
    def _get_version_string(self) -> str:
        """Get version string"""
        try:
            return platform.platform()
        except:
            return "Unknown"
    
    def _calculate_system_score(self, cpu_info: Dict, gpu_info: Dict, memory_info: Dict) -> float:
        """Calculate system performance score"""
        try:
            score = 0.0
            
            # CPU score (0-40 points)
            cpu_score = min(40, cpu_info.get('cores', 0) * 5 + cpu_info.get('threads', 0) * 2.5)
            score += cpu_score
            
            # GPU score (0-30 points)
            gpu_count = len(gpu_info.get('gpus', []))
            gpu_score = min(30, gpu_count * 15)
            score += gpu_score
            
            # Memory score (0-20 points)
            memory_gb = memory_info.get('total_gb', 0)
            memory_score = min(20, memory_gb * 2)
            score += memory_score
            
            # Bonus points (0-10 points)
            if cpu_info.get('cores', 0) >= 8:
                score += 5
            if memory_gb >= 16:
                score += 3
            if gpu_count >= 2:
                score += 2
            
            return min(100, score)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate system score: {e}")
            return 0.0
    
    def _generate_optimization_profile(self) -> OptimizationProfile:
        """Generate optimization profile based on system info"""
        if not self.system_info:
            return OptimizationProfile(
                system_type=SystemType.UNKNOWN,
                hardware_profile=HardwareProfile.UNKNOWN,
                cpu_optimizations={},
                gpu_optimizations={},
                memory_optimizations={},
                network_optimizations={},
                ui_optimizations={},
                power_optimizations={}
            )
        
        # Generate Windows 11 specific optimizations
        if self.system_info.system_type == SystemType.WINDOWS_11:
            return self._generate_windows_11_optimizations()
        elif self.system_info.system_type == SystemType.WINDOWS_10:
            return self._generate_windows_10_optimizations()
        else:
            return self._generate_generic_optimizations()
    
    def _generate_windows_11_optimizations(self) -> OptimizationProfile:
        """Generate Windows 11 specific optimizations"""
        return OptimizationProfile(
            system_type=SystemType.WINDOWS_11,
            hardware_profile=self.system_info.hardware_profile,
            cpu_optimizations={
                'power_plan': 'Ultimate Performance',
                'process_priority': 'High',
                'cpu_cores': 'All Cores',
                'thread_management': 'Optimized',
                'scheduler': 'Windows 11 Scheduler'
            },
            gpu_optimizations={
                'directx_version': 'DirectX 12 Ultimate',
                'shader_cache': 'Enabled',
                'variable_refresh_rate': 'Enabled',
                'auto_hdr': 'Enabled',
                'gpu_scheduling': 'Hardware Accelerated GPU Scheduling'
            },
            memory_optimizations={
                'memory_compression': 'Enabled',
                'virtual_memory': 'Automatic',
                'standby_list': 'Optimized',
                'working_set': 'Optimized'
            },
            network_optimizations={
                'tcp_autotuning': 'High',
                'receive_side_scaling': 'Enabled',
                'tcp_fast_open': 'Enabled',
                'dns_over_https': 'Enabled'
            },
            ui_optimizations={
                'animations': 'Optimized',
                'snap_layouts': 'Enabled',
                'widgets': 'Enabled',
                'centered_taskbar': 'Enabled',
                'rounded_corners': 'Enabled'
            },
            power_optimizations={
                'power_throttling': 'Enabled',
                'battery_saver': 'Smart',
                'sleep_mode': 'Optimized',
                'hibernation': 'Available'
            }
        )
    
    def _generate_windows_10_optimizations(self) -> OptimizationProfile:
        """Generate Windows 10 specific optimizations"""
        return OptimizationProfile(
            system_type=SystemType.WINDOWS_10,
            hardware_profile=self.system_info.hardware_profile,
            cpu_optimizations={
                'power_plan': 'High Performance',
                'process_priority': 'Normal',
                'cpu_cores': 'All Cores',
                'thread_management': 'Standard',
                'scheduler': 'Windows 10 Scheduler',
                'cpu_frequency_scaling': 'Balanced',
                'core_parking': 'Enabled'
            },
            gpu_optimizations={
                'directx_version': 'DirectX 12',
                'shader_cache': 'Enabled',
                'variable_refresh_rate': 'Disabled',
                'auto_hdr': 'Disabled',
                'gpu_scheduling': 'Standard',
                'game_mode': 'Enabled',
                'game_bar': 'Enabled',
                'gpu_work_queue': 'Standard'
            },
            memory_optimizations={
                'memory_compression': 'Enabled',
                'virtual_memory': 'Automatic',
                'standby_list': 'Standard',
                'working_set': 'Standard',
                'prefetch': 'Enabled',
                'superfetch': 'Enabled',
                'readyboost': 'Available'
            },
            network_optimizations={
                'tcp_autotuning': 'Normal',
                'receive_side_scaling': 'Enabled',
                'tcp_fast_open': 'Disabled',
                'dns_over_https': 'Disabled',
                'network_throttling': 'Standard',
                'qos': 'Enabled',
                'chimney_offload': 'Enabled'
            },
            ui_optimizations={
                'animations': 'Standard',
                'snap_layouts': 'Disabled',
                'widgets': 'Disabled',
                'centered_taskbar': 'Disabled',
                'rounded_corners': 'Disabled',
                'timeline': 'Enabled',
                'action_center': 'Enabled',
                'cortana': 'Available',
                'virtual_desktops': 'Enabled',
                'focus_assist': 'Enabled'
            },
            power_optimizations={
                'power_throttling': 'Enabled',
                'battery_saver': 'Standard',
                'sleep_mode': 'Standard',
                'hibernation': 'Available',
                'fast_startup': 'Enabled',
                'hybrid_sleep': 'Available',
                'connected_standby': 'Enabled'
            }
        )
    
    def _generate_generic_optimizations(self) -> OptimizationProfile:
        """Generate generic optimizations"""
        return OptimizationProfile(
            system_type=self.system_info.system_type,
            hardware_profile=self.system_info.hardware_profile,
            cpu_optimizations={'power_plan': 'Balanced'},
            gpu_optimizations={'directx_version': 'Auto'},
            memory_optimizations={'virtual_memory': 'Automatic'},
            network_optimizations={'tcp_autotuning': 'Normal'},
            ui_optimizations={'animations': 'Standard'},
            power_optimizations={'power_throttling': 'Enabled'}
        )
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        if not self.system_info:
            return recommendations
        
        # System-specific recommendations
        if self.system_info.system_type == SystemType.WINDOWS_11:
            recommendations.extend([
                "Enable Windows 11 Snap Layouts for better multitasking",
                "Use Windows Terminal for improved command-line experience",
                "Enable Hardware Accelerated GPU Scheduling",
                "Configure Auto HDR for supported games",
                "Use Windows 11 Power Modes for better battery life"
            ])
        elif self.system_info.system_type == SystemType.WINDOWS_10:
            recommendations.extend([
                "Enable Windows 10 Game Mode for gaming performance",
                "Configure Windows 10 Timeline for activity tracking",
                "Use Windows 10 Virtual Desktops for organization",
                "Enable Focus Assist for productivity and concentration",
                "Configure Storage Sense for automatic disk cleanup",
                "Use Windows 10 Action Center for notifications",
                "Enable Cortana for voice assistance",
                "Configure Windows 10 Fast Startup for quick boot",
                "Use Windows 10 Game Bar for gaming overlay",
                "Enable Windows Defender Security Center",
                "Configure Windows 10 Power Throttling",
                "Use Windows 10 ReadyBoost for memory optimization",
                "Enable Windows 10 Prefetch for faster app loading",
                "Configure Windows 10 Superfetch for system optimization"
            ])
        
        # Hardware-specific recommendations
        if self.system_info.hardware_profile == HardwareProfile.INTEL_NVIDIA:
            recommendations.extend([
                "Enable NVIDIA GPU acceleration",
                "Configure Intel Quick Sync Video",
                "Use NVIDIA Control Panel for optimal settings"
            ])
        
        # Capability-specific recommendations
        if SystemCapability.GAMING in self.system_info.capabilities:
            recommendations.extend([
                "Configure gaming power settings",
                "Enable game mode and game bar",
                "Optimize GPU settings for gaming"
            ])
        
        if SystemCapability.DEVELOPMENT in self.system_info.capabilities:
            recommendations.extend([
                "Enable developer mode",
                "Configure WSL for development",
                "Optimize for development workloads"
            ])
        
        return recommendations
    
    def apply_optimizations(self) -> bool:
        """Apply system optimizations"""
        if not self.optimization_profile:
            return False
        
        try:
            self.logger.info(f"Applying optimizations for {self.system_info.system_type.value}")
            
            # This would implement actual optimization application
            # For now, we'll just log what would be applied
            
            self.logger.info("CPU Optimizations:")
            for key, value in self.optimization_profile.cpu_optimizations.items():
                self.logger.info(f"  {key}: {value}")
            
            self.logger.info("GPU Optimizations:")
            for key, value in self.optimization_profile.gpu_optimizations.items():
                self.logger.info(f"  {key}: {value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimizations: {e}")
            return False
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system summary"""
        if not self.system_info:
            return {}
        
        return {
            'system_type': self.system_info.system_type.value,
            'hardware_profile': self.system_info.hardware_profile.value,
            'capabilities': [cap.value for cap in self.system_info.capabilities],
            'build_number': self.system_info.build_number,
            'version': self.system_info.version,
            'architecture': self.system_info.architecture,
            'total_score': self.system_info.total_score,
            'cpu_cores': self.system_info.cpu_info.get('cores', 0),
            'gpu_count': len(self.system_info.gpu_info.get('gpus', [])),
            'memory_gb': self.system_info.memory_info.get('total_gb', 0),
            'recommendations': self.get_optimization_recommendations()
        }

# Global instance
_smart_system_sensing = None

def get_smart_system_sensing() -> SmartSystemSensing:
    """Get global smart system sensing instance"""
    global _smart_system_sensing
    if _smart_system_sensing is None:
        _smart_system_sensing = SmartSystemSensing()
    return _smart_system_sensing

def detect_system(force_refresh: bool = False) -> SystemInfo:
    """Detect system information"""
    sensor = get_smart_system_sensing()
    return sensor.detect_system(force_refresh)

def get_optimization_profile() -> Optional[OptimizationProfile]:
    """Get optimization profile"""
    sensor = get_smart_system_sensing()
    return sensor.optimization_profile

def get_system_summary() -> Dict[str, Any]:
    """Get system summary"""
    sensor = get_smart_system_sensing()
    return sensor.get_system_summary()

def is_windows_11() -> bool:
    """Check if running on Windows 11"""
    sensor = get_smart_system_sensing()
    system_info = sensor.detect_system()
    return system_info.system_type == SystemType.WINDOWS_11

def is_windows_10() -> bool:
    """Check if running on Windows 10"""
    sensor = get_smart_system_sensing()
    system_info = sensor.detect_system()
    return system_info.system_type == SystemType.WINDOWS_10
