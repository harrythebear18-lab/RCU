#!/usr/bin/env python3
"""
Streamlined Homelab System
Inspired by the best features of Homelab Tools, RDMA, and Resource Optimization.
A focused, powerful, and efficient homelab management system.
"""

import os
import sys
import json
import time
import threading
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
import secrets

# Add project paths
current_dir = Path(__file__).parent
homelab_tools_path = Path("C:/Users/htsou/Desktop/Homelab Tools")
rdma_path = Path("C:/Users/htsou/Desktop/RDMA")

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(homelab_tools_path))
sys.path.insert(0, str(rdma_path))

# Core imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Try to import RDMA components
try:
    from ultra_low_latency_userspace import UltraLowLatencyDMA
    RDMA_AVAILABLE = True
except ImportError:
    RDMA_AVAILABLE = False

class ResourceStatus(Enum):
    """Resource status enumeration"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class SystemRole(Enum):
    """System role enumeration"""
    SERVER = "server"
    CLIENT = "client"
    HYBRID = "hybrid"

@dataclass
class Resource:
    """Resource definition"""
    id: str
    name: str
    type: str
    capacity: float
    allocated: float = 0.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    properties: Dict[str, Any] = None
    source_system: str = "unified"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Allocation:
    """Resource allocation definition"""
    id: str
    resource_id: str
    client_id: str
    amount: float
    properties: Dict[str, Any] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    status: str = "active"
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.created_at is None:
            self.created_at = datetime.now()

class StreamlinedHomelabSystem:
    """Streamlined homelab system inspired by Homelab Tools best features"""
    
    def __init__(self):
        self.db_path = current_dir / "streamlined_homelab.db"
        self.settings_file = current_dir / "streamlined_settings.json"
        
        # Setup logging
        self.setup_logging()
        
        # Core components
        self.resources = {}
        self.allocations = {}
        self.clients = {}
        self.events = []
        
        # System configuration
        self.settings = self.load_settings()
        self.role = self.detect_system_role()
        
        # Initialize database
        self.init_database()
        
        # Core services
        self.rdma_controller = None
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Initialize system
        self.initialize_system()
        
        self.logger.info(f"Streamlined Homelab System initialized as {self.role.value}")
    
    def setup_logging(self):
        """Setup logging system"""
        self.logger = logging.getLogger('StreamlinedHomelab')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = current_dir / "streamlined_homelab.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load system settings"""
        default_settings = {
            'system_name': 'Streamlined Homelab',
            'auto_discovery': True,
            'rdma_enabled': True,
            'resource_sharing': True,
            'monitoring_interval': 30,
            'allocation_timeout': 3600,
            'max_clients': 10,
            'security_enabled': True,
            'auto_optimization': True,
            'hardware_optimization': True,
            'network_optimization': True
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save system settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def detect_system_role(self) -> SystemRole:
        """Detect system role based on capabilities"""
        try:
            # Get system information
            cpu_count = psutil.cpu_count() if PSUTIL_AVAILABLE else 4
            memory_gb = psutil.virtual_memory().total / (1024**3) if PSUTIL_AVAILABLE else 8
            
            # Determine role based on resources
            if cpu_count >= 8 and memory_gb >= 16:
                return SystemRole.SERVER
            elif cpu_count >= 4 and memory_gb >= 8:
                return SystemRole.HYBRID
            else:
                return SystemRole.CLIENT
                
        except Exception as e:
            self.logger.error(f"Failed to detect system role: {e}")
            return SystemRole.CLIENT
    
    def init_database(self):
        """Initialize database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                capacity REAL NOT NULL,
                allocated REAL DEFAULT 0,
                status TEXT DEFAULT 'available',
                properties TEXT,
                source_system TEXT DEFAULT 'unified',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocations (
                id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                client_id TEXT NOT NULL,
                amount REAL NOT NULL,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (resource_id) REFERENCES resources (id)
            )
        ''')
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hostname TEXT,
                ip_address TEXT,
                role TEXT DEFAULT 'client',
                status TEXT DEFAULT 'offline',
                last_seen TIMESTAMP,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                source TEXT,
                description TEXT,
                details TEXT,
                priority TEXT DEFAULT 'normal'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_system(self):
        """Initialize system components"""
        try:
            # Initialize RDMA if available
            if RDMA_AVAILABLE and self.settings.get('rdma_enabled', True):
                self.initialize_rdma()
            
            # Initialize resources
            self.initialize_resources()
            
            # Start monitoring
            self.start_monitoring()
            
            self.log_event('system', 'initialization', 'System initialized successfully')
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            self.log_event('system', 'error', f'System initialization failed: {e}')
    
    def initialize_rdma(self):
        """Initialize RDMA controller"""
        try:
            self.rdma_controller = UltraLowLatencyDMA()
            self.log_event('rdma', 'initialization', 'RDMA controller initialized')
        except Exception as e:
            self.logger.error(f"Failed to initialize RDMA: {e}")
            self.log_event('rdma', 'error', f'RDMA initialization failed: {e}')
    
    def initialize_resources(self):
        """Initialize system resources"""
        try:
            # Get system information
            cpu_count = psutil.cpu_count() if PSUTIL_AVAILABLE else 4
            memory_gb = psutil.virtual_memory().total / (1024**3) if PSUTIL_AVAILABLE else 8
            
            # Create RAM resources
            ram_resources = [
                Resource(
                    id='ram_low_latency',
                    name='Low Latency RAM',
                    type='ram',
                    capacity=min(memory_gb * 0.3, 8),
                    properties={
                        'latency_target': '<100ns',
                        'rdma_optimized': True,
                        'priority': 'high'
                    }
                ),
                Resource(
                    id='ram_standard',
                    name='Standard RAM',
                    type='ram',
                    capacity=min(memory_gb * 0.5, 12),
                    properties={
                        'priority': 'medium',
                        'general_purpose': True
                    }
                )
            ]
            
            # Create CPU resources
            cpu_resources = [
                Resource(
                    id='cpu_performance',
                    name='Performance CPU',
                    type='cpu',
                    capacity=max(cpu_count * 0.5, 2),
                    properties={
                        'performance_mode': True,
                        'priority': 'high'
                    }
                ),
                Resource(
                    id='cpu_standard',
                    name='Standard CPU',
                    type='cpu',
                    capacity=max(cpu_count * 0.3, 1),
                    properties={
                        'general_purpose': True,
                        'priority': 'medium'
                    }
                )
            ]
            
            # Create RDMA resources if available
            rdma_resources = []
            if RDMA_AVAILABLE:
                rdma_resources = [
                    Resource(
                        id='rdma_ultra_low_latency',
                        name='Ultra Low Latency RDMA',
                        type='network',
                        capacity=10.0,
                        properties={
                            'latency_ns': '<500',
                            'throughput_gbps': 10,
                            'priority': 'critical'
                        }
                    )
                ]
            
            # Register all resources
            all_resources = ram_resources + cpu_resources + rdma_resources
            
            for resource in all_resources:
                self.register_resource(resource)
            
            self.log_event('resource', 'initialization', f'Initialized {len(all_resources)} resources')
            
        except Exception as e:
            self.logger.error(f"Failed to initialize resources: {e}")
            self.log_event('resource', 'error', f'Resource initialization failed: {e}')
    
    def register_resource(self, resource: Resource) -> bool:
        """Register a resource"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO resources 
                (id, name, type, capacity, allocated, status, properties, source_system, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (resource.id, resource.name, resource.type, resource.capacity,
                  resource.allocated, resource.status.value, json.dumps(resource.properties),
                  resource.source_system, resource.created_at))
            
            conn.commit()
            conn.close()
            
            self.resources[resource.id] = resource
            self.log_event('resource', 'registration', f'Registered resource: {resource.name}')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register resource {resource.id}: {e}")
            return False
    
    def allocate_resource(self, resource_id: str, client_id: str, amount: float, 
                         properties: Dict[str, Any] = None) -> Optional[Allocation]:
        """Allocate a resource to a client"""
        try:
            if resource_id not in self.resources:
                return None
            
            resource = self.resources[resource_id]
            
            # Check availability
            available = resource.capacity - resource.allocated
            if amount > available:
                return None
            
            # Create allocation
            allocation_id = f"alloc_{int(time.time())}_{secrets.token_hex(4)}"
            expires_at = datetime.now() + timedelta(seconds=self.settings.get('allocation_timeout', 3600))
            
            allocation = Allocation(
                id=allocation_id,
                resource_id=resource_id,
                client_id=client_id,
                amount=amount,
                properties=properties or {},
                expires_at=expires_at
            )
            
            # Update resource allocation
            resource.allocated += amount
            if resource.allocated >= resource.capacity:
                resource.status = ResourceStatus.ALLOCATED
            else:
                resource.status = ResourceStatus.BUSY
            
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE resources SET allocated = ?, status = ? WHERE id = ?
            ''', (resource.allocated, resource.status.value, resource_id))
            
            cursor.execute('''
                INSERT INTO allocations 
                (id, resource_id, client_id, amount, properties, expires_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (allocation.id, allocation.resource_id, allocation.client_id,
                  allocation.amount, json.dumps(allocation.properties),
                  allocation.expires_at, allocation.status))
            
            conn.commit()
            conn.close()
            
            self.allocations[allocation.id] = allocation
            self.log_event('resource', 'allocation', f'Allocated {amount} of {resource.name} to {client_id}')
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Failed to allocate resource {resource_id}: {e}")
            return None
    
    def release_resource(self, allocation_id: str) -> bool:
        """Release a resource allocation"""
        try:
            if allocation_id not in self.allocations:
                return False
            
            allocation = self.allocations[allocation_id]
            resource_id = allocation.resource_id
            
            if resource_id not in self.resources:
                return False
            
            resource = self.resources[resource_id]
            
            # Update resource allocation
            resource.allocated -= allocation.amount
            if resource.allocated <= 0:
                resource.allocated = 0
                resource.status = ResourceStatus.AVAILABLE
            else:
                resource.status = ResourceStatus.BUSY
            
            # Update database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE resources SET allocated = ?, status = ? WHERE id = ?
            ''', (resource.allocated, resource.status.value, resource_id))
            
            cursor.execute('DELETE FROM allocations WHERE id = ?', (allocation_id,))
            
            conn.commit()
            conn.close()
            
            # Remove from memory
            del self.allocations[allocation_id]
            
            self.log_event('resource', 'release', f'Released allocation {allocation_id}')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release resource allocation {allocation_id}: {e}")
            return False
    
    def register_client(self, client_id: str, name: str, hostname: str, ip_address: str, 
                       role: str = 'client', properties: Dict[str, Any] = None) -> bool:
        """Register a client"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO clients 
                (id, name, hostname, ip_address, role, status, last_seen, properties)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, name, hostname, ip_address, role, 'online',
                  datetime.now(), json.dumps(properties or {})))
            
            conn.commit()
            conn.close()
            
            self.clients[client_id] = {
                'id': client_id,
                'name': name,
                'hostname': hostname,
                'ip_address': ip_address,
                'role': role,
                'status': 'online',
                'last_seen': datetime.now(),
                'properties': properties or {}
            }
            
            self.log_event('client', 'registration', f'Client registered: {name}')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register client {client_id}: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1) if PSUTIL_AVAILABLE else 0
            memory = psutil.virtual_memory() if PSUTIL_AVAILABLE else None
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'system_name': self.settings.get('system_name', 'Streamlined Homelab'),
                'role': self.role.value,
                'uptime': time.time(),
                'resources': {
                    'total': len(self.resources),
                    'available': len([r for r in self.resources.values() if r.status == ResourceStatus.AVAILABLE]),
                    'allocated': len([r for r in self.resources.values() if r.status == ResourceStatus.ALLOCATED]),
                    'busy': len([r for r in self.resources.values() if r.status == ResourceStatus.BUSY])
                },
                'clients': {
                    'total': len(self.clients),
                    'online': len([c for c in self.clients.values() if c['status'] == 'online']),
                    'offline': len([c for c in self.clients.values() if c['status'] == 'offline'])
                },
                'allocations': {
                    'total': len(self.allocations),
                    'active': len([a for a in self.allocations.values() if a.status == 'active'])
                },
                'system_metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent if memory else 0,
                    'memory_available_gb': memory.available / (1024**3) if memory else 0
                },
                'rdma_enabled': RDMA_AVAILABLE and self.rdma_controller is not None,
                'monitoring_active': self.monitoring_active
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {}
    
    def log_event(self, source: str, event_type: str, description: str, 
                 details: Dict[str, Any] = None, priority: str = 'normal'):
        """Log an event"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (event_type, source, description, details, priority)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, source, description, json.dumps(details or {}), priority))
            
            conn.commit()
            conn.close()
            
            # Add to memory events (keep last 1000)
            self.events.append({
                'timestamp': datetime.now(),
                'source': source,
                'event_type': event_type,
                'description': description,
                'details': details or {},
                'priority': priority
            })
            
            if len(self.events) > 1000:
                self.events = self.events[-1000:]
            
        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")
    
    def start_monitoring(self):
        """Start system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.log_event('system', 'monitoring', 'System monitoring started')
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.log_event('system', 'monitoring', 'System monitoring stopped')
    
    def _monitoring_loop(self):
        """System monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for expired allocations
                self._cleanup_expired_allocations()
                
                # Update client status
                self._update_client_status()
                
                # Update resource status
                self._update_resource_status()
                
                # Sleep for monitoring interval
                time.sleep(self.settings.get('monitoring_interval', 30))
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def _cleanup_expired_allocations(self):
        """Clean up expired allocations"""
        current_time = datetime.now()
        expired_allocations = []
        
        for allocation_id, allocation in self.allocations.items():
            if allocation.expires_at and current_time > allocation.expires_at:
                expired_allocations.append(allocation_id)
        
        for allocation_id in expired_allocations:
            self.release_resource(allocation_id)
            self.log_event('resource', 'cleanup', f'Expired allocation cleaned up: {allocation_id}')
    
    def _update_client_status(self):
        """Update client status based on last seen"""
        try:
            timeout_minutes = 5
            cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
            
            offline_clients = []
            
            for client_id, client in self.clients.items():
                if client['last_seen'] < cutoff_time:
                    client['status'] = 'offline'
                    offline_clients.append(client_id)
            
            # Update database
            if offline_clients:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                for client_id in offline_clients:
                    cursor.execute('UPDATE clients SET status = ?, last_seen = ? WHERE id = ?',
                                 ('offline', datetime.now(), client_id))
                
                conn.commit()
                conn.close()
                
                self.log_event('client', 'status_update', f'Marked {len(offline_clients)} clients as offline')
                
        except Exception as e:
            self.logger.error(f"Failed to update client status: {e}")
    
    def _update_resource_status(self):
        """Update resource status based on allocations"""
        try:
            for resource in self.resources.values():
                if resource.allocated >= resource.capacity:
                    resource.status = ResourceStatus.ALLOCATED
                elif resource.allocated > 0:
                    resource.status = ResourceStatus.BUSY
                else:
                    resource.status = ResourceStatus.AVAILABLE
                
                # Update database
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('UPDATE resources SET allocated = ?, status = ? WHERE id = ?',
                             (resource.allocated, resource.status.value, resource.id))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Failed to update resource status: {e}")

# Global system instance
streamlined_homelab = StreamlinedHomelabSystem()

if __name__ == '__main__':
    # Test the streamlined system
    print("🏠 Testing Streamlined Homelab System")
    
    # Get system status
    status = streamlined_homelab.get_system_status()
    print(f"System Status: {status}")
    
    # Test resource allocation
    allocation = streamlined_homelab.allocate_resource(
        'ram_low_latency',
        'test_client',
        2.0,
        {'test': True}
    )
    
    if allocation:
        print(f"✅ Resource allocated: {allocation.id}")
        
        # Release allocation
        if streamlined_homelab.release_resource(allocation.id):
            print("✅ Resource released")
    
    # Keep running
    try:
        while True:
            time.sleep(60)
            status = streamlined_homelab.get_system_status()
            print(f"🔄 System running... Resources: {status['resources']['total']}, Clients: {status['clients']['total']}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        streamlined_homelab.stop_monitoring()
