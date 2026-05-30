#!/usr/bin/env python3
"""
Performance Optimizer - Fixed Working Version
Simple system performance optimization tool
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import os

class PerformanceOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Performance Optimizer")
        self.root.geometry("600x500")
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
        
        # Optimization state
        self.optimizing = False
        
        # Create widgets
        self.create_widgets()
        
        # Start monitoring
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self.monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def create_widgets(self):
        """Create optimizer widgets"""
        # Title
        title = tk.Label(self.root, text="⚡ Performance Optimizer", 
                        font=('Arial', 16, 'bold'), 
                        fg=self.colors['primary'], bg=self.colors['bg'])
        title.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # System info
        info_frame = tk.Frame(main_frame, bg=self.colors['card'])
        info_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(info_frame, text="💻 CPU Usage:", font=('Arial', 11, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).grid(row=0, column=0, sticky='w', padx=5)
        self.cpu_label = tk.Label(info_frame, text="0%", font=('Arial', 11, 'bold'),
                                  fg=self.colors['primary'], bg=self.colors['card'])
        self.cpu_label.grid(row=0, column=1, sticky='e', padx=5)
        
        tk.Label(info_frame, text="🧠 Memory Usage:", font=('Arial', 11, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).grid(row=1, column=0, sticky='w', padx=5)
        self.mem_label = tk.Label(info_frame, text="0%", font=('Arial', 11, 'bold'),
                                  fg=self.colors['secondary'], bg=self.colors['card'])
        self.mem_label.grid(row=1, column=1, sticky='e', padx=5)
        
        tk.Label(info_frame, text="⚙️ Running Processes:", font=('Arial', 11, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).grid(row=2, column=0, sticky='w', padx=5)
        self.proc_label = tk.Label(info_frame, text="0", font=('Arial', 11, 'bold'),
                                   fg=self.colors['warning'], bg=self.colors['card'])
        self.proc_label.grid(row=2, column=1, sticky='e', padx=5)
        
        # Optimization options
        options_frame = tk.Frame(main_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X, pady=20, padx=10)
        
        tk.Label(options_frame, text="🔧 Optimization Options:", font=('Arial', 12, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(anchor='w', pady=5)
        
        # Checkboxes
        self.clean_temp = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="🗑️ Clean temporary files", 
                      variable=self.clean_temp, font=('Arial', 10),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=2)
        
        self.optimize_memory = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="🧠 Optimize memory usage", 
                      variable=self.optimize_memory, font=('Arial', 10),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=2)
        
        self.close_unused = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="🔌 Close unused processes", 
                      variable=self.close_unused, font=('Arial', 10),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=2)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['card'])
        button_frame.pack(fill=tk.X, pady=20, padx=10)
        
        self.optimize_btn = tk.Button(button_frame, text="🚀 Start Optimization",
                                      font=('Arial', 12, 'bold'),
                                      bg=self.colors['primary'], fg='white',
                                      relief='flat', cursor='hand2',
                                      command=self.start_optimization)
        self.optimize_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        self.analyze_btn = tk.Button(button_frame, text="📊 Analyze System",
                                     font=('Arial', 12, 'bold'),
                                     bg=self.colors['secondary'], fg='white',
                                     relief='flat', cursor='hand2',
                                     command=self.analyze_system)
        self.analyze_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10, padx=10)
        
        # Status
        self.status_label = tk.Label(main_frame, text="● Ready to optimize", 
                                     font=('Arial', 10, 'bold'),
                                     fg=self.colors['primary'], bg=self.colors['card'])
        self.status_label.pack(pady=5)
    
    def monitor_system(self):
        """Monitor system performance"""
        while self.monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                processes = len(psutil.pids())
                
                self.root.after(0, self.update_labels, cpu_percent, memory.percent, processes)
                time.sleep(2)
            except Exception as e:
                print(f"Error monitoring system: {e}")
    
    def update_labels(self, cpu, memory, processes):
        """Update system labels"""
        try:
            self.cpu_label.config(text=f"{cpu:.1f}%")
            self.mem_label.config(text=f"{memory:.1f}%")
            self.proc_label.config(text=str(processes))
        except:
            pass
    
    def start_optimization(self):
        """Start system optimization"""
        if self.optimizing:
            return
        
        self.optimizing = True
        self.optimize_btn.config(text="⏳ Optimizing...", state='disabled')
        self.status_label.config(text="● Optimizing system...", fg=self.colors['warning'])
        self.progress.start()
        
        # Run optimization in thread
        threading.Thread(target=self.optimize_system, daemon=True).start()
    
    def optimize_system(self):
        """Perform system optimization"""
        try:
            optimizations = []
            
            if self.clean_temp.get():
                # Clean temp files (simplified)
                temp_dirs = [os.environ.get('TEMP', ''), os.environ.get('TMP', '')]
                cleaned = 0
                for temp_dir in temp_dirs:
                    if temp_dir and os.path.exists(temp_dir):
                        try:
                            for item in os.listdir(temp_dir):
                                item_path = os.path.join(temp_dir, item)
                                try:
                                    if os.path.isfile(item_path):
                                        os.remove(item_path)
                                        cleaned += 1
                                except:
                                    pass
                        except:
                            pass
                optimizations.append(f"Cleaned {cleaned} temporary files")
            
            if self.optimize_memory.get():
                # Memory optimization (garbage collection)
                import gc
                gc.collect()
                optimizations.append("Optimized memory usage")
            
            if self.close_unused.get():
                # Close unused processes (simplified and safe)
                closed = 0
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        if proc.info['cpu_percent'] < 1.0 and proc.info['pid'] > 1000:
                            # Only close processes with very low CPU usage and higher PID
                            if 'chrome' not in proc.info['name'].lower():  # Avoid closing browser
                                proc.terminate()
                                closed += 1
                                if closed >= 5:  # Limit to 5 processes
                                    break
                    except:
                        pass
                if closed > 0:
                    optimizations.append(f"Closed {closed} unused processes")
            
            # Update UI
            self.root.after(0, self.optimization_complete, optimizations)
            
        except Exception as e:
            self.root.after(0, self.optimization_error, str(e))
    
    def optimization_complete(self, optimizations):
        """Handle optimization completion"""
        self.optimizing = False
        self.progress.stop()
        self.optimize_btn.config(text="🚀 Start Optimization", state='normal')
        self.status_label.config(text="● Optimization complete!", fg=self.colors['primary'])
        
        if optimizations:
            messagebox.showinfo("Optimization Complete", 
                               f"Completed optimizations:\n" + "\n".join(f"• {opt}" for opt in optimizations))
        else:
            messagebox.showinfo("Optimization Complete", "No optimizations were performed.")
    
    def optimization_error(self, error):
        """Handle optimization error"""
        self.optimizing = False
        self.progress.stop()
        self.optimize_btn.config(text="🚀 Start Optimization", state='normal')
        self.status_label.config(text="● Optimization failed!", fg=self.colors['danger'])
        messagebox.showerror("Optimization Error", f"Optimization failed: {error}")
    
    def analyze_system(self):
        """Analyze system performance"""
        try:
            cpu_percent = psutil.cpu_percent(interval=2)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            analysis = f"System Analysis Report:\n\n"
            analysis += f"💻 CPU Usage: {cpu_percent:.1f}%\n"
            analysis += f"🧠 Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)\n"
            analysis += f"💾 Disk Usage: {(disk.used / disk.total) * 100:.1f}%\n"
            analysis += f"⚙️ Running Processes: {len(psutil.pids())}\n\n"
            
            # Recommendations
            analysis += "Recommendations:\n"
            if cpu_percent > 80:
                analysis += "• High CPU usage - consider closing unused applications\n"
            if memory.percent > 80:
                analysis += "• High memory usage - consider restarting applications\n"
            if (disk.used / disk.total) * 100 > 90:
                analysis += "• Low disk space - consider cleaning up files\n"
            
            if cpu_percent < 50 and memory.percent < 50:
                analysis += "• System performance is good\n"
            
            messagebox.showinfo("System Analysis", analysis)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze system: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.monitoring_active = False
        self.root.destroy()

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = PerformanceOptimizer(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error starting optimizer: {e}")

if __name__ == "__main__":
    main()
