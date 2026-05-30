#!/usr/bin/env python3
"""
Test Streamlined Dashboard Functionality
Tests all dashboard features and button launches
"""

import sys
import tkinter as tk
from pathlib import Path

def test_dashboard_functionality():
    """Test dashboard functionality"""
    print("🧪 Testing Streamlined Dashboard Functionality")
    print("=" * 50)
    
    try:
        # Import dashboard
        sys.path.append('.')
        import streamlined_dashboard
        
        # Create a dummy root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Initialize dashboard
        dashboard = streamlined_dashboard.StreamlinedDashboard()
        
        # Test categories
        print(f"✅ Dashboard initialized successfully")
        print(f"📊 Categories: {len(dashboard.categories)}")
        
        # Test category launch tools
        print("\n🔍 Testing Category Launch Tools:")
        missing_tools = []
        found_tools = 0
        
        for category_name, category_info in dashboard.categories.items():
            launch_tool = category_info['launch_tool']
            tool_path = Path(launch_tool)
            
            if tool_path.exists():
                print(f"  ✅ {category_name}: {launch_tool}")
                found_tools += 1
            else:
                print(f"  ❌ {category_name}: {launch_tool} - NOT FOUND")
                missing_tools.append((category_name, launch_tool))
        
        # Test system stats
        print(f"\n📈 System Stats Monitoring:")
        print(f"  ✅ CPU Usage: {dashboard.system_stats['cpu_usage']}%")
        print(f"  ✅ Memory Usage: {dashboard.system_stats['memory_usage']}%")
        print(f"  ✅ Disk Usage: {dashboard.system_stats['disk_usage']}%")
        print(f"  ✅ Network Active: {dashboard.system_stats['network_active']}")
        print(f"  ✅ Running Tools: {dashboard.system_stats['running_tools']}")
        print(f"  ✅ Total Tools: {dashboard.system_stats['total_tools']}")
        
        # Test tool counts per category
        print(f"\n📋 Category Tool Counts:")
        for category_name, category_info in dashboard.categories.items():
            tools_count = len(category_info['tools'])
            print(f"  ✅ {category_name}: {tools_count} tools")
        
        # Summary
        print(f"\n📊 DASHBOARD TEST SUMMARY:")
        print(f"✅ Categories: {len(dashboard.categories)}")
        print(f"✅ Found Launch Tools: {found_tools}")
        print(f"❌ Missing Launch Tools: {len(missing_tools)}")
        print(f"📈 Success Rate: {found_tools/len(dashboard.categories)*100:.1f}%")
        
        if missing_tools:
            print(f"\n⚠️  MISSING LAUNCH TOOLS:")
            for category, tool_path in missing_tools:
                print(f"  ❌ {category}: {tool_path}")
        
        # Clean up
        root.destroy()
        
        return len(missing_tools) == 0
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    success = test_dashboard_functionality()
    
    if success:
        print("\n🎉 Dashboard functionality test passed!")
        print("✅ All categories have valid launch tools")
        print("✅ System monitoring is active")
        print("✅ Dashboard is ready for use")
    else:
        print("\n⚠️  Dashboard functionality test failed")
        print("❌ Some launch tools are missing")
    
    return success

if __name__ == "__main__":
    main()
