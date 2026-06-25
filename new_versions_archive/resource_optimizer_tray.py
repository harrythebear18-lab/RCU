#!/usr/bin/env python3
"""
Windows 11 Resource Optimizer - System Tray Mode
Launches the resource optimizer in system tray mode for background operation.
"""

import subprocess
import sys
import os

def main():
    """Launch resource optimizer in system tray mode"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resource_optimizer_path = os.path.join(script_dir, 'resource_optimizer.py')
    
    if not os.path.exists(resource_optimizer_path):
        print("Error: resource_optimizer.py not found!")
        sys.exit(1)
    
    # Launch resource optimizer with --tray argument
    try:
        subprocess.run([sys.executable, resource_optimizer_path, '--tray'])
    except Exception as e:
        print(f"Error launching resource optimizer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
