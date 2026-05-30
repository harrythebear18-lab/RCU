#!/usr/bin/env python3
"""
Frontend Backend Synchronization
Fallback implementation for CPU Monitor compatibility
"""

class SimpleSyncManager:
    """Simple synchronization manager"""
    
    def sync_data(self, data: dict) -> None:
        """Sync data between frontend and backend"""
        pass
    
    def get_sync_data(self) -> dict:
        """Get synchronized data"""
        return {}

def get_frontend_backend_sync():
    """Get frontend backend sync instance"""
    return SimpleSyncManager()

def sync_data(data: dict) -> None:
    """Sync data function"""
    pass
