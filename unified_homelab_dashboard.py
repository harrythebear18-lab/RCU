#!/usr/bin/env python3
"""
Unified Homelab Dashboard
Integrates Homelab Tools, RDMA, and Resource Optimization into a single interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Import unified system
from unified_homelab_integration import unified_homelab

# Import from all three projects
current_dir = Path(__file__).parent
homelab_tools_path = Path("C:/Users/htsou/Desktop/Homelab Tools")
rdma_path = Path("C:/Users/htsou/Desktop/RDMA")
ram_clean_path = Path("C:/Users/htsou/Desktop/Ram clean up")

sys.path.insert(0, str(homelab_tools_path))
sys.path.insert(0, str(rdma_path))
sys.path.insert(0, str(ram_clean_path))

try:
    from homelab_launcher import HomelabLauncher
    from Auto_RAM_Connect import AutoRAMConnect
    from resource_optimizer import ResourceOptimizer
except ImportError:
    pass

class UnifiedHomelabDashboard:
    """Unified dashboard for all homelab components"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("[HOME] Unified Homelab Dashboard")
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
        
        # Component status
        self.component_status = {
            'homelab_tools': {'status': 'unknown', 'details': {}},
            'rdma': {'status': 'unknown', 'details': {}},
            'resource_optimizer': {'status': 'unknown', 'details': {}}
        }
        
        # Monitoring data
        self.monitoring_data = {
            'resource_utilization': {},
            'performance_metrics': {},
            'integration_events': []
        }
        
        # Create UI
        self.create_ui()
        
        # Start monitoring
        self.start_monitoring()
    
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
        
        # Create three main sections
        self.create_component_status(content_frame)
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
        
        title_label = tk.Label(title_frame, text="[HOME] Unified Homelab Dashboard",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        self.overall_status_label = tk.Label(title_frame, text="[REFRESH] Initializing...",
                                            font=('Segoe UI', 10),
                                            fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.overall_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg=self.colors['card'])
        control_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start All",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=self.colors['success'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.start_all_components)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop All",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['danger'], fg=self.colors['bg'],
                                 relief='flat', cursor='hand2',
                                 command=self.stop_all_components)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(control_frame, text="[REFRESH] Refresh",
                                   font=('Segoe UI', 10, 'bold'),
                                   bg=self.colors['primary'], fg=self.colors['bg'],
                                   relief='flat', cursor='hand2',
                                   command=self.refresh_status)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_component_status(self, parent):
        """Create component status section"""
        # Component status frame
        status_frame = tk.Frame(parent, bg=self.colors['card'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(status_frame, text="[TOOL] Component Status",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Component cards container
        cards_container = tk.Frame(status_frame, bg=self.colors['card'])
        cards_container.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Create three component cards
        self.create_component_card(cards_container, "Homelab Tools", "homelab_tools", 0)
        self.create_component_card(cards_container, "RDMA System", "rdma", 1)
        self.create_component_card(cards_container, "Resource Optimizer", "resource_optimizer", 2)
    
    def create_component_card(self, parent, title, component_id, column):
        """Create individual component card"""
        card = tk.Frame(parent, bg=self.colors['card'], relief='flat', bd=1)
        card.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Component header
        header_frame = tk.Frame(card, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        name_label = tk.Label(header_frame, text=title,
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        name_label.pack(side=tk.LEFT)
        
        # Status indicator
        status_frame = tk.Frame(header_frame, bg=self.colors['card'])
        status_frame.pack(side=tk.RIGHT)
        
        status_label = tk.Label(status_frame, text="●",
                                font=('Segoe UI', 16, 'bold'),
                                fg=self.colors['warning'], bg=self.colors['card'])
        status_label.pack()
        
        # Component details
        details_frame = tk.Frame(card, bg=self.colors['card'])
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        details_text = tk.Text(details_frame, height=4, width=30,
                               bg=self.colors['bg'], fg=self.colors['text'],
                               font=('Consolas', 8), relief='flat')
        details_text.pack(fill=tk.X)
        
        # Control buttons
        button_frame = tk.Frame(card, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        start_comp_btn = tk.Button(button_frame, text="▶️ Start",
                                    font=('Segoe UI', 9),
                                    bg=self.colors['success'], fg=self.colors['bg'],
                                    relief='flat', cursor='hand2')
        start_comp_btn.pack(side=tk.LEFT, padx=2)
        
        stop_comp_btn = tk.Button(button_frame, text="⏹️ Stop",
                                   font=('Segoe UI', 9),
                                   bg=self.colors['danger'], fg=self.colors['bg'],
                                   relief='flat', cursor='hand2')
        stop_comp_btn.pack(side=tk.LEFT, padx=2)
        
        config_btn = tk.Button(button_frame, text="[SETTINGS] Config",
                                 font=('Segoe UI', 9),
                                 bg=self.colors['primary'], fg=self.colors['bg'],
                                 relief='flat', cursor='hand2')
        config_btn.pack(side=tk.LEFT, padx=2)
        
        # Store references
        setattr(self, f"{component_id}_card", card)
        setattr(self, f"{component_id}_status", status_label)
        setattr(self, f"{component_id}_details", details_text)
    
    def create_resource_management(self, parent):
        """Create resource management section"""
        # Resource management frame
        resource_frame = tk.Frame(parent, bg=self.colors['card'])
        resource_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Title
        title_label = tk.Label(resource_frame, text="[CHART] Resource Management",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(resource_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Resource pools tab
        pools_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(pools_frame, text="Resource Pools")
        
        # Create resource pool display
        self.create_resource_pools(pools_frame)
        
        # Allocations tab
        allocations_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(allocations_frame, text="Active Allocations")
        
        # Create allocations display
        self.create_allocations_display(allocations_frame)
        
        # Cross-project integration tab
        integration_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(integration_frame, text="Integration")
        
        # Create integration display
        self.create_integration_display(integration_frame)
    
    def create_resource_pools(self, parent):
        """Create resource pools display"""
        # Pools container
        pools_container = tk.Frame(parent, bg=self.colors['card'])
        pools_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for resource pools
        columns = ('Pool Name', 'Type', 'Capacity', 'Allocated', 'Utilization', 'Source')
        self.pools_tree = ttk.Treeview(pools_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.pools_tree.heading(col, text=col)
            self.pools_tree.column(col, width=120)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        self.pools_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(pools_container, orient='vertical', command=self.pools_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pools_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_allocations_display(self, parent):
        """Create allocations display"""
        # Allocations container
        allocations_container = tk.Frame(parent, bg=self.colors['card'])
        allocations_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for allocations
        columns = ('Client', 'Resource', 'Amount', 'Expires', 'Status', 'Source')
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
        
        allocate_btn = tk.Button(button_frame, text=" Allocate Resource",
                                 font=('Segoe UI', 9),
                                 bg=self.colors['primary'], fg=self.colors['bg'],
                                 relief='flat', cursor='hand2')
        allocate_btn.pack(side=tk.LEFT, padx=5)
        
        release_btn = tk.Button(button_frame, text=" Release Resource",
                                font=('Segoe UI', 9),
                                bg=self.colors['warning'], fg=self.colors['bg'],
                                relief='flat', cursor='hand2')
        release_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(button_frame, text="[REFRESH] Refresh",
                               font=('Segoe UI', 9),
                               bg=self.colors['success'], fg=self.colors['bg'],
                               relief='flat', cursor='hand2',
                               command=self.refresh_allocations)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_integration_display(self, parent):
        """Create integration display"""
        # Integration container
        integration_container = tk.Frame(parent, bg=self.colors['card'])
        integration_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text display for integration events
        self.integration_text = scrolledtext.ScrolledText(
            integration_container, height=15, width=80,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.integration_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        button_frame = tk.Frame(integration_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        test_btn = tk.Button(button_frame, text="[TEST] Test Integration",
                            font=('Segoe UI', 9),
                            bg=self.colors['primary'], fg=self.colors['bg'],
                            relief='flat', cursor='hand2',
                            command=self.test_integration)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear Events",
                             font=('Segoe UI', 9),
                             bg=self.colors['warning'], fg=self.colors['bg'],
                             relief='flat', cursor='hand2',
                             command=self.clear_events)
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def create_monitoring_section(self, parent):
        """Create monitoring section"""
        # Monitoring frame
        monitoring_frame = tk.Frame(parent, bg=self.colors['card'])
        monitoring_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(monitoring_frame, text="[UP] System Monitoring",
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
    
    def start_all_components(self):
        """Start all homelab components"""
        try:
            self.overall_status_label.config(text="[REFRESH] Starting components...")
            
            # Start unified system
            if unified_homelab.start_all_components():
                self.overall_status_label.config(text="[OK] All components started")
                self.refresh_status()
                messagebox.showinfo("Success", "All homelab components started successfully!")
            else:
                self.overall_status_label.config(text="[ERROR] Failed to start components")
                messagebox.showerror("Error", "Failed to start some components")
                
        except Exception as e:
            self.overall_status_label.config(text="[ERROR] Error starting components")
            messagebox.showerror("Error", f"Failed to start components: {e}")
    
    def stop_all_components(self):
        """Stop all homelab components"""
        try:
            self.overall_status_label.config(text="[REFRESH] Stopping components...")
            
            # Stop unified system
            unified_homelab.stop_all_components()
            
            self.overall_status_label.config(text="⏹️ All components stopped")
            self.refresh_status()
            messagebox.showinfo("Success", "All homelab components stopped successfully!")
            
        except Exception as e:
            self.overall_status_label.config(text="[ERROR] Error stopping components")
            messagebox.showerror("Error", f"Failed to stop components: {e}")
    
    def refresh_status(self):
        """Refresh component status"""
        try:
            # Get unified status
            status = unified_homelab.get_unified_status()
            
            # Update component status
            for name, comp_status in status['components'].items():
                if hasattr(self, f"{name}_status"):
                    status_label = getattr(self, f"{name}_status")
                    if comp_status['available']:
                        if comp_status['status'] == 'running':
                            status_label.config(fg=self.colors['success'])
                        elif comp_status['status'] == 'ready':
                            status_label.config(fg=self.colors['warning'])
                        else:
                            status_label.config(fg=self.colors['danger'])
                    else:
                        status_label.config(fg=self.colors['text_secondary'])
                
                if hasattr(self, f"{name}_details"):
                    details_text = getattr(self, f"{name}_details")
                    details_text.delete(1.0, tk.END)
                    details_text.insert(1.0, f"Status: {comp_status['status']}\n")
                    details_text.insert(tk.END, f"Available: {comp_status['available']}\n")
                    details_text.insert(tk.END, f"Timestamp: {status['timestamp']}\n")
            
            # Update overall status
            running_count = len([c for c in status['components'].values() 
                                if c['available'] and c['status'] in ['running', 'ready']])
            total_count = len(status['components'])
            
            if running_count == total_count:
                self.overall_status_label.config(text=f"[OK] All {total_count} components running")
            elif running_count > 0:
                self.overall_status_label.config(text=f"[WARNING] {running_count}/{total_count} components running")
            else:
                self.overall_status_label.config(text=f"[ERROR] No components running")
            
            # Update resource pools
            self.update_resource_pools()
            
            # Update allocations
            self.update_allocations()
            
            # Update integration events
            self.update_integration_events()
            
            # Update monitoring charts
            self.update_monitoring_charts()
            
        except Exception as e:
            print(f"Error refreshing status: {e}")
    
    def update_resource_pools(self):
        """Update resource pools display"""
        try:
            # Clear existing items
            for item in self.pools_tree.get_children():
                self.pools_tree.delete(item)
            
            # Add resource pools
            for pool_id, pool in unified_homelab.resource_pools.items():
                allocated = sum(a['amount'] for a in unified_homelab.active_allocations.values() 
                               if a['resource_id'] == pool_id)
                utilization = (allocated / pool['capacity']) * 100 if pool['capacity'] > 0 else 0
                
                self.pools_tree.insert('', 'end', values=(
                    pool['name'],
                    pool['type'],
                    f"{pool['capacity']:.1f}",
                    f"{allocated:.1f}",
                    f"{utilization:.1f}%",
                    pool['source_project']
                ))
                
        except Exception as e:
            print(f"Error updating resource pools: {e}")
    
    def update_allocations(self):
        """Update allocations display"""
        try:
            # Clear existing items
            for item in self.allocations_tree.get_children():
                self.allocations_tree.delete(item)
            
            # Add active allocations
            for alloc_id, allocation in unified_homelab.active_allocations.items():
                self.allocations_tree.insert('', 'end', values=(
                    allocation['client_id'],
                    allocation['resource_id'],
                    f"{allocation['amount']:.1f}",
                    allocation['expires_at'][:19],  # Show only date/time
                    allocation['status'],
                    allocation['source_project']
                ))
                
        except Exception as e:
            print(f"Error updating allocations: {e}")
    
    def update_integration_events(self):
        """Update integration events display"""
        try:
            self.integration_text.delete(1.0, tk.END)
            
            # Add recent integration events
            events = [
                f"[{datetime.now().strftime('%H:%M:%S')}] [REFRESH] Unified system monitoring active\n",
                f"[{datetime.now().strftime('%H:%M:%S')}] [CHART] Resource pools: {len(unified_homelab.resource_pools)}\n",
                f"[{datetime.now().strftime('%H:%M:%S')}] [LINK] Active allocations: {len(unified_homelab.active_allocations)}\n",
                f"[{datetime.now().strftime('%H:%M:%S')}] [HOME] Connected clients: {len(unified_homelab.connected_clients)}\n"
            ]
            
            for event in events:
                self.integration_text.insert(tk.END, event)
            
            self.integration_text.see(tk.END)
            
        except Exception as e:
            print(f"Error updating integration events: {e}")
    
    def update_monitoring_charts(self):
        """Update monitoring charts"""
        try:
            self.ax.clear()
            
            # Create sample data for demonstration
            time_points = np.arange(0, 60, 1)
            
            # Resource utilization data
            ram_utilization = 50 + 20 * np.sin(np.linspace(0, 2*np.pi, 60))
            cpu_utilization = 40 + 30 * np.sin(np.linspace(0, 2*np.pi, 60) + np.pi/4)
            gpu_utilization = 30 + 25 * np.sin(np.linspace(0, 2*np.pi, 60) + np.pi/2)
            
            # Plot utilization
            self.ax.plot(time_points, ram_utilization, label='RAM Utilization', color=self.colors['primary'])
            self.ax.plot(time_points, cpu_utilization, label='CPU Utilization', color=self.colors['success'])
            self.ax.plot(time_points, gpu_utilization, label='GPU Utilization', color=self.colors['warning'])
            
            self.ax.set_xlabel('Time (seconds)')
            self.ax.set_ylabel('Utilization (%)')
            self.ax.set_title('Resource Utilization Over Time')
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
    
    def refresh_allocations(self):
        """Refresh allocations display"""
        self.update_allocations()
    
    def test_integration(self):
        """Test integration between components"""
        try:
            # Test resource allocation
            allocation = unified_homelab.allocate_unified_resource(
                'unified_ram_low_latency',
                'test_client',
                1.0,
                {'test': True}
            )
            
            if allocation:
                messagebox.showinfo("Integration Test", 
                                  f"[OK] Resource allocation successful!\n"
                                  f"Allocation ID: {allocation['allocation_id']}\n"
                                  f"Resource: {allocation['resource_id']}\n"
                                  f"Amount: {allocation['amount']}")
                
                # Release the test allocation
                unified_homelab.release_unified_resource(allocation['allocation_id'])
                
                # Update displays
                self.refresh_status()
            else:
                messagebox.showwarning("Integration Test", "[ERROR] Resource allocation failed")
                
        except Exception as e:
            messagebox.showerror("Integration Test", f"[ERROR] Integration test failed: {e}")
    
    def clear_events(self):
        """Clear integration events display"""
        self.integration_text.delete(1.0, tk.END)
        self.integration_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Events cleared\n")
    
    def start_monitoring(self):
        """Start dashboard monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitoring_loop(self):
        """Dashboard monitoring loop"""
        while True:
            try:
                self.refresh_status()
                time.sleep(30)  # Refresh every 30 seconds
            except Exception as e:
                print(f"Dashboard monitoring error: {e}")
                time.sleep(10)

if __name__ == '__main__':
    # Create dashboard window
    root = tk.Tk()
    dashboard = UnifiedHomelabDashboard(root)
    
    # Handle window closing
    def on_closing():
        try:
            dashboard.stop_all_components()
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the dashboard
    root.mainloop()
