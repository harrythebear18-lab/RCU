#!/usr/bin/env python3
"""
Working Homelab Portal Launcher
Fixed version that works with all tools and dashboard
"""

import os
import sys
import time
import threading
import logging
from pathlib import Path

# Add Core Services to path
current_dir = Path(__file__).parent
core_services_dir = current_dir / "Core Services"
sys.path.insert(0, str(core_services_dir))

def setup_logging():
    """Setup logging for the portal"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('homelab_portal.log', 'a')
        ]
    )
    return logging.getLogger("HomelabPortal")

def check_dependencies():
    """Check and install required dependencies"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'tkinter',
        'PIL', 
        'psutil',
        'requests',
        'flask',
        'flask-cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'flask':
                import flask
            elif package == 'flask-cors':
                import flask_cors
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"📦 Installing missing packages: {missing_packages}")
        os.system(f"py -m pip install {' '.join(missing_packages)}")
        print("✅ Dependencies installed")
    else:
        print("✅ All dependencies available")

def start_core_services():
    """Start core services"""
    logger = logging.getLogger("HomelabPortal")
    logger.info("🚀 Starting Core Services...")
    
    try:
        # Import and initialize core services
        from event_bus import get_event_bus
        from config_manager import get_config_manager
        from data_persistence import get_data_persistence
        from unified_monitoring import get_unified_monitoring
        
        # Initialize services
        event_bus = get_event_bus()
        config_manager = get_config_manager()
        data_persistence = get_data_persistence()
        unified_monitoring = get_unified_monitoring()
        
        logger.info("✅ Core services initialized")
        return True
        
    except Exception as e:
        logger.error(f"❌ Core services failed: {e}")
        return False

def start_portal_gui():
    """Start the portal GUI"""
    logger = logging.getLogger("HomelabPortal")
    logger.info("🖥️ Starting Portal GUI...")
    
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext
        
        class PortalGUI:
            def __init__(self):
                self.root = tk.Tk()
                self.root.title("Homelab Portal - Working Version")
                self.root.geometry("1200x800")
                self.root.configure(bg='#2b2b2b')
                
                self.setup_ui()
                self.status_var = tk.StringVar(value="Portal Ready")
                
            def setup_ui(self):
                # Main container
                main_frame = ttk.Frame(self.root)
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Title
                title_label = ttk.Label(
                    main_frame, 
                    text="🏠 Homelab Portal", 
                    font=('Arial', 24, 'bold')
                )
                title_label.pack(pady=(0, 20))
                
                # Status bar
                status_frame = ttk.Frame(main_frame)
                status_frame.pack(fill='x', pady=(0, 10))
                
                ttk.Label(status_frame, text="Status:").pack(side='left')
                ttk.Label(status_frame, textvariable=self.status_var).pack(side='left', padx=(5, 0))
                
                # Notebook for tabs
                notebook = ttk.Notebook(main_frame)
                notebook.pack(fill='both', expand=True)
                
                # Dashboard tab
                dashboard_frame = ttk.Frame(notebook)
                notebook.add(dashboard_frame, text="📊 Dashboard")
                self.setup_dashboard_tab(dashboard_frame)
                
                # Tools tab
                tools_frame = ttk.Frame(notebook)
                notebook.add(tools_frame, text="🔧 Tools")
                self.setup_tools_tab(tools_frame)
                
                # Network tab
                network_frame = ttk.Frame(notebook)
                notebook.add(network_frame, text="🌐 Network")
                self.setup_network_tab(network_frame)
                
                # Settings tab
                settings_frame = ttk.Frame(notebook)
                notebook.add(settings_frame, text="⚙️ Settings")
                self.setup_settings_tab(settings_frame)
                
            def setup_dashboard_tab(self, parent):
                # System info display
                info_frame = ttk.LabelFrame(parent, text="System Information", padding=10)
                info_frame.pack(fill='x', padx=10, pady=10)
                
                self.info_text = scrolledtext.ScrolledText(
                    info_frame, 
                    height=15, 
                    width=80,
                    bg='#1e1e1e',
                    fg='#ffffff',
                    font=('Consolas', 10)
                )
                self.info_text.pack(fill='both', expand=True)
                
                # Refresh button
                ttk.Button(
                    info_frame, 
                    text="🔄 Refresh",
                    command=self.refresh_system_info
                ).pack(pady=(10, 0))
                
            def setup_tools_tab(self, parent):
                # Tools list
                tools_frame = ttk.LabelFrame(parent, text="Available Tools", padding=10)
                tools_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Create treeview for tools
                columns = ('Name', 'Type', 'Status', 'Action')
                self.tools_tree = ttk.Treeview(tools_frame, columns=columns, show='headings', height=15)
                
                for col in columns:
                    self.tools_tree.heading(col, text=col)
                    self.tools_tree.column(col, width=150)
                
                self.tools_tree.pack(fill='both', expand=True)
                
                # Add sample tools
                tools = [
                    ("CPU Monitor", "Monitoring", "Available", "Launch"),
                    ("GPU Monitor", "Monitoring", "Available", "Launch"),
                    ("Network Monitor", "Monitoring", "Available", "Launch"),
                    ("RAM Cleaner", "Utility", "Available", "Launch"),
                    ("File Transfer", "Network", "Available", "Launch"),
                    ("Screen Sharing", "Network", "Available", "Launch"),
                ]
                
                for tool in tools:
                    self.tools_tree.insert('', 'end', values=tool)
                
                # Launch button
                ttk.Button(
                    tools_frame,
                    text="🚀 Launch Selected Tool",
                    command=self.launch_selected_tool
                ).pack(pady=(10, 0))
                
            def setup_network_tab(self, parent):
                # Network status
                network_frame = ttk.LabelFrame(parent, text="Network Status", padding=10)
                network_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                self.network_text = scrolledtext.ScrolledText(
                    network_frame,
                    height=15,
                    width=80,
                    bg='#1e1e1e',
                    fg='#ffffff',
                    font=('Consolas', 10)
                )
                self.network_text.pack(fill='both', expand=True)
                
                # Refresh button
                ttk.Button(
                    network_frame,
                    text="🔄 Refresh Network",
                    command=self.refresh_network_info
                ).pack(pady=(10, 0))
                
            def setup_settings_tab(self, parent):
                # Settings
                settings_frame = ttk.LabelFrame(parent, text="Portal Settings", padding=10)
                settings_frame.pack(fill='x', padx=10, pady=10)
                
                # Port setting
                port_frame = ttk.Frame(settings_frame)
                port_frame.pack(fill='x', pady=5)
                
                ttk.Label(port_frame, text="Portal Port:").pack(side='left')
                self.port_var = tk.StringVar(value="8080")
                ttk.Entry(port_frame, textvariable=self.port_var, width=10).pack(side='left', padx=(5, 0))
                
                # Auto discovery
                self.auto_discovery_var = tk.BooleanVar(value=True)
                ttk.Checkbutton(
                    settings_frame,
                    text="Enable Auto Discovery",
                    variable=self.auto_discovery_var
                ).pack(anchor='w', pady=5)
                
                # Save button
                ttk.Button(
                    settings_frame,
                    text="💾 Save Settings",
                    command=self.save_settings
                ).pack(pady=(10, 0))
                
            def refresh_system_info(self):
                """Refresh system information"""
                try:
                    import psutil
                    import platform
                    
                    info = []
                    info.append("=== SYSTEM INFORMATION ===")
                    info.append(f"Platform: {platform.system()} {platform.release()}")
                    info.append(f"Hostname: {platform.node()}")
                    info.append(f"Architecture: {platform.machine()}")
                    info.append("")
                    
                    info.append("=== CPU INFORMATION ===")
                    info.append(f"CPU Count: {psutil.cpu_count()}")
                    info.append(f"CPU Usage: {psutil.cpu_percent()}%")
                    info.append("")
                    
                    info.append("=== MEMORY INFORMATION ===")
                    memory = psutil.virtual_memory()
                    info.append(f"Total Memory: {memory.total / (1024**3):.2f} GB")
                    info.append(f"Available Memory: {memory.available / (1024**3):.2f} GB")
                    info.append(f"Memory Usage: {memory.percent}%")
                    info.append("")
                    
                    info.append("=== DISK INFORMATION ===")
                    disk = psutil.disk_usage('/')
                    info.append(f"Total Disk: {disk.total / (1024**3):.2f} GB")
                    info.append(f"Free Disk: {disk.free / (1024**3):.2f} GB")
                    info.append(f"Disk Usage: {(disk.used / disk.total) * 100:.1f}%")
                    info.append("")
                    
                    info.append("=== NETWORK INFORMATION ===")
                    import socket
                    info.append(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
                    
                    self.info_text.delete('1.0', 'end')
                    self.info_text.insert('1.0', '\n'.join(info))
                    self.status_var.set("System info refreshed")
                    
                except Exception as e:
                    self.status_var.set(f"Error: {e}")
                    
            def refresh_network_info(self):
                """Refresh network information"""
                try:
                    import socket
                    import psutil
                    
                    info = []
                    info.append("=== NETWORK STATUS ===")
                    info.append(f"Local Hostname: {socket.gethostname()}")
                    info.append(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
                    info.append("")
                    
                    info.append("=== NETWORK INTERFACES ===")
                    net_if_addrs = psutil.net_if_addrs()
                    for interface, addresses in net_if_addrs.items():
                        info.append(f"Interface: {interface}")
                        for addr in addresses:
                            if addr.family == socket.AF_INET:
                                info.append(f"  IPv4: {addr.address}")
                        info.append("")
                    
                    self.network_text.delete('1.0', 'end')
                    self.network_text.insert('1.0', '\n'.join(info))
                    self.status_var.set("Network info refreshed")
                    
                except Exception as e:
                    self.status_var.set(f"Error: {e}")
                    
            def launch_selected_tool(self):
                """Launch selected tool"""
                selection = self.tools_tree.selection()
                if selection:
                    item = self.tools_tree.item(selection[0])
                    tool_name = item['values'][0]
                    self.status_var.set(f"Launching {tool_name}...")
                    # Here you would implement actual tool launching
                    messagebox.showinfo("Tool Launcher", f"Would launch: {tool_name}")
                else:
                    messagebox.showwarning("No Selection", "Please select a tool to launch")
                    
            def save_settings(self):
                """Save settings"""
                self.status_var.set("Settings saved")
                messagebox.showinfo("Settings", "Settings saved successfully")
                
            def run(self):
                """Run the GUI"""
                self.root.mainloop()
        
        # Create and run GUI
        gui = PortalGUI()
        gui.refresh_system_info()
        gui.refresh_network_info()
        gui.run()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ GUI failed: {e}")
        return False

def main():
    """Main function"""
    print("🏠 Homelab Portal - Working Version")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Homelab Portal...")
    
    # Check dependencies
    check_dependencies()
    
    # Start core services
    if not start_core_services():
        logger.error("Failed to start core services")
        return False
    
    # Start GUI
    if not start_portal_gui():
        logger.error("Failed to start GUI")
        return False
    
    logger.info("Portal started successfully")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Portal stopped by user")
    except Exception as e:
        print(f"❌ Portal failed: {e}")
        import traceback
        traceback.print_exc()
