#!/usr/bin/env python3
"""
Test script for the Fully Unified GUI
"""

import sys
import tkinter as tk
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("[OK] tkinter imported successfully")
    except ImportError as e:
        print(f"[ERROR] tkinter import failed: {e}")
        return False
    
    try:
        from tkinter import ttk, messagebox, scrolledtext
        print("[OK] tkinter ttk components imported successfully")
    except ImportError as e:
        print(f"[ERROR] tkinter ttk import failed: {e}")
        return False
    
    # Test optional imports
    try:
        import matplotlib.pyplot as plt
        print("[OK] matplotlib imported successfully")
    except ImportError:
        print("[WARNING] matplotlib not available - charts will be disabled")
    
    try:
        import psutil
        print("[OK] psutil imported successfully")
    except ImportError:
        print("[WARNING] psutil not available - system monitoring will be limited")
    
    # Test system imports
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        from streamlined_homelab_system import streamlined_homelab
        print("[OK] streamlined_homelab_system imported successfully")
    except ImportError as e:
        print(f"[WARNING] streamlined_homelab_system import failed: {e}")
    
    try:
        from pc_auth_system import pc_auth_system
        print("[OK] pc_auth_system imported successfully")
    except ImportError as e:
        print(f"[WARNING] pc_auth_system import failed: {e}")
    
    try:
        from integrated_homelab_with_auth import integrated_homelab
        print("[OK] integrated_homelab_with_auth imported successfully")
    except ImportError as e:
        print(f"[WARNING] integrated_homelab_with_auth import failed: {e}")
    
    try:
        from unified_launcher import unified_launcher
        print("[OK] unified_launcher imported successfully")
    except ImportError as e:
        print(f"[WARNING] unified_launcher import failed: {e}")
    
    return True

def test_tkinter():
    """Test if tkinter can create a window"""
    print("\nTesting tkinter...")
    
    try:
        root = tk.Tk()
        root.title("Test Window")
        root.geometry("300x200")
        
        label = tk.Label(root, text="GUI Test Successful!", font=('Arial', 12))
        label.pack(pady=50)
        
        button = tk.Button(root, text="Close", command=root.quit)
        button.pack(pady=20)
        
        print("[OK] tkinter window created successfully")
        print("[CLIPBOARD] Test window will appear briefly...")
        
        # Auto-close after 3 seconds
        root.after(3000, root.quit)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] tkinter test failed: {e}")
        return False

def main():
    """Main test function"""
    print("[TEST] Testing Fully Unified GUI Components")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n[ERROR] Import tests failed - GUI may not work properly")
        return False
    
    # Test tkinter
    if not test_tkinter():
        print("\n[ERROR] tkinter test failed - GUI will not work")
        return False
    
    print("\n[OK] All tests passed! GUI should work correctly.")
    print("\n[ROCKET] You can now run: python fully_unified_gui.py")
    
    return True

if __name__ == '__main__':
    main()
