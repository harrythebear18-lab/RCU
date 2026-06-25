#!/usr/bin/env python3
"""
Advanced Security System
Enhanced permissions, audit logging, and security features.
"""

import os
import json
import hashlib
import hmac
import secrets
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
import win32security
import win32con
import win32api
import ntsecuritycon
import subprocess
import logging

class AdvancedSecurityManager:
    """Advanced Security Manager"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'security_audit.db')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'security_settings.json')
        self.log_file = os.path.join(os.path.dirname(__file__), 'security_audit.log')
        
        # Security settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Setup logging
        self.setup_logging()
        
        # Security monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Session management
        self.sessions = {}
        self.session_timeout = 3600  # 1 hour
        
        # Permission levels
        self.permission_levels = {
            'guest': 0,
            'user': 1,
            'power_user': 2,
            'administrator': 3,
            'system': 4
        }
        
        # Start monitoring if enabled
        if self.settings.get('audit_logging_enabled', True):
            self.start_monitoring()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load security settings"""
        default_settings = {
            'audit_logging_enabled': True,
            'permission_checking_enabled': True,
            'secure_file_deletion': True,
            'privacy_cleanup_enabled': True,
            'intrusion_detection': True,
            'session_timeout': 3600,
            'max_failed_attempts': 5,
            'lockout_duration': 900,
            'require_admin_for_critical_ops': True,
            'encrypt_sensitive_data': True,
            'audit_retention_days': 90,
            'real_time_monitoring': True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception:
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save security settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def init_database(self):
        """Initialize security database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                action TEXT NOT NULL,
                resource TEXT,
                result TEXT,
                details TEXT,
                severity TEXT DEFAULT 'info',
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                resource TEXT NOT NULL,
                permission_level TEXT NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by TEXT,
                expires_at TIMESTAMP,
                conditions TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                source_ip TEXT,
                user_id TEXT,
                blocked BOOLEAN DEFAULT FALSE,
                details TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                action TEXT,
                ip_address TEXT,
                reason TEXT,
                blocked BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_permissions_user ON permissions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_failed_attempts_timestamp ON failed_attempts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
        
        conn.commit()
        conn.close()
    
    def setup_logging(self):
        """Setup security logging"""
        self.logger = logging.getLogger('AdvancedSecurity')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def log_audit_event(self, user_id: str, action: str, resource: str = None, 
                        result: str = 'success', details: str = None, 
                        severity: str = 'info', ip_address: str = None, 
                        user_agent: str = None, session_id: str = None):
        """Log audit event"""
        if not self.settings.get('audit_logging_enabled', True):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_log 
                (user_id, action, resource, result, details, severity, ip_address, user_agent, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, action, resource, result, details, severity, ip_address, user_agent, session_id))
            
            conn.commit()
            conn.close()
            
            # Also log to file
            self.logger.info(f"AUDIT: {user_id} - {action} - {resource} - {result}")
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
    
    def check_permission(self, user_id: str, resource: str, action: str = 'access', 
                         context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Check user permission for resource"""
        if not self.settings.get('permission_checking_enabled', True):
            return True, "Permission checking disabled"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user permissions
            cursor.execute('''
                SELECT permission_level, expires_at, conditions 
                FROM permissions 
                WHERE user_id = ? AND resource = ? AND 
                      (expires_at IS NULL OR expires_at > datetime('now'))
            ''', (user_id, resource))
            
            permissions = cursor.fetchall()
            conn.close()
            
            if not permissions:
                self.log_audit_event(user_id, f"permission_denied", resource, 
                                   "failed", "No permission found", "warning")
                return False, "Permission denied"
            
            # Check permission level
            for perm_level, expires_at, conditions in permissions:
                if self.permission_levels.get(perm_level, 0) >= self.permission_levels.get(action, 0):
                    # Check conditions if any
                    if conditions:
                        conditions_dict = json.loads(conditions) if isinstance(conditions, str) else conditions
                        if self._check_conditions(conditions_dict, context or {}):
                            self.log_audit_event(user_id, f"permission_granted", resource, 
                                               "success", f"Permission granted: {perm_level}", "info")
                            return True, "Permission granted"
                    else:
                        self.log_audit_event(user_id, f"permission_granted", resource, 
                                           "success", f"Permission granted: {perm_level}", "info")
                        return True, "Permission granted"
            
            self.log_audit_event(user_id, f"permission_denied", resource, 
                               "failed", "Insufficient permission level", "warning")
            return False, "Insufficient permission"
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False, "Permission check failed"
    
    def _check_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check permission conditions"""
        for key, value in conditions.items():
            if key not in context or context[key] != value:
                return False
        return True
    
    def grant_permission(self, user_id: str, resource: str, permission_level: str, 
                        granted_by: str = None, expires_at: datetime = None, 
                        conditions: Dict[str, Any] = None):
        """Grant permission to user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_str = expires_at.isoformat() if expires_at else None
            conditions_str = json.dumps(conditions) if conditions else None
            
            cursor.execute('''
                INSERT INTO permissions 
                (user_id, resource, permission_level, granted_by, expires_at, conditions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, resource, permission_level, granted_by, expires_str, conditions_str))
            
            conn.commit()
            conn.close()
            
            self.log_audit_event(granted_by or 'system', f"permission_granted", 
                               f"{user_id}:{resource}", "success", 
                               f"Granted {permission_level} permission", "info")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to grant permission: {e}")
            return False
    
    def revoke_permission(self, user_id: str, resource: str, revoked_by: str = None):
        """Revoke permission from user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM permissions WHERE user_id = ? AND resource = ?', 
                         (user_id, resource))
            
            conn.commit()
            conn.close()
            
            self.log_audit_event(revoked_by or 'system', f"permission_revoked", 
                               f"{user_id}:{resource}", "success", 
                               "Permission revoked", "info")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke permission: {e}")
            return False
    
    def secure_delete_file(self, file_path: str, passes: int = 3) -> bool:
        """Securely delete file"""
        if not self.settings.get('secure_file_deletion', True):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            
            # Overwrite file multiple times
            with open(file_path, 'wb') as f:
                for pass_num in range(passes):
                    # Generate random data
                    random_data = os.urandom(file_size)
                    f.write(random_data)
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove file
            os.remove(file_path)
            
            self.log_audit_event('system', f"secure_delete", file_path, "success", 
                               f"File securely deleted with {passes} passes", "info")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Secure file deletion failed: {e}")
            return False
    
    def privacy_cleanup(self) -> Dict[str, Any]:
        """Perform privacy cleanup"""
        if not self.settings.get('privacy_cleanup_enabled', True):
            return {"status": "disabled", "cleaned_items": 0}
        
        cleaned_items = []
        
        try:
            # Clean temporary files
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
                os.path.join(os.environ.get('APPDATA', ''), 'Temp')
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                if self.secure_delete_file(item_path):
                                    cleaned_items.append(item_path)
                        except Exception:
                            continue
            
            # Clean browser cache (simplified)
            browser_cache_dirs = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
            ]
            
            for cache_dir in browser_cache_dirs:
                if os.path.exists(cache_dir):
                    for item in os.listdir(cache_dir):
                        item_path = os.path.join(cache_dir, item)
                        try:
                            if os.path.isfile(item_path):
                                if self.secure_delete_file(item_path):
                                    cleaned_items.append(item_path)
                        except Exception:
                            continue
            
            # Clean recent documents
            recent_docs = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Recent')
            if os.path.exists(recent_docs):
                for item in os.listdir(recent_docs):
                    if item.endswith('.lnk'):
                        item_path = os.path.join(recent_docs, item)
                        try:
                            if self.secure_delete_file(item_path):
                                cleaned_items.append(item_path)
                        except Exception:
                            continue
            
            self.log_audit_event('system', 'privacy_cleanup', 'system', 'success', 
                               f"Cleaned {len(cleaned_items)} items", "info")
            
            return {
                "status": "success",
                "cleaned_items": len(cleaned_items),
                "items": cleaned_items
            }
            
        except Exception as e:
            self.logger.error(f"Privacy cleanup failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "cleaned_items": len(cleaned_items)
            }
    
    def detect_intrusion(self, event_type: str, severity: str, description: str, 
                        source_ip: str = None, user_id: str = None, 
                        details: Dict[str, Any] = None) -> bool:
        """Detect and handle potential intrusion"""
        if not self.settings.get('intrusion_detection', True):
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for suspicious patterns
            blocked = False
            
            # Check for multiple failed attempts
            if event_type == 'failed_login':
                cursor.execute('''
                    SELECT COUNT(*) FROM failed_attempts 
                    WHERE timestamp > datetime('now', '-1 hour') 
                    AND ip_address = ?
                ''', (source_ip or 'unknown',))
                
                failed_count = cursor.fetchone()[0]
                max_attempts = self.settings.get('max_failed_attempts', 5)
                
                if failed_count >= max_attempts:
                    blocked = True
                    self._block_ip(source_ip, f"Too many failed attempts: {failed_count}")
            
            # Check for unusual access patterns
            if event_type == 'unusual_access':
                blocked = True
                self._block_ip(source_ip, "Unusual access pattern detected")
            
            # Log security event
            cursor.execute('''
                INSERT INTO security_events 
                (event_type, severity, description, source_ip, user_id, blocked, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event_type, severity, description, source_ip, user_id, blocked, 
                  json.dumps(details) if details else None))
            
            conn.commit()
            conn.close()
            
            if blocked:
                self.log_audit_event('system', 'intrusion_blocked', source_ip, 
                                   "success", f"Blocked due to: {description}", "warning")
            
            return blocked
            
        except Exception as e:
            self.logger.error(f"Intrusion detection failed: {e}")
            return False
    
    def _block_ip(self, ip_address: str, reason: str):
        """Block IP address (simplified implementation)"""
        # This is a simplified implementation
        # In a real system, you would integrate with firewall APIs
        self.log_audit_event('system', 'ip_blocked', ip_address, "success", 
                           f"IP blocked: {reason}", "warning")
    
    def create_session(self, user_id: str, ip_address: str = None, 
                      user_agent: str = None) -> str:
        """Create user session"""
        session_id = secrets.token_urlsafe(32)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions 
                (id, user_id, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
            # Store in memory
            self.sessions[session_id] = {
                'user_id': user_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'ip_address': ip_address
            }
            
            self.log_audit_event(user_id, 'session_created', session_id, "success", 
                               f"Session created from {ip_address}", "info")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return None
    
    def validate_session(self, session_id: str) -> bool:
        """Validate session"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Check session timeout
        if datetime.now() - session['last_activity'] > timedelta(seconds=self.session_timeout):
            self.destroy_session(session_id)
            return False
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        return True
    
    def destroy_session(self, session_id: str):
        """Destroy session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            
            conn.commit()
            conn.close()
            
            if session_id in self.sessions:
                user_id = self.sessions[session_id]['user_id']
                del self.sessions[session_id]
                
                self.log_audit_event(user_id, 'session_destroyed', session_id, "success", 
                                   "Session destroyed", "info")
            
        except Exception as e:
            self.logger.error(f"Failed to destroy session: {e}")
    
    def start_monitoring(self):
        """Start security monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Security monitoring started")
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Security monitoring stopped")
    
    def _monitoring_loop(self):
        """Security monitoring loop"""
        while self.monitoring_active:
            try:
                # Clean expired sessions
                self._cleanup_expired_sessions()
                
                # Clean old audit logs
                self._cleanup_old_logs()
                
                # Check for suspicious activities
                self._check_suspicious_activities()
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Security monitoring error: {e}")
                time.sleep(60)
    
    def _cleanup_expired_sessions(self):
        """Clean expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['last_activity'] > timedelta(seconds=self.session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.destroy_session(session_id)
    
    def _cleanup_old_logs(self):
        """Clean old audit logs"""
        retention_days = self.settings.get('audit_retention_days', 90)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clean old audit logs
            cursor.execute('DELETE FROM audit_log WHERE timestamp < ?', (cutoff_date,))
            
            # Clean old security events
            cursor.execute('DELETE FROM security_events WHERE timestamp < ?', (cutoff_date,))
            
            # Clean old failed attempts
            cursor.execute('DELETE FROM failed_attempts WHERE timestamp < ?', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")
    
    def _check_suspicious_activities(self):
        """Check for suspicious activities"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for multiple failed logins from same IP
            cursor.execute('''
                SELECT ip_address, COUNT(*) as count 
                FROM failed_attempts 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY ip_address 
                HAVING count > ?
            ''', (self.settings.get('max_failed_attempts', 5),))
            
            suspicious_ips = cursor.fetchall()
            
            for ip_address, count in suspicious_ips:
                self.detect_intrusion('multiple_failed_attempts', 'high', 
                                  f"Multiple failed attempts from {ip_address}: {count}", 
                                  ip_address)
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to check suspicious activities: {e}")
    
    def get_security_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate security report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get audit statistics
            cursor.execute('''
                SELECT action, COUNT(*) as count 
                FROM audit_log 
                WHERE timestamp > ?
                GROUP BY action
            ''', (cutoff_date,))
            
            audit_stats = dict(cursor.fetchall())
            
            # Get security events
            cursor.execute('''
                SELECT event_type, severity, COUNT(*) as count 
                FROM security_events 
                WHERE timestamp > ?
                GROUP BY event_type, severity
            ''', (cutoff_date,))
            
            security_events = cursor.fetchall()
            
            # Get failed attempts
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM failed_attempts 
                WHERE timestamp > ?
            ''', (cutoff_date,))
            
            failed_attempts = cursor.fetchone()[0]
            
            # Get active sessions
            cursor.execute('SELECT COUNT(*) FROM sessions WHERE active = 1')
            active_sessions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'period_days': days,
                'audit_events': audit_stats,
                'security_events': security_events,
                'failed_attempts': failed_attempts,
                'active_sessions': active_sessions,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate security report: {e}")
            return {'error': str(e)}
    
    def create_security_panel(self, parent):
        """Create security settings panel"""
        panel = tk.Frame(parent)
        
        # Title
        title = tk.Label(panel, text="Advanced Security Settings",
                        font=('Segoe UI', 12, 'bold'))
        title.pack(pady=10)
        
        # Settings
        settings_frame = tk.Frame(panel)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Audit logging
        audit_var = tk.BooleanVar(value=self.settings.get('audit_logging_enabled', True))
        audit_cb = tk.Checkbutton(settings_frame, text="Enable Audit Logging",
                                 variable=audit_var,
                                 command=lambda: self.save_settings({'audit_logging_enabled': audit_var.get()}))
        audit_cb.pack(anchor=tk.W, pady=5)
        
        # Permission checking
        perm_var = tk.BooleanVar(value=self.settings.get('permission_checking_enabled', True))
        perm_cb = tk.Checkbutton(settings_frame, text="Enable Permission Checking",
                              variable=perm_var,
                              command=lambda: self.save_settings({'permission_checking_enabled': perm_var.get()}))
        perm_cb.pack(anchor=tk.W, pady=5)
        
        # Secure deletion
        secure_var = tk.BooleanVar(value=self.settings.get('secure_file_deletion', True))
        secure_cb = tk.Checkbutton(settings_frame, text="Enable Secure File Deletion",
                                variable=secure_var,
                                command=lambda: self.save_settings({'secure_file_deletion': secure_var.get()}))
        secure_cb.pack(anchor=tk.W, pady=5)
        
        # Privacy cleanup
        privacy_var = tk.BooleanVar(value=self.settings.get('privacy_cleanup_enabled', True))
        privacy_cb = tk.Checkbutton(settings_frame, text="Enable Privacy Cleanup",
                                 variable=privacy_var,
                                 command=lambda: self.save_settings({'privacy_cleanup_enabled': privacy_var.get()}))
        privacy_cb.pack(anchor=tk.W, pady=5)
        
        # Intrusion detection
        intrusion_var = tk.BooleanVar(value=self.settings.get('intrusion_detection', True))
        intrusion_cb = tk.Checkbutton(settings_frame, text="Enable Intrusion Detection",
                                   variable=intrusion_var,
                                   command=lambda: self.save_settings({'intrusion_detection': intrusion_var.get()}))
        intrusion_cb.pack(anchor=tk.W, pady=5)
        
        # Action buttons
        button_frame = tk.Frame(panel)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        privacy_btn = tk.Button(button_frame, text="Run Privacy Cleanup",
                             command=self._run_privacy_cleanup)
        privacy_btn.pack(side=tk.LEFT, padx=5)
        
        report_btn = tk.Button(button_frame, text="Security Report",
                             command=self._show_security_report)
        report_btn.pack(side=tk.LEFT, padx=5)
        
        return panel
    
    def _run_privacy_cleanup(self):
        """Run privacy cleanup"""
        result = self.privacy_cleanup()
        
        if result['status'] == 'success':
            messagebox.showinfo("Privacy Cleanup", 
                              f"Privacy cleanup completed successfully.\n"
                              f"Cleaned {result['cleaned_items']} items.")
        else:
            messagebox.showerror("Privacy Cleanup Failed", 
                               f"Privacy cleanup failed: {result.get('error', 'Unknown error')}")
    
    def _show_security_report(self):
        """Show security report"""
        report = self.get_security_report()
        
        if 'error' in report:
            messagebox.showerror("Security Report Error", f"Failed to generate report: {report['error']}")
            return
        
        # Create report dialog
        report_dialog = tk.Toplevel()
        report_dialog.title("Security Report")
        report_dialog.geometry("600x500")
        
        # Display report
        report_text = tk.Text(report_dialog, wrap=tk.WORD)
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        report_text.insert(tk.END, f"Security Report - Last {report['period_days']} Days\n")
        report_text.insert(tk.END, f"Generated: {report['generated_at']}\n\n")
        
        report_text.insert(tk.END, f"Audit Events:\n")
        for action, count in report['audit_events'].items():
            report_text.insert(tk.END, f"  {action}: {count}\n")
        
        report_text.insert(tk.END, f"\nFailed Attempts: {report['failed_attempts']}\n")
        report_text.insert(tk.END, f"Active Sessions: {report['active_sessions']}\n")
        
        report_text.insert(tk.END, f"\nSecurity Events:\n")
        for event_type, severity, count in report['security_events']:
            report_text.insert(tk.END, f"  {event_type} ({severity}): {count}\n")
        
        report_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(report_dialog, text="Close", command=report_dialog.destroy)
        close_btn.pack(pady=10)

# Global security manager instance
security_manager = AdvancedSecurityManager()

# Convenience functions
def log_audit(user_id: str, action: str, resource: str = None, **kwargs):
    """Log audit event"""
    security_manager.log_audit_event(user_id, action, resource, **kwargs)

def check_permission(user_id: str, resource: str, action: str = 'access', **kwargs):
    """Check permission"""
    return security_manager.check_permission(user_id, resource, action, **kwargs)

def secure_delete(file_path: str, passes: int = 3):
    """Securely delete file"""
    return security_manager.secure_delete_file(file_path, passes)

def privacy_cleanup():
    """Run privacy cleanup"""
    return security_manager.privacy_cleanup()

if __name__ == '__main__':
    # Test advanced security
    print("Testing Advanced Security System")
    print(f"Audit logging enabled: {security_manager.settings.get('audit_logging_enabled')}")
    print(f"Permission checking enabled: {security_manager.settings.get('permission_checking_enabled')}")
    print(f"Secure deletion enabled: {security_manager.settings.get('secure_file_deletion')}")
    print(f"Privacy cleanup enabled: {security_manager.settings.get('privacy_cleanup_enabled')}")
    print(f"Intrusion detection enabled: {security_manager.settings.get('intrusion_detection')}")
    
    # Test audit logging
    log_audit('test_user', 'test_action', 'test_resource')
    
    # Test permission checking
    result, message = check_permission('test_user', 'test_resource')
    print(f"Permission check result: {result} - {message}")
    
    # Test security report
    report = security_manager.get_security_report()
    print(f"Security report: {report.get('period_days', 'N/A')} days")
