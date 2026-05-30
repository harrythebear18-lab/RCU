#!/usr/bin/env python3
"""
RAM Monitor GUI - Memory monitoring with mesh integration
Part of Homelab Tools mesh VPN system
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
import threading
import json
from pathlib import Path
import logging
from datetime import datetime

# Add Core Services to path
import sys
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from mesh_app_communication import MeshAppCommunication
    MESH_AVAILABLE = True
except ImportError:
    MESH_AVAILABLE = False

class RAMMonitorGUI:
    """RAM Monitor with GUI and mesh integration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homelab RAM Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0'
        }
        
        # State
        self.monitoring = False
        self.monitor_thread = None
        self.mesh_comm = None
        
        # Setup logging
        self.setup_logging()
        
        # Initialize mesh communication
        self.init_mesh_communication()
        
        # Create GUI
        self.create_widgets()
        
        # Start monitoring
        self.start_monitoring()
    
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/ram_monitor.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('RAMMonitorGUI')
    
    def init_mesh_communication(self):
        """Initialize mesh communication"""
        try:
            if MESH_AVAILABLE:
                self.mesh_comm = MeshAppCommunication()
                self.mesh_comm.start()
                
                # Register with mesh
                self.app_id = self.mesh_comm.register_application(
                    app_name="ram-monitor",
                    app_type="memory",
                    port=8084,
                    endpoints=["/api/memory/status", "/api/memory/share", "/api/memory/alloc"],
                    capabilities=["memory_monitoring", "memory_sharing", "performance_tracking"]
                )
                
                # Register message handlers
                self.mesh_comm.register_message_handler("memory_status_request", self.handle_status_request)
                self.mesh_comm.register_message_handler("memory_share_request", self.handle_share_request)
                
                self.logger.info("Mesh communication initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize mesh communication: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = tk.Label(title_frame, text="🧠 RAM Monitor", 
                               font=('Segoe UI', 24, 'bold'), 
                               bg=self.colors['bg'], fg=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Mesh status
        self.mesh_status_label = tk.Label(title_frame, text="🌐 Mesh: Offline", 
                                         font=('Segoe UI', 12), 
                                         bg=self.colors['bg'], fg=self.colors['text_secondary'])
        self.mesh_status_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Memory info frame
        info_frame = tk.Frame(self.root, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Total memory
        total_frame = tk.Frame(info_frame, bg=self.colors['card'])
        total_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(total_frame, text="Total Memory:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.total_memory_label = tk.Label(total_frame, text="0 GB", font=('Segoe UI', 12),
                                          bg=self.colors['card'], fg=self.colors['primary'])
        self.total_memory_label.pack(side=tk.RIGHT)
        
        # Available memory
        avail_frame = tk.Frame(info_frame, bg=self.colors['card'])
        avail_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(avail_frame, text="Available:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.available_memory_label = tk.Label(avail_frame, text="0 GB", font=('Segoe UI', 12),
                                              bg=self.colors['card'], fg=self.colors['success'])
        self.available_memory_label.pack(side=tk.RIGHT)
        
        # Used memory
        used_frame = tk.Frame(info_frame, bg=self.colors['card'])
        used_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(used_frame, text="Used:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.used_memory_label = tk.Label(used_frame, text="0 GB", font=('Segoe UI', 12),
                                        bg=self.colors['card'], fg=self.colors['warning'])
        self.used_memory_label.pack(side=tk.RIGHT)
        
        # Memory usage bar
        bar_frame = tk.Frame(info_frame, bg=self.colors['card'])
        bar_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(bar_frame, text="Usage:", font=('Segoe UI', 12, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.usage_bar = ttk.Progressbar(bar_frame, length=200, mode='determinate')
        self.usage_bar.pack(side=tk.RIGHT, padx=10)
        
        # Percentage label
        self.percentage_label = tk.Label(bar_frame, text="0%", font=('Segoe UI', 12),
                                        bg=self.colors['card'], fg=self.colors['text'])
        self.percentage_label.pack(side=tk.RIGHT)
        
        # Processes frame
        processes_frame = tk.Frame(self.root, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        processes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(processes_frame, text="Top Memory Processes", font=('Segoe UI', 14, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(padx=20, pady=10)
        
        # Processes list
        self.processes_text = tk.Text(processes_frame, height=15, bg='#1a1a1a', fg=self.colors['text'],
                                     font=('Consolas', 10))
        self.processes_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.share_button = tk.Button(control_frame, text="🔗 Share Memory", 
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['primary'], fg='white',
                                     relief=tk.FLAT, cursor='hand2',
                                     command=self.share_memory)
        self.share_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = tk.Button(control_frame, text="🔄 Refresh", 
                                       font=('Segoe UI', 10, 'bold'),
                                       bg=self.colors['success'], fg='white',
                                       relief=tk.FLAT, cursor='hand2',
                                       command=self.refresh_data)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="⏹️ Stop", 
                                    font=('Segoe UI', 10, 'bold'),
                                    bg=self.colors['danger'], fg='white',
                                    relief=tk.FLAT, cursor='hand2',
                                    command=self.stop_monitoring)
        self.stop_button.pack(side=tk.RIGHT, padx=5)
    
    def start_monitoring(self):
        """Start memory monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Update mesh status
        if self.mesh_comm:
            self.mesh_status_label.config(text="🌐 Mesh: Connected", fg=self.colors['success'])
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_memory_info()
                self.update_processes_list()
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(5)
    
    def update_memory_info(self):
        """Update memory information"""
        try:
            memory = psutil.virtual_memory()
            
            # Convert to GB
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            used_gb = memory.used / (1024**3)
            percentage = memory.percent
            
            # Update labels
            self.root.after(0, lambda: self.total_memory_label.config(text=f"{total_gb:.1f} GB"))
            self.root.after(0, lambda: self.available_memory_label.config(text=f"{available_gb:.1f} GB"))
            self.root.after(0, lambda: self.used_memory_label.config(text=f"{used_gb:.1f} GB"))
            self.root.after(0, lambda: self.percentage_label.config(text=f"{percentage:.1f}%"))
            self.root.after(0, lambda: self.usage_bar.config(value=percentage))
            
            # Update color based on usage
            if percentage > 80:
                color = self.colors['danger']
            elif percentage > 60:
                color = self.colors['warning']
            else:
                color = self.colors['success']
            
            self.root.after(0, lambda: self.percentage_label.config(fg=color))
            
            # Broadcast to mesh if available
            if self.mesh_comm:
                memory_data = {
                    "total_gb": total_gb,
                    "available_gb": available_gb,
                    "used_gb": used_gb,
                    "percentage": percentage,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.mesh_comm.send_message(
                    "ram-monitor",
                    "memory_status_update",
                    memory_data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to update memory info: {e}")
    
    def update_processes_list(self):
        """Update top memory processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    processes.append((proc.info['name'], memory_mb, proc.info['pid']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x[1], reverse=True)
            
            # Update text widget
            self.root.after(0, lambda: self.update_processes_text(processes[:10]))
            
        except Exception as e:
            self.logger.error(f"Failed to update processes: {e}")
    
    def update_processes_text(self, processes):
        """Update processes text widget"""
        try:
            self.processes_text.delete(1.0, tk.END)
            
            for i, (name, memory_mb, pid) in enumerate(processes, 1):
                line = f"{i:2d}. {name:<30} {memory_mb:>8.1f} MB (PID: {pid})\n"
                self.processes_text.insert(tk.END, line)
                
        except Exception as e:
            self.logger.error(f"Failed to update processes text: {e}")
    
    def share_memory(self):
        """Share memory resources via mesh"""
        try:
            if not self.mesh_comm:
                messagebox.showerror("Mesh Error", "Mesh communication not available")
                return
            
            # Get current memory info
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 1.0:
                messagebox.showwarning("Low Memory", f"Only {available_gb:.1f} GB available for sharing")
                return
            
            # Share memory
            share_data = {
                "available_gb": available_gb,
                "shareable_gb": min(available_gb * 0.5, 4.0),  # Share up to 50% or 4GB
                "node": "ram-monitor",
                "timestamp": datetime.now().isoformat()
            }
            
            self.mesh_comm.send_message(
                "ram-monitor",
                "memory_share_offer",
                share_data
            )
            
            messagebox.showinfo("Memory Shared", f"Sharing {share_data['shareable_gb']:.1f} GB of memory")
            
        except Exception as e:
            self.logger.error(f"Failed to share memory: {e}")
            messagebox.showerror("Share Error", f"Failed to share memory: {e}")
    
    def refresh_data(self):
        """Force refresh of data"""
        try:
            self.update_memory_info()
            self.update_processes_list()
            self.logger.info("Data refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh data: {e}")
    
    def handle_status_request(self, message_data):
        """Handle mesh status request"""
        try:
            data = message_data.get('data', {})
            self.logger.info(f"Memory status request from {message_data.get('source_app')}")
            
            # Send current status
            memory = psutil.virtual_memory()
            status_data = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percentage": memory.percent,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.mesh_comm:
                self.mesh_comm.send_message(
                    message_data.get('source_app'),
                    "memory_status_response",
                    status_data
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle status request: {e}")
    
    def handle_share_request(self, message_data):
        """Handle mesh share request"""
        try:
            data = message_data.get('data', {})
            self.logger.info(f"Memory share request from {message_data.get('source_app')}")
            
            # Check if we can share
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            requested_gb = data.get('requested_gb', 0)
            
            if available_gb >= requested_gb:
                response = {
                    "status": "approved",
                    "available_gb": available_gb,
                    "granted_gb": min(requested_gb, available_gb * 0.5)
                }
            else:
                response = {
                    "status": "denied",
                    "available_gb": available_gb,
                    "reason": "Insufficient memory"
                }
            
            if self.mesh_comm:
                self.mesh_comm.send_message(
                    message_data.get('source_app'),
                    "memory_share_response",
                    response
                )
                
        except Exception as e:
            self.logger.error(f"Failed to handle share request: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.mesh_comm:
            self.mesh_comm.stop()
        self.logger.info("RAM monitoring stopped")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Main entry point"""
    app = RAMMonitorGUI()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.root.mainloop()

if __name__ == "__main__":
    main()
