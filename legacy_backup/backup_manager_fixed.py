#!/usr/bin/env python3
"""
Backup Manager - Fixed Working Version
Simple backup management tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os
import json
import zipfile
from datetime import datetime
import threading
import time

class BackupManager:
    def __init__(self, root):
        self.root = root
        self.root.title("💾 Backup Manager")
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
            'success': '#00ff88',
            'text': '#ffffff',
            'text_secondary': '#cccccc'
        }
        
        # Backup state
        self.backup_running = False
        self.backup_dir = "backups"
        
        # Data file
        self.data_file = "backup_manager_data.json"
        
        # Initialize
        self.init_backup_system()
        self.create_widgets()
        self.load_backup_history()
    
    def init_backup_system(self):
        """Initialize backup system"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        if not os.path.exists(self.data_file):
            default_data = {
                "backup_history": [],
                "settings": {
                    "default_backup_dir": self.backup_dir,
                    "compression": True,
                    "max_backups": 10
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="💾 Backup Manager", 
                font=('Arial', 18, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Status indicator
        self.status_label = tk.Label(header_frame, text="● Ready", 
                                     font=('Arial', 12, 'bold'),
                                     fg=self.colors['success'], bg=self.colors['card'])
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Main content with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Backup tab
        self.create_backup_tab(notebook)
        
        # Restore tab
        self.create_restore_tab(notebook)
        
        # History tab
        self.create_history_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
    
    def create_backup_tab(self, notebook):
        """Create backup tab"""
        backup_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(backup_frame, text="💾 Backup")
        
        # Source selection
        source_frame = tk.Frame(backup_frame, bg=self.colors['card'], relief='raised', bd=1)
        source_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(source_frame, text="📁 Select Source", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Source path
        path_frame = tk.Frame(source_frame, bg=self.colors['card'])
        path_frame.pack(fill=tk.X, pady=5, padx=20)
        
        tk.Label(path_frame, text="Source Path:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.source_path_var = tk.StringVar(value=os.getcwd())
        self.source_entry = tk.Entry(path_frame, textvariable=self.source_path_var, 
                                     font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(path_frame, text="📂 Browse",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.browse_source).pack(side=tk.RIGHT, padx=5)
        
        # Backup options
        options_frame = tk.Frame(backup_frame, bg=self.colors['card'], relief='raised', bd=1)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(options_frame, text="⚙️ Backup Options", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Options
        self.compression_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="🗜️ Enable compression",
                      variable=self.compression_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        self.include_hidden_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="👁️ Include hidden files",
                      variable=self.include_hidden_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', padx=20, pady=5)
        
        # Backup name
        name_frame = tk.Frame(options_frame, bg=self.colors['card'])
        name_frame.pack(fill=tk.X, pady=5, padx=20)
        
        tk.Label(name_frame, text="Backup Name:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.backup_name_var = tk.StringVar(value=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.backup_name_entry = tk.Entry(name_frame, textvariable=self.backup_name_var,
                                         font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.backup_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Progress
        self.progress_frame = tk.Frame(backup_frame, bg=self.colors['card'], relief='raised', bd=1)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(self.progress_frame, text="📊 Progress", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)
        
        self.progress_label = tk.Label(self.progress_frame, text="Ready to start backup",
                                     font=('Arial', 10), fg=self.colors['text'], bg=self.colors['card'])
        self.progress_label.pack(pady=5)
        
        # Action buttons
        action_frame = tk.Frame(backup_frame, bg=self.colors['bg'])
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.backup_btn = tk.Button(action_frame, text="🚀 Start Backup",
                                   font=('Arial', 12, 'bold'),
                                   bg=self.colors['primary'], fg='white',
                                   relief='flat', cursor='hand2',
                                   command=self.start_backup)
        self.backup_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(action_frame, text="🔄 Refresh",
                 font=('Arial', 12, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_interface).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_restore_tab(self, notebook):
        """Create restore tab"""
        restore_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(restore_frame, text="🔄 Restore")
        
        # Available backups
        backups_frame = tk.Frame(restore_frame, bg=self.colors['card'], relief='raised', bd=1)
        backups_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(backups_frame, text="📋 Available Backups", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Backups list
        self.backups_listbox = tk.Listbox(backups_frame, font=('Arial', 11),
                                          bg=self.colors['bg'], fg=self.colors['text'])
        self.backups_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Restore actions
        restore_actions_frame = tk.Frame(backups_frame, bg=self.colors['card'])
        restore_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(restore_actions_frame, text="🔄 Restore Selected",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        
        tk.Button(restore_actions_frame, text="🗑️ Delete",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.delete_backup).pack(side=tk.LEFT, padx=5)
        
        tk.Button(restore_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_backups).pack(side=tk.LEFT, padx=5)
        
        # Restore destination
        dest_frame = tk.Frame(restore_frame, bg=self.colors['card'], relief='raised', bd=1)
        dest_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(dest_frame, text="📁 Restore Destination", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        dest_path_frame = tk.Frame(dest_frame, bg=self.colors['card'])
        dest_path_frame.pack(fill=tk.X, pady=5, padx=20)
        
        tk.Label(dest_path_frame, text="Destination:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.dest_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "restored"))
        self.dest_entry = tk.Entry(dest_path_frame, textvariable=self.dest_path_var,
                                   font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(dest_path_frame, text="📂 Browse",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.browse_destination).pack(side=tk.RIGHT, padx=5)
        
        # Load backups
        self.refresh_backups()
    
    def create_history_tab(self, notebook):
        """Create history tab"""
        history_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(history_frame, text="📋 History")
        
        # History display
        history_display_frame = tk.Frame(history_frame, bg=self.colors['card'], relief='raised', bd=1)
        history_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(history_display_frame, text="📋 Backup History", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # History text
        self.history_text = tk.Text(history_display_frame, font=('Consolas', 10),
                                   bg=self.colors['bg'], fg=self.colors['text'],
                                   wrap=tk.WORD)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # History scrollbar
        history_scrollbar = tk.Scrollbar(self.history_text)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=history_scrollbar.set)
        history_scrollbar.config(command=self.history_text.yview)
        
        # History actions
        history_actions_frame = tk.Frame(history_display_frame, bg=self.colors['card'])
        history_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(history_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        
        tk.Button(history_actions_frame, text="🗑️ Clear History",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        # Load history
        self.refresh_history()
    
    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings display
        settings_display_frame = tk.Frame(settings_frame, bg=self.colors['card'], relief='raised', bd=1)
        settings_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(settings_display_frame, text="⚙️ Backup Settings", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Settings options
        settings_options_frame = tk.Frame(settings_display_frame, bg=self.colors['card'])
        settings_options_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Default backup directory
        tk.Label(settings_options_frame, text="📁 Default Backup Directory:",
                font=('Arial', 11), fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w', pady=5)
        
        self.backup_dir_var = tk.StringVar(value=self.backup_dir)
        backup_dir_entry = tk.Entry(settings_options_frame, textvariable=self.backup_dir_var,
                                   font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        backup_dir_entry.pack(fill=tk.X, pady=5)
        
        # Max backups
        tk.Label(settings_options_frame, text="🔢 Maximum Backups to Keep:",
                font=('Arial', 11), fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w', pady=5)
        
        self.max_backups_var = tk.IntVar(value=10)
        max_backups_spinbox = tk.Spinbox(settings_options_frame, from_=1, to=100, textvariable=self.max_backups_var,
                                         font=('Arial', 11), bg=self.colors['bg'], fg=self.colors['text'])
        max_backups_spinbox.pack(fill=tk.X, pady=5)
        
        # Auto cleanup
        self.auto_cleanup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_options_frame, text="🧹 Automatically cleanup old backups",
                      variable=self.auto_cleanup_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=5)
        
        # Save button
        tk.Button(settings_display_frame, text="💾 Save Settings",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.save_settings).pack(pady=20)
    
    def browse_source(self):
        """Browse for source directory"""
        directory = filedialog.askdirectory(initialdir=self.source_path_var.get())
        if directory:
            self.source_path_var.set(directory)
    
    def browse_destination(self):
        """Browse for restore destination"""
        directory = filedialog.askdirectory(initialdir=self.dest_path_var.get())
        if directory:
            self.dest_path_var.set(directory)
    
    def start_backup(self):
        """Start backup process"""
        if self.backup_running:
            return
        
        source_path = self.source_path_var.get()
        backup_name = self.backup_name_var.get()
        
        if not source_path or not os.path.exists(source_path):
            messagebox.showerror("Error", "Invalid source path!")
            return
        
        if not backup_name:
            messagebox.showerror("Error", "Please enter a backup name!")
            return
        
        self.backup_running = True
        self.backup_btn.config(text="⏳ Backing up...", state='disabled')
        self.status_label.config(text="● Backing up...", fg=self.colors['warning'])
        
        # Run backup in thread
        threading.Thread(target=self.perform_backup, args=(source_path, backup_name), daemon=True).start()
    
    def perform_backup(self, source_path, backup_name):
        """Perform the actual backup"""
        try:
            # Create backup filename
            if self.compression_var.get():
                backup_filename = f"{backup_name}.zip"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                
                # Create ZIP backup
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(source_path):
                        for file in files:
                            if not self.include_hidden_var.get() and file.startswith('.'):
                                continue
                            
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_path)
                            zipf.write(file_path, arcname)
                            
                            # Update progress
                            self.root.after(0, self.update_progress, f"Backing up: {file}")
            else:
                backup_filename = f"{backup_name}"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                
                # Create directory backup
                shutil.copytree(source_path, backup_path, ignore=shutil.ignore_patterns('.git'))
            
            # Record backup in history
            self.record_backup(backup_name, backup_path, source_path)
            
            # Update UI
            self.root.after(0, self.backup_complete, True, "Backup completed successfully!")
            
        except Exception as e:
            self.root.after(0, self.backup_complete, False, f"Backup failed: {e}")
    
    def update_progress(self, message):
        """Update progress display"""
        self.progress_label.config(text=message)
        self.progress_bar['value'] = min(self.progress_bar['value'] + 10, 100)
    
    def backup_complete(self, success, message):
        """Handle backup completion"""
        self.backup_running = False
        self.backup_btn.config(text="🚀 Start Backup", state='normal')
        
        if success:
            self.status_label.config(text="● Backup complete", fg=self.colors['success'])
            self.progress_bar['value'] = 100
            messagebox.showinfo("Backup Complete", message)
        else:
            self.status_label.config(text="● Backup failed", fg=self.colors['danger'])
            self.progress_bar['value'] = 0
            messagebox.showerror("Backup Failed", message)
        
        # Reset progress after delay
        self.root.after(3000, self.reset_progress)
        self.refresh_backups()
    
    def reset_progress(self):
        """Reset progress display"""
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready to start backup")
        self.status_label.config(text="● Ready", fg=self.colors['success'])
    
    def refresh_backups(self):
        """Refresh backup list"""
        self.backups_listbox.delete(0, tk.END)
        
        if os.path.exists(self.backup_dir):
            for item in os.listdir(self.backup_dir):
                item_path = os.path.join(self.backup_dir, item)
                if os.path.isfile(item_path) or os.path.isdir(item_path):
                    size = self.get_size(item_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M:%S")
                    self.backups_listbox.insert(tk.END, f"{item} - {size} - {modified}")
    
    def get_size(self, path):
        """Get human readable size"""
        if os.path.isfile(path):
            size = os.path.getsize(path)
        else:
            size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                      for dirpath, dirnames, filenames in os.walk(path) 
                      for filename in filenames)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def restore_backup(self):
        """Restore selected backup"""
        selection = self.backups_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a backup to restore!")
            return
        
        selected_text = self.backups_listbox.get(selection[0])
        backup_name = selected_text.split(" - ")[0]
        backup_path = os.path.join(self.backup_dir, backup_name)
        dest_path = self.dest_path_var.get()
        
        if not os.path.exists(backup_path):
            messagebox.showerror("Error", "Backup file not found!")
            return
        
        if not dest_path:
            messagebox.showerror("Error", "Please specify restore destination!")
            return
        
        if messagebox.askyesno("Confirm Restore", f"Restore '{backup_name}' to '{dest_path}'?"):
            try:
                if backup_path.endswith('.zip'):
                    # Extract ZIP
                    with zipfile.ZipFile(backup_path, 'r') as zipf:
                        zipf.extractall(dest_path)
                else:
                    # Copy directory
                    shutil.copytree(backup_path, dest_path, dirs_exist_ok=True)
                
                messagebox.showinfo("Restore Complete", f"Backup restored to {dest_path}")
                self.record_operation("restore", backup_name, dest_path)
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Failed to restore backup: {e}")
    
    def delete_backup(self):
        """Delete selected backup"""
        selection = self.backups_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a backup to delete!")
            return
        
        selected_text = self.backups_listbox.get(selection[0])
        backup_name = selected_text.split(" - ")[0]
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if messagebox.askyesno("Confirm Delete", f"Delete backup '{backup_name}'?"):
            try:
                if os.path.isfile(backup_path):
                    os.remove(backup_path)
                else:
                    shutil.rmtree(backup_path)
                
                messagebox.showinfo("Delete Complete", "Backup deleted successfully")
                self.refresh_backups()
                self.record_operation("delete", backup_name, "")
            except Exception as e:
                messagebox.showerror("Delete Failed", f"Failed to delete backup: {e}")
    
    def record_backup(self, name, path, source):
        """Record backup in history"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            backup_info = {
                "name": name,
                "path": path,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "size": self.get_size(path),
                "type": "backup"
            }
            
            data["backup_history"].append(backup_info)
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def record_operation(self, operation, name, path):
        """Record operation in history"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            operation_info = {
                "operation": operation,
                "name": name,
                "path": path,
                "timestamp": datetime.now().isoformat(),
                "type": "operation"
            }
            
            data["backup_history"].append(operation_info)
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def load_backup_history(self):
        """Load backup history"""
        try:
            with open(self.data_file, 'r') as f:
                self.backup_data = json.load(f)
        except:
            self.backup_data = {"backup_history": [], "settings": {}}
    
    def refresh_history(self):
        """Refresh history display"""
        self.history_text.delete(1.0, tk.END)
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                history = data.get("backup_history", [])
            
            for item in reversed(history[-50:]):  # Show last 50 items
                timestamp = item.get("timestamp", "")
                operation = item.get("operation", item.get("type", "unknown"))
                name = item.get("name", "")
                path = item.get("path", "")
                
                history_entry = f"[{timestamp}] {operation.upper()}: {name}\n"
                if path:
                    history_entry += f"  Path: {path}\n"
                
                self.history_text.insert(tk.END, history_entry + "\n")
            
            self.history_text.see(tk.END)
        except:
            self.history_text.insert(tk.END, "No history available")
    
    def clear_history(self):
        """Clear backup history"""
        if messagebox.askyesno("Confirm", "Clear all backup history?"):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                data["backup_history"] = []
                
                with open(self.data_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                self.refresh_history()
                messagebox.showinfo("Success", "History cleared successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {e}")
    
    def save_settings(self):
        """Save settings"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            data["settings"] = {
                "default_backup_dir": self.backup_dir_var.get(),
                "compression": self.compression_var.get(),
                "max_backups": self.max_backups_var.get(),
                "auto_cleanup": self.auto_cleanup_var.get()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def refresh_interface(self):
        """Refresh interface"""
        self.refresh_backups()
        self.refresh_history()
        messagebox.showinfo("Refresh", "Interface refreshed!")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = BackupManager(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting backup manager: {e}")

if __name__ == "__main__":
    main()
