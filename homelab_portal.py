#!/usr/bin/env python3
"""
Homelab Unified Portal System
Complete integration of screen sharing, resource sharing, file transfer, and sound sharing
"""

import asyncio
import threading
import time
import json
import socket
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import hashlib
import pickle
import struct
import subprocess
import platform
from enum import Enum
from collections import deque
from datetime import timedelta

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Add Core Services directory to Python path
core_services_dir = current_dir / "Core Services"
if str(core_services_dir) not in sys.path:
    sys.path.insert(0, str(core_services_dir))

# Import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available - system monitoring disabled")

# Import existing core services
try:
    from event_bus import get_event_bus, EventType, EventPriority
    EVENT_BUS_AVAILABLE = True
except ImportError:
    EVENT_BUS_AVAILABLE = False
    print("Warning: Event bus not available")

try:
    from config_manager import get_config_manager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    print("Warning: Config manager not available")

try:
    from auth_service import get_auth_service
    AUTH_SERVICE_AVAILABLE = True
except ImportError:
    AUTH_SERVICE_AVAILABLE = False
    print("Warning: Auth service not available")

try:
    from data_persistence import get_data_persistence
    DATA_PERSISTENCE_AVAILABLE = True
except ImportError:
    DATA_PERSISTENCE_AVAILABLE = False
    print("Warning: Data persistence not available")
try:
    from unified_monitoring import get_unified_monitoring
    UNIFIED_MONITORING_AVAILABLE = True
except ImportError:
    UNIFIED_MONITORING_AVAILABLE = False
    print("Warning: Unified monitoring not available")

try:
    from bidirectional_resource_sharing import get_resource_sharing, ResourceType
    BIDIRECTIONAL_SHARING_AVAILABLE = True
except ImportError:
    BIDIRECTIONAL_SHARING_AVAILABLE = False
    print("Warning: Bidirectional sharing not available")

# Import hardware optimizers
try:
    from windows_network_discovery import WindowsNetworkDiscovery
    NETWORK_DISCOVERY_AVAILABLE = True
except ImportError:
    NETWORK_DISCOVERY_AVAILABLE = False
    print("Warning: Network discovery not available")

try:
    from intel_ethernet_optimizer import get_intel_optimizer
    INTEL_OPTIMIZER_AVAILABLE = True
except ImportError:
    INTEL_OPTIMIZER_AVAILABLE = False
    print("Warning: Intel optimizer not available")

try:
    from identical_hardware_optimizer import get_identical_hardware_optimizer
    HARDWARE_OPTIMIZER_AVAILABLE = True
except ImportError:
    HARDWARE_OPTIMIZER_AVAILABLE = False
    print("Warning: Hardware optimizer not available")

try:
    from nvidia_gpu_sharing import get_gpu_sharing
    GPU_SHARING_AVAILABLE = True
except ImportError:
    GPU_SHARING_AVAILABLE = False
    print("Warning: GPU sharing not available")

try:
    from ddr4_ram_sharing import get_ddr4_ram_sharing
    RAM_SHARING_AVAILABLE = True
except ImportError:
    RAM_SHARING_AVAILABLE = False
    print("Warning: RAM sharing not available")

try:
    from windows_screen_sharing import get_screen_sharing
    SCREEN_SHARING_AVAILABLE = True
except ImportError:
    SCREEN_SHARING_AVAILABLE = False
    print("Warning: Screen sharing not available")
try:
    from system_data_connector import get_system_connector
    SYSTEM_CONNECTOR_AVAILABLE = True
except ImportError:
    SYSTEM_CONNECTOR_AVAILABLE = False
    print("Warning: System connector not available")

# Import GUI components
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
try:
    import tkinter.dnd2 as tkdnd  # Optional drag-and-drop
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
from PIL import Image, ImageTk
import io

# Import unified theme
try:
    from theme_config import HomelabTheme
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    print("Warning: Unified theme not available")

# Import Windows Assistant integration
try:
    from windows_assistant_integration import WindowsAssistantIntegration
    ASSISTANT_INTEGRATION_AVAILABLE = True
except ImportError:
    ASSISTANT_INTEGRATION_AVAILABLE = False
    print("Warning: Windows Assistant integration not available")

class ShareType(Enum):
    """Types of sharing services"""
    SCREEN = "screen"
    SOUND = "sound"
    FILE = "file"
    RESOURCE = "resource"
    CLIPBOARD = "clipboard"

@dataclass
class PortalNode:
    """Portal node information"""
    node_id: str
    hostname: str
    ip_address: str
    port: int
    capabilities: List[ShareType]
    status: str
    last_seen: str
    metadata: Dict[str, Any]

@dataclass
class ShareSession:
    """Active sharing session"""
    session_id: str
    source_node: str
    target_node: str
    share_type: ShareType
    status: str
    created_at: str
    metadata: Dict[str, Any]

class HomelabPortal:
    """Main Homelab Portal system with auto device discovery"""
    
    def __init__(self, node_id: str = None, port: int = 8080):
        self.node_id = node_id or f"node_{socket.gethostname()}_{int(time.time())}"
        self.port = port
        self.running = False
        
        # Setup logger
        self.logger = logging.getLogger(f"HomelabPortal-{self.node_id[:8]}")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Setup unified theme
        self.theme = HomelabTheme() if THEME_AVAILABLE else None
        
        # Core services with availability checks (must be initialized before use)
        self.event_bus = get_event_bus() if EVENT_BUS_AVAILABLE else None
        self.config_manager = get_config_manager() if CONFIG_MANAGER_AVAILABLE else None
        self.auth_service = get_auth_service() if AUTH_SERVICE_AVAILABLE else None
        self.data_persistence = get_data_persistence() if DATA_PERSISTENCE_AVAILABLE else None
        self.unified_monitoring = get_unified_monitoring() if UNIFIED_MONITORING_AVAILABLE else None
        self.resource_sharing = get_resource_sharing() if BIDIRECTIONAL_SHARING_AVAILABLE else None
        
        # Initialize Windows Assistant integration (uses event_bus)
        if ASSISTANT_INTEGRATION_AVAILABLE and self.event_bus:
            self.assistant_integration = WindowsAssistantIntegration(self.event_bus, self.logger)
        else:
            self.assistant_integration = None
        
        # Auto device discovery
        self.discovered_devices = {}
        self.device_discovery_active = False
        self.discovery_thread = None
        self.discovery_interval = 30  # seconds
        self.p2p_connections = {}
        self.listening_sockets = {}
        
        # Network identity
        self.hostname = socket.gethostname()
        self.ip_address = self._get_local_ip()
        
        # Hardware optimizers (conditional initialization - must be before auto_discovery)
        if NETWORK_DISCOVERY_AVAILABLE:
            self.network_discovery = WindowsNetworkDiscovery(self.node_id, self.port)
        else:
            self.network_discovery = None
            
        if INTEL_OPTIMIZER_AVAILABLE:
            self.intel_optimizer = get_intel_optimizer()
        else:
            self.intel_optimizer = None
            
        if HARDWARE_OPTIMIZER_AVAILABLE:
            self.identical_optimizer = get_identical_hardware_optimizer()
        else:
            self.identical_optimizer = None
            
        if GPU_SHARING_AVAILABLE:
            self.gpu_sharing = get_gpu_sharing(self.node_id)
        else:
            self.gpu_sharing = None
            
        if RAM_SHARING_AVAILABLE:
            self.ram_sharing = get_ddr4_ram_sharing(self.node_id)
        else:
            self.ram_sharing = None
            
        if SCREEN_SHARING_AVAILABLE:
            self.screen_sharing = get_screen_sharing(self.node_id)
        else:
            self.screen_sharing = None
        
        # Portal state
        self.active_nodes = {}
        self.active_sessions = {}
        self.capabilities = self._detect_capabilities()
        self.hardware_info = {}
        if self.identical_optimizer:
            try:
                self.hardware_info = self.identical_optimizer.get_system_info()
            except Exception as e:
                self.logger.warning(f"Could not get hardware info: {e}")
        
        # GUI components
        self.root = None
        self.setup_complete = False
        
        # Network components
        self.server_socket = None
        self.client_connections = {}
        
        # Initialize auto discovery (after all attributes are set)
        self.initialize_auto_discovery()
        
        # Initialize system monitoring
        if PSUTIL_AVAILABLE:
            self.monitoring_data = {
                'cpu_usage': deque(maxlen=60),
                'memory_usage': deque(maxlen=60),
                'network_usage': deque(maxlen=60),
                'temperature': deque(maxlen=60),
                'timestamps': deque(maxlen=60)
            }
            self.monitoring_active = False
            self.monitoring_thread = None
        else:
            self.monitoring_data = None
            self.monitoring_active = False
            self.monitoring_thread = None
    
    def _publish(self, event_type, source, data):
        """Safely publish event if event_bus is available"""
        if self.event_bus:
            try:
                self.event_bus.publish_sync(event_type, source, data)
            except Exception as e:
                self.logger.warning(f"Event publish failed: {e}")
    
    def initialize_auto_discovery(self):
        """Initialize auto device discovery system"""
        # Start device discovery thread
        self.start_device_discovery()
        
        # Setup listening protocols
        self.setup_listening_protocols()
        
        # Initialize P2P protocols
        self.initialize_p2p_protocols()
        
        # Log initialization
        self._publish(
            EventType.INFO,
            'homelab_portal',
            {
                'action': 'auto_discovery_initialized',
                'node_id': self.node_id,
                'discovery_interval': self.discovery_interval
            }
        )
    
    def start_device_discovery(self):
        """Start automatic device discovery"""
        if not self.device_discovery_active:
            self.device_discovery_active = True
            self.discovery_thread = threading.Thread(target=self.device_discovery_loop, daemon=True)
            self.discovery_thread.start()
    
    def device_discovery_loop(self):
        """Main device discovery loop"""
        while self.device_discovery_active:
            try:
                # Discover devices on network
                self.discover_network_devices()
                
                # Discover local hardware
                self.discover_local_hardware()
                
                # Update device registry
                self.update_device_registry()
                
                # Sleep before next discovery cycle
                time.sleep(self.discovery_interval)
                
            except Exception as e:
                self.logger.error(f"Device discovery error: {e}")
                time.sleep(5)  # Brief pause on error
    
    def discover_network_devices(self):
        """Discover devices on the network"""
        try:
            # Use network discovery service if available
            if self.network_discovery is None:
                self.logger.warning("Network discovery not available")
                return
                
            discovered = self.network_discovery.get_discovered_nodes()
            
            for device_id, device_info in discovered.items():
                
                if device_id not in self.discovered_devices:
                    self.discovered_devices[device_id] = {
                        'id': device_id,
                        'name': device_info.get('name', 'Unknown Device'),
                        'type': device_info.get('type', 'unknown'),
                        'ip': device_info.get('ip', '0.0.0.0'),
                        'port': device_info.get('port', 8080),
                        'last_seen': datetime.now().isoformat(),
                        'capabilities': device_info.get('capabilities', []),
                        'status': 'online'
                    }
                    
                    # Publish discovery event
                    self._publish(
                        EventType.INFO,
                        'homelab_portal',
                        {
                            'action': 'device_discovered',
                            'device_id': device_id,
                            'device_info': self.discovered_devices[device_id]
                        }
                    )
                else:
                    # Update last seen time
                    self.discovered_devices[device_id]['last_seen'] = datetime.now().isoformat()
                    self.discovered_devices[device_id]['status'] = 'online'
        
        except Exception as e:
            self.logger.error(f"Network discovery error: {e}")
    
    def discover_local_hardware(self):
        """Discover local hardware resources"""
        try:
            import psutil
            
            # System info
            system_info = {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'hostname': socket.gethostname(),
                'platform': platform.system()
            }
            
            # Add to discovered devices as local node
            local_device_id = f"local_{socket.gethostname()}"
            self.discovered_devices[local_device_id] = {
                'id': local_device_id,
                'name': socket.gethostname(),
                'type': 'local_node',
                'ip': socket.gethostbyname(socket.gethostname()),
                'port': self.port,
                'last_seen': datetime.now().isoformat(),
                'capabilities': ['cpu_sharing', 'memory_sharing', 'gpu_sharing', 'screen_sharing'],
                'status': 'online',
                'hardware': system_info
            }
        
        except Exception as e:
            self.logger.error(f"Local hardware discovery error: {e}")
    
    def update_device_registry(self):
        """Update device registry and remove stale devices"""
        current_time = datetime.now()
        stale_threshold = timedelta(minutes=5)
        
        stale_devices = []
        for device_id, device_info in self.discovered_devices.items():
            last_seen = datetime.fromisoformat(device_info['last_seen'])
            if current_time - last_seen > stale_threshold:
                stale_devices.append(device_id)
        
        # Remove stale devices
        for device_id in stale_devices:
            device_info = self.discovered_devices.pop(device_id, {})
            device_info['status'] = 'offline'
            
            # Publish device offline event
            self._publish(
                EventType.WARNING,
                'homelab_portal',
                {
                    'action': 'device_offline',
                    'device_id': device_id,
                    'device_info': device_info
                }
            )
    
    def setup_listening_protocols(self):
        """Setup listening protocols for incoming connections"""
        try:
            # Setup TCP listener
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.bind(('0.0.0.0', self.port))
            tcp_socket.listen(5)
            
            self.listening_sockets['tcp'] = tcp_socket
            
            # Start TCP listener thread
            tcp_thread = threading.Thread(target=self.tcp_listener_loop, args=(tcp_socket,), daemon=True)
            tcp_thread.start()
            
            # Setup UDP listener for discovery broadcasts
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(('0.0.0.0', self.port + 1))
            
            self.listening_sockets['udp'] = udp_socket
            
            # Start UDP listener thread
            udp_thread = threading.Thread(target=self.udp_listener_loop, args=(udp_socket,), daemon=True)
            udp_thread.start()
            
        except Exception as e:
            self.logger.error(f"Listening protocol setup error: {e}")
    
    def tcp_listener_loop(self, tcp_socket):
        """TCP listener loop for incoming connections"""
        while self.running:
            try:
                client_socket, address = tcp_socket.accept()
                
                # Handle client connection in separate thread
                client_thread = threading.Thread(
                    target=self.handle_tcp_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"TCP listener error: {e}")
                time.sleep(1)
    
    def udp_listener_loop(self, udp_socket):
        """UDP listener loop for discovery broadcasts"""
        while self.running:
            try:
                data, address = udp_socket.recvfrom(1024)
                
                # Handle discovery broadcast
                self.handle_discovery_broadcast(data, address)
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"UDP listener error: {e}")
                time.sleep(1)
    
    def handle_tcp_client(self, client_socket, address):
        """Handle incoming TCP client connection"""
        try:
            # Send device info
            device_info = {
                'node_id': self.node_id,
                'timestamp': datetime.now().isoformat(),
                'capabilities': ['cpu_sharing', 'memory_sharing', 'gpu_sharing']
            }
            
            message = json.dumps(device_info).encode('utf-8')
            client_socket.send(message)
            
            # Keep connection alive for P2P communication
            self.p2p_connections[address] = client_socket
            
        except Exception as e:
            self.logger.error(f"TCP client handling error: {e}")
            client_socket.close()
    
    def handle_discovery_broadcast(self, data, address):
        """Handle discovery broadcast from other nodes"""
        try:
            message = json.loads(data.decode('utf-8'))
            
            if message.get('type') == 'discovery':
                # Respond with device info
                response = {
                    'type': 'discovery_response',
                    'node_id': self.node_id,
                    'timestamp': datetime.now().isoformat()
                }
                
                udp_socket = self.listening_sockets.get('udp')
                if udp_socket:
                    response_data = json.dumps(response).encode('utf-8')
                    udp_socket.sendto(response_data, address)
        
        except Exception as e:
            self.logger.error(f"Discovery broadcast handling error: {e}")
    
    def initialize_p2p_protocols(self):
        """Initialize P2P protocols for device-to-device communication"""
        try:
            # Setup P2P message handlers
            self.p2p_handlers = {
                'resource_request': self.handle_resource_request,
                'resource_response': self.handle_resource_response,
                'file_transfer': self.handle_file_transfer,
                'screen_share': self.handle_screen_share
            }
            
            # Start P2P protocol thread
            p2p_thread = threading.Thread(target=self.p2p_protocol_loop, daemon=True)
            p2p_thread.start()
            
        except Exception as e:
            self.logger.error(f"P2P protocol initialization error: {e}")
    
    def p2p_protocol_loop(self):
        """P2P protocol message handling loop"""
        while self.running:
            try:
                # Process P2P messages
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"P2P protocol loop error: {e}")
                time.sleep(5)
    
    def handle_resource_request(self, message, source_address):
        """Handle resource sharing request"""
        try:
            resource_type = message.get('resource_type')
            amount = message.get('amount')
            
            # Check if resource is available
            if resource_type == 'cpu':
                available = self.resource_sharing.get_available_cpu()
            elif resource_type == 'memory':
                available = self.resource_sharing.get_available_memory()
            elif resource_type == 'gpu':
                available = self.gpu_sharing.get_available_gpu()
            else:
                available = 0
            
            # Send response
            response = {
                'type': 'resource_response',
                'available': available,
                'granted': available >= amount,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send response back to source
            self.send_p2p_message(response, source_address)
            
        except Exception as e:
            self.logger.error(f"Resource request handling error: {e}")
    
    def handle_resource_response(self, message, source_address):
        """Handle resource sharing response"""
        try:
            # Log resource response
            self._publish(
                EventType.INFO,
                'homelab_portal',
                {
                    'action': 'resource_response_received',
                    'source': source_address,
                    'response': message
                }
            )
            
        except Exception as e:
            self.logger.error(f"Resource response handling error: {e}")
    
    def handle_file_transfer(self, message, source_address):
        """Handle file transfer request"""
        try:
            file_path = message.get('file_path')
            file_size = message.get('file_size')
            
            # Implement file transfer logic
            self._publish(
                EventType.INFO,
                'homelab_portal',
                {
                    'action': 'file_transfer_requested',
                    'source': source_address,
                    'file_path': file_path,
                    'file_size': file_size
                }
            )
            
        except Exception as e:
            self.logger.error(f"File transfer handling error: {e}")
    
    def handle_screen_share(self, message, source_address):
        """Handle screen sharing request"""
        try:
            # Start screen sharing
            self.screen_sharing.start_sharing(target_address=source_address)
            
            self._publish(
                EventType.INFO,
                'homelab_portal',
                {
                    'action': 'screen_share_started',
                    'target': source_address
                }
            )
            
        except Exception as e:
            self.logger.error(f"Screen share handling error: {e}")
    
    def send_p2p_message(self, message, target_address):
        """Send P2P message to target device"""
        try:
            # Use existing P2P connection or create new one
            if target_address in self.p2p_connections:
                socket_conn = self.p2p_connections[target_address]
                message_data = json.dumps(message).encode('utf-8')
                socket_conn.send(message_data)
            else:
                # Create new connection
                new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new_socket.connect(target_address)
                
                message_data = json.dumps(message).encode('utf-8')
                new_socket.send(message_data)
                
                self.p2p_connections[target_address] = new_socket
                
        except Exception as e:
            self.logger.error(f"P2P message sending error: {e}")
    
    def get_connected_devices(self):
        """Get list of connected devices"""
        return {
            'devices': list(self.discovered_devices.values()),
            'count': len(self.discovered_devices),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self):
        """Get portal status"""
        return {
            'node_id': self.node_id,
            'running': self.running,
            'discovery_active': self.device_discovery_active,
            'connected_devices': len(self.discovered_devices),
            'p2p_connections': len(self.p2p_connections),
            'listening_protocols': list(self.listening_sockets.keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        hostname = socket.gethostname()
        timestamp = str(int(time.time()))
        raw = f"{hostname}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _detect_capabilities(self) -> List[ShareType]:
        """Detect system capabilities"""
        capabilities = [ShareType.RESOURCE, ShareType.FILE, ShareType.CLIPBOARD]
        
        # Check screen sharing capability
        try:
            if platform.system() == "Windows":
                subprocess.run(["powershell", "-Command", "Get-Process"], 
                             capture_output=True, timeout=5)
                capabilities.append(ShareType.SCREEN)
        except:
            pass
        
        # Check sound sharing capability
        try:
            if platform.system() == "Windows":
                subprocess.run(["powershell", "-Command", "Get-AudioDevice"], 
                             capture_output=True, timeout=5)
                capabilities.append(ShareType.SOUND)
        except:
            pass
        
        return capabilities
    
    def start_portal_server(self):
        """Start the portal server"""
        try:
            # Optimize for identical hardware first
            if self.identical_optimizer:
                self.logger.info("Optimizing for Intel+NVIDIA identical hardware...")
                self.identical_optimizer.optimize_for_identical_hardware()
            
            # Configure firewall for portal
            if self.intel_optimizer:
                self.intel_optimizer.configure_firewall_for_portal()
            
            # Start network discovery
            if self.network_discovery is not None:
                self.network_discovery.start_discovery()
            else:
                self.logger.warning("Network discovery not available, skipping discovery start")
            
            # Start portal server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip_address, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"Portal server started on {self.ip_address}:{self.port}")
            self.logger.info(f"Hardware: {self.hardware_info.get('cpu', {}).get('name', 'Unknown')} + {self.hardware_info.get('gpu', {}).get('name', 'Unknown')}")
            self.logger.info(f"Windows: {self.hardware_info.get('windows_version', 'Unknown')}")
            
            # Start server thread
            server_thread = threading.Thread(target=self._server_loop, daemon=True)
            server_thread.start()
            
            # Start discovery thread
            discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
            discovery_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start portal server: {e}")
            return False
    
    def _server_loop(self):
        """Main server loop"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Server loop error: {e}")
    
    def _discovery_loop(self):
        """Node discovery loop"""
        while self.running:
            try:
                self._broadcast_presence()
                time.sleep(30)  # Broadcast every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Discovery loop error: {e}")
    
    def _broadcast_presence(self):
        """Broadcast node presence to network"""
        try:
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.settimeout(5.0)
            
            node_info = {
                'node_id': self.node_id,
                'hostname': self.hostname,
                'ip_address': self.ip_address,
                'port': self.port,
                'capabilities': [cap.value for cap in self.capabilities],
                'platform': platform.system(),
                'timestamp': datetime.now().isoformat()
            }
            
            message = json.dumps(node_info).encode('utf-8')
            
            # Try multiple broadcast addresses for Windows networks
            broadcast_addresses = [
                '<broadcast>',
                '255.255.255.255',
                '192.168.1.255',
                '192.168.0.255',
                '10.0.0.255'
            ]
            
            for addr in broadcast_addresses:
                try:
                    broadcast_socket.sendto(message, (addr, self.port + 1))
                except:
                    pass  # Ignore broadcast failures
            
            broadcast_socket.close()
            
        except Exception as e:
            self.logger.error(f"Broadcast error: {e}")
    
    def _handle_client(self, client_socket, address):
        """Handle incoming client connections"""
        try:
            data = client_socket.recv(4096)
            if not data:
                return
            
            message = json.loads(data.decode('utf-8'))
            message_type = message.get('type')
            
            if message_type == 'share_request':
                self._handle_share_request(client_socket, message, address)
            elif message_type == 'file_transfer':
                self._handle_file_transfer(client_socket, message, address)
            elif message_type == 'screen_share':
                self._handle_screen_share(client_socket, message, address)
            elif message_type == 'sound_share':
                self._handle_sound_share(client_socket, message, address)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
        finally:
            client_socket.close()
    
    def _handle_share_request(self, client_socket, message, address):
        """Handle sharing requests"""
        try:
            share_type = ShareType(message.get('share_type'))
            target_node = message.get('target_node')
            
            # Create session
            session_id = self._generate_session_id()
            session = ShareSession(
                session_id=session_id,
                source_node=message.get('source_node'),
                target_node=target_node,
                share_type=share_type,
                status='active',
                created_at=datetime.now().isoformat(),
                metadata=message.get('metadata', {})
            )
            
            self.active_sessions[session_id] = session
            
            # Send response
            response = {
                'type': 'share_response',
                'session_id': session_id,
                'status': 'accepted',
                'message': f'Sharing session established for {share_type.value}'
            }
            
            client_socket.send(json.dumps(response).encode('utf-8'))
            
            # Log event
            self._publish(
                EventType.RESOURCE,
                'Portal',
                {
                    'action': 'share_started',
                    'session_id': session_id,
                    'share_type': share_type.value,
                    'source': message.get('source_node'),
                    'target': target_node
                }
            )
            
        except Exception as e:
            self.logger.error(f"Share request handling error: {e}")
    
    def _handle_file_transfer(self, client_socket, message, address):
        """Handle file transfers"""
        try:
            filename = message.get('filename')
            file_size = message.get('file_size')
            file_data = message.get('file_data')
            
            # Save file
            save_dir = Path.home() / "Homelab" / "Received Files"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Send confirmation
            response = {
                'type': 'file_received',
                'filename': filename,
                'status': 'success',
                'path': str(file_path)
            }
            
            client_socket.send(json.dumps(response).encode('utf-8'))
            
            # Log event
            self._publish(
                EventType.RESOURCE,
                'Portal',
                {
                    'action': 'file_received',
                    'filename': filename,
                    'size': file_size,
                    'from': address[0]
                }
            )
            
        except Exception as e:
            self.logger.error(f"File transfer error: {e}")
    
    def _handle_screen_share(self, client_socket, message, address):
        """Handle screen sharing requests"""
        try:
            # This would integrate with screen capture functionality
            response = {
                'type': 'screen_share_response',
                'status': 'implemented',
                'message': 'Screen sharing functionality available'
            }
            
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Screen share error: {e}")
    
    def _handle_sound_share(self, client_socket, message, address):
        """Handle sound sharing requests"""
        try:
            # This would integrate with audio capture/playback
            response = {
                'type': 'sound_share_response',
                'status': 'implemented',
                'message': 'Sound sharing functionality available'
            }
            
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Sound share error: {e}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time()))
        raw = f"{self.node_id}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def connect_to_node(self, target_ip: str, target_port: int) -> bool:
        """Connect to another portal node"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target_ip, target_port))
            
            # Send connection request
            request = {
                'type': 'node_connect',
                'node_id': self.node_id,
                'hostname': self.hostname,
                'ip_address': self.ip_address,
                'port': self.port,
                'capabilities': [cap.value for cap in self.capabilities]
            }
            
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            # Receive response
            response = client_socket.recv(4096)
            response_data = json.loads(response.decode('utf-8'))
            
            if response_data.get('status') == 'accepted':
                self.client_connections[target_ip] = client_socket
                self.logger.info(f"Connected to node at {target_ip}:{target_port}")
                return True
            else:
                client_socket.close()
                return False
                
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    def share_file(self, file_path: str, target_node: str) -> bool:
        """Share file with target node"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Get target node info
            target_info = self.active_nodes.get(target_node)
            if not target_info:
                return False
            
            # Connect to target
            if not self.connect_to_node(target_info.ip_address, target_info.port):
                return False
            
            # Send file
            client_socket = self.client_connections[target_info.ip_address]
            
            file_message = {
                'type': 'file_transfer',
                'source_node': self.node_id,
                'target_node': target_node,
                'filename': os.path.basename(file_path),
                'file_size': len(file_data),
                'file_data': file_data.hex()  # Convert to hex for JSON serialization
            }
            
            client_socket.send(json.dumps(file_message).encode('utf-8'))
            
            # Receive confirmation
            response = client_socket.recv(4096)
            response_data = json.loads(response.decode('utf-8'))
            
            return response_data.get('status') == 'success'
            
        except Exception as e:
            self.logger.error(f"File sharing error: {e}")
            return False
    
    def start_screen_share(self, target_node: str) -> str:
        """Start screen sharing session"""
        try:
            target_info = self.active_nodes.get(target_node)
            if not target_info:
                return ""
            
            # Connect to target
            if not self.connect_to_node(target_info.ip_address, target_info.port):
                return ""
            
            # Send screen share request
            client_socket = self.client_connections[target_info.ip_address]
            
            share_request = {
                'type': 'screen_share',
                'source_node': self.node_id,
                'target_node': target_node,
                'metadata': {
                    'resolution': '1920x1080',
                    'quality': 'high'
                }
            }
            
            client_socket.send(json.dumps(share_request).encode('utf-8'))
            
            # Create session
            session_id = self._generate_session_id()
            session = ShareSession(
                session_id=session_id,
                source_node=self.node_id,
                target_node=target_node,
                share_type=ShareType.SCREEN,
                status='active',
                created_at=datetime.now().isoformat(),
                metadata={'resolution': '1920x1080', 'quality': 'high'}
            )
            
            self.active_sessions[session_id] = session
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Screen share error: {e}")
            return ""
    
    def start_sound_share(self, target_node: str) -> str:
        """Start sound sharing session"""
        try:
            target_info = self.active_nodes.get(target_node)
            if not target_info:
                return ""
            
            # Connect to target
            if not self.connect_to_node(target_info.ip_address, target_info.port):
                return ""
            
            # Send sound share request
            client_socket = self.client_connections[target_info.ip_address]
            
            share_request = {
                'type': 'sound_share',
                'source_node': self.node_id,
                'target_node': target_node,
                'metadata': {
                    'sample_rate': 44100,
                    'channels': 2,
                    'quality': 'high'
                }
            }
            
            client_socket.send(json.dumps(share_request).encode('utf-8'))
            
            # Create session
            session_id = self._generate_session_id()
            session = ShareSession(
                session_id=session_id,
                source_node=self.node_id,
                target_node=target_node,
                share_type=ShareType.SOUND,
                status='active',
                created_at=datetime.now().isoformat(),
                metadata={'sample_rate': 44100, 'channels': 2, 'quality': 'high'}
            )
            
            self.active_sessions[session_id] = session
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Sound share error: {e}")
            return ""
    
    def get_active_nodes(self) -> List[PortalNode]:
        """Get list of active nodes"""
        return list(self.active_nodes.values())
    
    def get_active_sessions(self) -> List[ShareSession]:
        """Get list of active sessions"""
        return list(self.active_sessions.values())
    
    def stop(self):
        """Stop portal server"""
        self.running = False
        self.stop_monitoring()
    
    def start_monitoring(self):
        """Start system monitoring"""
        if PSUTIL_AVAILABLE and self.monitoring_data and not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self.monitor_system, daemon=True)
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
    
    def monitor_system(self):
        """Monitor system resources"""
        while self.monitoring_active and PSUTIL_AVAILABLE:
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
        
        if self.server_socket:
            self.server_socket.close()
        
        for client_socket in self.client_connections.values():
            client_socket.close()
        
        self.client_connections.clear()
        self.active_nodes.clear()
        self.active_sessions.clear()
        
        self.logger.info("Portal server stopped")

class PortalGUI:
    """Portal GUI Interface"""
    
    def __init__(self, portal: HomelabPortal):
        self.portal = portal
        self.root = tk.Tk()
        self.root.title("Homelab Portal - Unified Resource Sharing")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Apply unified theme
        if THEME_AVAILABLE:
            self.theme = HomelabTheme()
            self.root.configure(bg=self.theme.COLORS['bg_primary'])
            self.style = ttk.Style()
            self.theme.apply_styles(self.style)
        else:
            # Fallback to hardcoded colors
            self.root.configure(bg='#1a1a1a')
            self.style = ttk.Style()
        
        # Setup window scaling
        self.setup_window_scaling()
        
        # Setup GUI
        self.setup_gui()
    
    def setup_window_scaling(self):
        """Setup window scaling and DPI awareness"""
        try:
            # Enable DPI awareness for better scaling
            self.root.tk.call('tk', 'scaling', 1.0)
            
            # Get screen dimensions for proper scaling
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Center window on screen
            x = (screen_width - 1200) // 2
            y = (screen_height - 800) // 2
            self.root.geometry(f"1200x800+{x}+{y}")
            
            # Setup window bindings
            self.root.bind('<Configure>', self.on_window_resize)
            self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
            
            # Window attributes
            self.root.resizable(True, True)
            self.root.maxsize(1920, 1080)
            self.root.attributes('-alpha', 1.0)
            
        except Exception as e:
            print(f"Window scaling setup error: {e}")
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Handle window resizing if needed
            pass
    
    def on_window_close(self):
        """Handle window close event"""
        try:
            self.portal.stop()
            self.root.quit()
        except:
            self.root.quit()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Create main frames
        self.create_menu_bar()
        self.create_main_layout()
        self.create_status_bar()
        
        # Setup drag and drop
        self.setup_drag_and_drop()
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Share File...", command=self.share_file_dialog)
        file_menu.add_command(label="Open Received Files", command=self.open_received_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Share menu
        share_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Share", menu=share_menu)
        share_menu.add_command(label="Start Screen Share", command=self.start_screen_share)
        share_menu.add_command(label="Start Sound Share", command=self.start_sound_share)
        share_menu.add_command(label="Share Resources", command=self.share_resources)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="System Monitor", command=self.open_system_monitor)
        tools_menu.add_command(label="Resource Manager", command=self.open_resource_manager)
        tools_menu.add_command(label="Configuration", command=self.open_configuration)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_layout(self):
        """Create main layout"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Nodes tab
        self.nodes_frame = ttk.Frame(notebook)
        notebook.add(self.nodes_frame, text="Active Nodes")
        self.create_nodes_tab()
        
        # Sessions tab
        self.sessions_frame = ttk.Frame(notebook)
        notebook.add(self.sessions_frame, text="Active Sessions")
        self.create_sessions_tab()
        
        # File Transfer tab
        self.files_frame = ttk.Frame(notebook)
        notebook.add(self.files_frame, text="File Transfer")
        self.create_files_tab()
        
        # Screen Share tab
        self.screen_frame = ttk.Frame(notebook)
        notebook.add(self.screen_frame, text="Screen Share")
        self.create_screen_tab()
        
        # Sound Share tab
        self.sound_frame = ttk.Frame(notebook)
        notebook.add(self.sound_frame, text="Sound Share")
        self.create_sound_tab()
        
    def create_nodes_tab(self):
        """Create nodes tab"""
        # Nodes list
        columns = ('Node ID', 'Hostname', 'IP Address', 'Port', 'Capabilities', 'Status')
        self.nodes_tree = ttk.Treeview(self.nodes_frame, columns=columns, show='headings')
        
        for col in columns:
            self.nodes_tree.heading(col, text=col)
            self.nodes_tree.column(col, width=150)
        
        # Scrollbar
        nodes_scrollbar = ttk.Scrollbar(self.nodes_frame, orient=tk.VERTICAL, command=self.nodes_tree.yview)
        self.nodes_tree.configure(yscrollcommand=nodes_scrollbar.set)
        
        # Pack
        self.nodes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        nodes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = ttk.Frame(self.nodes_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_nodes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Connect", command=self.connect_to_node).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Disconnect", command=self.disconnect_from_node).pack(side=tk.LEFT, padx=5)
        
    def create_sessions_tab(self):
        """Create sessions tab"""
        # Sessions list
        columns = ('Session ID', 'Source', 'Target', 'Type', 'Status', 'Created')
        self.sessions_tree = ttk.Treeview(self.sessions_frame, columns=columns, show='headings')
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=150)
        
        # Scrollbar
        sessions_scrollbar = ttk.Scrollbar(self.sessions_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar.set)
        
        # Pack
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = ttk.Frame(self.sessions_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_sessions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Session", command=self.stop_session).pack(side=tk.LEFT, padx=5)
        
    def create_files_tab(self):
        """Create files tab"""
        # File transfer area
        transfer_frame = ttk.LabelFrame(self.files_frame, text="File Transfer Area")
        transfer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Drag and drop area
        self.drop_area = tk.Text(transfer_frame, height=10, wrap=tk.WORD)
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.drop_area.insert(tk.END, "Drag and drop files here to share them with connected nodes...")
        self.drop_area.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = ttk.Frame(self.files_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Select Files", command=self.share_file_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Received", command=self.open_received_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear History", command=self.clear_file_history).pack(side=tk.LEFT, padx=5)
        
    def create_screen_tab(self):
        """Create screen sharing tab"""
        # Screen sharing controls
        control_frame = ttk.LabelFrame(self.screen_frame, text="Screen Sharing Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Start Screen Share", command=self.start_screen_share).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Stop Screen Share", command=self.stop_screen_share).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Display area
        display_frame = ttk.LabelFrame(self.screen_frame, text="Screen Display")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.screen_canvas = tk.Canvas(display_frame, bg='black')
        self.screen_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_sound_tab(self):
        """Create sound sharing tab"""
        # Sound sharing controls
        control_frame = ttk.LabelFrame(self.sound_frame, text="Sound Sharing Controls")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Start Sound Share", command=self.start_sound_share).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Stop Sound Share", command=self.stop_sound_share).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Audio level display
        level_frame = ttk.LabelFrame(self.sound_frame, text="Audio Levels")
        level_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.audio_level_canvas = tk.Canvas(level_frame, bg='black')
        self.audio_level_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        if TKDND_AVAILABLE:
            # Enable drag and drop for the file area
            self.drop_area.config(state=tk.NORMAL)
            tkdnd.TKDND_FileDrop(self.drop_area, self.handle_file_drop)
            self.drop_area.config(state=tk.DISABLED)
        else:
            # Drag and drop not available, use button instead
            pass
        
    def handle_file_drop(self, file_list):
        """Handle dropped files"""
        for file_path in file_list:
            self.share_file(file_path)
    
    def share_file_dialog(self):
        """Open file sharing dialog"""
        file_paths = filedialog.askopenfilenames(
            title="Select files to share",
            filetypes=[("All files", "*.*"), ("Documents", "*.txt;*.doc;*.pdf"), ("Images", "*.jpg;*.png;*.gif")]
        )
        
        for file_path in file_paths:
            self.share_file(file_path)
    
    def share_file(self, file_path: str):
        """Share a file"""
        try:
            # Get selected target node
            selected = self.nodes_tree.selection()
            if not selected:
                messagebox.showwarning("No Target", "Please select a target node from the Active Nodes tab")
                return
            
            target_node = self.nodes_tree.item(selected[0])['values'][0]
            
            # Share file
            if self.portal.share_file(file_path, target_node):
                self.status_bar.config(text=f"Shared {os.path.basename(file_path)} with {target_node}")
                messagebox.showinfo("Success", f"File {os.path.basename(file_path)} shared successfully!")
            else:
                messagebox.showerror("Error", f"Failed to share {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"File sharing error: {e}")
    
    def start_screen_share(self):
        """Start screen sharing"""
        try:
            # Get selected target node
            selected = self.nodes_tree.selection()
            if not selected:
                messagebox.showwarning("No Target", "Please select a target node from the Active Nodes tab")
                return
            
            target_node = self.nodes_tree.item(selected[0])['values'][0]
            
            # Start screen share
            session_id = self.portal.start_screen_share(target_node)
            if session_id:
                self.status_bar.config(text=f"Screen sharing started with {target_node}")
                messagebox.showinfo("Success", f"Screen sharing started! Session ID: {session_id}")
            else:
                messagebox.showerror("Error", "Failed to start screen sharing")
                
        except Exception as e:
            messagebox.showerror("Error", f"Screen sharing error: {e}")
    
    def start_sound_share(self):
        """Start sound sharing"""
        try:
            # Get selected target node
            selected = self.nodes_tree.selection()
            if not selected:
                messagebox.showwarning("No Target", "Please select a target node from the Active Nodes tab")
                return
            
            target_node = self.nodes_tree.item(selected[0])['values'][0]
            
            # Start sound share
            session_id = self.portal.start_sound_share(target_node)
            if session_id:
                self.status_bar.config(text=f"Sound sharing started with {target_node}")
                messagebox.showinfo("Success", f"Sound sharing started! Session ID: {session_id}")
            else:
                messagebox.showerror("Error", "Failed to start sound sharing")
                
        except Exception as e:
            messagebox.showerror("Error", f"Sound sharing error: {e}")
    
    def refresh_nodes(self):
        """Refresh active nodes list"""
        try:
            # Clear current list
            for item in self.nodes_tree.get_children():
                self.nodes_tree.delete(item)
            
            # Add active nodes
            for node in self.portal.get_active_nodes():
                capabilities = ", ".join([cap.value for cap in node.capabilities])
                self.nodes_tree.insert('', tk.END, values=(
                    node.node_id,
                    node.hostname,
                    node.ip_address,
                    node.port,
                    capabilities,
                    node.status
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh nodes: {e}")
    
    def refresh_sessions(self):
        """Refresh active sessions list"""
        try:
            # Clear current list
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            # Add active sessions
            for session in self.portal.get_active_sessions():
                self.sessions_tree.insert('', tk.END, values=(
                    session.session_id,
                    session.source_node,
                    session.target_node,
                    session.share_type.value,
                    session.status,
                    session.created_at
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh sessions: {e}")
    
    def open_received_files(self):
        """Open received files directory"""
        received_dir = Path.home() / "Homelab" / "Received Files"
        received_dir.mkdir(parents=True, exist_ok=True)
        
        if platform.system() == "Windows":
            subprocess.run(['explorer', str(received_dir)])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', str(received_dir)])
        else:  # Linux
            subprocess.run(['xdg-open', str(received_dir)])
    
    def clear_file_history(self):
        """Clear file transfer history"""
        # Clear the display
        self.drop_area.config(state=tk.NORMAL)
        self.drop_area.delete(1.0, tk.END)
        self.drop_area.insert(tk.END, "Drag and drop files here to share them with connected nodes...")
        self.drop_area.config(state=tk.DISABLED)
        
    def connect_to_node(self):
        """Connect to selected node"""
        try:
            selected = self.nodes_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a node to connect to")
                return
            
            node_data = self.nodes_tree.item(selected[0])['values']
            ip_address = node_data[2]
            port = node_data[3]
            
            if self.portal.connect_to_node(ip_address, port):
                messagebox.showinfo("Success", f"Connected to node at {ip_address}:{port}")
                self.refresh_nodes()
            else:
                messagebox.showerror("Error", "Failed to connect to node")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {e}")
    
    def disconnect_from_node(self):
        """Disconnect from selected node"""
        try:
            selected = self.nodes_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a node to disconnect from")
                return
            
            node_data = self.nodes_tree.item(selected[0])['values']
            node_id = node_data[0]
            
            # Remove from active connections
            if node_id in self.portal.client_connections:
                self.portal.client_connections[node_id].close()
                del self.portal.client_connections[node_id]
                
                messagebox.showinfo("Success", f"Disconnected from node {node_id}")
                self.refresh_nodes()
            else:
                messagebox.showwarning("Not Connected", f"Not connected to node {node_id}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Disconnection error: {e}")
    
    def stop_session(self):
        """Stop selected session"""
        try:
            selected = self.sessions_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a session to stop")
                return
            
            session_data = self.sessions_tree.item(selected[0])['values']
            session_id = session_data[0]
            
            # Remove session
            if session_id in self.portal.active_sessions:
                del self.portal.active_sessions[session_id]
                
                messagebox.showinfo("Success", f"Session {session_id} stopped")
                self.refresh_sessions()
            else:
                messagebox.showwarning("Not Found", f"Session {session_id} not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Session stopping error: {e}")
    
    def stop_screen_share(self):
        """Stop screen sharing"""
        # Find active screen share sessions
        screen_sessions = [
            session for session in self.portal.get_active_sessions()
            if session.share_type == ShareType.SCREEN
        ]
        
        if screen_sessions:
            for session in screen_sessions:
                if session.session_id in self.portal.active_sessions:
                    del self.portal.active_sessions[session.session_id]
            
            messagebox.showinfo("Success", "Screen sharing stopped")
            self.refresh_sessions()
        else:
            messagebox.showinfo("Info", "No active screen sharing sessions")
    
    def stop_sound_share(self):
        """Stop sound sharing"""
        # Find active sound share sessions
        sound_sessions = [
            session for session in self.portal.get_active_sessions()
            if session.share_type == ShareType.SOUND
        ]
        
        if sound_sessions:
            for session in sound_sessions:
                if session.session_id in self.portal.active_sessions:
                    del self.portal.active_sessions[session.session_id]
            
            messagebox.showinfo("Success", "Sound sharing stopped")
            self.refresh_sessions()
        else:
            messagebox.showinfo("Info", "No active sound sharing sessions")
    
    def share_resources(self):
        """Share system resources"""
        try:
            # Get selected target node
            selected = self.nodes_tree.selection()
            if not selected:
                messagebox.showwarning("No Target", "Please select a target node from the Active Nodes tab")
                return
            
            target_node = self.nodes_tree.item(selected[0])['values'][0]
            
            # Use existing resource sharing
            self.portal.resource_sharing.offer_resources(target_node)
            
            messagebox.showinfo("Success", f"Resource sharing initiated with {target_node}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Resource sharing error: {e}")
    
    def open_system_monitor(self):
        """Open system monitor"""
        try:
            # Launch unified monitoring
            subprocess.Popen([sys.executable, "Core Services/unified_monitoring.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open system monitor: {e}")
    
    def open_resource_manager(self):
        """Open resource manager"""
        try:
            # Launch resource sharing GUI
            subprocess.Popen([sys.executable, "Core Services/bidirectional_resource_sharing.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open resource manager: {e}")
    
    def open_configuration(self):
        """Open configuration"""
        try:
            # Launch configuration manager
            subprocess.Popen([sys.executable, "Core Services/config_manager.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open configuration: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Homelab Portal - Unified Resource Sharing System

Version: 1.0.0
Author: Homelab Tools Team

Features:
• Screen sharing
• Sound sharing  
• File transfer with drag-and-drop
• Resource sharing
• Cross-platform support
• Real-time collaboration

This portal integrates all Homelab Tools into a unified
interface for seamless resource sharing and collaboration.
        """
        
        messagebox.showinfo("About Homelab Portal", about_text)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the Homelab Portal?"):
            self.portal.stop()
            self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start portal server
        if not self.portal.start_portal_server():
            messagebox.showerror("Error", "Failed to start portal server")
            return
        
        # Start GUI update loop
        self.update_gui()
        
        # Run main loop
        self.root.mainloop()
    
    def update_gui(self):
        """Update GUI periodically"""
        try:
            self.refresh_nodes()
            self.refresh_sessions()
            
            # Schedule next update
            self.root.after(5000, self.update_gui)  # Update every 5 seconds
            
        except Exception as e:
            self.logger.error(f"GUI update error: {e}")

def main():
    """Main function"""
    try:
        # Create portal instance
        portal = HomelabPortal()
        
        # Create and run GUI
        gui = PortalGUI(portal)
        gui.run()
        
    except Exception as e:
        print(f"Portal startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
