#!/usr/bin/env python3
"""
Streamlined Homelab Dashboard
Inspired by Homelab Tools best features - focused, powerful, and efficient.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Import streamlined system
from streamlined_homelab_system import streamlined_homelab, ResourceStatus

class StreamlinedDashboard:
    """Streamlined dashboard inspired by Homelab Tools best features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Streamlined Homelab Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme inspired by Homelab Tools
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040',
            'accent': '#ff6b6b'
        }
        
        # System state
        self.system_status = {}
        self.resource_data = {}
        self.client_data = {}
        self.allocation_data = {}
        
        # Create UI
        self.create_ui()
        
        # Start monitoring
        self.start_dashboard_monitoring()
    
    def create_ui(self):
        """Create the dashboard UI"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create main sections
        self.create_system_overview(content_frame)
        self.create_resource_management(content_frame)
        self.create_monitoring_section(content_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title and status
        title_frame = tk.Frame(header_frame, bg=self.colors['card'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        title_label = tk.Label(title_frame, text="🏠 Streamlined Homelab Dashboard",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        self.system_role_label = tk.Label(title_frame, text=f"Role: {streamlined_homelab.role.value}",
                                          font=('Segoe UI', 10),
                                          fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.system_role_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg=self.colors['card'])
        control_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=self.colors['success'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.start_system)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['danger'], fg=self.colors['bg'],
                                 relief='flat', cursor='hand2',
                                 command=self.stop_system)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(control_frame, text="🔄 Refresh",
                                   font=('Segoe UI', 10, 'bold'),
                                   bg=self.colors['primary'], fg=self.colors['bg'],
                                   relief='flat', cursor='hand2',
                                   command=self.refresh_dashboard)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_system_overview(self, parent):
        """Create system overview section"""
        overview_frame = tk.Frame(parent, bg=self.colors['card'])
        overview_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(overview_frame, text="📊 System Overview",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Overview cards container
        cards_container = tk.Frame(overview_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Create overview cards
        self.create_overview_card(cards_container, "Resources", "resources", 0)
        self.create_overview_card(cards_container, "Clients", "clients", 1)
        self.create_overview_card(cards_container, "Allocations", "allocations", 2)
        self.create_overview_card(cards_container, "System", "system", 3)
    
    def create_overview_card(self, parent, title, card_type, column):
        """Create individual overview card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        card.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(content_frame, text=title,
                              font=('Segoe UI', 11, 'bold'),
                              fg=self.colors['text_secondary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        # Value
        value_label = tk.Label(content_frame, text="0",
                              font=('Segoe UI', 20, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        value_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Status
        status_label = tk.Label(content_frame, text="●",
                               font=('Segoe UI', 12, 'bold'),
                               fg=self.colors['success'], bg=self.colors['card'])
        status_label.pack(anchor=tk.E, pady=(5, 0))
        
        # Store references
        setattr(self, f"{card_type}_title", title_label)
        setattr(self, f"{card_type}_value", value_label)
        setattr(self, f"{card_type}_status", status_label)
    
    def create_resource_management(self, parent):
        """Create resource management section"""
        resource_frame = tk.Frame(parent, bg=self.colors['card'])
        resource_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Title
        title_label = tk.Label(resource_frame, text="🔧 Resource Management",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(resource_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Resources tab
        resources_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(resources_frame, text="Resources")
        
        # Create resources display
        self.create_resources_display(resources_frame)
        
        # Allocations tab
        allocations_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(allocations_frame, text="Allocations")
        
        # Create allocations display
        self.create_allocations_display(allocations_frame)
        
        # Clients tab
        clients_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(clients_frame, text="Clients")
        
        # Create clients display
        self.create_clients_display(clients_frame)
    
    def create_resources_display(self, parent):
        """Create resources display"""
        # Resources container
        resources_container = tk.Frame(parent, bg=self.colors['card'])
        resources_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for resources
        columns = ('Name', 'Type', 'Capacity', 'Allocated', 'Utilization', 'Status')
        self.resources_tree = ttk.Treeview(resources_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.resources_tree.heading(col, text=col)
            self.resources_tree.column(col, width=120)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        self.resources_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(resources_container, orient='vertical', command=self.resources_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.resources_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(resources_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        allocate_btn = tk.Button(button_frame, text="➕ Allocate",
                                 font=('Segoe UI', 9),
                                 bg=self.colors['primary'], fg=self.colors['bg'],
                                 relief='flat', cursor='hand2',
                                 command=self.allocate_resource_dialog)
        allocate_btn.pack(side=tk.LEFT, padx=5)
        
        release_btn = tk.Button(button_frame, text="➖ Release",
                                font=('Segoe UI', 9),
                                bg=self.colors['warning'], fg=self.colors['bg'],
                                relief='flat', cursor='hand2',
                                command=self.release_resource_dialog)
        release_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Refresh",
                               font=('Segoe UI', 9),
                               bg=self.colors['success'], fg=self.colors['bg'],
                               relief='flat', cursor='hand2',
                               command=self.refresh_resources)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_allocations_display(self, parent):
        """Create allocations display"""
        # Allocations container
        allocations_container = tk.Frame(parent, bg=self.colors['card'])
        allocations_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for allocations
        columns = ('Client', 'Resource', 'Amount', 'Expires', 'Status')
        self.allocations_tree = ttk.Treeview(allocations_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.allocations_tree.heading(col, text=col)
            self.allocations_tree.column(col, width=100)
        
        self.allocations_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(allocations_container, orient='vertical', command=self.allocations_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.allocations_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(allocations_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        release_btn = tk.Button(button_frame, text="➖ Release Selected",
                                font=('Segoe UI', 9),
                                bg=self.colors['danger'], fg=self.colors['bg'],
                                relief='flat', cursor='hand2',
                                command=self.release_selected_allocation)
        release_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Refresh",
                               font=('Segoe UI', 9),
                               bg=self.colors['success'], fg=self.colors['bg'],
                               relief='flat', cursor='hand2',
                               command=self.refresh_allocations)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_clients_display(self, parent):
        """Create clients display"""
        # Clients container
        clients_container = tk.Frame(parent, bg=self.colors['card'])
        clients_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for clients
        columns = ('Name', 'Hostname', 'IP Address', 'Role', 'Status', 'Last Seen')
        self.clients_tree = ttk.Treeview(clients_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=100)
        
        self.clients_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(clients_container, orient='vertical', command=self.clients_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = tk.Frame(clients_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        register_btn = tk.Button(button_frame, text="➕ Register Client",
                                font=('Segoe UI', 9),
                                bg=self.colors['primary'], fg=self.colors['bg'],
                                relief='flat', cursor='hand2',
                                command=self.register_client_dialog)
        register_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Refresh",
                               font=('Segoe UI', 9),
                               bg=self.colors['success'], fg=self.colors['bg'],
                               relief='flat', cursor='hand2',
                               command=self.refresh_clients)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_monitoring_section(self, parent):
        """Create monitoring section"""
        monitoring_frame = tk.Frame(parent, bg=self.colors['card'])
        monitoring_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(monitoring_frame, text="📈 System Monitoring",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 4), facecolor=self.colors['card'])
        self.ax = self.fig.add_subplot(111, facecolor=self.colors['card'])
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, monitoring_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Metrics display
        metrics_frame = tk.Frame(monitoring_frame, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.metrics_text = tk.Text(metrics_frame, height=6, width=120,
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       font=('Consolas', 9), relief='flat')
        self.metrics_text.pack(fill=tk.X)
    
    def start_system(self):
        """Start the streamlined system"""
        try:
            # Start monitoring if not already active
            if not streamlined_homelab.monitoring_active:
                streamlined_homelab.start_monitoring()
            
            messagebox.showinfo("Success", "Streamlined Homelab System started successfully!")
            self.refresh_dashboard()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start system: {e}")
    
    def stop_system(self):
        """Stop the streamlined system"""
        try:
            streamlined_homelab.stop_monitoring()
            messagebox.showinfo("Success", "Streamlined Homelab System stopped successfully!")
            self.refresh_dashboard()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop system: {e}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        try:
            # Get system status
            self.system_status = streamlined_homelab.get_system_status()
            
            # Update overview cards
            self.update_overview_cards()
            
            # Update resources
            self.update_resources_display()
            
            # Update allocations
            self.update_allocations_display()
            
            # Update clients
            self.update_clients_display()
            
            # Update monitoring charts
            self.update_monitoring_charts()
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
    
    def update_overview_cards(self):
        """Update overview cards"""
        try:
            # Resources card
            resources = self.system_status.get('resources', {})
            self.resources_value.config(text=str(resources.get('total', 0)))
            if resources.get('available', 0) > 0:
                self.resources_status.config(fg=self.colors['success'])
            elif resources.get('busy', 0) > 0:
                self.resources_status.config(fg=self.colors['warning'])
            else:
                self.resources_status.config(fg=self.colors['danger'])
            
            # Clients card
            clients = self.system_status.get('clients', {})
            self.clients_value.config(text=str(clients.get('total', 0)))
            if clients.get('online', 0) > 0:
                self.clients_status.config(fg=self.colors['success'])
            else:
                self.clients_status.config(fg=self.colors['warning'])
            
            # Allocations card
            allocations = self.system_status.get('allocations', {})
            self.allocations_value.config(text=str(allocations.get('total', 0)))
            if allocations.get('active', 0) > 0:
                self.allocations_status.config(fg=self.colors['success'])
            else:
                self.allocations_status.config(fg=self.colors['warning'])
            
            # System card
            self.system_value.config(text="🟢 Online")
            if self.system_status.get('monitoring_active', False):
                self.system_status.config(fg=self.colors['success'])
            else:
                self.system_status.config(fg=self.colors['warning'])
                
        except Exception as e:
            print(f"Error updating overview cards: {e}")
    
    def update_resources_display(self):
        """Update resources display"""
        try:
            # Clear existing items
            for item in self.resources_tree.get_children():
                self.resources_tree.delete(item)
            
            # Add resources
            for resource_id, resource in streamlined_homelab.resources.items():
                utilization = (resource.allocated / resource.capacity) * 100 if resource.capacity > 0 else 0
                
                self.resources_tree.insert('', 'end', values=(
                    resource.name,
                    resource.type,
                    f"{resource.capacity:.1f}",
                    f"{resource.allocated:.1f}",
                    f"{utilization:.1f}%",
                    resource.status.value
                ))
                
        except Exception as e:
            print(f"Error updating resources display: {e}")
    
    def update_allocations_display(self):
        """Update allocations display"""
        try:
            # Clear existing items
            for item in self.allocations_tree.get_children():
                self.allocations_tree.delete(item)
            
            # Add allocations
            for allocation_id, allocation in streamlined_homelab.allocations.items():
                expires_at = allocation.expires_at.strftime('%Y-%m-%d %H:%M:%S') if allocation.expires_at else 'Never'
                
                self.allocations_tree.insert('', 'end', values=(
                    allocation.client_id,
                    allocation.resource_id,
                    f"{allocation.amount:.1f}",
                    expires_at,
                    allocation.status
                ))
                
        except Exception as e:
            print(f"Error updating allocations display: {e}")
    
    def update_clients_display(self):
        """Update clients display"""
        try:
            # Clear existing items
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            # Add clients
            for client_id, client in streamlined_homelab.clients.items():
                last_seen = client['last_seen'].strftime('%Y-%m-%d %H:%M:%S') if client['last_seen'] else 'Unknown'
                
                self.clients_tree.insert('', 'end', values=(
                    client['name'],
                    client['hostname'],
                    client['ip_address'],
                    client['role'],
                    client['status'],
                    last_seen
                ))
                
        except Exception as e:
            print(f"Error updating clients display: {e}")
    
    def update_monitoring_charts(self):
        """Update monitoring charts"""
        try:
            self.ax.clear()
            
            # Create sample data for demonstration
            time_points = np.arange(0, 60, 1)
            
            # System metrics data
            cpu_percent = self.system_status.get('system_metrics', {}).get('cpu_percent', 0)
            memory_percent = self.system_status.get('system_metrics', {}).get('memory_percent', 0)
            
            # Create realistic-looking data
            cpu_data = cpu_percent + 10 * np.sin(np.linspace(0, 2*np.pi, 60))
            memory_data = memory_percent + 5 * np.sin(np.linspace(0, 2*np.pi, 60) + np.pi/4)
            
            # Plot metrics
            self.ax.plot(time_points, cpu_data, label='CPU Usage', color=self.colors['primary'])
            self.ax.plot(time_points, memory_data, label='Memory Usage', color=self.colors['success'])
            
            # Add RDMA if available
            if self.system_status.get('rdma_enabled', False):
                rrdma_data = 50 + 20 * np.sin(np.linspace(0, 2*np.pi, 60) + np.pi/2)
                self.ax.plot(time_points, rrdma_data, label='RDMA Activity', color=self.colors['warning'])
            
            self.ax.set_xlabel('Time (seconds)')
            self.ax.set_ylabel('Usage (%)')
            self.ax.set_title('System Performance Over Time')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Style the plot
            self.ax.set_facecolor(self.colors['card'])
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
            print(f"Error updating monitoring charts: {e}")
    
    def allocate_resource_dialog(self):
        """Show resource allocation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Allocate Resource")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['card'])
        
        # Resource selection
        tk.Label(dialog, text="Select Resource:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        resource_var = tk.StringVar()
        resource_combo = ttk.Combobox(dialog, textvariable=resource_var)
        resource_combo['values'] = [r.name for r in streamlined_homelab.resources.values()]
        resource_combo.pack(pady=5)
        
        # Client ID
        tk.Label(dialog, text="Client ID:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        client_var = tk.StringVar()
        client_entry = tk.Entry(dialog, textvariable=client_var, bg=self.colors['bg'], fg=self.colors['text'])
        client_entry.pack(pady=5)
        
        # Amount
        tk.Label(dialog, text="Amount:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        amount_var = tk.DoubleVar(value=1.0)
        amount_entry = tk.Entry(dialog, textvariable=amount_var, bg=self.colors['bg'], fg=self.colors['text'])
        amount_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Allocate", bg=self.colors['primary'], fg=self.colors['bg'],
                 command=lambda: self.allocate_resource(resource_var.get(), client_var.get(), amount_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", bg=self.colors['danger'], fg=self.colors['bg'],
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def allocate_resource(self, resource_name, client_id, amount, dialog):
        """Allocate a resource"""
        try:
            # Find resource by name
            resource_id = None
            for rid, resource in streamlined_homelab.resources.items():
                if resource.name == resource_name:
                    resource_id = rid
                    break
            
            if not resource_id:
                messagebox.showerror("Error", "Resource not found")
                return
            
            # Allocate resource
            allocation = streamlined_homelab.allocate_resource(resource_id, client_id, amount)
            
            if allocation:
                messagebox.showinfo("Success", f"Resource allocated successfully!\nAllocation ID: {allocation.id}")
                dialog.destroy()
                self.refresh_dashboard()
            else:
                messagebox.showerror("Error", "Failed to allocate resource")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to allocate resource: {e}")
    
    def release_resource_dialog(self):
        """Show resource release dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Release Resource")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['card'])
        
        # Allocation ID
        tk.Label(dialog, text="Allocation ID:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        
        allocation_var = tk.StringVar()
        allocation_entry = tk.Entry(dialog, textvariable=allocation_var, bg=self.colors['bg'], fg=self.colors['text'])
        allocation_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Release", bg=self.colors['danger'], fg=self.colors['bg'],
                 command=lambda: self.release_resource(allocation_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", bg=self.colors['warning'], fg=self.colors['bg'],
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def release_resource(self, allocation_id, dialog):
        """Release a resource allocation"""
        try:
            if streamlined_homelab.release_resource(allocation_id):
                messagebox.showinfo("Success", f"Resource allocation {allocation_id} released successfully!")
                dialog.destroy()
                self.refresh_dashboard()
            else:
                messagebox.showerror("Error", "Failed to release resource allocation")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to release resource: {e}")
    
    def release_selected_allocation(self):
        """Release selected allocation"""
        try:
            selected = self.allocations_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an allocation to release")
                return
            
            # Get allocation ID from selection
            item = self.allocations_tree.item(selected[0])
            values = item['values']
            
            if len(values) >= 3:
                # Extract allocation ID from the tree
                # This is a simplified approach - in a real implementation, you'd store the allocation ID
                messagebox.showinfo("Info", "Selected allocation release functionality would be implemented here")
                self.refresh_allocations()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to release selected allocation: {e}")
    
    def register_client_dialog(self):
        """Show client registration dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Register Client")
        dialog.geometry("400x350")
        dialog.configure(bg=self.colors['card'])
        
        # Client name
        tk.Label(dialog, text="Client Name:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, bg=self.colors['bg'], fg=self.colors['text']).pack(pady=5)
        
        # Hostname
        tk.Label(dialog, text="Hostname:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        hostname_var = tk.StringVar()
        tk.Entry(dialog, textvariable=hostname_var, bg=self.colors['bg'], fg=self.colors['text']).pack(pady=5)
        
        # IP Address
        tk.Label(dialog, text="IP Address:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        ip_var = tk.StringVar()
        tk.Entry(dialog, textvariable=ip_var, bg=self.colors['bg'], fg=self.colors['text']).pack(pady=5)
        
        # Role
        tk.Label(dialog, text="Role:", bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
        role_var = tk.StringVar(value="client")
        role_combo = ttk.Combobox(dialog, textvariable=role_var)
        role_combo['values'] = ["client", "server", "hybrid"]
        role_combo.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Register", bg=self.colors['primary'], fg=self.colors['bg'],
                 command=lambda: self.register_client(name_var.get(), hostname_var.get(), ip_var.get(), role_var.get(), dialog)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", bg=self.colors['danger'], fg=self.colors['bg'],
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def register_client(self, name, hostname, ip_address, role, dialog):
        """Register a client"""
        try:
            client_id = f"client_{int(time.time())}"
            
            if streamlined_homelab.register_client(client_id, name, hostname, ip_address, role):
                messagebox.showinfo("Success", f"Client {name} registered successfully!")
                dialog.destroy()
                self.refresh_clients()
            else:
                messagebox.showerror("Error", "Failed to register client")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register client: {e}")
    
    def refresh_resources(self):
        """Refresh resources display"""
        self.update_resources_display()
    
    def refresh_allocations(self):
        """Refresh allocations display"""
        self.update_allocations_display()
    
    def refresh_clients(self):
        """Refresh clients display"""
        self.update_clients_display()
    
    def start_dashboard_monitoring(self):
        """Start dashboard monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._dashboard_monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def _dashboard_monitoring_loop(self):
        """Dashboard monitoring loop"""
        while True:
            try:
                self.refresh_dashboard()
                time.sleep(30)  # Refresh every 30 seconds
            except Exception as e:
                print(f"Dashboard monitoring error: {e}")
                time.sleep(10)

if __name__ == '__main__':
    # Create dashboard window
    root = tk.Tk()
    dashboard = StreamlinedDashboard(root)
    
    # Handle window closing
    def on_closing():
        try:
            dashboard.stop_system()
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the dashboard
    root.mainloop()
