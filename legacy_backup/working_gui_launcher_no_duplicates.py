#!/usr/bin/env python3
"""
Homelab Launcher - No Duplicates Version
All working tools with no duplicates
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
from pathlib import Path

class NoDuplicatesLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Homelab Launcher")
        self.root.geometry("1600x900")
        self.root.configure(bg='#1a1a1a')
        
        # Center window on screen
        self.center_window()
        
        # Base path
        self.base_path = Path(__file__).parent
        
        # Create simple layout
        self.create_simple_layout()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_simple_layout(self):
        """Create simple layout that definitely shows buttons"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="🏠 Homelab Launcher", 
                        font=('Arial', 20, 'bold'), 
                        fg='#00ff88', bg='#1a1a1a')
        title.pack(pady=10)
        
        # Create scrollable tools frame
        self.create_scrollable_tools(main_frame)
    
    def create_scrollable_tools(self, parent):
        """Create scrollable tools frame with dynamic scaling"""
        # Create canvas without scrollbar - no container frame to maximize width
        self.canvas = tk.Canvas(parent, bg='#1a1a1a', highlightthickness=0)
        scrollable_frame = tk.Frame(self.canvas, bg='#1a1a1a')
        
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
        
        # Also enable keyboard scrolling
        def _on_key_down(event):
            if event.keysym == "Down":
                self.canvas.yview_scroll(1, "units")
            elif event.keysym == "Up":
                self.canvas.yview_scroll(-1, "units")
            elif event.keysym == "Page_Down":
                self.canvas.yview_scroll(1, "pages")
            elif event.keysym == "Page_Up":
                self.canvas.yview_scroll(-1, "pages")
            elif event.keysym == "Home":
                self.canvas.yview_moveto(0)
            elif event.keysym == "End":
                self.canvas.yview_moveto(1)
        
        self.canvas.bind_all("<Down>", _on_key_down)
        self.canvas.bind_all("<Up>", _on_key_down)
        self.canvas.bind_all("<Page_Down>", _on_key_down)
        self.canvas.bind_all("<Page_Up>", _on_key_down)
        self.canvas.bind_all("<Home>", _on_key_down)
        self.canvas.bind_all("<End>", _on_key_down)
        
        # Add all tools to scrollable frame
        self.add_all_tools(scrollable_frame)
    
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
    
    def add_all_tools(self, parent):
        """Add working tools with no duplicates - only best versions"""
        all_tools = [
            # Working Systems - Only Best Versions
            ("⭐ Simple Unified GUI", "simple_unified_gui.PY", "#2ecc71"),
            ("🚀 Unified Launcher GUI", "launcher_gui.py", "#3498db"),
            ("🔐 PC Authentication GUI", "pc_auth_gui.py", "#9b59b6"),
            ("📊 Streamlined Dashboard", "streamlined_dashboard.py", "#e67e22"),
            ("📈 Enhanced Dashboard (Fixed)", "enhanced_dashboard_fixed.py", "#d35400"),
            ("🌟 Fully Unified GUI", "fully_unified_gui.py", "#27ae60"),
            
            # Windows Server & Client
            ("🏢 Windows 10 Homelab Server", "win10_homelab_server.py", "#27ae60"),
            ("🚀 Windows 10 Server Launcher", "win10_server_launcher.py", "#3498db"),
            ("💻 Windows 11 Homelab Client", "win11_homelab_client.py", "#e67e22"),
            ("🔌 Windows 11 RDMA Client", "win11_rdma_client.py", "#f39c12"),
            
            # Overclocking & Performance - Only Fixed Versions
            ("🔧 Overclocking Dashboard", "overclocking_dashboard.py", "#e67e22"),
            ("⚡ Performance Optimizer (Fixed)", "performance_optimizer_fixed.py", "#27ae60"),
            ("🔧 Resource Optimizer Fixed", "resource_optimizer_fixed.py", "#d35400"),
            ("📊 Performance Reports", "performance_reports.py", "#f39c12"),
            ("💚 System Health Scorer", "system_health_scorer.py", "#2ecc71"),
            
            # RDMA & Networking - Only Fixed Version
            ("🔌 RDMA Integration (Fixed)", "rdma_integration_fixed.py", "#3498db"),
            ("🏢 Homelab Server", "homelab_server.py", "#27ae60"),
            ("💻 Homelab Client", "homelab_client.py", "#e67e22"),
            ("📊 Homelab Dashboard", "homelab_dashboard.py", "#f39c12"),
            ("🌐 Unified Homelab Dashboard", "unified_homelab_dashboard.py", "#3498db"),
            
            # System Cleanup & Optimization - Verified Working
            ("🧹 Aggressive RAM Cleaner", "aggressive_ram_cleaner.py", "#c0392b"),
            ("🧽 Soft RAM Cleaner", "soft_ram_cleaner.py", "#3498db"),
            ("🔄 RAM Cleanup Script", "ram_cleanup_script.py", "#f39c12"),
            ("⚡ CPU Cleanup Script", "cpu_cleanup_script.py", "#27ae60"),
            ("🎮 GPU Cleanup Script", "gpu_cleanup_script.py", "#e67e22"),
            ("👑 System Cleanup Master", "system_cleanup_master.py", "#9b59b6"),
            ("⚡ Memory Jolt", "memory_jolt.py", "#c0392b"),
            
            # Security & Authentication - Verified Working
            ("🔐 PC Authentication System", "pc_auth_system.py", "#9b59b6"),
            ("🛡️ Advanced Security", "advanced_security.py", "#c0392b"),
            ("🤖 Automated Interventions", "automated_interventions.py", "#3498db"),
            ("📡 Automated Responses", "automated_responses.py", "#f39c12"),
            
            # Backup & Management - Only Fixed Versions
            ("💾 Backup Manager (Fixed)", "backup_manager_fixed.py", "#27ae60"),
            ("⚙️ Settings Manager (Fixed)", "settings_manager_fixed.py", "#3498db"),
            ("🗄️ Database Schema (Fixed)", "database_schema_fixed.py", "#e67e22"),
            ("📅 Task Scheduler (Fixed)", "task_scheduler_fixed.py", "#f39c12"),
            
            # Testing & Diagnostics
            ("🎮 Test GPU Monitoring", "test_gpu_monitoring.py", "#e67e22"),
            ("🖥️ Test GUI", "test_gui.py", "#3498db"),
            ("🐛 Debug GPU GUI", "debug_gpu_gui.py", "#c0392b"),
            ("🎯 Test NVIDIA SMI", "test_nvidia_smi.py", "#27ae60"),
            
            # Utilities & Tools - Only Fixed Versions
            ("🖥️ Console Launcher", "console_launcher.PY", "#3498db"),
            ("🔄 Stay Open Launcher", "stay_open_launcher.PY", "#27ae60"),
            ("🔌 System API", "system_api.py", "#e67e22"),
            ("❓ Help System", "help_system.py", "#f39c12"),
            ("📧 Email Notifications", "email_notifications.py", "#9b59b6"),
            ("🌍 Internationalization (Fixed)", "internationalization_fixed.py", "#2ecc71"),
            ("♿ Accessibility", "accessibility.py", "#3498db"),
            ("🤖 Machine Learning", "machine_learning.py", "#e67e22"),
            
            # Legacy Tools - Verified Working
            ("🚀 System Dashboard", "system_dashboard.py", "#16a085"),
            ("🧹 RAM Monitor", "ram_monitor_gui.py", "#f39c12"),
            ("🎮 GPU Monitor", "gpu_monitor_gui.py", "#c0392b"),
            ("⚡ CPU Monitor", "cpu_monitor_gui.py", "#5dade2")
        ]
        
        # Create categories - updated for 51 tools (duplicates removed)
        categories = [
            ("🔥 Working Systems", 0, 6),  # 6 working systems
            ("🖥️ Windows Server & Client", 6, 10),  # 4 Windows tools
            ("⚡ Overclocking & Performance", 10, 15),  # 5 performance tools
            ("🔌 RDMA & Networking", 15, 20),  # 5 networking tools
            ("🧹 System Cleanup & Optimization", 20, 27),  # 7 cleanup tools
            ("🔐 Security & Authentication", 27, 31),  # 4 security tools
            ("💾 Backup & Management", 31, 35),  # 4 management tools
            ("🧪 Testing & Diagnostics", 35, 39),  # 4 testing tools
            ("🛠️ Utilities & Tools", 39, 47),  # 8 utility tools
            ("📜 Legacy Tools", 47, 51)  # 4 legacy tools
        ]
        
        # Create category sections
        for cat_name, start_idx, end_idx in categories:
            # Category header
            cat_frame = tk.Frame(parent, bg='#1a1a1a', relief='raised', bd=1)
            cat_frame.pack(fill=tk.X, pady=(10, 5), padx=5)
            
            cat_label = tk.Label(cat_frame, text=cat_name,
                                font=('Arial', 14, 'bold'),
                                fg='#00ff88', bg='#1a1a1a')
            cat_label.pack(pady=5, padx=10, anchor='w')
            
            # Tools in this category
            cat_tools_frame = tk.Frame(parent, bg='#2d2d2d')
            cat_tools_frame.pack(fill=tk.X, pady=(0, 5), padx=5)
            
            # Create buttons for this category - 6 per row for full width
            for i in range(start_idx, min(end_idx, len(all_tools))):
                name, filename, color = all_tools[i]
                row = (i - start_idx) // 6
                
                # Create row if needed
                if (i - start_idx) % 6 == 0:
                    row_frame = tk.Frame(cat_tools_frame, bg='#2d2d2d')
                    row_frame.pack(fill=tk.X, pady=2)
                
                # Create button
                button = tk.Button(row_frame, text=name,
                                 font=('Arial', 9, 'bold'),
                                 bg=color, fg='white',
                                 relief='flat', cursor='hand2',
                                 padx=8, pady=6,
                                 command=lambda f=filename, n=name: self.launch_tool(f, n))
                button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
    
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
        app = NoDuplicatesLauncher(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting launcher: {e}")

if __name__ == "__main__":
    main()
