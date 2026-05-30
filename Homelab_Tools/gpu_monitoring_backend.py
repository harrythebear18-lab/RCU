"""
Single GPU Monitoring Backend with Multiple Front-End Support
One backend that can serve multiple front-ends (launcher, GPU monitor, etc.)
"""

import time
import threading
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

class GPUBackend(Enum):
    """Available GPU monitoring backends"""
    NVML = "nvidia-ml"
    GPUTIL = "gputil"
    SYSTEM = "system"

@dataclass
class GPUInfo:
    """GPU information structure"""
    usage: float
    temperature: float
    memory_used: int
    memory_total: int
    memory_percent: float
    name: str
    backend: str
    timestamp: float

class GPUMonitoringService:
    """Single GPU monitoring service that can serve multiple front-ends"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure one backend instance"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the GPU monitoring service"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self._active_backend = None
        self._subscribers: List[Callable[[GPUInfo], None]] = []
        self._current_info: Optional[GPUInfo] = None
        self._monitoring = False
        self._monitor_thread = None
        self._update_interval = 1.0  # Update every second
        self._last_error = None
        
        # Initialize the best available backend
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the best available GPU monitoring backend"""
        # Try NVML first (most accurate for NVIDIA)
        if self._test_nvidia_ml():
            self._active_backend = GPUBackend.NVML
            print("GPU Backend: Using NVIDIA-ML")
            return
        
        # Try GPUtil next (cross-platform)
        if self._test_gputil():
            self._active_backend = GPUBackend.GPUTIL
            print("GPU Backend: Using GPUtil")
            return
        
        # Fallback to system info
        self._active_backend = GPUBackend.SYSTEM
        print("GPU Backend: Using System Info (limited functionality)")
    
    def _test_nvidia_ml(self) -> bool:
        """Test if NVIDIA ML backend is available"""
        try:
            import nvidia_ml_py3 as nvml
            nvml.nvmlInit()
            # Test if we can actually get a GPU
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            nvml.nvmlDeviceGetUtilizationRates(handle)
            return True
        except ImportError:
            print("NVIDIA ML library not available - install with: pip install nvidia-ml-py3")
            return False
        except Exception as e:
            print(f"NVIDIA ML initialization failed: {e}")
            return False
    
    def _test_gputil(self) -> bool:
        """Test if GPUtil backend is available"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except ImportError:
            print("GPUtil library not available - install with: pip install GPUtil")
            return False
        except Exception as e:
            print(f"GPUtil initialization failed: {e}")
            return False
    
    def _get_gpu_info_nvidia_ml(self) -> Optional[GPUInfo]:
        """Get GPU info using NVIDIA ML backend"""
        try:
            import nvidia_ml_py3 as nvml
            
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            
            # Get utilization
            util = nvml.nvmlDeviceGetUtilizationRates(handle)
            usage = util.gpu
            
            # Get temperature
            try:
                temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            except:
                temp = 0.0
            
            # Get memory info
            mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
            memory_used = mem_info.used
            memory_total = mem_info.total
            memory_percent = (memory_used / memory_total) * 100 if memory_total > 0 else 0
            
            # Get name
            try:
                name = nvml.nvmlDeviceGetName(handle).decode('utf-8')
            except:
                name = "NVIDIA GPU"
            
            return GPUInfo(
                usage=usage,
                temperature=temp,
                memory_used=memory_used,
                memory_total=memory_total,
                memory_percent=memory_percent,
                name=name,
                backend=GPUBackend.NVML.value,
                timestamp=time.time()
            )
        except Exception as e:
            self._last_error = f"NVML Error: {e}"
            return None
    
    def _get_gpu_info_gputil(self) -> Optional[GPUInfo]:
        """Get GPU info using GPUtil backend"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if not gpus:
                return None
            
            gpu = gpus[0]  # Use first GPU
            
            return GPUInfo(
                usage=gpu.load * 100,
                temperature=gpu.temperature if gpu.temperature else 0.0,
                memory_used=gpu.memoryUsed,
                memory_total=gpu.memoryTotal,
                memory_percent=(gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal > 0 else 0,
                name=gpu.name,
                backend=GPUBackend.GPUTIL.value,
                timestamp=time.time()
            )
        except Exception as e:
            self._last_error = f"GPUtil Error: {e}"
            return None
    
    def _get_gpu_info_system(self) -> Optional[GPUInfo]:
        """Get GPU info using system info (fallback)"""
        try:
            # Very basic fallback - just return zeros
            return GPUInfo(
                usage=0.0,
                temperature=0.0,
                memory_used=0,
                memory_total=0,
                memory_percent=0.0,
                name="Unknown GPU",
                backend=GPUBackend.SYSTEM.value,
                timestamp=time.time()
            )
        except Exception as e:
            self._last_error = f"System Error: {e}"
            return None
    
    def _get_gpu_info(self) -> Optional[GPUInfo]:
        """Get GPU info using the active backend"""
        if self._active_backend == GPUBackend.NVML:
            return self._get_gpu_info_nvidia_ml()
        elif self._active_backend == GPUBackend.GPUTIL:
            return self._get_gpu_info_gputil()
        else:
            return self._get_gpu_info_system()
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                info = self._get_gpu_info()
                if info:
                    self._current_info = info
                    # Notify all subscribers
                    for subscriber in self._subscribers:
                        try:
                            subscriber(info)
                        except Exception as e:
                            print(f"Subscriber error: {e}")
                
                time.sleep(self._update_interval)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                time.sleep(self._update_interval)
    
    # Public API for front-ends
    
    def start_monitoring(self, update_interval: float = 1.0):
        """Start background monitoring"""
        if self._monitoring:
            return
        
        self._update_interval = update_interval
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("GPU monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        print("GPU monitoring stopped")
    
    def subscribe(self, callback: Callable[[GPUInfo], None]):
        """Subscribe to GPU updates (for front-ends)"""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            # Send current info immediately if available
            if self._current_info:
                callback(self._current_info)
    
    def unsubscribe(self, callback: Callable[[GPUInfo], None]):
        """Unsubscribe from GPU updates"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def get_current_info(self) -> Optional[GPUInfo]:
        """Get current GPU info (synchronous call)"""
        if not self._monitoring:
            # If not monitoring, get fresh data
            return self._get_gpu_info()
        return self._current_info
    
    def get_usage(self) -> Optional[float]:
        """Get just the GPU usage percentage"""
        info = self.get_current_info()
        return info.usage if info else None
    
    def get_temperature(self) -> Optional[float]:
        """Get just the GPU temperature"""
        info = self.get_current_info()
        return info.temperature if info else None
    
    def get_memory_percent(self) -> Optional[float]:
        """Get just the GPU memory percentage"""
        info = self.get_current_info()
        return info.memory_percent if info else None
    
    def get_backend_name(self) -> str:
        """Get the active backend name"""
        return self._active_backend.value if self._active_backend else "None"
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error that occurred"""
        return self._last_error
    
    def is_available(self) -> bool:
        """Check if GPU monitoring is available"""
        return self._active_backend != GPUBackend.SYSTEM

# Global instance for easy access
_gpu_service = None

def get_gpu_service() -> GPUMonitoringService:
    """Get the singleton GPU service instance"""
    global _gpu_service
    if _gpu_service is None:
        _gpu_service = GPUMonitoringService()
    return _gpu_service

# Convenience functions for simple usage
def start_gpu_monitoring(update_interval: float = 1.0):
    """Start GPU monitoring"""
    return get_gpu_service().start_monitoring(update_interval)

def stop_gpu_monitoring():
    """Stop GPU monitoring"""
    return get_gpu_service().stop_monitoring()

def get_gpu_usage() -> Optional[float]:
    """Get GPU usage"""
    return get_gpu_service().get_usage()

def get_gpu_info() -> Optional[GPUInfo]:
    """Get full GPU info"""
    return get_gpu_service().get_current_info()

def subscribe_gpu_updates(callback: Callable[[GPUInfo], None]):
    """Subscribe to GPU updates"""
    return get_gpu_service().subscribe(callback)
