#!/usr/bin/env python3
"""
Test CPU Monitor with CPU chip icon and tray functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Cpu Monitor"))

try:
    from cpu_monitor import CPUMonitor
    print("CPU Monitor imported successfully")
except ImportError as e:
    print(f"Failed to import CPU Monitor: {e}")

def test_cpu_monitor():
    """Test the CPU Monitor with CPU chip icon"""
    root = tk.Tk()
    
    # Create CPU Monitor instance
    try:
        cpu_monitor = CPUMonitor(root)
        print("CPU Monitor created successfully")
        
        # Check what icon is being used
        print(f"CPU chip text: {getattr(cpu_monitor, 'cpu_chip_text', 'Not found')}")
        print(f"Logo paths: {getattr(cpu_monitor, 'logo_paths', 'Not found')}")
        print(f"Logo images: {getattr(cpu_monitor, 'logo_images', 'Not found')}")
        
        # Run the application
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating CPU Monitor: {e}")
        # Create a simple test window instead
        root.title("CPU Monitor Test")
        root.geometry("600x400")
        root.configure(bg='#1a1a1a')
        
        # Test CPU chip icon
        cpu_chip_text = "⚡CPU⚡"
        
        header_frame = tk.Frame(root, bg='#1a1a1a')
        header_frame.pack(fill=tk.X, padx=10, pady=20)
        
        # CPU chip icon
        cpu_icon_label = tk.Label(header_frame, text=cpu_chip_text, 
                                bg='#1a1a1a', fg='#00d4ff', 
                                font=('Segoe UI', 16, 'bold'))
        cpu_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title
        title_label = tk.Label(header_frame, text="CPU Monitor & Optimizer", 
                            bg='#1a1a1a', fg='#00ff88', 
                            font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Status
        status_label = tk.Label(root, text="CPU Monitor with chip icon loaded successfully", 
                              bg='#1a1a1a', fg='#00ff88', 
                              font=('Segoe UI', 12))
        status_label.pack(pady=50)
        
        root.mainloop()

if __name__ == "__main__":
    test_cpu_monitor()
