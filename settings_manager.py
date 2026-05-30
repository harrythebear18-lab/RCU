#!/usr/bin/env python3
"""
Settings Manager for Windows 11 Resource Optimization System
Handles user preferences, configuration storage, and settings persistence.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading

class SettingsManager:
    """Manages application settings and user preferences"""
    
    def __init__(self, app_name="ResourceOptimizer"):
        self.app_name = app_name
        self.settings_file = os.path.join(os.path.dirname(__file__), f"{app_name}_settings.json")
        self.lock = threading.Lock()
        
        # Default settings
        self.default_settings = {
            "general": {
                "auto_start": False,
                "minimize_to_tray": True,
                "start_minimized": False,
                "language": "en_US",
                "theme": "dark",
                "auto_save_interval": 300,  # 5 minutes
                "enable_notifications": True,
                "enable_sounds": False
            },
            "monitoring": {
                "update_interval": 2000,  # milliseconds
                "history_retention_days": 7,
                "enable_cpu_monitoring": True,
                "enable_gpu_monitoring": True,
                "enable_ram_monitoring": True,
                "enable_network_monitoring": False,
                "enable_disk_monitoring": False,
                "enable_temperature_monitoring": True
            },
            "alerts": {
                "cpu_threshold_warning": 80.0,
                "cpu_threshold_critical": 95.0,
                "ram_threshold_warning": 85.0,
                "ram_threshold_critical": 95.0,
                "gpu_threshold_warning": 85.0,
                "gpu_threshold_critical": 95.0,
                "temperature_threshold_warning": 75.0,
                "temperature_threshold_critical": 85.0,
                "enable_alerts": True,
                "alert_sound": False,
                "alert_duration": 5000,  # milliseconds
                "auto_optimization": False
            },
            "optimization": {
                "default_profile": "balanced",
                "auto_profile_switching": False,
                "optimization_aggressiveness": "moderate",
                "enable_process_prioritization": True,
                "enable_memory_optimization": True,
                "enable_gpu_optimization": False,
                "enable_network_optimization": False,
                "optimization_interval": 30,  # seconds
                "backup_profiles": True
            },
            "ui": {
                "window_geometry": {"width": 1200, "height": 800, "x": 0, "y": 0},
                "show_graphs": True,
                "graph_history_points": 60,
                "graph_update_interval": 1000,
                "compact_mode": False,
                "show_tooltips": True,
                "animation_enabled": True,
                "font_size": 10,
                "color_scheme": "default"
            },
            "data": {
                "export_format": "json",
                "auto_export": False,
                "export_interval": 3600,  # 1 hour
                "compress_exports": True,
                "max_export_size_mb": 100,
                "backup_data": True,
                "backup_retention_days": 30
            },
            "advanced": {
                "debug_mode": False,
                "verbose_logging": False,
                "enable_api": False,
                "api_port": 8080,
                "enable_plugins": False,
                "plugin_directory": "",
                "experimental_features": False
            }
        }
        
        # Current settings (loaded from file or defaults)
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                return self._merge_settings(self.default_settings, loaded_settings)
            else:
                # Create default settings file
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """Save settings to file"""
        try:
            with self.lock:
                settings_to_save = settings if settings is not None else self.settings
                
                # Create backup of existing settings
                if os.path.exists(self.settings_file):
                    backup_file = f"{self.settings_file}.backup"
                    try:
                        os.replace(self.settings_file, backup_file)
                    except:
                        pass
                
                # Save new settings
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings_to_save, f, indent=2, ensure_ascii=False)
                
                return True
        
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _merge_settings(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults"""
        merged = defaults.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_settings(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            return self.settings.get(category, {}).get(key, default)
        except:
            return default
    
    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            with self.lock:
                if category not in self.settings:
                    self.settings[category] = {}
                
                self.settings[category][key] = value
                return self.save_settings()
        except Exception as e:
            print(f"Error setting {category}.{key}: {e}")
            return False
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category"""
        return self.settings.get(category, {})
    
    def set_category(self, category: str, settings: Dict[str, Any]) -> bool:
        """Set all settings in a category"""
        try:
            with self.lock:
                self.settings[category] = settings
                return self.save_settings()
        except Exception as e:
            print(f"Error setting category {category}: {e}")
            return False
    
    def reset_to_defaults(self, category: Optional[str] = None) -> bool:
        """Reset settings to defaults"""
        try:
            with self.lock:
                if category:
                    if category in self.default_settings:
                        self.settings[category] = self.default_settings[category].copy()
                else:
                    self.settings = self.default_settings.copy()
                
                return self.save_settings()
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to file"""
        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "app_name": self.app_name,
                "version": "2.0",
                "settings": self.settings
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: str, merge: bool = True) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "settings" in import_data:
                imported_settings = import_data["settings"]
                
                if merge:
                    self.settings = self._merge_settings(self.settings, imported_settings)
                else:
                    self.settings = imported_settings
                
                return self.save_settings()
            
            return False
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
    
    def validate_settings(self) -> Dict[str, list]:
        """Validate settings and return any issues"""
        issues = {
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate monitoring settings
            update_interval = self.get_setting("monitoring", "update_interval")
            if not isinstance(update_interval, int) or update_interval < 500 or update_interval > 60000:
                issues["errors"].append("Update interval must be between 500ms and 60 seconds")
            
            # Validate alert thresholds
            cpu_warning = self.get_setting("alerts", "cpu_threshold_warning")
            cpu_critical = self.get_setting("alerts", "cpu_threshold_critical")
            if not isinstance(cpu_warning, (int, float)) or not isinstance(cpu_critical, (int, float)):
                issues["errors"].append("CPU thresholds must be numeric")
            elif cpu_warning >= cpu_critical:
                issues["warnings"].append("CPU warning threshold should be lower than critical")
            
            # Validate optimization settings
            optimization_interval = self.get_setting("optimization", "optimization_interval")
            if not isinstance(optimization_interval, int) or optimization_interval < 10 or optimization_interval > 300:
                issues["errors"].append("Optimization interval must be between 10 and 300 seconds")
            
            # Validate UI settings
            font_size = self.get_setting("ui", "font_size")
            if not isinstance(font_size, int) or font_size < 8 or font_size > 24:
                issues["warnings"].append("Font size should be between 8 and 24")
            
        except Exception as e:
            issues["errors"].append(f"Validation error: {e}")
        
        return issues
    
    def get_setting_info(self) -> Dict[str, Any]:
        """Get information about all available settings"""
        return {
            "categories": list(self.default_settings.keys()),
            "total_settings": sum(len(category) for category in self.default_settings.values()),
            "file_path": self.settings_file,
            "last_modified": datetime.fromtimestamp(os.path.getmtime(self.settings_file)).isoformat() if os.path.exists(self.settings_file) else None,
            "file_size": os.path.getsize(self.settings_file) if os.path.exists(self.settings_file) else 0
        }

# Global settings manager instance
settings_manager = SettingsManager()
