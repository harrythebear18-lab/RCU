#!/usr/bin/env python3
"""
Unified Monitoring and Alerting System
Centralized monitoring for all homelab components with intelligent alerting
"""

import asyncio
import threading
import time
import psutil
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from event_bus import get_event_bus, EventType, EventPriority
from config_manager import get_config_manager
from data_persistence import get_data_persistence
from auth_service import get_auth_service

class AlertSeverity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    created_at: datetime
    status: AlertStatus
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ThresholdRule:
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    severity: AlertSeverity
    description: str
    source: str = "*"
    enabled: bool = True

class UnifiedMonitoring:
    """Unified monitoring and alerting system"""
    
    def __init__(self):
        self._config = get_config_manager()
        self._event_bus = get_event_bus()
        self._data_persistence = get_data_persistence()
        self._auth_service = get_auth_service()
        
        self._logger = self._setup_logger()
        self._lock = threading.RLock()
        
        # Monitoring state
        self._alerts: Dict[str, Alert] = {}
        self._threshold_rules: List[ThresholdRule] = []
        self._monitoring_active = False
        self._last_check = datetime.now()
        
        # Initialize default threshold rules
        self._initialize_threshold_rules()
        
        # Subscribe to events
        self._subscribe_to_events()
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup monitoring logger"""
        logger = logging.getLogger('UnifiedMonitoring')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _initialize_threshold_rules(self):
        """Initialize default threshold rules"""
        self._threshold_rules = [
            # CPU thresholds
            ThresholdRule(
                metric_name="cpu_usage",
                operator=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                description="High CPU usage detected",
                source="*"
            ),
            ThresholdRule(
                metric_name="cpu_usage",
                operator=">",
                threshold=95.0,
                severity=AlertSeverity.ERROR,
                description="Critical CPU usage",
                source="*"
            ),
            
            # Memory thresholds
            ThresholdRule(
                metric_name="memory_usage",
                operator=">",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                description="High memory usage",
                source="*"
            ),
            ThresholdRule(
                metric_name="memory_usage",
                operator=">",
                threshold=95.0,
                severity=AlertSeverity.ERROR,
                description="Critical memory usage",
                source="*"
            ),
            
            # Disk thresholds
            ThresholdRule(
                metric_name="disk_usage",
                operator=">",
                threshold=90.0,
                severity=AlertSeverity.WARNING,
                description="High disk usage",
                source="*"
            ),
            
            # Network latency thresholds
            ThresholdRule(
                metric_name="network_latency",
                operator=">",
                threshold=100.0,
                severity=AlertSeverity.WARNING,
                description="High network latency",
                source="*"
            ),
            
            # RAM sharing specific thresholds
            ThresholdRule(
                metric_name="ram_sharing_latency",
                operator=">",
                threshold=50.0,
                severity=AlertSeverity.WARNING,
                description="RAM sharing high latency",
                source="ram_sharing"
            ),
            
            # RDMA thresholds
            ThresholdRule(
                metric_name="rdma_latency",
                operator=">",
                threshold=20.0,
                severity=AlertSeverity.ERROR,
                description="RDMA high latency",
                source="rdma"
            )
        ]
        
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        # Subscribe to monitoring events
        self._event_bus.subscribe(EventType.MONITORING, self._handle_monitoring_event)
        self._event_bus.subscribe(EventType.ERROR, self._handle_error_event)
        self._event_bus.subscribe(EventType.RESOURCE, self._handle_resource_event)
        
    def _handle_monitoring_event(self, event):
        """Handle monitoring events"""
        try:
            data = event.data
            
            # Store monitoring data
            if 'metric_type' in data and 'value' in data:
                self._data_persistence.store_metric(
                    source=event.source,
                    metric_type=data['metric_type'],
                    value=data['value'],
                    unit=data.get('unit', ''),
                    tags=data.get('tags', {}),
                    metadata=data.get('metadata', {})
                )
                
            # Check thresholds
            self._check_thresholds(event.source, data)
            
        except Exception as e:
            self._logger.error(f"Error handling monitoring event: {e}")
            
    def _handle_error_event(self, event):
        """Handle error events"""
        try:
            # Create alert for error events
            alert = self._create_alert(
                title=f"Error in {event.source}",
                description=event.data.get('error', 'Unknown error'),
                severity=AlertSeverity.ERROR,
                source=event.source,
                metadata=event.data
            )
            
            self._add_alert(alert)
            
        except Exception as e:
            self._logger.error(f"Error handling error event: {e}")
            
    def _handle_resource_event(self, event):
        """Handle resource events"""
        try:
            data = event.data
            
            # Store resource metrics
            if 'resource_type' in data and 'value' in data:
                self._data_persistence.store_metric(
                    source=event.source,
                    metric_type=data['resource_type'],
                    value=data['value'],
                    unit=data.get('unit', ''),
                    tags={'resource': 'true'},
                    metadata=data.get('metadata', {})
                )
                
        except Exception as e:
            self._logger.error(f"Error handling resource event: {e}")
            
    def _check_thresholds(self, source: str, data: Dict[str, Any]):
        """Check threshold rules against data"""
        for rule in self._threshold_rules:
            if not rule.enabled:
                continue
                
            # Check if rule applies to this source
            if rule.source != "*" and rule.source != source:
                continue
                
            # Get metric value
            metric_value = data.get(rule.metric_name)
            if metric_value is None:
                continue
                
            # Evaluate threshold
            if self._evaluate_threshold(metric_value, rule.operator, rule.threshold):
                # Create alert
                alert_id = f"{source}_{rule.metric_name}_{int(time.time())}"
                alert = self._create_alert(
                    title=f"Threshold Alert: {rule.description}",
                    description=f"{rule.metric_name} = {metric_value} (threshold: {rule.threshold})",
                    severity=rule.severity,
                    source=source,
                    metadata={
                        'rule': asdict(rule),
                        'current_value': metric_value
                    }
                )
                
                self._add_alert(alert)
                
    def _evaluate_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate threshold condition"""
        try:
            if operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == ">=":
                return value >= threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "==":
                return value == threshold
            elif operator == "!=":
                return value != threshold
            else:
                return False
        except:
            return False
            
    def create_alert(self, title: str, description: str, severity: AlertSeverity,
                   source: str, metadata: Dict[str, Any] = None) -> str:
        """Create new alert and return alert ID"""
        alert = self._create_alert(title, description, severity, source, metadata)
        self._add_alert(alert)
        return alert.id
    
    def _create_alert(self, title: str, description: str, severity: AlertSeverity,
                     source: str, metadata: Dict[str, Any] = None) -> Alert:
        """Create new alert"""
        alert_id = hashlib.md5(f"{title}{source}{time.time()}".encode()).hexdigest()[:16]
        
        return Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            source=source,
            created_at=datetime.now(),
            status=AlertStatus.ACTIVE,
            metadata=metadata
        )
        
    def _add_alert(self, alert: Alert):
        """Add new alert"""
        with self._lock:
            # Check if similar alert already exists
            existing_alert = self._find_similar_alert(alert)
            if existing_alert:
                # Update existing alert
                existing_alert.created_at = alert.created_at
                existing_alert.metadata = alert.metadata
                return
                
            # Add new alert
            self._alerts[alert.id] = alert
            
            # Store alert in database
            self._data_persistence.store_event(
                event_id=f"alert_{alert.id}",
                event_type="alert_created",
                source=alert.source,
                data=asdict(alert)
            )
            
            # Publish alert event
            self._event_bus.publish_sync(
                EventType.ERROR,
                "UnifiedMonitoring",
                {
                    'alert_id': alert.id,
                    'title': alert.title,
                    'severity': alert.severity.name,
                    'source': alert.source
                },
                priority=EventPriority.HIGH
            )
            
            self._logger.warning(f"Alert created: {alert.title} from {alert.source}")
            
    def _find_similar_alert(self, new_alert: Alert) -> Optional[Alert]:
        """Find similar existing alert"""
        for alert in self._alerts.values():
            if (alert.source == new_alert.source and 
                alert.title == new_alert.title and 
                alert.status == AlertStatus.ACTIVE):
                return alert
        return None
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        self._monitoring_active = True
        
        while self._monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check for stale alerts
                self._check_stale_alerts()
                
                # Sleep for configured interval
                interval = self._config.get('monitoring.update_interval_seconds', 5)
                time.sleep(interval)
                
            except Exception as e:
                self._logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
                
    def _collect_system_metrics(self):
        """Collect basic system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self._data_persistence.store_metric(
                source="system",
                metric_type="cpu_usage",
                value=cpu_percent,
                unit="percent",
                tags={'system': 'true'}
            )
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._data_persistence.store_metric(
                source="system",
                metric_type="memory_usage",
                value=memory.percent,
                unit="percent",
                tags={'system': 'true'}
            )
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._data_persistence.store_metric(
                source="system",
                metric_type="disk_usage",
                value=disk_percent,
                unit="percent",
                tags={'system': 'true'}
            )
            
            # Network metrics
            network = psutil.net_io_counters()
            self._data_persistence.store_metric(
                source="system",
                metric_type="network_bytes_sent",
                value=network.bytes_sent,
                unit="bytes",
                tags={'system': 'true'}
            )
            
            self._data_persistence.store_metric(
                source="system",
                metric_type="network_bytes_recv",
                value=network.bytes_recv,
                unit="bytes",
                tags={'system': 'true'}
            )
            
        except Exception as e:
            self._logger.error(f"Error collecting system metrics: {e}")
            
    def _check_stale_alerts(self):
        """Check for stale alerts"""
        with self._lock:
            stale_threshold = timedelta(hours=1)
            current_time = datetime.now()
            
            for alert in list(self._alerts.values()):
                if alert.status == AlertStatus.ACTIVE:
                    if current_time - alert.created_at > stale_threshold:
                        # Auto-resolve stale alerts
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = current_time
                        
                        self._logger.info(f"Auto-resolved stale alert: {alert.id}")
                        
    def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """Get active alerts"""
        with self._lock:
            alerts = [alert for alert in self._alerts.values() if alert.status == AlertStatus.ACTIVE]
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
                
            return sorted(alerts, key=lambda x: (x.severity.value, x.created_at), reverse=True)
            
    def get_all_alerts(self, limit: int = 100) -> List[Alert]:
        """Get all alerts"""
        with self._lock:
            alerts = list(self._alerts.values())
            return sorted(alerts, key=lambda x: x.created_at, reverse=True)[:limit]
            
    def acknowledge_alert(self, alert_id: str, username: str) -> bool:
        """Acknowledge alert"""
        with self._lock:
            if alert_id not in self._alerts:
                return False
                
            alert = self._alerts[alert_id]
            if alert.status != AlertStatus.ACTIVE:
                return False
                
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = username
            alert.acknowledged_at = datetime.now()
            
            # Store alert update
            self._data_persistence.store_event(
                event_id=f"alert_ack_{alert_id}",
                event_type="alert_acknowledged",
                source=alert.source,
                data={
                    'alert_id': alert_id,
                    'acknowledged_by': username
                }
            )
            
            self._logger.info(f"Alert acknowledged: {alert_id} by {username}")
            return True
            
    def resolve_alert(self, alert_id: str, username: str) -> bool:
        """Resolve alert"""
        with self._lock:
            if alert_id not in self._alerts:
                return False
                
            alert = self._alerts[alert_id]
            if alert.status == AlertStatus.RESOLVED:
                return True
                
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            # Store alert in database
            self._data_persistence.store_event(
                event_id=f"alert_{alert.id}",
                event_type="alert_created",
                source=alert.source,
                data={
                    'alert_id': alert.id,
                    'title': alert.title,
                    'severity': alert.severity.name
                }
            )
            self._logger.info(f"Alert resolved: {alert_id} by {username}")
            return True
            
    def add_threshold_rule(self, rule: ThresholdRule) -> bool:
        """Add new threshold rule"""
        with self._lock:
            self._threshold_rules.append(rule)
            self._logger.info(f"Added threshold rule: {rule.description}")
            return True
            
    def remove_threshold_rule(self, rule_index: int) -> bool:
        """Remove threshold rule"""
        with self._lock:
            if 0 <= rule_index < len(self._threshold_rules):
                rule = self._threshold_rules.pop(rule_index)
                self._logger.info(f"Removed threshold rule: {rule.description}")
                return True
            return False
            
    def get_threshold_rules(self) -> List[ThresholdRule]:
        """Get all threshold rules"""
        with self._lock:
            return self._threshold_rules.copy()
            
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        with self._lock:
            active_alerts = len([a for a in self._alerts.values() if a.status == AlertStatus.ACTIVE])
            total_alerts = len(self._alerts)
            
            severity_counts = {}
            for alert in self._alerts.values():
                severity_name = alert.severity.name
                severity_counts[severity_name] = severity_counts.get(severity_name, 0) + 1
                
            return {
                'active_alerts': active_alerts,
                'total_alerts': total_alerts,
                'severity_breakdown': severity_counts,
                'threshold_rules': len(self._threshold_rules),
                'monitoring_active': self._monitoring_active,
                'last_check': self._last_check.isoformat()
            }
            
    def stop(self):
        """Stop monitoring system"""
        self._monitoring_active = False
        if self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)

# Global unified monitoring instance
_unified_monitoring = None

def get_unified_monitoring() -> UnifiedMonitoring:
    """Get global unified monitoring instance"""
    global _unified_monitoring
    if _unified_monitoring is None:
        _unified_monitoring = UnifiedMonitoring()
    return _unified_monitoring

# Convenience functions
def create_alert(title: str, description: str, severity: AlertSeverity, source: str) -> str:
    """Create new alert"""
    monitoring = get_unified_monitoring()
    alert = monitoring._create_alert(title, description, severity, source)
    monitoring._add_alert(alert)
    return alert.id

def get_active_alerts(severity: AlertSeverity = None) -> List[Alert]:
    """Get active alerts"""
    monitoring = get_unified_monitoring()
    return monitoring.get_active_alerts(severity)

def acknowledge_alert(alert_id: str, username: str) -> bool:
    """Acknowledge alert"""
    monitoring = get_unified_monitoring()
    return monitoring.acknowledge_alert(alert_id, username)
