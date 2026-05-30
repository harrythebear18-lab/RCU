#!/usr/bin/env python3
"""
RAM Sharing GUI - Homelab Tools
Graphical interface for sharing RAM between PCs
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
from datetime import datetime
import json

class RAMSharingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Homelab RAM Sharing Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.is_server_running = False
        self.is_client_connected = False
        self.current_action = None
        
        # Style configuration
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start status monitoring
        self.update_status()
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        button_color = '#4a4a4a'
        accent_color = '#0078d7'
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=button_color, foreground=fg_color)
        style.map('TButton', background=[('active', accent_color)])
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=accent_color)
        style.configure('Status.TLabel', font=('Segoe UI', 10))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="🖥️ Homelab RAM Sharing Manager", style='Header.TLabel').pack(side='left')
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, width=350)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Server Section
        server_frame = ttk.LabelFrame(left_panel, text="📡 Server Setup (PC 1: 192.168.1.186)")
        server_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(server_frame, text="RAM Size (GB):").pack(anchor='w', padx=5, pady=2)
        self.ram_size_var = tk.StringVar(value="4")
        ram_combo = ttk.Combobox(server_frame, textvariable=self.ram_size_var, 
                                values=["2", "4", "8", "16"], width=10)
        ram_combo.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(server_frame, text="Drive Letter:").pack(anchor='w', padx=5, pady=2)
        self.drive_letter_var = tk.StringVar(value="R")
        drive_combo = ttk.Combobox(server_frame, textvariable=self.drive_letter_var,
                                  values=["R", "S", "T", "U"], width=10)
        drive_combo.pack(anchor='w', padx=5, pady=2)
        
        self.server_status_var = tk.StringVar(value="❌ Server Not Running")
        ttk.Label(server_frame, textvariable=self.server_status_var, 
                 style='Status.TLabel').pack(anchor='w', padx=5, pady=5)
        
        button_frame = ttk.Frame(server_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_server_btn = ttk.Button(button_frame, text="🚀 Start Server", 
                                          command=self.start_server)
        self.start_server_btn.pack(side='left', padx=2)
        
        self.stop_server_btn = ttk.Button(button_frame, text="⏹️ Stop Server", 
                                         command=self.stop_server, state='disabled')
        self.stop_server_btn.pack(side='left', padx=2)
        
        # Client Section
        client_frame = ttk.LabelFrame(left_panel, text="🔗 Client Connection (PC 2: 192.168.1.132)")
        client_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(client_frame, text="Server IP:").pack(anchor='w', padx=5, pady=2)
        self.server_ip_var = tk.StringVar(value="192.168.1.186")
        ttk.Entry(client_frame, textvariable=self.server_ip_var, width=15).pack(anchor='w', padx=5, pady=2)
        
        self.client_status_var = tk.StringVar(value="❌ Not Connected")
        ttk.Label(client_frame, textvariable=self.client_status_var,
                 style='Status.TLabel').pack(anchor='w', padx=5, pady=5)
        
        client_button_frame = ttk.Frame(client_frame)
        client_button_frame.pack(fill='x', padx=5, pady=5)
        
        self.connect_btn = ttk.Button(client_button_frame, text="🔌 Connect", 
                                     command=self.connect_to_server)
        self.connect_btn.pack(side='left', padx=2)
        
        self.disconnect_btn = ttk.Button(client_button_frame, text="🔌 Disconnect", 
                                        command=self.disconnect_from_server, state='disabled')
        self.disconnect_btn.pack(side='left', padx=2)
        
        # Performance Section
        perf_frame = ttk.LabelFrame(left_panel, text="⚡ Performance")
        perf_frame.pack(fill='x', pady=(0, 10))
        
        self.perf_info_var = tk.StringVar(value="No performance data available")
        ttk.Label(perf_frame, textvariable=self.perf_info_var,
                 style='Status.TLabel').pack(anchor='w', padx=5, pady=5)
        
        self.test_perf_btn = ttk.Button(perf_frame, text="🧪 Test Performance",
                                       command=self.test_performance)
        self.test_perf_btn.pack(anchor='w', padx=5, pady=5)
        
        # Right panel - Log
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True)
        
        log_frame = ttk.LabelFrame(right_panel, text="📋 Activity Log")
        log_frame.pack(fill='both', expand=True)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                bg='#1e1e1e', fg='#ffffff',
                                                font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="🧹 Cleanup All", 
                  command=self.cleanup_all).pack(side='left', padx=5)
        ttk.Button(bottom_frame, text="📖 Help", 
                  command=self.show_help).pack(side='left', padx=5)
        ttk.Button(bottom_frame, text="❌ Exit", 
                  command=self.exit_app).pack(side='right', padx=5)
        
        # Initial log entry
        self.log("RAM Sharing GUI initialized")
        self.log("Ready to set up RAM sharing between PCs")
        
    def log(self, message, level="INFO"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "#ffffff",
            "SUCCESS": "#00ff00", 
            "ERROR": "#ff0000",
            "WARNING": "#ffff00"
        }
        color = color_map.get(level, "#ffffff")
        
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        
        # Auto-limit log size
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 500:
            self.log_text.delete("1.0", "100.0")
            
    def run_command(self, command, capture_output=True):
        """Run a command and return result"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, capture_output=True, 
                                      text=True, timeout=60)
                return result.returncode == 0, result.stdout, result.stderr
            else:
                subprocess.run(command, shell=True, timeout=60)
                return True, "", ""
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
            
    def start_server(self):
        """Start RAM sharing server"""
        if self.current_action:
            messagebox.showwarning("Busy", "Another action is in progress")
            return
            
        self.current_action = "start_server"
        self.start_server_btn.config(state='disabled')
        self.log("Starting RAM sharing server...")
        
        def run_server():
            try:
                # Run the PowerShell setup script
                script_path = os.path.join(os.path.dirname(__file__), "Robust_RAM_Sharing.ps1")
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action setup -RAMSizeGB {self.ram_size_var.get()} -DriveLetter {self.drive_letter_var.get()}'
                
                success, stdout, stderr = self.run_command(command)
                
                if success:
                    self.log("Server started successfully", "SUCCESS")
                    self.is_server_running = True
                    self.server_status_var.set("✅ Server Running")
                    self.stop_server_btn.config(state='normal')
                else:
                    self.log(f"Server start failed: {stderr}", "ERROR")
                    self.server_status_var.set("❌ Server Failed")
                    
            except Exception as e:
                self.log(f"Error starting server: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                self.start_server_btn.config(state='normal')
                
        threading.Thread(target=run_server, daemon=True).start()
        
    def stop_server(self):
        """Stop RAM sharing server"""
        if self.current_action:
            messagebox.showwarning("Busy", "Another action is in progress")
            return
            
        self.current_action = "stop_server"
        self.stop_server_btn.config(state='disabled')
        self.log("Stopping RAM sharing server...")
        
        def stop_server_thread():
            try:
                script_path = os.path.join(os.path.dirname(__file__), "Robust_RAM_Sharing.ps1")
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action cleanup'
                
                success, stdout, stderr = self.run_command(command)
                
                if success:
                    self.log("Server stopped successfully", "SUCCESS")
                    self.is_server_running = False
                    self.server_status_var.set("❌ Server Stopped")
                    self.start_server_btn.config(state='normal')
                    self.stop_server_btn.config(state='disabled')
                else:
                    self.log(f"Server stop failed: {stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"Error stopping server: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                self.stop_server_btn.config(state='normal')
                
        threading.Thread(target=stop_server_thread, daemon=True).start()
        
    def connect_to_server(self):
        """Connect to RAM sharing server"""
        if self.current_action:
            messagebox.showwarning("Busy", "Another action is in progress")
            return
            
        self.current_action = "connect"
        self.connect_btn.config(state='disabled')
        self.log(f"Connecting to server at {self.server_ip_var.get()}...")
        
        def connect_thread():
            try:
                script_path = os.path.join(os.path.dirname(__file__), "Robust_RAM_Sharing.ps1")
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action map -TargetIP {self.server_ip_var.get()}'
                
                success, stdout, stderr = self.run_command(command)
                
                if success:
                    self.log("Connected to server successfully", "SUCCESS")
                    self.is_client_connected = True
                    self.client_status_var.set("✅ Connected")
                    self.disconnect_btn.config(state='normal')
                else:
                    self.log(f"Connection failed: {stderr}", "ERROR")
                    self.client_status_var.set("❌ Connection Failed")
                    
            except Exception as e:
                self.log(f"Error connecting: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                self.connect_btn.config(state='normal')
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_from_server(self):
        """Disconnect from RAM sharing server"""
        if self.current_action:
            messagebox.showwarning("Busy", "Another action is in progress")
            return
            
        self.current_action = "disconnect"
        self.disconnect_btn.config(state='disabled')
        self.log("Disconnecting from server...")
        
        def disconnect_thread():
            try:
                # Remove network drives
                success, _, _ = self.run_command('net use * /delete /y')
                
                if success:
                    self.log("Disconnected successfully", "SUCCESS")
                    self.is_client_connected = False
                    self.client_status_var.set("❌ Disconnected")
                    self.connect_btn.config(state='normal')
                    self.disconnect_btn.config(state='disabled')
                else:
                    self.log("Disconnect completed with warnings", "WARNING")
                    
            except Exception as e:
                self.log(f"Error disconnecting: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                self.disconnect_btn.config(state='normal')
                
        threading.Thread(target=disconnect_thread, daemon=True).start()
        
    def test_performance(self):
        """Test RAM sharing performance"""
        if self.current_action:
            messagebox.showwarning("Busy", "Another action is in progress")
            return
            
        self.current_action = "test_perf"
        self.test_perf_btn.config(state='disabled')
        self.log("Testing performance...")
        
        def test_thread():
            try:
                script_path = os.path.join(os.path.dirname(__file__), "Robust_RAM_Sharing.ps1")
                command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action test -DriveLetter {self.drive_letter_var.get()}'
                
                success, stdout, stderr = self.run_command(command)
                
                if success:
                    # Parse performance results
                    lines = stdout.split('\n')
                    perf_info = []
                    for line in lines:
                        if 'Write:' in line or 'Read:' in line:
                            perf_info.append(line.strip())
                    
                    if perf_info:
                        perf_text = '\n'.join(perf_info)
                        self.perf_info_var.set(perf_text)
                        self.log("Performance test completed", "SUCCESS")
                        self.log(perf_text)
                    else:
                        self.perf_info_var.set("Test completed but no data")
                        self.log("Performance test completed but no data found", "WARNING")
                else:
                    self.log(f"Performance test failed: {stderr}", "ERROR")
                    self.perf_info_var.set("Test failed")
                    
            except Exception as e:
                self.log(f"Error testing performance: {str(e)}", "ERROR")
            finally:
                self.current_action = None
                self.test_perf_btn.config(state='normal')
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def cleanup_all(self):
        """Clean up all RAM sharing components"""
        if messagebox.askyesno("Confirm Cleanup", "This will remove all RAM sharing components. Continue?"):
            if self.current_action:
                messagebox.showwarning("Busy", "Another action is in progress")
                return
                
            self.current_action = "cleanup"
            self.log("Starting cleanup...")
            
            def cleanup_thread():
                try:
                    script_path = os.path.join(os.path.dirname(__file__), "Robust_RAM_Sharing.ps1")
                    command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action cleanup'
                    
                    success, stdout, stderr = self.run_command(command)
                    
                    if success:
                        self.log("Cleanup completed successfully", "SUCCESS")
                        self.is_server_running = False
                        self.is_client_connected = False
                        self.server_status_var.set("❌ Server Stopped")
                        self.client_status_var.set("❌ Not Connected")
                        self.start_server_btn.config(state='normal')
                        self.stop_server_btn.config(state='disabled')
                        self.connect_btn.config(state='normal')
                        self.disconnect_btn.config(state='disabled')
                    else:
                        self.log(f"Cleanup failed: {stderr}", "ERROR")
                        
                except Exception as e:
                    self.log(f"Error during cleanup: {str(e)}", "ERROR")
                finally:
                    self.current_action = None
                    
            threading.Thread(target=cleanup_thread, daemon=True).start()
            
    def show_help(self):
        """Show help dialog"""
        help_text = """
Homelab RAM Sharing Manager Help

SERVER SETUP (PC 1 - 192.168.1.186):
1. Select RAM size and drive letter
2. Click 'Start Server' to create and share RAM disk
3. Server will create both SMB and iSCSI shares

CLIENT CONNECTION (PC 2 - 192.168.1.132):
1. Ensure server IP is correct (192.168.1.186)
2. Click 'Connect' to map shared RAM disk
3. System will try iSCSI first, then SMB share

PERFORMANCE:
- Click 'Test Performance' to benchmark
- Expect 100+ MB/s on gigabit network
- iSCSI generally faster than SMB

TROUBLESHOOTING:
- Run as Administrator on both PCs
- Ensure both PCs on same network
- Check Windows Firewall settings
- Verify network connectivity

CLEANUP:
- Use 'Cleanup All' to remove all components
- Stops server and removes all shares
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - RAM Sharing")
        help_window.geometry("500x400")
        help_window.configure(bg='#2b2b2b')
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD,
                                              bg='#1e1e1e', fg='#ffffff',
                                              font=('Segoe UI', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        ttk.Button(help_window, text="Close", 
                  command=help_window.destroy).pack(pady=10)
                  
    def exit_app(self):
        """Exit the application"""
        if self.current_action:
            messagebox.showwarning("Busy", "Cannot exit while action is in progress")
            return
            
        if messagebox.askyesno("Exit", "Exit RAM Sharing Manager?"):
            self.root.destroy()
            
    def update_status(self):
        """Update status indicators"""
        # This could be enhanced to check actual system status
        self.root.after(5000, self.update_status)  # Update every 5 seconds

def main():
    """Main entry point"""
    root = tk.Tk()
    app = RAMSharingGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
