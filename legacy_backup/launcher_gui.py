#!/usr/bin/env python3
"""
Unified Launcher GUI
Easy connection to all dashboards/tools or solo mode operation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import json

# Import unified launcher
from unified_launcher import unified_launcher, LauncherMode, ToolStatus

class UnifiedLauncherGUI:
    """GUI for the unified homelab launcher"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Unified Homelab Launcher")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
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
        
        # GUI state
        self.selected_tool = None
        self.refresh_active = False
        self.refresh_thread = None
        
        # Create UI
        self.create_ui()
        
        # Start GUI monitoring
        self.start_gui_monitoring()
    
    def create_ui(self):
        """Create the GUI interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create main sections
        self.create_mode_selection(content_frame)
        self.create_tool_management(content_frame)
        self.create_status_monitoring(content_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title and status
        title_frame = tk.Frame(header_frame, bg=self.colors['card'])
        title_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        title_label = tk.Label(title_frame, text="🚀 Unified Homelab Launcher",
                              font=('Segoe UI', 18, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W)
        
        self.mode_label = tk.Label(title_frame, text=f"Mode: {unified_launcher.current_mode.value}",
                                  font=('Segoe UI', 10),
                                  fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.mode_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Control buttons
        control_frame = tk.Frame(header_frame, bg=self.colors['card'])
        control_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.refresh_btn = tk.Button(control_frame, text="🔄 Refresh",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg=self.colors['success'], fg=self.colors['bg'],
                                    relief='flat', cursor='hand2',
                                    command=self.refresh_display)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = tk.Button(control_frame, text="⚙️ Settings",
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['warning'], fg=self.colors['bg'],
                                     relief='flat', cursor='hand2',
                                     command=self.open_settings)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = tk.Button(control_frame, text="🚪 Quit",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=self.colors['danger'], fg=self.colors['bg'],
                                  relief='flat', cursor='hand2',
                                  command=self.quit_application)
        self.quit_btn.pack(side=tk.LEFT, padx=5)
    
    def create_mode_selection(self, parent):
        """Create mode selection section"""
        mode_frame = tk.Frame(parent, bg=self.colors['card'])
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(mode_frame, text="🎯 Operation Mode",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Mode buttons container
        buttons_container = tk.Frame(mode_frame, bg=self.colors['card'])
        buttons_container.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Create mode buttons
        self.create_mode_button(buttons_container, "Dashboard Mode", LauncherMode.DASHBOARD, 
                              "Start all dashboard tools and main interface", 0)
        self.create_mode_button(buttons_container, "Solo Mode", LauncherMode.SOLO, 
                              "Run individual tools in standalone mode", 1)
        self.create_mode_button(buttons_container, "Integrated Mode", LauncherMode.INTEGRATED, 
                              "Start full integrated system with authentication", 2)
        self.create_mode_button(buttons_container, "Auth Mode", LauncherMode.AUTH, 
                              "Start authentication tools only", 3)
        self.create_mode_button(buttons_container, "Legacy Mode", LauncherMode.LEGACY, 
                              "Run original Homelab Tools", 4)
    
    def create_mode_button(self, parent, title, mode, description, column):
        """Create individual mode button"""
        button_frame = tk.Frame(parent, bg=self.colors['card'])
        button_frame.grid(row=0, column=column, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Mode button
        mode_btn = tk.Button(button_frame, text=title,
                           font=('Segoe UI', 11, 'bold'),
                           bg=self.colors['primary'] if unified_launcher.current_mode == mode else self.colors['card'],
                           fg=self.colors['bg'] if unified_launcher.current_mode == mode else self.colors['text'],
                           relief='flat', cursor='hand2',
                           command=lambda m=mode: self.switch_mode(m))
        mode_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Description label
        desc_label = tk.Label(button_frame, text=description,
                             font=('Segoe UI', 9),
                             fg=self.colors['text_secondary'], bg=self.colors['card'])
        desc_label.pack(anchor=tk.W, padx=5, pady=(0, 5))
        
        # Store reference
        setattr(self, f"{mode.value}_btn", mode_btn)
    
    def create_tool_management(self, parent):
        """Create tool management section"""
        tools_frame = tk.Frame(parent, bg=self.colors['card'])
        tools_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Title
        title_label = tk.Label(tools_frame, text="🔧 Tool Management",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Create notebook for tool categories
        notebook = ttk.Notebook(tools_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Current mode tools tab
        current_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(current_frame, text="Current Mode")
        
        # All tools tab
        all_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(all_frame, text="All Tools")
        
        # Running tools tab
        running_frame = tk.Frame(notebook, bg=self.colors['card'])
        notebook.add(running_frame, text="Running")
        
        # Create tool displays
        self.create_current_tools_display(current_frame)
        self.create_all_tools_display(all_frame)
        self.create_running_tools_display(running_frame)
    
    def create_current_tools_display(self, parent):
        """Create current mode tools display"""
        # Tools container
        tools_container = tk.Frame(parent, bg=self.colors['card'])
        tools_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for tools
        columns = ('Name', 'Status', 'Port', 'URL', 'Last Run')
        self.current_tools_tree = ttk.Treeview(tools_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.current_tools_tree.heading(col, text=col)
            self.current_tools_tree.column(col, width=120)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        self.current_tools_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tools_container, orient='vertical', command=self.current_tools_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.current_tools_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.current_tools_tree.bind('<<TreeviewSelect>>', self.on_current_tool_select)
        
        # Action buttons
        button_frame = tk.Frame(tools_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_current_btn = tk.Button(button_frame, text="▶️ Start Selected",
                                         font=('Segoe UI', 9),
                                         bg=self.colors['success'], fg=self.colors['bg'],
                                         relief='flat', cursor='hand2',
                                         command=self.start_selected_current_tool)
        self.start_current_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_current_btn = tk.Button(button_frame, text="⏹️ Stop Selected",
                                        font=('Segoe UI', 9),
                                        bg=self.colors['danger'], fg=self.colors['bg'],
                                        relief='flat', cursor='hand2',
                                        command=self.stop_selected_current_tool)
        self.stop_current_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_current_btn = tk.Button(button_frame, text="🌐 Open URL",
                                         font=('Segoe UI', 9),
                                         bg=self.colors['primary'], fg=self.colors['bg'],
                                         relief='flat', cursor='hand2',
                                         command=self.open_selected_current_url)
        self.open_current_btn.pack(side=tk.LEFT, padx=5)
    
    def create_all_tools_display(self, parent):
        """Create all tools display"""
        # Tools container
        tools_container = tk.Frame(parent, bg=self.colors['card'])
        tools_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for all tools
        columns = ('Name', 'Mode', 'Status', 'Description')
        self.all_tools_tree = ttk.Treeview(tools_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.all_tools_tree.heading(col, text=col)
            self.all_tools_tree.column(col, width=120)
        
        self.all_tools_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tools_container, orient='vertical', command=self.all_tools_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.all_tools_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.all_tools_tree.bind('<<TreeviewSelect>>', self.on_all_tool_select)
        
        # Action buttons
        button_frame = tk.Frame(tools_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_all_btn = tk.Button(button_frame, text="▶️ Start Selected",
                                     font=('Segoe UI', 9),
                                     bg=self.colors['success'], fg=self.colors['bg'],
                                     relief='flat', cursor='hand2',
                                     command=self.start_selected_all_tool)
        self.start_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_all_btn = tk.Button(button_frame, text="⏹️ Stop Selected",
                                    font=('Segoe UI', 9),
                                    bg=self.colors['danger'], fg=self.colors['bg'],
                                    rel='flat', cursor='hand2',
                                    command=self.stop_selected_all_tool)
        self.stop_all_btn.pack(side=tk.LEFT, padx=5)
    
    def create_running_tools_display(self, parent):
        """Create running tools display"""
        # Tools container
        tools_container = tk.Frame(parent, bg=self.colors['card'])
        tools_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for running tools
        columns = ('Name', 'PID', 'Mode', 'Port', 'URL', 'Start Time')
        self.running_tools_tree = ttk.Treeview(tools_container, columns=columns, show='tree headings')
        
        # Configure columns
        for col in columns:
            self.running_tools_tree.heading(col, text=col)
            self.running_tools_tree.column(col, width=100)
        
        self.running_tools_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tools_container, orient='vertical', command=self.running_tools_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.running_tools_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.running_tools_tree.bind('<<TreeviewSelect>>', self.on_running_tool_select)
        
        # Action buttons
        button_frame = tk.Frame(tools_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stop_running_btn = tk.Button(button_frame, text="⏹️ Stop Selected",
                                        font=('Segoe UI', 9),
                                        bg=self.colors['danger'], fg=self.colors['bg'],
                                        relief='flat', cursor='hand2',
                                        command=self.stop_selected_running_tool)
        self.stop_running_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_all_running_btn = tk.Button(button_frame, text="⏹️ Stop All",
                                              font=('Segoe UI', 9),
                                              bg=self.colors['warning'], fg=self.colors['bg'],
                                              relief='flat', cursor='hand2',
                                              command=self.stop_all_running_tools)
        self.stop_all_running_btn.pack(side=tk.LEFT, padx=5)
    
    def create_status_monitoring(self, parent):
        """Create status monitoring section"""
        status_frame = tk.Frame(parent, bg=self.colors['card'])
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(status_frame, text="📊 Status Monitoring",
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['text'], bg=self.colors['card'])
        title_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Status container
        status_container = tk.Frame(status_frame, bg=self.colors['card'])
        status_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(
            status_container, height=10, width=120,
            bg=self.colors['bg'], fg=self.colors['text'],
            font=('Consolas', 9), relief='flat'
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        button_frame = tk.Frame(status_container, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.clear_status_btn = tk.Button(button_frame, text="🗑️ Clear Status",
                                         font=('Segoe UI', 9),
                                         bg=self.colors['warning'], fg=self.colors['bg'],
                                         relief='flat', cursor='hand2',
                                         command=self.clear_status)
        self.clear_status_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_status_btn = tk.Button(button_frame, text="📥 Export Status",
                                           font=('Segoe UI', 9),
                                           bg=self.colors['primary'], fg=self.colors['bg'],
                                           relief='flat', cursor='hand2',
                                           command=self.export_status)
        self.export_status_btn.pack(side=tk.LEFT, padx=5)
    
    def switch_mode(self, mode: LauncherMode):
        """Switch to a different mode"""
        try:
            # Stop all running tools
            self.stop_all_running_tools()
            
            # Update current mode
            unified_launcher.current_mode = mode
            self.mode_label.config(text=f"Mode: {mode.value}")
            
            # Update button colors
            for m in LauncherMode:
                btn = getattr(self, f"{m.value}_btn", None)
                if btn:
                    if m == mode:
                        btn.config(bg=self.colors['primary'], fg=self.colors['bg'])
                    else:
                        btn.config(bg=self.colors['card'], fg=self.colors['text'])
            
            # Refresh displays
            self.refresh_display()
            
            # Log mode switch
            self.log_status(f"Switched to {mode.value} mode")
            
            messagebox.showinfo("Mode Switch", f"Switched to {mode.value} mode successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch mode: {e}")
    
    def refresh_display(self):
        """Refresh all displays"""
        try:
            # Update current mode tools
            self.update_current_tools_display()
            
            # Update all tools display
            self.update_all_tools_display()
            
            # Update running tools display
            self.update_running_tools_display()
            
            # Update status
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh display: {e}")
    
    def update_current_tools_display(self):
        """Update current mode tools display"""
        try:
            # Clear existing items
            for item in self.current_tools_tree.get_children():
                self.current_tools_tree.delete(item)
            
            # Get tools for current mode
            current_tools = unified_launcher.get_tools_by_mode(unified_launcher.current_mode)
            
            for tool in current_tools:
                status_color = self.get_status_color(tool.status)
                last_run = tool.last_run.strftime('%H:%M:%S') if tool.last_run else 'Never'
                
                self.current_tools_tree.insert('', 'end', values=(
                    tool.name,
                    tool.status.value,
                    tool.port or '-',
                    tool.url or '-',
                    last_run
                ), tags=(tool.id,))
            
        except Exception as e:
            print(f"Error updating current tools display: {e}")
    
    def update_all_tools_display(self):
        """Update all tools display"""
        try:
            # Clear existing items
            for item in self.all_tools_tree.get_children():
                self.all_tools_tree.delete(item)
            
            # Add all tools
            for tool in unified_launcher.tools.values():
                self.all_tools_tree.insert('', 'end', values=(
                    tool.name,
                    tool.mode.value,
                    tool.status.value,
                    tool.description[:50] + '...' if len(tool.description) > 50 else tool.description
                ), tags=(tool.id,))
            
        except Exception as e:
            print(f"Error updating all tools display: {e}")
    
    def update_running_tools_display(self):
        """Update running tools display"""
        try:
            # Clear existing items
            for item in self.running_tools_tree.get_children():
                self.running_tools_tree.delete(item)
            
            # Add running tools
            running_tools = unified_launcher.get_running_tools()
            
            for tool in running_tools:
                start_time = "Unknown"
                if tool.last_run:
                    start_time = tool.last_run.strftime('%H:%M:%S')
                
                self.running_tools_tree.insert('', 'end', values=(
                    tool.name,
                    tool.process_id or '-',
                    tool.mode.value,
                    tool.port or '-',
                    tool.url or '-',
                    start_time
                ), tags=(tool.id,))
            
        except Exception as e:
            print(f"Error updating running tools display: {e}")
    
    def update_status(self):
        """Update status display"""
        try:
            # Get launcher status
            status = unified_launcher.get_launcher_status()
            
            # Format status information
            status_text = f"""Launcher Status - {status.get('timestamp', 'Unknown')}
===============================
Current Mode: {status.get('current_mode', 'Unknown')}
Total Tools: {status.get('total_tools', 0)}
Running Tools: {status.get('running_tools', 0)}

Tools by Mode:
"""
            
            tools_by_mode = status.get('tools_by_mode', {})
            for mode, count in tools_by_mode.items():
                status_text += f"  {mode}: {count}\n"
            
            status_text += f"""
Settings:
---------
Auto-start Tools: {', '.join(status.get('settings', {}).get('auto_start_tools', []))}
Check Dependencies: {status.get('settings', {}).get('check_dependencies', True)}
Max Concurrent Tools: {status.get('settings', {}).get('max_concurrent_tools', 5)}

Recent Events:
"""
            
            # Add recent events (simplified)
            status_text += f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Launcher status updated\n"
            status_text += f"[{datetime.now().strftime('%H:%M:%S')}] 📊 {status.get('running_tools', 0)} tools running\n"
            
            # Update status text
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, status_text)
            self.status_text.see(tk.END)
            
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def get_status_color(self, status: ToolStatus) -> str:
        """Get color for tool status"""
        colors = {
            ToolStatus.RUNNING: self.colors['success'],
            ToolStatus.STOPPED: self.colors['text_secondary'],
            ToolStatus.ERROR: self.colors['danger'],
            ToolStatus.AVAILABLE: self.colors['primary'],
            ToolStatus.UNKNOWN: self.colors['warning']
        }
        return colors.get(status, self.colors['text'])
    
    def on_current_tool_select(self, event):
        """Handle current tool selection"""
        try:
            selection = self.current_tools_tree.selection()
            if selection:
                item = self.current_tools_tree.item(selection[0])
                values = item['values']
                if len(values) >= 1:
                    # Find tool by name
                    tool_name = values[0]
                    for tool_id, tool in unified_launcher.tools.items():
                        if tool.name == tool_name:
                            self.selected_tool = tool_id
                            break
        except Exception as e:
            print(f"Error handling current tool selection: {e}")
    
    def on_all_tool_select(self, event):
        """Handle all tool selection"""
        try:
            selection = self.all_tools_tree.selection()
            if selection:
                item = self.all_tools_tree.item(selection[0])
                values = item['values']
                if len(values) >= 1:
                    # Find tool by name
                    tool_name = values[0]
                    for tool_id, tool in unified_launcher.tools.items():
                        if tool.name == tool_name:
                            self.selected_tool = tool_id
                            break
        except Exception as e:
            print(f"Error handling all tool selection: {e}")
    
    def on_running_tool_select(self, event):
        """Handle running tool selection"""
        try:
            selection = self.running_tools_tree.selection()
            if selection:
                item = self.running_tools_tree.item(selection[0])
                values = item['values']
                if len(values) >= 1:
                    # Find tool by name
                    tool_name = values[0]
                    for tool_id, tool in unified_launcher.tools.items():
                        if tool.name == tool_name:
                            self.selected_tool = tool_id
                            break
        except Exception as e:
            print(f"Error handling running tool selection: {e}")
    
    def start_selected_current_tool(self):
        """Start selected current mode tool"""
        if self.selected_tool:
            if unified_launcher.start_tool(self.selected_tool):
                messagebox.showinfo("Success", f"Tool started successfully!")
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to start tool")
        else:
            messagebox.showwarning("Warning", "Please select a tool to start")
    
    def stop_selected_current_tool(self):
        """Stop selected current mode tool"""
        if self.selected_tool:
            if unified_launcher.stop_tool(self.selected_tool):
                messagebox.showinfo("Success", f"Tool stopped successfully!")
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to stop tool")
        else:
            messagebox.showwarning("Warning", "Please select a tool to stop")
    
    def open_selected_current_url(self):
        """Open URL for selected current tool"""
        try:
            if self.selected_tool and self.selected_tool in unified_launcher.tools:
                tool = unified_launcher.tools[self.selected_tool]
                if tool.url:
                    webbrowser.open(tool.url)
                    self.log_status(f"Opened URL for {tool.name}: {tool.url}")
                else:
                    messagebox.showinfo("Info", "No URL available for this tool")
            else:
                messagebox.showwarning("Warning", "Please select a tool")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open URL: {e}")
    
    def start_selected_all_tool(self):
        """Start selected tool from all tools"""
        if self.selected_tool:
            if unified_launcher.start_tool(self.selected_tool):
                messagebox.showinfo("Success", f"Tool started successfully!")
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to start tool")
        else:
            messagebox.showwarning("Warning", "Please select a tool to start")
    
    def stop_selected_all_tool(self):
        """Stop selected tool from all tools"""
        if self.selected_tool:
            if unified_launcher.stop_tool(self.selected_tool):
                messagebox.showinfo("Success", f"Tool stopped successfully!")
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to stop tool")
        else:
            messagebox.showwarning("Warning", "Please select a tool to stop")
    
    def stop_selected_running_tool(self):
        """Stop selected running tool"""
        if self.selected_tool:
            if unified_launcher.stop_tool(self.selected_tool):
                messagebox.showinfo("Success", f"Tool stopped successfully!")
                self.refresh_display()
            else:
                messagebox.showerror("Error", "Failed to stop tool")
        else:
            messagebox.showwarning("Warning", "Please select a tool to stop")
    
    def stop_all_running_tools(self):
        """Stop all running tools"""
        try:
            running_tools = unified_launcher.get_running_tools()
            if not running_tools:
                messagebox.showinfo("Info", "No tools are currently running")
                return
            
            if messagebox.askyesno("Stop All Tools", f"Stop all {len(running_tools)} running tools?"):
                for tool in running_tools:
                    unified_launcher.stop_tool(tool.id)
                
                messagebox.showinfo("Success", f"Stopped {len(running_tools)} tools")
                self.refresh_display()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop all tools: {e}")
    
    def clear_status(self):
        """Clear status display"""
        try:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Status cleared\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear status: {e}")
    
    def export_status(self):
        """Export status to file"""
        try:
            status_content = self.status_text.get(1.0, tk.END)
            
            # Save to file
            status_file = Path(__file__).parent / f"launcher_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(status_file, 'w') as f:
                f.write(status_content)
            
            messagebox.showinfo("Export", f"Status exported to {status_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export status: {e}")
    
    def open_settings(self):
        """Open settings dialog"""
        try:
            # Create settings dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Launcher Settings")
            dialog.geometry("500x400")
            dialog.configure(bg=self.colors['card'])
            
            # Settings title
            tk.Label(dialog, text="Launcher Settings",
                    font=('Segoe UI', 12, 'bold'),
                    bg=self.colors['card'], fg=self.colors['text']).pack(pady=10)
            
            # Settings content
            settings = unified_launcher.settings
            settings_content = f"""Current Settings:
================
Default Mode: {settings.get('default_mode', 'dashboard')}
Auto-start Tools: {', '.join(settings.get('auto_start_tools', []))}
Auto Discover: {settings.get('auto_discover', True)}
Check Dependencies: {settings.get('check_dependencies', True)}
Health Check Interval: {settings.get('health_check_interval', 30)}s
Max Concurrent Tools: {settings.get('max_concurrent_tools', 5)}
Tool Timeout: {settings.get('tool_timeout', 60)}s

Preferred Ports:
- Streamlined Dashboard: {settings.get('preferred_ports', {}).get('streamlined_dashboard', 8080)}
- PC Auth GUI: {settings.get('preferred_ports', {}).get('pc_auth_gui', 8081)}
- Streamlined Homelab: {settings.get('preferred_ports', {}).get('streamlined_homelab', 8082)}
- PC Auth System: {settings.get('preferred_ports', {}).get('pc_auth_system', 8083)}

Solo Mode Tools: {', '.join(settings.get('solo_mode_tools', []))}
Dashboard Mode Tools: {', '.join(settings.get('dashboard_mode_tools', []))}
Legacy Tools Path: {settings.get('legacy_tools_path', 'N/A')}
"""
            
            settings_text = scrolledtext.ScrolledText(
                dialog, height=15, width=60,
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Consolas', 9), relief='flat'
            )
            settings_text.pack(padx=10, pady=10)
            settings_text.insert(tk.END, settings_content)
            settings_text.config(state='disabled')
            
            # Close button
            tk.Button(dialog, text="Close", bg=self.colors['primary'], fg=self.colors['bg'],
                     command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def quit_application(self):
        """Quit the application"""
        try:
            if messagebox.askyesno("Quit", "Stop all tools and quit the launcher?"):
                # Stop all running tools
                self.stop_all_running_tools()
                
                # Close application
                self.root.quit()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to quit: {e}")
    
    def log_status(self, message: str):
        """Log a status message"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.status_text.see(tk.END)
        except:
            pass
    
    def start_gui_monitoring(self):
        """Start GUI monitoring"""
        self.refresh_active = True
        self.refresh_thread = threading.Thread(target=self._gui_monitoring_loop, daemon=True)
        self.refresh_thread.start()
    
    def _gui_monitoring_loop(self):
        """GUI monitoring loop"""
        while self.refresh_active:
            try:
                self.refresh_display()
                time.sleep(30)  # Refresh every 30 seconds
            except Exception as e:
                print(f"GUI monitoring error: {e}")
                time.sleep(10)

if __name__ == '__main__':
    # Create GUI window
    root = tk.Tk()
    gui = UnifiedLauncherGUI(root)
    
    # Handle window closing
    def on_closing():
        try:
            gui.stop_all_running_tools()
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()
