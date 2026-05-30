#!/usr/bin/env python3
"""
Core Services Integration Helper
Provides dynamic path handling for Core Services directory with spaces
"""

import sys
import os

# Add Core Services to path with proper handling
current_dir = os.path.dirname(os.path.abspath(__file__))
core_services_path = os.path.join(current_dir, '..', 'Core Services')

if core_services_path not in sys.path:
    sys.path.insert(0, core_services_path)

# Now import Core Services
try:
    from event_bus import get_event_bus, EventType, EventPriority
    from config_manager import get_config_manager
    from data_persistence import get_data_persistence
    from unified_monitoring import get_unified_monitoring, AlertSeverity
    from auth_service import get_auth_service
    
    # Export all functions
    __all__ = [
        'get_event_bus', 'EventType', 'EventPriority',
        'get_config_manager',
        'get_data_persistence',
        'get_unified_monitoring', 'AlertSeverity',
        'get_auth_service'
    ]
    
except ImportError as e:
    print(f"Error importing Core Services: {e}")
    print("Make sure Core Services directory exists and contains the required modules")
    
    # Create dummy functions for graceful fallback
    def get_event_bus():
        return None
        
    def get_config_manager():
        return None
        
    def get_data_persistence():
        return None
        
    def get_unified_monitoring():
        return None
        
    def get_auth_service():
        return None
        
    # Create dummy classes
    class EventType:
        pass
        
    class EventPriority:
        pass
        
    class AlertSeverity:
        pass
