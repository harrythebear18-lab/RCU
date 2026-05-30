#!/usr/bin/env python3
"""
Homelab Server Component
Manages and hosts shared resources (eRAM, eGPU) for Windows 10/11 clients.
"""

import os
import json
import socket
import threading
import time
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
import psutil
import GPUtil
try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
    nvml.nvmlInit()
except ImportError:
    NVML_AVAILABLE = False
    nvml = None

import flask
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
from enum import Enum

class ResourceType(Enum):
    """Resource types available on server"""
    ERAM = "eram"
    EGPU = "egpu"
    ECPU = "ecpu"
    ESTORAGE = "estorage"
    ENETWORK = "enetwork"

class ResourceStatus(Enum):
    """Resource status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class HomelabServer:
    """Main homelab server for resource hosting"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.db_path = os.path.join(os.path.dirname(__file__), 'homelab_server.db')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'server_settings.json')
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Setup logging
        self.setup_logging()
        
        # Resource registry
        self.resources = {}
        self.allocations = {}
        self.clients = {}
        
        # Authentication
        self.api_keys = {}
        self.session_tokens = {}
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config['SECRET_KEY'] = self.settings.get('secret_key', secrets.token_urlsafe(32))
        
        # Setup routes
        self.setup_routes()
        
        # Initialize resources
        self.initialize_resources()
        
        # Load clients and API keys
        self.load_clients()
        self.load_api_keys()
        
        # Start monitoring thread
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load server settings"""
        default_settings = {
            'server_name': 'Homelab Resource Server',
            'max_clients': 10,
            'session_timeout': 3600,
            'allocation_timeout': 7200,
            'resource_check_interval': 30,
            'enable_authentication': True,
            'enable_encryption': True,
            'log_level': 'INFO',
            'backup_interval': 3600,
            'max_eram_allocation_gb': 32,
            'enable_egpu_passthrough': True,
            'enable_load_balancing': True,
            'auto_cleanup': True
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
        """Save server settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def init_database(self):
        """Initialize server database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Resource registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                capacity REAL,
                allocated REAL DEFAULT 0,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Client registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hostname TEXT,
                os_version TEXT,
                ip_address TEXT,
                mac_address TEXT,
                status TEXT DEFAULT 'offline',
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Allocation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allocations (
                id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                amount REAL,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (resource_id) REFERENCES resources (id)
            )
        ''')
        
        # Usage logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                allocation_id TEXT,
                usage_amount REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (resource_id) REFERENCES resources (id)
            )
        ''')
        
        # API keys table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocations_client ON allocations(client_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocations_resource ON allocations(resource_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_keys_client ON api_keys(client_id)')
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """Setup server logging"""
        self.logger = logging.getLogger('HomelabServer')
        
        log_level = getattr(logging, self.settings.get('log_level', 'INFO').upper())
        self.logger.setLevel(log_level)
        
        # Create file handler
        log_file = os.path.join(os.path.dirname(__file__), 'homelab_server.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def initialize_resources(self):
        """Initialize available resources"""
        # Initialize eRAM resources
        self._initialize_eram_resources()
        
        # Initialize eGPU resources
        self._initialize_egpu_resources()
        
        # Initialize eCPU resources
        self._initialize_ecpu_resources()
        
        # Initialize storage resources
        self._initialize_storage_resources()
        
        # Initialize network resources
        self._initialize_network_resources()
    
    def _initialize_eram_resources(self):
        """Initialize eRAM resources"""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            available_memory_gb = memory.available / (1024**3)
            
            # Create eRAM resource pools
            eram_pools = [
                {
                    'id': 'eram_small',
                    'name': 'eRAM Small Pool',
                    'capacity': min(4, available_memory_gb * 0.2),
                    'properties': {
                        'pool_size': 'small',
                        'priority': 'low',
                        'max_allocation_gb': 4
                    }
                },
                {
                    'id': 'eram_medium',
                    'name': 'eRAM Medium Pool',
                    'capacity': min(8, available_memory_gb * 0.3),
                    'properties': {
                        'pool_size': 'medium',
                        'priority': 'medium',
                        'max_allocation_gb': 8
                    }
                },
                {
                    'id': 'eram_large',
                    'name': 'eRAM Large Pool',
                    'capacity': min(16, available_memory_gb * 0.4),
                    'properties': {
                        'pool_size': 'large',
                        'priority': 'high',
                        'max_allocation_gb': 16
                    }
                }
            ]
            
            for pool in eram_pools:
                self._register_resource(
                    resource_id=pool['id'],
                    name=pool['name'],
                    resource_type=ResourceType.ERAM,
                    capacity=pool['capacity'],
                    properties=pool['properties']
                )
            
            self.logger.info(f"Initialized {len(eram_pools)} eRAM resource pools")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize eRAM resources: {e}")
    
    def _initialize_egpu_resources(self):
        """Initialize eGPU resources"""
        try:
            gpu_resources = []
            
            # Check for NVIDIA GPUs
            if NVML_AVAILABLE:
                device_count = nvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    name = nvml.nvmlDeviceGetName(handle).decode('utf-8')
                    memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                    memory_gb = memory_info.total / (1024**3)
                    
                    gpu_resources.append({
                        'id': f'egpu_nvidia_{i}',
                        'name': f'eGPU {name}',
                        'capacity': memory_gb,
                        'properties': {
                            'gpu_type': 'nvidia',
                            'device_index': i,
                            'memory_total': memory_info.total,
                            'supports_passthrough': True,
                            'compute_capability': self._get_compute_capability(handle)
                        }
                    })
            
            # Check for GPUs with GPUtil
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_resources.append({
                        'id': f'egpu_{gpu.id}',
                        'name': f'eGPU {gpu.name}',
                        'capacity': gpu.memoryTotal / 1024,  # Convert MB to GB
                        'properties': {
                            'gpu_type': 'general',
                            'device_id': gpu.id,
                            'memory_total': gpu.memoryTotal,
                            'driver_version': gpu.driver,
                            'temperature': gpu.temperature
                        }
                    })
            except:
                pass
            
            # Register GPU resources
            for gpu in gpu_resources:
                self._register_resource(
                    resource_id=gpu['id'],
                    name=gpu['name'],
                    resource_type=ResourceType.EGPU,
                    capacity=gpu['capacity'],
                    properties=gpu['properties']
                )
            
            self.logger.info(f"Initialized {len(gpu_resources)} eGPU resources")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize eGPU resources: {e}")
    
    def _initialize_ecpu_resources(self):
        """Initialize eCPU resources (virtual CPU cores)"""
        try:
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Create CPU resource pools
            cpu_pools = [
                {
                    'id': 'ecpu_light',
                    'name': 'eCPU Light Pool',
                    'capacity': cpu_count * 0.25,
                    'properties': {
                        'pool_type': 'light',
                        'max_cores': int(cpu_count * 0.25),
                        'priority': 'low',
                        'frequency': cpu_freq.current if cpu_freq else 0
                    }
                },
                {
                    'id': 'ecpu_medium',
                    'name': 'eCPU Medium Pool',
                    'capacity': cpu_count * 0.5,
                    'properties': {
                        'pool_type': 'medium',
                        'max_cores': int(cpu_count * 0.5),
                        'priority': 'medium',
                        'frequency': cpu_freq.current if cpu_freq else 0
                    }
                },
                {
                    'id': 'ecpu_heavy',
                    'name': 'eCPU Heavy Pool',
                    'capacity': cpu_count * 0.75,
                    'properties': {
                        'pool_type': 'heavy',
                        'max_cores': int(cpu_count * 0.75),
                        'priority': 'high',
                        'frequency': cpu_freq.current if cpu_freq else 0
                    }
                }
            ]
            
            for pool in cpu_pools:
                self._register_resource(
                    resource_id=pool['id'],
                    name=pool['name'],
                    resource_type=ResourceType.ECPU,
                    capacity=pool['capacity'],
                    properties=pool['properties']
                )
            
            self.logger.info(f"Initialized {len(cpu_pools)} eCPU resource pools")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize eCPU resources: {e}")
    
    def _initialize_storage_resources(self):
        """Initialize storage resources"""
        try:
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                if partition.device and partition.mountpoint:
                    usage = psutil.disk_usage(partition.mountpoint)
                    free_gb = usage.free / (1024**3)
                    total_gb = usage.total / (1024**3)
                    
                    # Create storage resource if significant free space
                    if free_gb > 10:  # Only pools with >10GB free
                        self._register_resource(
                            resource_id=f'estorage_{partition.device.replace(':', '').replace('\\', '_')}',
                            name=f'eStorage {partition.device}',
                            resource_type=ResourceType.ESTORAGE,
                            capacity=free_gb,
                            properties={
                                'device': partition.device,
                                'mountpoint': partition.mountpoint,
                                'fstype': partition.fstype,
                                'total_space': total_gb,
                                'free_space': free_gb,
                                'used_space': usage.used / (1024**3)
                            }
                        )
            
            self.logger.info(f"Initialized storage resources")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage resources: {e}")
    
    def _initialize_network_resources(self):
        """Initialize network resources"""
        try:
            network_interfaces = psutil.net_if_addrs()
            network_stats = psutil.net_if_stats()
            
            for interface_name, addresses in network_interfaces.items():
                if interface_name in network_stats:
                    stats = network_stats[interface_name]
                    
                    # Only include active interfaces
                    if stats.isup:
                        self._register_resource(
                            resource_id=f'enetwork_{interface_name}',
                            name=f'eNetwork {interface_name}',
                            resource_type=ResourceType.ENETWORK,
                            capacity=1000,  # Mbps
                            properties={
                                'interface': interface_name,
                                'speed': stats.speed,
                                'mtu': stats.mtu,
                                'duplex': stats.duplex,
                                'addresses': [addr.address for addr in addresses]
                            }
                        )
            
            self.logger.info(f"Initialized network resources")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize network resources: {e}")
    
    def _register_resource(self, resource_id: str, name: str, resource_type: ResourceType,
                          capacity: float, properties: Dict[str, Any] = None):
        """Register a resource in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO resources 
                (id, name, type, status, capacity, properties, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (resource_id, name, resource_type.value, ResourceStatus.AVAILABLE.value,
                  capacity, json.dumps(properties or {}), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            # Update in-memory registry
            self.resources[resource_id] = {
                'id': resource_id,
                'name': name,
                'type': resource_type.value,
                'status': ResourceStatus.AVAILABLE.value,
                'capacity': capacity,
                'allocated': 0,
                'properties': properties or {}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register resource {resource_id}: {e}")
    
    def _get_compute_capability(self, handle) -> str:
        """Get GPU compute capability"""
        try:
            major, minor = nvml.nvmlDeviceGetCudaComputeCapability(handle)
            return f"{major}.{minor}"
        except:
            return "unknown"
    
    def load_clients(self):
        """Load registered clients"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM clients')
            rows = cursor.fetchall()
            
            for row in rows:
                client_id = row[0]
                self.clients[client_id] = {
                    'id': client_id,
                    'name': row[1],
                    'hostname': row[2],
                    'os_version': row[3],
                    'ip_address': row[4],
                    'mac_address': row[5],
                    'status': row[6],
                    'last_seen': row[7],
                    'created_at': row[8]
                }
            
            conn.close()
            self.logger.info(f"Loaded {len(self.clients)} registered clients")
            
        except Exception as e:
            self.logger.error(f"Failed to load clients: {e}")
    
    def load_api_keys(self):
        """Load API keys"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM api_keys')
            rows = cursor.fetchall()
            
            for row in rows:
                key_id = row[0]
                self.api_keys[key_id] = {
                    'id': key_id,
                    'client_id': row[1],
                    'key_hash': row[2],
                    'permissions': json.loads(row[3]) if row[3] else [],
                    'created_at': row[4],
                    'expires_at': row[5],
                    'last_used': row[6]
                }
            
            conn.close()
            self.logger.info(f"Loaded {len(self.api_keys)} API keys")
            
        except Exception as e:
            self.logger.error(f"Failed to load API keys: {e}")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/api/v1/server/status', methods=['GET'])
        def server_status():
            """Get server status"""
            return jsonify({
                'status': 'online',
                'server_name': self.settings.get('server_name'),
                'version': '1.0.0',
                'uptime': time.time(),
                'resources': len(self.resources),
                'clients': len(self.clients),
                'active_allocations': len(self.allocations)
            })
        
        @self.app.route('/api/v1/resources', methods=['GET'])
        def list_resources():
            """List available resources"""
            if not self._authenticate_request():
                return jsonify({'error': 'Unauthorized'}), 401
            
            resource_type = request.args.get('type')
            status_filter = request.args.get('status')
            
            filtered_resources = []
            for resource in self.resources.values():
                if resource_type and resource['type'] != resource_type:
                    continue
                if status_filter and resource['status'] != status_filter:
                    continue
                filtered_resources.append(resource)
            
            return jsonify({
                'resources': filtered_resources,
                'total': len(filtered_resources)
            })
        
        @self.app.route('/api/v1/resources/<resource_id>/allocate', methods=['POST'])
        def allocate_resource(resource_id):
            """Allocate a resource"""
            if not self._authenticate_request():
                return jsonify({'error': 'Unauthorized'}), 401
            
            client_id = request.json.get('client_id')
            amount = request.json.get('amount', 0)
            properties = request.json.get('properties', {})
            
            if not client_id or resource_id not in self.resources:
                return jsonify({'error': 'Invalid request'}), 400
            
            return self._allocate_resource(resource_id, client_id, amount, properties)
        
        @self.app.route('/api/v1/resources/<resource_id>/release', methods=['POST'])
        def release_resource(resource_id):
            """Release a resource"""
            if not self._authenticate_request():
                return jsonify({'error': 'Unauthorized'}), 401
            
            client_id = request.json.get('client_id')
            allocation_id = request.json.get('allocation_id')
            
            if not client_id:
                return jsonify({'error': 'Invalid request'}), 400
            
            return self._release_resource(resource_id, client_id, allocation_id)
        
        @self.app.route('/api/v1/clients/register', methods=['POST'])
        def register_client():
            """Register a new client"""
            client_data = request.json
            
            required_fields = ['name', 'hostname', 'os_version', 'ip_address', 'mac_address']
            if not all(field in client_data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            return self._register_client(client_data)
        
        @self.app.route('/api/v1/clients/<client_id>/status', methods=['POST'])
        def update_client_status(client_id):
            """Update client status"""
            if not self._authenticate_request():
                return jsonify({'error': 'Unauthorized'}), 401
            
            status_data = request.json
            
            return self._update_client_status(client_id, status_data)
        
        @self.app.route('/api/v1/allocations', methods=['GET'])
        def list_allocations():
            """List resource allocations"""
            if not self._authenticate_request():
                return jsonify({'error': 'Unauthorized'}), 401
            
            client_id = request.args.get('client_id')
            
            filtered_allocations = []
            for allocation in self.allocations.values():
                if client_id and allocation['client_id'] != client_id:
                    continue
                filtered_allocations.append(allocation)
            
            return jsonify({
                'allocations': filtered_allocations,
                'total': len(filtered_allocations)
            })
        
        @self.app.route('/api/v1/monitoring/metrics', methods=['GET'])
        def get_metrics():
            """Get system monitoring metrics"""
            if not self._authenticate_request():
                return jsonify({'error': 'Unauthorized'}), 401
            
            return self._get_system_metrics()
        
        @self.app.route('/api/v1/auth/generate_key', methods=['POST'])
        def generate_api_key():
            """Generate API key for client"""
            client_data = request.json
            client_id = client_data.get('client_id')
            permissions = client_data.get('permissions', ['read'])
            
            if not client_id or client_id not in self.clients:
                return jsonify({'error': 'Invalid client'}), 400
            
            return self._generate_api_key(client_id, permissions)
    
    def _authenticate_request(self) -> bool:
        """Authenticate API request"""
        if not self.settings.get('enable_authentication', True):
            return True
        
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False
        
        # Check against stored API keys
        for key_data in self.api_keys.values():
            if hmac.compare_digest(key_data['key_hash'], hashlib.sha256(api_key.encode()).hexdigest()):
                # Update last used
                key_data['last_used'] = datetime.now().isoformat()
                return True
        
        return False
    
    def _allocate_resource(self, resource_id: str, client_id: str, amount: float, 
                         properties: Dict[str, Any]) -> flask.Response:
        """Allocate resource to client"""
        try:
            if resource_id not in self.resources:
                return jsonify({'error': 'Resource not found'}), 404
            
            resource = self.resources[resource_id]
            
            # Check if resource is available
            if resource['status'] != ResourceStatus.AVAILABLE.value:
                return jsonify({'error': 'Resource not available'}), 409
            
            # Check if allocation is possible
            available_capacity = resource['capacity'] - resource['allocated']
            if amount > available_capacity:
                return jsonify({'error': 'Insufficient capacity'}), 409
            
            # Create allocation
            allocation_id = f"alloc_{int(time.time())}_{secrets.token_hex(4)}"
            expires_at = datetime.now() + timedelta(seconds=self.settings.get('allocation_timeout', 7200))
            
            # Update resource
            resource['allocated'] += amount
            if resource['allocated'] >= resource['capacity']:
                resource['status'] = ResourceStatus.ALLOCATED.value
            
            # Store allocation
            self.allocations[allocation_id] = {
                'id': allocation_id,
                'resource_id': resource_id,
                'client_id': client_id,
                'amount': amount,
                'properties': properties,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'status': 'active'
            }
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO allocations 
                (id, client_id, resource_id, amount, properties, expires_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (allocation_id, client_id, resource_id, amount, 
                  json.dumps(properties), expires_at.isoformat(), 'active'))
            
            cursor.execute('''
                UPDATE resources SET allocated = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (resource['allocated'], resource['status'], datetime.now().isoformat(), resource_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Allocated {amount} of {resource_id} to client {client_id}")
            
            return jsonify({
                'allocation_id': allocation_id,
                'resource_id': resource_id,
                'amount': amount,
                'expires_at': expires_at.isoformat(),
                'status': 'active'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to allocate resource {resource_id}: {e}")
            return jsonify({'error': 'Allocation failed'}), 500
    
    def _release_resource(self, resource_id: str, client_id: str, allocation_id: str) -> flask.Response:
        """Release resource allocation"""
        try:
            if allocation_id not in self.allocations:
                return jsonify({'error': 'Allocation not found'}), 404
            
            allocation = self.allocations[allocation_id]
            
            if allocation['client_id'] != client_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            resource = self.resources[resource_id]
            
            # Update resource
            resource['allocated'] -= allocation['amount']
            if resource['allocated'] <= 0:
                resource['allocated'] = 0
                resource['status'] = ResourceStatus.AVAILABLE.value
            else:
                resource['status'] = ResourceStatus.AVAILABLE.value
            
            # Remove allocation
            del self.allocations[allocation_id]
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM allocations WHERE id = ?', (allocation_id,))
            cursor.execute('''
                UPDATE resources SET allocated = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (resource['allocated'], resource['status'], datetime.now().isoformat(), resource_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Released allocation {allocation_id} from client {client_id}")
            
            return jsonify({'status': 'released'})
            
        except Exception as e:
            self.logger.error(f"Failed to release resource {resource_id}: {e}")
            return jsonify({'error': 'Release failed'}), 500
    
    def _register_client(self, client_data: Dict[str, Any]) -> flask.Response:
        """Register new client"""
        try:
            client_id = f"client_{int(time.time())}_{secrets.token_hex(4)}"
            
            # Store client
            self.clients[client_id] = {
                'id': client_id,
                'name': client_data['name'],
                'hostname': client_data['hostname'],
                'os_version': client_data['os_version'],
                'ip_address': client_data['ip_address'],
                'mac_address': client_data['mac_address'],
                'status': 'online',
                'last_seen': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clients 
                (id, name, hostname, os_version, ip_address, mac_address, status, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, client_data['name'], client_data['hostname'],
                  client_data['os_version'], client_data['ip_address'],
                  client_data['mac_address'], 'online', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Registered client: {client_data['name']} ({client_id})")
            
            return jsonify({
                'client_id': client_id,
                'status': 'registered'
            })
            
        except Exception as e:
            self.logger.error(f"Failed to register client: {e}")
            return jsonify({'error': 'Registration failed'}), 500
    
    def _update_client_status(self, client_id: str, status_data: Dict[str, Any]) -> flask.Response:
        """Update client status"""
        try:
            if client_id not in self.clients:
                return jsonify({'error': 'Client not found'}), 404
            
            client = self.clients[client_id]
            client['status'] = status_data.get('status', 'online')
            client['last_seen'] = datetime.now().isoformat()
            
            # Update additional status data
            for key, value in status_data.items():
                if key != 'status':
                    client[key] = value
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE clients SET status = ?, last_seen = ? WHERE id = ?
            ''', (client['status'], client['last_seen'], client_id))
            
            conn.commit()
            conn.close()
            
            return jsonify({'status': 'updated'})
            
        except Exception as e:
            self.logger.error(f"Failed to update client status: {e}")
            return jsonify({'error': 'Update failed'}), 500
    
    def _get_system_metrics(self) -> flask.Response:
        """Get system monitoring metrics"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
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
                'network': [],
                'gpu': []
            }
            
            # Disk metrics
            for partition in psutil.disk_partitions():
                usage = psutil.disk_usage(partition.mountpoint)
                metrics['disk'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                })
            
            # Network metrics
            net_io = psutil.net_io_counters()
            metrics['network'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
            
            # GPU metrics
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    metrics['gpu'].append({
                        'id': gpu.id,
                        'name': gpu.name,
                        'load': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal,
                        'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                        'temperature': gpu.temperature
                    })
            except:
                pass
            
            return jsonify(metrics)
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return jsonify({'error': 'Failed to get metrics'}), 500
    
    def _generate_api_key(self, client_id: str, permissions: List[str]) -> flask.Response:
        """Generate API key for client"""
        try:
            if client_id not in self.clients:
                return jsonify({'error': 'Client not found'}), 404
            
            # Generate API key
            api_key = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            key_id = f"key_{int(time.time())}_{secrets.token_hex(4)}"
            
            # Store API key
            self.api_keys[key_id] = {
                'id': key_id,
                'client_id': client_id,
                'key_hash': key_hash,
                'permissions': permissions,
                'created_at': datetime.now().isoformat(),
                'expires_at': None,
                'last_used': None
            }
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_keys 
                (id, client_id, key_hash, permissions, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (key_id, client_id, key_hash, json.dumps(permissions), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Generated API key for client {client_id}")
            
            return jsonify({
                'api_key': api_key,
                'key_id': key_id,
                'permissions': permissions,
                'created_at': self.api_keys[key_id]['created_at']
            })
            
        except Exception as e:
            self.logger.error(f"Failed to generate API key: {e}")
            return jsonify({'error': 'Key generation failed'}), 500
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Resource monitoring loop"""
        while self.monitoring_active:
            try:
                # Check expired allocations
                self._cleanup_expired_allocations()
                
                # Update resource status
                self._update_resource_status()
                
                # Check client heartbeats
                self._check_client_heartbeats()
                
                # Sleep for monitoring interval
                time.sleep(self.settings.get('resource_check_interval', 30))
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def _cleanup_expired_allocations(self):
        """Clean up expired allocations"""
        current_time = datetime.now()
        expired_allocations = []
        
        for allocation_id, allocation in self.allocations.items():
            expires_at = datetime.fromisoformat(allocation['expires_at'])
            if current_time > expires_at:
                expired_allocations.append(allocation_id)
        
        for allocation_id in expired_allocations:
            allocation = self.allocations[allocation_id]
            resource_id = allocation['resource_id']
            client_id = allocation['client_id']
            
            # Release resource
            if resource_id in self.resources:
                self.resources[resource_id]['allocated'] -= allocation['amount']
                if self.resources[resource_id]['allocated'] <= 0:
                    self.resources[resource_id]['allocated'] = 0
                    self.resources[resource_id]['status'] = ResourceStatus.AVAILABLE.value
                else:
                    self.resources[resource_id]['status'] = ResourceStatus.AVAILABLE.value
            
            # Remove allocation
            del self.allocations[allocation_id]
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM allocations WHERE id = ?', (allocation_id,))
            cursor.execute('''
                UPDATE resources SET allocated = ?, status = ?, updated_at = ?
                WHERE id = ?
            ''', (self.resources[resource_id]['allocated'], 
                  self.resources[resource_id]['status'], 
                  current_time.isoformat(), resource_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Expired allocation {allocation_id} cleaned up")
    
    def _update_resource_status(self):
        """Update resource status based on current system state"""
        try:
            # This would involve checking actual resource availability
            # For now, just ensure consistency
            for resource_id, resource in self.resources.items():
                if resource['allocated'] >= resource['capacity']:
                    resource['status'] = ResourceStatus.ALLOCATED.value
                elif resource['allocated'] > 0:
                    resource['status'] = ResourceStatus.BUSY.value
                else:
                    resource['status'] = ResourceStatus.AVAILABLE.value
            
        except Exception as e:
            self.logger.error(f"Failed to update resource status: {e}")
    
    def _check_client_heartbeats(self):
        """Check client heartbeats and update status"""
        try:
            timeout_minutes = 5
            cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
            
            offline_clients = []
            
            for client_id, client in self.clients.items():
                if client['last_seen']:
                    last_seen = datetime.fromisoformat(client['last_seen'])
                    if last_seen < cutoff_time:
                        client['status'] = 'offline'
                        offline_clients.append(client_id)
            
            # Update database for offline clients
            if offline_clients:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                for client_id in offline_clients:
                    cursor.execute('UPDATE clients SET status = ? WHERE id = ?', 
                                 ('offline', client_id))
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Marked {len(offline_clients)} clients as offline")
            
        except Exception as e:
            self.logger.error(f"Failed to check client heartbeats: {e}")
    
    def run(self):
        """Run the server"""
        self.logger.info(f"Starting Homelab Server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False, threaded=True)

# Global server instance
homelab_server = HomelabServer()

if __name__ == '__main__':
    # Run the server
    homelab_server.run()
