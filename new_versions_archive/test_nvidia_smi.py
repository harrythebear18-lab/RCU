#!/usr/bin/env python3
"""
Test nvidia-smi integration for GPU monitoring
"""

import subprocess
import sys
import os

def test_nvidia_smi():
    """Test nvidia-smi data retrieval"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"[OK] nvidia-smi working, found {len(lines)} GPU(s)")
            
            for i, line in enumerate(lines):
                values = line.split(', ')
                if len(values) >= 4:
                    memory_total = float(values[0])
                    memory_used = float(values[1])
                    gpu_usage = float(values[2])
                    temperature = float(values[3])
                    memory_percent = (memory_used / memory_total) * 100
                    
                    print(f"GPU {i}:")
                    print(f"  VRAM: {memory_used:.0f}MB / {memory_total:.0f}MB ({memory_percent:.1f}%)")
                    print(f"  Usage: {gpu_usage:.1f}%")
                    print(f"  Temp: {temperature:.0f}°C")
            return True
        else:
            print(f"[ERROR] nvidia-smi failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] nvidia-smi error: {e}")
        return False

if __name__ == "__main__":
    test_nvidia_smi()
