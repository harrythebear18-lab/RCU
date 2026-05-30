#!/usr/bin/env python3
"""
Homelab Resource Management Dashboard
Integrated dashboard for managing server-client homelab ecosystem.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from homelab_server import HomelabServer, ResourceType, ResourceStatus
from homelab_client import HomelabClientManager, ClientStatus

class HomelabDashboard:
    """Main dashboard for homelab resource management"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Homelab Resource Management Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f0f0f')
        
        # Modern color scheme
        self.colors = {
            'bg': '#0f0f0f',
            'card': '#1a1a1a',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#333333',
            'accent': '#ff6b6b'
        }
        
        # Initialize components
        self.server = None
        self.client_manager = None
        self.server_running = False
        self.client_connected = False
        
        # Data storage
        self.server_metrics = {}
        self.client_metrics = {}
        self.resource_data = {}
        self.allocation_data = {}
        
        # Create UI
        self.create_ui()
        
        # Start monitoring thread
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()
    
    def create_ui(self):
        """Create dashboard UI"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Server controls
        left_panel = tk.Frame(content_frame, bg=self.colors['bg'], width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=(False, False))
        
        self.create_server_panel(left_panel)
        
        # Center panel - Resource overview
        center_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 10))
        
        self.create_resource_panel(center_panel)
        
        # Right panel - Client status
        right_panel = tk.Frame(content_frame, bg=self.colors['bg'], width=400)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=(False, False))
        
        self.create_client_panel(right_panel)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🏠 Homelab Resource Management",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg=self.colors['card'])
        status_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Server status
        self.server_status_label = tk.Label(status_frame, text="🔴 Server: Offline",
                                          font=('Segoe UI', 10),
                                          fg=self.colors['danger'], bg=self.colors['card'])
        self.server_status_label.pack(side=tk.LEFT, padx=10)
        
        # Client status
        self.client_status_label = tk.Label(status_frame, text="🔴 Client: Disconnected",
                                          font=('Segoe UI', 10),
                                          fg=self.colors['danger'], bg=self.colors['card'])
        self.client_status_label.pack(side=tk.LEFT, padx=10)
    
    def create_server_panel(self, parent):
        """Create server control panel"""
        # Server card
        server_card = tk.Frame(parent, bg=self.colors['card'])
        server_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Server header
        server_header = tk.Frame(server_card, bg=self.colors['card'])
        server_header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(server_header, text="🖥️ Server Management",
                 font=('Segoe UI', 14, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Server controls
        controls_frame = tk.Frame(server_card, bg=self.colors['card'])
        controls_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Start/Stop server button
        self.server_toggle_btn = tk.Button(controls_frame, text="▶️ Start Server",
                                          font=('Segoe UI', 10, 'bold'),
                                          bg=self.colors['success'], fg=self.colors['bg'],
                                          relief='flat', cursor='hand2',
                                          command=self.toggle_server)
        self.server_toggle_btn.pack(fill=tk.X, pady=5)
        
        # Server metrics
        metrics_frame = tk.Frame(server_card, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Label(metrics_frame, text="📊 Server Metrics",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Metrics display
        self.server_metrics_text = tk.Text(metrics_frame, height=8, width=40,
                                           bg=self.colors['bg'], fg=self.colors['text'],
                                           font=('Consolas', 9), relief='flat')
        self.server_metrics_text.pack(fill=tk.X, pady=5)
        
        # Resource management
        resource_mgmt_frame = tk.Frame(server_card, bg=self.colors['card'])
        resource_mgmt_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        tk.Label(resource_mgmt_frame, text="⚙️ Resource Management",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Resource list
        self.resource_listbox = tk.Listbox(resource_mgmt_frame, height=6,
                                          bg=self.colors['bg'], fg=self.colors['text'],
                                          font=('Segoe UI', 9), relief='flat')
        self.resource_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def create_resource_panel(self, parent):
        """Create resource overview panel"""
        # Resource card
        resource_card = tk.Frame(parent, bg=self.colors['card'])
        resource_card.pack(fill=tk.BOTH, expand=True)
        
        # Resource header
        resource_header = tk.Frame(resource_card, bg=self.colors['card'])
        resource_header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(resource_header, text="📈 Resource Overview",
                 font=('Segoe UI', 14, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Create matplotlib figure for resource visualization
        self.fig = Figure(figsize=(8, 4), facecolor=self.colors['card'])
        self.ax = self.fig.add_subplot(111, facecolor=self.colors['card'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, resource_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Allocation controls
        allocation_frame = tk.Frame(resource_card, bg=self.colors['card'])
        allocation_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Label(allocation_frame, text="🎯 Quick Actions",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Action buttons
        action_frame = tk.Frame(allocation_frame, bg=self.colors['card'])
        action_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(action_frame, text="🔄 Refresh Resources",
                 font=('Segoe UI', 9),
                 bg=self.colors['primary'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2',
                 command=self.refresh_resources).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📊 Generate Report",
                 font=('Segoe UI', 9),
                 bg=self.colors['accent'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2',
                 command=self.generate_report).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="🧹 Cleanup Allocations",
                 font=('Segoe UI', 9),
                 bg=self.colors['warning'], fg=self.colors['bg'],
                 relief='flat', cursor='hand2',
                 command=self.cleanup_allocations).pack(side=tk.LEFT, padx=5)
    
    def create_client_panel(self, parent):
        """Create client status panel"""
        # Client card
        client_card = tk.Frame(parent, bg=self.colors['card'])
        client_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Client header
        client_header = tk.Frame(client_card, bg=self.colors['card'])
        client_header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(client_header, text="💻 Client Management",
                 font=('Segoe UI', 14, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Client controls
        controls_frame = tk.Frame(client_card, bg=self.colors['card'])
        controls_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Connect/Disconnect button
        self.client_toggle_btn = tk.Button(controls_frame, text="🔗 Connect Client",
                                          font=('Segoe UI', 10, 'bold'),
                                          bg=self.colors['primary'], fg=self.colors['bg'],
                                          relief='flat', cursor='hand2',
                                          command=self.toggle_client)
        self.client_toggle_btn.pack(fill=tk.X, pady=5)
        
        # Server URL input
        url_frame = tk.Frame(controls_frame, bg=self.colors['card'])
        url_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(url_frame, text="Server URL:",
                 font=('Segoe UI', 9),
                 fg=self.colors['text_secondary'], bg=self.colors['card']).pack(anchor=tk.W)
        
        self.server_url_var = tk.StringVar(value="http://localhost:8080")
        url_entry = tk.Entry(url_frame, textvariable=self.server_url_var,
                             bg=self.colors['bg'], fg=self.colors['text'],
                             font=('Segoe UI', 9), relief='flat')
        url_entry.pack(fill=tk.X, pady=2)
        
        # Client metrics
        metrics_frame = tk.Frame(client_card, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Label(metrics_frame, text="📊 Client Metrics",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Metrics display
        self.client_metrics_text = tk.Text(metrics_frame, height=8, width=40,
                                           bg=self.colors['bg'], fg=self.colors['text'],
                                           font=('Consolas', 9), relief='flat')
        self.client_metrics_text.pack(fill=tk.X, pady=5)
        
        # Allocations
        allocations_frame = tk.Frame(client_card, bg=self.colors['card'])
        allocations_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        tk.Label(allocations_frame, text="📦 Current Allocations",
                 font=('Segoe UI', 12, 'bold'),
                 fg=self.colors['text'], bg=self.colors['card']).pack(anchor=tk.W)
        
        # Allocations list
        self.allocations_listbox = tk.Listbox(allocations_frame, height=6,
                                              bg=self.colors['bg'], fg=self.colors['text'],
                                              font=('Segoe UI', 9), relief='flat')
        self.allocations_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def toggle_server(self):
        """Toggle server on/off"""
        if not self.server_running:
            # Start server
            try:
                self.server = HomelabServer()
                self.server_running = True
                
                # Start server in background thread
                server_thread = threading.Thread(target=self.server.run, daemon=True)
                server_thread.start()
                
                self.server_toggle_btn.config(text="⏹️ Stop Server", bg=self.colors['danger'])
                self.server_status_label.config(text="🟢 Server: Online", fg=self.colors['success'])
                
                messagebox.showinfo("Server", "Homelab server started successfully!")
                
            except Exception as e:
                messagebox.showerror("Server Error", f"Failed to start server: {e}")
        else:
            # Stop server
            try:
                if self.server:
                    self.server.stop_monitoring()
                self.server = None
                self.server_running = False
                
                self.server_toggle_btn.config(text="▶️ Start Server", bg=self.colors['success'])
                self.server_status_label.config(text="🔴 Server: Offline", fg=self.colors['danger'])
                
                messagebox.showinfo("Server", "Homelab server stopped!")
                
            except Exception as e:
                messagebox.showerror("Server Error", f"Failed to stop server: {e}")
    
    def toggle_client(self):
        """Toggle client connection"""
        if not self.client_connected:
            # Connect client
            try:
                server_url = self.server_url_var.get()
                self.client_manager = HomelabClientManager(server_url)
                
                if self.client_manager.connect():
                    self.client_connected = True
                    
                    self.client_toggle_btn.config(text="🔌 Disconnect Client", bg=self.colors['danger'])
                    self.client_status_label.config(text="🟢 Client: Connected", fg=self.colors['success'])
                    
                    messagebox.showinfo("Client", "Connected to homelab server successfully!")
                else:
                    messagebox.showerror("Client Error", "Failed to connect to server")
                    
            except Exception as e:
                messagebox.showerror("Client Error", f"Failed to connect: {e}")
        else:
            # Disconnect client
            try:
                if self.client_manager:
                    self.client_manager.disconnect()
                self.client_manager = None
                self.client_connected = False
                
                self.client_toggle_btn.config(text="🔗 Connect Client", bg=self.colors['primary'])
                self.client_status_label.config(text="🔴 Client: Disconnected", fg=self.colors['danger'])
                
                messagebox.showinfo("Client", "Disconnected from homelab server!")
                
            except Exception as e:
                messagebox.showerror("Client Error", f"Failed to disconnect: {e}")
    
    def refresh_resources(self):
        """Refresh resource information"""
        if not self.server_running:
            messagebox.showwarning("Warning", "Server is not running!")
            return
        
        try:
            # Get server resources
            if self.server:
                resources = self.server.get_all_resources()
                
                # Update resource listbox
                self.resource_listbox.delete(0, tk.END)
                
                for resource in resources:
                    status_emoji = "🟢" if resource['status'] == 'available' else "🟡" if resource['status'] == 'allocated' else "🔴"
                    resource_text = f"{status_emoji} {resource['name']} ({resource['type']}) - {resource['capacity']:.1f}GB"
                    self.resource_listbox.insert(tk.END, resource_text)
                
                # Update visualization
                self.update_resource_visualization(resources)
                
                # Update server metrics
                self.update_server_metrics()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh resources: {e}")
    
    def update_resource_visualization(self, resources):
        """Update resource visualization chart"""
        try:
            self.ax.clear()
            
            # Group resources by type
            resource_types = {}
            for resource in resources:
                resource_type = resource['type']
                if resource_type not in resource_types:
                    resource_types[resource_type] = {'total': 0, 'allocated': 0}
                
                resource_types[resource_type]['total'] += resource['capacity']
                resource_types[resource_type]['allocated'] += resource['allocated']
            
            # Create bar chart
            types = list(resource_types.keys())
            total_values = [resource_types[t]['total'] for t in types]
            allocated_values = [resource_types[t]['allocated'] for t in types]
            
            x = np.arange(len(types))
            width = 0.35
            
            bars1 = self.ax.bar(x - width/2, total_values, width, label='Total', color=self.colors['primary'])
            bars2 = self.ax.bar(x + width/2, allocated_values, width, label='Allocated', color=self.colors['accent'])
            
            self.ax.set_xlabel('Resource Type')
            self.ax.set_ylabel('Capacity (GB)')
            self.ax.set_title('Resource Allocation Overview')
            self.ax.set_xticks(x)
            self.ax.set_xticklabels([t.upper() for t in types])
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Style the plot
            self.ax.spines['bottom'].set_color(self.colors['text_secondary'])
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['left'].set_color(self.colors['text_secondary'])
            self.ax.tick_params(colors=self.colors['text_secondary'])
            self.ax.xaxis.label.set_color(self.colors['text'])
            self.ax.yaxis.label.set_color(self.colors['text'])
            self.ax.title.set_color(self.colors['text'])
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating visualization: {e}")
    
    def update_server_metrics(self):
        """Update server metrics display"""
        try:
            if self.server:
                status = self.server.get_scheduler_status()
                
                metrics_text = f"""
Server Status: {status['scheduler_active']}
Total Resources: {status['total_resources']}
Enabled Tasks: {status['enabled_tasks']}
Running Tasks: {status['running_tasks']}
Active Clients: {len(self.server.clients)}
Active Allocations: {len(self.server.allocations)}

Next Runs:
"""
                
                for next_run in status.get('next_runs', [])[:5]:
                    metrics_text += f"• {next_run['name']}: {next_run['next_run']}\n"
                
                self.server_metrics_text.delete(1.0, tk.END)
                self.server_metrics_text.insert(1.0, metrics_text)
                
        except Exception as e:
            print(f"Error updating server metrics: {e}")
    
    def update_client_metrics(self):
        """Update client metrics display"""
        try:
            if self.client_manager and self.client_connected:
                status = self.client_manager.get_status()
                
                metrics_text = f"""
Client ID: {status.get('client_id', 'N/A')}
Connection Status: {status.get('status', 'N/A')}
Server URL: {status.get('server_url', 'N/A')}
Allocated Resources: {status.get('allocated_resources', 0)}

Local Metrics:
"""
                
                # Get local metrics
                local_metrics = self.client_manager.client.get_local_metrics()
                
                if local_metrics:
                    metrics_text += f"CPU Usage: {local_metrics.get('cpu', {}).get('usage_percent', 0):.1f}%\n"
                    metrics_text += f"Memory Usage: {local_metrics.get('memory', {}).get('percent', 0):.1f}%\n"
                    metrics_text += f"Disk Usage: {len(local_metrics.get('disk', []))} drives\n"
                
                self.client_metrics_text.delete(1.0, tk.END)
                self.client_metrics_text.insert(1.0, metrics_text)
                
                # Update allocations list
                allocations = self.client_manager.client.get_allocations()
                self.allocations_listbox.delete(0, tk.END)
                
                for allocation in allocations:
                    allocation_text = f"📦 {allocation['resource_id']} - {allocation['amount']:.1f}GB"
                    self.allocations_listbox.insert(tk.END, allocation_text)
                
        except Exception as e:
            print(f"Error updating client metrics: {e}")
    
    def generate_report(self):
        """Generate resource allocation report"""
        try:
            if not self.server_running:
                messagebox.showwarning("Warning", "Server is not running!")
                return
            
            # Generate report data
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'server_status': 'online' if self.server_running else 'offline',
                'client_status': 'connected' if self.client_connected else 'disconnected',
                'resources': {},
                'allocations': {},
                'clients': {}
            }
            
            if self.server:
                # Resource statistics
                resources = self.server.get_all_resources()
                for resource in resources:
                    resource_type = resource['type']
                    if resource_type not in report_data['resources']:
                        report_data['resources'][resource_type] = {
                            'total_capacity': 0,
                            'allocated_capacity': 0,
                            'available_capacity': 0,
                            'count': 0
                        }
                    
                    report_data['resources'][resource_type]['total_capacity'] += resource['capacity']
                    report_data['resources'][resource_type]['allocated_capacity'] += resource['allocated']
                    report_data['resources'][resource_type]['available_capacity'] += (resource['capacity'] - resource['allocated'])
                    report_data['resources'][resource_type]['count'] += 1
                
                # Allocation statistics
                for allocation_id, allocation in self.server.allocations.items():
                    resource_type = allocation.get('resource_type', 'unknown')
                    if resource_type not in report_data['allocations']:
                        report_data['allocations'][resource_type] = 0
                    report_data['allocations'][resource_type] += 1
                
                # Client statistics
                for client_id, client in self.server.clients.items():
                    report_data['clients'][client_id] = {
                        'name': client['name'],
                        'status': client['status'],
                        'last_seen': client['last_seen']
                    }
            
            # Save report
            report_file = f"homelab_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            messagebox.showinfo("Report Generated", f"Report saved to {report_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def cleanup_allocations(self):
        """Clean up expired allocations"""
        try:
            if not self.server_running:
                messagebox.showwarning("Warning", "Server is not running!")
                return
            
            # Count expired allocations
            expired_count = 0
            current_time = datetime.now()
            
            for allocation_id, allocation in list(self.server.allocations.items()):
                expires_at = datetime.fromisoformat(allocation['expires_at'])
                if current_time > expires_at:
                    expired_count += 1
            
            if expired_count > 0:
                result = messagebox.askyesno("Cleanup", f"Found {expired_count} expired allocations. Clean them up?")
                if result:
                    # Force cleanup
                    self.server._cleanup_expired_allocations()
                    messagebox.showinfo("Cleanup", f"Cleaned up {expired_count} expired allocations")
            else:
                messagebox.showinfo("Cleanup", "No expired allocations found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cleanup allocations: {e}")
    
    def start_monitoring(self):
        """Start monitoring thread"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Monitoring loop for dashboard updates"""
        while self.monitoring_active:
            try:
                # Update server metrics
                if self.server_running:
                    self.update_server_metrics()
                
                # Update client metrics
                if self.client_connected:
                    self.update_client_metrics()
                
                # Sleep for update interval
                time.sleep(10)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def on_closing(self):
        """Handle window closing"""
        try:
            # Stop monitoring
            self.stop_monitoring()
            
            # Stop client
            if self.client_connected:
                self.toggle_client()
            
            # Stop server
            if self.server_running:
                self.toggle_server()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        # Close window
        self.root.destroy()

if __name__ == '__main__':
    # Create dashboard window
    root = tk.Tk()
    dashboard = HomelabDashboard(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    
    # Start the dashboard
    root.mainloop()
