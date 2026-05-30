#!/usr/bin/env python3
"""
Homelab Bidirectional Launcher
Complete launcher with Windows Assistant integration and unified dark theme
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
import requests
from datetime import datetime

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

class HomelabBidirectionalLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 Homelab Bidirectional Launcher")
        self.root.geometry("1400x900")
        self.root.minsize(900, 700)
        
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
        self.portal_process = None
        self.assistant_process = None
        
        # Integration status
        self.integration_status = {
            'portal_running': False,
            'assistant_running': False,
            'integration_active': False,
            'last_check': None
        }
        
        # Tool definitions with bidirectional capabilities
        self.tools = {
            "Core Services": {
                "Homelab Portal": {
                    "path": "Core Services\\homelab_portal.py",
                    "description": "Main portal with bidirectional assistant integration",
                    "icon": "🌐",
                    "category": "Core",
                    "dependencies": ["psutil", "PIL", "flask", "flask-cors"],
                    "bidirectional": True
                },
                "Resource Sharing": {
                    "path": "Core Services\\bidirectional_resource_sharing.py", 
                    "description": "P2P resource sharing with assistant coordination",
                    "icon": "🔄",
                    "category": "Core",
                    "dependencies": ["psutil", "socket"],
                    "bidirectional": True
                },
                "System Monitor": {
                    "path": "Core Services\\unified_monitoring.py",
                    "description": "System monitoring with assistant alerts",
                    "icon": "📊",
                    "category": "Monitoring",
                    "dependencies": ["psutil", "matplotlib"],
                    "bidirectional": True
                }
            },
            "Assistant & Integration": {
                "Windows Assistant": {
                    "path": "Windows Assistant\\main.py",
                    "description": "Modern Clippy-style assistant with portal integration",
                    "icon": "📎",
                    "category": "Assistant",
                    "dependencies": ["PIL", "psutil", "pywin32", "plyer", "requests"],
                    "bidirectional": True
                },
                "Integration Monitor": {
                    "path": "Core Services\\windows_assistant_integration.py",
                    "description": "Monitor and manage assistant-portal integration",
                    "icon": "🔗",
                    "category": "Integration",
                    "dependencies": ["threading", "requests", "json"],
                    "bidirectional": True
                }
            },
            "Monitoring Tools": {
                "CPU Monitor": {
                    "path": "Cpu Monitor\\cpu_monitor.py",
                    "description": "Real-time CPU monitoring with assistant notifications",
                    "icon": "💻",
                    "category": "Monitoring", 
                    "dependencies": ["psutil", "matplotlib", "PIL"],
                    "bidirectional": True
                },
                "GPU Monitor": {
                    "path": "Gpu Monitor\\gpu_monitor.py",
                    "description": "GPU monitoring with assistant resource coordination",
                    "icon": "🎮",
                    "category": "Monitoring",
                    "dependencies": ["psutil", "matplotlib", "PIL", "GPUtil"],
                    "bidirectional": True
                },
                "Network Monitor": {
                    "path": "Network Monitor\\network_monitor.py", 
                    "description": "Network monitoring with assistant connectivity alerts",
                    "icon": "🌍",
                    "category": "Monitoring",
                    "dependencies": ["psutil", "matplotlib", "PIL"],
                    "bidirectional": True
                }
            },
            "System Tools": {
                "RAM Cleaner": {
                    "path": "Ram clean up\\ram_monitor_gui.py",
                    "description": "RAM optimization with assistant automation",
                    "icon": "🧹",
                    "category": "Utilities",
                    "dependencies": ["psutil", "matplotlib", "PIL"],
                    "bidirectional": True
                },
                "File Manager": {
                    "path": "Core Services\\data_persistence.py",
                    "description": "File management with assistant help",
                    "icon": "📁",
                    "category": "Utilities",
                    "dependencies": ["sqlite3", "json"],
                    "bidirectional": False
                }
            },
            "Advanced Tools": {
                "Automation Framework": {
                    "path": "Core Services\\automation_framework.py",
                    "description": "Automation with assistant triggers",
                    "icon": "⚙️",
                    "category": "Automation",
                    "dependencies": ["threading", "subprocess", "json"],
                    "bidirectional": True
                },
                "Security Manager": {
                    "path": "Core Services\\advanced_security.py",
                    "description": "Security monitoring with assistant alerts",
                    "icon": "🔒",
                    "category": "Security",
                    "dependencies": ["hashlib", "cryptography"],
                    "bidirectional": True
                }
            }
        }
        
        self.setup_gui()
        self.start_status_monitor()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with integration status
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill='x', pady=(0, 20))
        
        if THEME_AVAILABLE:
            title_label = ttk.Label(header_frame, text="🏠 Homelab Bidirectional Launcher", 
                                  style='Title.TLabel')
        else:
            title_label = ttk.Label(header_frame, text="🏠 Homelab Bidirectional Launcher",
                                  font=('Segoe UI', 20, 'bold'), bg='#1a1a1a', fg='#00d4ff')
        title_label.pack(side='left')
        
        # Integration status indicator
        self.integration_status_var = tk.StringVar(value="Initializing...")
        if THEME_AVAILABLE:
            status_label = ttk.Label(header_frame, textvariable=self.integration_status_var,
                                   style='Secondary.TLabel')
        else:
            status_label = ttk.Label(header_frame, textvariable=self.integration_status_var,
                                   font=('Segoe UI', 10), bg='#1a1a1a', fg='#b0b0b0')
        status_label.pack(side='right')
        
        # Integration status panel
        self.create_integration_panel(main_container)
        
        # Create notebook for tool categories
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))
        
        # Create tabs for each category
        for category_name, tools in self.tools.items():
            self.create_category_tab(category_name, tools)
        
        # Control panel
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill='x', pady=(20, 0))
        
        # Launch buttons
        if THEME_AVAILABLE:
            launch_btn = ttk.Button(control_frame, text="🚀 Launch Selected Tool",
                                  command=self.launch_selected_tool, style='Primary.TButton')
            stop_btn = ttk.Button(control_frame, text="⏹️ Stop Selected Tool",
                                command=self.stop_selected_tool, style='Danger.TButton')
            refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Status",
                                   command=self.refresh_status, style='Secondary.TButton')
            launch_all_btn = ttk.Button(control_frame, text="🚀 Launch Bidirectional Stack",
                                      command=self.launch_bidirectional_stack, style='Success.TButton')
        else:
            launch_btn = ttk.Button(control_frame, text="🚀 Launch Selected Tool",
                                  command=self.launch_selected_tool)
            stop_btn = ttk.Button(control_frame, text="⏹️ Stop Selected Tool",
                                command=self.stop_selected_tool)
            refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Status",
                                   command=self.refresh_status)
            launch_all_btn = ttk.Button(control_frame, text="🚀 Launch Bidirectional Stack",
                                      command=self.launch_bidirectional_stack)
        
        launch_btn.pack(side='left', padx=(0, 10))
        stop_btn.pack(side='left', padx=(0, 10))
        refresh_btn.pack(side='left', padx=(0, 10))
        launch_all_btn.pack(side='right')
        
    def create_integration_panel(self, parent):
        """Create integration status panel"""
        panel_frame = ttk.LabelFrame(parent, text="🔗 Integration Status", padding=10)
        panel_frame.pack(fill='x', pady=(0, 20))
        
        # Status indicators
        indicators_frame = ttk.Frame(panel_frame)
        indicators_frame.pack(fill='x')
        
        # Portal status
        self.portal_status_var = tk.StringVar(value="🔴 Portal: Offline")
        if THEME_AVAILABLE:
            portal_label = ttk.Label(indicators_frame, textvariable=self.portal_status_var,
                                   style='Info.TLabel')
        else:
            portal_label = ttk.Label(indicators_frame, textvariable=self.portal_status_var,
                                   font=('Segoe UI', 11, 'bold'), bg='#2d2d2d', fg='#00d4ff')
        portal_label.pack(side='left', padx=(0, 20))
        
        # Assistant status
        self.assistant_status_var = tk.StringVar(value="🔴 Assistant: Offline")
        if THEME_AVAILABLE:
            assistant_label = ttk.Label(indicators_frame, textvariable=self.assistant_status_var,
                                      style='Info.TLabel')
        else:
            assistant_label = ttk.Label(indicators_frame, textvariable=self.assistant_status_var,
                                      font=('Segoe UI', 11, 'bold'), bg='#2d2d2d', fg='#00d4ff')
        assistant_label.pack(side='left', padx=(0, 20))
        
        # Integration status
        self.connection_status_var = tk.StringVar(value="🔴 Integration: Inactive")
        if THEME_AVAILABLE:
            connection_label = ttk.Label(indicators_frame, textvariable=self.connection_status_var,
                                       style='Info.TLabel')
        else:
            connection_label = ttk.Label(indicators_frame, textvariable=self.connection_status_var,
                                       font=('Segoe UI', 11, 'bold'), bg='#2d2d2d', fg='#00d4ff')
        connection_label.pack(side='left')
        
        # Action buttons
        actions_frame = ttk.Frame(panel_frame)
        actions_frame.pack(fill='x', pady=(10, 0))
        
        if THEME_AVAILABLE:
            test_btn = ttk.Button(actions_frame, text="🧪 Test Integration",
                               command=self.test_integration, style='Secondary.TButton')
            sync_btn = ttk.Button(actions_frame, text="🔄 Sync Status",
                              command=self.sync_integration_status, style='Secondary.TButton')
        else:
            test_btn = ttk.Button(actions_frame, text="🧪 Test Integration",
                               command=self.test_integration)
            sync_btn = ttk.Button(actions_frame, text="🔄 Sync Status",
                              command=self.sync_integration_status)
        
        test_btn.pack(side='left', padx=(0, 10))
        sync_btn.pack(side='left')
        
    def create_category_tab(self, category_name, tools):
        """Create a tab for a tool category"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=category_name)
        
        # Create treeview for tools
        columns = ('Tool', 'Description', 'Status', 'Integration', 'Action')
        self.tree = ttk.Treeview(tab_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Tool', text='Tool')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Integration', text='Integration')
        self.tree.heading('Action', text='Action')
        
        self.tree.column('Tool', width=180)
        self.tree.column('Description', width=350)
        self.tree.column('Status', width=100)
        self.tree.column('Integration', width=100)
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
            integration = "✅ Yes" if tool_info.get('bidirectional', False) else "⚪ No"
            
            self.tree.insert('', 'end', iid=tool_name, values=(
                f"{tool_info['icon']} {tool_name}",
                tool_info['description'],
                status,
                integration,
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
    
    def start_status_monitor(self):
        """Start monitoring integration status"""
        def monitor():
            while True:
                try:
                    self.check_integration_status()
                    time.sleep(5)  # Check every 5 seconds
                except:
                    time.sleep(10)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def check_integration_status(self):
        """Check the status of portal and assistant integration"""
        try:
            # Check portal
            portal_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('homelab_portal' in ' '.join(proc.info['cmdline']) for cmd in proc.info['cmdline']):
                        portal_running = True
                        break
                except:
                    continue
            
            # Check assistant
            assistant_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('main.py' in ' '.join(proc.info['cmdline']) and 'Windows Assistant' in ' '.join(proc.info['cmdline']) for cmd in proc.info['cmdline']):
                        assistant_running = True
                        break
                except:
                    continue
            
            # Check integration via API
            integration_active = False
            if portal_running:
                try:
                    response = requests.get('http://localhost:8080/api/assistant/integration', timeout=2)
                    if response.status_code == 200:
                        integration_active = response.json().get('integration_active', False)
                except:
                    pass
            
            # Update status
            self.integration_status['portal_running'] = portal_running
            self.integration_status['assistant_running'] = assistant_running
            self.integration_status['integration_active'] = integration_active
            self.integration_status['last_check'] = datetime.now()
            
            # Update UI
            self.portal_status_var.set(f"{'🟢' if portal_running else '🔴'} Portal: {'Online' if portal_running else 'Offline'}")
            self.assistant_status_var.set(f"{'🟢' if assistant_running else '🔴'} Assistant: {'Online' if assistant_running else 'Offline'}")
            self.connection_status_var.set(f"{'🟢' if integration_active else '🔴'} Integration: {'Active' if integration_active else 'Inactive'}")
            
            overall_status = "Connected" if portal_running and assistant_running and integration_active else "Partial" if (portal_running or assistant_running) else "Disconnected"
            self.integration_status_var.set(f"Status: {overall_status}")
            
        except Exception as e:
            print(f"Status check error: {e}")
    
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
            
            # Launch in subprocess
            process = subprocess.Popen([sys.executable, str(tool_path)], 
                                    cwd=str(tool_path.parent))
            
            # Track the process
            self.running_tools[tool_name] = process
            
            # Special handling for portal and assistant
            if tool_name == "Homelab Portal":
                self.portal_process = process
            elif tool_name == "Windows Assistant":
                self.assistant_process = process
            
            # Update status
            self.refresh_status()
            
            messagebox.showinfo("Success", f"{tool_name} launched successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool_name}: {e}")
    
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
                
                # Special handling
                if tool_name == "Homelab Portal":
                    self.portal_process = None
                elif tool_name == "Windows Assistant":
                    self.assistant_process = None
                
                self.refresh_status()
                messagebox.showinfo("Success", f"{tool_name} stopped")
            except:
                messagebox.showerror("Error", f"Failed to stop {tool_name}")
        else:
            messagebox.showwarning("Not Running", f"{tool_name} is not being tracked by launcher")
    
    def launch_bidirectional_stack(self):
        """Launch the complete bidirectional integration stack"""
        launched = []
        failed = []
        
        # Launch in order: Portal first, then Assistant
        launch_order = ["Homelab Portal", "Windows Assistant"]
        
        for tool_name in launch_order:
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
                    time.sleep(2)  # Give each tool time to start
                except:
                    failed.append(tool_name)
        
        if launched and not failed:
            messagebox.showinfo("Success", f"Bidirectional stack launched: {', '.join(launched)}")
        elif launched and failed:
            messagebox.showwarning("Partial Success", 
                                f"Launched: {', '.join(launched)}\nFailed: {', '.join(failed)}")
        else:
            messagebox.showerror("Error", "Failed to launch bidirectional stack")
    
    def refresh_status(self):
        """Refresh tool and integration status"""
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
                            current_values[3],
                            current_values[4]
                        ))
                except:
                    pass
        
        self.check_integration_status()
    
    def test_integration(self):
        """Test the bidirectional integration"""
        try:
            if not self.integration_status['portal_running']:
                messagebox.showwarning("Portal Offline", "Please start the Homelab Portal first")
                return
            
            # Test API endpoints
            response = requests.get('http://localhost:8080/api/assistant/integration', timeout=5)
            if response.status_code == 200:
                status = response.json()
                messagebox.showinfo("Integration Test", 
                    f"✅ Integration Status: Active\n"
                    f"Registered Assistants: {status.get('registered_assistants', 0)}\n"
                    f"Pending Commands: {status.get('pending_commands', 0)}")
            else:
                messagebox.showerror("Test Failed", f"API returned status {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Test Error", f"Integration test failed: {e}")
    
    def sync_integration_status(self):
        """Force sync integration status"""
        self.check_integration_status()
        messagebox.showinfo("Sync Complete", "Integration status synchronized")
    
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
        launcher = HomelabBidirectionalLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        messagebox.showerror("Fatal Error", f"Launcher failed to start: {e}")

if __name__ == "__main__":
    main()
