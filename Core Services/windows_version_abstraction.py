#!/usr/bin/env python3
"""
Windows Version Abstraction Layer
Provides Windows 10 and Windows 11 specific optimizations and features
"""

import platform
import subprocess
import logging
import ctypes
import os
import time
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
import psutil

class WindowsVersion(Enum):
    """Windows version enumeration"""
    WINDOWS_10 = "Windows 10"
    WINDOWS_11 = "Windows 11"
    UNKNOWN = "Unknown"

class WindowsFeature(Enum):
    """Windows features by version"""
    # Windows 10 features
    WSL_1 = "wsl_1"
    POWER_TOYS = "power_toys"
    WINDOWS_TERMINAL = "windows_terminal"
    WINGET = "winget"
    
    # Windows 11 features
    WSL_2 = "wsl_2"
    WIDGETS = "widgets"
    SNAP_LAYOUTS = "snap_layouts"
    DIRECTX_12_ULTIMATE = "directx_12_ultimate"
    AUTO_HDR = "auto_hdr"
    STORAGE_SPACES = "storage_spaces"

class WindowsAbstractionLayer(ABC):
    """Abstract base class for Windows version-specific features"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.version = self._detect_version()
        self.build_number = self._get_build_number()
        self.available_features = self._detect_features()
        
    @abstractmethod
    def _detect_version(self) -> WindowsVersion:
        """Detect Windows version"""
        pass
    
    def _get_build_number(self) -> int:
        """Get Windows build number"""
        try:
            version_info = platform.version()
            if "10.0" in version_info:
                parts = version_info.split('.')
                if len(parts) >= 3:
                    return int(parts[2])
        except:
            pass
        return 0
    
    def _detect_features(self) -> List[WindowsFeature]:
        """Detect available Windows features"""
        features = []
        
        # Check for common features
        if self._check_wsl():
            features.append(WindowsFeature.WSL_1)
            if self.version == WindowsVersion.WINDOWS_11:
                features.append(WindowsFeature.WSL_2)
        
        if self._check_winget():
            features.append(WindowsFeature.WINGET)
        
        if self._check_windows_terminal():
            features.append(WindowsFeature.WINDOWS_TERMINAL)
        
        if self.version == WindowsVersion.WINDOWS_11:
            features.extend([WindowsFeature.WIDGETS, WindowsFeature.SNAP_LAYOUTS])
        
        return features
    
    def _check_wsl(self) -> bool:
        """Check if WSL is available"""
        try:
            result = subprocess.run(['wsl', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_winget(self) -> bool:
        """Check if winget is available"""
        try:
            result = subprocess.run(['winget', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_windows_terminal(self) -> bool:
        """Check if Windows Terminal is available"""
        try:
            # Check for Windows Terminal installation
            terminal_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Microsoft.WindowsTerminal_8wekyb3d8bbwe\WindowsTerminal.exe"),
                os.path.expandvars(r"%ProgramFiles%\WindowsApps\Microsoft.WindowsTerminal_*\WindowsTerminal.exe")
            ]
            
            for path in terminal_paths:
                if os.path.exists(path) or any(os.path.exists(p) for p in glob.glob(path)):
                    return True
            return False
        except:
            return False
    
    @abstractmethod
    def get_system_optimizations(self) -> Dict[str, Any]:
        """Get system-specific optimizations"""
        pass
    
    @abstractmethod
    def get_performance_tuning(self) -> Dict[str, Any]:
        """Get performance tuning parameters"""
        pass
    
    @abstractmethod
    def get_network_optimizations(self) -> Dict[str, Any]:
        """Get network optimizations"""
        pass
    
    @abstractmethod
    def get_gpu_optimizations(self) -> Dict[str, Any]:
        """Get GPU optimizations"""
        pass

class Windows10AbstractionLayer(WindowsAbstractionLayer):
    """Windows 10 specific abstraction layer"""
    
    def __init__(self):
        super().__init__()
        self.logger.info("Windows 10 Abstraction Layer initialized")
    
    def _detect_version(self) -> WindowsVersion:
        """Detect Windows 10"""
        try:
            version_info = platform.version()
            build_number = self._get_build_number()
            
            if "10.0" in version_info and build_number < 22000:
                return WindowsVersion.WINDOWS_10
        except:
            pass
        return WindowsVersion.UNKNOWN
    
    def get_system_optimizations(self) -> Dict[str, Any]:
        """Get Windows 10 specific optimizations"""
        return {
            'power_plan': 'High Performance',
            'visual_effects': 'Best Performance',
            'virtual_memory': {
                'initial_size': '4096',
                'maximum_size': '8192'
            },
            'system_protection': {
                'create_restore_point': True,
                'disk_space_usage': '5%'
            },
            'gaming_mode': False,  # Windows 10 gaming mode
            'game_bar': True,
            'xbox_game_dvr': False
        }
    
    def get_performance_tuning(self) -> Dict[str, Any]:
        """Get Windows 10 performance tuning"""
        return {
            'cpu_priority': 'High',
            'process_priority': 'Normal',
            'memory_management': {
                'clear_standby_list': True,
                'compress_memory': True,
                'prefetch': 'Enabled'
            },
            'disk_optimization': {
                'defrag_schedule': 'Weekly',
                'trim_ssd': True,
                'compress_os_drive': False
            },
            'network_tuning': {
                'qos': 'Enabled',
                'tcp_autotuning': 'Normal',
                'receive_side_scaling': 'Enabled'
            }
        }
    
    def get_network_optimizations(self) -> Dict[str, Any]:
        """Get Windows 10 network optimizations"""
        return {
            'tcp_settings': {
                'autotuning': 'normal',
                'chimney_offload': 'enabled',
                'rss': 'enabled',
                'netdma': 'enabled'
            },
            'dns_settings': {
                'cache_timeout': '300',
                'negative_cache_ttl': '5'
            },
            'power_management': {
                'disable_wol': False,
                'energy_efficient_ethernet': True
            }
        }
    
    def get_gpu_optimizations(self) -> Dict[str, Any]:
        """Get Windows 10 GPU optimizations"""
        return {
            'directx': '12',
            'shader_cache': 'Enabled',
            'texture_quality': 'High',
            'vsync': 'Application Controlled',
            'power_management': 'Prefer Maximum Performance',
            'multi_display': 'Single Display Performance'
        }

class Windows11AbstractionLayer(WindowsAbstractionLayer):
    """Windows 11 specific abstraction layer"""
    
    def __init__(self):
        super().__init__()
        self.logger.info("Windows 11 Abstraction Layer initialized")
    
    def _detect_version(self) -> WindowsVersion:
        """Detect Windows 11"""
        try:
            version_info = platform.version()
            build_number = self._get_build_number()
            
            if "10.0" in version_info and build_number >= 22000:
                return WindowsVersion.WINDOWS_11
        except:
            pass
        return WindowsVersion.UNKNOWN
    
    def get_system_optimizations(self) -> Dict[str, Any]:
        """Get Windows 11 specific optimizations"""
        return {
            'power_plan': 'Ultimate Performance',
            'visual_effects': 'Best Performance',
            'virtual_memory': {
                'initial_size': '8192',
                'maximum_size': '16384'
            },
            'system_protection': {
                'create_restore_point': True,
                'disk_space_usage': '3%'
            },
            'gaming_mode': True,  # Windows 11 gaming mode
            'game_bar': True,
            'xbox_game_dvr': False,
            'snap_assist': True,
            'widgets': True
        }
    
    def get_performance_tuning(self) -> Dict[str, Any]:
        """Get Windows 11 performance tuning"""
        return {
            'cpu_priority': 'Realtime',
            'process_priority': 'High',
            'memory_management': {
                'clear_standby_list': True,
                'compress_memory': True,
                'prefetch': 'Enabled',
                'process_working_set': 'Optimized'
            },
            'disk_optimization': {
                'defrag_schedule': 'Weekly',
                'trim_ssd': True,
                'compress_os_drive': True,
                'storage_spaces': 'Enabled'
            },
            'network_tuning': {
                'qos': 'Enabled',
                'tcp_autotuning': 'High',
                'receive_side_scaling': 'Enabled',
                'tcp_fast_open': 'Enabled'
            }
        }
    
    def get_network_optimizations(self) -> Dict[str, Any]:
        """Get Windows 11 network optimizations"""
        return {
            'tcp_settings': {
                'autotuning': 'high',
                'chimney_offload': 'enabled',
                'rss': 'enabled',
                'netdma': 'enabled',
                'tcp_fast_open': 'enabled'
            },
            'dns_settings': {
                'cache_timeout': '300',
                'negative_cache_ttl': '5',
                'dns_over_https': 'Enabled'
            },
            'power_management': {
                'disable_wol': False,
                'energy_efficient_ethernet': False,
                'usb_selective_suspend': False
            }
        }
    
    def get_gpu_optimizations(self) -> Dict[str, Any]:
        """Get Windows 11 GPU optimizations"""
        return {
            'directx': '12_ultimate',
            'shader_cache': 'Enabled',
            'texture_quality': 'Ultra',
            'vsync': 'Fast Sync',
            'power_management': 'Prefer Maximum Performance',
            'multi_display': 'Multi Display Performance',
            'auto_hdr': True,
            'variable_refresh_rate': True
        }

class WindowsVersionDetector:
    """Detects Windows version and returns appropriate abstraction layer"""
    
    @staticmethod
    def get_abstraction_layer() -> WindowsAbstractionLayer:
        """Get appropriate Windows abstraction layer"""
        try:
            version_info = platform.version()
            build_number = 0
            
            if "10.0" in version_info:
                parts = version_info.split('.')
                if len(parts) >= 3:
                    build_number = int(parts[2])
            
            if build_number >= 22000:
                return Windows11AbstractionLayer()
            else:
                return Windows10AbstractionLayer()
                
        except Exception as e:
            logging.getLogger("WindowsVersionDetector").error(f"Failed to detect Windows version: {e}")
            # Default to Windows 10 layer
            return Windows10AbstractionLayer()

# Global instance
_windows_abstraction_layer = None

def get_windows_abstraction_layer() -> WindowsAbstractionLayer:
    """Get global Windows abstraction layer instance"""
    global _windows_abstraction_layer
    if _windows_abstraction_layer is None:
        _windows_abstraction_layer = WindowsVersionDetector.get_abstraction_layer()
    return _windows_abstraction_layer

def is_windows_11() -> bool:
    """Check if running on Windows 11"""
    layer = get_windows_abstraction_layer()
    return layer.version == WindowsVersion.WINDOWS_11

def is_windows_10() -> bool:
    """Check if running on Windows 10"""
    layer = get_windows_abstraction_layer()
    return layer.version == WindowsVersion.WINDOWS_10

def get_windows_features() -> List[WindowsFeature]:
    """Get available Windows features"""
    layer = get_windows_abstraction_layer()
    return layer.available_features

def get_windows_optimizations() -> Dict[str, Any]:
    """Get Windows-specific optimizations"""
    layer = get_windows_abstraction_layer()
    return {
        'system': layer.get_system_optimizations(),
        'performance': layer.get_performance_tuning(),
        'network': layer.get_network_optimizations(),
        'gpu': layer.get_gpu_optimizations(),
        'version': layer.version.value,
        'build_number': layer.build_number,
        'features': [f.value for f in layer.available_features]
    }
