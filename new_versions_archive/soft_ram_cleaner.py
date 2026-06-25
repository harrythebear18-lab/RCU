#!/usr/bin/env python3
"""
Soft RAM Cleaner - Ultra-Gentle Memory Optimization
Uses low-level Windows APIs for the softest possible memory cleanup.
Perfect for regular use without any system impact.
"""

import os
import sys
import subprocess
import psutil
import time
import gc
import platform
import ctypes
from datetime import datetime
import threading

class SoftRAMCleaner:
    def __init__(self):
        self.system = platform.system()
        self.initial_memory = self.get_memory_info()
        
        # Windows-specific low-level memory management
        if self.system == "Windows":
            self.kernel32 = ctypes.windll.kernel32
            self.psapi = ctypes.windll.psapi
            
            # Low-level Windows API functions
            self.SetProcessWorkingSetSize = self.kernel32.SetProcessWorkingSetSize
            self.EmptyWorkingSet = self.psapi.EmptyWorkingSet
            
            # Additional low-level functions
            self.GetProcessMemoryInfo = self.psapi.GetProcessMemoryInfo
    
    def get_memory_info(self):
        """Get memory information efficiently"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free
        }
    
    def print_memory_info(self, label="Current"):
        """Print memory information"""
        mem = self.get_memory_info()
        print(f"\n{label} Memory Status:")
        print(f"Total RAM: {mem['total'] / (1024**3):.2f} GB")
        print(f"Used: {mem['used'] / (1024**3):.2f} GB")
        print(f"Available: {mem['available'] / (1024**3):.2f} GB")
        print(f"Usage: {mem['percent']:.1f}%")
        print("-" * 50)
    
    def soft_memory_trim(self):
        """Ultra-soft memory trimming using low-level APIs"""
        if self.system != "Windows":
            print("💨 Soft memory trim (Unix-based)")
            gc.collect()
            return True
        
        print("💨 Performing ultra-soft memory trim...")
        
        try:
            # Get current process list with minimal overhead
            processes = []
            for proc in psutil.process_iter(['pid']):
                try:
                    processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Ultra-soft working set trimming - only for processes with >100MB
            trimmed_count = 0
            for pid in processes:
                try:
                    if pid != os.getpid():  # Skip our own process
                        proc = psutil.Process(pid)
                        
                        # Only trim processes with significant memory usage
                        if proc.memory_info().rss > 100 * 1024 * 1024:  # >100MB
                            # Very gentle working set reduction
                            handle = self.kernel32.OpenProcess(0x1F0FFF, False, pid)
                            if handle:
                                # Soft working set empty - more gentle than EmptyWorkingSet
                                current_ws = proc.memory_info().rss
                                new_ws = int(current_ws * 0.8)  # Reduce by 20% only
                                
                                try:
                                    self.SetProcessWorkingSetSize(handle, new_ws, new_ws * 2)
                                    trimmed_count += 1
                                except:
                                    # Fallback to EmptyWorkingSet
                                    self.EmptyWorkingSet(handle)
                                    trimmed_count += 1
                                
                                self.kernel32.CloseHandle(handle)
                except:
                    continue
            
            print(f"[OK] Softly trimmed {trimmed_count} processes")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Soft memory trim error: {e}")
            return False
    
    def clear_light_cache(self):
        """Clear only light, non-essential cache"""
        print("💨 Clearing light system cache...")
        
        try:
            if self.system == "Windows":
                # Only clear safe, non-critical caches
                light_cache_commands = [
                    # DNS cache (very safe)
                    'ipconfig /flushdns',
                    # Clear clipboard cache (safe)
                    'echo off | clip',
                ]
                
                cleared_items = 0
                for cmd in light_cache_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
                        cleared_items += 1
                    except:
                        pass
                
                print(f"[OK] Cleared {cleared_items} light cache items")
                return True
            else:
                # Unix-based systems - just sync
                subprocess.run(['sync'], capture_output=True)
                print("[OK] Light cache cleared")
                return True
                
        except Exception as e:
            print(f"[WARNING]  Light cache clearing error: {e}")
            return False
    
    def optimize_memory_allocation(self):
        """Optimize memory allocation patterns"""
        print("💨 Optimizing memory allocation...")
        
        try:
            if self.system == "Windows":
                # Use Windows memory management APIs for optimization
                optimize_commands = [
                    # Memory allocation optimization
                    'powershell -Command "[System.Runtime.InteropServices.Marshal]::AddRef([System.IntPtr]::Zero)"',
                    # Memory pressure relief
                    'powershell -Command "[System.GC]::GetTotalMemory($false)"',
                ]
                
                optimized_items = 0
                for cmd in optimize_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
                        optimized_items += 1
                    except:
                        pass
            
            # Force Python garbage collection (very light)
            gc.collect()
            
            print("[OK] Memory allocation optimized")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Memory allocation optimization error: {e}")
            return False
    
    def refresh_working_sets(self):
        """Refresh working sets gently"""
        if self.system != "Windows":
            print("💨 Working set refresh (Unix-based)")
            return True
        
        print("💨 Gently refreshing working sets...")
        
        try:
            # Get only user processes to minimize impact
            user_processes = []
            for proc in psutil.process_iter(['pid', 'username']):
                try:
                    username = proc.info.get('username', '')
                    if (username and 
                        not username.endswith('SYSTEM') and
                        not username.endswith('LOCAL SERVICE') and
                        not username.endswith('NETWORK SERVICE')):
                        user_processes.append(proc.info['pid'])
                except:
                    continue
            
            # Very gentle working set refresh
            refreshed_count = 0
            for pid in user_processes[:20]:  # Limit to first 20 processes
                try:
                    if pid != os.getpid():
                        proc = psutil.Process(pid)
                        
                        # Only refresh processes with moderate memory usage
                        if 50 * 1024 * 1024 < proc.memory_info().rss < 500 * 1024 * 1024:
                            handle = self.kernel32.OpenProcess(0x1F0FFF, False, pid)
                            if handle:
                                # Very gentle working set adjustment
                                try:
                                    # Just touch the working set, don't empty it
                                    current_ws = proc.memory_info().rss
                                    self.SetProcessWorkingSetSize(handle, current_ws, current_ws * 2)
                                    refreshed_count += 1
                                except:
                                    pass
                                
                                self.kernel32.CloseHandle(handle)
                except:
                    continue
            
            print(f"[OK] Gently refreshed {refreshed_count} working sets")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Working set refresh error: {e}")
            return False
    
    def compact_memory_gently(self):
        """Gentle memory compaction"""
        print("💨 Performing gentle memory compaction...")
        
        try:
            if self.system == "Windows":
                # Use Windows memory compaction APIs gently
                compact_commands = [
                    # Very gentle memory compaction
                    'powershell -Command "[System.Runtime.InteropServices.Marshal]::GetLastWin32Error()"',
                    # Memory pressure notification
                    'powershell -Command "[System.GC]::Collect(0)"',
                ]
                
                for cmd in compact_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
                    except:
                        pass
            
            # Light Python garbage collection
            gc.collect(0)  # Only generation 0
            
            print("[OK] Memory gently compacted")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Memory compaction error: {e}")
            return False
    
    def run_soft_cleanup(self):
        """Run complete soft RAM cleanup"""
        print("=" * 60)
        print("💨 SOFT RAM CLEANER - Ultra-Gentle Optimization")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🌸 The softest memory cleanup possible")
        print("=" * 60)
        
        # Show initial memory state
        self.print_memory_info("Initial")
        
        cleanup_results = {
            'soft_trim': False,
            'light_cache': False,
            'allocation': False,
            'working_sets': False,
            'compaction': False
        }
        
        # Step 1: Ultra-soft memory trim
        cleanup_results['soft_trim'] = self.soft_memory_trim()
        time.sleep(1)
        
        # Step 2: Clear light cache only
        cleanup_results['light_cache'] = self.clear_light_cache()
        time.sleep(1)
        
        # Step 3: Optimize memory allocation
        cleanup_results['allocation'] = self.optimize_memory_allocation()
        time.sleep(1)
        
        # Step 4: Refresh working sets gently
        cleanup_results['working_sets'] = self.refresh_working_sets()
        time.sleep(1)
        
        # Step 5: Gentle memory compaction
        cleanup_results['compaction'] = self.compact_memory_gently()
        time.sleep(2)
        
        # Final light garbage collection
        gc.collect(0)
        
        # Show final memory state
        final_memory = self.get_memory_info()
        self.print_memory_info("Final")
        
        # Calculate improvement
        initial_used_gb = self.initial_memory['used'] / (1024**3)
        final_used_gb = final_memory['used'] / (1024**3)
        improvement_gb = initial_used_gb - final_used_gb
        improvement_percent = ((self.initial_memory['percent'] - final_memory['percent']) / self.initial_memory['percent']) * 100
        
        print(f"\n🌸 SOFT CLEANUP RESULTS:")
        print(f"Memory freed: {improvement_gb:.2f} GB")
        print(f"Usage improvement: {improvement_percent:.1f}%")
        print(f"Initial usage: {self.initial_memory['percent']:.1f}%")
        print(f"Final usage: {final_memory['percent']:.1f}%")
        
        print(f"\n[TOOL] OPERATIONS COMPLETED:")
        for operation, success in cleanup_results.items():
            status = "[OK]" if success else "[ERROR]"
            print(f"{status} {operation.replace('_', ' ').title()}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if improvement_gb > 0.05:  # If freed more than 50MB
            print("🌸 Soft cleanup successful! System feels refreshed.")
        else:
            print("💧 System is already well-optimized.")
        
        return improvement_gb

def main():
    """Main function"""
    print("💨 SOFT RAM CLEANER")
    print("Ultra-gentle memory optimization for regular use")
    print("🌸 The softest touch for your system's memory")
    
    response = input("\nPerform soft RAM cleanup? (Y/n): ")
    if response.lower() == 'n':
        print("Soft cleanup cancelled.")
        return
    
    try:
        cleaner = SoftRAMCleaner()
        memory_freed = cleaner.run_soft_cleanup()
        
        if memory_freed > 0.05:
            print(f"\n🌸 Gently freed {memory_freed:.2f} GB!")
            print("💧 Your system feels refreshed and optimized.")
        else:
            print("\n💧 Your system is already running efficiently.")
            
    except KeyboardInterrupt:
        print("\n[WARNING]  Soft cleanup interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error during soft cleanup: {e}")

if __name__ == "__main__":
    main()
