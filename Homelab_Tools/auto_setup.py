#!/usr/bin/env python3
"""
Homelab Tools - One-Click Auto Setup
This script automatically configures the entire homelab environment
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class HomelabSetupGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homelab Tools - Auto Setup")
        self.root.geometry("600x400")
        self.root.configure(bg='#1e1e1e')
        
        # Setup GUI
        self.setup_gui()
        
        # Start setup automatically
        self.root.after(1000, self.start_setup)
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="Homelab Tools - Auto Setup", 
            font=("Segoe UI", 16, "bold"),
            fg='#00ff00',
            bg='#1e1e1e'
        )
        title_label.pack(pady=20)
        
        # Progress frame
        progress_frame = tk.Frame(self.root, bg='#1e1e1e')
        progress_frame.pack(pady=20, padx=20, fill='x')
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame, 
            length=560, 
            mode='indeterminate'
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            progress_frame,
            text="Initializing setup...",
            font=("Segoe UI", 10),
            fg='#ffffff',
            bg='#1e1e1e'
        )
        self.status_label.pack()
        
        # Log text area
        log_frame = tk.Frame(self.root, bg='#1e1e1e')
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            bg='#2d2d2d',
            fg='#00ff00',
            font=("Consolas", 9),
            wrap='word'
        )
        self.log_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(pady=10)
        
        # Launch button (initially disabled)
        self.launch_button = tk.Button(
            button_frame,
            text="Launch Homelab Tools",
            font=("Segoe UI", 10, "bold"),
            bg='#00ff00',
            fg='#000000',
            state='disabled',
            command=self.launch_homelab
        )
        self.launch_button.pack(side='left', padx=5)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            font=("Segoe UI", 10),
            bg='#ff0000',
            fg='#ffffff',
            command=self.root.quit
        )
        exit_button.pack(side='left', padx=5)
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.root.update()
    
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
        self.root.update()
    
    def run_command(self, cmd, show_output=True):
        """Run a command and return result"""
        try:
            if show_output:
                self.log(f"Running: {cmd}")
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=os.getcwd()
            )
            
            if show_output and result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            
            if result.stderr and show_output:
                self.log(f"Error: {result.stderr.strip()}")
            
            return result.returncode == 0
        except Exception as e:
            self.log(f"Exception: {e}")
            return False
    
    def check_python(self):
        """Check Python installation"""
        self.update_status("Checking Python installation...")
        self.log("Checking Python installation...")
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.log(f"✓ Python {version.major}.{version.minor}.{version.micro} found")
            return True
        else:
            self.log(f"✗ Python {version.major}.{version.minor}.{version.micro} found (need 3.8+)")
            messagebox.showerror("Python Required", "Python 3.8 or higher is required!")
            return False
    
    def check_git(self):
        """Check Git installation"""
        self.update_status("Checking Git installation...")
        self.log("Checking Git installation...")
        
        if self.run_command("git --version", show_output=False):
            self.log("✓ Git found")
            return True
        else:
            self.log("✗ Git not found")
            self.log("Installing Git...")
            if self.run_command("winget install Git.Git --accept-package-agreements --accept-source-agreements"):
                self.log("✓ Git installed")
                return True
            else:
                self.log("✗ Git installation failed")
                messagebox.showerror("Git Required", "Git is required! Please install manually.")
                return False
    
    def setup_git_lfs(self):
        """Setup Git LFS"""
        self.update_status("Setting up Git LFS...")
        self.log("Setting up Git LFS...")
        
        # Try to use bundled git-lfs
        if os.path.exists("git-lfs.exe"):
            self.log("Using bundled Git LFS...")
            if self.run_command(".\\git-lfs.exe install"):
                self.log("✓ Git LFS installed from bundle")
                return True
        
        # Try to install via winget
        self.log("Installing Git LFS...")
        if self.run_command("winget install GitHub.GitLFS --accept-package-agreements --accept-source-agreements"):
            if self.run_command("git lfs install"):
                self.log("✓ Git LFS installed")
                return True
        
        self.log("✗ Git LFS installation failed")
        return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.update_status("Installing Python dependencies...")
        self.log("Installing Python dependencies...")
        
        # Upgrade pip
        self.log("Upgrading pip...")
        self.run_command("python -m pip install --upgrade pip")
        
        # Install from requirements.txt
        self.log("Installing from requirements.txt...")
        if self.run_command("pip install -r requirements.txt"):
            self.log("✓ Dependencies installed")
            return True
        else:
            self.log("✗ Dependencies installation failed")
            return False
    
    def setup_directories(self):
        """Create necessary directories"""
        self.update_status("Setting up directories...")
        self.log("Creating directories...")
        
        directories = ["logs", "cache", "temp", "performance_data", "monitoring_data"]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.log(f"✓ Created {directory} directory")
        
        return True
    
    def pull_lfs_objects(self):
        """Pull LFS objects"""
        self.update_status("Downloading large files...")
        self.log("Downloading LFS objects...")
        
        if self.run_command("git lfs pull"):
            self.log("✓ LFS objects downloaded")
            return True
        else:
            self.log("⚠ Some LFS objects may not be available")
            return False
    
    def create_shortcuts(self):
        """Create desktop shortcuts"""
        self.update_status("Creating shortcuts...")
        self.log("Creating desktop shortcut...")
        
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Homelab Tools.lnk")
            target = os.path.join(os.getcwd(), "homelab_launcher.py")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = os.getcwd()
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            self.log("✓ Desktop shortcut created")
            return True
        except Exception as e:
            self.log(f"⚠ Could not create desktop shortcut: {e}")
            return False
    
    def test_functionality(self):
        """Test basic functionality"""
        self.update_status("Testing functionality...")
        self.log("Testing basic functionality...")
        
        try:
            import psutil
            import matplotlib
            import numpy
            
            self.log("✓ Core dependencies working")
            return True
        except ImportError as e:
            self.log(f"✗ Core dependencies test failed: {e}")
            return False
    
    def setup_complete(self):
        """Setup completion"""
        self.update_status("Setup complete!")
        self.log("=" * 50)
        self.log("SETUP COMPLETE!")
        self.log("=" * 50)
        self.log("You can now launch Homelab Tools!")
        
        # Enable launch button
        self.launch_button.config(state='normal')
        
        # Show completion message
        messagebox.showinfo(
            "Setup Complete", 
            "Homelab Tools setup is complete!\n\nClick 'Launch Homelab Tools' to start."
        )
    
    def launch_homelab(self):
        """Launch Homelab Tools"""
        self.log("Launching Homelab Tools...")
        try:
            subprocess.Popen([sys.executable, "homelab_launcher.py"])
            self.log("✓ Homelab Tools launched")
            self.root.quit()
        except Exception as e:
            self.log(f"✗ Failed to launch: {e}")
            messagebox.showerror("Launch Failed", f"Failed to launch Homelab Tools: {e}")
    
    def setup_thread(self):
        """Setup thread function"""
        try:
            # Check requirements
            if not self.check_python():
                return
            
            if not self.check_git():
                return
            
            # Setup Git LFS
            self.setup_git_lfs()
            
            # Install dependencies
            if not self.install_dependencies():
                return
            
            # Setup directories
            self.setup_directories()
            
            # Pull LFS objects
            self.pull_lfs_objects()
            
            # Create shortcuts
            self.create_shortcuts()
            
            # Test functionality
            self.test_functionality()
            
            # Complete
            self.setup_complete()
            
        except Exception as e:
            self.log(f"Setup failed: {e}")
            messagebox.showerror("Setup Failed", f"Setup failed: {e}")
        finally:
            self.progress.stop()
    
    def start_setup(self):
        """Start the setup process"""
        self.log("Starting Homelab Tools setup...")
        self.progress.start()
        
        # Run setup in separate thread
        thread = threading.Thread(target=self.setup_thread, daemon=True)
        thread.start()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting Homelab Tools Auto Setup...")
    
    # Check if we're in the right directory
    if not os.path.exists("homelab_launcher.py"):
        print("Error: homelab_launcher.py not found!")
        print("Please run this script from the Homelab Tools directory.")
        sys.exit(1)
    
    # Check if GUI is available
    try:
        import tkinter
        # Run GUI setup
        gui = HomelabSetupGUI()
        gui.run()
    except ImportError:
        # Run command line setup
        print("GUI not available, running command line setup...")
        run_command_line_setup()

def run_command_line_setup():
    """Command line setup function"""
    print("Homelab Tools - Command Line Setup")
    print("=" * 40)
    
    # Simple command line setup
    commands = [
        ("Checking Python", "python --version"),
        ("Checking Git", "git --version"),
        ("Installing Git LFS", "git lfs install"),
        ("Upgrading pip", "python -m pip install --upgrade pip"),
        ("Installing dependencies", "pip install -r requirements.txt"),
        ("Pulling LFS objects", "git lfs pull")
    ]
    
    for description, command in commands:
        print(f"\n{description}...")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {description} completed")
            else:
                print(f"✗ {description} failed: {result.stderr}")
        except Exception as e:
            print(f"✗ {description} failed: {e}")
    
    print("\nSetup complete! Run: python homelab_launcher.py")

if __name__ == "__main__":
    main()
