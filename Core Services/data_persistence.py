#!/usr/bin/env python3
"""
Data Persistence Layer for Homelab System
Provides unified data storage and retrieval for critical metrics
"""

import sqlite3
import json
import os
import threading
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import pickle
import gzip
from event_bus import get_event_bus, EventType, publish_system_event_sync
from config_manager import get_config_manager

@dataclass
class MetricData:
    timestamp: datetime
    source: str
    metric_type: str
    value: Union[float, int, str]
    unit: str
    tags: Dict[str, str]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class HistoricalData:
    metric_type: str
    source: str
    start_time: datetime
    end_time: datetime
    data_points: List[Dict[str, Any]]
    aggregation: str = 'raw'  # raw, avg, min, max, sum

class DataPersistence:
    """Unified data persistence layer"""
    
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path or os.path.join(os.path.dirname(__file__), '..', 'data', 'homelab.db'))
        self.db_path.parent.mkdir(exist_ok=True)
        
        self._lock = threading.RLock()
        self._logger = self._setup_logger()
        self._config = get_config_manager()
        self._event_bus = get_event_bus()
        
        # Initialize database
        self._init_database()
        
        # Start cleanup thread
        self._cleanup_running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_data, daemon=True)
        self._cleanup_thread.start()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup data persistence logger"""
        logger = logging.getLogger('DataPersistence')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _init_database(self):
        """Initialize database schema"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    source TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    tags TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    data TEXT NOT NULL,
                    priority INTEGER DEFAULT 2,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # System state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    state_key TEXT NOT NULL,
                    state_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(component, state_key)
                )
            ''')
            
            # Performance data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    component TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_source_type ON metrics(source, metric_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_component ON performance_data(component)')
            
            conn.commit()
            conn.close()
            
            self._logger.info("Database initialized successfully")
            
    def store_metric(self, source: str, metric_type: str, value: Union[float, int, str], 
                     unit: str = '', tags: Dict[str, str] = None, 
                     metadata: Dict[str, Any] = None, timestamp: datetime = None) -> bool:
        """Store metric data"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
                
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO metrics (timestamp, source, metric_type, value, unit, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp.isoformat(),
                    source,
                    metric_type,
                    float(value) if isinstance(value, (int, float)) else value,
                    unit,
                    json.dumps(tags or {}),
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                conn.close()
                
            self._logger.debug(f"Stored metric: {source}.{metric_type} = {value}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing metric {source}.{metric_type}: {e}")
            return False
            
    def store_event(self, event_id: str, event_type: str, source: str, 
                   data: Dict[str, Any], priority: int = 2, 
                   timestamp: datetime = None) -> bool:
        """Store event data"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
                
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO events (event_id, event_type, source, timestamp, data, priority)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    event_id,
                    event_type,
                    source,
                    timestamp.isoformat(),
                    json.dumps(data),
                    priority
                ))
                
                conn.commit()
                conn.close()
                
            self._logger.debug(f"Stored event: {event_type} from {source}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing event {event_id}: {e}")
            return False
            
    def store_system_state(self, component: str, state_key: str, state_value: str) -> bool:
        """Store system state"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO system_state (component, state_key, state_value, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    component,
                    state_key,
                    state_value,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                conn.close()
                
            self._logger.debug(f"Stored state: {component}.{state_key} = {state_value}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing system state {component}.{state_key}: {e}")
            return False
            
    def store_performance_data(self, component: str, operation: str, duration_ms: float, 
                              success: bool, metadata: Dict[str, Any] = None) -> bool:
        """Store performance data"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO performance_data (timestamp, component, operation, duration_ms, success, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    component,
                    operation,
                    duration_ms,
                    success,
                    json.dumps(metadata or {})
                ))
                
                conn.commit()
                conn.close()
                
            self._logger.debug(f"Stored performance: {component}.{operation} = {duration_ms}ms")
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing performance data {component}.{operation}: {e}")
            return False
            
    def get_metrics(self, source: str = None, metric_type: str = None, 
                   start_time: datetime = None, end_time: datetime = None,
                   limit: int = 1000) -> List[MetricData]:
        """Retrieve metrics with optional filtering"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                query = "SELECT timestamp, source, metric_type, value, unit, tags, metadata FROM metrics WHERE 1=1"
                params = []
                
                if source:
                    query += " AND source = ?"
                    params.append(source)
                    
                if metric_type:
                    query += " AND metric_type = ?"
                    params.append(metric_type)
                    
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                    
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                    
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                metrics = []
                for row in rows:
                    metrics.append(MetricData(
                        timestamp=datetime.fromisoformat(row[0]),
                        source=row[1],
                        metric_type=row[2],
                        value=row[3],
                        unit=row[4] or '',
                        tags=json.loads(row[5]) if row[5] else {},
                        metadata=json.loads(row[6]) if row[6] else None
                    ))
                    
                return metrics
                
        except Exception as e:
            self._logger.error(f"Error retrieving metrics: {e}")
            return []
            
    def get_events(self, event_type: str = None, source: str = None,
                  start_time: datetime = None, end_time: datetime = None,
                  limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve events with optional filtering"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                query = "SELECT event_id, event_type, source, timestamp, data, priority FROM events WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                    
                if source:
                    query += " AND source = ?"
                    params.append(source)
                    
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                    
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                    
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                events = []
                for row in rows:
                    events.append({
                        'event_id': row[0],
                        'event_type': row[1],
                        'source': row[2],
                        'timestamp': datetime.fromisoformat(row[3]),
                        'data': json.loads(row[4]),
                        'priority': row[5]
                    })
                    
                return events
                
        except Exception as e:
            self._logger.error(f"Error retrieving events: {e}")
            return []
            
    def get_system_state(self, component: str = None) -> Dict[str, str]:
        """Retrieve system state"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                query = "SELECT state_key, state_value FROM system_state"
                params = []
                
                if component:
                    query += " WHERE component = ?"
                    params.append(component)
                    
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                return {row[0]: row[1] for row in rows}
                
        except Exception as e:
            self._logger.error(f"Error retrieving system state: {e}")
            return {}
            
    def get_performance_stats(self, component: str = None, operation: str = None,
                             start_time: datetime = None, end_time: datetime = None) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                query = "SELECT duration_ms, success FROM performance_data WHERE 1=1"
                params = []
                
                if component:
                    query += " AND component = ?"
                    params.append(component)
                    
                if operation:
                    query += " AND operation = ?"
                    params.append(operation)
                    
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                    
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                    
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                if not rows:
                    return {}
                    
                durations = [row[0] for row in rows if row[1]]  # Only successful operations
                success_count = sum(1 for row in rows if row[1])
                total_count = len(rows)
                
                return {
                    'total_operations': total_count,
                    'successful_operations': success_count,
                    'success_rate': (success_count / total_count) * 100,
                    'avg_duration_ms': sum(durations) / len(durations) if durations else 0,
                    'min_duration_ms': min(durations) if durations else 0,
                    'max_duration_ms': max(durations) if durations else 0
                }
                
        except Exception as e:
            self._logger.error(f"Error retrieving performance stats: {e}")
            return {}
            
    def get_aggregated_metrics(self, source: str, metric_type: str, 
                             start_time: datetime, end_time: datetime,
                             aggregation: str = 'avg', interval: int = 60) -> List[Dict[str, Any]]:
        """Get aggregated metrics over time intervals"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Build aggregation query
                agg_func = {
                    'avg': 'AVG(value)',
                    'min': 'MIN(value)',
                    'max': 'MAX(value)',
                    'sum': 'SUM(value)',
                    'count': 'COUNT(value)'
                }.get(aggregation, 'AVG(value)')
                
                query = f'''
                    SELECT 
                        datetime((strftime('%s', timestamp) / {interval}) * {interval}, 'unixepoch') as time_bucket,
                        {agg_func} as aggregated_value,
                        COUNT(*) as count
                    FROM metrics
                    WHERE source = ? AND metric_type = ? AND timestamp >= ? AND timestamp <= ?
                    GROUP BY time_bucket
                    ORDER BY time_bucket
                '''
                
                cursor.execute(query, (
                    source,
                    metric_type,
                    start_time.isoformat(),
                    end_time.isoformat()
                ))
                
                rows = cursor.fetchall()
                conn.close()
                
                return [
                    {
                        'timestamp': datetime.fromisoformat(row[0]),
                        'value': row[1],
                        'count': row[2]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            self._logger.error(f"Error retrieving aggregated metrics: {e}")
            return []
            
    def delete_old_data(self, retention_days: int = None) -> int:
        """Delete old data based on retention policy"""
        if retention_days is None:
            retention_days = self._config.get('monitoring.history_retention_days', 30)
            
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Delete old metrics
                cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date.isoformat(),))
                deleted_count += cursor.rowcount
                
                # Delete old events
                cursor.execute("DELETE FROM events WHERE timestamp < ?", (cutoff_date.isoformat(),))
                deleted_count += cursor.rowcount
                
                # Delete old performance data
                cursor.execute("DELETE FROM performance_data WHERE timestamp < ?", (cutoff_date.isoformat(),))
                deleted_count += cursor.rowcount
                
                conn.commit()
                conn.close()
                
            self._logger.info(f"Deleted {deleted_count} old records (older than {retention_days} days)")
            return deleted_count
            
        except Exception as e:
            self._logger.error(f"Error deleting old data: {e}")
            return 0
            
    def _cleanup_old_data(self):
        """Background cleanup thread"""
        while self._cleanup_running:
            try:
                retention_days = self._config.get('monitoring.history_retention_days', 30)
                self.delete_old_data(retention_days)
                
                # Sleep for 24 hours
                time.sleep(86400)
                
            except Exception as e:
                self._logger.error(f"Error in cleanup thread: {e}")
                time.sleep(3600)  # Wait 1 hour on error
                
    def backup_database(self, backup_path: str = None) -> bool:
        """Create database backup"""
        if backup_path is None:
            backup_path = self.db_path.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                backup_conn = sqlite3.connect(str(backup_path))
                
                # Use SQLite backup API
                conn.backup(backup_conn)
                
                conn.close()
                backup_conn.close()
                
            self._logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error backing up database: {e}")
            return False
            
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                tables = ['metrics', 'events', 'system_state', 'performance_data']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f'{table}_count'] = cursor.fetchone()[0]
                    
                # Database size
                stats['database_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
                
                # Oldest and newest records
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM metrics")
                oldest, newest = cursor.fetchone()
                stats['oldest_record'] = oldest
                stats['newest_record'] = newest
                
                conn.close()
                return stats
                
        except Exception as e:
            self._logger.error(f"Error getting database stats: {e}")
            return {}
            
    def stop(self):
        """Stop data persistence service"""
        self._cleanup_running = False
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
    
    def close(self):
        """Close database connection"""
        if hasattr(self, '_conn') and self._conn:
            self._conn.close()
    
    def initialize_database(self) -> bool:
        """Initialize database schema"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Create tables
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        source TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        tags TEXT,
                        metadata TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        data TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT,
                        severity INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        source TEXT,
                        acknowledged_by TEXT,
                        acknowledged_at TEXT,
                        resolved_by TEXT,
                        resolved_at TEXT,
                        resolution_message TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_state (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        component TEXT NOT NULL,
                        state TEXT NOT NULL,
                        data TEXT
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_source ON metrics(source)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)')
                
                conn.commit()
                conn.close()
                
            self._logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Error initializing database: {e}")
            return False
    
    def get_table_info(self) -> List[str]:
        """Get list of tables in database"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                conn.close()
                return tables
                
        except Exception as e:
            self._logger.error(f"Error getting table info: {e}")
            return []
    
    def get_metrics(self, source: str = None, metric_type: str = None, 
                   start_time: datetime = None, end_time: datetime = None,
                   tags: Dict[str, str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get metrics with optional filtering"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                query = "SELECT * FROM metrics WHERE 1=1"
                params = []
                
                if source:
                    query += " AND source = ?"
                    params.append(source)
                    
                if metric_type:
                    query += " AND metric_type = ?"
                    params.append(metric_type)
                    
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time.isoformat())
                    
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time.isoformat())
                    
                if tags:
                    for key, value in tags.items():
                        query += f" AND tags LIKE ?"
                        params.append(f'%"{key}":"{value}"%')
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dict format
                columns = [desc[0] for desc in cursor.description]
                metrics = []
                for row in rows:
                    metric = dict(zip(columns, row))
                    # Parse JSON fields
                    if metric['tags']:
                        metric['tags'] = json.loads(metric['tags'])
                    else:
                        metric['tags'] = {}
                    if metric['metadata']:
                        metric['metadata'] = json.loads(metric['metadata'])
                    else:
                        metric['metadata'] = {}
                    metrics.append(metric)
                
                conn.close()
                return metrics
                
        except Exception as e:
            self._logger.error(f"Error getting metrics: {e}")
            return []
    
    def store_bulk_metrics(self, metrics: List[Dict[str, Any]]) -> bool:
        """Store multiple metrics efficiently"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                data = []
                for metric in metrics:
                    data.append((
                        datetime.now().isoformat(),
                        metric['source'],
                        metric['metric_type'],
                        metric['value'],
                        metric.get('unit', ''),
                        json.dumps(metric.get('tags', {})),
                        json.dumps(metric.get('metadata', {}))
                    ))
                
                cursor.executemany('''
                    INSERT INTO metrics (timestamp, source, metric_type, value, unit, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', data)
                
                conn.commit()
                conn.close()
                
            self._logger.info(f"Stored {len(metrics)} bulk metrics")
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing bulk metrics: {e}")
            return False
    
    def store_event(self, event_type: str, source: str, data: Dict[str, Any]) -> bool:
        """Store event data"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO events (timestamp, event_type, source, data)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.now().isoformat(), event_type, source, json.dumps(data)))
                
                conn.commit()
                conn.close()
                
            return True
            
        except Exception as e:
            self._logger.error(f"Error storing event: {e}")
            return False
    
    def get_correlated_metrics(self, metric_types: List[str], tags: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Get correlated metrics across multiple types"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                query = f"SELECT * FROM metrics WHERE metric_type IN ({','.join(['?']*len(metric_types))})"
                params = metric_types.copy()
                
                if tags:
                    for key, value in tags.items():
                        query += f" AND tags LIKE ?"
                        params.append(f'%"{key}":"{value}"%')
                
                query += " ORDER BY timestamp DESC LIMIT 1000"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                columns = [desc[0] for desc in cursor.description]
                metrics = []
                for row in rows:
                    metric = dict(zip(columns, row))
                    if metric['tags']:
                        metric['tags'] = json.loads(metric['tags'])
                    else:
                        metric['tags'] = {}
                    metrics.append(metric)
                
                conn.close()
                return metrics
                
        except Exception as e:
            self._logger.error(f"Error getting correlated metrics: {e}")
            return []
    
    def get_system_statistics(self, systems: List[str], metric_types: List[str]) -> Dict[str, Any]:
        """Get aggregated statistics for multiple systems"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                stats = {}
                
                for system in systems:
                    system_stats = {}
                    for metric_type in metric_types:
                        cursor.execute('''
                            SELECT AVG(value), MIN(value), MAX(value), COUNT(*)
                            FROM metrics 
                            WHERE source = ? AND metric_type = ?
                        ''', (system, metric_type))
                        
                        result = cursor.fetchone()
                        if result and result[3] > 0:  # If count > 0
                            system_stats[metric_type] = {
                                'avg': result[0],
                                'min': result[1],
                                'max': result[2],
                                'count': result[3]
                            }
                    
                    stats[system] = system_stats
                
                conn.close()
                return stats
                
        except Exception as e:
            self._logger.error(f"Error getting system statistics: {e}")
            return {}
    
    def get_time_series(self, metric_type: str, start_time: datetime, end_time: datetime,
                       aggregation: str = 'avg') -> List[Dict[str, Any]]:
        """Get time series data with aggregation"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                agg_func = aggregation.upper()
                cursor.execute(f'''
                    SELECT 
                        datetime(timestamp) as time_bucket,
                        {agg_func}(value) as value,
                        COUNT(*) as count
                    FROM metrics 
                    WHERE metric_type = ? AND timestamp BETWEEN ? AND ?
                    GROUP BY datetime(timestamp)
                    ORDER BY time_bucket
                ''', (metric_type, start_time.isoformat(), end_time.isoformat()))
                
                rows = cursor.fetchall()
                
                time_series = []
                for row in rows:
                    time_series.append({
                        'timestamp': row[0],
                        'value': row[1],
                        'count': row[2]
                    })
                
                conn.close()
                return time_series
                
        except Exception as e:
            self._logger.error(f"Error getting time series: {e}")
            return []
    
    def archive_data(self, days: int) -> str:
        """Archive old data to compressed file"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            archive_path = self.db_path.parent / f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.gz"
            
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Get old data
                cursor.execute('''
                    SELECT * FROM metrics WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                columns = [desc[0] for desc in cursor.description]
                old_data = []
                for row in cursor.fetchall():
                    record = dict(zip(columns, row))
                    old_data.append(record)
                
                # Delete old data
                cursor.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff_date.isoformat(),))
                conn.commit()
                conn.close()
                
                # Compress and save
                with gzip.open(archive_path, 'wt') as f:
                    json.dump(old_data, f)
                
            self._logger.info(f"Archived {len(old_data)} records to {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            self._logger.error(f"Error archiving data: {e}")
            return None
    
    def optimize_database(self) -> bool:
        """Optimize database performance"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Run optimization commands
                cursor.execute("VACUUM")
                cursor.execute("ANALYZE")
                
                conn.commit()
                conn.close()
                
            self._logger.info("Database optimized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Error optimizing database: {e}")
            return False

# Global data persistence instance
_data_persistence = None

def get_data_persistence() -> DataPersistence:
    """Get global data persistence instance"""
    global _data_persistence
    if _data_persistence is None:
        _data_persistence = DataPersistence()
    return _data_persistence

# Convenience functions
def store_metric(source: str, metric_type: str, value: Union[float, int, str], **kwargs) -> bool:
    """Store metric data"""
    persistence = get_data_persistence()
    return persistence.store_metric(source, metric_type, value, **kwargs)

def store_event(event_id: str, event_type: str, source: str, data: Dict[str, Any], **kwargs) -> bool:
    """Store event data"""
    persistence = get_data_persistence()
    return persistence.store_event(event_id, event_type, source, data, **kwargs)

def get_metrics(source: str = None, metric_type: str = None, **kwargs) -> List[MetricData]:
    """Retrieve metrics"""
    persistence = get_data_persistence()
    return persistence.get_metrics(source, metric_type, **kwargs)
