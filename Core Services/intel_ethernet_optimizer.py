#!/usr/bin/env python3
"""
Intel-to-Intel Ethernet Optimizer for Homelab Portal
Optimized for Intel-based Windows systems on Ethernet subnet
"""

import subprocess
import socket
import threading
import time
import logging
from typing import Dict, List, Any, Optional
import platform
import psutil
from system_data_connector import get_system_connector

class IntelEthernetOptimizer:
    """Intel-specific optimizations for Ethernet communication"""
    
    def __init__(self):
        self.logger = logging.getLogger("IntelEthernetOptimizer")
        self.is_intel_system = self._detect_intel_system()
        self.ethernet_interfaces = self._detect_ethernet_interfaces()
        
    def _detect_intel_system(self) -> bool:
        """Detect if running on Intel system"""
        try:
            connector = get_system_connector()
            return connector.detect_intel_cpu()
            
        except Exception as e:
            self.logger.error(f"Failed to detect Intel CPU: {e}")
        
        return False
    
    def _detect_ethernet_interfaces(self) -> List[Dict[str, Any]]:
        """Detect Ethernet network interfaces"""
        interfaces = []
        
        try:
            connector = get_system_connector()
            network_interfaces = connector.get_network_interfaces()
            
            for interface in network_interfaces:
                # Look for Ethernet adapters
                if 'ethernet' in interface['name'].lower() or interface.get('speed', 0) > 0:
                    interfaces.append({
                        'name': interface['name'],
                        'type': 'Ethernet',
                        'connection_id': interface['name'],
                        'speed': str(interface.get('speed', 'Unknown')),
                        'is_active': interface.get('is_up', False)
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to detect Ethernet interfaces: {e}")
        
        return interfaces
    
    def _is_interface_active(self, connection_id: str) -> bool:
        """Check if network interface is active"""
        try:
            result = subprocess.run(['wmic', 'nic', 'where', f'NetConnectionID="{connection_id}"', 'get', 'NetConnectionStatus'], 
                                 capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                status = result.stdout.strip().split('\n')[-1].strip()
                return status == '2'  # Connected status is 2
            
        except Exception:
            pass
        
        return False
    
    def optimize_network_settings(self) -> bool:
        """Optimize network settings for Intel Ethernet"""
        if not self.is_intel_system:
            self.logger.warning("Not an Intel system, skipping Intel optimizations")
            return False
        
        success = True
        
        # Optimize each active Ethernet interface
        for interface in self.ethernet_interfaces:
            if interface['is_active']:
                success &= self._optimize_interface(interface)
        
        return success
    
    def _optimize_interface(self, interface: Dict[str, Any]) -> bool:
        """Optimize individual Ethernet interface"""
        try:
            connection_id = interface['connection_id']
            self.logger.info(f"Optimizing Intel Ethernet interface: {connection_id}")
            
            # Enable TCP Chimney Offload (Intel feature)
            self._enable_tcp_chimney(connection_id)
            
            # Enable RSS (Receive Side Scaling)
            self._enable_rss(connection_id)
            
            # Optimize TCP settings
            self._optimize_tcp_settings()
            
            # Disable power saving for network adapter
            self._disable_power_saving(connection_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize interface {interface['name']}: {e}")
            return False
    
    def _enable_tcp_chimney(self, connection_id: str):
        """Enable TCP Chimney Offload"""
        try:
            # Enable TCP Chimney Offload
            subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'chimney=enabled'], 
                         capture_output=True, timeout=5)
            
            self.logger.info("TCP Chimney Offload enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to enable TCP Chimney: {e}")
    
    def _enable_rss(self, connection_id: str):
        """Enable Receive Side Scaling"""
        try:
            # Enable RSS for Intel adapters
            subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'rss=enabled'], 
                         capture_output=True, timeout=5)
            
            self.logger.info("RSS enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to enable RSS: {e}")
    
    def _optimize_tcp_settings(self):
        """Optimize TCP settings for high-speed Ethernet"""
        try:
            # Set TCP parameters for optimal performance
            tcp_settings = [
                ('netsh int tcp set global autotuninglevel=restricted', 'TCP AutoTuning'),
                ('netsh int tcp set global chimney=enabled', 'TCP Chimney'),
                ('netsh int tcp set global rss=enabled', 'TCP RSS'),
                ('netsh int tcp set global netdma=enabled', 'TCP NetDMA')
            ]
            
            for command, description in tcp_settings:
                try:
                    subprocess.run(command.split(), capture_output=True, timeout=5)
                    self.logger.info(f"Optimized: {description}")
                except Exception as e:
                    self.logger.warning(f"Failed to optimize {description}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to optimize TCP settings: {e}")
    
    def _disable_power_saving(self, connection_id: str):
        """Disable power saving for network adapter"""
        try:
            # Disable power saving through Windows power management
            subprocess.run(['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', '19a7bdd1-ffb0-4f1e-9d0f-6e7e6e1c6d1e', '100'], 
                         capture_output=True, timeout=5)
            
            subprocess.run(['powercfg', '/setdcvalueindex', 'SCHEME_CURRENT', '19a7bdd1-ffb0-4f1e-9d0f-6e7e6e1c6d1e', '100'], 
                         capture_output=True, timeout=5)
            
            self.logger.info("Power saving disabled for network adapter")
            
        except Exception as e:
            self.logger.error(f"Failed to disable power saving: {e}")
    
    def get_network_performance_stats(self) -> Dict[str, Any]:
        """Get network performance statistics"""
        stats = {
            'is_intel_system': self.is_intel_system,
            'ethernet_interfaces': self.ethernet_interfaces,
            'network_stats': {},
            'tcp_stats': {}
        }
        
        try:
            # Get network interface statistics
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface in self.ethernet_interfaces:
                if interface['name'] in net_io:
                    stats['network_stats'][interface['name']] = {
                        'bytes_sent': net_io[interface['name']].bytes_sent,
                        'bytes_recv': net_io[interface['name']].bytes_recv,
                        'packets_sent': net_io[interface['name']].packets_sent,
                        'packets_recv': net_io[interface['name']].packets_recv,
                        'errin': net_io[interface['name']].errin,
                        'errout': net_io[interface['name']].errout,
                        'dropin': net_io[interface['name']].dropin,
                        'dropout': net_io[interface['name']].dropout
                    }
            
            # Get TCP statistics
            tcp_stats = psutil.net_connections(kind='tcp')
            stats['tcp_stats'] = {
                'total_connections': len(tcp_stats),
                'established_connections': len([c for c in tcp_stats if c.status == 'ESTABLISHED']),
                'listening_connections': len([c for c in tcp_stats if c.status == 'LISTEN'])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get network stats: {e}")
        
        return stats
    
    def test_ethernet_performance(self, target_ip: str, port: int = 30000) -> Dict[str, Any]:
        """Test Ethernet performance to target system"""
        test_results = {
            'target_ip': target_ip,
            'port': port,
            'latency_ms': None,
            'bandwidth_mbps': None,
            'packet_loss': None,
            'success': False
        }
        
        try:
            # Test latency
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            result = sock.connect_ex((target_ip, port))
            end_time = time.time()
            
            if result == 0:
                test_results['latency_ms'] = (end_time - start_time) * 1000
                test_results['success'] = True
                
                # Simple bandwidth test
                test_data = b'A' * 1024 * 1024  # 1MB test data
                start_time = time.time()
                sock.send(test_data)
                end_time = time.time()
                
                test_results['bandwidth_mbps'] = (len(test_data) * 8) / ((end_time - start_time) * 1000000)
                
            sock.close()
            
        except Exception as e:
            self.logger.error(f"Performance test failed: {e}")
        
        return test_results
    
    def configure_firewall_for_portal(self) -> bool:
        """Configure Windows Firewall for Homelab Portal"""
        try:
            # Add firewall rules for Homelab Portal
            firewall_rules = [
                ('Homelab Portal TCP', 'in', 'tcp', '30000', 'Allow'),
                ('Homelab Portal Discovery UDP', 'in', 'udp', '30001', 'Allow'),
                ('Homelab Portal TCP Out', 'out', 'tcp', '30000', 'Allow'),
                ('Homelab Portal Discovery UDP Out', 'out', 'udp', '30001', 'Allow')
            ]
            
            for rule_name, direction, protocol, port, action in firewall_rules:
                try:
                    # Check if rule exists
                    result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=' + rule_name], 
                                         capture_output=True, text=True, timeout=5)
                    
                    if rule_name not in result.stdout:
                        # Add rule
                        subprocess.run([
                            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                            f'name={rule_name}',
                            f'dir={direction}',
                            f'action={action}',
                            f'protocol={protocol}',
                            f'localport={port}',
                            'enable=yes'
                        ], capture_output=True, timeout=5)
                        
                        self.logger.info(f"Added firewall rule: {rule_name}")
                    else:
                        self.logger.info(f"Firewall rule already exists: {rule_name}")
                        
                except Exception as e:
                    self.logger.error(f"Failed to configure firewall rule {rule_name}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure firewall: {e}")
            return False
    
    def get_intel_specific_info(self) -> Dict[str, Any]:
        """Get Intel-specific system information"""
        intel_info = {
            'is_intel_system': self.is_intel_system,
            'cpu_info': {},
            'network_adapters': [],
            'optimization_status': 'not_optimized'
        }
        
        if self.is_intel_system:
            try:
                # Get detailed CPU information
                result = subprocess.run(['wmic', 'cpu', 'get', 'name,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors'], 
                                     capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    if lines and lines[0].strip():
                        parts = [part.strip() for part in lines[0].split('  ') if part.strip()]
                        if len(parts) >= 4:
                            intel_info['cpu_info'] = {
                                'name': parts[0],
                                'max_clock_speed': parts[1],
                                'cores': parts[2],
                                'logical_processors': parts[3]
                            }
                
                # Get Intel network adapter information
                for interface in self.ethernet_interfaces:
                    if 'INTEL' in interface['name'].upper():
                        intel_info['network_adapters'].append({
                            'name': interface['name'],
                            'type': interface['type'],
                            'speed': interface['speed'],
                            'connection_id': interface['connection_id'],
                            'is_active': interface['is_active']
                        })
                
                intel_info['optimization_status'] = 'ready'
                
            except Exception as e:
                self.logger.error(f"Failed to get Intel info: {e}")
        
        return intel_info

# Global optimizer instance
_intel_optimizer = None

def get_intel_optimizer() -> IntelEthernetOptimizer:
    """Get global Intel optimizer instance"""
    global _intel_optimizer
    if _intel_optimizer is None:
        _intel_optimizer = IntelEthernetOptimizer()
    return _intel_optimizer
