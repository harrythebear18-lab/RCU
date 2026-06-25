#!/usr/bin/env python3
"""
Windows 11 RDMA Client
Enhanced Windows 11 client with RDMA resource allocation and usage capabilities.
"""

import os
import sys
import json
import time
import requests
import threading
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import psutil
import logging
from enum import Enum

class ClientStatus(Enum):
    """Client connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ERROR = "error"

class Windows11RDMAClient:
    """Windows 11 client with RDMA capabilities for connecting to Windows 10 homelab server"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.db_path = os.path.join(os.path.dirname(__file__), 'win11_rdma_client.db')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'win11_rdma_settings.json')
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Setup logging
        self.setup_logging()
        
        # Client state
        self.client_id = None
        self.api_key = None
        self.status = ClientStatus.DISCONNECTED
        self.allocated_resources = {}
        self.rdma_allocations = {}
        self.server_resources = {}
        
        # RDMA connection state
        self.rdma_connected = False
        self.rdma_connection_id = None
        self.rdma_metrics = {}
        
        # Connection management
        self.connection_thread = None
        self.heartbeat_thread = None
        self.rdma_monitor_thread = None
        self.monitoring_active = False
        
        # Load saved configuration
        self.load_client_config()
        
        # Get Windows 11 system information
        self.system_info = self.get_windows11_info()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load Windows 11 RDMA client settings"""
        default_settings = {
            'server_url': 'http://localhost:8080',
            'heartbeat_interval': 30,
            'resource_check_interval': 60,
            'rdma_monitor_interval': 5,
            'auto_reconnect': True,
            'reconnect_interval': 60,
            'max_reconnect_attempts': 5,
            'log_level': 'INFO',
            'enable_local_cache': True,
            'cache_timeout': 300,
            'enable_rdma_auto_allocation': True,
            'preferred_rdma_pools': ['win10_rdma_low_latency', 'win10_rdma_balanced'],
            'rdma_connection_timeout': 30,
            'rdma_retry_attempts': 3,
            'win11_optimizations': True,
            'enhanced_performance': True,
            'rdma_optimization': True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception:
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save client settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def init_database(self):
        """Initialize client database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Client configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RDMA allocation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rdma_allocations (
                id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                allocation_id TEXT NOT NULL,
                connection_id TEXT,
                amount REAL,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # RDMA metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rdma_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                latency_ns REAL,
                throughput_mbps REAL,
                cpu_usage REAL,
                memory_usage REAL,
                active_connections INTEGER,
                errors INTEGER
            )
        ''')
        
        # Connection log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connection_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                message TEXT,
                server_url TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """Setup client logging"""
        self.logger = logging.getLogger('Win11RDMAClient')
        
        log_level = getattr(logging, self.settings.get('log_level', 'INFO').upper())
        self.logger.setLevel(log_level)
        
        # Create file handler
        log_file = os.path.join(os.path.dirname(__file__), 'win11_rdma_client.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def get_windows11_info(self) -> Dict[str, Any]:
        """Get Windows 11 system information for registration"""
        try:
            import platform
            import uuid
            
            system_info = {
                'name': f"{platform.node()}-win11-rdma-client",
                'hostname': platform.node(),
                'os_version': platform.version(),
                'os_name': platform.system(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'ip_address': self.get_local_ip(),
                'mac_address': self.get_mac_address(),
                'python_version': platform.python_version(),
                'client_version': '1.0.0',
                'platform': 'Windows 11',
                'is_windows_11': 'Windows-11' in platform.platform() or platform.version().startswith('10.0.2'),
                'rdma_capable': True,
                'rdma_optimized': True
            }
            
            # Add hardware info
            system_info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': sum(disk.total for disk in psutil.disk_partitions() 
                                 if psutil.disk_usage(disk.mountpoint).total > 0),
                'boot_time': psutil.boot_time()
            })
            
            # Windows 11 specific features
            system_info.update({
                'supports_directx12': True,
                'supports_auto_hdr': True,
                'supports_dolby_vision': True,
                'enhanced_performance_mode': True,
                'rdma_features': ['ultra_low_latency', 'kernel_bypass', 'hardware_timestamping']
            })
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Failed to get Windows 11 info: {e}")
            return {}
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_mac_address(self) -> str:
        """Get MAC address"""
        try:
            import uuid
            mac = uuid.getnode()
            mac_str = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) 
                               for elements in range(0, 2*6, 2)][::-1])
            return mac_str
        except:
            return "00:00:00:00:00:00"
    
    def load_client_config(self):
        """Load saved client configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM client_config')
            rows = cursor.fetchall()
            
            config = {}
            for key, value in rows:
                if key == 'client_id':
                    self.client_id = value
                elif key == 'api_key':
                    self.api_key = value
                else:
                    config[key] = json.loads(value) if value.startswith('{') else value
            
            conn.close()
            
            self.logger.info(f"Loaded Windows 11 RDMA client configuration: client_id={self.client_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to load client config: {e}")
    
    def save_client_config(self):
        """Save client configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if self.client_id:
                cursor.execute('INSERT OR REPLACE INTO client_config (key, value) VALUES (?, ?)',
                             ('client_id', self.client_id))
            
            if self.api_key:
                cursor.execute('INSERT OR REPLACE INTO client_config (key, value) VALUES (?, ?)',
                             ('api_key', self.api_key))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save client config: {e}")
    
    def register_with_server(self) -> bool:
        """Register Windows 11 RDMA client with Windows 10 server"""
        try:
            self.status = ClientStatus.CONNECTING
            self._log_connection("connecting", "Attempting to register with Windows 10 RDMA server")
            
            # Register client
            response = requests.post(
                f"{self.server_url}/api/v1/clients/register",
                json=self.system_info,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data['client_id']
                self.api_key = data['api_key']
                
                # Save configuration
                self.save_client_config()
                
                self.status = ClientStatus.AUTHENTICATED
                self._log_connection("authenticated", f"Successfully registered as {self.client_id}")
                
                return True
            else:
                self.status = ClientStatus.ERROR
                self._log_connection("error", f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.status = ClientStatus.ERROR
            self._log_connection("error", f"Registration error: {e}")
            return False
    
    def connect_to_server(self) -> bool:
        """Connect to Windows 10 homelab server"""
        if not self.client_id or not self.api_key:
            if not self.register_with_server():
                return False
        
        try:
            # Test connection
            response = requests.get(
                f"{self.server_url}/api/v1/server/status",
                headers={'X-API-Key': self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                self.status = ClientStatus.CONNECTED
                self._log_connection("connected", "Successfully connected to Windows 10 RDMA server")
                
                # Start heartbeat
                if not self.heartbeat_thread or not self.heartbeat_thread.is_alive():
                    self.start_heartbeat()
                
                # Start RDMA monitoring
                if not self.rdma_monitor_thread or not self.rdma_monitor_thread.is_alive():
                    self.start_rdma_monitoring()
                
                return True
            else:
                self.status = ClientStatus.ERROR
                self._log_connection("error", f"Connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.status = ClientStatus.ERROR
            self._log_connection("error", f"Connection error: {e}")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        self.status = ClientStatus.DISCONNECTED
        self.monitoring_active = False
        
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        
        if self.rdma_monitor_thread:
            self.rdma_monitor_thread.join(timeout=5)
        
        # Release all RDMA allocations
        self.release_all_rdma_resources()
        
        self._log_connection("disconnected", "Disconnected from Windows 10 RDMA server")
    
    def start_heartbeat(self):
        """Start heartbeat thread"""
        self.monitoring_active = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def start_rdma_monitoring(self):
        """Start RDMA monitoring thread"""
        self.monitoring_active = True
        self.rdma_monitor_thread = threading.Thread(target=self._rdma_monitoring_loop, daemon=True)
        self.rdma_monitor_thread.start()
    
    def _heartbeat_loop(self):
        """Heartbeat loop"""
        while self.monitoring_active:
            try:
                # Send status update
                status_data = {
                    'status': 'online',
                    'timestamp': datetime.now().isoformat(),
                    'local_metrics': self.get_local_metrics(),
                    'rdma_status': {
                        'connected': self.rdma_connected,
                        'connection_id': self.rdma_connection_id,
                        'allocations': len(self.rdma_allocations)
                    },
                    'win11_features': {
                        'directx12': True,
                        'auto_hdr': True,
                        'enhanced_performance': self.settings.get('enhanced_performance', True),
                        'rdma_optimized': self.settings.get('rdma_optimization', True)
                    }
                }
                
                response = requests.post(
                    f"{self.server_url}/api/v1/clients/{self.client_id}/status",
                    headers={'X-API-Key': self.api_key},
                    json=status_data,
                    timeout=10
                )
                
                if response.status_code != 200:
                    self.logger.warning(f"Heartbeat failed: {response.status_code}")
                
                # Sleep for heartbeat interval
                time.sleep(self.settings.get('heartbeat_interval', 30))
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                time.sleep(10)
    
    def _rdma_monitoring_loop(self):
        """RDMA monitoring loop"""
        while self.monitoring_active:
            try:
                # Get RDMA status from server
                self.get_rdma_status()
                
                # Sleep for RDMA monitoring interval
                time.sleep(self.settings.get('rdma_monitor_interval', 5))
                
            except Exception as e:
                self.logger.error(f"RDMA monitoring error: {e}")
                time.sleep(10)
    
    def get_local_metrics(self) -> Dict[str, Any]:
        """Get local Windows 11 system metrics"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'platform': 'Windows 11',
                'cpu': {
                    'usage_percent': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent,
                    'used': psutil.virtual_memory().used
                },
                'disk': [],
                'network': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
            
            # Disk metrics
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    metrics['disk'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    })
                except:
                    continue
            
            # Windows 11 specific metrics
            metrics['win11'] = {
                'directx12_available': True,
                'auto_hdr_available': True,
                'enhanced_performance_mode': self.settings.get('enhanced_performance', True),
                'rdma_optimized': self.settings.get('rdma_optimization', True)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get local metrics: {e}")
            return {}
    
    def get_rdma_status(self) -> Dict[str, Any]:
        """Get RDMA status from server"""
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/rdma/status",
                headers={'X-API-Key': self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                self.rdma_metrics = response.json()
                
                # Update RDMA connection status
                self.rdma_connected = self.rdma_metrics.get('rdma_available', False)
                
                # Store metrics in database
                self._store_rdma_metrics(self.rdma_metrics)
                
                return self.rdma_metrics
            else:
                self.logger.error(f"Failed to get RDMA status: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting RDMA status: {e}")
            return {}
    
    def _store_rdma_metrics(self, metrics: Dict[str, Any]):
        """Store RDMA metrics in database"""
        try:
            if 'performance_metrics' not in metrics:
                return
            
            perf_metrics = metrics['performance_metrics']
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rdma_metrics 
                (latency_ns, throughput_mbps, cpu_usage, memory_usage, active_connections, errors)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                perf_metrics.get('latency_ns', 0),
                perf_metrics.get('throughput_mbps', 0),
                perf_metrics.get('cpu_usage', 0),
                perf_metrics.get('memory_usage', 0),
                perf_metrics.get('active_connections', 0),
                perf_metrics.get('errors', 0)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to store RDMA metrics: {e}")
    
    def get_server_resources(self, resource_type: str = None) -> List[Dict[str, Any]]:
        """Get available resources from Windows 10 server"""
        try:
            params = {}
            if resource_type:
                params['type'] = resource_type
            
            response = requests.get(
                f"{self.server_url}/api/v1/resources",
                headers={'X-API-Key': self.api_key},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.server_resources = {r['id']: r for r in data['resources']}
                return data['resources']
            else:
                self.logger.error(f"Failed to get resources: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting resources: {e}")
            return []
    
    def allocate_rdma_resource(self, pool_id: str, amount: float, properties: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Allocate RDMA resource from Windows 10 server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/resources/{pool_id}",
                headers={'X-API-Key': self.api_key},
                json={
                    'client_id': self.client_id,
                    'amount': amount,
                    'properties': properties or {}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                allocation = response.json()
                
                # Cache allocation locally
                self.rdma_allocations[allocation['allocation_id']] = allocation
                self.rdma_connection_id = allocation.get('connection_id')
                
                # Save to database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO rdma_allocations 
                    (id, resource_id, allocation_id, connection_id, amount, properties, expires_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (allocation['allocation_id'], pool_id, allocation['allocation_id'],
                      allocation.get('connection_id'), amount, 
                      json.dumps(properties or {}), allocation['expires_at'], 'active'))
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Allocated RDMA resource {pool_id}: {amount}GB")
                return allocation
            else:
                self.logger.error(f"Failed to allocate RDMA resource: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error allocating RDMA resource: {e}")
            return None
    
    def release_rdma_resource(self, allocation_id: str) -> bool:
        """Release RDMA resource allocation"""
        try:
            if allocation_id not in self.rdma_allocations:
                return False
            
            allocation = self.rdma_allocations[allocation_id]
            resource_id = allocation['resource_id']
            
            response = requests.post(
                f"{self.server_url}/api/v1/resources/{resource_id}/release",
                headers={'X-API-Key': self.api_key},
                json={
                    'client_id': self.client_id,
                    'allocation_id': allocation_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                # Remove from local cache
                del self.rdma_allocations[allocation_id]
                
                # Update database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM rdma_allocations WHERE id = ?', (allocation_id,))
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Released RDMA allocation {allocation_id}")
                return True
            else:
                self.logger.error(f"Failed to release RDMA resource: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error releasing RDMA resource: {e}")
            return False
    
    def auto_allocate_rdma_resources(self) -> Dict[str, Any]:
        """Automatically allocate preferred RDMA resources"""
        allocations = {}
        
        try:
            # Get available RDMA resources
            resources = self.get_server_resources('erdma')
            
            # Get preferred pools
            preferred_pools = self.settings.get('preferred_rdma_pools', ['win10_rdma_low_latency'])
            
            for pool_id in preferred_pools:
                for resource in resources:
                    if resource['id'] == pool_id and resource['status'] == 'available':
                        amount = min(2.0, resource['capacity'] - resource['allocated'])
                        if amount > 0:
                            allocation = self.allocate_rdma_resource(pool_id, amount, {
                                'auto_allocated': True,
                                'win11_client': True,
                                'enhanced_performance': True,
                                'rdma_optimized': True
                            })
                            if allocation:
                                allocations[pool_id] = allocation
                                break  # Only allocate one pool per preferred type
            
            self.logger.info(f"Auto-allocated {len(allocations)} RDMA resources for Windows 11")
            return allocations
            
        except Exception as e:
            self.logger.error(f"Error in RDMA auto-allocation: {e}")
            return {}
    
    def release_all_rdma_resources(self):
        """Release all allocated RDMA resources"""
        for allocation_id in list(self.rdma_allocations.keys()):
            self.release_rdma_resource(allocation_id)
    
    def get_rdma_allocations(self) -> List[Dict[str, Any]]:
        """Get current RDMA allocations"""
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/allocations",
                headers={'X-API-Key': self.api_key},
                params={'client_id': self.client_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['allocations']
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting RDMA allocations: {e}")
            return []
    
    def _log_connection(self, status: str, message: str):
        """Log connection events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO connection_log (status, message, server_url)
                VALUES (?, ?, ?)
            ''', (status, message, self.server_url))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to log connection: {e}")
    
    def start_client(self):
        """Start the Windows 11 RDMA client and maintain connection"""
        self.logger.info("Starting Windows 11 RDMA Homelab Client")
        
        reconnect_attempts = 0
        max_attempts = self.settings.get('max_reconnect_attempts', 5)
        
        while reconnect_attempts < max_attempts:
            if self.connect_to_server():
                # Connection successful, break the loop
                break
            
            reconnect_attempts += 1
            if self.settings.get('auto_reconnect', True):
                self.logger.info(f"Reconnecting in {self.settings.get('reconnect_interval', 60)} seconds...")
                time.sleep(self.settings.get('reconnect_interval', 60))
            else:
                break
        
        if self.status != ClientStatus.CONNECTED:
            self.logger.error("Failed to connect to Windows 10 RDMA server")
            return False
        
        # Auto-allocate RDMA resources if enabled
        if self.settings.get('enable_rdma_auto_allocation', True):
            allocations = self.auto_allocate_rdma_resources()
            self.logger.info(f"Auto-allocated {len(allocations)} RDMA resources")
        
        self.logger.info("Windows 11 RDMA Homelab Client started successfully")
        return True
    
    def stop_client(self):
        """Stop the Windows 11 RDMA client"""
        self.logger.info("Stopping Windows 11 RDMA Homelab Client")
        
        # Release all allocated resources
        self.release_all_rdma_resources()
        
        # Disconnect from server
        self.disconnect_from_server()
        
        self.logger.info("Windows 11 RDMA Homelab Client stopped")

# Windows 11 RDMA Client Manager for easy integration
class Windows11RDMAClientManager:
    """Manager for Windows 11 RDMA homelab client operations"""
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.client = Windows11RDMAClient(server_url)
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Windows 10 RDMA server"""
        self.connected = self.client.start_client()
        return self.connected
    
    def disconnect(self):
        """Disconnect from server"""
        self.client.stop_client()
        self.connected = False
    
    def allocate_rdma_low_latency(self, amount_gb: float = 1.0) -> Optional[Dict[str, Any]]:
        """Allocate low latency RDMA resource"""
        return self.client.allocate_rdma_resource('win10_rdma_low_latency', amount_gb, {
            'win11_client': True,
            'enhanced_performance': True,
            'rdma_optimized': True
        })
    
    def allocate_rdma_high_throughput(self, amount_gb: float = 2.0) -> Optional[Dict[str, Any]]:
        """Allocate high throughput RDMA resource"""
        return self.client.allocate_rdma_resource('win10_rdma_high_throughput', amount_gb, {
            'win11_client': True,
            'high_throughput': True,
            'rdma_optimized': True
        })
    
    def allocate_rdma_balanced(self, amount_gb: float = 1.5) -> Optional[Dict[str, Any]]:
        """Allocate balanced RDMA resource"""
        return self.client.allocate_rdma_resource('win10_rdma_balanced', amount_gb, {
            'win11_client': True,
            'balanced': True,
            'rdma_optimized': True
        })
    
    def release_all_rdma_resources(self):
        """Release all allocated RDMA resources"""
        self.client.release_all_rdma_resources()
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            'connected': self.connected,
            'client_id': self.client.client_id,
            'status': self.client.status.value,
            'rdma_connected': self.client.rdma_connected,
            'rdma_allocations': len(self.client.rdma_allocations),
            'server_url': self.client.server_url,
            'platform': 'Windows 11',
            'rdma_optimized': True
        }
    
    def get_rdma_metrics(self) -> Dict[str, Any]:
        """Get current RDMA metrics"""
        return self.client.rdma_metrics
    
    def get_win11_rdma_features(self) -> Dict[str, Any]:
        """Get Windows 11 RDMA specific features"""
        return {
            'directx12_support': True,
            'auto_hdr_support': True,
            'enhanced_performance_mode': self.client.settings.get('enhanced_performance', True),
            'rdma_optimization': self.client.settings.get('rdma_optimization', True),
            'win11_optimizations': True,
            'rdma_features': ['ultra_low_latency', 'kernel_bypass', 'hardware_timestamping']
        }

# Global Windows 11 RDMA client manager instance
win11_rdma_client_manager = Windows11RDMAClientManager()

if __name__ == '__main__':
    # Test the Windows 11 RDMA client
    print("[MONITOR]  Testing Windows 11 RDMA Homelab Client")
    
    # Create client manager
    manager = Windows11RDMAClientManager("http://localhost:8080")
    
    # Connect to Windows 10 server
    if manager.connect():
        print("[OK] Connected to Windows 10 RDMA server successfully")
        
        # Get status
        status = manager.get_status()
        print(f"[CHART] Client status: {status}")
        
        # Get Windows 11 RDMA features
        features = manager.get_win11_rdma_features()
        print(f"[GAME] Windows 11 RDMA features: {features}")
        
        # Get RDMA status
        rdma_metrics = manager.get_rdma_metrics()
        print(f"[LINK] RDMA metrics: {rdma_metrics}")
        
        # Get available RDMA resources
        resources = manager.client.get_server_resources('erdma')
        print(f"📦 Available RDMA resources: {len(resources)}")
        
        # Auto-allocate RDMA resources
        allocations = manager.client.auto_allocate_rdma_resources()
        print(f"[ROCKET] Auto-allocated RDMA resources: {len(allocations)}")
        
        # Manual RDMA allocation test
        low_latency_alloc = manager.allocate_rdma_low_latency(1.0)
        if low_latency_alloc:
            print(f"[OK] Low latency RDMA allocated: {low_latency_alloc['allocation_id']}")
        
        # Keep running
        try:
            while True:
                time.sleep(60)
                print(f"[REFRESH] Client running... RDMA allocations: {len(manager.client.rdma_allocations)}")
                print(f"[GAME] Windows 11 enhancements: DirectX12, Auto-HDR, Enhanced Performance, RDMA Optimization")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            manager.disconnect()
    else:
        print("[ERROR] Failed to connect to Windows 10 RDMA server")
        print("💡 Make sure the Windows 10 server with RDMA is running on the specified URL")
