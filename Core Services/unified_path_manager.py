#!/usr/bin/env python3
"""
Unified Path Manager
Integrates all paths and data with abstraction layers
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import abstraction layers
try:
    from data_abstraction_layer import get_data_abstraction_layer, DataType
    from windows_version_abstraction import get_windows_abstraction_layer, get_windows_optimizations
    from frontend_backend_mixer import get_frontend_backend_mixer, broadcast_data, broadcast_status
    ABSTRACTION_AVAILABLE = True
except ImportError as e:
    logging.getLogger("UnifiedPathManager").warning(f"Abstraction layers not available: {e}")
    ABSTRACTION_AVAILABLE = False

class PathType(Enum):
    """Path types for unified management"""
    CORE_SERVICES = "core_services"
    MONITORING_TOOLS = "monitoring_tools"
    HARDWARE_TOOLS = "hardware_tools"
    CONFIG_FILES = "config_files"
    DATA_STORAGE = "data_storage"
    LOG_FILES = "log_files"
    TEMP_FILES = "temp_files"
    USER_DATA = "user_data"
    SYSTEM_DATA = "system_data"
    WEB_ASSETS = "web_assets"
    MOBILE_ASSETS = "mobile_assets"

class DataSource(Enum):
    """Data source types"""
    ABSTRACTION_LAYER = "abstraction_layer"
    WINDOWS_VERSION = "windows_version"
    FRONTEND_MIXER = "frontend_mixer"
    DIRECT_FILE = "direct_file"
    SYSTEM_API = "system_api"

@dataclass
class PathConfig:
    """Path configuration"""
    path_type: PathType
    base_path: str
    data_source: DataSource
    relative_path: Optional[str] = None
    file_pattern: Optional[str] = None
    cache_enabled: bool = True
    cache_timeout: float = 60.0
    metadata: Optional[Dict[str, Any]] = None

class UnifiedPathManager:
    """Manages all paths and data with abstraction layers"""
    
    def __init__(self, root_dir: str = None):
        self.logger = logging.getLogger("UnifiedPathManager")
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).parent.parent
        self.path_configs: Dict[PathType, PathConfig] = {}
        self.data_cache: Dict[str, Dict[str, Any]] = {}
        self.last_cache_update: Dict[str, float] = {}
        
        # Initialize abstraction layers
        if ABSTRACTION_AVAILABLE:
            self.data_layer = get_data_abstraction_layer()
            self.windows_layer = get_windows_abstraction_layer()
            self.mixer_layer = get_frontend_backend_mixer()
        else:
            self.data_layer = None
            self.windows_layer = None
            self.mixer_layer = None
        
        self._setup_default_paths()
        self._initialize_abstraction_integration()
    
    def _setup_default_paths(self):
        """Setup default path configurations"""
        self.path_configs = {
            PathType.CORE_SERVICES: PathConfig(
                path_type=PathType.CORE_SERVICES,
                base_path=str(self.root_dir / "Core Services"),
                data_source=DataSource.DIRECT_FILE,
                file_pattern="*.py"
            ),
            PathType.MONITORING_TOOLS: PathConfig(
                path_type=PathType.MONITORING_TOOLS,
                base_path=str(self.root_dir),
                data_source=DataSource.ABSTRACTION_LAYER,
                relative_path="monitoring_data"
            ),
            PathType.HARDWARE_TOOLS: PathConfig(
                path_type=PathType.HARDWARE_TOOLS,
                base_path=str(self.root_dir),
                data_source=DataSource.WINDOWS_VERSION,
                relative_path="hardware_data"
            ),
            PathType.CONFIG_FILES: PathConfig(
                path_type=PathType.CONFIG_FILES,
                base_path=str(self.root_dir / "config"),
                data_source=DataSource.DIRECT_FILE,
                file_pattern="*.json"
            ),
            PathType.DATA_STORAGE: PathConfig(
                path_type=PathType.DATA_STORAGE,
                base_path=str(self.root_dir / "data"),
                data_source=DataSource.ABSTRACTION_LAYER,
                cache_enabled=True
            ),
            PathType.LOG_FILES: PathConfig(
                path_type=PathType.LOG_FILES,
                base_path=str(self.root_dir / "logs"),
                data_source=DataSource.DIRECT_FILE,
                file_pattern="*.log"
            ),
            PathType.TEMP_FILES: PathConfig(
                path_type=PathType.TEMP_FILES,
                base_path=str(self.root_dir / "temp"),
                data_source=DataSource.DIRECT_FILE,
                cache_enabled=False
            ),
            PathType.USER_DATA: PathConfig(
                path_type=PathType.USER_DATA,
                base_path=str(self.root_dir / "user_data"),
                data_source=DataSource.FRONTEND_MIXER,
                cache_enabled=True
            ),
            PathType.SYSTEM_DATA: PathConfig(
                path_type=PathType.SYSTEM_DATA,
                base_path=str(self.root_dir / "system_data"),
                data_source=DataSource.ABSTRACTION_LAYER,
                cache_enabled=True
            ),
            PathType.WEB_ASSETS: PathConfig(
                path_type=PathType.WEB_ASSETS,
                base_path=str(self.root_dir / "Mobile_Interface"),
                data_source=DataSource.DIRECT_FILE,
                file_pattern="*.*"
            ),
            PathType.MOBILE_ASSETS: PathConfig(
                path_type=PathType.MOBILE_ASSETS,
                base_path=str(self.root_dir / "Mobile_Interface"),
                data_source=DataSource.FRONTEND_MIXER,
                cache_enabled=True
            )
        }
    
    def _initialize_abstraction_integration(self):
        """Initialize integration with abstraction layers"""
        if not ABSTRACTION_AVAILABLE:
            return
        
        try:
            # Start data layer monitoring
            if self.data_layer:
                self.data_layer.start_monitoring(interval=2.0)
                
                # Subscribe to data updates
                self.data_layer.subscribe(DataType.SYSTEM_INFO, self._handle_system_data_update)
                self.data_layer.subscribe(DataType.CPU_INFO, self._handle_cpu_data_update)
                self.data_layer.subscribe(DataType.MEMORY_INFO, self._handle_memory_data_update)
                self.data_layer.subscribe(DataType.GPU_INFO, self._handle_gpu_data_update)
                self.data_layer.subscribe(DataType.NETWORK_INFO, self._handle_network_data_update)
            
            # Start frontend-backend mixer
            if self.mixer_layer:
                self.mixer_layer.start_mixer()
            
            self.logger.info("Abstraction layer integration initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize abstraction integration: {e}")
    
    def get_path(self, path_type: PathType, relative_path: str = None) -> Path:
        """Get path for specified type"""
        config = self.path_configs.get(path_type)
        if not config:
            raise ValueError(f"Unknown path type: {path_type}")
        
        base_path = Path(config.base_path)
        if relative_path:
            return base_path / relative_path
        elif config.relative_path:
            return base_path / config.relative_path
        return base_path
    
    def get_data(self, path_type: PathType, data_key: str = None, force_refresh: bool = False) -> Any:
        """Get data using appropriate abstraction layer"""
        config = self.path_configs.get(path_type)
        if not config:
            raise ValueError(f"Unknown path type: {path_type}")
        
        cache_key = f"{path_type.value}_{data_key or 'default'}"
        
        # Check cache
        if not force_refresh and config.cache_enabled:
            if cache_key in self.data_cache:
                last_update = self.last_cache_update.get(cache_key, 0)
                if time.time() - last_update < config.cache_timeout:
                    return self.data_cache[cache_key]
        
        # Get data based on source
        data = None
        try:
            if config.data_source == DataSource.ABSTRACTION_LAYER and self.data_layer:
                data = self._get_data_from_abstraction_layer(path_type, data_key)
            elif config.data_source == DataSource.WINDOWS_VERSION and self.windows_layer:
                data = self._get_data_from_windows_layer(path_type, data_key)
            elif config.data_source == DataSource.FRONTEND_MIXER and self.mixer_layer:
                data = self._get_data_from_mixer_layer(path_type, data_key)
            elif config.data_source == DataSource.DIRECT_FILE:
                data = self._get_data_from_file(path_type, data_key)
            elif config.data_source == DataSource.SYSTEM_API:
                data = self._get_data_from_system_api(path_type, data_key)
            
            # Cache the result
            if config.cache_enabled and data is not None:
                self.data_cache[cache_key] = data
                self.last_cache_update[cache_key] = time.time()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get data for {path_type}: {e}")
            return None
    
    def _get_data_from_abstraction_layer(self, path_type: PathType, data_key: str) -> Any:
        """Get data from abstraction layer"""
        if not self.data_layer:
            return None
        
        # Map path types to data types
        data_type_mapping = {
            PathType.SYSTEM_DATA: DataType.SYSTEM_INFO,
            PathType.MONITORING_TOOLS: DataType.PERFORMANCE_METRICS,
            PathType.DATA_STORAGE: DataType.MEMORY_INFO,
            PathType.USER_DATA: DataType.RESOURCE_SHARING
        }
        
        data_type = data_type_mapping.get(path_type)
        if not data_type:
            return None
        
        data_packet = self.data_layer.get_data(data_type)
        if data_packet and not data_packet.error:
            if data_key:
                return data_packet.data.get(data_key)
            return data_packet.data
        
        return None
    
    def _get_data_from_windows_layer(self, path_type: PathType, data_key: str) -> Any:
        """Get data from Windows version layer"""
        if not self.windows_layer:
            return None
        
        # Get Windows-specific data
        if path_type == PathType.HARDWARE_TOOLS:
            optimizations = get_windows_optimizations()
            if data_key:
                return optimizations.get(data_key)
            return optimizations
        
        return None
    
    def _get_data_from_mixer_layer(self, path_type: PathType, data_key: str) -> Any:
        """Get data from frontend-backend mixer"""
        if not self.mixer_layer:
            return None
        
        # Get mixer status or component data
        if path_type == PathType.USER_DATA or path_type == PathType.MOBILE_ASSETS:
            status = self.mixer_layer.get_mixer_status()
            if data_key:
                return status.get(data_key)
            return status
        
        return None
    
    def _get_data_from_file(self, path_type: PathType, data_key: str) -> Any:
        """Get data from direct file access"""
        try:
            file_path = self.get_path(path_type, data_key)
            
            if file_path.is_file():
                if file_path.suffix == '.json':
                    with open(file_path, 'r') as f:
                        return json.load(f)
                elif file_path.suffix == '.py':
                    # Return module info
                    return {
                        'file_path': str(file_path),
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime
                    }
                else:
                    # Return file content as text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
            elif file_path.is_dir():
                # Return directory listing
                return {
                    'path': str(file_path),
                    'files': [f.name for f in file_path.iterdir()],
                    'count': len(list(file_path.iterdir()))
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get file data: {e}")
        
        return None
    
    def _get_data_from_system_api(self, path_type: PathType, data_key: str) -> Any:
        """Get data from system API"""
        # This would integrate with system APIs
        return None
    
    def set_data(self, path_type: PathType, data_key: str, data: Any) -> bool:
        """Set data using appropriate layer"""
        config = self.path_configs.get(path_type)
        if not config:
            return False
        
        try:
            if config.data_source == DataSource.ABSTRACTION_LAYER and self.data_layer:
                # Data layer is read-only for now
                pass
            elif config.data_source == DataSource.FRONTEND_MIXER and self.mixer_layer:
                # Broadcast data to frontend
                broadcast_data({data_key: data})
            elif config.data_source == DataSource.DIRECT_FILE:
                # Save to file
                file_path = self.get_path(path_type, data_key)
                if file_path.suffix == '.json':
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)
                else:
                    with open(file_path, 'w') as f:
                        f.write(str(data))
            
            # Update cache
            cache_key = f"{path_type.value}_{data_key}"
            if config.cache_enabled:
                self.data_cache[cache_key] = data
                self.last_cache_update[cache_key] = time.time()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set data for {path_type}: {e}")
            return False
    
    def list_paths(self, path_type: PathType, pattern: str = "*") -> List[Path]:
        """List all paths for specified type"""
        base_path = self.get_path(path_type)
        if base_path.is_dir():
            return list(base_path.glob(pattern))
        return []
    
    def clear_cache(self, path_type: PathType = None):
        """Clear cache for specified path type or all"""
        if path_type:
            keys_to_remove = [k for k in self.data_cache.keys() if k.startswith(path_type.value)]
            for key in keys_to_remove:
                del self.data_cache[key]
                if key in self.last_cache_update:
                    del self.last_cache_update[key]
        else:
            self.data_cache.clear()
            self.last_cache_update.clear()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            'root_directory': str(self.root_dir),
            'path_configs': len(self.path_configs),
            'cache_size': len(self.data_cache),
            'abstraction_layers': {
                'data_available': self.data_layer is not None,
                'windows_available': self.windows_layer is not None,
                'mixer_available': self.mixer_layer is not None
            }
        }
        
        if ABSTRACTION_AVAILABLE:
            if self.data_layer:
                status['data_providers'] = self.data_layer.get_provider_status()
            if self.windows_layer:
                status['windows_version'] = self.windows_layer.version.value
            if self.mixer_layer:
                status['mixer_status'] = self.mixer_layer.get_mixer_status()
        
        return status
    
    # Data update handlers
    def _handle_system_data_update(self, data_packet):
        """Handle system data updates"""
        self.data_cache['system_info'] = data_packet.data
        self.last_cache_update['system_info'] = time.time()
        
        # Broadcast to frontend
        if self.mixer_layer:
            broadcast_data({'system_info': data_packet.data})
    
    def _handle_cpu_data_update(self, data_packet):
        """Handle CPU data updates"""
        self.data_cache['cpu_info'] = data_packet.data
        self.last_cache_update['cpu_info'] = time.time()
        
        # Broadcast to frontend
        if self.mixer_layer:
            broadcast_data({'cpu_info': data_packet.data})
    
    def _handle_memory_data_update(self, data_packet):
        """Handle memory data updates"""
        self.data_cache['memory_info'] = data_packet.data
        self.last_cache_update['memory_info'] = time.time()
        
        # Broadcast to frontend
        if self.mixer_layer:
            broadcast_data({'memory_info': data_packet.data})
    
    def _handle_gpu_data_update(self, data_packet):
        """Handle GPU data updates"""
        self.data_cache['gpu_info'] = data_packet.data
        self.last_cache_update['gpu_info'] = time.time()
        
        # Broadcast to frontend
        if self.mixer_layer:
            broadcast_data({'gpu_info': data_packet.data})
    
    def _handle_network_data_update(self, data_packet):
        """Handle network data updates"""
        self.data_cache['network_info'] = data_packet.data
        self.last_cache_update['network_info'] = time.time()
        
        # Broadcast to frontend
        if self.mixer_layer:
            broadcast_data({'network_info': data_packet.data})
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.data_layer:
                self.data_layer.stop_monitoring()
            if self.mixer_layer:
                self.mixer_layer.stop_mixer()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Global instance
_unified_path_manager = None

def get_unified_path_manager(root_dir: str = None) -> UnifiedPathManager:
    """Get global unified path manager instance"""
    global _unified_path_manager
    if _unified_path_manager is None:
        _unified_path_manager = UnifiedPathManager(root_dir)
    return _unified_path_manager

def get_path(path_type: PathType, relative_path: str = None) -> Path:
    """Get path using unified manager"""
    manager = get_unified_path_manager()
    return manager.get_path(path_type, relative_path)

def get_data(path_type: PathType, data_key: str = None, force_refresh: bool = False) -> Any:
    """Get data using unified manager"""
    manager = get_unified_path_manager()
    return manager.get_data(path_type, data_key, force_refresh)

def set_data(path_type: PathType, data_key: str, data: Any) -> bool:
    """Set data using unified manager"""
    manager = get_unified_path_manager()
    return manager.set_data(path_type, data_key, data)

def get_system_status() -> Dict[str, Any]:
    """Get system status"""
    manager = get_unified_path_manager()
    return manager.get_system_status()
