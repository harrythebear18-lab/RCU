#!/usr/bin/env python3
"""
PC-to-PC Authentication System
Simple, secure authentication and handshake system for same-subnet homelab PCs.
"""

import os
import sys
import json
import time
import socket
import threading
import hashlib
import secrets
import hmac
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sqlite3
import subprocess
import platform
import ipaddress
from dataclasses import dataclass, asdict
from enum import Enum

class AuthStatus(Enum):
    """Authentication status enumeration"""
    UNKNOWN = "unknown"
    PENDING = "pending"
    AUTHENTICATED = "authenticated"
    TRUSTED = "trusted"
    BLOCKED = "blocked"
    EXPIRED = "expired"

class PeerRole(Enum):
    """Peer role enumeration"""
    SERVER = "server"
    CLIENT = "client"
    PEER = "peer"

@dataclass
class PeerInfo:
    """Peer information structure"""
    id: str
    name: str
    hostname: str
    ip_address: str
    mac_address: str
    role: PeerRole
    status: AuthStatus
    fingerprint: str
    created_at: datetime
    last_seen: datetime
    auth_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()

class PCAuthSystem:
    """PC-to-PC authentication system for same-subnet homelab"""
    
    def __init__(self, port: int = 8081):
        self.port = port
        self.db_path = Path(__file__).parent / "pc_auth.db"
        self.settings_file = Path(__file__).parent / "pc_auth_settings.json"
        
        # Setup logging
        self.setup_logging()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Peer management
        self.peers = {}
        self.trusted_peers = set()
        self.blocked_peers = set()
        
        # Authentication tokens
        self.auth_tokens = {}
        self.session_tokens = {}
        
        # Get local system info
        self.local_peer = self.get_local_peer_info()
        
        # Network discovery
        self.discovery_active = False
        self.discovery_thread = None
        self.discovery_socket = None
        
        # Authentication server
        self.server_active = False
        self.server_thread = None
        self.server_socket = None
        
        # Client connections
        self.client_connections = {}
        
        # Initialize system
        self.initialize_system()
        
        self.logger.info(f"PC Auth System initialized - Role: {self.local_peer.role.value}")
    
    def setup_logging(self):
        """Setup logging system"""
        self.logger = logging.getLogger('PCAuthSystem')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = Path(__file__).parent / "pc_auth.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load authentication settings"""
        default_settings = {
            'subnet': '192.168.1.0/24',
            'discovery_enabled': True,
            'discovery_interval': 30,
            'auth_timeout': 3600,
            'session_timeout': 1800,
            'max_peers': 20,
            'auto_trust': False,
            'require_approval': True,
            'encryption_enabled': True,
            'log_level': 'INFO'
        }
        
        try:
            if self.settings_file.exists():
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
        """Save authentication settings"""
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
        """Initialize authentication database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Peers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hostname TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                mac_address TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'unknown',
                fingerprint TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                auth_token TEXT,
                expires_at TIMESTAMP,
                properties TEXT
            )
        ''')
        
        # Authentication tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id TEXT PRIMARY KEY,
                peer_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_used TIMESTAMP,
                properties TEXT,
                FOREIGN KEY (peer_id) REFERENCES peers (id)
            )
        ''')
        
        # Session tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_tokens (
                id TEXT PRIMARY KEY,
                peer_id TEXT NOT NULL,
                session_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_activity TIMESTAMP,
                properties TEXT,
                FOREIGN KEY (peer_id) REFERENCES peers (id)
            )
        ''')
        
        # Authentication events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_peer TEXT,
                target_peer TEXT,
                event_type TEXT NOT NULL,
                description TEXT,
                details TEXT,
                success BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_local_peer_info(self) -> PeerInfo:
        """Get local peer information"""
        try:
            # Get system information
            hostname = socket.gethostname()
            
            # Get IP address
            local_ip = self.get_local_ip()
            
            # Get MAC address
            mac_address = self.get_mac_address()
            
            # Generate fingerprint
            fingerprint = self.generate_fingerprint(hostname, local_ip, mac_address)
            
            # Determine role based on system capabilities
            role = self.determine_peer_role()
            
            return PeerInfo(
                id=f"peer_{hash(hostname + local_ip) % 10000}",
                name=f"{hostname}-PC",
                hostname=hostname,
                ip_address=local_ip,
                mac_address=mac_address,
                role=role,
                status=AuthStatus.UNKNOWN,
                fingerprint=fingerprint,
                created_at=datetime.now(),
                last_seen=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get local peer info: {e}")
            return PeerInfo(
                id="unknown_peer",
                name="Unknown PC",
                hostname="unknown",
                ip_address="127.0.0.1",
                mac_address="00:00:00:00:00:00",
                role=PeerRole.PEER,
                status=AuthStatus.UNKNOWN,
                fingerprint="unknown",
                created_at=datetime.now(),
                last_seen=datetime.now()
            )
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Try to get local IP by connecting to external address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            # Fallback to hostname resolution
            try:
                return socket.gethostbyname(socket.gethostname())
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
    
    def generate_fingerprint(self, hostname: str, ip: str, mac: str) -> str:
        """Generate unique fingerprint for peer"""
        try:
            fingerprint_data = f"{hostname}|{ip}|{mac}|{platform.platform()}"
            return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        except:
            return hashlib.sha256(f"{hostname}{ip}{mac}".encode()).hexdigest()[:16]
    
    def determine_peer_role(self) -> PeerRole:
        """Determine peer role based on system capabilities"""
        try:
            # Get system information
            cpu_count = os.cpu_count() or 4
            memory_gb = psutil.virtual_memory().total / (1024**3) if hasattr(psutil, 'virtual_memory') else 8
            
            # Determine role based on capabilities
            if cpu_count >= 8 and memory_gb >= 16:
                return PeerRole.SERVER
            elif cpu_count >= 4 and memory_gb >= 8:
                return PeerRole.PEER
            else:
                return PeerRole.CLIENT
                
        except Exception as e:
            self.logger.error(f"Failed to determine peer role: {e}")
            return PeerRole.PEER
    
    def initialize_system(self):
        """Initialize the authentication system"""
        try:
            # Load existing peers from database
            self.load_peers()
            
            # Load trusted peers
            self.load_trusted_peers()
            
            # Load blocked peers
            self.load_blocked_peers()
            
            # Register local peer
            self.register_peer(self.local_peer)
            
            self.logger.info(f"PC Auth System initialized with {len(self.peers)} known peers")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
    
    def load_peers(self):
        """Load peers from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM peers')
            rows = cursor.fetchall()
            
            for row in rows:
                peer = PeerInfo(
                    id=row[0],
                    name=row[1],
                    hostname=row[2],
                    ip_address=row[3],
                    mac_address=row[4],
                    role=PeerRole(row[5]),
                    status=AuthStatus(row[6]),
                    fingerprint=row[7],
                    created_at=datetime.fromisoformat(row[8]),
                    last_seen=datetime.fromisoformat(row[9]),
                    auth_token=row[10],
                    expires_at=datetime.fromisoformat(row[11]) if row[11] else None,
                    properties=json.loads(row[12]) if row[12] else {}
                )
                self.peers[peer.id] = peer
            
            conn.close()
            self.logger.info(f"Loaded {len(self.peers)} peers from database")
            
        except Exception as e:
            self.logger.error(f"Failed to load peers: {e}")
    
    def load_trusted_peers(self):
        """Load trusted peers from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM peers WHERE status = ?', (AuthStatus.TRUSTED.value,))
            rows = cursor.fetchall()
            
            self.trusted_peers = {row[0] for row in rows}
            
            conn.close()
            self.logger.info(f"Loaded {len(self.trusted_peers)} trusted peers")
            
        except Exception as e:
            self.logger.error(f"Failed to load trusted peers: {e}")
    
    def load_blocked_peers(self):
        """Load blocked peers from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM peers WHERE status = ?', (AuthStatus.BLOCKED.value,))
            rows = cursor.fetchall()
            
            self.blocked_peers = {row[0] for row in rows}
            
            conn.close()
            self.logger.info(f"Loaded {len(self.blocked_peers)} blocked peers")
            
        except Exception as e:
            self.logger.error(f"Failed to load blocked peers: {e}")
    
    def register_peer(self, peer: PeerInfo) -> bool:
        """Register a peer in the system"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO peers 
                (id, name, hostname, ip_address, mac_address, role, status, fingerprint, 
                 created_at, last_seen, auth_token, expires_at, properties)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (peer.id, peer.name, peer.hostname, peer.ip_address, peer.mac_address,
                  peer.role.value, peer.status.value, peer.fingerprint,
                  peer.created_at, peer.last_seen, peer.auth_token, peer.expires_at,
                  json.dumps(peer.properties)))
            
            conn.commit()
            conn.close()
            
            self.peers[peer.id] = peer
            
            # Log authentication event
            self.log_auth_event('system', peer.id, 'peer_registered', 
                             f"Peer {peer.name} registered successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register peer {peer.id}: {e}")
            return False
    
    def discover_peers(self) -> List[PeerInfo]:
        """Discover peers on the same subnet"""
        try:
            discovered_peers = []
            subnet = ipaddress.IPv4Network(self.settings.get('subnet', '192.168.1.0/24'))
            
            # Scan subnet for active hosts
            for ip in subnet.hosts():
                ip_str = str(ip)
                if ip_str == self.local_peer.ip_address:
                    continue  # Skip self
                
                if self.ping_host(ip_str):
                    # Try to get peer info from the host
                    peer_info = self.get_peer_info_from_host(ip_str)
                    if peer_info:
                        discovered_peers.append(peer_info)
                        self.register_peer(peer_info)
            
            self.logger.info(f"Discovered {len(discovered_peers)} peers on subnet")
            return discovered_peers
            
        except Exception as e:
            self.logger.error(f"Failed to discover peers: {e}")
            return []
    
    def ping_host(self, ip: str, timeout: float = 1.0) -> bool:
        """Ping a host to check if it's reachable"""
        try:
            # Use ping command (cross-platform)
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(int(timeout * 1000)), ip]
            else:
                cmd = ['ping', '-c', '1', '-W', str(int(timeout)), ip]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1)
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.debug(f"Ping failed for {ip}: {e}")
            return False
    
    def get_peer_info_from_host(self, ip: str) -> Optional[PeerInfo]:
        """Get peer info from remote host"""
        try:
            # Try to connect to peer info service
            response = self.send_discovery_request(ip)
            if response:
                return PeerInfo(**response)
        except Exception as e:
            self.logger.debug(f"Failed to get peer info from {ip}: {e}")
        return None
    
    def send_discovery_request(self, ip: str) -> Optional[Dict[str, Any]]:
        """Send discovery request to remote peer"""
        try:
            # Create discovery request
            request = {
                'type': 'discovery_request',
                'source_peer_id': self.local_peer.id,
                'timestamp': datetime.now().isoformat(),
                'fingerprint': self.local_peer.fingerprint
            }
            
            # Send request (simplified version)
            # In a real implementation, this would use HTTP or UDP
            return {'status': 'success', 'peer_info': 'discovered'}
            
        except Exception as e:
            self.logger.error(f"Failed to send discovery request to {ip}: {e}")
            return None
    
    def start_discovery_service(self):
        """Start network discovery service"""
        if self.discovery_active:
            return
        
        self.discovery_active = True
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()
        
        self.logger.info("Network discovery service started")
    
    def stop_discovery_service(self):
        """Stop network discovery service"""
        self.discovery_active = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=5)
        
        self.logger.info("Network discovery service stopped")
    
    def _discovery_loop(self):
        """Discovery service loop"""
        while self.discovery_active:
            try:
                if self.settings.get('discovery_enabled', True):
                    self.discover_peers()
                
                # Sleep for discovery interval
                time.sleep(self.settings.get('discovery_interval', 30))
                
            except Exception as e:
                self.logger.error(f"Discovery loop error: {e}")
                time.sleep(10)
    
    def authenticate_peer(self, peer_id: str, credentials: Dict[str, Any]) -> Optional[str]:
        """Authenticate a peer and return session token"""
        try:
            if peer_id not in self.peers:
                self.logger.error(f"Unknown peer: {peer_id}")
                return None
            
            peer = self.peers[peer_id]
            
            # Check if peer is blocked
            if peer_id in self.blocked_peers:
                self.logger.warning(f"Blocked peer attempted authentication: {peer_id}")
                return None
            
            # Verify credentials
            if not self.verify_credentials(peer, credentials):
                self.logger.warning(f"Invalid credentials for peer: {peer_id}")
                return None
            
            # Generate session token
            session_token = self.generate_session_token(peer_id)
            
            # Update peer status
            peer.status = AuthStatus.AUTHENTICATED
            peer.last_seen = datetime.now()
            peer.expires_at = datetime.now() + timedelta(seconds=self.settings.get('session_timeout', 1800))
            
            # Save to database
            self.update_peer(peer)
            
            # Store session token
            self.session_tokens[session_token] = {
                'peer_id': peer_id,
                'created_at': datetime.now(),
                'expires_at': peer.expires_at
            }
            
            # Log authentication event
            self.log_auth_event('authentication', peer_id, 'peer_authenticated',
                             f"Peer {peer.name} authenticated successfully")
            
            return session_token
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate peer {peer_id}: {e}")
            return None
    
    def verify_credentials(self, peer: PeerInfo, credentials: Dict[str, Any]) -> bool:
        """Verify peer credentials"""
        try:
            # Check if credentials match expected format
            if 'fingerprint' not in credentials:
                return False
            
            # Verify fingerprint
            if credentials['fingerprint'] != peer.fingerprint:
                return False
            
            # Check timestamp (prevent replay attacks)
            if 'timestamp' in credentials:
                try:
                    timestamp = datetime.fromisoformat(credentials['timestamp'])
                    if datetime.now() - timestamp > timedelta(minutes=5):
                        return False
                except:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify credentials: {e}")
            return False
    
    def generate_session_token(self, peer_id: str) -> str:
        """Generate session token for peer"""
        try:
            token_data = f"{peer_id}:{datetime.now().isoformat()}:{secrets.token_hex(16)}"
            token_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            # Store token hash in database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO session_tokens 
                (id, peer_id, session_hash, created_at, expires_at, last_activity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (token_hash[:16], peer_id, token_hash, datetime.now(),
                  datetime.now() + timedelta(seconds=self.settings.get('session_timeout', 1800)),
                  datetime.now()))
            
            conn.commit()
            conn.close()
            
            return token_hash[:16]  # Return first 16 characters as token
            
        except Exception as e:
            self.logger.error(f"Failed to generate session token: {e}")
            return None
    
    def validate_session_token(self, token: str) -> Optional[str]:
        """Validate session token and return peer_id"""
        try:
            if token not in self.session_tokens:
                return None
            
            token_data = self.session_tokens[token]
            
            # Check if token is expired
            if datetime.now() > token_data['expires_at']:
                del self.session_tokens[token]
                return None
            
            # Update last activity
            token_data['last_activity'] = datetime.now()
            
            return token_data['peer_id']
            
        except Exception as e:
            self.logger.error(f"Failed to validate session token: {e}")
            return None
    
    def trust_peer(self, peer_id: str) -> bool:
        """Trust a peer"""
        try:
            if peer_id not in self.peers:
                return False
            
            peer = self.peers[peer_id]
            peer.status = AuthStatus.TRUSTED
            peer.expires_at = None  # Trusted peers don't expire
            
            # Update database
            self.update_peer(peer)
            
            # Add to trusted set
            self.trusted_peers.add(peer_id)
            
            # Log event
            self.log_auth_event('trust', peer_id, 'peer_trusted',
                             f"Peer {peer.name} marked as trusted")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trust peer {peer_id}: {e}")
            return False
    
    def block_peer(self, peer_id: str) -> bool:
        """Block a peer"""
        try:
            if peer_id not in self.peers:
                return False
            
            peer = self.peers[peer_id]
            peer.status = AuthStatus.BLOCKED
            
            # Update database
            self.update_peer(peer)
            
            # Add to blocked set
            self.blocked_peers.add(peer_id)
            
            # Remove from trusted if it was trusted
            self.trusted_peers.discard(peer_id)
            
            # Remove session tokens
            tokens_to_remove = [token for token, data in self.session_tokens.items() 
                               if data['peer_id'] == peer_id]
            for token in tokens_to_remove:
                del self.session_tokens[token]
            
            # Log event
            self.log_auth_event('block', peer_id, 'peer_blocked',
                             f"Peer {peer.name} marked as blocked")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to block peer {peer_id}: {e}")
            return False
    
    def update_peer(self, peer: PeerInfo) -> bool:
        """Update peer in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE peers SET name=?, hostname=?, ip_address=?, mac_address=?,
                role=?, status=?, fingerprint=?, last_seen=?, auth_token=?,
                expires_at=?, properties=? WHERE id=?
            ''', (peer.name, peer.hostname, peer.ip_address, peer.mac_address,
                  peer.role.value, peer.status.value, peer.fingerprint,
                  peer.last_seen, peer.auth_token, peer.expires_at,
                  json.dumps(peer.properties), peer.id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update peer {peer.id}: {e}")
            return False
    
    def log_auth_event(self, source: str, target: str, event_type: str, 
                      description: str, details: Dict[str, Any] = None, success: bool = True):
        """Log authentication event"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO auth_events 
                (source_peer, target_peer, event_type, description, details, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source, target, event_type, description, json.dumps(details or {}), success))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to log auth event: {e}")
    
    def get_peer_status(self, peer_id: str) -> Dict[str, Any]:
        """Get peer status information"""
        try:
            if peer_id not in self.peers:
                return {'status': 'unknown', 'message': 'Peer not found'}
            
            peer = self.peers[peer_id]
            
            return {
                'id': peer.id,
                'name': peer.name,
                'hostname': peer.hostname,
                'ip_address': peer.ip_address,
                'role': peer.role.value,
                'status': peer.status.value,
                'fingerprint': peer.fingerprint,
                'created_at': peer.created_at.isoformat(),
                'last_seen': peer.last_seen.isoformat(),
                'is_trusted': peer_id in self.trusted_peers,
                'is_blocked': peer_id in self.blocked_peers,
                'has_session': any(data['peer_id'] == peer_id for data in self.session_tokens.values())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get peer status for {peer_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            return {
                'local_peer': {
                    'id': self.local_peer.id,
                    'name': self.local_peer.name,
                    'hostname': self.local_peer.hostname,
                    'ip_address': self.local_peer.ip_address,
                    'role': self.local_peer.role.value,
                    'status': self.local_peer.status.value
                },
                'peers': {
                    'total': len(self.peers),
                    'trusted': len(self.trusted_peers),
                    'blocked': len(self.blocked_peers),
                    'authenticated': len([p for p in self.peers.values() if p.status == AuthStatus.AUTHENTICATED]),
                    'unknown': len([p for p in self.peers.values() if p.status == AuthStatus.UNKNOWN])
                },
                'sessions': {
                    'active': len(self.session_tokens),
                    'max_sessions': self.settings.get('max_peers', 20)
                },
                'services': {
                    'discovery_active': self.discovery_active,
                    'server_active': self.server_active,
                    'local_ip': self.local_peer.ip_address,
                    'subnet': self.settings.get('subnet', '192.168.1.0/24')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {'status': 'error', 'message': str(e)}

# Global PC auth system instance
pc_auth_system = PCAuthSystem()

if __name__ == '__main__':
    # Test the PC auth system
    print("[LOCK] Testing PC-to-PC Authentication System")
    
    # Get system status
    status = pc_auth_system.get_system_status()
    print(f"System Status: {status}")
    
    # Start discovery service
    pc_auth_system.start_discovery_service()
    
    # Keep running
    try:
        while True:
            time.sleep(60)
            status = pc_auth_system.get_system_status()
            print(f"[REFRESH] Auth system running... Peers: {status['peers']['total']}, Sessions: {status['sessions']['active']}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        pc_auth_system.stop_discovery_service()
