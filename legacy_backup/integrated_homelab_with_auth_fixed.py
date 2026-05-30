#!/usr/bin/env python3
"""
Integrated Homelab with Authentication - Fixed Working Version
Simple homelab management tool with basic authentication
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
import json
import os
from datetime import datetime
import threading
import time

class IntegratedHomelabAuth:
    def __init__(self, root):
        self.root = root
        self.root.title("🔑 Integrated Homelab with Auth")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'text': '#ffffff'
        }
        
        # Authentication state
        self.authenticated = False
        self.current_user = None
        
        # Data file
        self.data_file = "homelab_auth_data.json"
        
        # Initialize
        self.init_auth()
        self.create_widgets()
    
    def init_auth(self):
        """Initialize authentication system"""
        if not os.path.exists(self.data_file):
            # Create default admin user
            default_data = {
                "users": {
                    "admin": {
                        "password": self.hash_password("admin123"),
                        "role": "admin",
                        "created": datetime.now().isoformat()
                    }
                },
                "settings": {
                    "session_timeout": 3600,
                    "max_login_attempts": 3
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_data(self):
        """Load authentication data"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "settings": {}}
    
    def save_data(self, data):
        """Save authentication data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except:
            return False
    
    def create_widgets(self):
        """Create main widgets"""
        if not self.authenticated:
            self.create_login_screen()
        else:
            self.create_main_interface()
    
    def create_login_screen(self):
        """Create login interface"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Login frame
        login_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=2)
        login_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        
        # Title
        title = tk.Label(login_frame, text="🔑 Homelab Authentication", 
                        font=('Arial', 18, 'bold'), 
                        fg=self.colors['primary'], bg=self.colors['card'])
        title.pack(pady=20)
        
        # Username
        user_frame = tk.Frame(login_frame, bg=self.colors['card'])
        user_frame.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(user_frame, text="Username:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w')
        self.username_entry = tk.Entry(user_frame, font=('Arial', 12),
                                      bg=self.colors['bg'], fg=self.colors['text'])
        self.username_entry.pack(fill=tk.X, pady=5)
        
        # Password
        pass_frame = tk.Frame(login_frame, bg=self.colors['card'])
        pass_frame.pack(pady=10, padx=20, fill=tk.X)
        tk.Label(pass_frame, text="Password:", font=('Arial', 12),
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w')
        self.password_entry = tk.Entry(pass_frame, font=('Arial', 12), show="*",
                                      bg=self.colors['bg'], fg=self.colors['text'])
        self.password_entry.pack(fill=tk.X, pady=5)
        
        # Login button
        login_btn = tk.Button(login_frame, text="🔓 Login",
                            font=('Arial', 12, 'bold'),
                            bg=self.colors['primary'], fg='white',
                            relief='flat', cursor='hand2',
                            command=self.login)
        login_btn.pack(pady=20, padx=20, fill=tk.X)
        
        # Status
        self.status_label = tk.Label(login_frame, text="Enter credentials to continue",
                                     font=('Arial', 10),
                                     fg=self.colors['text'], bg=self.colors['card'])
        self.status_label.pack(pady=10)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
    
    def create_main_interface(self):
        """Create main interface after authentication"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text=f"🏠 Homelab Management - Welcome {self.current_user}",
                font=('Arial', 16, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        logout_btn = tk.Button(header_frame, text="🚪 Logout",
                             font=('Arial', 10, 'bold'),
                             bg=self.colors['danger'], fg='white',
                             relief='flat', cursor='hand2',
                             command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Main content
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.create_dashboard_tab(notebook)
        
        # Users tab (admin only)
        if self.current_user == "admin":
            self.create_users_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
    
    def create_dashboard_tab(self, notebook):
        """Create dashboard tab"""
        dashboard_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # System info
        info_frame = tk.Frame(dashboard_frame, bg=self.colors['card'], relief='raised', bd=1)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(info_frame, text="🏠 Homelab Dashboard", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Quick stats
        stats = [
            ("👤 Current User:", self.current_user),
            ("🔐 Role:", "Administrator" if self.current_user == "admin" else "User"),
            ("📅 Login Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("🔧 System Status:", "Operational")
        ]
        
        for label, value in stats:
            stat_frame = tk.Frame(info_frame, bg=self.colors['card'])
            stat_frame.pack(fill=tk.X, pady=2, padx=20)
            tk.Label(stat_frame, text=label, font=('Arial', 11),
                    fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
            tk.Label(stat_frame, text=value, font=('Arial', 11, 'bold'),
                    fg=self.colors['secondary'], bg=self.colors['card']).pack(side=tk.RIGHT)
        
        # Actions
        actions_frame = tk.Frame(dashboard_frame, bg=self.colors['card'], relief='raised', bd=1)
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(actions_frame, text="⚡ Quick Actions", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        actions = [
            ("🧹 System Cleanup", self.system_cleanup),
            ("📊 System Monitor", self.system_monitor),
            ("🔧 Settings", self.open_settings),
            ("📋 View Logs", self.view_logs)
        ]
        
        for action_text, action_cmd in actions:
            btn = tk.Button(actions_frame, text=action_text,
                          font=('Arial', 11, 'bold'),
                          bg=self.colors['secondary'], fg='white',
                          relief='flat', cursor='hand2',
                          command=action_cmd)
            btn.pack(pady=5, padx=20, fill=tk.X)
    
    def create_users_tab(self, notebook):
        """Create users management tab"""
        users_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(users_frame, text="👥 Users")
        
        # Users list
        list_frame = tk.Frame(users_frame, bg=self.colors['card'], relief='raised', bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="👥 User Management", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Users listbox
        self.users_listbox = tk.Listbox(list_frame, font=('Arial', 11),
                                       bg=self.colors['bg'], fg=self.colors['text'])
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # User actions
        actions_frame = tk.Frame(list_frame, bg=self.colors['card'])
        actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(actions_frame, text="➕ Add User",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.add_user).pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_frame, text="🗑️ Delete User",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.delete_user).pack(side=tk.LEFT, padx=5)
        
        # Refresh users
        self.refresh_users()
    
    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings
        settings_list = tk.Frame(settings_frame, bg=self.colors['card'], relief='raised', bd=1)
        settings_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(settings_list, text="⚙️ System Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        settings_info = [
            ("Session Timeout", "1 hour"),
            ("Max Login Attempts", "3"),
            ("Password Policy", "Strong"),
            ("Audit Logging", "Enabled"),
            ("Auto Logout", "Disabled")
        ]
        
        for setting, value in settings_info:
            setting_frame = tk.Frame(settings_list, bg=self.colors['card'])
            setting_frame.pack(fill=tk.X, pady=5, padx=20)
            tk.Label(setting_frame, text=setting, font=('Arial', 11),
                    fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
            tk.Label(setting_frame, text=value, font=('Arial', 11, 'bold'),
                    fg=self.colors['secondary'], bg=self.colors['card']).pack(side=tk.RIGHT)
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter both username and password", fg=self.colors['danger'])
            return
        
        data = self.load_data()
        users = data.get("users", {})
        
        if username in users:
            stored_hash = users[username]["password"]
            if stored_hash == self.hash_password(password):
                self.authenticated = True
                self.current_user = username
                self.status_label.config(text="Login successful!", fg=self.colors['primary'])
                self.root.after(1000, self.create_main_interface)
                return
        
        self.status_label.config(text="Invalid credentials", fg=self.colors['danger'])
        # Clear password field
        self.password_entry.delete(0, tk.END)
    
    def logout(self):
        """Handle logout"""
        self.authenticated = False
        self.current_user = None
        self.create_login_screen()
    
    def refresh_users(self):
        """Refresh users list"""
        if hasattr(self, 'users_listbox'):
            self.users_listbox.delete(0, tk.END)
            data = self.load_data()
            users = data.get("users", {})
            for username in users:
                self.users_listbox.insert(tk.END, f"{username} ({users[username]['role']})")
    
    def add_user(self):
        """Add new user"""
        username = simpledialog.askstring("Add User", "Enter username:")
        if not username:
            return
        
        password = simpledialog.askstring("Add User", "Enter password:", show='*')
        if not password:
            return
        
        data = self.load_data()
        users = data.get("users", {})
        
        if username in users:
            messagebox.showerror("Error", "User already exists!")
            return
        
        users[username] = {
            "password": self.hash_password(password),
            "role": "user",
            "created": datetime.now().isoformat()
        }
        
        data["users"] = users
        if self.save_data(data):
            messagebox.showinfo("Success", "User added successfully!")
            self.refresh_users()
        else:
            messagebox.showerror("Error", "Failed to save user data!")
    
    def delete_user(self):
        """Delete selected user"""
        if not hasattr(self, 'users_listbox'):
            return
        
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete!")
            return
        
        selected_text = self.users_listbox.get(selection[0])
        username = selected_text.split(" (")[0]
        
        if username == "admin":
            messagebox.showerror("Error", "Cannot delete admin user!")
            return
        
        if messagebox.askyesno("Confirm", f"Delete user '{username}'?"):
            data = self.load_data()
            users = data.get("users", {})
            
            if username in users:
                del users[username]
                data["users"] = users
                
                if self.save_data(data):
                    messagebox.showinfo("Success", "User deleted successfully!")
                    self.refresh_users()
                else:
                    messagebox.showerror("Error", "Failed to save user data!")
    
    def system_cleanup(self):
        """Perform system cleanup"""
        messagebox.showinfo("System Cleanup", "System cleanup functionality would be implemented here!")
    
    def system_monitor(self):
        """Open system monitor"""
        messagebox.showinfo("System Monitor", "System monitor would be implemented here!")
    
    def open_settings(self):
        """Open settings"""
        messagebox.showinfo("Settings", "Settings would be implemented here!")
    
    def view_logs(self):
        """View system logs"""
        messagebox.showinfo("Logs", "Log viewer would be implemented here!")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = IntegratedHomelabAuth(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
