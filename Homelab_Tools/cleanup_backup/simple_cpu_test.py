#!/usr/bin/env python3
"""
Simple CPU Monitor Test - Shows CPU chip icon only
"""

import tkinter as tk
from tkinter import ttk

def simple_cpu_test():
    """Simple test showing CPU chip icon"""
    root = tk.Tk()
    root.title("CPU Monitor Test")
    root.geometry("500x300")
    root.configure(bg='#1a1a1a')
    
    # Header with CPU chip icon
    header_frame = tk.Frame(root, bg='#1a1a1a')
    header_frame.pack(fill=tk.X, padx=20, pady=20)
    
    # CPU chip icon
    cpu_chip_text = "⚡CPU⚡"
    cpu_icon_label = tk.Label(header_frame, text=cpu_chip_text, 
                            bg='#1a1a1a', fg='#00d4ff', 
                            font=('Segoe UI', 20, 'bold'))
    cpu_icon_label.pack(side=tk.LEFT, padx=(0, 15))
    
    # Title
    title_label = tk.Label(header_frame, text="CPU Monitor & Optimizer", 
                        bg='#1a1a1a', fg='#00ff88', 
                        font=('Segoe UI', 16, 'bold'))
    title_label.pack(side=tk.LEFT)
    
    # Status
    status_frame = tk.Frame(root, bg='#2d2d2d', relief='raised', bd=1)
    status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    status_label = tk.Label(status_frame, 
                          text="✓ CPU Monitor with chip icon loaded\n✓ No Visentrix logo in CPU monitor\n✓ CPU chip icon: ⚡CPU⚡", 
                          bg='#2d2d2d', fg='#00ff88', 
                          font=('Segoe UI', 12),
                          justify='center')
    status_label.pack(expand=True)
    
    # Controls
    control_frame = tk.Frame(root, bg='#1a1a1a')
    control_frame.pack(fill=tk.X, padx=20, pady=10)
    
    ttk.Button(control_frame, text="Start Monitoring").pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Optimize CPU").pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Settings").pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

if __name__ == "__main__":
    simple_cpu_test()
