#!/usr/bin/env python3
"""
Simple test to verify launcher functionality
"""

import subprocess
import sys
from pathlib import Path

def test_direct_launch():
    """Test launching monitoring tools directly"""
    print("🧪 Testing Direct Launch of Monitoring Tools")
    print("=" * 50)
    
    tools = [
        ("CPU Monitor", "Cpu Monitor/cpu_monitor.py"),
        ("GPU Monitor", "Gpu Monitor/gpu_monitor.py"),
        ("Network Monitor", "Network Monitor/network_monitor.py"),
        ("Storage Monitor", "Storage Monitor/storage_monitor.py"),
        ("Memory Monitor", "Memory Monitor/ram_monitor_gui.py")
    ]
    
    base_path = Path(__file__).parent
    
    for tool_name, tool_path in tools:
        full_path = base_path / tool_path
        print(f"\n🔍 Testing {tool_name}...")
        print(f"   Path: {full_path}")
        print(f"   Exists: {full_path.exists()}")
        
        if full_path.exists():
            try:
                # Test compilation
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Syntax OK")
                else:
                    print(f"   ❌ Syntax Error: {result.stderr[:100]}...")
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
        else:
            print(f"   ❌ File not found")

def test_launcher_paths():
    """Test launcher path configuration"""
    print(f"\n🔧 Testing Launcher Path Configuration")
    print("=" * 50)
    
    # Read launcher config
    launcher_file = Path(__file__).parent / "simple_launcher.py"
    if launcher_file.exists():
        print("✅ Launcher file exists")
        
        # Test if launcher can be imported
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(launcher_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✅ Launcher syntax OK")
            else:
                print(f"❌ Launcher syntax error: {result.stderr[:100]}...")
        except Exception as e:
            print(f"❌ Launcher test failed: {e}")
    else:
        print("❌ Launcher file not found")

if __name__ == "__main__":
    test_direct_launch()
    test_launcher_paths()
    
    print(f"\n📊 Summary:")
    print("The launcher should be able to find and launch these tools.")
    print("If files exist but launcher can't find them, the issue is in path resolution.")
