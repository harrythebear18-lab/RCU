#!/usr/bin/env python3
"""
Subnet Discovery System - App-to-App Communication
Enables broad app-to-app connections on the same subnet with service discovery
"""

import socket
import json
import threading
import time
import hashlib
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import ipaddress
import subprocess
import platform

@dataclass
class ServiceInfo:
    """Service information for discovery"""
    service_id: str
    app_name: str
    app_type: str
    host: str
    port: int
    version: str
    capabilities: List[str]
    status: str
    last_seen: float
    metadata: Dict[str, Any]

class SubnetDiscovery:
    """Subnet-wide service discovery and communication system"""
    
    def __init__(self, app_name: str, app_type: str, port: int = 25566):
        self.app_name = app_name
        self.app_type = app_type
        self.port = port
        self.broadcast_port = 25567  # Broadcast port for discovery
        
        # Service registry
        self.services: Dict[str, ServiceInfo] = {}
        self.local_services: Dict[str, ServiceInfo] = {}
        
        # Network configuration
        self.subnet_range = self._get_subnet_range()
        self.broadcast_address = self._get_broadcast_address()
        
        # Communication
        self.discovery_socket = None
        self.communication_socket = None
        self.running = False
        self.cleanup_thread = None
        self.announcement_thread = None
        
        # Callbacks
        self.callbacks: Dict[str, Callable] = {
            'service_discovered': [],
            'service_lost': [],
            'message_received': []
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"SubnetDiscovery_{app_name}")
        
        # Initialize
        self._initialize_sockets()
    
    def _get_subnet_range(self) -> str:
        """Get the local subnet range"""
        try:
            # Get local IP and subnet mask
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Try to get subnet mask
            if platform.system() == "Windows":
                # Windows method
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    if local_ip in line and 'Subnet Mask' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            subnet_mask = parts[2].strip()
                            # Calculate subnet range
                            ip_parts = list(map(int, local_ip.split('.')))
                            mask_parts = list(map(int, subnet_mask.split('.')))
                            network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
                            return f"{network_parts[0]}.{network_parts[1]}.{network_parts[2]}.0/24"
            
            # Fallback to /24 subnet
            ip_parts = local_ip.split('.')
            return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            
        except Exception as e:
            self.logger.warning(f"Failed to get subnet range: {e}")
            return "192.168.1.0/24"  # Default fallback
    
    def _get_broadcast_address(self) -> str:
        """Get the broadcast address for the subnet"""
        try:
            # Parse subnet range
            subnet = ipaddress.IPv4Network(self.subnet_range, strict=False)
            return str(subnet.broadcast_address)
        except Exception as e:
            self.logger.warning(f"Failed to get broadcast address: {e}")
            return "192.168.1.255"  # Default fallback
    
    def _initialize_sockets(self):
        """Initialize discovery and communication sockets"""
        try:
            # Discovery socket (UDP broadcast)
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_socket.settimeout(1.0)
            
            # Try to bind to the broadcast port, fall back to any available port if needed
            try:
                self.discovery_socket.bind(('', self.broadcast_port))
            except OSError:
                # If port is busy, let the system choose an available port
                self.discovery_socket.bind(('', 0))
                self.broadcast_port = self.discovery_socket.getsockname()[1]
                self.logger.warning(f"Port {self.broadcast_port} busy, using port {self.broadcast_port}")
            
            # Communication socket (TCP)
            self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.communication_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.communication_socket.bind(('', self.port))
            self.communication_socket.listen(10)
            
            self.logger.info(f"Initialized discovery on port {self.broadcast_port}")
            self.logger.info(f"Initialized communication on port {self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize sockets: {e}")
            raise
    
    def start_discovery(self):
        """Start the discovery service"""
        if self.running:
            return
        
        self.running = True
        
        # Start discovery threads
        threading.Thread(target=self._discovery_listener, daemon=True).start()
        threading.Thread(target=self._communication_listener, daemon=True).start()
        threading.Thread(target=self._service_announcement_loop, daemon=True).start()
        threading.Thread(target=self._cleanup_services, daemon=True).start()
        
        self.logger.info("Subnet discovery started")
    
    def stop_discovery(self):
        """Stop the discovery service"""
        self.running = False
        
        # Send shutdown announcement
        self._announce_shutdown()
        
        # Close sockets
        if self.discovery_socket:
            self.discovery_socket.close()
        if self.communication_socket:
            self.communication_socket.close()
        
        self.logger.info("Subnet discovery stopped")
    
    def register_service(self, capabilities: List[str], metadata: Dict[str, Any] = None):
        """Register this application as a service"""
        service_id = self._generate_service_id()
        
        service_info = ServiceInfo(
            service_id=service_id,
            app_name=self.app_name,
            app_type=self.app_type,
            host=self._get_local_ip(),
            port=self.port,
            version="1.0.0",
            capabilities=capabilities,
            status="active",
            last_seen=time.time(),
            metadata=metadata or {}
        )
        
        self.local_services[service_id] = service_info
        self.services[service_id] = service_info
        
        self.logger.info(f"Registered service: {self.app_name} ({service_id})")
        return service_id
    
    def unregister_service(self, service_id: str):
        """Unregister a service"""
        if service_id in self.local_services:
            del self.local_services[service_id]
        if service_id in self.services:
            del self.services[service_id]
        
        self.logger.info(f"Unregistered service: {service_id}")
    
    def discover_services(self) -> List[ServiceInfo]:
        """Get all discovered services"""
        return list(self.services.values())
    
    def get_services_by_type(self, app_type: str) -> List[ServiceInfo]:
        """Get services by application type"""
        return [s for s in self.services.values() if s.app_type == app_type]
    
    def get_services_by_capability(self, capability: str) -> List[ServiceInfo]:
        """Get services by capability"""
        return [s for s in self.services.values() if capability in s.capabilities]
    
    def send_message(self, service_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific service"""
        try:
            service = self.services.get(service_id)
            if not service:
                self.logger.error(f"Service not found: {service_id}")
                return False
            
            # Create message
            message_data = {
                'from_service': list(self.local_services.keys())[0] if self.local_services else None,
                'to_service': service_id,
                'message_type': 'direct_message',
                'timestamp': time.time(),
                'data': message
            }
            
            # Send via TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((service.host, service.port))
            sock.sendall(json.dumps(message_data).encode())
            sock.close()
            
            self.logger.info(f"Sent message to {service.app_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {service_id}: {e}")
            return False
    
    def broadcast_message(self, message: Dict[str, Any], target_type: str = None):
        """Broadcast a message to all services or specific type"""
        message_data = {
            'from_service': list(self.local_services.keys())[0] if self.local_services else None,
            'message_type': 'broadcast',
            'target_type': target_type,
            'timestamp': time.time(),
            'data': message
        }
        
        # Send to relevant services
        target_services = []
        if target_type:
            target_services = self.get_services_by_type(target_type)
        else:
            target_services = list(self.services.values())
        
        for service in target_services:
            if service.service_id not in self.local_services:  # Don't send to self
                self.send_message(service.service_id, message_data)
    
    def add_callback(self, event_type: str, callback: Callable):
        """Add event callback"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _generate_service_id(self) -> str:
        """Generate a unique service ID"""
        timestamp = str(time.time())
        app_hash = hashlib.md5(f"{self.app_name}{timestamp}".encode()).hexdigest()[:8]
        return f"{self.app_name.lower().replace(' ', '_')}_{app_hash}"
    
    def register_local_service(self, app_name: str, app_type: str, port: int, version: str, capabilities: List[str], status: str) -> str:
        """Register a local service"""
        service_id = self._generate_service_id()
        
        service_info = ServiceInfo(
            service_id=service_id,
            app_name=app_name,
            app_type=app_type,
            host=self._get_local_ip(),
            port=port,
            version=version,
            capabilities=capabilities,
            status=status,
            last_seen=time.time(),
            metadata={}
        )
        
        self.local_services[service_id] = service_info
        self.services[service_id] = service_info
        
        # Announce the service
        self._announce_service(service_info)
        
        self.logger.info(f"Registered local service: {app_name} ({service_id})")
        return service_id
    
    def _service_announcement_loop(self):
        """Announce local services periodically"""
        while self.running:
            try:
                # Validate socket is still valid
                if not self.discovery_socket or self.discovery_socket.fileno() == -1:
                    self.logger.warning("Discovery socket invalid, reinitializing...")
                    self._initialize_sockets()
                    
                for service_info in self.local_services.values():
                    announcement = {
                        'type': 'service_announcement',
                        'service': asdict(service_info)
                    }
                    
                    # Validate broadcast address and use fallback if needed
                    try:
                        self.discovery_socket.sendto(
                            json.dumps(announcement).encode(),
                            (self.broadcast_address, self.broadcast_port)
                        )
                    except (OSError, socket.error) as send_error:
                        if "10022" in str(send_error) or "invalid argument" in str(send_error).lower():
                            # Try with localhost fallback
                            try:
                                self.discovery_socket.sendto(
                                    json.dumps(announcement).encode(),
                                    ("127.0.0.1", self.broadcast_port)
                                )
                                self.logger.warning("Used localhost fallback for broadcast")
                            except Exception as fallback_error:
                                self.logger.error(f"Even fallback failed: {fallback_error}")
                        else:
                            raise send_error
                
                time.sleep(30)  # Announce every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Announcement error: {e}")
                time.sleep(5)
    
    def _announce_service(self, service_info: ServiceInfo):
        """Announce a service to the subnet"""
        try:
            announcement = {
                'type': 'service_announcement',
                'service': asdict(service_info)
            }
            
            self.discovery_socket.sendto(
                json.dumps(announcement).encode(),
                (self.broadcast_address, self.broadcast_port)
            )
            
            self.logger.debug(f"Announced service: {service_info.app_name}")
            
        except (OSError, socket.error) as send_error:
            if "10022" in str(send_error) or "invalid argument" in str(send_error).lower():
                # Try with localhost fallback
                try:
                    self.discovery_socket.sendto(
                        json.dumps(announcement).encode(),
                        ("127.0.0.1", self.broadcast_port)
                    )
                    self.logger.warning("Used localhost fallback for service announcement")
                except Exception as fallback_error:
                    self.logger.error(f"Service announcement fallback failed: {fallback_error}")
            else:
                raise send_error
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Create a socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def _discovery_listener(self):
        """Listen for discovery broadcasts"""
        while self.running:
            try:
                data, addr = self.discovery_socket.recvfrom(1024)
                discovery_data = json.loads(data.decode())
                
                if discovery_data.get('type') == 'service_announcement':
                    service_info = ServiceInfo(**discovery_data['service'])
                    
                    # Update or add service
                    self.services[service_info.service_id] = service_info
                    
                    # Trigger callback
                    for callback in self.callbacks['service_discovered']:
                        callback(service_info)
                    
                    self.logger.debug(f"Discovered service: {service_info.app_name}")
                
                elif discovery_data.get('type') == 'service_shutdown':
                    service_id = discovery_data['service_id']
                    
                    if service_id in self.services:
                        service = self.services[service_id]
                        del self.services[service_id]
                        
                        # Trigger callback
                        for callback in self.callbacks['service_lost']:
                            callback(service)
                        
                        self.logger.debug(f"Service lost: {service.app_name}")
                
            except socket.timeout:
                continue
            except Exception as e:
                self.logger.error(f"Discovery listener error: {e}")
                time.sleep(1)
    
    def _communication_listener(self):
        """Listen for direct communication"""
        while self.running:
            try:
                client, addr = self.communication_socket.accept()
                
                # Handle communication in separate thread
                threading.Thread(target=self._handle_client, args=(client, addr), daemon=True).start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Communication listener error: {e}")
                time.sleep(1)
    
    def _handle_client(self, client: socket.socket, addr: tuple):
        """Handle incoming client connection"""
        try:
            data = client.recv(4096)
            message_data = json.loads(data.decode())
            
            # Trigger message received callback
            for callback in self.callbacks['message_received']:
                callback(message_data, addr)
            
            self.logger.debug(f"Received message from {addr}")
            
        except Exception as e:
            self.logger.error(f"Error handling client {addr}: {e}")
        finally:
            client.close()
    
                
    
    def _announce_shutdown(self):
        """Announce service shutdown"""
        try:
            for service_id in self.local_services.keys():
                shutdown_msg = {
                    'type': 'service_shutdown',
                    'service_id': service_id
                }
                
                self.discovery_socket.sendto(
                    json.dumps(shutdown_msg).encode(),
                    (self.broadcast_address, self.broadcast_port)
                )
                
        except Exception as e:
            self.logger.error(f"Shutdown announcement error: {e}")
    
    def _cleanup_services(self):
        """Clean up stale services"""
        while self.running:
            try:
                current_time = time.time()
                stale_services = []
                
                for service_id, service in self.services.items():
                    if current_time - service.last_seen > 120:  # 2 minutes timeout
                        stale_services.append(service_id)
                
                for service_id in stale_services:
                    if service_id in self.services:
                        service = self.services[service_id]
                        del self.services[service_id]
                        
                        # Trigger callback
                        for callback in self.callbacks['service_lost']:
                            callback(service)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
                time.sleep(30)

class SubnetCommunicator:
    """High-level communicator for subnet-wide app communication"""
    
    def __init__(self, app_name: str, app_type: str, port: int = None):
        self.discovery = SubnetDiscovery(app_name, app_type, port or (25566 + hash(app_name) % 100))
        self.message_handlers: Dict[str, Callable] = {}
        
        # Setup default handlers
        self.discovery.add_callback('message_received', self._handle_message)
    
    def start(self, capabilities: List[str] = None, metadata: Dict[str, Any] = None):
        """Start the communicator"""
        self.discovery.start_discovery()
        return self.discovery.register_service(capabilities or [], metadata or {})
    
    def stop(self):
        """Stop the communicator"""
        self.discovery.stop_discovery()
    
    def on_message(self, message_type: str, handler: Callable = None):
        """Register message handler - supports both decorator and direct call"""
        if handler is None:
            # Used as decorator
            def decorator(func):
                self.message_handlers[message_type] = func
                return func
            return decorator
        else:
            # Used as direct call
            self.message_handlers[message_type] = handler
    
    def send_to_app(self, app_name: str, message: Dict[str, Any]) -> bool:
        """Send message to specific app"""
        services = [s for s in self.discovery.discover_services() if s.app_name == app_name]
        if services:
            return self.discovery.send_message(services[0].service_id, message)
        return False
    
    def send_to_type(self, app_type: str, message: Dict[str, Any]):
        """Send message to all apps of specific type"""
        self.discovery.broadcast_message(message, app_type)
    
    def send_to_capability(self, capability: str, message: Dict[str, Any]):
        """Send message to all apps with specific capability"""
        services = self.discovery.get_services_by_capability(capability)
        for service in services:
            self.discovery.send_message(service.service_id, message)
    
    def get_all_apps(self) -> List[str]:
        """Get all discovered app names"""
        return list(set(s.app_name for s in self.discovery.discover_services()))
    
    def get_apps_by_type(self, app_type: str) -> List[str]:
        """Get apps by type"""
        return [s.app_name for s in self.discovery.get_services_by_type(app_type)]
    
    def get_apps_by_capability(self, capability: str) -> List[str]:
        """Get apps by capability"""
        return [s.app_name for s in self.discovery.get_services_by_capability(capability)]
    
    def _handle_message(self, message_data: Dict[str, Any], addr: tuple):
        """Handle incoming messages"""
        message_type = message_data.get('data', {}).get('type', 'unknown')
        
        if message_type in self.message_handlers:
            try:
                self.message_handlers[message_type](message_data, addr)
            except Exception as e:
                logging.error(f"Message handler error for {message_type}: {e}")

# Example usage and integration functions
def create_homelab_communicator(app_name: str, app_type: str, capabilities: List[str] = None):
    """Create a communicator for homelab apps"""
    communicator = SubnetCommunicator(app_name, app_type)
    service_id = communicator.start(capabilities or [])
    return communicator, service_id

def get_homelab_services():
    """Get all homelab services on the subnet"""
    temp_communicator = SubnetCommunicator("temp_discovery", "discovery")
    temp_communicator.discovery.start_discovery()
    time.sleep(2)  # Wait for discovery
    services = temp_communicator.discovery.discover_services()
    temp_communicator.stop()
    return services

if __name__ == "__main__":
    # Test the subnet discovery system
    logging.basicConfig(level=logging.INFO)
    
    # Create a test communicator
    communicator, service_id = create_homelab_communicator(
        "Test App", 
        "monitoring", 
        ["cpu_monitor", "memory_monitor"]
    )
    
    print(f"Service registered: {service_id}")
    
    # Wait for discovery
    time.sleep(5)
    
    # Show discovered services
    services = communicator.get_all_apps()
    print(f"Discovered apps: {services}")
    
    # Stop
    communicator.stop()
