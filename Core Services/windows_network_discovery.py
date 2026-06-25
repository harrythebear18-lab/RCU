#!/usr/bin/env python3
"""
Windows Network Discovery for Homelab Portal
Optimized for Windows 10/11 bidirectional communication
"""

import socket
import threading
import time
import json
import subprocess
import platform
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class WindowsNetworkDiscovery:
    """Windows-specific network discovery for Homelab Portal"""
    
    def __init__(self, node_id: str, port: int = 30000):
        self.node_id = node_id
        self.port = port
        self.discovery_port = port + 1  # UDP port for discovery
        self.broadcast_socket = None
        self.listen_socket = None
        self.running = False
        self.discovered_nodes = {}
        self.logger = logging.getLogger("WindowsNetworkDiscovery")
        
    def start_discovery(self):
        """Start network discovery service"""
        try:
            # Start listening for broadcasts
            self._start_listening()
            
            # Start broadcasting
            self._start_broadcasting()
            
            self.running = True
            self.logger.info("Windows network discovery started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start discovery: {e}")
            return False
    
    def _start_listening(self):
        """Start listening for discovery broadcasts"""
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind(('', self.discovery_port))
            self.listen_socket.settimeout(1.0)
            
            # Start listening thread
            listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            listen_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
    
    def _listen_loop(self):
        """Listen for discovery broadcasts"""
        while self.running:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                
                try:
                    node_info = json.loads(data.decode('utf-8'))
                    
                    # Ignore our own broadcasts
                    if node_info.get('node_id') == self.node_id:
                        continue
                    
                    # Add discovered node
                    self.discovered_nodes[node_info['node_id']] = {
                        'node_info': node_info,
                        'address': addr[0],
                        'last_seen': datetime.now()
                    }
                    
                    self.logger.info(f"Discovered node: {node_info.get('hostname')} from {addr[0]}")
                    
                except json.JSONDecodeError:
                    continue
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"Listen loop error: {e}")
    
    def _start_broadcasting(self):
        """Start broadcasting our presence"""
        try:
            broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
            broadcast_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start broadcasting: {e}")
    
    def _broadcast_loop(self):
        """Broadcast our presence periodically"""
        while self.running:
            try:
                self._broadcast_presence()
                time.sleep(15)  # Broadcast every 15 seconds
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Broadcast loop error: {e}")
    
    def _broadcast_presence(self):
        """Broadcast our presence to the network"""
        try:
            # Create node info
            node_info = {
                'node_id': self.node_id,
                'hostname': socket.gethostname(),
                'ip_address': self._get_local_ip(),
                'port': self.port,
                'platform': platform.system(),
                'platform_version': platform.version(),
                'capabilities': self._get_capabilities(),
                'timestamp': datetime.now().isoformat()
            }
            
            message = json.dumps(node_info).encode('utf-8')
            
            # Get Windows network interfaces
            broadcast_addresses = self._get_broadcast_addresses()
            
            for broadcast_addr in broadcast_addresses:
                try:
                    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    temp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    temp_socket.settimeout(2.0)
                    
                    temp_socket.sendto(message, (broadcast_addr, self.discovery_port))
                    temp_socket.close()
                    
                except Exception:
                    continue  # Ignore broadcast failures
                    
        except Exception as e:
            self.logger.error(f"Broadcast presence error: {e}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to external server to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_broadcast_addresses(self) -> List[str]:
        """Get broadcast addresses for all network interfaces"""
        broadcast_addresses = []
        
        try:
            # Get network interfaces using Windows commands
            if platform.system() == "Windows":
                # Use ipconfig to get network information
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
                
                # Parse ipconfig output to find network interfaces
                lines = result.stdout.split('\n')
                current_ip = None
                
                for line in lines:
                    line = line.strip()
                    
                    # Look for IPv4 Address
                    if 'IPv4 Address' in line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            current_ip = parts[1].strip()
                    
                    # Look for Subnet Mask
                    elif 'Subnet Mask' in line and ':' in line and current_ip:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            subnet_mask = parts[1].strip()
                            broadcast_addr = self._calculate_broadcast_address(current_ip, subnet_mask)
                            if broadcast_addr:
                                broadcast_addresses.append(broadcast_addr)
                            current_ip = None
                
                # Add common broadcast addresses
                broadcast_addresses.extend([
                    '255.255.255.255',
                    '192.168.1.255',
                    '192.168.0.255',
                    '10.0.0.255',
                    '172.16.0.255'
                ])
                
                # Remove duplicates
                broadcast_addresses = list(set(broadcast_addresses))
                
        except Exception as e:
            self.logger.error(f"Failed to get broadcast addresses: {e}")
            # Fallback to common addresses
            broadcast_addresses = ['255.255.255.255', '192.168.1.255', '192.168.0.255']
        
        return broadcast_addresses
    
    def _calculate_broadcast_address(self, ip: str, subnet_mask: str) -> Optional[str]:
        """Calculate broadcast address from IP and subnet mask"""
        try:
            ip_parts = [int(part) for part in ip.split('.')]
            mask_parts = [int(part) for part in subnet_mask.split('.')]
            
            if len(ip_parts) != 4 or len(mask_parts) != 4:
                return None
            
            # Calculate broadcast address
            broadcast_parts = []
            for i in range(4):
                broadcast_part = ip_parts[i] | (~mask_parts[i] & 255)
                broadcast_parts.append(str(broadcast_part))
            
            return '.'.join(broadcast_parts)
            
        except Exception:
            return None
    
    def _get_capabilities(self) -> List[str]:
        """Get system capabilities"""
        capabilities = ['file_transfer', 'resource_sharing']
        
        try:
            # Check screen sharing capability
            if platform.system() == "Windows":
                # Check if screen capture is available
                result = subprocess.run(['powershell', '-Command', 
                    'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width'], 
                    capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    capabilities.append('screen_sharing')
        except:
            pass
        
        try:
            # Check sound sharing capability
            if platform.system() == "Windows":
                # Check if audio devices are available
                result = subprocess.run(['powershell', '-Command', 
                    'Get-WmiObject -Class Win32_SoundDevice'], 
                    capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    capabilities.append('sound_sharing')
        except:
            pass
        
        return capabilities
    
    def get_discovered_nodes(self) -> Dict[str, Any]:
        """Get list of discovered nodes"""
        # Clean up old nodes (older than 2 minutes)
        current_time = datetime.now()
        expired_nodes = []
        
        for node_id, node_data in self.discovered_nodes.items():
            if (current_time - node_data['last_seen']).seconds > 120:
                expired_nodes.append(node_id)
        
        for node_id in expired_nodes:
            del self.discovered_nodes[node_id]
        
        return {
            node_id: {
                **node_data['node_info'],
                'address': node_data['address'],
                'last_seen': node_data['last_seen'].isoformat()
            }
            for node_id, node_data in self.discovered_nodes.items()
        }
    
    def stop(self):
        """Stop network discovery"""
        self.running = False
        
        if self.broadcast_socket:
            self.broadcast_socket.close()
        
        if self.listen_socket:
            self.listen_socket.close()
        
        self.discovered_nodes.clear()
        self.logger.info("Windows network discovery stopped")
