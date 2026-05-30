#!/usr/bin/env python3
"""
Fixed Homelab Launcher - Only Working Tools
All tools verified to exist and function
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
from pathlib import Path
import os

class FixedLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Homelab Launcher - Working Tools")
        self.root.geometry("1600x900")
        self.root.configure(bg='#1a1a1a')
        
        # Center window on screen
        self.center_window()
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#2ecc71',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#c0392b',
            'info': '#9b59b6'
        }
        
        # Base path
        self.base_path = Path(__file__).parent
        
        # Create widgets
        self.create_widgets()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create widgets with working tools only"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="🏠 Homelab Launcher", 
                        font=('Arial', 20, 'bold'), 
                        fg=self.colors['primary'], bg=self.colors['bg'])
        title.pack(pady=10)
        
        # Create scrollable tools frame
        self.create_scrollable_tools(main_frame)
    
    def create_scrollable_tools(self, parent):
        """Create scrollable tools frame with dynamic scaling"""
        # Create canvas without scrollbar
        self.canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window that fills entire canvas width
        self.canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.canvas.winfo_width())
        
        # Pack canvas to fill entire parent with no padding
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Bind window resize event for dynamic scaling
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Initial width update
        self.update_canvas_width()
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add working tools to scrollable frame
        self.add_working_tools(scrollable_frame)
    
    def on_window_resize(self, event):
        """Handle window resize for dynamic scaling"""
        if event.widget == self.root:
            self.update_canvas_width()
    
    def update_canvas_width(self):
        """Update canvas width to match window width"""
        try:
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            if canvas_width > 1:  # Only update if canvas has valid width
                self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        except:
            pass
    
    def add_working_tools(self, parent):
        """Add only verified working tools"""
        # Verified working tools based on actual file existence and functionality
        working_tools = [
            # System Monitors - These work well
            ("🚀 System Dashboard", "system_dashboard.py", self.colors['primary']),
            ("🧹 RAM Monitor", "ram_monitor_gui.py", self.colors['warning']),
            ("🎮 GPU Monitor", "gpu_monitor_gui.py", self.colors['danger']),
            ("⚡ CPU Monitor", "cpu_monitor_gui.py", self.colors['info']),
            
            # Launchers - Simple and functional
            ("🚀 Launcher", "launcher.py", self.colors['secondary']),
            ("🖥️ Console Launcher", "console_launcher.PY", self.colors['success']),
            ("🔄 Stay Open Launcher", "stay_open_launcher.PY", self.colors['primary']),
            
            # System Tools - Basic utilities that work
            ("🧹 Aggressive RAM Cleaner", "aggressive_ram_cleaner.py", self.colors['danger']),
            ("🧽 Soft RAM Cleaner", "soft_ram_cleaner.py", self.colors['secondary']),
            ("⚡ Memory Jolt", "memory_jolt.py", self.colors['warning']),
            
            # Security Tools - Functional
            ("🔐 PC Authentication System", "pc_auth_system.py", self.colors['info']),
            ("🛡️ Advanced Security", "advanced_security.py", self.colors['danger']),
            
            # Communication Tools - Working
            ("📧 Email Notifications", "email_notifications.py", self.colors['success']),
            ("❓ Help System", "help_system.py", self.colors['secondary']),
            
            # Accessibility - Simple and working
            ("♿ Accessibility", "accessibility.py", self.colors['primary']),
            
            # Testing Tools - Simple test scripts
            ("🖥️ Test GUI", "test_gui.py", self.colors['warning']),
            ("🎮 Test GPU Monitoring", "test_gpu_monitoring.py", self.colors['danger']),
            ("🎯 Test NVIDIA SMI", "test_nvidia_smi.py", self.colors['info'])
        ]
        
        # Create category sections
        categories = [
            ("📊 System Monitors", 0, 4),
            ("🚀 Launchers", 4, 7),
            ("🧹 System Tools", 7, 10),
            ("🔐 Security Tools", 10, 12),
            ("📧 Communication", 12, 14),
            ("♿ Accessibility", 14, 15),
            ("🧪 Testing Tools", 15, 18)
        ]
        
        for cat_name, start_idx, end_idx in categories:
            # Category header
            cat_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=1)
            cat_frame.pack(fill=tk.X, pady=(10, 5), padx=5)
            
            cat_label = tk.Label(cat_frame, text=cat_name,
                                font=('Arial', 14, 'bold'),
                                fg=self.colors['primary'], bg=self.colors['card'])
            cat_label.pack(pady=5, padx=10, anchor='w')
            
            # Tools in this category
            cat_tools_frame = tk.Frame(parent, bg=self.colors['card'])
            cat_tools_frame.pack(fill=tk.X, pady=(0, 5), padx=5)
            
            # Create buttons for this category - 4 per row for good spacing
            for i in range(start_idx, min(end_idx, len(working_tools))):
                name, filename, color = working_tools[i]
                
                # Create row if needed
                if (i - start_idx) % 4 == 0:
                    row_frame = tk.Frame(cat_tools_frame, bg=self.colors['card'])
                    row_frame.pack(fill=tk.X, pady=2)
                
                # Create button
                button = tk.Button(row_frame, text=name,
                                 font=('Arial', 10, 'bold'),
                                 bg=color, fg='white',
                                 relief='flat', cursor='hand2',
                                 padx=10, pady=8,
                                 command=lambda f=filename, n=name: self.launch_tool(f, n))
                button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def launch_tool(self, filename, tool_name):
        """Launch a tool with proper error handling"""
        try:
            # Check if file exists
            file_path = self.base_path / filename
            if not file_path.exists():
                messagebox.showerror("Error", f"Tool not found: {filename}")
                return
            
            # Launch the tool
            subprocess.Popen([sys.executable, filename])
            print(f"Launched {tool_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {e}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = FixedLauncherGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting launcher: {e}")
        messagebox.showerror("Error", f"Failed to start launcher: {e}")

if __name__ == "__main__":
    main()
