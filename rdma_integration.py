#!/usr/bin/env python3
"""
RDMA Integration for Windows 10 Homelab Server
Integrates the existing RDMA application with the homelab resource management system.
"""

import os
import sys
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import logging
from enum import Enum

# Add RDMA directory to path
rdma_path = os.path.join(os.path.dirname(__file__), '..', 'RDMA')
if os.path.exists(rdma_path):
    sys.path.insert(0, rdma_path)

# Try to import RDMA components
try:
    from ultra_low_latency_userspace import UltraLowLatencyDMA
    from monitoring_system import MonitoringSystem
    from rdma_rest_api import app as rdma_api
    RDMA_AVAILABLE = True
    print("[OK] RDMA components imported successfully")
except ImportError as e:
    RDMA_AVAILABLE = False
    # Handle specific Python 3.13 compatibility issues gracefully
    if "MimeText" in str(e):
        print("[WARNING] RDMA components not available: Python 3.13 compatibility issue")
    else:
        print(f"[WARNING] RDMA components not available: {e}")
    
    # Create dummy classes to prevent import errors
    class UltraLowLatencyDMA:
        def __init__(self):
            pass
        def start(self):
            return False
        def stop(self):
            return False
    
    class MonitoringSystem:
        def __init__(self):
            pass
        def get_metrics(self):
            return {}
        def start_monitoring(self):
            return False
    
    # Create dummy Flask app
    from flask import Flask
    rdma_api = Flask('rdma_api')

class RDMAStatus(Enum):
    """RDMA service status"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class RDMAIntegration:
    """Integration layer for RDMA application with homelab server"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'homelab_server.db')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'rdma_settings.json')
        
        # Setup logging
        self.logger = logging.getLogger('RDMAIntegration')
        self.logger.setLevel(logging.INFO)
        
        # Create log handler
        log_file = os.path.join(os.path.dirname(__file__), 'rdma_integration.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # RDMA state
        self.status = RDMAStatus.STOPPED
        self.dma_controller = None
        self.monitoring_system = None
        self.rdma_api_process = None
        self.rdma_api_thread = None
        
        # Performance metrics
        self.performance_metrics = {
            'latency_ns': 0,
            'throughput_mbps': 0,
            'cpu_usage': 0,
            'memory_usage': 0,
            'active_connections': 0,
            'total_transfers': 0,
            'errors': 0
        }
        
        # Resource pools
        self.rdma_pools = {}
        
        # Load settings
        self.load_settings()
        
        # Initialize RDMA resources
        self.initialize_rdma_resources()
        
        # Start monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load RDMA integration settings"""
        default_settings = {
            'rdma_enabled': True,
            'auto_start': False,
            'max_latency_ns': 1000,  # 1 microsecond
            'min_throughput_mbps': 1000,  # 1 Gbps
            'max_connections': 10,
            'resource_pool_size_gb': 4,
            'enable_monitoring': True,
            'monitoring_interval': 5,
            'api_port': 5001,
            'enable_fault_tolerance': True,
            'enable_security': True
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
            self.logger.error(f"Failed to load RDMA settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save RDMA integration settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save RDMA settings: {e}")
            return False
    
    def initialize_rdma_resources(self):
        """Initialize RDMA resource pools for homelab"""
        try:
            if not RDMA_AVAILABLE:
                self.logger.warning("RDMA components not available, creating mock resources")
                self.create_mock_rdma_resources()
                return
            
            # Create RDMA resource pools
            self.rdma_pools = {
                'rdma_low_latency': {
                    'id': 'win10_rdma_low_latency',
                    'name': 'Win10 RDMA Low Latency Pool',
                    'type': 'rdma',
                    'capacity': 4.0,  # GB equivalent
                    'allocated': 0,
                    'properties': {
                        'pool_type': 'low_latency',
                        'max_latency_ns': 500,
                        'min_throughput_mbps': 2000,
                        'priority': 'high',
                        'features': ['ultra_low_latency', 'kernel_bypass', 'hardware_timestamping']
                    }
                },
                'rdma_high_throughput': {
                    'id': 'win10_rdma_high_throughput',
                    'name': 'Win10 RDMA High Throughput Pool',
                    'type': 'rdma',
                    'capacity': 8.0,  # GB equivalent
                    'allocated': 0,
                    'properties': {
                        'pool_type': 'high_throughput',
                        'max_latency_ns': 2000,
                        'min_throughput_mbps': 10000,
                        'priority': 'medium',
                        'features': ['high_throughput', 'zero_copy', 'scatter_gather']
                    }
                },
                'rdma_balanced': {
                    'id': 'win10_rdma_balanced',
                    'name': 'Win10 RDMA Balanced Pool',
                    'type': 'rdma',
                    'capacity': 6.0,  # GB equivalent
                    'allocated': 0,
                    'properties': {
                        'pool_type': 'balanced',
                        'max_latency_ns': 1000,
                        'min_throughput_mbps': 5000,
                        'priority': 'medium',
                        'features': ['balanced', 'adaptive', 'auto_tuning']
                    }
                }
            }
            
            # Register RDMA resources with homelab server
            self.register_rdma_resources()
            
            self.logger.info(f"Initialized {len(self.rdma_pools)} RDMA resource pools")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RDMA resources: {e}")
            self.create_mock_rdma_resources()
    
    def create_mock_rdma_resources(self):
        """Create mock RDMA resources when RDMA components are not available"""
        self.rdma_pools = {
            'rdma_mock': {
                'id': 'win10_rdma_mock',
                'name': 'Win10 RDMA Mock Pool',
                'type': 'rdma',
                'capacity': 2.0,  # GB equivalent
                'allocated': 0,
                'properties': {
                    'pool_type': 'mock',
                    'max_latency_ns': 1000,
                    'min_throughput_mbps': 1000,
                    'priority': 'low',
                    'features': ['mock', 'simulation'],
                    'status': 'mock_mode'
                }
            }
        }
        
        self.register_rdma_resources()
        self.logger.info("Created mock RDMA resources (RDMA components not available)")
    
    def register_rdma_resources(self):
        """Register RDMA resources with homelab server database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for pool_id, pool_data in self.rdma_pools.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO resources 
                    (id, name, type, status, capacity, properties, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (pool_data['id'], pool_data['name'], pool_data['type'], 'available',
                      pool_data['capacity'], json.dumps(pool_data['properties']), 
                      datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Registered {len(self.rdma_pools)} RDMA resources with homelab server")
            
        except Exception as e:
            self.logger.error(f"Failed to register RDMA resources: {e}")
    
    def start_rdma_services(self) -> bool:
        """Start RDMA services"""
        try:
            if not RDMA_AVAILABLE:
                self.logger.warning("RDMA components not available, starting in mock mode")
                self.status = RDMAStatus.RUNNING
                return True
            
            self.status = RDMAStatus.STARTING
            self.logger.info("Starting RDMA services...")
            
            # Initialize DMA controller
            try:
                self.dma_controller = UltraLowLatencyDMA()
                self.logger.info("DMA controller initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize DMA controller: {e}")
                self.status = RDMAStatus.ERROR
                return False
            
            # Initialize monitoring system
            try:
                self.monitoring_system = MonitoringSystem()
                self.monitoring_system.start_monitoring()
                self.logger.info("RDMA monitoring system started")
            except Exception as e:
                self.logger.error(f"Failed to start monitoring system: {e}")
            
            # Start RDMA REST API
            try:
                self.start_rdma_api()
                self.logger.info("RDMA REST API started")
            except Exception as e:
                self.logger.error(f"Failed to start RDMA API: {e}")
            
            self.status = RDMAStatus.RUNNING
            self.logger.info("RDMA services started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start RDMA services: {e}")
            self.status = RDMAStatus.ERROR
            return False
    
    def start_rdma_api(self):
        """Start RDMA REST API in separate thread"""
        if not RDMA_AVAILABLE:
            return
        
        def run_api():
            try:
                # Configure RDMA API to use different port
                rdma_api.config['DEBUG'] = False
                rdma_api.run(host='0.0.0.0', port=self.settings.get('api_port', 5001), threaded=True)
            except Exception as e:
                self.logger.error(f"RDMA API error: {e}")
        
        self.rdma_api_thread = threading.Thread(target=run_api, daemon=True)
        self.rdma_api_thread.start()
    
    def stop_rdma_services(self):
        """Stop RDMA services"""
        try:
            self.status = RDMAStatus.STOPPED
            self.logger.info("Stopping RDMA services...")
            
            # Stop DMA controller
            if self.dma_controller:
                try:
                    self.dma_controller.cleanup()
                    self.dma_controller = None
                except Exception as e:
                    self.logger.error(f"Error stopping DMA controller: {e}")
            
            # Stop monitoring system
            if self.monitoring_system:
                try:
                    self.monitoring_system.stop_monitoring()
                    self.monitoring_system = None
                except Exception as e:
                    self.logger.error(f"Error stopping monitoring system: {e}")
            
            # Stop RDMA API
            if self.rdma_api_thread:
                try:
                    # Note: Flask doesn't have a clean shutdown in development mode
                    self.rdma_api_thread = None
                except Exception as e:
                    self.logger.error(f"Error stopping RDMA API: {e}")
            
            self.logger.info("RDMA services stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop RDMA services: {e}")
    
    def get_rdma_metrics(self) -> Dict[str, Any]:
        """Get current RDMA performance metrics"""
        try:
            if not RDMA_AVAILABLE or self.status != RDMAStatus.RUNNING:
                # Return mock metrics
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': self.status.value,
                    'latency_ns': 800 + (hash(time.time()) % 400),  # Mock latency 400-1200ns
                    'throughput_mbps': 2000 + (hash(time.time()) % 8000),  # Mock throughput 2-10Gbps
                    'cpu_usage': 15 + (hash(time.time()) % 25),  # Mock CPU 15-40%
                    'memory_usage': 200 + (hash(time.time()) % 600),  # Mock memory 200-800MB
                    'active_connections': 0,
                    'total_transfers': 0,
                    'errors': 0,
                    'pool_utilization': self.get_pool_utilization()
                }
            
            # Get real metrics from RDMA components
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'status': self.status.value
            }
            
            # Get metrics from DMA controller
            if self.dma_controller:
                try:
                    dma_metrics = self.dma_controller.get_performance_metrics()
                    metrics.update(dma_metrics)
                except Exception as e:
                    self.logger.error(f"Error getting DMA metrics: {e}")
            
            # Get metrics from monitoring system
            if self.monitoring_system:
                try:
                    monitoring_metrics = self.monitoring_system.get_current_metrics()
                    metrics.update(monitoring_metrics)
                except Exception as e:
                    self.logger.error(f"Error getting monitoring metrics: {e}")
            
            # Add pool utilization
            metrics['pool_utilization'] = self.get_pool_utilization()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get RDMA metrics: {e}")
            return self.performance_metrics
    
    def get_pool_utilization(self) -> Dict[str, Any]:
        """Get RDMA resource pool utilization"""
        utilization = {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for pool_id, pool_data in self.rdma_pools.items():
                cursor.execute('SELECT allocated FROM resources WHERE id = ?', (pool_id,))
                result = cursor.fetchone()
                
                allocated = result[0] if result else 0
                capacity = pool_data['capacity']
                
                utilization[pool_id] = {
                    'allocated': allocated,
                    'capacity': capacity,
                    'utilization_percent': (allocated / capacity * 100) if capacity > 0 else 0,
                    'available': capacity - allocated
                }
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to get pool utilization: {e}")
        
        return utilization
    
    def allocate_rdma_resource(self, pool_id: str, amount: float, client_id: str, properties: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Allocate RDMA resource to client"""
        try:
            if pool_id not in self.rdma_pools:
                return None
            
            pool = self.rdma_pools[pool_id]
            
            # Check availability
            available = pool['capacity'] - pool['allocated']
            if amount > available:
                return None
            
            # Create allocation
            allocation_id = f"rdma_alloc_{int(time.time())}_{hash(client_id) % 10000}"
            expires_at = datetime.now() + timedelta(hours=2)  # 2 hour default
            
            # Update pool allocation
            pool['allocated'] += amount
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE resources SET allocated = ?, updated_at = ?
                WHERE id = ?
            ''', (pool['allocated'], datetime.now().isoformat(), pool_id))
            
            cursor.execute('''
                INSERT INTO allocations 
                (id, client_id, resource_id, amount, properties, expires_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (allocation_id, client_id, pool_id, amount, 
                  json.dumps(properties or {}), expires_at.isoformat(), 'active'))
            
            conn.commit()
            conn.close()
            
            # Initialize RDMA connection for client if available
            if RDMA_AVAILABLE and self.dma_controller:
                try:
                    connection_id = self.dma_controller.create_client_connection(
                        client_id, 
                        pool['properties'].get('pool_type', 'balanced')
                    )
                    
                    allocation = {
                        'allocation_id': allocation_id,
                        'resource_id': pool_id,
                        'amount': amount,
                        'connection_id': connection_id,
                        'expires_at': expires_at.isoformat(),
                        'status': 'active',
                        'properties': {
                            **pool['properties'],
                            **(properties or {})
                        }
                    }
                    
                    self.logger.info(f"Allocated RDMA resource {pool_id} to client {client_id}")
                    return allocation
                    
                except Exception as e:
                    self.logger.error(f"Failed to create RDMA connection: {e}")
            
            # Fallback allocation without RDMA connection
            allocation = {
                'allocation_id': allocation_id,
                'resource_id': pool_id,
                'amount': amount,
                'connection_id': None,
                'expires_at': expires_at.isoformat(),
                'status': 'active',
                'properties': {
                    **pool['properties'],
                    **(properties or {}),
                    'rdma_unavailable': True
                }
            }
            
            self.logger.info(f"Allocated RDMA resource {pool_id} to client {client_id} (mock mode)")
            return allocation
            
        except Exception as e:
            self.logger.error(f"Failed to allocate RDMA resource: {e}")
            return None
    
    def release_rdma_resource(self, allocation_id: str, client_id: str) -> bool:
        """Release RDMA resource allocation"""
        try:
            # Get allocation from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT resource_id, amount FROM allocations 
                WHERE id = ? AND client_id = ?
            ''', (allocation_id, client_id))
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return False
            
            resource_id, amount = result
            
            # Update pool allocation
            if resource_id in self.rdma_pools:
                self.rdma_pools[resource_id]['allocated'] -= amount
                if self.rdma_pools[resource_id]['allocated'] < 0:
                    self.rdma_pools[resource_id]['allocated'] = 0
            
                # Update database
                cursor.execute('''
                    UPDATE resources SET allocated = ?, updated_at = ?
                    WHERE id = ?
                ''', (self.rdma_pools[resource_id]['allocated'], 
                      datetime.now().isoformat(), resource_id))
            
            # Remove allocation
            cursor.execute('DELETE FROM allocations WHERE id = ?', (allocation_id,))
            
            conn.commit()
            conn.close()
            
            # Close RDMA connection if available
            if RDMA_AVAILABLE and self.dma_controller:
                try:
                    self.dma_controller.close_client_connection(allocation_id)
                except Exception as e:
                    self.logger.error(f"Failed to close RDMA connection: {e}")
            
            self.logger.info(f"Released RDMA allocation {allocation_id} from client {client_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to release RDMA resource: {e}")
            return False
    
    def start_monitoring(self):
        """Start RDMA monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("RDMA integration monitoring started")
    
    def stop_monitoring(self):
        """Stop RDMA monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("RDMA integration monitoring stopped")
    
    def _monitoring_loop(self):
        """RDMA monitoring loop"""
        while self.monitoring_active:
            try:
                # Update performance metrics
                self.performance_metrics = self.get_rdma_metrics()
                
                # Check RDMA service health
                if self.status == RDMAStatus.RUNNING:
                    self._check_rdma_health()
                
                # Sleep for monitoring interval
                time.sleep(self.settings.get('monitoring_interval', 5))
                
            except Exception as e:
                self.logger.error(f"RDMA monitoring error: {e}")
                time.sleep(10)
    
    def _check_rdma_health(self):
        """Check RDMA service health"""
        try:
            # Check if services are responsive
            if RDMA_AVAILABLE:
                # Check DMA controller
                if self.dma_controller:
                    try:
                        dma_status = self.dma_controller.get_status()
                        if dma_status.get('status') != 'healthy':
                            self.logger.warning(f"DMA controller unhealthy: {dma_status}")
                    except Exception as e:
                        self.logger.error(f"DMA controller health check failed: {e}")
                
                # Check monitoring system
                if self.monitoring_system:
                    try:
                        monitoring_status = self.monitoring_system.get_health_status()
                        if not monitoring_status.get('healthy', True):
                            self.logger.warning(f"Monitoring system unhealthy: {monitoring_status}")
                    except Exception as e:
                        self.logger.error(f"Monitoring system health check failed: {e}")
            
        except Exception as e:
            self.logger.error(f"RDMA health check failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get RDMA integration status"""
        return {
            'status': self.status.value,
            'rdma_available': RDMA_AVAILABLE,
            'services': {
                'dma_controller': self.dma_controller is not None,
                'monitoring_system': self.monitoring_system is not None,
                'rest_api': self.rdma_api_thread is not None
            },
            'resource_pools': len(self.rdma_pools),
            'performance_metrics': self.performance_metrics,
            'settings': self.settings
        }

# Global RDMA integration instance
rdma_integration = RDMAIntegration()

if __name__ == '__main__':
    # Test RDMA integration
    print("🔗 Testing RDMA Integration")
    
    status = rdma_integration.get_status()
    print(f"Status: {status}")
    
    # Start RDMA services
    if rdma_integration.start_rdma_services():
        print("✅ RDMA services started successfully")
        
        # Get metrics
        metrics = rdma_integration.get_rdma_metrics()
        print(f"Metrics: {metrics}")
        
        # Test resource allocation
        allocation = rdma_integration.allocate_rdma_resource(
            'win10_rdma_low_latency', 
            1.0, 
            'test_client',
            {'test': True}
        )
        
        if allocation:
            print(f"✅ Test allocation successful: {allocation['allocation_id']}")
            
            # Release allocation
            if rdma_integration.release_rdma_resource(allocation['allocation_id'], 'test_client'):
                print("✅ Test release successful")
        else:
            print("❌ Test allocation failed")
        
        # Stop services
        rdma_integration.stop_rdma_services()
        print("🛑 RDMA services stopped")
    else:
        print("❌ Failed to start RDMA services")
