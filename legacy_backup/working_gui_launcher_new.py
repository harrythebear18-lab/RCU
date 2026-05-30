#!/usr/bin/env python3
"""
Simple Working Homelab Launcher
Clean, simple launcher with all tools visible and working
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from pathlib import Path
import threading
import time
import psutil
from datetime import datetime

class SimpleLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Homelab Launcher")
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window to full screen
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1a1a1a')
        
        # Colors
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
            'text_secondary': '#cccccc'
        }
        
        # Base path
        self.base_path = Path(__file__).parent
        
        # System stats
        self.system_stats = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_active': False,
            'running_processes': 0
        }
        
        # Start monitoring
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.update_system_stats, daemon=True)
        self.monitoring_thread.start()
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create widgets that use full screen width"""
        # Main container that fills entire screen
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)  # No padding for full width
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="🏠 Homelab Launcher", 
                              font=('Arial', 20, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=5)
        
        # System monitor
        self.create_system_monitor(main_frame)
        
        # Tools section
        self.create_tools_section(main_frame)
        
        # Status bar
        self.create_status_bar()
    
    def create_system_monitor(self, parent):
        """Create system monitor that uses full width"""
        monitor_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=1)
        monitor_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(monitor_frame, text="📊 System Status", 
                              font=('Arial', 12, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(pady=5)
        
        # Stats frame
        stats_frame = tk.Frame(monitor_frame, bg=self.colors['card'])
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.stat_labels = {}
        stats = [
            ('cpu', '💻 CPU', self.colors['primary']),
            ('memory', '🧠 Memory', self.colors['secondary']),
            ('disk', '💾 Disk', self.colors['warning']),
            ('processes', '⚙️ Processes', self.colors['info']),
            ('network', '🌐 Network', self.colors['success'])
        ]
        
        for key, label, color in stats:
            stat_frame = tk.Frame(stats_frame, bg=self.colors['card'])
            stat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            stat_label = tk.Label(stat_frame, text=label, 
                                 font=('Arial', 9), 
                                 fg=self.colors['text_secondary'], bg=self.colors['card'])
            stat_label.pack()
            
            stat_value = tk.Label(stat_frame, text="0%", 
                                 font=('Arial', 12, 'bold'), 
                                 fg=color, bg=self.colors['card'])
            stat_value.pack()
            
            self.stat_labels[key] = stat_value
    
    def create_tools_section(self, parent):
        """Create tools section that uses full width"""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add all tools
        self.add_all_tools(scrollable_frame)
    
    def add_all_tools(self, parent):
        """Add all tools in horizontal layout"""
        # All tools with their files and colors
        tools = [
            # Working Systems
            ("⭐ Simple Unified GUI", "simple_unified_gui.PY", "#00ff88"),
            ("🚀 Unified Launcher GUI", "launcher_gui.py", "#00aaff"),
            ("🔐 PC Authentication GUI", "pc_auth_gui.py", "#8e44ad"),
            ("📊 Streamlined Dashboard", "streamlined_dashboard.py", "#e74c3c"),
            ("📈 Enhanced Dashboard", "system_dashboard_enhanced.py", "#ff6b35"),
            ("🌟 Fully Unified GUI", "fully_unified_gui.py", "#00ff88"),
            ("🔑 Integrated Homelab with Auth", "integrated_homelab_with_auth.py", "#8e44ad"),
            ("🎯 Streamlined Homelab System", "streamlined_homelab_system.py", "#00aaff"),
            
            # Windows Server & Client
            ("🏢 Windows 10 Homelab Server", "win10_homelab_server.py", "#00ff88"),
            ("🚀 Windows 10 Server Launcher", "win10_server_launcher.py", "#00aaff"),
            ("💻 Windows 11 Homelab Client", "win11_homelab_client.py", "#ff6b35"),
            ("🔌 Windows 11 RDMA Client", "win11_rdma_client.py", "#ffaa00"),
            
            # Overclocking & Performance
            ("🔧 Overclocking Dashboard", "overclocking_dashboard.py", "#ff6b35"),
            ("⚡ Performance Optimizer", "performance_optimizer.py", "#00ff88"),
            ("🎯 Resource Optimizer", "resource_optimizer.py", "#00aaff"),
            ("🔧 Resource Optimizer Fixed", "resource_optimizer_fixed.py", "#ff6b35"),
            ("📊 Performance Reports", "performance_reports.py", "#ffaa00"),
            ("💚 System Health Scorer", "system_health_scorer.py", "#00ff88"),
            
            # RDMA & Networking
            ("🔌 RDMA Integration", "rdma_integration.py", "#00aaff"),
            ("🏢 Homelab Server", "homelab_server.py", "#00ff88"),
            ("💻 Homelab Client", "homelab_client.py", "#ff6b35"),
            ("📊 Homelab Dashboard", "homelab_dashboard.py", "#ffaa00"),
            
            # System Cleanup & Optimization
            ("🧹 Aggressive RAM Cleaner", "aggressive_ram_cleaner.py", "#ff4444"),
            ("🧽 Soft RAM Cleaner", "soft_ram_cleaner.py", "#00aaff"),
            ("🔄 RAM Cleanup Script", "ram_cleanup_script.py", "#ffaa00"),
            ("⚡ CPU Cleanup Script", "cpu_cleanup_script.py", "#00ff88"),
            ("🎮 GPU Cleanup Script", "gpu_cleanup_script.py", "#ff6b35"),
            ("👑 System Cleanup Master", "system_cleanup_master.py", "#8e44ad"),
            ("⚡ Memory Jolt", "memory_jolt.py", "#ff4444"),
            
            # Security & Authentication
            ("🔐 PC Authentication System", "pc_auth_system.py", "#8e44ad"),
            ("🛡️ Advanced Security", "advanced_security.py", "#ff4444"),
            ("🤖 Automated Interventions", "automated_interventions.py", "#00aaff"),
            ("📡 Automated Responses", "automated_responses.py", "#ffaa00"),
            
            # Backup & Management
            ("💾 Backup Manager", "backup_manager.py", "#00ff88"),
            ("⚙️ Settings Manager", "settings_manager.py", "#00aaff"),
            ("🗄️ Database Schema", "database_schema.py", "#ff6b35"),
            ("📅 Task Scheduler", "task_scheduler.py", "#ffaa00"),
            
            # Testing & Diagnostics
            ("🎮 Test GPU Monitoring", "test_gpu_monitoring.py", "#ff6b35"),
            ("🖥️ Test GUI", "test_gui.py", "#00aaff"),
            ("🐛 Debug GPU GUI", "debug_gpu_gui.py", "#ff4444"),
            ("🎯 Test NVIDIA SMI", "test_nvidia_smi.py", "#00ff88"),
            
            # Utilities & Tools
            ("🖥️ Console Launcher", "console_launcher.PY", "#00aaff"),
            ("🔄 Stay Open Launcher", "stay_open_launcher.PY", "#00ff88"),
            ("🔌 System API", "system_api.py", "#ff6b35"),
            ("❓ Help System", "help_system.py", "#ffaa00"),
            ("📧 Email Notifications", "email_notifications.py", "#8e44ad"),
            ("🌍 Internationalization", "internationalization.py", "#00ff88"),
            ("♿ Accessibility", "accessibility.py", "#00aaff"),
            ("🤖 Machine Learning", "machine_learning.py", "#ff6b35"),
            
            # Legacy Tools
            ("🚀 System Dashboard", "system_dashboard.py", "#4ecdc4"),
            ("🧹 RAM Monitor", "ram_monitor_gui.py", "#ffaa00"),
            ("🎮 GPU Monitor", "gpu_monitor_gui.py", "#ff4444"),
            ("⚡ CPU Monitor", "cpu_monitor_gui.py", "#87CEEB"),
            ("🚀 Launcher", "launcher.py", "#00aaff")
        ]
        
        # Category headers with horizontal layout
        categories = [
            ("🔥 Working Systems", 0, 8),
            ("🖥️ Windows Server & Client", 8, 12),
            ("⚡ Overclocking & Performance", 12, 18),
            ("🔌 RDMA & Networking", 18, 22),
            ("🧹 System Cleanup & Optimization", 22, 29),
            ("🔐 Security & Authentication", 29, 33),
            ("💾 Backup & Management", 33, 37),
            ("🧪 Testing & Diagnostics", 37, 41),
            ("🛠️ Utilities & Tools", 41, 49),
            ("📜 Legacy Tools", 49, 54)
        ]
        
        for cat_name, start_idx, end_idx in categories:
            # Category header
            cat_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=1)
            cat_frame.pack(fill=tk.X, pady=(10, 5), padx=10)
            
            cat_label = tk.Label(cat_frame, text=cat_name, 
                                font=('Arial', 16, 'bold'), 
                                fg=self.colors['primary'], bg=self.colors['card'])
            cat_label.pack(pady=10, padx=20, anchor='w')
            
            # Horizontal grid for tools in this category
            tools_in_cat = tools[start_idx:end_idx]
            self.create_horizontal_tool_grid(parent, tools_in_cat)
    
    def create_horizontal_tool_grid(self, parent, tools):
        """Create horizontal grid of tools for full screen width"""
        # Use 8 tools per row for maximum width utilization
        tools_per_row = 8  # Increased for maximum width utilization
        
        for i in range(0, len(tools), tools_per_row):
            # Create row frame
            row_frame = tk.Frame(parent, bg=self.colors['card'])
            row_frame.pack(fill=tk.X, pady=1, padx=2)  # Minimal spacing
            
            # Add tools to this row
            for j in range(tools_per_row):
                tool_index = i + j
                if tool_index < len(tools):
                    tool_name, tool_file, tool_color = tools[tool_index]
                    self.create_horizontal_tool_button(row_frame, tool_name, tool_file, tool_color)
    
    def create_horizontal_tool_button(self, parent, name, filename, color):
        """Create horizontal tool button for maximum width utilization"""
        button = tk.Button(parent, 
                          text=name, 
                          font=('Arial', 9, 'bold'),  # Smaller for more buttons
                          bg=color, fg='white',
                          relief='flat', bd=0, cursor='hand2',
                          padx=6, pady=4,  # Minimal padding for maximum space
                          command=lambda f=filename, n=name: self.launch_tool(f, n))
        button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)  # Minimal spacing
        
        # Simple hover effect
        def on_enter(e):
            button.config(relief='raised', bd=2)
        
        def on_leave(e):
            button.config(relief='flat', bd=0)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="● Ready", 
                                    font=('Arial', 10, 'bold'), 
                                    bg=self.colors['card'], fg=self.colors['success'])
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Time display
        self.time_label = tk.Label(status_frame, text="", 
                                  font=('Arial', 10), 
                                  bg=self.colors['card'], fg=self.colors['text_secondary'])
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Update time
        self.update_time()
    
    def launch_tool(self, filename, tool_name):
        """Launch a tool"""
        if self.check_file_exists(filename):
            self.status_label.config(text=f"● Starting {tool_name}...", fg=self.colors['success'])
            self.root.after(1000, self.run_script, filename, tool_name)
        else:
            messagebox.showerror("Error", f"{filename} not found!")
    
    def run_script(self, script_name, tool_name):
        """Run a Python script"""
        try:
            subprocess.Popen([sys.executable, script_name])
            self.status_label.config(text=f"● Launched {tool_name}", fg=self.colors['success'])
            self.root.after(2000, self.root.quit)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {e}")
            self.status_label.config(text="● Launch failed", fg=self.colors['danger'])
    
    def check_file_exists(self, filename):
        """Check if file exists"""
        file_path = self.base_path / filename
        return file_path.exists()
    
    def update_system_stats(self):
        """Update system statistics"""
        while self.monitoring_active:
            try:
                self.system_stats['cpu_usage'] = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.system_stats['memory_usage'] = memory.percent
                disk = psutil.disk_usage('/')
                self.system_stats['disk_usage'] = (disk.used / disk.total) * 100
                network = psutil.net_io_counters()
                self.system_stats['network_active'] = network.bytes_sent + network.bytes_recv > 0
                self.system_stats['running_processes'] = len(psutil.pids())
                
                self.root.after(0, self.update_stats_display)
                time.sleep(2)
            except Exception as e:
                print(f"Error updating stats: {e}")
    
    def update_stats_display(self):
        """Update statistics display"""
        try:
            self.stat_labels['cpu'].config(text=f"{self.system_stats['cpu_usage']:.1f}%")
            self.stat_labels['memory'].config(text=f"{self.system_stats['memory_usage']:.1f}%")
            self.stat_labels['disk'].config(text=f"{self.system_stats['disk_usage']:.1f}%")
            self.stat_labels['processes'].config(text=str(self.system_stats['running_processes']))
            
            network_text = "Active" if self.system_stats['network_active'] else "Idle"
            network_color = self.colors['success'] if self.system_stats['network_active'] else self.colors['text_secondary']
            self.stat_labels['network'].config(text=network_text, fg=network_color)
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def update_time(self):
        """Update time display"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, self.update_time)
        except:
            pass

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = SimpleLauncherGUI(root)
        
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
