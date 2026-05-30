#!/usr/bin/env python3
"""
Windows 10 Homelab Server Launcher
Simple launcher to start the Windows 10 homelab server and manage connections.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import subprocess
import sys
import os
from datetime import datetime
import socket

class Win10ServerLauncher:
    """Windows 10 Homelab Server Launcher GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ Windows 10 Homelab Server Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040'
        }
        
        # Server state
        self.server_process = None
        self.server_running = False
        self.server_thread = None
        self.local_ip = self.get_local_ip()
        
        # Create UI
        self.create_ui()
        
        # Check system requirements
        self.check_system_requirements()
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def create_ui(self):
        """Create the launcher UI"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_container, text="🖥️ Windows 10 Homelab Server",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=(0, 20))
        
        # Status card
        status_card = tk.Frame(main_container, bg=self.colors['card'])
        status_card.pack(fill=tk.X, pady=(0, 20))
        
        # Server status
        status_frame = tk.Frame(status_card, bg=self.colors['card'])
        status_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.status_label = tk.Label(status_frame, text="🔴 Server: Offline",
                                   font=('Segoe UI', 14, 'bold'),
                                   fg=self.colors['danger'], bg=self.colors['card'])
        self.status_label.pack(anchor=tk.W)
        
        self.ip_label = tk.Label(status_frame, text=f"🌐 Local IP: {self.local_ip}",
                               font=('Segoe UI', 10),
                               fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.ip_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.url_label = tk.Label(status_frame, text=f"🔗 Server URL: http://{self.local_ip}:8080",
                                font=('Segoe UI', 10),
                                fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.url_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Control buttons
        control_frame = tk.Frame(status_card, bg=self.colors['card'])
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start Server",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['success'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop Server",
                                 font=('Segoe UI', 12, 'bold'),
                                 bg=self.colors['danger'], fg=self.colors['bg'],
                                 relief='flat', cursor='hand2',
                                 command=self.stop_server,
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.test_btn = tk.Button(control_frame, text="🔍 Test Connection",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['primary'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=10)
        
        # Info card
        info_card = tk.Frame(main_container, bg=self.colors['card'])
        info_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        info_frame = tk.Frame(info_card, bg=self.colors['card'])
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(info_frame, text="📋 System Information",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # System info display
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10, width=70,
                                                  bg=self.colors['bg'], fg=self.colors['text'],
                                                  font=('Consolas', 9), relief='flat')
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Instructions
        instructions_frame = tk.Frame(main_container, bg=self.colors['card'])
        instructions_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(instructions_frame, text="📖 Instructions",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        instructions_text = """
1. Click "Start Server" to begin hosting resources
2. Windows 11 clients can connect to: http://{}:8080
3. Server will automatically detect and host available resources
4. Monitor server status in the log above
5. Use "Test Connection" to verify server is responding
        """.format(self.local_ip).strip()
        
        tk.Label(instructions_frame, text=instructions_text,
                 font=('Segoe UI', 9),
                 fg=self.colors['text_secondary'], bg=self.colors['card']).pack(anchor=tk.W, padx=20, pady=(0, 10))
        
        # Status bar
        self.status_bar = tk.Label(main_container, text="Ready to start Windows 10 Homelab Server",
                                  font=('Segoe UI', 9),
                                  fg=self.colors['text_secondary'], bg=self.colors['bg'])
        self.status_bar.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def check_system_requirements(self):
        """Check Windows 10 system requirements"""
        try:
            import psutil
            import platform
            
            # System info
            system_info = f"""
=== Windows 10 System Check ===
Platform: {platform.platform()}
OS Version: {platform.version()}
Architecture: {platform.architecture()[0]}
CPU Cores: {psutil.cpu_count()}
Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB
Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB
Local IP: {self.local_ip}

=== Compatibility Check ===
Windows 10 Compatible: {'✅' if 'Windows-10' in platform.platform() else '⚠️'}
Python Version: {platform.python_version()}
Network Access: {'✅' if self.local_ip != '127.0.0.1' else '⚠️'}
"""
            
            # Check for required modules
            required_modules = ['psutil', 'requests', 'sqlite3']
            missing_modules = []
            
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)
            
            if missing_modules:
                system_info += f"\n❌ Missing modules: {', '.join(missing_modules)}"
                system_info += "\nInstall with: pip install " + " ".join(missing_modules)
            else:
                system_info += "\n✅ All required modules installed"
            
            # Check available resources
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                system_info += f"\n\n=== Available Resources ==="
                system_info += f"\nGPUs Detected: {len(gpus)}"
                for gpu in gpus:
                    system_info += f"\n  - {gpu.name}: {gpu.memoryTotal/1024:.1f}GB"
            except:
                system_info += "\n\n⚠️ GPU detection not available (GPUtil not installed)"
            
            # Disk space
            disk_partitions = psutil.disk_partitions()
            system_info += f"\n\n=== Storage ==="
            for partition in disk_partitions[:3]:  # Show first 3 partitions
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    free_gb = usage.free / (1024**3)
                    system_info += f"\n{partition.device}: {free_gb:.1f}GB free"
                except:
                    continue
            
            self.info_text.insert(tk.END, system_info)
            
            # Show warning if requirements not met
            if missing_modules:
                messagebox.showwarning("Missing Dependencies", 
                                      f"Please install missing modules:\n{', '.join(missing_modules)}")
            
        except Exception as e:
            self.info_text.insert(tk.END, f"Error checking system requirements: {e}")
    
    def start_server(self):
        """Start the Windows 10 homelab server"""
        if self.server_running:
            messagebox.showwarning("Server Running", "Server is already running!")
            return
        
        try:
            # Update UI
            self.status_label.config(text="🟡 Server: Starting...", fg=self.colors['warning'])
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_bar.config(text="Starting Windows 10 Homelab Server...")
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # Wait a moment for server to start
            self.root.after(2000, self._check_server_status)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
            self._reset_ui_state()
    
    def _run_server(self):
        """Run the server process"""
        try:
            # Import and run the server
            import win10_homelab_server
            
            # Add log output to GUI
            original_log = win10_homelab_server.Windows10HomelabServer.logger.info
            def gui_log(message):
                original_log(message)
                self.root.after(0, lambda: self._add_log_message(message))
            
            win10_homelab_server.Windows10HomelabServer.logger.info = gui_log
            
            # Start server
            self.server_running = True
            server = win10_homelab_server.Windows10HomelabServer()
            server.run()
            
        except Exception as e:
            self.root.after(0, lambda: self._add_log_message(f"Server error: {e}"))
            self.server_running = False
    
    def _check_server_status(self):
        """Check if server started successfully"""
        if self.server_running:
            self.status_label.config(text="🟢 Server: Online", fg=self.colors['success'])
            self.status_bar.config(text=f"Windows 10 Homelab Server running on http://{self.local_ip}:8080")
            self._add_log_message(f"✅ Server started successfully on http://{self.local_ip}:8080")
            self._add_log_message("🚀 Ready to host resources for Windows 11 clients")
        else:
            self.status_label.config(text="🔴 Server: Failed", fg=self.colors['danger'])
            self.status_bar.config(text="Failed to start server")
            self._reset_ui_state()
    
    def stop_server(self):
        """Stop the Windows 10 homelab server"""
        if not self.server_running:
            messagebox.showwarning("Server Not Running", "Server is not running!")
            return
        
        try:
            # Update UI
            self.status_label.config(text="🟡 Server: Stopping...", fg=self.colors['warning'])
            self.status_bar.config(text="Stopping Windows 10 Homelab Server...")
            
            # Stop server
            self.server_running = False
            
            # If server was started as subprocess, terminate it
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            
            # Reset UI
            self._reset_ui_state()
            self._add_log_message("🛑 Server stopped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {e}")
    
    def test_connection(self):
        """Test server connection"""
        if not self.server_running:
            messagebox.showwarning("Server Not Running", "Please start the server first!")
            return
        
        try:
            import requests
            
            self.status_bar.config(text="Testing server connection...")
            
            # Test server status endpoint
            response = requests.get(f"http://{self.local_ip}:8080/api/v1/server/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Connection Test Successful", 
                                  f"✅ Server is responding!\n\n"
                                  f"Server: {data.get('server_name', 'Unknown')}\n"
                                  f"Resources: {data.get('resources', 0)}\n"
                                  f"Clients: {data.get('clients', 0)}")
                self._add_log_message("✅ Connection test successful")
            else:
                messagebox.showerror("Connection Test Failed", 
                                  f"Server returned status code: {response.status_code}")
                self._add_log_message(f"❌ Connection test failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Test Failed", f"Failed to connect to server: {e}")
            self._add_log_message(f"❌ Connection test failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test error: {e}")
            self._add_log_message(f"❌ Connection test error: {e}")
    
    def _add_log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.info_text.insert(tk.END, log_entry)
        self.info_text.see(tk.END)
    
    def _reset_ui_state(self):
        """Reset UI to initial state"""
        self.status_label.config(text="🔴 Server: Offline", fg=self.colors['danger'])
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="Ready to start Windows 10 Homelab Server")

if __name__ == '__main__':
    # Create launcher window
    root = tk.Tk()
    launcher = Win10ServerLauncher(root)
    
    # Handle window closing
    def on_closing():
        if launcher.server_running:
            if messagebox.askyesno("Server Running", "Server is still running. Stop it and exit?"):
                launcher.stop_server()
                root.after(1000, root.destroy)  # Wait a moment for cleanup
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the launcher
    root.mainloop()
