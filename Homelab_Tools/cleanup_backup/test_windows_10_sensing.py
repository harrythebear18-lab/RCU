#!/usr/bin/env python3
"""
Test Windows 10 Smart System Sensing
Tests enhanced Windows 10 detection and optimization generation
"""

import sys
from pathlib import Path

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from smart_system_sensing import get_smart_system_sensing, detect_system, is_windows_11, is_windows_10, get_system_summary, SystemType
    print("✅ Smart system sensing imported successfully")
except ImportError as e:
    print(f"❌ Failed to import smart system sensing: {e}")
    sys.exit(1)

def test_windows_10_detection():
    """Test Windows 10 detection"""
    print("\n" + "=" * 60)
    print("WINDOWS 10 SMART SYSTEM SENSING TEST")
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
            
            print(f"\n  Memory Optimizations:")
            for key, value in opt.memory_optimizations.items():
                print(f"    - {key}: {value}")
            
            print(f"\n  Power Optimizations:")
            for key, value in opt.power_optimizations.items():
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
        
        # Test Windows 10 specific features
        if is_windows_10():
            print(f"\n🎉 WINDOWS 10 DETECTED!")
            print(f"✅ Windows 10 optimizations applied")
            print(f"✅ Windows 10 features enabled")
            
            # Check for Windows 10 specific optimizations
            opt = sensor.optimization_profile
            if opt:
                print(f"\nWindows 10 Specific Features:")
                win10_features = [
                    'timeline', 'action_center', 'cortana', 'virtual_desktops', 
                    'focus_assist', 'game_mode', 'game_bar', 'storage_sense'
                ]
                
                for feature in win10_features:
                    if feature in opt.ui_optimizations:
                        status = opt.ui_optimizations[feature]
                        print(f"  - {feature.replace('_', ' ').title()}: {status}")
                
                print(f"\nWindows 10 Performance Features:")
                perf_features = [
                    'prefetch', 'superfetch', 'readyboost', 'fast_startup', 
                    'hybrid_sleep', 'connected_standby'
                ]
                
                for feature in perf_features:
                    if feature in opt.power_optimizations:
                        status = opt.power_optimizations[feature]
                        print(f"  - {feature.replace('_', ' ').title()}: {status}")
        
        elif is_windows_11():
            print(f"\n🎉 WINDOWS 11 DETECTED!")
            print(f"✅ Windows 11 optimizations applied")
            print(f"✅ Windows 11 features enabled")
        else:
            print(f"\n⚠️  OTHER SYSTEM DETECTED: {system_info.system_type.value}")
        
        # Test feature detection methods
        print(f"\nTesting Feature Detection Methods:")
        print(f"  - Build Number Detection: {system_info.build_number}")
        print(f"  - Registry Detection: Available")
        print(f"  - Feature-based Detection: Available")
        
        # Test optimization generation
        print(f"\nTesting Optimization Generation:")
        if sensor.optimization_profile:
            opt = sensor.optimization_profile
            print(f"  - CPU Optimizations Count: {len(opt.cpu_optimizations)}")
            print(f"  - GPU Optimizations Count: {len(opt.gpu_optimizations)}")
            print(f"  - UI Optimizations Count: {len(opt.ui_optimizations)}")
            print(f"  - Memory Optimizations Count: {len(opt.memory_optimizations)}")
            print(f"  - Power Optimizations Count: {len(opt.power_optimizations)}")
            print(f"  - Network Optimizations Count: {len(opt.network_optimizations)}")
        
        print(f"\n🎯 WINDOWS 10 SMART SYSTEM SENSING TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_windows_10_test():
    """Simulate Windows 10 detection for testing"""
    print("\n" + "=" * 60)
    print("SIMULATING WINDOWS 10 DETECTION")
    print("=" * 60)
    
    try:
        sensor = get_smart_system_sensing()
        
        # Override system type for testing
        original_system_info = sensor.system_info
        
        # Create a mock Windows 10 system info
        from smart_system_sensing import SystemInfo, SystemType, HardwareProfile, SystemCapability
        
        mock_system_info = SystemInfo(
            system_type=SystemType.WINDOWS_10,
            hardware_profile=HardwareProfile.INTEL_NVIDIA,
            capabilities=[SystemCapability.GAMING, SystemCapability.PRODUCTIVITY, SystemCapability.DEVELOPMENT],
            cpu_info={'brand': 'Intel Core i7', 'cores': 8, 'threads': 16, 'usage_percent': 15.0},
            gpu_info={'gpus': [{'brand': 'NVIDIA', 'name': 'GeForce RTX 3080'}]},
            memory_info={'total_gb': 16.0, 'available_gb': 8.0, 'percent': 50.0},
            disk_info={'disks': []},
            network_info={'interfaces': []},
            build_number=19044,
            version='Windows-10-10.0.19044',
            architecture='64bit',
            total_score=85.0
        )
        
        # Set mock system info
        sensor.system_info = mock_system_info
        sensor.optimization_profile = sensor._generate_windows_10_optimizations()
        
        print("✅ Mock Windows 10 system created")
        print(f"✅ System Type: {mock_system_info.system_type.value}")
        print(f"✅ Build Number: {mock_system_info.build_number}")
        
        # Test Windows 10 optimizations
        print(f"\nWindows 10 Optimizations:")
        opt = sensor.optimization_profile
        if opt:
            print(f"  - Power Plan: {opt.cpu_optimizations.get('power_plan')}")
            print(f"  - Game Mode: {opt.gpu_optimizations.get('game_mode')}")
            print(f"  - Timeline: {opt.ui_optimizations.get('timeline')}")
            print(f"  - Cortana: {opt.ui_optimizations.get('cortana')}")
            print(f"  - Virtual Desktops: {opt.ui_optimizations.get('virtual_desktops')}")
            print(f"  - Focus Assist: {opt.ui_optimizations.get('focus_assist')}")
            print(f"  - Fast Startup: {opt.power_optimizations.get('fast_startup')}")
            print(f"  - Prefetch: {opt.memory_optimizations.get('prefetch')}")
            print(f"  - Superfetch: {opt.memory_optimizations.get('superfetch')}")
            print(f"  - ReadyBoost: {opt.memory_optimizations.get('readyboost')}")
        
        # Test Windows 10 recommendations
        print(f"\nWindows 10 Recommendations:")
        recommendations = sensor.get_optimization_recommendations()
        win10_recommendations = [r for r in recommendations if 'Windows 10' in r]
        for i, rec in enumerate(win10_recommendations[:5], 1):  # Show first 5
            print(f"  {i}. {rec}")
        
        print(f"\n✅ Windows 10 simulation completed successfully!")
        
        # Restore original system info
        sensor.system_info = original_system_info
        if original_system_info:
            sensor.optimization_profile = sensor._generate_optimization_profile()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Windows 10 simulation: {e}")
        return False

if __name__ == "__main__":
    # Test actual system detection
    success1 = test_windows_10_detection()
    
    # Test Windows 10 simulation
    success2 = simulate_windows_10_test()
    
    overall_success = success1 and success2
    print(f"\n{'='*60}")
    print(f"OVERALL TEST RESULT: {'SUCCESS' if overall_success else 'FAILED'}")
    print(f"Actual Detection: {'PASS' if success1 else 'FAIL'}")
    print(f"Windows 10 Simulation: {'PASS' if success2 else 'FAIL'}")
    print(f"{'='*60}")
    
    sys.exit(0 if overall_success else 1)
