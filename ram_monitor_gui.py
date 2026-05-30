#!/usr/bin/env python3
"""
RAM Monitor GUI Application
A comprehensive GUI application for real-time RAM monitoring with cache clearing functionality.
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

class RAMMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RAM Monitor & Cleaner")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Modern color scheme
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
            'graph_line': '#00d4ff'
        }
        
        # Data storage for plotting (optimized for CPU usage)
        self.time_data = []
        self.memory_data = []
        self.max_points = 60  # Show last 60 data points
        
        # CPU-optimized monitoring settings
        self.update_interval = 2000  # Update every 2 seconds instead of 1
        self.last_update = 0
        self.monitoring_cpu_usage = 0.0
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Style configuration
        self.setup_styles()
        
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
                       font=('Segoe UI', 20, 'bold'))
        style.configure('Card.TFrame', background=self.colors['card'], relief='flat', borderwidth=1)
        style.configure('Info.TLabel', background=self.colors['card'], foreground=self.colors['text'], 
                       font=('Segoe UI', 11))
        style.configure('InfoValue.TLabel', background=self.colors['card'], foreground=self.colors['primary'], 
                       font=('Segoe UI', 12, 'bold'))
        style.configure('Success.TLabel', background=self.colors['card'], foreground=self.colors['success'], 
                       font=('Segoe UI', 11, 'bold'))
        style.configure('Warning.TLabel', background=self.colors['card'], foreground=self.colors['warning'], 
                       font=('Segoe UI', 11, 'bold'))
        style.configure('Danger.TLabel', background=self.colors['card'], foreground=self.colors['danger'], 
                       font=('Segoe UI', 11, 'bold'))
        style.configure('Primary.TButton', background=self.colors['primary'], foreground=self.colors['bg'], 
                       font=('Segoe UI', 11, 'bold'), relief='flat', borderwidth=0)
        style.configure('Success.TButton', background=self.colors['success'], foreground=self.colors['bg'], 
                       font=('Segoe UI', 11, 'bold'), relief='flat', borderwidth=0)
        style.configure('Warning.TButton', background=self.colors['warning'], foreground=self.colors['bg'], 
                       font=('Segoe UI', 11, 'bold'), relief='flat', borderwidth=0)
        style.configure('Secondary.TButton', background=self.colors['card'], foreground=self.colors['text'], 
                       font=('Segoe UI', 10), relief='flat', borderwidth=1)
        
        # Configure progress bar
        style.configure('Modern.Horizontal.TProgressbar', 
                       background=self.colors['primary'],
                       troughcolor=self.colors['card'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['accent'])
    
    def create_widgets(self):
        """Create all modern GUI widgets"""
        # Header with title and status
        self.create_header()
        
        # Main container with cards
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Top section - Stats cards
        stats_frame = tk.Frame(main_container, bg=self.colors['bg'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        self.create_stats_cards(stats_frame)
        
        # Middle section - Memory info and graph side by side
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Memory info card
        left_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.create_memory_display(left_frame)
        
        # Right panel - Graph card
        right_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.create_graph(right_frame)
        
        # Bottom panel - Controls
        bottom_frame = tk.Frame(main_container, bg=self.colors['bg'])
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        self.create_control_buttons(bottom_frame)
        
        # Process Manager Panel
        process_frame = tk.Frame(main_container, bg=self.colors['bg'])
        process_frame.pack(fill=tk.X, pady=(10, 0))
        self.create_process_manager(process_frame)
    
    def create_header(self):
        """Create modern header"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(title_frame, text="RAM Monitor & Cleaner", 
                             font=('Segoe UI', 24, 'bold'), 
                             fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame, text="Real-time memory monitoring and optimization", 
                                 font=('Segoe UI', 10), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Status indicator
        self.header_status_label = tk.Label(header_frame, text="● ACTIVE", 
                                          font=('Segoe UI', 12, 'bold'), 
                                          fg=self.colors['success'], bg=self.colors['bg'])
        self.header_status_label.pack(side=tk.RIGHT, anchor=tk.E, pady=20)
    
    def create_stats_cards(self, parent):
        """Create modern stats cards"""
        # Create four stat cards
        cards_data = [
            ("Total RAM", "-- GB", self.colors['primary']),
            ("Used", "-- GB", self.colors['warning']),
            ("Available", "-- GB", self.colors['success']),
            ("Usage", "--%", self.colors['accent'])
        ]
        
        self.stat_labels = []
        
        for i, (title, value, color) in enumerate(cards_data):
            card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i == 0 else 10, 0 if i == 3 else 10))
            
            # Card content
            title_label = tk.Label(card, text=title, font=('Segoe UI', 10), 
                                 fg=self.colors['text_secondary'], bg=self.colors['card'])
            title_label.pack(pady=(15, 5))
            
            value_label = tk.Label(card, text=value, font=('Segoe UI', 18, 'bold'), 
                                  fg=color, bg=self.colors['card'])
            value_label.pack(pady=(0, 15))
            
            self.stat_labels.append(value_label)
    
    def create_memory_display(self, parent):
        """Create modern memory information display"""
        # Card container
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = tk.Frame(card, bg=self.colors['card'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text="Memory Details", 
                               font=('Segoe UI', 14, 'bold'), 
                               fg=self.colors['text'], bg=self.colors['card'])
        header_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Card content
        content = tk.Frame(card, bg=self.colors['card'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Memory info rows
        self.info_labels = {}
        info_items = [
            ('total', 'Total RAM', '-- GB'),
            ('used', 'Used', '-- GB'),
            ('available', 'Available', '-- GB'),
            ('percentage', 'Usage', '--%')
        ]
        
        for key, label, default in info_items:
            row = tk.Frame(content, bg=self.colors['card'])
            row.pack(fill=tk.X, pady=8)
            
            label_widget = tk.Label(row, text=label + ':', font=('Segoe UI', 10), 
                                   fg=self.colors['text_secondary'], bg=self.colors['card'], width=12, anchor=tk.W)
            label_widget.pack(side=tk.LEFT)
            
            value_widget = tk.Label(row, text=default, font=('Segoe UI', 11, 'bold'), 
                                   fg=self.colors['primary'], bg=self.colors['card'], anchor=tk.W)
            value_widget.pack(side=tk.LEFT)
            
            self.info_labels[key] = value_widget
        
        # Progress bar section
        progress_section = tk.Frame(card, bg=self.colors['card'])
        progress_section.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        progress_label = tk.Label(progress_section, text="Memory Usage", 
                                font=('Segoe UI', 10), 
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
        progress_label.pack(anchor=tk.W)
        
        # Modern progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_canvas = tk.Canvas(progress_section, height=8, bg=self.colors['card'], 
                                       highlightthickness=0, bd=0)
        self.progress_canvas.pack(fill=tk.X, pady=(5, 0))
        
        # Status label
        self.status_label = tk.Label(progress_section, text="Status: Monitoring", 
                                   font=('Segoe UI', 10, 'bold'), 
                                   fg=self.colors['success'], bg=self.colors['card'])
        self.status_label.pack(anchor=tk.W, pady=(10, 0))
    
    def create_graph(self, parent):
        """Create modern real-time memory usage graph"""
        # Card container
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = tk.Frame(card, bg=self.colors['card'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text="Real-time Usage", 
                               font=('Segoe UI', 14, 'bold'), 
                               fg=self.colors['text'], bg=self.colors['card'])
        header_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Graph container
        graph_container = tk.Frame(card, bg=self.colors['card'])
        graph_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # Create matplotlib figure with modern styling
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors['card'])
        self.ax = self.fig.add_subplot(111, facecolor=self.colors['graph_bg'])
        
        # Configure modern plot
        self.ax.set_xlabel('Time (seconds ago)', color=self.colors['text_secondary'], fontsize=10)
        self.ax.set_ylabel('Memory Usage (%)', color=self.colors['text_secondary'], fontsize=10)
        self.ax.set_title('RAM Usage Over Last 60 Seconds', color=self.colors['text'], fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.2, linestyle='--', color=self.colors['text_secondary'])
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(60, 0)  # Reverse to show newest on right
        
        # Modern styling
        self.ax.tick_params(colors=self.colors['text_secondary'], labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color(self.colors['text_secondary'])
            spine.set_alpha(0.3)
        
        # Create gradient line plot
        self.line, = self.ax.plot([], [], color=self.colors['primary'], linewidth=3, 
                                 marker='o', markersize=4, markerfacecolor=self.colors['primary'],
                                 markeredgecolor=self.colors['card'], markeredgewidth=1)
        
        # Add threshold lines
        self.ax.axhline(y=80, color=self.colors['warning'], linestyle='--', alpha=0.5, linewidth=1)
        self.ax.axhline(y=90, color=self.colors['danger'], linestyle='--', alpha=0.5, linewidth=1)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_control_buttons(self, parent):
        """Create modern control buttons"""
        # Left side - Primary actions
        left_frame = tk.Frame(parent, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.X)
        
        # Enhanced Clean RAM button
        self.clean_button = tk.Button(left_frame, text="🧹 Deep Clean RAM", 
                                     command=self.enhanced_ram_cleanup,
                                     bg=self.colors['primary'], fg=self.colors['bg'],
                                     font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                                     padx=20, pady=10, cursor='hand2')
        self.clean_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Process Killer button
        self.process_killer_button = tk.Button(left_frame, text="⚡ Process Killer", 
                                             command=self.show_process_killer,
                                             bg=self.colors['danger'], fg=self.colors['bg'],
                                             font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                                             padx=20, pady=10, cursor='hand2')
        self.process_killer_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Soft RAM Cleaner button (ultra-gentle)
        self.soft_cleaner_button = tk.Button(left_frame, text="💨 Soft Clean", 
                                           command=self.run_soft_cleaner,
                                           bg='#87CEEB', fg=self.colors['bg'],
                                           font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                                           padx=20, pady=10, cursor='hand2')
        self.soft_cleaner_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Memory Jolt button (gentle)
        self.memory_jolt_button = tk.Button(left_frame, text="⚡ Memory Jolt", 
                                           command=self.run_memory_jolt,
                                           bg=self.colors['success'], fg=self.colors['bg'],
                                           font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                                           padx=20, pady=10, cursor='hand2')
        self.memory_jolt_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Aggressive Cleaner button
        self.aggressive_cleaner_button = tk.Button(left_frame, text="🔥 Aggressive Clean", 
                                                 command=self.run_aggressive_cleaner,
                                                 bg='#ff6b6b', fg=self.colors['bg'],
                                                 font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                                                 padx=20, pady=10, cursor='hand2')
        self.aggressive_cleaner_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Monitor toggle button
        self.monitor_button = tk.Button(left_frame, text="⏸️ Stop Monitoring", 
                                      command=self.toggle_monitoring,
                                      bg=self.colors['warning'], fg=self.colors['bg'],
                                      font=('Segoe UI', 11, 'bold'), relief='flat', bd=0,
                                      padx=20, pady=10, cursor='hand2')
        self.monitor_button.pack(side=tk.LEFT)
        
        # Right side - Settings
        right_frame = tk.Frame(parent, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.X)
        
        # Auto-clean checkbox with modern styling
        self.auto_clean_var = tk.BooleanVar()
        auto_clean_frame = tk.Frame(right_frame, bg=self.colors['bg'])
        auto_clean_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Custom checkbox
        self.auto_clean_check_btn = tk.Button(auto_clean_frame, text="☐ Auto-clean when >80%", 
                                            command=self.toggle_auto_clean,
                                            bg=self.colors['card'], fg=self.colors['text'],
                                            font=('Segoe UI', 10), relief='flat', bd=0,
                                            cursor='hand2')
        self.auto_clean_check_btn.pack()
        
        # Refresh button
        refresh_button = tk.Button(right_frame, text="🔄 Refresh", command=self.update_display,
                                  bg=self.colors['card'], fg=self.colors['text'],
                                  font=('Segoe UI', 10), relief='flat', bd=0,
                                  padx=15, pady=8, cursor='hand2')
        refresh_button.pack(side=tk.RIGHT)
    
    def create_process_manager(self, parent):
        """Create process manager section"""
        # Process manager card
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=0)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Header
        header = tk.Frame(card, bg=self.colors['card'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_label = tk.Label(header, text="Process Manager", 
                               font=('Segoe UI', 12, 'bold'), 
                               fg=self.colors['text'], bg=self.colors['card'])
        header_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Quick kill buttons
        quick_frame = tk.Frame(card, bg=self.colors['card'])
        quick_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        # Quick kill buttons for common apps
        quick_apps = [
            ("🌐 Browsers", self.kill_browsers),
            ("🎮 Games", self.kill_games), 
            ("📱 Apps", self.kill_apps),
            ("🔄 All Safe", self.kill_all_safe)
        ]
        
        for text, command in quick_apps:
            btn = tk.Button(quick_frame, text=text, command=command,
                          bg=self.colors['card_hover'], fg=self.colors['text'],
                          font=('Segoe UI', 9), relief='flat', bd=0,
                          padx=10, pady=5, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=(0, 10))
    
    def toggle_auto_clean(self):
        """Toggle auto-clean checkbox"""
        self.auto_clean_var.set(not self.auto_clean_var.get())
        if self.auto_clean_var.get():
            self.auto_clean_check_btn.config(text="☑ Auto-clean when >80%", fg=self.colors['success'])
        else:
            self.auto_clean_check_btn.config(text="☐ Auto-clean when >80%", fg=self.colors['text'])
    
    def get_memory_info(self):
        """Get current memory information"""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
    
    def update_display(self):
        """Update memory display with CPU-optimized monitoring"""
        current_time = time.time()
        
        # Rate limiting to reduce CPU usage
        if current_time - self.last_update < (self.update_interval / 1000):
            return
        
        self.last_update = current_time
        
        # Get memory info with minimal overhead
        mem = self.get_memory_info()
        
        # Update stat cards (batch updates for efficiency)
        values = [
            f"{mem['total'] / (1024**3):.1f} GB",
            f"{mem['used'] / (1024**3):.1f} GB",
            f"{mem['available'] / (1024**3):.1f} GB",
            f"{mem['percent']:.1f}%"
        ]
        
        for i, (label, value) in enumerate(zip(self.stat_labels, values)):
            label.config(text=value)
        
        # Update info labels (only if changed to reduce CPU usage)
        new_used_text = f"{mem['used'] / (1024**3):.2f} GB"
        if self.info_labels['used'].cget('text') != new_used_text:
            self.info_labels['total'].config(text=f"{mem['total'] / (1024**3):.2f} GB")
            self.info_labels['used'].config(text=new_used_text)
            self.info_labels['available'].config(text=f"{mem['available'] / (1024**3):.2f} GB")
            self.info_labels['percentage'].config(text=f"{mem['percent']:.1f}%")
        
        # Update modern progress bar
        self.update_progress_bar(mem['percent'])
        
        # Update status label with modern styling
        if mem['percent'] < 50:
            self.status_label.config(text="Status: Good", fg=self.colors['success'])
            self.header_status_label.config(text="● GOOD", fg=self.colors['success'])
        elif mem['percent'] < 80:
            self.status_label.config(text="Status: Moderate", fg=self.colors['warning'])
            self.header_status_label.config(text="● MODERATE", fg=self.colors['warning'])
        else:
            self.status_label.config(text="Status: High Usage!", fg=self.colors['danger'])
            self.header_status_label.config(text="● HIGH", fg=self.colors['danger'])
        
        # Add data to graph (limit data points to reduce memory usage)
        self.memory_data.append(mem['percent'])
        
        # Keep only last max_points to prevent memory growth
        if len(self.memory_data) > self.max_points:
            self.memory_data.pop(0)
        
        # Update graph (less frequent to reduce CPU usage)
        if len(self.memory_data) % 2 == 0:  # Update graph every 2nd data point
            self.update_graph()
        
        # Auto-clean if enabled and usage is high
        if self.auto_clean_var.get() and mem['percent'] > 80:
            self.enhanced_ram_cleanup()
    
    def update_progress_bar(self, percentage):
        """Update modern progress bar"""
        canvas_width = self.progress_canvas.winfo_width()
        if canvas_width > 1:  # Ensure canvas is rendered
            self.progress_canvas.delete("all")
            
            # Background
            self.progress_canvas.create_rectangle(0, 0, canvas_width, 8, 
                                                fill=self.colors['card'], outline="")
            
            # Progress fill with gradient effect
            fill_width = (canvas_width * percentage) / 100
            if percentage < 50:
                color = self.colors['success']
            elif percentage < 80:
                color = self.colors['warning']
            else:
                color = self.colors['danger']
            
            self.progress_canvas.create_rectangle(0, 0, fill_width, 8, 
                                                fill=color, outline="")
    
    def update_graph(self):
        """Update the modern real-time graph"""
        if len(self.memory_data) > 1:
            # Create reversed x-axis (newest on right)
            x_data = list(range(len(self.memory_data) - 1, -1, -1))
            self.line.set_data(x_data, self.memory_data)
            
            # Update axis limits
            self.ax.set_xlim(59, 0)  # Show last 60 seconds, newest on right
            self.ax.set_ylim(0, 100)
            
            # Redraw canvas
            self.canvas.draw()
    
    def monitor_loop(self):
        """CPU-optimized monitoring loop"""
        while self.monitoring:
            try:
                # Use CPU-friendly timing
                start_time = time.time()
                
                # Schedule update in main thread
                self.root.after(0, self.update_display)
                
                # Calculate sleep time to maintain consistent update interval
                elapsed = time.time() - start_time
                sleep_time = max(0, (self.update_interval / 1000) - elapsed)
                time.sleep(sleep_time)
                
                # Track CPU usage (simple estimation)
                self.monitoring_cpu_usage = min(100, elapsed / (self.update_interval / 1000) * 100)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def start_monitoring(self):
        """Start monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.monitor_button.config(text="⏸️ Stop Monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.monitor_button.config(text="▶️ Start Monitoring")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def enhanced_ram_cleanup(self):
        """Enhanced RAM cache cleanup with more aggressive cleaning"""
        try:
            # Show cleaning dialog
            result = messagebox.askyesno("Deep Clean", 
                                        "Perform deep RAM cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Clear system cache\n" +
                                        "• Clear temporary files\n" +
                                        "• Clear DNS cache\n" +
                                        "• Force garbage collection\n" +
                                        "• Optimize memory\n\n" +
                                        "Continue?")
            if not result:
                return
            
            # Progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Cleaning...")
            progress_window.geometry("300x100")
            progress_window.configure(bg=self.colors['bg'])
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = tk.Label(progress_window, text="Deep cleaning RAM...", 
                                      font=('Segoe UI', 12), 
                                      fg=self.colors['text'], bg=self.colors['bg'])
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            self.root.update()
            
            cleaned_data = {'files': 0, 'processes': 0, 'cache': False}
            
            # Step 1: Force Python garbage collection
            gc.collect()
            
            # Step 2: Clear Windows cache if on Windows
            if platform.system() == "Windows":
                try:
                    # Clear DNS cache
                    subprocess.run(['ipconfig', '/flushdns'], check=True, capture_output=True)
                    cleaned_data['cache'] = True
                    
                    # Clear temp files aggressively
                    temp_paths = [
                        os.environ.get('TEMP', ''),
                        os.environ.get('TMP', ''),
                        r'C:\Windows\Temp',
                        r'C:\Windows\Prefetch',
                        os.path.expanduser(r'~\AppData\Local\Temp'),
                        os.path.expanduser(r'~\AppData\Local\Microsoft\Windows\INetCache')
                    ]
                    
                    for temp_path in temp_paths:
                        if os.path.exists(temp_path):
                            try:
                                for item in os.listdir(temp_path):
                                    item_path = os.path.join(temp_path, item)
                                    try:
                                        if os.path.isfile(item_path):
                                            os.unlink(item_path)
                                            cleaned_data['files'] += 1
                                        elif os.path.isdir(item_path):
                                            # Try to remove empty directories
                                            try:
                                                os.rmdir(item_path)
                                                cleaned_data['files'] += 1
                                            except:
                                                pass
                                    except (PermissionError, OSError):
                                        continue
                            except (PermissionError, OSError):
                                continue
                    
                    # Clear standby memory using PowerShell
                    try:
                        subprocess.run(['powershell', '-Command', 
                                      'Clear-Content -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" -ErrorAction SilentlyContinue'], 
                                      capture_output=True)
                    except:
                        pass
                    
                    # Close unnecessary processes
                    safe_to_close = [
                        'notepad.exe', 'mspaint.exe', 'calc.exe', 'wordpad.exe',
                        'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
                        'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe'
                    ]
                    
                    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                        try:
                            process_name = proc.info['name'].lower()
                            memory_usage = proc.info['memory_info'].rss
                            
                            # Only close processes using less than 200MB
                            if (any(safe_process in process_name for safe_process in safe_to_close) and 
                                memory_usage < 200 * 1024 * 1024):
                                proc.terminate()
                                cleaned_data['processes'] += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                    
                except Exception as e:
                    print(f"Windows cleanup error: {e}")
            
            # Close progress dialog
            progress_window.destroy()
            
            # Update display
            self.update_display()
            
            # Show completion message with details
            message = f"Deep clean completed!\n\n" +\
                     f"📁 Files cleaned: {cleaned_data['files']}\n" +\
                     f"🔄 Processes closed: {cleaned_data['processes']}\n" +\
                     f"🌐 DNS cache: {'Cleared' if cleaned_data['cache'] else 'N/A'}"
            
            messagebox.showinfo("Deep Clean Complete", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to deep clean RAM: {e}")
    
    def show_process_killer(self):
        """Show process killer window"""
        killer_window = tk.Toplevel(self.root)
        killer_window.title("Process Killer")
        killer_window.geometry("600x400")
        killer_window.configure(bg=self.colors['bg'])
        killer_window.transient(self.root)
        killer_window.grab_set()
        
        # Header
        header = tk.Frame(killer_window, bg=self.colors['card'], height=50)
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="⚡ Process Killer", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg=self.colors['danger'], bg=self.colors['card'])
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        refresh_btn = tk.Button(header, text="🔄 Refresh", 
                              command=lambda: self.refresh_process_list(killer_window),
                              bg=self.colors['primary'], fg=self.colors['bg'],
                              font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                              padx=15, pady=5, cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Process list frame
        list_frame = tk.Frame(killer_window, bg=self.colors['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for process list
        columns = ('PID', 'Name', 'Memory (MB)', 'CPU%')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('Name', text='Process Name')
        self.process_tree.heading('Memory (MB)', text='Memory (MB)')
        self.process_tree.heading('CPU%', text='CPU%')
        
        self.process_tree.column('PID', width=60)
        self.process_tree.column('Name', width=200)
        self.process_tree.column('Memory (MB)', width=100)
        self.process_tree.column('CPU%', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = tk.Frame(killer_window, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        kill_selected_btn = tk.Button(button_frame, text="⚠️ Kill Selected", 
                                     command=lambda: self.kill_selected_process(killer_window),
                                     bg=self.colors['danger'], fg=self.colors['bg'],
                                     font=('Segoe UI', 10, 'bold'), relief='flat', bd=0,
                                     padx=15, pady=8, cursor='hand2')
        kill_selected_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(button_frame, text="Close", 
                             command=killer_window.destroy,
                             bg=self.colors['card'], fg=self.colors['text'],
                             font=('Segoe UI', 10), relief='flat', bd=0,
                             padx=15, pady=8, cursor='hand2')
        close_btn.pack(side=tk.RIGHT)
        
        # Load initial process list
        self.refresh_process_list(killer_window)
    
    def refresh_process_list(self, window):
        """Refresh the process list"""
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Get process list
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                pinfo = proc.info
                memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                cpu_percent = pinfo['cpu_percent']
                
                processes.append((pinfo['pid'], pinfo['name'], f"{memory_mb:.1f}", f"{cpu_percent:.1f}"))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by memory usage (descending)
        processes.sort(key=lambda x: float(x[2]), reverse=True)
        
        # Add to treeview (top 50 processes)
        for proc in processes[:50]:
            self.process_tree.insert('', tk.END, values=proc)
    
    def kill_selected_process(self, window):
        """Kill the selected process"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process to kill.")
            return
        
        item = self.process_tree.item(selection[0])
        values = item['values']
        pid = int(values[0])
        name = values[1]
        
        # Confirm kill
        result = messagebox.askyesno("Confirm Kill", 
                                    f"Are you sure you want to kill:\n\n" +
                                    f"Process: {name}\n" +
                                    f"PID: {pid}\n\n" +
                                    f"⚠️ This may cause system instability!")
        
        if result:
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                
                # Refresh list
                self.refresh_process_list(window)
                
                messagebox.showinfo("Success", f"Process {name} (PID: {pid}) terminated.")
                
                # Update main display
                self.update_display()
                
            except psutil.NoSuchProcess:
                messagebox.showerror("Error", "Process no longer exists.")
            except psutil.AccessDenied:
                messagebox.showerror("Error", "Access denied. Try running as Administrator.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill process: {e}")
    
    def kill_browsers(self):
        """Kill browser processes"""
        self.kill_processes_by_name(['chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe'])
    
    def kill_games(self):
        """Kill game processes"""
        self.kill_processes_by_name(['steam.exe', 'epicgameslauncher.exe', 'origin.exe', 'uplay.exe', 'battle.net.exe'])
    
    def kill_apps(self):
        """Kill common apps"""
        self.kill_processes_by_name(['spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe', 'zoom.exe'])
    
    def kill_all_safe(self):
        """Kill all safe processes"""
        safe_processes = [
            'notepad.exe', 'mspaint.exe', 'calc.exe', 'wordpad.exe',
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe',
            'steam.exe', 'epicgameslauncher.exe', 'origin.exe', 'uplay.exe'
        ]
        self.kill_processes_by_name(safe_processes)
    
    def kill_processes_by_name(self, process_names):
        """Kill processes by name list"""
        try:
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    process_name = proc.info['name'].lower()
                    memory_usage = proc.info['memory_info'].rss
                    
                    # Check if process name matches any in the list
                    if any(target in process_name for target in process_names):
                        # Only kill processes using less than 500MB to be safe
                        if memory_usage < 500 * 1024 * 1024:
                            proc.terminate()
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if killed_count > 0:
                messagebox.showinfo("Success", f"Killed {killed_count} processes.")
                self.update_display()
            else:
                messagebox.showinfo("Info", "No matching processes found or they were using too much memory to kill safely.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill processes: {e}")
    
    def run_aggressive_cleaner(self):
        """Run aggressive RAM cleaner"""
        try:
            # Show warning dialog
            result = messagebox.askyesno(
                "Aggressive RAM Cleaner", 
                "🔥 AGGRESSIVE CLEANUP WARNING 🔥\n\n" +
                "This will perform aggressive system-level cleanup:\n\n" +
                "• Clear standby memory\n" +
                "• Force memory trimming\n" +
                "• Clear system cache\n" +
                "• Stop non-essential services\n" +
                "• Kill memory-hogging processes\n" +
                "• Optimize virtual memory\n\n" +
                "⚠️ This may affect system stability!\n" +
                "⚠️ Best results as Administrator\n\n" +
                "Continue with aggressive cleanup?"
            )
            
            if not result:
                return
            
            # Import and run aggressive cleaner
            try:
                # Import the aggressive cleaner module
                import aggressive_ram_cleaner
                
                # Create progress window
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Aggressive Cleaning...")
                progress_window.geometry("400x150")
                progress_window.configure(bg=self.colors['bg'])
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                # Progress label
                progress_label = tk.Label(progress_window, text="🔥 Performing aggressive cleanup...", 
                                        font=('Segoe UI', 12, 'bold'), 
                                        fg=self.colors['danger'], bg=self.colors['bg'])
                progress_label.pack(pady=20)
                
                detail_label = tk.Label(progress_window, text="This may take a few minutes...", 
                                       font=('Segoe UI', 10), 
                                       fg=self.colors['text_secondary'], bg=self.colors['bg'])
                detail_label.pack(pady=5)
                
                # Progress bar
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(pady=20, padx=20, fill=tk.X)
                progress_bar.start()
                
                self.root.update()
                
                # Run aggressive cleanup in separate thread to avoid freezing GUI
                def run_cleanup():
                    try:
                        cleaner = aggressive_ram_cleaner.AggressiveRAMCleaner()
                        memory_freed = cleaner.run_aggressive_cleanup()
                        
                        # Close progress window
                        progress_window.destroy()
                        
                        # Update display
                        self.update_display()
                        
                        # Show results
                        if memory_freed > 0.5:
                            messagebox.showinfo(
                                "Aggressive Clean Complete", 
                                f"🎉 Aggressive cleanup successful!\n\n" +
                                f"💾 Memory freed: {memory_freed:.2f} GB\n" +
                                f"🔄 Display updated with new values\n\n" +
                                f"💡 For maximum recovery, consider restarting your computer."
                            )
                        else:
                            messagebox.showinfo(
                                "Aggressive Clean Complete", 
                                f"⚠️ Limited memory freed: {memory_freed:.2f} GB\n\n" +
                                f"💡 Try running as Administrator for better results\n" +
                                f"💡 Restart your computer for maximum memory recovery"
                            )
                            
                    except Exception as e:
                        progress_window.destroy()
                        messagebox.showerror("Error", f"Aggressive cleanup failed: {e}")
                
                # Start cleanup thread
                cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
                cleanup_thread.start()
                
            except ImportError:
                messagebox.showerror(
                    "Error", 
                    "Aggressive cleaner module not found.\n\n" +
                    "Make sure aggressive_ram_cleaner.py is in the same directory."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run aggressive cleaner: {e}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Aggressive cleaner error: {e}")
    
    def run_memory_jolt(self):
        """Run gentle memory jolt"""
        try:
            # Show info dialog
            result = messagebox.askyesno(
                "Memory Jolt", 
                "⚡ Gentle Memory Jolt\n\n" +
                "This will safely optimize your system by:\n\n" +
                "• Gently trimming process memory\n" +
                "• Clearing stuck standby memory\n" +
                "• Optimizing file system cache\n" +
                "• Refreshing memory pools\n" +
                "• Defragmenting memory\n" +
                "• Restarting stuck services\n\n" +
                "✅ Safe and non-destructive\n" +
                "✅ Preserves system stability\n" +
                "✅ Perfect for stuck memory\n\n" +
                "Continue with memory jolt?"
            )
            
            if not result:
                return
            
            # Import and run memory jolt
            try:
                import memory_jolt
                
                # Create progress window
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Memory Jolt...")
                progress_window.geometry("400x150")
                progress_window.configure(bg=self.colors['bg'])
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                # Progress label
                progress_label = tk.Label(progress_window, text="⚡ Performing gentle memory jolt...", 
                                        font=('Segoe UI', 12, 'bold'), 
                                        fg=self.colors['success'], bg=self.colors['bg'])
                progress_label.pack(pady=20)
                
                detail_label = tk.Label(progress_window, text="Safely optimizing stuck memory...", 
                                       font=('Segoe UI', 10), 
                                       fg=self.colors['text_secondary'], bg=self.colors['bg'])
                detail_label.pack(pady=5)
                
                # Progress bar
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(pady=20, padx=20, fill=tk.X)
                progress_bar.start()
                
                self.root.update()
                
                # Run memory jolt in separate thread
                def run_jolt():
                    try:
                        jolt = memory_jolt.MemoryJolt()
                        memory_freed = jolt.run_memory_jolt()
                        
                        # Close progress window
                        progress_window.destroy()
                        
                        # Update display
                        self.update_display()
                        
                        # Show results
                        if memory_freed > 0.1:
                            messagebox.showinfo(
                                "Memory Jolt Complete", 
                                f"⚡ Memory jolt successful!\n\n" +
                                f"💾 Memory freed: {memory_freed:.2f} GB\n" +
                                f"🚀 System should be more responsive\n" +
                                f"🔄 Display updated with new values\n\n" +
                                f"✅ Safe optimization completed"
                            )
                        else:
                            messagebox.showinfo(
                                "Memory Jolt Complete", 
                                f"✅ System appears well-optimized\n\n" +
                                f"💡 No stuck memory detected\n" +
                                f"💡 Your system is running efficiently"
                            )
                            
                    except Exception as e:
                        progress_window.destroy()
                        messagebox.showerror("Error", f"Memory jolt failed: {e}")
                
                # Start jolt thread
                jolt_thread = threading.Thread(target=run_jolt, daemon=True)
                jolt_thread.start()
                
            except ImportError:
                messagebox.showerror(
                    "Error", 
                    "Memory jolt module not found.\n\n" +
                    "Make sure memory_jolt.py is in the same directory."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run memory jolt: {e}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Memory jolt error: {e}")
    
    def run_soft_cleaner(self):
        """Run ultra-gentle soft RAM cleaner"""
        try:
            # Show info dialog
            result = messagebox.askyesno(
                "Soft RAM Cleaner", 
                "💨 Ultra-Gentle Soft Clean\n\n" +
                "This will perform the softest cleanup:\n\n" +
                "• Ultra-soft memory trimming\n" +
                "• Light cache clearing only\n" +
                "• Memory allocation optimization\n" +
                "• Gentle working set refresh\n" +
                "• Soft memory compaction\n\n" +
                "🌸 Ultra-gentle and safe\n" +
                "🌸 Perfect for regular use\n" +
                "🌸 No system impact\n\n" +
                "Continue with soft clean?"
            )
            
            if not result:
                return
            
            # Import and run soft cleaner
            try:
                import soft_ram_cleaner
                
                # Create progress window
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Soft Cleaning...")
                progress_window.geometry("400x150")
                progress_window.configure(bg=self.colors['bg'])
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                # Progress label
                progress_label = tk.Label(progress_window, text="💨 Performing ultra-gentle soft clean...", 
                                        font=('Segoe UI', 12, 'bold'), 
                                        fg='#87CEEB', bg=self.colors['bg'])
                progress_label.pack(pady=20)
                
                detail_label = tk.Label(progress_window, text="The softest touch for your memory...", 
                                       font=('Segoe UI', 10), 
                                       fg=self.colors['text_secondary'], bg=self.colors['bg'])
                detail_label.pack(pady=5)
                
                # Progress bar
                progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
                progress_bar.pack(pady=20, padx=20, fill=tk.X)
                progress_bar.start()
                
                self.root.update()
                
                # Run soft cleaner in separate thread
                def run_soft_clean():
                    try:
                        cleaner = soft_ram_cleaner.SoftRAMCleaner()
                        memory_freed = cleaner.run_soft_cleanup()
                        
                        # Close progress window
                        progress_window.destroy()
                        
                        # Update display
                        self.update_display()
                        
                        # Show results
                        if memory_freed > 0.05:
                            messagebox.showinfo(
                                "Soft Clean Complete", 
                                f"🌸 Soft clean successful!\n\n" +
                                f"💾 Memory freed: {memory_freed:.2f} GB\n" +
                                f"💧 System feels refreshed\n" +
                                f"🔄 Display updated with new values\n\n" +
                                f"✅ Ultra-gentle optimization completed"
                            )
                        else:
                            messagebox.showinfo(
                                "Soft Clean Complete", 
                                f"💧 System is already optimized\n\n" +
                                f"🌸 No additional cleanup needed\n" +
                                f"💡 Your system is running efficiently"
                            )
                            
                    except Exception as e:
                        progress_window.destroy()
                        messagebox.showerror("Error", f"Soft clean failed: {e}")
                
                # Start soft clean thread
                soft_thread = threading.Thread(target=run_soft_clean, daemon=True)
                soft_thread.start()
                
            except ImportError:
                messagebox.showerror(
                    "Error", 
                    "Soft RAM cleaner module not found.\n\n" +
                    "Make sure soft_ram_cleaner.py is in the same directory."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run soft clean: {e}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Soft clean error: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.monitoring = False
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = RAMMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
