#!/usr/bin/env python3
"""
Streamlined Homelab System - Fixed Working Version
Simple homelab management dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
from datetime import datetime
import json
import os

class StreamlinedHomelabSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Streamlined Homelab System")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'success': '#00ff88',
            'text': '#ffffff',
            'text_secondary': '#cccccc'
        }
        
        # System monitoring
        self.monitoring_active = True
        self.system_stats = {}
        
        # Data file
        self.data_file = "homelab_system_data.json"
        
        # Initialize
        self.init_system()
        self.create_widgets()
        self.start_monitoring()
    
    def init_system(self):
        """Initialize system data"""
        if not os.path.exists(self.data_file):
            default_data = {
                "services": {
                    "web_server": {"status": "stopped", "port": 8080},
                    "database": {"status": "stopped", "port": 5432},
                    "file_server": {"status": "stopped", "port": 21},
                    "vpn": {"status": "stopped", "port": 1194}
                },
                "settings": {
                    "auto_start": False,
                    "backup_enabled": True,
                    "monitoring_interval": 5
                },
                "logs": []
            }
            with open(self.data_file, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="🎯 Streamlined Homelab System", 
                font=('Arial', 18, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status indicator
        self.status_indicator = tk.Label(header_frame, text="● Online", 
                                        font=('Arial', 12, 'bold'),
                                        fg=self.colors['success'], bg=self.colors['card'])
        self.status_indicator.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Main content with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.create_dashboard_tab(notebook)
        
        # Services tab
        self.create_services_tab(notebook)
        
        # System tab
        self.create_system_tab(notebook)
        
        # Logs tab
        self.create_logs_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
    
    def create_dashboard_tab(self, notebook):
        """Create dashboard tab"""
        dashboard_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # System overview
        overview_frame = tk.Frame(dashboard_frame, bg=self.colors['card'], relief='raised', bd=1)
        overview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(overview_frame, text="📊 System Overview", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Stats grid
        stats_frame = tk.Frame(overview_frame, bg=self.colors['card'])
        stats_frame.pack(pady=10)
        
        # CPU
        cpu_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        cpu_frame.grid(row=0, column=0, padx=10, pady=5)
        tk.Label(cpu_frame, text="💻 CPU", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.cpu_label = tk.Label(cpu_frame, text="0%", font=('Arial', 14, 'bold'),
                                  fg=self.colors['primary'], bg=self.colors['card'])
        self.cpu_label.pack()
        
        # Memory
        mem_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        mem_frame.grid(row=0, column=1, padx=10, pady=5)
        tk.Label(mem_frame, text="🧠 Memory", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.mem_label = tk.Label(mem_frame, text="0%", font=('Arial', 14, 'bold'),
                                  fg=self.colors['secondary'], bg=self.colors['card'])
        self.mem_label.pack()
        
        # Disk
        disk_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        disk_frame.grid(row=0, column=2, padx=10, pady=5)
        tk.Label(disk_frame, text="💾 Disk", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.disk_label = tk.Label(disk_frame, text="0%", font=('Arial', 14, 'bold'),
                                   fg=self.colors['warning'], bg=self.colors['card'])
        self.disk_label.pack()
        
        # Network
        net_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        net_frame.grid(row=0, column=3, padx=10, pady=5)
        tk.Label(net_frame, text="🌐 Network", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack()
        self.net_label = tk.Label(net_frame, text="Active", font=('Arial', 14, 'bold'),
                                  fg=self.colors['success'], bg=self.colors['card'])
        self.net_label.pack()
        
        # Quick actions
        actions_frame = tk.Frame(dashboard_frame, bg=self.colors['card'], relief='raised', bd=1)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(actions_frame, text="⚡ Quick Actions", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        actions = [
            ("🔄 Refresh System", self.refresh_system),
            ("🧹 System Cleanup", self.system_cleanup),
            ("📊 Generate Report", self.generate_report),
            ("🔧 System Settings", self.open_settings)
        ]
        
        for action_text, action_cmd in actions:
            btn = tk.Button(actions_frame, text=action_text,
                          font=('Arial', 11, 'bold'),
                          bg=self.colors['secondary'], fg='white',
                          relief='flat', cursor='hand2',
                          command=action_cmd)
            btn.pack(pady=5, padx=20, fill=tk.X)
    
    def create_services_tab(self, notebook):
        """Create services management tab"""
        services_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(services_frame, text="🔧 Services")
        
        # Services list
        services_list_frame = tk.Frame(services_frame, bg=self.colors['card'], relief='raised', bd=1)
        services_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(services_list_frame, text="🔧 Service Management", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Services display
        self.services_frame = tk.Frame(services_list_frame, bg=self.colors['card'])
        self.services_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Service actions
        service_actions_frame = tk.Frame(services_list_frame, bg=self.colors['card'])
        service_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(service_actions_frame, text="▶️ Start All",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.start_all_services).pack(side=tk.LEFT, padx=5)
        
        tk.Button(service_actions_frame, text="⏹️ Stop All",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.stop_all_services).pack(side=tk.LEFT, padx=5)
        
        tk.Button(service_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_services).pack(side=tk.LEFT, padx=5)
        
        # Load services
        self.refresh_services()
    
    def create_system_tab(self, notebook):
        """Create system information tab"""
        system_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(system_frame, text="💻 System")
        
        # System info
        info_frame = tk.Frame(system_frame, bg=self.colors['card'], relief='raised', bd=1)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(info_frame, text="💻 System Information", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # System details
        details_frame = tk.Frame(info_frame, bg=self.colors['card'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        system_info = [
            ("🖥️ Hostname", psutil.os.uname().nodename if hasattr(psutil.os, 'uname') else "Unknown"),
            ("💻 OS", f"{psutil.os.name} {psutil.os.version()}"),
            ("🔧 Architecture", "64-bit" if psutil.os.name == 'nt' else "Unknown"),
            ("⚙️ CPU Cores", str(psutil.cpu_count())),
            ("🧠 Total Memory", f"{psutil.virtual_memory().total // (1024**3)} GB"),
            ("💾 Disk Space", f"{psutil.disk_usage('/').total // (1024**3)} GB"),
            ("🕐 Boot Time", datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")),
            ("⏱️ Uptime", self.calculate_uptime())
        ]
        
        for label, value in system_info:
            info_row = tk.Frame(details_frame, bg=self.colors['card'])
            info_row.pack(fill=tk.X, pady=3)
            tk.Label(info_row, text=label + ":", font=('Arial', 11),
                    fg=self.colors['text_secondary'], bg=self.colors['card']).pack(side=tk.LEFT)
            tk.Label(info_row, text=value, font=('Arial', 11, 'bold'),
                    fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.RIGHT)
    
    def create_logs_tab(self, notebook):
        """Create logs tab"""
        logs_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(logs_frame, text="📋 Logs")
        
        # Logs display
        logs_display_frame = tk.Frame(logs_frame, bg=self.colors['card'], relief='raised', bd=1)
        logs_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(logs_display_frame, text="📋 System Logs", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Logs text widget
        self.logs_text = tk.Text(logs_display_frame, font=('Consolas', 10),
                                bg=self.colors['bg'], fg=self.colors['text'],
                                wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Logs scrollbar
        logs_scrollbar = tk.Scrollbar(self.logs_text)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.config(yscrollcommand=logs_scrollbar.set)
        logs_scrollbar.config(command=self.logs_text.yview)
        
        # Log actions
        log_actions_frame = tk.Frame(logs_display_frame, bg=self.colors['card'])
        log_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(log_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_actions_frame, text="🗑️ Clear",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        # Load initial logs
        self.refresh_logs()
    
    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings
        settings_display_frame = tk.Frame(settings_frame, bg=self.colors['card'], relief='raised', bd=1)
        settings_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(settings_display_frame, text="⚙️ System Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Settings options
        settings_options_frame = tk.Frame(settings_display_frame, bg=self.colors['card'])
        settings_options_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Auto start
        self.auto_start_var = tk.BooleanVar(value=False)
        tk.Checkbutton(settings_options_frame, text="🚀 Auto-start services on boot",
                      variable=self.auto_start_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=5)
        
        # Backup enabled
        self.backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_options_frame, text="💾 Enable automatic backups",
                      variable=self.backup_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=5)
        
        # Monitoring interval
        tk.Label(settings_options_frame, text="⏱️ Monitoring Interval (seconds):",
                font=('Arial', 11), fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w', pady=5)
        self.monitoring_interval = tk.Spinbox(settings_options_frame, from_=1, to=60, value=5,
                                             font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.monitoring_interval.pack(fill=tk.X, pady=5)
        
        # Save button
        tk.Button(settings_display_frame, text="💾 Save Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_settings).pack(pady=20)
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def monitor_system(self):
        """Monitor system statistics"""
        while self.monitoring_active:
            try:
                self.system_stats = {
                    'cpu': psutil.cpu_percent(interval=1),
                    'memory': psutil.virtual_memory().percent,
                    'disk': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                    'network': len(psutil.net_connections())
                }
                
                self.root.after(0, self.update_dashboard)
                time.sleep(5)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def update_dashboard(self):
        """Update dashboard with current stats"""
        try:
            if 'cpu' in self.system_stats:
                self.cpu_label.config(text=f"{self.system_stats['cpu']:.1f}%")
                self.mem_label.config(text=f"{self.system_stats['memory']:.1f}%")
                self.disk_label.config(text=f"{self.system_stats['disk']:.1f}%")
                
                # Update status based on system load
                if self.system_stats['cpu'] > 80 or self.system_stats['memory'] > 80:
                    self.status_indicator.config(text="● High Load", fg=self.colors['warning'])
                else:
                    self.status_indicator.config(text="● Normal", fg=self.colors['success'])
        except:
            pass
    
    def calculate_uptime(self):
        """Calculate system uptime"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    def refresh_services(self):
        """Refresh services display"""
        # Clear existing services
        for widget in self.services_frame.winfo_children():
            widget.destroy()
        
        # Load services data
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                services = data.get("services", {})
        except:
            services = {}
        
        # Display services
        for service_name, service_info in services.items():
            service_frame = tk.Frame(self.services_frame, bg=self.colors['card'], relief='raised', bd=1)
            service_frame.pack(fill=tk.X, pady=5)
            
            # Service info
            info_frame = tk.Frame(service_frame, bg=self.colors['card'])
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
            
            tk.Label(info_frame, text=f"🔧 {service_name.replace('_', ' ').title()}", 
                    font=('Arial', 11, 'bold'),
                    fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w')
            
            status_color = self.colors['success'] if service_info['status'] == 'running' else self.colors['danger']
            tk.Label(info_frame, text=f"Status: {service_info['status']} | Port: {service_info.get('port', 'N/A')}", 
                    font=('Arial', 9),
                    fg=status_color, bg=self.colors['card']).pack(anchor='w')
            
            # Service controls
            controls_frame = tk.Frame(service_frame, bg=self.colors['card'])
            controls_frame.pack(side=tk.RIGHT, padx=10, pady=10)
            
            if service_info['status'] == 'stopped':
                tk.Button(controls_frame, text="▶️",
                         font=('Arial', 10, 'bold'),
                         bg=self.colors['success'], fg='white',
                         relief='flat', cursor='hand2',
                         command=lambda s=service_name: self.start_service(s)).pack(side=tk.LEFT, padx=2)
            else:
                tk.Button(controls_frame, text="⏹️",
                         font=('Arial', 10, 'bold'),
                         bg=self.colors['danger'], fg='white',
                         relief='flat', cursor='hand2',
                         command=lambda s=service_name: self.stop_service(s)).pack(side=tk.LEFT, padx=2)
    
    def start_service(self, service_name):
        """Start a service"""
        self.add_log(f"Starting service: {service_name}")
        # Update service status
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            data["services"][service_name]["status"] = "running"
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.refresh_services()
            self.add_log(f"Service {service_name} started successfully")
        except Exception as e:
            self.add_log(f"Failed to start service {service_name}: {e}")
    
    def stop_service(self, service_name):
        """Stop a service"""
        self.add_log(f"Stopping service: {service_name}")
        # Update service status
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            data["services"][service_name]["status"] = "stopped"
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.refresh_services()
            self.add_log(f"Service {service_name} stopped successfully")
        except Exception as e:
            self.add_log(f"Failed to stop service {service_name}: {e}")
    
    def start_all_services(self):
        """Start all services"""
        self.add_log("Starting all services...")
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            for service_name in data["services"]:
                data["services"][service_name]["status"] = "running"
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.refresh_services()
            self.add_log("All services started successfully")
        except Exception as e:
            self.add_log(f"Failed to start all services: {e}")
    
    def stop_all_services(self):
        """Stop all services"""
        self.add_log("Stopping all services...")
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            for service_name in data["services"]:
                data["services"][service_name]["status"] = "stopped"
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.refresh_services()
            self.add_log("All services stopped successfully")
        except Exception as e:
            self.add_log(f"Failed to stop all services: {e}")
    
    def refresh_system(self):
        """Refresh system information"""
        self.add_log("System information refreshed")
        messagebox.showinfo("System Refresh", "System information has been refreshed!")
    
    def system_cleanup(self):
        """Perform system cleanup"""
        self.add_log("Performing system cleanup...")
        # Simulate cleanup
        import time
        time.sleep(2)
        self.add_log("System cleanup completed")
        messagebox.showinfo("System Cleanup", "System cleanup completed successfully!")
    
    def generate_report(self):
        """Generate system report"""
        self.add_log("Generating system report...")
        report = f"""
System Report - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

CPU Usage: {self.system_stats.get('cpu', 'N/A')}%
Memory Usage: {self.system_stats.get('memory', 'N/A')}%
Disk Usage: {self.system_stats.get('disk', 'N/A')}%
Network Connections: {self.system_stats.get('network', 'N/A')}

System Status: {'High Load' if self.system_stats.get('cpu', 0) > 80 else 'Normal'}
"""
        self.add_log("System report generated")
        messagebox.showinfo("System Report", report)
    
    def open_settings(self):
        """Open settings"""
        messagebox.showinfo("Settings", "Settings functionality would be implemented here!")
    
    def refresh_logs(self):
        """Refresh logs display"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                logs = data.get("logs", [])
            
            self.logs_text.delete(1.0, tk.END)
            for log in logs[-50:]:  # Show last 50 logs
                self.logs_text.insert(tk.END, f"{log}\n")
            
            self.logs_text.see(tk.END)
        except:
            self.logs_text.delete(1.0, tk.END)
            self.logs_text.insert(tk.END, "No logs available")
    
    def clear_logs(self):
        """Clear logs"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            data["logs"] = []
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.refresh_logs()
            self.add_log("Logs cleared")
        except:
            pass
    
    def add_log(self, message):
        """Add a log entry"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
            data["logs"].append(log_entry)
            
            # Keep only last 1000 logs
            if len(data["logs"]) > 1000:
                data["logs"] = data["logs"][-1000:]
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def save_settings(self):
        """Save settings"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            data["settings"] = {
                "auto_start": self.auto_start_var.get(),
                "backup_enabled": self.backup_var.get(),
                "monitoring_interval": int(self.monitoring_interval.get())
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.add_log("Settings saved successfully")
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = StreamlinedHomelabSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
