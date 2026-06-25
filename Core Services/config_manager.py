#!/usr/bin/env python3
"""
Unified Configuration Management System
Centralized configuration for all homelab components
"""

import json
import os
import sys
import yaml
import threading
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

# Add path handling
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import event bus with availability check
try:
    from event_bus import get_event_bus, EventType, publish_system_event_sync
    EVENT_BUS_AVAILABLE = True
except ImportError:
    EVENT_BUS_AVAILABLE = False

@dataclass
class ConfigurationItem:
    key: str
    value: Any
    description: str
    category: str
    modified_at: datetime
    modified_by: str
    is_sensitive: bool = False

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.join(os.path.dirname(__file__), '..', 'config'))
        self.config_dir.mkdir(exist_ok=True)
        
        self._config_file = self.config_dir / 'homelab_config.json'
        self._secure_config_file = self.config_dir / 'secure_config.json'
        self._user_config_file = self.config_dir / 'user_config.json'
        
        self._config: Dict[str, Any] = {}
        self._secure_config: Dict[str, Any] = {}
        self._user_config: Dict[str, Any] = {}
        
        self._lock = threading.RLock()
        self._logger = self._setup_logger()
        self._event_bus = get_event_bus()
        
        # Load existing configurations
        self._load_default_config()
        self._load_all_configs()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup configuration manager logger"""
        logger = logging.getLogger('ConfigManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _load_default_config(self):
        """Load default configuration"""
        self._config = {
            'system': {
                'name': 'Homelab System',
                'version': '1.0.0',
                'debug': False,
                'log_level': 'INFO',
                'max_log_size_mb': 100,
                'backup_retention_days': 30
            },
            'network': {
                'server_ip': '192.168.1.186',
                'client_ip': '192.168.1.132',
                'port_range': '25565-25575',
                'timeout_seconds': 30,
                'retry_attempts': 3,
                'use_ipv6': False
            },
            'ram_sharing': {
                'enabled': True,
                'ram_size_gb': 4,
                'drive_letter': 'R',
                'auto_connect': True,
                'share_name': 'RamDisk',
                'use_iscsi': True,
                'use_smb': True
            },
            'monitoring': {
                'enabled': True,
                'update_interval_seconds': 2,
                'history_retention_hours': 24,
                'alert_threshold_cpu': 80,
                'alert_threshold_memory': 85,
                'alert_threshold_disk': 90
            },
            'rdma': {
                'enabled': True,
                'port': 25565,
                'buffer_size_mb': 64,
                'latency_target_us': 10,
                'auto_optimize': True,
                'fault_tolerance': True
            },
            'security': {
                'require_authentication': False,
                'session_timeout_minutes': 60,
                'max_failed_attempts': 5,
                'encryption_enabled': False,
                'audit_logging': True
            },
            'ui': {
                'theme': 'dark',
                'auto_refresh': True,
                'refresh_interval_seconds': 5,
                'show_advanced_options': False,
                'compact_mode': False
            }
        }
        
        self._secure_config = {
            'credentials': {},
            'api_keys': {},
            'certificates': {},
            'secrets': {}
        }
        
        self._user_config = {
            'preferences': {},
            'favorites': [],
            'recent_tools': [],
            'window_positions': {},
            'custom_settings': {}
        }
        
    def _load_all_configs(self):
        """Load all configuration files"""
        try:
            # Load main config
            if self._config_file.exists():
                with open(self._config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._merge_config(self._config, loaded_config)
                    
            # Load secure config
            if self._secure_config_file.exists():
                with open(self._secure_config_file, 'r') as f:
                    self._secure_config.update(json.load(f))
                    
            # Load user config
            if self._user_config_file.exists():
                with open(self._user_config_file, 'r') as f:
                    self._user_config.update(json.load(f))
                    
            self._logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self._logger.error(f"Error loading configuration: {e}")
            
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Recursively merge configuration dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_config(target[key], value)
            else:
                target[key] = value
                
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        with self._lock:
            # Check user config first
            if key in self._user_config:
                return self._user_config[key]
                
            # Check main config
            keys = key.split('.')
            current = self._config
            
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            
            return current
            
    def get_all(self, category: str = 'general') -> Dict[str, Any]:
        """Get all configuration values"""
        try:
            with self._lock:
                if category == 'user':
                    return self._user_config.copy()
                elif category == 'secure':
                    return self._secure_config.copy()
                else:
                    return self._config.copy()
        except Exception as e:
            self._logger.error(f"Error getting all config: {e}")
            return {}
            
    def get_secure(self, key: str, default: Any = None) -> Any:
        """Get secure configuration value"""
        with self._lock:
            keys = key.split('.')
            current = self._secure_config
            
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
                    
            return current
            
    def set(self, key: str, value: Any, category: str = 'general', 
            description: str = '', is_sensitive: bool = False, 
            modified_by: str = 'system') -> bool:
        """Set configuration value"""
        try:
            with self._lock:
                keys = key.split('.')
                current = self._user_config if category == 'user' else self._config
                
                # Navigate to the target location
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                    
                # Set the value
                old_value = current.get(keys[-1])
                current[keys[-1]] = value
                
                # Save to appropriate file
                if category == 'user':
                    self._save_user_config()
                elif is_sensitive:
                    self._secure_config[keys[-1]] = value
                    self._save_secure_config()
                else:
                    self._save_config()
                    
                # Publish configuration change event
                publish_system_event_sync(
                    'ConfigManager',
                    {
                        'action': 'config_changed',
                        'key': key,
                        'old_value': old_value,
                        'new_value': value,
                        'category': category
                    }
                )
                
                self._logger.info(f"Configuration updated: {key} = {value}")
                return True
                
        except Exception as e:
            self._logger.error(f"Error setting configuration {key}: {e}")
            return False
            
    def set_secure(self, key: str, value: Any, modified_by: str = 'system') -> bool:
        """Set secure configuration value"""
        try:
            with self._lock:
                keys = key.split('.')
                current = self._secure_config
                
                # Navigate to the target location
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                    
                # Set the value
                old_value = current.get(keys[-1])
                current[keys[-1]] = value
                
                # Save secure config
                self._save_secure_config()
                
                # Publish configuration change event
                publish_system_event_sync(
                    'ConfigManager',
                    {
                        'action': 'secure_config_changed',
                        'key': key,
                        'old_value': old_value,
                        'new_value': value
                    }
                )
                
                self._logger.info(f"Secure configuration updated: {key}")
                return True
                
        except Exception as e:
            self._logger.error(f"Error setting secure configuration {key}: {e}")
            return False
            
    def _save_config(self):
        """Save main configuration"""
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=2, default=str)
        except Exception as e:
            self._logger.error(f"Error saving configuration: {e}")
            
    def _save_secure_config(self):
        """Save secure configuration"""
        try:
            with open(self._secure_config_file, 'w') as f:
                json.dump(self._secure_config, f, indent=2, default=str)
        except Exception as e:
            self._logger.error(f"Error saving secure configuration: {e}")
            
    def _save_user_config(self):
        """Save user configuration"""
        try:
            with open(self._user_config_file, 'w') as f:
                json.dump(self._user_config, f, indent=2, default=str)
        except Exception as e:
            self._logger.error(f"Error saving user configuration: {e}")
            
    def save_all(self) -> bool:
        """Save all configurations"""
        try:
            with self._lock:
                self._save_config()
                self._save_secure_config()
                self._save_user_config()
                
            self._logger.info("All configurations saved")
            return True
            
        except Exception as e:
            self._logger.error(f"Error saving configurations: {e}")
            return False
            
    def backup_config(self, backup_name: str = None) -> str:
        """Create configuration backup"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        backup_file = self.config_dir / backup_name
        
        try:
            with self._lock:
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'config': self._config,
                    'user_config': self._user_config
                    # Note: secure config is not backed up automatically
                }
                
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2, default=str)
                    
            self._logger.info(f"Configuration backup created: {backup_name}")
            return str(backup_file)
            
        except Exception as e:
            self._logger.error(f"Error creating backup: {e}")
            return ""
            
    def restore_config(self, backup_file: str) -> bool:
        """Restore configuration from backup"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
                
            with self._lock:
                if 'config' in backup_data:
                    self._config = backup_data['config']
                if 'user_config' in backup_data:
                    self._user_config = backup_data['user_config']
                    
                self._save_config()
                self._save_user_config()
                
            self._logger.info(f"Configuration restored from: {backup_file}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error restoring configuration: {e}")
            return False
            
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration"""
        with self._lock:
            return {
                'config': self._config.copy(),
                'user_config': self._user_config.copy(),
                'secure_config_keys': list(self._secure_config.keys())
            }
            
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration"""
        issues = []
        warnings = []
        
        # Validate network configuration
        server_ip = self.get('network.server_ip')
        client_ip = self.get('network.client_ip')
        
        if not server_ip or not client_ip:
            issues.append("Network IP addresses not configured")
        elif server_ip == client_ip:
            issues.append("Server and client IP addresses cannot be the same")
            
        # Validate RAM sharing configuration
        ram_size = self.get('ram_sharing.ram_size_gb')
        if ram_size and (ram_size < 1 or ram_size > 32):
            warnings.append(f"RAM size {ram_size}GB may be too small or too large")
            
        # Validate monitoring configuration
        update_interval = self.get('monitoring.update_interval_seconds')
        if update_interval and (update_interval < 1 or update_interval > 60):
            warnings.append(f"Update interval {update_interval}s may be too fast or too slow")
            
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
        
    def reset_to_defaults(self, category: str = None) -> bool:
        """Reset configuration to defaults"""
        try:
            with self._lock:
                if category == 'all':
                    self._load_default_config()
                    self._save_config()
                    self._save_user_config()
                elif category == 'user':
                    self._user_config = {}
                    self._save_user_config()
                else:
                    # Reset specific category
                    if category in self._config:
                        self._load_default_config()
                        self._save_config()
                        
                self._logger.info(f"Configuration reset: {category}")
                return True
                
        except Exception as e:
            self._logger.error(f"Error resetting configuration: {e}")
            return False

# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    manager = get_config_manager()
    return manager.get(key, default)

if __name__ == "__main__":
    """Main execution block for config manager"""
    try:
        # Initialize and start the config manager
        config_manager = get_config_manager()
        print("Configuration manager started successfully")
        
        # Example usage
        print("Configuration manager is running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping configuration manager...")
        config_manager.stop()
        print("Configuration manager stopped")
    except Exception as e:
        print(f"Configuration manager error: {e}")

def set_config(key: str, value: Any, **kwargs) -> bool:
    """Set configuration value"""
    manager = get_config_manager()
    return manager.set(key, value, **kwargs)

def get_secure_config(key: str, default: Any = None) -> Any:
    """Get secure configuration value"""
    manager = get_config_manager()
    return manager.get_secure(key, default)

def set_secure_config(key: str, value: Any, **kwargs) -> bool:
    """Set secure configuration value"""
    manager = get_config_manager()
    return manager.set_secure(key, value, **kwargs)
