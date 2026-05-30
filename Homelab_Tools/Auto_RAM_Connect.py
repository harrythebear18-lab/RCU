#!/usr/bin/env python3
"""
Auto RAM Connection Script
Automatically configures and connects RAM sharing between PCs
Real-time data synchronization and monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
import json
import socket
import psutil
from datetime import datetime
from pathlib import Path

class AutoRAMConnect:
    def __init__(self):
        # Configuration
        self.server_ip = "192.168.1.186"  # PC with more RAM (Windows 11)
        self.client_ip = "192.168.1.132"   # PC with less RAM (Windows 10)
        self.ram_size_gb = 4
        self.drive_letter = "R"
        
        # Status tracking
        self.is_server = None
        self.connection_status = "disconnected"
        self.real_time_data = {}
        self.monitoring_active = False
        
        # Auto-detect system role
        self.detect_system_role()
        
    def detect_system_role(self):
        """Auto-detect if this is server or client based on IP"""
        try:
            # Get local IP addresses
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Check if we match server or client IP
            if local_ip == self.server_ip:
                self.is_server = True
                print(f"✅ Detected as SERVER (IP: {local_ip})")
            elif local_ip == self.client_ip:
                self.is_server = False
                print(f"✅ Detected as CLIENT (IP: {local_ip})")
            else:
                # Fallback: check available RAM
                ram_gb = psutil.virtual_memory().total / (1024**3)
                if ram_gb >= 16:  # Assume system with 16GB+ is server
                    self.is_server = True
                    print(f"✅ Detected as SERVER (RAM: {ram_gb:.1f}GB)")
                else:
                    self.is_server = False
                    print(f"✅ Detected as CLIENT (RAM: {ram_gb:.1f}GB)")
                    
        except Exception as e:
            print(f"⚠️ Could not auto-detect role: {e}")
            # Default to client for safety
            self.is_server = False
            
    def check_python_command(self):
        """Check if python or py is available"""
        try:
            subprocess.run(['python', '--version'], capture_output=True, timeout=3)
            return 'python'
        except:
            try:
                subprocess.run(['py', '--version'], capture_output=True, timeout=3)
                return 'py'
            except:
                return None
                
    def run_command(self, command, timeout=60):
        """Run a command and return result"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
            
    def auto_configure_server(self):
        """Auto-configure server settings"""
        print("🚀 Auto-configuring RAM sharing server...")
        
        python_cmd = self.check_python_command()
        if not python_cmd:
            print("❌ Python not found, using batch files...")
            return self.auto_configure_server_batch()
            
        # Use PowerShell script for better control
        script_path = "Robust_RAM_Sharing.ps1"
        if os.path.exists(script_path):
            command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action setup -RAMSizeGB {self.ram_size_gb} -DriveLetter {self.drive_letter}'
            success, stdout, stderr = self.run_command(command)
            
            if success:
                print("✅ Server auto-configuration successful!")
                print(f"📊 RAM disk created: {self.drive_letter}: ({self.ram_size_gb}GB)")
                print(f"🔗 SMB Share: \\\\{self.server_ip}\\RamDisk")
                print(f"⚡ iSCSI Target: RAMDiskTarget")
                return True
            else:
                print(f"❌ Server configuration failed: {stderr}")
                return False
        else:
            print("❌ PowerShell script not found")
            return False
            
    def auto_configure_server_batch(self):
        """Auto-configure server using batch files"""
        print("🚀 Using batch files for server configuration...")
        
        success, stdout, stderr = self.run_command("Setup_RAM_Sharing.bat")
        
        if success:
            print("✅ Server configuration successful!")
            return True
        else:
            print(f"❌ Server configuration failed: {stderr}")
            return False
            
    def auto_connect_client(self):
        """Auto-connect client to server"""
        print("🔗 Auto-connecting to RAM sharing server...")
        
        # Test connectivity first
        success, _, _ = self.run_command(f"ping -n 2 {self.server_ip}")
        if not success:
            print(f"❌ Cannot reach server at {self.server_ip}")
            return False
            
        python_cmd = self.check_python_command()
        if not python_cmd:
            print("❌ Python not found, using batch files...")
            return self.auto_connect_client_batch()
            
        # Use PowerShell script for better control
        script_path = "Robust_RAM_Sharing.ps1"
        if os.path.exists(script_path):
            command = f'powershell -ExecutionPolicy Bypass -File "{script_path}" -Action map -TargetIP {self.server_ip}'
            success, stdout, stderr = self.run_command(command)
            
            if success:
                print("✅ Client auto-connection successful!")
                print(f"🔗 Connected to server: {self.server_ip}")
                self.connection_status = "connected"
                return True
            else:
                print(f"❌ Client connection failed: {stderr}")
                return False
        else:
            print("❌ PowerShell script not found")
            return False
            
    def auto_connect_client_batch(self):
        """Auto-connect client using batch files"""
        print("🔗 Using batch files for client connection...")
        
        success, stdout, stderr = self.run_command("Map_RAM_Sharing.bat")
        
        if success:
            print("✅ Client connection successful!")
            self.connection_status = "connected"
            return True
        else:
            print(f"❌ Client connection failed: {stderr}")
            return False
            
    def start_real_time_monitoring(self):
        """Start real-time monitoring and data synchronization"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        print("📊 Starting real-time monitoring...")
        
        def monitor():
            while self.monitoring_active:
                try:
                    # Collect real-time data
                    self.real_time_data = {
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'cpu_usage': psutil.cpu_percent(),
                        'memory_usage': psutil.virtual_memory().percent,
                        'connection_status': self.connection_status,
                        'is_server': self.is_server,
                        'ram_disk_available': self.check_ram_disk(),
                        'network_latency': self.test_network_latency()
                    }
                    
                    # Update display every 2 seconds
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"⚠️ Monitoring error: {e}")
                    time.sleep(5)
                    
        threading.Thread(target=monitor, daemon=True).start()
        
    def check_ram_disk(self):
        """Check if RAM disk is available"""
        try:
            if self.is_server:
                # Check if RAM disk exists on server
                return os.path.exists(f"{self.drive_letter}:\\")
            else:
                # Check if network share is mapped
                drives = psutil.disk_partitions()
                for drive in drives:
                    if 'RamDisk' in drive.mountpoint or drive.device == f"{self.drive_letter}:":
                        return True
                return False
        except:
            return False
            
    def test_network_latency(self):
        """Test network latency to other PC"""
        target = self.client_ip if self.is_server else self.server_ip
        try:
            result = subprocess.run(['ping', '-n', '1', target], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract latency from ping output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'time=' in line.lower() or 'time<' in line.lower():
                        return line.strip()
            return "N/A"
        except:
            return "N/A"
            
    def display_real_time_status(self):
        """Display real-time status in console"""
        if not self.real_time_data:
            return
            
        data = self.real_time_data
        print(f"\n📊 Real-Time Status - {data['timestamp']}")
        print(f"🖥️  Role: {'SERVER' if data['is_server'] else 'CLIENT'}")
        print(f"🔗 Connection: {data['connection_status']}")
        print(f"💾 RAM Disk: {'✅ Available' if data['ram_disk_available'] else '❌ Not Available'}")
        print(f"📈 CPU Usage: {data['cpu_usage']:.1f}%")
        print(f"🧠 Memory Usage: {data['memory_usage']:.1f}%")
        print(f"🌐 Network: {data['network_latency']}")
        print("-" * 50)
        
    def run_console_mode(self):
        """Run in console mode"""
        print("🖥️  Auto RAM Connection - Console Mode")
        print("=" * 50)
        
        # Auto-configure based on role
        if self.is_server:
            print("🚀 Configuring as SERVER...")
            if self.auto_configure_server():
                print("✅ Server ready for client connections")
            else:
                print("❌ Server configuration failed")
                return
        else:
            print("🔗 Configuring as CLIENT...")
            if self.auto_connect_client():
                print("✅ Client connected to server")
            else:
                print("❌ Client connection failed")
                return
                
        # Start real-time monitoring
        self.start_real_time_monitoring()
        
        # Console loop
        try:
            while True:
                self.display_real_time_status()
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            
    def run_gui_mode(self):
        """Run in GUI mode"""
        root = tk.Tk()
        app = AutoRAMConnectGUI(root, self)
        root.mainloop()
        
    def auto_connect_all(self):
        """Auto-connect everything with one command"""
        print("🚀 Auto-connecting RAM sharing system...")
        
        # Step 1: Fix compatibility issues
        print("📋 Step 1: Fixing Windows compatibility...")
        self.run_command("Fix_Windows_Compatibility.bat")
        
        # Step 2: Configure based on role
        if self.is_server:
            print("📋 Step 2: Configuring server...")
            if not self.auto_configure_server():
                return False
        else:
            print("📋 Step 2: Connecting to server...")
            if not self.auto_connect_client():
                return False
                
        # Step 3: Start monitoring
        print("📋 Step 3: Starting real-time monitoring...")
        self.start_real_time_monitoring()
        
        print("✅ Auto-connection complete!")
        return True

class AutoRAMConnectGUI:
    def __init__(self, root, auto_connect):
        self.root = root
        self.auto_connect = auto_connect
        self.root.title("🖥️ Auto RAM Connection")
        self.root.geometry("600x500")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'success': '#00ff88',
            'danger': '#ff4444',
            'warning': '#ffaa00',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0'
        }
        
        self.create_widgets()
        self.start_gui_monitoring()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill='x', padx=10, pady=10)
        
        role_text = "SERVER" if self.auto_connect.is_server else "CLIENT"
        ttk.Label(header, text=f"🖥️ Auto RAM Connection - {role_text}", 
                 font=('Segoe UI', 16, 'bold')).pack()
        
        # Status frame
        status_frame = ttk.LabelFrame(self.root, text="System Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_labels = {}
        status_items = [
            ('role', 'Role', 'SERVER' if self.auto_connect.is_server else 'CLIENT'),
            ('connection', 'Connection', self.auto_connect.connection_status),
            ('ram_disk', 'RAM Disk', 'Checking...'),
            ('cpu', 'CPU Usage', '0%'),
            ('memory', 'Memory Usage', '0%'),
            ('network', 'Network', 'Checking...')
        ]
        
        for key, label, value in status_items:
            frame = ttk.Frame(status_frame)
            frame.pack(fill='x', pady=2)
            ttk.Label(frame, text=f"{label}:", width=15).pack(side='left')
            self.status_labels[key] = ttk.Label(frame, text=value, width=20)
            self.status_labels[key].pack(side='left')
            
        # Control buttons
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text="🚀 Auto-Connect All", 
                  command=self.auto_connect_all).pack(side='left', padx=5)
        ttk.Button(control_frame, text="🔧 Fix Compatibility", 
                  command=self.fix_compatibility).pack(side='left', padx=5)
        ttk.Button(control_frame, text="🧹 Cleanup", 
                  command=self.cleanup).pack(side='left', padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(self.root, text="Activity Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD,
                                                  bg='#242424', fg=self.colors['text'],
                                                  font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        
        self.log("GUI initialized", "INFO")
        
    def log(self, message, level="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        
    def start_gui_monitoring(self):
        """Start GUI monitoring"""
        def update_gui():
            while True:
                try:
                    if self.auto_connect.real_time_data:
                        data = self.auto_connect.real_time_data
                        
                        # Update status labels
                        self.status_labels['connection'].config(
                            text=data['connection_status'].upper(),
                            foreground='green' if data['connection_status'] == 'connected' else 'red'
                        )
                        self.status_labels['ram_disk'].config(
                            text='✅ Available' if data['ram_disk_available'] else '❌ Not Available',
                            foreground='green' if data['ram_disk_available'] else 'red'
                        )
                        self.status_labels['cpu'].config(text=f"{data['cpu_usage']:.1f}%")
                        self.status_labels['memory'].config(text=f"{data['memory_usage']:.1f}%")
                        self.status_labels['network'].config(text=str(data['network_latency']))
                        
                    time.sleep(2)
                except Exception as e:
                    self.log(f"GUI update error: {e}", "ERROR")
                    time.sleep(5)
                    
        threading.Thread(target=update_gui, daemon=True).start()
        
    def auto_connect_all(self):
        """Auto-connect all components"""
        self.log("Starting auto-connection...", "INFO")
        
        def run_auto_connect():
            if self.auto_connect.auto_connect_all():
                self.log("Auto-connection successful!", "SUCCESS")
            else:
                self.log("Auto-connection failed", "ERROR")
                
        threading.Thread(target=run_auto_connect, daemon=True).start()
        
    def fix_compatibility(self):
        """Fix compatibility issues"""
        self.log("Fixing Windows compatibility...", "INFO")
        
        def run_fix():
            success, _, _ = self.auto_connect.run_command("Fix_Windows_Compatibility.bat")
            if success:
                self.log("Compatibility fix completed", "SUCCESS")
            else:
                self.log("Compatibility fix failed", "ERROR")
                
        threading.Thread(target=run_fix, daemon=True).start()
        
    def cleanup(self):
        """Cleanup all components"""
        self.log("Starting cleanup...", "INFO")
        
        def run_cleanup():
            success, _, _ = self.auto_connect.run_command("Cleanup_RAM_Sharing.bat")
            if success:
                self.log("Cleanup completed", "SUCCESS")
                self.auto_connect.connection_status = "disconnected"
            else:
                self.log("Cleanup failed", "ERROR")
                
        threading.Thread(target=run_cleanup, daemon=True).start()

def main():
    """Main entry point"""
    auto_connect = AutoRAMConnect()
    
    # Check for GUI availability
    try:
        import tkinter
        has_gui = True
    except ImportError:
        has_gui = False
        
    # Choose mode based on arguments or availability
    if len(sys.argv) > 1:
        if sys.argv[1] == "--console":
            auto_connect.run_console_mode()
        elif sys.argv[1] == "--gui" and has_gui:
            auto_connect.run_gui_mode()
        else:
            print("Usage: python Auto_RAM_Connect.py [--console|--gui]")
    else:
        # Auto-choose: try GUI first, fallback to console
        if has_gui:
            print("🖥️ Starting GUI mode...")
            auto_connect.run_gui_mode()
        else:
            print("📺 GUI not available, using console mode...")
            auto_connect.run_console_mode()

if __name__ == "__main__":
    main()
