#!/usr/bin/env python3
"""
Debug Dashboard Buttons
Simple test to identify why dashboard buttons are not working
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from pathlib import Path

def test_simple_button():
    """Test a simple button to ensure tkinter is working"""
    root = tk.Tk()
    root.title("Button Test")
    root.geometry("300x200")
    
    def on_button_click():
        messagebox.showinfo("Test", "Button clicked successfully!")
        print("Button was clicked!")
    
    # Simple test button
    btn = tk.Button(root, text="Test Button", command=on_button_click,
                    bg="#00ff88", fg="white", font=("Arial", 12, "bold"))
    btn.pack(pady=50)
    
    root.mainloop()

def test_dashboard_button():
    """Test dashboard-style button with lambda"""
    root = tk.Tk()
    root.title("Dashboard Button Test")
    root.geometry("400x300")
    
    def launch_tool(tool_name, tool_path):
        messagebox.showinfo("Launch", f"Launching {tool_name}")
        print(f"Would launch: {tool_path}")
        # Try to actually launch something
        try:
            if tool_path.endswith('.py') and Path(tool_path).exists():
                subprocess.Popen(['python', tool_path])
                messagebox.showinfo("Success", f"{tool_name} launched!")
            else:
                messagebox.showerror("Error", f"Tool not found: {tool_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch: {e}")
    
    # Test with actual tool
    tool_name = "CPU Monitor"
    tool_path = "CPU Monitor/cpu_monitor.py"
    
    # Create dashboard-style button
    btn = tk.Button(root, text=f"🚀 Launch {tool_name}", 
                    command=lambda tn=tool_name, tp=tool_path: launch_tool(tn, tp),
                    bg="#00ff88", fg="white", font=("Arial", 10, "bold"))
    btn.pack(pady=50)
    
    # Add status label
    status = tk.Label(root, text="Click the button to test")
    status.pack()
    
    root.mainloop()

def main():
    """Run button tests"""
    print("🧪 Testing Dashboard Button Functionality")
    print("=" * 50)
    
    # Test 1: Simple button
    print("Test 1: Simple button functionality...")
    test_simple_button()
    
    # Test 2: Dashboard-style button
    print("Test 2: Dashboard-style button with lambda...")
    test_dashboard_button()
    
    print("✅ Button tests completed")

if __name__ == "__main__":
    main()
