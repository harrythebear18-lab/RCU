#!/usr/bin/env python3
"""
Debug GPU GUI issues
"""

import sys
import os
import subprocess

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gpu_info_in_gui_context():
    """Test GPU info retrieval in GUI-like context"""
    print("Testing GPU info retrieval...")
    
    gpu_info = {
        'name': 'Unknown',
        'usage': 0,
        'memory_used': 0,
        'memory_total': 0,
        'memory_percent': 0,
        'temperature': 0
    }
    
    # Simulate WMI detection
    try:
        import wmi
        c = wmi.WMI()
        gpus = c.Win32_VideoController()
        if len(gpus) > 1:
            gpu = gpus[1]  # NVIDIA GPU is usually second
            gpu_info['name'] = gpu.Name
            print(f"WMI detected: {gpu.Name}")
    except Exception as e:
        print(f"WMI error: {e}")
    
    # Test nvidia-smi
    if 'NVIDIA' in gpu_info.get('name', '').upper():
        print("Testing nvidia-smi integration...")
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"nvidia-smi return code: {result.returncode}")
            print(f"nvidia-smi stdout: {result.stdout}")
            print(f"nvidia-smi stderr: {result.stderr}")
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 0:
                    values = lines[0].split(', ')
                    print(f"Parsed values: {values}")
                    if len(values) >= 4:
                        gpu_info['memory_total'] = float(values[0])
                        gpu_info['memory_used'] = float(values[1])
                        gpu_info['usage'] = float(values[2])
                        gpu_info['temperature'] = float(values[3])
                        gpu_info['memory_percent'] = (gpu_info['memory_used'] / gpu_info['memory_total']) * 100
        except Exception as e:
            print(f"nvidia-smi error: {e}")
    
    print(f"Final GPU info: {gpu_info}")
    return gpu_info

if __name__ == "__main__":
    test_gpu_info_in_gui_context()
