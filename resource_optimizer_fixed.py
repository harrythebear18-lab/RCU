#!/usr/bin/env python3
"""
Windows 11 Resource Sharing Optimization Algorithm - Fixed Version
Enhanced with proper permissions, dependencies, and administrative checks.
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
import json
import sys
import math
from collections import deque

# Check and install dependencies
def check_dependencies():
    """Check and install required dependencies"""
    missing_deps = []
    
    # Check for required modules
    try:
        import numpy as np
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import matplotlib
        matplotlib.use('TkAgg')  # Use TkAgg backend
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
    except ImportError:
        missing_deps.append("matplotlib")
    
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        missing_deps.extend(["pystray", "pillow"])
    
    # Install missing dependencies
    if missing_deps:
        print(f"Installing missing dependencies: {', '.join(missing_deps)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_deps)
            print("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    
    return True

# Check administrative privileges
def check_admin_privileges():
    """Check if running with administrative privileges"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

# Request administrative privileges
def request_admin_privileges():
    """Request administrative privileges"""
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                # Re-run the script with admin rights
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)
        except:
            return False
    return True

# Import monitoring modules with fallbacks
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
    try:
        nvml.nvmlInit()
    except:
        NVML_AVAILABLE = False
        nvml = None
except ImportError:
    NVML_AVAILABLE = False
    nvml = None

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class SafeResourceOptimizer:
    """Safe Windows 11 Resource Sharing Optimization Algorithm"""
    
    def __init__(self):
        self.optimization_active = False
        self.monitoring_thread = None
        self.resource_history = deque(maxlen=300)
        
        # Resource allocation weights
        self.allocation_weights = {
            'gaming': {'cpu': 0.7, 'gpu': 0.8, 'ram': 0.6, 'io': 0.5},
            'productivity': {'cpu': 0.5, 'gpu': 0.3, 'ram': 0.7, 'io': 0.6},
            'multimedia': {'cpu': 0.4, 'gpu': 0.6, 'ram': 0.5, 'io': 0.7},
            'development': {'cpu': 0.6, 'gpu': 0.4, 'ram': 0.8, 'io': 0.5},
            'balanced': {'cpu': 0.5, 'gpu': 0.5, 'ram': 0.5, 'io': 0.5}
        }
        
        # Windows 11 specific optimization parameters
        self.win11_params = {
            'memory_compression': True,
            'standby_list_optimization': True,
            'process_priority_boost': True,
            'io_priority_adjustment': False,  # Disabled for safety
            'cpu_affinity_optimization': False,  # Disabled for safety
            'gpu_scheduler_tuning': False,  # Disabled for safety
            'network_priority_optimization': False  # Disabled for safety
        }
        
        # Resource thresholds - more conservative
        self.thresholds = {
            'cpu_high': 85.0,
            'cpu_critical': 95.0,
            'ram_high': 90.0,
            'ram_critical': 95.0,
            'gpu_high': 85.0,
            'gpu_critical': 95.0,
            'io_high': 85.0,
            'io_critical': 95.0
        }
        
        # Process classification
        self.process_classes = {
            'critical': ['system', 'csrss', 'winlogon', 'services', 'lsass'],
            'gaming': ['steam', 'epicgameslauncher', 'origin', 'uplay', 'battle.net'],
            'productivity': ['chrome', 'firefox', 'msedge', 'office', 'winword', 'excel'],
            'multimedia': ['vlc', 'mpc', 'spotify', 'itunes', 'photoshop'],
            'development': ['code', 'python', 'node', 'java', 'docker'],
            'background': ['onedrive', 'dropbox', 'googledrive', 'discord', 'slack']
        }
        
        self.current_profile = 'balanced'
        self.optimization_level = 'adaptive'
        
        # Check permissions
        self.is_admin = check_admin_privileges()
        
    def get_safe_resource_snapshot(self):
        """Get resource snapshot with maximum safety"""
        try:
            snapshot = {
                'timestamp': time.time(),
                'cpu': {
                    'usage': psutil.cpu_percent(interval=0.1),
                    'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                    'temp': self.get_cpu_temperature_safe(),
                    'load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
                    'processes': self.get_cpu_processes_safe()
                },
                'memory': {
                    'usage': psutil.virtual_memory().percent,
                    'available': psutil.virtual_memory().available / (1024**3),
                    'swap': psutil.swap_memory().percent if psutil.swap_memory() else 0,
                    'standby': 0.0,  # Disabled for safety
                    'compressed': 0.0  # Disabled for safety
                },
                'gpu': {
                    'usage': self.get_gpu_usage_safe(),
                    'memory': self.get_gpu_memory_safe(),
                    'temp': self.get_gpu_temperature_safe(),
                    'freq': 0.0,  # Disabled for safety
                    'processes': []
                },
                'disk': {
                    'usage': self.get_disk_usage_safe(),
                    'io': self.get_disk_io_safe(),
                    'queue_length': 0.0  # Disabled for safety
                },
                'network': {
                    'io': self.get_network_io_safe(),
                    'latency': 0.0  # Disabled for safety
                }
            }
            
            self.resource_history.append(snapshot)
            return snapshot
            
        except Exception as e:
            print(f"Error getting safe resource snapshot: {e}")
            return None
    
    def get_cpu_processes_safe(self):
        """Get CPU processes safely with very limited scope"""
        processes = []
        try:
            # Limit to top 3 processes to prevent blocking
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 15:  # Only include processes using >15% CPU
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu': pinfo['cpu_percent'],
                            'memory': pinfo['memory_percent'],
                            'class': self.classify_process(pinfo['name'])
                        })
                        if len(processes) >= 3:  # Limit to 3 processes
                            break
                except:
                    continue
            return sorted(processes, key=lambda x: x['cpu'], reverse=True)
        except:
            return []
    
    def get_cpu_temperature_safe(self):
        """Get CPU temperature safely"""
        try:
            if WMI_AVAILABLE and self.is_admin:
                c = wmi.WMI()
                for temp in c.Win32_TemperatureProbe():
                    if temp.CurrentTemperature:
                        return temp.CurrentTemperature - 273.15
            return 0.0
        except:
            return 0.0
    
    def get_gpu_usage_safe(self):
        """Get GPU usage safely"""
        try:
            if NVML_AVAILABLE and self.is_admin:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                return util.gpu
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].load * 100
            return 0.0
        except:
            return 0.0
    
    def get_gpu_memory_safe(self):
        """Get GPU memory usage safely"""
        try:
            if NVML_AVAILABLE and self.is_admin:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                return (mem_info.used / mem_info.total) * 100
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].memoryUtil * 100
            return 0.0
        except:
            return 0.0
    
    def get_gpu_temperature_safe(self):
        """Get GPU temperature safely"""
        try:
            if NVML_AVAILABLE and self.is_admin:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                return nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
            elif GPU_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    return gpus[0].temperature
            return 0.0
        except:
            return 0.0
    
    def get_disk_usage_safe(self):
        """Get disk usage safely"""
        try:
            disk_usage = {}
            # Limit to first 2 partitions
            for i, partition in enumerate(psutil.disk_partitions()):
                if i >= 2:
                    break
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'used_percent': (usage.used / usage.total) * 100,
                        'free_gb': usage.free / (1024**3)
                    }
                except:
                    continue
            return disk_usage
        except:
            return {}
    
    def get_disk_io_safe(self):
        """Get disk I/O safely"""
        try:
            io = psutil.disk_io_counters()
            return {
                'read_mb': io.read_bytes / (1024**2),
                'write_mb': io.write_bytes / (1024**2),
                'read_ops': io.read_count,
                'write_ops': io.write_count
            }
        except:
            return {}
    
    def get_network_io_safe(self):
        """Get network I/O safely"""
        try:
            io = psutil.net_io_counters()
            return {
                'sent_mb': io.bytes_sent / (1024**2),
                'recv_mb': io.bytes_recv / (1024**2),
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv
            }
        except:
            return {}
    
    def classify_process(self, process_name):
        """Classify process by type"""
        process_name = process_name.lower()
        
        for class_name, processes in self.process_classes.items():
            for proc in processes:
                if proc in process_name:
                    return class_name
        
        return 'unknown'
    
    def is_system_stable(self):
        """Quick system stability check"""
        try:
            # Check CPU responsiveness
            start_time = time.time()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            response_time = time.time() - start_time
            
            # If CPU check takes too long, system might be unstable
            if response_time > 3.0:
                return False
            
            # Check for extreme CPU usage that might indicate system freeze
            if cpu_percent > 99:
                return False
            
            # Check memory availability
            memory = psutil.virtual_memory()
            if memory.available < (200 * 1024 * 1024):  # Less than 200MB available
                return False
            
            return True
            
        except Exception:
            return False
    
    def calculate_pressure_score(self, snapshot):
        """Calculate overall resource pressure score"""
        score = 0
        
        # CPU pressure
        if snapshot['cpu']['usage'] > self.thresholds['cpu_critical']:
            score += 3
        elif snapshot['cpu']['usage'] > self.thresholds['cpu_high']:
            score += 2
        elif snapshot['cpu']['usage'] > 80:
            score += 1
        
        # Memory pressure
        if snapshot['memory']['usage'] > self.thresholds['ram_critical']:
            score += 3
        elif snapshot['memory']['usage'] > self.thresholds['ram_high']:
            score += 2
        elif snapshot['memory']['usage'] > 80:
            score += 1
        
        # GPU pressure
        if snapshot['gpu']['usage'] > self.thresholds['gpu_critical']:
            score += 3
        elif snapshot['gpu']['usage'] > self.thresholds['gpu_high']:
            score += 2
        elif snapshot['gpu']['usage'] > 80:
            score += 1
        
        return score
    
    def safe_optimization_loop(self):
        """Very safe optimization loop"""
        last_optimization_time = 0
        system_stable_count = 0
        
        while self.optimization_active:
            try:
                current_time = time.time()
                
                # Rate limiting - only check every 5 seconds minimum
                if current_time - last_optimization_time < 5:
                    time.sleep(2)
                    continue
                
                # Quick system stability check
                if not self.is_system_stable():
                    system_stable_count += 1
                    if system_stable_count > 2:  # If unstable for 2 consecutive checks
                        time.sleep(15)  # Wait longer before trying again
                        system_stable_count = 0
                    continue
                else:
                    system_stable_count = 0
                
                # Get resource snapshot with timeout
                snapshot = self.get_safe_resource_snapshot()
                if not snapshot:
                    time.sleep(10)
                    continue
                
                # Calculate resource pressure
                pressure_score = self.calculate_pressure_score(snapshot)
                
                # Apply optimizations with very conservative approach
                if pressure_score >= 3 and current_time - last_optimization_time > 30:  # 30 seconds minimum
                    # Critical pressure - very light optimization
                    self.safe_memory_cleanup()
                    last_optimization_time = current_time
                elif pressure_score >= 2 and current_time - last_optimization_time > 60:  # 60 seconds minimum
                    # High pressure - very light optimization
                    self.safe_memory_cleanup()
                    last_optimization_time = current_time
                
                # Conservative sleep
                time.sleep(10)  # Very conservative 10-second intervals
                
            except Exception as e:
                print(f"Safe optimization error: {e}")
                time.sleep(15)  # Longer error recovery time
    
    def safe_memory_cleanup(self):
        """Very safe memory cleanup"""
        try:
            # Only light garbage collection
            gc.collect()
            
        except Exception as e:
            print(f"Safe memory cleanup failed: {e}")
    
    def start_optimization(self, profile='balanced'):
        """Start safe resource optimization"""
        if self.optimization_active:
            return False
        
        self.current_profile = profile
        self.optimization_active = True
        
        # Start safe optimization thread
        self.monitoring_thread = threading.Thread(target=self.safe_optimization_loop, daemon=True)
        self.monitoring_thread.start()
        
        return True
    
    def stop_optimization(self):
        """Stop resource optimization"""
        self.optimization_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        return True
    
    def get_optimization_status(self):
        """Get current optimization status"""
        return {
            'active': self.optimization_active,
            'profile': self.current_profile,
            'resource_count': len(self.resource_history),
            'last_snapshot': self.resource_history[-1] if self.resource_history else None,
            'is_admin': self.is_admin
        }

class SafeResourceOptimizerGUI:
    """Safe GUI for Windows 11 Resource Optimizer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Windows 11 Resource Optimizer (Safe Mode)")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0f0f0f')
        self.root.resizable(True, True)
        
        # Color scheme
        self.colors = {
            'bg': '#0f0f0f',
            'card': '#1e1e1e',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#a0a0a0'
        }
        
        # Initialize optimizer
        self.optimizer = SafeResourceOptimizer()
        
        # Create GUI
        self.create_widgets()
        
        # Start monitoring
        self.start_monitoring()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🧠 Windows 11 Resource Optimizer (Safe Mode)", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=(20, 5))
        
        # Admin status
        admin_status = "Admin" if self.optimizer.is_admin else "User"
        admin_color = self.colors['success'] if self.optimizer.is_admin else self.colors['warning']
        
        admin_label = tk.Label(header_frame, text=f"Running as: {admin_status}", 
                               font=('Segoe UI', 11), 
                               fg=admin_color, bg=self.colors['bg'])
        admin_label.pack()
        
        # Control panel
        control_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        control_title = tk.Label(control_frame, text="🎛️ Optimization Controls", 
                                font=('Segoe UI', 14, 'bold'), 
                                fg=self.colors['primary'], bg=self.colors['card'])
        control_title.pack(pady=(15, 10))
        
        # Profile selection
        profile_frame = tk.Frame(control_frame, bg=self.colors['card'])
        profile_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(profile_frame, text="Profile:", font=('Segoe UI', 11), 
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.profile_var = tk.StringVar(value='balanced')
        profiles = ['balanced', 'gaming', 'productivity', 'multimedia', 'development']
        
        for profile in profiles:
            rb = tk.Radiobutton(profile_frame, text=profile.capitalize(), 
                              variable=self.profile_var, value=profile,
                              bg=self.colors['card'], fg=self.colors['text'],
                              selectcolor=self.colors['card'], 
                              activebackground=self.colors['card'],
                              font=('Segoe UI', 10))
            rb.pack(side=tk.LEFT, padx=10)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg=self.colors['card'])
        button_frame.pack(pady=(0, 20))
        
        self.start_btn = tk.Button(button_frame, text="▶️ Start Optimization", 
                                  font=('Segoe UI', 11, 'bold'), 
                                  bg=self.colors['success'], fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                                  command=self.start_optimization)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop Optimization", 
                                 font=('Segoe UI', 11, 'bold'), 
                                 bg=self.colors['danger'], fg=self.colors['bg'],
                                 relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                                 command=self.stop_optimization, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Status display
        status_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        status_title = tk.Label(status_frame, text="[CHART] Resource Status", 
                               font=('Segoe UI', 14, 'bold'), 
                               fg=self.colors['primary'], bg=self.colors['card'])
        status_title.pack(pady=(15, 10))
        
        # Resource displays
        self.resource_frame = tk.Frame(status_frame, bg=self.colors['card'])
        self.resource_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create resource labels
        self.create_resource_displays()
        
        # Optimization log
        log_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_title = tk.Label(log_frame, text="[CLIPBOARD] Optimization Log", 
                            font=('Segoe UI', 14, 'bold'), 
                            fg=self.colors['primary'], bg=self.colors['card'])
        log_title.pack(pady=(15, 10))
        
        # Log text widget
        self.log_text = tk.Text(log_frame, height=8, bg=self.colors['bg'], fg=self.colors['text'],
                               font=('Consolas', 9), relief='flat', bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbar for log
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def create_resource_displays(self):
        """Create resource display widgets"""
        # CPU Display
        cpu_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(cpu_frame, text="CPU", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.cpu_usage_label = tk.Label(cpu_frame, text="0%", font=('Segoe UI', 16, 'bold'), 
                                       fg=self.colors['text'], bg=self.colors['card'])
        self.cpu_usage_label.pack()
        
        # Memory Display
        mem_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(mem_frame, text="Memory", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.mem_usage_label = tk.Label(mem_frame, text="0%", font=('Segoe UI', 16, 'bold'), 
                                       fg=self.colors['text'], bg=self.colors['card'])
        self.mem_usage_label.pack()
        
        self.mem_available_label = tk.Label(mem_frame, text="0 GB free", font=('Segoe UI', 10), 
                                           fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.mem_available_label.pack(pady=(5, 10))
        
        # GPU Display
        gpu_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        gpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(gpu_frame, text="GPU", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.gpu_usage_label = tk.Label(gpu_frame, text="0%", font=('Segoe UI', 16, 'bold'), 
                                       fg=self.colors['text'], bg=self.colors['card'])
        self.gpu_usage_label.pack()
        
        # I/O Display
        io_frame = tk.Frame(self.resource_frame, bg=self.colors['card'], relief='solid', bd=1)
        io_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(io_frame, text="I/O", font=('Segoe UI', 12, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=(10, 5))
        
        self.io_ops_label = tk.Label(io_frame, text="0 ops/s", font=('Segoe UI', 10), 
                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.io_ops_label.pack(pady=(5, 10))
    
    def start_optimization(self):
        """Start resource optimization"""
        try:
            profile = self.profile_var.get()
            self.log_message(f"[REFRESH] Starting optimization with {profile} profile...")
            
            # Update button states immediately for feedback
            self.start_btn.config(state='disabled', text="⏳ Starting...")
            self.root.update_idletasks()
            
            if self.optimizer.start_optimization(profile):
                self.start_btn.config(state='disabled', text="▶️ Start Optimization")
                self.stop_btn.config(state='normal')
                self.log_message(f"[ROCKET] Optimization started with {profile} profile")
            else:
                self.start_btn.config(state='normal', text="▶️ Start Optimization")
                self.log_message("[ERROR] Failed to start optimization")
                messagebox.showerror("Error", "Failed to start optimization")
        except Exception as e:
            self.start_btn.config(state='normal', text="▶️ Start Optimization")
            self.log_message(f"[ERROR] Error starting optimization: {e}")
            messagebox.showerror("Error", f"Error starting optimization: {e}")
    
    def stop_optimization(self):
        """Stop resource optimization"""
        try:
            self.log_message("[REFRESH] Stopping optimization...")
            
            # Update button states immediately for feedback
            self.stop_btn.config(state='disabled', text="⏳ Stopping...")
            self.root.update_idletasks()
            
            if self.optimizer.stop_optimization():
                self.start_btn.config(state='normal', text="▶️ Start Optimization")
                self.stop_btn.config(state='disabled', text="⏹️ Stop Optimization")
                self.log_message("⏹️ Optimization stopped")
            else:
                self.stop_btn.config(state='normal', text="⏹️ Stop Optimization")
                self.log_message("[ERROR] Failed to stop optimization")
                messagebox.showerror("Error", "Failed to stop optimization")
        except Exception as e:
            self.stop_btn.config(state='normal', text="⏹️ Stop Optimization")
            self.log_message(f"[ERROR] Error stopping optimization: {e}")
            messagebox.showerror("Error", f"Error stopping optimization: {e}")
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def update_display(self):
        """Update resource displays"""
        snapshot = self.optimizer.get_safe_resource_snapshot()
        if not snapshot:
            return
        
        # Update CPU
        self.cpu_usage_label.config(text=f"{snapshot['cpu']['usage']:.1f}%")
        
        # Update Memory
        self.mem_usage_label.config(text=f"{snapshot['memory']['usage']:.1f}%")
        self.mem_available_label.config(text=f"{snapshot['memory']['available']:.1f} GB free")
        
        # Update GPU
        self.gpu_usage_label.config(text=f"{snapshot['gpu']['usage']:.1f}%")
        
        # Update I/O
        io_ops = snapshot['disk']['io'].get('read_ops', 0) + snapshot['disk']['io'].get('write_ops', 0)
        self.io_ops_label.config(text=f"{io_ops} ops")
    
    def start_monitoring(self):
        """Start monitoring thread"""
        def monitor():
            while True:
                try:
                    self.root.after(0, self.update_display)
                    time.sleep(3)  # Conservative 3-second intervals
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

def main():
    """Main function with comprehensive checks"""
    print("[TOOL] Checking dependencies and permissions...")
    
    # Check dependencies
    if not check_dependencies():
        print("[ERROR] Failed to install dependencies")
        messagebox.showerror("Error", "Failed to install required dependencies")
        return
    
    # Check administrative privileges
    is_admin = check_admin_privileges()
    if not is_admin:
        print("[WARNING] Running without administrative privileges")
        print("Some features may be limited")
        
        response = messagebox.askyesno(
            "Administrative Privileges Required",
            "This application works best with administrative privileges.\n"
            "Would you like to restart with administrative privileges?"
        )
        
        if response:
            if request_admin_privileges():
                return
    
    # Create and run GUI
    root = tk.Tk()
    app = SafeResourceOptimizerGUI(root)
    
    # Handle window closing
    def on_closing():
        app.optimizer.stop_optimization()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
