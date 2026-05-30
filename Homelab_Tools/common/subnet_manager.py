#!/usr/bin/env python3
"""
Subnet Communication Manager - Unified App-to-App Communication
Manages broad subnet-wide communication between all homelab tools
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import time
from datetime import datetime
import logging
from typing import List, Dict, Any
from subnet_discovery import SubnetCommunicator, create_homelab_communicator, get_homelab_services

class SubnetManager:
    """Unified subnet communication manager for homelab tools"""
    
    def __init__(self, root=None):
        self.root = root
        self.running = False
        self.communicator = None
        self.service_id = None
        
        # UI elements
        self.services_tree = None
        self.messages_text = None
        self.status_label = None
        
        # Colors for UI
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00d4ff',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0'
        }
        
        # Setup logging
        self.logger = logging.getLogger("SubnetManager")
        
        # Initialize UI if root provided
        if root:
            self.create_ui()
    
    def create_ui(self):
        """Create the subnet manager UI"""
        self.root.title("🌐 Subnet Communication Manager")
        self.root.geometry("800x600")
        self.root.configure(bg=self.colors['bg'])
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="🌐 Subnet Communication Manager",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        control_frame.pack(side=tk.RIGHT)
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start",
                                  command=self.start_service,
                                  bg=self.colors['success'], fg='white',
                                  font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=15, pady=5)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop",
                                 command=self.stop_service,
                                 bg=self.colors['danger'], fg='white',
                                 font=('Segoe UI', 10, 'bold'),
                                 relief='flat', padx=15, pady=5,
                                 state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(control_frame, text="🔄 Refresh",
                                    command=self.refresh_services,
                                    bg=self.colors['info'], fg='white',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='flat', padx=15, pady=5)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(header_frame, text="● Inactive",
                                    font=('Segoe UI', 12, 'bold'),
                                    fg=self.colors['danger'], bg=self.colors['bg'])
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Services
        left_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        services_label = tk.Label(left_frame, text="📡 Discovered Services",
                                  font=('Segoe UI', 14, 'bold'),
                                  fg=self.colors['text'], bg=self.colors['bg'])
        services_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Services tree
        tree_frame = tk.Frame(left_frame, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('App Name', 'Type', 'Host', 'Port', 'Status')
        self.services_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=scrollbar.set)
        
        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - Messages and controls
        right_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Message section
        messages_label = tk.Label(right_frame, text="💬 Messages",
                                   font=('Segoe UI', 14, 'bold'),
                                   fg=self.colors['text'], bg=self.colors['bg'])
        messages_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.messages_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD,
                                                      bg=self.colors['card'], fg=self.colors['text'],
                                                      font=('Consolas', 9), height=10)
        self.messages_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Communication controls
        comm_frame = tk.LabelFrame(right_frame, text="📤 Send Message",
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Segoe UI', 12, 'bold'))
        comm_frame.pack(fill=tk.X)
        
        # Target selection
        target_frame = tk.Frame(comm_frame, bg=self.colors['card'])
        target_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(target_frame, text="Target:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        
        self.target_var = tk.StringVar(value="broadcast")
        target_combo = ttk.Combobox(target_frame, textvariable=self.target_var,
                                     values=["broadcast", "monitoring", "computing", "infrastructure", "management"],
                                     width=20)
        target_combo.pack(side=tk.LEFT, padx=5)
        
        # Message input
        msg_frame = tk.Frame(comm_frame, bg=self.colors['card'])
        msg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.message_entry = tk.Entry(msg_frame, bg=self.colors['graph_bg'], fg=self.colors['text'])
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        send_btn = tk.Button(msg_frame, text="📤 Send",
                           command=self.send_message,
                           bg=self.colors['primary'], fg='white',
                           font=('Segoe UI', 10, 'bold'),
                           relief='flat', padx=10)
        send_btn.pack(side=tk.RIGHT)
    
    def start_service(self):
        """Start the subnet communication service"""
        try:
            # Create communicator
            self.communicator, self.service_id = create_homelab_communicator(
                "SubnetManager",
                "infrastructure",
                ["service_discovery", "message_routing", "subnet_management"]
            )
            
            # Setup message handlers
            self.communicator.on_message("service_update", self.handle_service_update)
            self.communicator.on_message("ping", self.handle_ping)
            self.communicator.on_message("status_request", self.handle_status_request)
            
            self.running = True
            
            # Update UI
            if hasattr(self, 'start_btn'):
                self.start_btn.config(state='disabled')
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state='normal')
            if hasattr(self, 'status_label'):
                self.status_label.config(text="● Active", fg=self.colors['success'])
            
            # Start refresh loop
            threading.Thread(target=self.refresh_loop, daemon=True).start()
            
            self.log_message("Subnet communication service started")
            
        except Exception as e:
            self.log_message(f"Failed to start service: {e}", "error")
            if self.root:  # Only show messagebox if running with UI
                messagebox.showerror("Error", f"Failed to start service: {e}")
    
    def register_service(self, app_name, app_type, port, version, capabilities, status):
        """Register a new service with the subnet communicator"""
        if self.communicator:
            return self.communicator.register_local_service(
                app_name=app_name,
                app_type=app_type, 
                port=port,
                version=version,
                capabilities=capabilities,
                status=status
            )
        return None
    
    def stop_service(self):
        """Stop the subnet communication service"""
        try:
            if self.communicator:
                self.communicator.stop()
                self.communicator = None
            
            self.running = False
            self.service_id = None
            
            # Update UI
            if hasattr(self, 'start_btn'):
                self.start_btn.config(state='normal')
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state='disabled')
            if hasattr(self, 'status_label'):
                self.status_label.config(text="● Inactive", fg=self.colors['danger'])
            
            self.log_message("Subnet communication service stopped")
            
        except Exception as e:
            self.log_message(f"Failed to stop service: {e}", "error")
    
    def refresh_services(self):
        """Refresh the services list"""
        try:
            if self.communicator:
                # Clear tree
                if self.services_tree is not None:
                    for item in self.services_tree.get_children():
                        self.services_tree.delete(item)
                
                # Get services
                services = self.communicator.discovery.discover_services()
                
                if self.services_tree is not None:
                    for service in services:
                        status_color = self.colors['success'] if service.status == 'active' else self.colors['warning']
                        
                        self.services_tree.insert('', 'end', values=(
                            service.app_name,
                            service.app_type,
                            service.host,
                            service.port,
                            service.status
                        ))
                
                self.log_message(f"Refreshed {len(services)} services")
            
        except Exception as e:
            self.log_message(f"Failed to refresh services: {e}", "error")
    
    def refresh_loop(self):
        """Background refresh loop"""
        while self.running:
            try:
                self.refresh_services()
                time.sleep(10)  # Refresh every 10 seconds
            except Exception as e:
                self.log_message(f"Refresh loop error: {e}", "error")
                time.sleep(5)
    
    def send_message(self):
        """Send a message to selected target"""
        try:
            message_text = self.message_entry.get().strip()
            if not message_text:
                return
            
            target = self.target_var.get()
            message = {
                'type': 'user_message',
                'text': message_text,
                'sender': 'SubnetManager',
                'timestamp': time.time()
            }
            
            if target == "broadcast":
                self.communicator.send_to_type("all", message)
                self.log_message(f"Broadcast: {message_text}")
            else:
                self.communicator.send_to_type(target, message)
                self.log_message(f"Sent to {target}: {message_text}")
            
            # Clear entry
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            self.log_message(f"Failed to send message: {e}", "error")
    
    def handle_service_update(self, message_data, addr):
        """Handle service update messages"""
        try:
            data = message_data.get('data', {})
            self.log_message(f"Service update from {addr[0]}: {data}")
            self.refresh_services()
        except Exception as e:
            self.log_message(f"Error handling service update: {e}", "error")
    
    def handle_ping(self, message_data, addr):
        """Handle ping messages"""
        try:
            data = message_data.get('data', {})
            self.log_message(f"Ping from {addr[0]}: {data.get('message', 'ping')}")
            
            # Send pong response
            if self.communicator:
                response = {
                    'type': 'pong',
                    'message': 'pong from SubnetManager',
                    'timestamp': time.time()
                }
                self.communicator.send_message(message_data.get('from_service'), response)
        
        except Exception as e:
            self.log_message(f"Error handling ping: {e}", "error")
    
    def handle_status_request(self, message_data, addr):
        """Handle status request messages"""
        try:
            if self.communicator:
                status = {
                    'type': 'status_response',
                    'service': 'SubnetManager',
                    'status': 'active' if self.running else 'inactive',
                    'services_count': len(self.communicator.discovery.discover_services()),
                    'timestamp': time.time()
                }
                self.communicator.send_message(message_data.get('from_service'), status)
        
        except Exception as e:
            self.log_message(f"Error handling status request: {e}", "error")
    
    def log_message(self, message, level="info"):
        """Log message to messages text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            prefix = "❌"
        elif level == "warning":
            prefix = "⚠️"
        else:
            prefix = "ℹ️"
        
        log_entry = f"[{timestamp}] {prefix} {message}\n"
        
        if self.messages_text is not None:
            self.messages_text.insert(tk.END, log_entry)
            self.messages_text.see(tk.END)
            
            # Limit to last 1000 lines
            lines = self.messages_text.get(1.0, tk.END).split('\n')
            if len(lines) > 1000:
                self.messages_text.delete(1.0, f"{len(lines)-1000}.0")
        
        # Also log to console
        print(f"[SubnetManager] {level.upper()}: {message}")

# Integration functions for other homelab tools
def integrate_subnet_discovery(app_name: str, app_type: str, capabilities: List[str] = None):
    """Integrate subnet discovery into any homelab tool"""
    communicator, service_id = create_homelab_communicator(app_name, app_type, capabilities)
    
    # Setup default message handlers
    @communicator.on_message("ping")
    def handle_ping(message_data, addr):
        print(f"Ping received from {addr[0]}")
        response = {'type': 'pong', 'message': f'pong from {app_name}'}
        communicator.send_message(message_data.get('from_service'), response)
    
    @communicator.on_message("status_request")
    def handle_status_request(message_data, addr):
        print(f"Status request from {addr[0]}")
        status = {
            'type': 'status_response',
            'service': app_name,
            'status': 'active',
            'timestamp': time.time()
        }
        communicator.send_message(message_data.get('from_service'), status)
    
    return communicator

def send_subnet_message(app_name: str, target_app: str, message: Dict[str, Any]):
    """Send a message to another app on the subnet"""
    try:
        temp_communicator = SubnetCommunicator(f"{app_name}_temp", "temp")
        temp_communicator.discovery.start_discovery()
        time.sleep(1)  # Wait for discovery
        
        success = temp_communicator.send_to_app(target_app, message)
        temp_communicator.stop()
        
        return success
    except Exception as e:
        print(f"Failed to send message to {target_app}: {e}")
        return False

def get_subnet_apps() -> Dict[str, List[str]]:
    """Get all apps on the subnet organized by type"""
    try:
        services = get_homelab_services()
        apps_by_type = {}
        
        for service in services:
            app_type = service.app_type
            if app_type not in apps_by_type:
                apps_by_type[app_type] = []
            
            if service.app_name not in apps_by_type[app_type]:
                apps_by_type[app_type].append(service.app_name)
        
        return apps_by_type
    except Exception as e:
        print(f"Failed to get subnet apps: {e}")
        return {}

if __name__ == "__main__":
    # Run the subnet manager GUI
    import tkinter as tk
    root = tk.Tk()
    app = SubnetManager(root)
    root.mainloop()
