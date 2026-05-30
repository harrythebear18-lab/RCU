#!/usr/bin/env python3
"""
Unified Path Manager
Fallback implementation for CPU Monitor compatibility
"""

from pathlib import Path
from typing import Optional, Any

class PathType:
    """Path type constants"""
    CONFIG = "config"
    DATA = "data"
    LOG = "log"
    TEMP = "temp"

def get_unified_path_manager():
    """Get unified path manager instance"""
    class SimplePathManager:
        def get_path(self, path_type: PathType, name: str) -> Path:
            """Get path for given type and name"""
            base_path = Path(__file__).parent
            if path_type == PathType.DATA:
                return base_path / "data" / name
            elif path_type == PathType.CONFIG:
                return base_path / "config" / name
            elif path_type == PathType.LOG:
                return base_path / "logs" / name
            elif path_type == PathType.TEMP:
                return base_path / "temp" / name
            return base_path / name
            
        def ensure_directory(self, path: Path) -> None:
            """Ensure directory exists"""
            path.mkdir(parents=True, exist_ok=True)
    
    return SimplePathManager()

def get_data(key: str, default: Any = None) -> Any:
    """Get data from storage"""
    return default

def set_data(key: str, value: Any) -> None:
    """Set data in storage"""
    pass
