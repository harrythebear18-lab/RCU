#!/usr/bin/env python3
"""
Analytics Engine for Homelab Portal
Comprehensive analytics and reporting system
"""

import time
import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    event_type: str
    timestamp: datetime
    source_node: str
    target_node: Optional[str]
    data: Dict[str, Any]
    duration_ms: Optional[float]
    success: bool
    error_message: Optional[str]

class AnalyticsEngine:
    """Comprehensive analytics engine for Homelab Portal"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("AnalyticsEngine")
        self.running = False
        self.aggregation_thread = None
        self.event_queue = []
        self.queue_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize analytics database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    source_node TEXT NOT NULL,
                    target_node TEXT,
                    data TEXT,
                    duration_ms REAL,
                    success BOOLEAN,
                    error_message TEXT
                )
            ''')
            
            # Create aggregations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_aggregations (
                    aggregation_id TEXT PRIMARY KEY,
                    aggregation_type TEXT NOT NULL,
                    time_period TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON analytics_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON analytics_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_source ON analytics_events(source_node)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_target ON analytics_events(target_node)')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Analytics database initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
    
    def start(self):
        """Start analytics engine"""
        if self.running:
            return
        
        self.running = True
        
        # Start aggregation thread
        self.aggregation_thread = threading.Thread(target=self._aggregation_loop, daemon=True)
        self.aggregation_thread.start()
        
        self.logger.info("Analytics engine started")
    
    def stop(self):
        """Stop analytics engine"""
        self.running = False
        
        if self.aggregation_thread:
            self.aggregation_thread.join(timeout=5)
        
        self.logger.info("Analytics engine stopped")
    
    def track_event(self, event_type: str, source_node: str, target_node: str = None, 
                    data: Dict[str, Any] = None, duration_ms: float = None, 
                    success: bool = True, error_message: str = None):
        """Track an analytics event"""
        try:
            event = AnalyticsEvent(
                event_id=self._generate_event_id(),
                event_type=event_type,
                timestamp=datetime.now(),
                source_node=source_node,
                target_node=target_node,
                data=data or {},
                duration_ms=duration_ms,
                success=success,
                error_message=error_message
            )
            
            # Add to queue for batch processing
            with self.queue_lock:
                self.event_queue.append(event)
            
        except Exception as e:
            self.logger.error(f"Failed to track event: {e}")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(int(time.time()))
        raw = f"event:{timestamp}:{len(self.event_queue)}"
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def _aggregation_loop(self):
        """Background aggregation loop"""
        while self.running:
            try:
                # Process queued events
                events_to_process = []
                
                with self.queue_lock:
                    if self.event_queue:
                        events_to_process = self.event_queue.copy()
                        self.event_queue.clear()
                
                if events_to_process:
                    self._process_events(events_to_process)
                
                # Run periodic aggregations
                self._run_periodic_aggregations()
                
                # Sleep for aggregation interval
                time.sleep(60)  # Aggregate every minute
                
            except Exception as e:
                self.logger.error(f"Aggregation loop error: {e}")
                time.sleep(60)
    
    def _process_events(self, events: List[AnalyticsEvent]):
        """Process batch of events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for event in events:
                cursor.execute('''
                    INSERT INTO analytics_events 
                    (event_id, event_type, timestamp, source_node, target_node, 
                     data, duration_ms, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.event_type,
                    event.timestamp,
                    event.source_node,
                    event.target_node,
                    json.dumps(event.data),
                    event.duration_ms,
                    event.success,
                    event.error_message
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Processed {len(events)} analytics events")
            
        except Exception as e:
            self.logger.error(f"Failed to process events: {e}")
    
    def _run_periodic_aggregations(self):
        """Run periodic aggregations"""
        try:
            now = datetime.now()
            
            # Hourly aggregations
            if now.minute == 0:
                self._create_hourly_aggregation(now)
            
            # Daily aggregations
            if now.hour == 0 and now.minute == 0:
                self._create_daily_aggregation(now)
            
        except Exception as e:
            self.logger.error(f"Periodic aggregation error: {e}")
    
    def _create_hourly_aggregation(self, timestamp: datetime):
        """Create hourly aggregation"""
        try:
            start_time = timestamp.replace(minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            
            metrics = self._calculate_metrics(start_time, end_time)
            
            aggregation_id = f"hourly_{start_time.strftime('%Y%m%d_%H')}"
            
            self._save_aggregation(aggregation_id, "hourly", start_time, end_time, metrics)
            
        except Exception as e:
            self.logger.error(f"Hourly aggregation failed: {e}")
    
    def _create_daily_aggregation(self, timestamp: datetime):
        """Create daily aggregation"""
        try:
            start_time = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
            
            metrics = self._calculate_metrics(start_time, end_time)
            
            aggregation_id = f"daily_{start_time.strftime('%Y%m%d')}"
            
            self._save_aggregation(aggregation_id, "daily", start_time, end_time, metrics)
            
        except Exception as e:
            self.logger.error(f"Daily aggregation failed: {e}")
    
    def _calculate_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Calculate metrics for time period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get events in time period
            cursor.execute('''
                SELECT event_type, source_node, target_node, duration_ms, success, data
                FROM analytics_events
                WHERE timestamp >= ? AND timestamp < ?
            ''', (start_time, end_time))
            
            events = cursor.fetchall()
            conn.close()
            
            if not events:
                return {}
            
            # Calculate metrics
            metrics = {
                'total_events': len(events),
                'successful_events': sum(1 for e in events if e[5]),
                'failed_events': sum(1 for e in events if not e[5]),
                'success_rate': (sum(1 for e in events if e[5]) / len(events)) * 100,
                'event_types': defaultdict(int),
                'source_nodes': defaultdict(int),
                'target_nodes': defaultdict(int),
                'average_duration': 0,
                'duration_by_type': defaultdict(list),
                'errors': []
            }
            
            durations = []
            
            for event in events:
                event_type, source_node, target_node, duration_ms, success, data = event
                
                metrics['event_types'][event_type] += 1
                metrics['source_nodes'][source_node] += 1
                
                if target_node:
                    metrics['target_nodes'][target_node] += 1
                
                if duration_ms:
                    durations.append(duration_ms)
                    metrics['duration_by_type'][event_type].append(duration_ms)
                
                if not success:
                    try:
                        event_data = json.loads(data) if data else {}
                        error_msg = event_data.get('error', 'Unknown error')
                        metrics['errors'].append({
                            'event_type': event_type,
                            'source_node': source_node,
                            'error': error_msg,
                            'timestamp': str(datetime.now())
                        })
                    except:
                        pass
            
            # Calculate average duration
            if durations:
                metrics['average_duration'] = statistics.mean(durations)
                metrics['median_duration'] = statistics.median(durations)
                metrics['min_duration'] = min(durations)
                metrics['max_duration'] = max(durations)
            
            # Calculate duration by type
            for event_type, type_durations in metrics['duration_by_type'].items():
                if type_durations:
                    metrics[f'{event_type}_avg_duration'] = statistics.mean(type_durations)
                    metrics[f'{event_type}_median_duration'] = statistics.median(type_durations)
            
            # Convert defaultdicts to regular dicts
            metrics['event_types'] = dict(metrics['event_types'])
            metrics['source_nodes'] = dict(metrics['source_nodes'])
            metrics['target_nodes'] = dict(metrics['target_nodes'])
            metrics['duration_by_type'] = dict(metrics['duration_by_type'])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate metrics: {e}")
            return {}
    
    def _save_aggregation(self, aggregation_id: str, aggregation_type: str, 
                         start_time: datetime, end_time: datetime, metrics: Dict[str, Any]):
        """Save aggregation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO analytics_aggregations 
                (aggregation_id, aggregation_type, time_period, start_time, end_time, metrics)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                aggregation_id,
                aggregation_type,
                f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}",
                start_time,
                end_time,
                json.dumps(metrics)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to save aggregation: {e}")
    
    def get_events(self, event_type: str = None, source_node: str = None, 
                   start_time: datetime = None, end_time: datetime = None, 
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Get analytics events with filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM analytics_events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if source_node:
                query += " AND source_node = ?"
                params.append(source_node)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
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
                    'timestamp': row[2],
                    'source_node': row[3],
                    'target_node': row[4],
                    'data': json.loads(row[5]) if row[5] else {},
                    'duration_ms': row[6],
                    'success': row[7],
                    'error_message': row[8]
                })
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get events: {e}")
            return []
    
    def get_aggregation(self, aggregation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific aggregation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT aggregation_id, aggregation_type, time_period, start_time, end_time, metrics
                FROM analytics_aggregations
                WHERE aggregation_id = ?
            ''', (aggregation_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'aggregation_id': row[0],
                    'aggregation_type': row[1],
                    'time_period': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'metrics': json.loads(row[5]) if row[5] else {}
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get aggregation: {e}")
            return None
    
    def get_recent_aggregations(self, aggregation_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent aggregations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM analytics_aggregations"
            params = []
            
            if aggregation_type:
                query += " WHERE aggregation_type = ?"
                params.append(aggregation_type)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            aggregations = []
            for row in rows:
                aggregations.append({
                    'aggregation_id': row[0],
                    'aggregation_type': row[1],
                    'time_period': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'metrics': json.loads(row[5]) if row[5] else {},
                    'created_at': row[6]
                })
            
            return aggregations
            
        except Exception as e:
            self.logger.error(f"Failed to get recent aggregations: {e}")
            return []
    
    def generate_report(self, report_type: str = 'summary', start_time: datetime = None, 
                        end_time: datetime = None) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            if not start_time:
                start_time = datetime.now() - timedelta(days=7)
            if not end_time:
                end_time = datetime.now()
            
            # Get events in period
            events = self.get_events(start_time=start_time, end_time=end_time, limit=10000)
            
            if not events:
                return {
                    'report_type': report_type,
                    'period': f"{start_time} - {end_time}",
                    'total_events': 0,
                    'message': 'No events found in period'
                }
            
            # Generate report based on type
            if report_type == 'summary':
                return self._generate_summary_report(events, start_time, end_time)
            elif report_type == 'performance':
                return self._generate_performance_report(events, start_time, end_time)
            elif report_type == 'usage':
                return self._generate_usage_report(events, start_time, end_time)
            elif report_type == 'errors':
                return self._generate_error_report(events, start_time, end_time)
            else:
                return self._generate_summary_report(events, start_time, end_time)
                
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return {'error': str(e)}
    
    def _generate_summary_report(self, events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate summary report"""
        try:
            total_events = len(events)
            successful_events = sum(1 for e in events if e['success'])
            failed_events = total_events - successful_events
            
            # Event type distribution
            event_types = defaultdict(int)
            for event in events:
                event_types[event['event_type']] += 1
            
            # Node activity
            source_nodes = defaultdict(int)
            target_nodes = defaultdict(int)
            for event in events:
                source_nodes[event['source_node']] += 1
                if event['target_node']:
                    target_nodes[event['target_node']] += 1
            
            # Duration statistics
            durations = [e['duration_ms'] for e in events if e['duration_ms']]
            duration_stats = {}
            if durations:
                duration_stats = {
                    'average': statistics.mean(durations),
                    'median': statistics.median(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'std_dev': statistics.stdev(durations) if len(durations) > 1 else 0
                }
            
            return {
                'report_type': 'summary',
                'period': f"{start_time} - {end_time}",
                'total_events': total_events,
                'successful_events': successful_events,
                'failed_events': failed_events,
                'success_rate': (successful_events / total_events) * 100 if total_events > 0 else 0,
                'event_types': dict(event_types),
                'source_nodes': dict(source_nodes),
                'target_nodes': dict(target_nodes),
                'duration_statistics': duration_stats,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary report: {e}")
            return {'error': str(e)}
    
    def _generate_performance_report(self, events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate performance report"""
        try:
            # Performance metrics by event type
            performance_by_type = defaultdict(lambda: {'durations': [], 'success_count': 0, 'total_count': 0})
            
            for event in events:
                event_type = event['event_type']
                performance_by_type[event_type]['total_count'] += 1
                
                if event['success']:
                    performance_by_type[event_type]['success_count'] += 1
                
                if event['duration_ms']:
                    performance_by_type[event_type]['durations'].append(event['duration_ms'])
            
            # Calculate performance metrics
            performance_metrics = {}
            for event_type, data in performance_by_type.items():
                durations = data['durations']
                metrics = {
                    'total_events': data['total_count'],
                    'success_rate': (data['success_count'] / data['total_count']) * 100 if data['total_count'] > 0 else 0
                }
                
                if durations:
                    metrics.update({
                        'avg_duration': statistics.mean(durations),
                        'median_duration': statistics.median(durations),
                        'min_duration': min(durations),
                        'max_duration': max(durations),
                        'p95_duration': sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations)
                    })
                
                performance_metrics[event_type] = metrics
            
            return {
                'report_type': 'performance',
                'period': f"{start_time} - {end_time}",
                'performance_metrics': performance_metrics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    def _generate_usage_report(self, events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate usage report"""
        try:
            # Usage patterns by hour
            hourly_usage = defaultdict(int)
            daily_usage = defaultdict(int)
            
            for event in events:
                timestamp = datetime.fromisoformat(event['timestamp'])
                hourly_usage[timestamp.hour] += 1
                daily_usage[timestamp.strftime('%Y-%m-%d')] += 1
            
            # Most active nodes
            node_activity = defaultdict(int)
            for event in events:
                node_activity[event['source_node']] += 1
            
            # Feature usage
            feature_usage = defaultdict(int)
            for event in events:
                feature_usage[event['event_type']] += 1
            
            return {
                'report_type': 'usage',
                'period': f"{start_time} - {end_time}",
                'hourly_usage': dict(hourly_usage),
                'daily_usage': dict(daily_usage),
                'most_active_nodes': dict(sorted(node_activity.items(), key=lambda x: x[1], reverse=True)[:10]),
                'feature_usage': dict(feature_usage),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate usage report: {e}")
            return {'error': str(e)}
    
    def _generate_error_report(self, events: List[Dict[str, Any]], start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate error report"""
        try:
            # Filter error events
            error_events = [e for e in events if not e['success']]
            
            if not error_events:
                return {
                    'report_type': 'errors',
                    'period': f"{start_time} - {end_time}",
                    'total_errors': 0,
                    'message': 'No errors found in period'
                }
            
            # Error types
            error_types = defaultdict(int)
            for event in error_events:
                error_types[event['event_type']] += 1
            
            # Error messages
            error_messages = defaultdict(int)
            for event in error_events:
                error_msg = event['error_message'] or 'Unknown error'
                error_messages[error_msg] += 1
            
            # Errors by node
            errors_by_node = defaultdict(int)
            for event in error_events:
                errors_by_node[event['source_node']] += 1
            
            return {
                'report_type': 'errors',
                'period': f"{start_time} - {end_time}",
                'total_errors': len(error_events),
                'error_rate': (len(error_events) / len(events)) * 100 if events else 0,
                'error_types': dict(error_types),
                'error_messages': dict(sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10]),
                'errors_by_node': dict(errors_by_node),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate error report: {e}")
            return {'error': str(e)}
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old analytics data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old events
            cursor.execute('DELETE FROM analytics_events WHERE timestamp < ?', (cutoff_date,))
            
            # Delete old aggregations (keep daily)
            cursor.execute('DELETE FROM analytics_aggregations WHERE created_at < ? AND aggregation_type != "daily"', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned up analytics data older than {days_to_keep} days")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")

# Global analytics instance
_analytics_engine = None

def get_analytics_engine(db_path: str = "analytics.db") -> AnalyticsEngine:
    """Get global analytics engine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine(db_path)
    return _analytics_engine

if __name__ == "__main__":
    # Test analytics engine
    engine = get_analytics_engine()
    print("Analytics Engine initialized successfully")
    print(f"Database: {engine.db_path}")
    print(f"Events tracked: {len(engine.get_events(limit=100))}")
    print("Analytics Engine is ready for use")
