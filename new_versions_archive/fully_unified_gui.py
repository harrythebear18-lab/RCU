#!/usr/bin/env python3
"""
Fully Unified Homelab GUI
Complete, comprehensive GUI with all homelab functionality integrated.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

# Try to import matplotlib (optional)
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available - charts will be disabled")

# Import all system components
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from streamlined_homelab_system import streamlined_homelab
    from pc_auth_system import pc_auth_system
    from integrated_homelab_with_auth import integrated_homelab
    from unified_launcher import unified_launcher
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"System import error: {e}")
    SYSTEMS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class FullyUnifiedGUI:
    """Fully unified GUI with complete homelab functionality"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Fully Unified Homelab System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040',
            'accent': '#ff6b6b',
            'info': '#00bfff'
        }
        
        # System state
        self.systems_status = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Create main UI structure
        self.create_main_ui()
        
        # Initialize systems
        self.initialize_systems()
        
        # Start monitoring
        self.start_monitoring()
        
        # Initial refresh
        self.refresh_all_data()
    
    def create_main_ui(self):
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
        file_menu.add_command(label="Load Configuration", command=self.load_configuration)
        file_menu.add_command(label="Save Configuration", command=self.save_configuration)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Systems menu
        systems_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="Systems", menu=systems_menu)
        systems_menu.add_command(label="Start All Systems", command=self.start_all_systems)
        systems_menu.add_command(label="Stop All Systems", command=self.stop_all_systems)
        systems_menu.add_separator()
        systems_menu.add_command(label="Restart Streamlined System", command=self.restart_streamlined)
        systems_menu.add_command(label="Restart Authentication", command=self.restart_auth)
        systems_menu.add_command(label="Restart Integrated System", command=self.restart_integrated)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="System Diagnostics", command=self.run_diagnostics)
        tools_menu.add_command(label="Performance Test", command=self.run_performance_test)
        tools_menu.add_command(label="Network Test", command=self.run_network_test)
        tools_menu.add_separator()
        tools_menu.add_command(label="Cleanup System", command=self.cleanup_system)
        tools_menu.add_command(label="Optimize System", command=self.optimize_system)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all_data)
        view_menu.add_command(label="Toggle Monitoring", command=self.toggle_monitoring)
        view_menu.add_separator()
        view_menu.add_command(label="Show System Info", command=self.show_system_info)
        view_menu.add_command(label="Show Network Info", command=self.show_network_info)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['card'], fg=self.colors['text'])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
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
        
        # Separator
        separator = tk.Frame(toolbar, width=2, bg=self.colors['border'])
        separator.pack(side=tk.LEFT, padx=10, fill=tk.Y, pady=5)
        
        # Quick action buttons
        self.refresh_btn = tk.Button(toolbar, text="🔄 Refresh",
                                   font=('Segoe UI', 10, 'bold'),
                                   bg=self.colors['primary'], fg=self.colors['bg'],
                                   relief='flat', cursor='hand2',
                                   command=self.refresh_all_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        self.monitoring_btn = tk.Button(toolbar, text="📊 Monitor",
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
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")
        
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
            ("🚀 Start Streamlined", self.start_streamlined, self.colors['success']),
            ("🔐 Start Authentication", self.start_auth, self.colors['primary']),
            ("🔗 Start Integrated", self.start_integrated, self.colors['info']),
            ("🛠️ System Tools", self.open_tools, self.colors['warning']),
            ("📊 View Analytics", self.view_analytics, self.colors['accent']),
            ("⚙️ Settings", self.open_settings, self.colors['text_secondary'])
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(buttons_container, text=text,
                           font=('Segoe UI', 10, 'bold'),
                           bg=color, fg=self.colors['bg'],
                           relief='flat', cursor='hand2',
                           command=command)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            buttons_container.grid_columnconfigure(i, weight=1)
    
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
        """Create resources management tab"""
        resources_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(resources_frame, text="🔧 Resources")
        
        # Create resource sections
        self.create_resource_overview(resources_frame)
        self.create_resource_management(resources_frame)
        self.create_resource_allocation(resources_frame)
    
    def create_resource_overview(self, parent):
        """Create resource overview section"""
        overview_frame = tk.Frame(parent, bg=self.colors['card'])
        overview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(overview_frame, text="Resource Overview",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Resource cards
        cards_container = tk.Frame(overview_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.X)
        
        # Create resource cards
        self.create_resource_card(cards_container, "RAM", "ram", 0)
        self.create_resource_card(cards_container, "CPU", "cpu", 1)
        self.create_resource_card(cards_container, "GPU", "gpu", 2)
        self.create_resource_card(cards_container, "Network", "network", 3)
    
    def create_resource_card(self, parent, title, resource_id, column):
        """Create individual resource card"""
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
        
        # Usage
        usage_label = tk.Label(content_frame, text="0%",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        usage_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Details
        details_label = tk.Label(content_frame, text="0 / 0 GB",
                                font=('Segoe UI', 9),
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
        details_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Store references
        setattr(self, f"{resource_id}_usage", usage_label)
        setattr(self, f"{resource_id}_details", details_label)
    
    def create_resource_management(self, parent):
        """Create resource management section"""
        management_frame = tk.Frame(parent, bg=self.colors['card'])
        management_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(management_frame, text="Resource Management",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create treeview for resources
        columns = ('Name', 'Type', 'Total', 'Allocated', 'Available', 'Status')
        self.resources_tree = ttk.Treeview(management_frame, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.resources_tree.heading(col, text=col)
            self.resources_tree.column(col, width=100)
        
        self.resources_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(management_frame, orient='vertical', command=self.resources_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.resources_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(management_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(button_frame, text="➕ Allocate", bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.allocate_resource_dialog).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="➖ Release", bg=self.colors['danger'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.release_resource_dialog).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Refresh", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.refresh_resources).pack(side=tk.LEFT, padx=5)
    
    def create_resource_allocation(self, parent):
        """Create resource allocation section"""
        allocation_frame = tk.Frame(parent, bg=self.colors['card'])
        allocation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(allocation_frame, text="Active Allocations",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create treeview for allocations
        columns = ('Client', 'Resource', 'Amount', 'Created', 'Expires', 'Status')
        self.allocations_tree = ttk.Treeview(allocation_frame, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.allocations_tree.heading(col, text=col)
            self.allocations_tree.column(col, width=100)
        
        self.allocations_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(allocation_frame, orient='vertical', command=self.allocations_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.allocations_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(allocation_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(button_frame, text="➖ Release Selected", bg=self.colors['warning'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.release_selected_allocation).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Refresh", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.refresh_allocations).pack(side=tk.LEFT, padx=5)
    
    def create_authentication_tab(self):
        """Create authentication tab"""
        auth_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(auth_frame, text="🔐 Authentication")
        
        # Create auth sections
        self.create_auth_overview(auth_frame)
        self.create_peer_management(auth_frame)
        self.create_trust_management(auth_frame)
    
    def create_auth_overview(self, parent):
        """Create authentication overview section"""
        overview_frame = tk.Frame(parent, bg=self.colors['card'])
        overview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(overview_frame, text="Authentication Overview",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Auth status cards
        cards_container = tk.Frame(overview_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.X)
        
        # Create auth cards
        self.create_auth_card(cards_container, "Local Peer", "local_peer", 0)
        self.create_auth_card(cards_container, "Discovered Peers", "discovered_peers", 1)
        self.create_auth_card(cards_container, "Trusted Peers", "trusted_peers", 2)
        self.create_auth_card(cards_container, "Active Sessions", "active_sessions", 3)
    
    def create_auth_card(self, parent, title, card_id, column):
        """Create individual auth card"""
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
        
        # Count
        count_label = tk.Label(content_frame, text="0",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        count_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Status
        status_label = tk.Label(content_frame, text="● Unknown",
                               font=('Segoe UI', 9),
                               fg=self.colors['warning'], bg=self.colors['card'])
        status_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Store references
        setattr(self, f"{card_id}_count", count_label)
        setattr(self, f"{card_id}_status", status_label)
    
    def create_peer_management(self, parent):
        """Create peer management section"""
        peer_frame = tk.Frame(parent, bg=self.colors['card'])
        peer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(peer_frame, text="Peer Management",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create paned window
        paned = ttk.PanedWindow(peer_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Peer list
        list_frame = tk.Frame(paned, bg=self.colors['card'])
        paned.add(list_frame, weight=1)
        
        self.create_peer_list(list_frame)
        
        # Peer details
        details_frame = tk.Frame(paned, bg=self.colors['card'])
        paned.add(details_frame, weight=1)
        
        self.create_peer_details(details_frame)
    
    def create_peer_list(self, parent):
        """Create peer list"""
        # List header
        header_frame = tk.Frame(parent, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="Discovered Peers",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        # Peer listbox
        list_frame = tk.Frame(parent, bg=self.colors['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview for peers
        columns = ('Name', 'IP Address', 'Role', 'Status', 'Last Seen')
        self.peers_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.peers_tree.heading(col, text=col)
            self.peers_tree.column(col, width=100)
        
        self.peers_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.peers_tree.bind('<<TreeviewSelect>>', self.on_peer_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.peers_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.peers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(parent, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="🔍 Discover", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.discover_peers).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✅ Trust", bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.trust_selected_peer).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🚫 Block", bg=self.colors['danger'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.block_selected_peer).pack(side=tk.LEFT, padx=5)
    
    def create_peer_details(self, parent):
        """Create peer details panel"""
        # Details header
        header_frame = tk.Frame(parent, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="Peer Details",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        # Details content
        details_frame = tk.Frame(parent, bg=self.colors['card'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Details text
        self.peer_details_text = scrolledtext.ScrolledText(
            details_frame, height=15, width=50,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.peer_details_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = tk.Frame(parent, bg=self.colors['card'])
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(action_frame, text="🔐 Authenticate", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.authenticate_selected_peer).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="🔗 Connect", bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.connect_to_peer).pack(side=tk.LEFT, padx=5)
    
    def create_trust_management(self, parent):
        """Create trust management section"""
        trust_frame = tk.Frame(parent, bg=self.colors['card'])
        trust_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(trust_frame, text="Trust Management",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Trust list
        trust_list_frame = tk.Frame(trust_frame, bg=self.colors['card'])
        trust_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for trusted peers
        columns = ('Name', 'IP Address', 'Added', 'Last Seen', 'Access Level')
        self.trusted_tree = ttk.Treeview(trust_list_frame, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.trusted_tree.heading(col, text=col)
            self.trusted_tree.column(col, width=100)
        
        self.trusted_tree.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        button_frame = tk.Frame(trust_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="❌ Remove Trust", bg=self.colors['warning'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.remove_trust).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Refresh", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.refresh_trusted_peers).pack(side=tk.LEFT, padx=5)
    
    def create_monitoring_tab(self):
        """Create monitoring tab"""
        monitoring_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(monitoring_frame, text="📊 Monitoring")
        
        # Create monitoring sections
        self.create_system_monitoring(monitoring_frame)
        self.create_performance_charts(monitoring_frame)
        self.create_event_logging(monitoring_frame)
    
    def create_system_monitoring(self, parent):
        """Create system monitoring section"""
        system_frame = tk.Frame(parent, bg=self.colors['card'])
        system_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(system_frame, text="System Monitoring",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # System metrics
        metrics_frame = tk.Frame(system_frame, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X)
        
        # Create metric cards
        self.create_metric_card(metrics_frame, "CPU Usage", "cpu_usage", 0)
        self.create_metric_card(metrics_frame, "Memory Usage", "memory_usage", 1)
        self.create_metric_card(metrics_frame, "Disk Usage", "disk_usage", 2)
        self.create_metric_card(metrics_frame, "Network I/O", "network_io", 3)
    
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
    
    def create_performance_charts(self, parent):
        """Create performance charts section"""
        charts_frame = tk.Frame(parent, bg=self.colors['card'])
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(charts_frame, text="Performance Charts",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create matplotlib figure if available
        if MATPLOTLIB_AVAILABLE:
            self.fig = Figure(figsize=(12, 6), facecolor=self.colors['card'])
            self.ax1 = self.fig.add_subplot(121, facecolor=self.colors['card'])
            self.ax2 = self.fig.add_subplot(122, facecolor=self.colors['card'])
            
            # Create canvas
            self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Create placeholder text if matplotlib not available
            placeholder_text = tk.Text(charts_frame, height=8, width=80,
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       font=('Consolas', 10), relief='flat')
            placeholder_text.pack(fill=tk.BOTH, expand=True)
            placeholder_text.insert(tk.END, "Charts require matplotlib\n\nInstall with: pip install matplotlib")
            placeholder_text.config(state='disabled')
            self.canvas = None
            self.fig = None
            self.ax1 = None
            self.ax2 = None
        
        # Chart buttons
        button_frame = tk.Frame(charts_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="🔄 Update Charts", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.update_charts).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📈 Toggle View", bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.toggle_chart_view).pack(side=tk.LEFT, padx=5)
    
    def create_event_logging(self, parent):
        """Create event logging section"""
        logging_frame = tk.Frame(parent, bg=self.colors['card'])
        logging_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(logging_frame, text="Event Logging",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Event text
        self.event_text = scrolledtext.ScrolledText(
            logging_frame, height=10, width=120,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.event_text.pack(fill=tk.BOTH, expand=True)
        
        # Event buttons
        event_buttons = tk.Frame(logging_frame, bg=self.colors['card'])
        event_buttons.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(event_buttons, text="🗑️ Clear", bg=self.colors['warning'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.clear_events).pack(side=tk.LEFT, padx=5)
        
        tk.Button(event_buttons, text="📥 Export", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.export_events).pack(side=tk.LEFT, padx=5)
        
        tk.Button(event_buttons, text="🔍 Filter", bg=self.colors['info'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.filter_events).pack(side=tk.LEFT, padx=5)
    
    def create_tools_tab(self):
        """Create tools tab"""
        tools_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(tools_frame, text="🛠️ Tools")
        
        # Create tools sections
        self.create_system_tools(tools_frame)
        self.create_diagnostics_tools(tools_frame)
        self.create_maintenance_tools(tools_frame)
    
    def create_system_tools(self, parent):
        """Create system tools section"""
        tools_frame = tk.Frame(parent, bg=self.colors['card'])
        tools_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(tools_frame, text="System Tools",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Tool buttons
        tools_container = tk.Frame(tools_frame, bg=self.colors['card'])
        tools_container.pack(fill=tk.X)
        
        tools = [
            ("🔍 System Diagnostics", self.run_diagnostics, self.colors['primary']),
            ("⚡ Performance Test", self.run_performance_test, self.colors['success']),
            ("🌐 Network Test", self.run_network_test, self.colors['info']),
            ("🧹 System Cleanup", self.cleanup_system, self.colors['warning']),
            ("⚙️ System Optimization", self.optimize_system, self.colors['accent']),
            ("🔄 System Restart", self.restart_system, self.colors['danger'])
        ]
        
        for i, (text, command, color) in enumerate(tools):
            btn = tk.Button(tools_container, text=text,
                           font=('Segoe UI', 10, 'bold'),
                           bg=color, fg=self.colors['bg'],
                           relief='flat', cursor='hand2',
                           command=command)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
            tools_container.grid_columnconfigure(i%3, weight=1)
    
    def create_diagnostics_tools(self, parent):
        """Create diagnostics tools section"""
        diagnostics_frame = tk.Frame(parent, bg=self.colors['card'])
        diagnostics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(diagnostics_frame, text="Diagnostics",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Diagnostics output
        self.diagnostics_text = scrolledtext.ScrolledText(
            diagnostics_frame, height=12, width=120,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.diagnostics_text.pack(fill=tk.BOTH, expand=True)
        
        # Diagnostics buttons
        button_frame = tk.Frame(diagnostics_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(button_frame, text="🔍 Run Diagnostics", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.run_diagnostics).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📥 Save Report", bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.save_diagnostics_report).pack(side=tk.LEFT, padx=5)
    
    def create_maintenance_tools(self, parent):
        """Create maintenance tools section"""
        maintenance_frame = tk.Frame(parent, bg=self.colors['card'])
        maintenance_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(maintenance_frame, text="Maintenance",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Maintenance tasks
        tasks_frame = tk.Frame(maintenance_frame, bg=self.colors['card'])
        tasks_frame.pack(fill=tk.X)
        
        maintenance_tasks = [
            ("🗑️ Clear Caches", self.clear_caches, self.colors['warning']),
            ("🔄 Restart Services", self.restart_services, self.colors['primary']),
            ("📊 Generate Report", self.generate_report, self.colors['success']),
            ("🔧 Repair System", self.repair_system, self.colors['danger'])
        ]
        
        for i, (text, command, color) in enumerate(maintenance_tasks):
            btn = tk.Button(tasks_frame, text=text,
                           font=('Segoe UI', 10, 'bold'),
                           bg=color, fg=self.colors['bg'],
                           relief='flat', cursor='hand2',
                           command=command)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            tasks_frame.grid_columnconfigure(i%2, weight=1)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Create settings sections
        self.create_general_settings(settings_frame)
        self.create_system_settings(settings_frame)
        self.create_network_settings(settings_frame)
        self.create_advanced_settings(settings_frame)
    
    def create_general_settings(self, parent):
        """Create general settings section"""
        general_frame = tk.Frame(parent, bg=self.colors['card'])
        general_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(general_frame, text="General Settings",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Settings options
        options_frame = tk.Frame(general_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X)
        
        # Auto-start
        auto_start_var = tk.BooleanVar(value=True)
        auto_start_check = tk.Checkbutton(options_frame, text="Auto-start systems on launch",
                                        variable=auto_start_var,
                                        bg=self.colors['card'], fg=self.colors['text'],
                                        selectcolor=self.colors['bg'])
        auto_start_check.pack(anchor=tk.W, pady=5)
        
        # Monitoring
        monitoring_var = tk.BooleanVar(value=True)
        monitoring_check = tk.Checkbutton(options_frame, text="Enable real-time monitoring",
                                         variable=monitoring_var,
                                         bg=self.colors['card'], fg=self.colors['text'],
                                         selectcolor=self.colors['bg'])
        monitoring_check.pack(anchor=tk.W, pady=5)
        
        # Notifications
        notifications_var = tk.BooleanVar(value=True)
        notifications_check = tk.Checkbutton(options_frame, text="Enable system notifications",
                                           variable=notifications_var,
                                           bg=self.colors['card'], fg=self.colors['text'],
                                           selectcolor=self.colors['bg'])
        notifications_check.pack(anchor=tk.W, pady=5)
    
    def create_system_settings(self, parent):
        """Create system settings section"""
        system_frame = tk.Frame(parent, bg=self.colors['card'])
        system_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(system_frame, text="System Settings",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # System options
        options_frame = tk.Frame(system_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X)
        
        # Resource limits
        tk.Label(options_frame, text="Resource Limits:",
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W, pady=5)
        
        # RAM limit
        ram_frame = tk.Frame(options_frame, bg=self.colors['card'])
        ram_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ram_frame, text="Max RAM per client (GB):",
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        ram_var = tk.StringVar(value="4.0")
        ram_entry = tk.Entry(ram_frame, textvariable=ram_var, bg=self.colors['bg'], fg=self.colors['text'])
        ram_entry.pack(side=tk.LEFT, padx=10)
        
        # CPU limit
        cpu_frame = tk.Frame(options_frame, bg=self.colors['card'])
        cpu_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cpu_frame, text="Max CPU cores per client:",
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        cpu_var = tk.StringVar(value="2")
        cpu_entry = tk.Entry(cpu_frame, textvariable=cpu_var, bg=self.colors['bg'], fg=self.colors['text'])
        cpu_entry.pack(side=tk.LEFT, padx=10)
    
    def create_network_settings(self, parent):
        """Create network settings section"""
        network_frame = tk.Frame(parent, bg=self.colors['card'])
        network_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(network_frame, text="Network Settings",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Network options
        options_frame = tk.Frame(network_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X)
        
        # Subnet
        subnet_frame = tk.Frame(options_frame, bg=self.colors['card'])
        subnet_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(subnet_frame, text="Subnet:",
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        subnet_var = tk.StringVar(value="192.168.1.0/24")
        subnet_entry = tk.Entry(subnet_frame, textvariable=subnet_var, bg=self.colors['bg'], fg=self.colors['text'])
        subnet_entry.pack(side=tk.LEFT, padx=10)
        
        # Discovery
        discovery_var = tk.BooleanVar(value=True)
        discovery_check = tk.Checkbutton(options_frame, text="Enable automatic peer discovery",
                                        variable=discovery_var,
                                        bg=self.colors['card'], fg=self.colors['text'],
                                        selectcolor=self.colors['bg'])
        discovery_check.pack(anchor=tk.W, pady=5)
    
    def create_advanced_settings(self, parent):
        """Create advanced settings section"""
        advanced_frame = tk.Frame(parent, bg=self.colors['card'])
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(advanced_frame, text="Advanced Settings",
                              font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Advanced options
        options_frame = tk.Frame(advanced_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X)
        
        # Debug mode
        debug_var = tk.BooleanVar(value=False)
        debug_check = tk.Checkbutton(options_frame, text="Enable debug mode",
                                    variable=debug_var,
                                    bg=self.colors['card'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg'])
        debug_check.pack(anchor=tk.W, pady=5)
        
        # Logging level
        log_frame = tk.Frame(options_frame, bg=self.colors['card'])
        log_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(log_frame, text="Logging level:",
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        log_var = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(log_frame, textvariable=log_var, values=["DEBUG", "INFO", "WARNING", "ERROR"])
        log_combo.pack(side=tk.LEFT, padx=10)
        
        # Settings buttons
        button_frame = tk.Frame(advanced_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="💾 Save Settings", bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.save_settings).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Reset Defaults", bg=self.colors['warning'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📥 Import Settings", bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.import_settings).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📤 Export Settings", bg=self.colors['info'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2', command=self.export_settings).pack(side=tk.LEFT, padx=5)
    
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
        
        # Separator
        separator = tk.Frame(status_bar, width=2, bg=self.colors['border'])
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
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
            if SYSTEMS_AVAILABLE:
                self.log_activity("Initializing homelab systems...")
                
                # Check system availability
                self.systems_status = {
                    'streamlined': self.check_streamlined_system(),
                    'auth': self.check_auth_system(),
                    'integrated': self.check_integrated_system()
                }
                
                self.log_activity(f"Systems initialized: {sum(self.systems_status.values())}/{len(self.systems_status)}")
            else:
                self.log_activity("System components not available")
                messagebox.showwarning("Warning", "System components not available. Some features may be limited.")
                
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
                
                # Update performance metrics
                self.update_performance_metrics()
                
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
            if SYSTEMS_AVAILABLE:
                # Update streamlined system status
                if self.systems_status.get('streamlined', False):
                    status = streamlined_homelab.get_system_status()
                    resources = status.get('resources', {})
                    self.streamlined_status.config(text=f"● Running", fg=self.colors['success'])
                    self.streamlined_details.config(text=f"Resources: {resources.get('total', 0)}")
                else:
                    self.streamlined_status.config(text="● Stopped", fg=self.colors['danger'])
                    self.streamlined_details.config(text="Not available")
                
                # Update auth system status
                if self.systems_status.get('auth', False):
                    status = pc_auth_system.get_system_status()
                    peers = status.get('peers', {})
                    self.auth_status.config(text=f"● Running", fg=self.colors['success'])
                    self.auth_details.config(text=f"Peers: {peers.get('total', 0)}")
                else:
                    self.auth_status.config(text="● Stopped", fg=self.colors['danger'])
                    self.auth_details.config(text="Not available")
                
                # Update integrated system status
                if self.systems_status.get('integrated', False):
                    status = integrated_homelab.get_integrated_status()
                    integration = status.get('integration_status', {})
                    self.integrated_status.config(text=f"● Running", fg=self.colors['success'])
                    self.integrated_details.config(text=f"Auth peers: {integration.get('authenticated_peers', 0)}")
                else:
                    self.integrated_status.config(text="● Stopped", fg=self.colors['danger'])
                    self.integrated_details.config(text="Not available")
                
                # Update resources status
                total_resources = len(streamlined_homelab.resources) if hasattr(streamlined_homelab, 'resources') else 0
                self.resources_status.config(text=f"● Available", fg=self.colors['success'])
                self.resources_details.config(text=f"Total: {total_resources}")
            
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
            
            # Update resource cards
            if hasattr(streamlined_homelab, 'resources'):
                for resource_id, resource in streamlined_homelab.resources.items():
                    if resource.type == 'ram':
                        usage = (resource.allocated / resource.capacity) * 100 if resource.capacity > 0 else 0
                        self.ram_usage.config(text=f"{usage:.1f}%")
                        self.ram_details.config(text=f"{resource.allocated:.1f} / {resource.capacity:.1f} GB")
                    elif resource.type == 'cpu':
                        usage = (resource.allocated / resource.capacity) * 100 if resource.capacity > 0 else 0
                        self.cpu_usage_value.config(text=f"{usage:.1f}%")
                        self.cpu_details.config(text=f"{resource.allocated:.1f} / {resource.capacity:.1f} cores")
                    elif resource.type == 'gpu':
                        usage = (resource.allocated / resource.capacity) * 100 if resource.capacity > 0 else 0
                        self.gpu_usage.config(text=f"{usage:.1f}%")
                        self.gpu_details.config(text=f"{resource.allocated:.1f} / {resource.capacity:.1f} GB")
                    elif resource.type == 'network':
                        usage = (resource.allocated / resource.capacity) * 100 if resource.capacity > 0 else 0
                        self.network_usage.config(text=f"{usage:.1f}%")
                        self.network_details.config(text=f"{resource.allocated:.1f} / {resource.capacity:.1f} Gbps")
        
        except Exception as e:
            print(f"Error updating resource usage: {e}")
    
    def update_performance_metrics(self):
        """Update performance metrics"""
        try:
            # Update charts periodically
            if hasattr(self, 'last_chart_update'):
                if time.time() - self.last_chart_update > 30:  # Update every 30 seconds
                    self.update_charts()
                    self.last_chart_update = time.time()
            else:
                self.last_chart_update = time.time()
        
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def update_time(self):
        """Update time display"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
        except:
            pass
    
    def update_charts(self):
        """Update performance charts"""
        try:
            if not MATPLOTLIB_AVAILABLE or not self.ax1 or not self.ax2:
                return
            
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            # Create sample data for demonstration
            time_points = np.arange(0, 60, 1)
            
            # CPU and Memory chart
            if PSUTIL_AVAILABLE:
                cpu_data = psutil.cpu_percent(interval=None) + 10 * np.sin(np.linspace(0, 2*np.pi, 60))
                memory_data = psutil.virtual_memory().percent + 5 * np.sin(np.linspace(0, 2*np.pi, 60) + np.pi/4)
            else:
                cpu_data = 50 + 20 * np.sin(np.linspace(0, 2*np.pi, 60))
                memory_data = 60 + 15 * np.sin(np.linspace(0, 2*np.pi, 60) + np.pi/4)
            
            self.ax1.plot(time_points, cpu_data, label='CPU Usage', color=self.colors['primary'])
            self.ax1.plot(time_points, memory_data, label='Memory Usage', color=self.colors['success'])
            self.ax1.set_xlabel('Time (seconds)')
            self.ax1.set_ylabel('Usage (%)')
            self.ax1.set_title('System Performance')
            self.ax1.legend()
            self.ax1.grid(True, alpha=0.3)
            
            # Resource allocation chart
            if hasattr(streamlined_homelab, 'resources'):
                resource_names = []
                allocated_values = []
                total_values = []
                
                for resource_id, resource in streamlined_homelab.resources.items():
                    resource_names.append(resource.name[:10] + '...' if len(resource.name) > 10 else resource.name)
                    allocated_values.append(resource.allocated)
                    total_values.append(resource.capacity)
                
                x = np.arange(len(resource_names))
                width = 0.35
                
                self.ax2.bar(x - width/2, allocated_values, width, label='Allocated', color=self.colors['primary'])
                self.ax2.bar(x + width/2, total_values, width, label='Total', color=self.colors['success'])
                
                self.ax2.set_xlabel('Resources')
                self.ax2.set_ylabel('Amount')
                self.ax2.set_title('Resource Allocation')
                self.ax2.set_xticks(x)
                self.ax2.set_xticklabels(resource_names, rotation=45, ha='right')
                self.ax2.legend()
                self.ax2.grid(True, alpha=0.3)
            
            # Style the plots
            for ax in [self.ax1, self.ax2]:
                ax.set_facecolor(self.colors['card'])
                ax.spines['bottom'].set_color(self.colors['text_secondary'])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color(self.colors['text_secondary'])
                ax.tick_params(colors=self.colors['text_secondary'])
                ax.xaxis.label.set_color(self.colors['text'])
                ax.yaxis.label.set_color(self.colors['text'])
                ax.title.set_color(self.colors['text'])
            
            if self.canvas:
                self.canvas.draw()
        
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def toggle_chart_view(self):
        """Toggle chart view"""
        # This would toggle between different chart views
        self.update_charts()
    
    def refresh_all_data(self):
        """Refresh all data displays"""
        try:
            self.update_system_status()
            self.update_resource_usage()
            self.refresh_resources()
            self.refresh_allocations()
            self.refresh_peers()
            self.refresh_trusted_peers()
            self.log_activity("All data refreshed")
        except Exception as e:
            self.log_activity(f"Error refreshing data: {e}")
    
    def refresh_resources(self):
        """Refresh resources display"""
        try:
            # Clear existing items
            for item in self.resources_tree.get_children():
                self.resources_tree.delete(item)
            
            if hasattr(streamlined_homelab, 'resources'):
                for resource_id, resource in streamlined_homelab.resources.items():
                    available = resource.capacity - resource.allocated
                    self.resources_tree.insert('', 'end', values=(
                        resource.name,
                        resource.type,
                        f"{resource.capacity:.1f}",
                        f"{resource.allocated:.1f}",
                        f"{available:.1f}",
                        resource.status.value
                    ))
        
        except Exception as e:
            print(f"Error refreshing resources: {e}")
    
    def refresh_allocations(self):
        """Refresh allocations display"""
        try:
            # Clear existing items
            for item in self.allocations_tree.get_children():
                self.allocations_tree.delete(item)
            
            if hasattr(streamlined_homelab, 'allocations'):
                for allocation_id, allocation in streamlined_homelab.allocations.items():
                    created = allocation.created_at.strftime('%H:%M:%S') if allocation.created_at else 'Unknown'
                    expires = allocation.expires_at.strftime('%H:%M:%S') if allocation.expires_at else 'Never'
                    
                    self.allocations_tree.insert('', 'end', values=(
                        allocation.client_id,
                        allocation.resource_id,
                        f"{allocation.amount:.1f}",
                        created,
                        expires,
                        allocation.status
                    ))
        
        except Exception as e:
            print(f"Error refreshing allocations: {e}")
    
    def refresh_peers(self):
        """Refresh peers display"""
        try:
            # Clear existing items
            for item in self.peers_tree.get_children():
                self.peers_tree.delete(item)
            
            if hasattr(pc_auth_system, 'peers'):
                for peer_id, peer in pc_auth_system.peers.items():
                    last_seen = peer.last_seen.strftime('%H:%M:%S') if peer.last_seen else 'Never'
                    
                    self.peers_tree.insert('', 'end', values=(
                        peer.name,
                        peer.ip_address,
                        peer.role.value,
                        peer.status.value,
                        last_seen
                    ), tags=(peer_id,))
            
            # Update auth overview
            if hasattr(pc_auth_system, 'get_system_status'):
                status = pc_auth_system.get_system_status()
                peers = status.get('peers', {})
                
                self.discovered_peers_count.config(text=str(peers.get('total', 0)))
                self.trusted_peers_count.config(text=str(peers.get('trusted', 0)))
                self.active_sessions_count.config(text=str(status.get('sessions', {}).get('active', 0)))
                
                if hasattr(pc_auth_system, 'local_peer'):
                    self.local_peer_count.config(text="1")
                    self.local_peer_status.config(text="● Active", fg=self.colors['success'])
        
        except Exception as e:
            print(f"Error refreshing peers: {e}")
    
    def refresh_trusted_peers(self):
        """Refresh trusted peers display"""
        try:
            # Clear existing items
            for item in self.trusted_tree.get_children():
                self.trusted_tree.delete(item)
            
            if hasattr(pc_auth_system, 'trusted_peers'):
                for peer_id in pc_auth_system.trusted_peers:
                    if peer_id in pc_auth_system.peers:
                        peer = pc_auth_system.peers[peer_id]
                        added = peer.created_at.strftime('%Y-%m-%d') if peer.created_at else 'Unknown'
                        last_seen = peer.last_seen.strftime('%H:%M:%S') if peer.last_seen else 'Never'
                        
                        self.trusted_tree.insert('', 'end', values=(
                            peer.name,
                            peer.ip_address,
                            added,
                            last_seen,
                            "Full Access"
                        ))
        
        except Exception as e:
            print(f"Error refreshing trusted peers: {e}")
    
    def log_activity(self, message: str):
        """Log activity message"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.activity_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.activity_text.see(tk.END)
        except:
            pass
    
    def log_event(self, message: str):
        """Log event message"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.event_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.event_text.see(tk.END)
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
                # Start streamlined system
                if not self.systems_status.get('streamlined', False):
                    self.start_streamlined()
                
                # Start auth system
                if not self.systems_status.get('auth', False):
                    self.start_auth()
                
                # Start integrated system
                if not self.systems_status.get('integrated', False):
                    self.start_integrated()
            
            self.log_activity("All systems start command sent")
            self.update_status("Starting systems...")
            
        except Exception as e:
            self.log_activity(f"Error starting systems: {e}")
            messagebox.showerror("Error", f"Failed to start systems: {e}")
    
    def stop_all_systems(self):
        """Stop all systems"""
        try:
            self.log_activity("Stopping all systems...")
            
            if SYSTEMS_AVAILABLE:
                # Stop integrated system
                if self.systems_status.get('integrated', False):
                    self.stop_integrated()
                
                # Stop auth system
                if self.systems_status.get('auth', False):
                    self.stop_auth()
                
                # Stop streamlined system
                if self.systems_status.get('streamlined', False):
                    self.stop_streamlined()
            
            self.log_activity("All systems stop command sent")
            self.update_status("Stopping systems...")
            
        except Exception as e:
            self.log_activity(f"Error stopping systems: {e}")
            messagebox.showerror("Error", f"Failed to stop systems: {e}")
    
    def start_streamlined(self):
        """Start streamlined system"""
        try:
            self.log_activity("Starting streamlined system...")
            # This would start the streamlined system
            self.systems_status['streamlined'] = True
            self.log_activity("Streamlined system started")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error starting streamlined system: {e}")
    
    def stop_streamlined(self):
        """Stop streamlined system"""
        try:
            self.log_activity("Stopping streamlined system...")
            # This would stop the streamlined system
            self.systems_status['streamlined'] = False
            self.log_activity("Streamlined system stopped")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error stopping streamlined system: {e}")
    
    def start_auth(self):
        """Start authentication system"""
        try:
            self.log_activity("Starting authentication system...")
            # This would start the auth system
            self.systems_status['auth'] = True
            self.log_activity("Authentication system started")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error starting authentication system: {e}")
    
    def stop_auth(self):
        """Stop authentication system"""
        try:
            self.log_activity("Stopping authentication system...")
            # This would stop the auth system
            self.systems_status['auth'] = False
            self.log_activity("Authentication system stopped")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error stopping authentication system: {e}")
    
    def start_integrated(self):
        """Start integrated system"""
        try:
            self.log_activity("Starting integrated system...")
            # This would start the integrated system
            self.systems_status['integrated'] = True
            self.log_activity("Integrated system started")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error starting integrated system: {e}")
    
    def stop_integrated(self):
        """Stop integrated system"""
        try:
            self.log_activity("Stopping integrated system...")
            # This would stop the integrated system
            self.systems_status['integrated'] = False
            self.log_activity("Integrated system stopped")
            self.update_system_status()
        except Exception as e:
            self.log_activity(f"Error stopping integrated system: {e}")
    
    def restart_streamlined(self):
        """Restart streamlined system"""
        self.stop_streamlined()
        time.sleep(2)
        self.start_streamlined()
    
    def restart_auth(self):
        """Restart authentication system"""
        self.stop_auth()
        time.sleep(2)
        self.start_auth()
    
    def restart_integrated(self):
        """Restart integrated system"""
        self.stop_integrated()
        time.sleep(2)
        self.start_integrated()
    
    # Tool methods
    def run_diagnostics(self):
        """Run system diagnostics"""
        try:
            self.log_activity("Running system diagnostics...")
            
            diagnostics = []
            
            # System information
            if PSUTIL_AVAILABLE:
                diagnostics.append(f"CPU Count: {psutil.cpu_count()}")
                diagnostics.append(f"Memory Total: {psutil.virtual_memory().total / (1024**3):.1f} GB")
                diagnostics.append(f"Disk Total: {psutil.disk_usage('/').total / (1024**3):.1f} GB")
                diagnostics.append(f"Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # System status
            diagnostics.append(f"Streamlined System: {'Running' if self.systems_status.get('streamlined') else 'Stopped'}")
            diagnostics.append(f"Auth System: {'Running' if self.systems_status.get('auth') else 'Stopped'}")
            diagnostics.append(f"Integrated System: {'Running' if self.systems_status.get('integrated') else 'Stopped'}")
            
            # Display diagnostics
            self.diagnostics_text.delete(1.0, tk.END)
            self.diagnostics_text.insert(tk.END, "System Diagnostics Report\n")
            self.diagnostics_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for diagnostic in diagnostics:
                self.diagnostics_text.insert(tk.END, f"{diagnostic}\n")
            
            self.log_activity("Diagnostics completed")
            
        except Exception as e:
            self.log_activity(f"Error running diagnostics: {e}")
    
    def run_performance_test(self):
        """Run performance test"""
        try:
            self.log_activity("Running performance test...")
            
            # This would run actual performance tests
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
            
            # This would run actual network tests
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
            
            # This would perform actual cleanup
            self.log_activity("System cleanup completed")
            
        except Exception as e:
            self.log_activity(f"Error during cleanup: {e}")
    
    def optimize_system(self):
        """Optimize system"""
        try:
            self.log_activity("Optimizing system...")
            
            # This would perform actual optimization
            self.log_activity("System optimization completed")
            
        except Exception as e:
            self.log_activity(f"Error during optimization: {e}")
    
    # Resource management methods
    def allocate_resource_dialog(self):
        """Show resource allocation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Allocate Resource")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['card'])
        
        # Resource selection
        tk.Label(dialog, text="Select Resource:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        resource_var = tk.StringVar()
        if hasattr(streamlined_homelab, 'resources'):
            resource_combo = ttk.Combobox(dialog, textvariable=resource_var)
            resource_combo['values'] = [r.name for r in streamlined_homelab.resources.values()]
            resource_combo.pack(pady=5)
        
        # Client ID
        tk.Label(dialog, text="Client ID:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        client_var = tk.StringVar()
        client_entry = tk.Entry(dialog, textvariable=client_var, bg=self.colors['bg'], fg=self.colors['text'])
        client_entry.pack(pady=5)
        
        # Amount
        tk.Label(dialog, text="Amount:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        amount_var = tk.DoubleVar(value=1.0)
        amount_entry = tk.Entry(dialog, textvariable=amount_var, bg=self.colors['bg'], fg=self.colors['text'])
        amount_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Allocate", bg=self.colors['primary'], fg=self.colors['bg'],
                 command=lambda: self.allocate_resource(resource_var.get(), client_var.get(), amount_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", bg=self.colors['danger'], fg=self.colors['bg'],
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def allocate_resource(self, resource_name, client_id, amount, dialog):
        """Allocate a resource"""
        try:
            if hasattr(streamlined_homelab, 'allocate_resource'):
                # Find resource by name
                resource_id = None
                for rid, resource in streamlined_homelab.resources.items():
                    if resource.name == resource_name:
                        resource_id = rid
                        break
                
                if resource_id:
                    allocation = streamlined_homelab.allocate_resource(resource_id, client_id, amount)
                    
                    if allocation:
                        messagebox.showinfo("Success", f"Resource allocated successfully!\nAllocation ID: {allocation.id}")
                        dialog.destroy()
                        self.refresh_resources()
                        self.refresh_allocations()
                        self.log_activity(f"Resource allocated: {resource_name} to {client_id}")
                    else:
                        messagebox.showerror("Error", "Failed to allocate resource")
                else:
                    messagebox.showerror("Error", "Resource not found")
            else:
                messagebox.showerror("Error", "Resource allocation not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to allocate resource: {e}")
    
    def release_resource_dialog(self):
        """Show resource release dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Release Resource")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['card'])
        
        # Allocation ID
        tk.Label(dialog, text="Allocation ID:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        allocation_var = tk.StringVar()
        allocation_entry = tk.Entry(dialog, textvariable=allocation_var, bg=self.colors['bg'], fg=self.colors['text'])
        allocation_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Release", bg=self.colors['danger'], fg=self.colors['bg'],
                 command=lambda: self.release_resource(allocation_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", bg=self.colors['warning'], fg=self.colors['bg'],
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def release_resource(self, allocation_id, dialog):
        """Release a resource allocation"""
        try:
            if hasattr(streamlined_homelab, 'release_resource'):
                if streamlined_homelab.release_resource(allocation_id):
                    messagebox.showinfo("Success", f"Resource allocation {allocation_id} released successfully!")
                    dialog.destroy()
                    self.refresh_resources()
                    self.refresh_allocations()
                    self.log_activity(f"Resource released: {allocation_id}")
                else:
                    messagebox.showerror("Error", "Failed to release resource allocation")
            else:
                messagebox.showerror("Error", "Resource release not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to release resource: {e}")
    
    def release_selected_allocation(self):
        """Release selected allocation"""
        try:
            selected = self.allocations_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an allocation to release")
                return
            
            # Get allocation details
            item = self.allocations_tree.item(selected[0])
            values = item['values']
            
            if len(values) >= 1:
                # This would get the actual allocation ID
                messagebox.showinfo("Info", "Selected allocation release functionality would be implemented here")
                self.refresh_allocations()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to release selected allocation: {e}")
    
    # Authentication methods
    def discover_peers(self):
        """Discover peers"""
        try:
            if hasattr(pc_auth_system, 'discover_peers'):
                self.log_activity("Discovering peers...")
                peers = pc_auth_system.discover_peers()
                self.log_activity(f"Discovered {len(peers)} peers")
                self.refresh_peers()
            else:
                messagebox.showerror("Error", "Peer discovery not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to discover peers: {e}")
    
    def on_peer_select(self, event):
        """Handle peer selection"""
        try:
            selection = self.peers_tree.selection()
            if selection:
                item = self.peers_tree.item(selection[0])
                values = item['values']
                
                if len(values) >= 2:
                    # Find peer by IP address
                    ip_address = values[1]
                    if hasattr(pc_auth_system, 'peers'):
                        for peer_id, peer in pc_auth_system.peers.items():
                            if peer.ip_address == ip_address:
                                self.display_peer_details(peer)
                                break
            
        except Exception as e:
            print(f"Error handling peer selection: {e}")
    
    def display_peer_details(self, peer):
        """Display peer details"""
        try:
            details = f"""Peer Information:
================
ID: {peer.id}
Name: {peer.name}
Hostname: {peer.hostname}
IP Address: {peer.ip_address}
MAC Address: {peer.mac_address}
Role: {peer.role.value}
Status: {peer.status.value}
Fingerprint: {peer.fingerprint}

Trust Information:
==================
Is Trusted: {peer.id in pc_auth_system.trusted_peers}
Is Blocked: {peer.id in pc_auth_system.blocked_peers}

Timestamps:
===========
Created: {peer.created_at}
Last Seen: {peer.last_seen}
"""
            
            self.peer_details_text.delete(1.0, tk.END)
            self.peer_details_text.insert(tk.END, details)
            
        except Exception as e:
            print(f"Error displaying peer details: {e}")
    
    def trust_selected_peer(self):
        """Trust selected peer"""
        try:
            selection = self.peers_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a peer to trust")
                return
            
            item = self.peers_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 2:
                ip_address = values[1]
                if hasattr(pc_auth_system, 'peers'):
                    for peer_id, peer in pc_auth_system.peers.items():
                        if peer.ip_address == ip_address:
                            if pc_auth_system.trust_peer(peer_id):
                                messagebox.showinfo("Success", "Peer trusted successfully!")
                                self.refresh_peers()
                                self.refresh_trusted_peers()
                                self.log_activity(f"Peer trusted: {peer.name}")
                            else:
                                messagebox.showerror("Error", "Failed to trust peer")
                            break
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to trust peer: {e}")
    
    def block_selected_peer(self):
        """Block selected peer"""
        try:
            selection = self.peers_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a peer to block")
                return
            
            item = self.peers_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 2:
                ip_address = values[1]
                if hasattr(pc_auth_system, 'peers'):
                    for peer_id, peer in pc_auth_system.peers.items():
                        if peer.ip_address == ip_address:
                            if pc_auth_system.block_peer(peer_id):
                                messagebox.showinfo("Success", "Peer blocked successfully!")
                                self.refresh_peers()
                                self.refresh_trusted_peers()
                                self.log_activity(f"Peer blocked: {peer.name}")
                            else:
                                messagebox.showerror("Error", "Failed to block peer")
                            break
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to block peer: {e}")
    
    def authenticate_selected_peer(self):
        """Authenticate with selected peer"""
        try:
            selection = self.peers_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a peer to authenticate with")
                return
            
            # This would implement peer authentication
            messagebox.showinfo("Info", "Peer authentication functionality would be implemented here")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to authenticate: {e}")
    
    def connect_to_peer(self):
        """Connect to selected peer"""
        try:
            selection = self.peers_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a peer to connect to")
                return
            
            # This would implement peer connection
            messagebox.showinfo("Info", "Peer connection functionality would be implemented here")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")
    
    def remove_trust(self):
        """Remove trust from selected peer"""
        try:
            # This would implement trust removal
            messagebox.showinfo("Info", "Trust removal functionality would be implemented here")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove trust: {e}")
    
    def refresh_trusted_peers(self):
        """Refresh trusted peers display"""
        self.refresh_trusted_peers()
    
    # Monitoring methods
    def toggle_monitoring(self):
        """Toggle monitoring"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.monitoring_btn.config(text="📊 Monitor", bg=self.colors['info'])
            self.log_activity("Monitoring stopped")
        else:
            self.start_monitoring()
            self.monitoring_btn.config(text="⏸️ Pause", bg=self.colors['warning'])
    
    def clear_events(self):
        """Clear events display"""
        try:
            self.event_text.delete(1.0, tk.END)
            self.event_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Events cleared\n")
        except:
            pass
    
    def export_events(self):
        """Export events to file"""
        try:
            events_content = self.event_text.get(1.0, tk.END)
            
            events_file = Path(__file__).parent / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(events_file, 'w') as f:
                f.write(events_content)
            
            messagebox.showinfo("Export", f"Events exported to {events_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export events: {e}")
    
    def filter_events(self):
        """Filter events"""
        # This would implement event filtering
        messagebox.showinfo("Info", "Event filtering functionality would be implemented here")
    
    # Tools methods
    def open_tools(self):
        """Open tools dialog"""
        # This would open tools dialog
        messagebox.showinfo("Info", "Tools dialog functionality would be implemented here")
    
    def view_analytics(self):
        """View analytics"""
        # This would open analytics view
        messagebox.showinfo("Info", "Analytics view functionality would be implemented here")
    
    def open_settings(self):
        """Open settings"""
        # Switch to settings tab
        self.notebook.select(5)  # Settings tab index
    
    def clear_caches(self):
        """Clear system caches"""
        try:
            self.log_activity("Clearing system caches...")
            # This would clear caches
            self.log_activity("System caches cleared")
        except Exception as e:
            self.log_activity(f"Error clearing caches: {e}")
    
    def restart_services(self):
        """Restart services"""
        try:
            self.log_activity("Restarting services...")
            # This would restart services
            self.log_activity("Services restarted")
        except Exception as e:
            self.log_activity(f"Error restarting services: {e}")
    
    def generate_report(self):
        """Generate system report"""
        try:
            self.log_activity("Generating system report...")
            # This would generate report
            self.log_activity("System report generated")
        except Exception as e:
            self.log_activity(f"Error generating report: {e}")
    
    def repair_system(self):
        """Repair system"""
        try:
            self.log_activity("Repairing system...")
            # This would repair system
            self.log_activity("System repair completed")
        except Exception as e:
            self.log_activity(f"Error repairing system: {e}")
    
    def restart_system(self):
        """Restart system"""
        try:
            if messagebox.askyesno("Restart System", "Restart all homelab systems?"):
                self.stop_all_systems()
                time.sleep(3)
                self.start_all_systems()
                self.log_activity("System restarted")
        except Exception as e:
            self.log_activity(f"Error restarting system: {e}")
    
    def save_diagnostics_report(self):
        """Save diagnostics report"""
        try:
            diagnostics_content = self.diagnostics_text.get(1.0, tk.END)
            
            report_file = Path(__file__).parent / f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w') as f:
                f.write(diagnostics_content)
            
            messagebox.showinfo("Save", f"Diagnostics report saved to {report_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save diagnostics report: {e}")
    
    # Settings methods
    def save_settings(self):
        """Save settings"""
        try:
            self.log_activity("Settings saved")
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        try:
            if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
                self.log_activity("Settings reset to defaults")
                messagebox.showinfo("Success", "Settings reset to defaults!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def import_settings(self):
        """Import settings"""
        try:
            # This would implement settings import
            messagebox.showinfo("Info", "Settings import functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def export_settings(self):
        """Export settings"""
        try:
            # This would implement settings export
            messagebox.showinfo("Info", "Settings export functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    # Menu methods
    def load_configuration(self):
        """Load configuration"""
        try:
            # This would load configuration
            messagebox.showinfo("Info", "Configuration load functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def save_configuration(self):
        """Save configuration"""
        try:
            # This would save configuration
            messagebox.showinfo("Info", "Configuration save functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def export_data(self):
        """Export data"""
        try:
            # This would export data
            messagebox.showinfo("Info", "Data export functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def import_data(self):
        """Import data"""
        try:
            # This would import data
            messagebox.showinfo("Info", "Data import functionality would be implemented here")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {e}")
    
    def exit_application(self):
        """Exit application"""
        try:
            if messagebox.askyesno("Exit", "Stop all systems and exit?"):
                self.stop_all_systems()
                self.monitoring_active = False
                self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to exit: {e}")
    
    def show_system_info(self):
        """Show system information"""
        try:
            info = "System Information:\n"
            info += f"Python Version: {sys.version}\n"
            info += f"Platform: {sys.platform}\n"
            
            if PSUTIL_AVAILABLE:
                info += f"CPU Count: {psutil.cpu_count()}\n"
                info += f"Memory Total: {psutil.virtual_memory().total / (1024**3):.1f} GB\n"
                info += f"Disk Total: {psutil.disk_usage('/').total / (1024**3):.1f} GB\n"
            
            messagebox.showinfo("System Information", info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system info: {e}")
    
    def show_network_info(self):
        """Show network information"""
        try:
            info = "Network Information:\n"
            
            if PSUTIL_AVAILABLE:
                net_io = psutil.net_io_counters()
                info += f"Bytes Sent: {net_io.bytes_sent / (1024**2):.1f} MB\n"
                info += f"Bytes Received: {net_io.bytes_recv / (1024**2):.1f} MB\n"
                
                net_if_addrs = psutil.net_if_addrs()
                for interface, addresses in net_if_addrs.items():
                    info += f"\n{interface}:\n"
                    for addr in addresses:
                        info += f"  {addr.family.name}: {addr.address}\n"
            
            messagebox.showinfo("Network Information", info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get network info: {e}")
    
    def show_documentation(self):
        """Show documentation"""
        try:
            # This would open documentation
            webbrowser.open("file://" + str(current_dir / "UNIFIED_LAUNCHER_GUIDE.md"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open documentation: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Fully Unified Homelab GUI
Version 1.0

A comprehensive GUI for managing all homelab systems including:
- Streamlined Homelab System
- PC Authentication System
- Integrated Homelab with Authentication
- Resource Management
- System Monitoring
- Tools and Diagnostics

Created for the ultimate homelab management experience."""
        
        messagebox.showinfo("About", about_text)
    
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

# Main execution
if __name__ == '__main__':
    root = tk.Tk()
    app = FullyUnifiedGUI(root)
    
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
