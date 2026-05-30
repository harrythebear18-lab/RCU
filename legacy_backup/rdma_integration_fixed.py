#!/usr/bin/env python3
"""
RDMA Integration - Fixed Working Version
Simple RDMA network monitoring tool
"""

import tkinter as tk
from tkinter import ttk, messagebox
import socket
import subprocess
import threading
import time
import psutil

class RDMAIntegration:
    def __init__(self, root):
        self.root = root
        self.root.title("🔌 RDMA Network Integration")
        self.root.geometry("700x600")
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
        
        # Network monitoring state
        self.monitoring = False
        
        # Create widgets
        self.create_widgets()
        
        # Start network monitoring
        self.start_monitoring()
    
    def create_widgets(self):
        """Create RDMA integration widgets"""
        # Title
        title = tk.Label(self.root, text="🔌 RDMA Network Integration", 
                        font=('Arial', 16, 'bold'), 
                        fg=self.colors['primary'], bg=self.colors['bg'])
        title.pack(pady=10)
        
        # Network info frame
        info_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(info_frame, text="🌐 Network Information", font=('Arial', 12, 'bold'),
                fg=self.colors['secondary'], bg=self.colors['card']).pack(pady=5)
        
        # Hostname
        host_frame = tk.Frame(info_frame, bg=self.colors['card'])
        host_frame.pack(fill=tk.X, pady=2, padx=10)
        tk.Label(host_frame, text="🏠 Hostname:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.hostname_label = tk.Label(host_frame, text=socket.gethostname(), font=('Arial', 10, 'bold'),
                                       fg=self.colors['primary'], bg=self.colors['card'])
        self.hostname_label.pack(side=tk.RIGHT)
        
        # IP Address
        ip_frame = tk.Frame(info_frame, bg=self.colors['card'])
        ip_frame.pack(fill=tk.X, pady=2, padx=10)
        tk.Label(ip_frame, text="📍 IP Address:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.ip_label = tk.Label(ip_frame, text="Loading...", font=('Arial', 10, 'bold'),
                                 fg=self.colors['secondary'], bg=self.colors['card'])
        self.ip_label.pack(side=tk.RIGHT)
        
        # Network interfaces
        interfaces_frame = tk.Frame(info_frame, bg=self.colors['card'])
        interfaces_frame.pack(fill=tk.X, pady=2, padx=10)
        tk.Label(interfaces_frame, text="🔌 Interfaces:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.interfaces_label = tk.Label(interfaces_frame, text="Loading...", font=('Arial', 10, 'bold'),
                                        fg=self.colors['warning'], bg=self.colors['card'])
        self.interfaces_label.pack(side=tk.RIGHT)
        
        # Connection status
        conn_frame = tk.Frame(info_frame, bg=self.colors['card'])
        conn_frame.pack(fill=tk.X, pady=2, padx=10)
        tk.Label(conn_frame, text="🔗 Connections:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.connections_label = tk.Label(conn_frame, text="Loading...", font=('Arial', 10, 'bold'),
                                         fg=self.colors['danger'], bg=self.colors['card'])
        self.connections_label.pack(side=tk.RIGHT)
        
        # RDMA Status frame
        rdma_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        rdma_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(rdma_frame, text="🚀 RDMA Status", font=('Arial', 12, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=5)
        
        # RDMA check
        rdma_check_frame = tk.Frame(rdma_frame, bg=self.colors['card'])
        rdma_check_frame.pack(fill=tk.X, pady=2, padx=10)
        tk.Label(rdma_check_frame, text="🔍 RDMA Support:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.rdma_status_label = tk.Label(rdma_check_frame, text="Checking...", font=('Arial', 10, 'bold'),
                                          fg=self.colors['warning'], bg=self.colors['card'])
        self.rdma_status_label.pack(side=tk.RIGHT)
        
        # Network performance frame
        perf_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        perf_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(perf_frame, text="📊 Network Performance", font=('Arial', 12, 'bold'),
                fg=self.colors['secondary'], bg=self.colors['card']).pack(pady=5)
        
        # Performance metrics
        metrics_frame = tk.Frame(perf_frame, bg=self.colors['card'])
        metrics_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Bytes sent
        sent_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        sent_frame.pack(fill=tk.X, pady=2)
        tk.Label(sent_frame, text="📤 Bytes Sent:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.bytes_sent_label = tk.Label(sent_frame, text="0 MB", font=('Arial', 10, 'bold'),
                                        fg=self.colors['primary'], bg=self.colors['card'])
        self.bytes_sent_label.pack(side=tk.RIGHT)
        
        # Bytes received
        recv_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        recv_frame.pack(fill=tk.X, pady=2)
        tk.Label(recv_frame, text="📥 Bytes Received:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.bytes_recv_label = tk.Label(recv_frame, text="0 MB", font=('Arial', 10, 'bold'),
                                        fg=self.colors['secondary'], bg=self.colors['card'])
        self.bytes_recv_label.pack(side=tk.RIGHT)
        
        # Packets sent
        packets_sent_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        packets_sent_frame.pack(fill=tk.X, pady=2)
        tk.Label(packets_sent_frame, text="📦 Packets Sent:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.packets_sent_label = tk.Label(packets_sent_frame, text="0", font=('Arial', 10, 'bold'),
                                           fg=self.colors['warning'], bg=self.colors['card'])
        self.packets_sent_label.pack(side=tk.RIGHT)
        
        # Packets received
        packets_recv_frame = tk.Frame(metrics_frame, bg=self.colors['card'])
        packets_recv_frame.pack(fill=tk.X, pady=2)
        tk.Label(packets_recv_frame, text="📦 Packets Received:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.packets_recv_label = tk.Label(packets_recv_frame, text="0", font=('Arial', 10, 'bold'),
                                           fg=self.colors['danger'], bg=self.colors['card'])
        self.packets_recv_label.pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.test_btn = tk.Button(button_frame, text="🔍 Test Connection",
                                 font=('Arial', 11, 'bold'),
                                 bg=self.colors['secondary'], fg='white',
                                 relief='flat', cursor='hand2',
                                 command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.refresh_btn = tk.Button(button_frame, text="🔄 Refresh",
                                    font=('Arial', 11, 'bold'),
                                    bg=self.colors['warning'], fg='white',
                                    relief='flat', cursor='hand2',
                                    command=self.refresh_info)
        self.refresh_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="● Initializing...", 
                                     font=('Arial', 10, 'bold'),
                                     fg=self.colors['warning'], bg=self.colors['bg'])
        self.status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Initial network info update
        self.update_network_info()
        self.check_rdma_support()
    
    def start_monitoring(self):
        """Start network monitoring"""
        self.monitoring = True
        self.monitoring_thread = threading.Thread(target=self.monitor_network, daemon=True)
        self.monitoring_thread.start()
    
    def monitor_network(self):
        """Monitor network performance"""
        last_stats = None
        
        while self.monitoring:
            try:
                current_stats = psutil.net_io_counters()
                
                if last_stats:
                    bytes_sent = (current_stats.bytes_sent - last_stats.bytes_sent) // (1024 * 1024)  # MB
                    bytes_recv = (current_stats.bytes_recv - last_stats.bytes_recv) // (1024 * 1024)  # MB
                    packets_sent = current_stats.packets_sent - last_stats.packets_sent
                    packets_recv = current_stats.packets_recv - last_stats.packets_recv
                    
                    self.root.after(0, self.update_performance_labels, bytes_sent, bytes_recv, 
                                  packets_sent, packets_recv)
                
                last_stats = current_stats
                time.sleep(2)
                
            except Exception as e:
                print(f"Error monitoring network: {e}")
                time.sleep(5)
    
    def update_performance_labels(self, bytes_sent, bytes_recv, packets_sent, packets_recv):
        """Update performance labels"""
        try:
            self.bytes_sent_label.config(text=f"{bytes_sent} MB")
            self.bytes_recv_label.config(text=f"{bytes_recv} MB")
            self.packets_sent_label.config(text=str(packets_sent))
            self.packets_recv_label.config(text=str(packets_recv))
        except:
            pass
    
    def update_network_info(self):
        """Update network information"""
        try:
            # Get IP address
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            self.ip_label.config(text=ip_address)
            
            # Get network interfaces
            interfaces = list(psutil.net_if_addrs().keys())
            self.interfaces_label.config(text=f"{len(interfaces)} interfaces")
            
            # Get connections
            connections = len(psutil.net_connections())
            self.connections_label.config(text=str(connections))
            
            self.status_label.config(text="● Network monitoring active", fg=self.colors['primary'])
            
        except Exception as e:
            self.status_label.config(text="● Network error", fg=self.colors['danger'])
            print(f"Error updating network info: {e}")
    
    def check_rdma_support(self):
        """Check for RDMA support"""
        try:
            # Check for RDMA devices (simplified check)
            result = subprocess.run(['rdma', 'dev'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                self.rdma_status_label.config(text="✅ Supported", fg=self.colors['primary'])
            else:
                self.rdma_status_label.config(text="❌ Not detected", fg=self.colors['danger'])
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # RDMA tools not available
            self.rdma_status_label.config(text="❓ Unknown", fg=self.colors['warning'])
        except Exception as e:
            self.rdma_status_label.config(text="❓ Error", fg=self.colors['danger'])
            print(f"Error checking RDMA: {e}")
    
    def test_connection(self):
        """Test network connection"""
        try:
            self.status_label.config(text="● Testing connection...", fg=self.colors['warning'])
            
            # Test connectivity to Google DNS
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("8.8.8.8", 53))
            sock.close()
            
            if result == 0:
                self.status_label.config(text="● Connection successful", fg=self.colors['primary'])
                messagebox.showinfo("Connection Test", "✅ Network connection is working properly!")
            else:
                self.status_label.config(text="● Connection failed", fg=self.colors['danger'])
                messagebox.showerror("Connection Test", "❌ Network connection failed!")
                
        except Exception as e:
            self.status_label.config(text="● Connection error", fg=self.colors['danger'])
            messagebox.showerror("Connection Test", f"❌ Connection test failed: {e}")
    
    def refresh_info(self):
        """Refresh network information"""
        self.update_network_info()
        self.check_rdma_support()
        self.status_label.config(text="● Information refreshed", fg=self.colors['secondary'])
    
    def on_closing(self):
        """Handle window closing"""
        self.monitoring = False
        self.root.destroy()

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = RDMAIntegration(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error starting RDMA integration: {e}")

if __name__ == "__main__":
    main()
