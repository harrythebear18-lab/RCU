#!/usr/bin/env python3
"""
System Cleanup Master Script
A comprehensive script to run RAM, GPU, and CPU cleanup for optimal gaming performance.
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path to import cleanup modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ram_cleanup_script import RAMCleaner
    RAM_AVAILABLE = True
except ImportError:
    RAM_AVAILABLE = False
    print("[WARNING]  RAM cleanup module not available")

try:
    from gpu_cleanup_script import GPUCleaner
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("[WARNING]  GPU cleanup module not available")

try:
    from cpu_cleanup_script import CPUCleaner
    CPU_AVAILABLE = True
except ImportError:
    CPU_AVAILABLE = False
    print("[WARNING]  CPU cleanup module not available")

class SystemCleanupMaster:
    def __init__(self):
        self.start_time = datetime.now()
        
    def run_ram_cleanup(self):
        """Run RAM cleanup"""
        if not RAM_AVAILABLE:
            print("[WARNING]  Skipping RAM cleanup - module not available")
            return
        
        print("\n" + "="*60)
        print("[CLEAN] RUNNING RAM CLEANUP")
        print("="*60)
        
        try:
            cleaner = RAMCleaner()
            cleaner.run_full_cleanup()
            return True
        except Exception as e:
            print(f"[ERROR] RAM cleanup failed: {e}")
            return False
    
    def run_gpu_cleanup(self):
        """Run GPU cleanup"""
        if not GPU_AVAILABLE:
            print("[WARNING]  Skipping GPU cleanup - module not available")
            return
        
        print("\n" + "="*60)
        print("[GAME] RUNNING GPU CLEANUP")
        print("="*60)
        
        try:
            cleaner = GPUCleaner()
            cleaner.run_full_cleanup()
            return True
        except Exception as e:
            print(f"[ERROR] GPU cleanup failed: {e}")
            return False
    
    def run_cpu_cleanup(self):
        """Run CPU cleanup"""
        if not CPU_AVAILABLE:
            print("[WARNING]  Skipping CPU cleanup - module not available")
            return
        
        print("\n" + "="*60)
        print("[POWER] RUNNING CPU CLEANUP")
        print("="*60)
        
        try:
            cleaner = CPUCleaner()
            cleaner.run_full_cleanup()
            return True
        except Exception as e:
            print(f"[ERROR] CPU cleanup failed: {e}")
            return False
    
    def run_full_system_cleanup(self):
        """Run complete system cleanup"""
        print("[ROCKET] SYSTEM CLEANUP MASTER")
        print("This script will optimize RAM, GPU, and CPU for gaming")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            'ram': False,
            'gpu': False,
            'cpu': False
        }
        
        # Run cleanups in sequence
        results['ram'] = self.run_ram_cleanup()
        time.sleep(2)  # Wait between cleanups
        
        results['gpu'] = self.run_gpu_cleanup()
        time.sleep(2)  # Wait between cleanups
        
        results['cpu'] = self.run_cpu_cleanup()
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "="*60)
        print("[CHART] CLEANUP SUMMARY")
        print("="*60)
        print(f"⏰ Started:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
        print()
        print("Results:")
        print(f"  RAM Cleanup:  {'[OK] Success' if results['ram'] else '[ERROR] Failed'}")
        print(f"  GPU Cleanup:  {'[OK] Success' if results['gpu'] else '[ERROR] Failed'}")
        print(f"  CPU Cleanup:  {'[OK] Success' if results['cpu'] else '[ERROR] Failed'}")
        
        success_count = sum(results.values())
        if success_count == 3:
            print("\n🎉 All system cleanups completed successfully!")
            print("[GAME] Your system is now optimized for gaming!")
        elif success_count > 0:
            print(f"\n[WARNING]  {success_count}/3 cleanups completed successfully")
        else:
            print("\n[ERROR] All cleanups failed")
        
        print("="*60)

def main():
    """Main function"""
    print("[ROCKET] System Cleanup Master Script")
    print("This script will run RAM, GPU, and CPU cleanup utilities")
    
    # Check available modules
    if not any([RAM_AVAILABLE, GPU_AVAILABLE, CPU_AVAILABLE]):
        print("[ERROR] No cleanup modules available!")
        print("Make sure the cleanup scripts are in the same directory.")
        sys.exit(1)
    
    master = SystemCleanupMaster()
    
    try:
        master.run_full_system_cleanup()
    except KeyboardInterrupt:
        print("\n[WARNING]  System cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error during system cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
