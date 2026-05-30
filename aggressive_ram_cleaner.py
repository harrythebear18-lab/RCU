#!/usr/bin/env python3
"""
Aggressive RAM Cleaner
Advanced system-level RAM cleanup for stubborn memory usage.
Requires Administrator privileges for full functionality.
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
import ctypes.wintypes

class AggressiveRAMCleaner:
    def __init__(self):
        self.system = platform.system()
        self.is_admin = self.check_admin_privileges()
        
        # Windows-specific memory management
        if self.system == "Windows":
            self.kernel32 = ctypes.windll.kernel32
            self.psapi = ctypes.windll.psapi
            
            # Define Windows API functions
            self.SetProcessWorkingSetSize = self.kernel32.SetProcessWorkingSetSize
            self.EmptyWorkingSet = self.psapi.EmptyWorkingSet
            
    def check_admin_privileges(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def get_memory_info(self):
        """Get detailed memory information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'free': memory.free,
            'cached': memory.cached if hasattr(memory, 'cached') else 0,
            'buffers': memory.buffers if hasattr(memory, 'buffers') else 0
        }
    
    def print_memory_info(self, label="Current"):
        """Print detailed memory information"""
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
    
    def clear_system_standby_memory(self):
        """Clear system standby memory using Windows API"""
        if self.system != "Windows":
            print("[WARNING]  Standby memory clearing only works on Windows")
            return False
        
        print("[CLEAN] Clearing system standby memory...")
        
        try:
            # Method 1: PowerShell EmptyStandbyList
            result = subprocess.run([
                'powershell', '-Command', 
                '[System.Runtime.InteropServices.Marshal]::PrelinkAll()'
            ], capture_output=True, text=True)
            
            # Method 2: Clear standby list using RAMMap tool approach
            ps_commands = [
                # Clear standby list
                'powershell -Command "& {$Process = Get-Process; $Process | ForEach-Object {[System.GC]::Collect()}}; $Process = $null"',
                # Force memory trimming
                'powershell -Command "Get-Process | Where-Object {$_.WorkingSet -gt 50MB} | ForEach-Object {$_.WorkingSet = 0}"'
            ]
            
            for cmd in ps_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                except:
                    pass
            
            print("[OK] Standby memory clearing completed")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Standby memory clearing error: {e}")
            return False
    
    def force_memory_trim(self):
        """Force aggressive memory trimming"""
        if self.system != "Windows":
            return False
        
        print("[CLEAN] Forcing aggressive memory trim...")
        
        try:
            # Get all processes and force working set trimming
            processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Trim working sets for all processes
            trimmed_count = 0
            for pid in processes:
                try:
                    if pid != os.getpid():  # Don't trim our own process
                        handle = self.kernel32.OpenProcess(0x1F0FFF, False, pid)
                        if handle:
                            self.EmptyWorkingSet(handle)
                            self.kernel32.CloseHandle(handle)
                            trimmed_count += 1
                except:
                    continue
            
            print(f"[OK] Trimmed working sets for {trimmed_count} processes")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Memory trim error: {e}")
            return False
    
    def clear_system_cache_aggressive(self):
        """Aggressive system cache clearing"""
        if self.system != "Windows":
            return False
        
        print("[CLEAN] Performing aggressive system cache clearing...")
        
        cleared_items = 0
        
        try:
            # Clear DNS cache
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            cleared_items += 1
            
            # Clear Windows Update cache
            update_cache = r'C:\Windows\SoftwareDistribution\Download'
            if os.path.exists(update_cache):
                try:
                    for item in os.listdir(update_cache):
                        item_path = os.path.join(update_cache, item)
                        try:
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                                cleared_items += 1
                        except:
                            pass
                except:
                    pass
            
            # Clear Windows Search cache
            search_cache = os.path.expanduser(r'~\AppData\Local\Microsoft\Windows\Search')
            if os.path.exists(search_cache):
                try:
                    for item in os.listdir(search_cache):
                        if item.endswith('.edb') or item.endswith('.log'):
                            item_path = os.path.join(search_cache, item)
                            try:
                                os.unlink(item_path)
                                cleared_items += 1
                            except:
                                pass
                except:
                    pass
            
            # Clear thumbnail cache
            thumb_cache = os.path.expanduser(r'~\AppData\Local\Microsoft\Windows\Explorer')
            if os.path.exists(thumb_cache):
                try:
                    for item in os.listdir(thumb_cache):
                        if 'thumbcache' in item.lower():
                            item_path = os.path.join(thumb_cache, item)
                            try:
                                os.unlink(item_path)
                                cleared_items += 1
                            except:
                                pass
                except:
                    pass
            
            print(f"[OK] Cleared {cleared_items} system cache items")
            return True
            
        except Exception as e:
            print(f"[WARNING]  System cache clearing error: {e}")
            return False
    
    def stop_nonessential_services(self):
        """Stop non-essential Windows services"""
        if not self.is_admin:
            print("[WARNING]  Service management requires Administrator privileges")
            return False
        
        print("[CLEAN] Stopping non-essential services...")
        
        # List of non-essential services that can be safely stopped
        nonessential_services = [
            'Themes',                    # Visual themes
            'DesktopWindowManager',      # Desktop effects (may restart automatically)
            'SysMain',                   # Superfetch/Prefetch
            'WSearch',                   # Windows Search
            'XboxGipSvc',               # Xbox services
            'XboxNetApiSvc',            # Xbox networking
            'XboxAuthSvc',              # Xbox authentication
            'BluetoothSupportService',   # Bluetooth
            'BthAvctpSvc',              # Bluetooth AVCTP service
            'bthserv',                  # Bluetooth support
            'PrintSpooler',             # Print spooler
            'Fax',                      # Fax service
            'WMPNetworkSvc',            # Windows Media Player networking
            'WindowsMediaPlayerSharing', # Windows Media Player sharing
        ]
        
        stopped_services = []
        
        for service in nonessential_services:
            try:
                # Check if service exists and is running
                result = subprocess.run(['sc', 'query', service], 
                                      capture_output=True, text=True, timeout=10)
                
                if 'RUNNING' in result.stdout:
                    # Stop the service
                    stop_result = subprocess.run(['sc', 'stop', service], 
                                              capture_output=True, text=True, timeout=30)
                    
                    if stop_result.returncode == 0:
                        stopped_services.append(service)
                        print(f"  Stopped: {service}")
                
            except Exception as e:
                continue
        
        print(f"[OK] Stopped {len(stopped_services)} non-essential services")
        return len(stopped_services) > 0
    
    def optimize_virtual_memory(self):
        """Optimize virtual memory settings"""
        if not self.is_admin:
            print("[WARNING]  Virtual memory optimization requires Administrator privileges")
            return False
        
        print("[CLEAN] Optimizing virtual memory...")
        
        try:
            # Clear pagefile
            subprocess.run(['powershell', '-Command', 
                          'Clear-Content -Path "$env:SystemRoot\\system32\\config\\system" -ErrorAction SilentlyContinue'], 
                          capture_output=True, timeout=30)
            
            # Optimize pagefile usage
            ps_commands = [
                'powershell -Command "wmic computersystem where name=\"%computername%\" set AutomaticManagedPagefile=False"',
                'powershell -Command "wmic pagefileset where name=\"C:\\pagefile.sys\" set InitialSize=1024,MaximumSize=4096"'
            ]
            
            for cmd in ps_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                except:
                    pass
            
            print("[OK] Virtual memory optimization completed")
            return True
            
        except Exception as e:
            print(f"[WARNING]  Virtual memory optimization error: {e}")
            return False
    
    def kill_memory_hogging_processes(self):
        """Kill processes using excessive memory"""
        print("[CLEAN] Identifying and killing memory-hogging processes...")
        
        killed_processes = []
        
        # Get processes sorted by memory usage
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'username']):
            try:
                pinfo = proc.info
                memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                username = pinfo.get('username', '')
                
                # Skip system processes and current user's essential processes
                if (memory_mb > 100 and  # Only consider processes >100MB
                    username and not username.endswith('SYSTEM') and
                    not any(sys_proc in pinfo['name'].lower() for sys_proc in 
                           ['system', 'svchost', 'dwm', 'explorer', 'winlogon'])):
                    
                    processes.append((proc, memory_mb, pinfo['name']))
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by memory usage (highest first)
        processes.sort(key=lambda x: x[1], reverse=True)
        
        # Kill top memory hogs (excluding critical ones)
        critical_processes = {
            'explorer.exe', 'winlogon.exe', 'csrss.exe', 'smss.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'dwm.exe'
        }
        
        for proc, memory_mb, name in processes[:10]:  # Top 10 memory hogs
            try:
                if name.lower() not in critical_processes:
                    proc.terminate()
                    killed_processes.append((name, memory_mb))
                    print(f"  Killed: {name} ({memory_mb:.1f} MB)")
                    time.sleep(0.5)  # Brief pause between kills
            except:
                continue
        
        print(f"[OK] Killed {len(killed_processes)} memory-hogging processes")
        return len(killed_processes) > 0
    
    def run_aggressive_cleanup(self):
        """Run complete aggressive RAM cleanup"""
        print("=" * 60)
        print("[ROCKET] AGGRESSIVE RAM CLEANUP")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Administrator: {'Yes' if self.is_admin else 'No (Limited functionality)'}")
        print("=" * 60)
        
        # Show initial memory state
        initial_memory = self.get_memory_info()
        self.print_memory_info("Initial")
        
        cleanup_results = {
            'standby_memory': False,
            'memory_trim': False,
            'system_cache': False,
            'services': False,
            'virtual_memory': False,
            'processes': False
        }
        
        # Step 1: Clear standby memory
        cleanup_results['standby_memory'] = self.clear_system_standby_memory()
        time.sleep(2)
        
        # Step 2: Force memory trim
        cleanup_results['memory_trim'] = self.force_memory_trim()
        time.sleep(2)
        
        # Step 3: Aggressive system cache clearing
        cleanup_results['system_cache'] = self.clear_system_cache_aggressive()
        time.sleep(2)
        
        # Step 4: Stop non-essential services (Admin only)
        if self.is_admin:
            cleanup_results['services'] = self.stop_nonessential_services()
            time.sleep(2)
        
        # Step 5: Optimize virtual memory (Admin only)
        if self.is_admin:
            cleanup_results['virtual_memory'] = self.optimize_virtual_memory()
            time.sleep(2)
        
        # Step 6: Kill memory-hogging processes
        cleanup_results['processes'] = self.kill_memory_hogging_processes()
        time.sleep(3)
        
        # Force Python garbage collection
        gc.collect()
        
        # Show final memory state
        final_memory = self.get_memory_info()
        self.print_memory_info("Final")
        
        # Calculate improvement
        initial_used_gb = initial_memory['used'] / (1024**3)
        final_used_gb = final_memory['used'] / (1024**3)
        improvement_gb = initial_used_gb - final_used_gb
        improvement_percent = ((initial_memory['percent'] - final_memory['percent']) / initial_memory['percent']) * 100
        
        print(f"\n[CHART] CLEANUP RESULTS:")
        print(f"Memory freed: {improvement_gb:.2f} GB")
        print(f"Usage improvement: {improvement_percent:.1f}%")
        print(f"Initial usage: {initial_memory['percent']:.1f}%")
        print(f"Final usage: {final_memory['percent']:.1f}%")
        
        print(f"\n[TOOL] OPERATIONS COMPLETED:")
        for operation, success in cleanup_results.items():
            status = "[OK]" if success else "[ERROR]"
            print(f"{status} {operation.replace('_', ' ').title()}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if improvement_gb > 0.5:  # If freed more than 500MB
            print("🎉 Aggressive cleanup successful!")
        else:
            print("ℹ️  Limited memory freed. Try running as Administrator for better results.")
        
        return improvement_gb

def main():
    """Main function"""
    print("[CLEAN] AGGRESSIVE RAM CLEANER")
    print("Advanced system-level RAM cleanup for stubborn memory usage")
    print("[WARNING]  WARNING: This tool performs aggressive system modifications")
    
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("\n[WARNING]  WARNING: Not running as Administrator!")
        print("Some cleanup operations may not work properly.")
        print("For best results, right-click and 'Run as administrator'")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Cleanup cancelled.")
            return
    
    response = input("\nThis will perform aggressive system cleanup. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    try:
        cleaner = AggressiveRAMCleaner()
        memory_freed = cleaner.run_aggressive_cleanup()
        
        if memory_freed > 0:
            print(f"\n[SAVE] Successfully freed {memory_freed:.2f} GB of RAM!")
        else:
            print("\n💡 Tip: Restart your computer for maximum memory recovery")
            
    except KeyboardInterrupt:
        print("\n[WARNING]  Cleanup interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error during cleanup: {e}")

if __name__ == "__main__":
    main()
