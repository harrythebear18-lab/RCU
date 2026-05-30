#!/usr/bin/env python3
"""
Database Schema Manager
Creates and manages the complete database schema for the system.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DatabaseSchema:
    """Database schema manager"""
    
    def __init__(self, db_path="system_monitoring.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the complete database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create all tables
        self.create_user_preferences_table(cursor)
        self.create_historical_performance_table(cursor)
        self.create_alert_configurations_table(cursor)
        self.create_optimization_profiles_table(cursor)
        self.create_system_events_log_table(cursor)
        self.create_automated_responses_table(cursor)
        self.create_backup_registry_table(cursor)
        self.create_email_notifications_table(cursor)
        self.create_api_usage_table(cursor)
        self.create_performance_metrics_table(cursor)
        
        # Create indexes for performance
        self.create_indexes(cursor)
        
        # Create triggers for data integrity
        self.create_triggers(cursor)
        
        conn.commit()
        conn.close()
    
    def create_user_preferences_table(self, cursor):
        """Create user preferences table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                value_type TEXT DEFAULT 'string',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        ''')
        
        # Insert default preferences
        default_preferences = [
            ('general', 'theme', 'dark', 'string', 'UI theme (dark/light/auto)'),
            ('general', 'language', 'en', 'string', 'Interface language'),
            ('general', 'auto_start', 'false', 'boolean', 'Auto-start with system'),
            ('monitoring', 'update_interval', '2000', 'integer', 'Update interval in milliseconds'),
            ('monitoring', 'history_retention', '7', 'integer', 'Days to keep history'),
            ('monitoring', 'enable_gpu_monitoring', 'true', 'boolean', 'Enable GPU monitoring'),
            ('alerts', 'enable_alerts', 'true', 'boolean', 'Enable alert notifications'),
            ('alerts', 'cpu_warning', '80', 'integer', 'CPU warning threshold (%)'),
            ('alerts', 'cpu_critical', '95', 'integer', 'CPU critical threshold (%)'),
            ('alerts', 'memory_warning', '85', 'integer', 'Memory warning threshold (%)'),
            ('alerts', 'memory_critical', '95', 'integer', 'Memory critical threshold (%)'),
            ('alerts', 'gpu_warning', '85', 'integer', 'GPU warning threshold (%)'),
            ('alerts', 'gpu_critical', '95', 'integer', 'GPU critical threshold (%)'),
            ('alerts', 'temp_warning', '75', 'integer', 'Temperature warning threshold (°C)'),
            ('alerts', 'temp_critical', '85', 'integer', 'Temperature critical threshold (°C)'),
            ('notifications', 'email_enabled', 'false', 'boolean', 'Enable email notifications'),
            ('notifications', 'email_address', '', 'string', 'Email address for notifications'),
            ('notifications', 'system_health_notifications', 'false', 'boolean', 'System health email notifications'),
            ('notifications', 'daily_reports', 'false', 'boolean', 'Daily report emails'),
            ('notifications', 'weekly_reports', 'true', 'boolean', 'Weekly report emails'),
            ('optimization', 'auto_optimize', 'false', 'boolean', 'Enable automatic optimization'),
            ('optimization', 'optimization_interval', '300', 'integer', 'Auto-optimization interval (seconds)'),
            ('optimization', 'profile', 'balanced', 'string', 'Default optimization profile'),
            ('backup', 'auto_backup', 'true', 'boolean', 'Enable automatic backups'),
            ('backup', 'backup_interval', 'daily', 'string', 'Backup interval (daily/weekly/monthly)'),
            ('backup', 'max_backups', '30', 'integer', 'Maximum number of backups to keep'),
            ('backup', 'compress_backups', 'true', 'boolean', 'Compress backup files'),
            ('ui', 'window_geometry', '', 'string', 'Window geometry and position'),
            ('ui', 'graph_history_points', '100', 'integer', 'Number of points in graphs'),
            ('ui', 'show_tooltips', 'true', 'boolean', 'Show tooltips in UI'),
            ('api', 'enable_api', 'true', 'boolean', 'Enable REST API'),
            ('api', 'api_port', '5000', 'integer', 'API server port'),
            ('api', 'require_api_key', 'true', 'boolean', 'Require API key for access'),
            ('advanced', 'debug_mode', 'false', 'boolean', 'Enable debug mode'),
            ('advanced', 'log_level', 'INFO', 'string', 'Logging level (DEBUG/INFO/WARNING/ERROR)'),
            ('advanced', 'performance_profiling', 'false', 'boolean', 'Enable performance profiling')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO user_preferences 
            (category, key, value, value_type, description) 
            VALUES (?, ?, ?, ?, ?)
        ''', default_preferences)
    
    def create_historical_performance_table(self, cursor):
        """Create historical performance data table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cpu_usage REAL,
                cpu_freq REAL,
                cpu_temp REAL,
                ram_usage REAL,
                ram_used INTEGER,
                ram_total INTEGER,
                gpu_usage REAL,
                gpu_memory_used INTEGER,
                gpu_memory_total INTEGER,
                gpu_temp REAL,
                network_sent INTEGER,
                network_recv INTEGER,
                disk_read INTEGER,
                disk_write INTEGER,
                disk_queue REAL,
                health_score REAL,
                optimization_profile TEXT,
                INDEX(timestamp),
                INDEX(cpu_usage),
                INDEX(ram_usage),
                INDEX(gpu_usage),
                INDEX(health_score)
            )
        ''')
    
    def create_alert_configurations_table(self, cursor):
        """Create alert configurations table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                metric_type TEXT NOT NULL,
                warning_threshold REAL,
                critical_threshold REAL,
                enabled BOOLEAN DEFAULT 1,
                notification_type TEXT DEFAULT 'both',
                cooldown_minutes INTEGER DEFAULT 5,
                auto_response_enabled BOOLEAN DEFAULT 0,
                auto_response_action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default alert configurations
        default_alerts = [
            ('High CPU Usage', 'cpu_usage', 80.0, 95.0, 1, 'both', 5, 1, 'lower_process_priorities'),
            ('High Memory Usage', 'ram_usage', 85.0, 95.0, 1, 'both', 5, 1, 'memory_cleanup'),
            ('High GPU Usage', 'gpu_usage', 85.0, 95.0, 1, 'both', 5, 0, ''),
            ('High Temperature', 'cpu_temp', 75.0, 85.0, 1, 'both', 10, 1, 'reduce_process_priorities'),
            ('Low Disk Space', 'disk_usage', 90.0, 95.0, 1, 'both', 15, 1, 'temp_file_cleanup'),
            ('High Network I/O', 'network_io', 10000.0, 20000.0, 1, 'both', 5, 0, ''),
            ('High Disk I/O', 'disk_io', 10000.0, 20000.0, 1, 'both', 5, 0, '')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO alert_configurations 
            (name, metric_type, warning_threshold, critical_threshold, enabled, 
             notification_type, cooldown_minutes, auto_response_enabled, auto_response_action) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_alerts)
    
    def create_optimization_profiles_table(self, cursor):
        """Create optimization profiles table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_profiles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                cpu_priority INTEGER DEFAULT 50,
                memory_priority INTEGER DEFAULT 50,
                gpu_priority INTEGER DEFAULT 50,
                disk_priority INTEGER DEFAULT 50,
                network_priority INTEGER DEFAULT 50,
                aggressive BOOLEAN DEFAULT 0,
                auto_optimize BOOLEAN DEFAULT 0,
                settings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_custom BOOLEAN DEFAULT 0
            )
        ''')
        
        # Insert default optimization profiles
        default_profiles = [
            ('balanced', 'Balanced', 'Balanced performance for general use', 50, 50, 50, 50, 50, 0, 0,
             '{"cpu_limit": 80, "memory_limit": 80, "gpu_limit": 80}'),
            ('gaming', 'Gaming', 'Optimized for gaming performance', 90, 70, 90, 60, 70, 1, 0,
             '{"cpu_limit": 95, "memory_limit": 85, "gpu_limit": 95}'),
            ('productivity', 'Productivity', 'Optimized for office work', 60, 70, 40, 50, 60, 0, 0,
             '{"cpu_limit": 70, "memory_limit": 75, "gpu_limit": 60}'),
            ('multimedia', 'Multimedia', 'Optimized for media consumption', 70, 60, 80, 70, 80, 0, 0,
             '{"cpu_limit": 80, "memory_limit": 70, "gpu_limit": 90}'),
            ('development', 'Development', 'Optimized for programming', 80, 80, 60, 50, 60, 0, 0,
             '{"cpu_limit": 85, "memory_limit": 85, "gpu_limit": 70}')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO optimization_profiles 
            (id, name, description, cpu_priority, memory_priority, gpu_priority, 
             disk_priority, network_priority, aggressive, auto_optimize, settings) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_profiles)
    
    def create_system_events_log_table(self, cursor):
        """Create system events log table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_category TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                title TEXT NOT NULL,
                description TEXT,
                details TEXT,
                source TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at TIMESTAMP,
                acknowledged_by TEXT,
                INDEX(timestamp),
                INDEX(event_type),
                INDEX(severity),
                INDEX(acknowledged)
            )
        ''')
    
    def create_automated_responses_table(self, cursor):
        """Create automated responses table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automated_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                trigger_value REAL,
                response_type TEXT NOT NULL,
                response_action TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                error_message TEXT,
                execution_time_ms INTEGER,
                INDEX(executed_at),
                INDEX(status),
                INDEX(severity)
            )
        ''')
    
    def create_backup_registry_table(self, cursor):
        """Create backup registry table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL UNIQUE,
                backup_path TEXT NOT NULL,
                backup_type TEXT DEFAULT 'manual',
                components TEXT,
                file_size INTEGER,
                compressed BOOLEAN DEFAULT 0,
                checksum TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                restored_at TIMESTAMP,
                restore_success BOOLEAN,
                INDEX(created_at),
                INDEX(backup_type)
            )
        ''')
    
    def create_email_notifications_table(self, cursor):
        """Create email notifications table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_type TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                html_body BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX(status),
                INDEX(notification_type),
                INDEX(created_at)
            )
        ''')
    
    def create_api_usage_table(self, cursor):
        """Create API usage tracking table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                response_status INTEGER,
                response_time_ms INTEGER,
                request_size INTEGER,
                response_size INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX(timestamp),
                INDEX(endpoint),
                INDEX(response_status)
            )
        ''')
    
    def create_performance_metrics_table(self, cursor):
        """Create detailed performance metrics table"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_category TEXT NOT NULL,
                metric_value REAL,
                metric_unit TEXT,
                metadata TEXT,
                collection_method TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX(timestamp),
                INDEX(metric_name),
                INDEX(metric_category)
            )
        ''')
    
    def create_indexes(self, cursor):
        """Create performance indexes"""
        # Additional indexes for better query performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_user_preferences_category ON user_preferences(category)',
            'CREATE INDEX IF NOT EXISTS idx_user_preferences_updated ON user_preferences(updated_at)',
            'CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp_cpu ON system_metrics(timestamp, cpu_usage)',
            'CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp_memory ON system_metrics(timestamp, ram_usage)',
            'CREATE INDEX IF NOT EXISTS idx_alert_configurations_enabled ON alert_configurations(enabled)',
            'CREATE INDEX IF NOT EXISTS idx_optimization_profiles_custom ON optimization_profiles(is_custom)',
            'CREATE INDEX IF NOT EXISTS idx_system_events_category_severity ON system_events(event_category, severity)',
            'CREATE INDEX IF NOT EXISTS idx_automated_responses_rule_status ON automated_responses(rule_id, status)',
            'CREATE INDEX IF NOT EXISTS idx_backup_registry_created_type ON backup_registry(created_at, backup_type)',
            'CREATE INDEX IF NOT EXISTS idx_email_notifications_status_type ON email_notifications(status, notification_type)',
            'CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint_timestamp ON api_usage(endpoint, timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_category_timestamp ON performance_metrics(metric_name, metric_category, timestamp)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def create_triggers(self, cursor):
        """Create triggers for data integrity"""
        triggers = [
            # Update timestamp on preference update
            '''
            CREATE TRIGGER IF NOT EXISTS update_user_preferences_timestamp
            AFTER UPDATE ON user_preferences
            BEGIN
                UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            ''',
            
            # Update timestamp on alert configuration update
            '''
            CREATE TRIGGER IF NOT EXISTS update_alert_configurations_timestamp
            AFTER UPDATE ON alert_configurations
            BEGIN
                UPDATE alert_configurations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            ''',
            
            # Update timestamp on optimization profile update
            '''
            CREATE TRIGGER IF NOT EXISTS update_optimization_profiles_timestamp
            AFTER UPDATE ON optimization_profiles
            BEGIN
                UPDATE optimization_profiles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            ''',
            
            # Log system events for critical alerts
            '''
            CREATE TRIGGER IF NOT EXISTS log_critical_alerts
            AFTER INSERT INTO automated_responses
            WHEN NEW.severity = 'critical'
            BEGIN
                INSERT INTO system_events (event_type, event_category, severity, title, description, details)
                VALUES ('automated_response', 'alert', 'critical', 
                       'Critical Alert Triggered', 
                       'An automated response was triggered due to a critical alert.',
                       json_object('rule_id', NEW.rule_id, 'action', NEW.response_action));
            END
            ''',
            
            # Clean up old API usage logs (keep last 30 days)
            '''
            CREATE TRIGGER IF NOT EXISTS cleanup_api_usage
            AFTER INSERT ON api_usage
            BEGIN
                DELETE FROM api_usage WHERE timestamp < datetime('now', '-30 days');
            END
            ''',
            
            # Clean up old performance metrics (keep last 90 days)
            '''
            CREATE TRIGGER IF NOT EXISTS cleanup_performance_metrics
            AFTER INSERT INTO performance_metrics
            BEGIN
                DELETE FROM performance_metrics WHERE timestamp < datetime('now', '-90 days');
            END
            '''
        ]
        
        for trigger_sql in triggers:
            try:
                cursor.execute(trigger_sql)
            except sqlite3.Error as e:
                print(f"Warning: Failed to create trigger: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get table sizes
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_info[table] = cursor.fetchone()[0]
        
        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "database_path": self.db_path,
            "database_size_bytes": db_size,
            "tables": tables,
            "table_records": table_info,
            "created_at": datetime.fromtimestamp(os.path.getctime(self.db_path)).isoformat()
        }
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Database backup failed: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            conn = sqlite3.connect(backup_path)
            restore_conn = sqlite3.connect(self.db_path)
            conn.backup(restore_conn)
            restore_conn.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Database restore failed: {e}")
            return False
    
    def vacuum_database(self):
        """Optimize database and reclaim space"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        conn.commit()
        conn.close()

# Initialize database schema
if __name__ == '__main__':
    schema = DatabaseSchema()
    print("Database schema initialized successfully")
    
    # Display database info
    info = schema.get_database_info()
    print(f"Database: {info['database_path']}")
    print(f"Size: {info['database_size_bytes'] / 1024:.2f} KB")
    print(f"Tables: {len(info['tables'])}")
    for table, count in info['table_records'].items():
        print(f"  {table}: {count} records")
