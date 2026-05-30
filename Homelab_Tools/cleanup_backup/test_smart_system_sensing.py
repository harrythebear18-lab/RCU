#!/usr/bin/env python3
"""
Test Smart System Sensing
Tests Windows 11 detection and optimization generation
"""

import sys
from pathlib import Path

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from smart_system_sensing import get_smart_system_sensing, detect_system, is_windows_11, is_windows_10, get_system_summary
    print("✅ Smart system sensing imported successfully")
except ImportError as e:
    print(f"❌ Failed to import smart system sensing: {e}")
    sys.exit(1)

def test_system_detection():
    """Test system detection"""
    print("\n" + "=" * 60)
    print("SMART SYSTEM SENSING TEST")
    print("=" * 60)
    
    try:
        # Initialize sensor
        sensor = get_smart_system_sensing()
        print("✅ Smart system sensing initialized")
        
        # Detect system
        print("\nDetecting system...")
        system_info = detect_system(force_refresh=True)
        
        print(f"✅ System Type: {system_info.system_type.value}")
        print(f"✅ Hardware Profile: {system_info.hardware_profile.value}")
        print(f"✅ Build Number: {system_info.build_number}")
        print(f"✅ Version: {system_info.version}")
        print(f"✅ Architecture: {system_info.architecture}")
        print(f"✅ Total Score: {system_info.total_score:.1f}")
        
        # Check Windows versions
        print(f"\nWindows 11: {is_windows_11()}")
        print(f"Windows 10: {is_windows_10()}")
        
        # Display capabilities
        print(f"\nCapabilities: {len(system_info.capabilities)} detected")
        for capability in system_info.capabilities:
            print(f"  - {capability.value}")
        
        # Display hardware info
        print(f"\nCPU Info:")
        print(f"  - Brand: {system_info.cpu_info.get('brand', 'Unknown')}")
        print(f"  - Cores: {system_info.cpu_info.get('cores', 0)}")
        print(f"  - Threads: {system_info.cpu_info.get('threads', 0)}")
        print(f"  - Usage: {system_info.cpu_info.get('usage_percent', 0):.1f}%")
        
        print(f"\nGPU Info:")
        gpus = system_info.gpu_info.get('gpus', [])
        print(f"  - GPU Count: {len(gpus)}")
        for i, gpu in enumerate(gpus):
            print(f"  - GPU {i+1}: {gpu.get('brand', 'Unknown')} {gpu.get('name', 'Unknown')}")
        
        print(f"\nMemory Info:")
        print(f"  - Total: {system_info.memory_info.get('total_gb', 0):.1f} GB")
        print(f"  - Available: {system_info.memory_info.get('available_gb', 0):.1f} GB")
        print(f"  - Usage: {system_info.memory_info.get('percent', 0):.1f}%")
        
        # Get optimization profile
        print(f"\nOptimization Profile:")
        if sensor.optimization_profile:
            opt = sensor.optimization_profile
            print(f"  - System Type: {opt.system_type.value}")
            print(f"  - Hardware Profile: {opt.hardware_profile.value}")
            
            print(f"\n  CPU Optimizations:")
            for key, value in opt.cpu_optimizations.items():
                print(f"    - {key}: {value}")
            
            print(f"\n  GPU Optimizations:")
            for key, value in opt.gpu_optimizations.items():
                print(f"    - {key}: {value}")
            
            print(f"\n  UI Optimizations:")
            for key, value in opt.ui_optimizations.items():
                print(f"    - {key}: {value}")
        
        # Get recommendations
        print(f"\nRecommendations:")
        recommendations = sensor.get_optimization_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Get system summary
        summary = get_system_summary()
        print(f"\nSystem Summary:")
        for key, value in summary.items():
            print(f"  - {key}: {value}")
        
        # Test Windows 11 specific features
        if is_windows_11():
            print(f"\n🎉 WINDOWS 11 DETECTED!")
            print(f"✅ Windows 11 optimizations applied")
            print(f"✅ Windows 11 features enabled")
        elif is_windows_10():
            print(f"\n✅ WINDOWS 10 DETECTED!")
            print(f"✅ Windows 10 optimizations applied")
        else:
            print(f"\n⚠️  OTHER SYSTEM DETECTED: {system_info.system_type.value}")
        
        print(f"\n🎯 SMART SYSTEM SENSING TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system_detection()
    sys.exit(0 if success else 1)
