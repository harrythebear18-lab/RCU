#!/usr/bin/env python3
"""
Homelab Monitoring Dashboard
Unified dashboard launcher for all homelab monitoring tools
Integrates CPU, GPU, Network, RAM, and RDMA monitoring tools
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
import sys
from pathlib import Path
import json
import heapq
import queue
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
import psutil

class TaskScheduler:
    """Advanced task scheduler with priority queues"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.task_queue = []
        self.running_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.priority_weights = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        self.task_counter = 0
        self._lock = threading.RLock()
        
    def schedule_task(self, func, priority='medium', *args, **kwargs):
        """Schedule a task with priority"""
        with self._lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            
            task = {
                'id': task_id,
                'func': func,
                'args': args,
                'kwargs': kwargs,
                'priority': priority,
                'created_at': time.time()
            }
            
            priority_score = self.priority_weights.get(priority, 2)
            heapq.heappush(self.task_queue, (priority_score, task_id, task))
            return task_id
    
    def execute_next(self):
        """Execute the next highest priority task"""
        with self._lock:
            if not self.task_queue:
                return None
            
            score, task_id, task = heapq.heappop(self.task_queue)
            return self._execute_task(task)
    
    def _execute_task(self, task):
        """Execute a task"""
        task_id = task['id']
        self.running_tasks[task_id] = {
            'task': task,
            'started_at': time.time()
        }
        
        future = self.executor.submit(task['func'], *task['args'], **task['kwargs'])
        future.add_done_callback(lambda f: self._task_completed(task_id, f))
        return task_id
    
    def _task_completed(self, task_id, future):
        """Handle task completion"""
        with self._lock:
            if task_id in self.running_tasks:
                task_info = self.running_tasks.pop(task_id)
                task_info['completed_at'] = time.time()

class ResourceMonitor:
    """Advanced resource monitoring"""
    
    def __init__(self):
        self.cpu_history = deque(maxlen=60)
        self.memory_history = deque(maxlen=60)
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def _update_loop(self):
        """Background resource monitoring"""
        while True:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory.percent)
                
                time.sleep(2)
            except Exception:
                time.sleep(5)
    
    def get_load_score(self):
        """Get current system load score (0-1)"""
        current_cpu = self.cpu_history[-1] if self.cpu_history else 0
        current_memory = self.memory_history[-1] if self.memory_history else 0
        
        return (current_cpu / 100 * 0.6) + (current_memory / 100 * 0.4)

class HomelabDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Homelab Monitoring Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme (consistent with other tools)
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'card_hover': '#3a3a3a',
            'primary': '#00ff88',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00d4ff',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#0078ff',
            'border': '#3f3f46'
        }
        
        # Advanced performance systems
        self.task_scheduler = TaskScheduler(max_workers=6)
        self.resource_monitor = ResourceMonitor()
        
        # Tool definitions - Enhanced with main categories
        self.tools = {
    "CPU Monitor": {
        "path": "CPU Monitor/cpu_monitor.py",
        "icon": "\ud83d\udcbb",
        "description": "CPU usage monitoring",
        "status": "ready",
        "color": "#00ff88"
    },
    "GPU Monitor": {
        "path": "GPU Monitor/gpu_monitor.py",
        "icon": "\ud83c\udfae",
        "description": "GPU usage monitoring",
        "status": "ready",
        "color": "#00ff88"
    },
    "Network Monitor": {
        "path": "Network Monitor/network_monitor.py",
        "icon": "\ud83c\udf10",
        "description": "Network activity monitoring",
        "status": "ready",
        "color": "#00ff88"
    },
    "Storage Monitor": {
        "path": "Storage Monitor/storage_monitor.py",
        "icon": "\ud83d\udcbe",
        "description": "Disk space monitoring",
        "status": "ready",
        "color": "#00ff88"
    },
    "Memory Monitor": {
        "path": "Memory Monitor/ram_monitor_gui.py",
        "icon": "\ud83e\udde0",
        "description": "RAM usage monitoring",
        "status": "ready",
        "color": "#00ff88"
    },
    "Web Dashboard": {
        "path": "Core Services/web_dashboard.py",
        "icon": "\ud83d\udcca",
        "description": "Web-based monitoring dashboard",
        "status": "ready",
        "color": "#00aaff"
    },
    "Backup Manager": {
        "path": "Core Services/backup_manager.py",
        "icon": "\ud83d\udcbf",
        "description": "System backup management",
        "status": "ready",
        "color": "#00aaff"
    },
    "Power Manager": {
        "path": "Power Manager/power_manager.py",
        "icon": "\u26a1",
        "description": "Power management utilities",
        "status": "ready",
        "color": "#00aaff"
    },
    "VPN Gateway": {
        "path": "VPN Gateway/vpn_gateway.py",
        "icon": "\ud83d\udd10",
        "description": "VPN connection management",
        "status": "ready",
        "color": "#00aaff"
    },
    "RDMA Desktop App": {
        "path": "RDMA Desktop App/rdma_desktop_app.py",
        "icon": "\ud83d\udd0c",
        "description": "RDMA desktop application",
        "status": "ready",
        "color": "#00aaff"
    },
    "System Dashboard": {
        "path": "homelab_dashboard.py",
        "icon": "\ud83c\udfe0",
        "description": "Main system dashboard",
        "status": "ready",
        "color": "#00aaff"
    },
    "System Launcher": {
        "path": "homelab_launcher.py",
        "icon": "\ud83d\ude80",
        "description": "Main system launcher",
        "status": "ready",
        "color": "#00aaff"
    },
    "Auto Connect": {
        "path": "Auto_Connect_Launcher.bat",
        "icon": "\ud83d\udd17",
        "description": "Auto connection launcher",
        "status": "ready",
        "color": "#00aaff"
    },
    "Windows Compatibility Fix": {
        "path": "Fix_Windows_Compatibility.bat",
        "icon": "\ud83d\udd27",
        "description": "Windows compatibility fixes",
        "status": "ready",
        "color": "#00aaff"
    },
    "RAM Sharing GUI": {
        "path": "RAM_Sharing_GUI.py",
        "icon": "\ud83d\udd04",
        "description": "RAM sharing interface",
        "status": "ready",
        "color": "#00aaff"
    },
    "System Audit": {
        "path": "comprehensive_chunked_audit.py",
        "icon": "\ud83d\udd0d",
        "description": "Comprehensive system audit",
        "status": "ready",
        "color": "#00aaff"
    }
}

        
        # Category definitions for better organization
        self.categories = {
            'System Monitoring': {
                'icon': '📊',
                'color': '#00ff88',
                'description': 'Real-time system monitoring and optimization'
            },
            'Infrastructure & Management': {
                'icon': '🏗️',
                'color': '#ff6b6b',
                'description': 'Core infrastructure and management services'
            },
            'Distributed Computing': {
                'icon': '⚡',
                'color': '#0078ff',
                'description': 'High-performance computing and RDMA systems'
            },
            'RAM Sharing': {
                'icon': '🖥️',
                'color': '#00d4ff',
                'description': 'Cross-PC memory sharing and optimization'
            },
            'System Tools': {
                'icon': '🛠️',
                'color': '#ffaa00',
                'description': 'System utilities and testing tools'
            }
        }
        
        # Running processes tracking
        self.running_processes = {}
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Check tool availability
        self.check_tool_availability()
        
        # Start live monitoring
        self.start_live_monitoring()
    
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        styles = {
            'Title.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['primary'], 'font': ('Segoe UI', 24, 'bold')},
            'Subtitle.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['text_secondary'], 'font': ('Segoe UI', 12)},
            'Card.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'ToolCard.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'Info.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 11)},
            'ToolName.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 14, 'bold')},
            'ToolDesc.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text_secondary'], 'font': ('Segoe UI', 10)},
            'Status.TLabel': {'background': self.colors['card'], 'foreground': self.colors['success'], 'font': ('Segoe UI', 10, 'bold')},
            'Primary.TButton': {'background': self.colors['primary'], 'foreground': self.colors['bg'], 'font': ('Segoe UI', 11, 'bold'), 'relief': 'flat', 'borderwidth': 0},
            'Secondary.TButton': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 10), 'relief': 'flat', 'borderwidth': 1},
            'Danger.TButton': {'background': self.colors['danger'], 'foreground': self.colors['bg'], 'font': ('Segoe UI', 11, 'bold'), 'relief': 'flat', 'borderwidth': 0},
        }
        
        for style_name, config in styles.items():
            style.configure(style_name, **config)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Header
        self.create_header()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Quick stats bar
        self.create_stats_bar(main_container)
        
        # Tools grid
        tools_frame = tk.Frame(main_container, bg=self.colors['bg'])
        tools_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        self.create_tools_grid(tools_frame)
        
        # Bottom control panel
        self.create_control_panel(main_container)
    
    def create_header(self):
        """Create header"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=100)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title section
        title_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(title_frame, text="Homelab Monitoring Dashboard", 
                             font=('Segoe UI', 28, 'bold'), 
                             fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame, text="Unified monitoring and optimization toolkit", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(anchor=tk.W, pady=(8, 0))
        
        # Status indicator
        self.header_status = tk.Label(header_frame, text="● SYSTEM READY", 
                                     font=('Segoe UI', 14, 'bold'), 
                                     fg=self.colors['success'], bg=self.colors['bg'])
        self.header_status.pack(side=tk.RIGHT, anchor=tk.E, pady=30)
    
    def create_stats_bar(self, parent):
        """Create quick stats bar with live data"""
        stats_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Live system stats
        self.live_stats = {
            'cpu': tk.Label(stats_frame, text="CPU: 0%", 
                           font=('Segoe UI', 11, 'bold'), 
                           fg=self.colors['info'], bg=self.colors['card']),
            'memory': tk.Label(stats_frame, text="RAM: 0%", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg=self.colors['warning'], bg=self.colors['card']),
            'disk': tk.Label(stats_frame, text="Disk: 0%", 
                            font=('Segoe UI', 11, 'bold'), 
                            fg=self.colors['success'], bg=self.colors['card']),
            'network': tk.Label(stats_frame, text="🌐", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg=self.colors['text_secondary'], bg=self.colors['card']),
            'tools_available': tk.Label(stats_frame, text="19 Tools", 
                                       font=('Segoe UI', 11, 'bold'), 
                                       fg=self.colors['primary'], bg=self.colors['card']),
            'processes_running': tk.Label(stats_frame, text="0 Running", 
                                          font=('Segoe UI', 11, 'bold'), 
                                          fg=self.colors['warning'], bg=self.colors['card'])
        }
        
        # Pack stats
        for stat_label in self.live_stats.values():
            stat_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Start live monitoring
        self.start_live_monitoring()
    
    def create_tools_grid(self, parent):
        """Create tools grid organized by categories"""
        # Grid container
        grid_container = tk.Frame(parent, bg=self.colors['bg'])
        grid_container.pack(fill=tk.BOTH, expand=True)
        
        # Create category sections
        row = 0
        for category_name, category_info in self.categories.items():
            # Category header
            category_frame = tk.Frame(grid_container, bg=self.colors['bg'])
            category_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='ew')
            
            # Category title
            title_frame = tk.Frame(category_frame, bg=self.colors['card'], relief='flat', bd=0)
            title_frame.pack(fill=tk.X)
            
            # Category icon and name
            cat_header = tk.Frame(title_frame, bg=self.colors['card'])
            cat_header.pack(fill=tk.X, padx=20, pady=15)
            
            icon_label = tk.Label(cat_header, text=category_info['icon'], 
                                font=('Segoe UI', 20), 
                                fg=category_info['color'], bg=self.colors['card'])
            icon_label.pack(side=tk.LEFT)
            
            name_label = tk.Label(cat_header, text=category_name, 
                                font=('Segoe UI', 18, 'bold'), 
                                fg=self.colors['text'], bg=self.colors['card'])
            name_label.pack(side=tk.LEFT, padx=(15, 0))
            
            # Category description
            desc_label = tk.Label(cat_header, text=category_info['description'], 
                                font=('Segoe UI', 10), 
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
            desc_label.pack(side=tk.LEFT, padx=(20, 0))
            
            # Count of tools in this category
            tools_in_category = [name for name, info in self.tools.items() 
                               if info.get('category') == category_name]
            count_label = tk.Label(cat_header, text=f"{len(tools_in_category)} tools", 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg=category_info['color'], bg=self.colors['card'])
            count_label.pack(side=tk.RIGHT)
            
            # Tools in this category
            row += 1
            col = 0
            for tool_name, tool_info in self.tools.items():
                if tool_info.get('category') == category_name:
                    card = self.create_tool_card(grid_container, tool_name, tool_info)
                    card.grid(row=row, column=col, padx=10, pady=5, sticky='nsew')
                    
                    col += 1
                    if col >= 3:  # 3 columns per row
                        col = 0
                        row += 1
            
            if col > 0:  # Add spacing after category
                row += 1
        
        # Configure grid weights
        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1)
        for i in range(row + 1):
            grid_container.grid_rowconfigure(i, weight=1)
    
    def create_tool_card(self, parent, tool_name, tool_info):
        """Create individual tool card with original working design"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        card.configure(highlightbackground=tool_info['color'], highlightthickness=2)
        
        # Card content with proper spacing
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon and name header
        header_frame = tk.Frame(content_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = tk.Label(header_frame, text=tool_info['icon'], 
                            font=('Segoe UI', 24), 
                            fg=tool_info['color'], bg=self.colors['card'])
        icon_label.pack(side=tk.LEFT)
        
        name_label = tk.Label(header_frame, text=tool_name, 
                            font=('Segoe UI', 16, 'bold'), 
                            fg=self.colors['text'], bg=self.colors['card'])
        name_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status indicator
        status_text = "READY" if tool_info['status'] == 'ready' else "ADVANCED"
        status_color = self.colors['success'] if tool_info['status'] == 'ready' else self.colors['info']
        
        status_label = tk.Label(header_frame, text=f"● {status_text}", 
                              font=('Segoe UI', 10, 'bold'), 
                              fg=status_color, bg=self.colors['card'])
        status_label.pack(side=tk.RIGHT)
        
        # Description
        desc_label = tk.Label(content_frame, text=tool_info['description'], 
                            font=('Segoe UI', 10), 
                            fg=self.colors['text_secondary'], bg=self.colors['card'],
                            wraplength=250, justify=tk.LEFT)
        desc_label.pack(fill=tk.X, pady=(0, 15))
        
        # Action buttons - original working design
        button_frame = tk.Frame(content_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X)
        
        # Launch button - original style
        launch_btn = tk.Button(button_frame, text="🚀 Launch", 
                             command=lambda tn=tool_name, ti=tool_info: self.launch_tool(tn, ti),
                             bg=tool_info['color'], fg=self.colors['bg'], 
                             font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                             cursor='hand2', width=12, height=1)
        launch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Info button - original style
        info_btn = tk.Button(button_frame, text="ℹ️ Info", 
                           command=lambda tn=tool_name, ti=tool_info: self.show_tool_info(tn, ti),
                           bg=self.colors['border'], fg=self.colors['text'], 
                           font=('Segoe UI', 10), relief='flat', bd=1,
                           cursor='hand2', width=8, height=1)
        info_btn.pack(side=tk.RIGHT)
        
        return card
    
    def create_control_panel(self, parent):
        """Create bottom control panel"""
        control_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Left side - Global actions
        left_frame = tk.Frame(control_frame, bg=self.colors['card'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=15)
        
        actions = [
            ("🔄 Refresh All", self.refresh_all_tools, self.colors['info']),
            ("🛑 Stop All", self.stop_all_tools, self.colors['danger']),
            ("📊 System Report", self.generate_system_report, self.colors['warning'])
        ]
        
        for text, command, color in actions:
            btn = tk.Button(left_frame, text=text, command=command,
                          bg=color, fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                          relief='flat', bd=0, padx=15, pady=8, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Right side - Settings
        right_frame = tk.Frame(control_frame, bg=self.colors['card'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=15)
        
        settings_btn = tk.Button(right_frame, text="⚙️ Settings", 
                               command=self.open_settings,
                               bg=self.colors['card_hover'], fg=self.colors['text'], 
                               font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                               cursor='hand2')
        settings_btn.pack(side=tk.RIGHT)
    
    def check_tool_availability(self):
        """Check if all tools are available"""
        available_count = 0
        for tool_name, tool_info in self.tools.items():
            tool_path = Path(tool_info['path'])
            if tool_path.exists():
                tool_info['available'] = True
                available_count += 1
            else:
                tool_info['available'] = False
        
        if hasattr(self, 'live_stats'):
            self.live_stats['tools_available'].config(text=f"{available_count}/{len(self.tools)} Tools")
        
        if available_count == len(self.tools):
            self.header_status.config(text="All Tools Ready", fg=self.colors['success'])
        else:
            self.header_status.config(text="Some Tools Missing", fg=self.colors['warning'])
    
    def launch_tool(self, tool_name, tool_info):
        """Launch a monitoring tool"""
        print(f"Attempting to launch: {tool_name}")
        
        # Check if tool path exists directly
        tool_path = Path(tool_info['path'])
        if not tool_path.exists():
            messagebox.showerror("Tool Not Found", f"Tool not found: {tool_info['path']}")
            return
        
        if tool_name in self.running_processes:
            messagebox.showinfo("Tool Running", f"{tool_name} is already running")
            return
        
        try:
            print(f"Launching tool: {tool_name} from {tool_info['path']}")
            
            # Launch the tool based on file type
            if tool_info['path'].endswith('.py'):
                # Launch Python script
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(['python', tool_info['path']], 
                                            cwd=os.path.dirname(tool_info['path']) or '.',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    process = subprocess.Popen(['python3', tool_info['path']], 
                                            cwd=os.path.dirname(tool_info['path']) or '.')
            else:
                # Launch batch file or other executable
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen([tool_info['path']], 
                                            cwd=os.path.dirname(tool_info['path']) or '.',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    process = subprocess.Popen([tool_info['path']], 
                                            cwd=os.path.dirname(tool_info['path']) or '.')
            
            self.running_processes[tool_name] = process
            
            # Update header status
            self.header_status.config(text=f"● LAUNCHED {tool_name.upper()}", fg=self.colors['primary'])
            
            # Update running tools count
            if hasattr(self, 'live_stats'):
                self.live_stats['processes_running'].config(text=f"{len(self.running_processes)} Running")
            
            messagebox.showinfo("Launch Success", f"{tool_name} has been launched successfully!")
            
        except Exception as e:
            print(f"Error launching {tool_name}: {e}")
            messagebox.showerror("Launch Error", f"Failed to launch {tool_name}: {str(e)}")
    
    def show_tool_info(self, tool_name, tool_info):
        """Show detailed tool information"""
        info_window = tk.Toplevel(self.root)
        info_window.title(f"{tool_name} - Information")
        info_window.geometry("400x300")
        info_window.configure(bg=self.colors['bg'])
        info_window.transient(self.root)
        info_window.grab_set()
        
        # Tool info content
        info_frame = tk.Frame(info_window, bg=self.colors['card'], relief='flat', bd=0)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(info_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text=tool_info['icon'], 
                font=('Segoe UI', 32), 
                fg=tool_info['color'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        tk.Label(header_frame, text=tool_name, 
                font=('Segoe UI', 20, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(15, 0))
        
        # Details
        details_frame = tk.Frame(info_frame, bg=self.colors['card'])
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Category
        tk.Label(details_frame, text="Category:", 
                font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack(anchor='w')
        tk.Label(details_frame, text=tool_info.get('category', 'Unknown'), 
                font=('Segoe UI', 12), 
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w', pady=(0, 10))
        
        # Description
        tk.Label(details_frame, text="Description:", 
                font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack(anchor='w')
        tk.Label(details_frame, text=tool_info['description'], 
                font=('Segoe UI', 12), 
                fg=self.colors['text'], bg=self.colors['card'],
                wraplength=350, justify='left').pack(anchor='w', pady=(0, 10))
        
        # Path
        tk.Label(details_frame, text="Path:", 
                font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack(anchor='w')
        tk.Label(details_frame, text=tool_info['path'], 
                font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['card'],
                wraplength=350, justify='left').pack(anchor='w', pady=(0, 10))
        
        # Status
        tk.Label(details_frame, text="Status:", 
                font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack(anchor='w')
        status_text = "Available" if tool_info.get('available', True) else "Not Available"
        status_color = self.colors['success'] if tool_info.get('available', True) else self.colors['danger']
        tk.Label(details_frame, text=status_text, 
                font=('Segoe UI', 12, 'bold'), 
                fg=status_color, bg=self.colors['card']).pack(anchor='w', pady=(0, 10))
        
        # Availability
        if tool_info.get('available', True):
            available_text = "✅ Tool is available and ready to launch"
            available_color = self.colors['success']
        else:
            available_text = "❌ Tool file not found at expected location"
            available_color = self.colors['danger']
        
        tk.Label(details_frame, text=available_text, 
                font=('Segoe UI', 10), 
                fg=available_color, bg=self.colors['card']).pack(anchor='w', pady=(10, 0))
        
        # Close button
        close_btn = tk.Button(info_window, text="Close", 
                            command=info_window.destroy,
                            bg=self.colors['primary'], fg=self.colors['bg'], 
                            font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                            cursor='hand2')
        close_btn.pack(pady=20)
    
    def start_live_monitoring(self):
        """Start live system monitoring"""
        def update_stats():
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.live_stats['cpu'].config(text=f"CPU: {cpu_percent:.0f}%")
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.live_stats['memory'].config(text=f"RAM: {memory.percent:.0f}%")
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.live_stats['disk'].config(text=f"Disk: {disk_percent:.0f}%")
                
                # Network status
                net_io = psutil.net_io_counters()
                if net_io.bytes_sent > 0 or net_io.bytes_recv > 0:
                    self.live_stats['network'].config(text="🌐", fg=self.colors['success'])
                else:
                    self.live_stats['network'].config(text="🌐", fg=self.colors['text_secondary'])
                
                # Running processes
                self.live_stats['processes_running'].config(text=f"{len(self.running_processes)} Running")
                
                # Update header status based on system load
                if cpu_percent > 80 or memory.percent > 80:
                    self.header_status.config(text="● HIGH LOAD", fg=self.colors['danger'])
                elif len(self.running_processes) > 0:
                    self.header_status.config(text="● TOOLS ACTIVE", fg=self.colors['primary'])
                else:
                    self.header_status.config(text="● SYSTEM READY", fg=self.colors['success'])
                
            except Exception as e:
                print(f"Error updating stats: {e}")
            
            # Schedule next update
            self.root.after(2000, update_stats)  # Update every 2 seconds
        
        # Start the monitoring loop
        self.root.after(1000, update_stats)  # Start after 1 second
    
    def refresh_all_tools(self):
        """Refresh all tool status"""
        self.check_tool_availability()
        
        # Check running processes
        stopped_tools = []
        for tool_name, process in list(self.running_processes.items()):
            if process.poll() is not None:  # Process has ended
                stopped_tools.append(tool_name)
                del self.running_processes[tool_name]
        
        if stopped_tools:
            messagebox.showinfo("Refresh Complete", f"Tools refreshed. Stopped: {', '.join(stopped_tools)}")
        else:
            messagebox.showinfo("Refresh Complete", "All tools status refreshed")
        
        self.update_running_count()
    
    def stop_all_tools(self):
        """Stop all running tools"""
        if not self.running_processes:
            messagebox.showinfo("No Tools Running", "No monitoring tools are currently running")
            return
        
        result = messagebox.askyesno("Stop All Tools", 
                                    f"Stop all {len(self.running_processes)} running monitoring tools?")
        if not result:
            return
        
        stopped_count = 0
        for tool_name, process in list(self.running_processes.items()):
            try:
                process.terminate()
                stopped_count += 1
            except:
                pass
        
        self.running_processes.clear()
        self.update_running_count()
        
        messagebox.showinfo("Tools Stopped", f"Stopped {stopped_count} monitoring tools")
    
    def generate_system_report(self):
        """Generate system monitoring report"""
        report = "HOMELAB MONITORING REPORT\n"
        report += "=" * 40 + "\n\n"
        
        # Tool availability
        report += "TOOL STATUS:\n"
        for tool_name, tool_info in self.tools.items():
            status = "✓ Available" if tool_info.get('available', False) else "✗ Missing"
            running = " (Running)" if tool_name in self.running_processes else ""
            report += f"  {tool_name}: {status}{running}\n"
        
        report += f"\nRUNNING PROCESSES: {len(self.running_processes)}\n"
        
        # System info
        try:
            import psutil
            report += f"\nSYSTEM INFORMATION:\n"
            report += f"  CPU Usage: {psutil.cpu_percent()}%\n"
            report += f"  Memory Usage: {psutil.virtual_memory().percent}%\n"
            report += f"  Disk Usage: {psutil.disk_usage('/').percent}%\n"
        except:
            report += "\nSystem information unavailable (psutil required)\n"
        
        # Show report
        report_window = tk.Toplevel(self.root)
        report_window.title("System Report")
        report_window.geometry("500x400")
        report_window.configure(bg=self.colors['bg'])
        
        text_widget = tk.Text(report_window, bg=self.colors['card'], fg=self.colors['text'],
                             font=('Consolas', 10), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', report)
        text_widget.config(state=tk.DISABLED)
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Dashboard Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors['bg'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        main_frame = tk.Frame(settings_window, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title = tk.Label(main_frame, text="Dashboard Settings", 
                        font=('Segoe UI', 16, 'bold'), 
                        fg=self.colors['primary'], bg=self.colors['card'])
        title.pack(pady=(0, 20))
        
        # Auto-start option
        auto_start_var = tk.BooleanVar()
        auto_start_check = tk.Checkbutton(main_frame, text="Auto-start tools on dashboard launch",
                                        variable=auto_start_var,
                                        bg=self.colors['card'], fg=self.colors['text'],
                                        font=('Segoe UI', 11),
                                        selectcolor=self.colors['card_hover'])
        auto_start_check.pack(anchor=tk.W, pady=10)
        
        # Theme selection
        theme_label = tk.Label(main_frame, text="Theme:", 
                             font=('Segoe UI', 11), 
                             fg=self.colors['text'], bg=self.colors['card'])
        theme_label.pack(anchor=tk.W, pady=(20, 5))
        
        theme_var = tk.StringVar(value="Dark")
        theme_combo = ttk.Combobox(main_frame, textvariable=theme_var, 
                                 values=["Dark", "Light"], state="readonly")
        theme_combo.pack(anchor=tk.W, padx=(20, 0))
        
        # Close button
        close_btn = tk.Button(main_frame, text="Close", command=settings_window.destroy,
                            bg=self.colors['primary'], fg=self.colors['bg'], 
                            font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                            padx=20, pady=10)
        close_btn.pack(side=tk.BOTTOM, pady=20)
    
    def update_running_count(self):
        """Update running processes count"""
        count = len(self.running_processes)
        self.quick_stats['processes_running'].config(text=f"{count} Running")
        
        if count > 0:
            self.quick_stats['processes_running'].config(fg=self.colors['success'])
            self.header_status.config(text=f"● {count} TOOLS ACTIVE", fg=self.colors['info'])
        else:
            self.quick_stats['processes_running'].config(fg=self.colors['warning'])
            self.header_status.config(text="● SYSTEM READY", fg=self.colors['success'])

def main():
    """Main entry point"""
    root = tk.Tk()
    app = HomelabDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
