#!/usr/bin/env python3
"""
Working GUI Homelab Launcher
Fixed launcher with all working homelab systems and tools.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from pathlib import Path

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Working Homelab Launcher")
        self.root.geometry("520x980")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, True)
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0'
        }
        
        # Center the window
        self.center_window()
        
        # Create widgets
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create modern launcher widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title and icon
        title_label = tk.Label(header_frame, text="🏠 Working Homelab Launcher", 
                              font=('Segoe UI', 22, 'bold'), 
                              fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(pady=(30, 5))
        
        subtitle_label = tk.Label(header_frame, text="All tools are working - choose your system:", 
                                 font=('Segoe UI', 11), 
                                 fg=self.colors['success'], bg=self.colors['bg'])
        subtitle_label.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # === WORKING HOMELAB SYSTEMS ===
        
        # PC Authentication GUI button (RECOMMENDED)
        pc_auth_button = tk.Button(content_frame, text="🔐 PC Authentication GUI ⭐", 
                                  font=('Segoe UI', 14, 'bold'), 
                                  bg='#8e44ad', fg=self.colors['bg'],
                                  relief='flat', bd=0, cursor='hand2',
                                  command=self.launch_pc_auth_gui)
        pc_auth_button.pack(fill=tk.X, pady=(20, 10))
        
        # Streamlined Dashboard button
        streamlined_button = tk.Button(content_frame, text="📊 Streamlined Dashboard", 
                                     font=('Segoe UI', 12, 'bold'), 
                                     bg='#e74c3c', fg=self.colors['bg'],
                                     relief='flat', bd=0, cursor='hand2',
                                     command=self.launch_streamlined_dashboard)
        streamlined_button.pack(fill=tk.X, pady=10)
        
        # Overclocking Dashboard button
        overclock_button = tk.Button(content_frame, text="� Overclocking Dashboard", 
                                     font=('Segoe UI', 12, 'bold'), 
                                     bg='#ff6b35', fg=self.colors['bg'],
                                     relief='flat', bd=0, cursor='hand2',
                                     command=self.launch_overclock_dashboard)
        overclock_button.pack(fill=tk.X, pady=10)
        
        # Resource Optimizer button
        resource_button = tk.Button(content_frame, text="⚡ Resource Optimizer", 
                                   font=('Segoe UI', 12, 'bold'), 
                                   bg='#00d4ff', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.launch_resource_optimizer)
        resource_button.pack(fill=tk.X, pady=10)
        
        # === ADVANCED NETWORKING ===
        
        # Separator
        separator2 = tk.Frame(content_frame, height=2, bg=self.colors['card'])
        separator2.pack(fill=tk.X, pady=(20, 10))
        
        # Advanced Networking label
        advanced_label = tk.Label(content_frame, text="🚀 Advanced Networking", 
                                font=('Segoe UI', 10, 'bold'), 
                                fg=self.colors['text_secondary'], bg=self.colors['bg'])
        advanced_label.pack(pady=(0, 10))
        
        # RDMA Launcher button (PRODUCTION READY)
        rdma_button = tk.Button(content_frame, text="⚡ RDMA Launcher ⭐\nUltra Low Latency Interconnects", 
                               font=('Segoe UI', 12, 'bold'), 
                               bg='#ff6b6b', fg=self.colors['bg'],
                               relief='flat', bd=0, cursor='hand2',
                               command=self.launch_rdma_launcher)
        rdma_button.pack(fill=tk.X, pady=10)
        
        # === HOMELAB SYSTEMS ===
        
        # Separator
        separator3 = tk.Frame(content_frame, height=2, bg=self.colors['card'])
        separator3.pack(fill=tk.X, pady=(20, 10))
        
        # Homelab Tools button
        homelab_button = tk.Button(content_frame, text="🏠 Homelab Tools", 
                                   font=('Segoe UI', 12, 'bold'), 
                                   bg='#27ae60', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.launch_homelab_tools)
        homelab_button.pack(fill=tk.X, pady=10)
        
        # Homelab Portal button
        homelab_portal_button = tk.Button(content_frame, text="🌐 Homelab Portal\nMulti-Device Resource Sharing", 
                                          font=('Segoe UI', 12, 'bold'), 
                                          bg='#3498db', fg=self.colors['bg'],
                                          relief='flat', bd=0, cursor='hand2',
                                          command=self.launch_homelab_portal)
        homelab_portal_button.pack(fill=tk.X, pady=10)
        
        # === LEGACY SYSTEMS ===
        
        # Separator
        separator = tk.Frame(content_frame, height=2, bg=self.colors['card'])
        separator.pack(fill=tk.X, pady=(20, 10))
        
        # Legacy label
        legacy_label = tk.Label(content_frame, text="📜 Legacy Tools", 
                               font=('Segoe UI', 10, 'bold'), 
                               fg=self.colors['text_secondary'], bg=self.colors['bg'])
        legacy_label.pack(pady=(0, 10))
        
        # System Dashboard button
        dashboard_button = tk.Button(content_frame, text="🚀 System Dashboard", 
                                   font=('Segoe UI', 11, 'bold'), 
                                   bg='#4ecdc4', fg=self.colors['bg'],
                                   relief='flat', bd=0, cursor='hand2',
                                   command=self.launch_dashboard)
        dashboard_button.pack(fill=tk.X, pady=5)
        
        # RAM Monitor button
        ram_button = tk.Button(content_frame, text="🧹 RAM Monitor", 
                              font=('Segoe UI', 11, 'bold'), 
                              bg=self.colors['warning'], fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              command=self.launch_ram_gui)
        ram_button.pack(fill=tk.X, pady=5)
        
        # GPU Monitor button
        gpu_button = tk.Button(content_frame, text="🎮 GPU Monitor", 
                              font=('Segoe UI', 11, 'bold'), 
                              bg='#ff4444', fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              command=self.launch_gpu_gui)
        gpu_button.pack(fill=tk.X, pady=5)
        
        # CPU Monitor button
        cpu_button = tk.Button(content_frame, text="⚡ CPU Monitor", 
                              font=('Segoe UI', 11, 'bold'), 
                              bg='#87CEEB', fg=self.colors['bg'],
                              relief='flat', bd=0, cursor='hand2',
                              command=self.launch_cpu_gui)
        cpu_button.pack(fill=tk.X, pady=5)
        
        # RAM Cleanup Script button
        ram_cleanup_button = tk.Button(content_frame, text="🧹 RAM Cleanup Script", 
                                       font=('Segoe UI', 11, 'bold'), 
                                       bg='#ffaa00', fg=self.colors['bg'],
                                       relief='flat', bd=0, cursor='hand2',
                                       command=self.launch_cli)
        ram_cleanup_button.pack(fill=tk.X, pady=5)
        
        # Memory Jolt button
        memory_jolt_button = tk.Button(content_frame, text="⚡ Memory Jolt", 
                                       font=('Segoe UI', 11, 'bold'), 
                                       bg='#00ff88', fg=self.colors['bg'],
                                       relief='flat', bd=0, cursor='hand2',
                                       command=self.launch_memory_jolt)
        memory_jolt_button.pack(fill=tk.X, pady=5)
        
        # Soft RAM Cleaner button
        soft_cleaner_button = tk.Button(content_frame, text="🧽 Soft RAM Cleaner", 
                                       font=('Segoe UI', 11, 'bold'), 
                                       bg='#87CEEB', fg=self.colors['bg'],
                                       relief='flat', bd=0, cursor='hand2',
                                       command=self.launch_soft_cleaner)
        soft_cleaner_button.pack(fill=tk.X, pady=5)
        
        # Install Dependencies button
        install_button = tk.Button(content_frame, text="📦 Install Dependencies", 
                                  font=('Segoe UI', 10), 
                                  bg=self.colors['card'], fg=self.colors['text'],
                                  relief='flat', bd=1, cursor='hand2',
                                  command=self.install_dependencies)
        install_button.pack(fill=tk.X, pady=(20, 20))
        
        # Status label
        self.status_label = tk.Label(self.root, text="● Ready", 
                                    font=('Segoe UI', 10, 'bold'), 
                                    bg=self.colors['bg'], fg=self.colors['success'])
        self.status_label.pack(pady=(0, 20))
    
    # === HOMELAB SYSTEMS ===
    
    def launch_pc_auth_gui(self):
        """Launch PC Authentication GUI application"""
        if self.check_file_exists('pc_auth_gui.py'):
            self.status_label.config(text="● Starting PC Authentication GUI...", fg='#8e44ad')
            self.root.after(1000, self.run_script, 'pc_auth_gui.py')
        else:
            messagebox.showerror("Error", "pc_auth_gui.py not found!")
    
    def launch_streamlined_dashboard(self):
        """Launch Streamlined Dashboard application"""
        if self.check_file_exists('streamlined_dashboard.py'):
            self.status_label.config(text="● Starting Streamlined Dashboard...", fg='#e74c3c')
            self.root.after(1000, self.run_script, 'streamlined_dashboard.py')
        else:
            messagebox.showerror("Error", "streamlined_dashboard.py not found!")
    
    # === LEGACY SYSTEMS ===
    
    def launch_dashboard(self):
        """Launch System Dashboard application"""
        if self.check_file_exists('system_dashboard.py'):
            self.status_label.config(text="● Starting System Dashboard...", fg='#4ecdc4')
            self.root.after(1000, self.run_script, 'system_dashboard.py')
        else:
            messagebox.showerror("Error", "system_dashboard.py not found!")
    
    
    def launch_ram_gui(self):
        """Launch RAM GUI application"""
        if self.check_file_exists('ram_monitor_gui.py'):
            self.status_label.config(text="● Starting RAM Monitor...", fg=self.colors['warning'])
            self.root.after(1000, self.run_script, 'ram_monitor_gui.py')
        else:
            messagebox.showerror("Error", "ram_monitor_gui.py not found!")
    
    def launch_gpu_gui(self):
        """Launch GPU GUI application"""
        if self.check_file_exists('gpu_monitor_gui.py'):
            self.status_label.config(text="● Starting GPU Monitor...", fg='#ff4444')
            self.root.after(1000, self.run_script, 'gpu_monitor_gui.py')
        else:
            messagebox.showerror("Error", "gpu_monitor_gui.py not found!")
    
    def launch_cpu_gui(self):
        """Launch CPU GUI application"""
        if self.check_file_exists('cpu_monitor_gui.py'):
            self.status_label.config(text="● Starting CPU Monitor...", fg='#87CEEB')
            self.root.after(1000, self.run_script, 'cpu_monitor_gui.py')
        else:
            messagebox.showerror("Error", "cpu_monitor_gui.py not found!")
    
    def launch_overclock_dashboard(self):
        """Launch Overclocking Dashboard application"""
        if self.check_file_exists('overclocking_dashboard.py'):
            self.status_label.config(text="● Starting Overclocking Dashboard...", fg='#ff4444')
            self.root.after(1000, self.run_script, 'overclocking_dashboard.py')
        else:
            messagebox.showerror("Error", "overclocking_dashboard.py not found!")
    
    def launch_resource_optimizer(self):
        """Launch Resource Optimizer application"""
        if self.check_file_exists('resource_optimizer.py'):
            self.status_label.config(text="● Starting Resource Optimizer...", fg='#00d4ff')
            self.root.after(1000, self.run_script, 'resource_optimizer.py')
        else:
            messagebox.showerror("Error", "resource_optimizer.py not found!")
    
    def launch_resource_optimizer_tray(self):
        """Launch Resource Optimizer in system tray mode"""
        if self.check_file_exists('resource_optimizer_tray.py'):
            self.status_label.config(text="● Starting Resource Optimizer (Tray)...", fg='#8e44ad')
            self.root.after(1000, self.run_script, 'resource_optimizer_tray.py')
        else:
            messagebox.showerror("Error", "resource_optimizer_tray.py not found!")
    
    def launch_homelab_tools(self):
        """Launch Homelab Tools launcher"""
        homelab_path = r'C:\Users\htsou\Desktop\Ram clean up\Homelab_Tools\simple_launcher.py'
        if os.path.exists(homelab_path):
            self.status_label.config(text="● Starting Homelab Tools...", fg='#27ae60')
            try:
                subprocess.Popen([sys.executable, homelab_path], cwd=r'C:\Users\htsou\Desktop\Ram clean up\Homelab_Tools')
                self.status_label.config(text="● Launched Homelab Tools", fg=self.colors['success'])
                self.root.after(2000, self.root.quit)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch Homelab Tools: {e}")
                self.status_label.config(text="● Launch failed", fg='#ff4444')
        else:
            messagebox.showerror("Error", f"Homelab Tools launcher not found at:\n{homelab_path}")
    
    def launch_rdma_launcher(self):
        """Launch RDMA Launcher"""
        rdma_path = r'C:\Users\htsou\Desktop\Ram clean up\rdma_launcher.py'
        if os.path.exists(rdma_path):
            self.status_label.config(text="● Starting RDMA Launcher...", fg='#ff6b6b')
            try:
                subprocess.Popen([sys.executable, rdma_path], cwd=r'C:\Users\htsou\Desktop\Ram clean up')
                self.status_label.config(text="● Launched RDMA Launcher", fg=self.colors['success'])
                self.root.after(2000, self.root.quit)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch RDMA Launcher: {e}")
                self.status_label.config(text="● Launch failed", fg='#ff4444')
        else:
            messagebox.showerror("Error", f"RDMA Launcher not found at:\n{rdma_path}")
    
    def launch_homelab_portal(self):
        """Launch Homelab Portal"""
        homelab_portal_path = r'C:\Users\htsou\Desktop\Ram clean up\homelab_portal.py'
        if os.path.exists(homelab_portal_path):
            self.status_label.config(text="● Starting Homelab Portal...", fg='#3498db')
            try:
                subprocess.Popen([sys.executable, homelab_portal_path], cwd=r'C:\Users\htsou\Desktop\Ram clean up')
                self.status_label.config(text="● Launched Homelab Portal", fg=self.colors['success'])
                self.root.after(2000, self.root.quit)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch Homelab Portal: {e}")
                self.status_label.config(text="● Launch failed", fg='#ff4444')
        else:
            messagebox.showerror("Error", f"Homelab Portal not found at:\n{homelab_portal_path}")
    
    def launch_cli(self):
        """Launch CLI application"""
        if self.check_file_exists('ram_cleanup_script.py'):
            self.status_label.config(text="● Starting Command-Line Cleanup...", fg=self.colors['warning'])
            self.root.after(1000, self.run_script, 'ram_cleanup_script.py')
        else:
            messagebox.showerror("Error", "ram_cleanup_script.py not found!")
    
    def launch_memory_jolt(self):
        """Launch Memory Jolt application"""
        if self.check_file_exists('memory_jolt.py'):
            self.status_label.config(text="● Starting Memory Jolt...", fg=self.colors['success'])
            self.root.after(1000, self.run_script, 'memory_jolt.py')
        else:
            messagebox.showerror("Error", "memory_jolt.py not found!")
    
    def launch_soft_cleaner(self):
        """Launch Soft RAM Cleaner application"""
        if self.check_file_exists('soft_ram_cleaner.py'):
            self.status_label.config(text="● Starting Soft Clean...", fg='#87CEEB')
            self.root.after(1000, self.run_script, 'soft_ram_cleaner.py')
        else:
            messagebox.showerror("Error", "soft_ram_cleaner.py not found!")
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.status_label.config(text="● Installing dependencies...", fg=self.colors['warning'])
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Success", "Dependencies installed successfully!")
                self.status_label.config(text="● Dependencies installed", fg=self.colors['success'])
            else:
                messagebox.showerror("Error", f"Failed to install dependencies:\n{result.stderr}")
                self.status_label.config(text="● Installation failed", fg='#ff4444')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install dependencies: {e}")
            self.status_label.config(text="● Installation failed", fg='#ff4444')
    
    def check_file_exists(self, filename):
        """Check if file exists"""
        return os.path.exists(filename)
    
    def run_script(self, script_name):
        """Run a Python script"""
        try:
            # Use the same Python interpreter
            subprocess.Popen([sys.executable, script_name])
            self.status_label.config(text=f"● Launched {script_name}", fg=self.colors['success'])
            # Close launcher after a short delay
            self.root.after(2000, self.root.quit)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {script_name}: {e}")
            self.status_label.config(text="● Launch failed", fg='#ff4444')

def main():
    """Main function"""
    root = tk.Tk()
    app = LauncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
