#!/usr/bin/env python3
"""
Frontend-Backend Data Synchronization
Ensures frontend and backend respect the same paths and data flow
"""

import logging
import time
import json
import threading
import queue
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib

# Import unified path manager
try:
    from unified_path_manager import get_unified_path_manager, PathType, get_data, set_data, get_path
    from frontend_backend_mixer import get_frontend_backend_mixer, MessageType, MixerMessage, ComponentType
    SYNCHRONIZATION_AVAILABLE = True
except ImportError as e:
    logging.getLogger("FrontendBackendSynchronization").warning(f"Synchronization components not available: {e}")
    SYNCHRONIZATION_AVAILABLE = False

class SyncOperation(Enum):
    """Synchronization operations"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    SYNC_ALL = "sync_all"

class DataConflictResolution(Enum):
    """Data conflict resolution strategies"""
    FRONTEND_WINS = "frontend_wins"
    BACKEND_WINS = "backend_wins"
    MERGE = "merge"
    TIMESTAMP_WINS = "timestamp_wins"
    MANUAL_RESOLUTION = "manual_resolution"

@dataclass
class SyncEvent:
    """Synchronization event"""
    operation: SyncOperation
    path_type: PathType
    data_key: str
    data: Any
    timestamp: float
    source: str  # "frontend" or "backend"
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DataState:
    """Data state tracking"""
    path_type: PathType
    data_key: str
    checksum: str
    timestamp: float
    source: str
    size: int
    metadata: Dict[str, Any]

class FrontendBackendSynchronization:
    """Manages synchronization between frontend and backend"""
    
    def __init__(self):
        self.logger = logging.getLogger("FrontendBackendSynchronization")
        self.path_manager = get_unified_path_manager() if SYNCHRONIZATION_AVAILABLE else None
        self.mixer = get_frontend_backend_mixer() if SYNCHRONIZATION_AVAILABLE else None
        
        # Synchronization state
        self.data_states: Dict[str, DataState] = {}  # key: f"{path_type}_{data_key}"
        self.sync_queue = queue.Queue()
        self.conflict_queue = queue.Queue()
        self.is_syncing = False
        self.sync_thread = None
        self.conflict_thread = None
        
        # Configuration
        self.sync_interval = 5.0  # seconds
        self.conflict_resolution = DataConflictResolution.TIMESTAMP_WINS
        self.auto_sync = True
        self.max_retry_attempts = 3
        
        # Statistics
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'conflicts_resolved': 0,
            'last_sync_time': None
        }
        
        self._initialize_synchronization()
    
    def _initialize_synchronization(self):
        """Initialize synchronization system"""
        if not SYNCHRONIZATION_AVAILABLE:
            self.logger.error("Synchronization components not available")
            return
        
        try:
            # Register with mixer for data updates
            if self.mixer:
                # Subscribe to mixer events
                self.mixer.subscribe(MessageType.DATA_UPDATE, self._handle_data_update)
                self.mixer.subscribe(MessageType.CONFIG_CHANGE, self._handle_config_change)
            
            # Start synchronization threads
            self._start_sync_threads()
            
            # Initialize data states
            self._initialize_data_states()
            
            self.logger.info("Frontend-backend synchronization initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize synchronization: {e}")
    
    def _start_sync_threads(self):
        """Start synchronization threads"""
        if self.auto_sync:
            self.is_syncing = True
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            
            self.conflict_thread = threading.Thread(target=self._conflict_resolution_loop, daemon=True)
            self.conflict_thread.start()
    
    def _initialize_data_states(self):
        """Initialize data states for existing data"""
        if not self.path_manager:
            return
        
        try:
            # Initialize core data types
            core_types = [
                PathType.SYSTEM_DATA,
                PathType.USER_DATA,
                PathType.DATA_STORAGE,
                PathType.CONFIG_FILES
            ]
            
            for path_type in core_types:
                self._sync_path_type(path_type)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize data states: {e}")
    
    def sync_data(self, path_type: PathType, data_key: str, data: Any, source: str = "backend") -> bool:
        """Synchronize data between frontend and backend"""
        if not SYNCHRONIZATION_AVAILABLE:
            return False
        
        try:
            # Create sync event
            event = SyncEvent(
                operation=SyncOperation.UPDATE,
                path_type=path_type,
                data_key=data_key,
                data=data,
                timestamp=time.time(),
                source=source,
                checksum=self._calculate_checksum(data)
            )
            
            # Check for conflicts
            conflict = self._check_conflict(event)
            if conflict:
                self.conflict_queue.put((event, conflict))
                return False
            
            # Sync to unified path manager
            success = set_data(path_type, data_key, data)
            if success:
                # Update data state
                self._update_data_state(event)
                
                # Broadcast to other side
                self._broadcast_sync_event(event)
                
                # Update statistics
                self.sync_stats['total_syncs'] += 1
                self.sync_stats['successful_syncs'] += 1
                self.sync_stats['last_sync_time'] = time.time()
                
                self.logger.debug(f"Synced {path_type.value}/{data_key} from {source}")
                return True
            else:
                self.sync_stats['total_syncs'] += 1
                self.sync_stats['failed_syncs'] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to sync data: {e}")
            self.sync_stats['total_syncs'] += 1
            self.sync_stats['failed_syncs'] += 1
            return False
    
    def _check_conflict(self, event: SyncEvent) -> Optional[DataState]:
        """Check for data conflicts"""
        state_key = f"{event.path_type.value}_{event.data_key}"
        existing_state = self.data_states.get(state_key)
        
        if not existing_state:
            return None
        
        # Check if data is different
        if existing_state.checksum != event.checksum:
            # Check timestamps for conflict resolution
            if self.conflict_resolution == DataConflictResolution.TIMESTAMP_WINS:
                if event.timestamp > existing_state.timestamp:
                    return None  # No conflict, newer data wins
                else:
                    return existing_state  # Conflict, older data
            else:
                return existing_state  # Conflict detected
        
        return None
    
    def _resolve_conflict(self, event: SyncEvent, conflict_state: DataState) -> bool:
        """Resolve data conflicts"""
        try:
            if self.conflict_resolution == DataConflictResolution.TIMESTAMP_WINS:
                # Use newer data
                if event.timestamp > conflict_state.timestamp:
                    return self._apply_sync_event(event)
                else:
                    return True  # Keep existing data
            
            elif self.conflict_resolution == DataConflictResolution.FRONTEND_WINS:
                if event.source == "frontend":
                    return self._apply_sync_event(event)
                else:
                    return True
            
            elif self.conflict_resolution == DataConflictResolution.BACKEND_WINS:
                if event.source == "backend":
                    return self._apply_sync_event(event)
                else:
                    return True
            
            elif self.conflict_resolution == DataConflictResolution.MERGE:
                # Attempt to merge data (simplified)
                return self._merge_data(event, conflict_state)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resolve conflict: {e}")
            return False
    
    def _merge_data(self, event: SyncEvent, conflict_state: DataState) -> bool:
        """Merge conflicting data"""
        try:
            # Simple merge strategy for dictionaries
            if isinstance(event.data, dict) and isinstance(conflict_state, DataState):
                # Get existing data
                existing_data = get_data(event.path_type, event.data_key)
                if isinstance(existing_data, dict):
                    # Merge dictionaries
                    merged_data = {**existing_data, **event.data}
                    
                    # Apply merged data
                    merged_event = SyncEvent(
                        operation=SyncOperation.UPDATE,
                        path_type=event.path_type,
                        data_key=event.data_key,
                        data=merged_data,
                        timestamp=time.time(),
                        source="merged",
                        checksum=self._calculate_checksum(merged_data)
                    )
                    
                    return self._apply_sync_event(merged_event)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to merge data: {e}")
            return False
    
    def _apply_sync_event(self, event: SyncEvent) -> bool:
        """Apply synchronization event"""
        try:
            success = set_data(event.path_type, event.data_key, event.data)
            if success:
                self._update_data_state(event)
                self._broadcast_sync_event(event)
                
                # Update statistics
                self.sync_stats['conflicts_resolved'] += 1
                
                self.logger.info(f"Resolved conflict for {event.path_type.value}/{event.data_key}")
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply sync event: {e}")
        
        return False
    
    def _update_data_state(self, event: SyncEvent):
        """Update data state tracking"""
        state_key = f"{event.path_type.value}_{event.data_key}"
        
        state = DataState(
            path_type=event.path_type,
            data_key=event.data_key,
            checksum=event.checksum,
            timestamp=event.timestamp,
            source=event.source,
            size=len(str(event.data)) if event.data else 0,
            metadata=event.metadata or {}
        )
        
        self.data_states[state_key] = state
    
    def _broadcast_sync_event(self, event: SyncEvent):
        """Broadcast sync event to frontend/backend"""
        if not self.mixer:
            return
        
        try:
            # Create message for broadcasting
            message_data = {
                'operation': event.operation.value,
                'path_type': event.path_type.value,
                'data_key': event.data_key,
                'data': event.data,
                'timestamp': event.timestamp,
                'source': event.source,
                'checksum': event.checksum
            }
            
            # Broadcast to opposite side
            if event.source == "frontend":
                target = ComponentType.BACKEND_API
            else:
                target = ComponentType.FRONTEND_GUI
            
            message = MixerMessage(
                message_type=MessageType.DATA_UPDATE,
                source=ComponentType.BACKEND_API if event.source == "frontend" else ComponentType.FRONTEND_GUI,
                target=target,
                timestamp=event.timestamp,
                data=message_data
            )
            
            self.mixer.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast sync event: {e}")
    
    def _sync_loop(self):
        """Main synchronization loop"""
        while self.is_syncing:
            try:
                # Process sync queue
                try:
                    event = self.sync_queue.get(timeout=1.0)
                    self._process_sync_event(event)
                except queue.Empty:
                    continue
                
                # Periodic sync check
                time.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                time.sleep(1.0)
    
    def _conflict_resolution_loop(self):
        """Conflict resolution loop"""
        while self.is_syncing:
            try:
                # Process conflict queue
                try:
                    event, conflict = self.conflict_queue.get(timeout=1.0)
                    self._resolve_conflict(event, conflict)
                except queue.Empty:
                    continue
                
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error in conflict resolution loop: {e}")
                time.sleep(1.0)
    
    def _process_sync_event(self, event: SyncEvent):
        """Process synchronization event"""
        try:
            self.sync_data(event.path_type, event.data_key, event.data, event.source)
        except Exception as e:
            self.logger.error(f"Failed to process sync event: {e}")
    
    def _sync_path_type(self, path_type: PathType):
        """Synchronize all data for a path type"""
        if not self.path_manager:
            return
        
        try:
            # Get all data for path type
            data = get_data(path_type)
            if data and isinstance(data, dict):
                for data_key, data_value in data.items():
                    self.sync_data(path_type, data_key, data_value, "backend")
            
        except Exception as e:
            self.logger.error(f"Failed to sync path type {path_type}: {e}")
    
    def _handle_data_update(self, message):
        """Handle data update from mixer"""
        try:
            data = message.data
            path_type = PathType(data.get('path_type'))
            data_key = data.get('data_key')
            data_value = data.get('data')
            source = data.get('source', 'frontend')
            
            if path_type and data_key and data_value is not None:
                self.sync_data(path_type, data_key, data_value, source)
                
        except Exception as e:
            self.logger.error(f"Failed to handle data update: {e}")
    
    def _handle_config_change(self, message):
        """Handle configuration change"""
        try:
            # Re-sync configuration data
            self._sync_path_type(PathType.CONFIG_FILES)
        except Exception as e:
            self.logger.error(f"Failed to handle config change: {e}")
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data"""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except:
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def force_sync_all(self) -> bool:
        """Force synchronization of all data"""
        try:
            if not self.path_manager:
                return False
            
            # Sync all path types
            path_types = [
                PathType.SYSTEM_DATA,
                PathType.USER_DATA,
                PathType.DATA_STORAGE,
                PathType.CONFIG_FILES
            ]
            
            success_count = 0
            for path_type in path_types:
                try:
                    self._sync_path_type(path_type)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to sync {path_type}: {e}")
            
            return success_count == len(path_types)
            
        except Exception as e:
            self.logger.error(f"Failed to force sync all: {e}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        return {
            'is_syncing': self.is_syncing,
            'sync_queue_size': self.sync_queue.qsize(),
            'conflict_queue_size': self.conflict_queue.qsize(),
            'data_states_count': len(self.data_states),
            'sync_stats': self.sync_stats.copy(),
            'conflict_resolution': self.conflict_resolution.value,
            'sync_interval': self.sync_interval,
            'auto_sync': self.auto_sync
        }
    
    def set_conflict_resolution(self, resolution: DataConflictResolution):
        """Set conflict resolution strategy"""
        self.conflict_resolution = resolution
        self.logger.info(f"Conflict resolution set to: {resolution.value}")
    
    def stop_synchronization(self):
        """Stop synchronization"""
        self.is_syncing = False
        
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        if self.conflict_thread:
            self.conflict_thread.join(timeout=2)
        
        self.logger.info("Frontend-backend synchronization stopped")

# Global instance
_frontend_backend_sync = None

def get_frontend_backend_sync() -> FrontendBackendSynchronization:
    """Get global frontend-backend synchronization instance"""
    global _frontend_backend_sync
    if _frontend_backend_sync is None:
        _frontend_backend_sync = FrontendBackendSynchronization()
    return _frontend_backend_sync

def sync_data(path_type: PathType, data_key: str, data: Any, source: str = "backend") -> bool:
    """Synchronize data between frontend and backend"""
    sync = get_frontend_backend_sync()
    return sync.sync_data(path_type, data_key, data, source)

def force_sync_all() -> bool:
    """Force synchronization of all data"""
    sync = get_frontend_backend_sync()
    return sync.force_sync_all()

def get_sync_status() -> Dict[str, Any]:
    """Get synchronization status"""
    sync = get_frontend_backend_sync()
    return sync.get_sync_status()

def set_conflict_resolution(resolution: DataConflictResolution):
    """Set conflict resolution strategy"""
    sync = get_frontend_backend_sync()
    sync.set_conflict_resolution(resolution)
