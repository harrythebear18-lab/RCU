#!/usr/bin/env python3
"""
Comprehensive Monitoring and Alerting System for Software-Defined RDMA
Real-time metrics, health checks, and intelligent alerting
"""

import time
import threading
import json
import statistics
import smtplib
import requests
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from datetime import datetime, timedelta
import logging
import psutil
import matplotlib.pyplot as plt
import numpy as np
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

@dataclass
class Metric:
    """Performance metric definition"""
    name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    description: str
    severity: str  # critical, warning, info
    condition: str  # metric expression
    threshold: float
    duration: int  # seconds
    enabled: bool = True
    last_triggered: Optional[float] = None
    trigger_count: int = 0

@dataclass
class HealthCheck:
    """Health check definition"""
    name: str
    check_func: Callable
    interval: int  # seconds
    timeout: int  # seconds
    healthy: bool = True
    last_check: Optional[float] = None
    failure_count: int = 0

class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregates: Dict[str, Dict] = {}
        self.lock = threading.RLock()
        
        # Metric collection intervals
        self.collection_intervals = {
            'system': 1,      # System metrics every second
            'network': 1,     # Network metrics every second
            'dma': 0.1,       # DMA metrics every 100ms
            'application': 5  # Application metrics every 5 seconds
        }
        
        # Start collection threads
        self.running = True
        self.threads = []
        self._start_collection_threads()
    
    def _start_collection_threads(self):
        """Start metric collection threads"""
        for metric_type, interval in self.collection_intervals.items():
            thread = threading.Thread(target=self._collect_metrics, args=(metric_type, interval))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
    
    def _collect_metrics(self, metric_type: str, interval: float):
        """Collect metrics of specific type"""
        while self.running:
            try:
                timestamp = time.time()
                
                if metric_type == 'system':
                    self._collect_system_metrics(timestamp)
                elif metric_type == 'network':
                    self._collect_network_metrics(timestamp)
                elif metric_type == 'dma':
                    self._collect_dma_metrics(timestamp)
                elif metric_type == 'application':
                    self._collect_application_metrics(timestamp)
                
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"Error collecting {metric_type} metrics: {e}")
    
    def _collect_system_metrics(self, timestamp: float):
        """Collect system-level metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        self.add_metric(Metric("cpu_usage_percent", cpu_percent, "percent", timestamp))
        self.add_metric(Metric("cpu_count", cpu_count, "count", timestamp))
        if cpu_freq:
            self.add_metric(Metric("cpu_freq_mhz", cpu_freq.current, "mhz", timestamp))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.add_metric(Metric("memory_usage_percent", memory.percent, "percent", timestamp))
        self.add_metric(Metric("memory_used_gb", memory.used / (1024**3), "gb", timestamp))
        self.add_metric(Metric("memory_available_gb", memory.available / (1024**3), "gb", timestamp))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.add_metric(Metric("disk_usage_percent", disk.percent, "percent", timestamp))
        self.add_metric(Metric("disk_used_gb", disk.used / (1024**3), "gb", timestamp))
        
        # Load average
        load_avg = psutil.getloadavg()
        self.add_metric(Metric("load_avg_1m", load_avg[0], "load", timestamp))
        self.add_metric(Metric("load_avg_5m", load_avg[1], "load", timestamp))
        self.add_metric(Metric("load_avg_15m", load_avg[2], "load", timestamp))
    
    def _collect_network_metrics(self, timestamp: float):
        """Collect network metrics"""
        # Network I/O
        net_io = psutil.net_io_counters()
        self.add_metric(Metric("network_bytes_sent", net_io.bytes_sent, "bytes", timestamp))
        self.add_metric(Metric("network_bytes_recv", net_io.bytes_recv, "bytes", timestamp))
        self.add_metric(Metric("network_packets_sent", net_io.packets_sent, "packets", timestamp))
        self.add_metric(Metric("network_packets_recv", net_io.packets_recv, "packets", timestamp))
        
        # Network connections
        connections = len(psutil.net_connections())
        self.add_metric(Metric("network_connections", connections, "count", timestamp))
    
    def _collect_dma_metrics(self, timestamp: float):
        """Collect DMA-specific metrics"""
        # These would be collected from the DMA system
        # For now, we'll simulate some metrics
        
        # DMA throughput
        throughput = np.random.normal(500, 50)  # MB/s
        self.add_metric(Metric("dma_throughput_mbps", throughput, "mbps", timestamp))
        
        # DMA latency
        latency = np.random.normal(0.5, 0.1)  # microseconds
        self.add_metric(Metric("dma_latency_us", latency, "microseconds", timestamp))
        
        # DMA error rate
        error_rate = np.random.exponential(0.001)  # errors per operation
        self.add_metric(Metric("dma_error_rate", error_rate, "rate", timestamp))
        
        # Active connections
        connections = np.random.poisson(10)
        self.add_metric(Metric("dma_active_connections", connections, "count", timestamp))
    
    def _collect_application_metrics(self, timestamp: float):
        """Collect application-level metrics"""
        # Process memory
        process = psutil.Process()
        memory_info = process.memory_info()
        self.add_metric(Metric("app_memory_rss_mb", memory_info.rss / (1024**2), "mb", timestamp))
        self.add_metric(Metric("app_memory_vms_mb", memory_info.vms / (1024**2), "mb", timestamp))
        
        # Process CPU
        cpu_percent = process.cpu_percent()
        self.add_metric(Metric("app_cpu_percent", cpu_percent, "percent", timestamp))
        
        # Thread count
        thread_count = process.num_threads()
        self.add_metric(Metric("app_thread_count", thread_count, "count", timestamp))
        
        # File descriptors
        try:
            fd_count = process.num_fds()
            self.add_metric(Metric("app_fd_count", fd_count, "count", timestamp))
        except:
            pass
    
    def add_metric(self, metric: Metric):
        """Add a metric to the collector"""
        with self.lock:
            self.metrics[metric.name].append(metric)
            
            # Update aggregates
            if metric.name not in self.aggregates:
                self.aggregates[metric.name] = {
                    'count': 0,
                    'sum': 0.0,
                    'min': float('inf'),
                    'max': float('-inf'),
                    'last_value': metric.value,
                    'last_timestamp': metric.timestamp
                }
            
            agg = self.aggregates[metric.name]
            agg['count'] += 1
            agg['sum'] += metric.value
            agg['min'] = min(agg['min'], metric.value)
            agg['max'] = max(agg['max'], metric.value)
            agg['last_value'] = metric.value
            agg['last_timestamp'] = metric.timestamp
    
    def get_metric(self, name: str, since: Optional[float] = None) -> List[Metric]:
        """Get metrics for a specific name"""
        with self.lock:
            metrics = list(self.metrics[name])
            
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]
            
            return metrics
    
    def get_aggregate(self, name: str) -> Optional[Dict]:
        """Get aggregate statistics for a metric"""
        with self.lock:
            return self.aggregates.get(name)
    
    def get_recent_metrics(self, duration_seconds: int = 300) -> Dict[str, List[Metric]]:
        """Get all metrics from the last N seconds"""
        cutoff_time = time.time() - duration_seconds
        recent_metrics = {}
        
        with self.lock:
            for name, metric_deque in self.metrics.items():
                recent = [m for m in metric_deque if m.timestamp >= cutoff_time]
                if recent:
                    recent_metrics[name] = recent
        
        return recent_metrics
    
    def stop(self):
        """Stop metric collection"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1.0)

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Dict] = []
        self.notification_channels: List[Callable] = []
        self.lock = threading.RLock()
        
        # Load default alerts
        self._load_default_alerts()
        
        # Start alert evaluation thread
        self.running = True
        self.alert_thread = threading.Thread(target=self._evaluate_alerts)
        self.alert_thread.daemon = True
        self.alert_thread.start()
    
    def _load_default_alerts(self):
        """Load default alert definitions"""
        default_alerts = [
            Alert("high_cpu", "High CPU Usage", "CPU usage is above threshold", 
                  "warning", 80.0, 300),
            Alert("high_memory", "High Memory Usage", "Memory usage is above threshold", 
                  "warning", 85.0, 300),
            Alert("high_latency", "High DMA Latency", "DMA latency is above threshold", 
                  "critical", 5.0, 60),
            Alert("low_throughput", "Low DMA Throughput", "DMA throughput is below threshold", 
                  "warning", 100.0, 300),
            Alert("high_error_rate", "High Error Rate", "DMA error rate is above threshold", 
                  "critical", 0.01, 60),
            Alert("disk_space", "Low Disk Space", "Disk usage is above threshold", 
                  "critical", 90.0, 600),
        ]
        
        for alert in default_alerts:
            self.alerts[alert.id] = alert
    
    def add_alert(self, alert: Alert):
        """Add a new alert"""
        with self.lock:
            self.alerts[alert.id] = alert
    
    def remove_alert(self, alert_id: str):
        """Remove an alert"""
        with self.lock:
            if alert_id in self.alerts:
                del self.alerts[alert_id]
    
    def add_notification_channel(self, channel: Callable):
        """Add a notification channel"""
        self.notification_channels.append(channel)
    
    def _evaluate_alerts(self):
        """Continuously evaluate alerts"""
        while self.running:
            try:
                # This would integrate with the metrics collector
                # For now, we'll simulate evaluation
                
                with self.lock:
                    for alert in self.alerts.values():
                        if not alert.enabled:
                            continue
                        
                        # Simulate metric evaluation
                        current_time = time.time()
                        
                        # Check if alert should be evaluated
                        if (alert.last_triggered and 
                            current_time - alert.last_triggered < alert.duration):
                            continue
                        
                        # Evaluate condition (simplified)
                        triggered = self._evaluate_alert_condition(alert)
                        
                        if triggered:
                            self._trigger_alert(alert)
                        else:
                            # Reset if condition is no longer met
                            if alert.last_triggered:
                                self._resolve_alert(alert)
                
                time.sleep(10)  # Evaluate every 10 seconds
                
            except Exception as e:
                logging.error(f"Error evaluating alerts: {e}")
    
    def _evaluate_alert_condition(self, alert: Alert) -> bool:
        """Evaluate alert condition (simplified)"""
        # This would integrate with actual metrics
        # For demo, we'll use random values
        
        if alert.id == "high_cpu":
            return np.random.random() > 0.8
        elif alert.id == "high_memory":
            return np.random.random() > 0.85
        elif alert.id == "high_latency":
            return np.random.random() > 0.95
        elif alert.id == "low_throughput":
            return np.random.random() > 0.9
        elif alert.id == "high_error_rate":
            return np.random.random() > 0.99
        elif alert.id == "disk_space":
            return np.random.random() > 0.9
        
        return False
    
    def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        current_time = time.time()
        alert.last_triggered = current_time
        alert.trigger_count += 1
        
        # Log alert
        alert_event = {
            'timestamp': current_time,
            'alert_id': alert.id,
            'name': alert.name,
            'severity': alert.severity,
            'action': 'triggered',
            'trigger_count': alert.trigger_count
        }
        
        self.alert_history.append(alert_event)
        
        # Send notifications
        message = f"ALERT: {alert.name} - {alert.description}"
        
        for channel in self.notification_channels:
            try:
                channel(alert, message)
            except Exception as e:
                logging.error(f"Error sending notification: {e}")
    
    def _resolve_alert(self, alert: Alert):
        """Resolve an alert"""
        current_time = time.time()
        
        # Log resolution
        alert_event = {
            'timestamp': current_time,
            'alert_id': alert.id,
            'name': alert.name,
            'severity': alert.severity,
            'action': 'resolved',
            'trigger_count': alert.trigger_count
        }
        
        self.alert_history.append(alert_event)
        
        # Clear last triggered
        alert.last_triggered = None
    
    def get_active_alerts(self) -> List[Alert]:
        """Get currently active alerts"""
        with self.lock:
            current_time = time.time()
            return [
                alert for alert in self.alerts.values()
                if alert.last_triggered and 
                current_time - alert.last_triggered < alert.duration
            ]
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """Get alert history from last N hours"""
        cutoff_time = time.time() - (hours * 3600)
        return [event for event in self.alert_history if event['timestamp'] >= cutoff_time]
    
    def stop(self):
        """Stop alert manager"""
        self.running = False
        self.alert_thread.join(timeout=1.0)

class HealthChecker:
    """Performs health checks on system components"""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.check_results: Dict[str, Dict] = {}
        self.lock = threading.RLock()
        
        # Start health check thread
        self.running = True
        self.health_thread = threading.Thread(target=self._run_health_checks)
        self.health_thread.daemon = True
        self.health_thread.start()
        
        # Add default health checks
        self._add_default_health_checks()
    
    def _add_default_health_checks(self):
        """Add default health checks"""
        self.add_health_check(HealthCheck(
            "disk_space", self._check_disk_space, 60, 10
        ))
        
        self.add_health_check(HealthCheck(
            "memory", self._check_memory, 30, 5
        ))
        
        self.add_health_check(HealthCheck(
            "cpu_load", self._check_cpu_load, 30, 5
        ))
        
        self.add_health_check(HealthCheck(
            "dma_service", self._check_dma_service, 10, 5
        ))
    
    def add_health_check(self, check: HealthCheck):
        """Add a health check"""
        with self.lock:
            self.health_checks[check.name] = check
    
    def _run_health_checks(self):
        """Run health checks continuously"""
        while self.running:
            try:
                current_time = time.time()
                
                with self.lock:
                    for check in self.health_checks.values():
                        # Check if it's time to run this check
                        if (check.last_check is None or 
                            current_time - check.last_check >= check.interval):
                            
                            # Run health check
                            healthy = self._run_single_check(check)
                            
                            # Update check status
                            check.healthy = healthy
                            check.last_check = current_time
                            
                            if not healthy:
                                check.failure_count += 1
                            else:
                                check.failure_count = 0
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logging.error(f"Error in health checks: {e}")
    
    def _run_single_check(self, check: HealthCheck) -> bool:
        """Run a single health check"""
        try:
            # Run check with timeout
            result = check.check_func()
            return bool(result)
        except Exception as e:
            logging.error(f"Health check {check.name} failed: {e}")
            return False
    
    def _check_disk_space(self) -> bool:
        """Check disk space"""
        disk = psutil.disk_usage('/')
        return disk.percent < 90
    
    def _check_memory(self) -> bool:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        return memory.percent < 90
    
    def _check_cpu_load(self) -> bool:
        """Check CPU load"""
        load_avg = psutil.getloadavg()
        cpu_count = psutil.cpu_count()
        return load_avg[0] < cpu_count * 2
    
    def _check_dma_service(self) -> bool:
        """Check DMA service health"""
        # This would check the actual DMA service
        # For now, return True
        return True
    
    def get_health_status(self) -> Dict[str, Dict]:
        """Get health status of all checks"""
        with self.lock:
            return {
                name: {
                    'healthy': check.healthy,
                    'last_check': check.last_check,
                    'failure_count': check.failure_count
                }
                for name, check in self.health_checks.items()
            }
    
    def is_healthy(self) -> bool:
        """Check if all systems are healthy"""
        with self.lock:
            return all(check.healthy for check in self.health_checks.values())
    
    def stop(self):
        """Stop health checker"""
        self.running = False
        self.health_thread.join(timeout=1.0)

class MonitoringSystem:
    """Main monitoring system that coordinates all components"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_checker = HealthChecker()
        
        # Dashboard data
        self.dashboard_data = {
            'last_update': time.time(),
            'metrics': {},
            'alerts': [],
            'health': {}
        }
        
        # Add notification channels
        self._setup_notification_channels()
        
        # Start dashboard update thread
        self.running = True
        self.dashboard_thread = threading.Thread(target=self._update_dashboard)
        self.dashboard_thread.daemon = True
        self.dashboard_thread.start()
    
    def _setup_notification_channels(self):
        """Setup notification channels"""
        # Email notification
        self.alert_manager.add_notification_channel(self._send_email_notification)
        
        # Webhook notification
        self.alert_manager.add_notification_channel(self._send_webhook_notification)
    
    def _send_email_notification(self, alert: Alert, message: str):
        """Send email notification"""
        # This would send actual email
        # For demo, just log it
        print(f"EMAIL ALERT: {message}")
    
    def _send_webhook_notification(self, alert: Alert, message: str):
        """Send webhook notification"""
        # This would send actual webhook
        # For demo, just log it
        print(f"WEBHOOK ALERT: {message}")
    
    def _update_dashboard(self):
        """Update dashboard data"""
        while self.running:
            try:
                # Get recent metrics
                recent_metrics = self.metrics_collector.get_recent_metrics(300)  # Last 5 minutes
                
                # Get active alerts
                active_alerts = self.alert_manager.get_active_alerts()
                
                # Get health status
                health_status = self.health_checker.get_health_status()
                
                # Update dashboard data
                self.dashboard_data = {
                    'last_update': time.time(),
                    'metrics': {
                        name: [
                            {'timestamp': m.timestamp, 'value': m.value}
                            for m in metrics[-100:]  # Last 100 points
                        ]
                        for name, metrics in recent_metrics.items()
                    },
                    'alerts': [
                        {
                            'id': alert.id,
                            'name': alert.name,
                            'severity': alert.severity,
                            'last_triggered': alert.last_triggered
                        }
                        for alert in active_alerts
                    ],
                    'health': health_status,
                    'system_healthy': self.health_checker.is_healthy()
                }
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logging.error(f"Error updating dashboard: {e}")
    
    def get_dashboard_data(self) -> Dict:
        """Get current dashboard data"""
        return self.dashboard_data
    
    def generate_report(self, hours: int = 24) -> Dict:
        """Generate monitoring report"""
        cutoff_time = time.time() - (hours * 3600)
        
        # Get metrics summary
        metrics_summary = {}
        for name, agg in self.metrics_collector.aggregates.items():
            metrics_summary[name] = {
                'avg': agg['sum'] / agg['count'] if agg['count'] > 0 else 0,
                'min': agg['min'],
                'max': agg['max'],
                'last_value': agg['last_value']
            }
        
        # Get alert summary
        alert_history = self.alert_manager.get_alert_history(hours)
        alert_summary = {
            'total_alerts': len(alert_history),
            'critical_alerts': len([a for a in alert_history if a['severity'] == 'critical']),
            'warning_alerts': len([a for a in alert_history if a['severity'] == 'warning']),
            'most_triggered': self._get_most_triggered_alerts(alert_history)
        }
        
        # Get health summary
        health_status = self.health_checker.get_health_status()
        health_summary = {
            'overall_healthy': self.health_checker.is_healthy(),
            'healthy_checks': len([h for h in health_status.values() if h['healthy']]),
            'total_checks': len(health_status),
            'unhealthy_checks': [name for name, h in health_status.items() if not h['healthy']]
        }
        
        return {
            'report_time': time.time(),
            'period_hours': hours,
            'metrics': metrics_summary,
            'alerts': alert_summary,
            'health': health_summary
        }
    
    def _get_most_triggered_alerts(self, alert_history: List[Dict]) -> List[Dict]:
        """Get most frequently triggered alerts"""
        alert_counts = {}
        for alert in alert_history:
            alert_id = alert['alert_id']
            alert_counts[alert_id] = alert_counts.get(alert_id, 0) + 1
        
        return [
            {'alert_id': alert_id, 'count': count}
            for alert_id, count in sorted(alert_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]
    
    def create_dashboard_visualization(self, filename: str = "dma_dashboard.png"):
        """Create dashboard visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        dashboard = self.dashboard_data
        
        # CPU usage chart
        if 'cpu_usage_percent' in dashboard['metrics']:
            cpu_data = dashboard['metrics']['cpu_usage_percent']
            if cpu_data:
                timestamps = [d['timestamp'] for d in cpu_data]
                values = [d['value'] for d in cpu_data]
                ax1.plot(timestamps, values)
                ax1.set_title('CPU Usage (%)')
                ax1.set_ylim(0, 100)
        
        # Memory usage chart
        if 'memory_usage_percent' in dashboard['metrics']:
            mem_data = dashboard['metrics']['memory_usage_percent']
            if mem_data:
                timestamps = [d['timestamp'] for d in mem_data]
                values = [d['value'] for d in mem_data]
                ax2.plot(timestamps, values)
                ax2.set_title('Memory Usage (%)')
                ax2.set_ylim(0, 100)
        
        # DMA throughput chart
        if 'dma_throughput_mbps' in dashboard['metrics']:
            throughput_data = dashboard['metrics']['dma_throughput_mbps']
            if throughput_data:
                timestamps = [d['timestamp'] for d in throughput_data]
                values = [d['value'] for d in throughput_data]
                ax3.plot(timestamps, values)
                ax3.set_title('DMA Throughput (MB/s)')
        
        # DMA latency chart
        if 'dma_latency_us' in dashboard['metrics']:
            latency_data = dashboard['metrics']['dma_latency_us']
            if latency_data:
                timestamps = [d['timestamp'] for d in latency_data]
                values = [d['value'] for d in latency_data]
                ax4.plot(timestamps, values)
                ax4.set_title('DMA Latency (μs)')
        
        # Add system status
        fig.suptitle(f'DMA Monitoring Dashboard - {"HEALTHY" if dashboard["system_healthy"] else "UNHEALTHY"}', 
                    fontsize=16, color='green' if dashboard['system_healthy'] else 'red')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Dashboard saved to {filename}")
    
    def stop(self):
        """Stop monitoring system"""
        self.running = False
        
        self.metrics_collector.stop()
        self.alert_manager.stop()
        self.health_checker.stop()
        
        self.dashboard_thread.join(timeout=1.0)

def demo_monitoring_system():
    """Demonstration of monitoring system"""
    print("Monitoring System Demo")
    print("=" * 30)
    
    # Initialize monitoring system
    monitor = MonitoringSystem()
    
    try:
        # Let it run for a while to collect data
        print("Collecting metrics for 30 seconds...")
        time.sleep(30)
        
        # Get dashboard data
        dashboard = monitor.get_dashboard_data()
        print(f"System healthy: {dashboard['system_healthy']}")
        print(f"Active alerts: {len(dashboard['alerts'])}")
        print(f"Metrics collected: {len(dashboard['metrics'])}")
        
        # Generate report
        report = monitor.generate_report(hours=1)
        print(f"\nMonitoring Report (last hour):")
        print(f"  Total alerts: {report['alerts']['total_alerts']}")
        print(f"  Critical alerts: {report['alerts']['critical_alerts']}")
        print(f"  System healthy: {report['health']['overall_healthy']}")
        
        # Create dashboard visualization
        monitor.create_dashboard_visualization("demo_dashboard.png")
        
    finally:
        monitor.stop()

if __name__ == "__main__":
    demo_monitoring_system()
