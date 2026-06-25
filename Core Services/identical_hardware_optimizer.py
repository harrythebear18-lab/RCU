#!/usr/bin/env python3
"""
Identical Hardware Optimizer for Homelab Portal
Optimized for Intel CPU + NVIDIA GPU systems (Windows 10/11)
"""

import subprocess
import platform
import logging
from typing import Dict, List, Any, Optional
from system_data_connector import get_system_connector
import psutil
import socket
import time

class IdenticalHardwareOptimizer:
    """Optimizer for identical Intel+NVIDIA hardware systems"""
    
    def __init__(self):
        self.logger = logging.getLogger("IdenticalHardwareOptimizer")
        self.system_info = self._get_system_info()
        self.hardware_match = None
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get detailed system hardware information"""
        info = {
            'cpu': {},
            'gpu': {},
            'windows_version': '',
            'network_info': {},
            'memory_info': {},
            'ram_modules': []
        }
        
        try:
            # Get CPU information
            result = subprocess.run(['wmic', 'cpu', 'get', 'name,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors'], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                if lines and lines[0].strip():
                    parts = [part.strip() for part in lines[0].split('  ') if part.strip()]
                    if len(parts) >= 4:
                        info['cpu'] = {
                            'name': parts[0],
                            'max_clock_speed': parts[1],
                            'cores': parts[2],
                            'logical_processors': parts[3],
                            'is_intel': 'INTEL' in parts[0].upper()
                        }
            
            # Get GPU information
            result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name,AdapterRAM,DriverVersion'], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = [part.strip() for part in line.split('  ') if part.strip()]
                        if len(parts) >= 2 and 'NVIDIA' in parts[0].upper():
                            info['gpu'] = {
                                'name': parts[0],
                                'memory': parts[1] if len(parts) > 1 else 'Unknown',
                                'driver_version': parts[2] if len(parts) > 2 else 'Unknown',
                                'is_nvidia': 'NVIDIA' in parts[0].upper()
                            }
                            break
            
            # Get Windows version
            result = subprocess.run(['ver'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                if '10.0' in version_str:
                    result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Windows 11' in line:
                                info['windows_version'] = 'Windows 11'
                                break
                        else:
                            info['windows_version'] = 'Windows 10'
            
            # Get network information
            info['network_info'] = self._get_network_info()
            
            # Get memory information
            memory = psutil.virtual_memory()
            info['memory_info'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2)
            }
            
            # Get detailed RAM module information using data connector
            try:
                connector = get_system_connector()
                memory_info = connector.get_memory_info()
                info['memory_info'] = memory_info
            except Exception as e:
                self.logger.error(f"Failed to get memory info: {e}")
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = [part.strip() for part in line.split('  ') if part.strip()]
                        if len(parts) >= 4:
                            capacity_gb = int(parts[0]) // (1024**3) if parts[0].isdigit() else 0
                            speed_mhz = int(parts[1]) if parts[1].isdigit() else 0
                            memory_type = parts[2]
                            manufacturer = parts[3]
                            part_number = parts[4] if len(parts) > 4 else ''
                            locator = parts[5] if len(parts) > 5 else ''
                            
                            ram_module = {
                                'capacity_gb': capacity_gb,
                                'speed_mhz': speed_mhz,
                                'memory_type': memory_type,
                                'manufacturer': manufacturer,
                                'part_number': part_number,
                                'locator': locator,
                                'is_ddr4': memory_type == '28' or 'DDR4' in memory_type.upper()
                            }
                            
                            info['ram_modules'].append(ram_module)
            
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
        
        return info
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        network_info = {
            'interfaces': [],
            'local_ip': '',
            'subnet_mask': ''
        }
        
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            network_info['local_ip'] = local_ip
            
            # Get network interfaces
            result = subprocess.run(['wmic', 'nic', 'get', 'name,AdapterType,NetConnectionID,Speed'], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = [part.strip() for part in line.split('  ') if part.strip()]
                        if len(parts) >= 3 and 'ETHERNET' in parts[1].upper():
                            network_info['interfaces'].append({
                                'name': parts[0],
                                'type': parts[1],
                                'connection_id': parts[2],
                                'speed': parts[3] if len(parts) > 3 else 'Unknown'
                            })
            
            # Get subnet mask
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'IPv4 Address' in line and local_ip in line:
                        # Look for the next line with Subnet Mask
                        lines = result.stdout.split('\n')
                        current_index = lines.index(line)
                        for i in range(current_index + 1, min(current_index + 5, len(lines))):
                            if 'Subnet Mask' in lines[i]:
                                mask_part = lines[i].split(':')[-1].strip()
                                network_info['subnet_mask'] = mask_part
                                break
            
        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
        
        return network_info
    
    def check_hardware_compatibility(self, remote_system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check hardware compatibility with remote system"""
        compatibility = {
            'cpu_compatible': False,
            'gpu_compatible': False,
            'windows_compatible': False,
            'network_compatible': False,
            'ram_compatible': False,
            'overall_compatible': False,
            'differences': []
        }
        
        try:
            # CPU compatibility
            local_cpu = self.system_info['cpu'].get('name', '').upper()
            remote_cpu = remote_system_info.get('cpu', {}).get('name', '').upper()
            
            if 'INTEL' in local_cpu and 'INTEL' in remote_cpu:
                compatibility['cpu_compatible'] = True
            else:
                compatibility['differences'].append(f"CPU mismatch: {local_cpu} vs {remote_cpu}")
            
            # GPU compatibility
            local_gpu = self.system_info['gpu'].get('name', '').upper()
            remote_gpu = remote_system_info.get('gpu', {}).get('name', '').upper()
            
            if 'NVIDIA' in local_gpu and 'NVIDIA' in remote_gpu:
                compatibility['gpu_compatible'] = True
            else:
                compatibility['differences'].append(f"GPU mismatch: {local_gpu} vs {remote_gpu}")
            
            # Windows compatibility
            local_windows = self.system_info['windows_version']
            remote_windows = remote_system_info.get('windows_version', '')
            
            if local_windows and remote_windows:
                compatibility['windows_compatible'] = True
                if local_windows != remote_windows:
                    compatibility['differences'].append(f"Windows version difference: {local_windows} vs {remote_windows}")
            
            # Network compatibility (same subnet)
            local_ip = self.system_info['network_info'].get('local_ip', '')
            remote_ip = remote_system_info.get('network_info', {}).get('local_ip', '')
            
            if local_ip and remote_ip:
                # Simple subnet check for common home networks
                local_parts = local_ip.split('.')
                remote_parts = remote_ip.split('.')
                
                if len(local_parts) == 4 and len(remote_parts) == 4:
                    if local_parts[0] == remote_parts[0] and local_parts[1] == remote_parts[1] and local_parts[2] == remote_parts[2]:
                        compatibility['network_compatible'] = True
                    else:
                        compatibility['differences'].append(f"Different subnets: {local_ip} vs {remote_ip}")
            
            # RAM compatibility
            local_ram_modules = self.system_info.get('ram_modules', [])
            remote_ram_modules = remote_system_info.get('ram_modules', [])
            
            if local_ram_modules and remote_ram_modules:
                local_ddr4 = any(module.get('is_ddr4') for module in local_ram_modules)
                remote_ddr4 = any(module.get('is_ddr4') for module in remote_ram_modules)
                
                if local_ddr4 and remote_ddr4:
                    compatibility['ram_compatible'] = True
                else:
                    compatibility['differences'].append(f"RAM type mismatch: DDR4 {local_ddr4} vs DDR4 {remote_ddr4}")
            else:
                compatibility['differences'].append("RAM information not available")
            
            # Overall compatibility
            compatibility['overall_compatible'] = (
                compatibility['cpu_compatible'] and 
                compatibility['gpu_compatible'] and 
                compatibility['windows_compatible'] and 
                compatibility['network_compatible'] and
                compatibility['ram_compatible']
            )
            
        except Exception as e:
            self.logger.error(f"Failed to check compatibility: {e}")
        
        return compatibility
    
    def optimize_for_identical_hardware(self) -> bool:
        """Optimize system for identical hardware communication"""
        try:
            success = True
            
            # Optimize network settings for identical hardware
            success &= self._optimize_identical_network_settings()
            
            # Optimize GPU settings for NVIDIA
            success &= self._optimize_nvidia_settings()
            
            # Optimize CPU settings for Intel
            success &= self._optimize_intel_settings()
            
            # Configure Windows settings for cross-version compatibility
            success &= self._configure_windows_compatibility()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for identical hardware: {e}")
            return False
    
    def _optimize_identical_network_settings(self) -> bool:
        """Optimize network settings for identical hardware communication"""
        try:
            # Enable high-performance network settings
            network_settings = [
                ('netsh int tcp set global autotuninglevel=restricted', 'TCP AutoTuning'),
                ('netsh int tcp set global chimney=enabled', 'TCP Chimney'),
                ('netsh int tcp set global rss=enabled', 'TCP RSS'),
                ('netsh int tcp set global netdma=enabled', 'TCP NetDMA'),
                ('netsh int tcp set global timestamps=enabled', 'TCP Timestamps')
            ]
            
            for command, description in network_settings:
                try:
                    subprocess.run(command.split(), capture_output=True, timeout=5)
                    self.logger.info(f"Optimized: {description}")
                except Exception as e:
                    self.logger.warning(f"Failed to optimize {description}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize network settings: {e}")
            return False
    
    def _optimize_nvidia_settings(self) -> bool:
        """Optimize NVIDIA GPU settings"""
        try:
            # Check if NVIDIA GPU is available
            if not self.system_info['gpu'].get('is_nvidia'):
                self.logger.warning("No NVIDIA GPU detected")
                return False
            
            # Try to optimize NVIDIA settings
            nvidia_settings = [
                ('nvidia-smi -pm 1', 'Enable persistence mode'),
                ('nvidia-smi -ac 877,1215', 'Set GPU clocks (if supported)'),
                ('nvidia-smi -pl 250', 'Set power limit (if supported)')
            ]
            
            for command, description in nvidia_settings:
                try:
                    result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self.logger.info(f"NVIDIA optimization: {description}")
                    else:
                        self.logger.warning(f"NVIDIA optimization failed: {description}")
                except Exception as e:
                    self.logger.warning(f"NVIDIA command failed: {description} - {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize NVIDIA settings: {e}")
            return False
    
    def _optimize_intel_settings(self) -> bool:
        """Optimize Intel CPU settings"""
        try:
            # Check if Intel CPU is available
            if not self.system_info['cpu'].get('is_intel'):
                self.logger.warning("No Intel CPU detected")
                return False
            
            # Set power plan to High Performance
            try:
                subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], capture_output=True, timeout=5)
                self.logger.info("Set power plan to High Performance")
            except Exception as e:
                self.logger.warning(f"Failed to set power plan: {e}")
            
            # Optimize CPU affinity and priority for portal
            try:
                # This would be applied when the portal starts
                self.logger.info("CPU optimization ready for portal process")
            except Exception as e:
                self.logger.warning(f"CPU optimization failed: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize Intel settings: {e}")
            return False
    
    def _configure_windows_compatibility(self) -> bool:
        """Configure Windows settings for cross-version compatibility"""
        try:
            # Configure Windows Firewall
            firewall_rules = [
                ('Homelab Portal TCP', 'in', 'tcp', '30000', 'Allow'),
                ('Homelab Portal Discovery UDP', 'in', 'udp', '30001', 'Allow'),
                ('NVIDIA Sharing TCP', 'in', 'tcp', '30002', 'Allow'),
                ('Screen Sharing TCP', 'in', 'tcp', '30003', 'Allow')
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
                            'enable=yes',
                            'profile=any'
                        ], capture_output=True, timeout=5)
                        
                        self.logger.info(f"Added firewall rule: {rule_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to configure firewall rule {rule_name}: {e}")
            
            # Configure Windows sharing settings
            try:
                # Enable network discovery
                subprocess.run(['netsh', 'advfirewall', 'firewall', 'set', 'rule', 'group="Network Discovery"', 'new', 'enable=Yes'], 
                             capture_output=True, timeout=5)
                
                # Enable file and printer sharing
                subprocess.run(['netsh', 'advfirewall', 'firewall', 'set', 'rule', 'group="File and Printer Sharing"', 'new', 'enable=Yes'], 
                             capture_output=True, timeout=5)
                
                self.logger.info("Windows sharing settings configured")
                
            except Exception as e:
                self.logger.warning(f"Failed to configure Windows sharing: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure Windows compatibility: {e}")
            return False
    
    def get_performance_benchmarks(self) -> Dict[str, Any]:
        """Get performance benchmarks for identical hardware"""
        benchmarks = {
            'cpu_benchmark': self._run_cpu_benchmark(),
            'gpu_benchmark': self._run_gpu_benchmark(),
            'network_benchmark': self._run_network_benchmark(),
            'memory_benchmark': self._run_memory_benchmark()
        }
        
        return benchmarks
    
    def _run_cpu_benchmark(self) -> Dict[str, Any]:
        """Run CPU benchmark"""
        try:
            start_time = time.time()
            
            # Simple CPU benchmark - calculate prime numbers
            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True
            
            primes = []
            for i in range(2, 10000):
                if is_prime(i):
                    primes.append(i)
            
            end_time = time.time()
            
            return {
                'score': len(primes),
                'time_seconds': end_time - start_time,
                'primes_per_second': len(primes) / (end_time - start_time)
            }
            
        except Exception as e:
            self.logger.error(f"CPU benchmark failed: {e}")
            return {'error': str(e)}
    
    def _run_gpu_benchmark(self) -> Dict[str, Any]:
        """Run GPU benchmark"""
        try:
            if not self.system_info['gpu'].get('is_nvidia'):
                return {'error': 'No NVIDIA GPU detected'}
            
            # Use nvidia-smi to get GPU utilization
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], 
                                 capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    parts = [part.strip() for part in lines[0].split(',')]
                    if len(parts) >= 3:
                        return {
                            'gpu_utilization': int(parts[0]),
                            'memory_used_mb': int(parts[1]),
                            'memory_total_mb': int(parts[2]),
                            'memory_utilization': (int(parts[1]) / int(parts[2])) * 100
                        }
            
            return {'error': 'Failed to get GPU info'}
            
        except Exception as e:
            self.logger.error(f"GPU benchmark failed: {e}")
            return {'error': str(e)}
    
    def _run_network_benchmark(self) -> Dict[str, Any]:
        """Run network benchmark"""
        try:
            # Test network latency to Google DNS
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            result = sock.connect_ex(("8.8.8.8", 53))
            end_time = time.time()
            sock.close()
            
            if result == 0:
                return {
                    'latency_ms': (end_time - start_time) * 1000,
                    'status': 'connected'
                }
            else:
                return {'error': 'Network connection failed'}
                
        except Exception as e:
            self.logger.error(f"Network benchmark failed: {e}")
            return {'error': str(e)}
    
    def _run_memory_benchmark(self) -> Dict[str, Any]:
        """Run memory benchmark"""
        try:
            start_time = time.time()
            
            # Simple memory benchmark - allocate and process data
            data = []
            for i in range(100000):
                data.append(i * i)
            
            # Process the data
            total = sum(data)
            
            end_time = time.time()
            
            return {
                'time_seconds': end_time - start_time,
                'operations_per_second': 100000 / (end_time - start_time),
                'total': total
            }
            
        except Exception as e:
            self.logger.error(f"Memory benchmark failed: {e}")
            return {'error': str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get complete system information"""
        return self.system_info

# Global optimizer instance
_identical_optimizer = None

def get_identical_hardware_optimizer() -> IdenticalHardwareOptimizer:
    """Get global identical hardware optimizer instance"""
    global _identical_optimizer
    if _identical_optimizer is None:
        _identical_optimizer = IdenticalHardwareOptimizer()
    return _identical_optimizer
