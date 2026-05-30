#!/usr/bin/env python3
"""
Enhanced Dashboard - Fixed Working Version
Simple system monitoring dashboard
"""

import tkinter as tk
from tkinter import ttk
import psutil
import time
from datetime import datetime
import threading

class EnhancedDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Enhanced System Dashboard")
        self.root.geometry("800x600")
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
        
        # Create widgets
        self.create_widgets()
        
        # Start monitoring
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.update_stats, daemon=True)
        self.monitoring_thread.start()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Title
        title = tk.Label(self.root, text="📊 Enhanced System Dashboard", 
                        font=('Arial', 18, 'bold'), 
                        fg=self.colors['primary'], bg=self.colors['bg'])
        title.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # CPU
        cpu_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        cpu_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(cpu_frame, text="💻 CPU Usage:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.cpu_label = tk.Label(cpu_frame, text="0%", font=('Arial', 12, 'bold'),
                                  fg=self.colors['primary'], bg=self.colors['card'])
        self.cpu_label.pack(side=tk.RIGHT)
        
        # Memory
        mem_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        mem_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(mem_frame, text="🧠 Memory Usage:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.mem_label = tk.Label(mem_frame, text="0%", font=('Arial', 12, 'bold'),
                                  fg=self.colors['secondary'], bg=self.colors['card'])
        self.mem_label.pack(side=tk.RIGHT)
        
        # Disk
        disk_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        disk_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(disk_frame, text="💾 Disk Usage:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.disk_label = tk.Label(disk_frame, text="0%", font=('Arial', 12, 'bold'),
                                   fg=self.colors['warning'], bg=self.colors['card'])
        self.disk_label.pack(side=tk.RIGHT)
        
        # Processes
        proc_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        proc_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(proc_frame, text="⚙️ Processes:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.proc_label = tk.Label(proc_frame, text="0", font=('Arial', 12, 'bold'),
                                   fg=self.colors['danger'], bg=self.colors['card'])
        self.proc_label.pack(side=tk.RIGHT)
        
        # Time
        time_frame = tk.Frame(stats_frame, bg=self.colors['card'])
        time_frame.pack(fill=tk.X, pady=10, padx=10)
        tk.Label(time_frame, text="🕐 Time:", font=('Arial', 12, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        self.time_label = tk.Label(time_frame, text="", font=('Arial', 12, 'bold'),
                                   fg=self.colors['text'], bg=self.colors['card'])
        self.time_label.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="● Monitoring Active", 
                                     font=('Arial', 10, 'bold'),
                                     fg=self.colors['primary'], bg=self.colors['bg'])
        self.status_label.pack(side=tk.BOTTOM, pady=5)
    
    def update_stats(self):
        """Update system statistics"""
        while self.monitoring_active:
            try:
                # Get system stats
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                processes = len(psutil.pids())
                
                # Update labels
                self.root.after(0, self.update_labels, cpu_percent, memory.percent, 
                              (disk.used / disk.total) * 100, processes)
                
                time.sleep(2)
            except Exception as e:
                print(f"Error updating stats: {e}")
    
    def update_labels(self, cpu, memory, disk, processes):
        """Update dashboard labels"""
        try:
            self.cpu_label.config(text=f"{cpu:.1f}%")
            self.mem_label.config(text=f"{memory:.1f}%")
            self.disk_label.config(text=f"{disk:.1f}%")
            self.proc_label.config(text=str(processes))
            self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Update status based on CPU usage
            if cpu > 80:
                self.status_label.config(text="● High CPU Usage", fg=self.colors['danger'])
            elif cpu > 50:
                self.status_label.config(text="● Moderate CPU Usage", fg=self.colors['warning'])
            else:
                self.status_label.config(text="● System Normal", fg=self.colors['primary'])
        except:
            pass
    
    def on_closing(self):
        """Handle window closing"""
        self.monitoring_active = False
        self.root.destroy()

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = EnhancedDashboard(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error starting dashboard: {e}")

if __name__ == "__main__":
    main()
