#!/usr/bin/env python3
"""
Integrated RAM Sharing Launcher
Complete integration with Homelab Launcher and Dashboard systems
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
from datetime import datetime

class IntegratedRAMLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ Integrated RAM Sharing Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'card_hover': '#3a3a3a',
            'primary': '#00ff88',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00d4ff',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#0078ff'
        }
        
        # Tool definitions
        self.tools = {
            "GUI Tools": {
                "RAM Sharing Manager": {
                    "path": "RAM_Sharing_GUI.py",
                    "icon": "🖥️",
                    "description": "Full-featured GUI with tkinter",
                    "python_required": True,
                    "category": "gui"
                },
                "Simple RAM Sharing": {
                    "path": "RAM_Sharing_Simple_GUI.py", 
                    "icon": "🔗",
                    "description": "Console-based GUI (no tkinter)",
                    "python_required": True,
                    "category": "gui"
                }
            },
            "Batch Tools": {
                "Universal Launcher": {
                    "path": "Universal_Launcher.bat",
                    "icon": "⚡",
                    "description": "Universal launcher for all RAM tools",
                    "python_required": False,
                    "category": "batch"
                },
                "RAM Server Setup": {
                    "path": "Setup_RAM_Sharing.bat",
                    "icon": "🚀",
                    "description": "Start RAM sharing server (PC 1)",
                    "python_required": False,
                    "category": "batch"
                },
                "RAM Client Connect": {
                    "path": "Map_RAM_Sharing.bat",
                    "icon": "🔌",
                    "description": "Connect to RAM server (PC 2)",
                    "python_required": False,
                    "category": "batch"
                },
                "Windows Compatibility Fix": {
                    "path": "Fix_Windows_Compatibility.bat",
                    "icon": "🔧",
                    "description": "Fix Windows 10/11 compatibility",
                    "python_required": False,
                    "category": "batch"
                },
                "Complete Setup": {
                    "path": "Cross_Version_Setup.bat",
                    "icon": "🛠️",
                    "description": "Complete Windows 10/11 setup",
                    "python_required": False,
                    "category": "batch"
                }
            },
            "Quick Actions": {
                "Test Network": {
                    "path": "ping 192.168.1.132",
                    "icon": "🌐",
                    "description": "Test connection to client PC",
                    "python_required": False,
                    "category": "quick"
                },
                "Cleanup All": {
                    "path": "Cleanup_RAM_Sharing.bat",
                    "icon": "🧹",
                    "description": "Remove all RAM sharing components",
                    "python_required": False,
                    "category": "quick"
                }
            }
        }
        
        self.running_processes = {}
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        styles = {
            'Title.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['primary'], 'font': ('Segoe UI', 20, 'bold')},
            'Subtitle.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['text_secondary'], 'font': ('Segoe UI', 11)},
            'Card.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'ToolCard.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'Info.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 10)},
            'ToolName.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 12, 'bold')},
            'ToolDesc.TLabel': {'background': self.colors['card'], 'foreground': self.colors['text_secondary'], 'font': ('Segoe UI', 9)},
            'Status.TLabel': {'background': self.colors['card'], 'foreground': self.colors['success'], 'font': ('Segoe UI', 9, 'bold')},
            'Launch.TButton': {'background': self.colors['primary'], 'foreground': self.colors['bg'], 'font': ('Segoe UI', 10, 'bold')},
            'Log.TFrame': {'background': self.colors['bg'], 'relief': 'flat', 'borderwidth': 1}
        }
        
        for style_name, config in styles.items():
            style.configure(style_name, **config)
            
        style.map('Launch.TButton', background=[('active', self.colors['accent'])])
        
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="🖥️ Integrated RAM Sharing Manager", style='Title.TLabel').pack(anchor='w', padx=15, pady=(15, 5))
        ttk.Label(header_frame, text="Cross-PC RAM sharing with Windows 10/11 compatibility", style='Subtitle.TLabel').pack(anchor='w', padx=15, pady=(0, 15))
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Tools section
        tools_frame = ttk.Frame(main_frame)
        tools_frame.pack(fill='both', expand=True)
        
        # Create notebook for categories
        self.notebook = ttk.Notebook(tools_frame)
        self.notebook.pack(fill='both', expand=True)
        
        for category_name, tools in self.tools.items():
            self.create_category_tab(category_name, tools)
            
        # Status bar
        self.create_status_bar()
        
    def create_category_tab(self, category_name, tools):
        """Create a tab for each tool category"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=category_name)
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add tools to the tab
        row = 0
        for tool_name, tool_info in tools.items():
            self.create_tool_card(scrollable_frame, tool_name, tool_info, row)
            row += 1
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_tool_card(self, parent, tool_name, tool_info, row):
        """Create a tool card"""
        card_frame = ttk.Frame(parent, style='ToolCard.TFrame')
        card_frame.grid(row=row, column=0, padx=10, pady=8, sticky='ew')
        parent.grid_columnconfigure(0, weight=1)
        
        # Tool info
        info_frame = ttk.Frame(card_frame, style='ToolCard.TFrame')
        info_frame.pack(side='left', fill='both', expand=True, padx=15, pady=10)
        
        # Icon and name
        name_frame = ttk.Frame(info_frame, style='ToolCard.TFrame')
        name_frame.pack(fill='x')
        
        ttk.Label(name_frame, text=tool_info['icon'], font=('Segoe UI', 16)).pack(side='left')
        ttk.Label(name_frame, text=tool_name, style='ToolName.TLabel').pack(side='left', padx=(8, 0))
        
        # Description
        ttk.Label(info_frame, text=tool_info['description'], style='ToolDesc.TLabel').pack(anchor='w', pady=(5, 0))
        
        # Status indicator
        if tool_info.get('python_required', False):
            ttk.Label(info_frame, text="🐍 Python Required", style='Status.TLabel').pack(anchor='w', pady=(5, 0))
        
        # Launch button
        button_frame = ttk.Frame(card_frame, style='ToolCard.TFrame')
        button_frame.pack(side='right', padx=15, pady=10)
        
        launch_btn = ttk.Button(button_frame, text="Launch", style='Launch.TButton',
                              command=lambda tn=tool_name, ti=tool_info: self.launch_tool(tn, ti))
        launch_btn.pack()
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root, style='Log.TFrame')
        status_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Status text
        self.status_var = tk.StringVar(value="Ready - Select a tool to launch")
        ttk.Label(status_frame, textvariable=self.status_var, style='Info.TLabel').pack(side='left', padx=10, pady=5)
        
        # Clear log button
        ttk.Button(status_frame, text="Clear Log", command=self.clear_log).pack(side='right', padx=10, pady=5)
        
        # Log area
        log_frame = ttk.Frame(self.root, style='Log.TFrame')
        log_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD,
                                                bg='#242424', fg=self.colors['text'],
                                                font=('Consolas', 9))
        self.log_text.pack(fill='x', padx=5, pady=5)
        
    def log(self, message, level="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": self.colors['text'],
            "SUCCESS": self.colors['success'],
            "ERROR": self.colors['danger'],
            "WARNING": self.colors['warning']
        }
        color = color_map.get(level, self.colors['text'])
        
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        
        # Auto-limit log size
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 100:
            self.log_text.delete("1.0", "20.0")
            
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete("1.0", tk.END)
        
    def check_python(self):
        """Check if Python is available"""
        try:
            # Try python first
            result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'python'
        except:
            pass
            
        try:
            # Try py
            result = subprocess.run(['py', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'py'
        except:
            pass
            
        return None
        
    def launch_tool(self, tool_name, tool_info):
        """Launch a tool"""
        if tool_name in self.running_processes:
            messagebox.showwarning("Already Running", f"{tool_name} is already running!")
            return
            
        path = tool_info['path']
        
        # Check Python requirement
        if tool_info.get('python_required', False):
            python_cmd = self.check_python()
            if not python_cmd:
                messagebox.showerror("Python Required", 
                    f"{tool_name} requires Python but it's not installed or not in PATH.\n\n"
                    "Please install Python 3.7+ or use batch tools instead.")
                return
                
            command = [python_cmd, path]
        else:
            # For batch files, use cmd
            if path.endswith('.bat'):
                command = ['cmd', '/c', path]
            else:
                command = path.split()
                
        self.log(f"Launching {tool_name}...", "INFO")
        self.status_var.set(f"Launching {tool_name}...")
        
        def run_tool():
            try:
                process = subprocess.Popen(command, cwd=os.getcwd(), 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         text=True, bufsize=1, universal_newlines=True)
                
                self.running_processes[tool_name] = process
                self.status_var.set(f"{tool_name} running...")
                
                # Monitor process
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    self.log(f"{tool_name} completed successfully", "SUCCESS")
                else:
                    self.log(f"{tool_name} failed with code {process.returncode}", "ERROR")
                    if stderr:
                        self.log(f"Error: {stderr.strip()}", "ERROR")
                        
            except Exception as e:
                self.log(f"Failed to launch {tool_name}: {str(e)}", "ERROR")
            finally:
                if tool_name in self.running_processes:
                    del self.running_processes[tool_name]
                self.status_var.set("Ready - Select a tool to launch")
                
        threading.Thread(target=run_tool, daemon=True).start()
        
    def __del__(self):
        """Cleanup on exit"""
        for process in self.running_processes.values():
            try:
                process.terminate()
            except:
                pass

def main():
    """Main entry point"""
    root = tk.Tk()
    app = IntegratedRAMLauncher(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
