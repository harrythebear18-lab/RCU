#!/usr/bin/env python3
"""
Visentrix Homelab Tools Launcher
Professional launcher with Visentrix branding for all homelab tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
import sys
from pathlib import Path
from PIL import Image, ImageTk
import json

class VisentrixLauncher:
    """Main Visentrix launcher for all homelab tools"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Visentrix Homelab Tools Launcher")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Logo paths
        self.logo_paths = {
            'primary': 'D:\\Home Projects\\dx11(homelab)\\logo.png',
            'secondary': 'D:\\Home Projects\\dx11(homelab)\\logo1.png'
        }
        self.logo_images = {}
        
        # Tool categories and paths
        self.tool_categories = {
            'Monitoring': {
                'CPU Monitor': 'Cpu Monitor/cpu_monitor.py',
                'GPU Monitor': 'Gpu Monitor/gpu_monitor.py', 
                'Network Monitor': 'Network Monitor/network_monitor.py',
                'RAM Monitor': 'Ram clean up/ram_monitor.py'
            },
            'Utilities': {
                'Storage Manager': 'Storage Management/storage_manager.py',
                'Backup System': 'Backup System/backup_manager.py',
                'Power Manager': 'Power Management/power_manager.py',
                'RAM Cleaner': 'Ram clean up/ram_cleaner.py'
            },
            'Networking': {
                'RDMA Tools': 'RDMA/rdma_tools.py',
                'Subnet Portal': 'Subnet Portal/subnet_portal.py',
                'Network Discovery': 'Core Services/windows_network_discovery.py'
            },
            'Computing': {
                'Compute Sharing': 'Compute Sharing/compute_client.py',
                'Container Manager': 'Container Manager/container_manager.py',
                'Media Server': 'Media Server/media_server_manager.py',
                'Hybrid Compute': 'Hybrid Compute/hybrid_client.py'
            },
            'Security': {
                'Advanced Security': 'Core Services/advanced_security.py',
                'Auth Service': 'Core Services/auth_service.py',
                'Automation Framework': 'Core Services/automation_framework.py'
            },
            'Portals': {
                'Unified Dashboard': 'Core Services/unified_dashboard.py',
                'Homelab Portal': 'Core Services/homelab_portal.py',
                'Web Dashboard': 'Web Dashboard/web_dashboard.py'
            }
        }
        
        # Tool status tracking
        self.tool_status = {}
        self.running_tools = {}
        
        # Load logos and setup UI
        self.load_logo_images()
        self.setup_ui()
        
        # Start status monitoring
        self.start_status_monitoring()
    
    def load_logo_images(self):
        """Load Visentrix logo images"""
        try:
            # Load primary logo
            if os.path.exists(self.logo_paths['primary']):
                logo_img = Image.open(self.logo_paths['primary'])
                logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)
                self.logo_images['primary'] = ImageTk.PhotoImage(logo_img)
            
            # Load secondary logo
            if os.path.exists(self.logo_paths['secondary']):
                logo_img = Image.open(self.logo_paths['secondary'])
                logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.logo_images['secondary'] = ImageTk.PhotoImage(logo_img)
                
        except Exception as e:
            print(f"Warning: Failed to load logo images: {e}")
    
    def setup_ui(self):
        """Setup the main launcher UI"""
        # Create main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with logo and title
        self.create_header(main_container)
        
        # Tool categories notebook
        self.create_tool_categories(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create header with Visentrix branding"""
        header_frame = tk.Frame(parent, bg='#2d2d2d', relief=tk.RAISED, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo and title section
        title_section = tk.Frame(header_frame, bg='#2d2d2d')
        title_section.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Add Visentrix logo
        if 'primary' in self.logo_images:
            logo_label = tk.Label(title_section, image=self.logo_images['primary'], bg='#2d2d2d')
            logo_label.image = self.logo_images['primary']  # Keep reference
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Title
        title_label = tk.Label(
            title_section, 
            text="Visentrix Homelab Tools", 
            bg='#2d2d2d', 
            fg='#00ff88', 
            font=('Segoe UI', 20, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(
            title_section,
            text="Professional System Management Suite",
            bg='#2d2d2d',
            fg='#b0b0b0',
            font=('Segoe UI', 10)
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Quick actions section
        actions_section = tk.Frame(header_frame, bg='#2d2d2d')
        actions_section.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Quick action buttons
        ttk.Button(
            actions_section, 
            text="🚀 Launch All", 
            command=self.launch_all_tools
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_section, 
            text="🔄 Refresh", 
            command=self.refresh_tool_status
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_section, 
            text="ℹ️ About", 
            command=self.show_about
        ).pack(side=tk.LEFT, padx=5)
    
    def create_tool_categories(self, parent):
        """Create tool categories with notebook"""
        # Create notebook for categories
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a')
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Create tabs for each category
        self.category_frames = {}
        self.tool_buttons = {}
        
        for category_name, tools in self.tool_categories.items():
            # Create tab frame
            tab_frame = tk.Frame(self.notebook, bg='#1a1a1a')
            self.notebook.add(tab_frame, text=category_name)
            self.category_frames[category_name] = tab_frame
            
            # Create tool grid for this category
            self.create_tool_grid(tab_frame, category_name, tools)
    
    def create_tool_grid(self, parent, category_name, tools):
        """Create grid of tool buttons for a category"""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg='#1a1a1a', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create tool cards in grid
        row, col = 0, 0
        max_cols = 3
        
        for tool_name, tool_path in tools.items():
            self.create_tool_card(scrollable_frame, tool_name, tool_path, category_name, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def create_tool_card(self, parent, tool_name, tool_path, category_name, row, col):
        """Create individual tool card"""
        # Card frame
        card_frame = tk.Frame(
            parent, 
            bg='#2d2d2d', 
            relief=tk.RAISED, 
            bd=1,
            padx=15,
            pady=15
        )
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        # Tool icon/logo
        if 'secondary' in self.logo_images:
            icon_label = tk.Label(card_frame, image=self.logo_images['secondary'], bg='#2d2d2d')
            icon_label.image = self.logo_images['secondary']  # Keep reference
            icon_label.pack(pady=(0, 10))
        
        # Tool name
        name_label = tk.Label(
            card_frame,
            text=tool_name,
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Segoe UI', 12, 'bold')
        )
        name_label.pack(pady=(0, 5))
        
        # Tool status
        status_frame = tk.Frame(card_frame, bg='#2d2d2d')
        status_frame.pack(pady=(0, 10))
        
        status_label = tk.Label(
            status_frame,
            text="● Ready",
            bg='#2d2d2d',
            fg='#00ff88',
            font=('Segoe UI', 9)
        )
        status_label.pack()
        
        # Store status label reference
        self.tool_status[tool_name] = status_label
        
        # Action buttons frame
        button_frame = tk.Frame(card_frame, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Launch button
        launch_btn = tk.Button(
            button_frame,
            text="🚀 Launch",
            bg='#00ff88',
            fg='#1a1a1a',
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
            command=lambda tn=tool_name, tp=tool_path: self.launch_tool(tn, tp)
        )
        launch_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Info button
        info_btn = tk.Button(
            button_frame,
            text="ℹ️",
            bg='#0078ff',
            fg='#ffffff',
            font=('Segoe UI', 9),
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=5,
            command=lambda tn=tool_name, tp=tool_path: self.show_tool_info(tn, tp)
        )
        info_btn.pack(side=tk.LEFT)
        
        # Store button reference
        if category_name not in self.tool_buttons:
            self.tool_buttons[category_name] = {}
        self.tool_buttons[category_name][tool_name] = {
            'launch_btn': launch_btn,
            'info_btn': info_btn,
            'status_label': status_label
        }
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = tk.Frame(parent, bg='#2d2d2d', relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="Visentrix Launcher Ready",
            bg='#2d2d2d',
            fg='#00ff88',
            font=('Segoe UI', 9),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Running tools counter
        self.running_counter = tk.Label(
            status_frame,
            text="Running: 0",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Segoe UI', 9),
            anchor=tk.E
        )
        self.running_counter.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def launch_tool(self, tool_name, tool_path):
        """Launch a specific tool"""
        try:
            # Check if tool exists
            if not os.path.exists(tool_path):
                messagebox.showerror("Tool Not Found", f"Tool not found: {tool_path}")
                return
            
            # Check if already running
            if tool_name in self.running_tools:
                messagebox.showwarning("Already Running", f"{tool_name} is already running!")
                return
            
            # Launch the tool
            process = subprocess.Popen(['python', tool_path])
            self.running_tools[tool_name] = process
            
            # Update status
            self.update_tool_status(tool_name, "Running", '#ffaa00')
            self.status_label.config(text=f"Launched: {tool_name}")
            self.update_running_counter()
            
            # Monitor process
            threading.Thread(
                target=self.monitor_tool_process,
                args=(tool_name, process),
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("Launch Failed", f"Failed to launch {tool_name}: {str(e)}")
            self.update_tool_status(tool_name, "Error", '#ff4444')
    
    def monitor_tool_process(self, tool_name, process):
        """Monitor tool process and update status when it exits"""
        try:
            process.wait()
            # Tool has exited
            if tool_name in self.running_tools:
                del self.running_tools[tool_name]
            self.update_tool_status(tool_name, "Ready", '#00ff88')
            self.update_running_counter()
        except:
            pass
    
    def update_tool_status(self, tool_name, status, color):
        """Update tool status display"""
        if tool_name in self.tool_status:
            self.tool_status[tool_name].config(
                text=f"● {status}",
                fg=color
            )
    
    def update_running_counter(self):
        """Update running tools counter"""
        count = len(self.running_tools)
        self.running_counter.config(text=f"Running: {count}")
    
    def launch_all_tools(self):
        """Launch all available tools"""
        launched = 0
        failed = 0
        
        for category_name, tools in self.tool_categories.items():
            for tool_name, tool_path in tools.items():
                try:
                    if os.path.exists(tool_path) and tool_name not in self.running_tools:
                        process = subprocess.Popen(['python', tool_path])
                        self.running_tools[tool_name] = process
                        self.update_tool_status(tool_name, "Running", '#ffaa00')
                        launched += 1
                        
                        # Monitor process
                        threading.Thread(
                            target=self.monitor_tool_process,
                            args=(tool_name, process),
                            daemon=True
                        ).start()
                    else:
                        failed += 1
                except:
                    failed += 1
        
        self.update_running_counter()
        messagebox.showinfo(
            "Launch All Results", 
            f"Launched: {launched} tools\nFailed: {failed} tools"
        )
    
    def refresh_tool_status(self):
        """Refresh status of all tools"""
        self.status_label.config(text="Refreshing tool status...")
        
        for category_name, tools in self.tool_categories.items():
            for tool_name, tool_path in tools.items():
                if tool_name not in self.running_tools:
                    if os.path.exists(tool_path):
                        self.update_tool_status(tool_name, "Ready", '#00ff88')
                    else:
                        self.update_tool_status(tool_name, "Missing", '#ff4444')
        
        self.status_label.config(text="Tool status refreshed")
    
    def show_tool_info(self, tool_name, tool_path):
        """Show information about a tool"""
        info_window = tk.Toplevel(self.root)
        info_window.title(f"Tool Info: {tool_name}")
        info_window.geometry("400x300")
        info_window.configure(bg='#2d2d2d')
        
        # Logo
        if 'secondary' in self.logo_images:
            logo_label = tk.Label(info_window, image=self.logo_images['secondary'], bg='#2d2d2d')
            logo_label.image = self.logo_images['secondary']
            logo_label.pack(pady=10)
        
        # Tool name
        name_label = tk.Label(
            info_window,
            text=tool_name,
            bg='#2d2d2d',
            fg='#00ff88',
            font=('Segoe UI', 14, 'bold')
        )
        name_label.pack(pady=5)
        
        # Tool path
        path_label = tk.Label(
            info_window,
            text=f"Path: {tool_path}",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Segoe UI', 10)
        )
        path_label.pack(pady=5)
        
        # Status
        status = "Running" if tool_name in self.running_tools else "Ready"
        status_color = '#ffaa00' if tool_name in self.running_tools else '#00ff88'
        
        status_label = tk.Label(
            info_window,
            text=f"Status: {status}",
            bg='#2d2d2d',
            fg=status_color,
            font=('Segoe UI', 10)
        )
        status_label.pack(pady=5)
        
        # Close button
        close_btn = tk.Button(
            info_window,
            text="Close",
            bg='#ff4444',
            fg='#ffffff',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            command=info_window.destroy
        )
        close_btn.pack(pady=20)
    
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Visentrix Homelab Tools")
        about_window.geometry("500x400")
        about_window.configure(bg='#2d2d2d')
        
        # Logo
        if 'primary' in self.logo_images:
            logo_label = tk.Label(about_window, image=self.logo_images['primary'], bg='#2d2d2d')
            logo_label.image = self.logo_images['primary']
            logo_label.pack(pady=20)
        
        # Title
        title_label = tk.Label(
            about_window,
            text="Visentrix Homelab Tools",
            bg='#2d2d2d',
            fg='#00ff88',
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=5)
        
        # Version
        version_label = tk.Label(
            about_window,
            text="Version 2.0.0",
            bg='#2d2d2d',
            fg='#ffffff',
            font=('Segoe UI', 12)
        )
        version_label.pack(pady=5)
        
        # Description
        desc_text = """
Professional system management suite for homelab environments.
Features advanced monitoring, resource sharing, and automation capabilities.

Categories:
• Monitoring - Real-time system monitoring
• Utilities - System maintenance tools  
• Networking - Network management and discovery
• Computing - Distributed computing resources
• Security - Advanced security and automation
• Portals - Unified dashboard and portal access

© 2024 Visentrix Technologies
        """
        
        desc_label = tk.Label(
            about_window,
            text=desc_text,
            bg='#2d2d2d',
            fg='#b0b0b0',
            font=('Segoe UI', 10),
            justify=tk.LEFT
        )
        desc_label.pack(pady=20, padx=20)
        
        # Close button
        close_btn = tk.Button(
            about_window,
            text="Close",
            bg='#00ff88',
            fg='#1a1a1a',
            font=('Segoe UI', 10, 'bold'),
            relief=tk.FLAT,
            command=about_window.destroy
        )
        close_btn.pack(pady=10)
    
    def start_status_monitoring(self):
        """Start background status monitoring"""
        def monitor():
            while True:
                try:
                    # Update running counter
                    self.update_running_counter()
                    time.sleep(2)
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        launcher = VisentrixLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\nLauncher stopped by user")
    except Exception as e:
        messagebox.showerror("Launcher Error", f"Failed to start launcher: {str(e)}")

if __name__ == "__main__":
    main()
