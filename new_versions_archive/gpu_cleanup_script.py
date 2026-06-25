#!/usr/bin/env python3
"""
GPU Cleanup Script for Windows
A comprehensive script to monitor GPU usage, clean VRAM, and manage GPU processes for gaming sessions.
"""

import os
import sys
import subprocess
import psutil
import time
import gc
import platform
import json
from datetime import datetime

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("[WARNING]  GPUtil not installed. GPU monitoring will be limited.")

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class GPUCleaner:
    def __init__(self):
        self.system = platform.system()
        self.initial_gpu_info = self.get_gpu_info()
        
    def get_gpu_info(self):
        """Get current GPU information"""
        gpu_info = []
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_info.append({
                        'id': gpu.id,
                        'name': gpu.name,
                        'memory_total': gpu.memoryTotal,
                        'memory_used': gpu.memoryUsed,
                        'memory_free': gpu.memoryFree,
                        'memory_percent': gpu.memoryUtil * 100,
                        'load': gpu.load * 100,
                        'temperature': gpu.temperature
                    })
            except Exception as e:
                print(f"[WARNING]  Error getting GPU info with GPUtil: {e}")
        
        # Fallback to WMI if GPUtil fails
        if not gpu_info and WMI_AVAILABLE and self.system == "Windows":
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    gpu_info.append({
                        'name': gpu.Name,
                        'adapter_ram': gpu.AdapterRAM,
                        'driver_version': gpu.DriverVersion
                    })
            except Exception as e:
                print(f"[WARNING]  Error getting GPU info with WMI: {e}")
        
        return gpu_info
    
    def print_gpu_info(self, label="Current"):
        """Print GPU information"""
        gpu_info = self.get_gpu_info()
        
        if not gpu_info:
            print(f"\n{label} GPU Status: No GPU information available")
            return
        
        print(f"\n{label} GPU Status:")
        for i, gpu in enumerate(gpu_info):
            print(f"GPU {i}: {gpu.get('name', 'Unknown')}")
            
            if 'memory_total' in gpu:
                print(f"  VRAM: {gpu['memory_used']:.0f}MB / {gpu['memory_total']:.0f}MB ({gpu['memory_percent']:.1f}%)")
                print(f"  Load: {gpu['load']:.1f}%")
                if gpu.get('temperature'):
                    print(f"  Temperature: {gpu['temperature']:.0f}°C")
            elif 'adapter_ram' in gpu:
                total_mb = gpu['adapter_ram'] / (1024 * 1024) if gpu['adapter_ram'] else 0
                print(f"  Adapter RAM: {total_mb:.0f}MB")
                print(f"  Driver Version: {gpu.get('driver_version', 'Unknown')}")
    
    def clear_gpu_processes(self):
        """Close GPU-intensive processes to free up VRAM"""
        print("[CLEAN] Closing GPU-intensive processes...")
        
        # List of GPU-intensive processes that are generally safe to close
        gpu_intensive = [
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe',
            'obs.exe', 'streamlabs.exe', 'xsplit.exe',
            'blender.exe', 'photoshop.exe', 'premiere.exe', 'afterfx.exe',
            'dota2.exe', 'csgo.exe', 'valorant.exe', 'league of legends.exe'
        ]
        
        closed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                process_name = proc.info['name'].lower()
                if any(gpu_proc in process_name for gpu_proc in gpu_intensive):
                    # Check if process is actually using significant resources
                    memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    cpu_usage = proc.info['cpu_percent']
                    
                    if memory_mb > 100 or cpu_usage > 5:  # Only close processes using >100MB RAM or >5% CPU
                        proc.terminate()
                        closed_processes.append(f"{process_name} ({memory_mb:.0f}MB, {cpu_usage:.0f}% CPU)")
                        print(f"  Closed: {process_name} - {memory_mb:.0f}MB RAM, {cpu_usage:.0f}% CPU")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        print(f"[OK] Closed {len(closed_processes)} GPU-intensive processes")
        return closed_processes
    
    def clear_gpu_cache(self):
        """Clear GPU cache and reset GPU state"""
        if self.system != "Windows":
            print("[WARNING]  GPU cache clearing only works on Windows")
            return
        
        print("[CLEAN] Clearing GPU cache...")
        
        try:
            # Clear DirectX shader cache
            shader_cache_paths = [
                os.path.expandvars(r'%LOCALAPPDATA%\D3DSCache'),
                os.path.expandvars(r'%LOCALAPPDATA%\NVIDIA\DXCache'),
                os.path.expandvars(r'%LOCALAPPDATA%\AMD\DxCache'),
                os.path.expandvars(r'%PROGRAMDATA%\NVIDIA Corporation\Downloader'),
            ]
            
            cleared_files = 0
            for cache_path in shader_cache_paths:
                if os.path.exists(cache_path):
                    try:
                        for item in os.listdir(cache_path):
                            item_path = os.path.join(cache_path, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.unlink(item_path)
                                    cleared_files += 1
                                elif os.path.isdir(item_path):
                                    import shutil
                                    shutil.rmtree(item_path, ignore_errors=True)
                                    cleared_files += 1
                            except (PermissionError, OSError):
                                continue
                    except (PermissionError, OSError):
                        continue
            
            print(f"[OK] Cleared {cleared_files} shader cache files")
            
            # Reset GPU using PowerShell (NVIDIA)
            try:
                subprocess.run(['powershell', '-Command', 
                              'Get-Process -Name "nvidia*" -ErrorAction SilentlyContinue | Stop-Process -Force'], 
                              capture_output=True)
                print("[OK] NVIDIA processes reset")
            except:
                pass
            
        except Exception as e:
            print(f"[WARNING]  GPU cache clearing error: {e}")
    
    def optimize_gpu_settings(self):
        """Optimize GPU settings for gaming"""
        if self.system != "Windows":
            print("[WARNING]  GPU optimization only works on Windows")
            return
        
        print("[CLEAN] Optimizing GPU settings...")
        
        try:
            # Set power plan to High Performance
            subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], 
                          capture_output=True, check=True)
            print("[OK] Power plan set to High Performance")
            
            # Disable Windows Game DVR (can impact GPU performance)
            try:
                subprocess.run(['powershell', '-Command', 
                              'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" -Name "AllowGameDVR" -Value 0 -Force'], 
                              capture_output=True)
                print("[OK] Game DVR disabled")
            except:
                pass
            
            # Clear GPU work queues
            if WMI_AVAILABLE:
                try:
                    c = wmi.WMI()
                    for gpu in c.Win32_VideoController():
                        print(f"[OK] Reset GPU: {gpu.Name}")
                except:
                    pass
            
        except Exception as e:
            print(f"[WARNING]  GPU optimization error: {e}")
    
    def monitor_gpu_temperature(self):
        """Monitor GPU temperature and provide warnings"""
        gpu_info = self.get_gpu_info()
        
        for gpu in gpu_info:
            if gpu.get('temperature'):
                temp = gpu['temperature']
                if temp > 85:
                    print(f"[FIRE] WARNING: GPU {gpu['name']} is running hot at {temp}°C!")
                    print("  Consider checking cooling or reducing workload")
                elif temp > 75:
                    print(f"[WARNING]  GPU {gpu['name']} is warm at {temp}°C")
                else:
                    print(f"[OK] GPU {gpu['name']} temperature is normal at {temp}°C")
    
    def run_full_cleanup(self):
        """Run complete GPU cleanup process"""
        print("=" * 50)
        print("[ROCKET] Starting GPU Cleanup Process")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Show initial GPU state
        self.print_gpu_info("Initial")
        self.monitor_gpu_temperature()
        
        # Run cleanup steps
        self.clear_gpu_processes()
        self.clear_gpu_cache()
        self.optimize_gpu_settings()
        
        # Wait a moment for changes to take effect
        time.sleep(3)
        
        # Show final GPU state
        self.print_gpu_info("Final")
        self.monitor_gpu_temperature()
        
        # Calculate improvement
        initial_vram = 0
        final_vram = 0
        
        if self.initial_gpu_info and 'memory_percent' in self.initial_gpu_info[0]:
            initial_vram = self.initial_gpu_info[0]['memory_percent']
        
        final_gpu_info = self.get_gpu_info()
        if final_gpu_info and 'memory_percent' in final_gpu_info[0]:
            final_vram = final_gpu_info[0]['memory_percent']
        
        if initial_vram > 0 and final_vram > 0:
            improvement = initial_vram - final_vram
            print(f"\n[CHART] VRAM Usage Improvement: {improvement:.1f}%")
        
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        if initial_vram > final_vram:
            print("🎉 GPU cleanup successful!")
        else:
            print("ℹ️  No significant GPU improvement detected")

def main():
    """Main function"""
    print("[CLEAN] GPU Cleanup Script")
    print("This script will clean up GPU resources for better gaming performance")
    
    # Check if running as administrator (recommended for Windows)
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[WARNING]  Warning: Running without administrator privileges")
                print("Some GPU cleanup operations may not work properly.")
                print("Consider running as administrator for best results.")
        except:
            pass
    
    # Check for GPU monitoring libraries
    if not GPU_AVAILABLE and not WMI_AVAILABLE:
        print("[WARNING]  Limited GPU monitoring capabilities.")
        print("Install GPUtil for better GPU monitoring: pip install GPUtil")
        print("Install WMI for Windows GPU info: pip install WMI")
    
    cleaner = GPUCleaner()
    
    try:
        cleaner.run_full_cleanup()
    except KeyboardInterrupt:
        print("\n[WARNING]  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
