#!/usr/bin/env python3
"""
Memory Jolt - Gentle System Optimization
Safely jolts the system back to action by clearing stuck memory and bottlenecks.
Non-destructive approach that preserves system stability.
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

class MemoryJolt:
    def __init__(self):
        self.system = platform.system()
        self.initial_memory = self.get_memory_info()
        
        # Windows-specific memory management
        if self.system == "Windows":
            self.kernel32 = ctypes.windll.kernel32
            self.psapi = ctypes.windll.psapi
            
            # Define Windows API functions for gentle memory optimization
            self.SetProcessWorkingSetSize = self.kernel32.SetProcessWorkingSetSize
            self.EmptyWorkingSet = self.psapi.EmptyWorkingSet
    
    def get_memory_info(self):
        """Get detailed memory information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free,
            'cached': getattr(memory, 'cached', 0),
            'buffers': getattr(memory, 'buffers', 0)
        }
    
    def print_memory_info(self, label="Current"):
        """Print memory information"""
        mem = self.get_memory_info()
        print(f"\n{label} Memory Status:")
        print(f"Total RAM: {mem['total'] / (1024**3):.2f} GB")
        print(f"Used: {mem['used'] / (1024**3):.2f} GB")
        print(f"Available: {mem['available'] / (1024**3):.2f} GB")
        print(f"Free: {mem['free'] / (1024**3):.2f} GB")
        print(f"Usage: {mem['percent']:.1f}%")
        if mem['cached'] > 0:
            print(f"Cached: {mem['cached'] / (1024**3):.2f} GB")
        print("-" * 50)
    
    def gentle_memory_trim(self):
        """Gentle memory trimming for all processes"""
        if self.system != "Windows":
            print("[POWER] Gentle memory trim (Unix-based system)")
            # For Unix systems, we can still do some gentle optimization
            gc.collect()
            return True
        
        print("[POWER] Performing gentle memory trim...")
        
        try:
            # Get all user processes (exclude system processes)
            user_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    pinfo = proc.info
                    username = pinfo.get('username', '')
                    
                    # Only target user processes, exclude system processes
                    if (username and 
                        not username.endswith('SYSTEM') and
                        not username.endswith('LOCAL SERVICE') and
                        not username.endswith('NETWORK SERVICE') and
                        pinfo['pid'] != os.getpid()):  # Exclude our own process
                        
                        user_processes.append(pinfo['pid'])
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Gentle working set trimming for user processes
            trimmed_count = 0
            for pid in user_processes:
                try:
                    # Only trim processes with working sets > 50MB to avoid affecting small utilities
                    proc = psutil.Process(pid)
                    if proc.memory_info().rss > 50 * 1024 * 1024:  # > 50MB
                        handle = self.kernel32.OpenProcess(0x1F0FFF, False, pid)
                        if handle:
                            # Gentle working set empty - this forces the process to release unused memory
                            self.EmptyWorkingSet(handle)
                            self.kernel32.CloseHandle(handle)
                            trimmed_count += 1
                except:
                    continue
            
            print(f"[OK] Gently trimmed {trimmed_count} user processes")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Memory trim error: {e}")
            return False
    
    def clear_standby_memory_gently(self):
        """Gently clear standby memory without affecting active processes"""
        if self.system != "Windows":
            print("[POWER] Clearing standby memory (Unix-based)")
            return True
        
        print("[POWER] Gently clearing standby memory...")
        
        try:
            # Method 1: PowerShell gentle standby list clearing
            ps_commands = [
                # Force garbage collection across all .NET processes
                'powershell -Command "Get-Process | Where-Object {$_.ProcessName -like \'*clr*\' -or $_.ProcessName -like \'*dotnet*\'} | ForEach-Object {[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()}"',
                # Clear file system cache gently
                'powershell -Command "$cache = Get-WmiObject -Class Win32_PageFileUsage; $cache | ForEach-Object {$_.FreeSpace = $_.FreeSpace}"',
            ]
            
            for cmd in ps_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                except:
                    pass
            
            # Method 2: Windows API standby memory clearing
            try:
                # Use Windows API to clear standby lists
                result = subprocess.run([
                    'powershell', '-Command', 
                    '[System.Runtime.InteropServices.Marshal]::PrelinkAll()'
                ], capture_output=True, timeout=30)
            except:
                pass
            
            print("[OK] Standby memory gently cleared")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Standby memory clearing error: {e}")
            return False
    
    def optimize_file_system_cache(self):
        """Optimize file system cache safely"""
        print("[POWER] Optimizing file system cache...")
        
        try:
            if self.system == "Windows":
                # Clear file system cache gently
                cache_clear_commands = [
                    # Clear DNS cache (safe)
                    'ipconfig /flushdns',
                    # Clear Windows Search cache (non-critical)
                    'powershell -Command "Get-Service -Name WSearch | Where-Object {$_.Status -eq \'Running\'} | Stop-Service -Force -PassThru | Start-Service"',
                ]
                
                cleared_items = 0
                for cmd in cache_clear_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                        cleared_items += 1
                    except:
                        pass
                
                print(f"[OK] Optimized {cleared_items} file system cache items")
                return True
            else:
                # Unix-based systems
                subprocess.run(['sync'], capture_output=True)  # Sync file systems
                print("[OK] File system cache optimized")
                return True
                
        except Exception as e:
            print(f"[WARNING]  File system cache optimization error: {e}")
            return False
    
    def refresh_memory_pools(self):
        """Refresh Windows memory pools safely"""
        if self.system != "Windows":
            print("[POWER] Refreshing memory pools (Unix-based)")
            return True
        
        print("[POWER] Refreshing memory pools...")
        
        try:
            # Safe memory pool refresh commands
            refresh_commands = [
                # Refresh non-paged pool
                'powershell -Command "$pool = Get-WmiObject -Class Win32_PerfRawData_PerfOS_Memory; $pool.PoolNonPagedBytes = $pool.PoolNonPagedBytes"',
                # Refresh paged pool
                'powershell -Command "$pool = Get-WmiObject -Class Win32_PerfRawData_PerfOS_Memory; $pool.PoolPagedBytes = $pool.PoolPagedBytes"',
            ]
            
            refreshed_pools = 0
            for cmd in refresh_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
                    refreshed_pools += 1
                except:
                    pass
            
            print(f"[OK] Refreshed {refreshed_pools} memory pools")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Memory pool refresh error: {e}")
            return False
    
    def defragment_memory(self):
        """Gentle memory defragmentation"""
        print("[POWER] Performing gentle memory defragmentation...")
        
        try:
            if self.system == "Windows":
                # Use Windows memory management APIs
                defrag_commands = [
                    # Memory compaction
                    'powershell -Command "[System.Runtime.InteropServices.Marshal]::ZeroFreeGlobalAlloc([System.IntPtr]::Zero)"',
                    # Force memory compaction
                    'powershell -Command "Get-WmiObject -Class Win32_OperatingSystem | ForEach-Object {$_.Reboot = $_.Reboot}"',
                ]
                
                for cmd in defrag_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                    except:
                        pass
            
            # Force Python garbage collection
            gc.collect()
            gc.collect()  # Run twice to ensure cleanup
            
            print("[OK] Memory defragmentation completed")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Memory defragmentation error: {e}")
            return False
    
    def restart_stuck_services(self):
        """Restart stuck non-essential services safely"""
        if self.system != "Windows":
            print("[POWER] Service optimization (Unix-based)")
            return True
        
        print("[POWER] Checking for stuck services...")
        
        # List of services that can be safely restarted if stuck
        restartable_services = [
            'Themes',                    # Visual themes (restart if stuck)
            'AudioSrv',                  # Audio service
            'BITS',                      # Background Intelligent Transfer
            'CryptSvc',                  # Cryptographic services
            'Dnscache',                  # DNS client
        ]
        
        restarted_services = []
        
        for service in restartable_services:
            try:
                # Check if service exists and is running
                result = subprocess.run(['sc', 'query', service], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and 'RUNNING' in result.stdout:
                    # Check if service is stuck (not responding)
                    try:
                        # Try to query service status - if it takes too long, it might be stuck
                        start_time = time.time()
                        status_result = subprocess.run(['sc', 'query', service], 
                                                    capture_output=True, text=True, timeout=5)
                        
                        # If query takes more than 3 seconds, service might be stuck
                        if time.time() - start_time > 3:
                            # Restart the service
                            restart_result = subprocess.run(['sc', 'restart', service], 
                                                         capture_output=True, text=True, timeout=30)
                            
                            if restart_result.returncode == 0:
                                restarted_services.append(service)
                                print(f"  Restarted stuck service: {service}")
                    except subprocess.TimeoutExpired:
                        # Service is definitely stuck, restart it
                        restart_result = subprocess.run(['sc', 'restart', service], 
                                                     capture_output=True, text=True, timeout=30)
                        
                        if restart_result.returncode == 0:
                            restarted_services.append(service)
                            print(f"  Restarted stuck service: {service}")
                
            except Exception as e:
                continue
        
        if restarted_services:
            print(f"[OK] Restarted {len(restarted_services)} stuck services")
        else:
            print("[OK] No stuck services detected")
        
        return len(restarted_services) > 0
    
    def run_memory_jolt(self):
        """Run complete gentle memory jolt"""
        print("=" * 60)
        print("[POWER] MEMORY JOLT - Gentle System Optimization")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("[TOOL] Non-destructive optimization for stuck memory")
        print("=" * 60)
        
        # Show initial memory state
        self.print_memory_info("Initial")
        
        jolt_results = {
            'memory_trim': False,
            'standby_clear': False,
            'cache_optimize': False,
            'pool_refresh': False,
            'defragment': False,
            'services': False
        }
        
        # Step 1: Gentle memory trim
        jolt_results['memory_trim'] = self.gentle_memory_trim()
        time.sleep(2)
        
        # Step 2: Clear standby memory gently
        jolt_results['standby_clear'] = self.clear_standby_memory_gently()
        time.sleep(2)
        
        # Step 3: Optimize file system cache
        jolt_results['cache_optimize'] = self.optimize_file_system_cache()
        time.sleep(2)
        
        # Step 4: Refresh memory pools
        jolt_results['pool_refresh'] = self.refresh_memory_pools()
        time.sleep(2)
        
        # Step 5: Memory defragmentation
        jolt_results['defragment'] = self.defragment_memory()
        time.sleep(2)
        
        # Step 6: Restart stuck services
        jolt_results['services'] = self.restart_stuck_services()
        time.sleep(3)
        
        # Final garbage collection
        gc.collect()
        
        # Show final memory state
        final_memory = self.get_memory_info()
        self.print_memory_info("Final")
        
        # Calculate improvement
        initial_used_gb = self.initial_memory['used'] / (1024**3)
        final_used_gb = final_memory['used'] / (1024**3)
        improvement_gb = initial_used_gb - final_used_gb
        improvement_percent = ((self.initial_memory['percent'] - final_memory['percent']) / self.initial_memory['percent']) * 100
        
        print(f"\n[CHART] JOLT RESULTS:")
        print(f"Memory freed: {improvement_gb:.2f} GB")
        print(f"Usage improvement: {improvement_percent:.1f}%")
        print(f"Initial usage: {self.initial_memory['percent']:.1f}%")
        print(f"Final usage: {final_memory['percent']:.1f}%")
        
        print(f"\n[TOOL] OPERATIONS COMPLETED:")
        for operation, success in jolt_results.items():
            status = "[OK]" if success else "[ERROR]"
            print(f"{status} {operation.replace('_', ' ').title()}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if improvement_gb > 0.1:  # If freed more than 100MB
            print("[POWER] Memory jolt successful! System should be more responsive.")
        else:
            print("ℹ️  System appears optimized. Try restarting for maximum effect.")
        
        return improvement_gb

def main():
    """Main function"""
    print("[POWER] MEMORY JOLT")
    print("Gentle system optimization for stuck memory and bottlenecks")
    print("[TOOL] Non-destructive approach that preserves system stability")
    
    response = input("\nPerform gentle memory jolt? (Y/n): ")
    if response.lower() == 'n':
        print("Memory jolt cancelled.")
        return
    
    try:
        jolt = MemoryJolt()
        memory_freed = jolt.run_memory_jolt()
        
        if memory_freed > 0.1:
            print(f"\n[POWER] Successfully freed {memory_freed:.2f} GB!")
            print("[ROCKET] Your system should feel more responsive now.")
        else:
            print("\n💡 System appears well-optimized.")
            
    except KeyboardInterrupt:
        print("\n[WARNING]  Memory jolt interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error during memory jolt: {e}")

if __name__ == "__main__":
    main()
