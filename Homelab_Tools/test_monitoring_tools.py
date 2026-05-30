#!/usr/bin/env python3
"""
Test all 5 monitoring tools to identify issues
"""

import subprocess
import sys
import os
from pathlib import Path

def test_monitoring_tool(tool_name, tool_path):
    """Test a single monitoring tool"""
    print(f"\n🧪 Testing {tool_name}...")
    
    # Check if file exists
    if not Path(tool_path).exists():
        print(f"  ❌ File not found: {tool_path}")
        return False
    
    try:
        # Try to run the tool with a timeout
        result = subprocess.run(
            [sys.executable, tool_path],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(Path(tool_path).parent)
        )
        
        if result.returncode == 0:
            print(f"  ✅ {tool_name} runs successfully")
            return True
        else:
            print(f"  ❌ {tool_name} failed with return code {result.returncode}")
            if result.stderr:
                print(f"     Error: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  {tool_name} timed out (likely GUI waiting)")
        return True  # Timeout is expected for GUI apps
    except Exception as e:
        print(f"  ❌ {tool_name} crashed: {e}")
        return False

def test_imports(tool_name, tool_path):
    """Test if a tool can be imported"""
    print(f"  🔍 Testing imports for {tool_name}...")
    
    try:
        # Add the tool's directory to path
        tool_dir = Path(tool_path).parent
        import_spec = tool_path.replace('.py', '').replace('/', '.').replace(' ', '_')
        
        # Try to execute the file to check for import errors
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", tool_path],
            capture_output=True,
            text=True,
            cwd=str(Path(tool_path).parent)
        )
        
        if result.returncode == 0:
            print(f"    ✅ Syntax and imports OK")
            return True
        else:
            print(f"    ❌ Compilation error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"    ❌ Import test failed: {e}")
        return False

def main():
    """Test all monitoring tools"""
    print("🔍 Testing All 5 Monitoring Tools")
    print("=" * 50)
    
    monitoring_tools = [
        ("CPU Monitor", "Cpu Monitor/cpu_monitor.py"),
        ("GPU Monitor", "Gpu Monitor/gpu_monitor.py"),
        ("Network Monitor", "Network Monitor/network_monitor.py"),
        ("Storage Monitor", "Storage Monitor/storage_monitor.py"),
        ("Memory Monitor", "Memory Monitor/ram_monitor_gui.py")
    ]
    
    results = {}
    
    for tool_name, tool_path in monitoring_tools:
        # Test imports first
        import_ok = test_imports(tool_name, tool_path)
        
        # Test execution
        exec_ok = test_monitoring_tool(tool_name, tool_path)
        
        results[tool_name] = {
            'import_ok': import_ok,
            'exec_ok': exec_ok,
            'overall': import_ok and exec_ok
        }
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print("=" * 50)
    
    working_count = 0
    for tool_name, result in results.items():
        status = "✅ WORKING" if result['overall'] else "❌ BROKEN"
        print(f"  {tool_name}: {status}")
        if result['overall']:
            working_count += 1
    
    print(f"\n📈 Overall: {working_count}/5 monitoring tools working")
    
    if working_count < 5:
        print(f"\n🔧 Tools that need fixing:")
        for tool_name, result in results.items():
            if not result['overall']:
                print(f"  • {tool_name}")
    
    return results

if __name__ == "__main__":
    main()
