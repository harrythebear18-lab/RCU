#!/usr/bin/env python3
"""
CPU Cleanup Script for Windows
A comprehensive script to monitor CPU usage, optimize processes, and manage CPU resources for gaming sessions.
"""

import os
import sys
import subprocess
import psutil
import time
import gc
import platform
import threading
from datetime import datetime

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class CPUCleaner:
    def __init__(self):
        self.system = platform.system()
        self.initial_cpu_info = self.get_cpu_info()
        self.cpu_count = psutil.cpu_count(logical=True)
        self.cpu_physical = psutil.cpu_count(logical=False)
        
    def get_cpu_info(self):
        """Get current CPU information"""
        cpu_info = {
            'usage_percent': psutil.cpu_percent(interval=1),
            'freq_current': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'freq_min': psutil.cpu_freq().min if psutil.cpu_freq() else 0,
            'freq_max': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
            'per_cpu': psutil.cpu_percent(interval=1, percpu=True)
        }
        
        # Add temperature info if available
        if WMI_AVAILABLE and self.system == "Windows":
            try:
                c = wmi.WMI()
                temps = c.Win32_TemperatureProbe()
                if temps:
                    cpu_info['temperature'] = temps[0].CurrentTemperature
            except:
                pass
        
        return cpu_info
    
    def print_cpu_info(self, label="Current"):
        """Print CPU information"""
        cpu_info = self.get_cpu_info()
        
        print(f"\n{label} CPU Status:")
        print(f"Usage: {cpu_info['usage_percent']:.1f}%")
        print(f"Cores: {self.cpu_physical} physical, {self.cpu_count} logical")
        
        if cpu_info['freq_current'] > 0:
            print(f"Frequency: {cpu_info['freq_current']:.0f} MHz (min: {cpu_info['freq_min']:.0f}, max: {cpu_info['freq_max']:.0f})")
        
        if cpu_info.get('temperature'):
            temp_celsius = cpu_info['temperature'] - 273.15  # Convert from Kelvin to Celsius
            print(f"Temperature: {temp_celsius:.1f}°C")
        
        print("Per-core usage:")
        for i, usage in enumerate(cpu_info['per_cpu']):
            print(f"  Core {i}: {usage:.1f}%")
    
    def get_cpu_intensive_processes(self, min_cpu=5):
        """Get list of CPU-intensive processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username']):
            try:
                cpu_usage = proc.info['cpu_percent'] or 0
                memory_info = proc.info.get('memory_info')
                
                if cpu_usage > min_cpu and memory_info:  # Only include processes using >min_cpu% CPU
                    memory_mb = memory_info.rss / (1024 * 1024)
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': cpu_usage,
                        'memory_mb': memory_mb,
                        'username': proc.info.get('username', 'Unknown') or 'Unknown'
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                continue
        
        # Sort by CPU usage (highest first)
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes
    
    def print_top_processes(self, limit=10):
        """Print top CPU-consuming processes"""
        processes = self.get_cpu_intensive_processes()
        
        print(f"\nTop {limit} CPU-consuming processes:")
        if processes:
            print(f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory':<10} {'User':<15}")
            print("-" * 70)
            
            for i, proc in enumerate(processes[:limit]):
                print(f"{proc['pid']:<8} {proc['name'][:19]:<20} {proc['cpu_percent']:<8.1f} {proc['memory_mb']:<10.1f} {proc['username'][:14]:<15}")
        else:
            print("No significant CPU-consuming processes found.")
    
    def close_cpu_intensive_processes(self):
        """Close CPU-intensive processes that are safe to terminate"""
        print("[CLEAN] Closing CPU-intensive processes...")
        
        # List of processes that are generally safe to close
        safe_to_close = [
            'notepad.exe', 'mspaint.exe', 'calc.exe', 'wordpad.exe',
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe',
            'steam.exe', 'epicgameslauncher.exe', 'origin.exe', 'uplay.exe',
            'onedrive.exe', 'googledrivesync.exe', 'dropbox.exe',
            'update.exe', 'installer.exe', 'setup.exe'
        ]
        
        processes = self.get_cpu_intensive_processes()
        closed_processes = []
        
        for proc in processes:
            process_name = proc['name'].lower()
            
            # Check if process is safe to close
            if any(safe_proc in process_name for safe_proc in safe_to_close):
                try:
                    # Don't close system processes or processes using too much memory (might be important)
                    if proc['memory_mb'] < 1000 and proc['cpu_percent'] > 10:  # <1GB RAM and >10% CPU
                        process = psutil.Process(proc['pid'])
                        process.terminate()
                        closed_processes.append(f"{proc['name']} (PID: {proc['pid']}, CPU: {proc['cpu_percent']:.1f}%)")
                        print(f"  Closed: {proc['name']} - CPU: {proc['cpu_percent']:.1f}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        print(f"[OK] Closed {len(closed_processes)} CPU-intensive processes")
        return closed_processes
    
    def optimize_cpu_priority(self):
        """Adjust process priorities for better gaming performance"""
        print("[CLEAN] Optimizing CPU priorities...")
        
        # Lower priority of background processes
        background_processes = [
            'svchost.exe', 'services.exe', 'lsass.exe', 'csrss.exe',
            'wininit.exe', 'winlogon.exe', 'explorer.exe'
        ]
        
        adjusted_processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name'].lower()
                if any(bg_proc in process_name for bg_proc in background_processes):
                    process = psutil.Process(proc.info['pid'])
                    # Set to below normal priority (Windows)
                    if self.system == "Windows":
                        process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                        adjusted_processes.append(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"[OK] Adjusted priority for {len(adjusted_processes)} background processes")
        return adjusted_processes
    
    def clear_cpu_cache(self):
        """Clear CPU cache and optimize performance"""
        print("[CLEAN] Clearing CPU cache...")
        
        if self.system == "Windows":
            try:
                # Clear system cache
                subprocess.run(['powershell', '-Command', 
                              'Clear-Content -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" -ErrorAction SilentlyContinue'], 
                              capture_output=True)
                
                # Optimize CPU scheduling
                subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], 
                              capture_output=True, check=True)
                
                print("[OK] CPU cache cleared and power optimized")
            except Exception as e:
                print(f"[WARNING]  CPU cache clearing error: {e}")
        else:
            print("[WARNING]  CPU cache clearing only works on Windows")
    
    def monitor_cpu_temperature(self):
        """Monitor CPU temperature and provide warnings"""
        cpu_info = self.get_cpu_info()
        
        if cpu_info.get('temperature'):
            temp_celsius = cpu_info['temperature'] - 273.15
            if temp_celsius > 80:
                print(f"[FIRE] WARNING: CPU is running hot at {temp_celsius:.1f}°C!")
                print("  Consider checking cooling or reducing workload")
            elif temp_celsius > 70:
                print(f"[WARNING]  CPU is warm at {temp_celsius:.1f}°C")
            else:
                print(f"[OK] CPU temperature is normal at {temp_celsius:.1f}°C")
        else:
            print("ℹ️  CPU temperature monitoring not available")
    
    def set_gaming_mode(self):
        """Optimize system for gaming"""
        print("[GAME] Setting up gaming mode...")
        
        if self.system == "Windows":
            try:
                # Set power plan to Ultimate Performance (if available) or High Performance
                try:
                    subprocess.run(['powercfg', '/setactive', 'e9a42b02-d5df-448d-aa00-03f14749eb61'], 
                                  capture_output=True, check=True)  # Ultimate Performance
                    print("[OK] Power plan set to Ultimate Performance")
                except:
                    subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], 
                                  capture_output=True, check=True)  # High Performance
                    print("[OK] Power plan set to High Performance")
                
                # Disable Windows Update service temporarily
                try:
                    subprocess.run(['sc', 'stop', 'wuauserv'], capture_output=True)
                    print("[OK] Windows Update service stopped")
                except:
                    pass
                
                # Disable indexing service
                try:
                    subprocess.run(['sc', 'stop', 'wsearch'], capture_output=True)
                    print("[OK] Windows Search service stopped")
                except:
                    pass
                
            except Exception as e:
                print(f"[WARNING]  Gaming mode setup error: {e}")
    
    def run_full_cleanup(self):
        """Run complete CPU cleanup process"""
        print("=" * 50)
        print("[ROCKET] Starting CPU Cleanup Process")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Show initial CPU state
        self.print_cpu_info("Initial")
        self.print_top_processes()
        self.monitor_cpu_temperature()
        
        # Run cleanup steps
        self.close_cpu_intensive_processes()
        self.optimize_cpu_priority()
        self.clear_cpu_cache()
        self.set_gaming_mode()
        
        # Wait a moment for changes to take effect
        time.sleep(3)
        
        # Show final CPU state
        self.print_cpu_info("Final")
        self.print_top_processes()
        self.monitor_cpu_temperature()
        
        # Calculate improvement
        initial_usage = self.initial_cpu_info['usage_percent']
        final_usage = self.get_cpu_info()['usage_percent']
        improvement = initial_usage - final_usage
        
        print(f"\n[CHART] CPU Usage Improvement: {improvement:.1f}%")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        if improvement > 0:
            print("🎉 CPU cleanup successful!")
        else:
            print("ℹ️  No significant CPU improvement detected")

def main():
    """Main function"""
    print("[CLEAN] CPU Cleanup Script")
    print("This script will optimize CPU resources for better gaming performance")
    
    # Check if running as administrator (recommended for Windows)
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[WARNING]  Warning: Running without administrator privileges")
                print("Some CPU cleanup operations may not work properly.")
                print("Consider running as administrator for best results.")
        except:
            pass
    
    # Check for WMI availability
    if not WMI_AVAILABLE and platform.system() == "Windows":
        print("[WARNING]  WMI not installed. CPU temperature monitoring will be limited.")
        print("Install WMI for better CPU monitoring: pip install WMI")
    
    cleaner = CPUCleaner()
    
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
