#!/usr/bin/env python3
"""
Advanced Security Features for Homelab Portal
Comprehensive security system with encryption, authentication, and monitoring
"""

import hashlib
import secrets
import time
import logging
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import ipaddress
import re
from enum import Enum

class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatLevel(Enum):
    """Threat level enumeration"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    timestamp: datetime
    event_type: str
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    policy_id: str
    name: str
    description: str
    security_level: SecurityLevel
    rules: List[Dict[str, Any]]
    enabled: bool = True
    created_at: datetime = None

class AdvancedSecurity:
    """Advanced security system for Homelab Portal"""
    
    def __init__(self, db_path: str = "security.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("AdvancedSecurity")
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.running = False
        self.monitoring_thread = None
        self.blocked_ips = set()
        self.failed_attempts = {}
        self.security_policies = {}
        
        # Initialize database
        self._init_database()
        
        # Load security policies
        self._load_default_policies()
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key"""
        password = b"homelab_portal_security_key_2026"
        salt = b"homelab_salt_2026"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _init_database(self):
        """Initialize security database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    event_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    user_id TEXT,
                    description TEXT,
                    details TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME
                )
            ''')
            
            # Create blocked IPs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocked_ips (
                    ip_address TEXT PRIMARY KEY,
                    blocked_at DATETIME NOT NULL,
                    blocked_until DATETIME,
                    reason TEXT,
                    permanent BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create failed attempts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS failed_attempts (
                    attempt_id TEXT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    ip_address TEXT NOT NULL,
                    user_id TEXT,
                    attempt_type TEXT NOT NULL,
                    details TEXT
                )
            ''')
            
            # Create security policies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_policies (
                    policy_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    security_level TEXT NOT NULL,
                    rules TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_ip ON security_events(source_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_threat ON security_events(threat_level)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Security database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security database: {e}")
    
    def _load_default_policies(self):
        """Load default security policies"""
        try:
            # Network security policy
            self.security_policies['network'] = SecurityPolicy(
                policy_id='network',
                name='Network Security',
                description='Monitor and protect against network threats',
                security_level=SecurityLevel.HIGH,
                rules=[
                    {
                        'type': 'rate_limit',
                        'max_requests_per_minute': 100,
                        'block_duration_minutes': 5
                    },
                    {
                        'type': 'ip_whitelist',
                        'allowed_networks': ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12'],
                        'block_unknown': False
                    },
                    {
                        'type': 'port_scan_detection',
                        'threshold': 10,
                        'time_window_minutes': 5,
                        'block_duration_hours': 1
                    }
                ]
            )
            
            # Authentication security policy
            self.security_policies['auth'] = SecurityPolicy(
                policy_id='auth',
                name='Authentication Security',
                description='Protect against unauthorized access',
                security_level=SecurityLevel.CRITICAL,
                rules=[
                    {
                        'type': 'failed_login_threshold',
                        'max_attempts': 5,
                        'lockout_duration_minutes': 15
                    },
                    {
                        'type': 'password_policy',
                        'min_length': 8,
                        'require_special_chars': True,
                        'require_numbers': True,
                        'password_history': 5
                    },
                    {
                        'type': 'session_management',
                        'max_session_duration_hours': 8,
                        'idle_timeout_minutes': 30
                    }
                ]
            )
            
            # Data security policy
            self.security_policies['data'] = SecurityPolicy(
                policy_id='data',
                name='Data Security',
                description='Protect sensitive data and ensure privacy',
                security_level=SecurityLevel.HIGH,
                rules=[
                    {
                        'type': 'encryption_required',
                        'sensitive_fields': ['password', 'api_key', 'private_key'],
                        'encryption_algorithm': 'AES-256'
                    },
                    {
                        'type': 'data_retention',
                        'log_retention_days': 90,
                        'session_data_retention_hours': 24
                    },
                    {
                        'type': 'access_control',
                        'principle_of_least_privilege': True,
                        'audit_trail': True
                    }
                ]
            )
            
            self.logger.info("Default security policies loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load default policies: {e}")
    
    def start(self):
        """Start security monitoring"""
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Advanced security system started")
    
    def stop(self):
        """Stop security monitoring"""
        self.running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Advanced security system stopped")
    
    def _monitoring_loop(self):
        """Main security monitoring loop"""
        while self.running:
            try:
                # Check blocked IPs
                self._check_blocked_ips()
                
                # Clean up old failed attempts
                self._cleanup_failed_attempts()
                
                # Analyze security events
                self._analyze_security_events()
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Security monitoring loop error: {e}")
                time.sleep(60)
    
    def _check_blocked_ips(self):
        """Check and update blocked IPs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get expired blocks
            cursor.execute('''
                SELECT ip_address FROM blocked_ips
                WHERE permanent = FALSE AND blocked_until < ?
            ''', (datetime.now(),))
            
            expired_ips = [row[0] for row in cursor.fetchall()]
            
            # Remove expired blocks
            for ip in expired_ips:
                cursor.execute('DELETE FROM blocked_ips WHERE ip_address = ?', (ip,))
                self.blocked_ips.discard(ip)
                self.logger.info(f"Unblocked IP: {ip}")
            
            # Update blocked_ips set
            cursor.execute('SELECT ip_address FROM blocked_ips')
            self.blocked_ips = {row[0] for row in cursor.fetchall()}
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to check blocked IPs: {e}")
    
    def _cleanup_failed_attempts(self):
        """Clean up old failed attempts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete attempts older than 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            cursor.execute('DELETE FROM failed_attempts WHERE timestamp < ?', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup failed attempts: {e}")
    
    def _analyze_security_events(self):
        """Analyze security events for patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent events
            cursor.execute('''
                SELECT * FROM security_events
                WHERE resolved = FALSE AND threat_level IN ('HIGH', 'CRITICAL')
                ORDER BY timestamp DESC
                LIMIT 100
            ''')
            
            events = cursor.fetchall()
            conn.close()
            
            # Analyze for patterns
            self._detect_attack_patterns(events)
            
        except Exception as e:
            self.logger.error(f"Failed to analyze security events: {e}")
    
    def _detect_attack_patterns(self, events):
        """Detect attack patterns from events"""
        try:
            # Group events by IP
            ip_events = {}
            for event in events:
                ip = event[4]  # source_ip
                if ip not in ip_events:
                    ip_events[ip] = []
                ip_events[ip].append(event)
            
            # Detect patterns
            for ip, ip_event_list in ip_events.items():
                # Check for repeated failed attempts
                failed_attempts = len([e for e in ip_event_list if 'failed' in e[2]])
                
                if failed_attempts >= 10:
                    self._block_ip_temporarily(ip, 60, "High number of failed attempts")
                
                # Check for port scanning
                port_scan_events = [e for e in ip_event_list if 'port_scan' in e[2]]
                if len(port_scan_events) >= 5:
                    self._block_ip_temporarily(ip, 120, "Port scanning detected")
                
                # Check for brute force attacks
                brute_force_events = [e for e in ip_event_list if 'brute_force' in e[2]]
                if len(brute_force_events) >= 5:
                    self._block_ip_temporarily(ip, 180, "Brute force attack detected")
            
        except Exception as e:
            self.logger.error(f"Failed to detect attack patterns: {e}")
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def _block_ip_temporarily(self, ip_address: str, duration_minutes: int, reason: str):
        """Block IP temporarily"""
        try:
            blocked_until = datetime.now() + timedelta(minutes=duration_minutes)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO blocked_ips
                (ip_address, blocked_at, blocked_until, reason, permanent)
                VALUES (?, ?, ?, ?, FALSE)
            ''', (ip_address, datetime.now(), blocked_until, reason))
            
            conn.commit()
            conn.close()
            
            self.blocked_ips.add(ip_address)
            
            # Log security event
            self.log_security_event(
                event_type='ip_blocked',
                threat_level=ThreatLevel.HIGH,
                source_ip=ip_address,
                description=f"IP blocked temporarily: {reason}",
                details={
                    'duration_minutes': duration_minutes,
                    'blocked_until': blocked_until.isoformat(),
                    'reason': reason
                }
            )
            
            self.logger.warning(f"IP blocked temporarily: {ip_address} for {duration_minutes} minutes")
            
        except Exception as e:
            self.logger.error(f"Failed to block IP {ip_address}: {e}")
    
    def block_ip_permanently(self, ip_address: str, reason: str):
        """Block IP permanently"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO blocked_ips
                (ip_address, blocked_at, blocked_until, reason, permanent)
                VALUES (?, ?, ?, ?, TRUE)
            ''', (ip_address, datetime.now(), None, reason))
            
            conn.commit()
            conn.close()
            
            self.blocked_ips.add(ip_address)
            
            # Log security event
            self.log_security_event(
                event_type='ip_blocked_permanent',
                threat_level=ThreatLevel.CRITICAL,
                source_ip=ip_address,
                description=f"IP blocked permanently: {reason}",
                details={
                    'reason': reason,
                    'permanent': True
                }
            )
            
            self.logger.warning(f"IP blocked permanently: {ip_address}")
            
        except Exception as e:
            self.logger.error(f"Failed to block IP {ip_address} permanently: {e}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM blocked_ips WHERE ip_address = ?', (ip_address,))
            
            conn.commit()
            conn.close()
            
            self.blocked_ips.discard(ip_address)
            
            # Log security event
            self.log_security_event(
                event_type='ip_unblocked',
                threat_level=ThreatLevel.INFO,
                source_ip=ip_address,
                description="IP unblocked",
                details={}
            )
            
            self.logger.info(f"IP unblocked: {ip_address}")
            
        except Exception as e:
            self.logger.error(f"Failed to unblock IP {ip_address}: {e}")
    
    def log_failed_attempt(self, ip_address: str, user_id: str = None, attempt_type: str = 'unknown', details: Dict[str, Any] = None):
        """Log failed authentication attempt"""
        try:
            attempt_id = self._generate_event_id()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO failed_attempts
                (attempt_id, timestamp, ip_address, user_id, attempt_type, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (attempt_id, datetime.now(), ip_address, user_id, attempt_type, json.dumps(details or {})))
            
            conn.commit()
            conn.close()
            
            # Check for repeated failures
            self._check_repeated_failures(ip_address, user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to log failed attempt: {e}")
    
    def _check_repeated_failures(self, ip_address: str, user_id: str = None):
        """Check for repeated failed attempts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count recent failures
            cutoff_time = datetime.now() - timedelta(minutes=15)
            cursor.execute('''
                SELECT COUNT(*) FROM failed_attempts
                WHERE ip_address = ? AND timestamp > ?
            ''', (ip_address, cutoff_time))
            
            count = cursor.fetchone()[0]
            
            # Block if threshold exceeded
            if count >= 10:
                self._block_ip_temporarily(ip_address, 30, "Too many failed attempts")
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to check repeated failures: {e}")
    
    def log_security_event(self, event_type: str, threat_level: ThreatLevel, source_ip: str, 
                          user_id: str = None, description: str = "", details: Dict[str, Any] = None):
        """Log security event"""
        try:
            event_id = self._generate_event_id()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events
                (event_id, timestamp, event_type, threat_level, source_ip, user_id, description, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, datetime.now(), event_type, threat_level.value, source_ip, user_id, description, json.dumps(details or {})))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Security event logged: {event_type} from {source_ip}")
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            return encrypted_data
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password against security policy"""
        try:
            auth_policy = self.security_policies.get('auth')
            if not auth_policy:
                return True, []
            
            rules = auth_policy.rules
            errors = []
            
            # Check length
            length_rule = next((r for r in rules if r['type'] == 'password_policy'), None)
            if length_rule:
                if len(password) < length_rule.get('min_length', 8):
                    errors.append(f"Password must be at least {length_rule.get('min_length', 8)} characters")
                
                if length_rule.get('require_special_chars') and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                    errors.append("Password must contain at least one special character")
                
                if length_rule.get('require_numbers') and not re.search(r'\d', password):
                    errors.append("Password must contain at least one number")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            self.logger.error(f"Failed to validate password: {e}")
            return False, ["Password validation failed"]
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Validate IP address format and range"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check if IP is in allowed networks
            network_policy = self.security_policies.get('network')
            if network_policy:
                rules = network_policy.rules
                ip_rule = next((r for r in rules if r['type'] == 'ip_whitelist'), None)
                
                if ip_rule:
                    allowed_networks = ip_rule.get('allowed_networks', [])
                    for network_str in allowed_networks:
                        try:
                            network = ipaddress.ip_network(network_str)
                            if ip in network:
                                return True
                        except:
                            continue
                    
                    if ip_rule.get('block_unknown', True):
                        return False
            
            return True
            
        except ValueError:
            return False
        except Exception as e:
            self.logger.error(f"Failed to validate IP address: {e}")
            return False
    
    def get_security_events(self, threat_level: ThreatLevel = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events with optional filtering"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM security_events"
            params = []
            
            if threat_level:
                query += " WHERE threat_level = ?"
                params.append(threat_level.value)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append({
                    'event_id': row[0],
                    'timestamp': row[1],
                    'event_type': row[2],
                    'threat_level': row[3],
                    'source_ip': row[4],
                    'user_id': row[5],
                    'description': row[6],
                    'details': json.loads(row[7]) if row[7] else {},
                    'resolved': row[8],
                    'resolved_at': row[9]
                })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get security events: {e}")
            return []
    
    def get_blocked_ips(self) -> List[Dict[str, Any]]:
        """Get list of blocked IPs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ip_address, blocked_at, blocked_until, reason, permanent
                FROM blocked_ips
                ORDER BY blocked_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            blocked_ips = []
            for row in rows:
                blocked_ips.append({
                    'ip_address': row[0],
                    'blocked_at': row[1],
                    'blocked_until': row[2],
                    'reason': row[3],
                    'permanent': row[4]
                })
            
            return blocked_ips
            
        except Exception as e:
            self.logger.error(f"Failed to get blocked IPs: {e}")
            return []
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get event counts by threat level
            cursor.execute('''
                SELECT threat_level, COUNT(*) FROM security_events
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY threat_level
            ''')
            
            threat_counts = dict(cursor.fetchall())
            
            # Get blocked IP count
            cursor.execute('SELECT COUNT(*) FROM blocked_ips')
            blocked_count = cursor.fetchone()[0]
            
            # Get failed attempts count
            cursor.execute('''
                SELECT COUNT(*) FROM failed_attempts
                WHERE timestamp > datetime('now', '-24 hours')
            ''')
            
            failed_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'threat_level_counts': threat_counts,
                'blocked_ips_count': blocked_count,
                'failed_attempts_24h': failed_count,
                'security_policies_count': len(self.security_policies),
                'monitoring_active': self.running
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get security summary: {e}")
            return {}
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(int(time.time()))
        raw = f"event:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

# Global security instance
_advanced_security = None

def get_advanced_security(db_path: str = "security.db") -> AdvancedSecurity:
    """Get global advanced security instance"""
    global _advanced_security
    if _advanced_security is None:
        _advanced_security = AdvancedSecurity(db_path)
    return _advanced_security

if __name__ == "__main__":
    # Test advanced security
    security = get_advanced_security()
    print("Advanced Security initialized successfully")
    print(f"Database: {security.db_path}")
    print(f"Security policies loaded: {len(security.security_policies)}")
    print("Advanced Security is ready for use")
