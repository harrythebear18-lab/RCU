#!/usr/bin/env python3
"""
Enhanced Homelab Launcher with Mesh Communication
Fixed tool launching and integrated mesh connectivity
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import json
import threading
import time
from pathlib import Path
from datetime import datetime
import logging

# Add Core Services to path
current_dir = Path(__file__).parent
core_services_dir = current_dir / "Core Services"
if str(core_services_dir) not in sys.path:
    sys.path.insert(0, str(core_services_dir))

try:
    from mesh_app_communication import MeshAppCommunication
    MESH_COMM_AVAILABLE = True
except ImportError:
    MESH_COMM_AVAILABLE = False
    print("Mesh communication not available")

class EnhancedHomelabLauncher:
    """Enhanced launcher with fixed tool launching and mesh connectivity"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Homelab Tools Launcher - Enhanced")
        self.root.geometry("1200x800")
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
        self.running_tools = {}
        self.tool_status = {}
        self.mesh_comm = None
        
        # Setup logging
        self.setup_logging()
        
        # Initialize mesh communication
        self.init_mesh_communication()
        
        # Create GUI
        self.create_widgets()
        
        # Load tools
        self.load_tools()
        
        # Start status monitoring
        self.start_status_monitoring()
    
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/enhanced_launcher.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('EnhancedHomelabLauncher')
    
    def init_mesh_communication(self):
        """Initialize mesh communication"""
        try:
            if MESH_COMM_AVAILABLE:
                self.mesh_comm = MeshAppCommunication()
                self.mesh_comm.start()
                
                # Register launcher as mesh app
                self.launcher_id = self.mesh_comm.register_application(
                    app_name="homelab-launcher",
                    app_type="launcher",
                    port=8090,
                    endpoints=["/api/tools", "/api/launch", "/api/status"],
                    capabilities=["tool_management", "status_monitoring", "mesh_coordination"]
                )
                
                # Register message handlers
                self.mesh_comm.register_message_handler("tool_launch_request", self.handle_mesh_launch_request)
                self.mesh_comm.register_message_handler("tool_status_update", self.handle_mesh_status_update)
                self.mesh_comm.register_message_handler("mesh_tools_sync", self.handle_mesh_tools_sync)
                
                self.logger.info("Mesh communication initialized")
            else:
                self.logger.warning("Mesh communication not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize mesh communication: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(header_frame, text="🚀 Homelab Tools Launcher", 
                               font=('Segoe UI', 24, 'bold'), 
                               bg=self.colors['bg'], fg=self.colors['primary'])
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Mesh status
        self.mesh_status_label = tk.Label(header_frame, text="🌐 Mesh: Offline", 
                                         font=('Segoe UI', 12), 
                                         bg=self.colors['bg'], fg=self.colors['text_secondary'])
        self.mesh_status_label.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create notebook for categories
        self.notebook = ttk.Notebook(main_container, style='Card.TFrame')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tool categories
        self.categories = {
            "Core Services": ["VPN Gateway", "Network Monitor", "Web Dashboard", "System Monitor"],
            "Resource Sharing": ["GPU Monitor", "RAM Monitor", "Storage Monitor", "CPU Monitor"],
            "Development": ["Container Manager", "CI/CD Pipeline", "System Integration Test"],
            "Management": ["Backup System", "Power Management", "Media Server", "IoT Platform"],
            "Advanced": ["RDMA Desktop App", "RDMA Modern App", "RDMA Memory Portal"]
        }
        
        self.tool_widgets = {}
        
        # Create category tabs
        for category, tools in self.categories.items():
            self.create_category_tab(category, tools)
        
        # Status bar
        self.create_status_bar()
    
    def create_category_tab(self, category, tools):
        """Create a category tab with tools"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(tab_frame, text=category)
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Tool grid
        tool_grid = tk.Frame(scrollable_frame, bg=self.colors['card'])
        tool_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create tool cards
        for i, tool_name in enumerate(tools):
            row = i // 3
            col = i % 3
            
            tool_card = self.create_tool_card(tool_grid, tool_name, row, col)
            self.tool_widgets[tool_name] = tool_card
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_tool_card(self, parent, tool_name, row, col):
        """Create a tool card widget"""
        card = tk.Frame(parent, bg=self.colors['card'], relief=tk.RAISED, bd=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Tool icon and name
        icon_frame = tk.Frame(card, bg=self.colors['card'])
        icon_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Tool icon (using emoji for now)
        icon = self.get_tool_icon(tool_name)
        icon_label = tk.Label(icon_frame, text=icon, font=('Segoe UI', 24), 
                            bg=self.colors['card'], fg=self.colors['primary'])
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tool name
        name_label = tk.Label(icon_frame, text=tool_name, font=('Segoe UI', 12, 'bold'),
                             bg=self.colors['card'], fg=self.colors['text'])
        name_label.pack(side=tk.LEFT)
        
        # Status indicator
        status_label = tk.Label(icon_frame, text="● Ready", font=('Segoe UI', 10),
                               bg=self.colors['card'], fg=self.colors['success'])
        status_label.pack(side=tk.RIGHT)
        
        # Description
        desc = self.get_tool_description(tool_name)
        desc_label = tk.Label(card, text=desc, font=('Segoe UI', 9),
                             bg=self.colors['card'], fg=self.colors['text_secondary'],
                             wraplength=250, justify=tk.LEFT)
        desc_label.pack(padx=15, pady=(0, 10))
        
        # Launch button
        launch_button = tk.Button(card, text="🚀 Launch", 
                                font=('Segoe UI', 10, 'bold'),
                                bg=self.colors['primary'], fg='white',
                                relief=tk.FLAT, cursor='hand2')
        launch_button.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Store widget references
        tool_info = {
            'card': card,
            'status_label': status_label,
            'button': launch_button,
            'name': tool_name,
            'path': self.get_tool_path(tool_name),
            'category': self.get_tool_category(tool_name)
        }
        
        # Bind launch event
        launch_button.config(command=lambda: self.launch_tool(tool_name, tool_info))
        
        return tool_info
    
    def get_tool_icon(self, tool_name):
        """Get icon for tool"""
        icons = {
            "VPN Gateway": "🔐",
            "Network Monitor": "🌐",
            "Web Dashboard": "📊",
            "System Monitor": "🖥️",
            "GPU Monitor": "🎮",
            "RAM Monitor": "💾",
            "Storage Monitor": "💿",
            "CPU Monitor": "⚡",
            "Container Manager": "📦",
            "CI/CD Pipeline": "🔄",
            "System Integration Test": "🧪",
            "Backup System": "💾",
            "Power Management": "🔋",
            "Media Server": "🎬",
            "IoT Platform": "🌍",
            "RDMA Desktop App": "🔗",
            "RDMA Modern App": "🚀",
            "RDMA Memory Portal": "🧠"
        }
        return icons.get(tool_name, "🔧")
    
    def get_tool_description(self, tool_name):
        """Get description for tool"""
        descriptions = {
            "VPN Gateway": "Secure mesh VPN management and coordination",
            "Network Monitor": "Real-time network monitoring and analysis",
            "Web Dashboard": "Central web interface for all services",
            "System Monitor": "System-wide performance monitoring",
            "GPU Monitor": "Graphics card monitoring and sharing",
            "RAM Monitor": "Memory usage monitoring and sharing",
            "Storage Monitor": "Disk usage and storage management",
            "CPU Monitor": "Processor monitoring and optimization",
            "Container Manager": "Container orchestration and management",
            "CI/CD Pipeline": "Automated build and deployment",
            "System Integration Test": "Comprehensive system testing",
            "Backup System": "Automated backup and recovery",
            "Power Management": "Power usage optimization",
            "Media Server": "Media streaming and management",
            "IoT Platform": "IoT device management",
            "RDMA Desktop App": "RDMA desktop application",
            "RDMA Modern App": "Modern RDMA interface",
            "RDMA Memory Portal": "RDMA memory sharing portal"
        }
        return descriptions.get(tool_name, "Homelab management tool")
    
    def get_tool_path(self, tool_name):
        """Get file path for tool"""
        paths = {
            "VPN Gateway": "VPN Gateway/vpn_gateway.py",
            "Network Monitor": "Network Monitor/network_monitor.py",
            "Web Dashboard": "Core Services/web_dashboard.py",
            "System Monitor": "Core Services/unified_monitoring.py",
            "GPU Monitor": "GPU Monitor/gpu_monitor.py",
            "RAM Monitor": "Memory Monitor/ram_monitor_gui.py",
            "Storage Monitor": "Storage Monitor/storage_monitor.py",
            "CPU Monitor": "CPU Monitor/cpu_monitor.py",
            "Container Manager": "Container Manager/container_manager.py",
            "CI/CD Pipeline": "Core Services/cicd_manager.py",
            "System Integration Test": "complete_system_verification.py",
            "Backup System": "Core Services/backup_manager.py",
            "Power Management": "Power Manager/power_manager.py",
            "Media Server": "Media Server/media_server_manager.py",
            "IoT Platform": "IoT Platform/iot_platform.py",
            "RDMA Desktop App": "RDMA Desktop App/rdma_desktop_app.py",
            "RDMA Modern App": "RDMA Desktop App/rdma_modern_tkinter.py",
            "RDMA Memory Portal": "Memory Portal/memory_portal_gui.py"
        }
        return paths.get(tool_name, f"{tool_name.lower().replace(' ', '_')}.py")
    
    def get_tool_category(self, tool_name):
        """Get category for tool"""
        for category, tools in self.categories.items():
            if tool_name in tools:
                return category.lower().replace(' ', '_')
        return "other"
    
    def launch_tool(self, tool_name, tool_info):
        """Launch a tool with proper error handling"""
        try:
            # Check if already running
            if tool_name in self.running_tools:
                process = self.running_tools[tool_name]
                if process.poll() is None:
                    messagebox.showinfo("Tool Running", f"{tool_name} is already running!")
                    return
                else:
                    del self.running_tools[tool_name]
            
            # Update UI
            tool_info['status_label'].config(text="● Starting", fg=self.colors['warning'])
            tool_info['button'].config(state='disabled', text="⏳ Starting...")
            
            # Get tool path
            base_path = Path(__file__).parent
            tool_path = base_path / tool_info['path']
            
            if not tool_path.exists():
                self.update_tool_status(tool_info, "● Not Found", self.colors['danger'], "🚀 Launch")
                messagebox.showerror("Tool Not Found", f"Tool file not found: {tool_path}")
                return
            
            # Launch in thread
            threading.Thread(target=self._launch_tool_thread, args=(tool_name, tool_info, tool_path, base_path), daemon=True).start()
            
            # Notify mesh if available
            if self.mesh_comm:
                self.mesh_comm.send_message(
                    "homelab-launcher",
                    "tool_launched",
                    {"tool_name": tool_name, "timestamp": datetime.now().isoformat()}
                )
            
        except Exception as e:
            self.logger.error(f"Failed to launch {tool_name}: {e}")
            self.update_tool_status(tool_info, "● Error", self.colors['danger'], "🚀 Launch")
            messagebox.showerror("Launch Error", f"Failed to launch {tool_name}: {e}")
    
    def _launch_tool_thread(self, tool_name, tool_info, tool_path, base_path):
        """Tool launch thread"""
        try:
            # Determine if GUI tool
            gui_tools = ["VPN Gateway", "Network Monitor", "GPU Monitor", "RAM Monitor", 
                        "Storage Monitor", "CPU Monitor", "Web Dashboard", 
                        "Container Manager", "Backup System", "Power Management",
                        "Media Server", "IoT Platform", "RDMA Desktop App", 
                        "RDMA Modern App", "RDMA Memory Portal"]
            
            is_gui = tool_name in gui_tools
            
            # Prepare environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(base_path)
            
            # Launch process
            if is_gui:
                # GUI application
                if os.name == 'nt':  # Windows
                    # Use pythonw for GUI apps
                    pythonw_path = self.find_pythonw_executable()
                    if pythonw_path and Path(pythonw_path).exists():
                        process = subprocess.Popen(
                            [pythonw_path, str(tool_path)],
                            cwd=str(base_path),
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    else:
                        # Fallback to python
                        process = subprocess.Popen(
                            [sys.executable, str(tool_path)],
                            cwd=str(base_path),
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                else:
                    # Linux/Unix
                    process = subprocess.Popen(
                        [sys.executable, str(tool_path)],
                        cwd=str(base_path),
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
            else:
                # Console application
                process = subprocess.Popen(
                    [sys.executable, str(tool_path)],
                    cwd=str(base_path),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # Store process
            self.running_tools[tool_name] = process
            
            # Update UI
            self.root.after(0, lambda: self.update_tool_status(tool_info, "● Running", self.colors['success'], "⏹️ Stop"))
            
            # Monitor process
            self.monitor_process(tool_name, tool_info, process)
            
        except Exception as e:
            self.logger.error(f"Error launching {tool_name}: {e}")
            self.root.after(0, lambda: self.update_tool_status(tool_info, "● Error", self.colors['danger'], "🚀 Launch"))
    
    def find_pythonw_executable(self):
        """Find pythonw executable on Windows"""
        try:
            # Check common locations
            pythonw_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WindowsApps', 'pythonw3.exe'),
                os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'WindowsApps', 'pythonw3.exe'),
                os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
            ]
            
            for path in pythonw_paths:
                if Path(path).exists():
                    return path
            
            return None
        except:
            return None
    
    def monitor_process(self, tool_name, tool_info, process):
        """Monitor running process"""
        def monitor():
            try:
                # Wait for process to complete
                stdout, stderr = process.communicate()
                
                # Update UI when process ends
                self.root.after(0, lambda: self.update_tool_status(tool_info, "● Stopped", self.colors['text_secondary'], "🚀 Launch"))
                
                # Remove from running tools
                if tool_name in self.running_tools:
                    del self.running_tools[tool_name]
                
                # Log completion
                if process.returncode == 0:
                    self.logger.info(f"Tool {tool_name} completed successfully")
                else:
                    self.logger.error(f"Tool {tool_name} exited with code {process.returncode}")
                    if stderr:
                        self.logger.error(f"Error: {stderr}")
                
                # Notify mesh if available
                if self.mesh_comm:
                    self.mesh_comm.send_message(
                        "homelab-launcher",
                        "tool_stopped",
                        {"tool_name": tool_name, "exit_code": process.returncode}
                    )
                    
            except Exception as e:
                self.logger.error(f"Error monitoring {tool_name}: {e}")
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def update_tool_status(self, tool_info, status_text, status_color, button_text):
        """Update tool status in UI"""
        try:
            tool_info['status_label'].config(text=status_text, fg=status_color)
            tool_info['button'].config(state='normal', text=button_text)
        except:
            pass  # UI might be destroyed
    
    def stop_tool(self, tool_name, tool_info):
        """Stop a running tool"""
        try:
            if tool_name in self.running_tools:
                process = self.running_tools[tool_name]
                process.terminate()
                
                # Wait a bit for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                del self.running_tools[tool_name]
                self.update_tool_status(tool_info, "● Stopped", self.colors['text_secondary'], "🚀 Launch")
                
                self.logger.info(f"Stopped tool: {tool_name}")
        except Exception as e:
            self.logger.error(f"Failed to stop {tool_name}: {e}")
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Running tools count
        self.running_tools_label = tk.Label(status_frame, text="🔧 Running Tools: 0", 
                                          font=('Segoe UI', 10),
                                          bg=self.colors['card'], fg=self.colors['text'])
        self.running_tools_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Mesh status
        if self.mesh_comm:
            self.mesh_status_label.config(text="🌐 Mesh: Connected", fg=self.colors['success'])
        
        # System info
        self.system_info_label = tk.Label(status_frame, text="🖥️ HAZACER", 
                                         font=('Segoe UI', 10),
                                         bg=self.colors['card'], fg=self.colors['text_secondary'])
        self.system_info_label.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def load_tools(self):
        """Load and initialize tools"""
        self.logger.info("Loading tools...")
        
        # Check tool availability
        for tool_name, tool_info in self.tool_widgets.items():
            tool_path = Path(__file__).parent / tool_info['path']
            if tool_path.exists():
                self.update_tool_status(tool_info, "● Ready", self.colors['success'], "🚀 Launch")
            else:
                self.update_tool_status(tool_info, "● Not Found", self.colors['danger'], "🚀 Launch")
    
    def start_status_monitoring(self):
        """Start status monitoring"""
        def update_status():
            try:
                # Update running tools count
                running_count = len(self.running_tools)
                self.running_tools_label.config(text=f"🔧 Running Tools: {running_count}")
                
                # Update mesh status
                if self.mesh_comm:
                    apps = self.mesh_comm.discover_applications()
                    self.mesh_status_label.config(text=f"🌐 Mesh: {len(apps)} Apps", fg=self.colors['success'])
                
            except Exception as e:
                self.logger.error(f"Status update error: {e}")
            
            # Schedule next update
            self.root.after(5000, update_status)
        
        # Start monitoring
        self.root.after(1000, update_status)
    
    # Mesh communication handlers
    def handle_mesh_launch_request(self, message_data):
        """Handle mesh launch request from other node"""
        try:
            data = message_data.get('data', {})
            tool_name = data.get('tool_name')
            
            if tool_name and tool_name in self.tool_widgets:
                self.logger.info(f"Mesh launch request for {tool_name}")
                self.root.after(0, lambda: self.launch_tool(tool_name, self.tool_widgets[tool_name]))
                
        except Exception as e:
            self.logger.error(f"Failed to handle mesh launch request: {e}")
    
    def handle_mesh_status_update(self, message_data):
        """Handle mesh status update"""
        try:
            data = message_data.get('data', {})
            self.logger.info(f"Mesh status update: {data}")
        except Exception as e:
            self.logger.error(f"Failed to handle mesh status update: {e}")
    
    def handle_mesh_tools_sync(self, message_data):
        """Handle mesh tools synchronization"""
        try:
            data = message_data.get('data', {})
            remote_tools = data.get('tools', {})
            
            self.logger.info(f"Received tools sync from {message_data.get('source_app')}")
            
            # Update UI with remote tool status if needed
            for tool_name, status in remote_tools.items():
                if tool_name in self.tool_widgets:
                    # Update local status based on remote status
                    pass
                    
        except Exception as e:
            self.logger.error(f"Failed to handle mesh tools sync: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop all running tools
            for tool_name, process in list(self.running_tools.items()):
                try:
                    process.terminate()
                except:
                    pass
            
            # Stop mesh communication
            if self.mesh_comm:
                self.mesh_comm.stop()
                
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = EnhancedHomelabLauncher(root)
    
    try:
        root.mainloop()
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()
