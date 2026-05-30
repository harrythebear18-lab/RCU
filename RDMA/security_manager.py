#!/usr/bin/env python3
"""
Security Manager for Software-Defined RDMA
Provides authentication, authorization, and encryption
"""

import os
import hashlib
import hmac
import json
import time
import threading
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import secrets

@dataclass
class User:
    """User account for DMA access"""
    username: str
    password_hash: str
    salt: str
    permissions: Set[str]
    created_at: float
    last_login: Optional[float] = None
    active: bool = True
    api_keys: List[str] = None
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = []

@dataclass
class AccessPolicy:
    """Access control policy for memory regions"""
    region_id: str
    allowed_users: Set[str]
    permissions: Set[str]  # read, write, admin
    max_bandwidth_mbps: Optional[int] = None
    time_restrictions: Optional[Dict] = None
    ip_whitelist: List[str] = None

@dataclass
class SecurityConfig:
    """Security configuration"""
    require_authentication: bool = True
    require_encryption: bool = True
    session_timeout: int = 3600  # 1 hour
    max_failed_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    audit_log_retention: int = 30  # days
    encryption_algorithm: str = "AES-256-GCM"

class SecurityManager:
    """Comprehensive security management for DMA operations"""
    
    def __init__(self, config_file: str = "dma_security.json"):
        self.config_file = config_file
        self.config = SecurityConfig()
        
        # Security storage
        self.users: Dict[str, User] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self.failed_attempts: Dict[str, List[float]] = {}
        
        # Encryption keys
        self.master_key: Optional[bytes] = None
        self.encryption_keys: Dict[str, bytes] = {}
        
        # Audit log
        self.audit_log: List[Dict] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Load existing configuration
        self._load_configuration()
        self._initialize_encryption()
    
    def _load_configuration(self):
        """Load security configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Load config
                if 'config' in data:
                    config_dict = data['config']
                    self.config = SecurityConfig(**config_dict)
                
                # Load users
                if 'users' in data:
                    for username, user_data in data['users'].items():
                        user = User(
                            username=user_data['username'],
                            password_hash=user_data['password_hash'],
                            salt=user_data['salt'],
                            permissions=set(user_data['permissions']),
                            created_at=user_data['created_at'],
                            last_login=user_data.get('last_login'),
                            active=user_data.get('active', True),
                            api_keys=user_data.get('api_keys', [])
                        )
                        self.users[username] = user
                
                # Load policies
                if 'policies' in data:
                    for region_id, policy_data in data['policies'].items():
                        policy = AccessPolicy(
                            region_id=policy_data['region_id'],
                            allowed_users=set(policy_data['allowed_users']),
                            permissions=set(policy_data['permissions']),
                            max_bandwidth_mbps=policy_data.get('max_bandwidth_mbps'),
                            time_restrictions=policy_data.get('time_restrictions'),
                            ip_whitelist=policy_data.get('ip_whitelist', [])
                        )
                        self.policies[region_id] = policy
                
                # Load audit log
                if 'audit_log' in data:
                    self.audit_log = data['audit_log']
                    
            except Exception as e:
                print(f"Failed to load security configuration: {e}")
                self._create_default_configuration()
        else:
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default security configuration"""
        # Create admin user
        admin_password = "admin123"  # Should be changed immediately
        admin_salt = secrets.token_hex(16)
        admin_hash = self._hash_password(admin_password, admin_salt)
        
        admin_user = User(
            username="admin",
            password_hash=admin_hash,
            salt=admin_salt,
            permissions={"admin", "read", "write", "create_region", "delete_region"},
            created_at=time.time(),
            active=True
        )
        self.users["admin"] = admin_user
        
        # Create default policy for all regions
        default_policy = AccessPolicy(
            region_id="*",
            allowed_users={"admin"},
            permissions={"admin", "read", "write"},
            max_bandwidth_mbps=1000,
            ip_whitelist=["127.0.0.1", "::1"]
        )
        self.policies["*"] = default_policy
        
        self._save_configuration()
    
    def _initialize_encryption(self):
        """Initialize encryption keys"""
        # Generate or load master key
        key_file = "dma_master.key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.master_key = f.read()
        else:
            # Generate new master key
            self.master_key = secrets.token_bytes(32)
            with open(key_file, 'wb') as f:
                f.write(self.master_key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
        
        # Initialize Fernet for general encryption
        self.fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password: str, user: User) -> bool:
        """Verify password against hash"""
        return hmac.compare_digest(self._hash_password(password, user.salt), user.password_hash)
    
    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM"""
        if not self.config.require_encryption:
            return data
        
        # Generate random IV
        iv = secrets.token_bytes(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Return IV + ciphertext + tag
        return iv + ciphertext + encryptor.tag
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        if not self.config.require_encryption:
            return encrypted_data
        
        # Extract IV, ciphertext, and tag
        iv = encrypted_data[:12]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[12:-16]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _log_audit_event(self, event_type: str, username: str, details: Dict):
        """Log security audit event"""
        with self.lock:
            event = {
                'timestamp': time.time(),
                'event_type': event_type,
                'username': username,
                'details': details,
                'ip_address': details.get('ip_address', 'unknown')
            }
            
            self.audit_log.append(event)
            
            # Trim old log entries
            cutoff_time = time.time() - (self.config.audit_log_retention * 24 * 3600)
            self.audit_log = [e for e in self.audit_log if e['timestamp'] > cutoff_time]
    
    def authenticate_user(self, username: str, password: str, ip_address: str = "unknown") -> Optional[str]:
        """Authenticate user and return session token"""
        with self.lock:
            # Check if user is locked out
            if username in self.failed_attempts:
                recent_attempts = [t for t in self.failed_attempts[username] 
                                if time.time() - t < self.config.lockout_duration]
                if len(recent_attempts) >= self.config.max_failed_attempts:
                    self._log_audit_event("login_blocked", username, 
                                        {"reason": "too_many_failed_attempts", "ip_address": ip_address})
                    return None
            
            # Check user exists and is active
            if username not in self.users or not self.users[username].active:
                self._log_audit_event("login_failed", username, 
                                    {"reason": "invalid_user", "ip_address": ip_address})
                return None
            
            # Verify password
            user = self.users[username]
            if not self._verify_password(password, user):
                # Record failed attempt
                if username not in self.failed_attempts:
                    self.failed_attempts[username] = []
                self.failed_attempts[username].append(time.time())
                
                self._log_audit_event("login_failed", username, 
                                    {"reason": "invalid_password", "ip_address": ip_address})
                return None
            
            # Clear failed attempts
            if username in self.failed_attempts:
                del self.failed_attempts[username]
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Store session
            self.active_sessions[session_token] = {
                'username': username,
                'created_at': time.time(),
                'last_activity': time.time(),
                'ip_address': ip_address
            }
            
            # Update user last login
            user.last_login = time.time()
            
            self._log_audit_event("login_success", username, {"ip_address": ip_address})
            
            return session_token
    
    def authenticate_api_key(self, api_key: str, ip_address: str = "unknown") -> Optional[str]:
        """Authenticate using API key"""
        with self.lock:
            # Find user with this API key
            for username, user in self.users.items():
                if api_key in user.api_keys and user.active:
                    # Generate session token
                    session_token = secrets.token_urlsafe(32)
                    
                    self.active_sessions[session_token] = {
                        'username': username,
                        'created_at': time.time(),
                        'last_activity': time.time(),
                        'ip_address': ip_address,
                        'api_key': True
                    }
                    
                    self._log_audit_event("api_login_success", username, {"ip_address": ip_address})
                    
                    return session_token
            
            self._log_audit_event("api_login_failed", "unknown", {"ip_address": ip_address})
            return None
    
    def validate_session(self, session_token: str, ip_address: str = "unknown") -> Optional[str]:
        """Validate session token and return username"""
        with self.lock:
            if session_token not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_token]
            
            # Check session timeout
            if time.time() - session['last_activity'] > self.config.session_timeout:
                del self.active_sessions[session_token]
                self._log_audit_event("session_expired", session['username'], {"ip_address": ip_address})
                return None
            
            # Check IP address (optional security measure)
            if session['ip_address'] != ip_address:
                del self.active_sessions[session_token]
                self._log_audit_event("session_hijack_attempt", session['username'], 
                                    {"original_ip": session['ip_address'], "new_ip": ip_address})
                return None
            
            # Update last activity
            session['last_activity'] = time.time()
            
            return session['username']
    
    def check_permission(self, username: str, region_id: str, permission: str, 
                        ip_address: str = "unknown") -> bool:
        """Check if user has permission for specific operation"""
        with self.lock:
            user = self.users.get(username)
            if not user or not user.active:
                return False
            
            # Check admin permission
            if "admin" in user.permissions:
                return True
            
            # Find applicable policy
            policy = None
            if region_id in self.policies:
                policy = self.policies[region_id]
            elif "*" in self.policies:
                policy = self.policies["*"]
            
            if not policy:
                return False
            
            # Check if user is allowed
            if username not in policy.allowed_users:
                self._log_audit_event("permission_denied", username, 
                                    {"region_id": region_id, "permission": permission, 
                                     "reason": "not_in_allowed_users", "ip_address": ip_address})
                return False
            
            # Check specific permission
            if permission not in policy.permissions and permission not in user.permissions:
                self._log_audit_event("permission_denied", username, 
                                    {"region_id": region_id, "permission": permission, 
                                     "reason": "insufficient_permissions", "ip_address": ip_address})
                return False
            
            # Check IP whitelist
            if policy.ip_whitelist and ip_address not in policy.ip_whitelist:
                self._log_audit_event("permission_denied", username, 
                                    {"region_id": region_id, "permission": permission, 
                                     "reason": "ip_not_whitelisted", "ip_address": ip_address})
                return False
            
            # Check time restrictions
            if policy.time_restrictions:
                current_time = time.time()
                current_hour = time.localtime(current_time).tm_hour
                
                if 'allowed_hours' in policy.time_restrictions:
                    if current_hour not in policy.time_restrictions['allowed_hours']:
                        self._log_audit_event("permission_denied", username, 
                                            {"region_id": region_id, "permission": permission, 
                                             "reason": "time_restriction", "ip_address": ip_address})
                        return False
            
            return True
    
    def create_user(self, username: str, password: str, permissions: Set[str], 
                   created_by: str = "system") -> bool:
        """Create new user account"""
        with self.lock:
            if username in self.users:
                return False
            
            # Validate permissions
            valid_permissions = {"admin", "read", "write", "create_region", "delete_region", "manage_users"}
            if not permissions.issubset(valid_permissions):
                return False
            
            # Create user
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            user = User(
                username=username,
                password_hash=password_hash,
                salt=salt,
                permissions=permissions,
                created_at=time.time(),
                active=True
            )
            
            self.users[username] = user
            
            self._log_audit_event("user_created", username, 
                                {"created_by": created_by, "permissions": list(permissions)})
            
            return True
    
    def create_api_key(self, username: str, created_by: str = "system") -> Optional[str]:
        """Create API key for user"""
        with self.lock:
            user = self.users.get(username)
            if not user or not user.active:
                return None
            
            api_key = self._generate_api_key()
            user.api_keys.append(api_key)
            
            self._log_audit_event("api_key_created", username, 
                                {"created_by": created_by, "api_key_prefix": api_key[:8]})
            
            return api_key
    
    def revoke_api_key(self, username: str, api_key: str, revoked_by: str = "system") -> bool:
        """Revoke API key"""
        with self.lock:
            user = self.users.get(username)
            if not user:
                return False
            
            if api_key in user.api_keys:
                user.api_keys.remove(api_key)
                self._log_audit_event("api_key_revoked", username, 
                                    {"revoked_by": revoked_by, "api_key_prefix": api_key[:8]})
                return True
            
            return False
    
    def create_access_policy(self, region_id: str, allowed_users: Set[str], 
                          permissions: Set[str], created_by: str = "system") -> bool:
        """Create access policy for memory region"""
        with self.lock:
            # Validate users exist
            for username in allowed_users:
                if username not in self.users:
                    return False
            
            # Validate permissions
            valid_permissions = {"read", "write", "admin"}
            if not permissions.issubset(valid_permissions):
                return False
            
            policy = AccessPolicy(
                region_id=region_id,
                allowed_users=allowed_users,
                permissions=permissions
            )
            
            self.policies[region_id] = policy
            
            self._log_audit_event("policy_created", created_by, 
                                {"region_id": region_id, "allowed_users": list(allowed_users), 
                                 "permissions": list(permissions)})
            
            return True
    
    def encrypt_dma_data(self, data: bytes, region_id: str) -> bytes:
        """Encrypt DMA data for transmission"""
        if not self.config.require_encryption:
            return data
        
        # Use region-specific key if available, otherwise master key
        key = self.encryption_keys.get(region_id, self.master_key)
        
        # Generate random IV
        iv = secrets.token_bytes(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Return IV + ciphertext + tag
        return iv + ciphertext + encryptor.tag
    
    def decrypt_dma_data(self, encrypted_data: bytes, region_id: str) -> bytes:
        """Decrypt DMA data after transmission"""
        if not self.config.require_encryption:
            return encrypted_data
        
        # Use region-specific key if available, otherwise master key
        key = self.encryption_keys.get(region_id, self.master_key)
        
        # Extract IV, ciphertext, and tag
        iv = encrypted_data[:12]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[12:-16]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def get_audit_log(self, username: str = None, event_type: str = None, 
                     start_time: float = None, end_time: float = None) -> List[Dict]:
        """Get filtered audit log"""
        with self.lock:
            filtered_log = self.audit_log.copy()
            
            # Apply filters
            if username:
                filtered_log = [e for e in filtered_log if e['username'] == username]
            
            if event_type:
                filtered_log = [e for e in filtered_log if e['event_type'] == event_type]
            
            if start_time:
                filtered_log = [e for e in filtered_log if e['timestamp'] >= start_time]
            
            if end_time:
                filtered_log = [e for e in filtered_log if e['timestamp'] <= end_time]
            
            return filtered_log
    
    def _save_configuration(self):
        """Save security configuration to file"""
        try:
            data = {
                'config': asdict(self.config),
                'users': {
                    username: {
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'salt': user.salt,
                        'permissions': list(user.permissions),
                        'created_at': user.created_at,
                        'last_login': user.last_login,
                        'active': user.active,
                        'api_keys': user.api_keys
                    }
                    for username, user in self.users.items()
                },
                'policies': {
                    region_id: {
                        'region_id': policy.region_id,
                        'allowed_users': list(policy.allowed_users),
                        'permissions': list(policy.permissions),
                        'max_bandwidth_mbps': policy.max_bandwidth_mbps,
                        'time_restrictions': policy.time_restrictions,
                        'ip_whitelist': policy.ip_whitelist
                    }
                    for region_id, policy in self.policies.items()
                },
                'audit_log': self.audit_log[-1000:]  # Save last 1000 entries
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)
            
        except Exception as e:
            print(f"Failed to save security configuration: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        with self.lock:
            current_time = time.time()
            expired_tokens = [
                token for token, session in self.active_sessions.items()
                if current_time - session['last_activity'] > self.config.session_timeout
            ]
            
            for token in expired_tokens:
                session = self.active_sessions[token]
                self._log_audit_event("session_expired", session['username'], 
                                    {"reason": "timeout"})
                del self.active_sessions[token]
    
    def get_security_stats(self) -> Dict:
        """Get security statistics"""
        with self.lock:
            return {
                'total_users': len(self.users),
                'active_users': len([u for u in self.users.values() if u.active]),
                'active_sessions': len(self.active_sessions),
                'total_policies': len(self.policies),
                'audit_log_entries': len(self.audit_log),
                'failed_attempts': len(self.failed_attempts),
                'config': asdict(self.config)
            }

def demo_security_manager():
    """Demonstration of security manager"""
    print("Security Manager Demo")
    print("=" * 30)
    
    # Initialize security manager
    sec = SecurityManager()
    
    # Test authentication
    print("Testing authentication...")
    session_token = sec.authenticate_user("admin", "admin123", "127.0.0.1")
    if session_token:
        print("✓ Admin authentication successful")
        
        # Test session validation
        username = sec.validate_session(session_token, "127.0.0.1")
        if username:
            print(f"✓ Session validation successful for {username}")
        
        # Test permission check
        if sec.check_permission(username, "test_region", "read"):
            print("✓ Permission check successful")
        
        # Test data encryption
        test_data = b"Sensitive DMA data"
        encrypted = sec.encrypt_dma_data(test_data, "test_region")
        decrypted = sec.decrypt_dma_data(encrypted, "test_region")
        
        if decrypted == test_data:
            print("✓ Data encryption/decryption successful")
        
        # Create API key
        api_key = sec.create_api_key(username)
        if api_key:
            print(f"✓ API key created: {api_key[:8]}...")
        
        # Get security stats
        stats = sec.get_security_stats()
        print(f"Security stats: {stats}")
    
    else:
        print("✗ Authentication failed")

if __name__ == "__main__":
    demo_security_manager()
