#!/usr/bin/env python3
"""
RDMA Launcher - High-Performance Device Interconnects
Launches RDMA tools for ultra low-latency device communication
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
from pathlib import Path
import threading
import time

class RDMA_Launcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ RDMA Launcher - Ultra Low Latency Interconnects")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0f0f0f')
        
        # Colors matching RAM cleanup theme
        self.colors = {
            'bg': '#0f0f0f',
            'card': '#1e1e1e',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#aaaaaa'
        }
        
        # RDMA directory path
        self.rdma_path = r'C:\Users\htsou\Desktop\RDMA'
        
        # Running processes
        self.running_processes = {}
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="⚡ RDMA Launcher", 
                              font=('Segoe UI', 24, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Ultra Low Latency Device Interconnects - TESTED & VERIFIED", 
                                 font=('Segoe UI', 12), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(pady=(0, 10))
        
        # Status display
        self.status_label = tk.Label(header_frame, text="● Ready", 
                                    font=('Segoe UI', 10, 'bold'), 
                                    fg=self.colors['success'], bg=self.colors['bg'])
        self.status_label.pack(pady=(5, 10))
        
        # Core RDMA Tools section
        core_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        core_frame.pack(fill=tk.X, pady=(0, 20))
        
        core_title = tk.Label(core_frame, text="🚀 Core RDMA Tools", 
                             font=('Segoe UI', 14, 'bold'), 
                             fg=self.colors['primary'], bg=self.colors['card'])
        core_title.pack(pady=(15, 10))
        
        # RDMA Desktop App
        rdma_desktop_btn = tk.Button(core_frame, 
                                     text="🖥️ RDMA Desktop App\nComprehensive desktop GUI with connectivity and monitoring",
                                     font=('Segoe UI', 11), 
                                     bg=self.colors['primary'], fg=self.colors['bg'],
                                     relief='flat', bd=0, cursor='hand2',
                                     padx=20, pady=15,
                                     command=self.launch_rdma_desktop)
        rdma_desktop_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # RDMA REST API
        rdma_api_btn = tk.Button(core_frame, 
                                text="🌐 RDMA REST API\nREST API for RDMA operations",
                                font=('Segoe UI', 11), 
                                bg=self.colors['primary'], fg=self.colors['bg'],
                                relief='flat', bd=0, cursor='hand2',
                                padx=20, pady=15,
                                command=self.launch_rdma_api)
        rdma_api_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Performance Profiler
        perf_profiler_btn = tk.Button(core_frame, 
                                     text="📊 Performance Profiler\nPerformance profiling and benchmarking",
                                     font=('Segoe UI', 11), 
                                     bg=self.colors['primary'], fg=self.colors['bg'],
                                     relief='flat', bd=0, cursor='hand2',
                                     padx=20, pady=15,
                                     command=self.launch_performance_profiler)
        perf_profiler_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Ultra Latency Benchmark
        latency_benchmark_btn = tk.Button(core_frame, 
                                        text="⚡ Ultra Latency Benchmark\nTESTED & VERIFIED ultra low-latency benchmarking",
                                        font=('Segoe UI', 11), 
                                        bg=self.colors['success'], fg=self.colors['bg'],
                                        relief='flat', bd=0, cursor='hand2',
                                        padx=20, pady=15,
                                        command=self.launch_latency_benchmark)
        latency_benchmark_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Advanced RDMA Tools section
        advanced_frame = tk.Frame(main_container, bg=self.colors['card'], relief='solid', bd=1)
        advanced_frame.pack(fill=tk.X, pady=(0, 20))
        
        advanced_title = tk.Label(advanced_frame, text="🔧 Advanced RDMA Tools", 
                                 font=('Segoe UI', 14, 'bold'), 
                                 fg=self.colors['primary'], bg=self.colors['card'])
        advanced_title.pack(pady=(15, 10))
        
        # Zero-Copy Operations
        zero_copy_btn = tk.Button(advanced_frame, 
                                  text="💾 Zero-Copy Operations\nTESTED & VERIFIED zero-copy memory operations",
                                  font=('Segoe UI', 11), 
                                  bg=self.colors['primary'], fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  padx=20, pady=15,
                                  command=self.launch_zero_copy)
        zero_copy_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # UDP Memory Bridge
        udp_bridge_btn = tk.Button(advanced_frame, 
                                  text="🌉 UDP Memory Bridge\nTESTED & VERIFIED UDP-based memory bridge",
                                  font=('Segoe UI', 11), 
                                  bg=self.colors['primary'], fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  padx=20, pady=15,
                                  command=self.launch_udp_bridge)
        udp_bridge_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # PCIe Tunneling
        pcie_tunnel_btn = tk.Button(advanced_frame, 
                                   text="🔌 PCIe Tunneling\nTESTED & VERIFIED PCIe tunneling for device interconnects",
                                   font=('Segoe UI', 11), 
                                   bg=self.colors['primary'], fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   padx=20, pady=15,
                                   command=self.launch_pcie_tunnel)
        pcie_tunnel_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Network Bypass
        network_bypass_btn = tk.Button(advanced_frame, 
                                      text="🚀 Network Bypass\nTESTED & VERIFIED network layer bypass",
                                      font=('Segoe UI', 11), 
                                      bg=self.colors['primary'], fg=self.colors['bg'],
                                      relief='flat', bd=0, cursor='hand2',
                                      padx=20, pady=15,
                                      command=self.launch_network_bypass)
        network_bypass_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Monitoring System
        monitoring_btn = tk.Button(advanced_frame, 
                                  text="📈 Monitoring System\nSystem monitoring and health checks",
                                  font=('Segoe UI', 11), 
                                  bg=self.colors['primary'], fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  padx=20, pady=15,
                                  command=self.launch_monitoring)
        monitoring_btn.pack(fill=tk.X, padx=20, pady=10)
        
        # Close button
        close_btn = tk.Button(main_container, 
                             text="❌ Close Launcher", 
                             font=('Segoe UI', 11, 'bold'), 
                             bg=self.colors['danger'], fg=self.colors['bg'],
                             relief='flat', bd=0, cursor='hand2',
                             padx=20, pady=10,
                             command=self.close_launcher)
        close_btn.pack(pady=20)
    
    def launch_rdma_desktop(self):
        """Launch RDMA Desktop App"""
        script_path = os.path.join(self.rdma_path, 'rdma_desktop_app.py')
        self.launch_script(script_path, "RDMA Desktop App")
    
    def launch_rdma_api(self):
        """Launch RDMA REST API"""
        script_path = os.path.join(self.rdma_path, 'rdma_rest_api.py')
        self.launch_script(script_path, "RDMA REST API")
    
    def launch_performance_profiler(self):
        """Launch Performance Profiler"""
        script_path = os.path.join(self.rdma_path, 'performance_profiler.py')
        self.launch_script(script_path, "Performance Profiler")
    
    def launch_latency_benchmark(self):
        """Launch Ultra Latency Benchmark"""
        script_path = os.path.join(self.rdma_path, 'ultra_latency_benchmark.py')
        self.launch_script(script_path, "Ultra Latency Benchmark")
    
    def launch_zero_copy(self):
        """Launch Zero-Copy Operations"""
        script_path = os.path.join(self.rdma_path, 'zero_copy_rdmda.py')
        self.launch_script(script_path, "Zero-Copy Operations")
    
    def launch_udp_bridge(self):
        """Launch UDP Memory Bridge"""
        script_path = os.path.join(self.rdma_path, 'udp_memory_bridge.py')
        self.launch_script(script_path, "UDP Memory Bridge")
    
    def launch_pcie_tunnel(self):
        """Launch PCIe Tunneling"""
        script_path = os.path.join(self.rdma_path, 'virtual_pcie_tunnel.py')
        self.launch_script(script_path, "PCIe Tunneling")
    
    def launch_network_bypass(self):
        """Launch Network Bypass"""
        script_path = os.path.join(self.rdma_path, 'raw_network_bypass.py')
        self.launch_script(script_path, "Network Bypass")
    
    def launch_monitoring(self):
        """Launch Monitoring System"""
        script_path = os.path.join(self.rdma_path, 'monitoring_system.py')
        self.launch_script(script_path, "Monitoring System")
    
    def launch_script(self, script_path, tool_name):
        """Launch a script in a new process"""
        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Script not found:\n{script_path}")
            return
        
        try:
            self.status_label.config(text=f"● Starting {tool_name}...", fg=self.colors['warning'])
            self.root.update()
            
            # Launch in new process
            process = subprocess.Popen([sys.executable, script_path], 
                                      cwd=self.rdma_path)
            self.running_processes[tool_name] = process
            
            self.status_label.config(text=f"● {tool_name} launched", fg=self.colors['success'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}:\n{e}")
            self.status_label.config(text="● Launch failed", fg=self.colors['danger'])
    
    def close_launcher(self):
        """Close launcher and cleanup"""
        # Terminate running processes
        for tool_name, process in self.running_processes.items():
            try:
                process.terminate()
            except:
                pass
        
        self.root.destroy()

if __name__ == "__main__":
    launcher = RDMA_Launcher()
    launcher.root.mainloop()
