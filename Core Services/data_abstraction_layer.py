#!/usr/bin/env python3
"""
Data Abstraction Layer
Provides reliable data passing between all tools and services
"""

import logging
import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import weakref

class DataType(Enum):
    """Data types for the abstraction layer"""
    SYSTEM_INFO = "system_info"
    CPU_INFO = "cpu_info"
    GPU_INFO = "gpu_info"
    MEMORY_INFO = "memory_info"
    NETWORK_INFO = "network_info"
    DISK_INFO = "disk_info"
    PROCESS_INFO = "process_info"
    HARDWARE_DETECTION = "hardware_detection"
    PERFORMANCE_METRICS = "performance_metrics"
    SECURITY_EVENTS = "security_events"
    RESOURCE_SHARING = "resource_sharing"

@dataclass
class DataPacket:
    """Standard data packet format"""
    data_type: DataType
    source: str
    timestamp: float
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    def get_data(self, data_type: DataType) -> Optional[DataPacket]:
        """Get data of specified type"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

class SystemDataProvider(DataProvider):
    """System data provider using psutil and platform APIs"""
    
    def __init__(self):
        self.logger = logging.getLogger("SystemDataProvider")
        self._cache = {}
        self._cache_timeout = 1.0  # Cache for 1 second
        self._last_update = {}
        
    def get_data(self, data_type: DataType) -> Optional[DataPacket]:
        """Get system data"""
        try:
            current_time = time.time()
            
            # Check cache
            if data_type in self._cache:
                cache_entry = self._cache[data_type]
                if current_time - cache_entry['timestamp'] < self._cache_timeout:
                    return cache_entry['packet']
            
            # Get fresh data
            data = None
            if data_type == DataType.SYSTEM_INFO:
                data = self._get_system_info()
            elif data_type == DataType.CPU_INFO:
                data = self._get_cpu_info()
            elif data_type == DataType.MEMORY_INFO:
                data = self._get_memory_info()
            elif data_type == DataType.NETWORK_INFO:
                data = self._get_network_info()
            elif data_type == DataType.DISK_INFO:
                data = self._get_disk_info()
            elif data_type == DataType.PROCESS_INFO:
                data = self._get_process_info()
            elif data_type == DataType.HARDWARE_DETECTION:
                data = self._get_hardware_detection()
            
            if data:
                packet = DataPacket(
                    data_type=data_type,
                    source="SystemDataProvider",
                    timestamp=current_time,
                    data=data
                )
                
                # Cache the result
                self._cache[data_type] = {
                    'packet': packet,
                    'timestamp': current_time
                }
                
                return packet
            
        except Exception as e:
            self.logger.error(f"Failed to get {data_type.value}: {e}")
            return DataPacket(
                data_type=data_type,
                source="SystemDataProvider",
                timestamp=time.time(),
                data={},
                error=str(e)
            )
        
        return None
    
    def is_available(self) -> bool:
        """Check if system data provider is available"""
        try:
            import psutil
            import platform
            return True
        except ImportError:
            return False
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import platform
        import socket
        
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'hostname': socket.gethostname()
        }
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        import psutil
        import platform
        
        cpu_freq = psutil.cpu_freq()
        return {
            'brand': platform.processor(),
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'usage_percent': psutil.cpu_percent(interval=0.1),
            'frequency': cpu_freq._asdict() if cpu_freq else None,
            'architecture': platform.architecture()[0],
            'machine': platform.machine()
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        import psutil
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
    
    def _get_network_info(self) -> List[Dict[str, Any]]:
        """Get network interface information"""
        import psutil
        
        interfaces = []
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, addresses in net_if_addrs.items():
            stats = net_if_stats.get(interface_name)
            if stats:
                interface_info = {
                    'name': interface_name,
                    'is_up': stats.isup,
                    'speed': stats.speed,
                    'mtu': stats.mtu,
                    'duplex': stats.duplex,
                    'addresses': []
                }
                
                for addr in addresses:
                    address_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    interface_info['addresses'].append(address_info)
                
                interfaces.append(interface_info)
        
        return interfaces
    
    def _get_disk_info(self) -> List[Dict[str, Any]]:
        """Get disk information"""
        import psutil
        
        disks = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                disks.append(disk_info)
            except:
                continue
        
        return disks
    
    def _get_process_info(self) -> List[Dict[str, Any]]:
        """Get running process information"""
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except:
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return processes[:20]  # Return top 20 processes
    
    def _get_hardware_detection(self) -> Dict[str, Any]:
        """Get hardware detection information"""
        import platform
        
        return {
            'intel_cpu': 'Intel' in platform.processor(),
            'system_type': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }

class SecurityDataProvider(DataProvider):
    """Security events data provider"""
    
    def __init__(self):
        self.logger = logging.getLogger("SecurityDataProvider")
        self._events = []
        
    def get_data(self, data_type: DataType) -> Optional[DataPacket]:
        """Get security events data"""
        if data_type != DataType.SECURITY_EVENTS:
            return None
        
        try:
            # Generate sample security events (in real implementation, this would connect to actual security service)
            events = [
                {
                    'event_id': 'sec_001',
                    'type': 'login_attempt',
                    'severity': 'info',
                    'message': 'Admin login successful',
                    'timestamp': time.time(),
                    'source': 'auth_service'
                },
                {
                    'event_id': 'sec_002', 
                    'type': 'system_check',
                    'severity': 'info',
                    'message': 'Security scan completed',
                    'timestamp': time.time() - 60,
                    'source': 'security_service'
                }
            ]
            
            return DataPacket(
                data_type=DataType.SECURITY_EVENTS,
                source="SecurityDataProvider",
                timestamp=time.time(),
                data={'events': events, 'total_count': len(events)}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get security events: {e}")
            return DataPacket(
                data_type=DataType.SECURITY_EVENTS,
                source="SecurityDataProvider",
                timestamp=time.time(),
                data={'events': [], 'total_count': 0},
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if security provider is available"""
        return True

class ResourceSharingDataProvider(DataProvider):
    """Resource sharing data provider"""
    
    def __init__(self):
        self.logger = logging.getLogger("ResourceSharingDataProvider")
        
    def get_data(self, data_type: DataType) -> Optional[DataPacket]:
        """Get resource sharing data"""
        if data_type != DataType.RESOURCE_SHARING:
            return None
        
        try:
            # Generate sample resource sharing data
            sharing_data = {
                'active_shares': [
                    {
                        'share_id': 'share_001',
                        'type': 'screen',
                        'source': 'node_1',
                        'target': 'node_2',
                        'status': 'active',
                        'bandwidth': '100Mbps'
                    },
                    {
                        'share_id': 'share_002',
                        'type': 'memory',
                        'source': 'node_1',
                        'target': 'node_3',
                        'status': 'active',
                        'bandwidth': '10Gbps'
                    }
                ],
                'total_shares': 2,
                'available_resources': ['screen', 'memory', 'gpu', 'cpu']
            }
            
            return DataPacket(
                data_type=DataType.RESOURCE_SHARING,
                source="ResourceSharingDataProvider",
                timestamp=time.time(),
                data=sharing_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get resource sharing data: {e}")
            return DataPacket(
                data_type=DataType.RESOURCE_SHARING,
                source="ResourceSharingDataProvider",
                timestamp=time.time(),
                data={'active_shares': [], 'total_shares': 0},
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if resource sharing provider is available"""
        return True

class PerformanceMetricsDataProvider(DataProvider):
    """Performance metrics data provider"""
    
    def __init__(self):
        self.logger = logging.getLogger("PerformanceMetricsDataProvider")
        
    def get_data(self, data_type: DataType) -> Optional[DataPacket]:
        """Get performance metrics data"""
        if data_type != DataType.PERFORMANCE_METRICS:
            return None
        
        try:
            import psutil
            
            # Get performance metrics
            metrics = {
                'cpu_metrics': {
                    'usage_percent': psutil.cpu_percent(interval=0.1),
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                    'context_switches': psutil.cpu_stats().ctx_switches,
                    'interrupts': psutil.cpu_stats().interrupts
                },
                'memory_metrics': {
                    'usage_percent': psutil.virtual_memory().percent,
                    'available_gb': psutil.virtual_memory().available / (1024**3),
                    'swap_usage_percent': psutil.swap_memory().percent
                },
                'disk_metrics': {
                    'read_bytes': psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                    'write_bytes': psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
                    'read_count': psutil.disk_io_counters().read_count if psutil.disk_io_counters() else 0,
                    'write_count': psutil.disk_io_counters().write_count if psutil.disk_io_counters() else 0
                },
                'network_metrics': {
                    'bytes_sent': psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
                    'bytes_recv': psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0,
                    'packets_sent': psutil.net_io_counters().packets_sent if psutil.net_io_counters() else 0,
                    'packets_recv': psutil.net_io_counters().packets_recv if psutil.net_io_counters() else 0
                }
            }
            
            return DataPacket(
                data_type=DataType.PERFORMANCE_METRICS,
                source="PerformanceMetricsDataProvider",
                timestamp=time.time(),
                data=metrics
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return DataPacket(
                data_type=DataType.PERFORMANCE_METRICS,
                source="PerformanceMetricsDataProvider",
                timestamp=time.time(),
                data={},
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if performance metrics provider is available"""
        try:
            import psutil
            return True
        except ImportError:
            return False

class GPUDataProvider(DataProvider):
    """GPU data provider"""
    
    def __init__(self):
        self.logger = logging.getLogger("GPUDataProvider")
        
    def get_data(self, data_type: DataType) -> Optional[DataPacket]:
        """Get GPU data"""
        if data_type != DataType.GPU_INFO:
            return None
        
        try:
            gpu_info = {}
            
            # Try to get NVIDIA GPU info
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines):
                        if line.strip():
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 6:
                                gpu_info[f'nvidia_gpu_{i}'] = {
                                    'name': parts[0],
                                    'memory_total': int(parts[1]),
                                    'memory_used': int(parts[2]),
                                    'memory_free': int(parts[3]),
                                    'utilization': int(parts[4]),
                                    'temperature': int(parts[5]) if parts[5] != 'N/A' else None
                                }
            except:
                pass
            
            # Try to get AMD GPU info
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_info[f'amd_gpu_{i}'] = {
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal,
                        'memory_used': gpu.memoryUsed,
                        'memory_free': gpu.memoryFree,
                        'utilization': gpu.load * 100,
                        'temperature': gpu.temperature
                    }
            except:
                pass
            
            return DataPacket(
                data_type=DataType.GPU_INFO,
                source="GPUDataProvider",
                timestamp=time.time(),
                data=gpu_info
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get GPU info: {e}")
            return DataPacket(
                data_type=DataType.GPU_INFO,
                source="GPUDataProvider",
                timestamp=time.time(),
                data={},
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if GPU provider is available"""
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            try:
                import GPUtil
                return len(GPUtil.getGPUs()) > 0
            except:
                return False

class DataAbstractionLayer:
    """Main data abstraction layer"""
    
    def __init__(self):
        self.logger = logging.getLogger("DataAbstractionLayer")
        self.providers: Dict[str, DataProvider] = {}
        self.subscribers: Dict[DataType, List[Callable]] = {}
        self.event_queue = queue.Queue()
        self._running = False
        self._worker_thread = None
        
        # Register default providers
        self.register_provider("system", SystemDataProvider())
        self.register_provider("gpu", GPUDataProvider())
        self.register_provider("security", SecurityDataProvider())
        self.register_provider("resource_sharing", ResourceSharingDataProvider())
        self.register_provider("performance", PerformanceMetricsDataProvider())
        
    def register_provider(self, name: str, provider: DataProvider):
        """Register a data provider"""
        self.providers[name] = provider
        self.logger.info(f"Registered provider: {name}")
    
    def subscribe(self, data_type: DataType, callback: Callable[[DataPacket], None]):
        """Subscribe to data updates"""
        if data_type not in self.subscribers:
            self.subscribers[data_type] = []
        self.subscribers[data_type].append(callback)
        self.logger.info(f"Subscribed to {data_type.value}")
    
    def get_data(self, data_type: DataType, provider_name: Optional[str] = None) -> Optional[DataPacket]:
        """Get data from specified provider or all providers"""
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
            if provider.is_available():
                return provider.get_data(data_type)
        else:
            # Try all providers
            for name, provider in self.providers.items():
                if provider.is_available():
                    data = provider.get_data(data_type)
                    if data and not data.error:
                        return data
        return None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous monitoring"""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._monitoring_loop, args=(interval,))
        self._worker_thread.daemon = True
        self._worker_thread.start()
        self.logger.info("Started data monitoring")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2)
        self.logger.info("Stopped data monitoring")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self._running:
            try:
                # Get data from all providers
                for data_type in DataType:
                    data = self.get_data(data_type)
                    if data:
                        # Notify subscribers
                        if data_type in self.subscribers:
                            for callback in self.subscribers[data_type]:
                                try:
                                    callback(data)
                                except Exception as e:
                                    self.logger.error(f"Error in subscriber callback: {e}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = provider.is_available()
        return status

# Global instance
_data_abstraction_layer = None

def get_data_abstraction_layer() -> DataAbstractionLayer:
    """Get global data abstraction layer instance"""
    global _data_abstraction_layer
    if _data_abstraction_layer is None:
        _data_abstraction_layer = DataAbstractionLayer()
    return _data_abstraction_layer
