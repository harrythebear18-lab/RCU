#!/usr/bin/env python3
"""
Test GPU monitoring functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import GPUtil
    print("[OK] GPUtil available")
    gpus = GPUtil.getGPUs()
    print(f"   Found {len(gpus)} GPU(s) with GPUtil")
    for i, gpu in enumerate(gpus):
        print(f"   GPU {i}: {gpu.name}")
        print(f"     VRAM: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil*100:.1f}%)")
        print(f"     Usage: {gpu.load*100:.1f}%")
        print(f"     Temp: {gpu.temperature}°C")
except ImportError:
    print("[ERROR] GPUtil not available")
except Exception as e:
    print(f"[ERROR] GPUtil error: {e}")

try:
    import nvidia_ml_py3 as nvml
    nvml.nvmlInit()
    print("[OK] NVML available")
    device_count = nvml.nvmlDeviceGetCount()
    print(f"   Found {device_count} GPU(s) with NVML")
    for i in range(device_count):
        handle = nvml.nvmlDeviceGetHandleByIndex(i)
        name = nvml.nvmlDeviceGetName(handle).decode('utf-8')
        print(f"   GPU {i}: {name}")
        
        # Get memory info
        mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
        print(f"     VRAM: {mem_info.used//1024//1024}MB / {mem_info.total//1024//1024}MB ({mem.info.used/mem_info.total*100:.1f}%)")
        
        # Get utilization
        util = nvml.nvmlDeviceGetUtilizationRates(handle)
        print(f"     Usage: {util.gpu}%")
        
        # Get temperature
        try:
            temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            print(f"     Temp: {temp}°C")
        except:
            print(f"     Temp: N/A")
except ImportError:
    print("[ERROR] NVML not available")
except Exception as e:
    print(f"[ERROR] NVML error: {e}")

try:
    import wmi
    c = wmi.WMI()
    gpus = c.Win32_VideoController()
    print("[OK] WMI available")
    print(f"   Found {len(gpus)} GPU(s) with WMI")
    for i, gpu in enumerate(gpus):
        print(f"   GPU {i}: {gpu.Name}")
        if gpu.AdapterRAM:
            ram_mb = gpu.AdapterRAM / (1024 * 1024)
            print(f"     RAM: {ram_mb:.0f}MB")
except ImportError:
    print("[ERROR] WMI not available")
except Exception as e:
    print(f"[ERROR] WMI error: {e}")
