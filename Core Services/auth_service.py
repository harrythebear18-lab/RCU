#!/usr/bin/env python3
"""
Authentication Service for Homelab System
Provides centralized authentication and single sign-on
"""

import hashlib
import secrets
import time
import threading
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from event_bus import get_event_bus, EventType
from config_manager import get_config_manager

@dataclass
class User:
    username: str
    email: str
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_attempts: int = 0

@dataclass
class Session:
    session_id: str
    username: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str

@dataclass
class Role:
    name: str
    permissions: List[str]
    description: str

class AuthService:
    """Centralized authentication service"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Session] = {}
        self._roles: Dict[str, Role] = {}
        self._lock = threading.RLock()
        self._logger = self._setup_logger()
        self._config = get_config_manager()
        self._event_bus = get_event_bus()
        
        # Initialize default roles and users
        self._initialize_roles()
        self._initialize_default_users()
        
        # Start session cleanup
        self._cleanup_running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self._cleanup_thread.start()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup authentication service logger"""
        logger = logging.getLogger('AuthService')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _initialize_roles(self):
        """Initialize default roles"""
        self._roles = {
            'admin': Role(
                name='admin',
                permissions=[
                    'system.admin',
                    'system.config',
                    'system.monitor',
                    'user.manage',
                    'security.audit',
                    'resource.all'
                ],
                description='Full system administrator'
            ),
            'operator': Role(
                name='operator',
                permissions=[
                    'system.monitor',
                    'system.config',
                    'resource.manage',
                    'security.view'
                ],
                description='System operator with management rights'
            ),
            'viewer': Role(
                name='viewer',
                permissions=[
                    'system.monitor',
                    'security.view'
                ],
                description='Read-only access to monitoring data'
            ),
            'guest': Role(
                name='guest',
                permissions=[
                    'system.monitor.basic'
                ],
                description='Limited guest access'
            )
        }
        
    def _initialize_default_users(self):
        """Initialize default users"""
        # Create admin user with default password
        self._users['admin'] = User(
            username='admin',
            email='admin@homelab.local',
            role='admin',
            created_at=datetime.now(),
            is_active=True
        )
        
        # Create guest user
        self._users['guest'] = User(
            username='guest',
            email='guest@homelab.local',
            role='guest',
            created_at=datetime.now(),
            is_active=True
        )
        
        # Set default passwords (should be changed on first login)
        self._set_password('admin', 'admin123')
        self._set_password('guest', 'guest')
        
    def _set_password(self, username: str, password: str):
        """Set user password (hashed)"""
        if username in self._users:
            # Generate salt and hash
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            # Store in secure configuration
            self._config.set_secure(f'credentials.{username}.hash', password_hash)
            self._config.set_secure(f'credentials.{username}.salt', salt)
            self._config.set_secure(f'credentials.{username}.changed_at', datetime.now().isoformat())
            
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        
    def _verify_password(self, username: str, password: str) -> bool:
        """Verify user password"""
        try:
            password_hash = self._config.get_secure(f'credentials.{username}.hash')
            salt = self._config.get_secure(f'credentials.{username}.salt')
            
            if not password_hash or not salt:
                return False
                
            expected_hash = self._hash_password(password, salt)
            return secrets.compare_digest(expected_hash, password_hash)
            
        except Exception as e:
            self._logger.error(f"Error verifying password for {username}: {e}")
            return False
            
    def authenticate(self, username: str, password: str, ip_address: str, 
                    user_agent: str) -> Optional[str]:
        """Authenticate user and create session"""
        with self._lock:
            # Check if user exists and is active
            if username not in self._users:
                self._log_security_event('authentication_failed', {
                    'username': username,
                    'reason': 'user_not_found',
                    'ip_address': ip_address
                })
                return None
                
            user = self._users[username]
            
            if not user.is_active:
                self._log_security_event('authentication_failed', {
                    'username': username,
                    'reason': 'user_inactive',
                    'ip_address': ip_address
                })
                return None
                
            # Check failed attempts
            max_attempts = self._config.get('security.max_failed_attempts', 5)
            if user.failed_attempts >= max_attempts:
                self._log_security_event('authentication_failed', {
                    'username': username,
                    'reason': 'too_many_attempts',
                    'failed_attempts': user.failed_attempts,
                    'ip_address': ip_address
                })
                return None
                
            # Verify password
            if not self._verify_password(username, password):
                user.failed_attempts += 1
                self._log_security_event('authentication_failed', {
                    'username': username,
                    'reason': 'invalid_password',
                    'failed_attempts': user.failed_attempts,
                    'ip_address': ip_address
                })
                return None
                
            # Reset failed attempts on successful authentication
            user.failed_attempts = 0
            user.last_login = datetime.now()
            
            # Create session
            session_id = self._generate_session_id()
            session_timeout = self._config.get('security.session_timeout_minutes', 60)
            
            session = Session(
                session_id=session_id,
                username=username,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=session_timeout),
                last_activity=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self._sessions[session_id] = session
            
            # Log successful authentication
            self._log_security_event('authentication_success', {
                'username': username,
                'session_id': session_id,
                'ip_address': ip_address
            })
            
            self._logger.info(f"User {username} authenticated successfully")
            return session_id
            
    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user"""
        with self._lock:
            if session_id not in self._sessions:
                return None
                
            session = self._sessions[session_id]
            
            # Check if session expired
            if datetime.now() > session.expires_at:
                del self._sessions[session_id]
                self._log_security_event('session_expired', {
                    'session_id': session_id,
                    'username': session.username
                })
                return None
                
            # Update last activity
            session.last_activity = datetime.now()
            
            # Extend session timeout
            session_timeout = self._config.get('security.session_timeout_minutes', 60)
            session.expires_at = datetime.now() + timedelta(minutes=session_timeout)
            
            return self._users.get(session.username)
            
    def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        with self._lock:
            if session_id not in self._sessions:
                return False
                
            session = self._sessions[session_id]
            username = session.username
            
            del self._sessions[session_id]
            
            self._log_security_event('user_logout', {
                'username': username,
                'session_id': session_id
            })
            
            self._logger.info(f"User {username} logged out")
            return True
            
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        if not user or user.role not in self._roles:
            return False
            
        role = self._roles[user.role]
        return permission in role.permissions or 'system.admin' in role.permissions
        
    def create_user(self, username: str, email: str, role: str, password: str) -> bool:
        """Create new user"""
        with self._lock:
            if username in self._users:
                return False
                
            if role not in self._roles:
                return False
                
            user = User(
                username=username,
                email=email,
                role=role,
                created_at=datetime.now(),
                is_active=True
            )
            
            self._users[username] = user
            self._set_password(username, password)
            
            self._log_security_event('user_created', {
                'username': username,
                'email': email,
                'role': role
            })
            
            self._logger.info(f"User {username} created with role {role}")
            return True
            
    def update_user(self, username: str, **kwargs) -> bool:
        """Update user information"""
        with self._lock:
            if username not in self._users:
                return False
                
            user = self._users[username]
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                    
            self._log_security_event('user_updated', {
                'username': username,
                'updates': kwargs
            })
            
            return True
            
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        with self._lock:
            if username not in self._users:
                return False
                
            if not self._verify_password(username, old_password):
                return False
                
            self._set_password(username, new_password)
            
            # Invalidate all sessions for this user
            sessions_to_remove = []
            for session_id, session in self._sessions.items():
                if session.username == username:
                    sessions_to_remove.append(session_id)
                    
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
                
            self._log_security_event('password_changed', {
                'username': username
            })
            
            self._logger.info(f"Password changed for user {username}")
            return True
            
    def _generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
        
    def _log_security_event(self, event_type: str, data: Dict[str, Any]):
        """Log security event"""
        try:
            self.event_bus.publish_sync(EventType.SECURITY, 'AuthService', {
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            })
        except Exception as e:
            self._logger.error(f"Failed to log security event: {e}")
        
    def _cleanup_expired_sessions(self):
        """Cleanup expired sessions"""
        while self._cleanup_running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                with self._lock:
                    for session_id, session in self._sessions.items():
                        if current_time > session.expires_at:
                            expired_sessions.append(session_id)
                            
                    for session_id in expired_sessions:
                        session = self._sessions[session_id]
                        del self._sessions[session_id]
                        
                        self._log_security_event('session_expired', {
                            'session_id': session_id,
                            'username': session.username
                        })
                        
                if expired_sessions:
                    self._logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                    
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                self._logger.error(f"Error in session cleanup: {e}")
                time.sleep(60)
                
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information"""
        with self._lock:
            if username not in self._users:
                return None
                
            user = self._users[username]
            return {
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'failed_attempts': user.failed_attempts
            }
            
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        with self._lock:
            sessions = []
            for session in self._sessions.values():
                sessions.append({
                    'session_id': session.session_id,
                    'username': session.username,
                    'created_at': session.created_at.isoformat(),
                    'expires_at': session.expires_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'ip_address': session.ip_address,
                    'user_agent': session.user_agent
                })
            return sessions
            
    def get_roles(self) -> Dict[str, Any]:
        """Get all roles"""
        with self._lock:
            return {name: asdict(role) for name, role in self._roles.items()}
            
    def stop(self):
        """Stop authentication service"""
        self._cleanup_running = False
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)

# Global authentication service instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get global authentication service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

# Convenience functions
def authenticate_user(username: str, password: str, ip_address: str = '127.0.0.1', 
                     user_agent: str = 'Unknown') -> Optional[str]:
    """Authenticate user"""
    service = get_auth_service()
    return service.authenticate(username, password, ip_address, user_agent)

def validate_session(session_id: str) -> Optional[User]:
    """Validate session"""
    service = get_auth_service()
    return service.validate_session(session_id)

def logout_user(session_id: str) -> bool:
    """Logout user"""
    service = get_auth_service()
    return service.logout(session_id)

def check_permission(user: User, permission: str) -> bool:
    """Check user permission"""
    service = get_auth_service()
    return service.has_permission(user, permission)
