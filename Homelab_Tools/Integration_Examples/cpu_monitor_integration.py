#!/usr/bin/env python3
"""
CPU Monitor Integration Example
Demonstrates how to integrate existing tools with Core Services
"""

import sys
import time
import psutil
import os
from datetime import datetime

# Import Core Services with proper path handling
from core_services_import import (
    get_event_bus, EventType, EventPriority,
    get_config_manager,
    get_data_persistence,
    get_unified_monitoring, AlertSeverity
)

class IntegratedCPUMonitor:
    """CPU Monitor with Core Services integration"""
    
    def __init__(self):
        # Initialize Core Services
        self.event_bus = get_event_bus()
        self.config_manager = get_config_manager()
        self.data_persistence = get_data_persistence()
        self.unified_monitoring = get_unified_monitoring()
        
        # Get configuration
        self.update_interval = self.config_manager.get('monitoring.update_interval_seconds', 2)
        self.alert_threshold = self.config_manager.get('monitoring.alert_threshold_cpu', 80)
        
        # Component info
        self.component_name = "cpu_monitor"
        self.running = False
        
        # Subscribe to configuration changes
        self.event_bus.subscribe(EventType.CONFIGURATION, self.handle_config_change)
        
        print(f"✅ CPU Monitor initialized with {self.update_interval}s interval")
        
    def handle_config_change(self, event):
        """Handle configuration changes"""
        data = event.data
        if data.get('key') == 'monitoring.update_interval_seconds':
            self.update_interval = data.get('new_value', self.update_interval)
            print(f"📊 Update interval changed to {self.update_interval}s")
        elif data.get('key') == 'monitoring.alert_threshold_cpu':
            self.alert_threshold = data.get('new_value', self.alert_threshold)
            print(f"🚨 CPU alert threshold changed to {self.alert_threshold}%")
            
    def start_monitoring(self):
        """Start CPU monitoring"""
        self.running = True
        print("🚀 Starting CPU monitoring with Core Services integration...")
        
        # Publish start event
        self.event_bus.publish_sync(
            EventType.SYSTEM,
            self.component_name,
            {
                'action': 'monitoring_started',
                'update_interval': self.update_interval,
                'alert_threshold': self.alert_threshold
            }
        )
        
        try:
            while self.running:
                # Collect CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                
                # Create metric data
                metric_data = {
                    'cpu_usage': cpu_percent,
                    'cpu_count': cpu_count,
                    'cpu_freq_current': cpu_freq.current if cpu_freq else 0,
                    'cpu_freq_max': cpu_freq.max if cpu_freq else 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store in data persistence
                self.data_persistence.store_metric(
                    source=self.component_name,
                    metric_type='cpu_usage',
                    value=cpu_percent,
                    unit='percent',
                    tags={'core_count': str(cpu_count)},
                    metadata=metric_data
                )
                
                self.data_persistence.store_metric(
                    source=self.component_name,
                    metric_type='cpu_count',
                    value=cpu_count,
                    unit='count',
                    metadata=metric_data
                )
                
                if cpu_freq:
                    self.data_persistence.store_metric(
                        source=self.component_name,
                        metric_type='cpu_frequency',
                        value=cpu_freq.current,
                        unit='MHz',
                        metadata=metric_data
                    )
                
                # Publish monitoring event
                self.event_bus.publish_sync(
                    EventType.MONITORING,
                    self.component_name,
                    {
                        'metric_type': 'cpu_usage',
                        'value': cpu_percent,
                        'unit': 'percent',
                        'tags': {'core_count': str(cpu_count)},
                        'metadata': metric_data
                    }
                )
                
                # Check for alerts
                if cpu_percent > self.alert_threshold:
                    self.event_bus.publish_sync(
                        EventType.ERROR,
                        self.component_name,
                        {
                            'error': f'High CPU usage: {cpu_percent:.1f}%',
                            'threshold': self.alert_threshold,
                            'severity': 'warning' if cpu_percent < 90 else 'error'
                        },
                        priority=EventPriority.HIGH if cpu_percent > 90 else EventPriority.MEDIUM
                    )
                    
                    # Create unified monitoring alert
                    severity = AlertSeverity.ERROR if cpu_percent > 90 else AlertSeverity.WARNING
                    alert_id = self.unified_monitoring.create_alert(
                        f"High CPU Usage: {cpu_percent:.1f}%",
                        f"CPU usage is {cpu_percent:.1f}% (threshold: {self.alert_threshold}%)",
                        severity,
                        self.component_name,
                        metadata=metric_data
                    )
                    
                    print(f"🚨 Alert created: {alert_id}")
                
                # Log status
                status = "🔴 HIGH" if cpu_percent > 90 else "🟡 MEDIUM" if cpu_percent > self.alert_threshold else "🟢 NORMAL"
                print(f"{status} CPU: {cpu_percent:.1f}% | Cores: {cpu_count} | Freq: {cpu_freq.current:.0f}MHz" if cpu_freq else f"{status} CPU: {cpu_percent:.1f}% | Cores: {cpu_count}")
                
                # Sleep for configured interval
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error in monitoring: {e}")
        finally:
            self.stop_monitoring()
            
    def stop_monitoring(self):
        """Stop CPU monitoring"""
        self.running = False
        
        # Publish stop event
        self.event_bus.publish_sync(
            EventType.SYSTEM,
            self.component_name,
            {
                'action': 'monitoring_stopped',
                'timestamp': datetime.now().isoformat()
            }
        )
        
        print("⏹️  CPU monitoring stopped")
        
    def get_historical_data(self, hours=1):
        """Get historical CPU data"""
        from datetime import timedelta
        
        start_time = datetime.now() - timedelta(hours=hours)
        metrics = self.data_persistence.get_metrics(
            source=self.component_name,
            metric_type='cpu_usage',
            start_time=start_time
        )
        
        return metrics
        
    def get_performance_stats(self):
        """Get performance statistics"""
        stats = self.data_persistence.get_performance_stats(
            component=self.component_name,
            operation='monitoring'
        )
        
        return stats

def main():
    """Main demonstration"""
    print("🖥️  CPU Monitor - Core Services Integration Example")
    print("=" * 60)
    
    # Initialize integrated monitor
    monitor = IntegratedCPUMonitor()
    
    try:
        # Show configuration
        print(f"⚙️  Configuration:")
        print(f"   Update Interval: {monitor.update_interval}s")
        print(f"   Alert Threshold: {monitor.alert_threshold}%")
        print()
        
        # Start monitoring
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Show final stats
        print("\n📊 Final Statistics:")
        stats = monitor.get_performance_stats()
        if stats:
            print(f"   Total Operations: {stats.get('total_operations', 0)}")
            print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
            print(f"   Avg Duration: {stats.get('avg_duration_ms', 0):.2f}ms")
        
        # Show recent data
        print("\n📈 Recent CPU Data (last 10 readings):")
        recent_data = monitor.get_historical_data(hours=1)[:10]
        for metric in recent_data:
            print(f"   {metric.timestamp.strftime('%H:%M:%S')} - {metric.value:.1f}%")

if __name__ == "__main__":
    main()
