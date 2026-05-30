#!/usr/bin/env python3
"""
Test Dashboard Launch Functionality
Tests if the dashboard launch buttons are working properly
"""

import sys
import tkinter as tk
from pathlib import Path

def test_dashboard_launch():
    """Test dashboard launch functionality"""
    print("🧪 Testing Dashboard Launch Functionality")
    print("=" * 50)
    
    try:
        # Import dashboard
        sys.path.append('.')
        import homelab_dashboard
        
        # Create a dummy root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Initialize dashboard
        dashboard = homelab_dashboard.HomelabDashboard(root)
        
        # Test tool availability
        print(f"📊 Total tools in dashboard: {len(dashboard.tools)}")
        
        # Check tool paths and availability
        available_tools = 0
        missing_tools = []
        
        for tool_name, tool_info in dashboard.tools.items():
            tool_path = Path(tool_info['path'])
            
            if tool_path.exists():
                available_tools += 1
                print(f"✅ {tool_name}: {tool_info['path']}")
            else:
                missing_tools.append((tool_name, tool_info['path']))
                print(f"❌ {tool_name}: {tool_info['path']} - NOT FOUND")
        
        print(f"\n📈 Tool Availability Summary:")
        print(f"✅ Available: {available_tools}")
        print(f"❌ Missing: {len(missing_tools)}")
        print(f"📊 Success Rate: {available_tools/len(dashboard.tools)*100:.1f}%")
        
        # Test launch method for a simple tool
        if available_tools > 0:
            print(f"\n🚀 Testing launch method...")
            
            # Find a simple tool to test
            test_tool = None
            for tool_name, tool_info in dashboard.tools.items():
                if tool_info['path'].endswith('.py') and Path(tool_info['path']).exists():
                    test_tool = (tool_name, tool_info)
                    break
            
            if test_tool:
                tool_name, tool_info = test_tool
                print(f"Testing launch for: {tool_name}")
                
                # Test the launch method (but don't actually launch)
                try:
                    # Check if the launch method exists and is callable
                    if hasattr(dashboard, 'launch_tool'):
                        print(f"✅ launch_tool method exists")
                        
                        # Check if tool is marked as available
                        if tool_info.get('available', False):
                            print(f"✅ Tool is marked as available")
                        else:
                            print(f"❌ Tool is not marked as available")
                            
                        # Check if tool path exists
                        if Path(tool_info['path']).exists():
                            print(f"✅ Tool path exists")
                        else:
                            print(f"❌ Tool path does not exist")
                            
                    else:
                        print(f"❌ launch_tool method does not exist")
                        
                except Exception as e:
                    print(f"❌ Error testing launch method: {e}")
            else:
                print(f"❌ No suitable test tool found")
        
        # Clean up
        root.destroy()
        
        return len(missing_tools) == 0
        
    except Exception as e:
        print(f"❌ Error testing dashboard launch: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    success = test_dashboard_launch()
    
    if success:
        print("\n🎉 Dashboard launch functionality test passed!")
    else:
        print("\n⚠️  Dashboard launch functionality test failed")
    
    return success

if __name__ == "__main__":
    main()
