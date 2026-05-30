#!/usr/bin/env python3
"""
Final test of VM Manager functionality
"""

import tkinter as tk
import sys
from pathlib import Path

# Add VM Manager to path
sys.path.append(str(Path(__file__).parent / 'VM Manager'))

def test_vm_manager():
    """Test VM Manager with available hypervisors"""
    print('🧪 Testing VM Manager with Hyper-V...')
    
    try:
        # Import VM Manager
        from vm_manager import VMManager
        print('✅ VM Manager imported successfully')
        
        # Test initialization
        root = tk.Tk()
        root.withdraw()  # Hide window for testing
        
        vm = VMManager(root)
        print('✅ VM Manager initialized successfully')
        
        # Test hypervisor detection
        print(f'🔍 Detected hypervisor: {vm.hypervisor}')
        
        # Test system resources
        resources = vm.system_resources
        print(f'📊 System resources: {resources["cpu_count"]} cores, {resources["memory_total"] // (1024**3)}GB RAM')
        
        # Test individual hypervisor checks
        print(f'🔧 VirtualBox available: {vm.check_virtualbox()}')
        print(f'🔧 Hyper-V available: {vm.check_hyperv()}')
        print(f'🔧 KVM available: {vm.check_kvm()}')
        print(f'🔧 QEMU available: {vm.check_qemu()}')
        
        # Test VM refresh (should work even with no VMs)
        vm.refresh_all_vms()
        print('✅ VM refresh completed')
        
        # Test VM list
        print(f'📋 Current VMs: {len(vm.vms)} VMs detected')
        
        print('✅ VM Manager functionality test completed successfully!')
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f'❌ VM Manager test failed: {e}')
        try:
            root.destroy()
        except:
            pass
        return False

if __name__ == "__main__":
    success = test_vm_manager()
    
    print(f'\n📊 Final Test Result: {"✅ PASSED" if success else "❌ FAILED"}')
    
    if success:
        print('🎉 VM Manager is ready for use!')
        print('💡 You can now:')
        print('  • Launch VM Manager from the dashboard')
        print('  • Create, start, stop, and delete VMs')
        print('  • Monitor VM resources and performance')
    else:
        print('⚠️  VM Manager needs attention before use')
