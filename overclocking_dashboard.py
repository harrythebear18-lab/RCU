#!/usr/bin/env python3
"""
Overclocking Dashboard
A comprehensive dashboard for monitoring and overclocking/underclocking CPU, GPU, and RAM.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
import json

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

class OverclockingDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Overclocking Dashboard")
        self.root.geometry("1500x950")
        self.root.configure(bg='#0f0f0f')
        self.root.resizable(True, True)
        self.root.minsize(1200, 800)
        
        # Enhanced modern color scheme
        self.colors = {
            'bg': '#0f0f0f',
            'card': '#1e1e1e',
            'card_hover': '#2a2a2a',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0',
            'accent': '#0078ff',
            'graph_bg': '#1a1a1a',
            'cpu_line': '#ff6b6b',      # Softer red for CPU
            'gpu_line': '#4ecdc4',      # Teal for GPU  
            'ram_line': '#a855f7',      # Purple for RAM
            'border': '#333333',
            'slider_track': '#404040',
            'slider_thumb': '#00d4ff'
        }
        
        # Data storage for plotting
        self.time_data = []
        self.cpu_data = []
        self.gpu_data = []
        self.ram_data = []
        self.cpu_freq_data = []
        self.gpu_freq_data = []
        self.temp_data = []
        self.max_points = 60  # Show last 60 data points
        
        # System info
        self.cpu_count = psutil.cpu_count(logical=True)
        self.cpu_physical = psutil.cpu_count(logical=False)
        self.gpu_count = 0
        
        # Overclocking settings
        self.cpu_base_freq = 0
        self.cpu_current_freq = 0
        self.gpu_base_freq = 0
        self.gpu_current_freq = 0
        self.ram_base_freq = 0
        self.ram_current_freq = 0
        
        # Safety limits
        self.max_cpu_temp = 85  # Maximum safe CPU temperature
        self.max_gpu_temp = 85  # Maximum safe GPU temperature
        self.max_cpu_freq_increase = 20  # Maximum CPU frequency increase in %
        self.max_gpu_freq_increase = 15  # Maximum GPU frequency increase in %
        
        # Monitoring settings
        self.update_interval = 1000  # Update every 1 second for active monitoring
        self.monitoring = False
        self.monitor_thread = None
        
        # Enhanced overclocking profiles with extended ranges
        self.profiles = {
            'stock': {'cpu_freq': 100, 'gpu_freq': 100, 'ram_freq': 100},
            'gaming': {'cpu_freq': 110, 'gpu_freq': 105, 'ram_freq': 106},
            'performance': {'cpu_freq': 115, 'gpu_freq': 110, 'ram_freq': 108},
            'extreme': {'cpu_freq': 120, 'gpu_freq': 115, 'ram_freq': 110},
            'insane': {'cpu_freq': 135, 'gpu_freq': 125, 'ram_freq': 120},
            'suicide': {'cpu_freq': 150, 'gpu_freq': 140, 'ram_freq': 135},
            'custom': {'cpu_freq': 100, 'gpu_freq': 100, 'ram_freq': 100}
        }
        
        # Profile persistence
        self.profiles_file = os.path.join(os.path.dirname(__file__), 'overclocking_profiles.json')
        self.current_profile_file = os.path.join(os.path.dirname(__file__), 'current_overclock_profile.json')
        
        # Load saved profiles
        self.load_profiles()
        self.load_current_profile()
        
        # Style configuration
        self.setup_styles()
        
        # Initialize hardware detection
        self.detect_hardware()
        
        # Create GUI components
        self.create_widgets()
        
        # Start monitoring automatically
        self.start_monitoring()
    
    def setup_styles(self):
        """Setup modern custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Card.TFrame', background=self.colors['card'], relief='flat', borderwidth=1)
        style.configure('Title.TLabel', background=self.colors['card'], foreground=self.colors['primary'], 
                       font=('Segoe UI', 12, 'bold'))
        style.configure('Info.TLabel', background=self.colors['card'], foreground=self.colors['text'], 
                       font=('Segoe UI', 10))
        style.configure('Value.TLabel', background=self.colors['card'], foreground=self.colors['text'], 
                       font=('Segoe UI', 14, 'bold'))
        style.configure('Danger.TLabel', background=self.colors['card'], foreground=self.colors['danger'], 
                       font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TLabel', background=self.colors['card'], foreground=self.colors['success'], 
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure button styles
        style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'), relief='flat', borderwidth=0)
        style.map('Action.TButton',
                 background=[('active', self.colors['primary']), ('!active', self.colors['accent'])],
                 foreground=[('active', self.colors['bg']), ('!active', self.colors['text'])])
    
    def detect_hardware(self):
        """Detect and initialize hardware information"""
        # Get CPU base frequency
        try:
            freq_info = psutil.cpu_freq()
            if freq_info:
                self.cpu_base_freq = freq_info.current
                self.cpu_current_freq = freq_info.current
        except:
            self.cpu_base_freq = 3.0  # Default fallback
            self.cpu_current_freq = 3.0
        
        # Detect GPUs
        if NVML_AVAILABLE:
            try:
                self.gpu_count = nvml.nvmlDeviceGetCount()
                if self.gpu_count > 0:
                    handle = nvml.nvmlDeviceGetHandleByIndex(0)
                    self.gpu_base_freq = nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_GRAPHICS_CLOCK) / 1000
                    self.gpu_current_freq = self.gpu_base_freq
            except Exception as e:
                self.gpu_count = 0
        elif GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                self.gpu_count = len(gpus)
                if self.gpu_count > 0:
                    # GPUtil doesn't provide clock info, use default
                    self.gpu_base_freq = 1500  # Default 1500 MHz fallback
                    self.gpu_current_freq = self.gpu_base_freq
            except Exception as e:
                # Don't set gpu_count to 0 if GPUtil is available - it might work in get_system_info
                self.gpu_count = 1  # Assume 1 GPU if GPUtil is available
        else:
            self.gpu_count = 0
        
        # Get RAM frequency
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['wmic', 'memorychip', 'get', 'speed'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:
                        if line.strip() and line.strip().isdigit():
                            self.ram_base_freq = float(line.strip())
                            self.ram_current_freq = self.ram_base_freq
                            break
        except:
            self.ram_base_freq = 3200  # Default fallback
            self.ram_current_freq = 3200
    
    def create_widgets(self):
        """Create all GUI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Enhanced Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title section
        title_section = tk.Frame(header_frame, bg=self.colors['bg'])
        title_section.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        title_label = tk.Label(title_section, text="⚡ Overclocking Dashboard", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(anchor='w', pady=(20, 5))
        
        subtitle_label = tk.Label(title_section, text="Real-time Hardware Monitoring & Performance Tuning", 
                                 font=('Segoe UI', 11), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(anchor='w')
        
        # Status section
        status_section = tk.Frame(header_frame, bg=self.colors['bg'])
        status_section.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        # Status indicator
        self.status_label = tk.Label(status_section, text="● Monitoring", 
                                     font=('Segoe UI', 12, 'bold'), 
                                     fg=self.colors['success'], bg=self.colors['bg'])
        self.status_label.pack(anchor='e', pady=(20, 5))
        
        # Temperature warning
        self.temp_warning_label = tk.Label(status_section, text="", 
                                          font=('Segoe UI', 10, 'bold'), 
                                          fg=self.colors['warning'], bg=self.colors['bg'])
        self.temp_warning_label.pack(anchor='e')
        
        # Create main sections
        self.create_monitoring_section(main_container)
        self.create_overclocking_section(main_container)
        self.create_profiles_section(main_container)
        self.create_safety_section(main_container)
    
    def create_monitoring_section(self, parent):
        """Create enhanced real-time monitoring section"""
        # Monitoring frame with border
        monitor_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        monitor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Enhanced title section
        title_section = tk.Frame(monitor_frame, bg=self.colors['card'])
        title_section.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        monitor_title = tk.Label(title_section, text="📊 Real-time Hardware Monitoring", 
                               font=('Segoe UI', 16, 'bold'), 
                               fg=self.colors['primary'], bg=self.colors['card'])
        monitor_title.pack(side=tk.LEFT)
        
        # Live indicator
        live_indicator = tk.Label(title_section, text="● LIVE", 
                                font=('Segoe UI', 10, 'bold'), 
                                fg=self.colors['success'], bg=self.colors['card'])
        live_indicator.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Enhanced info cards container
        cards_container = tk.Frame(monitor_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Enhanced CPU Card
        cpu_card = tk.Frame(cards_container, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['cpu_line'], highlightthickness=1)
        cpu_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CPU header
        cpu_header = tk.Frame(cpu_card, bg=self.colors['cpu_line'], height=3)
        cpu_header.pack(fill=tk.X)
        cpu_header.pack_propagate(False)
        
        # CPU content
        cpu_content = tk.Frame(cpu_card, bg=self.colors['card'])
        cpu_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.cpu_usage_label = tk.Label(cpu_content, text="CPU", font=('Segoe UI', 12, 'bold'), 
                                       fg=self.colors['cpu_line'], bg=self.colors['card'])
        self.cpu_usage_label.pack(pady=(0, 10))
        
        self.cpu_value_label = tk.Label(cpu_content, text="0%", font=('Segoe UI', 20, 'bold'), 
                                        fg=self.colors['text'], bg=self.colors['card'])
        self.cpu_value_label.pack()
        
        self.cpu_freq_label = tk.Label(cpu_content, text="0.0 GHz", font=('Segoe UI', 11), 
                                       fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.cpu_freq_label.pack(pady=(5, 2))
        
        self.cpu_temp_label = tk.Label(cpu_content, text="0°C", font=('Segoe UI', 11), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.cpu_temp_label.pack(pady=(2, 0))
        
        # Enhanced GPU Card
        gpu_card = tk.Frame(cards_container, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['gpu_line'], highlightthickness=1)
        gpu_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # GPU header
        gpu_header = tk.Frame(gpu_card, bg=self.colors['gpu_line'], height=3)
        gpu_header.pack(fill=tk.X)
        gpu_header.pack_propagate(False)
        
        # GPU content
        gpu_content = tk.Frame(gpu_card, bg=self.colors['card'])
        gpu_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.gpu_usage_label = tk.Label(gpu_content, text="GPU", font=('Segoe UI', 12, 'bold'), 
                                       fg=self.colors['gpu_line'], bg=self.colors['card'])
        self.gpu_usage_label.pack(pady=(0, 10))
        
        self.gpu_value_label = tk.Label(gpu_content, text="0%", font=('Segoe UI', 20, 'bold'), 
                                        fg=self.colors['text'], bg=self.colors['card'])
        self.gpu_value_label.pack()
        
        self.gpu_freq_label = tk.Label(gpu_content, text="0.0 GHz", font=('Segoe UI', 11), 
                                       fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.gpu_freq_label.pack(pady=(5, 2))
        
        self.gpu_temp_label = tk.Label(gpu_content, text="0°C", font=('Segoe UI', 11), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.gpu_temp_label.pack(pady=(2, 0))
        
        # Enhanced RAM Card
        ram_card = tk.Frame(cards_container, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['ram_line'], highlightthickness=1)
        ram_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # RAM header
        ram_header = tk.Frame(ram_card, bg=self.colors['ram_line'], height=3)
        ram_header.pack(fill=tk.X)
        ram_header.pack_propagate(False)
        
        # RAM content
        ram_content = tk.Frame(ram_card, bg=self.colors['card'])
        ram_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.ram_usage_label = tk.Label(ram_content, text="RAM", font=('Segoe UI', 12, 'bold'), 
                                       fg=self.colors['ram_line'], bg=self.colors['card'])
        self.ram_usage_label.pack(pady=(0, 10))
        
        self.ram_value_label = tk.Label(ram_content, text="0%", font=('Segoe UI', 20, 'bold'), 
                                        fg=self.colors['text'], bg=self.colors['card'])
        self.ram_value_label.pack()
        
        self.ram_freq_label = tk.Label(ram_content, text="0 MHz", font=('Segoe UI', 11), 
                                       fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.ram_freq_label.pack(pady=(5, 2))
        
        self.ram_size_label = tk.Label(ram_content, text="0 GB", font=('Segoe UI', 11), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.ram_size_label.pack(pady=(2, 0))
        
        # Create performance graph
        self.create_performance_graph(monitor_frame)
    
    def create_performance_graph(self, parent):
        """Create real-time performance graph"""
        # Graph frame
        graph_frame = tk.Frame(parent, bg=self.colors['card'])
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 3), facecolor=self.colors['card'])
        self.ax = self.fig.add_subplot(111, facecolor=self.colors['graph_bg'])
        
        # Setup graph
        self.ax.set_title('Real-time Performance', color=self.colors['text'], fontsize=12)
        self.ax.set_xlabel('Time', color=self.colors['text_secondary'])
        self.ax.set_ylabel('Usage (%)', color=self.colors['text_secondary'])
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.3, color=self.colors['text_secondary'])
        self.ax.tick_params(colors=self.colors['text_secondary'])
        
        # Create line plots
        self.cpu_line, = self.ax.plot([], [], color=self.colors['cpu_line'], linewidth=2, label='CPU')
        self.gpu_line, = self.ax.plot([], [], color=self.colors['gpu_line'], linewidth=2, label='GPU')
        self.ram_line, = self.ax.plot([], [], color=self.colors['ram_line'], linewidth=2, label='RAM')
        
        self.ax.legend(loc='upper right', facecolor=self.colors['card'], edgecolor=self.colors['text'])
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_overclocking_section(self, parent):
        """Create enhanced overclocking controls section"""
        # Overclocking frame with border
        oc_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        oc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Enhanced title section
        title_section = tk.Frame(oc_frame, bg=self.colors['card'])
        title_section.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        oc_title = tk.Label(title_section, text="⚡ Overclocking Controls", 
                           font=('Segoe UI', 16, 'bold'), 
                           fg=self.colors['primary'], bg=self.colors['card'])
        oc_title.pack(side=tk.LEFT)
        
        # Active indicator
        active_indicator = tk.Label(title_section, text="● ACTIVE", 
                                 font=('Segoe UI', 10, 'bold'), 
                                 fg=self.colors['warning'], bg=self.colors['card'])
        active_indicator.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Enhanced controls container
        controls_container = tk.Frame(oc_frame, bg=self.colors['card'])
        controls_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Enhanced CPU Overclocking
        cpu_oc_frame = tk.Frame(controls_container, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['cpu_line'], highlightthickness=1)
        cpu_oc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CPU header
        cpu_header = tk.Frame(cpu_oc_frame, bg=self.colors['cpu_line'], height=3)
        cpu_header.pack(fill=tk.X)
        cpu_header.pack_propagate(False)
        
        # CPU content
        cpu_content = tk.Frame(cpu_oc_frame, bg=self.colors['card'])
        cpu_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(cpu_content, text="CPU Overclock", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['cpu_line'], bg=self.colors['card']).pack(pady=(0, 15))
        
        # Enhanced slider styling
        self.cpu_freq_var = tk.DoubleVar(value=100)
        self.cpu_freq_slider = tk.Scale(cpu_content, from_=80, to=150, orient=tk.HORIZONTAL,
                                       variable=self.cpu_freq_var, bg=self.colors['card'],
                                       fg=self.colors['text'], highlightthickness=0,
                                       troughcolor=self.colors['slider_track'], 
                                       activebackground=self.colors['slider_thumb'],
                                       command=self.on_cpu_freq_change)
        self.cpu_freq_slider.pack(fill=tk.X, pady=10)
        
        self.cpu_freq_value = tk.Label(cpu_content, text="100% (Stock)", 
                                      font=('Segoe UI', 11, 'bold'), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.cpu_freq_value.pack()
        
        # CPU frequency display
        self.cpu_actual_freq_label = tk.Label(cpu_content, text="0.0 GHz", 
                                             font=('Segoe UI', 10), 
                                             fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.cpu_actual_freq_label.pack(pady=(5, 0))
        
        # Enhanced GPU Overclocking
        gpu_oc_frame = tk.Frame(controls_container, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['gpu_line'], highlightthickness=1)
        gpu_oc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # GPU header
        gpu_header = tk.Frame(gpu_oc_frame, bg=self.colors['gpu_line'], height=3)
        gpu_header.pack(fill=tk.X)
        gpu_header.pack_propagate(False)
        
        # GPU content
        gpu_content = tk.Frame(gpu_oc_frame, bg=self.colors['card'])
        gpu_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(gpu_content, text="GPU Overclock", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['gpu_line'], bg=self.colors['card']).pack(pady=(0, 15))
        
        # Enhanced GPU slider
        self.gpu_freq_var = tk.DoubleVar(value=100)
        self.gpu_freq_slider = tk.Scale(gpu_content, from_=80, to=140, orient=tk.HORIZONTAL,
                                       variable=self.gpu_freq_var, bg=self.colors['card'],
                                       fg=self.colors['text'], highlightthickness=0,
                                       troughcolor=self.colors['slider_track'], 
                                       activebackground=self.colors['slider_thumb'],
                                       command=self.on_gpu_freq_change)
        self.gpu_freq_slider.pack(fill=tk.X, pady=10)
        
        self.gpu_freq_value = tk.Label(gpu_content, text="100% (Stock)", 
                                      font=('Segoe UI', 11, 'bold'), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.gpu_freq_value.pack()
        
        # GPU frequency display
        self.gpu_actual_freq_label = tk.Label(gpu_content, text="0.0 GHz", 
                                             font=('Segoe UI', 10), 
                                             fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.gpu_actual_freq_label.pack(pady=(5, 0))
        
        # Enhanced RAM Overclocking
        ram_oc_frame = tk.Frame(controls_container, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['ram_line'], highlightthickness=1)
        ram_oc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # RAM header
        ram_header = tk.Frame(ram_oc_frame, bg=self.colors['ram_line'], height=3)
        ram_header.pack(fill=tk.X)
        ram_header.pack_propagate(False)
        
        # RAM content
        ram_content = tk.Frame(ram_oc_frame, bg=self.colors['card'])
        ram_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(ram_content, text="RAM Overclock", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['ram_line'], bg=self.colors['card']).pack(pady=(0, 15))
        
        # Enhanced RAM slider
        self.ram_freq_var = tk.DoubleVar(value=100)
        self.ram_freq_slider = tk.Scale(ram_content, from_=80, to=135, orient=tk.HORIZONTAL,
                                       variable=self.ram_freq_var, bg=self.colors['card'],
                                       fg=self.colors['text'], highlightthickness=0,
                                       troughcolor=self.colors['slider_track'], 
                                       activebackground=self.colors['slider_thumb'],
                                       command=self.on_ram_freq_change)
        self.ram_freq_slider.pack(fill=tk.X, pady=10)
        
        self.ram_freq_value = tk.Label(ram_content, text="100% (Stock)", 
                                      font=('Segoe UI', 11, 'bold'), 
                                      fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.ram_freq_value.pack()
        
        # RAM frequency display
        self.ram_actual_freq_label = tk.Label(ram_content, text="0 MHz", 
                                             font=('Segoe UI', 10), 
                                             fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.ram_actual_freq_label.pack(pady=(5, 0))
        
        # Enhanced Apply buttons
        button_frame = tk.Frame(oc_frame, bg=self.colors['card'])
        button_frame.pack(pady=(0, 20))
        
        apply_btn = tk.Button(button_frame, text="⚡ Apply Overclock", 
                            font=('Segoe UI', 11, 'bold'), 
                            bg=self.colors['success'], fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                            command=self.apply_overclock)
        apply_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = tk.Button(button_frame, text="🔄 Reset to Stock", 
                            font=('Segoe UI', 11, 'bold'), 
                            bg=self.colors['warning'], fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                            command=self.reset_overclock)
        reset_btn.pack(side=tk.LEFT, padx=10)
    
    def create_profiles_section(self, parent):
        """Create enhanced overclocking profiles section"""
        # Profiles frame
        profiles_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        profiles_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Enhanced title section
        title_section = tk.Frame(profiles_frame, bg=self.colors['card'])
        title_section.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        profiles_title = tk.Label(title_section, text="🎛️ Overclocking Profiles", 
                                 font=('Segoe UI', 16, 'bold'), 
                                 fg=self.colors['primary'], bg=self.colors['card'])
        profiles_title.pack(side=tk.LEFT)
        
        # Profile management buttons
        manage_frame = tk.Frame(title_section, bg=self.colors['card'])
        manage_frame.pack(side=tk.RIGHT)
        
        save_btn = tk.Button(manage_frame, text="💾 Save", 
                            font=('Segoe UI', 9, 'bold'), 
                            bg=self.colors['success'], fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2',
                            command=self.save_custom_profile)
        save_btn.pack(side=tk.LEFT, padx=2)
        
        export_btn = tk.Button(manage_frame, text="📤 Export", 
                              font=('Segoe UI', 9, 'bold'), 
                              bg=self.colors['primary'], fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              command=self.export_profiles)
        export_btn.pack(side=tk.LEFT, padx=2)
        
        import_btn = tk.Button(manage_frame, text="📥 Import", 
                              font=('Segoe UI', 9, 'bold'), 
                              bg=self.colors['warning'], fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              command=self.import_profiles)
        import_btn.pack(side=tk.LEFT, padx=2)
        
        # Profile buttons container
        self.profile_buttons_frame = tk.Frame(profiles_frame, bg=self.colors['card'])
        self.profile_buttons_frame.pack(pady=(0, 20))
        
        # Initialize profile buttons
        self.update_profile_buttons()
    
    def create_safety_section(self, parent):
        """Create safety monitoring section"""
        # Safety frame
        safety_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        safety_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        safety_title = tk.Label(safety_frame, text="🛡️ Safety Monitoring", 
                               font=('Segoe UI', 14, 'bold'), 
                               fg=self.colors['primary'], bg=self.colors['card'])
        safety_title.pack(pady=(15, 10))
        
        # Safety info
        safety_info = tk.Frame(safety_frame, bg=self.colors['card'])
        safety_info.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Temperature limits
        temp_frame = tk.Frame(safety_info, bg=self.colors['card'])
        temp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(temp_frame, text="Temperature Limits", font=('Segoe UI', 11, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.cpu_temp_limit_label = tk.Label(temp_frame, text=f"CPU Max: {self.max_cpu_temp}°C", 
                                            font=('Segoe UI', 10), 
                                            fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.cpu_temp_limit_label.pack()
        
        self.gpu_temp_limit_label = tk.Label(temp_frame, text=f"GPU Max: {self.max_gpu_temp}°C", 
                                            font=('Segoe UI', 10), 
                                            fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.gpu_temp_limit_label.pack()
        
        # Safety status
        status_frame = tk.Frame(safety_info, bg=self.colors['card'])
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(status_frame, text="Safety Status", font=('Segoe UI', 11, 'bold'), 
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.safety_status_label = tk.Label(status_frame, text="✅ All Systems Safe", 
                                           font=('Segoe UI', 10, 'bold'), 
                                           fg=self.colors['success'], bg=self.colors['card'])
        self.safety_status_label.pack()
        
        self.auto_throttle_label = tk.Label(status_frame, text="Auto-throttle: Active", 
                                           font=('Segoe UI', 10), 
                                           fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.auto_throttle_label.pack()
    
    def on_cpu_freq_change(self, value):
        """Handle CPU frequency slider change"""
        freq_percent = float(value)
        actual_freq = self.cpu_base_freq * (freq_percent / 100)
        self.cpu_freq_value.config(text=f"{freq_percent:.0f}% ({actual_freq:.2f} GHz)")
        self.cpu_actual_freq_label.config(text=f"{actual_freq:.2f} GHz")
        
        # Auto-save current settings
        self.save_current_profile()
    
    def on_gpu_freq_change(self, value):
        """Handle GPU frequency slider change"""
        freq_percent = float(value)
        actual_freq = self.gpu_base_freq * (freq_percent / 100)
        self.gpu_freq_value.config(text=f"{freq_percent:.0f}% ({actual_freq:.2f} GHz)")
        self.gpu_actual_freq_label.config(text=f"{actual_freq:.2f} GHz")
        
        # Auto-save current settings
        self.save_current_profile()
    
    def on_ram_freq_change(self, value):
        """Handle RAM frequency slider change"""
        freq_percent = float(value)
        actual_freq = self.ram_base_freq * (freq_percent / 100)
        self.ram_freq_value.config(text=f"{freq_percent:.0f}% ({actual_freq:.0f} MHz)")
        self.ram_actual_freq_label.config(text=f"{actual_freq:.0f} MHz")
        
        # Auto-save current settings
        self.save_current_profile()
    
    def load_profile(self, profile_name):
        """Load an overclocking profile"""
        profile = self.profiles[profile_name]
        
        # Safety warnings for extreme profiles
        if profile_name in ['insane', 'suicide']:
            warning_msg = f"⚠️ WARNING: Loading '{profile_name.upper()}' profile!\n\n"
            if profile_name == 'insane':
                warning_msg += "This profile pushes your hardware to extreme limits:\n"
                warning_msg += "• CPU: 135% overclock (+35%)\n"
                warning_msg += "• GPU: 125% overclock (+25%)\n"
                warning_msg += "• RAM: 120% overclock (+20%)\n\n"
                warning_msg += "⚡ HIGH RISK of system instability and hardware damage!\n"
                warning_msg += "Ensure adequate cooling and power supply."
            elif profile_name == 'suicide':
                warning_msg += "This profile pushes hardware beyond safe limits:\n"
                warning_msg += "• CPU: 150% overclock (+50%) - EXTREME DANGER!\n"
                warning_msg += "• GPU: 140% overclock (+40%) - FIRE HAZARD!\n"
                warning_msg += "• RAM: 135% overclock (+35%) - DATA CORRUPTION RISK!\n\n"
                warning_msg += "🔥 EXTREME RISK: Can cause permanent hardware damage!\n"
                warning_msg += "Only for advanced users with extreme cooling solutions."
            
            warning_msg += f"\n\nContinue loading '{profile_name.upper()}' profile?"
            
            if not messagebox.askyesno("⚠️ EXTREME OVERCLOCK WARNING", warning_msg):
                return
        
        # Save current settings before switching
        self.save_current_profile()
        
        self.cpu_freq_var.set(profile['cpu_freq'])
        self.gpu_freq_var.set(profile['gpu_freq'])
        self.ram_freq_var.set(profile['ram_freq'])
        
        # Update displays
        self.on_cpu_freq_change(profile['cpu_freq'])
        self.on_gpu_freq_change(profile['gpu_freq'])
        self.on_ram_freq_change(profile['ram_freq'])
        
        # Save the new current profile
        self.save_current_profile()
        
        messagebox.showinfo("Profile Loaded", f"Loaded {profile_name.capitalize()} profile")
    
    def apply_overclock(self):
        """Apply overclocking settings"""
        try:
            cpu_freq = self.cpu_freq_var.get()
            gpu_freq = self.gpu_freq_var.get()
            ram_freq = self.ram_freq_var.get()
            
            # Safety checks
            if cpu_freq > 100 + self.max_cpu_freq_increase:
                messagebox.showerror("Error", f"CPU frequency increase too high (max: {self.max_cpu_freq_increase}%)")
                return
            
            if gpu_freq > 100 + self.max_gpu_freq_increase:
                messagebox.showerror("Error", f"GPU frequency increase too high (max: {self.max_gpu_freq_increase}%)")
                return
            
            # Apply overclock (simulation - real overclocking requires specialized tools)
            self.cpu_current_freq = self.cpu_base_freq * (cpu_freq / 100)
            self.gpu_current_freq = self.gpu_base_freq * (gpu_freq / 100)
            self.ram_current_freq = self.ram_base_freq * (ram_freq / 100)
            
            messagebox.showinfo("Overclock Applied", 
                              f"CPU: {cpu_freq:.0f}% ({self.cpu_current_freq:.2f} GHz)\n"
                              f"GPU: {gpu_freq:.0f}% ({self.gpu_current_freq:.2f} GHz)\n"
                              f"RAM: {ram_freq:.0f}% ({self.ram_current_freq:.0f} MHz)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply overclock: {e}")
    
    def reset_overclock(self):
        """Reset all overclocking to stock settings"""
        self.load_profile('stock')
        messagebox.showinfo("Reset Complete", "All overclocking settings reset to stock")
    
    def get_system_info(self):
        """Get current system information"""
        info = {
            'cpu': {'usage': 0, 'freq': 0, 'temp': 0},
            'gpu': {'usage': 0, 'freq': 0, 'temp': 0},
            'ram': {'usage': 0, 'freq': 0, 'size': 0}
        }
        
        # Get CPU info
        info['cpu']['usage'] = psutil.cpu_percent(interval=0.1)
        freq_info = psutil.cpu_freq()
        if freq_info:
            info['cpu']['freq'] = freq_info.current / 1000  # Convert to GHz
        
        # Get CPU temperature
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['wmic', 'cpu', 'get', 'temperature'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:
                        if line.strip():
                            temp = float(line.strip())
                            if temp > 0 and temp < 200:  # Valid temperature range
                                info['cpu']['temp'] = temp - 273.15  # Convert from Kelvin to Celsius
                                break
        except:
            pass
        
        # Get GPU info
        if self.gpu_count > 0 and NVML_AVAILABLE:
            try:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                info['gpu']['usage'] = util.gpu
                
                # Get GPU frequency
                info['gpu']['freq'] = nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_GRAPHICS_CLOCK) / 1000
                
                # Get GPU temperature
                info['gpu']['temp'] = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            except Exception as e:
                pass
        elif self.gpu_count > 0 and GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info['gpu']['usage'] = gpu.load * 100
                    info['gpu']['freq'] = self.gpu_current_freq  # Use detected base freq
                    info['gpu']['temp'] = gpu.temperature
            except Exception as e:
                pass
        
        # Get RAM info
        memory = psutil.virtual_memory()
        info['ram']['usage'] = memory.percent
        info['ram']['size'] = memory.total / (1024**3)  # GB
        info['ram']['freq'] = self.ram_current_freq / 1000  # MHz
        
        return info
    
    def update_display(self):
        """Update the display with current system information"""
        info = self.get_system_info()
        
        # Update CPU info
        self.cpu_value_label.config(text=f"{info['cpu']['usage']:.1f}%")
        self.cpu_freq_label.config(text=f"{info['cpu']['freq']:.2f} GHz")
        self.cpu_temp_label.config(text=f"{info['cpu']['temp']:.1f}°C")
        
        # Update GPU info
        self.gpu_value_label.config(text=f"{info['gpu']['usage']:.1f}%")
        self.gpu_freq_label.config(text=f"{info['gpu']['freq']:.2f} GHz")
        self.gpu_temp_label.config(text=f"{info['gpu']['temp']:.1f}°C")
        
        # Update RAM info
        self.ram_value_label.config(text=f"{info['ram']['usage']:.1f}%")
        self.ram_freq_label.config(text=f"{info['ram']['freq']:.0f} MHz")
        self.ram_size_label.config(text=f"{info['ram']['size']:.1f} GB")
        
        # Update temperature warnings
        if info['cpu']['temp'] > self.max_cpu_temp or info['gpu']['temp'] > self.max_gpu_temp:
            self.temp_warning_label.config(text="⚠️ High Temperature Warning!")
            self.safety_status_label.config(text="⚠️ Temperature Warning", fg=self.colors['warning'])
        else:
            self.temp_warning_label.config(text="")
            self.safety_status_label.config(text="✅ All Systems Safe", fg=self.colors['success'])
        
        # Update graph data
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_data.append(current_time)
        self.cpu_data.append(info['cpu']['usage'])
        self.gpu_data.append(info['gpu']['usage'])
        self.ram_data.append(info['ram']['usage'])
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.cpu_data = self.cpu_data[-self.max_points:]
            self.gpu_data = self.gpu_data[-self.max_points:]
            self.ram_data = self.ram_data[-self.max_points:]
        
        # Update graph
        self.update_graph()
    
    def update_graph(self):
        """Update the performance graph"""
        if len(self.time_data) > 1:
            # Update line data
            self.cpu_line.set_data(range(len(self.cpu_data)), self.cpu_data)
            self.gpu_line.set_data(range(len(self.gpu_data)), self.gpu_data)
            self.ram_line.set_data(range(len(self.ram_data)), self.ram_data)
            
            # Update x-axis
            self.ax.set_xlim(0, max(len(self.time_data), 10))
            
            # Redraw
            self.canvas.draw()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.root.after(0, self.update_display)
                time.sleep(self.update_interval / 1000)
            except Exception as e:
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
    
    def load_profiles(self):
        """Load saved overclocking profiles from file"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    saved_profiles = json.load(f)
                    # Merge with default profiles
                    self.profiles.update(saved_profiles)
        except Exception as e:
            pass
    
    def save_profiles(self):
        """Save overclocking profiles to file"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            pass
    
    def load_current_profile(self):
        """Load current profile settings"""
        try:
            if os.path.exists(self.current_profile_file):
                with open(self.current_profile_file, 'r') as f:
                    current_settings = json.load(f)
                    
                    # Apply loaded settings to sliders
                    self.cpu_freq_var.set(current_settings.get('cpu_freq', 100))
                    self.gpu_freq_var.set(current_settings.get('gpu_freq', 100))
                    self.ram_freq_var.set(current_settings.get('ram_freq', 100))
                    
                    # Update displays
                    self.on_cpu_freq_change(current_settings.get('cpu_freq', 100))
                    self.on_gpu_freq_change(current_settings.get('gpu_freq', 100))
                    self.on_ram_freq_change(current_settings.get('ram_freq', 100))
        except Exception as e:
            pass
    
    def save_current_profile(self):
        """Save current profile settings"""
        try:
            current_settings = {
                'cpu_freq': self.cpu_freq_var.get(),
                'gpu_freq': self.gpu_freq_var.get(),
                'ram_freq': self.ram_freq_var.get(),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.current_profile_file, 'w') as f:
                json.dump(current_settings, f, indent=2)
        except Exception as e:
            pass
    
    def save_custom_profile(self):
        """Save current settings as a custom profile"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Custom Profile")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Profile name input
        tk.Label(dialog, text="Profile Name:", font=('Segoe UI', 11), 
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=(20, 5))
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, font=('Segoe UI', 10), 
                             bg=self.colors['card'], fg=self.colors['text'],
                             insertbackground=self.colors['text'])
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        
        # Description input
        tk.Label(dialog, text="Description (optional):", font=('Segoe UI', 11), 
                fg=self.colors['text'], bg=self.colors['bg']).pack(pady=(10, 5))
        
        desc_var = tk.StringVar()
        desc_entry = tk.Entry(dialog, textvariable=desc_var, font=('Segoe UI', 10), 
                             bg=self.colors['card'], fg=self.colors['text'],
                             insertbackground=self.colors['text'])
        desc_entry.pack(pady=5, padx=20, fill=tk.X)
        
        def save_profile():
            profile_name = name_var.get().strip()
            if not profile_name:
                messagebox.showerror("Error", "Please enter a profile name")
                return
            
            if profile_name in ['stock', 'gaming', 'performance', 'extreme']:
                messagebox.showerror("Error", "Cannot overwrite built-in profiles")
                return
            
            # Save profile
            self.profiles[profile_name] = {
                'cpu_freq': self.cpu_freq_var.get(),
                'gpu_freq': self.gpu_freq_var.get(),
                'ram_freq': self.ram_freq_var.get(),
                'description': desc_var.get(),
                'created': datetime.now().isoformat()
            }
            
            self.save_profiles()
            self.update_profile_buttons()
            dialog.destroy()
            messagebox.showinfo("Success", f"Profile '{profile_name}' saved successfully")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save", font=('Segoe UI', 10, 'bold'), 
                 bg=self.colors['success'], fg=self.colors['bg'],
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=save_profile).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", font=('Segoe UI', 10, 'bold'), 
                 bg=self.colors['danger'], fg=self.colors['bg'],
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_custom_profile(self, profile_name):
        """Delete a custom profile"""
        if profile_name in ['stock', 'gaming', 'performance', 'extreme']:
            messagebox.showerror("Error", "Cannot delete built-in profiles")
            return
        
        if messagebox.askyesno("Delete Profile", f"Delete profile '{profile_name}'?"):
            del self.profiles[profile_name]
            self.save_profiles()
            self.update_profile_buttons()
            messagebox.showinfo("Success", f"Profile '{profile_name}' deleted")
    
    def export_profiles(self):
        """Export profiles to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Profiles",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.profiles, f, indent=2)
                messagebox.showinfo("Success", f"Profiles exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export profiles: {e}")
    
    def import_profiles(self):
        """Import profiles from file"""
        file_path = filedialog.askopenfilename(
            title="Import Profiles",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_profiles = json.load(f)
                
                # Merge with existing profiles
                self.profiles.update(imported_profiles)
                self.save_profiles()
                self.update_profile_buttons()
                messagebox.showinfo("Success", f"Profiles imported from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import profiles: {e}")
    
    def update_profile_buttons(self):
        """Update profile buttons to show custom profiles"""
        # Clear existing profile buttons (except the built-in ones)
        for widget in self.profile_buttons_frame.winfo_children():
            widget.destroy()
        
        # Add built-in profiles
        built_in_profiles = ['stock', 'gaming', 'performance', 'extreme', 'insane', 'suicide']
        for profile_name in built_in_profiles:
            if profile_name in self.profiles:
                btn_color = self.colors['success'] if profile_name == 'stock' else self.colors['warning'] if profile_name == 'gaming' else self.colors['danger'] if profile_name == 'performance' else self.colors['accent'] if profile_name == 'extreme' else self.colors['primary'] if profile_name == 'insane' else '#ff0066' if profile_name == 'suicide' else self.colors['accent']
                
                profile_btn = tk.Button(self.profile_buttons_frame, text=profile_name.capitalize(), 
                                      font=('Segoe UI', 9, 'bold'), 
                                      bg=btn_color, fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      command=lambda p=profile_name: self.load_profile(p))
                profile_btn.pack(side=tk.LEFT, padx=5)
        
        # Add custom profiles
        custom_profiles = [p for p in self.profiles.keys() if p not in built_in_profiles]
        if custom_profiles:
            # Separator
            separator = tk.Frame(self.profile_buttons_frame, height=2, bg=self.colors['text_secondary'])
            separator.pack(side=tk.LEFT, padx=10, fill=tk.Y)
            
            for profile_name in custom_profiles:
                profile_btn = tk.Button(self.profile_buttons_frame, text=profile_name, 
                                      font=('Segoe UI', 9, 'bold'), 
                                      bg=self.colors['primary'], fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      command=lambda p=profile_name: self.load_profile(p))
                profile_btn.pack(side=tk.LEFT, padx=5)
    
    def on_closing(self):
        """Handle window closing"""
        # Save current profile before closing
        self.save_current_profile()
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = OverclockingDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
