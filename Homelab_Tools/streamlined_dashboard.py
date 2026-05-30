#!/usr/bin/env python3
"""
Streamlined Homelab Dashboard
Main tool categories with live stats and launch buttons to relevant tool panels
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
import sys
from pathlib import Path
import psutil
import json
from datetime import datetime

class StreamlinedDashboard:
    """Streamlined dashboard with main tool categories and live stats"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homelab Tools Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'card': '#2d2d30',
            'primary': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'danger': '#d13438',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'border': '#3f3f46'
        }
        
        # System stats
        self.system_stats = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_active': False,
            'running_tools': 0,
            'total_tools': 205
        }
        
        # Main categories with representative tools and correct paths
        self.categories = {
            'System Monitoring': {
                'icon': '📊',
                'color': '#00ff88',
                'tools': ['CPU Monitor', 'GPU Monitor', 'Network Monitor', 'Storage Monitor', 'RAM Monitor', 'Memory Monitor'],
                'launch_tool': 'CPU Monitor/cpu_monitor.py',
                'description': 'Real-time system monitoring and optimization'
            },
            'Distributed Computing': {
                'icon': '⚡',
                'color': '#0078ff',
                'tools': ['RDMA Desktop App', 'RDMA Modern App', 'Memory Portal', 'Hybrid Compute', 'RDMA Terminal'],
                'launch_tool': 'RDMA Desktop App/rdma_desktop_app.py',
                'description': 'High-performance computing and RDMA systems'
            },
            'Infrastructure & Management': {
                'icon': '🏗️',
                'color': '#ff6b6b',
                'tools': ['Web Dashboard', 'VPN Gateway', 'Backup Manager', 'Power Manager', 'Container Manager', 'VM Manager', 'System Manager'],
                'launch_tool': 'Core Services/web_dashboard.py',
                'description': 'Core infrastructure and management services'
            },
            'Network & Security': {
                'icon': '🔐',
                'color': '#ffaa00',
                'tools': ['Mesh VPN Server', 'Mesh VPN Client', 'WireGuard Installer', 'Network Security', 'Firewall Manager'],
                'launch_tool': 'VPN Gateway/vpn_gateway.py',
                'description': 'VPN, security, and network management'
            },
            'RAM Sharing': {
                'icon': '🖥️',
                'color': '#00d4ff',
                'tools': ['RAM Sharing Manager', 'Simple RAM Sharing', 'Advanced RAM Sharing', 'Memory Optimizer'],
                'launch_tool': 'RAM Sharing/ram_sharing_gui.py',
                'description': 'Cross-PC memory sharing and optimization'
            },
            'System Tools': {
                'icon': '🛠️',
                'color': '#ff6b6b',
                'tools': ['System Integration Test', 'Homelab Launcher', 'Comprehensive Audit', 'System Diagnostics', 'Performance Tuner'],
                'launch_tool': 'homelab_launcher.py',
                'description': 'System utilities and testing tools'
            },
            'Virtualization': {
                'icon': '🖥️',
                'color': '#e74c3c',
                'tools': ['VM Manager', 'Container Manager', 'Docker Manager', 'KVM Manager', 'VirtualBox Manager'],
                'launch_tool': 'VM Manager/vm_manager.py',
                'description': 'Virtual machine and container management'
            },
            'Advanced Features': {
                'icon': '🚀',
                'color': '#9b59b6',
                'tools': ['AI Assistant', 'Automation Hub', 'Task Scheduler', 'Resource Monitor'],
                'launch_tool': 'Core Services/automation_hub.py',
                'description': 'Advanced automation and AI features'
            }
        }
        
        # Running processes
        self.running_processes = {}
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Start monitoring
        self.start_monitoring()
        
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        styles = {
            'Title.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 24, 'bold')},
            'Card.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'Category.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 16, 'bold')},
            'Stats.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text_secondary'], 'font': ('Segoe UI', 10)},
            'Value.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 12, 'bold')},
            'Launch.TButton': {'background': self.colors['primary'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 10, 'bold'), 'relief': 'flat', 'borderwidth': 0}
        }
        
        for style_name, config in styles.items():
            style.configure(style_name, **config)
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # System stats bar
        self.create_stats_bar(main_container)
        
        # Categories grid
        categories_frame = tk.Frame(main_container, bg=self.colors['bg'])
        categories_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.create_categories_grid(categories_frame)
        
    def create_header(self, parent):
        """Create header"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="Homelab Tools Dashboard", 
                              font=('Segoe UI', 28, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(header_frame, text="● SYSTEM READY", 
                                    font=('Segoe UI', 14, 'bold'), 
                                    fg=self.colors['success'], bg=self.colors['bg'])
        self.status_label.pack(side=tk.RIGHT)
        
    def create_stats_bar(self, parent):
        """Create system stats bar"""
        stats_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # CPU Usage
        cpu_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(cpu_frame, text="CPU", font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()
        self.cpu_label = tk.Label(cpu_frame, text="0%", font=('Segoe UI', 18, 'bold'), 
                                 fg=self.colors['text'], bg=self.colors['card'])
        self.cpu_label.pack()
        
        # Memory Usage
        mem_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(mem_frame, text="Memory", font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()
        self.memory_label = tk.Label(mem_frame, text="0%", font=('Segoe UI', 18, 'bold'), 
                                     fg=self.colors['text'], bg=self.colors['card'])
        self.memory_label.pack()
        
        # Disk Usage
        disk_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        disk_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(disk_frame, text="Disk", font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()
        self.disk_label = tk.Label(disk_frame, text="0%", font=('Segoe UI', 18, 'bold'), 
                                   fg=self.colors['text'], bg=self.colors['card'])
        self.disk_label.pack()
        
        # Network Status
        net_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        net_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(net_frame, text="Network", font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()
        self.network_label = tk.Label(net_frame, text="●", font=('Segoe UI', 18, 'bold'), 
                                      fg=self.colors['text'], bg=self.colors['card'])
        self.network_label.pack()
        
        # Running Tools
        tools_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        tools_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(tools_frame, text="Running Tools", font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()
        self.tools_label = tk.Label(tools_frame, text="0/205", font=('Segoe UI', 18, 'bold'), 
                                   fg=self.colors['text'], bg=self.colors['card'])
        self.tools_label.pack()
    
    def create_categories_grid(self, parent):
        """Create categories grid"""
        # Create grid layout
        cols = 3
        rows = 2
        
        for i, (category_name, category_info) in enumerate(self.categories.items()):
            row = i // cols
            col = i % cols
            
            category_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
            category_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Configure grid weights
            parent.grid_rowconfigure(row, weight=1)
            parent.grid_columnconfigure(col, weight=1)
            
            self.create_category_panel(category_frame, category_name, category_info)
    
    def create_category_panel(self, parent, category_name, category_info):
        """Create individual category panel"""
        # Header
        header_frame = tk.Frame(parent, bg=category_info['color'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Icon and title
        title_frame = tk.Frame(header_frame, bg=category_info['color'])
        title_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(title_frame, text=category_info['icon'], 
                font=('Segoe UI', 24), fg='white', bg=category_info['color']).pack(side=tk.LEFT, padx=15)
        
        tk.Label(title_frame, text=category_name, 
                font=('Segoe UI', 16, 'bold'), fg='white', bg=category_info['color']).pack(side=tk.LEFT, padx=10)
        
        # Content
        content_frame = tk.Frame(parent, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Description
        tk.Label(content_frame, text=category_info['description'], 
                font=('Segoe UI', 10), fg=self.colors['text_secondary'], 
                bg=self.colors['card'], wraplength=300, justify='left').pack(anchor='w')
        
        # Tools count
        tools_count = len(category_info['tools'])
        tk.Label(content_frame, text=f"{tools_count} tools available", 
                font=('Segoe UI', 9, 'bold'), fg=category_info['color'], 
                bg=self.colors['card']).pack(anchor='w', pady=(10, 0))
        
        # Tool list (show first 3)
        tools_text = ", ".join(category_info['tools'][:3])
        if tools_count > 3:
            tools_text += f" +{tools_count - 3} more"
        
        tk.Label(content_frame, text=tools_text, 
                font=('Segoe UI', 9), fg=self.colors['text_secondary'], 
                bg=self.colors['card'], wraplength=300, justify='left').pack(anchor='w', pady=(5, 15))
        
        # Launch button
        launch_btn = tk.Button(content_frame, text=f"LAUNCH {category_name.upper()}", 
                             font=('Segoe UI', 10, 'bold'), fg='white', 
                             bg=category_info['color'], relief='flat', bd=0,
                             cursor='hand2',
                             command=lambda cat=category_name, info=category_info: self.launch_category(cat, info))
        launch_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Individual tool buttons
        tools_frame = tk.Frame(content_frame, bg=self.colors['card'])
        tools_frame.pack(fill=tk.X, pady=(10, 0))
        
        for tool in category_info['tools'][:2]:  # Show first 2 tools
            tool_btn = tk.Button(tools_frame, text=tool, 
                               font=('Segoe UI', 8), fg=self.colors['text'], 
                               bg=self.colors['border'], relief='flat', bd=1,
                               cursor='hand2')
            tool_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def launch_category(self, category_name, category_info):
        """Launch main tool for category"""
        launch_tool = category_info['launch_tool']
        
        try:
            # Launch the main tool for this category
            self.launch_tool(category_name, launch_tool)
            
            # Update status
            self.status_label.config(text=f"● LAUNCHED {category_name.upper()}", fg=self.colors['primary'])
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch {category_name}: {str(e)}")
    
    def launch_tool(self, tool_name, tool_path):
        """Launch a tool with proper path resolution"""
        try:
            base_path = Path(os.getenv('HOMELAB_ROOT', os.path.dirname(os.path.abspath(__file__))))
            full_tool_path = base_path / tool_path
            
            # Check if tool exists at specified path
            if not full_tool_path.exists():
                # Try to find the tool in common directories
                possible_dirs = [
                    "CPU Monitor", "GPU Monitor", "Network Monitor", "Storage Monitor", "Memory Monitor",
                    "Core Services", "VPN Gateway", "Power Manager", "Container Manager", "Web Dashboard",
                    "RDMA Desktop App", "Memory Portal", "Hybrid Compute", "RAM Sharing", "System Tools"
                ]
                
                for dir_name in possible_dirs:
                    test_path = base_path / dir_name / Path(tool_path).name
                    if test_path.exists():
                        full_tool_path = test_path
                        break
                else:
                    messagebox.showerror("Tool Not Found", f"Tool not found: {tool_path}")
                    return
            
            # Determine if GUI or console
            is_gui = full_tool_path.suffix == '.py'
            
            if is_gui:
                # Launch GUI application
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['python', str(full_tool_path)], 
                                   cwd=full_tool_path.parent,
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen(['python3', str(full_tool_path)], 
                                   cwd=full_tool_path.parent)
            else:
                # Launch batch file
                if os.name == 'nt':  # Windows
                    subprocess.Popen([str(full_tool_path)], 
                                   cwd=full_tool_path.parent,
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    subprocess.Popen([str(full_tool_path)], 
                                   cwd=full_tool_path.parent)
            
            # Track running process
            self.running_processes[tool_name] = {
                'path': str(full_tool_path),
                'started': datetime.now()
            }
            
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch {tool_name}: {str(e)}")
    
    def update_system_stats(self):
        """Update system statistics"""
        try:
            # CPU usage
            self.system_stats['cpu_usage'] = psutil.cpu_percent(interval=1)
            self.cpu_label.config(text=f"{self.system_stats['cpu_usage']:.0f}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_stats['memory_usage'] = memory.percent
            self.memory_label.config(text=f"{self.system_stats['memory_usage']:.0f}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_stats['disk_usage'] = (disk.used / disk.total) * 100
            self.disk_label.config(text=f"{self.system_stats['disk_usage']:.0f}%")
            
            # Network status
            net_io = psutil.net_io_counters()
            self.system_stats['network_active'] = net_io.bytes_sent > 0 or net_io.bytes_recv > 0
            network_color = self.colors['success'] if self.system_stats['network_active'] else self.colors['text_secondary']
            self.network_label.config(text="●", fg=network_color)
            
            # Running tools
            self.system_stats['running_tools'] = len(self.running_processes)
            self.tools_label.config(text=f"{self.system_stats['running_tools']}/{self.system_stats['total_tools']}")
            
            # Update status based on system load
            if self.system_stats['cpu_usage'] > 80 or self.system_stats['memory_usage'] > 80:
                self.status_label.config(text="● HIGH LOAD", fg=self.colors['warning'])
            elif self.system_stats['running_tools'] > 0:
                self.status_label.config(text="● TOOLS ACTIVE", fg=self.colors['primary'])
            else:
                self.status_label.config(text="● SYSTEM READY", fg=self.colors['success'])
                
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def start_monitoring(self):
        """Start system monitoring"""
        def monitor():
            while True:
                try:
                    self.update_system_stats()
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def run(self):
        """Run the dashboard"""
        self.root.mainloop()

def main():
    """Main entry point"""
    dashboard = StreamlinedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
