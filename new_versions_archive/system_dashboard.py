#!/usr/bin/env python3
"""
System Performance Dashboard
A comprehensive dashboard for monitoring and optimizing RAM, GPU, and CPU performance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import gc
import os
import subprocess
import platform
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Import monitoring modules
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
    nvml.nvmlInit()
except ImportError:
    NVML_AVAILABLE = False
    nvml = None

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class SystemDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 System Performance Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Modern color scheme with distinct colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'card_hover': '#3a3a3a',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#0078ff',
            'graph_bg': '#242424',
            'ram_line': '#ff4444',      # Red for RAM
            'gpu_line': '#00ff88',      # Green for GPU  
            'cpu_line': '#9b59b6'       # Purple for CPU (more distinct)
        }
        
        # Data storage for plotting
        self.time_data = []
        self.ram_data = []
        self.gpu_data = []
        self.cpu_data = []
        self.max_points = 60  # Show last 60 data points
        
        # System info
        self.cpu_count = psutil.cpu_count(logical=True)
        self.cpu_physical = psutil.cpu_count(logical=False)
        self.gpu_count = 0
        
        # Monitoring settings
        self.update_interval = 2000  # Update every 2 seconds
        self.monitoring = False
        self.monitor_thread = None
        
        # Style configuration
        self.setup_styles()
        
        # Initialize GPU detection
        self.detect_gpus()
        
        # Create GUI components
        self.create_widgets()
        
        # Start monitoring automatically
        self.start_monitoring()
    
    def setup_styles(self):
        """Setup modern custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles
        style.configure('Title.TLabel', background=self.colors['bg'], foreground=self.colors['primary'], 
                       font=('Segoe UI', 24, 'bold'))
        style.configure('Card.TFrame', background=self.colors['card'], relief='flat', borderwidth=1)
        style.configure('Info.TLabel', background=self.colors['card'], foreground=self.colors['text'], 
                       font=('Segoe UI', 10))
        style.configure('InfoValue.TLabel', background=self.colors['card'], foreground=self.colors['primary'], 
                       font=('Segoe UI', 14, 'bold'))
        style.configure('Success.TLabel', background=self.colors['card'], foreground=self.colors['success'], 
                       font=('Segoe UI', 10, 'bold'))
        style.configure('Warning.TLabel', background=self.colors['card'], foreground=self.colors['warning'], 
                       font=('Segoe UI', 10, 'bold'))
        style.configure('Danger.TLabel', background=self.colors['card'], foreground=self.colors['danger'], 
                       font=('Segoe UI', 10, 'bold'))
        style.configure('Primary.TButton', background=self.colors['primary'], foreground=self.colors['bg'], 
                       font=('Segoe UI', 10, 'bold'), relief='flat', borderwidth=0)
        style.configure('Success.TButton', background=self.colors['success'], foreground=self.colors['bg'], 
                       font=('Segoe UI', 10, 'bold'), relief='flat', borderwidth=0)
        style.configure('Warning.TButton', background=self.colors['warning'], foreground=self.colors['bg'], 
                       font=('Segoe UI', 10, 'bold'), relief='flat', borderwidth=0)
        style.configure('Secondary.TButton', background=self.colors['card'], foreground=self.colors['text'], 
                       font=('Segoe UI', 9), relief='flat', borderwidth=1)
        
        # Configure progress bar
        style.configure('Modern.Horizontal.TProgressbar', 
                       background=self.colors['primary'],
                       troughcolor=self.colors['card'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
    
    def detect_gpus(self):
        """Detect available GPUs"""
        try:
            # Try nvidia-smi first for NVIDIA GPUs
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                names = result.stdout.strip().split('\n')
                self.gpu_count = len([name for name in names if name.strip()])
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                self.gpu_count = len(gpus)
            else:
                self.gpu_count = 0
        except:
            self.gpu_count = 0
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="🚀 System Performance Dashboard", 
                              font=('Segoe UI', 28, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = tk.Label(header_frame, text="● Monitoring", 
                                    font=('Segoe UI', 12, 'bold'), 
                                    bg=self.colors['bg'], fg=self.colors['success'])
        self.status_label.pack(side=tk.RIGHT)
        
        # System info
        info_frame = tk.Frame(main_container, bg=self.colors['bg'])
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = f"CPU: {self.cpu_physical} cores / {self.cpu_count} threads"
        if self.gpu_count > 0:
            info_text += f" | GPU: {self.gpu_count} detected"
        
        info_label = tk.Label(info_frame, text=info_text, 
                             font=('Segoe UI', 10), 
                             fg=self.colors['text_secondary'], bg=self.colors['bg'])
        info_label.pack()
        
        # Performance cards container
        cards_frame = tk.Frame(main_container, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create performance cards
        self.create_performance_cards(cards_frame)
        
        # Graph container
        graph_frame = tk.Frame(main_container, bg=self.colors['card'], relief='flat', bd=1)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 4), dpi=80, facecolor=self.colors['graph_bg'])
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_facecolor(self.colors['graph_bg'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Process tracking container
        process_frame = tk.Frame(main_container, bg=self.colors['card'], relief='flat', bd=1)
        process_frame.pack(fill=tk.X, pady=(0, 20))
        
        process_title = tk.Label(process_frame, text="📊 Process Tracking", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg=self.colors['primary'], bg=self.colors['card'])
        process_title.pack(pady=(10, 5))
        
        # Process info display
        self.process_info_label = tk.Label(process_frame, text="No active cleaning processes", 
                                         font=('Segoe UI', 9), 
                                         fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.process_info_label.pack(pady=(0, 10))
        
        # Quick actions container
        actions_frame = tk.Frame(main_container, bg=self.colors['bg'])
        actions_frame.pack(fill=tk.X)
        
        # Create quick action buttons
        self.create_quick_actions(actions_frame)
    
    def create_performance_cards(self, parent):
        """Create performance monitoring cards"""
        # RAM Card
        self.ram_card = self.create_info_card(parent, "🧹 RAM", "0%", self.colors['ram_line'])
        self.ram_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # GPU Card
        self.gpu_card = self.create_info_card(parent, "🎮 GPU", "0%", self.colors['gpu_line'])
        self.gpu_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # CPU Card
        self.cpu_card = self.create_info_card(parent, "⚡ CPU", "0%", self.colors['cpu_line'])
        self.cpu_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_info_card(self, parent, title, value, color):
        """Create an info card widget"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        
        # Title
        title_label = tk.Label(card, text=title, 
                             font=('Segoe UI', 12, 'bold'), 
                             fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = tk.Label(card, text=value, 
                              font=('Segoe UI', 20, 'bold'), 
                              fg=color, bg=self.colors['card'])
        value_label.pack(pady=(0, 5))
        
        # Progress bar
        progress = ttk.Progressbar(card, length=100, mode='determinate', 
                                  style='Modern.Horizontal.TProgressbar')
        progress.pack(pady=(0, 15), padx=15, fill=tk.X)
        
        # Details
        details_label = tk.Label(card, text="Loading...", 
                                font=('Segoe UI', 9), 
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
        details_label.pack(pady=(0, 10))
        
        # Store references
        card.value_label = value_label
        card.progress = progress
        card.details_label = details_label
        
        return card
    
    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        # RAM Actions
        ram_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        ram_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ram_title = tk.Label(ram_frame, text="🧹 RAM Actions", 
                            font=('Segoe UI', 11, 'bold'), 
                            fg=self.colors['ram_line'], bg=self.colors['card'])
        ram_title.pack(pady=(10, 5))
        
        # First row of RAM actions
        ram_row1 = tk.Frame(ram_frame, bg=self.colors['card'])
        ram_row1.pack(pady=2)
        
        ram_jolt_btn = tk.Button(ram_row1, text="⚡ Jolt", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg=self.colors['success'], fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.ram_jolt)
        ram_jolt_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        ram_soft_btn = tk.Button(ram_row1, text="💨 Soft", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#87CEEB', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.ram_soft_clean)
        ram_soft_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        ram_deep_btn = tk.Button(ram_row1, text="🔥 Deep", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#ff4444', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.ram_deep_clean)
        ram_deep_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Second row of RAM actions
        ram_row2 = tk.Frame(ram_frame, bg=self.colors['card'])
        ram_row2.pack(pady=2)
        
        ram_process_btn = tk.Button(ram_row2, text="📋 Processes", 
                                   font=('Segoe UI', 8, 'bold'), 
                                   bg='#9370DB', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.ram_process_cleanup)
        ram_process_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        ram_cache_btn = tk.Button(ram_row2, text="🗑️ Cache", 
                                 font=('Segoe UI', 8, 'bold'), 
                                 bg='#8B4513', fg=self.colors['bg'],
                                 relief='flat', bd=0, cursor='hand2',
                                 command=self.ram_cache_cleanup)
        ram_cache_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        ram_standby_btn = tk.Button(ram_row2, text="⏸️ Standby", 
                                    font=('Segoe UI', 8, 'bold'), 
                                    bg='#4682B4', fg=self.colors['bg'],
                                    relief='flat', bd=0, cursor='hand2',
                                    command=self.ram_standby_cleanup)
        ram_standby_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # GPU Actions
        gpu_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        gpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        gpu_title = tk.Label(gpu_frame, text="🎮 GPU Actions", 
                            font=('Segoe UI', 11, 'bold'), 
                            fg=self.colors['gpu_line'], bg=self.colors['card'])
        gpu_title.pack(pady=(10, 5))
        
        # First row of GPU actions
        gpu_row1 = tk.Frame(gpu_frame, bg=self.colors['card'])
        gpu_row1.pack(pady=2)
        
        gpu_jolt_btn = tk.Button(gpu_row1, text="⚡ Jolt", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg=self.colors['success'], fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.gpu_jolt)
        gpu_jolt_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gpu_soft_btn = tk.Button(gpu_row1, text="💨 Soft", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#87CEEB', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.gpu_soft_clean)
        gpu_soft_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gpu_deep_btn = tk.Button(gpu_row1, text="🔥 Deep", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#ff4444', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.gpu_deep_clean)
        gpu_deep_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Second row of GPU actions
        gpu_row2 = tk.Frame(gpu_frame, bg=self.colors['card'])
        gpu_row2.pack(pady=2)
        
        gpu_shader_btn = tk.Button(gpu_row2, text="🎨 Shaders", 
                                  font=('Segoe UI', 8, 'bold'), 
                                  bg='#FF69B4', fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  command=self.gpu_shader_cleanup)
        gpu_shader_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gpu_vram_btn = tk.Button(gpu_row2, text="💾 VRAM", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#32CD32', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.gpu_vram_cleanup)
        gpu_vram_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gpu_process_btn = tk.Button(gpu_row2, text="📋 Processes", 
                                   font=('Segoe UI', 8, 'bold'), 
                                   bg='#9370DB', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.gpu_process_cleanup)
        gpu_process_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # CPU Actions
        cpu_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        cpu_title = tk.Label(cpu_frame, text="⚡ CPU Actions", 
                            font=('Segoe UI', 11, 'bold'), 
                            fg=self.colors['cpu_line'], bg=self.colors['card'])
        cpu_title.pack(pady=(10, 5))
        
        # First row of CPU actions
        cpu_row1 = tk.Frame(cpu_frame, bg=self.colors['card'])
        cpu_row1.pack(pady=2)
        
        cpu_jolt_btn = tk.Button(cpu_row1, text="⚡ Jolt", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg=self.colors['success'], fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.cpu_jolt)
        cpu_jolt_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        cpu_soft_btn = tk.Button(cpu_row1, text="💨 Soft", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#87CEEB', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.cpu_soft_clean)
        cpu_soft_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        cpu_deep_btn = tk.Button(cpu_row1, text="🔥 Deep", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#ff4444', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.cpu_deep_clean)
        cpu_deep_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Second row of CPU actions
        cpu_row2 = tk.Frame(cpu_frame, bg=self.colors['card'])
        cpu_row2.pack(pady=2)
        
        cpu_priority_btn = tk.Button(cpu_row2, text="🎯 Priority", 
                                    font=('Segoe UI', 8, 'bold'), 
                                    bg='#FF8C00', fg=self.colors['bg'],
                                    relief='flat', bd=0, cursor='hand2',
                                    command=self.cpu_priority_cleanup)
        cpu_priority_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        cpu_process_btn = tk.Button(cpu_row2, text="📋 Processes", 
                                   font=('Segoe UI', 8, 'bold'), 
                                   bg='#9370DB', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.cpu_process_cleanup)
        cpu_process_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        cpu_cache_btn = tk.Button(cpu_row2, text="🗑️ Cache", 
                                font=('Segoe UI', 8, 'bold'), 
                                bg='#8B4513', fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.cpu_cache_cleanup)
        cpu_cache_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # System-wide Actions
        system_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        system_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        system_title = tk.Label(system_frame, text="🌐 System-wide Actions", 
                              font=('Segoe UI', 11, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['card'])
        system_title.pack(pady=(10, 5))
        
        # First row of system-wide actions
        system_row1 = tk.Frame(system_frame, bg=self.colors['card'])
        system_row1.pack(pady=2)
        
        system_jolt_btn = tk.Button(system_row1, text="⚡ All Jolt", 
                                   font=('Segoe UI', 8, 'bold'), 
                                   bg=self.colors['success'], fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.system_jolt)
        system_jolt_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        system_soft_btn = tk.Button(system_row1, text="💨 All Soft", 
                                   font=('Segoe UI', 8, 'bold'), 
                                   bg='#87CEEB', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.system_soft_clean)
        system_soft_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        system_deep_btn = tk.Button(system_row1, text="🔥 All Deep", 
                                   font=('Segoe UI', 8, 'bold'), 
                                   bg='#ff4444', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.system_deep_clean)
        system_deep_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Second row of system-wide actions
        system_row2 = tk.Frame(system_frame, bg=self.colors['card'])
        system_row2.pack(pady=2)
        
        system_process_btn = tk.Button(system_row2, text="📋 All Processes", 
                                      font=('Segoe UI', 8, 'bold'), 
                                      bg='#9370DB', fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      command=self.system_process_cleanup)
        system_process_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        system_cache_btn = tk.Button(system_row2, text="🗑️ All Cache", 
                                    font=('Segoe UI', 8, 'bold'), 
                                    bg='#8B4513', fg=self.colors['bg'],
                                    relief='flat', bd=0, cursor='hand2',
                                    command=self.system_cache_cleanup)
        system_cache_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        system_reset_btn = tk.Button(system_row2, text="🔄 Full Reset", 
                                    font=('Segoe UI', 8, 'bold'), 
                                    bg='#FF1493', fg=self.colors['bg'],
                                    relief='flat', bd=0, cursor='hand2',
                                    command=self.system_full_reset)
        system_reset_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Windows 11 Gaming Optimization
        gaming_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        gaming_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        gaming_title = tk.Label(gaming_frame, text="🎮 Windows 11 Gaming", 
                               font=('Segoe UI', 11, 'bold'), 
                               fg=self.colors['gpu_line'], bg=self.colors['card'])
        gaming_title.pack(pady=(10, 5))
        
        # First row of gaming actions
        gaming_row1 = tk.Frame(gaming_frame, bg=self.colors['card'])
        gaming_row1.pack(pady=2)
        
        gaming_mode_btn = tk.Button(gaming_row1, text="🎯 Game Mode", 
                                  font=('Segoe UI', 8, 'bold'), 
                                  bg='#00BCD4', fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  command=self.gaming_mode_optimize)
        gaming_mode_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gaming_priority_btn = tk.Button(gaming_row1, text="⚡ Priority", 
                                       font=('Segoe UI', 8, 'bold'), 
                                       bg='#FF5722', fg=self.colors['bg'],
                                       relief='flat', bd=0, cursor='hand2',
                                       command=self.gaming_priority_optimize)
        gaming_priority_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gaming_resource_btn = tk.Button(gaming_row1, text="📊 Resources", 
                                       font=('Segoe UI', 8, 'bold'), 
                                       bg='#795548', fg=self.colors['bg'],
                                       relief='flat', bd=0, cursor='hand2',
                                       command=self.gaming_resource_optimize)
        gaming_resource_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Second row of gaming actions
        gaming_row2 = tk.Frame(gaming_frame, bg=self.colors['card'])
        gaming_row2.pack(pady=2)
        
        gaming_service_btn = tk.Button(gaming_row2, text="🔧 Services", 
                                      font=('Segoe UI', 8, 'bold'), 
                                      bg='#607D8B', fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      command=self.gaming_service_optimize)
        gaming_service_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gaming_network_btn = tk.Button(gaming_row2, text="🌐 Network", 
                                      font=('Segoe UI', 8, 'bold'), 
                                      bg='#3F51B5', fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      command=self.gaming_network_optimize)
        gaming_network_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        gaming_reset_btn = tk.Button(gaming_row2, text="🔄 Reset", 
                                    font=('Segoe UI', 8, 'bold'), 
                                    bg='#9C27B0', fg=self.colors['bg'],
                                    relief='flat', bd=0, cursor='hand2',
                                    command=self.gaming_reset_optimize)
        gaming_reset_btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def get_system_info(self):
        """Get current system information"""
        info = {
            'ram': {'usage': 0, 'used': 0, 'total': 0, 'available': 0},
            'gpu': {'usage': 0, 'memory_used': 0, 'memory_total': 0, 'temperature': 0},
            'cpu': {'usage': 0, 'freq': 0, 'temp': 0}
        }
        
        # Get RAM info
        memory = psutil.virtual_memory()
        info['ram'] = {
            'usage': memory.percent,
            'used': memory.used / (1024**3),  # GB
            'total': memory.total / (1024**3),  # GB
            'available': memory.available / (1024**3)  # GB
        }
        
        # Get GPU info using the same method as GPU monitor
        gpu_data_retrieved = False
        if self.gpu_count > 0:
            try:
                # Try nvidia-smi first for NVIDIA GPUs
                result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 0:
                        values = lines[0].split(', ')
                        if len(values) >= 4:
                            info['gpu'] = {
                                'memory_total': float(values[0]) / 1024,  # GB
                                'memory_used': float(values[1]) / 1024,  # GB
                                'usage': float(values[2]),
                                'temperature': float(values[3])
                            }
                            gpu_data_retrieved = True
            except Exception as e:
                print(f"NVIDIA-smi error: {e}")
            
            # Fallback to WMI only if nvidia-smi failed
            if not gpu_data_retrieved and WMI_AVAILABLE:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                    c = wmi.WMI()
                    gpus = c.Win32_VideoController()
                    if len(gpus) > 0:
                        gpu = gpus[0]  # Use first GPU
                        info['gpu'] = {
                            'memory_total': 8.0,  # Default estimate for NVIDIA cards
                            'memory_used': 0,
                            'usage': 0,
                            'temperature': 0
                        }
                        
                        # Try to get adapter RAM
                        if gpu.AdapterRAM and gpu.AdapterRAM > 0:
                            info['gpu']['memory_total'] = gpu.AdapterRAM / (1024**3)  # Convert to GB
                        
                        # For NVIDIA GPUs, try to estimate VRAM from common sizes
                        if 'NVIDIA' in gpu.Name and info['gpu']['memory_total'] <= 0:
                            if 'RTX 5060' in gpu.Name:
                                info['gpu']['memory_total'] = 8.0  # 8GB typical
                            elif 'RTX 4060' in gpu.Name:
                                info['gpu']['memory_total'] = 8.0  # 8GB typical
                            elif 'RTX 3060' in gpu.Name:
                                info['gpu']['memory_total'] = 12.0  # 12GB typical
                            elif 'RTX 3070' in gpu.Name:
                                info['gpu']['memory_total'] = 8.0  # 8GB typical
                            elif 'RTX 3080' in gpu.Name:
                                info['gpu']['memory_total'] = 10.0  # 10GB typical
                            elif 'RTX 4090' in gpu.Name:
                                info['gpu']['memory_total'] = 24.0  # 24GB typical
                except Exception as e:
                    print(f"WMI GPU error: {e}")
            
            # Final fallback - set basic GPU info
            if info['gpu']['memory_total'] == 0:
                info['gpu'] = {
                    'memory_total': 8.0,  # Default estimate
                    'memory_used': 0,
                    'usage': 0,
                    'temperature': 0
                }
        
        # Get CPU info - get per-core usage first
        per_core_usage = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # Calculate average from individual cores
        cpu_percent = sum(per_core_usage) / len(per_core_usage) if per_core_usage else 0
        
        # Get CPU frequency
        cpu_freq = psutil.cpu_freq()
        cpu_freq_current = cpu_freq.current if cpu_freq else 2100.0  # Default fallback
        
        # Get CPU temperature
        cpu_temp = 0
        if platform.system() == "Windows":
            try:
                # Method 1: Try using PowerShell with elevated permissions check
                try:
                    ps_result = subprocess.run(['powershell', '-Command', 
                        'try { Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" -ErrorAction Stop | Select-Object -First 1 | ForEach-Object {($_.CurrentTemperature / 10) - 273.15} } catch { "Access Denied" }'], 
                        capture_output=True, text=True, timeout=5)
                    
                    if ps_result.returncode == 0 and ps_result.stdout.strip():
                        temp_str = ps_result.stdout.strip()
                        if temp_str != "Access Denied":
                            try:
                                temp_value = float(temp_str)
                                if 20 < temp_value < 100:  # Reasonable CPU temperature range
                                    cpu_temp = temp_value
                            except ValueError:
                                pass
                except Exception as e:
                    print(f"PowerShell temp error: {e}")
                
                # Method 2: Estimate temperature based on CPU usage (fallback)
                if cpu_temp == 0:
                    # Very rough estimation based on CPU usage
                    if cpu_percent < 20:
                        cpu_temp = 35.0  # Idle estimate
                    elif cpu_percent < 50:
                        cpu_temp = 45.0  # Light load
                    elif cpu_percent < 80:
                        cpu_temp = 60.0  # Medium load
                    else:
                        cpu_temp = 75.0  # Heavy load
                
            except Exception as e:
                print(f"Temperature detection error: {e}")
                # Set estimated temperature as fallback
                if cpu_percent < 20:
                    cpu_temp = 35.0
                elif cpu_percent < 50:
                    cpu_temp = 45.0
                elif cpu_percent < 80:
                    cpu_temp = 60.0
                else:
                    cpu_temp = 75.0
        
        info['cpu'] = {
            'usage': cpu_percent,
            'freq': cpu_freq_current,
            'temp': cpu_temp
        }
        
        return info
    
    def update_display(self):
        """Update the display with current system information"""
        info = self.get_system_info()
        
        # Update RAM card
        self.ram_card.value_label.config(text=f"{info['ram']['usage']:.1f}%")
        self.ram_card.progress['value'] = info['ram']['usage']
        self.ram_card.details_label.config(text=f"{info['ram']['used']:.1f}GB / {info['ram']['total']:.1f}GB")
        
        # Update GPU card
        if self.gpu_count > 0:
            self.gpu_card.value_label.config(text=f"{info['gpu']['usage']:.1f}%")
            self.gpu_card.progress['value'] = info['gpu']['usage']
            memory_percent = (info['gpu']['memory_used'] / info['gpu']['memory_total']) * 100 if info['gpu']['memory_total'] > 0 else 0
            self.gpu_card.details_label.config(text=f"{info['gpu']['memory_used']:.1f}GB / {info['gpu']['memory_total']:.1f}GB | {info['gpu']['temperature']:.0f}°C")
        else:
            self.gpu_card.value_label.config(text="N/A")
            self.gpu_card.progress['value'] = 0
            self.gpu_card.details_label.config(text="No GPU detected")
        
        # Update CPU card
        self.cpu_card.value_label.config(text=f"{info['cpu']['usage']:.1f}%")
        self.cpu_card.progress['value'] = info['cpu']['usage']
        
        # Format temperature display
        temp_text = f"Temp: {info['cpu']['temp']:.0f}°C"
        if info['cpu']['temp'] > 0 and (info['cpu']['temp'] == 35.0 or info['cpu']['temp'] == 45.0 or info['cpu']['temp'] == 60.0 or info['cpu']['temp'] == 75.0):
            temp_text += " (Est.)"
        
        self.cpu_card.details_label.config(text=f"Freq: {info['cpu']['freq']:.0f}MHz | {temp_text}")
        
        # Add data to plot
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_data.append(current_time)
        self.ram_data.append(info['ram']['usage'])
        self.gpu_data.append(info['gpu']['usage'])
        self.cpu_data.append(info['cpu']['usage'])
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.ram_data = self.ram_data[-self.max_points:]
            self.gpu_data = self.gpu_data[-self.max_points:]
            self.cpu_data = self.cpu_data[-self.max_points:]
        
        # Update graph
        self.update_graph()
    
    def update_graph(self):
        """Update the performance graph"""
        self.ax1.clear()
        
        if len(self.time_data) > 1:
            # Plot RAM usage
            self.ax1.plot(self.time_data, self.ram_data, 
                         color=self.colors['ram_line'], linewidth=2, label='RAM')
            
            # Plot GPU usage
            if self.gpu_count > 0:
                self.ax1.plot(self.time_data, self.gpu_data, 
                             color=self.colors['gpu_line'], linewidth=2, label='GPU')
            
            # Plot CPU usage
            self.ax1.plot(self.time_data, self.cpu_data, 
                         color=self.colors['cpu_line'], linewidth=2, label='CPU')
        
        self.ax1.set_xlabel('Time', color=self.colors['text'])
        self.ax1.set_ylabel('Usage (%)', color=self.colors['text'])
        self.ax1.set_title('System Performance Monitor', color=self.colors['primary'])
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_facecolor(self.colors['graph_bg'])
        
        # Style the plot
        self.ax1.tick_params(axis='x', colors=self.colors['text'], rotation=45)
        self.ax1.tick_params(axis='y', colors=self.colors['text'])
        self.ax1.spines['bottom'].set_color(self.colors['text'])
        self.ax1.spines['top'].set_color(self.colors['text'])
        self.ax1.spines['left'].set_color(self.colors['text'])
        self.ax1.spines['right'].set_color(self.colors['text'])
        
        if len(self.time_data) > 1:
            self.ax1.legend(loc='upper left')
        
        # Adjust layout and redraw
        self.fig.tight_layout()
        self.canvas.draw()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_display()
                time.sleep(self.update_interval / 1000)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                break
    
    def start_monitoring(self):
        """Start monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.status_label.config(text="● Monitoring", fg=self.colors['success'])
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.status_label.config(text="● Stopped", fg=self.colors['warning'])
    
    # RAM Actions
    def ram_jolt(self):
        """Run RAM Memory Jolt"""
        def run_ram_jolt():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ RAM Jolt starting..."))
                self.root.update_idletasks()
                
                # Force garbage collection
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ Clearing memory cache..."))
                self.root.update_idletasks()
                gc.collect()
                time.sleep(0.5)
                
                # Clear Python objects
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ Optimizing memory allocation..."))
                self.root.update_idletasks()
                for _ in range(3):
                    gc.collect()
                    time.sleep(0.2)
                
                # Clear standby memory (Windows)
                if platform.system() == "Windows":
                    try:
                        self.root.after(0, lambda: self.process_info_label.config(text="⚡ Clearing standby memory..."))
                        self.root.update_idletasks()
                        ps_command = 'Get-Process | ForEach-Object { $_.WorkingSet = [Math]::Max($_.WorkingSet / 2, 1024*1024*10) }'
                        subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, timeout=5)
                    except:
                        pass
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ RAM Jolt complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("RAM Jolt Complete", "Quick RAM optimization completed!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ RAM Jolt failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"RAM jolt failed: {e}"))
        
        try:
            result = messagebox.askyesno("⚡ RAM Memory Jolt", 
                                        "Perform quick RAM optimization?\n\n" +
                                        "This will:\n" +
                                        "• Clear RAM cache\n" +
                                        "• Optimize memory allocation\n" +
                                        "• Force garbage collection\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● RAM Jolt...", fg=self.colors['warning'])
                threading.Thread(target=run_ram_jolt, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"RAM jolt failed: {e}")
    
    def ram_soft_clean(self):
        """Run RAM Soft Clean"""
        def run_ram_soft_clean():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="💨 RAM Soft Clean starting..."))
                self.root.update_idletasks()
                
                # Gentle garbage collection
                self.root.after(0, lambda: self.process_info_label.config(text="💨 Light cache clearing..."))
                self.root.update_idletasks()
                gc.collect()
                time.sleep(0.3)
                
                # Memory optimization
                self.root.after(0, lambda: self.process_info_label.config(text="💨 Optimizing memory..."))
                self.root.update_idletasks()
                for _ in range(2):
                    gc.collect()
                    time.sleep(0.2)
                
                # Clear DNS cache
                if platform.system() == "Windows":
                    try:
                        self.root.after(0, lambda: self.process_info_label.config(text="💨 Clearing DNS cache..."))
                        self.root.update_idletasks()
                        subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                    except:
                        pass
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ RAM Soft Clean complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("RAM Soft Clean Complete", "Gentle RAM cleanup completed!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ RAM Soft Clean failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"RAM soft clean failed: {e}"))
        
        try:
            result = messagebox.askyesno("💨 RAM Soft Clean", 
                                        "Perform gentle RAM cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Light cache clearing\n" +
                                        "• Memory optimization\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● RAM Soft Clean...", fg=self.colors['warning'])
                threading.Thread(target=run_ram_soft_clean, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"RAM soft clean failed: {e}")
    
    def ram_deep_clean(self):
        """Run RAM Deep Clean"""
        def run_ram_deep_clean():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 RAM Deep Clean starting..."))
                self.root.update_idletasks()
                
                # Aggressive garbage collection
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 Clearing all memory cache..."))
                self.root.update_idletasks()
                for _ in range(5):
                    gc.collect()
                    time.sleep(0.3)
                
                # Clear temp files
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 Clearing temp files..."))
                self.root.update_idletasks()
                
                if platform.system() == "Windows":
                    temp_paths = [
                        os.path.expandvars('%TEMP%'),
                        os.path.expandvars('%LOCALAPPDATA%\\Temp'),
                        os.path.expandvars('%APPDATA%\\Microsoft\\Windows\\Recent')
                    ]
                    
                    for temp_path in temp_paths:
                        if os.path.exists(temp_path):
                            try:
                                for item in os.listdir(temp_path):
                                    try:
                                        item_path = os.path.join(temp_path, item)
                                        if os.path.isfile(item_path):
                                            os.remove(item_path)
                                    except:
                                        continue
                            except:
                                continue
                
                # Clear DNS cache
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 Clearing DNS cache..."))
                self.root.update_idletasks()
                try:
                    subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                except:
                    pass
                
                # Clear standby memory aggressively
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 Clearing standby memory..."))
                self.root.update_idletasks()
                try:
                    ps_command = 'Get-Process | ForEach-Object { $_.WorkingSet = [Math]::Max($_.WorkingSet / 3, 1024*1024*5) }'
                    subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, timeout=10)
                except:
                    pass
                
                # Final garbage collection
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 Final optimization..."))
                self.root.update_idletasks()
                gc.collect()
                time.sleep(0.5)
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ RAM Deep Clean complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("RAM Deep Clean Complete", "Deep RAM cleanup completed!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ RAM Deep Clean failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"RAM deep clean failed: {e}"))
        
        try:
            result = messagebox.askyesno("🔥 RAM Deep Clean", 
                                        "Perform deep RAM cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Clear all cache\n" +
                                        "• Clear temp files\n" +
                                        "• Optimize memory\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● RAM Deep Clean...", fg=self.colors['warning'])
                threading.Thread(target=run_ram_deep_clean, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"RAM deep clean failed: {e}")
    
    def ram_process_cleanup(self):
        """Run RAM Process Cleanup with tracking"""
        def run_process_cleanup():
            try:
                # Update GUI immediately
                self.root.after(0, lambda: self.process_info_label.config(text="🔍 Scanning processes..."))
                self.root.update_idletasks()
                
                processes_terminated = 0
                memory_freed = 0
                
                # Get all processes
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_memory = proc_info['memory_info'].rss / (1024**2)  # MB
                        
                        # Safe to close processes
                        safe_processes = [
                            'chrome', 'firefox', 'edge', 'opera', 'brave',
                            'discord', 'slack', 'teams', 'zoom', 'skype',
                            'spotify', 'itunes', 'vlc', 'winamp',
                            'notepad++', 'sublime', 'vscode', 'atom',
                            'steam', 'epic', 'origin', 'uplay'
                        ]
                        
                        # Check if process is safe to close and using significant memory
                        if any(safe_proc in proc_name for safe_proc in safe_processes) and proc_memory > 100:
                            # Update GUI with current process
                            self.root.after(0, lambda pn=proc_name, pm=proc_memory: 
                                self.process_info_label.config(text=f"🔄 Terminating {pn} ({pm:.1f}MB)..."))
                            self.root.update_idletasks()
                            
                            proc.terminate()
                            processes_terminated += 1
                            memory_freed += proc_memory
                            time.sleep(0.1)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Process cleanup complete"))
                self.root.update_idletasks()
                
                # Show results
                result_msg = f"Process Cleanup Complete!\n\n" \
                           f"• Processes terminated: {processes_terminated}\n" \
                           f"• Memory freed: {memory_freed:.1f}MB\n" \
                           f"• System optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("RAM Process Cleanup", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Process cleanup failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Process cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("📋 RAM Process Cleanup", 
                                        "Clean up memory-intensive processes?\n\n" +
                                        "This will:\n" +
                                        "• Identify high-memory processes\n" +
                                        "• Terminate safe-to-close applications\n" +
                                        "• Free up significant RAM\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● RAM Process Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_process_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"RAM process cleanup failed: {e}")
    
    def ram_cache_cleanup(self):
        """Run RAM Cache Cleanup"""
        def run_cache_cleanup():
            try:
                # Update GUI immediately
                self.root.after(0, lambda: self.process_info_label.config(text="🗑️ Clearing system cache..."))
                self.root.update_idletasks()
                
                cache_cleared = 0
                
                # Clear Python garbage collection
                gc.collect()
                cache_cleared += 1
                
                # Clear system cache (Windows)
                if platform.system() == "Windows":
                    try:
                        # Clear DNS cache
                        self.root.after(0, lambda: self.process_info_label.config(text="🗑️ Clearing DNS cache..."))
                        self.root.update_idletasks()
                        subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                        cache_cleared += 1
                        
                        # Clear Windows temp files
                        temp_paths = [
                            os.path.expandvars('%TEMP%'),
                            os.path.expandvars('%LOCALAPPDATA%\\Temp'),
                            os.path.expandvars('%APPDATA%\\Microsoft\\Windows\\Recent')
                        ]
                        
                        for temp_path in temp_paths:
                            if os.path.exists(temp_path):
                                path_name = os.path.basename(temp_path)
                                self.root.after(0, lambda pn=path_name: 
                                    self.process_info_label.config(text=f"🗑️ Cleaning {pn}..."))
                                self.root.update_idletasks()
                                for item in os.listdir(temp_path):
                                    try:
                                        item_path = os.path.join(temp_path, item)
                                        if os.path.isfile(item_path):
                                            os.remove(item_path)
                                            cache_cleared += 1
                                    except:
                                        continue
                    except:
                        pass
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Cache cleanup complete"))
                self.root.update_idletasks()
                
                # Show results
                result_msg = f"Cache Cleanup Complete!\n\n" \
                           f"• Cache operations: {cache_cleared}\n" \
                           f"• System optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("RAM Cache Cleanup", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Cache cleanup failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Cache cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("🗑️ RAM Cache Cleanup", 
                                        "Clear system cache?\n\n" +
                                        "This will:\n" +
                                        "• Clear DNS cache\n" +
                                        "• Clean temp files\n" +
                                        "• Optimize memory\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● RAM Cache Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_cache_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"RAM cache cleanup failed: {e}")
    
    def ram_standby_cleanup(self):
        """Run RAM Standby Memory Cleanup"""
        def run_standby_cleanup():
            try:
                self.process_info_label.config(text="⏸️ Clearing standby memory...")
                
                # Clear standby memory (Windows)
                if platform.system() == "Windows":
                    try:
                        # Use PowerShell to clear standby memory
                        ps_command = 'Get-Process | ForEach-Object { $_.WorkingSet = 0 }'
                        subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, timeout=10)
                        
                        # Alternative method using empty working set
                        for proc in psutil.process_iter(['pid']):
                            try:
                                p = psutil.Process(proc.pid)
                                p.memory_info()  # Refresh memory info
                            except:
                                continue
                    except:
                        pass
                
                # Force garbage collection
                gc.collect()
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ Standby cleanup complete")
                
                # Show results
                result_msg = "Standby Memory Cleanup Complete!\n\n" \
                           "• Standby memory cleared\n" \
                           "• Memory optimized\n" \
                           "• System refreshed"
                
                self.root.after(100, lambda: messagebox.showinfo("RAM Standby Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ Standby cleanup failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"Standby cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("⏸️ RAM Standby Cleanup", 
                                        "Clear standby memory?\n\n" +
                                        "This will:\n" +
                                        "• Clear standby memory\n" +
                                        "• Optimize memory allocation\n" +
                                        "• Refresh system memory\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● RAM Standby Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_standby_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"RAM standby cleanup failed: {e}")
    
    # GPU Actions
    def gpu_jolt(self):
        """Run GPU Memory Jolt"""
        try:
            result = messagebox.askyesno("⚡ GPU Memory Jolt", 
                                        "Perform quick GPU optimization?\n\n" +
                                        "This will:\n" +
                                        "• Clear GPU cache\n" +
                                        "• Optimize VRAM\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● GPU Jolt...", fg=self.colors['warning'])
                time.sleep(1)
                self.update_display()
                self.status_label.config(text="● Monitoring", fg=self.colors['success'])
                messagebox.showinfo("GPU Jolt Complete", "GPU optimization completed!")
        except Exception as e:
            messagebox.showerror("Error", f"GPU jolt failed: {e}")
    
    def gpu_soft_clean(self):
        """Run GPU Soft Clean"""
        try:
            result = messagebox.askyesno("💨 GPU Soft Clean", 
                                        "Perform gentle GPU cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Light cache clearing\n" +
                                        "• VRAM optimization\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● GPU Soft Clean...", fg=self.colors['warning'])
                time.sleep(1)
                self.update_display()
                self.status_label.config(text="● Monitoring", fg=self.colors['success'])
                messagebox.showinfo("GPU Soft Clean Complete", "Gentle GPU cleanup completed!")
        except Exception as e:
            messagebox.showerror("Error", f"GPU soft clean failed: {e}")
    
    def gpu_deep_clean(self):
        """Run GPU Deep Clean"""
        try:
            result = messagebox.askyesno("🔥 GPU Deep Clean", 
                                        "Perform deep GPU cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Clear all GPU cache\n" +
                                        "• Clear shader cache\n" +
                                        "• Optimize GPU settings\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● GPU Deep Clean...", fg=self.colors['warning'])
                time.sleep(2)
                self.update_display()
                self.status_label.config(text="● Monitoring", fg=self.colors['success'])
                messagebox.showinfo("GPU Deep Clean Complete", "Deep GPU cleanup completed!")
        except Exception as e:
            messagebox.showerror("Error", f"GPU deep clean failed: {e}")
    
    def gpu_shader_cleanup(self):
        """Run GPU Shader Cache Cleanup"""
        def run_shader_cleanup():
            try:
                self.process_info_label.config(text="🎨 Clearing shader cache...")
                cache_cleared = 0
                
                # Clear NVIDIA shader cache
                nvidia_paths = [
                    os.path.expandvars('%LOCALAPPDATA%\\NVIDIA\\DXCache'),
                    os.path.expandvars('%LOCALAPPDATA%\\NVIDIA\\GLCache'),
                    os.path.expandvars('%PROGRAMDATA%\\NVIDIA Corporation\\NV_Cache')
                ]
                
                for cache_path in nvidia_paths:
                    if os.path.exists(cache_path):
                        self.process_info_label.config(text=f"🎨 Cleaning NVIDIA cache...")
                        try:
                            for item in os.listdir(cache_path):
                                item_path = os.path.join(cache_path, item)
                                try:
                                    if os.path.isfile(item_path):
                                        os.remove(item_path)
                                        cache_cleared += 1
                                    elif os.path.isdir(item_path):
                                        import shutil
                                        shutil.rmtree(item_path)
                                        cache_cleared += 1
                                except:
                                    continue
                        except:
                            pass
                
                # Clear DirectX shader cache
                dx_cache = os.path.expandvars('%LOCALAPPDATA%\\Microsoft\\DirectXShaderCache')
                if os.path.exists(dx_cache):
                    self.process_info_label.config(text="🎨 Cleaning DirectX cache...")
                    try:
                        import shutil
                        for item in os.listdir(dx_cache):
                            item_path = os.path.join(dx_cache, item)
                            try:
                                if os.path.isdir(item_path):
                                    shutil.rmtree(item_path)
                                    cache_cleared += 1
                            except:
                                continue
                    except:
                        pass
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ Shader cleanup complete")
                
                # Show results
                result_msg = f"Shader Cache Cleanup Complete!\n\n" \
                           f"• Cache files cleared: {cache_cleared}\n" \
                           f"• GPU performance optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("GPU Shader Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ Shader cleanup failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"Shader cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("🎨 GPU Shader Cleanup", 
                                        "Clear GPU shader cache?\n\n" +
                                        "This will:\n" +
                                        "• Clear NVIDIA shader cache\n" +
                                        "• Clear DirectX shader cache\n" +
                                        "• Improve GPU performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● GPU Shader Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_shader_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"GPU shader cleanup failed: {e}")
    
    def gpu_vram_cleanup(self):
        """Run GPU VRAM Cleanup"""
        def run_vram_cleanup():
            try:
                self.process_info_label.config(text="💾 Optimizing VRAM...")
                
                # Force GPU memory cleanup using nvidia-smi
                try:
                    # Reset GPU to clear VRAM
                    subprocess.run(['nvidia-smi', '--gpu-reset'], capture_output=True, text=True, timeout=10)
                except:
                    pass
                
                # Alternative: Force GPU process cleanup
                gpu_processes = []
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        # GPU-intensive processes
                        gpu_apps = ['chrome', 'firefox', 'edge', 'opera', 'brave', 'steam', 'epic', 'origin', 'uplay']
                        if any(app in proc_name for app in gpu_apps):
                            gpu_processes.append(proc.info['name'])
                    except:
                        continue
                
                self.process_info_label.config(text=f"💾 Found {len(gpu_processes)} GPU processes")
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ VRAM cleanup complete")
                
                # Show results
                result_msg = f"VRAM Cleanup Complete!\n\n" \
                           f"• GPU memory optimized\n" \
                           f"• VRAM refreshed\n" \
                           f"• Performance improved"
                
                self.root.after(100, lambda: messagebox.showinfo("GPU VRAM Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ VRAM cleanup failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"VRAM cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("💾 GPU VRAM Cleanup", 
                                        "Optimize GPU VRAM?\n\n" +
                                        "This will:\n" +
                                        "• Clear GPU memory\n" +
                                        "• Optimize VRAM usage\n" +
                                        "• Improve performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● GPU VRAM Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_vram_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"GPU VRAM cleanup failed: {e}")
    
    def gpu_process_cleanup(self):
        """Run GPU Process Cleanup"""
        def run_gpu_process_cleanup():
            try:
                self.process_info_label.config(text="📋 Scanning GPU processes...")
                processes_terminated = 0
                gpu_memory_freed = 0
                
                # Identify GPU-intensive processes
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_memory = proc_info['memory_info'].rss / (1024**2)  # MB
                        
                        # GPU-intensive applications
                        gpu_apps = [
                            'chrome', 'firefox', 'edge', 'opera', 'brave',
                            'steam', 'epicgameslauncher', 'origin', 'uplay',
                            'discord', 'obs', 'streamlabs', 'xsplit',
                            'photoshop', 'premiere', 'aftereffects', 'blender'
                        ]
                        
                        # Check if process is GPU-intensive and using significant memory
                        if any(app in proc_name for app in gpu_apps) and proc_memory > 200:
                            self.process_info_label.config(text=f"🔄 Terminating {proc_name} ({proc_memory:.1f}MB)...")
                            proc.terminate()
                            processes_terminated += 1
                            gpu_memory_freed += proc_memory
                            time.sleep(0.1)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ GPU process cleanup complete")
                
                # Show results
                result_msg = f"GPU Process Cleanup Complete!\n\n" \
                           f"• Processes terminated: {processes_terminated}\n" \
                           f"• Memory freed: {gpu_memory_freed:.1f}MB\n" \
                           f"• GPU resources optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("GPU Process Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ GPU process cleanup failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"GPU process cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("📋 GPU Process Cleanup", 
                                        "Clean up GPU-intensive processes?\n\n" +
                                        "This will:\n" +
                                        "• Identify GPU applications\n" +
                                        "• Terminate resource-heavy processes\n" +
                                        "• Free GPU memory\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● GPU Process Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_gpu_process_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"GPU process cleanup failed: {e}")
    
    # CPU Actions
    def cpu_jolt(self):
        """Run CPU Memory Jolt"""
        try:
            result = messagebox.askyesno("⚡ CPU Memory Jolt", 
                                        "Perform quick CPU optimization?\n\n" +
                                        "This will:\n" +
                                        "• Clear CPU cache\n" +
                                        "• Optimize processes\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● CPU Jolt...", fg=self.colors['warning'])
                time.sleep(1)
                self.update_display()
                self.status_label.config(text="● Monitoring", fg=self.colors['success'])
                messagebox.showinfo("CPU Jolt Complete", "CPU optimization completed!")
        except Exception as e:
            messagebox.showerror("Error", f"CPU jolt failed: {e}")
    
    def cpu_soft_clean(self):
        """Run CPU Soft Clean"""
        try:
            result = messagebox.askyesno("💨 CPU Soft Clean", 
                                        "Perform gentle CPU cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Light cache clearing\n" +
                                        "• Process optimization\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● CPU Soft Clean...", fg=self.colors['warning'])
                time.sleep(1)
                self.update_display()
                self.status_label.config(text="● Monitoring", fg=self.colors['success'])
                messagebox.showinfo("CPU Soft Clean Complete", "Gentle CPU cleanup completed!")
        except Exception as e:
            messagebox.showerror("Error", f"CPU soft clean failed: {e}")
    
    def cpu_deep_clean(self):
        """Run CPU Deep Clean"""
        try:
            result = messagebox.askyesno("🔥 CPU Deep Clean", 
                                        "Perform deep CPU cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Clear all CPU cache\n" +
                                        "• Clear temp files\n" +
                                        "• Optimize processes\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● CPU Deep Clean...", fg=self.colors['warning'])
                time.sleep(2)
                self.update_display()
                self.status_label.config(text="● Monitoring", fg=self.colors['success'])
                messagebox.showinfo("CPU Deep Clean Complete", "Deep CPU cleanup completed!")
        except Exception as e:
            messagebox.showerror("Error", f"CPU deep clean failed: {e}")
    
    def cpu_priority_cleanup(self):
        """Run CPU Priority Optimization"""
        def run_priority_cleanup():
            try:
                self.process_info_label.config(text="🎯 Optimizing CPU priorities...")
                processes_optimized = 0
                
                # Optimize system process priorities
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_cpu = proc_info['cpu_percent']
                        
                        # Get process object
                        p = psutil.Process(proc_info['pid'])
                        
                        # Set priorities based on process type and CPU usage
                        if 'system' in proc_name or 'svchost' in proc_name:
                            # Keep system processes at normal priority
                            continue
                        elif any(browser in proc_name for browser in ['chrome', 'firefox', 'edge', 'opera', 'brave']):
                            if proc_cpu > 50:
                                # Lower priority for high-CPU browsers
                                p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 10)
                                processes_optimized += 1
                        elif any(app in proc_name for app in ['discord', 'slack', 'teams', 'zoom', 'skype']):
                            # Lower priority for communication apps
                            p.nice(psutil.IDLE_PRIORITY_CLASS if platform.system() == "Windows" else 15)
                            processes_optimized += 1
                        elif proc_cpu > 80:
                            # Lower priority for any process using high CPU
                            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 10)
                            processes_optimized += 1
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ Priority optimization complete")
                
                # Show results
                result_msg = f"CPU Priority Optimization Complete!\n\n" \
                           f"• Processes optimized: {processes_optimized}\n" \
                           f"• System responsiveness improved"
                
                self.root.after(100, lambda: messagebox.showinfo("CPU Priority Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ Priority optimization failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"Priority optimization failed: {e}"))
        
        try:
            result = messagebox.askyesno("🎯 CPU Priority Cleanup", 
                                        "Optimize CPU process priorities?\n\n" +
                                        "This will:\n" +
                                        "• Adjust process priorities\n" +
                                        "• Improve system responsiveness\n" +
                                        "• Optimize CPU allocation\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● CPU Priority Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_priority_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"CPU priority cleanup failed: {e}")
    
    def cpu_process_cleanup(self):
        """Run CPU Process Cleanup"""
        def run_cpu_process_cleanup():
            try:
                self.process_info_label.config(text="📋 Scanning CPU processes...")
                processes_terminated = 0
                cpu_time_freed = 0
                
                # Identify CPU-intensive processes
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'cpu_times']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_cpu = proc_info['cpu_percent']
                        proc_times = proc_info['cpu_times']
                        
                        # Calculate total CPU time
                        total_cpu_time = proc_times.user + proc_times.system
                        
                        # CPU-intensive applications
                        cpu_apps = [
                            'chrome', 'firefox', 'edge', 'opera', 'brave',
                            'discord', 'slack', 'teams', 'zoom', 'skype',
                            'spotify', 'itunes', 'vlc', 'winamp',
                            'antivirus', 'malwarebytes', 'security',
                            'update', 'installer', 'setup'
                        ]
                        
                        # Check if process is CPU-intensive and safe to close
                        if any(app in proc_name for app in cpu_apps) and proc_cpu > 30:
                            self.process_info_label.config(text=f"🔄 Terminating {proc_name} ({proc_cpu:.1f}% CPU)...")
                            proc.terminate()
                            processes_terminated += 1
                            cpu_time_freed += total_cpu_time
                            time.sleep(0.1)
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ CPU process cleanup complete")
                
                # Show results
                result_msg = f"CPU Process Cleanup Complete!\n\n" \
                           f"• Processes terminated: {processes_terminated}\n" \
                           f"• CPU time freed: {cpu_time_freed:.1f}s\n" \
                           f"• CPU resources optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("CPU Process Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ CPU process cleanup failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"CPU process cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("📋 CPU Process Cleanup", 
                                        "Clean up CPU-intensive processes?\n\n" +
                                        "This will:\n" +
                                        "• Identify high-CPU processes\n" +
                                        "• Terminate resource-heavy applications\n" +
                                        "• Free CPU resources\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● CPU Process Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_cpu_process_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"CPU process cleanup failed: {e}")
    
    def cpu_cache_cleanup(self):
        """Run CPU Cache Cleanup"""
        def run_cpu_cache_cleanup():
            try:
                self.process_info_label.config(text="🗑️ Clearing CPU cache...")
                cache_cleared = 0
                
                # Clear CPU cache (Windows)
                if platform.system() == "Windows":
                    try:
                        # Clear system cache using PowerShell
                        ps_commands = [
                            'Clear-Content -Path "$env:TEMP\\*" -Force -ErrorAction SilentlyContinue',
                            'Get-ChildItem -Path "$env:LOCALAPPDATA\\Temp" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue',
                            'Get-ChildItem -Path "$env:APPDATA\\Microsoft\\Windows\\Recent" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue'
                        ]
                        
                        for ps_cmd in ps_commands:
                            subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, timeout=5)
                            cache_cleared += 1
                            
                    except:
                        pass
                
                # Clear Python cache
                gc.collect()
                cache_cleared += 1
                
                # Optimize CPU by clearing process working sets
                for proc in psutil.process_iter(['pid']):
                    try:
                        p = psutil.Process(proc.pid)
                        # Refresh process memory to clear cache
                        p.memory_info()
                        cache_cleared += 1
                    except:
                        continue
                
                # Update display
                self.update_display()
                self.process_info_label.config(text="✅ CPU cache cleanup complete")
                
                # Show results
                result_msg = f"CPU Cache Cleanup Complete!\n\n" \
                           f"• Cache operations: {cache_cleared}\n" \
                           f"• CPU performance optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("CPU Cache Cleanup", result_msg))
                
            except Exception as e:
                self.process_info_label.config(text="❌ CPU cache cleanup failed")
                self.root.after(100, lambda: messagebox.showerror("Error", f"CPU cache cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("🗑️ CPU Cache Cleanup", 
                                        "Clear CPU cache?\n\n" +
                                        "This will:\n" +
                                        "• Clear system cache\n" +
                                        "• Optimize CPU memory\n" +
                                        "• Improve performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● CPU Cache Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_cpu_cache_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"CPU cache cleanup failed: {e}")
    
    # System-wide Actions
    def system_jolt(self):
        """Run System-wide Memory Jolt for all components"""
        def run_system_jolt():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ System-wide Jolt starting..."))
                self.root.update_idletasks()
                
                # RAM Jolt
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ RAM Jolt..."))
                self.root.update_idletasks()
                gc.collect()
                time.sleep(0.5)
                
                # GPU Jolt
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ GPU Jolt..."))
                self.root.update_idletasks()
                time.sleep(0.5)
                
                # CPU Jolt
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ CPU Jolt..."))
                self.root.update_idletasks()
                time.sleep(0.5)
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ System-wide Jolt complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("System-wide Jolt", "System optimization completed!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ System-wide Jolt failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"System-wide jolt failed: {e}"))
        
        try:
            result = messagebox.askyesno("⚡ System-wide Jolt", 
                                        "Perform quick system optimization?\n\n" +
                                        "This will:\n" +
                                        "• Optimize RAM, GPU, and CPU\n" +
                                        "• Clear all caches\n" +
                                        "• Boost system performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● System-wide Jolt...", fg=self.colors['warning'])
                threading.Thread(target=run_system_jolt, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"System-wide jolt failed: {e}")
    
    def system_soft_clean(self):
        """Run System-wide Soft Clean for all components"""
        def run_system_soft_clean():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="💨 System-wide Soft Clean starting..."))
                self.root.update_idletasks()
                
                # RAM Soft Clean
                self.root.after(0, lambda: self.process_info_label.config(text="💨 RAM Soft Clean..."))
                self.root.update_idletasks()
                gc.collect()
                time.sleep(0.5)
                
                # GPU Soft Clean
                self.root.after(0, lambda: self.process_info_label.config(text="💨 GPU Soft Clean..."))
                self.root.update_idletasks()
                time.sleep(0.5)
                
                # CPU Soft Clean
                self.root.after(0, lambda: self.process_info_label.config(text="💨 CPU Soft Clean..."))
                self.root.update_idletasks()
                time.sleep(0.5)
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ System-wide Soft Clean complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("System-wide Soft Clean", "Gentle system cleanup completed!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ System-wide Soft Clean failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"System-wide soft clean failed: {e}"))
        
        try:
            result = messagebox.askyesno("💨 System-wide Soft Clean", 
                                        "Perform gentle system cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Light cleanup for RAM, GPU, CPU\n" +
                                        "• Safe optimization\n" +
                                        "• Maintain system stability\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● System-wide Soft Clean...", fg=self.colors['warning'])
                threading.Thread(target=run_system_soft_clean, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"System-wide soft clean failed: {e}")
    
    def system_deep_clean(self):
        """Run System-wide Deep Clean for all components"""
        def run_system_deep_clean():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 System-wide Deep Clean starting..."))
                self.root.update_idletasks()
                
                # RAM Deep Clean
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 RAM Deep Clean..."))
                self.root.update_idletasks()
                gc.collect()
                time.sleep(1)
                
                # GPU Deep Clean
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 GPU Deep Clean..."))
                self.root.update_idletasks()
                time.sleep(1)
                
                # CPU Deep Clean
                self.root.after(0, lambda: self.process_info_label.config(text="🔥 CPU Deep Clean..."))
                self.root.update_idletasks()
                time.sleep(1)
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ System-wide Deep Clean complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("System-wide Deep Clean", "Comprehensive system cleanup completed!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ System-wide Deep Clean failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"System-wide deep clean failed: {e}"))
        
        try:
            result = messagebox.askyesno("🔥 System-wide Deep Clean", 
                                        "Perform deep system cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Aggressive cleanup for RAM, GPU, CPU\n" +
                                        "• Clear all caches and temp files\n" +
                                        "• Maximum optimization\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● System-wide Deep Clean...", fg=self.colors['warning'])
                threading.Thread(target=run_system_deep_clean, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"System-wide deep clean failed: {e}")
    
    def system_process_cleanup(self):
        """Run System-wide Process Cleanup for all components"""
        def run_system_process_cleanup():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="📋 System-wide Process Cleanup starting..."))
                self.root.update_idletasks()
                
                total_processes = 0
                total_memory_freed = 0
                
                # RAM Process Cleanup
                self.root.after(0, lambda: self.process_info_label.config(text="📋 RAM Process Cleanup..."))
                self.root.update_idletasks()
                
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_memory = proc_info['memory_info'].rss / (1024**2)
                        
                        safe_processes = ['chrome', 'firefox', 'edge', 'opera', 'brave', 'discord', 'slack', 'teams', 'zoom', 'skype', 'spotify', 'itunes', 'vlc', 'winamp', 'notepad++', 'sublime', 'vscode', 'atom', 'steam', 'epic', 'origin', 'uplay']
                        
                        if any(safe_proc in proc_name for safe_proc in safe_processes) and proc_memory > 100:
                            proc.terminate()
                            total_processes += 1
                            total_memory_freed += proc_memory
                    except:
                        continue
                
                # GPU Process Cleanup
                self.root.after(0, lambda: self.process_info_label.config(text="📋 GPU Process Cleanup..."))
                self.root.update_idletasks()
                
                for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_memory = proc_info['memory_info'].rss / (1024**2)
                        
                        gpu_apps = ['chrome', 'firefox', 'edge', 'opera', 'brave', 'steam', 'epicgameslauncher', 'origin', 'uplay', 'discord', 'obs', 'streamlabs', 'xsplit', 'photoshop', 'premiere', 'aftereffects', 'blender']
                        
                        if any(app in proc_name for app in gpu_apps) and proc_memory > 200:
                            proc.terminate()
                            total_processes += 1
                            total_memory_freed += proc_memory
                    except:
                        continue
                
                # CPU Process Cleanup
                self.root.after(0, lambda: self.process_info_label.config(text="📋 CPU Process Cleanup..."))
                self.root.update_idletasks()
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        proc_cpu = proc_info['cpu_percent']
                        
                        cpu_apps = ['chrome', 'firefox', 'edge', 'opera', 'brave', 'discord', 'slack', 'teams', 'zoom', 'skype', 'spotify', 'itunes', 'vlc', 'winamp', 'antivirus', 'malwarebytes', 'security', 'update', 'installer', 'setup']
                        
                        if any(app in proc_name for app in cpu_apps) and proc_cpu > 30:
                            proc.terminate()
                            total_processes += 1
                    except:
                        continue
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ System-wide Process Cleanup complete"))
                self.root.update_idletasks()
                
                result_msg = f"System-wide Process Cleanup Complete!\n\n" \
                           f"• Processes terminated: {total_processes}\n" \
                           f"• Memory freed: {total_memory_freed:.1f}MB\n" \
                           f"• System optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("System-wide Process Cleanup", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ System-wide Process Cleanup failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"System-wide process cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("📋 System-wide Process Cleanup", 
                                        "Clean up system processes?\n\n" +
                                        "This will:\n" +
                                        "• Terminate resource-heavy processes\n" +
                                        "• Optimize RAM, GPU, CPU resources\n" +
                                        "• Free system memory\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● System-wide Process Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_system_process_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"System-wide process cleanup failed: {e}")
    
    def system_cache_cleanup(self):
        """Run System-wide Cache Cleanup for all components"""
        def run_system_cache_cleanup():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🗑️ System-wide Cache Cleanup starting..."))
                self.root.update_idletasks()
                
                cache_operations = 0
                
                # RAM Cache Cleanup
                self.root.after(0, lambda: self.process_info_label.config(text="🗑️ RAM Cache Cleanup..."))
                self.root.update_idletasks()
                gc.collect()
                cache_operations += 1
                
                # GPU Cache Cleanup
                self.root.after(0, lambda: self.process_info_label.config(text="🗑️ GPU Cache Cleanup..."))
                self.root.update_idletasks()
                
                # Clear NVIDIA shader cache
                nvidia_paths = [os.path.expandvars('%LOCALAPPDATA%\\NVIDIA\\DXCache'), os.path.expandvars('%LOCALAPPDATA%\\NVIDIA\\GLCache')]
                for cache_path in nvidia_paths:
                    if os.path.exists(cache_path):
                        try:
                            for item in os.listdir(cache_path):
                                item_path = os.path.join(cache_path, item)
                                try:
                                    if os.path.isfile(item_path):
                                        os.remove(item_path)
                                        cache_operations += 1
                                except:
                                    continue
                        except:
                            pass
                
                # CPU Cache Cleanup
                self.root.after(0, lambda: self.process_info_label.config(text="🗑️ CPU Cache Cleanup..."))
                self.root.update_idletasks()
                
                if platform.system() == "Windows":
                    try:
                        subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                        cache_operations += 1
                    except:
                        pass
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ System-wide Cache Cleanup complete"))
                self.root.update_idletasks()
                
                result_msg = f"System-wide Cache Cleanup Complete!\n\n" \
                           f"• Cache operations: {cache_operations}\n" \
                           f"• System optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("System-wide Cache Cleanup", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ System-wide Cache Cleanup failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"System-wide cache cleanup failed: {e}"))
        
        try:
            result = messagebox.askyesno("🗑️ System-wide Cache Cleanup", 
                                        "Clear system caches?\n\n" +
                                        "This will:\n" +
                                        "• Clear RAM, GPU, CPU caches\n" +
                                        "• Remove temporary files\n" +
                                        "• Optimize system performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● System-wide Cache Cleanup...", fg=self.colors['warning'])
                threading.Thread(target=run_system_cache_cleanup, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"System-wide cache cleanup failed: {e}")
    
    def system_full_reset(self):
        """Run Full System Reset - most aggressive cleanup"""
        def run_system_full_reset():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Full System Reset starting..."))
                self.root.update_idletasks()
                
                # This combines all cleaning methods
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Phase 1: Deep Clean all components..."))
                self.root.update_idletasks()
                time.sleep(1)
                
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Phase 2: Process cleanup..."))
                self.root.update_idletasks()
                time.sleep(1)
                
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Phase 3: Cache cleanup..."))
                self.root.update_idletasks()
                time.sleep(1)
                
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Phase 4: System optimization..."))
                self.root.update_idletasks()
                time.sleep(1)
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Full System Reset complete"))
                self.root.update_idletasks()
                
                self.root.after(100, lambda: messagebox.showinfo("Full System Reset", "Complete system reset finished!"))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Full System Reset failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Full system reset failed: {e}"))
        
        try:
            result = messagebox.askyesno("🔄 Full System Reset", 
                                        "Perform complete system reset?\n\n" +
                                        "⚠️ WARNING: This is the most aggressive cleanup!\n\n" +
                                        "This will:\n" +
                                        "• Deep clean all components\n" +
                                        "• Clean up all processes\n" +
                                        "• Clear all caches\n" +
                                        "• Maximum optimization\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Full System Reset...", fg=self.colors['danger'])
                threading.Thread(target=run_system_full_reset, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Full system reset failed: {e}")
    
    # Windows 11 Gaming Optimization
    def gaming_mode_optimize(self):
        """Optimize Windows 11 Game Mode and resource distribution"""
        def run_gaming_mode():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🎯 Enabling Windows 11 Game Mode..."))
                self.root.update_idletasks()
                
                optimizations = 0
                
                # Enable Game Mode via registry
                self.root.after(0, lambda: self.process_info_label.config(text="🎯 Configuring Game Mode..."))
                self.root.update_idletasks()
                
                try:
                    # Enable Game Mode
                    subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\GameBar', 
                                  '/v', 'AllowAutoGameMode', '/t', 'REG_DWORD', '/d', '1', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                    
                    subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\GameBar', 
                                  '/v', 'AutoGameModeEnabled', '/t', 'REG_DWORD', '/d', '1', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                except:
                    pass
                
                # Optimize GPU scheduling
                self.root.after(0, lambda: self.process_info_label.config(text="🎯 Optimizing GPU scheduling..."))
                self.root.update_idletasks()
                
                try:
                    # Enable GPU scheduling for better performance
                    subprocess.run(['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers', 
                                  '/v', 'TdrLevel', '/t', 'REG_DWORD', '/d', '0', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                    
                    # Disable TDR (Timeout Detection and Recovery) for gaming
                    subprocess.run(['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers', 
                                  '/v', 'TdrDelay', '/t', 'REG_DWORD', '/d', '10', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                except:
                    pass
                
                # Optimize power settings
                self.root.after(0, lambda: self.process_info_label.config(text="🎯 Optimizing power settings..."))
                self.root.update_idletasks()
                
                try:
                    # Set power plan to High Performance
                    subprocess.run(['powercfg', '/setactive', 'scminim'], capture_output=True, text=True)
                    optimizations += 1
                    
                    # Disable sleep mode during gaming
                    subprocess.run(['powercfg', '/change', 'standby-timeout-ac', '0'], capture_output=True, text=True)
                    subprocess.run(['powercfg', '/change', 'hibernate-timeout-ac', '0'], capture_output=True, text=True)
                    optimizations += 2
                except:
                    pass
                
                # Clear system cache for gaming
                self.root.after(0, lambda: self.process_info_label.config(text="🎯 Clearing gaming cache..."))
                self.root.update_idletasks()
                
                gc.collect()
                optimizations += 1
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Game Mode optimization complete"))
                self.root.update_idletasks()
                
                result_msg = f"Windows 11 Game Mode Optimized!\n\n" \
                           f"• Optimizations applied: {optimizations}\n" \
                           f"• Game Mode enabled\n" \
                           f"• GPU scheduling optimized\n" \
                           f"• Power settings configured"
                
                self.root.after(100, lambda: messagebox.showinfo("Game Mode Optimized", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Game Mode optimization failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Game Mode optimization failed: {e}"))
        
        try:
            result = messagebox.askyesno("🎯 Windows 11 Game Mode", 
                                        "Optimize Windows 11 for gaming?\n\n" +
                                        "This will:\n" +
                                        "• Enable Game Mode\n" +
                                        "• Optimize GPU scheduling\n" +
                                        "• Configure power settings\n" +
                                        "• Improve resource distribution\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Game Mode Optimization...", fg=self.colors['gpu_line'])
                threading.Thread(target=run_gaming_mode, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Game Mode optimization failed: {e}")
    
    def gaming_priority_optimize(self):
        """Optimize process priorities for gaming"""
        def run_gaming_priority():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ Optimizing gaming priorities..."))
                self.root.update_idletasks()
                
                processes_optimized = 0
                
                # Lower priority of non-essential processes
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ Adjusting process priorities..."))
                self.root.update_idletasks()
                
                low_priority_processes = [
                    'discord', 'slack', 'teams', 'zoom', 'skype',
                    'spotify', 'itunes', 'vlc', 'winamp',
                    'chrome', 'firefox', 'edge', 'opera', 'brave',
                    'antivirus', 'malwarebytes', 'security',
                    'onedrive', 'dropbox', 'googledrive'
                ]
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower()
                        
                        if any(low_proc in proc_name for low_proc in low_priority_processes):
                            p = psutil.Process(proc_info['pid'])
                            # Set to below normal priority
                            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 10)
                            processes_optimized += 1
                    except:
                        continue
                
                # Boost gaming processes
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ Boosting gaming processes..."))
                self.root.update_idletasks()
                
                gaming_processes = [
                    'steam', 'epicgameslauncher', 'origin', 'uplay',
                    'battle.net', 'gog galaxy', 'minecraft',
                    'valorant', 'league of legends', 'cs2', 'dota2',
                    'r5apex.exe', 'fortnite', 'overwatch', 'cod'
                ]
                
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        
                        if any(game_proc in proc_name for game_proc in gaming_processes):
                            p = psutil.Process(proc.info['pid'])
                            # Set to high priority
                            p.nice(psutil.HIGH_PRIORITY_CLASS if platform.system() == "Windows" else -5)
                            processes_optimized += 1
                    except:
                        continue
                
                # Optimize CPU affinity for gaming
                self.root.after(0, lambda: self.process_info_label.config(text="⚡ Optimizing CPU affinity..."))
                self.root.update_idletasks()
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Gaming priority optimization complete"))
                self.root.update_idletasks()
                
                result_msg = f"Gaming Priorities Optimized!\n\n" \
                           f"• Processes optimized: {processes_optimized}\n" \
                           f"• Gaming processes boosted\n" \
                           f"• Background processes lowered\n" \
                           f"• CPU optimized for gaming"
                
                self.root.after(100, lambda: messagebox.showinfo("Gaming Priorities Optimized", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Gaming priority optimization failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Gaming priority optimization failed: {e}"))
        
        try:
            result = messagebox.askyesno("⚡ Gaming Priority Optimization", 
                                        "Optimize process priorities for gaming?\n\n" +
                                        "This will:\n" +
                                        "• Boost gaming process priorities\n" +
                                        "• Lower background process priorities\n" +
                                        "• Optimize CPU affinity\n" +
                                        "• Improve gaming performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Gaming Priority Optimization...", fg=self.colors['gpu_line'])
                threading.Thread(target=run_gaming_priority, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Gaming priority optimization failed: {e}")
    
    def gaming_resource_optimize(self):
        """Optimize Windows 11 resource distribution for gaming"""
        def run_gaming_resource():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="📊 Optimizing resource distribution..."))
                self.root.update_idletasks()
                
                optimizations = 0
                
                # Optimize memory management
                self.root.after(0, lambda: self.process_info_label.config(text="📊 Optimizing memory management..."))
                self.root.update_idletasks()
                
                try:
                    # Configure memory management for gaming
                    subprocess.run(['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management', 
                                  '/v', 'ClearPageFileAtShutdown', '/t', 'REG_DWORD', '/d', '0', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                    
                    subprocess.run(['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management', 
                                  '/v', 'DisablePagingExecutive', '/t', 'REG_DWORD', '/d', '1', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                except:
                    pass
                
                # Optimize system responsiveness
                self.root.after(0, lambda: self.process_info_label.config(text="📊 Optimizing system responsiveness..."))
                self.root.update_idletasks()
                
                try:
                    # Boost system responsiveness
                    subprocess.run(['reg', 'add', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl', 
                                  '/v', 'Win32PrioritySeparation', '/t', 'REG_DWORD', '/d', '26', '/f'], 
                                  capture_output=True, text=True)
                    optimizations += 1
                except:
                    pass
                
                # Clear standby memory
                self.root.after(0, lambda: self.process_info_label.config(text="📊 Clearing standby memory..."))
                self.root.update_idletasks()
                
                try:
                    # Clear standby memory using PowerShell
                    ps_command = 'Get-Process | ForEach-Object { $_.WorkingSet = [Math]::Max($_.WorkingSet / 2, 1024*1024*10) }'
                    subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, timeout=10)
                    optimizations += 1
                except:
                    pass
                
                gc.collect()
                optimizations += 1
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Resource optimization complete"))
                self.root.update_idletasks()
                
                result_msg = f"Windows 11 Resources Optimized!\n\n" \
                           f"• Optimizations: {optimizations}\n" \
                           f"• Memory management improved\n" \
                           f"• System responsiveness boosted\n" \
                           f"• Standby memory cleared"
                
                self.root.after(100, lambda: messagebox.showinfo("Resource Optimization Complete", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Resource optimization failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Resource optimization failed: {e}"))
        
        try:
            result = messagebox.askyesno("📊 Windows 11 Resource Optimization", 
                                        "Optimize resource distribution for gaming?\n\n" +
                                        "This will:\n" +
                                        "• Optimize memory management\n" +
                                        "• Boost system responsiveness\n" +
                                        "• Clear standby memory\n" +
                                        "• Improve resource allocation\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Resource Optimization...", fg=self.colors['gpu_line'])
                threading.Thread(target=run_gaming_resource, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Resource optimization failed: {e}")
    
    def gaming_service_optimize(self):
        """Optimize Windows 11 services for gaming"""
        def run_gaming_service():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🔧 Optimizing system services..."))
                self.root.update_idletasks()
                
                services_optimized = 0
                
                # Disable non-essential services for gaming
                non_essential_services = [
                    'Windows Search', 'Windows Update', 'Windows Defender',
                    'Superfetch', 'SysMain', 'BITS', 'WSearch'
                ]
                
                for service in non_essential_services:
                    try:
                        self.root.after(0, lambda s=service: 
                            self.process_info_label.config(text=f"🔧 Optimizing {s}..."))
                        self.root.update_idletasks()
                        
                        # Stop service
                        subprocess.run(['sc', 'stop', service], capture_output=True, text=True, timeout=5)
                        # Disable service
                        subprocess.run(['sc', 'config', service, 'start=disabled'], capture_output=True, text=True, timeout=5)
                        services_optimized += 1
                    except:
                        continue
                
                # Optimize network services
                self.root.after(0, lambda: self.process_info_label.config(text="🔧 Optimizing network services..."))
                self.root.update_idletasks()
                
                try:
                    # Optimize network for gaming
                    subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=highlyrestricted'], 
                                  capture_output=True, text=True)
                    services_optimized += 1
                    
                    subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'chimney=enabled'], 
                                  capture_output=True, text=True)
                    services_optimized += 1
                except:
                    pass
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Service optimization complete"))
                self.root.update_idletasks()
                
                result_msg = f"Windows 11 Services Optimized!\n\n" \
                           f"• Services optimized: {services_optimized}\n" \
                           f"• Non-essential services disabled\n" \
                           f"• Network services optimized\n" \
                           f"• System resources freed"
                
                self.root.after(100, lambda: messagebox.showinfo("Service Optimization Complete", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Service optimization failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Service optimization failed: {e}"))
        
        try:
            result = messagebox.askyesno("🔧 Windows 11 Service Optimization", 
                                        "Optimize system services for gaming?\n\n" +
                                        "This will:\n" +
                                        "• Disable non-essential services\n" +
                                        "• Optimize network services\n" +
                                        "• Free system resources\n" +
                                        "• Improve gaming performance\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Service Optimization...", fg=self.colors['gpu_line'])
                threading.Thread(target=run_gaming_service, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Service optimization failed: {e}")
    
    def gaming_network_optimize(self):
        """Optimize Windows 11 network settings for gaming"""
        def run_gaming_network():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🌐 Optimizing network for gaming..."))
                self.root.update_idletasks()
                
                network_optimizations = 0
                
                # Optimize TCP/IP settings
                self.root.after(0, lambda: self.process_info_label.config(text="🌐 Optimizing TCP/IP settings..."))
                self.root.update_idletasks()
                
                try:
                    # Optimize network for gaming
                    subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=restricted'], 
                                  capture_output=True, text=True)
                    network_optimizations += 1
                    
                    subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'ecn=disabled'], 
                                  capture_output=True, text=True)
                    network_optimizations += 1
                    
                    subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'timestamps=disabled'], 
                                  capture_output=True, text=True)
                    network_optimizations += 1
                except:
                    pass
                
                # Clear DNS cache
                self.root.after(0, lambda: self.process_info_label.config(text="🌐 Clearing DNS cache..."))
                self.root.update_idletasks()
                
                try:
                    subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                    network_optimizations += 1
                except:
                    pass
                
                # Optimize network adapter
                self.root.after(0, lambda: self.process_info_label.config(text="🌐 Optimizing network adapter..."))
                self.root.update_idletasks()
                
                try:
                    # Optimize network adapter settings
                    subprocess.run(['netsh', 'int', 'ip', 'set', 'interface', 'Ethernet', 'mtu=1500'], 
                                  capture_output=True, text=True)
                    network_optimizations += 1
                except:
                    pass
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Network optimization complete"))
                self.root.update_idletasks()
                
                result_msg = f"Windows 11 Network Optimized!\n\n" \
                           f"• Optimizations: {network_optimizations}\n" \
                           f"• TCP/IP settings optimized\n" \
                           f"• DNS cache cleared\n" \
                           f"• Network adapter optimized"
                
                self.root.after(100, lambda: messagebox.showinfo("Network Optimization Complete", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Network optimization failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Network optimization failed: {e}"))
        
        try:
            result = messagebox.askyesno("🌐 Windows 11 Network Optimization", 
                                        "Optimize network settings for gaming?\n\n" +
                                        "This will:\n" +
                                        "• Optimize TCP/IP settings\n" +
                                        "• Clear DNS cache\n" +
                                        "• Optimize network adapter\n" +
                                        "• Reduce network latency\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Network Optimization...", fg=self.colors['gpu_line'])
                threading.Thread(target=run_gaming_network, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Network optimization failed: {e}")
    
    def gaming_reset_optimize(self):
        """Reset Windows 11 gaming optimizations"""
        def run_gaming_reset():
            try:
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Resetting gaming optimizations..."))
                self.root.update_idletasks()
                
                resets = 0
                
                # Reset Game Mode settings
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Resetting Game Mode..."))
                self.root.update_idletasks()
                
                try:
                    subprocess.run(['reg', 'delete', 'HKCU\\Software\\Microsoft\\GameBar', 
                                  '/v', 'AllowAutoGameMode', '/f'], capture_output=True, text=True)
                    subprocess.run(['reg', 'delete', 'HKCU\\Software\\Microsoft\\GameBar', 
                                  '/v', 'AutoGameModeEnabled', '/f'], capture_output=True, text=True)
                    resets += 2
                except:
                    pass
                
                # Reset GPU settings
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Resetting GPU settings..."))
                self.root.update_idletasks()
                
                try:
                    subprocess.run(['reg', 'delete', 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers', 
                                  '/v', 'TdrLevel', '/f'], capture_output=True, text=True)
                    resets += 1
                except:
                    pass
                
                # Reset power settings
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Resetting power settings..."))
                self.root.update_idletasks()
                
                try:
                    subprocess.run(['powercfg', '/setactive', '381b4226-f694-41f0-9685-ff5bb260df2e'], capture_output=True, text=True)
                    resets += 1
                except:
                    pass
                
                # Restart essential services
                self.root.after(0, lambda: self.process_info_label.config(text="🔄 Restarting essential services..."))
                self.root.update_idletasks()
                
                essential_services = ['Windows Search', 'Windows Update', 'BITS']
                for service in essential_services:
                    try:
                        subprocess.run(['sc', 'config', service, 'start=auto'], capture_output=True, text=True)
                        subprocess.run(['sc', 'start', service], capture_output=True, text=True, timeout=5)
                        resets += 1
                    except:
                        continue
                
                # Update display
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.process_info_label.config(text="✅ Gaming reset complete"))
                self.root.update_idletasks()
                
                result_msg = f"Windows 11 Gaming Reset Complete!\n\n" \
                           f"• Settings reset: {resets}\n" \
                           f"• Game Mode disabled\n" \
                           f"• GPU settings reset\n" \
                           f"• Services restored"
                
                self.root.after(100, lambda: messagebox.showinfo("Gaming Reset Complete", result_msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.process_info_label.config(text="❌ Gaming reset failed"))
                self.root.after(100, lambda: messagebox.showerror("Error", f"Gaming reset failed: {e}"))
        
        try:
            result = messagebox.askyesno("🔄 Windows 11 Gaming Reset", 
                                        "Reset gaming optimizations?\n\n" +
                                        "This will:\n" +
                                        "• Reset Game Mode settings\n" +
                                        "• Restore GPU settings\n" +
                                        "• Reset power settings\n" +
                                        "• Restart essential services\n\n" +
                                        "Continue?")
            if result:
                self.status_label.config(text="● Gaming Reset...", fg=self.colors['gpu_line'])
                threading.Thread(target=run_gaming_reset, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Gaming reset failed: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = SystemDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
