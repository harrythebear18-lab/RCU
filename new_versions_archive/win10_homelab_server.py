#!/usr/bin/env python3
"""
Windows 10 Homelab Server
Optimized for Windows 10 Home to host shared resources for Windows 11 clients.
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
import platform
import logging
from enum import Enum

# Add RDMA integration
try:
    from rdma_integration import rdma_integration, RDMA_AVAILABLE
    RDMA_INTEGRATION_AVAILABLE = True
except ImportError:
    RDMA_INTEGRATION_AVAILABLE = False
    rdma_integration = None

# Windows 10 compatible imports
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
    wmi_client = wmi.WMI()
except ImportError:
    WMI_AVAILABLE = False
    wmi_client = None

class ResourceType(Enum):
    """Resource types available on Windows 10 server"""
    ERAM = "eram"
    EGPU = "egpu"
    ECPU = "ecpu"
    ESTORAGE = "estorage"
    ENETWORK = "enetwork"
    ERDMA = "erdma"

class ResourceStatus(Enum):
    """Resource status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class Windows10HomelabServer:
    """Windows 10 optimized homelab server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.db_path = os.path.join(os.path.dirname(__file__), 'win10_homelab_server.db')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'win10_server_settings.json')
        
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
        
        # Get Windows 10 system info
        self.system_info = self.get_windows10_info()
        
        # Initialize resources
        self.initialize_win10_resources()
        
        # Initialize RDMA integration
        self.initialize_rdma_integration()
        
        # Load clients and API keys
        self.load_clients()
        self.load_api_keys()
        
        # Start monitoring thread
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()
        
        # Simple HTTP server (Windows 10 compatible)
        self.http_server = None
        self.setup_http_server()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load Windows 10 server settings"""
        default_settings = {
            'server_name': 'Windows 10 Homelab Server',
            'max_clients': 5,  # Conservative for Win10 Home
            'session_timeout': 3600,
            'allocation_timeout': 7200,
            'resource_check_interval': 60,  # Longer intervals for Win10
            'enable_authentication': True,
            'enable_encryption': False,  # Disable for simplicity on Win10
            'log_level': 'INFO',
            'backup_interval': 7200,
            'max_eram_allocation_gb': 16,  # Conservative for Win10
            'enable_egpu_passthrough': True,
            'enable_load_balancing': True,
            'auto_cleanup': True,
            'win10_optimizations': True,
            'compatibility_mode': True
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
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """Setup server logging"""
        self.logger = logging.getLogger('Win10HomelabServer')
        
        log_level = getattr(logging, self.settings.get('log_level', 'INFO').upper())
        self.logger.setLevel(log_level)
        
        # Create file handler
        log_file = os.path.join(os.path.dirname(__file__), 'win10_homelab_server.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def get_windows10_info(self) -> Dict[str, Any]:
        """Get Windows 10 system information"""
        try:
            system_info = {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': socket.gethostname(),
                'ip_address': self.get_local_ip(),
                'is_windows_10': 'Windows-10' in platform.platform()
            }
            
            # Hardware info
            system_info.update({
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_total': self.get_total_disk_space(),
                'boot_time': psutil.boot_time()
            })
            
            # Windows 10 specific info
            if WMI_AVAILABLE:
                try:
                    computer_system = wmi_client.Win32_ComputerSystem()[0]
                    system_info.update({
                        'manufacturer': computer_system.Manufacturer,
                        'model': computer_system.Model,
                        'total_physical_memory': computer_system.TotalPhysicalMemory
                    })
                    
                    # Get GPU info via WMI
                    gpu_info = []
                    for gpu in wmi_client.Win32_VideoController():
                        gpu_info.append({
                            'name': gpu.Name,
                            'adapter_ram': gpu.AdapterRAM,
                            'driver_version': gpu.DriverVersion
                        })
                    system_info['gpus'] = gpu_info
                    
                except Exception as e:
                    self.logger.warning(f"WMI query failed: {e}")
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Failed to get Windows 10 info: {e}")
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
    
    def get_total_disk_space(self) -> int:
        """Get total disk space"""
        try:
            total_space = 0
            for partition in psutil.disk_partitions():
                if psutil.disk_usage(partition.mountpoint).total > 0:
                    total_space += psutil.disk_usage(partition.mountpoint).total
            return total_space
        except:
            return 0
    
    def initialize_win10_resources(self):
        """Initialize Windows 10 specific resources"""
        self.logger.info("Initializing Windows 10 resources...")
        
        # Initialize eRAM resources
        self._initialize_win10_eram()
        
        # Initialize eGPU resources
        self._initialize_win10_egpu()
        
        # Initialize eCPU resources
        self._initialize_win10_ecpu()
        
        # Initialize storage resources
        self._initialize_win10_storage()
        
        # Initialize network resources
        self._initialize_win10_network()
        
        self.logger.info(f"Initialized {len(self.resources)} Windows 10 resources")
    
    def _initialize_win10_eram(self):
        """Initialize eRAM resources for Windows 10"""
        try:
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            available_memory_gb = memory.available / (1024**3)
            
            # Conservative eRAM pools for Windows 10
            max_eram = self.settings.get('max_eram_allocation_gb', 16)
            usable_memory = min(available_memory_gb * 0.3, max_eram)  # Use 30% of available RAM
            
            if usable_memory > 1:  # Only create if we have at least 1GB
                eram_pools = [
                    {
                        'id': 'win10_eram_small',
                        'name': 'Win10 eRAM Small Pool',
                        'capacity': min(2, usable_memory * 0.3),
                        'properties': {
                            'pool_size': 'small',
                            'priority': 'low',
                            'max_allocation_gb': 2,
                            'win10_optimized': True
                        }
                    },
                    {
                        'id': 'win10_eram_medium',
                        'name': 'Win10 eRAM Medium Pool',
                        'capacity': min(4, usable_memory * 0.5),
                        'properties': {
                            'pool_size': 'medium',
                            'priority': 'medium',
                            'max_allocation_gb': 4,
                            'win10_optimized': True
                        }
                    },
                    {
                        'id': 'win10_eram_large',
                        'name': 'Win10 eRAM Large Pool',
                        'capacity': min(8, usable_memory * 0.7),
                        'properties': {
                            'pool_size': 'large',
                            'priority': 'high',
                            'max_allocation_gb': 8,
                            'win10_optimized': True
                        }
                    }
                ]
                
                for pool in eram_pools:
                    if pool['capacity'] > 0.5:  # Only create pools with meaningful capacity
                        self._register_resource(
                            resource_id=pool['id'],
                            name=pool['name'],
                            resource_type=ResourceType.ERAM,
                            capacity=pool['capacity'],
                            properties=pool['properties']
                        )
            
            self.logger.info(f"Initialized Win10 eRAM pools with {usable_memory:.1f}GB total capacity")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Win10 eRAM: {e}")
    
    def _initialize_win10_egpu(self):
        """Initialize eGPU resources for Windows 10"""
        try:
            gpu_resources = []
            
            # Use WMI for GPU detection (Windows 10 compatible)
            if WMI_AVAILABLE:
                try:
                    for gpu in wmi_client.Win32_VideoController():
                        if gpu.AdapterRAM and gpu.AdapterRAM > 0:  # Only include GPUs with memory
                            memory_gb = gpu.AdapterRAM / (1024**3)
                            
                            gpu_resources.append({
                                'id': f'win10_egpu_{gpu.Name.replace(" ", "_").replace("/", "_")}',
                                'name': f'Win10 eGPU {gpu.Name}',
                                'capacity': memory_gb,
                                'properties': {
                                    'gpu_type': 'wmi_detected',
                                    'adapter_ram': gpu.AdapterRAM,
                                    'driver_version': gpu.DriverVersion,
                                    'device_id': gpu.DeviceID,
                                    'win10_optimized': True,
                                    'supports_passthrough': True
                                }
                            })
                except Exception as e:
                    self.logger.warning(f"WMI GPU detection failed: {e}")
            
            # Fallback to GPUtil if available
            if GPU_AVAILABLE and not gpu_resources:
                try:
                    gpus = GPUtil.getGPUs()
                    for gpu in gpus:
                        gpu_resources.append({
                            'id': f'win10_egpu_gpu_{gpu.id}',
                            'name': f'Win10 eGPU {gpu.name}',
                            'capacity': gpu.memoryTotal / 1024,  # Convert MB to GB
                            'properties': {
                                'gpu_type': 'gputil_detected',
                                'device_id': gpu.id,
                                'memory_total': gpu.memoryTotal,
                                'driver_version': gpu.driver,
                                'temperature': gpu.temperature,
                                'win10_optimized': True
                            }
                        })
                except Exception as e:
                    self.logger.warning(f"GPUtil GPU detection failed: {e}")
            
            # Register GPU resources
            for gpu in gpu_resources:
                self._register_resource(
                    resource_id=gpu['id'],
                    name=gpu['name'],
                    resource_type=ResourceType.EGPU,
                    capacity=gpu['capacity'],
                    properties=gpu['properties']
                )
            
            self.logger.info(f"Initialized {len(gpu_resources)} Win10 eGPU resources")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Win10 eGPU: {e}")
    
    def _initialize_win10_ecpu(self):
        """Initialize eCPU resources for Windows 10"""
        try:
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Conservative CPU allocation for Windows 10
            max_cpu_allocation = cpu_count * 0.5  # Use up to 50% of CPU cores
            
            cpu_pools = [
                {
                    'id': 'win10_ecpu_light',
                    'name': 'Win10 eCPU Light Pool',
                    'capacity': min(1, max_cpu_allocation * 0.3),
                    'properties': {
                        'pool_type': 'light',
                        'max_cores': 1,
                        'priority': 'low',
                        'frequency': cpu_freq.current if cpu_freq else 0,
                        'win10_optimized': True
                    }
                },
                {
                    'id': 'win10_ecpu_medium',
                    'name': 'Win10 eCPU Medium Pool',
                    'capacity': min(2, max_cpu_allocation * 0.5),
                    'properties': {
                        'pool_type': 'medium',
                        'max_cores': 2,
                        'priority': 'medium',
                        'frequency': cpu_freq.current if cpu_freq else 0,
                        'win10_optimized': True
                    }
                },
                {
                    'id': 'win10_ecpu_heavy',
                    'name': 'Win10 eCPU Heavy Pool',
                    'capacity': min(4, max_cpu_allocation * 0.7),
                    'properties': {
                        'pool_type': 'heavy',
                        'max_cores': 4,
                        'priority': 'high',
                        'frequency': cpu_freq.current if cpu_freq else 0,
                        'win10_optimized': True
                    }
                }
            ]
            
            for pool in cpu_pools:
                if pool['capacity'] > 0.5:  # Only create meaningful pools
                    self._register_resource(
                        resource_id=pool['id'],
                        name=pool['name'],
                        resource_type=ResourceType.ECPU,
                        capacity=pool['capacity'],
                        properties=pool['properties']
                    )
            
            self.logger.info(f"Initialized Win10 eCPU pools with {max_cpu_allocation:.1f} cores total")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Win10 eCPU: {e}")
    
    def _initialize_win10_storage(self):
        """Initialize storage resources for Windows 10"""
        try:
            disk_partitions = psutil.disk_partitions()
            
            for partition in disk_partitions:
                if partition.device and partition.mountpoint:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        free_gb = usage.free / (1024**3)
                        
                        # Only create storage pools with significant free space
                        if free_gb > 5:  # At least 5GB free
                            self._register_resource(
                                resource_id=f'win10_estorage_{partition.device.replace(":", "").replace("\\", "_")}',
                                name=f'Win10 eStorage {partition.device}',
                                resource_type=ResourceType.ESTORAGE,
                                capacity=free_gb * 0.5,  # Share 50% of free space
                                properties={
                                    'device': partition.device,
                                    'mountpoint': partition.mountpoint,
                                    'fstype': partition.fstype,
                                    'total_space': usage.total / (1024**3),
                                    'free_space': free_gb,
                                    'used_space': usage.used / (1024**3),
                                    'win10_optimized': True
                                }
                            )
                    except:
                        continue
            
            self.logger.info("Initialized Win10 storage resources")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Win10 storage: {e}")
    
    def _initialize_win10_network(self):
        """Initialize network resources for Windows 10"""
        try:
            network_interfaces = psutil.net_if_addrs()
            network_stats = psutil.net_if_stats()
            
            for interface_name, addresses in network_interfaces.items():
                if interface_name in network_stats:
                    stats = network_stats[interface_name]
                    
                    # Only include active interfaces
                    if stats.isup and stats.speed > 0:
                        self._register_resource(
                            resource_id=f'win10_enetwork_{interface_name}',
                            name=f'Win10 eNetwork {interface_name}',
                            resource_type=ResourceType.ENETWORK,
                            capacity=stats.speed / 1000,  # Convert to Mbps
                            properties={
                                'interface': interface_name,
                                'speed': stats.speed,
                                'mtu': stats.mtu,
                                'duplex': stats.duplex,
                                'addresses': [addr.address for addr in addresses],
                                'win10_optimized': True
                            }
                        )
            
            self.logger.info("Initialized Win10 network resources")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Win10 network: {e}")
    
    def initialize_rdma_integration(self):
        """Initialize RDMA integration for homelab"""
        try:
            if RDMA_INTEGRATION_AVAILABLE:
                self.logger.info("Initializing RDMA integration...")
                
                # Start RDMA services if auto-start is enabled
                rdma_settings = rdma_integration.settings
                if rdma_settings.get('auto_start', False):
                    if rdma_integration.start_rdma_services():
                        self.logger.info("RDMA services started successfully")
                    else:
                        self.logger.warning("Failed to start RDMA services")
                
                # Get RDMA status
                rdma_status = rdma_integration.get_status()
                self.logger.info(f"RDMA integration status: {rdma_status['status']}")
                
                # RDMA resources are automatically registered by the integration
                self.logger.info("RDMA integration initialized successfully")
            else:
                self.logger.warning("RDMA integration not available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize RDMA integration: {e}")
    
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
    
    def setup_http_server(self):
        """Setup simple HTTP server for Windows 10 compatibility"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            from urllib.parse import urlparse, parse_qs
            import json
            
            class Win10APIHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, server_instance=None, **kwargs):
                    self.server_instance = server_instance
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    self.handle_request('GET')
                
                def do_POST(self):
                    self.handle_request('POST')
                
                def do_OPTIONS(self):
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
                    self.end_headers()
                
                def handle_request(self, method):
                    try:
                        parsed_path = urlparse(self.path)
                        path = parsed_path.path
                        
                        # CORS headers
                        self.send_header('Access-Control-Allow-Origin', '*')
                        
                        # Route handling
                        if path == '/api/v1/server/status':
                            self.handle_server_status()
                        elif path == '/api/v1/resources':
                            self.handle_list_resources(parsed_path.query)
                        elif path.startswith('/api/v1/resources/') and method == 'POST':
                            self.handle_resource_allocation(path)
                        elif path.startswith('/api/v1/clients/'):
                            self.handle_client_request(path, method)
                        elif path == '/api/v1/allocations':
                            self.handle_list_allocations()
                        elif path == '/api/v1/monitoring/metrics':
                            self.handle_metrics()
                        elif path == '/api/v1/rdma/status':
                            self.handle_rdma_status()
                        else:
                            self.send_error(404, "Endpoint not found")
                    
                    except Exception as e:
                        self.send_error(500, f"Internal server error: {e}")
                
                def handle_server_status(self):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    response = {
                        'status': 'online',
                        'server_name': self.server_instance.settings.get('server_name'),
                        'version': '1.0.0',
                        'platform': 'Windows 10',
                        'uptime': time.time(),
                        'resources': len(self.server_instance.resources),
                        'clients': len(self.server_instance.clients),
                        'active_allocations': len(self.server_instance.allocations)
                    }
                    
                    self.send_json_response(response)
                
                def handle_list_resources(self, query):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    params = parse_qs(query)
                    resource_type = params.get('type', [None])[0]
                    status_filter = params.get('status', [None])[0]
                    
                    filtered_resources = []
                    for resource in self.server_instance.resources.values():
                        if resource_type and resource['type'] != resource_type:
                            continue
                        if status_filter and resource['status'] != status_filter:
                            continue
                        filtered_resources.append(resource)
                    
                    response = {
                        'resources': filtered_resources,
                        'total': len(filtered_resources)
                    }
                    
                    self.send_json_response(response)
                
                def handle_client_request(self, path, method):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    # Parse client ID from path
                    path_parts = path.split('/')
                    if len(path_parts) < 4:
                        self.send_error(400, "Invalid client request")
                        return
                    
                    client_id = path_parts[3]
                    action = path_parts[4] if len(path_parts) > 4 else None
                    
                    if method == 'POST' and action == 'register':
                        self.handle_register_client()
                    elif method == 'POST' and action == 'status':
                        self.handle_update_client_status(client_id)
                    else:
                        self.send_error(404, "Client action not found")
                
                def handle_register_client(self):
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    client_data = json.loads(post_data.decode('utf-8'))
                    
                    required_fields = ['name', 'hostname', 'os_version', 'ip_address', 'mac_address']
                    if not all(field in client_data for field in required_fields):
                        self.send_error(400, "Missing required fields")
                        return
                    
                    client_id = f"win10_client_{int(time.time())}_{secrets.token_hex(4)}"
                    
                    client_info = {
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
                    
                    # Save client
                    self.server_instance.clients[client_id] = client_info
                    
                    # Save to database
                    conn = sqlite3.connect(self.server_instance.db_path)
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
                    
                    # Generate API key
                    api_key = secrets.token_urlsafe(32)
                    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
                    
                    key_id = f"win10_key_{int(time.time())}_{secrets.token_hex(4)}"
                    
                    self.server_instance.api_keys[key_id] = {
                        'id': key_id,
                        'client_id': client_id,
                        'key_hash': key_hash,
                        'permissions': ['read', 'allocate', 'release'],
                        'created_at': datetime.now().isoformat(),
                        'expires_at': None,
                        'last_used': None
                    }
                    
                    # Save API key
                    cursor.execute('''
                        INSERT INTO api_keys 
                        (id, client_id, key_hash, permissions, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (key_id, client_id, key_hash, json.dumps(['read', 'allocate', 'release']), 
                          datetime.now().isoformat()))
                    
                    conn.commit()
                    conn.close()
                    
                    response = {
                        'client_id': client_id,
                        'api_key': api_key,
                        'key_id': key_id,
                        'status': 'registered'
                    }
                    
                    self.send_json_response(response)
                
                def handle_update_client_status(self, client_id):
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    status_data = json.loads(post_data.decode('utf-8'))
                    
                    if client_id not in self.server_instance.clients:
                        self.send_error(404, "Client not found")
                        return
                    
                    client = self.server_instance.clients[client_id]
                    client['status'] = status_data.get('status', 'online')
                    client['last_seen'] = datetime.now().isoformat()
                    
                    # Update database
                    conn = sqlite3.connect(self.server_instance.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE clients SET status = ?, last_seen = ? WHERE id = ?
                    ''', (client['status'], client['last_seen'], client_id))
                    
                    conn.commit()
                    conn.close()
                    
                    response = {'status': 'updated'}
                    self.send_json_response(response)
                
                def handle_list_allocations(self):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    params = parse_qs(urlparse(self.path).query)
                    client_id = params.get('client_id', [None])[0]
                    
                    filtered_allocations = []
                    for allocation in self.server_instance.allocations.values():
                        if client_id and allocation['client_id'] != client_id:
                            continue
                        filtered_allocations.append(allocation)
                    
                    response = {
                        'allocations': filtered_allocations,
                        'total': len(filtered_allocations)
                    }
                    
                    self.send_json_response(response)
                
                def handle_metrics(self):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    metrics = self.server_instance.get_system_metrics()
                    self.send_json_response(metrics)
                
                def handle_resource_allocation(self, path):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    # Extract resource ID from path
                    resource_id = path.split('/')[-1]
                    
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    request_data = json.loads(post_data.decode('utf-8'))
                    
                    client_id = request_data.get('client_id')
                    amount = request_data.get('amount', 0)
                    properties = request_data.get('properties', {})
                    
                    if not client_id:
                        self.send_error(400, "Missing client_id")
                        return
                    
                    # Handle RDMA resource allocation
                    if resource_id.startswith('win10_rdma_') and RDMA_INTEGRATION_AVAILABLE:
                        allocation = rdma_integration.allocate_rdma_resource(resource_id, amount, client_id, properties)
                        if allocation:
                            response = {
                                'allocation_id': allocation['allocation_id'],
                                'resource_id': resource_id,
                                'amount': amount,
                                'connection_id': allocation.get('connection_id'),
                                'expires_at': allocation['expires_at'],
                                'status': 'active',
                                'properties': allocation.get('properties', {})
                            }
                            self.send_json_response(response)
                        else:
                            self.send_error(409, "RDMA resource not available")
                        return
                    
                    # Handle regular resource allocation
                    if resource_id not in self.server_instance.resources:
                        self.send_error(404, "Resource not found")
                        return
                    
                    return self.server_instance._allocate_resource(resource_id, client_id, amount, properties)
                
                def handle_rdma_status(self):
                    if not self.authenticate():
                        self.send_error(401, "Unauthorized")
                        return
                    
                    if RDMA_INTEGRATION_AVAILABLE:
                        rdma_status = rdma_integration.get_status()
                        rdma_metrics = rdma_integration.get_rdma_metrics()
                        
                        response = {
                            'rdma_available': True,
                            'status': rdma_status['status'],
                            'services': rdma_status['services'],
                            'resource_pools': rdma_status['resource_pools'],
                            'performance_metrics': rdma_metrics,
                            'settings': rdma_status['settings']
                        }
                    else:
                        response = {
                            'rdma_available': False,
                            'status': 'not_available',
                            'message': 'RDMA integration not available'
                        }
                    
                    self.send_json_response(response)
                
                def authenticate(self):
                    api_key = self.headers.get('X-API-Key')
                    if not api_key:
                        return False
                    
                    # Check against stored API keys
                    for key_data in self.server_instance.api_keys.values():
                        if hmac.compare_digest(key_data['key_hash'], hashlib.sha256(api_key.encode()).hexdigest()):
                            # Update last used
                            key_data['last_used'] = datetime.now().isoformat()
                            return True
                    
                    return False
                
                def send_json_response(self, data):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode('utf-8'))
                
                def log_message(self, format, *args):
                    # Suppress default HTTP logging
                    pass
            
            # Create HTTP server
            handler_class = lambda *args, **kwargs: Win10APIHandler(*args, server_instance=self, **kwargs)
            self.http_server = HTTPServer((self.host, self.port), handler_class)
            
            self.logger.info(f"Windows 10 HTTP server created on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup HTTP server: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system monitoring metrics"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'platform': 'Windows 10',
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
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Windows 10 resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Windows 10 resource monitoring stopped")
    
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
                time.sleep(self.settings.get('resource_check_interval', 60))
                
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
        """Run the Windows 10 server"""
        self.logger.info(f"Starting Windows 10 Homelab Server on {self.host}:{self.port}")
        self.logger.info(f"Platform: {self.system_info.get('platform', 'Unknown')}")
        self.logger.info(f"Available Resources: {len(self.resources)}")
        
        try:
            if self.http_server:
                self.http_server.serve_forever()
            else:
                self.logger.error("HTTP server not initialized")
        except KeyboardInterrupt:
            self.logger.info("Server shutting down...")
        finally:
            self.stop_monitoring()
            if self.http_server:
                self.http_server.shutdown()

# Global server instance
win10_homelab_server = Windows10HomelabServer()

if __name__ == '__main__':
    # Run the Windows 10 server
    print("[MONITOR]  Starting Windows 10 Homelab Server...")
    print(f"[CHART] System: {win10_homelab_server.system_info.get('platform', 'Unknown')}")
    print(f"[SAVE] Available Resources: {len(win10_homelab_server.resources)}")
    print(f"[WEB] Server URL: http://{win10_homelab_server.get_local_ip()}:8080")
    print("\n[ROCKET] Server is ready to host resources for Windows 11 clients!")
    print("Press Ctrl+C to stop the server.\n")
    
    win10_homelab_server.run()
