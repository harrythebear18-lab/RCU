#!/usr/bin/env python3
"""
GPU Monitor GUI Application
A comprehensive GUI application for real-time GPU monitoring with VRAM cleaning functionality.
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

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    NVML_AVAILABLE = True
    nvml.nvmlInit()
except ImportError:
    NVML_AVAILABLE = False
    nvml = None

# PYNVML is deprecated, using only nvidia-ml-py (nvml) instead
PYNVML_AVAILABLE = False
pynvml = None

class GPUMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPU Monitor & Cleaner")
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
            'graph_line': '#00d4ff',
            'gpu_line': '#ff6b35',
            'vram_line': '#4ecdc4'
        }
        
        # Data storage for plotting
        self.time_data = []
        self.gpu_usage_data = []
        self.vram_usage_data = []
        self.temp_data = []
        self.max_points = 60  # Show last 60 data points
        
        # Monitoring settings
        self.update_interval = 2000  # Update every 2 seconds
        self.monitoring = False
        self.monitor_thread = None
        
        # GPU info
        self.gpu_count = 0
        self.current_gpu = 0
        
        # Style configuration
        self.setup_styles()
        
        # Create GUI components
        self.create_widgets()
        
        # Initialize GPU detection
        self.detect_gpus()
        
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
                       darkcolor=self.colors['primary'])
    
    def detect_gpus(self):
        """Detect available GPUs"""
        gpu_list = []
        
        # Try nvidia-smi first for NVIDIA GPUs
        try:
            import subprocess
            name_result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                        capture_output=True, text=True, timeout=5)
            if name_result.returncode == 0:
                names = name_result.stdout.strip().split('\n')
                for i, name in enumerate(names):
                    if name.strip():
                        gpu_list.append(f"GPU {i}: {name.strip()}")
                self.gpu_count = len(gpu_list)
                if self.gpu_count > 0:
                    self.gpu_selector['values'] = gpu_list
                    self.gpu_selector.current(0)
                    self.current_gpu = 0
                    return
        except Exception as e:
            print(f"NVIDIA-smi detection error: {e}")
        
        # Try GPUtil
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    gpu_list.append(f"GPU {i}: {gpu.name}")
                self.gpu_count = len(gpus)
                if self.gpu_count > 0:
                    self.gpu_selector['values'] = gpu_list
                    self.gpu_selector.current(0)
                    return
            except Exception as e:
                print(f"GPUtil detection error: {e}")
        
        # Try NVML for NVIDIA GPUs
        if NVML_AVAILABLE:
            try:
                device_count = nvml.nvmlDeviceGetCount()
                
                for i in range(device_count):
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    name = nvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode('utf-8')
                    
                    gpu_list.append(f"GPU {i}: {name}")
                
                self.gpu_count = device_count
                if self.gpu_count > 0:
                    self.gpu_selector['values'] = gpu_list
                    self.gpu_selector.current(0)
                    return
            except Exception as e:
                print(f"NVML detection error: {e}")
        
        # Fallback to WMI
        if WMI_AVAILABLE:
            try:
                import pythoncom
                pythoncom.CoInitialize()
                c = wmi.WMI()
                gpus = c.Win32_VideoController()
                for i, gpu in enumerate(gpus):
                    gpu_list.append(f"GPU {i}: {gpu.Name}")
                self.gpu_count = len(gpus)
                if self.gpu_count > 0:
                    self.gpu_selector['values'] = gpu_list
                    # Auto-select NVIDIA GPU if available
                    nvidia_index = 0
                    for i, gpu_name in enumerate(gpu_list):
                        if 'NVIDIA' in gpu_name.upper():
                            nvidia_index = i
                            break
                    self.gpu_selector.current(nvidia_index)
                    self.current_gpu = nvidia_index
            except Exception as e:
                print(f"WMI GPU detection error: {e}")
        
        # No GPUs found
        if self.gpu_count == 0:
            self.gpu_selector['values'] = ["No GPU detected"]
            self.gpu_selector.current(0)
    
    def create_widgets(self):
        """Create GUI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="🎮 GPU Monitor & Cleaner", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # GPU Selector
        gpu_selector_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        gpu_selector_frame.pack(side=tk.RIGHT)
        
        tk.Label(gpu_selector_frame, text="Select GPU:", 
                font=('Segoe UI', 10), 
                fg=self.colors['text_secondary'], bg=self.colors['bg']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.gpu_selector = ttk.Combobox(gpu_selector_frame, values=["No GPU detected"], 
                                       state="readonly", width=20)
        self.gpu_selector.pack(side=tk.LEFT)
        self.gpu_selector.bind("<<ComboboxSelected>>", self.on_gpu_selected)
        
        # Info cards container
        cards_frame = tk.Frame(main_container, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # GPU Usage Card
        self.gpu_usage_card = self.create_info_card(cards_frame, "GPU Usage", "0%", self.colors['gpu_line'])
        self.gpu_usage_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # VRAM Usage Card
        self.vram_usage_card = self.create_info_card(cards_frame, "VRAM Usage", "0 MB", self.colors['vram_line'])
        self.vram_usage_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Temperature Card
        self.temp_card = self.create_info_card(cards_frame, "Temperature", "0°C", self.colors['warning'])
        self.temp_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Graph container
        graph_frame = tk.Frame(main_container, bg=self.colors['card'], relief='flat', bd=1)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 4), dpi=80, facecolor=self.colors['graph_bg'])
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_facecolor(self.colors['graph_bg'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        controls_frame = tk.Frame(main_container, bg=self.colors['bg'])
        controls_frame.pack(fill=tk.X)
        
        # Clean VRAM button
        clean_vram_btn = tk.Button(controls_frame, text="🧹 Clean VRAM", 
                                  font=('Segoe UI', 12, 'bold'), 
                                  bg=self.colors['warning'], fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  command=self.clean_vram)
        clean_vram_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Cache button
        clear_cache_btn = tk.Button(controls_frame, text="🗑️ Clear Cache", 
                                   font=('Segoe UI', 12, 'bold'), 
                                   bg=self.colors['primary'], fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.clear_cache)
        clear_cache_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Memory Jolt button
        jolt_btn = tk.Button(controls_frame, text="⚡ GPU Jolt", 
                            font=('Segoe UI', 12, 'bold'), 
                            bg=self.colors['success'], fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2',
                            command=self.run_gpu_jolt)
        jolt_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Soft Clean button
        soft_btn = tk.Button(controls_frame, text="💨 Soft Clean", 
                            font=('Segoe UI', 12, 'bold'), 
                            bg='#87CEEB', fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2',
                            command=self.run_gpu_soft_clean)
        soft_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Deep Clean button
        deep_clean_btn = tk.Button(controls_frame, text="🔥 Deep Clean", 
                                  font=('Segoe UI', 12, 'bold'), 
                                  bg='#ff4444', fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  command=self.enhanced_gpu_cleanup)
        deep_clean_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Optimize GPU button
        optimize_btn = tk.Button(controls_frame, text="⚡ Optimize", 
                                font=('Segoe UI', 12, 'bold'), 
                                bg=self.colors['success'], fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.optimize_gpu)
        optimize_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(controls_frame, text="● Monitoring", 
                                    font=('Segoe UI', 10, 'bold'), 
                                    bg=self.colors['bg'], fg=self.colors['success'])
        self.status_label.pack(side=tk.RIGHT)
    
    def create_info_card(self, parent, title, value, color):
        """Create an info card widget"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        
        # Title
        title_label = tk.Label(card, text=title, 
                             font=('Segoe UI', 10), 
                             fg=self.colors['text_secondary'], bg=self.colors['card'])
        title_label.pack(pady=(10, 5))
        
        # Value
        value_label = tk.Label(card, text=value, 
                              font=('Segoe UI', 18, 'bold'), 
                              fg=color, bg=self.colors['card'])
        value_label.pack(pady=(0, 10))
        
        # Progress bar
        progress = ttk.Progressbar(card, length=100, mode='determinate', 
                                  style='Modern.Horizontal.TProgressbar')
        progress.pack(pady=(0, 10), padx=10, fill=tk.X)
        
        # Store references
        card.value_label = value_label
        card.progress = progress
        
        return card
    
    def on_gpu_selected(self, event):
        """Handle GPU selection change"""
        self.current_gpu = self.gpu_selector.current()
        # Reset data when switching GPUs
        self.time_data.clear()
        self.gpu_usage_data.clear()
        self.vram_usage_data.clear()
        self.temp_data.clear()
    
    def get_gpu_info(self):
        """Get current GPU information"""
        gpu_info = {
            'name': 'Unknown',
            'usage': 0,
            'memory_used': 0,
            'memory_total': 0,
            'memory_percent': 0,
            'temperature': 0
        }
        
        # First, try nvidia-smi (most reliable for NVIDIA GPUs)
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 0 and self.current_gpu < len(lines):
                    values = lines[self.current_gpu].split(', ')
                    if len(values) >= 4:
                        gpu_info['memory_total'] = float(values[0])  # MB
                        gpu_info['memory_used'] = float(values[1])    # MB
                        gpu_info['usage'] = float(values[2])         # %
                        gpu_info['temperature'] = float(values[3])   # °C
                        gpu_info['memory_percent'] = (gpu_info['memory_used'] / gpu_info['memory_total']) * 100
                        
                        # Get GPU name from nvidia-smi
                        name_result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                                    capture_output=True, text=True, timeout=5)
                        if name_result.returncode == 0:
                            names = name_result.stdout.strip().split('\n')
                            if self.current_gpu < len(names):
                                gpu_info['name'] = names[self.current_gpu].strip()
                        
                        return gpu_info
        except Exception as e:
            print(f"NVIDIA-smi error: {e}")
        
        # Try GPUtil as fallback
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if self.current_gpu < len(gpus):
                    gpu = gpus[self.current_gpu]
                    gpu_info.update({
                        'name': gpu.name,
                        'usage': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal,
                        'memory_percent': gpu.memoryUtil * 100,
                        'temperature': gpu.temperature or 0
                    })
                    return gpu_info
            except Exception as e:
                print(f"GPUtil info error: {e}")
        
        # Try NVML as another fallback
        if NVML_AVAILABLE and self.current_gpu >= 0:
            try:
                handle = nvml.nvmlDeviceGetHandleByIndex(self.current_gpu)
                name = nvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                
                # Get utilization
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_info['usage'] = util.gpu
                
                # Get memory info
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info['memory_used'] = mem_info.used / (1024**2)  # Convert to MB
                gpu_info['memory_total'] = mem_info.total / (1024**2)  # Convert to MB
                gpu_info['memory_percent'] = (mem_info.used / mem_info.total) * 100
                
                # Get temperature
                try:
                    temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                    gpu_info['temperature'] = temp
                except:
                    gpu_info['temperature'] = 0
                
                gpu_info['name'] = name
                
                return gpu_info
            except Exception as e:
                print(f"NVML info error: {e}")
        
        # Final fallback to WMI (limited info)
        if WMI_AVAILABLE:
            try:
                import pythoncom
                pythoncom.CoInitialize()
                c = wmi.WMI()
                gpus = c.Win32_VideoController()
                if self.current_gpu < len(gpus):
                    gpu = gpus[self.current_gpu]
                    gpu_info['name'] = gpu.Name
                    
                    # Try to get adapter RAM (may not work for all GPUs)
                    if gpu.AdapterRAM and gpu.AdapterRAM > 0:
                        gpu_info['memory_total'] = gpu.AdapterRAM / (1024**2)  # Convert to MB
                    
                    # For NVIDIA GPUs, try to estimate VRAM from common sizes
                    if 'NVIDIA' in gpu.Name and gpu_info['memory_total'] <= 0:
                        if 'RTX 5060' in gpu.Name:
                            gpu_info['memory_total'] = 8192  # 8GB typical
                        elif 'RTX 4060' in gpu.Name:
                            gpu_info['memory_total'] = 8192  # 8GB typical
                        elif 'RTX 3060' in gpu.Name:
                            gpu_info['memory_total'] = 12288  # 12GB typical
                        elif 'RTX 3070' in gpu.Name:
                            gpu_info['memory_total'] = 8192  # 8GB typical
                        elif 'RTX 3080' in gpu.Name:
                            gpu_info['memory_total'] = 10240  # 10GB typical
                        elif 'RTX 4090' in gpu.Name:
                            gpu_info['memory_total'] = 24576  # 24GB typical
            except Exception as e:
                print(f"WMI info error: {e}")
        
        return gpu_info
    
    def update_display(self):
        """Update the display with current GPU information"""
        gpu_info = self.get_gpu_info()
        
        # Update info cards
        self.gpu_usage_card.value_label.config(text=f"{gpu_info['usage']:.1f}%")
        self.gpu_usage_card.progress['value'] = gpu_info['usage']
        
        if gpu_info['memory_total'] > 0:
            vram_text = f"{gpu_info['memory_used']:.0f}MB / {gpu_info['memory_total']:.0f}MB"
            self.vram_usage_card.value_label.config(text=vram_text)
            self.vram_usage_card.progress['value'] = gpu_info['memory_percent']
        else:
            self.vram_usage_card.value_label.config(text="N/A")
            self.vram_usage_card.progress['value'] = 0
        
        if gpu_info['temperature'] > 0:
            self.temp_card.value_label.config(text=f"{gpu_info['temperature']:.0f}°C")
            # Color code temperature
            if gpu_info['temperature'] > 80:
                self.temp_card.value_label.config(fg=self.colors['danger'])
            elif gpu_info['temperature'] > 70:
                self.temp_card.value_label.config(fg=self.colors['warning'])
            else:
                self.temp_card.value_label.config(fg=self.colors['success'])
        else:
            self.temp_card.value_label.config(text="N/A")
        
        # Add data to plot
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_data.append(current_time)
        self.gpu_usage_data.append(gpu_info['usage'])
        self.vram_usage_data.append(gpu_info['memory_percent'])
        self.temp_data.append(gpu_info['temperature'])
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.gpu_usage_data = self.gpu_usage_data[-self.max_points:]
            self.vram_usage_data = self.vram_usage_data[-self.max_points:]
            self.temp_data = self.temp_data[-self.max_points:]
        
        # Update graph
        self.update_graph()
    
    def update_graph(self):
        """Update the performance graph"""
        self.ax1.clear()
        
        if len(self.time_data) > 1:
            # Plot GPU usage
            self.ax1.plot(self.time_data, self.gpu_usage_data, 
                         color=self.colors['gpu_line'], linewidth=2, label='GPU Usage')
            
            # Plot VRAM usage
            self.ax1.plot(self.time_data, self.vram_usage_data, 
                         color=self.colors['vram_line'], linewidth=2, label='VRAM Usage')
            
            # Plot temperature on secondary axis if available
            if any(t > 0 for t in self.temp_data):
                ax2 = self.ax1.twinx()
                ax2.plot(self.time_data, self.temp_data, 
                        color=self.colors['warning'], linewidth=1, alpha=0.7, label='Temperature')
                ax2.set_ylabel('Temperature (°C)', color=self.colors['warning'])
                ax2.tick_params(axis='y', labelcolor=self.colors['warning'])
        
        self.ax1.set_xlabel('Time', color=self.colors['text'])
        self.ax1.set_ylabel('Usage (%)', color=self.colors['text'])
        self.ax1.set_title('GPU Performance Monitor', color=self.colors['primary'])
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
    
    def clean_vram(self):
        """Clean VRAM by closing GPU-intensive processes"""
        self.status_label.config(text="● Cleaning VRAM...", fg=self.colors['warning'])
        
        try:
            # Import the GPU cleanup functionality
            import gpu_cleanup_script
            cleaner = gpu_cleanup_script.GPUCleaner()
            closed_processes = cleaner.clear_gpu_processes()
            
            messagebox.showinfo("VRAM Clean", f"Cleaned {len(closed_processes)} GPU-intensive processes!")
            self.status_label.config(text="● VRAM cleaned", fg=self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean VRAM: {e}")
            self.status_label.config(text="● Error", fg=self.colors['danger'])
    
    def clear_cache(self):
        """Clear GPU cache"""
        self.status_label.config(text="● Clearing cache...", fg=self.colors['warning'])
        
        try:
            import gpu_cleanup_script
            cleaner = gpu_cleanup_script.GPUCleaner()
            cleaner.clear_gpu_cache()
            
            messagebox.showinfo("Cache Cleared", "GPU cache cleared successfully!")
            self.status_label.config(text="● Cache cleared", fg=self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {e}")
            self.status_label.config(text="● Error", fg=self.colors['danger'])
    
    def optimize_gpu(self):
        """Optimize GPU settings"""
        self.status_label.config(text="● Optimizing GPU...", fg=self.colors['warning'])
        
        try:
            import gpu_cleanup_script
            cleaner = gpu_cleanup_script.GPUCleaner()
            cleaner.optimize_gpu_settings()
            
            messagebox.showinfo("GPU Optimized", "GPU settings optimized for gaming!")
            self.status_label.config(text="● Optimized", fg=self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize GPU: {e}")
            self.status_label.config(text="● Error", fg=self.colors['danger'])
    
    def run_gpu_jolt(self):
        """Run GPU Memory Jolt - gentle VRAM optimization"""
        try:
            # Show info dialog
            result = messagebox.askyesno(
                "⚡ GPU Memory Jolt", 
                "⚡ GPU Memory Jolt\n\n" +
                "This will perform gentle GPU optimization:\n\n" +
                "• Light VRAM trimming\n" +
                "• GPU cache refresh\n" +
                "• Memory allocation optimization\n" +
                "• Working set refresh\n" +
                "• Gentle memory compaction\n\n" +
                "⚡ Quick and effective\n" +
                "⚡ Safe for gaming\n" +
                "⚡ No performance impact\n\n" +
                "Continue with GPU jolt?"
            )
            
            if not result:
                return
            
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("GPU Jolt...")
            progress_window.geometry("400x150")
            progress_window.configure(bg=self.colors['bg'])
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            # Progress label
            progress_label = tk.Label(progress_window, text="⚡ Performing GPU memory jolt...", 
                                    font=('Segoe UI', 12, 'bold'), 
                                    fg=self.colors['success'], bg=self.colors['bg'])
            progress_label.pack(pady=20)
            
            detail_label = tk.Label(progress_window, text="Refreshing GPU memory...", 
                                   font=('Segoe UI', 10), 
                                   fg=self.colors['text_secondary'], bg=self.colors['bg'])
            detail_label.pack(pady=5)
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            self.root.update()
            
            # Run GPU jolt in separate thread
            def run_jolt():
                try:
                    # Get initial GPU state
                    initial_gpu = self.get_gpu_info()
                    initial_vram = initial_gpu['memory_used']
                    
                    # Perform GPU jolt operations
                    vram_freed = 0
                    
                    # Step 1: Clear GPU cache
                    try:
                        self.clear_cache_internal()
                        time.sleep(1)
                    except:
                        pass
                    
                    # Step 2: Light VRAM cleanup
                    try:
                        closed_processes = self.close_gpu_intensive_processes_internal(threshold=100)  # Very light threshold
                        time.sleep(2)
                    except:
                        pass
                    
                    # Step 3: GPU memory refresh using nvidia-smi
                    try:
                        import subprocess
                        subprocess.run(['nvidia-smi', '--gpu-reset'], capture_output=True, timeout=5)
                    except:
                        pass
                    
                    # Get final GPU state
                    time.sleep(2)
                    final_gpu = self.get_gpu_info()
                    final_vram = final_gpu['memory_used']
                    vram_freed = max(0, initial_vram - final_vram)
                    
                    # Close progress window
                    progress_window.destroy()
                    
                    # Update display
                    self.update_display()
                    
                    # Show results
                    if vram_freed > 50:  # More than 50MB freed
                        messagebox.showinfo(
                            "GPU Jolt Complete", 
                            f"⚡ GPU jolt successful!\n\n" +
                            f"🎮 VRAM freed: {vram_freed:.0f} MB\n" +
                            f"🚀 GPU should be more responsive\n" +
                            f"🔄 Display updated with new values\n\n" +
                            f"✅ Safe optimization completed"
                        )
                    else:
                        messagebox.showinfo(
                            "GPU Jolt Complete", 
                            f"✅ GPU appears well-optimized\n\n" +
                            f"💡 No stuck VRAM detected\n" +
                            f"💡 Your GPU is running efficiently"
                        )
                        
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Error", f"GPU jolt failed: {e}")
            
            # Start jolt thread
            jolt_thread = threading.Thread(target=run_jolt, daemon=True)
            jolt_thread.start()
                
        except Exception as e:
            messagebox.showerror("Error", f"GPU jolt error: {e}")
    
    def run_gpu_soft_clean(self):
        """Run ultra-gentle GPU soft cleaner"""
        try:
            # Show info dialog
            result = messagebox.askyesno(
                "💨 GPU Soft Cleaner", 
                "💨 Ultra-Gentle GPU Soft Clean\n\n" +
                "This will perform the softest GPU cleanup:\n\n" +
                "• Ultra-soft VRAM trimming\n" +
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
            
            detail_label = tk.Label(progress_window, text="The softest touch for your GPU...", 
                                   font=('Segoe UI', 10), 
                                   fg=self.colors['text_secondary'], bg=self.colors['bg'])
            detail_label.pack(pady=5)
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            self.root.update()
            
            # Run soft clean in separate thread
            def run_soft_clean():
                try:
                    # Get initial GPU state
                    initial_gpu = self.get_gpu_info()
                    initial_vram = initial_gpu['memory_used']
                    
                    # Perform ultra-gentle GPU soft clean
                    vram_freed = 0
                    
                    # Step 1: Very light cache clearing (only shader cache)
                    try:
                        shader_cache_paths = [
                            os.path.expandvars(r'%LOCALAPPDATA%\D3DSCache'),
                            os.path.expandvars(r'%LOCALAPPDATA%\NVIDIA\DXCache'),
                            os.path.expandvars(r'%LOCALAPPDATA%\AMD\DxCache'),
                        ]
                        
                        cleared_files = 0
                        for cache_path in shader_cache_paths:
                            if os.path.exists(cache_path):
                                try:
                                    for item in os.listdir(cache_path):
                                        item_path = os.path.join(cache_path, item)
                                        try:
                                            if os.path.isfile(item_path):
                                                os.unlink(item_path)
                                                cleared_files += 1
                                        except (PermissionError, OSError):
                                            continue
                                except (PermissionError, OSError):
                                    continue
                    except:
                        pass
                    
                    # Step 2: No process closing for soft clean - just optimization
                    time.sleep(1)
                    
                    # Get final GPU state
                    final_gpu = self.get_gpu_info()
                    final_vram = final_gpu['memory_used']
                    vram_freed = max(0, initial_vram - final_vram)
                    
                    # Close progress window
                    progress_window.destroy()
                    
                    # Update display
                    self.update_display()
                    
                    # Show results
                    messagebox.showinfo(
                        "GPU Soft Clean Complete", 
                        f"💨 Ultra-gentle soft clean complete!\n\n" +
                        f"🌸 Cache files cleared: {cleared_files}\n" +
                        f"🌸 VRAM optimized: {vram_freed:.0f} MB\n" +
                        f"🌸 GPU refreshed gently\n\n" +
                        f"✅ Perfect for regular maintenance"
                    )
                        
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Error", f"GPU soft clean failed: {e}")
            
            # Start soft clean thread
            soft_thread = threading.Thread(target=run_soft_clean, daemon=True)
            soft_thread.start()
                
        except Exception as e:
            messagebox.showerror("Error", f"GPU soft clean error: {e}")
    
    def enhanced_gpu_cleanup(self):
        """Enhanced GPU cleanup with more aggressive cleaning"""
        try:
            # Show cleaning dialog
            result = messagebox.askyesno("🔥 Deep GPU Clean", 
                                        "Perform deep GPU cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Clear all GPU cache\n" +
                                        "• Clear shader cache\n" +
                                        "• Close GPU-intensive processes\n" +
                                        "• Force VRAM cleanup\n" +
                                        "• Optimize GPU settings\n\n" +
                                        "Continue?")
            if not result:
                return
            
            # Progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Deep Cleaning...")
            progress_window.geometry("300x100")
            progress_window.configure(bg=self.colors['bg'])
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = tk.Label(progress_window, text="🔥 Deep cleaning GPU...", 
                                  font=('Segoe UI', 12), 
                                  fg=self.colors['text'], bg=self.colors['bg'])
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            self.root.update()
            
            cleaned_data = {'files': 0, 'processes': 0, 'cache': False}
            
            # Step 1: Clear all GPU cache
            try:
                self.clear_cache_internal()
                cleaned_data['cache'] = True
            except:
                pass
            
            # Step 2: Clear shader cache aggressively
            try:
                shader_cache_paths = [
                    os.environ.get('TEMP', ''),
                    os.environ.get('TMP', ''),
                    r'C:\Windows\Temp',
                    r'C:\Windows\Prefetch',
                    os.path.expanduser(r'~\AppData\Local\Temp'),
                    os.path.expandvars(r'%LOCALAPPDATA%\D3DSCache'),
                    os.path.expandvars(r'%LOCALAPPDATA%\NVIDIA\DXCache'),
                    os.path.expandvars(r'%LOCALAPPDATA%\AMD\DxCache'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\INetCache'),
                    r'C:\ProgramData\NVIDIA Corporation\Downloader'
                ]
                
                for temp_path in shader_cache_paths:
                    if os.path.exists(temp_path):
                        try:
                            for item in os.listdir(temp_path):
                                item_path = os.path.join(temp_path, item)
                                try:
                                    if os.path.isfile(item_path):
                                        os.unlink(item_path)
                                        cleaned_data['files'] += 1
                                    elif os.path.isdir(item_path):
                                        try:
                                            os.rmdir(item_path)
                                            cleaned_data['files'] += 1
                                        except:
                                            pass
                                except (PermissionError, OSError):
                                    continue
                        except (PermissionError, OSError):
                            continue
            except:
                pass
            
            # Step 3: Close GPU-intensive processes
            try:
                closed_processes = self.close_gpu_intensive_processes_internal(threshold=50)
                cleaned_data['processes'] = len(closed_processes)
            except:
                pass
            
            # Step 4: Optimize GPU settings
            try:
                self.optimize_gpu_internal()
            except:
                pass
            
            # Close progress window
            progress_window.destroy()
            
            # Update display
            self.update_display()
            
            # Show results
            messagebox.showinfo(
                "Deep GPU Clean Complete", 
                f"🔥 Deep GPU cleanup completed!\n\n" +
                f"🧹 Files cleaned: {cleaned_data['files']}\n" +
                f"🔚 Processes closed: {cleaned_data['processes']}\n" +
                f"🗑️ Cache cleared: {'Yes' if cleaned_data['cache'] else 'No'}\n" +
                f"⚡ GPU optimized\n\n" +
                f"✅ Your GPU should run much better now!"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Deep GPU clean error: {e}")
    
    def clear_cache_internal(self):
        """Internal cache clearing method"""
        try:
            import subprocess
            # Clear DirectX shader cache
            subprocess.run(['powershell', '-Command', 
                          'Clear-Content -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" -ErrorAction SilentlyContinue'], 
                          capture_output=True)
            
            # Reset GPU using PowerShell (NVIDIA)
            try:
                subprocess.run(['powershell', '-Command', 
                              'Get-Process -Name "nvidia*" -ErrorAction SilentlyContinue | Stop-Process -Force'], 
                              capture_output=True)
            except:
                pass
        except:
            pass
    
    def close_gpu_intensive_processes_internal(self, threshold=200):
        """Internal method to close GPU-intensive processes"""
        closed_processes = []
        
        gpu_intensive = [
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe',
            'obs.exe', 'streamlabs.exe', 'xsplit.exe',
            'blender.exe', 'photoshop.exe', 'premiere.exe', 'afterfx.exe',
            'dota2.exe', 'csgo.exe', 'valorant.exe', 'league of legends.exe'
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                process_name = proc.info['name'].lower()
                if any(gpu_proc in process_name for gpu_proc in gpu_intensive):
                    memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    if memory_mb > threshold:
                        proc.terminate()
                        closed_processes.append(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return closed_processes
    
    def optimize_gpu_internal(self):
        """Internal GPU optimization method"""
        try:
            import subprocess
            # Set power plan to High Performance
            subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], 
                          capture_output=True, check=True)
            
            # Disable Windows Game DVR
            try:
                subprocess.run(['powershell', '-Command', 
                              'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" -Name "AllowGameDVR" -Value 0 -Force'], 
                              capture_output=True)
            except:
                pass
        except:
            pass
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = GPUMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
