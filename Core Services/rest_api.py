#!/usr/bin/env python3
"""
REST API for Homelab Core Services
Provides programmatic access to all unified system services
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from functools import wraps
import hashlib
import secrets
import psutil
from collections import deque
from pathlib import Path

# Add path handling
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import core services with availability checks
try:
    from event_bus import get_event_bus, EventType, EventPriority
    EVENT_BUS_AVAILABLE = True
except ImportError:
    EVENT_BUS_AVAILABLE = False

try:
    from config_manager import get_config_manager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False

try:
    from auth_service import get_auth_service
    AUTH_SERVICE_AVAILABLE = True
except ImportError:
    AUTH_SERVICE_AVAILABLE = False

try:
    from data_persistence import get_data_persistence
    DATA_PERSISTENCE_AVAILABLE = True
except ImportError:
    DATA_PERSISTENCE_AVAILABLE = False

try:
    from unified_monitoring import get_unified_monitoring, AlertSeverity, AlertStatus
    UNIFIED_MONITORING_AVAILABLE = True
except ImportError:
    UNIFIED_MONITORING_AVAILABLE = False

try:
    from bidirectional_resource_sharing import get_resource_sharing, ResourceType
    BIDIRECTIONAL_SHARING_AVAILABLE = True
except ImportError:
    BIDIRECTIONAL_SHARING_AVAILABLE = False

# Import portal components
try:
    from homelab_portal import HomelabPortal
    HOMELAB_PORTAL_AVAILABLE = True
except ImportError:
    HOMELAB_PORTAL_AVAILABLE = False

try:
    from nvidia_gpu_sharing import get_gpu_sharing
    NVIDIA_GPU_SHARING_AVAILABLE = True
except ImportError:
    NVIDIA_GPU_SHARING_AVAILABLE = False
try:
    from ddr4_ram_sharing import get_ddr4_ram_sharing
    DDR4_RAM_SHARING_AVAILABLE = True
except ImportError:
    DDR4_RAM_SHARING_AVAILABLE = False

try:
    from windows_screen_sharing import get_screen_sharing
    SCREEN_SHARING_AVAILABLE = True
except ImportError:
    SCREEN_SHARING_AVAILABLE = False

try:
    from identical_hardware_optimizer import get_identical_hardware_optimizer
    HARDWARE_OPTIMIZER_AVAILABLE = True
except ImportError:
    HARDWARE_OPTIMIZER_AVAILABLE = False

try:
    from portal_api_endpoints import PortalAPIEndpoints
    PORTAL_API_AVAILABLE = True
except ImportError:
    PORTAL_API_AVAILABLE = False

class HomelabRESTAPI:
    """REST API server for Homelab Core Services"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        
        self.host = host
        self.port = port
        
        # Initialize monitoring data
        self.monitoring_data = {
            'cpu_usage': deque(maxlen=60),
            'memory_usage': deque(maxlen=60),
            'network_usage': deque(maxlen=60),
            'temperature': deque(maxlen=60),
            'timestamps': deque(maxlen=60)
        }
        self.monitoring_active = False
        self.debug = debug
        
        # Initialize core services
        self.event_bus = get_event_bus()
        self.config_manager = get_config_manager()
        self.auth_service = get_auth_service()
        
        # Setup API routes
        self.setup_routes()
    
    def start_monitoring(self):
        """Start system monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            monitoring_thread = threading.Thread(target=self.monitor_system, daemon=True)
            monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
    
    def monitor_system(self):
        """Monitor system resources"""
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # CPU usage
                cpu_percent = psutil.cpu_percent()
                self.monitoring_data['cpu_usage'].append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.monitoring_data['memory_usage'].append(memory.percent)
                
                # Network usage
                network = psutil.net_io_counters()
                self.monitoring_data['network_usage'].append(network.bytes_sent + network.bytes_recv)
                
                # Temperature
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Get first available temperature
                        for name, entries in temps.items():
                            if entries and hasattr(entries[0], 'current'):
                                self.monitoring_data['temperature'].append(entries[0].current)
                                break
                except:
                    self.monitoring_data['temperature'].append(0)
                
                self.monitoring_data['timestamps'].append(current_time)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def setup_routes(self):
        """Setup all API routes"""
        
        # System endpoints
        @self.app.route('/api/system/status', methods=['GET'])
        def get_system_status():
            """Get system status"""
            return jsonify({
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'services': {
                    'event_bus': 'active',
                    'config_manager': 'active',
                    'auth_service': 'active',
                    'monitoring': 'active'
                }
            })
        
        @self.app.route('/api/system/info', methods=['GET'])
        def get_system_info():
            """Get detailed system information"""
            try:
                import psutil
                import platform
                
                return jsonify({
                    'system': {
                        'platform': platform.system(),
                        'version': platform.version(),
                        'architecture': platform.architecture()[0],
                        'processor': platform.processor()
                    },
                    'hardware': {
                        'cpu_count': psutil.cpu_count(),
                        'memory_total': psutil.virtual_memory().total,
                        'disk_total': psutil.disk_usage('/').total
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Monitoring endpoints
        @self.app.route('/api/monitoring/metrics', methods=['GET'])
        def get_monitoring_metrics():
            """Get current monitoring metrics"""
            try:
                monitoring = get_unified_monitoring()
                metrics = monitoring.get_current_metrics()
                return jsonify({
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/alerts', methods=['GET'])
        def get_monitoring_alerts():
            """Get monitoring alerts"""
            try:
                monitoring = get_unified_monitoring()
                alerts = monitoring.get_active_alerts()
                return jsonify({
                    'alerts': alerts,
                    'count': len(alerts),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/alerts', methods=['POST'])
        def create_monitoring_alert():
            """Create new monitoring alert"""
            try:
                data = request.get_json()
                monitoring = get_unified_monitoring()
                alert = monitoring.create_alert(
                    severity=AlertSeverity(data.get('severity', 'medium')),
                    message=data.get('message', ''),
                    source=data.get('source', 'api')
                )
                return jsonify({'alert_id': alert.id, 'status': 'created'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Resource sharing endpoints
        @self.app.route('/api/resources/sharing', methods=['GET'])
        def get_resource_sharing_status():
            """Get resource sharing status"""
            try:
                sharing = get_resource_sharing()
                status = sharing.get_sharing_status()
                return jsonify({
                    'sharing_status': status,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/resources/gpu', methods=['GET'])
        def get_gpu_resources():
            """Get GPU resource information"""
            try:
                gpu_sharing = get_gpu_sharing()
                resources = gpu_sharing.get_available_resources()
                return jsonify({
                    'gpu_resources': resources,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/resources/memory', methods=['GET'])
        def get_memory_resources():
            """Get memory resource information"""
            try:
                ram_sharing = get_ddr4_ram_sharing()
                resources = ram_sharing.get_available_resources()
                return jsonify({
                    'memory_resources': resources,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Configuration endpoints
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get system configuration"""
            try:
                config = self.config_manager.get_all_config()
                return jsonify({
                    'config': config,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config', methods=['PUT'])
        def update_config():
            """Update system configuration"""
            try:
                data = request.get_json()
                key = data.get('key')
                value = data.get('value')
                
                if not key or value is None:
                    return jsonify({'error': 'Key and value required'}), 400
                
                self.config_manager.set_config(key, value)
                return jsonify({'status': 'updated', 'key': key})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Event endpoints
        @self.app.route('/api/events', methods=['GET'])
        def get_events():
            """Get recent events"""
            try:
                limit = request.args.get('limit', 50, type=int)
                events = self.event_bus.get_recent_events(limit)
                return jsonify({
                    'events': events,
                    'count': len(events),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/events', methods=['POST'])
        def create_event():
            """Create new event"""
            try:
                data = request.get_json()
                event = self.event_bus.publish_sync(
                    EventType(data.get('type', 'info')),
                    'rest_api',
                    data.get('data', {}),
                    EventPriority(data.get('priority', 'normal'))
                )
                return jsonify({'event_id': event.id, 'status': 'created'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Windows Assistant endpoints
        @self.app.route('/api/devices/register', methods=['POST'])
        def register_assistant():
            """Register Windows Assistant"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'error': 'Assistant integration not available'}), 503
                
                data = request.get_json()
                result = self.portal.assistant_integration.register_assistant(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/devices/assistant', methods=['DELETE'])
        def unregister_assistant():
            """Unregister Windows Assistant"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'error': 'Assistant integration not available'}), 503
                
                device_id = request.args.get('device_id')
                if not device_id:
                    return jsonify({'error': 'device_id required'}), 400
                
                result = self.portal.assistant_integration.unregister_assistant(device_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/data/system', methods=['POST'])
        def receive_system_data():
            """Receive system data from Windows Assistant"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'error': 'Assistant integration not available'}), 503
                
                data = request.get_json()
                device_id = data.get('source', 'unknown')
                result = self.portal.assistant_integration.receive_system_data(device_id, data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/messages', methods=['POST'])
        def receive_assistant_message():
            """Receive message from Windows Assistant"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'error': 'Assistant integration not available'}), 503
                
                data = request.get_json()
                device_id = data.get('source', 'unknown')
                result = self.portal.assistant_integration.receive_message(device_id, data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assistants/status', methods=['GET'])
        def get_assistant_status():
            """Get Windows Assistant status"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'error': 'Assistant integration not available'}), 503
                
                device_id = request.args.get('device_id')
                result = self.portal.assistant_integration.get_assistant_status(device_id)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assistants/command', methods=['POST'])
        def send_assistant_command():
            """Send command to Windows Assistant"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'error': 'Assistant integration not available'}), 503
                
                data = request.get_json()
                device_id = data.get('device_id')
                command = data.get('command')
                
                if not device_id or not command:
                    return jsonify({'error': 'device_id and command required'}), 400
                
                result = self.portal.assistant_integration.send_command(device_id, command)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/actions/trigger', methods=['POST'])
        def trigger_portal_action():
            """Trigger action on Portal from Windows Assistant"""
            try:
                data = request.get_json()
                action = data.get('action')
                parameters = data.get('parameters', {})
                
                if not action:
                    return jsonify({'error': 'action required'}), 400
                
                # Handle different actions
                if action == 'start_monitoring':
                    self.portal.start_monitoring()
                elif action == 'stop_monitoring':
                    self.portal.stop_monitoring()
                elif action == 'restart_portal':
                    self.portal.restart_portal()
                elif action == 'get_system_info':
                    return jsonify({
                        'system_info': self.portal.get_system_info(),
                        'timestamp': datetime.now().isoformat()
                    })
                elif action == 'discovery_scan':
                    devices = self.portal.discover_devices()
                    return jsonify({'discovered_devices': devices})
                else:
                    return jsonify({'error': f'Unknown action: {action}'}), 400
                
                return jsonify({'success': True, 'action': action})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/assistant/integration', methods=['GET'])
        def get_integration_status():
            """Get Windows Assistant integration status"""
            try:
                if not self.portal.assistant_integration:
                    return jsonify({'integration_active': False})
                
                status = self.portal.assistant_integration.get_integration_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # Tool management endpoints
        @self.app.route('/api/tools', methods=['GET'])
        def get_tools():
            """Get available tools"""
            tools = [
                {
                    'name': 'CPU Monitor',
                    'path': 'Cpu Monitor/cpu_monitor.py',
                    'type': 'monitoring',
                    'status': 'available'
                },
                {
                    'name': 'GPU Monitor',
                    'path': 'Gpu Monitor/gpu_monitor.py',
                    'type': 'monitoring',
                    'status': 'available'
                },
                {
                    'name': 'Network Monitor',
                    'path': 'Network Monitor/network_monitor.py',
                    'type': 'monitoring',
                    'status': 'available'
                },
                {
                    'name': 'RAM Cleaner',
                    'path': 'Ram clean up/ram_monitor.py',
                    'type': 'utility',
                    'status': 'available'
                },
                {
                    'name': 'RDMA Tools',
                    'path': 'RDMA/rdma_tools.py',
                    'type': 'network',
                    'status': 'available'
                },
                {
                    'name': 'Storage Manager',
                    'path': 'Storage Management/storage_manager.py',
                    'type': 'storage',
                    'status': 'available'
                }
            ]
            return jsonify({
                'tools': tools,
                'count': len(tools),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/tools/<tool_name>/launch', methods=['POST'])
        def launch_tool(tool_name):
            """Launch a specific tool"""
            try:
                import subprocess
                import os
                
                # Map tool names to paths
                tool_paths = {
                    'cpu_monitor': 'Cpu Monitor/cpu_monitor.py',
                    'gpu_monitor': 'Gpu Monitor/gpu_monitor.py',
                    'network_monitor': 'Network Monitor/network_monitor.py',
                    'ram_cleaner': 'Ram clean up/ram_monitor.py',
                    'rdma_tools': 'RDMA/rdma_tools.py',
                    'storage_manager': 'Storage Management/storage_manager.py'
                }
                
                if tool_name not in tool_paths:
                    return jsonify({'error': 'Tool not found'}), 404
                
                tool_path = tool_paths[tool_name]
                if not os.path.exists(tool_path):
                    return jsonify({'error': 'Tool file not found'}), 404
                
                # Launch the tool
                subprocess.Popen(['python', tool_path])
                
                return jsonify({
                    'status': 'launched',
                    'tool': tool_name,
                    'path': tool_path,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Portal endpoints
        @self.app.route('/api/portal/status', methods=['GET'])
        def get_portal_status():
            """Get portal status"""
            try:
                portal = HomelabPortal()
                status = portal.get_status()
                return jsonify({
                    'portal_status': status,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/portal/devices', methods=['GET'])
        def get_portal_devices():
            """Get connected devices"""
            try:
                portal = HomelabPortal()
                devices = portal.get_connected_devices()
                return jsonify({
                    'devices': devices,
                    'count': len(devices),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Authentication endpoints
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            """User login"""
            try:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                if not username or not password:
                    return jsonify({'error': 'Username and password required'}), 400
                
                # Simple authentication (replace with proper auth)
                if username == 'admin' and password == 'admin':
                    token = secrets.token_hex(32)
                    return jsonify({
                        'token': token,
                        'user': username,
                        'expires': (datetime.now() + timedelta(hours=24)).isoformat()
                    })
                else:
                    return jsonify({'error': 'Invalid credentials'}), 401
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        def logout():
            """User logout"""
            return jsonify({'status': 'logged_out'})
        
        # Health check endpoint
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0'
            })
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
        self.data_persistence = get_data_persistence()
        self.unified_monitoring = get_unified_monitoring()
        self.resource_sharing = get_resource_sharing()
        
        # Initialize portal components
        self.portal = HomelabPortal()
        self.gpu_sharing = get_gpu_sharing(self.portal.node_id)
        self.ram_sharing = get_ddr4_ram_sharing(self.portal.node_id)
        self.screen_sharing = get_screen_sharing(self.portal.node_id)
        self.hardware_optimizer = get_identical_hardware_optimizer()
        
        # API keys and rate limiting
        self.api_keys = {}
        self.rate_limits = {}
        
        # Setup routes
        self._setup_routes()
        self.running = False
        self.server_thread = None
        
        # Setup logging
        self.logger = logging.getLogger("HomelabAPI")
        self.logger.setLevel(logging.INFO)
        
        # Rate limiting
        self.rate_limits = {}  # IP -> {last_request_time, request_count}
        self.rate_limit_window = 60  # 1 minute
        self.rate_limit_max_requests = 100  # 100 requests per minute
        
        # API Keys
        self.api_keys = {}  # key -> {user_id, created_at, permissions}
        
        # Setup core routes first
        self._setup_routes()
        
        # Register portal endpoints
        portal_endpoints = PortalAPIEndpoints(self)
        portal_endpoints.register_endpoints()
        
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Health check
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'services': {
                    'event_bus': 'running',
                    'config_manager': 'running',
                    'auth_service': 'running',
                    'data_persistence': 'running',
                    'unified_monitoring': 'running',
                    'resource_sharing': 'running',
                    'portal': 'running',
                    'gpu_sharing': 'running' if self.gpu_sharing.is_nvidia_available else 'not_available',
                    'ram_sharing': 'running' if self.ram_sharing.is_ddr4 else 'not_available',
                    'screen_sharing': 'running',
                    'hardware_optimizer': 'running'
                }
            })
        
        # Authentication endpoints
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            try:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                ip_address = request.remote_addr
                
                if not username or not password:
                    return jsonify({'error': 'Username and password required'}), 400
                
                session_id = self.auth_service.authenticate(username, password, ip_address, 'api')
                
                if session_id:
                    # Generate API key
                    api_key = self._generate_api_key(username)
                    self.api_keys[api_key] = {
                        'user_id': username,
                        'created_at': datetime.now().isoformat(),
                        'permissions': ['read', 'write']
                    }
                    
                    return jsonify({
                        'session_id': session_id,
                        'api_key': api_key,
                        'user': username,
                        'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
                    })
                else:
                    return jsonify({'error': 'Invalid credentials'}), 401
                    
            except Exception as e:
                self.logger.error(f"Login error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        @self._require_api_key
        def logout():
            try:
                api_key = request.headers.get('X-API-Key')
                user_id = self.api_keys.get(api_key, {}).get('user_id')
                
                if user_id:
                    self.auth_service.logout(user_id)
                    
                if api_key in self.api_keys:
                    del self.api_keys[api_key]
                
                return jsonify({'message': 'Logged out successfully'})
                
            except Exception as e:
                self.logger.error(f"Logout error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # Event Bus endpoints
        @self.app.route('/api/events', methods=['GET'])
        @self._require_api_key
        def get_events():
            try:
                event_type = request.args.get('type')
                limit = int(request.args.get('limit', 100))
                
                stats = self.event_bus.get_statistics()
                
                return jsonify({
                    'statistics': stats,
                    'event_types': [t.value for t in EventType],
                    'priorities': [p.value for p in EventPriority]
                })
                
            except Exception as e:
                self.logger.error(f"Get events error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/events', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def publish_event():
            try:
                data = request.get_json()
                event_type_str = data.get('type')
                source = data.get('source', 'api')
                event_data = data.get('data', {})
                priority_str = data.get('priority', 'medium')
                
                # Convert string to enum
                event_type = EventType(event_type_str)
                priority = EventPriority[priority_str.upper()]
                
                event_id = self.event_bus.publish_sync(event_type, source, event_data, priority)
                
                return jsonify({
                    'event_id': event_id,
                    'type': event_type_str,
                    'source': source,
                    'priority': priority_str,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Publish event error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # Configuration endpoints
        @self.app.route('/api/config', methods=['GET'])
        @self._require_api_key
        def get_config():
            try:
                key = request.args.get('key')
                
                if key:
                    value = self.config_manager.get(key)
                    return jsonify({'key': key, 'value': value})
                else:
                    # Get all config (with filtering for sensitive data)
                    all_config = self.config_manager.get_all()
                    filtered_config = {k: v for k, v in all_config.items() 
                                    if not any(sensitive in k.lower() 
                                              for sensitive in ['password', 'key', 'secret', 'token'])}
                    return jsonify(filtered_config)
                    
            except Exception as e:
                self.logger.error(f"Get config error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/config', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def set_config():
            try:
                data = request.get_json()
                key = data.get('key')
                value = data.get('value')
                description = data.get('description', '')
                source = data.get('source', 'api')
                
                if not key or value is None:
                    return jsonify({'error': 'Key and value required'}), 400
                
                success = self.config_manager.set(key, value, source, description)
                
                if success:
                    return jsonify({
                        'key': key,
                        'value': value,
                        'updated': True,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({'error': 'Failed to set configuration'}), 500
                    
            except Exception as e:
                self.logger.error(f"Set config error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # Data Persistence endpoints
        @self.app.route('/api/metrics', methods=['GET'])
        @self._require_api_key
        def get_metrics():
            try:
                source = request.args.get('source')
                metric_type = request.args.get('type')
                start_time = request.args.get('start_time')
                end_time = request.args.get('end_time')
                limit = int(request.args.get('limit', 1000))
                
                # Parse time parameters
                start_dt = datetime.fromisoformat(start_time) if start_time else None
                end_dt = datetime.fromisoformat(end_time) if end_time else None
                
                metrics = self.data_persistence.get_metrics(
                    source=source,
                    metric_type=metric_type,
                    start_time=start_dt,
                    end_time=end_dt,
                    limit=limit
                )
                
                return jsonify({
                    'metrics': metrics,
                    'count': len(metrics),
                    'filters': {
                        'source': source,
                        'type': metric_type,
                        'start_time': start_time,
                        'end_time': end_time
                    }
                })
                
            except Exception as e:
                self.logger.error(f"Get metrics error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/metrics', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def store_metric():
            try:
                data = request.get_json()
                source = data.get('source')
                metric_type = data.get('type')
                value = data.get('value')
                unit = data.get('unit', '')
                tags = data.get('tags', {})
                metadata = data.get('metadata', {})
                
                if not all([source, metric_type, value is not None]):
                    return jsonify({'error': 'source, type, and value required'}), 400
                
                success = self.data_persistence.store_metric(
                    source=source,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    tags=tags,
                    metadata=metadata
                )
                
                if success:
                    return jsonify({
                        'source': source,
                        'type': metric_type,
                        'value': value,
                        'unit': unit,
                        'stored': True,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({'error': 'Failed to store metric'}), 500
                    
            except Exception as e:
                self.logger.error(f"Store metric error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # Monitoring endpoints
        @self.app.route('/api/alerts', methods=['GET'])
        @self._require_api_key
        def get_alerts():
            try:
                severity = request.args.get('severity')
                status = request.args.get('status')
                limit = int(request.args.get('limit', 100))
                
                alerts = self.unified_monitoring.get_alerts(
                    severity=AlertSeverity[severity.upper()] if severity else None,
                    status=AlertStatus[status.upper()] if status else None,
                    limit=limit
                )
                
                return jsonify({
                    'alerts': alerts,
                    'count': len(alerts),
                    'filters': {
                        'severity': severity,
                        'status': status
                    }
                })
                
            except Exception as e:
                self.logger.error(f"Get alerts error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/alerts', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def create_alert():
            try:
                data = request.get_json()
                title = data.get('title')
                message = data.get('message', '')
                severity_str = data.get('severity', 'info')
                source = data.get('source', 'api')
                
                if not title:
                    return jsonify({'error': 'title required'}), 400
                
                severity = AlertSeverity[severity_str.upper()]
                alert_id = self.unified_monitoring.create_alert(title, message, severity, source)
                
                return jsonify({
                    'alert_id': alert_id,
                    'title': title,
                    'message': message,
                    'severity': severity_str,
                    'source': source,
                    'created': True,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Create alert error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def acknowledge_alert(alert_id):
            try:
                data = request.get_json()
                user = data.get('user', 'api_user')
                note = data.get('note', '')
                
                success = self.unified_monitoring.acknowledge_alert(alert_id, user, note)
                
                if success:
                    return jsonify({
                        'alert_id': alert_id,
                        'acknowledged': True,
                        'user': user,
                        'note': note,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({'error': 'Failed to acknowledge alert'}), 404
                    
            except Exception as e:
                self.logger.error(f"Acknowledge alert error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # Analytics endpoints
        @self.app.route('/api/analytics/events', methods=['GET'])
        def get_analytics_events():
            """Get analytics events"""
            try:
                # Import analytics engine
                from analytics_engine import get_analytics_engine
                
                analytics = get_analytics_engine()
                events = analytics.get_events(limit=100)
                
                return jsonify({
                    'events': events,
                    'count': len(events),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics/report', methods=['GET'])
        def generate_analytics_report():
            """Generate analytics report"""
            try:
                from analytics_engine import get_analytics_engine
                
                analytics = get_analytics_engine()
                report_type = request.args.get('type', 'summary')
                
                report = analytics.generate_report(report_type)
                
                return jsonify({
                    'report': report,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics/aggregations', methods=['GET'])
        def get_analytics_aggregations():
            """Get analytics aggregations"""
            try:
                from analytics_engine import get_analytics_engine
                
                analytics = get_analytics_engine()
                aggregations = analytics.get_recent_aggregations(limit=10)
                
                return jsonify({
                    'aggregations': aggregations,
                    'count': len(aggregations),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Automation endpoints
        @self.app.route('/api/automation/rules', methods=['GET'])
        def get_automation_rules():
            """Get automation rules"""
            try:
                from automation_framework import get_automation_framework
                
                automation = get_automation_framework(self.portal)
                rules = automation.get_rules()
                
                return jsonify({
                    'rules': rules,
                    'count': len(rules),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automation/rules', methods=['POST'])
        def create_automation_rule():
            """Create automation rule"""
            try:
                from automation_framework import get_automation_framework
                
                data = request.get_json()
                name = data.get('name')
                description = data.get('description', '')
                triggers = data.get('triggers', [])
                actions = data.get('actions', [])
                
                automation = get_automation_framework(self.portal)
                rule_id = automation.create_rule(name, description, triggers, actions)
                
                if rule_id:
                    return jsonify({
                        'success': True,
                        'rule_id': rule_id,
                        'message': 'Automation rule created'
                    })
                else:
                    return jsonify({'error': 'Failed to create rule'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/automation/rules/<rule_id>/run', methods=['POST'])
        def run_automation_rule(rule_id):
            """Run automation rule manually"""
            try:
                from automation_framework import get_automation_framework
                
                automation = get_automation_framework(self.portal)
                success = automation.run_rule_manually(rule_id)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Automation rule executed'
                    })
                else:
                    return jsonify({'error': 'Failed to run rule'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Security endpoints
        @self.app.route('/api/security/events', methods=['GET'])
        def get_security_events():
            """Get security events"""
            try:
                from advanced_security import get_advanced_security
                
                security = get_advanced_security()
                threat_level = request.args.get('threat_level')
                
                if threat_level:
                    from advanced_security import ThreatLevel
                    threat_level = ThreatLevel(threat_level)
                
                events = security.get_security_events(threat_level, limit=100)
                
                return jsonify({
                    'events': events,
                    'count': len(events),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/security/blocked-ips', methods=['GET'])
        def get_blocked_ips():
            """Get blocked IPs"""
            try:
                from advanced_security import get_advanced_security
                
                security = get_advanced_security()
                blocked_ips = security.get_blocked_ips()
                
                return jsonify({
                    'blocked_ips': blocked_ips,
                    'count': len(blocked_ips),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/security/summary', methods=['GET'])
        def get_security_summary():
            """Get security summary"""
            try:
                from advanced_security import get_advanced_security
                
                security = get_advanced_security()
                summary = security.get_security_summary()
                
                return jsonify({
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Resource Sharing endpoints
        @self.app.route('/api/resources/peers', methods=['GET'])
        @self._require_api_key
        def get_peers():
            try:
                status = self.resource_sharing.get_peer_status()
                return jsonify(status)
                
            except Exception as e:
                self.logger.error(f"Get peers error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/resources/offer', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def offer_resources():
            try:
                data = request.get_json()
                target_peer_id = data.get('target_peer_id')
                
                # This would be called asynchronously
                asyncio.create_task(self.resource_sharing.offer_resources(target_peer_id))
                
                return jsonify({
                    'action': 'offer_resources',
                    'target_peer_id': target_peer_id,
                    'initiated': True,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Offer resources error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/resources/request', methods=['POST'])
        @self._require_api_key
        @self._require_permission('write')
        def request_resource():
            try:
                data = request.get_json()
                resource_type_str = data.get('type')
                amount = data.get('amount')
                target_peer_id = data.get('target_peer_id')
                
                if not resource_type_str or amount is None:
                    return jsonify({'error': 'type and amount required'}), 400
                
                resource_type = ResourceType(resource_type_str)
                
                # This would be called asynchronously
                asyncio.create_task(self.resource_sharing.request_resource(
                    resource_type, amount, target_peer_id
                ))
                
                return jsonify({
                    'action': 'request_resource',
                    'type': resource_type_str,
                    'amount': amount,
                    'target_peer_id': target_peer_id,
                    'initiated': True,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Request resource error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # System status endpoint
        @self.app.route('/api/system/status', methods=['GET'])
        @self._require_api_key
        def system_status():
            try:
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'uptime': time.time(),
                    'services': {
                        'event_bus': self._get_service_status('event_bus'),
                        'config_manager': self._get_service_status('config_manager'),
                        'auth_service': self._get_service_status('auth_service'),
                        'data_persistence': self._get_service_status('data_persistence'),
                        'unified_monitoring': self._get_service_status('unified_monitoring'),
                        'resource_sharing': self._get_service_status('resource_sharing')
                    },
                    'database': self.data_persistence.get_database_stats(),
                    'monitoring': self.unified_monitoring.get_monitoring_stats(),
                    'resource_sharing': self.resource_sharing.get_peer_status()
                }
                
                return jsonify(status)
                
            except Exception as e:
                self.logger.error(f"System status error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
    
    def _generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        timestamp = str(int(time.time()))
        raw = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def _get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific service"""
        try:
            if service_name == 'event_bus':
                stats = self.event_bus.get_statistics()
                return {'status': 'running', 'stats': stats}
            elif service_name == 'config_manager':
                validation = self.config_manager.validate_config()
                return {'status': 'running', 'valid': validation['valid']}
            elif service_name == 'auth_service':
                return {'status': 'running'}
            elif service_name == 'data_persistence':
                stats = self.data_persistence.get_database_stats()
                return {'status': 'running', 'database_stats': stats}
            elif service_name == 'unified_monitoring':
                stats = self.unified_monitoring.get_monitoring_stats()
                return {'status': 'running', 'monitoring_stats': stats}
            elif service_name == 'resource_sharing':
                status = self.resource_sharing.get_peer_status()
                return {'status': 'running', 'peer_status': status}
            else:
                return {'status': 'unknown'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _require_api_key(self, f):
        """Decorator to require API key"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            if api_key not in self.api_keys:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Check rate limiting
            if not self._check_rate_limit(request.remote_addr):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    
    def _require_permission(self, permission: str):
        """Decorator to require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get('X-API-Key')
                user_permissions = self.api_keys.get(api_key, {}).get('permissions', [])
                
                if permission not in user_permissions:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def _check_rate_limit(self, ip_address: str) -> bool:
        """Check if IP address is within rate limits"""
        current_time = time.time()
        
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = {
                'last_request_time': current_time,
                'request_count': 1,
                'window_start': current_time
            }
            return True
        
        rate_info = self.rate_limits[ip_address]
        
        # Reset window if needed
        if current_time - rate_info['window_start'] > self.rate_limit_window:
            rate_info['request_count'] = 0
            rate_info['window_start'] = current_time
        
        # Check rate limit
        if rate_info['request_count'] >= self.rate_limit_max_requests:
            return False
        
        # Update rate info
        rate_info['request_count'] += 1
        rate_info['last_request_time'] = current_time
        
        return True
    
    def start(self):
        """Start the API server"""
        if self.running:
            self.logger.warning("API server is already running")
            return
        
        def run_server():
            self.app.run(host=self.host, port=self.port, debug=self.debug, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        self.logger.info(f"REST API server started on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the API server"""
        if not self.running:
            return
        
        self.running = False
        # Note: Flask doesn't provide a clean way to stop the server from code
        # This would typically be handled by the process manager
        self.logger.info("REST API server stopped")

# Global API instance
_api_instance = None

def get_api() -> HomelabRESTAPI:
    """Get global API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = HomelabRESTAPI()
    return _api_instance

def start_api_server(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    """Start the API server"""
    api = get_api()
    api.host = host
    api.port = port
    api.debug = debug
    api.start()
    return api

if __name__ == "__main__":
    # Run API server directly
    api = start_api_server(debug=True)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down API server...")
        api.stop()
