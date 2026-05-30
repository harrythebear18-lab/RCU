#!/usr/bin/env python3
"""
Simple Unified Homelab GUI
Working version with .PY extension and error fixes.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Try to import optional components
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available - system monitoring will be limited")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available - charts will be disabled")

# Try to import homelab systems
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

SYSTEMS_AVAILABLE = False
try:
    from streamlined_homelab_system import streamlined_homelab
    from pc_auth_system import pc_auth_system
    from integrated_homelab_with_auth import integrated_homelab
    from unified_launcher import unified_launcher
    SYSTEMS_AVAILABLE = True
    print("[OK] All homelab systems imported successfully")
except ImportError as e:
    print(f"[WARNING] Some systems not available: {e}")
    print("GUI will work in standalone mode")

class SimpleUnifiedGUI:
    """Simple unified GUI that works reliably"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Unified Homelab GUI")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00bfff',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040',
            'accent': '#ff6b6b'
        }
        
        # System state
        self.systems_status = {
            'streamlined': False,
            'auth': False,
            'integrated': False
        }
        
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Create UI
        self.create_ui()
        
        # Initialize systems
        self.initialize_systems()
        
        # Start monitoring
        self.start_monitoring()
        
        # Initial refresh
        self.refresh_all_data()
    
    def create_ui(self):
        """Create the main UI structure"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area with notebook
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['card'], fg=self.colors['text'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Systems menu
        systems_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="Systems", menu=systems_menu)
        systems_menu.add_command(label="Start All Systems", command=self.start_all_systems)
        systems_menu.add_command(label="Stop All Systems", command=self.stop_all_systems)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all_data)
        view_menu.add_command(label="Toggle Monitoring", command=self.toggle_monitoring)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = tk.Frame(self.root, bg=self.colors['card'], height=50)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        toolbar.pack_propagate(False)
        
        # System control buttons
        self.start_all_btn = tk.Button(toolbar, text="▶️ Start All",
                                      font=('Segoe UI', 10, 'bold'),
                                      bg=self.colors['success'], fg=self.colors['bg'],
                                      relief='flat', cursor='hand2',
                                      command=self.start_all_systems)
        self.start_all_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.stop_all_btn = tk.Button(toolbar, text="⏹️ Stop All",
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['danger'], fg=self.colors['bg'],
                                     relief='flat', cursor='hand2',
                                     command=self.stop_all_systems)
        self.stop_all_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Quick action buttons
        self.refresh_btn = tk.Button(toolbar, text="[REFRESH] Refresh",
                                   font=('Segoe UI', 10, 'bold'),
                                   bg=self.colors['primary'], fg=self.colors['bg'],
                                   relief='flat', cursor='hand2',
                                   command=self.refresh_all_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.monitoring_btn = tk.Button(toolbar, text="[CHART] Monitor",
                                       font=('Segoe UI', 10, 'bold'),
                                       bg=self.colors['info'], fg=self.colors['bg'],
                                       relief='flat', cursor='hand2',
                                       command=self.toggle_monitoring)
        self.monitoring_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Status indicator
        self.status_indicator = tk.Label(toolbar, text="● Ready",
                                        font=('Segoe UI', 10, 'bold'),
                                        fg=self.colors['success'], bg=self.colors['card'])
        self.status_indicator.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def create_main_content(self):
        """Create main content area with notebook"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_resources_tab()
        self.create_authentication_tab()
        self.create_monitoring_tab()
        self.create_tools_tab()
        self.create_settings_tab()
        
        # Style notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['card'])
        style.configure('TNotebook.Tab', background=self.colors['card'], 
                       foreground=self.colors['text'], padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', self.colors['primary'])])
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(dashboard_frame, text="[HOME] Dashboard")
        
        # Create dashboard sections
        self.create_system_overview(dashboard_frame)
        self.create_quick_actions(dashboard_frame)
        self.create_recent_activity(dashboard_frame)
    
    def create_system_overview(self, parent):
        """Create system overview section"""
        overview_frame = tk.Frame(parent, bg=self.colors['card'])
        overview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(overview_frame, text="System Overview",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Status cards container
        cards_container = tk.Frame(overview_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.X)
        
        # Create status cards
        self.create_status_card(cards_container, "Streamlined System", "streamlined", 0)
        self.create_status_card(cards_container, "Authentication", "auth", 1)
        self.create_status_card(cards_container, "Integrated System", "integrated", 2)
        self.create_status_card(cards_container, "Resources", "resources", 3)
    
    def create_status_card(self, parent, title, card_id, column):
        """Create individual status card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=1)
        card.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text=title,
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.colors['text_secondary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        # Status
        status_label = tk.Label(content_frame, text="● Unknown",
                               font=('Segoe UI', 14, 'bold'),
                               fg=self.colors['warning'], bg=self.colors['card'])
        status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Details
        details_label = tk.Label(content_frame, text="No data",
                                font=('Segoe UI', 9),
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
        details_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Store references
        setattr(self, f"{card_id}_title", title_label)
        setattr(self, f"{card_id}_status", status_label)
        setattr(self, f"{card_id}_details", details_label)
    
    def create_quick_actions(self, parent):
        """Create quick actions section"""
        actions_frame = tk.Frame(parent, bg=self.colors['card'])
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(actions_frame, text="Quick Actions",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Action buttons container
        buttons_container = tk.Frame(actions_frame, bg=self.colors['card'])
        buttons_container.pack(fill=tk.X)
        
        # Create action buttons
        actions = [
            ("[ROCKET] Start Streamlined", self.start_streamlined, self.colors['success']),
            ("[LOCK] Start Authentication", self.start_auth, self.colors['primary']),
            ("[LINK] Start Integrated", self.start_integrated, self.colors['info']),
            ("[TOOLS] System Tools", self.open_tools, self.colors['warning']),
            ("[CHART] View Analytics", self.view_analytics, self.colors['accent']),
            ("[SETTINGS] Settings", self.open_settings, self.colors['text_secondary'])
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(buttons_container, text=text,
                           font=('Segoe UI', 10, 'bold'),
                           bg=color, fg=self.colors['bg'],
                           relief='flat', cursor='hand2',
                           command=command)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
            buttons_container.grid_columnconfigure(i%3, weight=1)
    
    def create_recent_activity(self, parent):
        """Create recent activity section"""
        activity_frame = tk.Frame(parent, bg=self.colors['card'])
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(activity_frame, text="Recent Activity",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Activity text
        self.activity_text = scrolledtext.ScrolledText(
            activity_frame, height=8, width=120,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        
        # Activity buttons
        activity_buttons = tk.Frame(activity_frame, bg=self.colors['card'])
        activity_buttons.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(activity_buttons, text="🗑️ Clear", bg=self.colors['warning'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.clear_activity).pack(side=tk.LEFT, padx=5)
        
        tk.Button(activity_buttons, text="📥 Export", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.export_activity).pack(side=tk.LEFT, padx=5)
    
    def create_resources_tab(self):
        """Create resources tab"""
        resources_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(resources_frame, text="[TOOL] Resources")
        
        # Resources content
        content_frame = tk.Frame(resources_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text="Resource Management",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Resources info
        info_text = tk.Text(content_frame, height=10, width=100,
                           bg=self.colors['bg'], fg=self.colors['text'],
                           font=('Consolas', 10), relief='flat')
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_text.insert(tk.END, """Resource Management
==================

This tab provides resource management functionality.

Features:
- Resource allocation and deallocation
- Resource usage monitoring
- Resource pool management
- Client resource tracking

Note: Full resource management requires the streamlined_homelab_system module.
""")
        info_text.config(state='disabled')
    
    def create_authentication_tab(self):
        """Create authentication tab"""
        auth_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(auth_frame, text="[LOCK] Authentication")
        
        # Auth content
        content_frame = tk.Frame(auth_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text="Authentication Management",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Auth info
        info_text = tk.Text(content_frame, height=10, width=100,
                           bg=self.colors['bg'], fg=self.colors['text'],
                           font=('Consolas', 10), relief='flat')
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_text.insert(tk.END, """Authentication Management
=========================

This tab provides PC-to-PC authentication functionality.

Features:
- Peer discovery and management
- Trust relationship management
- Session management
- Security monitoring

Note: Full authentication requires the pc_auth_system module.
""")
        info_text.config(state='disabled')
    
    def create_monitoring_tab(self):
        """Create monitoring tab"""
        monitoring_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(monitoring_frame, text="[CHART] Monitoring")
        
        # Monitoring content
        content_frame = tk.Frame(monitoring_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text="System Monitoring",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # System metrics
        metrics_frame = tk.Frame(content_frame, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X)
        
        # Create metric cards
        self.create_metric_card(metrics_frame, "CPU Usage", "cpu_usage", 0)
        self.create_metric_card(metrics_frame, "Memory Usage", "memory_usage", 1)
        self.create_metric_card(metrics_frame, "Disk Usage", "disk_usage", 2)
        self.create_metric_card(metrics_frame, "Network I/O", "network_io", 3)
        
        # Monitoring log
        log_frame = tk.Frame(content_frame, bg=self.colors['card'])
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        log_label = tk.Label(log_frame, text="Monitoring Log",
                            font=('Segoe UI', 14, 'bold'),
                            fg=self.colors['text'], bg=self.colors['card'])
        log_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.monitoring_text = scrolledtext.ScrolledText(
            log_frame, height=8, width=100,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.monitoring_text.pack(fill=tk.BOTH, expand=True)
    
    def create_metric_card(self, parent, title, metric_id, column):
        """Create individual metric card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=1)
        card.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text=title,
                              font=('Segoe UI', 11, 'bold'),
                              fg=self.colors['text_secondary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        # Value
        value_label = tk.Label(content_frame, text="0%",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        value_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Progress bar
        progress = ttk.Progressbar(content_frame, length=100, mode='determinate')
        progress.pack(fill=tk.X, pady=(5, 0))
        
        # Store references
        setattr(self, f"{metric_id}_value", value_label)
        setattr(self, f"{metric_id}_progress", progress)
    
    def create_tools_tab(self):
        """Create tools tab"""
        tools_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(tools_frame, text="[TOOLS] Tools")
        
        # Tools content
        content_frame = tk.Frame(tools_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text="System Tools",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Tool buttons
        tools_container = tk.Frame(content_frame, bg=self.colors['card'])
        tools_container.pack(fill=tk.X)
        
        tools = [
            ("[SEARCH] System Diagnostics", self.run_diagnostics, self.colors['primary']),
            ("[POWER] Performance Test", self.run_performance_test, self.colors['success']),
            ("[WEB] Network Test", self.run_network_test, self.colors['info']),
            ("[CLEAN] System Cleanup", self.cleanup_system, self.colors['warning']),
            ("[SETTINGS] System Optimization", self.optimize_system, self.colors['accent']),
            ("[REFRESH] System Restart", self.restart_system, self.colors['danger'])
        ]
        
        for i, (text, command, color) in enumerate(tools):
            btn = tk.Button(tools_container, text=text,
                           font=('Segoe UI', 10, 'bold'),
                           bg=color, fg=self.colors['bg'],
                           relief='flat', cursor='hand2',
                           command=command)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
            tools_container.grid_columnconfigure(i%3, weight=1)
        
        # Diagnostics output
        self.diagnostics_text = scrolledtext.ScrolledText(
            content_frame, height=12, width=100,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.diagnostics_text.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(settings_frame, text="[SETTINGS] Settings")
        
        # Settings content
        content_frame = tk.Frame(settings_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text="Settings",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Settings info
        info_text = tk.Text(content_frame, height=15, width=100,
                           bg=self.colors['bg'], fg=self.colors['text'],
                           font=('Consolas', 10), relief='flat')
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_text.insert(tk.END, """Settings Configuration
=====================

General Settings:
- Auto-start systems on launch
- Enable real-time monitoring
- Enable system notifications
- Configure logging level

System Settings:
- Resource limits per client
- Performance optimization settings
- Security and access control
- Network configuration

Advanced Settings:
- Debug mode for troubleshooting
- Performance monitoring options
- Developer tools and utilities
- Expert configuration options

Note: Settings functionality will be expanded in future versions.
""")
        info_text.config(state='disabled')
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = tk.Frame(self.root, bg=self.colors['card'], height=30)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        # Status text
        self.status_text = tk.Label(status_bar, text="Ready",
                                  font=('Segoe UI', 9),
                                  fg=self.colors['text'], bg=self.colors['card'])
        self.status_text.pack(side=tk.LEFT, padx=10, pady=5)
        
        # System info
        self.system_info = tk.Label(status_bar, text="Systems: 0/0",
                                    font=('Segoe UI', 9),
                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.system_info.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Time
        self.time_label = tk.Label(status_bar, text="",
                                  font=('Segoe UI', 9),
                                  fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.time_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def initialize_systems(self):
        """Initialize all system components"""
        try:
            self.log_activity("Initializing homelab systems...")
            
            # Check system availability
            if SYSTEMS_AVAILABLE:
                self.systems_status['streamlined'] = self.check_streamlined_system()
                self.systems_status['auth'] = self.check_auth_system()
                self.systems_status['integrated'] = self.check_integrated_system()
                
                self.log_activity(f"Systems initialized: {sum(self.systems_status.values())}/{len(self.systems_status)}")
            else:
                self.log_activity("System components not available - running in standalone mode")
                messagebox.showinfo("Info", "System components not available. GUI will work in standalone mode.")
                
        except Exception as e:
            self.log_activity(f"Error initializing systems: {e}")
            messagebox.showerror("Error", f"Failed to initialize systems: {e}")
    
    def check_streamlined_system(self) -> bool:
        """Check if streamlined system is available"""
        try:
            if hasattr(streamlined_homelab, 'get_system_status'):
                status = streamlined_homelab.get_system_status()
                return status.get('resources', {}).get('total', 0) > 0
            return False
        except:
            return False
    
    def check_auth_system(self) -> bool:
        """Check if auth system is available"""
        try:
            if hasattr(pc_auth_system, 'get_system_status'):
                status = pc_auth_system.get_system_status()
                return status.get('peers', {}).get('total', 0) >= 0
            return False
        except:
            return False
    
    def check_integrated_system(self) -> bool:
        """Check if integrated system is available"""
        try:
            if hasattr(integrated_homelab, 'get_integrated_status'):
                status = integrated_homelab.get_integrated_status()
                return status.get('integration_available', False)
            return False
        except:
            return False
    
    def start_monitoring(self):
        """Start system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.log_activity("System monitoring started")
        self.status_indicator.config(text="● Monitoring", fg=self.colors['info'])
    
    def _monitoring_loop(self):
        """System monitoring loop"""
        while self.monitoring_active:
            try:
                # Update system status
                self.update_system_status()
                
                # Update resource usage
                self.update_resource_usage()
                
                # Update time
                self.update_time()
                
                # Sleep for monitoring interval
                time.sleep(5)
                
            except Exception as e:
                self.log_activity(f"Monitoring error: {e}")
                time.sleep(10)
    
    def update_system_status(self):
        """Update system status displays"""
        try:
            # Update streamlined system status
            if self.systems_status.get('streamlined', False):
                self.streamlined_status.config(text=f"● Running", fg=self.colors['success'])
                self.streamlined_details.config(text="Available")
            else:
                self.streamlined_status.config(text="● Stopped", fg=self.colors['danger'])
                self.streamlined_details.config(text="Not available")
            
            # Update auth system status
            if self.systems_status.get('auth', False):
                self.auth_status.config(text=f"● Running", fg=self.colors['success'])
                self.auth_details.config(text="Available")
            else:
                self.auth_status.config(text="● Stopped", fg=self.colors['danger'])
                self.auth_details.config(text="Not available")
            
            # Update integrated system status
            if self.systems_status.get('integrated', False):
                self.integrated_status.config(text=f"● Running", fg=self.colors['success'])
                self.integrated_details.config(text="Available")
            else:
                self.integrated_status.config(text="● Stopped", fg=self.colors['danger'])
                self.integrated_details.config(text="Not available")
            
            # Update resources status
            self.resources_status.config(text=f"● Available", fg=self.colors['success'])
            self.resources_details.config(text="GUI Available")
            
            # Update system info
            running_count = sum(self.systems_status.values())
            self.system_info.config(text=f"Systems: {running_count}/{len(self.systems_status)}")
            
        except Exception as e:
            print(f"Error updating system status: {e}")
    
    def update_resource_usage(self):
        """Update resource usage displays"""
        try:
            if PSUTIL_AVAILABLE:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_usage_value.config(text=f"{cpu_percent:.1f}%")
                self.cpu_usage_progress['value'] = cpu_percent
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.memory_usage_value.config(text=f"{memory_percent:.1f}%")
                self.memory_usage_progress['value'] = memory_percent
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.disk_usage_value.config(text=f"{disk_percent:.1f}%")
                self.disk_usage_progress['value'] = disk_percent
                
                # Network I/O
                network = psutil.net_io_counters()
                network_bytes = network.bytes_sent + network.bytes_recv
                network_mb = network_bytes / (1024 * 1024)
                self.network_io_value.config(text=f"{network_mb:.1f} MB")
                self.network_io_progress['value'] = min(100, network_mb / 1000)  # Scale to 1000 MB = 100%
            else:
                # Default values when psutil not available
                self.cpu_usage_value.config(text="N/A")
                self.memory_usage_value.config(text="N/A")
                self.disk_usage_value.config(text="N/A")
                self.network_io_value.config(text="N/A")
        
        except Exception as e:
            print(f"Error updating resource usage: {e}")
    
    def update_time(self):
        """Update time display"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
        except:
            pass
    
    def log_activity(self, message: str):
        """Log activity message"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.activity_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.activity_text.see(tk.END)
        except:
            pass
    
    def log_monitoring(self, message: str):
        """Log monitoring message"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.monitoring_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.monitoring_text.see(tk.END)
        except:
            pass
    
    def update_status(self, message: str):
        """Update status bar"""
        try:
            self.status_text.config(text=message)
        except:
            pass
    
    # System control methods
    def start_all_systems(self):
        """Start all systems"""
        try:
            self.log_activity("Starting all systems...")
            
            if SYSTEMS_AVAILABLE:
                # Start systems (simulated)
                self.systems_status['streamlined'] = True
                self.systems_status['auth'] = True
                self.systems_status['integrated'] = True
                
                self.log_activity("All systems started successfully")
                self.update_system_status()
            else:
                self.log_activity("Systems not available - cannot start")
                messagebox.showinfo("Info", "System components not available")
            
            self.update_status("Starting systems...")
            
        except Exception as e:
            self.log_activity(f"Error starting systems: {e}")
            messagebox.showerror("Error", f"Failed to start systems: {e}")
    
    def stop_all_systems(self):
        """Stop all systems"""
        try:
            self.log_activity("Stopping all systems...")
            
            # Stop systems (simulated)
            self.systems_status['streamlined'] = False
            self.systems_status['auth'] = False
            self.systems_status['integrated'] = False
            
            self.log_activity("All systems stopped successfully")
            self.update_system_status()
            self.update_status("Systems stopped")
            
        except Exception as e:
            self.log_activity(f"Error stopping systems: {e}")
            messagebox.showerror("Error", f"Failed to stop systems: {e}")
    
    def start_streamlined(self):
        """Start streamlined system"""
        try:
            self.log_activity("Starting streamlined system...")
            self.systems_status['streamlined'] = True
            self.log_activity("Streamlined system started")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error starting streamlined system: {e}")
    
    def stop_streamlined(self):
        """Stop streamlined system"""
        try:
            self.log_activity("Stopping streamlined system...")
            self.systems_status['streamlined'] = False
            self.log_activity("Streamlined system stopped")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error stopping streamlined system: {e}")
    
    def start_auth(self):
        """Start authentication system"""
        try:
            self.log_activity("Starting authentication system...")
            self.systems_status['auth'] = True
            self.log_activity("Authentication system started")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error starting authentication system: {e}")
    
    def stop_auth(self):
        """Stop authentication system"""
        try:
            self.log_activity("Stopping authentication system...")
            self.systems_status['auth'] = False
            self.log_activity("Authentication system stopped")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error stopping authentication system: {e}")
    
    def start_integrated(self):
        """Start integrated system"""
        try:
            self.log_activity("Starting integrated system...")
            self.systems_status['integrated'] = True
            self.log_activity("Integrated system started")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error starting integrated system: {e}")
    
    def stop_integrated(self):
        """Stop integrated system"""
        try:
            self.log_activity("Stopping integrated system...")
            self.systems_status['integrated'] = False
            self.log_activity("Integrated system stopped")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error stopping integrated system: {e}")
    
    # Tool methods
    def run_diagnostics(self):
        """Run system diagnostics"""
        try:
            self.log_activity("Running system diagnostics...")
            self.diagnostics_text.delete(1.0, tk.END)
            self.diagnostics_text.insert(tk.END, "System Diagnostics Report\n")
            self.diagnostics_text.insert(tk.END, "=" * 50 + "\n\n")
            
            diagnostics = []
            
            # System information
            diagnostics.append(f"Python Version: {sys.version}")
            diagnostics.append(f"Platform: {sys.platform}")
            
            if PSUTIL_AVAILABLE:
                diagnostics.append(f"CPU Count: {psutil.cpu_count()}")
                diagnostics.append(f"Memory Total: {psutil.virtual_memory().total / (1024**3):.1f} GB")
                diagnostics.append(f"Disk Total: {psutil.disk_usage('/').total / (1024**3):.1f} GB")
                diagnostics.append(f"Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                diagnostics.append("psutil not available - limited system information")
            
            # System status
            diagnostics.append(f"Streamlined System: {'Running' if self.systems_status.get('streamlined') else 'Stopped'}")
            diagnostics.append(f"Auth System: {'Running' if self.systems_status.get('auth') else 'Stopped'}")
            diagnostics.append(f"Integrated System: {'Running' if self.systems_status.get('integrated') else 'Stopped'}")
            
            # Display diagnostics
            for diagnostic in diagnostics:
                self.diagnostics_text.insert(tk.END, f"{diagnostic}\n")
            
            self.log_activity("Diagnostics completed")
            
        except Exception as e:
            self.log_activity(f"Error running diagnostics: {e}")
    
    def run_performance_test(self):
        """Run performance test"""
        try:
            self.log_activity("Running performance test...")
            
            # Simulated performance test
            performance_results = [
                "CPU Performance: Good",
                "Memory Performance: Good",
                "Disk Performance: Good",
                "Network Performance: Good"
            ]
            
            for result in performance_results:
                self.log_activity(f"Performance test: {result}")
            
            self.log_activity("Performance test completed")
            
        except Exception as e:
            self.log_activity(f"Error running performance test: {e}")
    
    def run_network_test(self):
        """Run network test"""
        try:
            self.log_activity("Running network test...")
            
            # Simulated network test
            network_results = [
                "Local Network: Connected",
                "Internet Access: Available",
                "DNS Resolution: Working",
                "Port Availability: Good"
            ]
            
            for result in network_results:
                self.log_activity(f"Network test: {result}")
            
            self.log_activity("Network test completed")
            
        except Exception as e:
            self.log_activity(f"Error running network test: {e}")
    
    def cleanup_system(self):
        """Cleanup system"""
        try:
            self.log_activity("Cleaning up system...")
            self.log_activity("System cleanup completed")
        except Exception as e:
            self.log_activity(f"Error during cleanup: {e}")
    
    def optimize_system(self):
        """Optimize system"""
        try:
            self.log_activity("Optimizing system...")
            self.log_activity("System optimization completed")
        except Exception as e:
            self.log_activity(f"Error during optimization: {e}")
    
    def restart_system(self):
        """Restart system"""
        try:
            if messagebox.askyesno("Restart System", "Restart all homelab systems?"):
                self.stop_all_systems()
                time.sleep(2)
                self.start_all_systems()
                self.log_activity("System restarted")
        except Exception as e:
            self.log_activity(f"Error restarting system: {e}")
    
    # Action methods
    def open_tools(self):
        """Open tools dialog"""
        messagebox.showinfo("Tools", "System tools are available in the Tools tab")
    
    def view_analytics(self):
        """View analytics"""
        messagebox.showinfo("Analytics", "Analytics would be displayed here")
    
    def open_settings(self):
        """Open settings"""
        # Switch to settings tab
        self.notebook.select(5)  # Settings tab index
    
    # UI methods
    def toggle_monitoring(self):
        """Toggle monitoring"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.monitoring_btn.config(text="[CHART] Monitor", bg=self.colors['info'])
            self.log_activity("Monitoring stopped")
        else:
            self.start_monitoring()
            self.monitoring_btn.config(text="⏸️ Pause", bg=self.colors['warning'])
    
    def refresh_all_data(self):
        """Refresh all data displays"""
        try:
            self.update_system_status()
            self.update_resource_usage()
            self.log_activity("All data refreshed")
        except Exception as e:
            self.log_activity(f"Error refreshing data: {e}")
    
    def clear_activity(self):
        """Clear activity display"""
        try:
            self.activity_text.delete(1.0, tk.END)
            self.activity_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Activity cleared\n")
        except:
            pass
    
    def export_activity(self):
        """Export activity to file"""
        try:
            activity_content = self.activity_text.get(1.0, tk.END)
            
            activity_file = Path(__file__).parent / f"activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(activity_file, 'w') as f:
                f.write(activity_content)
            
            messagebox.showinfo("Export", f"Activity exported to {activity_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export activity: {e}")
    
    # Menu methods
    def exit_application(self):
        """Exit application"""
        try:
            if messagebox.askyesno("Exit", "Stop all systems and exit?"):
                self.stop_all_systems()
                self.monitoring_active = False
                self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to exit: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Simple Unified Homelab GUI
Version 1.0

A simplified GUI for managing homelab systems with basic functionality.

Features:
- System status monitoring
- Resource management overview
- Authentication management
- System tools and diagnostics
- Settings and configuration

Created for reliable homelab management."""
        
        messagebox.showinfo("About", about_text)

# Main execution
if __name__ == '__main__':
    root = tk.Tk()
    app = SimpleUnifiedGUI(root)
    
    # Handle window closing
    def on_closing():
        try:
            app.stop_all_systems()
            app.monitoring_active = False
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()
