#!/usr/bin/env python3
"""
Homelab Unified Launcher
Integrates all Homelab Tools including Windows Assistant with unified dark theme
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import time
import os
import sys
from pathlib import Path
import json
import psutil

# Add current directory to path for theme import
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import unified theme
try:
    from Core_Services.theme_config import HomelabTheme
    THEME_AVAILABLE = True
except ImportError:
    try:
        from theme_config import HomelabTheme
        THEME_AVAILABLE = True
    except ImportError:
        THEME_AVAILABLE = False
        print("Warning: Unified theme not available")

class HomelabUnifiedLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 Homelab Unified Launcher")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Apply unified theme
        if THEME_AVAILABLE:
            self.theme = HomelabTheme()
            self.root.configure(bg=self.theme.COLORS['bg_primary'])
            self.style = ttk.Style()
            self.theme.apply_styles(self.style)
        else:
            # Fallback theme
            self.root.configure(bg='#1a1a1a')
            self.style = ttk.Style()
            self.style.theme_use('clam')
        
        # Running processes tracking
        self.running_tools = {}
        
        # Tool definitions with paths and commands
        self.tools = {
            "Core Services": {
                "Homelab Portal": {
                    "path": "Core Services\\homelab_portal.py",
                    "description": "Main portal for resource sharing and device management",
                    "icon": "🌐",
                    "category": "Core",
                    "dependencies": ["psutil", "PIL", "flask", "flask-cors"]
                },
                "Resource Sharing": {
                    "path": "Core Services\\bidirectional_resource_sharing.py", 
                    "description": "P2P resource sharing between devices",
                    "icon": "🔄",
                    "category": "Core",
                    "dependencies": ["psutil", "socket"]
                },
                "System Monitor": {
                    "path": "Core Services\\unified_monitoring.py",
                    "description": "Comprehensive system monitoring dashboard",
                    "icon": "📊",
                    "category": "Monitoring",
                    "dependencies": ["psutil", "matplotlib"]
                }
            },
            "Monitoring Tools": {
                "CPU Monitor": {
                    "path": "Cpu Monitor\\cpu_monitor.py",
                    "description": "Real-time CPU monitoring and performance tracking",
                    "icon": "💻",
                    "category": "Monitoring", 
                    "dependencies": ["psutil", "matplotlib", "PIL"]
                },
                "GPU Monitor": {
                    "path": "Gpu Monitor\\gpu_monitor.py",
                    "description": "GPU monitoring with temperature and usage tracking",
                    "icon": "🎮",
                    "category": "Monitoring",
                    "dependencies": ["psutil", "matplotlib", "PIL", "GPUtil"]
                },
                "Network Monitor": {
                    "path": "Network Monitor\\network_monitor.py", 
                    "description": "Network performance and connectivity monitoring",
                    "icon": "🌍",
                    "category": "Monitoring",
                    "dependencies": ["psutil", "matplotlib", "PIL"]
                }
            },
            "System Tools": {
                "RAM Cleaner": {
                    "path": "Ram clean up\\ram_monitor_gui.py",
                    "description": "RAM monitoring and memory optimization",
                    "icon": "🧹",
                    "category": "Utilities",
                    "dependencies": ["psutil", "matplotlib", "PIL"]
                },
                "Windows Assistant": {
                    "path": "Windows Assistant\\main.py",
                    "description": "Modern Clippy-style assistant with system help",
                    "icon": "📎",
                    "category": "Assistant",
                    "dependencies": ["PIL", "psutil", "pywin32", "plyer"]
                },
                "File Manager": {
                    "path": "Core Services\\data_persistence.py",
                    "description": "File and data management system",
                    "icon": "📁",
                    "category": "Utilities",
                    "dependencies": ["sqlite3", "json"]
                }
            },
            "Advanced Tools": {
                "Automation Framework": {
                    "path": "Core Services\\automation_framework.py",
                    "description": "System automation and scripting framework",
                    "icon": "⚙️",
                    "category": "Automation",
                    "dependencies": ["threading", "subprocess", "json"]
                },
                "Security Manager": {
                    "path": "Core Services\\advanced_security.py",
                    "description": "System security and monitoring tools",
                    "icon": "🔒",
                    "category": "Security",
                    "dependencies": ["hashlib", "cryptography"]
                },
                "Analytics Engine": {
                    "path": "Core Services\\analytics_engine.py",
                    "description": "System analytics and reporting",
                    "icon": "📈",
                    "category": "Analytics",
                    "dependencies": ["matplotlib", "pandas", "numpy"]
                }
            }
        }
        
        self.setup_gui()
        self.check_running_tools()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill='x', pady=(0, 20))
        
        if THEME_AVAILABLE:
            title_label = ttk.Label(header_frame, text="🏠 Homelab Unified Launcher", 
                                  style='Title.TLabel')
        else:
            title_label = ttk.Label(header_frame, text="🏠 Homelab Unified Launcher",
                                  font=('Segoe UI', 20, 'bold'), bg='#1a1a1a', fg='#00d4ff')
        title_label.pack(side='left')
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready")
        if THEME_AVAILABLE:
            status_label = ttk.Label(header_frame, textvariable=self.status_var,
                                   style='Secondary.TLabel')
        else:
            status_label = ttk.Label(header_frame, textvariable=self.status_var,
                                   font=('Segoe UI', 10), bg='#1a1a1a', fg='#b0b0b0')
        status_label.pack(side='right')
        
        # Create notebook for tool categories
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs for each category
        for category_name, tools in self.tools.items():
            self.create_category_tab(category_name, tools)
        
        # Control panel
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill='x', pady=(20, 0))
        
        # Launch selected button
        if THEME_AVAILABLE:
            launch_btn = ttk.Button(control_frame, text="🚀 Launch Selected Tool",
                                  command=self.launch_selected_tool, style='Primary.TButton')
        else:
            launch_btn = ttk.Button(control_frame, text="🚀 Launch Selected Tool",
                                  command=self.launch_selected_tool)
        launch_btn.pack(side='left', padx=(0, 10))
        
        # Stop selected button
        if THEME_AVAILABLE:
            stop_btn = ttk.Button(control_frame, text="⏹️ Stop Selected Tool",
                                command=self.stop_selected_tool, style='Danger.TButton')
        else:
            stop_btn = ttk.Button(control_frame, text="⏹️ Stop Selected Tool",
                                command=self.stop_selected_tool)
        stop_btn.pack(side='left', padx=(0, 10))
        
        # Refresh button
        if THEME_AVAILABLE:
            refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Status",
                                   command=self.check_running_tools, style='Secondary.TButton')
        else:
            refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Status",
                                   command=self.check_running_tools)
        refresh_btn.pack(side='left', padx=(0, 10))
        
        # Launch all button
        if THEME_AVAILABLE:
            launch_all_btn = ttk.Button(control_frame, text="🚀 Launch All Core Tools",
                                      command=self.launch_all_core_tools, style='Success.TButton')
        else:
            launch_all_btn = ttk.Button(control_frame, text="🚀 Launch All Core Tools",
                                      command=self.launch_all_core_tools)
        launch_all_btn.pack(side='right')
        
    def create_category_tab(self, category_name, tools):
        """Create a tab for a tool category"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=category_name)
        
        # Create treeview for tools
        columns = ('Tool', 'Description', 'Status', 'Action')
        self.tree = ttk.Treeview(tab_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Tool', text='Tool')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Action', text='Action')
        
        self.tree.column('Tool', width=200)
        self.tree.column('Description', width=400)
        self.tree.column('Status', width=100)
        self.tree.column('Action', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate with tools
        for tool_name, tool_info in tools.items():
            status = self.get_tool_status(tool_info['path'])
            self.tree.insert('', 'end', iid=tool_name, values=(
                f"{tool_info['icon']} {tool_name}",
                tool_info['description'],
                status,
                "Launch"
            ))
        
        # Bind double-click for launch
        self.tree.bind('<Double-1>', lambda e: self.launch_selected_tool())
        
    def get_tool_status(self, tool_path):
        """Check if a tool is currently running"""
        try:
            full_path = current_dir / tool_path
            tool_name = Path(tool_path).stem
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any(tool_name in ' '.join(proc.info['cmdline']) for cmd in proc.info['cmdline']):
                        return "🟢 Running"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        
        return "⚪ Stopped"
    
    def check_running_tools(self):
        """Check status of all running tools"""
        self.status_var.set("Checking tool status...")
        
        for category_name, tools in self.tools.items():
            for tool_name, tool_info in tools.items():
                status = self.get_tool_status(tool_info['path'])
                # Update tree view if it exists
                try:
                    if self.tree.exists(tool_name):
                        current_values = self.tree.item(tool_name)['values']
                        self.tree.item(tool_name, values=(
                            current_values[0],
                            current_values[1], 
                            status,
                            current_values[3]
                        ))
                except:
                    pass
        
        self.status_var.set(f"Status updated - {time.strftime('%H:%M:%S')}")
    
    def launch_selected_tool(self):
        """Launch the currently selected tool"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tool to launch")
            return
        
        tool_name = selection[0]
        
        # Find the tool info
        tool_info = None
        for category_tools in self.tools.values():
            if tool_name in category_tools:
                tool_info = category_tools[tool_name]
                break
        
        if not tool_info:
            messagebox.showerror("Error", f"Tool '{tool_name}' not found")
            return
        
        self.launch_tool(tool_name, tool_info)
    
    def launch_tool(self, tool_name, tool_info):
        """Launch a specific tool"""
        try:
            tool_path = current_dir / tool_info['path']
            
            if not tool_path.exists():
                messagebox.showerror("Error", f"Tool file not found: {tool_path}")
                return
            
            self.status_var.set(f"Launching {tool_name}...")
            
            # Launch in subprocess
            process = subprocess.Popen([sys.executable, str(tool_path)], 
                                    cwd=str(tool_path.parent))
            
            # Track the process
            self.running_tools[tool_name] = process
            
            # Update status
            self.check_running_tools()
            
            messagebox.showinfo("Success", f"{tool_name} launched successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {e}")
            self.status_var.set(f"Error launching {tool_name}")
    
    def stop_selected_tool(self):
        """Stop the currently selected tool"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tool to stop")
            return
        
        tool_name = selection[0]
        
        if tool_name in self.running_tools:
            try:
                process = self.running_tools[tool_name]
                process.terminate()
                del self.running_tools[tool_name]
                self.check_running_tools()
                messagebox.showinfo("Success", f"{tool_name} stopped")
            except:
                messagebox.showerror("Error", f"Failed to stop {tool_name}")
        else:
            messagebox.showwarning("Not Running", f"{tool_name} is not being tracked by launcher")
    
    def launch_all_core_tools(self):
        """Launch all core Homelab tools"""
        core_tools = ["Homelab Portal", "Resource Sharing", "System Monitor"]
        launched = []
        failed = []
        
        for tool_name in core_tools:
            # Find the tool info
            tool_info = None
            for category_tools in self.tools.values():
                if tool_name in category_tools:
                    tool_info = category_tools[tool_name]
                    break
            
            if tool_info:
                try:
                    self.launch_tool(tool_name, tool_info)
                    launched.append(tool_name)
                except:
                    failed.append(tool_name)
        
        if launched and not failed:
            messagebox.showinfo("Success", f"Launched core tools: {', '.join(launched)}")
        elif launched and failed:
            messagebox.showwarning("Partial Success", 
                                f"Launched: {', '.join(launched)}\nFailed: {', '.join(failed)}")
        else:
            messagebox.showerror("Error", "Failed to launch any core tools")
    
    def run(self):
        """Start the launcher"""
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start GUI
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        launcher = HomelabUnifiedLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        messagebox.showerror("Fatal Error", f"Launcher failed to start: {e}")

if __name__ == "__main__":
    main()
