#!/usr/bin/env python3
"""
Enhanced System Performance Dashboard
Comprehensive dashboard with settings, data persistence, and advanced monitoring.
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
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import json
import sqlite3
import csv
from collections import deque
import queue

# Import settings manager and new components
from settings_manager import SettingsManager
from performance_reports import PerformanceReports
from backup_manager import BackupManager
from email_notifications import EmailNotificationManager
from system_health_scorer import SystemHealthScorer
from automated_responses import AutomatedResponseManager

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

class DataPersistence:
    """Handles historical data storage and retrieval"""
    
    def __init__(self, db_path="system_monitoring.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage REAL,
                    cpu_freq REAL,
                    cpu_temp REAL,
                    ram_usage REAL,
                    ram_used REAL,
                    ram_total REAL,
                    gpu_usage REAL,
                    gpu_memory_used REAL,
                    gpu_memory_total REAL,
                    gpu_temp REAL,
                    network_sent REAL,
                    network_recv REAL,
                    disk_read REAL,
                    disk_write REAL,
                    disk_queue REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    message TEXT,
                    severity TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    details TEXT,
                    effectiveness REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def store_metrics(self, metrics):
        """Store system metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_usage, cpu_freq, cpu_temp, ram_usage, ram_used, ram_total,
                 gpu_usage, gpu_memory_used, gpu_memory_total, gpu_temp,
                 network_sent, network_recv, disk_read, disk_write, disk_queue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics['cpu']['usage'],
                metrics['cpu']['freq'],
                metrics['cpu']['temp'],
                metrics['memory']['usage'],
                metrics['memory']['used'],
                metrics['memory']['total'],
                metrics['gpu']['usage'],
                metrics['gpu']['memory_used'],
                metrics['gpu']['memory_total'],
                metrics['gpu']['temp'],
                metrics['network']['sent'],
                metrics['network']['recv'],
                metrics['disk']['read'],
                metrics['disk']['write'],
                metrics['disk']['queue']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing metrics: {e}")
    
    def get_metrics(self, hours=24):
        """Retrieve metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp
            '''.format(hours))
            
            data = cursor.fetchall()
            conn.close()
            
            return data
            
        except Exception as e:
            print(f"Error retrieving metrics: {e}")
            return []
    
    def store_alert(self, alert_type, message, severity):
        """Store alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (alert_type, message, severity)
                VALUES (?, ?, ?)
            ''', (alert_type, message, severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing alert: {e}")
    
    def get_recent_alerts(self, limit=10):
        """Get recent alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            alerts = cursor.fetchall()
            conn.close()
            
            return alerts
            
        except Exception as e:
            print(f"Error retrieving alerts: {e}")
            return []

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, settings_manager, data_persistence):
        self.settings = settings_manager
        self.db = data_persistence
        self.alert_queue = queue.Queue()
        self.alert_history = deque(maxlen=100)
        
    def check_thresholds(self, metrics):
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        # CPU alerts
        cpu_usage = metrics['cpu']['usage']
        cpu_warning = self.settings.get_setting('alerts', 'cpu_threshold_warning', 80.0)
        cpu_critical = self.settings.get_setting('alerts', 'cpu_threshold_critical', 95.0)
        
        if cpu_usage >= cpu_critical:
            alerts.append({
                'type': 'cpu_critical',
                'message': f'CPU usage critical: {cpu_usage:.1f}%',
                'severity': 'critical'
            })
        elif cpu_usage >= cpu_warning:
            alerts.append({
                'type': 'cpu_warning',
                'message': f'CPU usage high: {cpu_usage:.1f}%',
                'severity': 'warning'
            })
        
        # RAM alerts
        ram_usage = metrics['memory']['usage']
        ram_warning = self.settings.get_setting('alerts', 'ram_threshold_warning', 85.0)
        ram_critical = self.settings.get_setting('alerts', 'ram_threshold_critical', 95.0)
        
        if ram_usage >= ram_critical:
            alerts.append({
                'type': 'ram_critical',
                'message': f'RAM usage critical: {ram_usage:.1f}%',
                'severity': 'critical'
            })
        elif ram_usage >= ram_warning:
            alerts.append({
                'type': 'ram_warning',
                'message': f'RAM usage high: {ram_usage:.1f}%',
                'severity': 'warning'
            })
        
        # GPU alerts
        gpu_usage = metrics['gpu']['usage']
        if gpu_usage > 0:  # Only check if GPU is available
            gpu_warning = self.settings.get_setting('alerts', 'gpu_threshold_warning', 85.0)
            gpu_critical = self.settings.get_setting('alerts', 'gpu_threshold_critical', 95.0)
            
            if gpu_usage >= gpu_critical:
                alerts.append({
                    'type': 'gpu_critical',
                    'message': f'GPU usage critical: {gpu_usage:.1f}%',
                    'severity': 'critical'
                })
            elif gpu_usage >= gpu_warning:
                alerts.append({
                    'type': 'gpu_warning',
                    'message': f'GPU usage high: {gpu_usage:.1f}%',
                    'severity': 'warning'
                })
        
        # Temperature alerts
        cpu_temp = metrics['cpu']['temp']
        gpu_temp = metrics['gpu']['temp']
        temp_warning = self.settings.get_setting('alerts', 'temperature_threshold_warning', 75.0)
        temp_critical = self.settings.get_setting('alerts', 'temperature_threshold_critical', 85.0)
        
        if cpu_temp >= temp_critical:
            alerts.append({
                'type': 'cpu_temp_critical',
                'message': f'CPU temperature critical: {cpu_temp:.1f}°C',
                'severity': 'critical'
            })
        elif cpu_temp >= temp_warning:
            alerts.append({
                'type': 'cpu_temp_warning',
                'message': f'CPU temperature high: {cpu_temp:.1f}°C',
                'severity': 'warning'
            })
        
        if gpu_temp >= temp_critical:
            alerts.append({
                'type': 'gpu_temp_critical',
                'message': f'GPU temperature critical: {gpu_temp:.1f}°C',
                'severity': 'critical'
            })
        elif gpu_temp >= temp_warning:
            alerts.append({
                'type': 'gpu_temp_warning',
                'message': f'GPU temperature high: {gpu_temp:.1f}°C',
                'severity': 'warning'
            })
        
        # Store alerts
        for alert in alerts:
            self.db.store_alert(alert['type'], alert['message'], alert['severity'])
            self.alert_history.append(alert)
            self.alert_queue.put(alert)
        
        return alerts

class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings = settings_manager
        self.dialog = None
        self.widgets = {}
    
    def show(self):
        """Show settings dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("⚙️ Settings")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg='#1a1a1a')
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a1a')
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='#ffffff')
        
        # Create tabs
        self.create_general_tab(notebook)
        self.create_monitoring_tab(notebook)
        self.create_alerts_tab(notebook)
        self.create_optimization_tab(notebook)
        self.create_ui_tab(notebook)
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg='#1a1a1a')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Save", command=self.save_settings,
                 bg='#00ff88', fg='#1a1a1a', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=5).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(button_frame, text="Reset to Defaults", command=self.reset_settings,
                 bg='#ffaa00', fg='#1a1a1a', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=5).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 bg='#ff4444', fg='#1a1a1a', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=5).pack(side=tk.RIGHT, padx=5)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_general_tab(self, notebook):
        """Create general settings tab"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="General")
        
        # Auto start
        self.create_checkbox(frame, "Auto-start with Windows", "general", "auto_start", 0)
        
        # Minimize to tray
        self.create_checkbox(frame, "Minimize to tray", "general", "minimize_to_tray", 1)
        
        # Start minimized
        self.create_checkbox(frame, "Start minimized", "general", "start_minimized", 2)
        
        # Enable notifications
        self.create_checkbox(frame, "Enable notifications", "general", "enable_notifications", 3)
        
        # Enable sounds
        self.create_checkbox(frame, "Enable sounds", "general", "enable_sounds", 4)
        
        # Language
        self.create_combobox(frame, "Language", "general", "language", 
                           ["en_US", "es_ES", "fr_FR", "de_DE", "ja_JP"], 5)
        
        # Theme
        self.create_combobox(frame, "Theme", "general", "theme", 
                           ["dark", "light", "auto"], 6)
    
    def create_monitoring_tab(self, notebook):
        """Create monitoring settings tab"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="Monitoring")
        
        # Update interval
        self.create_spinbox(frame, "Update Interval (ms)", "monitoring", "update_interval", 
                          500, 60000, 100, 0)
        
        # History retention
        self.create_spinbox(frame, "History Retention (days)", "monitoring", "history_retention_days", 
                          1, 30, 1, 1)
        
        # Enable monitoring options
        self.create_checkbox(frame, "Enable CPU monitoring", "monitoring", "enable_cpu_monitoring", 2)
        self.create_checkbox(frame, "Enable GPU monitoring", "monitoring", "enable_gpu_monitoring", 3)
        self.create_checkbox(frame, "Enable RAM monitoring", "monitoring", "enable_ram_monitoring", 4)
        self.create_checkbox(frame, "Enable network monitoring", "monitoring", "enable_network_monitoring", 5)
        self.create_checkbox(frame, "Enable disk monitoring", "monitoring", "enable_disk_monitoring", 6)
        self.create_checkbox(frame, "Enable temperature monitoring", "monitoring", "enable_temperature_monitoring", 7)
    
    def create_alerts_tab(self, notebook):
        """Create alerts settings tab"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="Alerts")
        
        # Enable alerts
        self.create_checkbox(frame, "Enable alerts", "alerts", "enable_alerts", 0)
        
        # Alert sound
        self.create_checkbox(frame, "Alert sound", "alerts", "alert_sound", 1)
        
        # Auto optimization
        self.create_checkbox(frame, "Auto optimization on alerts", "alerts", "auto_optimization", 2)
        
        # Thresholds
        self.create_spinbox(frame, "CPU Warning Threshold (%)", "alerts", "cpu_threshold_warning", 
                          50, 95, 5, 3)
        self.create_spinbox(frame, "CPU Critical Threshold (%)", "alerts", "cpu_threshold_critical", 
                          80, 100, 5, 4)
        self.create_spinbox(frame, "RAM Warning Threshold (%)", "alerts", "ram_threshold_warning", 
                          50, 95, 5, 5)
        self.create_spinbox(frame, "RAM Critical Threshold (%)", "alerts", "ram_threshold_critical", 
                          80, 100, 5, 6)
        self.create_spinbox(frame, "GPU Warning Threshold (%)", "alerts", "gpu_threshold_warning", 
                          50, 95, 5, 7)
        self.create_spinbox(frame, "GPU Critical Threshold (%)", "alerts", "gpu_threshold_critical", 
                          80, 100, 5, 8)
        self.create_spinbox(frame, "Temperature Warning (°C)", "alerts", "temperature_threshold_warning", 
                          60, 90, 5, 9)
        self.create_spinbox(frame, "Temperature Critical (°C)", "alerts", "temperature_threshold_critical", 
                          70, 100, 5, 10)
    
    def create_optimization_tab(self, notebook):
        """Create optimization settings tab"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="Optimization")
        
        # Default profile
        self.create_combobox(frame, "Default Profile", "optimization", "default_profile", 
                           ["balanced", "gaming", "productivity", "multimedia", "development"], 0)
        
        # Auto profile switching
        self.create_checkbox(frame, "Auto profile switching", "optimization", "auto_profile_switching", 1)
        
        # Optimization aggressiveness
        self.create_combobox(frame, "Optimization Aggressiveness", "optimization", "optimization_aggressiveness", 
                           ["conservative", "moderate", "aggressive"], 2)
        
        # Enable optimization options
        self.create_checkbox(frame, "Enable process prioritization", "optimization", "enable_process_prioritization", 3)
        self.create_checkbox(frame, "Enable memory optimization", "optimization", "enable_memory_optimization", 4)
        self.create_checkbox(frame, "Enable GPU optimization", "optimization", "enable_gpu_optimization", 5)
        self.create_checkbox(frame, "Enable network optimization", "optimization", "enable_network_optimization", 6)
        
        # Optimization interval
        self.create_spinbox(frame, "Optimization Interval (seconds)", "optimization", "optimization_interval", 
                          10, 300, 10, 7)
        
        # Backup profiles
        self.create_checkbox(frame, "Backup profiles", "optimization", "backup_profiles", 8)
    
    def create_ui_tab(self, notebook):
        """Create UI settings tab"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="UI")
        
        # Show graphs
        self.create_checkbox(frame, "Show graphs", "ui", "show_graphs", 0)
        
        # Compact mode
        self.create_checkbox(frame, "Compact mode", "ui", "compact_mode", 1)
        
        # Show tooltips
        self.create_checkbox(frame, "Show tooltips", "ui", "show_tooltips", 2)
        
        # Animation enabled
        self.create_checkbox(frame, "Animation enabled", "ui", "animation_enabled", 3)
        
        # Font size
        self.create_spinbox(frame, "Font size", "ui", "font_size", 8, 24, 1, 4)
        
        # Graph history points
        self.create_spinbox(frame, "Graph history points", "ui", "graph_history_points", 30, 200, 10, 5)
        
        # Graph update interval
        self.create_spinbox(frame, "Graph update interval (ms)", "ui", "graph_update_interval", 500, 5000, 100, 6)
        
        # Color scheme
        self.create_combobox(frame, "Color scheme", "ui", "color_scheme", 
                           ["default", "blue", "green", "red", "purple"], 7)
    
    def create_checkbox(self, parent, text, category, key, row):
        """Create checkbox widget"""
        frame = tk.Frame(parent, bg='#1a1a1a')
        frame.pack(fill=tk.X, padx=20, pady=5)
        
        var = tk.BooleanVar(value=self.settings.get_setting(category, key, False))
        self.widgets[f"{category}_{key}"] = var
        
        tk.Checkbutton(frame, text=text, variable=var,
                      bg='#1a1a1a', fg='#ffffff', selectcolor='#2d2d2d',
                      font=('Segoe UI', 10)).pack(side=tk.LEFT)
    
    def create_spinbox(self, parent, text, category, key, from_val, to_val, increment, row):
        """Create spinbox widget"""
        frame = tk.Frame(parent, bg='#1a1a1a')
        frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame, text=text, bg='#1a1a1a', fg='#ffffff',
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        var = tk.IntVar(value=self.settings.get_setting(category, key, 0))
        self.widgets[f"{category}_{key}"] = var
        
        spinbox = tk.Spinbox(frame, from_=from_val, to=to_val, increment=increment,
                             textvariable=var, bg='#2d2d2d', fg='#ffffff',
                             font=('Segoe UI', 10))
        spinbox.pack(side=tk.RIGHT)
    
    def create_combobox(self, parent, text, category, key, values, row):
        """Create combobox widget"""
        frame = tk.Frame(parent, bg='#1a1a1a')
        frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(frame, text=text, bg='#1a1a1a', fg='#ffffff',
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        var = tk.StringVar(value=self.settings.get_setting(category, key, values[0]))
        self.widgets[f"{category}_{key}"] = var
        
        combobox = ttk.Combobox(frame, textvariable=var, values=values,
                                state='readonly', width=15)
        combobox.pack(side=tk.RIGHT)
    
    def save_settings(self):
        """Save all settings"""
        try:
            for key, var in self.widgets.items():
                category, setting_key = key.split('_', 1)
                value = var.get()
                self.settings.set_setting(category, setting_key, value)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?"):
            self.settings.reset_to_defaults()
            self.dialog.destroy()
            messagebox.showinfo("Success", "Settings reset to defaults!")

class EnhancedSystemDashboard:
    """Enhanced System Performance Dashboard with settings and persistence"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Enhanced System Performance Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(True, True)
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.data_persistence = DataPersistence()
        self.alert_manager = AlertManager(self.settings_manager, self.data_persistence)
        self.performance_reports = PerformanceReports()
        self.backup_manager = BackupManager()
        self.email_notifications = EmailNotificationManager()
        self.health_scorer = SystemHealthScorer()
        self.automated_responses = AutomatedResponseManager()
        
        # Apply settings
        self.apply_settings()
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = deque(maxlen=1000)
        
        # Color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0'
        }
        
        # Create GUI
        self.create_widgets()
        
        # Start monitoring
        if self.settings_manager.get_setting('general', 'auto_start', False):
            self.start_monitoring()
    
    def apply_settings(self):
        """Apply settings to the application"""
        # Window geometry
        geometry = self.settings_manager.get_setting('ui', 'window_geometry')
        if geometry:
            self.root.geometry(f"{geometry['width']}x{geometry['height']}+{geometry['x']}+{geometry['y']}")
        
        # Theme
        theme = self.settings_manager.get_setting('general', 'theme', 'dark')
        if theme == 'light':
            self.colors = {
                'bg': '#f0f0f0',
                'card': '#ffffff',
                'primary': '#0066cc',
                'success': '#00aa00',
                'warning': '#ff8800',
                'danger': '#cc0000',
                'text': '#000000',
                'text_secondary': '#666666'
            }
            self.root.configure(bg=self.colors['bg'])
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Menu bar
        self.create_menu()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Metrics
        self.create_metrics_panel(content_frame)
        
        # Right panel - Graphs and alerts
        self.create_graphs_panel(content_frame)
        
        # Status bar
        self.create_status_bar()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg='#2d2d2d', fg='#ffffff')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        tools_menu.add_command(label="Generate Report", command=self.generate_report)
        tools_menu.add_separator()
        tools_menu.add_command(label="Create Backup", command=self.create_backup)
        tools_menu.add_command(label="Restore Backup", command=self.restore_backup)
        tools_menu.add_command(label="Backup Manager", command=self.show_backup_manager)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear History", command=self.clear_history)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2d2d2d', fg='#ffffff')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(header_frame, text="🚀 Enhanced System Performance Dashboard",
                              font=('Segoe UI', 18, 'bold'), fg=self.colors['primary'],
                              bg=self.colors['card'])
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Control buttons
        button_frame = tk.Frame(header_frame, bg=self.colors['card'])
        button_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.start_btn = tk.Button(button_frame, text="▶️ Start", command=self.start_monitoring,
                                  bg=self.colors['success'], fg='#1a1a1a', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=5)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop", command=self.stop_monitoring,
                                 bg=self.colors['danger'], fg='#1a1a1a', font=('Segoe UI', 10, 'bold'),
                                 relief='flat', padx=15, pady=5, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="⚙️ Settings", command=self.show_settings,
                 bg=self.colors['primary'], fg='#1a1a1a', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
    
    def create_metrics_panel(self, parent):
        """Create metrics display panel"""
        metrics_frame = tk.Frame(parent, bg=self.colors['bg'])
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # CPU Card
        self.cpu_card = self.create_metric_card(metrics_frame, "CPU", self.colors['primary'])
        
        # RAM Card
        self.ram_card = self.create_metric_card(metrics_frame, "RAM", self.colors['success'])
        
        # GPU Card
        self.gpu_card = self.create_metric_card(metrics_frame, "GPU", self.colors['warning'])
        
        # Network Card
        self.network_card = self.create_metric_card(metrics_frame, "Network", self.colors['primary'])
        
        # Disk Card
        self.disk_card = self.create_metric_card(metrics_frame, "Disk", self.colors['success'])
    
    def create_metric_card(self, parent, title, color):
        """Create a metric card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card.pack(fill=tk.X, pady=5)
        
        # Title
        title_label = tk.Label(card, text=title, font=('Segoe UI', 12, 'bold'),
                              fg=color, bg=self.colors['card'])
        title_label.pack(pady=(10, 5))
        
        # Value
        value_label = tk.Label(card, text="0%", font=('Segoe UI', 16, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        value_label.pack()
        
        # Details
        details_label = tk.Label(card, text="Loading...", font=('Segoe UI', 9),
                               fg=self.colors['text_secondary'], bg=self.colors['card'])
        details_label.pack(pady=(5, 10))
        
        # Progress bar
        progress = ttk.Progressbar(card, length=200, mode='determinate')
        progress.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        # Store references
        card.value_label = value_label
        card.details_label = details_label
        card.progress = progress
        
        return card
    
    def create_graphs_panel(self, parent):
        """Create graphs and alerts panel"""
        graphs_frame = tk.Frame(parent, bg=self.colors['bg'])
        graphs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(graphs_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Performance graphs tab
        self.create_performance_graphs(notebook)
        
        # Alerts tab
        self.create_alerts_panel(notebook)
    
    def create_performance_graphs(self, notebook):
        """Create performance graphs"""
        graph_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(graph_frame, text="Performance")
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), facecolor=self.colors['bg'])
        self.ax1 = self.fig.add_subplot(221, facecolor=self.colors['card'])
        self.ax2 = self.fig.add_subplot(222, facecolor=self.colors['card'])
        self.ax3 = self.fig.add_subplot(223, facecolor=self.colors['card'])
        self.ax4 = self.fig.add_subplot(224, facecolor=self.colors['card'])
        
        # Configure axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor(self.colors['card'])
            ax.tick_params(colors=self.colors['text_secondary'])
            ax.spines['bottom'].set_color(self.colors['text_secondary'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors['text_secondary'])
        
        self.ax1.set_title('CPU Usage', color=self.colors['text'])
        self.ax2.set_title('RAM Usage', color=self.colors['text'])
        self.ax3.set_title('GPU Usage', color=self.colors['text'])
        self.ax4.set_title('Network I/O', color=self.colors['text'])
        
        self.fig.tight_layout()
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_alerts_panel(self, notebook):
        """Create alerts panel"""
        alerts_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(alerts_frame, text="Alerts")
        
        # Alerts list
        self.alerts_listbox = tk.Listbox(alerts_frame, bg=self.colors['card'], fg=self.colors['text'],
                                         font=('Consolas', 9), relief='flat')
        self.alerts_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.alerts_listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.alerts_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.alerts_listbox.yview)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], relief='solid', bd=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, text="● Ready", fg=self.colors['success'],
                                   bg=self.colors['card'], font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Alert indicator
        self.alert_indicator = tk.Label(status_frame, text="🔔 No Alerts", fg=self.colors['text_secondary'],
                                       bg=self.colors['card'], font=('Segoe UI', 9))
        self.alert_indicator.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self.root, self.settings_manager).show()
    
    def export_data(self):
        """Export monitoring data"""
        file_path = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_csv(file_path)
                else:
                    self.export_json(file_path)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")
    
    def export_csv(self, file_path):
        """Export data to CSV"""
        data = self.data_persistence.get_metrics()
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'cpu_usage', 'cpu_freq', 'cpu_temp', 'ram_usage', 
                            'ram_used', 'ram_total', 'gpu_usage', 'gpu_memory_used', 
                            'gpu_memory_total', 'gpu_temp', 'network_sent', 'network_recv',
                            'disk_read', 'disk_write', 'disk_queue'])
            writer.writerows(data)
    
    def export_json(self, file_path):
        """Export data to JSON"""
        data = self.data_persistence.get_metrics()
        
        columns = ['timestamp', 'cpu_usage', 'cpu_freq', 'cpu_temp', 'ram_usage', 
                  'ram_used', 'ram_total', 'gpu_usage', 'gpu_memory_used', 
                  'gpu_memory_total', 'gpu_temp', 'network_sent', 'network_recv',
                  'disk_read', 'disk_write', 'disk_queue']
        
        json_data = []
        for row in data:
            json_data.append(dict(zip(columns, row)))
        
        with open(file_path, 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, default=str)
    
    def import_data(self):
        """Import monitoring data"""
        messagebox.showinfo("Info", "Data import feature coming soon!")
    
    def generate_report(self):
        """Generate performance report"""
        try:
            # Generate daily report
            report = self.performance_reports.generate_daily_report()
            
            if "error" in report:
                messagebox.showerror("Error", f"Failed to generate report: {report['error']}")
                return
            
            # Show report dialog
            self.show_report_dialog(report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def clear_history(self):
        """Clear monitoring history"""
        if messagebox.askyesno("Clear History", "Clear all monitoring history?"):
            try:
                # Clear database
                conn = sqlite3.connect(self.data_persistence.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM system_metrics")
                cursor.execute("DELETE FROM alerts")
                conn.commit()
                conn.close()
                
                # Clear graphs
                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                self.ax4.clear()
                self.canvas.draw()
                
                messagebox.showinfo("Success", "History cleared successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {e}")
    
    def show_report_dialog(self, report: Dict[str, Any]):
        """Show performance report dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📊 Performance Report")
        dialog.geometry("800x600")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog, bg=self.colors['bg'])
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Report content
        title_label = tk.Label(scrollable_frame, text=f"Performance Report - {report.get('date', 'Unknown')}",
                              font=('Segoe UI', 16, 'bold'), fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=20)
        
        # Health score
        if 'health_score' in report:
            health = report['health_score']
            health_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
            health_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(health_frame, text=f"Health Score: {health['overall']:.1f}/100",
                    font=('Segoe UI', 14, 'bold'), fg=self.colors['success'], bg=self.colors['card']).pack(pady=10)
            tk.Label(health_frame, text=f"Grade: {health['grade']} ({health['status']})",
                    font=('Segoe UI', 12), fg=self.colors['text'], bg=self.colors['card']).pack()
        
        # Summary
        if 'summary' in report:
            summary = report['summary']
            summary_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
            summary_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(summary_frame, text="Summary Statistics", font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
            
            metrics_text = f"CPU: {summary.get('average_cpu', 0):.1f}% (Peak: {summary.get('max_cpu', 0):.1f}%)\n"
            metrics_text += f"Memory: {summary.get('average_memory', 0):.1f}% (Peak: {summary.get('max_memory', 0):.1f}%)\n"
            metrics_text += f"GPU: {summary.get('average_gpu', 0):.1f}% (Peak: {summary.get('max_gpu', 0):.1f}%)"
            
            tk.Label(summary_frame, text=metrics_text, font=('Segoe UI', 10),
                    fg=self.colors['text'], bg=self.colors['card'], justify=tk.LEFT).pack(pady=5)
        
        # Recommendations
        if 'recommendations' in report:
            recommendations = report['recommendations']
            rec_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
            rec_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(rec_frame, text="Recommendations", font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
            
            for rec in recommendations:
                tk.Label(rec_frame, text=f"• {rec}", font=('Segoe UI', 10),
                        fg=self.colors['text'], bg=self.colors['card'], wraplength=700, justify=tk.LEFT).pack(pady=2)
        
        # Export button
        button_frame = tk.Frame(scrollable_frame, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Export to HTML", command=lambda: self.export_report_html(report),
                 bg=self.colors['primary'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", command=dialog.destroy,
                 bg=self.colors['danger'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def export_report_html(self, report: Dict[str, Any]):
        """Export report to HTML"""
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                success = self.performance_reports.export_report_to_html(report, file_path)
                if success:
                    messagebox.showinfo("Success", f"Report exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {e}")
    
    def create_backup(self):
        """Create system backup"""
        try:
            result = self.backup_manager.create_backup()
            if result["success"]:
                messagebox.showinfo("Success", f"Backup created: {result['backup_name']}")
                
                # Send backup notification
                self.email_notifications.send_backup_notification(
                    result['backup_name'], result['backup_info']
                )
            else:
                messagebox.showerror("Error", f"Failed to create backup: {result['error']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {e}")
    
    def restore_backup(self):
        """Restore from backup"""
        try:
            # Get available backups
            backups = self.backup_manager.list_backups()
            
            if not backups:
                messagebox.showinfo("Info", "No backups available")
                return
            
            # Create backup selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Restore Backup")
            dialog.geometry("500x400")
            dialog.configure(bg=self.colors['bg'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(dialog, text="Select Backup to Restore", font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['primary'], bg=self.colors['bg']).pack(pady=20)
            
            # Backup list
            listbox = tk.Listbox(dialog, bg=self.colors['card'], fg=self.colors['text'],
                                font=('Segoe UI', 10), height=10)
            listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            for backup in backups:
                backup_text = f"{backup['name']} - {backup['created_at'][:10]}"
                listbox.insert(tk.END, backup_text)
            
            def do_restore():
                selection = listbox.curselection()
                if selection:
                    backup_name = backups[selection[0]]['name']
                    
                    result = self.backup_manager.restore_backup(backup_name)
                    if result["success"]:
                        messagebox.showinfo("Success", f"Backup restored: {backup_name}")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", f"Failed to restore backup: {result['error']}")
                else:
                    messagebox.showwarning("Warning", "Please select a backup to restore")
            
            # Buttons
            button_frame = tk.Frame(dialog, bg=self.colors['bg'])
            button_frame.pack(pady=20)
            
            tk.Button(button_frame, text="Restore", command=do_restore,
                     bg=self.colors['success'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                     bg=self.colors['danger'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show restore dialog: {e}")
    
    def show_backup_manager(self):
        """Show backup manager dialog"""
        try:
            # Get backup statistics
            stats = self.backup_manager.get_backup_statistics()
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Backup Manager")
            dialog.geometry("600x500")
            dialog.configure(bg=self.colors['bg'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(dialog, text="Backup Manager", font=('Segoe UI', 14, 'bold'),
                    fg=self.colors['primary'], bg=self.colors['bg']).pack(pady=20)
            
            # Statistics frame
            stats_frame = tk.Frame(dialog, bg=self.colors['card'], relief='solid', bd=1)
            stats_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(stats_frame, text="Backup Statistics", font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
            
            stats_text = f"Total Backups: {stats.get('total_backups', 0)}\n"
            stats_text += f"Total Size: {stats.get('total_size', 0) / (1024**2):.1f} MB\n"
            stats_text += f"Compressed: {stats.get('compressed_backups', 0)}\n"
            stats_text += f"Auto Backup: {'Enabled' if stats.get('auto_backup_enabled', False) else 'Disabled'}"
            
            tk.Label(stats_frame, text=stats_text, font=('Segoe UI', 10),
                    fg=self.colors['text'], bg=self.colors['card'], justify=tk.LEFT).pack(pady=5)
            
            # Buttons frame
            button_frame = tk.Frame(dialog, bg=self.colors['bg'])
            button_frame.pack(pady=20)
            
            tk.Button(button_frame, text="Create Backup", command=self.create_backup,
                     bg=self.colors['success'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="Restore Backup", command=self.restore_backup,
                     bg=self.colors['warning'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="Close", command=dialog.destroy,
                     bg=self.colors['danger'], fg=self.colors['bg'], font=('Segoe UI', 10, 'bold'),
                     relief='flat', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show backup manager: {e}")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Enhanced System Performance Dashboard\nVersion 2.0\n\nAdvanced system monitoring and optimization tool")
    
    def start_monitoring(self):
        """Start monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="● Monitoring", fg=self.colors['success'])
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="● Stopped", fg=self.colors['warning'])
    
    def monitor_loop(self):
        """Main monitoring loop"""
        update_interval = self.settings_manager.get_setting('monitoring', 'update_interval', 2000)
        
        while self.monitoring:
            try:
                # Get system metrics
                metrics = self.get_system_metrics()
                
                # Store metrics
                self.data_persistence.store_metrics(metrics)
                self.metrics_history.append(metrics)
                
                # Calculate health score
                health_score = self.health_scorer.calculate_current_health_score(metrics)
                
                # Check alerts
                if self.settings_manager.get_setting('alerts', 'enable_alerts', True):
                    alerts = self.alert_manager.check_thresholds(metrics)
                    self.update_alerts_display(alerts)
                    
                    # Process alerts for automated responses
                    for alert in alerts:
                        alert_data = {
                            'alert_type': alert['type'],
                            'message': alert['message'],
                            'severity': alert['severity'],
                            'cpu_usage': metrics['cpu']['usage'],
                            'memory_usage': metrics['memory']['usage'],
                            'gpu_usage': metrics['gpu']['usage'],
                            'cpu_temp': metrics['cpu']['temp'],
                            'gpu_temp': metrics['gpu']['temp']
                        }
                        self.automated_responses.process_alert(alert_data)
                        
                        # Send email notifications
                        self.email_notifications.send_alert_notification(
                            alert['type'], alert['message'], alert['severity'], alert_data
                        )
                
                # Send health notifications if enabled
                if self.settings_manager.get_setting('notifications', 'system_health_notifications', False):
                    self.email_notifications.send_system_health_notification(health_score)
                
                # Update GUI
                self.root.after(0, self.update_display, metrics)
                
                # Update graphs
                if len(self.metrics_history) > 1:
                    self.root.after(0, self.update_graphs)
                
                time.sleep(update_interval / 1000)
                
            except Exception as e:
                print(f"Monitor loop error: {e}")
                time.sleep(1)
    
    def get_system_metrics(self):
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
            cpu_temp = self.get_cpu_temperature()
            
            # RAM metrics
            memory = psutil.virtual_memory()
            ram_usage = memory.percent
            ram_used = memory.used / (1024**3)
            ram_total = memory.total / (1024**3)
            
            # GPU metrics
            gpu_usage = 0
            gpu_memory_used = 0
            gpu_memory_total = 0
            gpu_temp = 0
            
            if GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_usage = gpu.load * 100
                    gpu_memory_used = gpu.memoryUsed / 1024
                    gpu_memory_total = gpu.memoryTotal / 1024
                    gpu_temp = gpu.temperature
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent / (1024**2)
            network_recv = network.bytes_recv / (1024**2)
            
            # Disk metrics
            disk = psutil.disk_io_counters()
            disk_read = disk.read_bytes / (1024**2)
            disk_write = disk.write_bytes / (1024**2)
            disk_queue = 0  # Simplified for now
            
            return {
                'cpu': {'usage': cpu_usage, 'freq': cpu_freq, 'temp': cpu_temp},
                'memory': {'usage': ram_usage, 'used': ram_used, 'total': ram_total},
                'gpu': {'usage': gpu_usage, 'memory_used': gpu_memory_used, 'memory_total': gpu_memory_total, 'temp': gpu_temp},
                'network': {'sent': network_sent, 'recv': network_recv},
                'disk': {'read': disk_read, 'write': disk_write, 'queue': disk_queue}
            }
            
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return self.get_default_metrics()
    
    def get_default_metrics(self):
        """Get default metrics when monitoring fails"""
        return {
            'cpu': {'usage': 0, 'freq': 0, 'temp': 0},
            'memory': {'usage': 0, 'used': 0, 'total': 0},
            'gpu': {'usage': 0, 'memory_used': 0, 'memory_total': 0, 'temp': 0},
            'network': {'sent': 0, 'recv': 0},
            'disk': {'read': 0, 'write': 0, 'queue': 0}
        }
    
    def get_cpu_temperature(self):
        """Get CPU temperature"""
        try:
            if WMI_AVAILABLE:
                import pythoncom
                pythoncom.CoInitialize()
                c = wmi.WMI()
                for temp in c.Win32_TemperatureProbe():
                    if temp.CurrentTemperature:
                        return temp.CurrentTemperature - 273.15
            return 0.0
        except:
            return 0.0
    
    def update_display(self, metrics):
        """Update display with current metrics"""
        try:
            # Update CPU card
            self.cpu_card.value_label.config(text=f"{metrics['cpu']['usage']:.1f}%")
            self.cpu_card.progress['value'] = metrics['cpu']['usage']
            self.cpu_card.details_label.config(
                text=f"Freq: {metrics['cpu']['freq']:.0f}MHz | Temp: {metrics['cpu']['temp']:.1f}°C"
            )
            
            # Update RAM card
            self.ram_card.value_label.config(text=f"{metrics['memory']['usage']:.1f}%")
            self.ram_card.progress['value'] = metrics['memory']['usage']
            self.ram_card.details_label.config(
                text=f"{metrics['memory']['used']:.1f}GB / {metrics['memory']['total']:.1f}GB"
            )
            
            # Update GPU card
            self.gpu_card.value_label.config(text=f"{metrics['gpu']['usage']:.1f}%")
            self.gpu_card.progress['value'] = metrics['gpu']['usage']
            self.gpu_card.details_label.config(
                text=f"{metrics['gpu']['memory_used']:.1f}GB / {metrics['gpu']['memory_total']:.1f}GB | {metrics['gpu']['temp']:.1f}°C"
            )
            
            # Update Network card
            network_total = metrics['network']['sent'] + metrics['network']['recv']
            self.network_card.value_label.config(text=f"{network_total:.1f}MB")
            self.network_card.progress['value'] = min(network_total / 100, 100)  # Normalize to 100MB
            self.network_card.details_label.config(
                text=f"↑{metrics['network']['sent']:.1f}MB ↓{metrics['network']['recv']:.1f}MB"
            )
            
            # Update Disk card
            disk_total = metrics['disk']['read'] + metrics['disk']['write']
            self.disk_card.value_label.config(text=f"{disk_total:.1f}MB")
            self.disk_card.progress['value'] = min(disk_total / 100, 100)  # Normalize to 100MB
            self.disk_card.details_label.config(
                text=f"R:{metrics['disk']['read']:.1f}MB W:{metrics['disk']['write']:.1f}MB"
            )
            
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def update_graphs(self):
        """Update performance graphs"""
        try:
            if len(self.metrics_history) < 2:
                return
            
            # Get data for graphs
            history_points = min(len(self.metrics_history), self.settings_manager.get_setting('ui', 'graph_history_points', 60))
            recent_data = list(self.metrics_history)[-history_points:]
            
            timestamps = [datetime.now().strftime('%H:%M:%S') for _ in recent_data]
            cpu_data = [m['cpu']['usage'] for m in recent_data]
            ram_data = [m['memory']['usage'] for m in recent_data]
            gpu_data = [m['gpu']['usage'] for m in recent_data]
            network_data = [m['network']['sent'] + m['network']['recv'] for m in recent_data]
            
            # Clear and update graphs
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax4.clear()
            
            # CPU graph
            self.ax1.plot(timestamps, cpu_data, color=self.colors['primary'], linewidth=2)
            self.ax1.set_title('CPU Usage (%)', color=self.colors['text'])
            self.ax1.set_ylim(0, 100)
            self.ax1.grid(True, alpha=0.3)
            
            # RAM graph
            self.ax2.plot(timestamps, ram_data, color=self.colors['success'], linewidth=2)
            self.ax2.set_title('RAM Usage (%)', color=self.colors['text'])
            self.ax2.set_ylim(0, 100)
            self.ax2.grid(True, alpha=0.3)
            
            # GPU graph
            self.ax3.plot(timestamps, gpu_data, color=self.colors['warning'], linewidth=2)
            self.ax3.set_title('GPU Usage (%)', color=self.colors['text'])
            self.ax3.set_ylim(0, 100)
            self.ax3.grid(True, alpha=0.3)
            
            # Network graph
            self.ax4.plot(timestamps, network_data, color=self.colors['primary'], linewidth=2)
            self.ax4.set_title('Network I/O (MB)', color=self.colors['text'])
            self.ax4.grid(True, alpha=0.3)
            
            # Configure axes
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.set_facecolor(self.colors['card'])
                ax.tick_params(colors=self.colors['text_secondary'])
                ax.spines['bottom'].set_color(self.colors['text_secondary'])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color(self.colors['text_secondary'])
                
                # Rotate x-axis labels for better readability
                for label in ax.get_xticklabels():
                    label.set_rotation(45)
                    label.set_ha('right')
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating graphs: {e}")
    
    def update_alerts_display(self, alerts):
        """Update alerts display"""
        try:
            for alert in alerts:
                timestamp = datetime.now().strftime('%H:%M:%S')
                alert_text = f"[{timestamp}] {alert['severity'].upper()}: {alert['message']}"
                
                # Color code alerts
                if alert['severity'] == 'critical':
                    self.alerts_listbox.insert(tk.END, alert_text, 'critical')
                elif alert['severity'] == 'warning':
                    self.alerts_listbox.insert(tk.END, alert_text, 'warning')
                else:
                    self.alerts_listbox.insert(tk.END, alert_text)
                
                # Auto-scroll to bottom
                self.alerts_listbox.see(tk.END)
                
                # Limit listbox size
                if self.alerts_listbox.size() > 100:
                    self.alerts_listbox.delete(0)
            
            # Update alert indicator
            if alerts:
                self.alert_indicator.config(text="🔔 New Alerts", fg=self.colors['warning'])
            else:
                self.alert_indicator.config(text="🔔 No Alerts", fg=self.colors['text_secondary'])
            
        except Exception as e:
            print(f"Error updating alerts display: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        # Save window geometry
        geometry = self.root.geometry()
        if 'x' in geometry:
            parts = geometry.split('+')
            size_part = parts[0]
            x_pos = int(parts[1]) if len(parts) > 1 else 0
            y_pos = int(parts[2]) if len(parts) > 2 else 0
            
            width, height = map(int, size_part.split('x'))
            
            self.settings_manager.set_setting('ui', 'window_geometry', {
                'width': width, 'height': height, 'x': x_pos, 'y': y_pos
            })
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Destroy window
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = EnhancedSystemDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
