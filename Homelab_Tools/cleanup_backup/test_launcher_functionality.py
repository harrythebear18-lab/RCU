#!/usr/bin/env python3
"""
Test Launcher Functionality
Tests that all tools are properly organized and accessible from the launcher
"""

import sys
import tkinter as tk
from pathlib import Path

def test_launcher_tools():
    """Test launcher tool organization"""
    print("🧪 Testing Launcher Functionality")
    print("=" * 50)
    
    try:
        # Import launcher
        sys.path.append('.')
        import homelab_launcher
        
        # Create a dummy root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Initialize launcher
        launcher = homelab_launcher.HomelabLauncher(root)
        
        # Count tools
        total_tools = sum(len(tools) for tools in launcher.tools.values())
        print(f"✅ Launcher initialized successfully")
        print(f"📊 Categories: {len(launcher.tools)}")
        print(f"🔧 Total tools: {total_tools}")
        
        # Test tool paths
        print("\n🔍 Testing tool paths:")
        missing_tools = []
        found_tools = 0
        
        for category, tools in launcher.tools.items():
            print(f"\n📁 {category} ({len(tools)} tools):")
            
            for tool_name, tool_info in tools.items():
                tool_path = Path(tool_info['path'])
                
                if tool_path.exists():
                    print(f"  ✅ {tool_name}")
                    found_tools += 1
                else:
                    print(f"  ❌ {tool_name} - NOT FOUND: {tool_info['path']}")
                    missing_tools.append((category, tool_name, tool_info['path']))
        
        # Summary
        print(f"\n📊 TOOL PATH SUMMARY:")
        print(f"✅ Found: {found_tools}")
        print(f"❌ Missing: {len(missing_tools)}")
        print(f"📈 Success Rate: {found_tools/total_tools*100:.1f}%")
        
        if missing_tools:
            print(f"\n⚠️  MISSING TOOLS:")
            for category, tool_name, path in missing_tools[:10]:  # Show first 10
                print(f"  ❌ {category}/{tool_name}: {path}")
            if len(missing_tools) > 10:
                print(f"  ... and {len(missing_tools) - 10} more")
        
        # Save results
        results = {
            'total_tools': total_tools,
            'found_tools': found_tools,
            'missing_tools': len(missing_tools),
            'success_rate': found_tools/total_tools*100,
            'missing_details': missing_tools
        }
        
        import json
        with open('launcher_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: launcher_test_results.json")
        
        # Clean up
        root.destroy()
        
        return len(missing_tools) == 0
        
    except Exception as e:
        print(f"❌ Error testing launcher: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_launcher_tools()
    
    if success:
        print("\n🎉 All tools are accessible from the launcher!")
    else:
        print("\n⚠️  Some tools are missing or inaccessible")
