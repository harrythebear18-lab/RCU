#!/usr/bin/env python3
"""
Bidirectional Resource Sharing Service
Replaces port 25565 with robust peer-to-peer communication
Supports bidirectional data flow between Windows 10/11 systems
"""

import asyncio
import socket
import json
import time
import threading
import hashlib
import uuid
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import psutil
import platform
from enum import Enum

class ResourceType(Enum):
    CPU = "cpu"
    RAM = "ram"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"

class MessageType(Enum):
    RESOURCE_OFFER = "resource_offer"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_RESPONSE = "resource_response"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    DATA_TRANSFER = "data_transfer"
    ACKNOWLEDGMENT = "acknowledgment"

@dataclass
class ResourceInfo:
    type: str  # Store as string for JSON serialization
    amount: float
    unit: str
    available: bool
    priority: int
    system_id: str
    timestamp: str  # Store as string for JSON serialization

@dataclass
class PeerInfo:
    system_id: str
    hostname: str
    ip_address: str
    port: int
    last_seen: str  # Store as string for JSON serialization
    capabilities: List[str]  # Store as strings for JSON serialization
    status: str

@dataclass
class Message:
    type: str  # Store as string for JSON serialization
    sender_id: str
    receiver_id: Optional[str]
    timestamp: str  # Store as string for JSON serialization
    data: Dict[str, Any]
    message_id: str

class BidirectionalResourceSharing:
    """Robust bidirectional resource sharing system"""
    
    def __init__(self, system_id: str = None, port_range: Tuple[int, int] = (30000, 31000)):
        self.system_id = system_id or self._generate_system_id()
        self.hostname = socket.gethostname()
        self.local_ip = self._get_local_ip()
        self.port_range = port_range
        self.server_port = None
        self.server_socket = None
        self.peers: Dict[str, PeerInfo] = {}
        self.resources: Dict[str, ResourceInfo] = {}
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.running = False
        self.discovery_active = False
        
        # Setup logging
        self.logger = logging.getLogger(f"ResourceSharing-{self.system_id[:8]}")
        self.logger.setLevel(logging.INFO)
        
        # Initialize system resources
        self._initialize_resources()
        
    def _generate_system_id(self) -> str:
        """Generate unique system ID"""
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        return hashlib.sha256(f"{mac}-{platform.node()}-{time.time()}".encode()).hexdigest()[:16]
    
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
    
    def _initialize_resources(self):
        """Initialize system resources"""
        # CPU Resources
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        self.resources[f"cpu_{self.system_id}"] = ResourceInfo(
            type=ResourceType.CPU.value,
            amount=cpu_count,
            unit="cores",
            available=True,
            priority=1,
            system_id=self.system_id,
            timestamp=datetime.now().isoformat()
        )
        
        # RAM Resources
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        
        self.resources[f"ram_{self.system_id}"] = ResourceInfo(
            type=ResourceType.RAM.value,
            amount=available_gb,
            unit="GB",
            available=True,
            priority=2,
            system_id=self.system_id,
            timestamp=datetime.now().isoformat()
        )
        
        # GPU Resources (if available)
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                self.resources[f"gpu_{self.system_id}_{i}"] = ResourceInfo(
                    type=ResourceType.GPU.value,
                    amount=gpu.memoryFree / 1024,  # GB
                    unit="GB",
                    available=True,
                    priority=3,
                    system_id=self.system_id,
                    timestamp=datetime.now().isoformat()
                )
        except ImportError:
            self.logger.warning("GPUtil not available, GPU resources not detected")
        
        # Storage Resources
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        
        self.resources[f"storage_{self.system_id}"] = ResourceInfo(
            type=ResourceType.STORAGE.value,
            amount=free_gb,
            unit="GB",
            available=True,
            priority=4,
            system_id=self.system_id,
            timestamp=datetime.now().isoformat()
        )
        
        self.logger.info(f"Initialized {len(self.resources)} resources")
    
    def _find_available_port(self) -> int:
        """Find available port in range"""
        for port in range(self.port_range[0], self.port_range[1]):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        raise RuntimeError("No available ports in range")
    
    async def start_server(self) -> int:
        """Start the resource sharing server"""
        try:
            self.server_port = self._find_available_port()
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', self.server_port))
            self.server_socket.listen(10)
            
            self.running = True
            self.logger.info(f"Resource sharing server started on port {self.server_port}")
            
            # Start server loop
            asyncio.create_task(self._server_loop())
            
            return self.server_port
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    async def _server_loop(self):
        """Main server loop"""
        while self.running:
            try:
                client_socket, address = await asyncio.get_event_loop().sock_accept(self.server_socket)
                asyncio.create_task(self._handle_client(client_socket, address))
            except Exception as e:
                if self.running:
                    self.logger.error(f"Server loop error: {e}")
                break
    
    async def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle incoming client connections"""
        try:
            while self.running:
                data = await asyncio.get_event_loop().sock_recv(client_socket, 4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    await self._process_message(message, client_socket)
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON received from {address}")
                
        except Exception as e:
            self.logger.error(f"Client handler error: {e}")
        finally:
            client_socket.close()
    
    async def _process_message(self, message_data: Dict[str, Any], client_socket: socket.socket):
        """Process incoming message"""
        try:
            message = Message(
                type=message_data['type'],  # Already a string
                sender_id=message_data['sender_id'],
                receiver_id=message_data.get('receiver_id'),
                timestamp=message_data['timestamp'],  # Already a string
                data=message_data['data'],
                message_id=message_data['message_id']
            )
            
            self.logger.debug(f"Received {message.type} from {message.sender_id}")
            
            # Update peer info
            if message.sender_id != self.system_id:
                self._update_peer_info(message.sender_id, client_socket.getpeername()[0])
            
            # Handle message based on type
            if message.type == MessageType.DISCOVERY.value:
                await self._handle_discovery(message, client_socket)
            elif message.type == MessageType.RESOURCE_OFFER.value:
                await self._handle_resource_offer(message)
            elif message.type == MessageType.RESOURCE_REQUEST.value:
                await self._handle_resource_request(message)
            elif message.type == MessageType.RESOURCE_RESPONSE.value:
                await self._handle_resource_response(message)
            elif message.type == MessageType.HEARTBEAT.value:
                await self._handle_heartbeat(message)
            
            # Call custom handlers
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        self.logger.error(f"Handler error: {e}")
                        
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
    
    def _update_peer_info(self, sender_id: str, ip_address: str):
        """Update peer information"""
        if sender_id not in self.peers:
            self.peers[sender_id] = PeerInfo(
                system_id=sender_id,
                hostname="unknown",
                ip_address=ip_address,
                port=0,
                last_seen=datetime.now().isoformat(),
                capabilities=[],
                status="active"
            )
        else:
            self.peers[sender_id].last_seen = datetime.now().isoformat()
            self.peers[sender_id].status = "active"
    
    async def _handle_discovery(self, message: Message, client_socket: socket.socket):
        """Handle discovery message"""
        response = Message(
            type=MessageType.DISCOVERY.value,
            sender_id=self.system_id,
            receiver_id=message.sender_id,
            timestamp=datetime.now().isoformat(),
            data={
                'hostname': self.hostname,
                'ip_address': self.local_ip,
                'port': self.server_port,
                'capabilities': [r.type for r in self.resources.values()],
                'resources': {k: asdict(v) for k, v in self.resources.items()}
            },
            message_id=str(uuid.uuid4())
        )
        
        await self._send_message(response, client_socket)
    
    async def _handle_resource_offer(self, message: Message):
        """Handle resource offer"""
        resources = message.data.get('resources', {})
        for resource_id, resource_data in resources.items():
            resource_info = ResourceInfo(**resource_data)
            self.resources[resource_id] = resource_info
        
        self.logger.info(f"Received resource offer from {message.sender_id}: {len(resources)} resources")
    
    async def _handle_resource_request(self, message: Message):
        """Handle resource request"""
        requested_type = message.data.get('type')
        requested_amount = message.data.get('amount', 0)
        
        # Find available resources
        available_resources = [
            r for r in self.resources.values() 
            if r.type == requested_type and r.available and r.amount >= requested_amount
        ]
        
        if available_resources:
            # Select best resource (lowest priority number = higher priority)
            best_resource = min(available_resources, key=lambda r: r.priority)
            
            response = Message(
                type=MessageType.RESOURCE_RESPONSE.value,
                sender_id=self.system_id,
                receiver_id=message.sender_id,
                timestamp=datetime.now().isoformat(),
                data={
                    'resource_id': f"{best_resource.type}_{self.system_id}",
                    'amount': best_resource.amount,
                    'unit': best_resource.unit,
                    'granted': True
                },
                message_id=str(uuid.uuid4())
            )
        else:
            response = Message(
                type=MessageType.RESOURCE_RESPONSE.value,
                sender_id=self.system_id,
                receiver_id=message.sender_id,
                timestamp=datetime.now().isoformat(),
                data={
                    'granted': False,
                    'reason': 'No available resources'
                },
                message_id=str(uuid.uuid4())
            )
        
        # Send response back to requester
        peer_info = self.peers.get(message.sender_id)
        if peer_info:
            await self._send_to_peer(peer_info, response)
    
    async def _handle_resource_response(self, message: Message):
        """Handle resource response"""
        self.logger.info(f"Resource response from {message.sender_id}: {message.data}")
    
    async def _handle_heartbeat(self, message: Message):
        """Handle heartbeat message"""
        self._update_peer_info(message.sender_id, message.data.get('ip_address', ''))
    
    async def _send_message(self, message: Message, socket: socket.socket):
        """Send message through socket"""
        try:
            message_data = {
                'type': message.type,  # Already a string
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'timestamp': message.timestamp,  # Already a string
                'data': message.data,
                'message_id': message.message_id
            }
            
            data = json.dumps(message_data).encode()
            await asyncio.get_event_loop().sock_sendall(socket, data)
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
    
    async def _send_to_peer(self, peer: PeerInfo, message: Message):
        """Send message to specific peer"""
        try:
            reader, writer = await asyncio.open_connection(peer.ip_address, peer.port)
            
            message_data = {
                'type': message.type,  # Already a string
                'sender_id': message.sender_id,
                'receiver_id': message.receiver_id,
                'timestamp': message.timestamp,  # Already a string
                'data': message.data,
                'message_id': message.message_id
            }
            
            data = json.dumps(message_data).encode()
            writer.write(data)
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            self.logger.error(f"Failed to send to peer {peer.system_id}: {e}")
    
    async def discover_peers(self, target_network: str = "192.168.1.0/24"):
        """Discover peers on network"""
        self.discovery_active = True
        self.logger.info(f"Starting peer discovery on {target_network}")
        
        # Parse network range
        network_parts = target_network.split('.')
        base_ip = '.'.join(network_parts[:3])
        
        # Scan network range
        tasks = []
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            if ip != self.local_ip:  # Skip self
                tasks.append(self._scan_host(ip))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.discovery_active = False
        self.logger.info(f"Discovery completed. Found {len(self.peers)} peers")
    
    async def _scan_host(self, ip: str):
        """Scan specific host for resource sharing service"""
        for port in range(self.port_range[0], self.port_range[1]):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port), timeout=1.0
                )
                
                # Send discovery message
                discovery = Message(
                    type=MessageType.DISCOVERY.value,
                    sender_id=self.system_id,
                    receiver_id=None,
                    timestamp=datetime.now().isoformat(),
                    data={'scan': True},
                    message_id=str(uuid.uuid4())
                )
                
                await self._send_message(discovery, writer._socket)
                writer.close()
                await writer.wait_closed()
                
                break  # Found service, stop scanning this host
                
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                continue
    
    async def offer_resources(self, target_peer_id: str = None):
        """Offer resources to peers"""
        offer_message = Message(
            type=MessageType.RESOURCE_OFFER.value,
            sender_id=self.system_id,
            receiver_id=target_peer_id,
            timestamp=datetime.now().isoformat(),
            data={
                'resources': {k: asdict(v) for k, v in self.resources.items()}
            },
            message_id=str(uuid.uuid4())
        )
        
        if target_peer_id:
            # Send to specific peer
            peer = self.peers.get(target_peer_id)
            if peer:
                await self._send_to_peer(peer, offer_message)
        else:
            # Broadcast to all peers
            for peer in self.peers.values():
                await self._send_to_peer(peer, offer_message)
    
    async def request_resource(self, resource_type: ResourceType, amount: float, target_peer_id: str = None):
        """Request resource from peers"""
        request_message = Message(
            type=MessageType.RESOURCE_REQUEST.value,
            sender_id=self.system_id,
            receiver_id=target_peer_id,
            timestamp=datetime.now().isoformat(),
            data={
                'type': resource_type.value,
                'amount': amount
            },
            message_id=str(uuid.uuid4())
        )
        
        if target_peer_id:
            # Send to specific peer
            peer = self.peers.get(target_peer_id)
            if peer:
                await self._send_to_peer(peer, request_message)
        else:
            # Broadcast to all peers
            for peer in self.peers.values():
                await self._send_to_peer(peer, request_message)
    
    async def start_heartbeat(self, interval: int = 30):
        """Start heartbeat to maintain connections"""
        while self.running:
            try:
                heartbeat = Message(
                    type=MessageType.HEARTBEAT.value,
                    sender_id=self.system_id,
                    receiver_id=None,
                    timestamp=datetime.now().isoformat(),
                    data={'ip_address': self.local_ip},
                    message_id=str(uuid.uuid4())
                )
                
                for peer in list(self.peers.values()):
                    await self._send_to_peer(peer, heartbeat)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(interval)
    
    def add_message_handler(self, message_type: MessageType, handler: Callable):
        """Add custom message handler"""
        type_str = message_type.value
        if type_str not in self.message_handlers:
            self.message_handlers[type_str] = []
        self.message_handlers[type_str].append(handler)
    
    def get_peer_status(self) -> Dict[str, Any]:
        """Get peer and resource status"""
        return {
            'system_id': self.system_id,
            'hostname': self.hostname,
            'ip_address': self.local_ip,
            'port': self.server_port,
            'peers': {k: asdict(v) for k, v in self.peers.items()},
            'resources': {k: asdict(v) for k, v in self.resources.items()},
            'total_peers': len(self.peers),
            'total_resources': len(self.resources)
        }
    
    async def stop(self):
        """Stop the resource sharing service"""
        self.running = False
        self.discovery_active = False
        
        if self.server_socket:
            self.server_socket.close()
        
        self.logger.info("Resource sharing service stopped")

# Global instance for easy access
_resource_sharing_instance = None

def get_resource_sharing() -> BidirectionalResourceSharing:
    """Get global resource sharing instance"""
    global _resource_sharing_instance
    if _resource_sharing_instance is None:
        _resource_sharing_instance = BidirectionalResourceSharing()
    return _resource_sharing_instance

async def initialize_resource_sharing(port_range: Tuple[int, int] = (30000, 31000)) -> int:
    """Initialize resource sharing service"""
    sharing = get_resource_sharing()
    port = await sharing.start_server()
    
    # Start heartbeat
    asyncio.create_task(sharing.start_heartbeat())
    
    return port
