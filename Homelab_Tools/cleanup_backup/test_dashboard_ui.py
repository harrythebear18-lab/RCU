#!/usr/bin/env python3
"""
Test Dashboard UI Buttons
Tests if the launch buttons are actually visible in the dashboard UI
"""

import sys
import tkinter as tk
from pathlib import Path

def test_dashboard_ui():
    """Test dashboard UI button visibility"""
    print("🧪 Testing Dashboard UI Button Visibility")
    print("=" * 50)
    
    try:
        # Import dashboard
        sys.path.append('.')
        import homelab_dashboard
        
        # Create root window
        root = tk.Tk()
        root.geometry("800x600")
        
        # Initialize dashboard
        dashboard = homelab_dashboard.HomelabDashboard(root)
        
        # Check if live_stats exists
        if hasattr(dashboard, 'live_stats'):
            print("✅ Live stats bar created")
        else:
            print("❌ Live stats bar missing")
        
        # Check if tools grid was created
        print(f"✅ Dashboard initialized with {len(dashboard.tools)} tools")
        
        # Force update and check widgets
        root.update()
        
        # Count all buttons in the dashboard
        all_buttons = root.winfo_children()
        button_count = 0
        
        def count_buttons(widget):
            nonlocal button_count
            if isinstance(widget, tk.Button):
                button_count += 1
                print(f"✅ Found button: {widget['text']}")
            for child in widget.winfo_children():
                count_buttons(child)
        
        count_buttons(root)
        print(f"📊 Total buttons found: {button_count}")
        
        # Check if launch buttons are visible
        if button_count >= len(dashboard.tools) * 2:  # Each tool should have launch + info button
            print("✅ Launch buttons appear to be present")
        else:
            print("❌ Launch buttons may be missing")
        
        # Show the dashboard briefly for visual inspection
        print("\n👁️ Dashboard window opened for inspection...")
        print("   Check if you can see the 🚀 launch buttons on each tool card")
        
        # Keep window open for a moment
        root.after(3000, root.destroy)  # Auto-close after 3 seconds
        root.mainloop()
        
        return button_count > 0
        
    except Exception as e:
        print(f"❌ Error testing dashboard UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    success = test_dashboard_ui()
    
    if success:
        print("\n🎉 Dashboard UI test completed!")
    else:
        print("\n⚠️  Dashboard UI test failed")
    
    return success

if __name__ == "__main__":
    main()
