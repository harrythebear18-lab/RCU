#!/usr/bin/env python3
"""
Simple Working Launcher
Clean launcher with working launch buttons
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
from pathlib import Path
import psutil
import threading
import time
import ctypes
from ctypes import wintypes

class SimpleLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homelab Launcher")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00d4ff',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'accent': '#0078ff'
        }
        
        # Base path for all tools - use current directory
        self.base_path = Path(__file__).parent
        
        # Initialize DXGI for GPU monitoring
        self.init_dxgi_gpu_monitoring()
        
        # Working tools organized by category
        self.tools = {
            "Monitoring": {
                "CPU Monitor": {
                    "path": str(self.base_path / "Cpu Monitor/cpu_monitor.py"),
                    "icon": "💻",
                    "description": "Monitor CPU usage and performance"
                },
                "GPU Monitor": {
                    "path": str(self.base_path / "Gpu Monitor/gpu_monitor.py"), 
                    "icon": "🎮",
                    "description": "Monitor GPU usage and temperature"
                },
                "Network Monitor": {
                    "path": "Network Monitor/network_monitor.py",
                    "icon": "🌐",
                    "description": "Monitor network activity and bandwidth"
                },
                "Storage Monitor": {
                    "path": "Storage Monitor/storage_monitor.py",
                    "icon": "💾",
                    "description": "Monitor disk space and I/O"
                },
                "Memory Monitor": {
                    "path": "Memory Monitor/ram_monitor_gui.py",
                    "icon": "🧠",
                    "description": "Monitor RAM usage and memory"
                }
            },
            "Services": {
                "Web Dashboard": {
                    "path": "Core Services/web_dashboard.py",
                    "icon": "📊",
                    "description": "Web-based monitoring dashboard"
                },
                "VPN Gateway": {
                    "path": "VPN Gateway/vpn_gateway.py",
                    "icon": "🔐",
                    "description": "VPN connection management"
                },
                "Backup Manager": {
                    "path": "Core Services/backup_manager.py",
                    "icon": "💿",
                    "description": "System backup management"
                },
                "Power Manager": {
                    "path": "Power Manager/power_manager.py",
                    "icon": "⚡",
                    "description": "Power management utilities"
                }
            },
            "Advanced": {
                "RDMA Desktop": {
                    "path": "RDMA Desktop App/rdma_desktop_app.py",
                    "icon": "🔌",
                    "description": "RDMA desktop application"
                },
                "System Audit": {
                    "path": "comprehensive_chunked_audit.py",
                    "icon": "🔍",
                    "description": "Comprehensive system audit"
                }
            },
            "Sharing": {  # Separate category for sharing tools
                "RAM Sharing": {
                    "path": "RAM_Sharing_GUI.py",
                    "icon": "🔄",
                    "description": "RAM sharing interface"
                },
                "RAM Sharing Simple": {
                    "path": "RAM_Sharing_Simple_GUI.py",
                    "icon": "🔄",
                    "description": "Simple RAM sharing interface"
                }
            },
            "System": {  # System tools
                "System Dashboard": {
                    "path": "homelab_dashboard.py",
                    "icon": "🏠",
                    "description": "Main system dashboard"
                },
                "System Launcher": {
                    "path": "homelab_launcher.py",
                    "icon": "🚀",
                    "description": "Main system launcher"
                }
            },
            "Utilities": {
                "Auto Connect": {
                    "path": "Auto_Connect_Launcher.bat",
                    "icon": "🔗",
                    "description": "Auto connection launcher"
                },
                "Windows Fix": {
                    "path": "Fix_Windows_Compatibility.bat",
                    "icon": "🔧",
                    "description": "Windows compatibility fixes"
                },
                "Install WireGuard": {
                    "path": "install_wireguard.bat",
                    "icon": "🛡️",
                    "description": "Install WireGuard VPN"
                }
            }
        }
        
        self.running_tools = {}
        self.create_widgets()
        self.start_live_updates()
        
    def create_widgets(self):
        """Create launcher widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🚀 Homelab Launcher", 
                              font=('Arial', 28, 'bold'), 
                              fg=self.colors['text'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT, pady=20)
        
        # Live stats
        self.stats_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        self.stats_frame.pack(side=tk.RIGHT, pady=20)
        
        self.cpu_label = tk.Label(self.stats_frame, text="CPU: 0%", 
                                  font=('Arial', 12), 
                                  fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.cpu_label.pack(side=tk.LEFT, padx=10)
        
        self.ram_label = tk.Label(self.stats_frame, text="RAM: 0%", 
                                  font=('Arial', 12), 
                                  fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.ram_label.pack(side=tk.LEFT, padx=10)
        
        self.gpu_label = tk.Label(self.stats_frame, text="GPU: 0%", 
                                  font=('Arial', 12), 
                                  fg=self.colors['warning'], bg=self.colors['bg'])
        self.gpu_label.pack(side=tk.LEFT, padx=10)
        
        self.running_label = tk.Label(self.stats_frame, text="Running: 0", 
                                     font=('Arial', 12), 
                                     fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.running_label.pack(side=tk.LEFT, padx=10)
        
        # Create notebook for categories
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', background=self.colors['card'], 
                      foreground=self.colors['text'], padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', self.colors['primary'])])
        
        # Create category tabs
        for category_name, tools in self.tools.items():
            self.create_category_tab(category_name, tools)
        
        # Status bar
        self.create_status_bar()
        
        # Start background process monitoring
        self.start_process_monitoring()
        
    def init_dxgi_gpu_monitoring(self):
        """Initialize DirectX 11 DXGI for GPU monitoring"""
        try:
            # Define DXGI structures and constants
            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", wintypes.ULONG),
                    ("Data2", wintypes.USHORT),
                    ("Data3", wintypes.USHORT),
                    ("Data4", wintypes.BYTE * 8)
                ]
                
                @classmethod
                def from_string(cls, guid_string):
                    guid = cls()
                    import uuid
                    uuid_obj = uuid.UUID(guid_string)
                    guid.Data1 = uuid_obj.time_low
                    guid.Data2 = uuid_obj.time_mid
                    guid.Data3 = uuid_obj.time_hi_version
                    for i, byte in enumerate(uuid_obj.bytes[8:]):
                        guid.Data4[i] = byte
                    return guid
            
            class DXGI_QUERY_VIDEO_MEMORY_INFO(ctypes.Structure):
                _fields_ = [
                    ("Version", wintypes.ULONG),
                    ("ResizeBudget", ctypes.c_uint64),
                    ("CurrentUsage", ctypes.c_uint64),
                    ("AvailableForReservation", ctypes.c_uint64),
                    ("CurrentReservation", ctypes.c_uint64)
                ]
            
            # Simple approach - use working Python GPU libraries
            self.dxgi_available = False  # Mark DirectX as unavailable
            print("Using Python GPU libraries instead of DirectX for reliability")
                
        except Exception as e:
            self.dxgi_available = False
            print(f"DXGI GPU monitoring initialization failed: {e}")
    
    def get_dxgi_gpu_usage(self):
        """Get GPU usage using DirectX 11 DXGI"""
        if not hasattr(self, 'dxgi_available') or not self.dxgi_available:
            return None
            
        try:
            # Enumerate adapters
            adapter = ctypes.c_void_p()
            hr = self.dxgi_factory.EnumAdapters1(0, ctypes.byref(adapter))
            
            if hr != 0:  # Not S_OK
                return None
            
            # Get adapter3 interface for memory queries
            adapter3 = ctypes.c_void_p()
            hr = adapter.QueryInterface(ctypes.GUID.from_string("655295f2-3b1a-44f4-b238-5a4fec3e9200"), ctypes.byref(adapter3))
            
            if hr != 0:  # Not S_OK
                return None
            
            # Query video memory info
            memory_info = DXGI_QUERY_VIDEO_MEMORY_INFO()
            hr = adapter3.QueryVideoMemoryInfo(0, 0, ctypes.byref(memory_info))
            
            if hr == 0:  # S_OK
                # Calculate usage percentage
                if memory_info.ResizeBudget > 0:
                    usage_percent = (memory_info.CurrentUsage / memory_info.ResizeBudget) * 100
                    return min(100.0, max(0.0, usage_percent))
            
            return None
            
        except Exception as e:
            print(f"DXGI GPU query error: {e}")
            return None
        
    def create_category_tab(self, category_name, tools):
        """Create a tab for a tool category"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab_frame, text=category_name)
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create tool grid
        self.create_tool_grid(scrollable_frame, tools)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def create_tool_grid(self, parent, tools):
        """Create grid of tools"""
        row, col = 0, 0
        max_cols = 3
        
        for tool_name, tool_info in tools.items():
            self.create_tool_card(parent, tool_name, tool_info, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(max_cols):
            parent.grid_columnconfigure(i, weight=1)
        for i in range(row + 1):
            parent.grid_rowconfigure(i, weight=1)
    
    def create_tool_card(self, parent, tool_name, tool_info, row, col):
        """Create tool card with working button"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        card.configure(highlightbackground=self.colors['primary'], highlightthickness=2)
        
        # Tool icon
        icon_label = tk.Label(card, text=tool_info['icon'], 
                            font=('Arial', 36), 
                            fg=self.colors['primary'], bg=self.colors['card'])
        icon_label.pack(pady=(20, 10))
        
        # Tool name
        name_label = tk.Label(card, text=tool_name, 
                             font=('Arial', 14, 'bold'), 
                             fg=self.colors['text'], bg=self.colors['card'])
        name_label.pack(pady=(0, 5))
        
        # Description
        desc_label = tk.Label(card, text=tool_info['description'], 
                            font=('Arial', 10), 
                            fg=self.colors['text_secondary'], bg=self.colors['card'],
                            wraplength=200, justify='center')
        desc_label.pack(pady=(0, 20))
        
        # Launch button - WORKING
        launch_btn = tk.Button(card, text="🚀 Launch", 
                             command=lambda tn=tool_name, ti=tool_info: self.toggle_tool(tn, ti),
                             bg=self.colors['primary'], fg='white', 
                             font=('Arial', 12, 'bold'), relief='raised', bd=2,
                             cursor='hand2', width=12, height=1)
        launch_btn.pack(pady=(0, 20))
        
        # Status label
        status_label = tk.Label(card, text="● Ready", 
                               font=('Arial', 10), 
                               fg=self.colors['success'], bg=self.colors['card'])
        status_label.pack(pady=(0, 15))
        
        # Store references
        tool_info['button'] = launch_btn
        tool_info['status_label'] = status_label
        
    def launch_tool(self, tool_name, tool_info):
        """Launch tool with proper path resolution"""
        try:
            # Get base path (current directory)
            base_path = Path(__file__).parent
            
            # Convert forward slashes to proper path separators
            tool_path_str = tool_info['path'].replace('/', os.sep)
            tool_path = base_path / tool_path_str
            
            # Debug: Show what we're trying to launch
            print(f"Attempting to launch: {tool_name}")
            print(f"Base path: {base_path}")
            print(f"Tool path: {tool_path}")
            print(f"Tool exists: {tool_path.exists()}")
            
            # Check if file exists
            if not tool_path.exists():
                # Try to find the file by searching the directory
                filename = Path(tool_path_str).name
                found_path = None
                
                for root, dirs, files in os.walk(base_path):
                    if filename in files:
                        found_path = Path(root) / filename
                        print(f"Found file at: {found_path}")
                        break
                
                if found_path:
                    tool_path = found_path
                else:
                    messagebox.showerror("Tool Not Found", f"Tool not found: {filename}\nSearched in: {base_path}")
                    return
            
            # Check if already running
            if tool_name in self.running_tools:
                messagebox.showinfo("Already Running", f"{tool_name} is already running!")
                return
            
            # Set working directory
            working_dir = tool_path.parent if tool_path.parent.exists() else base_path
            
            # Launch based on file type
            if tool_path.suffix == '.py':
                # Python script - use sys.executable for proper Python path
                process = subprocess.Popen([sys.executable, str(tool_path)], 
                                         cwd=str(working_dir),
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif tool_path.suffix == '.bat':
                # Batch file
                process = subprocess.Popen([str(tool_path)], 
                                         cwd=str(working_dir),
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Other executable
                process = subprocess.Popen([str(tool_path)], 
                                         cwd=str(working_dir))
            
            # Update status
            tool_info['status_label'].config(text="● Running", fg=self.colors['success'])
            tool_info['button'].config(text="⏹️ Stop", bg=self.colors['danger'])
            self.running_tools[tool_name] = process
            
            messagebox.showinfo("Success", f"{tool_name} launched successfully!")
            
        except Exception as e:
            print(f"Error launching {tool_name}: {e}")
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {str(e)}")
    
    def toggle_tool(self, tool_name, tool_info):
        """Toggle tool launch/stop"""
        try:
            if tool_name in self.running_tools:
                # Tool is running, stop it
                self.stop_tool(tool_name, tool_info)
            else:
                # Tool is not running, launch it
                self.launch_tool(tool_name, tool_info)
        except Exception as e:
            print(f"Error toggling {tool_name}: {e}")
            messagebox.showerror("Error", f"Failed to toggle {tool_name}: {str(e)}")
    
    def stop_tool(self, tool_name, tool_info):
        """Stop a running tool"""
        try:
            if tool_name in self.running_tools:
                process = self.running_tools[tool_name]
                
                # Try to terminate gracefully
                process.terminate()
                
                # Wait a moment for graceful termination
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination fails
                    process.kill()
                    process.wait()
                
                del self.running_tools[tool_name]
                
                # Update status
                tool_info['status_label'].config(text="● Ready", fg=self.colors['success'])
                tool_info['button'].config(text="🚀 Launch", bg=self.colors['primary'])
                
                messagebox.showinfo("Success", f"{tool_name} stopped successfully!")
            else:
                messagebox.showinfo("Not Running", f"{tool_name} is not running!")
            
        except Exception as e:
            print(f"Error stopping {tool_name}: {e}")
            messagebox.showerror("Error", f"Failed to stop {tool_name}: {str(e)}")
    
    def check_running_processes(self):
        """Check if running processes are still alive and update status"""
        try:
            tools_to_remove = []
            
            for tool_name, process in self.running_tools.items():
                # Check if process is still running
                if process.poll() is not None:
                    # Process has ended
                    tools_to_remove.append(tool_name)
                    
                    # Update UI if tool info exists
                    for category_tools in self.tools.values():
                        if tool_name in category_tools:
                            tool_info = category_tools[tool_name]
                            if 'status_label' in tool_info and tool_info['status_label']:
                                tool_info['status_label'].config(text="● Ready", fg=self.colors['success'])
                            if 'button' in tool_info and tool_info['button']:
                                tool_info['button'].config(text="🚀 Launch", bg=self.colors['primary'])
                            break
            
            # Remove ended processes from tracking
            for tool_name in tools_to_remove:
                del self.running_tools[tool_name]
                
        except Exception as e:
            print(f"Error checking processes: {e}")
    
    def start_process_monitoring(self):
        """Start background process monitoring"""
        def monitor():
            while True:
                try:
                    self.check_running_processes()
                    time.sleep(2)  # Check every 2 seconds
                except Exception as e:
                    print(f"Process monitoring error: {e}")
                    time.sleep(5)  # Wait longer if error occurs
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=(0, 20))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    font=('Arial', 11), 
                                    fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.tools_count_label = tk.Label(status_frame, text=f"Tools: {sum(len(tools) for tools in self.tools.values())}", 
                                         font=('Arial', 11), 
                                         fg=self.colors['info'], bg=self.colors['card'])
        self.tools_count_label.pack(side=tk.RIGHT, padx=15, pady=10)
    
    def start_live_updates(self):
        """Start live updates"""
        def update_stats():
            try:
                # Update CPU
                cpu_percent = psutil.cpu_percent()
                self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
                
                # Update RAM
                memory = psutil.virtual_memory()
                self.ram_label.config(text=f"RAM: {memory.percent:.1f}%")
                
                # Update GPU using single backend service
                try:
                    from gpu_monitoring_backend import get_gpu_usage
                    gpu_usage = get_gpu_usage()
                    if gpu_usage is not None:
                        self.gpu_label.config(text=f"GPU: {gpu_usage:.1f}%")
                    else:
                        self.gpu_label.config(text="GPU: N/A")
                except Exception as e:
                    print(f"GPU monitoring error: {e}")
                    self.gpu_label.config(text="GPU: N/A")
                
                # Update running count
                self.running_label.config(text=f"Running: {len(self.running_tools)}")
                
                # Update status
                self.status_label.config(text=f"System running - {len(self.running_tools)} tools active")
                
            except:
                pass
            
            # Schedule next update
            self.root.after(2000, update_stats)
        
        update_stats()
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

if __name__ == "__main__":
    launcher = SimpleLauncher()
    launcher.run()
