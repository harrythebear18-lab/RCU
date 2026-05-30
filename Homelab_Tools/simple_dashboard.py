#!/usr/bin/env python3
"""
Simple Working Dashboard
Clean dashboard with working launch buttons
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from pathlib import Path
import psutil
import threading
import time

class SimpleDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homelab Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444'
        }
        
        # Working tools properly categorized
        self.tools = {
            # MONITORING TOOLS
            "CPU Monitor": {
                "path": "CPU Monitor/cpu_monitor.py",
                "icon": "💻",
                "description": "Monitor CPU usage and performance",
                "color": self.colors['primary']
            },
            "GPU Monitor": {
                "path": "GPU Monitor/gpu_monitor.py", 
                "icon": "🎮",
                "description": "Monitor GPU usage and temperature",
                "color": self.colors['secondary']
            },
            "Network Monitor": {
                "path": "Network Monitor/network_monitor.py",
                "icon": "🌐",
                "description": "Monitor network activity and bandwidth",
                "color": self.colors['primary']
            },
            "Storage Monitor": {
                "path": "Storage Monitor/storage_monitor.py",
                "icon": "💾",
                "description": "Monitor disk space and I/O",
                "color": self.colors['secondary']
            },
            "Memory Monitor": {
                "path": "Memory Monitor/ram_monitor_gui.py",
                "icon": "🧠",
                "description": "Monitor RAM usage and memory",
                "color": self.colors['primary']
            },
            
            # CORE SERVICES
            "Web Dashboard": {
                "path": "Core Services/web_dashboard.py",
                "icon": "📊",
                "description": "Web-based monitoring dashboard",
                "color": self.colors['secondary']
            },
            "VPN Gateway": {
                "path": "VPN Gateway/vpn_gateway.py",
                "icon": "🔐",
                "description": "VPN connection management",
                "color": self.colors['primary']
            },
            
            # ADVANCED TOOLS
            "RDMA Desktop": {
                "path": "RDMA Desktop App/rdma_desktop_app.py",
                "icon": "🔌",
                "description": "RDMA desktop application",
                "color": self.colors['secondary']
            },
            
            # SHARING TOOLS (separate category)
            "RAM Sharing": {
                "path": "RAM_Sharing_GUI.py",
                "icon": "�",
                "description": "RAM sharing interface",
                "color": "#ff9900"  # Orange for sharing
            },
            
            # SYSTEM TOOLS
            "System Launcher": {
                "path": "homelab_launcher.py",
                "icon": "�",
                "description": "Main system launcher",
                "color": self.colors['primary']
            },
            "System Audit": {
                "path": "comprehensive_chunked_audit.py",
                "icon": "🔍",
                "description": "Comprehensive system audit",
                "color": self.colors['secondary']
            },
            
            # UTILITIES
            "Auto Connect": {
                "path": "Auto_Connect_Launcher.bat",
                "icon": "🔗",
                "description": "Auto connection launcher",
                "color": "#9966ff"  # Purple for utilities
            }
        }
        
        self.running_processes = {}
        self.create_widgets()
        self.start_live_updates()
        
    def create_widgets(self):
        """Create dashboard widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🏠 Homelab Dashboard", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT, pady=20)
        
        # Live stats
        self.stats_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        self.stats_frame.pack(side=tk.RIGHT, pady=20)
        
        self.cpu_label = tk.Label(self.stats_frame, text="CPU: 0%", 
                                  font=('Arial', 12), 
                                  fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.cpu_label.pack(side=tk.LEFT, padx=10)
        
        self.ram_label = tk.Label(self.stats_frame, text="RAM: 0%", 
                                  font=('Arial', 12), 
                                  fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.ram_label.pack(side=tk.LEFT, padx=10)
        
        self.running_label = tk.Label(self.stats_frame, text="Running: 0", 
                                     font=('Arial', 12), 
                                     fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.running_label.pack(side=tk.LEFT, padx=10)
        
        # Tools grid
        self.create_tools_grid()
        
    def create_tools_grid(self):
        """Create tools grid"""
        tools_container = tk.Frame(self.root, bg=self.colors['bg'])
        tools_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create 3x4 grid of tools
        row, col = 0, 0
        for tool_name, tool_info in self.tools.items():
            self.create_tool_card(tools_container, tool_name, tool_info, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(3):
            tools_container.grid_columnconfigure(i, weight=1)
        for i in range(4):
            tools_container.grid_rowconfigure(i, weight=1)
    
    def create_tool_card(self, parent, tool_name, tool_info, row, col):
        """Create tool card with working button"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        card.configure(highlightbackground=tool_info['color'], highlightthickness=2)
        
        # Tool icon and name
        icon_label = tk.Label(card, text=tool_info['icon'], 
                            font=('Arial', 32), 
                            fg=tool_info['color'], bg=self.colors['card'])
        icon_label.pack(pady=(15, 5))
        
        name_label = tk.Label(card, text=tool_name, 
                             font=('Arial', 14, 'bold'), 
                             fg=self.colors['text'], bg=self.colors['card'])
        name_label.pack(pady=(0, 5))
        
        # Description
        desc_label = tk.Label(card, text=tool_info['description'], 
                            font=('Arial', 10), 
                            fg=self.colors['text_secondary'], bg=self.colors['card'],
                            wraplength=200, justify='center')
        desc_label.pack(pady=(0, 15))
        
        # Launch button - WORKING
        launch_btn = tk.Button(card, text="🚀 Launch", 
                             command=lambda tn=tool_name, ti=tool_info: self.launch_tool(tn, ti),
                             bg=tool_info['color'], fg='white', 
                             font=('Arial', 12, 'bold'), relief='raised', bd=2,
                             cursor='hand2', width=12, height=1)
        launch_btn.pack(pady=(0, 15))
        
        # Status label
        status_label = tk.Label(card, text="● Ready", 
                               font=('Arial', 10), 
                               fg=self.colors['success'], bg=self.colors['card'])
        status_label.pack(pady=(0, 10))
        
        # Store references
        tool_info['button'] = launch_btn
        tool_info['status_label'] = status_label
        
    def launch_tool(self, tool_name, tool_info):
        """Launch tool with proper path resolution"""
        try:
            # Get base path (current directory)
            base_path = Path(__file__).parent
            
            # Convert forward slashes to proper path separators
            tool_path_str = tool_info['path'].replace('/', os.sep)
            tool_path = base_path / tool_path_str
            
            # Debug: Show what we're trying to launch
            print(f"Attempting to launch: {tool_name}")
            print(f"Base path: {base_path}")
            print(f"Tool path: {tool_path}")
            print(f"Tool exists: {tool_path.exists()}")
            
            # Check if file exists
            if not tool_path.exists():
                # Try to find the file by searching the directory
                filename = Path(tool_path_str).name
                found_path = None
                
                for root, dirs, files in os.walk(base_path):
                    if filename in files:
                        found_path = Path(root) / filename
                        print(f"Found file at: {found_path}")
                        break
                
                if found_path:
                    tool_path = found_path
                else:
                    messagebox.showerror("Tool Not Found", f"Tool not found: {filename}\nSearched in: {base_path}")
                    return
            
            # Set working directory
            working_dir = tool_path.parent if tool_path.parent.exists() else base_path
            
            # Launch based on file type
            if tool_path.suffix == '.py':
                # Python script
                subprocess.Popen(['python', str(tool_path)], 
                                cwd=str(working_dir),
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif tool_path.suffix == '.bat':
                # Batch file
                subprocess.Popen([str(tool_path)], 
                                cwd=str(working_dir),
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Other executable
                subprocess.Popen([str(tool_path)], 
                                cwd=str(working_dir))
            
            # Update status
            tool_info['status_label'].config(text="● Running", fg=self.colors['success'])
            self.running_processes[tool_name] = True
            messagebox.showinfo("Success", f"{tool_name} launched successfully!")
            
        except Exception as e:
            print(f"Error launching {tool_name}: {e}")
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {str(e)}")
    
    def start_live_updates(self):
        """Start live updates"""
        def update_stats():
            try:
                # Update CPU
                cpu_percent = psutil.cpu_percent()
                self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
                
                # Update RAM
                memory = psutil.virtual_memory()
                self.ram_label.config(text=f"RAM: {memory.percent:.1f}%")
                
                # Update running count
                self.running_label.config(text=f"Running: {len(self.running_processes)}")
                
            except:
                pass
            
            # Schedule next update
            self.root.after(2000, update_stats)
        
        update_stats()
    
    def run(self):
        """Run the dashboard"""
        self.root.mainloop()

if __name__ == "__main__":
    dashboard = SimpleDashboard()
    dashboard.run()
