#!/usr/bin/env python3
"""
Integrated Homelab System with PC Authentication
Combines the streamlined homelab system with PC-to-PC authentication.
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import both systems
try:
    from streamlined_homelab_system import streamlined_homelab, Resource, Allocation
    from pc_auth_system import pc_auth_system, PeerInfo, AuthStatus
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Integration import error: {e}")
    INTEGRATION_AVAILABLE = False

class IntegratedHomelabSystem:
    """Integrated homelab system with PC authentication"""
    
    def __init__(self):
        self.db_path = current_dir / "integrated_homelab.db"
        self.settings_file = current_dir / "integrated_settings.json"
        
        # Setup logging
        self.setup_logging()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Integration state
        self.auth_enabled = self.settings.get('auth_enabled', True)
        self.resource_sharing_enabled = self.settings.get('resource_sharing_enabled', True)
        
        # Authenticated peers and their resource access
        self.authenticated_peers = {}
        self.peer_resource_access = {}
        
        # Initialize systems
        self.initialize_systems()
        
        # Start monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()
        
        self.logger.info("Integrated Homelab System with PC Authentication initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        self.logger = logging.getLogger('IntegratedHomelab')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = current_dir / "integrated_homelab.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load integrated system settings"""
        default_settings = {
            'auth_enabled': True,
            'resource_sharing_enabled': True,
            'auto_trust_peers': False,
            'require_auth_for_resources': True,
            'peer_resource_limits': {
                'max_ram_gb': 4.0,
                'max_cpu_cores': 2,
                'max_gpu_gb': 2.0
            },
            'auth_timeout': 3600,
            'session_timeout': 1800,
            'discovery_interval': 30,
            'monitoring_interval': 30
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
        """Save integrated system settings"""
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
        """Initialize integrated database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Peer resource access table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peer_resource_access (
                id TEXT PRIMARY KEY,
                peer_id TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                access_level TEXT DEFAULT 'read',
                allocated_amount REAL DEFAULT 0,
                max_allowed REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                properties TEXT,
                FOREIGN KEY (peer_id) REFERENCES peers (id)
            )
        ''')
        
        # Resource sharing events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_sharing_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_peer TEXT,
                target_peer TEXT,
                resource_id TEXT,
                event_type TEXT NOT NULL,
                amount REAL,
                description TEXT,
                details TEXT,
                success BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Integration settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_systems(self):
        """Initialize both homelab and auth systems"""
        try:
            if INTEGRATION_AVAILABLE:
                # Start PC discovery
                if self.auth_enabled:
                    pc_auth_system.start_discovery_service()
                    self.logger.info("PC authentication system started")
                
                # Initialize resource sharing with auth
                if self.resource_sharing_enabled:
                    self.setup_resource_sharing_with_auth()
                    self.logger.info("Resource sharing with authentication enabled")
                
            else:
                self.logger.error("Failed to initialize integration - systems not available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize systems: {e}")
    
    def setup_resource_sharing_with_auth(self):
        """Setup resource sharing with authentication integration"""
        try:
            # Register local peer in resource system
            self.register_local_peer_in_resources()
            
            # Setup peer resource access controls
            self.setup_peer_resource_access()
            
            # Hook into resource allocation for auth checks
            self.setup_resource_allocation_auth()
            
        except Exception as e:
            self.logger.error(f"Failed to setup resource sharing with auth: {e}")
    
    def register_local_peer_in_resources(self):
        """Register local peer in resource system"""
        try:
            # Create a client registration for local system
            client_id = f"peer_{pc_auth_system.local_peer.id}"
            
            # Register with streamlined homelab
            if hasattr(streamlined_homelab, 'register_client'):
                streamlined_homelab.register_client(
                    client_id=client_id,
                    name=pc_auth_system.local_peer.name,
                    hostname=pc_auth_system.local_peer.hostname,
                    ip_address=pc_auth_system.local_peer.ip_address,
                    role=pc_auth_system.local_peer.role.value,
                    properties={
                        'peer_id': pc_auth_system.local_peer.id,
                        'fingerprint': pc_auth_system.local_peer.fingerprint,
                        'authenticated': True
                    }
                )
            
            self.logger.info(f"Local peer registered in resource system: {client_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to register local peer in resources: {e}")
    
    def setup_peer_resource_access(self):
        """Setup peer resource access controls"""
        try:
            # Load existing peer resource access from database
            self.load_peer_resource_access()
            
            # Setup default access for trusted peers
            self.setup_trusted_peer_access()
            
        except Exception as e:
            self.logger.error(f"Failed to setup peer resource access: {e}")
    
    def load_peer_resource_access(self):
        """Load peer resource access from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM peer_resource_access')
            rows = cursor.fetchall()
            
            for row in rows:
                peer_id = row[1]
                resource_id = row[2]
                access_data = {
                    'access_level': row[3],
                    'allocated_amount': row[4],
                    'max_allowed': row[5],
                    'created_at': row[6],
                    'expires_at': row[7],
                    'properties': json.loads(row[8]) if row[8] else {}
                }
                
                if peer_id not in self.peer_resource_access:
                    self.peer_resource_access[peer_id] = {}
                
                self.peer_resource_access[peer_id][resource_id] = access_data
            
            conn.close()
            self.logger.info(f"Loaded resource access for {len(self.peer_resource_access)} peers")
            
        except Exception as e:
            self.logger.error(f"Failed to load peer resource access: {e}")
    
    def setup_trusted_peer_access(self):
        """Setup default access for trusted peers"""
        try:
            if not self.settings.get('auto_trust_peers', False):
                return
            
            # Get trusted peers from auth system
            trusted_peer_ids = pc_auth_system.trusted_peers
            
            for peer_id in trusted_peer_ids:
                if peer_id not in self.peer_resource_access:
                    # Setup default resource access for trusted peers
                    self.setup_default_peer_access(peer_id)
            
            self.logger.info(f"Setup default access for {len(trusted_peer_ids)} trusted peers")
            
        except Exception as e:
            self.logger.error(f"Failed to setup trusted peer access: {e}")
    
    def setup_default_peer_access(self, peer_id: str):
        """Setup default resource access for a peer"""
        try:
            # Get resource limits from settings
            limits = self.settings.get('peer_resource_limits', {})
            
            # Setup access to each resource type
            for resource_id, resource in streamlined_homelab.resources.items():
                access_data = {
                    'access_level': 'read' if resource.type == 'network' else 'read_write',
                    'allocated_amount': 0.0,
                    'max_allowed': 0.0,
                    'created_at': datetime.now(),
                    'expires_at': None,
                    'properties': {
                        'peer_id': peer_id,
                        'auto_granted': True,
                        'trusted_peer': True
                    }
                }
                
                # Set max allowed based on resource type
                if resource.type == 'ram':
                    access_data['max_allowed'] = limits.get('max_ram_gb', 4.0)
                elif resource.type == 'cpu':
                    access_data['max_allowed'] = limits.get('max_cpu_cores', 2.0)
                elif resource.type == 'gpu':
                    access_data['max_allowed'] = limits.get('max_gpu_gb', 2.0)
                elif resource.type == 'network':
                    access_data['max_allowed'] = resource.capacity * 0.5  # 50% of network
                
                # Save to database
                self.save_peer_resource_access(peer_id, resource_id, access_data)
                
                # Add to memory
                if peer_id not in self.peer_resource_access:
                    self.peer_resource_access[peer_id] = {}
                
                self.peer_resource_access[peer_id][resource_id] = access_data
            
        except Exception as e:
            self.logger.error(f"Failed to setup default access for peer {peer_id}: {e}")
    
    def setup_resource_allocation_auth(self):
        """Setup authentication checks for resource allocation"""
        try:
            # This would hook into the resource allocation system
            # For now, we'll provide the auth check methods
            self.logger.info("Resource allocation authentication checks enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to setup resource allocation auth: {e}")
    
    def authenticate_peer_for_resources(self, peer_id: str, session_token: str) -> bool:
        """Authenticate a peer for resource access"""
        try:
            if not self.auth_enabled:
                return True
            
            # Validate session token
            validated_peer_id = pc_auth_system.validate_session_token(session_token)
            
            if not validated_peer_id or validated_peer_id != peer_id:
                self.logger.warning(f"Invalid session token for peer {peer_id}")
                return False
            
            # Check if peer is blocked
            if peer_id in pc_auth_system.blocked_peers:
                self.logger.warning(f"Blocked peer {peer_id} attempted resource access")
                return False
            
            # Mark peer as authenticated for resources
            self.authenticated_peers[peer_id] = {
                'authenticated_at': datetime.now(),
                'session_token': session_token,
                'expires_at': datetime.now() + timedelta(seconds=self.settings.get('session_timeout', 1800))
            }
            
            self.logger.info(f"Peer {peer_id} authenticated for resource access")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to authenticate peer {peer_id}: {e}")
            return False
    
    def can_peer_allocate_resource(self, peer_id: str, resource_id: str, amount: float) -> bool:
        """Check if peer can allocate a resource"""
        try:
            if not self.resource_sharing_enabled:
                return False
            
            # Check if peer is authenticated
            if peer_id not in self.authenticated_peers:
                return False
            
            # Check if peer has access to this resource
            if peer_id not in self.peer_resource_access:
                return False
            
            if resource_id not in self.peer_resource_access[peer_id]:
                return False
            
            access_data = self.peer_resource_access[peer_id][resource_id]
            
            # Check access level
            if access_data['access_level'] not in ['read_write', 'full']:
                return False
            
            # Check allocation limits
            current_allocated = access_data['allocated_amount']
            max_allowed = access_data['max_allowed']
            
            if current_allocated + amount > max_allowed:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check peer resource allocation: {e}")
            return False
    
    def allocate_resource_to_peer(self, peer_id: str, resource_id: str, amount: float, 
                                session_token: str, properties: Dict[str, Any] = None) -> Optional[str]:
        """Allocate resource to authenticated peer"""
        try:
            # Authenticate peer
            if not self.authenticate_peer_for_resources(peer_id, session_token):
                return None
            
            # Check if allocation is allowed
            if not self.can_peer_allocate_resource(peer_id, resource_id, amount):
                return None
            
            # Create client ID for peer
            client_id = f"peer_{peer_id}"
            
            # Allocate resource through streamlined system
            allocation = streamlined_homelab.allocate_resource(resource_id, client_id, amount, properties)
            
            if allocation:
                # Update peer resource access
                access_data = self.peer_resource_access[peer_id][resource_id]
                access_data['allocated_amount'] += amount
                access_data['last_allocation'] = datetime.now()
                
                # Save to database
                self.save_peer_resource_access(peer_id, resource_id, access_data)
                
                # Log resource sharing event
                self.log_resource_sharing_event(peer_id, resource_id, 'allocation', amount,
                                             f"Peer {peer_id} allocated {amount} of {resource_id}")
                
                self.logger.info(f"Resource {resource_id} allocated to peer {peer_id}: {amount}")
                return allocation.id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to allocate resource to peer {peer_id}: {e}")
            return None
    
    def release_resource_from_peer(self, peer_id: str, allocation_id: str, session_token: str) -> bool:
        """Release resource allocation from peer"""
        try:
            # Authenticate peer
            if not self.authenticate_peer_for_resources(peer_id, session_token):
                return False
            
            # Find allocation
            if allocation_id not in streamlined_homelab.allocations:
                return False
            
            allocation = streamlined_homelab.allocations[allocation_id]
            
            # Check if allocation belongs to peer
            client_id = f"peer_{peer_id}"
            if allocation.client_id != client_id:
                return False
            
            # Release resource
            if streamlined_homelab.release_resource(allocation_id):
                # Update peer resource access
                resource_id = allocation.resource_id
                if peer_id in self.peer_resource_access and resource_id in self.peer_resource_access[peer_id]:
                    access_data = self.peer_resource_access[peer_id][resource_id]
                    access_data['allocated_amount'] -= allocation.amount
                    access_data['last_release'] = datetime.now()
                    
                    # Save to database
                    self.save_peer_resource_access(peer_id, resource_id, access_data)
                
                # Log resource sharing event
                self.log_resource_sharing_event(peer_id, resource_id, 'release', allocation.amount,
                                             f"Peer {peer_id} released {allocation.amount} of {resource_id}")
                
                self.logger.info(f"Resource allocation {allocation_id} released from peer {peer_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to release resource from peer {peer_id}: {e}")
            return False
    
    def save_peer_resource_access(self, peer_id: str, resource_id: str, access_data: Dict[str, Any]):
        """Save peer resource access to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO peer_resource_access 
                (id, peer_id, resource_id, access_level, allocated_amount, max_allowed, 
                 created_at, expires_at, properties)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"{peer_id}_{resource_id}", peer_id, resource_id, access_data['access_level'],
                  access_data['allocated_amount'], access_data['max_allowed'],
                  access_data['created_at'], access_data['expires_at'],
                  json.dumps(access_data['properties'])))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save peer resource access: {e}")
    
    def log_resource_sharing_event(self, peer_id: str, resource_id: str, event_type: str, 
                                 amount: float, description: str, details: Dict[str, Any] = None):
        """Log resource sharing event"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO resource_sharing_events 
                (source_peer, resource_id, event_type, amount, description, details, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (peer_id, resource_id, event_type, amount, description, 
                  json.dumps(details or {}), True))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to log resource sharing event: {e}")
    
    def get_integrated_status(self) -> Dict[str, Any]:
        """Get integrated system status"""
        try:
            # Get status from both systems
            homelab_status = streamlined_homelab.get_system_status() if INTEGRATION_AVAILABLE else {}
            auth_status = pc_auth_system.get_system_status() if INTEGRATION_AVAILABLE else {}
            
            # Get integration-specific status
            integration_status = {
                'auth_enabled': self.auth_enabled,
                'resource_sharing_enabled': self.resource_sharing_enabled,
                'authenticated_peers': len(self.authenticated_peers),
                'peer_resource_access': len(self.peer_resource_access),
                'trusted_peers_with_access': len([pid for pid in self.peer_resource_access 
                                                if pid in pc_auth_system.trusted_peers])
            }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'integration_available': INTEGRATION_AVAILABLE,
                'homelab_status': homelab_status,
                'auth_status': auth_status,
                'integration_status': integration_status
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get integrated status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def start_monitoring(self):
        """Start integrated system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Integrated system monitoring started")
    
    def stop_monitoring(self):
        """Stop integrated system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Integrated system monitoring stopped")
    
    def _monitoring_loop(self):
        """Integrated system monitoring loop"""
        while self.monitoring_active:
            try:
                # Clean up expired authenticated peers
                self.cleanup_expired_authenticated_peers()
                
                # Clean up expired peer resource access
                self.cleanup_expired_peer_access()
                
                # Monitor resource sharing with authenticated peers
                self.monitor_peer_resource_usage()
                
                # Sleep for monitoring interval
                time.sleep(self.settings.get('monitoring_interval', 30))
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def cleanup_expired_authenticated_peers(self):
        """Clean up expired authenticated peers"""
        try:
            current_time = datetime.now()
            expired_peers = []
            
            for peer_id, auth_data in self.authenticated_peers.items():
                if current_time > auth_data['expires_at']:
                    expired_peers.append(peer_id)
            
            for peer_id in expired_peers:
                del self.authenticated_peers[peer_id]
                self.logger.info(f"Cleaned up expired authentication for peer {peer_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired authenticated peers: {e}")
    
    def cleanup_expired_peer_access(self):
        """Clean up expired peer resource access"""
        try:
            current_time = datetime.now()
            expired_access = []
            
            for peer_id, resources in self.peer_resource_access.items():
                for resource_id, access_data in resources.items():
                    if access_data.get('expires_at') and current_time > access_data['expires_at']:
                        expired_access.append((peer_id, resource_id))
            
            for peer_id, resource_id in expired_access:
                del self.peer_resource_access[peer_id][resource_id]
                self.logger.info(f"Cleaned up expired resource access for peer {peer_id}, resource {resource_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired peer access: {e}")
    
    def monitor_peer_resource_usage(self):
        """Monitor resource usage by authenticated peers"""
        try:
            for peer_id, auth_data in self.authenticated_peers.items():
                # Get resource usage for this peer
                client_id = f"peer_{peer_id}"
                
                # Count active allocations for this peer
                active_allocations = 0
                total_allocated = 0.0
                
                for allocation in streamlined_homelab.allocations.values():
                    if allocation.client_id == client_id:
                        active_allocations += 1
                        total_allocated += allocation.amount
                
                # Log if peer has high usage
                if active_allocations > 0:
                    self.logger.debug(f"Peer {peer_id} has {active_allocations} active allocations, total: {total_allocated}")
                
        except Exception as e:
            self.logger.error(f"Failed to monitor peer resource usage: {e}")

# Global integrated system instance
integrated_homelab = IntegratedHomelabSystem()

if __name__ == '__main__':
    # Test the integrated system
    print("🏠🔐 Testing Integrated Homelab System with PC Authentication")
    
    # Get integrated status
    status = integrated_homelab.get_integrated_status()
    print(f"Integrated Status: {status}")
    
    # Keep running
    try:
        while True:
            time.sleep(60)
            status = integrated_homelab.get_integrated_status()
            auth_status = status.get('auth_status', {})
            integration_status = status.get('integration_status', {})
            print(f"🔄 Integrated system running... Authenticated Peers: {integration_status.get('authenticated_peers', 0)}, Resource Access: {integration_status.get('peer_resource_access', 0)}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        integrated_homelab.stop_monitoring()
        if INTEGRATION_AVAILABLE:
            pc_auth_system.stop_discovery_service()
