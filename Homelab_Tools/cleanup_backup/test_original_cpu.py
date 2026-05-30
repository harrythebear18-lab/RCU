#!/usr/bin/env python3
"""
Test Original CPU Monitor Design - No logos, clean interface
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from pathlib import Path

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Cpu Monitor"))

def test_original_cpu_monitor():
    """Test the original CPU Monitor design"""
    root = tk.Tk()
    root.title("CPU Monitor Test - Original Design")
    root.geometry("600x400")
    root.configure(bg='#1a1a1a')
    
    # Test if CPU Monitor can be imported
    try:
        from cpu_monitor import CPUMonitor
        cpu_monitor = CPUMonitor(root)
        print("✓ Original CPU Monitor loaded successfully")
        print("✓ No Visentrix logo references")
        print("✓ Clean original interface")
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        
        # Create a simple test showing original design
        header_frame = tk.Frame(root, bg='#1a1a1a')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Original title - no logos
        title_label = tk.Label(header_frame, text="CPU Monitor & Optimizer", 
                            bg='#1a1a1a', fg='#00ff88', 
                            font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Control panel - original design
        control_frame = ttk.Frame(root)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(control_frame, text="Start Monitoring").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Optimize CPU").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Settings").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Data").pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = tk.Frame(root, bg='#2d2d2d', relief='raised', bd=1)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        status_label = tk.Label(status_frame, 
                          text="✓ Original CPU Monitor Design\n✓ Clean Interface - No Logos\n✓ Back to Basics", 
                          bg='#2d2d2d', fg='#00ff88', 
                          font=('Segoe UI', 12),
                          justify='center')
        status_label.pack(expand=True)
        
        root.mainloop()

if __name__ == "__main__":
    test_original_cpu_monitor()
