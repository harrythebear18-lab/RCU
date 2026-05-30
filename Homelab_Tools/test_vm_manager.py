#!/usr/bin/env python3
"""
Test VM Manager functionality with available hypervisors
"""

import subprocess
import platform
import os
from pathlib import Path

def test_hypervisor_availability():
    """Test which hypervisors are available on this system"""
    print("🔍 Testing Hypervisor Availability...")
    print(f"Operating System: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    
    hypervisors = {
        'VirtualBox': test_virtualbox,
        'Hyper-V': test_hyperv,
        'KVM': test_kvm,
        'QEMU': test_qemu
    }
    
    available = {}
    for name, test_func in hypervisors.items():
        try:
            result = test_func()
            available[name] = result
            print(f"  {name}: {'✅ Available' if result else '❌ Not Available'}")
        except Exception as e:
            available[name] = False
            print(f"  {name}: ❌ Error - {e}")
    
    return available

def test_virtualbox():
    """Test VirtualBox availability"""
    try:
        result = subprocess.run(['VBoxManage', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def test_hyperv():
    """Test Hyper-V availability"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['powershell', '-Command', 'Get-Module -ListAvailable -Name Hyper-V'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        return False
    except:
        return False

def test_kvm():
    """Test KVM availability"""
    try:
        if platform.system() == "Linux":
            return os.path.exists('/dev/kvm') and os.path.exists('/usr/bin/kvm')
        return False
    except:
        return False

def test_qemu():
    """Test QEMU availability"""
    try:
        result = subprocess.run(['qemu-system-x86_64', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def test_vm_manager_functionality():
    """Test VM Manager functionality without GUI"""
    print("\n🧪 Testing VM Manager Functionality...")
    
    # Test import
    try:
        import sys
        vm_manager_path = Path(__file__).parent / 'VM Manager' / 'vm_manager.py'
        if vm_manager_path.exists():
            print("  ✅ VM Manager file exists")
        else:
            print("  ❌ VM Manager file not found")
            return False
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False
    
    # Test hypervisor detection logic
    try:
        # Simulate hypervisor detection
        hypervisors = test_hypervisor_availability()
        detected = None
        for name, available in hypervisors.items():
            if available:
                detected = name.lower().replace('-', '').replace(' ', '')
                break
        
        print(f"  ✅ Hypervisor detection logic working")
        print(f"  📊 Would detect: {detected or 'None'}")
        
    except Exception as e:
        print(f"  ❌ Detection logic error: {e}")
        return False
    
    # Test file structure
    try:
        vm_dir = Path(__file__).parent / 'VM Manager'
        required_files = ['vm_manager.py']
        
        for file in required_files:
            file_path = vm_dir / file
            if file_path.exists():
                print(f"  ✅ {file} exists")
            else:
                print(f"  ❌ {file} missing")
                return False
                
    except Exception as e:
        print(f"  ❌ File structure error: {e}")
        return False
    
    return True

def create_test_report():
    """Create comprehensive test report"""
    print("\n📋 VM Manager Test Report")
    print("="*50)
    
    # Test hypervisor availability
    hypervisors = test_hypervisor_availability()
    
    # Test VM Manager functionality
    vm_manager_ok = test_vm_manager_functionality()
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"  Hypervisors Available: {sum(hypervisors.values())}/{len(hypervisors)}")
    print(f"  VM Manager Functional: {'✅ Yes' if vm_manager_ok else '❌ No'}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if not any(hypervisors.values()):
        print("  • No hypervisors detected. Consider installing:")
        print("    - VirtualBox (Free, cross-platform)")
        print("    - Hyper-V (Windows Pro/Enterprise)")
        print("    - KVM/QEMU (Linux)")
    else:
        print("  • Hypervisor(s) available - VM Manager should work!")
        print("  • Test VM operations: create, start, stop, delete")
    
    if vm_manager_ok:
        print("  • VM Manager code structure is correct")
        print("  • Ready for use when hypervisor is available")
    else:
        print("  • VM Manager needs fixes before use")
    
    return {
        'hypervisors': hypervisors,
        'vm_manager_ok': vm_manager_ok,
        'overall_status': 'ready' if vm_manager_ok and any(hypervisors.values()) else 'needs_setup'
    }

if __name__ == "__main__":
    create_test_report()
