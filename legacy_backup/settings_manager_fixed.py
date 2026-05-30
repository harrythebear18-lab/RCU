#!/usr/bin/env python3
"""
Settings Manager - Fixed Working Version
Simple system settings management tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
from datetime import datetime

class SettingsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ Settings Manager")
        self.root.geometry("700x600")
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
        
        # Data file
        self.data_file = "settings_manager_data.json"
        
        # Initialize
        self.init_settings()
        self.create_widgets()
        self.load_settings()
    
    def init_settings(self):
        """Initialize settings data"""
        if not os.path.exists(self.data_file):
            default_settings = {
                "system": {
                    "theme": "dark",
                    "language": "en",
                    "auto_start": False,
                    "notifications": True
                },
                "performance": {
                    "cpu_priority": "normal",
                    "memory_limit": "unlimited",
                    "disk_cleanup": True,
                    "temp_cleanup_days": 7
                },
                "security": {
                    "auto_lock": False,
                    "session_timeout": 3600,
                    "password_policy": "medium",
                    "audit_logging": True
                },
                "network": {
                    "auto_connect": False,
                    "firewall_enabled": True,
                    "proxy_enabled": False,
                    "dns_servers": ["8.8.8.8", "8.8.4.4"]
                },
                "backup": {
                    "auto_backup": False,
                    "backup_interval": "daily",
                    "backup_location": "./backups",
                    "compression": True
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(default_settings, f, indent=2)
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="⚙️ Settings Manager", 
                font=('Arial', 18, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status
        self.status_label = tk.Label(header_frame, text="● Settings loaded", 
                                     font=('Arial', 12, 'bold'),
                                     fg=self.colors['success'], bg=self.colors['card'])
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Main content with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_system_tab(notebook)
        self.create_performance_tab(notebook)
        self.create_security_tab(notebook)
        self.create_network_tab(notebook)
        self.create_backup_tab(notebook)
        
        # Action buttons
        action_frame = tk.Frame(self.root, bg=self.colors['bg'])
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(action_frame, text="💾 Save Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_settings).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(action_frame, text="🔄 Reset to Defaults",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.reset_settings).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(action_frame, text="📁 Export Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.export_settings).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(action_frame, text="📁 Import Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['info'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.import_settings).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_system_tab(self, notebook):
        """Create system settings tab"""
        system_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(system_frame, text="💻 System")
        
        # System settings
        system_settings_frame = tk.Frame(system_frame, bg=self.colors['card'], relief='raised', bd=1)
        system_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(system_settings_frame, text="💻 System Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Theme
        theme_frame = tk.Frame(system_settings_frame, bg=self.colors['card'])
        theme_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(theme_frame, text="🎨 Theme:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.theme_var = tk.StringVar(value="dark")
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                   values=["dark", "light", "auto"], state="readonly")
        theme_combo.pack(side=tk.RIGHT, padx=5)
        
        # Language
        lang_frame = tk.Frame(system_settings_frame, bg=self.colors['card'])
        lang_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(lang_frame, text="🌐 Language:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.language_var = tk.StringVar(value="en")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                  values=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"], state="readonly")
        lang_combo.pack(side=tk.RIGHT, padx=5)
        
        # Auto start
        self.auto_start_var = tk.BooleanVar(value=False)
        tk.Checkbutton(system_settings_frame, text="🚀 Auto-start with system",
                      variable=self.auto_start_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Notifications
        self.notifications_var = tk.BooleanVar(value=True)
        tk.Checkbutton(system_settings_frame, text="🔔 Enable notifications",
                      variable=self.notifications_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
    
    def create_performance_tab(self, notebook):
        """Create performance settings tab"""
        performance_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(performance_frame, text="⚡ Performance")
        
        # Performance settings
        perf_settings_frame = tk.Frame(performance_frame, bg=self.colors['card'], relief='raised', bd=1)
        perf_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(perf_settings_frame, text="⚡ Performance Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # CPU Priority
        cpu_frame = tk.Frame(perf_settings_frame, bg=self.colors['card'])
        cpu_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(cpu_frame, text="💻 CPU Priority:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.cpu_priority_var = tk.StringVar(value="normal")
        cpu_combo = ttk.Combobox(cpu_frame, textvariable=self.cpu_priority_var,
                                 values=["low", "normal", "high", "realtime"], state="readonly")
        cpu_combo.pack(side=tk.RIGHT, padx=5)
        
        # Memory limit
        mem_frame = tk.Frame(perf_settings_frame, bg=self.colors['card'])
        mem_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(mem_frame, text="🧠 Memory Limit:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.memory_limit_var = tk.StringVar(value="unlimited")
        mem_combo = ttk.Combobox(mem_frame, textvariable=self.memory_limit_var,
                                 values=["unlimited", "1GB", "2GB", "4GB", "8GB", "16GB"], state="readonly")
        mem_combo.pack(side=tk.RIGHT, padx=5)
        
        # Disk cleanup
        self.disk_cleanup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(perf_settings_frame, text="🧹 Enable automatic disk cleanup",
                      variable=self.disk_cleanup_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Temp cleanup days
        temp_frame = tk.Frame(perf_settings_frame, bg=self.colors['card'])
        temp_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(temp_frame, text="🗑️ Temp file cleanup (days):", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.temp_cleanup_days_var = tk.IntVar(value=7)
        temp_spinbox = tk.Spinbox(temp_frame, from_=1, to=365, textvariable=self.temp_cleanup_days_var,
                                  font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        temp_spinbox.pack(side=tk.RIGHT, padx=5)
    
    def create_security_tab(self, notebook):
        """Create security settings tab"""
        security_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(security_frame, text="🔐 Security")
        
        # Security settings
        security_settings_frame = tk.Frame(security_frame, bg=self.colors['card'], relief='raised', bd=1)
        security_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(security_settings_frame, text="🔐 Security Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Auto lock
        self.auto_lock_var = tk.BooleanVar(value=False)
        tk.Checkbutton(security_settings_frame, text="🔒 Auto-lock after inactivity",
                      variable=self.auto_lock_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Session timeout
        timeout_frame = tk.Frame(security_settings_frame, bg=self.colors['card'])
        timeout_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(timeout_frame, text="⏱️ Session timeout (minutes):", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.session_timeout_var = tk.IntVar(value=60)
        timeout_spinbox = tk.Spinbox(timeout_frame, from_=5, to=480, textvariable=self.session_timeout_var,
                                     font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        timeout_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Password policy
        policy_frame = tk.Frame(security_settings_frame, bg=self.colors['card'])
        policy_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(policy_frame, text="🔑 Password policy:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.password_policy_var = tk.StringVar(value="medium")
        policy_combo = ttk.Combobox(policy_frame, textvariable=self.password_policy_var,
                                    values=["low", "medium", "high", "maximum"], state="readonly")
        policy_combo.pack(side=tk.RIGHT, padx=5)
        
        # Audit logging
        self.audit_logging_var = tk.BooleanVar(value=True)
        tk.Checkbutton(security_settings_frame, text="📋 Enable audit logging",
                      variable=self.audit_logging_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
    
    def create_network_tab(self, notebook):
        """Create network settings tab"""
        network_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(network_frame, text="🌐 Network")
        
        # Network settings
        network_settings_frame = tk.Frame(network_frame, bg=self.colors['card'], relief='raised', bd=1)
        network_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(network_settings_frame, text="🌐 Network Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Auto connect
        self.auto_connect_var = tk.BooleanVar(value=False)
        tk.Checkbutton(network_settings_frame, text="🔗 Auto-connect to networks",
                      variable=self.auto_connect_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Firewall
        self.firewall_var = tk.BooleanVar(value=True)
        tk.Checkbutton(network_settings_frame, text="🛡️ Enable firewall",
                      variable=self.firewall_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Proxy
        self.proxy_var = tk.BooleanVar(value=False)
        tk.Checkbutton(network_settings_frame, text="🌐 Enable proxy",
                      variable=self.proxy_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # DNS servers
        dns_frame = tk.Frame(network_settings_frame, bg=self.colors['card'])
        dns_frame.pack(fill=tk.X, pady=10, padx=20)
        tk.Label(dns_frame, text="🔧 DNS Servers:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w')
        
        self.dns1_var = tk.StringVar(value="8.8.8.8")
        self.dns2_var = tk.StringVar(value="8.8.4.4")
        
        dns1_entry = tk.Entry(dns_frame, textvariable=self.dns1_var,
                              font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        dns1_entry.pack(fill=tk.X, pady=2)
        
        dns2_entry = tk.Entry(dns_frame, textvariable=self.dns2_var,
                              font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        dns2_entry.pack(fill=tk.X, pady=2)
    
    def create_backup_tab(self, notebook):
        """Create backup settings tab"""
        backup_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(backup_frame, text="💾 Backup")
        
        # Backup settings
        backup_settings_frame = tk.Frame(backup_frame, bg=self.colors['card'], relief='raised', bd=1)
        backup_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(backup_settings_frame, text="💾 Backup Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Auto backup
        self.auto_backup_var = tk.BooleanVar(value=False)
        tk.Checkbutton(backup_settings_frame, text="🔄 Enable automatic backup",
                      variable=self.auto_backup_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Backup interval
        interval_frame = tk.Frame(backup_settings_frame, bg=self.colors['card'])
        interval_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(interval_frame, text="⏰ Backup interval:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.backup_interval_var = tk.StringVar(value="daily")
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.backup_interval_var,
                                      values=["hourly", "daily", "weekly", "monthly"], state="readonly")
        interval_combo.pack(side=tk.RIGHT, padx=5)
        
        # Backup location
        backup_loc_frame = tk.Frame(backup_settings_frame, bg=self.colors['card'])
        backup_loc_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(backup_loc_frame, text="📁 Backup location:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w')
        
        self.backup_location_var = tk.StringVar(value="./backups")
        backup_loc_entry = tk.Entry(backup_loc_frame, textvariable=self.backup_location_var,
                                    font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        backup_loc_entry.pack(fill=tk.X, pady=2)
        
        # Compression
        self.compression_var = tk.BooleanVar(value=True)
        tk.Checkbutton(backup_settings_frame, text="🗜️ Enable compression",
                      variable=self.compression_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            with open(self.data_file, 'r') as f:
                self.settings_data = json.load(f)
            
            # Load system settings
            system = self.settings_data.get("system", {})
            self.theme_var.set(system.get("theme", "dark"))
            self.language_var.set(system.get("language", "en"))
            self.auto_start_var.set(system.get("auto_start", False))
            self.notifications_var.set(system.get("notifications", True))
            
            # Load performance settings
            performance = self.settings_data.get("performance", {})
            self.cpu_priority_var.set(performance.get("cpu_priority", "normal"))
            self.memory_limit_var.set(performance.get("memory_limit", "unlimited"))
            self.disk_cleanup_var.set(performance.get("disk_cleanup", True))
            self.temp_cleanup_days_var.set(performance.get("temp_cleanup_days", 7))
            
            # Load security settings
            security = self.settings_data.get("security", {})
            self.auto_lock_var.set(security.get("auto_lock", False))
            self.session_timeout_var.set(security.get("session_timeout", 3600) // 60)
            self.password_policy_var.set(security.get("password_policy", "medium"))
            self.audit_logging_var.set(security.get("audit_logging", True))
            
            # Load network settings
            network = self.settings_data.get("network", {})
            self.auto_connect_var.set(network.get("auto_connect", False))
            self.firewall_var.set(network.get("firewall_enabled", True))
            self.proxy_var.set(network.get("proxy_enabled", False))
            dns_servers = network.get("dns_servers", ["8.8.8.8", "8.8.4.4"])
            if len(dns_servers) >= 2:
                self.dns1_var.set(dns_servers[0])
                self.dns2_var.set(dns_servers[1])
            
            # Load backup settings
            backup = self.settings_data.get("backup", {})
            self.auto_backup_var.set(backup.get("auto_backup", False))
            self.backup_interval_var.set(backup.get("backup_interval", "daily"))
            self.backup_location_var.set(backup.get("backup_location", "./backups"))
            self.compression_var.set(backup.get("compression", True))
            
            self.status_label.config(text="● Settings loaded", fg=self.colors['success'])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
            self.status_label.config(text="● Load failed", fg=self.colors['danger'])
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                "system": {
                    "theme": self.theme_var.get(),
                    "language": self.language_var.get(),
                    "auto_start": self.auto_start_var.get(),
                    "notifications": self.notifications_var.get()
                },
                "performance": {
                    "cpu_priority": self.cpu_priority_var.get(),
                    "memory_limit": self.memory_limit_var.get(),
                    "disk_cleanup": self.disk_cleanup_var.get(),
                    "temp_cleanup_days": self.temp_cleanup_days_var.get()
                },
                "security": {
                    "auto_lock": self.auto_lock_var.get(),
                    "session_timeout": self.session_timeout_var.get() * 60,
                    "password_policy": self.password_policy_var.get(),
                    "audit_logging": self.audit_logging_var.get()
                },
                "network": {
                    "auto_connect": self.auto_connect_var.get(),
                    "firewall_enabled": self.firewall_var.get(),
                    "proxy_enabled": self.proxy_var.get(),
                    "dns_servers": [self.dns1_var.get(), self.dns2_var.get()]
                },
                "backup": {
                    "auto_backup": self.auto_backup_var.get(),
                    "backup_interval": self.backup_interval_var.get(),
                    "backup_location": self.backup_location_var.get(),
                    "compression": self.compression_var.get()
                },
                "last_modified": datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.status_label.config(text="● Settings saved", fg=self.colors['success'])
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.status_label.config(text="● Save failed", fg=self.colors['danger'])
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Confirm Reset", "Reset all settings to default values?"):
            try:
                # Remove settings file to force recreation
                if os.path.exists(self.data_file):
                    os.remove(self.data_file)
                
                # Reinitialize
                self.init_settings()
                self.load_settings()
                
                self.status_label.config(text="● Settings reset", fg=self.colors['warning'])
                messagebox.showinfo("Success", "Settings reset to defaults!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def export_settings(self):
        """Export settings to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(self.data_file, 'r') as f:
                    settings = json.load(f)
                
                with open(filename, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                messagebox.showinfo("Success", f"Settings exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def import_settings(self):
        """Import settings from file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    settings = json.load(f)
                
                with open(self.data_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                self.load_settings()
                messagebox.showinfo("Success", f"Settings imported from {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings: {e}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = SettingsManager(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting settings manager: {e}")

if __name__ == "__main__":
    main()
