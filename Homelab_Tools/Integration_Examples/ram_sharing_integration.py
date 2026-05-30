#!/usr/bin/env python3
"""
RAM Sharing Integration Example
Demonstrates how to integrate RAM sharing with Core Services
"""

import sys
import time
import os
from datetime import datetime

# Import Core Services with proper path handling
from core_services_import import (
    get_event_bus, EventType, EventPriority,
    get_config_manager,
    get_data_persistence,
    get_unified_monitoring, AlertSeverity
)

class IntegratedRAMSharing:
    """RAM Sharing with Core Services integration"""
    
    def __init__(self):
        # Initialize Core Services
        self.event_bus = get_event_bus()
        self.config_manager = get_config_manager()
        self.data_persistence = get_data_persistence()
        self.unified_monitoring = get_unified_monitoring()
        
        # Component info
        self.component_name = "ram_sharing"
        self.status = "stopped"
        
        # Get configuration
        self.ram_size = self.config_manager.get('ram_sharing.ram_size_gb', 4)
        self.drive_letter = self.config_manager.get('ram_sharing.drive_letter', 'R')
        self.auto_connect = self.config_manager.get('ram_sharing.auto_connect', True)
        
        # Performance metrics
        self.performance_metrics = {
            'transfer_speed': 0,
            'latency': 0,
            'connected_clients': 0,
            'ram_utilization': 0
        }
        
        print(f"✅ RAM Sharing initialized with {self.ram_size}GB RAM disk")
        
    def start_server(self):
        """Start RAM sharing server"""
        print(f"🚀 Starting RAM sharing server...")
        
        # Publish start event
        self.event_bus.publish_sync(
            EventType.SYSTEM,
            self.component_name,
            {
                'action': 'server_starting',
                'ram_size_gb': self.ram_size,
                'drive_letter': self.drive_letter
            }
        )
        
        # Simulate server startup
        self.status = "starting"
        
        try:
            # Store configuration metrics
            self.data_persistence.store_metric(
                source=self.component_name,
                metric_type='ram_size',
                value=self.ram_size,
                unit='GB',
                tags={'type': 'configuration'}
            )
            
            self.data_persistence.store_metric(
                source=self.component_name,
                metric_type='drive_letter',
                value=ord(self.drive_letter),
                unit='ascii',
                tags={'type': 'configuration'}
            )
            
            # Simulate RAM disk creation
            time.sleep(2)
            self.status = "running"
            
            # Publish success event
            self.event_bus.publish_sync(
                EventType.SYSTEM,
                self.component_name,
                {
                    'action': 'server_started',
                    'ram_disk_path': f"{self.drive_letter}:\\",
                    'share_path': f"\\\\192.168.1.186\\RamDisk",
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Store system state
            self.data_persistence.store_system_state(
                self.component_name,
                'server_status',
                'running'
            )
            
            print(f"✅ RAM sharing server started successfully")
            print(f"   RAM Disk: {self.drive_letter}: ({self.ram_size}GB)")
            print(f"   Share Path: \\\\192.168.1.186\\RamDisk")
            
            # Start performance monitoring
            self.start_performance_monitoring()
            
        except Exception as e:
            self.status = "error"
            self.event_bus.publish_sync(
                EventType.ERROR,
                self.component_name,
                {
                    'error': f'Server startup failed: {str(e)}',
                    'severity': 'critical'
                }
            )
            print(f"❌ Server startup failed: {e}")
            
    def connect_client(self):
        """Connect client to RAM sharing server"""
        print(f"🔗 Connecting to RAM sharing server...")
        
        # Publish connection event
        self.event_bus.publish_sync(
            EventType.SYSTEM,
            self.component_name,
            {
                'action': 'client_connecting',
                'server_ip': '192.168.1.186'
            }
        )
        
        try:
            # Simulate connection process
            time.sleep(1)
            
            # Test connectivity
            latency = self.test_network_latency()
            
            if latency < 1000:  # Less than 1 second
                self.status = "connected"
                
                # Store connection metrics
                self.data_persistence.store_metric(
                    source=self.component_name,
                    metric_type='network_latency',
                    value=latency,
                    unit='ms',
                    tags={'type': 'connection'}
                )
                
                # Publish success event
                self.event_bus.publish_sync(
                    EventType.SYSTEM,
                    self.component_name,
                    {
                        'action': 'client_connected',
                        'server_ip': '192.168.1.186',
                        'latency_ms': latency,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                print(f"✅ Connected to RAM sharing server")
                print(f"   Latency: {latency}ms")
                
                # Start performance monitoring
                self.start_performance_monitoring()
                
            else:
                raise Exception(f"High latency: {latency}ms")
                
        except Exception as e:
            self.status = "error"
            self.event_bus.publish_sync(
                EventType.ERROR,
                self.component_name,
                {
                    'error': f'Connection failed: {str(e)}',
                    'severity': 'error'
                }
            )
            print(f"❌ Connection failed: {e}")
            
    def test_network_latency(self):
        """Test network latency to server"""
        # Simulate latency test
        import random
        return random.randint(5, 50)  # 5-50ms latency
        
    def start_performance_monitoring(self):
        """Start performance monitoring"""
        def monitor_performance():
            while self.status in ["running", "connected"]:
                try:
                    # Simulate performance metrics
                    self.performance_metrics['transfer_speed'] = 100 + (50 * (0.5 - random.random()))  # 50-150 MB/s
                    self.performance_metrics['latency'] = 10 + (20 * random.random())  # 10-30ms
                    self.performance_metrics['ram_utilization'] = 20 + (60 * random.random())  # 20-80%
                    self.performance_metrics['connected_clients'] = random.randint(1, 3)
                    
                    # Store performance metrics
                    for metric_name, value in self.performance_metrics.items():
                        unit = {
                            'transfer_speed': 'MB/s',
                            'latency': 'ms',
                            'ram_utilization': 'percent',
                            'connected_clients': 'count'
                        }.get(metric_name, '')
                        
                        self.data_persistence.store_metric(
                            source=self.component_name,
                            metric_type=metric_name,
                            value=value,
                            unit=unit,
                            tags={'monitoring': 'true'}
                        )
                        
                        # Publish monitoring event
                        self.event_bus.publish_sync(
                            EventType.MONITORING,
                            self.component_name,
                            {
                                'metric_type': metric_name,
                                'value': value,
                                'unit': unit,
                                'tags': {'monitoring': 'true'}
                            }
                        )
                    
                    # Check for performance alerts
                    if self.performance_metrics['transfer_speed'] < 50:
                        self.create_performance_alert(
                            "Low Transfer Speed",
                            f"Transfer speed is {self.performance_metrics['transfer_speed']:.1f} MB/s",
                            AlertSeverity.WARNING
                        )
                    
                    if self.performance_metrics['latency'] > 50:
                        self.create_performance_alert(
                            "High Latency",
                            f"Latency is {self.performance_metrics['latency']:.1f}ms",
                            AlertSeverity.ERROR
                        )
                    
                    if self.performance_metrics['ram_utilization'] > 85:
                        self.create_performance_alert(
                            "High RAM Utilization",
                            f"RAM utilization is {self.performance_metrics['ram_utilization']:.1f}%",
                            AlertSeverity.WARNING
                        )
                    
                    # Sleep for 5 seconds
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"⚠️ Performance monitoring error: {e}")
                    time.sleep(5)
                    
        # Start monitoring thread
        import threading
        monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
        monitor_thread.start()
        
    def create_performance_alert(self, title, description, severity):
        """Create performance alert"""
        alert_id = self.unified_monitoring.create_alert(
            title,
            description,
            severity,
            self.component_name,
            metadata=self.performance_metrics.copy()
        )
        
        print(f"🚨 Performance Alert: {title}")
        
    def stop(self):
        """Stop RAM sharing"""
        print(f"⏹️  Stopping RAM sharing...")
        
        # Publish stop event
        self.event_bus.publish_sync(
            EventType.SYSTEM,
            self.component_name,
            {
                'action': 'stopping',
                'timestamp': datetime.now().isoformat()
            }
        )
        
        self.status = "stopping"
        time.sleep(1)
        self.status = "stopped"
        
        # Update system state
        self.data_persistence.store_system_state(
            self.component_name,
            'server_status',
            'stopped'
        )
        
        print(f"✅ RAM sharing stopped")
        
    def get_status(self):
        """Get current status"""
        return {
            'status': self.status,
            'ram_size_gb': self.ram_size,
            'drive_letter': self.drive_letter,
            'performance_metrics': self.performance_metrics.copy()
        }
        
    def get_historical_performance(self, hours=1):
        """Get historical performance data"""
        from datetime import timedelta
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        performance_data = {}
        metric_types = ['transfer_speed', 'latency', 'ram_utilization', 'connected_clients']
        
        for metric_type in metric_types:
            metrics = self.data_persistence.get_metrics(
                source=self.component_name,
                metric_type=metric_type,
                start_time=start_time
            )
            performance_data[metric_type] = metrics
            
        return performance_data

def main():
    """Main demonstration"""
    print("🖥️  RAM Sharing - Core Services Integration Example")
    print("=" * 60)
    
    # Initialize integrated RAM sharing
    ram_sharing = IntegratedRAMSharing()
    
    try:
        # Show configuration
        print(f"⚙️  Configuration:")
        print(f"   RAM Size: {ram_sharing.ram_size}GB")
        print(f"   Drive Letter: {ram_sharing.drive_letter}:")
        print(f"   Auto Connect: {ram_sharing.auto_connect}")
        print()
        
        # Start server mode (simulate)
        print("🚀 Server Mode:")
        ram_sharing.start_server()
        
        # Let it run for a bit
        time.sleep(10)
        
        # Stop server
        ram_sharing.stop()
        print()
        
        # Client mode (simulate)
        print("🔗 Client Mode:")
        ram_sharing.connect_client()
        
        # Let it run for a bit
        time.sleep(10)
        
        # Stop client
        ram_sharing.stop()
        print()
        
        # Show historical data
        print("📊 Historical Performance Data:")
        historical_data = ram_sharing.get_historical_performance(hours=1)
        
        for metric_type, metrics in historical_data.items():
            if metrics:
                latest = metrics[-1]
                print(f"   {metric_type}: {latest.value:.2f} {latest.unit}")
        
        print()
        
        # Show final status
        status = ram_sharing.get_status()
        print("📋 Final Status:")
        print(f"   Status: {status['status']}")
        print(f"   RAM Size: {status['ram_size_gb']}GB")
        print(f"   Drive Letter: {status['drive_letter']}:")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("\n✅ RAM sharing integration demonstration complete")

if __name__ == "__main__":
    main()
