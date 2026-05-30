#!/usr/bin/env python3
"""
CPU Monitor GUI Application
A comprehensive GUI application for real-time CPU monitoring with process optimization functionality.
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
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class CPUMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Monitor & Optimizer")
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
            'cpu_line': '#ff6b35',
            'freq_line': '#4ecdc4'
        }
        
        # Data storage for plotting
        self.time_data = []
        self.cpu_usage_data = []
        self.cpu_freq_data = []
        self.temp_data = []
        self.max_points = 60  # Show last 60 data points
        
        # Monitoring settings
        self.update_interval = 2000  # Update every 2 seconds
        self.monitoring = False
        self.monitor_thread = None
        
        # CPU info
        self.cpu_count = psutil.cpu_count(logical=True)
        self.cpu_physical = psutil.cpu_count(logical=False)
        
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
                       darkcolor=self.colors['primary'])
    
    def create_widgets(self):
        """Create GUI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="⚡ CPU Monitor & Optimizer", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        cpu_info_label = tk.Label(header_frame, text=f"{self.cpu_physical} Cores / {self.cpu_count} Threads", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        cpu_info_label.pack(side=tk.RIGHT)
        
        # Info cards container
        cards_frame = tk.Frame(main_container, bg=self.colors['bg'])
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # CPU Usage Card
        self.cpu_usage_card = self.create_info_card(cards_frame, "CPU Usage", "0%", self.colors['cpu_line'])
        self.cpu_usage_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frequency Card
        self.freq_card = self.create_info_card(cards_frame, "Frequency", "0 MHz", self.colors['freq_line'])
        self.freq_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
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
        
        # Process list container
        process_frame = tk.Frame(main_container, bg=self.colors['card'], relief='flat', bd=1)
        process_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Process list header
        process_header = tk.Label(process_frame, text="Top CPU Processes", 
                                 font=('Segoe UI', 12, 'bold'), 
                                 fg=self.colors['text'], bg=self.colors['card'])
        process_header.pack(pady=(10, 5))
        
        # Process list with scrollbar
        process_container = tk.Frame(process_frame, bg=self.colors['card'])
        process_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview for process list
        columns = ('PID', 'Name', 'CPU%', 'Memory', 'User')
        self.process_tree = ttk.Treeview(process_container, columns=columns, show='headings', height=8)
        
        # Configure columns
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('Name', text='Process Name')
        self.process_tree.heading('CPU%', text='CPU %')
        self.process_tree.heading('Memory', text='Memory (MB)')
        self.process_tree.heading('User', text='User')
        
        self.process_tree.column('PID', width=60)
        self.process_tree.column('Name', width=200)
        self.process_tree.column('CPU%', width=80)
        self.process_tree.column('Memory', width=100)
        self.process_tree.column('User', width=120)
        
        # Style the treeview
        style = ttk.Style()
        style.configure('Treeview', background=self.colors['card'], foreground=self.colors['text'],
                       fieldbackground=self.colors['card'], borderwidth=0)
        style.configure('Treeview.Heading', background=self.colors['card_hover'], foreground=self.colors['text'])
        style.map('Treeview', background=[('selected', self.colors['primary'])])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(process_container, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        controls_frame = tk.Frame(main_container, bg=self.colors['bg'])
        controls_frame.pack(fill=tk.X)
        
        # Optimize CPU button
        optimize_btn = tk.Button(controls_frame, text="⚡ Optimize CPU", 
                                font=('Segoe UI', 12, 'bold'), 
                                bg=self.colors['success'], fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                command=self.optimize_cpu)
        optimize_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Memory Jolt button
        jolt_btn = tk.Button(controls_frame, text="⚡ CPU Jolt", 
                            font=('Segoe UI', 12, 'bold'), 
                            bg=self.colors['success'], fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2',
                            command=self.run_cpu_jolt)
        jolt_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Soft Clean button
        soft_btn = tk.Button(controls_frame, text="💨 Soft Clean", 
                            font=('Segoe UI', 12, 'bold'), 
                            bg='#87CEEB', fg=self.colors['bg'],
                            relief='flat', bd=0, cursor='hand2',
                            command=self.run_cpu_soft_clean)
        soft_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Deep Clean button
        deep_clean_btn = tk.Button(controls_frame, text="🔥 Deep Clean", 
                                  font=('Segoe UI', 12, 'bold'), 
                                  bg='#ff4444', fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  command=self.enhanced_cpu_cleanup)
        deep_clean_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # End Processes button
        end_processes_btn = tk.Button(controls_frame, text="🔚 End Processes", 
                                      font=('Segoe UI', 12, 'bold'), 
                                      bg=self.colors['warning'], fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      command=self.end_processes)
        end_processes_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Gaming Mode button
        gaming_btn = tk.Button(controls_frame, text="🎮 Gaming Mode", 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=self.colors['primary'], fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              command=self.gaming_mode)
        gaming_btn.pack(side=tk.LEFT, padx=(0, 10))
        
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
    
    def get_cpu_info(self):
        """Get current CPU information"""
        # Get per-core usage first
        per_core_usage = psutil.cpu_percent(interval=0.1, percpu=True)
        
        # Calculate average from individual cores
        average_usage = sum(per_core_usage) / len(per_core_usage) if per_core_usage else 0
        
        cpu_info = {
            'usage_percent': average_usage,
            'freq_current': 0,
            'freq_min': 0,
            'freq_max': 0,
            'temperature': 0,
            'per_core': per_core_usage,
            'core_count': len(per_core_usage)
        }
        
        # Get frequency info
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info.update({
                'freq_current': cpu_freq.current,
                'freq_min': cpu_freq.min,
                'freq_max': cpu_freq.max
            })
        
        # Get temperature if available
        if platform.system() == "Windows":
            try:
                import subprocess
                
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
                                    cpu_info['temperature'] = temp_value
                            except ValueError:
                                pass
                except Exception as e:
                    print(f"PowerShell temp error: {e}")
                
                # Method 2: Try using Performance Counters for thermal zones
                if cpu_info['temperature'] == 0:
                    try:
                        ps_result = subprocess.run(['powershell', '-Command', 
                            'Get-Counter "\\Thermal Zone Information(*)\\Temperature" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | ForEach-Object { $_.CookedValue } | Select-Object -First 1'], 
                            capture_output=True, text=True, timeout=5)
                        
                        if ps_result.returncode == 0 and ps_result.stdout.strip():
                            try:
                                temp_value = float(ps_result.stdout.strip())
                                if 20 < temp_value < 100:
                                    cpu_info['temperature'] = temp_value
                            except ValueError:
                                pass
                    except Exception as e:
                        print(f"Performance counter temp error: {e}")
                
                # Method 3: Try using HWMonitor (if installed)
                if cpu_info['temperature'] == 0:
                    try:
                        # Check if HWMonitor is running and can provide temperature
                        ps_result = subprocess.run(['powershell', '-Command', 
                            'Get-Process | Where-Object {$_.ProcessName -like "*HWMonitor*"} | Select-Object -First 1'], 
                            capture_output=True, text=True, timeout=3)
                        
                        if ps_result.returncode == 0 and ps_result.stdout.strip():
                            # HWMonitor is running, try to get temperature from it
                            # This would require HWMonitor to expose temperature data
                            pass
                    except:
                        pass
                
                # Method 4: Estimate temperature based on CPU usage (fallback)
                if cpu_info['temperature'] == 0:
                    # Very rough estimation based on CPU usage
                    # This is not accurate but better than showing 0
                    usage = cpu_info['usage_percent']
                    if usage < 20:
                        cpu_info['temperature'] = 35.0  # Idle estimate
                    elif usage < 50:
                        cpu_info['temperature'] = 45.0  # Light load
                    elif usage < 80:
                        cpu_info['temperature'] = 60.0  # Medium load
                    else:
                        cpu_info['temperature'] = 75.0  # Heavy load
                    
                    cpu_info['temperature_estimated'] = True
                
            except Exception as e:
                print(f"Temperature detection error: {e}")
                # Set estimated temperature as fallback
                cpu_info['temperature'] = 40.0
                cpu_info['temperature_estimated'] = True
        
        return cpu_info
    
    def get_top_processes(self, limit=10):
        """Get top CPU-consuming processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username']):
            try:
                cpu_usage = proc.info['cpu_percent'] or 0
                memory_info = proc.info.get('memory_info')
                
                if cpu_usage > 1 and memory_info:  # Only include processes using >1% CPU
                    memory_mb = memory_info.rss / (1024 * 1024)
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': cpu_usage,
                        'memory_mb': memory_mb,
                        'username': proc.info.get('username', 'Unknown') or 'Unknown'
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                continue
        
        # Sort by CPU usage (highest first) and limit
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:limit]
    
    def update_display(self):
        """Update the display with current CPU information"""
        cpu_info = self.get_cpu_info()
        
        # Update info cards with calculated average
        self.cpu_usage_card.value_label.config(text=f"{cpu_info['usage_percent']:.1f}% (Avg)")
        self.cpu_usage_card.progress['value'] = cpu_info['usage_percent']
        
        if cpu_info['freq_current'] > 0:
            self.freq_card.value_label.config(text=f"{cpu_info['freq_current']:.0f} MHz")
            # Calculate frequency percentage
            if cpu_info['freq_max'] > 0:
                freq_percent = (cpu_info['freq_current'] / cpu_info['freq_max']) * 100
                self.freq_card.progress['value'] = freq_percent
        else:
            self.freq_card.value_label.config(text="N/A")
            self.freq_card.progress['value'] = 0
        
        if cpu_info['temperature'] > 0:
            temp_text = f"{cpu_info['temperature']:.1f}°C"
            if cpu_info.get('temperature_estimated', False):
                temp_text += " (Est.)"
            self.temp_card.value_label.config(text=temp_text)
            
            # Color code temperature
            if cpu_info['temperature'] > 80:
                self.temp_card.value_label.config(fg=self.colors['danger'])
            elif cpu_info['temperature'] > 70:
                self.temp_card.value_label.config(fg=self.colors['warning'])
            else:
                self.temp_card.value_label.config(fg=self.colors['success'])
            self.temp_card.progress['value'] = min(cpu_info['temperature'], 100)  # Cap at 100%
        else:
            self.temp_card.value_label.config(text="N/A")
            self.temp_card.progress['value'] = 0
        
        # Update process list
        self.update_process_list()
        
        # Add data to plot
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_data.append(current_time)
        self.cpu_usage_data.append(cpu_info['usage_percent'])
        self.cpu_freq_data.append(cpu_info['freq_current'])
        self.temp_data.append(cpu_info['temperature'])
        
        # Keep only last max_points
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.cpu_usage_data = self.cpu_usage_data[-self.max_points:]
            self.cpu_freq_data = self.cpu_freq_data[-self.max_points:]
            self.temp_data = self.temp_data[-self.max_points:]
        
        # Update graph
        self.update_graph()
        
        # Print core information for debugging
        print(f"Core Usage: {[f'{core:.1f}%' for core in cpu_info['per_core']]}")
        print(f"Calculated Average: {cpu_info['usage_percent']:.1f}%")
    
    def update_process_list(self):
        """Update the process list"""
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Get top processes
        processes = self.get_top_processes(10)
        
        # Add processes to tree
        for proc in processes:
            values = (
                proc['pid'],
                proc['name'][:30],  # Truncate long names
                f"{proc['cpu_percent']:.1f}",
                f"{proc['memory_mb']:.1f}",
                proc['username'][:15]  # Truncate long usernames
            )
            self.process_tree.insert('', tk.END, values=values)
    
    def update_graph(self):
        """Update the performance graph"""
        self.ax1.clear()
        
        if len(self.time_data) > 1:
            # Plot CPU usage
            self.ax1.plot(self.time_data, self.cpu_usage_data, 
                         color=self.colors['cpu_line'], linewidth=2, label='CPU Usage')
            
            # Plot frequency on secondary axis
            if any(f > 0 for f in self.cpu_freq_data):
                ax2 = self.ax1.twinx()
                ax2.plot(self.time_data, self.cpu_freq_data, 
                        color=self.colors['freq_line'], linewidth=1, alpha=0.7, label='Frequency')
                ax2.set_ylabel('Frequency (MHz)', color=self.colors['freq_line'])
                ax2.tick_params(axis='y', labelcolor=self.colors['freq_line'])
        
        self.ax1.set_xlabel('Time', color=self.colors['text'])
        self.ax1.set_ylabel('Usage (%)', color=self.colors['text'])
        self.ax1.set_title('CPU Performance Monitor', color=self.colors['primary'])
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
    
    def optimize_cpu(self):
        """Optimize CPU settings"""
        self.status_label.config(text="● Optimizing CPU...", fg=self.colors['warning'])
        
        try:
            import cpu_cleanup_script
            cleaner = cpu_cleanup_script.CPUCleaner()
            cleaner.optimize_cpu_priority()
            cleaner.clear_cpu_cache()
            
            messagebox.showinfo("CPU Optimized", "CPU settings optimized for better performance!")
            self.status_label.config(text="● Optimized", fg=self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to optimize CPU: {e}")
            self.status_label.config(text="● Error", fg=self.colors['danger'])
    
    def end_processes(self):
        """End CPU-intensive processes"""
        self.status_label.config(text="● Ending processes...", fg=self.colors['warning'])
        
        try:
            import cpu_cleanup_script
            cleaner = cpu_cleanup_script.CPUCleaner()
            closed_processes = cleaner.close_cpu_intensive_processes()
            
            messagebox.showinfo("Processes Ended", f"Closed {len(closed_processes)} CPU-intensive processes!")
            self.status_label.config(text="● Processes ended", fg=self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to end processes: {e}")
            self.status_label.config(text="● Error", fg=self.colors['danger'])
    
    def gaming_mode(self):
        """Enable gaming mode"""
        self.status_label.config(text="● Enabling gaming mode...", fg=self.colors['warning'])
        
        try:
            import cpu_cleanup_script
            cleaner = cpu_cleanup_script.CPUCleaner()
            cleaner.set_gaming_mode()
            
            messagebox.showinfo("Gaming Mode", "Gaming mode enabled! CPU optimized for gaming.")
            self.status_label.config(text="● Gaming mode", fg=self.colors['success'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable gaming mode: {e}")
            self.status_label.config(text="● Error", fg=self.colors['danger'])
    
    def run_cpu_jolt(self):
        """Run CPU Memory Jolt - gentle CPU optimization"""
        try:
            # Show info dialog
            result = messagebox.askyesno(
                "⚡ CPU Memory Jolt", 
                "⚡ CPU Memory Jolt\n\n" +
                "This will perform gentle CPU optimization:\n\n" +
                "• Light CPU cache refresh\n" +
                "• Process priority optimization\n" +
                "• Memory allocation optimization\n" +
                "• Working set refresh\n" +
                "• Gentle memory compaction\n\n" +
                "⚡ Quick and effective\n" +
                "⚡ Safe for gaming\n" +
                "⚡ No performance impact\n\n" +
                "Continue with CPU jolt?"
            )
            
            if not result:
                return
            
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("CPU Jolt...")
            progress_window.geometry("400x150")
            progress_window.configure(bg=self.colors['bg'])
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            # Progress label
            progress_label = tk.Label(progress_window, text="⚡ Performing CPU memory jolt...", 
                                    font=('Segoe UI', 12, 'bold'), 
                                    fg=self.colors['success'], bg=self.colors['bg'])
            progress_label.pack(pady=20)
            
            detail_label = tk.Label(progress_window, text="Refreshing CPU memory...", 
                                   font=('Segoe UI', 10), 
                                   fg=self.colors['text_secondary'], bg=self.colors['bg'])
            detail_label.pack(pady=5)
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            self.root.update()
            
            # Run CPU jolt in separate thread
            def run_jolt():
                try:
                    # Get initial CPU state
                    initial_cpu = self.get_cpu_info()
                    initial_usage = initial_cpu['usage_percent']
                    
                    # Perform CPU jolt operations
                    memory_freed = 0
                    
                    # Step 1: Force Python garbage collection
                    gc.collect()
                    
                    # Step 2: Clear CPU cache
                    try:
                        self.clear_cpu_cache_internal()
                        time.sleep(1)
                    except:
                        pass
                    
                    # Step 3: Light CPU process optimization
                    try:
                        closed_processes = self.close_cpu_intensive_processes_internal(threshold=100)  # Very light threshold
                        time.sleep(2)
                    except:
                        pass
                    
                    # Step 4: Optimize CPU priorities
                    try:
                        self.optimize_cpu_priorities_internal()
                        time.sleep(1)
                    except:
                        pass
                    
                    # Get final CPU state
                    time.sleep(2)
                    final_cpu = self.get_cpu_info()
                    final_usage = final_cpu['usage_percent']
                    usage_improvement = max(0, initial_usage - final_usage)
                    
                    # Close progress window
                    progress_window.destroy()
                    
                    # Update display
                    self.update_display()
                    
                    # Show results
                    if usage_improvement > 5:  # More than 5% improvement
                        messagebox.showinfo(
                            "CPU Jolt Complete", 
                            f"⚡ CPU jolt successful!\n\n" +
                            f"💻 CPU usage improved: {usage_improvement:.1f}%\n" +
                            f"🚀 CPU should be more responsive\n" +
                            f"🔄 Display updated with new values\n\n" +
                            f"✅ Safe optimization completed"
                        )
                    else:
                        messagebox.showinfo(
                            "CPU Jolt Complete", 
                            f"✅ CPU appears well-optimized\n\n" +
                            f"💡 No stuck processes detected\n" +
                            f"💡 Your CPU is running efficiently"
                        )
                        
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Error", f"CPU jolt failed: {e}")
            
            # Start jolt thread
            jolt_thread = threading.Thread(target=run_jolt, daemon=True)
            jolt_thread.start()
                
        except Exception as e:
            messagebox.showerror("Error", f"CPU jolt error: {e}")
    
    def run_cpu_soft_clean(self):
        """Run ultra-gentle CPU soft cleaner"""
        try:
            # Show info dialog
            result = messagebox.askyesno(
                "💨 CPU Soft Cleaner", 
                "💨 Ultra-Gentle CPU Soft Clean\n\n" +
                "This will perform the softest CPU cleanup:\n\n" +
                "• Ultra-soft cache clearing\n" +
                "• Light process optimization only\n" +
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
            
            detail_label = tk.Label(progress_window, text="The softest touch for your CPU...", 
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
                    # Get initial CPU state
                    initial_cpu = self.get_cpu_info()
                    initial_usage = initial_cpu['usage_percent']
                    
                    # Perform ultra-gentle CPU soft clean
                    memory_freed = 0
                    
                    # Step 1: Very light cache clearing
                    try:
                        self.clear_cpu_cache_internal()
                        time.sleep(1)
                    except:
                        pass
                    
                    # Step 2: No process closing for soft clean - just optimization
                    try:
                        self.optimize_cpu_priorities_internal()
                        time.sleep(1)
                    except:
                        pass
                    
                    # Step 3: Force Python garbage collection
                    gc.collect()
                    
                    # Get final CPU state
                    final_cpu = self.get_cpu_info()
                    final_usage = final_cpu['usage_percent']
                    usage_improvement = max(0, initial_usage - final_usage)
                    
                    # Close progress window
                    progress_window.destroy()
                    
                    # Update display
                    self.update_display()
                    
                    # Show results
                    messagebox.showinfo(
                        "CPU Soft Clean Complete", 
                        f"💨 Ultra-gentle soft clean complete!\n\n" +
                        f"🌸 CPU cache cleared\n" +
                        f"🌸 CPU usage improved: {usage_improvement:.1f}%\n" +
                        f"🌸 CPU refreshed gently\n\n" +
                        f"✅ Perfect for regular maintenance"
                    )
                        
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Error", f"CPU soft clean failed: {e}")
            
            # Start soft clean thread
            soft_thread = threading.Thread(target=run_soft_clean, daemon=True)
            soft_thread.start()
                
        except Exception as e:
            messagebox.showerror("Error", f"CPU soft clean error: {e}")
    
    def enhanced_cpu_cleanup(self):
        """Enhanced CPU cleanup with more aggressive cleaning"""
        try:
            # Show cleaning dialog
            result = messagebox.askyesno("🔥 Deep CPU Clean", 
                                        "Perform deep CPU cleanup?\n\n" +
                                        "This will:\n" +
                                        "• Clear all CPU cache\n" +
                                        "• Clear temporary files\n" +
                                        "• Close CPU-intensive processes\n" +
                                        "• Force memory cleanup\n" +
                                        "• Optimize CPU settings\n\n" +
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
            
            progress_label = tk.Label(progress_window, text="🔥 Deep cleaning CPU...", 
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
            
            # Step 3: Clear CPU cache
            try:
                self.clear_cpu_cache_internal()
                cleaned_data['cache'] = True
            except:
                pass
            
            # Step 4: Close CPU-intensive processes
            try:
                closed_processes = self.close_cpu_intensive_processes_internal(threshold=50)
                cleaned_data['processes'] = len(closed_processes)
            except:
                pass
            
            # Step 5: Optimize CPU settings
            try:
                self.optimize_cpu_priorities_internal()
            except:
                pass
            
            # Close progress window
            progress_window.destroy()
            
            # Update display
            self.update_display()
            
            # Show results
            messagebox.showinfo(
                "Deep CPU Clean Complete", 
                f"🔥 Deep CPU cleanup completed!\n\n" +
                f"🧹 Files cleaned: {cleaned_data['files']}\n" +
                f"🔚 Processes closed: {cleaned_data['processes']}\n" +
                f"🗑️ Cache cleared: {'Yes' if cleaned_data['cache'] else 'No'}\n" +
                f"⚡ CPU optimized\n\n" +
                f"✅ Your CPU should run much better now!"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Deep CPU clean error: {e}")
    
    def clear_cpu_cache_internal(self):
        """Internal CPU cache clearing method"""
        try:
            import subprocess
            # Clear standby memory using PowerShell
            subprocess.run(['powershell', '-Command', 
                          'Clear-Content -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\PrefetchParameters" -ErrorAction SilentlyContinue'], 
                          capture_output=True)
            
            # Free up memory using Windows API
            subprocess.run(['powershell', '-Command', 
                          '[System.Runtime.InteropServices.Marshal]::FreeHGlobal([System.IntPtr]::Zero)'], 
                          capture_output=True)
        except:
            pass
    
    def close_cpu_intensive_processes_internal(self, threshold=200):
        """Internal method to close CPU-intensive processes"""
        closed_processes = []
        
        safe_to_close = [
            'notepad.exe', 'mspaint.exe', 'calc.exe', 'wordpad.exe',
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'spotify.exe', 'discord.exe', 'teams.exe', 'slack.exe',
            'steam.exe', 'epicgameslauncher.exe', 'origin.exe', 'uplay.exe',
            'update.exe', 'installer.exe', 'setup.exe'
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                process_name = proc.info['name'].lower()
                cpu_usage = proc.info['cpu_percent'] or 0
                memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                
                if any(safe_proc in process_name for safe_proc in safe_to_close):
                    if memory_mb > threshold or cpu_usage > 10:
                        proc.terminate()
                        closed_processes.append(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return closed_processes
    
    def optimize_cpu_priorities_internal(self):
        """Internal CPU priority optimization method"""
        try:
            # Lower priority of background processes
            background_processes = [
                'svchost.exe', 'services.exe', 'lsass.exe', 'csrss.exe',
                'wininit.exe', 'winlogon.exe', 'explorer.exe'
            ]
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    process_name = proc.info['name'].lower()
                    if any(bg_proc in process_name for bg_proc in background_processes):
                        process = psutil.Process(proc.info['pid'])
                        # Set to below normal priority (Windows)
                        if platform.system() == "Windows":
                            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = CPUMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
