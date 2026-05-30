#!/usr/bin/env python3
"""
Homelab Launcher - Complete Tool Management System
Central launcher with buttons for all homelab tools
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import time
import threading
import json
import logging
from pathlib import Path
import psutil
import platform
from datetime import datetime
import heapq
import queue
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor

# Add path handling
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Add Core Services to path
core_services_dir = current_dir / "Core Services"
if str(core_services_dir) not in sys.path:
    sys.path.insert(0, str(core_services_dir))
# Try to import PIL for logo support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - using text-based branding")

# Add common directory to path for subnet discovery
sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
try:
    from subnet_manager import integrate_subnet_discovery, get_subnet_apps
    SUBNET_AVAILABLE = True
except ImportError:
    SUBNET_AVAILABLE = False

class TaskScheduler:
    """Advanced task scheduler with priority queues and adaptive load balancing"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.task_queue = []
        self.running_tasks = {}
        self.completed_tasks = deque(maxlen=1000)
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
                self.completed_tasks.append(task_info)

class ResourceMonitor:
    """Advanced resource monitoring with predictive capabilities"""
    
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
    
    def get_current_usage(self):
        """Get current resource usage"""
        return {
            'cpu': self.cpu_history[-1] if self.cpu_history else 0,
            'memory': self.memory_history[-1] if self.memory_history else 0
        }

class EventBus:
    """Decoupled event system for efficient communication"""
    
    def __init__(self):
        self.subscribers = defaultdict(set)
        self.event_queue = queue.Queue()
        self.batch_size = 50
        self.batch_timeout = 0.1
        self._processing_thread = threading.Thread(target=self._process_events, daemon=True)
        self._processing_thread.start()
    
    def subscribe(self, event_type, callback):
        """Subscribe to event type"""
        self.subscribers[event_type].add(callback)
    
    def publish(self, event_type, data):
        """Publish event (non-blocking)"""
        try:
            self.event_queue.put_nowait((event_type, data, time.time()))
        except queue.Full:
            try:
                self.event_queue.get_nowait()
                self.event_queue.put_nowait((event_type, data, time.time()))
            except queue.Empty:
                pass
    
    def _process_events(self):
        """Process events in batches"""
        batch = []
        last_process = time.time()
        
        while True:
            try:
                timeout = self.batch_timeout - (time.time() - last_process)
                if timeout <= 0:
                    timeout = 0.001
                
                try:
                    event_type, data, timestamp = self.event_queue.get(timeout=timeout)
                    batch.append((event_type, data, timestamp))
                except queue.Empty:
                    pass
                
                current_time = time.time()
                should_process = (
                    len(batch) >= self.batch_size or
                    (batch and current_time - last_process >= self.batch_timeout)
                )
                
                if should_process and batch:
                    self._process_batch(batch)
                    batch.clear()
                    last_process = current_time
                
            except Exception as e:
                print(f"EventBus error: {e}")
                time.sleep(0.1)
    
    def _process_batch(self, batch):
        """Process a batch of events"""
        events_by_type = defaultdict(list)
        for event_type, data, timestamp in batch:
            events_by_type[event_type].append((data, timestamp))
        
        for event_type, events in events_by_type.items():
            subscribers = self.subscribers.get(event_type, set())
            for callback in subscribers:
                try:
                    for data, timestamp in events:
                        callback(data)
                except Exception as e:
                    print(f"Event callback error: {e}")

class HomelabLauncher:
    """Complete homelab tool launcher with Visentrix branding"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Visentrix Homelab Tools - Complete System Management")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        self.root.minsize(1200, 700)
        
        # Modern color scheme (consistent with all tools)
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
            'graph_bg': '#242424',
            'graph_line': '#00ff88'
        }
        
        # Visentrix logo paths
        self.logo_paths = {
            'primary': 'D:\\Home Projects\\dx11(homelab)\\logo.png',
            'secondary': 'D:\\Home Projects\\dx11(homelab)\\logo1.png'
        }
        self.logo_images = {}
        
        # Load logo images
        self.load_logo_images()
        
        # Tool management
        self.running_processes = {}
        self.tool_status = {}
        
        # Advanced performance systems
        self.task_scheduler = TaskScheduler(max_workers=6)
        self.resource_monitor = ResourceMonitor()
        self.event_bus = EventBus()
        
        # Tool definitions with paths and commands
        self.tools = {
    "root": {
        "CPU Monitor": {
            "path": "CPU Monitor/cpu_monitor.py",
            "icon": "\ud83d\udcbb",
            "description": "CPU usage monitoring",
            "category": "monitoring"
        },
        "GPU Monitor": {
            "path": "GPU Monitor/gpu_monitor.py",
            "icon": "\ud83c\udfae",
            "description": "GPU usage monitoring",
            "category": "monitoring"
        },
        "Network Monitor": {
            "path": "Network Monitor/network_monitor.py",
            "icon": "\ud83c\udf10",
            "description": "Network activity monitoring",
            "category": "monitoring"
        },
        "Storage Monitor": {
            "path": "Storage Monitor/storage_monitor.py",
            "icon": "\ud83d\udcbe",
            "description": "Disk space monitoring",
            "category": "monitoring"
        },
        "Memory Monitor": {
            "path": "Memory Monitor/ram_monitor_gui.py",
            "icon": "\ud83e\udde0",
            "description": "RAM usage monitoring",
            "category": "monitoring"
        },
        "Web Dashboard": {
            "path": "Core Services/web_dashboard.py",
            "icon": "\ud83d\udcca",
            "description": "Web-based monitoring dashboard",
            "category": "services"
        },
        "Backup Manager": {
            "path": "Core Services/backup_manager.py",
            "icon": "\ud83d\udcbf",
            "description": "System backup management",
            "category": "services"
        },
        "Power Manager": {
            "path": "Power Manager/power_manager.py",
            "icon": "\u26a1",
            "description": "Power management utilities",
            "category": "services"
        },
        "VPN Gateway": {
            "path": "VPN Gateway/vpn_gateway.py",
            "icon": "\ud83d\udd10",
            "description": "VPN connection management",
            "category": "network"
        },
        "RDMA Desktop App": {
            "path": "RDMA Desktop App/rdma_desktop_app.py",
            "icon": "\ud83d\udd0c",
            "description": "RDMA desktop application",
            "category": "rdma"
        },
        "System Dashboard": {
            "path": "homelab_dashboard.py",
            "icon": "\ud83c\udfe0",
            "description": "Main system dashboard",
            "category": "system"
        },
        "System Launcher": {
            "path": "homelab_launcher.py",
            "icon": "\ud83d\ude80",
            "description": "Main system launcher",
            "category": "system"
        },
        "Auto Connect": {
            "path": "Auto_Connect_Launcher.bat",
            "icon": "\ud83d\udd17",
            "description": "Auto connection launcher",
            "category": "utilities"
        },
        "Windows Compatibility Fix": {
            "path": "Fix_Windows_Compatibility.bat",
            "icon": "\ud83d\udd27",
            "description": "Windows compatibility fixes",
            "category": "utilities"
        },
        "RAM Sharing GUI": {
            "path": "RAM_Sharing_GUI.py",
            "icon": "\ud83d\udd04",
            "description": "RAM sharing interface",
            "category": "utilities"
        },
        "System Audit": {
            "path": "comprehensive_chunked_audit.py",
            "icon": "\ud83d\udd0d",
            "description": "Comprehensive system audit",
            "category": "utilities"
        }
    }
}

        
        # Running processes tracking
        self.running_tools = {}
        self.process_lock = threading.Lock()  # Add thread synchronization
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Setup logging
        self.setup_logging()
        
        self.log_message("Homelab Launcher initialized")
    
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        styles = {
            'Title.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['primary'], 'font': ('Segoe UI', 24, 'bold')},
            'Card.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'ToolButton.TButton': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 10), 'relief': 'flat', 'borderwidth': 1},
            'Category.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 16, 'bold')},
            'Info.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text_secondary'], 'font': ('Segoe UI', 9)},
            'Status.TLabel': {'background': self.colors['card'], 'foreground': self.colors['success'], 'font': ('Segoe UI', 10, 'bold')}
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
        
        # Live data dashboard
        self.create_live_dashboard()
        
        # Tool categories
        self.create_tool_categories(main_container)
        
        # Status bar
        self.create_status_bar()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize subnet discovery
        self.subnet_communicator = None
        if SUBNET_AVAILABLE:
            self.initialize_subnet_discovery()
        
        # Start live data updates
        self.start_live_updates()
    
    def create_header(self):
        """Create header with tasteful Visentrix branding"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title section with subtle logo
        title_section = tk.Frame(header_frame, bg=self.colors['bg'])
        title_section.pack(side=tk.LEFT, anchor=tk.W, pady=20)
        
        # Title - keep original but add small logo
        title_label = tk.Label(title_section, 
                              text="🏠 Homelab Tools - Complete System Management",
                              font=('Segoe UI', 20, 'bold'),
                              fg=self.colors['primary'], 
                              bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # Add subtle Visentrix logo as small watermark
        if 'primary' in self.logo_images:
            logo_label = tk.Label(title_section, image=self.logo_images['primary'], bg=self.colors['bg'])
            logo_label.image = self.logo_images['primary']  # Keep reference
            logo_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # System info
        info_label = tk.Label(header_frame,
                            text=f"🖥️ {platform.system()} {platform.release()} | 💾 {psutil.virtual_memory().total // (1024**3)}GB RAM",
                            font=('Segoe UI', 10),
                            fg=self.colors['info'], bg=self.colors['bg'])
        info_label.pack(side=tk.RIGHT, anchor=tk.E, pady=20)
        
        # System info
        system_info = f"Windows {platform.release()} • {psutil.cpu_count()} cores • {psutil.virtual_memory().total // (1024**3)}GB RAM"
        info_label = tk.Label(header_frame, text=system_info, 
                            font=('Segoe UI', 10), 
                            fg=self.colors['info'], bg=self.colors['bg'])
        info_label.pack(side=tk.RIGHT, anchor=tk.E, pady=20)
    
    def create_live_dashboard(self):
        """Create enhanced live data dashboard"""
        dashboard_frame = tk.Frame(self.root, bg=self.colors['card'], relief='flat', bd=1)
        dashboard_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        # Dashboard title with status
        title_frame = tk.Frame(dashboard_frame, bg=self.colors['card'])
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        title_label = tk.Label(title_frame, text="📊 System Status", 
                             font=('Segoe UI', 14, 'bold'), 
                             fg=self.colors['primary'], bg=self.colors['card'])
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Real-time clock
        self.clock_label = tk.Label(title_frame, text="", 
                                   font=('Segoe UI', 11), 
                                   fg=self.colors['info'], bg=self.colors['card'])
        self.clock_label.pack(side=tk.RIGHT, anchor=tk.E)
        
        # System metrics grid
        metrics_frame = tk.Frame(dashboard_frame, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X, padx=20, pady=(5, 15))
        
        # Create metric widgets
        self.monitor_widgets = {}
        
        # CPU metrics
        cpu_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        cpu_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(cpu_frame, text="CPU", font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.monitor_widgets['cpu_usage'] = tk.Label(cpu_frame, text="0%", 
                                                   font=('Segoe UI', 12), 
                                                   fg=self.colors['success'], bg=self.colors['card'])
        self.monitor_widgets['cpu_usage'].pack()
        self.monitor_widgets['cpu_cores'] = tk.Label(cpu_frame, text="0 cores", 
                                                    font=('Segoe UI', 9), 
                                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.monitor_widgets['cpu_cores'].pack()
        
        # Memory metrics
        mem_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        mem_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(mem_frame, text="RAM", font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.monitor_widgets['mem_usage'] = tk.Label(mem_frame, text="0%", 
                                                   font=('Segoe UI', 12), 
                                                   fg=self.colors['warning'], bg=self.colors['card'])
        self.monitor_widgets['mem_usage'].pack()
        self.monitor_widgets['mem_gb'] = tk.Label(mem_frame, text="0 GB", 
                                                  font=('Segoe UI', 9), 
                                                  fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.monitor_widgets['mem_gb'].pack()
        
        # Network metrics
        net_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        net_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(net_frame, text="Network", font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.monitor_widgets['net_status'] = tk.Label(net_frame, text="Inactive", 
                                                    font=('Segoe UI', 12), 
                                                    fg=self.colors['danger'], bg=self.colors['card'])
        self.monitor_widgets['net_status'].pack()
        self.monitor_widgets['net_speed'] = tk.Label(net_frame, text="0 Mbps", 
                                                    font=('Segoe UI', 9), 
                                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.monitor_widgets['net_speed'].pack()
        
        # Storage metrics
        storage_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        storage_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(storage_frame, text="Storage", font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.monitor_widgets['disk_usage'] = tk.Label(storage_frame, text="0%", 
                                                     font=('Segoe UI', 12), 
                                                     fg=self.colors['info'], bg=self.colors['card'])
        self.monitor_widgets['disk_usage'].pack()
        self.monitor_widgets['disk_gb'] = tk.Label(storage_frame, text="0 GB", 
                                                   font=('Segoe UI', 9), 
                                                   fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.monitor_widgets['disk_gb'].pack()
        
        # Running tools count
        tools_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        tools_frame.pack(side=tk.LEFT, padx=10, pady=5)
        tk.Label(tools_frame, text="Running", font=('Segoe UI', 10, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.monitor_widgets['running_tools'] = tk.Label(tools_frame, text="0/21", 
                                                        font=('Segoe UI', 12), 
                                                        fg=self.colors['primary'], bg=self.colors['card'])
        self.monitor_widgets['running_tools'].pack()
        tk.Label(tools_frame, text="Tools", font=('Segoe UI', 9), 
                fg=self.colors['text_secondary'], bg=self.colors['card']).pack()
        
        # Dashboard title
        title_frame = tk.Frame(dashboard_frame, bg=self.colors['card'])
        title_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        tk.Label(title_frame, text="System Overview", 
                font=('Segoe UI', 14, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.last_update_label = tk.Label(title_frame, text="", 
                                        font=('Segoe UI', 9), 
                                        fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.last_update_label.pack(side=tk.RIGHT)
        
        # Live data grid
        data_frame = tk.Frame(dashboard_frame, bg=self.colors['card'])
        data_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # System Monitoring widgets - use the existing ones from the initial dashboard
        # The widgets are already created in the create_live_dashboard method
    
    def start_live_updates(self):
        """Start live data updates"""
        def update_data():
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_count = psutil.cpu_count()
                if 'cpu_usage' in self.monitor_widgets:
                    self.monitor_widgets['cpu_usage'].config(text=f"{cpu_percent:.1f}%")
                    self.monitor_widgets['cpu_cores'].config(text=f"{cpu_count} cores")
                
                # Memory metrics
                memory = psutil.virtual_memory()
                if 'mem_usage' in self.monitor_widgets:
                    self.monitor_widgets['mem_usage'].config(text=f"{memory.percent:.1f}%")
                    self.monitor_widgets['mem_gb'].config(text=f"{memory.used / (1024**3):.1f} GB")
                
                # Network metrics
                net_io = psutil.net_io_counters()
                if 'net_status' in self.monitor_widgets:
                    if net_io:
                        self.monitor_widgets['net_status'].config(text="Active")
                        # Simple speed calculation (would need previous reading for real speed)
                        self.monitor_widgets['net_speed'].config(text="Connected")
                    else:
                        self.monitor_widgets['net_status'].config(text="Inactive")
                        self.monitor_widgets['net_speed'].config(text="0 Mbps")
                
                # Storage metrics (use Windows drive C:)
                try:
                    disk = psutil.disk_usage(os.path.expandvars('%SystemDrive%\\'))
                    disk_percent = (disk.used / disk.total) * 100
                    if 'disk_usage' in self.monitor_widgets:
                        self.monitor_widgets['disk_usage'].config(text=f"{disk_percent:.1f}%")
                        self.monitor_widgets['disk_gb'].config(text=f"{disk.used / (1024**3):.0f} GB")
                except:
                    if 'disk_usage' in self.monitor_widgets:
                        self.monitor_widgets['disk_usage'].config(text="N/A")
                        self.monitor_widgets['disk_gb'].config(text="N/A")
                
                # Tools status
                running_count = len(self.running_tools)
                # Calculate total tools correctly - should be 21
                total_tools = 21  # Fixed total based on actual tool count
                if 'running_tools' in self.monitor_widgets:
                    self.monitor_widgets['running_tools'].config(text=f"{running_count}/{total_tools}")
                
                # Update tools status label
                if 'tools_status' in self.monitor_widgets:
                    if running_count > 0:
                        self.monitor_widgets['tools_status'].config(text=f"{running_count} tools running")
                    else:
                        self.monitor_widgets['tools_status'].config(text="Ready")
                
                # Update clock
                self.clock_label.config(text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
            except Exception as e:
                self.log_message(f"Live update error: {e}")
            
            # Schedule next update
            self.root.after(2000, update_data)  # Update every 2 seconds
        
        # Start updates after GUI is ready
        self.root.after(1000, update_data)
    
    def load_logo_images(self):
        """Load Visentrix logo images with tasteful sizing"""
        if not PIL_AVAILABLE:
            # Create text-based branding when PIL is not available
            self.logo_images['primary'] = "⚡"  # Lightning bolt for Visentrix
            self.logo_images['secondary'] = "◆"  # Diamond for secondary branding
            print("Using text-based Visentrix branding")
            return
            
        try:
            # Load primary logo - smaller and more subtle
            if os.path.exists(self.logo_paths['primary']):
                logo_img = Image.open(self.logo_paths['primary'])
                logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
                self.logo_images['primary'] = ImageTk.PhotoImage(logo_img)
                print("Primary logo loaded successfully")
            
            # Load secondary logo - even smaller for tool cards
            if os.path.exists(self.logo_paths['secondary']):
                logo_img = Image.open(self.logo_paths['secondary'])
                logo_img = logo_img.resize((20, 20), Image.Resampling.LANCZOS)
                self.logo_images['secondary'] = ImageTk.PhotoImage(logo_img)
                print("Secondary logo loaded successfully")
                
        except Exception as e:
            print(f"Warning: Failed to load logo images: {e}")
            # Fallback to text-based branding
            self.logo_images['primary'] = "⚡"
            self.logo_images['secondary'] = "◆"
    
    def create_tool_categories(self, parent):
        """Create tool categories with buttons"""
        # Create notebook for categories
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Extract tools from root category and organize them
        if "root" in self.tools:
            # Create categories based on tool types
            categories = {
                "System Tools": {},
                "Monitoring": {},
                "Network": {},
                "Development": {},
                "Utilities": {},
                "Testing": {}
            }
            
            # Organize tools into categories
            for tool_name, tool_info in self.tools["root"].items():
                # Simple categorization based on tool name and description
                tool_name_lower = tool_name.lower()
                desc_lower = tool_info.get('description', '').lower()
                
                if any(keyword in tool_name_lower or keyword in desc_lower for keyword in ['monitor', 'cpu', 'gpu', 'ram', 'memory', 'disk', 'network']):
                    categories["Monitoring"][tool_name] = tool_info
                elif any(keyword in tool_name_lower or keyword in desc_lower for keyword in ['network', 'vpn', 'rdma', 'connect']):
                    categories["Network"][tool_name] = tool_info
                elif any(keyword in tool_name_lower or keyword in desc_lower for keyword in ['test', 'verify', 'audit', 'check']):
                    categories["Testing"][tool_name] = tool_info
                elif any(keyword in tool_name_lower or keyword in desc_lower for keyword in ['dev', 'code', 'script', 'python']):
                    categories["Development"][tool_name] = tool_info
                elif any(keyword in tool_name_lower or keyword in desc_lower for keyword in ['util', 'fix', 'setup', 'install', 'batch']):
                    categories["Utilities"][tool_name] = tool_info
                else:
                    categories["System Tools"][tool_name] = tool_info
            
            # Create tabs for non-empty categories
            for category_name, tools in categories.items():
                if tools:  # Only create tab if there are tools
                    self.create_category_tab(category_name, tools)
        else:
            # Fallback to original behavior
            for category_name, tools in self.tools.items():
                self.create_category_tab(category_name, tools)
    
    def create_category_tab(self, category_name, tools):
        """Create a tab for a tool category"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab_frame, text=category_name)
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create tool buttons in a grid
        self.create_tool_grid(scrollable_frame, tools)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def create_tool_grid(self, parent, tools):
        """Create a grid of tool buttons"""
        row = 0
        col = 0
        max_cols = 3
        
        for tool_name, tool_info in tools.items():
            # Create tool card
            tool_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
            tool_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Tool icon and name with CPU chip branding
            if tool_name == "CPU Monitor":
                # Show CPU chip icon for CPU Monitor
                cpu_chip_text = "⚡CPU⚡"
                icon_label = tk.Label(tool_frame, text=cpu_chip_text, 
                                    font=('Segoe UI', 20, 'bold'), 
                                    fg='#00d4ff', bg=self.colors['card'])
                icon_label.pack(pady=(15, 5))
            else:
                # Show tool icon
                icon_label = tk.Label(tool_frame, text=tool_info['icon'], 
                                    font=('Segoe UI', 24), 
                                    fg=self.colors['primary'], bg=self.colors['card'])
                icon_label.pack(pady=(15, 5))
            
            name_label = tk.Label(tool_frame, text=tool_name, 
                                 font=('Segoe UI', 12, 'bold'), 
                                 fg=self.colors['text'], bg=self.colors['card'])
            name_label.pack(pady=(0, 5))
            
            # Description
            desc_label = tk.Label(tool_frame, text=tool_info['description'], 
                                 font=('Segoe UI', 9), 
                                 fg=self.colors['text_secondary'], bg=self.colors['card'],
                                 wraplength=200, justify='center')
            desc_label.pack(pady=(0, 10))
            
            # Launch/Stop button
            launch_btn = tk.Button(tool_frame, text="🚀 Launch", 
                                 command=lambda t=tool_name, info=tool_info: self.toggle_tool(t, info),
                                 bg=self.colors['primary'], fg=self.colors['bg'],
                                 font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                                 padx=20, pady=8, cursor='hand2',
                                 activebackground=self.colors['success'], activeforeground=self.colors['bg'])
            launch_btn.pack(pady=(0, 15))
            
            # Status indicator
            status_label = tk.Label(tool_frame, text="● Ready", 
                                  font=('Segoe UI', 9), 
                                  fg=self.colors['success'], bg=self.colors['card'])
            status_label.pack(pady=(0, 10))
            
            # Store status label for updates
            tool_info['status_label'] = status_label
            tool_info['button'] = launch_btn
            
            # Grid configuration
            parent.grid_columnconfigure(col, weight=1)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=(0, 20))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=('Segoe UI', 10), 
                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.running_label = tk.Label(status_frame, text="Running: 0 tools", 
                                     font=('Segoe UI', 10), 
                                     fg=self.colors['info'], bg=self.colors['card'])
        self.running_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('homelab_launcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HomelabLauncher')
    
    def launch_tool(self, tool_name, tool_info):
        """Launch a homelab tool using advanced task scheduler"""
        try:
            # Schedule launch task with priority based on tool type
            priority = 'high' if tool_info.get('category') == 'monitoring' else 'medium'
            
            task_id = self.task_scheduler.schedule_task(
                self._launch_tool_task, 
                priority, 
                tool_name, 
                tool_info
            )
            
            # Execute immediately if resources available
            self.task_scheduler.execute_next()
            
        except Exception as e:
            self.logger.error(f"Failed to schedule launch for {tool_name}: {e}")
            messagebox.showerror("Launch Error", f"Failed to launch {tool_name}: {e}")
    
    def _launch_tool_task(self, tool_name, tool_info):
        """Actual tool launch task executed by scheduler"""
        try:
            # Check if tool is already running (thread-safe)
            with self.process_lock:
                if tool_name in self.running_tools:
                    process_info = self.running_tools[tool_name]
                    if process_info['process'].poll() is None:  # Still running
                        self.root.after(0, lambda: messagebox.showinfo("Tool Running", f"{tool_name} is already running!"))
                        return
                    else:
                        # Process ended, clean up
                        del self.running_tools[tool_name]
            
            # Publish start event
            self.event_bus.publish('tool_launching', {'tool_name': tool_name})
            
            # Update status
            self.root.after(0, lambda: tool_info['status_label'].config(text="● Starting", fg=self.colors['warning']))
            self.root.after(0, lambda: tool_info['button'].config(state='disabled', text="⏳ Starting..."))
            
            # Get tool path - handle both relative and absolute paths
            base_path = Path(os.getenv('HOMELAB_ROOT', os.path.dirname(os.path.abspath(__file__))))
            
            # Convert forward slashes to proper path separators
            tool_path_str = tool_info['path'].replace('/', os.sep)
            tool_path = base_path / tool_path_str
            
            # If not found, try to find the file by searching
            if not tool_path.exists():
                # Extract filename and search for it
                filename = Path(tool_info['path']).name
                
                # Search in the entire directory tree
                for root, dirs, files in os.walk(base_path):
                    if filename in files:
                        found_path = Path(root) / filename
                        if found_path.exists():
                            tool_path = found_path
                            break
            
            if not tool_path.exists():
                self.root.after(0, lambda: tool_info['status_label'].config(text="● Not Found", fg=self.colors['danger']))
                self.root.after(0, lambda: tool_info['button'].config(state='normal', text="🚀 Launch"))
                self.root.after(0, lambda: messagebox.showerror("Tool Not Found", f"Tool file not found: {tool_path}"))
                return
            
            # Launch tool with proper process management
            def launch_thread():
                try:
                    # Create process with proper environment
                    env = os.environ.copy()
                    env['PYTHONPATH'] = str(base_path)
                    
                    # Check if this is a GUI application
                    gui_tools = ['Hybrid Compute', 'CPU Monitor', 'GPU Monitor', 'Network Monitor', 'Storage Monitor', 'RAM Monitor', 
                                'RDMA Desktop App', 'RDMA Modern App', 'RDMA Memory Portal', 'Container Manager', 'Backup System',
                                'Web Dashboard', 'VPN Gateway', 'Media Server', 'CI/CD Pipeline', 'Power Management', 'IoT Platform']
                    is_gui = tool_name in gui_tools and tool_name != 'System Integration Test'
                    
                    if is_gui:
                        # GUI applications need different handling - launch as separate process
                        if os.name == 'nt':  # Windows
                            # Use start command to properly launch GUI apps
                            python_exe = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WindowsApps', 'pythonw3.exe')
                            process = subprocess.Popen(
                                ['start', 'cmd', '/c', python_exe, str(tool_path)],
                                cwd=str(base_path),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                env=env,
                                shell=True
                            )
                        else:
                            # Unix/Linux
                            process = subprocess.Popen(
                                ['py', str(tool_path)],
                                cwd=str(base_path),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                env=env
                            )
                    else:
                        # Console applications - capture output for progress window
                        if tool_name == 'System Integration Test':
                            # Special handling for system integration test
                            self.show_integration_test_progress(tool_name, tool_info, tool_path, base_path, env)
                            return
                        else:
                            # Other console applications
                            python_exe = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WindowsApps', 'pythonw3.exe')
                            process = subprocess.Popen(
                                [python_exe, str(tool_path)],
                                cwd=str(base_path),
                                stdout=None,  # Don't capture - let it go to console
                                stderr=None,  # Don't capture - let it go to console
                                text=True,
                                env=env,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                            )
                    
                    # Store process information (thread-safe)
                    with self.process_lock:
                        self.running_tools[tool_name] = {
                            'process': process,
                            'start_time': time.time(),
                            'tool_info': tool_info,
                            'thread': threading.current_thread()
                        }
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.update_tool_status(tool_name, tool_info, "● Running", self.colors['success']))
                    self.root.after(0, lambda: tool_info['button'].config(state='normal', text="⏹️ Stop"))
                    self.root.after(0, lambda: self.update_running_count())
                    
                    self.log_message(f"Launched {tool_name} (PID: {process.pid})")
                    
                    # Monitor process
                    self.monitor_process(tool_name)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.update_tool_status(tool_name, tool_info, "● Error", self.colors['danger']))
                    self.root.after(0, lambda: tool_info['button'].config(state='normal', text="🚀 Launch"))
                    self.log_message(f"Failed to launch {tool_name}: {e}")
            
            threading.Thread(target=launch_thread, daemon=True).start()
            
        except Exception as e:
            tool_info['status_label'].config(text="● Error", fg=self.colors['danger'])
            tool_info['button'].config(state='normal', text="🚀 Launch")
            messagebox.showerror("Launch Error", f"Failed to launch {tool_name}: {e}")
    
    def monitor_process(self, tool_name):
        """Monitor a running process with accurate tracking"""
        if tool_name not in self.running_tools:
            return
        
        process_info = self.running_tools[tool_name]
        process = process_info['process']
        tool_info = process_info['tool_info']
        
        def monitor_loop():
            while True:
                if tool_name not in self.running_tools:
                    break
                
                # Check process status
                poll_result = process.poll()
                
                if poll_result is not None:
                    # Process ended
                    exit_code = poll_result
                    runtime = time.time() - process_info['start_time']
                    
                    # Update status based on exit code
                    if exit_code == 0:
                        status = "● Completed"
                        color = self.colors['success']
                    else:
                        status = f"● Error (Code: {exit_code})"
                        color = self.colors['danger']
                    
                    self.root.after(0, lambda: self.update_tool_status(tool_name, tool_info, status, color))
                    self.root.after(0, lambda: tool_info['button'].config(state='normal', text="🚀 Launch"))
                    
                    self.log_message(f"{tool_name} ended (Code: {exit_code}, Runtime: {runtime:.1f}s)")
                    
                    # Clean up (thread-safe)
                    with self.process_lock:
                        if tool_name in self.running_tools:
                            del self.running_tools[tool_name]
                    
                    self.root.after(0, lambda: self.update_running_count())
                    break
                
                # Update runtime only if process is still running
                if tool_name in self.running_tools and process.poll() is None:
                    runtime = time.time() - process_info['start_time']
                    self.root.after(0, lambda: self.update_runtime(tool_name, tool_info, runtime))
                
                time.sleep(1)  # Check every second
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def show_integration_test_progress(self, tool_name, tool_info, tool_path, base_path, env):
        """Show progress window for system integration test"""
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("System Integration Test Progress")
        progress_window.geometry("600x400")
        progress_window.configure(bg='#1e1e1e')
        
        # Make window modal
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Title
        title_label = tk.Label(progress_window, text="🧪 System Integration Test", 
                              font=('Arial', 16, 'bold'), fg='#00ff00', bg='#1e1e1e')
        title_label.pack(pady=10)
        
        # Progress text widget
        text_widget = scrolledtext.ScrolledText(progress_window, wrap=tk.WORD, 
                                               bg='#2d2d2d', fg='#00ff00', 
                                               font=('Consolas', 10), height=20)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Close button (initially disabled)
        close_button = tk.Button(progress_window, text="Close", 
                                state='disabled', command=progress_window.destroy,
                                bg='#333333', fg='white', font=('Arial', 10))
        close_button.pack(pady=10)
        
        # Update status in main launcher
        tool_info['status_label'].config(text="● Running", fg=self.colors['success'])
        tool_info['button'].config(state='disabled', text="⏳ Testing...")
        
        # Start test in separate thread
        def run_test():
            try:
                process = subprocess.Popen(
                    ['py', str(tool_path)],
                    cwd=str(base_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                
                # Store process for monitoring (thread-safe)
                with self.process_lock:
                    self.running_tools[tool_name] = {
                        'process': process,
                        'start_time': time.time(),
                        'tool_info': tool_info,
                        'thread': threading.current_thread(),
                        'progress_window': progress_window
                    }
                
                # Read output line by line
                for line in iter(process.stdout.readline, ''):
                    if line:
                        # Update text widget in main thread
                        progress_window.after(0, lambda l=line: text_widget.insert(tk.END, l))
                        progress_window.after(0, lambda: text_widget.see(tk.END))
                        progress_window.after(0, lambda: progress_window.update())
                
                # Wait for process to complete
                process.wait()
                
                # Update UI
                progress_window.after(0, lambda: close_button.config(state='normal'))
                progress_window.after(0, lambda: text_widget.insert(tk.END, "\n\n✅ Test Completed!"))
                progress_window.after(0, lambda: text_widget.see(tk.END))
                
                # Update launcher status
                exit_code = process.returncode
                if exit_code == 0:
                    status = "● Completed"
                    color = self.colors['success']
                else:
                    status = f"● Error (Code: {exit_code})"
                    color = self.colors['danger']
                
                self.root.after(0, lambda: self.update_tool_status(tool_name, tool_info, status, color))
                self.root.after(0, lambda: tool_info['button'].config(state='normal', text="🚀 Launch"))
                
                # Clean up (thread-safe)
                with self.process_lock:
                    if tool_name in self.running_tools:
                        del self.running_tools[tool_name]
                
                self.root.after(0, lambda: self.update_running_count())
                
            except Exception as e:
                # Handle errors
                progress_window.after(0, lambda: text_widget.insert(tk.END, f"\n\n❌ Error: {e}"))
                progress_window.after(0, lambda: close_button.config(state='normal'))
                
                self.root.after(0, lambda: self.update_tool_status(tool_name, tool_info, "● Error", self.colors['danger']))
                self.root.after(0, lambda: tool_info['button'].config(state='normal', text="🚀 Launch"))
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def update_runtime(self, tool_name, tool_info, runtime):
        """Update runtime display for running tool"""
        try:
            # Double-check that tool is still running before updating
            if tool_name in self.running_tools:
                process_info = self.running_tools[tool_name]
                if process_info['process'].poll() is None:  # Still running
                    runtime_text = f"● Running ({runtime:.0f}s)"
                    tool_info['status_label'].config(text=runtime_text, fg=self.colors['success'])
        except:
            pass
    
    def toggle_tool(self, tool_name, tool_info):
        """Toggle between launching and stopping a tool"""
        # Check if tool is currently running
        if tool_name in self.running_tools:
            process_info = self.running_tools[tool_name]
            if process_info['process'].poll() is None:  # Still running
                self.stop_tool(tool_name, tool_info)
            else:
                # Process ended but not cleaned up
                del self.running_tools[tool_name]
                self.launch_tool(tool_name, tool_info)
        else:
            # Tool not running, launch it
            self.launch_tool(tool_name, tool_info)
    
    def stop_tool(self, tool_name, tool_info):
        """Stop a running tool"""
        try:
            if tool_name not in self.running_tools:
                return
            
            process_info = self.running_tools[tool_name]
            process = process_info['process']
            
            # Update status
            tool_info['status_label'].config(text="● Stopping", fg=self.colors['warning'])
            tool_info['button'].config(state='disabled', text="⏹️ Stopping...")
            
            # Stop process
            if os.name == 'nt':
                # Windows: use taskkill to force stop if needed
                try:
                    process.terminate()
                    # Give it time to terminate gracefully
                    time.sleep(2)
                    if process.poll() is None:
                        # Force kill
                        subprocess.run(['taskkill', '/F', '/PID', str(process.pid)], 
                                     capture_output=True)
                except:
                    pass
            else:
                # Unix/Linux
                process.terminate()
                if process.poll() is None:
                    process.kill()
            
            runtime = time.time() - process_info['start_time']
            self.log_message(f"Stopped {tool_name} (Runtime: {runtime:.1f}s)")
            
        except Exception as e:
            self.log_message(f"Failed to stop {tool_name}: {e}")
            # Reset UI anyway
            tool_info['status_label'].config(text="● Error", fg=self.colors['danger'])
            tool_info['button'].config(state='normal', text="🚀 Launch")
    
    def update_tool_status(self, tool_name, tool_info, status, color):
        """Update tool status display"""
        try:
            tool_info['status_label'].config(text=status, fg=color)
            self.status_label.config(text=f"{tool_name}: {status}")
        except:
            pass
    
    def update_running_count(self):
        """Update running tools count"""
        count = len(self.running_tools)
        self.running_label.config(text=f"Running: {count} tools")
    
    def log_message(self, message):
        """Log a message"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.logger.info(f"[{timestamp}] {message}")
        except:
            pass
    
    def initialize_subnet_discovery(self):
        """Initialize subnet discovery for launcher"""
        try:
            # Create communicator for launcher
            self.subnet_communicator = integrate_subnet_discovery(
                "HomelabLauncher",
                "infrastructure",
                ["tool_management", "system_monitoring", "service_discovery"]
            )
            
            # Setup message handlers
            @self.subnet_communicator.on_message("tool_request")
            def handle_tool_request(message_data, addr):
                self.handle_subnet_tool_request(message_data, addr)
            
            @self.subnet_communicator.on_message("status_broadcast")
            def handle_status_broadcast(message_data, addr):
                self.handle_subnet_status_broadcast(message_data, addr)
            
            @self.subnet_communicator.on_message("ping")
            def handle_ping(message_data, addr):
                self.handle_subnet_ping(message_data, addr)
            
            self.log_message("Subnet discovery initialized")
            
        except Exception as e:
            self.log_message(f"Failed to initialize subnet discovery: {e}")
    
    def handle_subnet_tool_request(self, message_data, addr):
        """Handle tool launch requests from other apps"""
        try:
            data = message_data.get('data', {})
            tool_name = data.get('tool_name')
            action = data.get('action', 'launch')
            
            if tool_name in self.tools:
                tool_info = self.tools.get(tool_name)
                if action == 'launch':
                    self.launch_tool(tool_name, tool_info)
                    self.log_message(f"Launched {tool_name} via subnet request from {addr[0]}")
                elif action == 'stop':
                    self.stop_tool(tool_name, tool_info)
                    self.log_message(f"Stopped {tool_name} via subnet request from {addr[0]}")
            
        except Exception as e:
            self.log_message(f"Error handling subnet tool request: {e}")
    
    def handle_subnet_status_broadcast(self, message_data, addr):
        """Handle status broadcasts from other apps"""
        try:
            data = message_data.get('data', {})
            app_name = data.get('app_name')
            status = data.get('status')
            
            self.log_message(f"Status broadcast from {app_name}: {status}")
            
        except Exception as e:
            self.log_message(f"Error handling status broadcast: {e}")
    
    def handle_subnet_ping(self, message_data, addr):
        """Handle ping messages"""
        try:
            data = message_data.get('data', {})
            message = data.get('message', 'ping')
            
            # Send pong response
            if self.subnet_communicator:
                response = {
                    'type': 'pong',
                    'message': 'pong from HomelabLauncher',
                    'running_tools': len(self.running_tools),
                    'timestamp': time.time()
                }
                self.subnet_communicator.send_message(message_data.get('from_service'), response)
            
            self.log_message(f"Ping from {addr[0]}: {message}")
            
        except Exception as e:
            self.log_message(f"Error handling ping: {e}")
    
    def broadcast_tool_status(self):
        """Broadcast current tool status to subnet"""
        if not self.subnet_communicator:
            return
        
        try:
            status_data = {
                'type': 'status_broadcast',
                'app_name': 'HomelabLauncher',
                'status': 'active',
                'running_tools': list(self.running_tools.keys()),
                'total_tools': len(self.tools),
                'timestamp': time.time()
            }
            
            self.subnet_communicator.send_to_type("all", status_data)
            
        except Exception as e:
            self.log_message(f"Failed to broadcast status: {e}")
    
    def stop_all_tools(self):
        """Stop all running tools"""
        for tool_name, process in list(self.running_tools.items()):
            try:
                process.terminate()
                self.log_message(f"Stopped {tool_name}")
            except:
                pass
        
        self.running_tools.clear()
        self.update_running_count()
        
        # Reset all tool statuses
        for category in self.tools.values():
            for tool_name, tool_info in category.items():
                tool_info['status_label'].config(text="● Ready", fg=self.colors['success'])
                tool_info['button'].config(state='normal')

def main():
    """Main entry point"""
    root = tk.Tk()
    app = HomelabLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    """Main execution block for homelab launcher"""
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher stopped by user")
    except Exception as e:
        print(f"Launcher error: {e}")
        try:
            messagebox.showerror("Error", f"Launcher failed to start: {e}")
        except:
            print(f"GUI error: {e}")

if __name__ == "__main__":
    main()
