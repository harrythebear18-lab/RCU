#!/usr/bin/env python3
"""
Unified Homelab Integration System
Blends Homelab Tools, RDMA, and Windows 11 Resource Optimization into a cohesive ecosystem.
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import sqlite3

# Add all three project paths
current_dir = Path(__file__).parent
homelab_tools_path = Path("C:/Users/htsou/Desktop/Homelab Tools")
rdma_path = Path("C:/Users/htsou/Desktop/RDMA")
ram_clean_path = Path("C:/Users/htsou/Desktop/Ram clean up")

# Add to sys.path for imports
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(homelab_tools_path))
sys.path.insert(0, str(rdma_path))
sys.path.insert(0, str(ram_clean_path))

# Import from all three projects
try:
    # From Homelab Tools
    from homelab_launcher import HomelabLauncher
    from Auto_RAM_Connect import AutoRAMConnect
    HOMELAB_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Homelab Tools import error: {e}")
    HOMELAB_TOOLS_AVAILABLE = False

try:
    # From RDMA
    from ultra_low_latency_userspace import UltraLowLatencyDMA
    from monitoring_system import MonitoringSystem
    RDMA_AVAILABLE = True
except ImportError as e:
    print(f"RDMA import error: {e}")
    RDMA_AVAILABLE = False

try:
    # From Ram clean up
    from win10_homelab_server import Windows10HomelabServer
    from win11_homelab_client import Windows11HomelabClient
    from rdma_integration import rdma_integration
    from resource_optimizer import ResourceOptimizer
    RAM_CLEAN_AVAILABLE = True
except ImportError as e:
    print(f"Ram clean up import error: {e}")
    RAM_CLEAN_AVAILABLE = False

class UnifiedHomelabSystem:
    """Unified system that integrates all three homelab projects"""
    
    def __init__(self):
        self.db_path = os.path.join(current_dir, 'unified_homelab.db')
        self.settings_file = os.path.join(current_dir, 'unified_settings.json')
        
        # Setup logging
        self.setup_logging()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Component status
        self.components = {
            'homelab_tools': {
                'available': HOMELAB_TOOLS_AVAILABLE,
                'launcher': None,
                'ram_connect': None,
                'status': 'stopped'
            },
            'rdma': {
                'available': RDMA_AVAILABLE,
                'dma_controller': None,
                'monitoring': None,
                'status': 'stopped'
            },
            'resource_optimizer': {
                'available': RAM_CLEAN_AVAILABLE,
                'server': None,
                'client': None,
                'optimizer': None,
                'status': 'stopped'
            }
        }
        
        # Unified resource management
        self.resource_pools = {}
        self.active_allocations = {}
        self.connected_clients = {}
        
        # Initialize components
        self.initialize_components()
        
        # Start monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()
    
    def setup_logging(self):
        """Setup unified logging"""
        self.logger = logging.getLogger('UnifiedHomelab')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(current_dir, 'unified_homelab.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load unified settings"""
        default_settings = {
            'unified_mode': True,
            'auto_start_components': True,
            'resource_sharing_enabled': True,
            'rdma_optimization': True,
            'performance_monitoring': True,
            'unified_dashboard': True,
            'cross_project_integration': True,
            'auto_discovery': True,
            'load_balancing': True,
            'security_level': 'high',
            'monitoring_interval': 30,
            'backup_interval': 3600
        }
        
        try:
            if os.path.exists(self.settings_file):
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
        """Save unified settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def init_database(self):
        """Initialize unified database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Components table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT,
                status TEXT DEFAULT 'stopped',
                last_start TIMESTAMP,
                last_stop TIMESTAMP,
                config TEXT
            )
        ''')
        
        # Unified resource pools table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unified_resource_pools (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                capacity REAL,
                allocated REAL DEFAULT 0,
                source_project TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cross-project allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_project_allocations (
                id TEXT PRIMARY KEY,
                client_project TEXT,
                client_id TEXT,
                resource_project TEXT,
                resource_id TEXT,
                amount REAL,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Integration events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_project TEXT,
                target_project TEXT,
                event_type TEXT,
                description TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_components(self):
        """Initialize all three project components"""
        self.logger.info("Initializing unified homelab components...")
        
        # Initialize Homelab Tools components
        if HOMELAB_TOOLS_AVAILABLE:
            self.initialize_homelab_tools()
        
        # Initialize RDMA components
        if RDMA_AVAILABLE:
            self.initialize_rdma()
        
        # Initialize Resource Optimizer components
        if RAM_CLEAN_AVAILABLE:
            self.initialize_resource_optimizer()
        
        # Create unified resource pools
        self.create_unified_resource_pools()
        
        self.logger.info("Component initialization complete")
    
    def initialize_homelab_tools(self):
        """Initialize Homelab Tools components"""
        try:
            # Initialize launcher
            self.components['homelab_tools']['launcher'] = HomelabLauncher()
            self.components['homelab_tools']['status'] = 'initialized'
            
            # Initialize RAM Connect
            self.components['homelab_tools']['ram_connect'] = AutoRAMConnect()
            
            self.logger.info("Homelab Tools components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Homelab Tools: {e}")
            self.components['homelab_tools']['status'] = 'error'
    
    def initialize_rdma(self):
        """Initialize RDMA components"""
        try:
            # Initialize DMA controller
            self.components['rdma']['dma_controller'] = UltraLowLatencyDMA()
            
            # Initialize monitoring system
            self.components['rdma']['monitoring'] = MonitoringSystem()
            self.components['rdma']['monitoring'].start_monitoring()
            
            self.components['rdma']['status'] = 'initialized'
            
            self.logger.info("RDMA components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RDMA: {e}")
            self.components['rdma']['status'] = 'error'
    
    def initialize_resource_optimizer(self):
        """Initialize Resource Optimizer components"""
        try:
            # Initialize Windows 10 server
            self.components['resource_optimizer']['server'] = Windows10HomelabServer()
            
            # Initialize Windows 11 client
            self.components['resource_optimizer']['client'] = Windows11HomelabClient()
            
            # Initialize resource optimizer
            self.components['resource_optimizer']['optimizer'] = ResourceOptimizer()
            
            self.components['resource_optimizer']['status'] = 'initialized'
            
            self.logger.info("Resource Optimizer components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Resource Optimizer: {e}")
            self.components['resource_optimizer']['status'] = 'error'
    
    def create_unified_resource_pools(self):
        """Create unified resource pools from all projects"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create RAM resource pools
            ram_pools = [
                {
                    'id': 'unified_ram_low_latency',
                    'name': 'Unified Low Latency RAM',
                    'type': 'ram',
                    'capacity': 8.0,
                    'source_project': 'all',
                    'properties': {
                        'latency_target': '<100ns',
                        'rdma_optimized': True,
                        'cross_project': True
                    }
                },
                {
                    'id': 'unified_ram_high_capacity',
                    'name': 'Unified High Capacity RAM',
                    'type': 'ram',
                    'capacity': 16.0,
                    'source_project': 'all',
                    'properties': {
                        'capacity_priority': True,
                        'load_balanced': True,
                        'cross_project': True
                    }
                }
            ]
            
            # Create GPU resource pools
            gpu_pools = [
                {
                    'id': 'unified_gpu_rdma_optimized',
                    'name': 'Unified RDMA Optimized GPU',
                    'type': 'gpu',
                    'capacity': 12.0,
                    'source_project': 'rdma+resource_optimizer',
                    'properties': {
                        'rdma_enabled': True,
                        'low_latency': True,
                        'cross_project': True
                    }
                }
            ]
            
            # Create CPU resource pools
            cpu_pools = [
                {
                    'id': 'unified_cpu_performance',
                    'name': 'Unified Performance CPU',
                    'type': 'cpu',
                    'capacity': 8.0,
                    'source_project': 'resource_optimizer',
                    'properties': {
                        'performance_mode': True,
                        'cross_project': True
                    }
                }
            ]
            
            # Create network resource pools
            network_pools = [
                {
                    'id': 'unified_network_rdma',
                    'name': 'Unified RDMA Network',
                    'type': 'network',
                    'capacity': 10.0,
                    'source_project': 'rdma',
                    'properties': {
                        'rdma_enabled': True,
                        'ultra_low_latency': True,
                        'cross_project': True
                    }
                }
            ]
            
            # Insert all pools
            all_pools = ram_pools + gpu_pools + cpu_pools + network_pools
            
            for pool in all_pools:
                cursor.execute('''
                    INSERT OR REPLACE INTO unified_resource_pools 
                    (id, name, type, capacity, source_project, properties)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (pool['id'], pool['name'], pool['type'], pool['capacity'],
                      pool['source_project'], json.dumps(pool['properties'])))
            
            conn.commit()
            conn.close()
            
            self.resource_pools = {pool['id']: pool for pool in all_pools}
            
            self.logger.info(f"Created {len(all_pools)} unified resource pools")
            
        except Exception as e:
            self.logger.error(f"Failed to create unified resource pools: {e}")
    
    def start_all_components(self) -> bool:
        """Start all components in the correct order"""
        try:
            self.logger.info("Starting unified homelab system...")
            
            # Step 1: Start Resource Optimizer (server)
            if RAM_CLEAN_AVAILABLE and self.components['resource_optimizer']['server']:
                self.logger.info("Starting Resource Optimizer server...")
                # Start server in background thread
                server_thread = threading.Thread(
                    target=self.components['resource_optimizer']['server'].run,
                    daemon=True
                )
                server_thread.start()
                self.components['resource_optimizer']['status'] = 'running'
                time.sleep(2)  # Give server time to start
            
            # Step 2: Start RDMA services
            if RDMA_AVAILABLE and self.components['rdma']['dma_controller']:
                self.logger.info("Starting RDMA services...")
                # RDMA services are already initialized
                self.components['rdma']['status'] = 'running'
            
            # Step 3: Start Resource Optimizer client
            if RAM_CLEAN_AVAILABLE and self.components['resource_optimizer']['client']:
                self.logger.info("Starting Resource Optimizer client...")
                if self.components['resource_optimizer']['client'].start_client():
                    self.components['resource_optimizer']['status'] = 'running'
                else:
                    self.logger.warning("Failed to start Resource Optimizer client")
            
            # Step 4: Start Homelab Tools
            if HOMELAB_TOOLS_AVAILABLE:
                self.logger.info("Starting Homelab Tools...")
                # Homelab Tools components are GUI-based, so we just mark them as ready
                self.components['homelab_tools']['status'] = 'ready'
            
            # Log integration event
            self.log_integration_event('system', 'system', 'start', 
                                    'Unified homelab system started', 
                                    {'components': list(self.components.keys())})
            
            self.logger.info("Unified homelab system started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start unified system: {e}")
            return False
    
    def stop_all_components(self):
        """Stop all components gracefully"""
        try:
            self.logger.info("Stopping unified homelab system...")
            
            # Stop Resource Optimizer client
            if RAM_CLEAN_AVAILABLE and self.components['resource_optimizer']['client']:
                self.components['resource_optimizer']['client'].stop_client()
            
            # Stop RDMA services
            if RDMA_AVAILABLE and self.components['rdma']['monitoring']:
                self.components['rdma']['monitoring'].stop_monitoring()
            
            # Stop monitoring
            self.stop_monitoring()
            
            # Log integration event
            self.log_integration_event('system', 'system', 'stop', 
                                    'Unified homelab system stopped', 
                                    {'components': list(self.components.keys())})
            
            self.logger.info("Unified homelab system stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop unified system: {e}")
    
    def allocate_unified_resource(self, pool_id: str, client_id: str, amount: float, 
                                properties: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Allocate resource from unified pools"""
        try:
            if pool_id not in self.resource_pools:
                return None
            
            pool = self.resource_pools[pool_id]
            
            # Check availability
            allocated = sum(a['amount'] for a in self.active_allocations.values() 
                           if a['resource_id'] == pool_id)
            available = pool['capacity'] - allocated
            
            if amount > available:
                return None
            
            # Create allocation
            allocation_id = f"unified_alloc_{int(time.time())}_{hash(client_id) % 10000}"
            expires_at = datetime.now() + timedelta(hours=2)
            
            allocation = {
                'allocation_id': allocation_id,
                'resource_id': pool_id,
                'client_id': client_id,
                'amount': amount,
                'properties': properties or {},
                'expires_at': expires_at.isoformat(),
                'status': 'active',
                'source_project': pool['source_project']
            }
            
            # Store allocation
            self.active_allocations[allocation_id] = allocation
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cross_project_allocations 
                (id, client_project, client_id, resource_project, resource_id, 
                 amount, properties, expires_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (allocation_id, 'unified', client_id, pool['source_project'], 
                  pool_id, amount, json.dumps(properties or {}), 
                  expires_at.isoformat(), 'active'))
            
            conn.commit()
            conn.close()
            
            # Log integration event
            self.log_integration_event('resource', pool['source_project'], 'allocate',
                                    f"Allocated {amount} from {pool_id}",
                                    {'allocation_id': allocation_id, 'client_id': client_id})
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Failed to allocate unified resource: {e}")
            return None
    
    def release_unified_resource(self, allocation_id: str) -> bool:
        """Release unified resource allocation"""
        try:
            if allocation_id not in self.active_allocations:
                return False
            
            allocation = self.active_allocations[allocation_id]
            
            # Remove from active allocations
            del self.active_allocations[allocation_id]
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cross_project_allocations WHERE id = ?', (allocation_id,))
            
            conn.commit()
            conn.close()
            
            # Log integration event
            self.log_integration_event('resource', allocation.get('source_project', 'unknown'), 'release',
                                    f"Released allocation {allocation_id}",
                                    {'allocation_id': allocation_id})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release unified resource: {e}")
            return False
    
    def get_unified_status(self) -> Dict[str, Any]:
        """Get unified system status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'components': {
                name: {
                    'available': comp['available'],
                    'status': comp['status']
                }
                for name, comp in self.components.items()
            },
            'resource_pools': len(self.resource_pools),
            'active_allocations': len(self.active_allocations),
            'connected_clients': len(self.connected_clients),
            'settings': self.settings
        }
    
    def log_integration_event(self, source_project: str, target_project: str, 
                            event_type: str, description: str, details: Dict[str, Any] = None):
        """Log cross-project integration events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO integration_events 
                (source_project, target_project, event_type, description, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (source_project, target_project, event_type, description, 
                  json.dumps(details or {})))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to log integration event: {e}")
    
    def start_monitoring(self):
        """Start unified monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Unified monitoring started")
    
    def stop_monitoring(self):
        """Stop unified monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Unified monitoring stopped")
    
    def _monitoring_loop(self):
        """Unified monitoring loop"""
        while self.monitoring_active:
            try:
                # Monitor component health
                self._monitor_component_health()
                
                # Monitor resource utilization
                self._monitor_resource_utilization()
                
                # Clean up expired allocations
                self._cleanup_expired_allocations()
                
                # Sleep for monitoring interval
                time.sleep(self.settings.get('monitoring_interval', 30))
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def _monitor_component_health(self):
        """Monitor health of all components"""
        for name, component in self.components.items():
            try:
                if name == 'resource_optimizer' and component.get('client'):
                    # Check client connection
                    if component['client'].status.value != 'connected':
                        self.logger.warning(f"Resource Optimizer client disconnected")
                        component['status'] = 'disconnected'
                
                elif name == 'rdma' and component.get('monitoring'):
                    # Check RDMA monitoring
                    health = component['monitoring'].get_health_status()
                    if not health.get('healthy', True):
                        self.logger.warning(f"RDMA monitoring unhealthy: {health}")
                        component['status'] = 'unhealthy'
                
            except Exception as e:
                self.logger.error(f"Error monitoring component {name}: {e}")
    
    def _monitor_resource_utilization(self):
        """Monitor resource utilization"""
        try:
            for pool_id, pool in self.resource_pools.items():
                allocated = sum(a['amount'] for a in self.active_allocations.values() 
                               if a['resource_id'] == pool_id)
                utilization = (allocated / pool['capacity']) * 100 if pool['capacity'] > 0 else 0
                
                if utilization > 90:
                    self.logger.warning(f"High utilization for {pool_id}: {utilization:.1f}%")
                
        except Exception as e:
            self.logger.error(f"Error monitoring resource utilization: {e}")
    
    def _cleanup_expired_allocations(self):
        """Clean up expired allocations"""
        current_time = datetime.now()
        expired_allocations = []
        
        for allocation_id, allocation in self.active_allocations.items():
            expires_at = datetime.fromisoformat(allocation['expires_at'])
            if current_time > expires_at:
                expired_allocations.append(allocation_id)
        
        for allocation_id in expired_allocations:
            self.release_unified_resource(allocation_id)
            self.logger.info(f"Cleaned up expired allocation: {allocation_id}")

# Global unified system instance
unified_homelab = UnifiedHomelabSystem()

if __name__ == '__main__':
    # Test unified system
    print("🔗 Testing Unified Homelab Integration")
    
    # Get status
    status = unified_homelab.get_unified_status()
    print(f"Status: {status}")
    
    # Start all components
    if unified_homelab.start_all_components():
        print("✅ Unified system started successfully")
        
        # Test resource allocation
        allocation = unified_homelab.allocate_unified_resource(
            'unified_ram_low_latency',
            'test_client',
            2.0,
            {'test': True}
        )
        
        if allocation:
            print(f"✅ Resource allocated: {allocation['allocation_id']}")
            
            # Release allocation
            if unified_homelab.release_unified_resource(allocation['allocation_id']):
                print("✅ Resource released")
        
        # Keep running
        try:
            while True:
                time.sleep(60)
                status = unified_homelab.get_unified_status()
                print(f"🔄 System running... Components: {len([c for c in status['components'].values() if c['available']])}")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            unified_homelab.stop_all_components()
    else:
        print("❌ Failed to start unified system")
