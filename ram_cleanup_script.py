#!/usr/bin/env python3
"""
RAM Cleanup Script for Windows
A comprehensive script to clean up system RAM for gaming sessions and general use.
"""

import os
import sys
import subprocess
import psutil
import time
import gc
import platform
from datetime import datetime

class RAMCleaner:
    def __init__(self):
        self.system = platform.system()
        self.initial_memory = self.get_memory_info()
        
    def get_memory_info(self):
        """Get current memory usage information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
    
    def print_memory_info(self, label="Current"):
        """Print memory information"""
        mem = self.get_memory_info()
        print(f"\n{label} Memory Status:")
        print(f"Total RAM: {mem['total'] / (1024**3):.2f} GB")
        print(f"Available: {mem['available'] / (1024**3):.2f} GB")
        print(f"Used: {mem['used'] / (1024**3):.2f} GB")
        print(f"Usage: {mem['percent']:.1f}%")
    
    def clear_python_memory(self):
        """Force Python garbage collection"""
        print("[CLEAN] Running Python garbage collection...")
        gc.collect()
        print("[OK] Python garbage collection completed")
    
    def clear_windows_cache(self):
        """Clear Windows system cache"""
        if self.system != "Windows":
            print("[WARNING]  Windows cache clearing only works on Windows")
            return
        
        print("[CLEAN] Clearing Windows system cache...")
        
        try:
            # Clear DNS cache
            subprocess.run(['ipconfig', '/flushdns'], check=True, capture_output=True)
            print("[OK] DNS cache cleared")
            
            # Clear Windows temp files
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                r'C:\Windows\Temp',
                r'C:\Windows\Prefetch'
            ]
            
            cleared_files = 0
            for temp_path in temp_paths:
                if os.path.exists(temp_path):
                    try:
                        for item in os.listdir(temp_path):
                            item_path = os.path.join(temp_path, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.unlink(item_path)
                                    cleared_files += 1
                                elif os.path.isdir(item_path):
                                    os.rmdir(item_path)
                                    cleared_files += 1
                            except (PermissionError, OSError):
                                continue
                    except (PermissionError, OSError):
                        continue
            
            print(f"[OK] Cleared {cleared_files} temporary files")
            
        except subprocess.CalledProcessError as e:
            print(f"[WARNING]  Error clearing cache: {e}")
    
    def close_unnecessary_processes(self):
        """Close unnecessary processes to free up RAM"""
        print("[CLEAN] Closing unnecessary processes...")
        
        # List of processes that are generally safe to close
        safe_to_close = [
            'notepad.exe', 'mspaint.exe', 'calc.exe', 'wordpad.exe',
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe',
            'steam.exe', 'epicgameslauncher.exe', 'origin.exe', 'uplay.exe'
        ]
        
        closed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                process_name = proc.info['name'].lower()
                if any(safe_process in process_name for safe_process in safe_to_close):
                    if proc.info['memory_info'].rss < 500 * 1024 * 1024:  # Only close processes using < 500MB
                        proc.terminate()
                        closed_processes.append(process_name)
                        print(f"  Closed: {process_name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        print(f"[OK] Closed {len(closed_processes)} unnecessary processes")
        return closed_processes
    
    def optimize_memory(self):
        """Windows memory optimization commands"""
        if self.system != "Windows":
            print("[WARNING]  Memory optimization only works on Windows")
            return
        
        print("[CLEAN] Running memory optimization...")
        
        try:
            # Clear standby memory
            subprocess.run(['powershell', '-Command', 
                          'Clear-Content -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" -ErrorAction SilentlyContinue'], 
                          capture_output=True)
            
            # Free up memory using Windows API
            subprocess.run(['powershell', '-Command', 
                          '[System.Runtime.InteropServices.Marshal]::FreeHGlobal([System.IntPtr]::Zero)'], 
                          capture_output=True)
            
            print("[OK] Memory optimization completed")
            
        except Exception as e:
            print(f"[WARNING]  Memory optimization error: {e}")
    
    def run_full_cleanup(self):
        """Run complete RAM cleanup process"""
        print("=" * 50)
        print("[ROCKET] Starting RAM Cleanup Process")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Show initial memory state
        self.print_memory_info("Initial")
        
        # Run cleanup steps
        self.clear_python_memory()
        self.clear_windows_cache()
        self.close_unnecessary_processes()
        self.optimize_memory()
        
        # Wait a moment for changes to take effect
        time.sleep(2)
        
        # Show final memory state
        self.print_memory_info("Final")
        
        # Calculate improvement
        initial_percent = self.initial_memory['percent']
        final_percent = self.get_memory_info()['percent']
        improvement = initial_percent - final_percent
        
        print(f"\n[CHART] Memory Usage Improvement: {improvement:.1f}%")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        if improvement > 0:
            print("🎉 RAM cleanup successful!")
        else:
            print("ℹ️  No significant memory improvement detected")

def main():
    """Main function"""
    print("[CLEAN] RAM Cleanup Script")
    print("This script will clean up system RAM for better gaming performance")
    
    # Check if running as administrator (recommended for Windows)
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[WARNING]  Warning: Running without administrator privileges")
                print("Some cleanup operations may not work properly.")
                print("Consider running as administrator for best results.")
        except:
            pass
    
    cleaner = RAMCleaner()
    
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
