"""
GPU Monitoring Abstraction Layer
Provides a clean interface for GPU monitoring with multiple backend support
"""

import abc
import psutil
from typing import Optional, Dict, Any

class GPUMonitoringBackend(abc.ABC):
    """Abstract base class for GPU monitoring backends"""
    
    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available on the system"""
        pass
    
    @abc.abstractmethod
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """Get GPU information including usage, temperature, memory"""
        pass
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Get the name of this backend"""
        pass

class GPULibBackend(GPUMonitoringBackend):
    """GPU monitoring using GPUtil library"""
    
    def get_name(self) -> str:
        return "GPUtil"
    
    def is_available(self) -> bool:
        try:
            import GPUtil
            return True
        except ImportError:
            return False
    
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                return {
                    'usage': gpu.load * 100,
                    'temperature': gpu.temperature,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal > 0 else 0,
                    'name': gpu.name,
                    'backend': self.get_name()
                }
        except Exception as e:
            print(f"GPUtil backend error: {e}")
        return None

class NVMLBackend(GPUMonitoringBackend):
    """GPU monitoring using NVIDIA ML library"""
    
    def get_name(self) -> str:
        return "NVIDIA-ML"
    
    def is_available(self) -> bool:
        try:
            import nvidia_ml_py3 as nvml
            nvml.nvmlInit()
            return True
        except (ImportError, Exception):
            return False
    
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        try:
            import nvidia_ml_py3 as nvml
            nvml.nvmlInit()
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            
            # Get utilization
            util = nvml.nvmlDeviceGetUtilizationRates(handle)
            usage = util.gpu
            
            # Get temperature
            try:
                temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            except:
                temp = 0
            
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
            
            return {
                'usage': usage,
                'temperature': temp,
                'memory_used': memory_used,
                'memory_total': memory_total,
                'memory_percent': memory_percent,
                'name': name,
                'backend': self.get_name()
            }
        except Exception as e:
            print(f"NVML backend error: {e}")
        return None

class DirectXBackend(GPUMonitoringBackend):
    """GPU monitoring using DirectX (placeholder for future implementation)"""
    
    def get_name(self) -> str:
        return "DirectX"
    
    def is_available(self) -> bool:
        # DirectX implementation would go here
        # For now, return False since we simplified this
        return False
    
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        # DirectX implementation would go here
        return None

class SystemInfoBackend(GPUMonitoringBackend):
    """Fallback backend using system information"""
    
    def get_name(self) -> str:
        return "System Info"
    
    def is_available(self) -> bool:
        return True  # Always available as fallback
    
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        try:
            # Use psutil for basic system info
            # This is a very basic fallback
            return {
                'usage': 0.0,
                'temperature': 0.0,
                'memory_used': 0,
                'memory_total': 0,
                'memory_percent': 0.0,
                'name': 'Unknown GPU',
                'backend': self.get_name()
            }
        except Exception as e:
            print(f"System info backend error: {e}")
            return None

class GPUMonitorAbstraction:
    """Main GPU monitoring abstraction layer"""
    
    def __init__(self):
        self.backends = [
            NVMLBackend(),
            GPULibBackend(),
            DirectXBackend(),
            SystemInfoBackend()  # Always last as fallback
        ]
        self.active_backend = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Find and initialize the best available backend"""
        for backend in self.backends:
            if backend.is_available():
                self.active_backend = backend
                print(f"GPU Monitor: Using {backend.get_name()} backend")
                break
        
        if not self.active_backend:
            print("GPU Monitor: No backend available")
    
    def get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """Get GPU information using the active backend"""
        if not self.active_backend:
            return None
        
        try:
            info = self.active_backend.get_gpu_info()
            if info:
                return info
            else:
                print(f"GPU Monitor: {self.active_backend.get_name()} backend failed, trying next")
                return self._try_next_backend()
        except Exception as e:
            print(f"GPU Monitor: {self.active_backend.get_name()} backend error: {e}")
            return self._try_next_backend()
    
    def _try_next_backend(self) -> Optional[Dict[str, Any]]:
        """Try the next available backend"""
        current_index = self.backends.index(self.active_backend) if self.active_backend else -1
        
        for i in range(current_index + 1, len(self.backends)):
            backend = self.backends[i]
            if backend.is_available():
                self.active_backend = backend
                print(f"GPU Monitor: Switched to {backend.get_name()} backend")
                return backend.get_gpu_info()
        
        print("GPU Monitor: All backends failed")
        return None
    
    def get_gpu_usage(self) -> Optional[float]:
        """Get just the GPU usage percentage"""
        info = self.get_gpu_info()
        return info.get('usage') if info else None
    
    def get_gpu_temperature(self) -> Optional[float]:
        """Get just the GPU temperature"""
        info = self.get_gpu_info()
        return info.get('temperature') if info else None
    
    def get_gpu_memory_percent(self) -> Optional[float]:
        """Get just the GPU memory usage percentage"""
        info = self.get_gpu_info()
        return info.get('memory_percent') if info else None
    
    def get_backend_name(self) -> str:
        """Get the name of the active backend"""
        return self.active_backend.get_name() if self.active_backend else "None"

# Singleton instance for easy use
_gpu_monitor = None

def get_gpu_monitor() -> GPUMonitorAbstraction:
    """Get the singleton GPU monitor instance"""
    global _gpu_monitor
    if _gpu_monitor is None:
        _gpu_monitor = GPUMonitorAbstraction()
    return _gpu_monitor

def get_gpu_usage() -> Optional[float]:
    """Convenience function to get GPU usage"""
    return get_gpu_monitor().get_gpu_usage()

def get_gpu_info() -> Optional[Dict[str, Any]]:
    """Convenience function to get full GPU info"""
    return get_gpu_monitor().get_gpu_info()
