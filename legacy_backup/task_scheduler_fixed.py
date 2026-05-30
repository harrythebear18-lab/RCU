#!/usr/bin/env python3
"""
Task Scheduler - Fixed Working Version
Simple task scheduling and automation tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
from datetime import datetime, timedelta
import subprocess

class TaskScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Task Scheduler")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'primary': '#00ff88',
            'secondary': '#00aaff',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'success': '#00ff88',
            'text': '#ffffff',
            'text_secondary': '#cccccc'
        }
        
        # Scheduler state
        self.scheduler_running = False
        self.tasks = []
        self.scheduler_thread = None
        
        # Data file
        self.data_file = "task_scheduler_data.json"
        
        # Initialize
        self.init_scheduler()
        self.create_widgets()
        self.load_tasks()
        self.start_scheduler()
    
    def init_scheduler(self):
        """Initialize scheduler data"""
        if not os.path.exists(self.data_file):
            default_data = {
                "tasks": [],
                "settings": {
                    "auto_start": True,
                    "max_concurrent_tasks": 5,
                    "log_retention_days": 30
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="📅 Task Scheduler", 
                font=('Arial', 18, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status
        self.status_label = tk.Label(header_frame, text="● Scheduler Running", 
                                   font=('Arial', 12, 'bold'),
                                   fg=self.colors['success'], bg=self.colors['card'])
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Scheduler controls
        scheduler_controls_frame = tk.Frame(header_frame, bg=self.colors['card'])
        scheduler_controls_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.start_stop_btn = tk.Button(scheduler_controls_frame, text="⏸️ Stop",
                                       font=('Arial', 10, 'bold'),
                                       bg=self.colors['warning'], fg='white',
                                       relief='flat', cursor='hand2',
                                       command=self.toggle_scheduler)
        self.start_stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Main content with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_tasks_tab(notebook)
        self.create_schedule_tab(notebook)
        self.create_logs_tab(notebook)
        self.create_settings_tab(notebook)
    
    def create_tasks_tab(self, notebook):
        """Create tasks management tab"""
        tasks_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tasks_frame, text="📋 Tasks")
        
        # Tasks list
        tasks_list_frame = tk.Frame(tasks_frame, bg=self.colors['card'], relief='raised', bd=1)
        tasks_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(tasks_list_frame, text="📋 Scheduled Tasks", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Tasks listbox with scrollbar
        tasks_container = tk.Frame(tasks_list_frame, bg=self.colors['card'])
        tasks_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(tasks_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tasks_listbox = tk.Listbox(tasks_container, font=('Consolas', 11),
                                        bg=self.colors['bg'], fg=self.colors['text'],
                                        yscrollcommand=scrollbar.set)
        self.tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tasks_listbox.yview)
        
        # Task actions
        task_actions_frame = tk.Frame(tasks_list_frame, bg=self.colors['card'])
        task_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(task_actions_frame, text="➕ Add",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.add_task).pack(side=tk.LEFT, padx=5)
        
        tk.Button(task_actions_frame, text="✏️ Edit",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.edit_task).pack(side=tk.LEFT, padx=5)
        
        tk.Button(task_actions_frame, text="▶️ Run Now",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.run_task_now).pack(side=tk.LEFT, padx=5)
        
        tk.Button(task_actions_frame, text="🗑️ Delete",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.delete_task).pack(side=tk.LEFT, padx=5)
        
        tk.Button(task_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_tasks).pack(side=tk.LEFT, padx=5)
    
    def create_schedule_tab(self, notebook):
        """Create schedule visualization tab"""
        schedule_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(schedule_frame, text="📅 Schedule")
        
        # Schedule display
        schedule_display_frame = tk.Frame(schedule_frame, bg=self.colors['card'], relief='raised', bd=1)
        schedule_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(schedule_display_frame, text="📅 Task Schedule", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Calendar view (simplified)
        calendar_frame = tk.Frame(schedule_display_frame, bg=self.colors['card'])
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Today's tasks
        today_frame = tk.Frame(calendar_frame, bg=self.colors['card'], relief='raised', bd=1)
        today_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(today_frame, text="📅 Today's Tasks", font=('Arial', 12, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=5)
        
        self.today_tasks_text = tk.Text(today_frame, font=('Consolas', 10),
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       height=10, wrap=tk.WORD)
        self.today_tasks_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Upcoming tasks
        upcoming_frame = tk.Frame(calendar_frame, bg=self.colors['card'], relief='raised', bd=1)
        upcoming_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(upcoming_frame, text="📆 Upcoming Tasks", font=('Arial', 12, 'bold'),
                fg=self.colors['secondary'], bg=self.colors['card']).pack(pady=5)
        
        self.upcoming_tasks_text = tk.Text(upcoming_frame, font=('Consolas', 10),
                                          bg=self.colors['bg'], fg=self.colors['text'],
                                          height=10, wrap=tk.WORD)
        self.upcoming_tasks_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh schedule
        self.refresh_schedule()
    
    def create_logs_tab(self, notebook):
        """Create logs tab"""
        logs_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(logs_frame, text="📋 Logs")
        
        # Logs display
        logs_display_frame = tk.Frame(logs_frame, bg=self.colors['card'], relief='raised', bd=1)
        logs_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(logs_display_frame, text="📋 Task Execution Logs", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Logs text
        logs_container = tk.Frame(logs_display_frame, bg=self.colors['card'])
        logs_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        logs_scrollbar = tk.Scrollbar(logs_container)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logs_text = tk.Text(logs_container, font=('Consolas', 10),
                                bg=self.colors['bg'], fg=self.colors['text'],
                                wrap=tk.WORD, yscrollcommand=logs_scrollbar.set)
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_scrollbar.config(command=self.logs_text.yview)
        
        # Log actions
        log_actions_frame = tk.Frame(logs_display_frame, bg=self.colors['card'])
        log_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(log_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_logs).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_actions_frame, text="🗑️ Clear",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_actions_frame, text="📄 Export",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.export_logs).pack(side=tk.LEFT, padx=5)
        
        # Load logs
        self.refresh_logs()
    
    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings display
        settings_display_frame = tk.Frame(settings_frame, bg=self.colors['card'], relief='raised', bd=1)
        settings_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(settings_display_frame, text="⚙️ Scheduler Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Settings options
        settings_options_frame = tk.Frame(settings_display_frame, bg=self.colors['card'])
        settings_options_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Auto start
        self.auto_start_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_options_frame, text="🚀 Auto-start scheduler",
                      variable=self.auto_start_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=5)
        
        # Max concurrent tasks
        max_tasks_frame = tk.Frame(settings_options_frame, bg=self.colors['card'])
        max_tasks_frame.pack(fill=tk.X, pady=5)
        tk.Label(max_tasks_frame, text="⚙️ Max concurrent tasks:",
                font=('Arial', 11), fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.max_concurrent_var = tk.IntVar(value=5)
        max_tasks_spinbox = tk.Spinbox(max_tasks_frame, from_=1, to=20, textvariable=self.max_concurrent_var,
                                       font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        max_tasks_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Log retention
        retention_frame = tk.Frame(settings_options_frame, bg=self.colors['card'])
        retention_frame.pack(fill=tk.X, pady=5)
        tk.Label(retention_frame, text="📋 Log retention (days):",
                font=('Arial', 11), fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.log_retention_var = tk.IntVar(value=30)
        retention_spinbox = tk.Spinbox(retention_frame, from_=1, to=365, textvariable=self.log_retention_var,
                                       font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        retention_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Save button
        tk.Button(settings_display_frame, text="💾 Save Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_settings).pack(pady=20)
    
    def start_scheduler(self):
        """Start the scheduler"""
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.status_label.config(text="● Scheduler Running", fg=self.colors['success'])
        self.start_stop_btn.config(text="⏸️ Stop", bg=self.colors['warning'])
    
    def toggle_scheduler(self):
        """Toggle scheduler on/off"""
        if self.scheduler_running:
            self.scheduler_running = False
            self.status_label.config(text="● Scheduler Stopped", fg=self.colors['danger'])
            self.start_stop_btn.config(text="▶️ Start", bg=self.colors['success'])
        else:
            self.start_scheduler()
    
    def scheduler_loop(self):
        """Main scheduler loop"""
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                
                for task in self.tasks:
                    if self.should_run_task(task, current_time):
                        self.run_task(task)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.add_log(f"Scheduler error: {e}")
                time.sleep(60)
    
    def should_run_task(self, task, current_time):
        """Check if task should run"""
        if not task.get('enabled', True):
            return False
        
        schedule_type = task.get('schedule_type', 'once')
        last_run = task.get('last_run')
        
        if schedule_type == 'once':
            return last_run is None and current_time >= datetime.fromisoformat(task['scheduled_time'])
        
        elif schedule_type == 'daily':
            if last_run:
                last_run_date = datetime.fromisoformat(last_run).date()
                if last_run_date >= current_time.date():
                    return False
            
            scheduled_time = datetime.fromisoformat(task['scheduled_time']).time()
            return current_time.time() >= scheduled_time
        
        elif schedule_type == 'weekly':
            if last_run:
                last_run_date = datetime.fromisoformat(last_run).date()
                days_diff = (current_time.date() - last_run_date).days
                if days_diff < 7:
                    return False
            
            scheduled_day = datetime.fromisoformat(task['scheduled_time']).weekday()
            return current_time.weekday() == scheduled_day
        
        elif schedule_type == 'hourly':
            if last_run:
                last_run_time = datetime.fromisoformat(last_run)
                if (current_time - last_run_time).seconds < 3600:
                    return False
            
            return True
        
        return False
    
    def run_task(self, task):
        """Run a task"""
        try:
            self.add_log(f"Running task: {task['name']}")
            
            task_type = task.get('type', 'command')
            
            if task_type == 'command':
                command = task.get('command', '')
                if command:
                    subprocess.Popen(command, shell=True)
            
            elif task_type == 'script':
                script_path = task.get('script_path', '')
                if script_path and os.path.exists(script_path):
                    subprocess.Popen(['python', script_path])
            
            elif task_type == 'message':
                message = task.get('message', '')
                if message:
                    messagebox.showinfo("Scheduled Task", message)
            
            # Update last run time
            task['last_run'] = datetime.now().isoformat()
            self.save_tasks()
            
            self.add_log(f"Task completed: {task['name']}")
            
        except Exception as e:
            self.add_log(f"Task failed: {task['name']} - {e}")
    
    def run_task_now(self):
        """Run selected task immediately"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to run!")
            return
        
        task_index = selection[0]
        if task_index < len(self.tasks):
            task = self.tasks[task_index]
            
            # Run in thread to avoid blocking UI
            threading.Thread(target=self.run_task, args=(task,), daemon=True).start()
    
    def add_task(self):
        """Add new task"""
        self.task_dialog = tk.Toplevel(self.root)
        self.task_dialog.title("Add Task")
        self.task_dialog.geometry("500x600")
        self.task_dialog.configure(bg=self.colors['bg'])
        
        # Task name
        tk.Label(self.task_dialog, text="Task Name:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.task_name_var = tk.StringVar()
        tk.Entry(self.task_dialog, textvariable=self.task_name_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Task type
        tk.Label(self.task_dialog, text="Task Type:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.task_type_var = tk.StringVar(value="command")
        type_combo = ttk.Combobox(self.task_dialog, textvariable=self.task_type_var,
                                 values=["command", "script", "message"], state="readonly")
        type_combo.pack(fill=tk.X, padx=20, pady=5)
        
        # Command/Script/Message
        tk.Label(self.task_dialog, text="Command/Script Path/Message:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.task_command_var = tk.StringVar()
        tk.Entry(self.task_dialog, textvariable=self.task_command_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Schedule type
        tk.Label(self.task_dialog, text="Schedule Type:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.schedule_type_var = tk.StringVar(value="daily")
        schedule_combo = ttk.Combobox(self.task_dialog, textvariable=self.schedule_type_var,
                                      values=["once", "daily", "weekly", "hourly"], state="readonly")
        schedule_combo.pack(fill=tk.X, padx=20, pady=5)
        
        # Scheduled time
        tk.Label(self.task_dialog, text="Scheduled Time:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.scheduled_time_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        tk.Entry(self.task_dialog, textvariable=self.scheduled_time_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Enabled
        self.task_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.task_dialog, text="Enable task",
                      variable=self.task_enabled_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['bg'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Description
        tk.Label(self.task_dialog, text="Description:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.task_description_var = tk.StringVar()
        tk.Entry(self.task_dialog, textvariable=self.task_description_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.task_dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(button_frame, text="💾 Save",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_task).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(button_frame, text="❌ Cancel",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.task_dialog.destroy).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def save_task(self):
        """Save task from dialog"""
        try:
            task = {
                'name': self.task_name_var.get(),
                'type': self.task_type_var.get(),
                'command': self.task_command_var.get(),
                'script_path': self.task_command_var.get(),
                'message': self.task_command_var.get(),
                'schedule_type': self.schedule_type_var.get(),
                'scheduled_time': self.scheduled_time_var.get(),
                'enabled': self.task_enabled_var.get(),
                'description': self.task_description_var.get(),
                'created_at': datetime.now().isoformat(),
                'last_run': None
            }
            
            self.tasks.append(task)
            self.save_tasks()
            self.refresh_tasks()
            self.refresh_schedule()
            
            self.task_dialog.destroy()
            self.add_log(f"Task added: {task['name']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save task: {e}")
    
    def edit_task(self):
        """Edit selected task"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to edit!")
            return
        
        task_index = selection[0]
        if task_index >= len(self.tasks):
            return
        
        task = self.tasks[task_index]
        
        # Create edit dialog (similar to add dialog but pre-filled)
        self.task_dialog = tk.Toplevel(self.root)
        self.task_dialog.title("Edit Task")
        self.task_dialog.geometry("500x600")
        self.task_dialog.configure(bg=self.colors['bg'])
        
        # Pre-fill fields
        self.task_name_var = tk.StringVar(value=task.get('name', ''))
        self.task_type_var = tk.StringVar(value=task.get('type', 'command'))
        self.task_command_var = tk.StringVar(value=task.get('command', task.get('script_path', task.get('message', ''))))
        self.schedule_type_var = tk.StringVar(value=task.get('schedule_type', 'daily'))
        self.scheduled_time_var = tk.StringVar(value=task.get('scheduled_time', ''))
        self.task_enabled_var = tk.BooleanVar(value=task.get('enabled', True))
        self.task_description_var = tk.StringVar(value=task.get('description', ''))
        
        # Create same UI as add task
        tk.Label(self.task_dialog, text="Task Name:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        tk.Entry(self.task_dialog, textvariable=self.task_name_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(self.task_dialog, text="Task Type:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        ttk.Combobox(self.task_dialog, textvariable=self.task_type_var,
                     values=["command", "script", "message"], state="readonly").pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(self.task_dialog, text="Command/Script Path/Message:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        tk.Entry(self.task_dialog, textvariable=self.task_command_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(self.task_dialog, text="Schedule Type:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        ttk.Combobox(self.task_dialog, textvariable=self.schedule_type_var,
                     values=["once", "daily", "weekly", "hourly"], state="readonly").pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(self.task_dialog, text="Scheduled Time:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        tk.Entry(self.task_dialog, textvariable=self.scheduled_time_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        tk.Checkbutton(self.task_dialog, text="Enable task",
                      variable=self.task_enabled_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['bg'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        tk.Label(self.task_dialog, text="Description:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        tk.Entry(self.task_dialog, textvariable=self.task_description_var,
                font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text']).pack(fill=tk.X, padx=20, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.task_dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(button_frame, text="💾 Update",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=lambda: self.update_task(task_index)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(button_frame, text="❌ Cancel",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.task_dialog.destroy).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def update_task(self, task_index):
        """Update existing task"""
        try:
            task = self.tasks[task_index]
            
            task['name'] = self.task_name_var.get()
            task['type'] = self.task_type_var.get()
            task['command'] = self.task_command_var.get()
            task['script_path'] = self.task_command_var.get()
            task['message'] = self.task_command_var.get()
            task['schedule_type'] = self.schedule_type_var.get()
            task['scheduled_time'] = self.scheduled_time_var.get()
            task['enabled'] = self.task_enabled_var.get()
            task['description'] = self.task_description_var.get()
            task['updated_at'] = datetime.now().isoformat()
            
            self.save_tasks()
            self.refresh_tasks()
            self.refresh_schedule()
            
            self.task_dialog.destroy()
            self.add_log(f"Task updated: {task['name']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update task: {e}")
    
    def delete_task(self):
        """Delete selected task"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return
        
        task_index = selection[0]
        if task_index >= len(self.tasks):
            return
        
        task = self.tasks[task_index]
        
        if messagebox.askyesno("Confirm Delete", f"Delete task '{task['name']}'?"):
            del self.tasks[task_index]
            self.save_tasks()
            self.refresh_tasks()
            self.refresh_schedule()
            self.add_log(f"Task deleted: {task['name']}")
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.tasks = data.get('tasks', [])
        except:
            self.tasks = []
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            data['tasks'] = self.tasks
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def refresh_tasks(self):
        """Refresh tasks list"""
        self.tasks_listbox.delete(0, tk.END)
        
        for task in self.tasks:
            status = "✅" if task.get('enabled', True) else "❌"
            schedule_type = task.get('schedule_type', 'once')
            last_run = task.get('last_run')
            
            display_text = f"{status} {task['name']} ({schedule_type})"
            if last_run:
                display_text += f" - Last: {datetime.fromisoformat(last_run).strftime('%Y-%m-%d %H:%M')}"
            
            self.tasks_listbox.insert(tk.END, display_text)
    
    def refresh_schedule(self):
        """Refresh schedule display"""
        current_time = datetime.now()
        
        # Today's tasks
        today_tasks = []
        upcoming_tasks = []
        
        for task in self.tasks:
            if not task.get('enabled', True):
                continue
            
            scheduled_time = datetime.fromisoformat(task['scheduled_time'])
            
            if scheduled_time.date() == current_time.date():
                today_tasks.append(f"📅 {task['name']} - {scheduled_time.strftime('%H:%M')} ({task.get('schedule_type', 'once')})")
            elif scheduled_time.date() > current_time.date():
                upcoming_tasks.append(f"📆 {task['name']} - {scheduled_time.strftime('%Y-%m-%d %H:%M')} ({task.get('schedule_type', 'once')})")
        
        # Update today's tasks
        self.today_tasks_text.delete(1.0, tk.END)
        if today_tasks:
            self.today_tasks_text.insert(1.0, "\n".join(today_tasks))
        else:
            self.today_tasks_text.insert(1.0, "No tasks scheduled for today")
        
        # Update upcoming tasks
        self.upcoming_tasks_text.delete(1.0, tk.END)
        if upcoming_tasks:
            self.upcoming_tasks_text.insert(1.0, "\n".join(upcoming_tasks[:20]))  # Show first 20
        else:
            self.upcoming_tasks_text.insert(1.0, "No upcoming tasks")
    
    def add_log(self, message):
        """Add log entry"""
        try:
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
            self.logs_text.insert(tk.END, log_entry)
            self.logs_text.see(tk.END)
            
            # Also save to file
            log_file = "task_scheduler.log"
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except:
            pass
    
    def refresh_logs(self):
        """Refresh logs display"""
        try:
            log_file = "task_scheduler.log"
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = f.readlines()
                
                self.logs_text.delete(1.0, tk.END)
                for log in logs[-100:]:  # Show last 100 lines
                    self.logs_text.insert(tk.END, log)
                self.logs_text.see(tk.END)
        except:
            pass
    
    def clear_logs(self):
        """Clear logs"""
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            try:
                self.logs_text.delete(1.0, tk.END)
                log_file = "task_scheduler.log"
                with open(log_file, 'w') as f:
                    f.write("")
                self.add_log("Logs cleared")
            except:
                pass
    
    def export_logs(self):
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def save_settings(self):
        """Save scheduler settings"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            data['settings'] = {
                'auto_start': self.auto_start_var.get(),
                'max_concurrent_tasks': self.max_concurrent_var.get(),
                'log_retention_days': self.log_retention_var.get()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = TaskScheduler(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting task scheduler: {e}")

if __name__ == "__main__":
    main()
