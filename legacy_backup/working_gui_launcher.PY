#!/usr/bin/env python3
"""
Enhanced Homelab Launcher
Advanced launcher with live system monitoring and category-based organization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import time
import psutil
from pathlib import Path
import json
from datetime import datetime

class EnhancedLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Enhanced Homelab Launcher")
        self.root.geometry("1600x900")  # Optimized for 1920x1080 with taskbar and margins
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Center window on 1920x1080 screen
        screen_width = 1920
        screen_height = 1080
        window_width = 1600
        window_height = 900
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Modern color scheme inspired by Homelab Tools
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00d4ff',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'border': '#404040',
            'accent': '#0078ff'
        }
        
        # Base path for tools
        self.base_path = Path(__file__).parent
        
        # System stats
        self.system_stats = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_active': False,
            'gpu_usage': 0,
            'running_processes': 0
        }
        
        # Comprehensive tool categories with all available tools
        self.tool_categories = {
            '🔥 Working Systems': {
                'tools': [
                    {'name': 'Simple Unified GUI', 'file': 'simple_unified_gui.PY', 'icon': '⭐', 'color': '#00ff88'},
                    {'name': 'Unified Launcher GUI', 'file': 'launcher_gui.py', 'icon': '🚀', 'color': '#00d4ff'},
                    {'name': 'PC Authentication GUI', 'file': 'pc_auth_gui.py', 'icon': '🔐', 'color': '#8e44ad'},
                    {'name': 'Streamlined Dashboard', 'file': 'streamlined_dashboard.py', 'icon': '📊', 'color': '#e74c3c'},
                    {'name': 'Enhanced Dashboard', 'file': 'system_dashboard_enhanced.py', 'icon': '📈', 'color': '#ff6b35'},
                    {'name': 'Fully Unified GUI', 'file': 'fully_unified_gui.py', 'icon': '🌟', 'color': '#00ff88'},
                    {'name': 'Integrated Homelab with Auth', 'file': 'integrated_homelab_with_auth.py', 'icon': '🔑', 'color': '#8e44ad'},
                    {'name': 'Streamlined Homelab System', 'file': 'streamlined_homelab_system.py', 'icon': '🎯', 'color': '#00d4ff'}
                ],
                'description': 'Tested and working homelab systems'
            },
            '🖥️ Windows Server & Client': {
                'tools': [
                    {'name': 'Windows 10 Homelab Server', 'file': 'win10_homelab_server.py', 'icon': '🏢', 'color': '#00ff88'},
                    {'name': 'Windows 10 Server Launcher', 'file': 'win10_server_launcher.py', 'icon': '🚀', 'color': '#00d4ff'},
                    {'name': 'Windows 11 Homelab Client', 'file': 'win11_homelab_client.py', 'icon': '💻', 'color': '#ff6b35'},
                    {'name': 'Windows 11 RDMA Client', 'file': 'win11_rdma_client.py', 'icon': '🔌', 'color': '#ffaa00'}
                ],
                'description': 'Windows 10/11 server and client tools for testing'
            },
            '⚡ Overclocking & Performance': {
                'tools': [
                    {'name': 'Overclocking Dashboard', 'file': 'overclocking_dashboard.py', 'icon': '🔧', 'color': '#ff6b35'},
                    {'name': 'Performance Optimizer', 'file': 'performance_optimizer.py', 'icon': '⚡', 'color': '#00ff88'},
                    {'name': 'Resource Optimizer', 'file': 'resource_optimizer.py', 'icon': '🎯', 'color': '#00d4ff'},
                    {'name': 'Resource Optimizer Fixed', 'file': 'resource_optimizer_fixed.py', 'icon': '🔧', 'color': '#ff6b35'},
                    {'name': 'Performance Reports', 'file': 'performance_reports.py', 'icon': '📊', 'color': '#ffaa00'},
                    {'name': 'System Health Scorer', 'file': 'system_health_scorer.py', 'icon': '💚', 'color': '#00ff88'}
                ],
                'description': 'System overclocking and performance optimization tools'
            },
            '� RDMA & Networking': {
                'tools': [
                    {'name': 'RDMA Integration', 'file': 'rdma_integration.py', 'icon': '🔌', 'color': '#00d4ff'},
                    {'name': 'Homelab Server', 'file': 'homelab_server.py', 'icon': '🏢', 'color': '#00ff88'},
                    {'name': 'Homelab Client', 'file': 'homelab_client.py', 'icon': '💻', 'color': '#ff6b35'},
                    {'name': 'Homelab Dashboard', 'file': 'homelab_dashboard.py', 'icon': '📊', 'color': '#ffaa00'}
                ],
                'description': 'RDMA integration and networking tools'
            },
            '🧹 System Cleanup & Optimization': {
                'tools': [
                    {'name': 'Aggressive RAM Cleaner', 'file': 'aggressive_ram_cleaner.py', 'icon': '🧹', 'color': '#ff4444'},
                    {'name': 'Soft RAM Cleaner', 'file': 'soft_ram_cleaner.py', 'icon': '🧽', 'color': '#00d4ff'},
                    {'name': 'RAM Cleanup Script', 'file': 'ram_cleanup_script.py', 'icon': '🔄', 'color': '#ffaa00'},
                    {'name': 'CPU Cleanup Script', 'file': 'cpu_cleanup_script.py', 'icon': '⚡', 'color': '#00ff88'},
                    {'name': 'GPU Cleanup Script', 'file': 'gpu_cleanup_script.py', 'icon': '🎮', 'color': '#ff6b35'},
                    {'name': 'System Cleanup Master', 'file': 'system_cleanup_master.py', 'icon': '👑', 'color': '#8e44ad'},
                    {'name': 'Memory Jolt', 'file': 'memory_jolt.py', 'icon': '⚡', 'color': '#ff4444'}
                ],
                'description': 'System cleanup and memory optimization tools'
            },
            '🔐 Security & Authentication': {
                'tools': [
                    {'name': 'PC Authentication System', 'file': 'pc_auth_system.py', 'icon': '🔐', 'color': '#8e44ad'},
                    {'name': 'Advanced Security', 'file': 'advanced_security.py', 'icon': '🛡️', 'color': '#ff4444'},
                    {'name': 'Automated Interventions', 'file': 'automated_interventions.py', 'icon': '🤖', 'color': '#00d4ff'},
                    {'name': 'Automated Responses', 'file': 'automated_responses.py', 'icon': '📡', 'color': '#ffaa00'}
                ],
                'description': 'Security systems and authentication tools'
            },
            '💾 Backup & Management': {
                'tools': [
                    {'name': 'Backup Manager', 'file': 'backup_manager.py', 'icon': '💾', 'color': '#00ff88'},
                    {'name': 'Settings Manager', 'file': 'settings_manager.py', 'icon': '⚙️', 'color': '#00d4ff'},
                    {'name': 'Database Schema', 'file': 'database_schema.py', 'icon': '🗄️', 'color': '#ff6b35'},
                    {'name': 'Task Scheduler', 'file': 'task_scheduler.py', 'icon': '📅', 'color': '#ffaa00'}
                ],
                'description': 'Backup, settings and management tools'
            },
            '🧪 Testing & Diagnostics': {
                'tools': [
                    {'name': 'Test GPU Monitoring', 'file': 'test_gpu_monitoring.py', 'icon': '🎮', 'color': '#ff6b35'},
                    {'name': 'Test GUI', 'file': 'test_gui.py', 'icon': '🖥️', 'color': '#00d4ff'},
                    {'name': 'Debug GPU GUI', 'file': 'debug_gpu_gui.py', 'icon': '🐛', 'color': '#ff4444'},
                    {'name': 'Test NVIDIA SMI', 'file': 'test_nvidia_smi.py', 'icon': '🎯', 'color': '#00ff88'}
                ],
                'description': 'Testing and diagnostic tools'
            },
            '🛠️ Utilities & Tools': {
                'tools': [
                    {'name': 'Console Launcher', 'file': 'console_launcher.PY', 'icon': '🖥️', 'color': '#00d4ff'},
                    {'name': 'Stay Open Launcher', 'file': 'stay_open_launcher.PY', 'icon': '🔄', 'color': '#00ff88'},
                    {'name': 'System API', 'file': 'system_api.py', 'icon': '🔌', 'color': '#ff6b35'},
                    {'name': 'Help System', 'file': 'help_system.py', 'icon': '❓', 'color': '#ffaa00'},
                    {'name': 'Email Notifications', 'file': 'email_notifications.py', 'icon': '📧', 'color': '#8e44ad'},
                    {'name': 'Internationalization', 'file': 'internationalization.py', 'icon': '🌍', 'color': '#00ff88'},
                    {'name': 'Accessibility', 'file': 'accessibility.py', 'icon': '♿', 'color': '#00d4ff'},
                    {'name': 'Machine Learning', 'file': 'machine_learning.py', 'icon': '🤖', 'color': '#ff6b35'}
                ],
                'description': 'Utility tools and additional features'
            },
            '� Legacy Tools': {
                'tools': [
                    {'name': 'System Dashboard', 'file': 'system_dashboard.py', 'icon': '🚀', 'color': '#4ecdc4'},
                    {'name': 'RAM Monitor', 'file': 'ram_monitor_gui.py', 'icon': '🧹', 'color': '#ffaa00'},
                    {'name': 'GPU Monitor', 'file': 'gpu_monitor_gui.py', 'icon': '🎮', 'color': '#ff4444'},
                    {'name': 'CPU Monitor', 'file': 'cpu_monitor_gui.py', 'icon': '⚡', 'color': '#87CEEB'},
                    {'name': 'Launcher', 'file': 'launcher.py', 'icon': '🚀', 'color': '#00d4ff'}
                ],
                'description': 'Original monitoring and launcher tools'
            }
        }
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.update_system_stats, daemon=True)
        self.monitoring_thread.start()
        
        # Center the window
        self.center_window()
        
        # Create widgets
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create modern launcher widgets with system monitoring"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with system stats
        self.create_header(main_container)
        
        # System monitoring panel
        self.create_system_monitor(main_container)
        
        # Tool categories
        self.create_tool_categories(main_container)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self, parent):
        """Create header with title and system info"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'], height=120)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🏠 Enhanced Homelab Launcher", 
                              font=('Segoe UI', 28, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(header_frame, text="Advanced launcher with live system monitoring", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack()
    
    def create_system_monitor(self, parent):
        """Create live system monitoring panel"""
        monitor_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        monitor_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Monitor title
        monitor_title = tk.Label(monitor_frame, text="📊 System Monitor", 
                               font=('Segoe UI', 14, 'bold'), 
                               fg=self.colors['text'], bg=self.colors['card'])
        monitor_title.pack(pady=(15, 10))
        
        # Stats container
        stats_container = tk.Frame(monitor_frame, bg=self.colors['card'])
        stats_container.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Create stat labels
        self.stat_labels = {}
        stats = [
            ('cpu', '💻 CPU', self.colors['primary']),
            ('memory', '🧠 Memory', self.colors['secondary']),
            ('disk', '💾 Disk', self.colors['warning']),
            ('processes', '⚙️ Processes', self.colors['info']),
            ('network', '🌐 Network', self.colors['success'])
        ]
        
        for key, label, color in stats:
            stat_frame = tk.Frame(stats_container, bg=self.colors['card'])
            stat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
            
            stat_label = tk.Label(stat_frame, text=label, 
                                 font=('Segoe UI', 10), 
                                 fg=self.colors['text_secondary'], bg=self.colors['card'])
            stat_label.pack()
            
            stat_value = tk.Label(stat_frame, text="0%", 
                                 font=('Segoe UI', 16, 'bold'), 
                                 fg=color, bg=self.colors['card'])
            stat_value.pack()
            
            self.stat_labels[key] = stat_value
    
    def create_tool_categories(self, parent):
        """Create categorized tool sections with enhanced scrolling"""
        # Create main scrollable container
        scroll_container = tk.Frame(parent, bg=self.colors['bg'])
        scroll_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(scroll_container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Enable keyboard scrolling
        def _on_key_press(event):
            if event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Home':
                canvas.yview_moveto(0)
            elif event.keysym == 'End':
                canvas.yview_moveto(1)
            elif event.keysym == 'Page_Up':
                canvas.yview_scroll(-1, "pages")
            elif event.keysym == 'Page_Down':
                canvas.yview_scroll(1, "pages")
        
        canvas.bind('<Key>', _on_key_press)
        canvas.focus_set()  # Allow canvas to receive keyboard events
        
        # Add padding to scrollable frame
        padding_frame = tk.Frame(scrollable_frame, bg=self.colors['bg'])
        padding_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create categories
        for category_name, category_data in self.tool_categories.items():
            self.create_category_section(padding_frame, category_name, category_data)
        
        # Store canvas reference for external access
        self.scroll_canvas = canvas
    
    def create_category_section(self, parent, category_name, category_data):
        """Create a category section with tools in proper 3-column grid"""
        # Category frame with better spacing
        category_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        category_frame.pack(fill=tk.X, pady=(0, 20), padx=5)
        
        # Add rounded corners effect
        category_frame.configure(relief='solid', bd=1)
        
        # Category header with better styling
        header_frame = tk.Frame(category_frame, bg=self.colors['card'], height=60)
        header_frame.pack(fill=tk.X, pady=(15, 10))
        header_frame.pack_propagate(False)
        
        # Category icon and name
        title_frame = tk.Frame(header_frame, bg=self.colors['card'])
        title_frame.pack(side=tk.LEFT, padx=20)
        
        category_label = tk.Label(title_frame, text=category_name, 
                                 font=('Segoe UI', 18, 'bold'), 
                                 fg=self.colors['text'], bg=self.colors['card'])
        category_label.pack(side=tk.LEFT)
        
        # Description on the right
        desc_label = tk.Label(header_frame, text=f"{category_data['description']}", 
                             font=('Segoe UI', 10), 
                             fg=self.colors['text_secondary'], bg=self.colors['card'])
        desc_label.pack(side=tk.RIGHT, padx=20)
        
        # Tools container with 3-column grid layout
        tools_container = tk.Frame(category_frame, bg=self.colors['card'])
        tools_container.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Create 3-column grid layout
        self.create_3_column_grid(tools_container, category_data['tools'])
    
    def create_3_column_grid(self, parent, tools):
        """Create single column layout with very large buttons"""
        # Use 1 column for very large buttons
        tools_per_row = 1
        num_tools = len(tools)
        num_rows = num_tools
        
        # Create grid rows with much larger button height
        for row in range(num_rows):
            row_frame = tk.Frame(parent, bg=self.colors['card'], height=100)  # Much taller rows
            row_frame.pack(fill=tk.X, pady=5)  # More spacing between buttons
            row_frame.pack_propagate(False)
            
            # Create single column
            tool_index = row
            if tool_index < num_tools:
                tool = tools[tool_index]
                self.create_tool_button_in_grid(row_frame, tool, 0)
    
    def create_tool_button_in_grid(self, parent, tool, column_index):
        """Create very large buttons that fill the window properly"""
        # Button container for single column with minimal margins
        button_container = tk.Frame(parent, bg=self.colors['card'])
        button_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)  # Minimal margins
        
        # Very large button that fills most of the row
        tool_button = tk.Button(button_container, 
                              text=f"{tool['icon']}  {tool['name']}", 
                              font=('Segoe UI', 18, 'bold'),  # Much larger font
                              bg=tool['color'], fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              padx=30, pady=25,  # Much larger padding
                              justify='left',
                              command=lambda f=tool['file']: self.launch_tool(f, tool['name']))
        tool_button.pack(fill=tk.BOTH, expand=True, pady=2)  # Fill entire container
        
        # Enhanced hover effects
        def on_enter(e):
            new_color = self.adjust_brightness(tool['color'], 1.15)
            tool_button.config(bg=new_color, relief='raised', bd=3)
        
        def on_leave(e):
            tool_button.config(bg=tool['color'], relief='flat', bd=0)
        
        def on_click(e):
            tool_button.config(relief='sunken', bd=4)
            self.root.after(100, lambda: tool_button.config(relief='raised', bd=3))
        
        tool_button.bind("<Enter>", on_enter)
        tool_button.bind("<Leave>", on_leave)
        tool_button.bind("<Button-1>", on_click)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="● Ready", 
                                    font=('Segoe UI', 10, 'bold'), 
                                    bg=self.colors['card'], fg=self.colors['success'])
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Time display
        self.time_label = tk.Label(status_frame, text="", 
                                  font=('Segoe UI', 10), 
                                  bg=self.colors['card'], fg=self.colors['text_secondary'])
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Update time
        self.update_time()
    
    def launch_tool(self, filename, tool_name):
        """Launch a tool with enhanced feedback"""
        if self.check_file_exists(filename):
            self.status_label.config(text=f"● Starting {tool_name}...", fg=self.colors['success'])
            self.root.after(1000, self.run_script, filename, tool_name)
        else:
            messagebox.showerror("Error", f"{filename} not found!")
    
    def update_system_stats(self):
        """Update system statistics in background thread"""
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_stats['cpu_usage'] = cpu_percent
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_stats['memory_usage'] = memory.percent
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.system_stats['disk_usage'] = (disk.used / disk.total) * 100
                
                # Network status
                network = psutil.net_io_counters()
                self.system_stats['network_active'] = network.bytes_sent + network.bytes_recv > 0
                
                # Running processes
                self.system_stats['running_processes'] = len(psutil.pids())
                
                # Update UI in main thread
                self.root.after(0, self.update_stats_display)
                
            except Exception as e:
                print(f"Error updating system stats: {e}")
            
            time.sleep(2)  # Update every 2 seconds
    
    def update_stats_display(self):
        """Update the statistics display"""
        try:
            # Update CPU
            cpu_text = f"{self.system_stats['cpu_usage']:.1f}%"
            self.stat_labels['cpu'].config(text=cpu_text)
            
            # Update Memory
            memory_text = f"{self.system_stats['memory_usage']:.1f}%"
            self.stat_labels['memory'].config(text=memory_text)
            
            # Update Disk
            disk_text = f"{self.system_stats['disk_usage']:.1f}%"
            self.stat_labels['disk'].config(text=disk_text)
            
            # Update Processes
            processes_text = str(self.system_stats['running_processes'])
            self.stat_labels['processes'].config(text=processes_text)
            
            # Update Network
            network_text = "Active" if self.system_stats['network_active'] else "Idle"
            network_color = self.colors['success'] if self.system_stats['network_active'] else self.colors['text_secondary']
            self.stat_labels['network'].config(text=network_text, fg=network_color)
            
        except Exception as e:
            print(f"Error updating stats display: {e}")
    
    def update_time(self):
        """Update the time display"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, self.update_time)  # Update every second
        except:
            pass
    
    def adjust_brightness(self, hex_color, factor):
        """Adjust brightness of a hex color"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Adjust brightness
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color
    
    def check_file_exists(self, filename):
        """Check if file exists with proper path handling"""
        file_path = self.base_path / filename
        return file_path.exists()
    
    def run_script(self, script_name, tool_name):
        """Run a Python script with enhanced error handling"""
        try:
            # Use the same Python interpreter
            subprocess.Popen([sys.executable, script_name])
            self.status_label.config(text=f"● Launched {tool_name}", fg=self.colors['success'])
            # Close launcher after a short delay
            self.root.after(2000, self.root.quit)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {e}")
            self.status_label.config(text="● Launch failed", fg=self.colors['danger'])
    
    def update_system_stats(self):
        """Update system statistics in background thread"""
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_stats['cpu_usage'] = cpu_percent
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_stats['memory_usage'] = memory.percent
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.system_stats['disk_usage'] = (disk.used / disk.total) * 100
                
                # Network status
                network = psutil.net_io_counters()
                self.system_stats['network_active'] = network.bytes_sent + network.bytes_recv > 0
                
                # Running processes
                self.system_stats['running_processes'] = len(psutil.pids())
                
                # Update UI in main thread
                self.root.after(0, self.update_stats_display)
                
            except Exception as e:
                print(f"Error updating system stats: {e}")
            
            time.sleep(2)  # Update every 2 seconds
    
    def update_stats_display(self):
        """Update the statistics display"""
        try:
            # Update CPU
            cpu_text = f"{self.system_stats['cpu_usage']:.1f}%"
            self.stat_labels['cpu'].config(text=cpu_text)
            
            # Update Memory
            memory_text = f"{self.system_stats['memory_usage']:.1f}%"
            self.stat_labels['memory'].config(text=memory_text)
            
            # Update Disk
            disk_text = f"{self.system_stats['disk_usage']:.1f}%"
            self.stat_labels['disk'].config(text=disk_text)
            
            # Update Processes
            processes_text = str(self.system_stats['running_processes'])
            self.stat_labels['processes'].config(text=processes_text)
            
            # Update Network
            network_text = "Active" if self.system_stats['network_active'] else "Idle"
            network_color = self.colors['success'] if self.system_stats['network_active'] else self.colors['text_secondary']
            self.stat_labels['network'].config(text=network_text, fg=network_color)
            
        except Exception as e:
            print(f"Error updating stats display: {e}")
    
    def update_time(self):
        """Update the time display"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, self.update_time)  # Update every second
        except:
            pass
    
    def adjust_brightness(self, hex_color, factor):
        """Adjust brightness of a hex color"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Adjust brightness
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color
    
    def check_file_exists(self, filename):
        """Check if file exists with proper path handling"""
        file_path = self.base_path / filename
        return file_path.exists()
    
    def run_script(self, script_name, tool_name):
        """Run a Python script with enhanced error handling"""
        try:
            # Use the same Python interpreter
            subprocess.Popen([sys.executable, script_name])
            self.status_label.config(text=f"● Launched {tool_name}", fg=self.colors['success'])
            # Close launcher after a short delay
            self.root.after(2000, self.root.quit)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {e}")
            self.status_label.config(text="● Launch failed", fg=self.colors['danger'])

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = EnhancedLauncherGUI(root)
        
        # Handle window closing
        def on_closing():
            app.monitoring_active = False
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error starting launcher: {e}")
        messagebox.showerror("Error", f"Failed to start launcher: {e}")

if __name__ == "__main__":
    main()
