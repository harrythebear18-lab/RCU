#!/usr/bin/env python3
"""
Database Schema - Fixed Working Version
Simple database schema management tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import json
import os
from datetime import datetime

class DatabaseSchema:
    def __init__(self, root):
        self.root = root
        self.root.title("🗄️ Database Schema Manager")
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
        
        # Database connection
        self.db_connection = None
        self.current_db = "homelab.db"
        
        # Create widgets
        self.create_widgets()
        self.connect_database()
    
    def create_widgets(self):
        """Create main widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['card'], relief='raised', bd=1)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(header_frame, text="🗄️ Database Schema Manager", 
                font=('Arial', 18, 'bold'), 
                fg=self.colors['primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Database status
        self.db_status_label = tk.Label(header_frame, text="● Not connected", 
                                       font=('Arial', 12, 'bold'),
                                       fg=self.colors['danger'], bg=self.colors['card'])
        self.db_status_label.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Database controls
        db_controls_frame = tk.Frame(header_frame, bg=self.colors['card'])
        db_controls_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Button(db_controls_frame, text="📁 Open",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.open_database).pack(side=tk.LEFT, padx=2)
        
        tk.Button(db_controls_frame, text="➕ New",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.create_database).pack(side=tk.LEFT, padx=2)
        
        # Main content with notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_schema_tab(notebook)
        self.create_tables_tab(notebook)
        self.create_query_tab(notebook)
        self.create_export_tab(notebook)
    
    def create_schema_tab(self, notebook):
        """Create schema overview tab"""
        schema_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(schema_frame, text="📋 Schema")
        
        # Schema display
        schema_display_frame = tk.Frame(schema_frame, bg=self.colors['card'], relief='raised', bd=1)
        schema_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(schema_display_frame, text="📋 Database Schema Overview", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Schema text
        self.schema_text = tk.Text(schema_display_frame, font=('Consolas', 10),
                                  bg=self.colors['bg'], fg=self.colors['text'],
                                  wrap=tk.NONE)
        self.schema_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Schema scrollbar
        schema_scrollbar_v = tk.Scrollbar(self.schema_text, orient='vertical')
        schema_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.schema_text.config(yscrollcommand=schema_scrollbar_v.set)
        schema_scrollbar_v.config(command=self.schema_text.yview)
        
        schema_scrollbar_h = tk.Scrollbar(self.schema_text, orient='horizontal')
        schema_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.schema_text.config(xscrollcommand=schema_scrollbar_h.set)
        schema_scrollbar_h.config(command=self.schema_text.xview)
        
        # Schema actions
        schema_actions_frame = tk.Frame(schema_display_frame, bg=self.colors['card'])
        schema_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(schema_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_schema).pack(side=tk.LEFT, padx=5)
        
        tk.Button(schema_actions_frame, text="📄 Generate Schema SQL",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.generate_schema_sql).pack(side=tk.LEFT, padx=5)
        
        tk.Button(schema_actions_frame, text="📋 Show Tables",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.show_tables).pack(side=tk.LEFT, padx=5)
    
    def create_tables_tab(self, notebook):
        """Create tables management tab"""
        tables_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(tables_frame, text="📊 Tables")
        
        # Tables list
        tables_list_frame = tk.Frame(tables_frame, bg=self.colors['card'], relief='raised', bd=1)
        tables_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(tables_list_frame, text="📊 Database Tables", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Tables listbox with scrollbar
        tables_container = tk.Frame(tables_list_frame, bg=self.colors['card'])
        tables_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(tables_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tables_listbox = tk.Listbox(tables_container, font=('Consolas', 11),
                                         bg=self.colors['bg'], fg=self.colors['text'],
                                         yscrollcommand=scrollbar.set)
        self.tables_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tables_listbox.yview)
        
        # Bind double-click
        self.tables_listbox.bind('<Double-Button-1>', self.show_table_structure)
        
        # Table actions
        table_actions_frame = tk.Frame(tables_list_frame, bg=self.colors['card'])
        table_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(table_actions_frame, text="📋 Structure",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.show_table_structure).pack(side=tk.LEFT, padx=5)
        
        tk.Button(table_actions_frame, text="📄 Data",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.show_table_data).pack(side=tk.LEFT, padx=5)
        
        tk.Button(table_actions_frame, text="🗑️ Drop",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['danger'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.drop_table).pack(side=tk.LEFT, padx=5)
        
        tk.Button(table_actions_frame, text="🔄 Refresh",
                 font=('Arial', 10, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.refresh_tables).pack(side=tk.LEFT, padx=5)
    
    def create_query_tab(self, notebook):
        """Create query tab"""
        query_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(query_frame, text="🔍 Query")
        
        # Query interface
        query_interface_frame = tk.Frame(query_frame, bg=self.colors['card'], relief='raised', bd=1)
        query_interface_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(query_interface_frame, text="🔍 SQL Query", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Query text
        query_text_frame = tk.Frame(query_interface_frame, bg=self.colors['card'])
        query_text_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(query_text_frame, text="SQL Query:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(anchor='w')
        
        self.query_text = tk.Text(query_text_frame, font=('Consolas', 11),
                                  bg=self.colors['bg'], fg=self.colors['text'],
                                  height=8, wrap=tk.NONE)
        self.query_text.pack(fill=tk.X, pady=5)
        
        # Query scrollbar
        query_scrollbar_v = tk.Scrollbar(self.query_text, orient='vertical')
        query_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.query_text.config(yscrollcommand=query_scrollbar_v.set)
        query_scrollbar_v.config(command=self.query_text.yview)
        
        query_scrollbar_h = tk.Scrollbar(self.query_text, orient='horizontal')
        query_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.query_text.config(xscrollcommand=query_scrollbar_h.set)
        query_scrollbar_h.config(command=self.query_text.xview)
        
        # Query actions
        query_actions_frame = tk.Frame(query_interface_frame, bg=self.colors['card'])
        query_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(query_actions_frame, text="▶️ Execute",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['success'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.execute_query).pack(side=tk.LEFT, padx=5)
        
        tk.Button(query_actions_frame, text="🗑️ Clear",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['warning'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.clear_query).pack(side=tk.LEFT, padx=5)
        
        tk.Button(query_actions_frame, text="📋 Templates",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['secondary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.show_query_templates).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = tk.Frame(query_interface_frame, bg=self.colors['card'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(results_frame, text="📊 Query Results", font=('Arial', 12, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=5)
        
        # Results text
        results_container = tk.Frame(results_frame, bg=self.colors['card'])
        results_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        results_scrollbar = tk.Scrollbar(results_container)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(results_container, font=('Consolas', 10),
                                    bg=self.colors['bg'], fg=self.colors['text'],
                                    wrap=tk.NONE, yscrollcommand=results_scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.config(command=self.results_text.yview)
    
    def create_export_tab(self, notebook):
        """Create export tab"""
        export_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(export_frame, text="📤 Export")
        
        # Export options
        export_options_frame = tk.Frame(export_frame, bg=self.colors['card'], relief='raised', bd=1)
        export_options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(export_options_frame, text="📤 Export Database", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Export format
        format_frame = tk.Frame(export_options_frame, bg=self.colors['card'])
        format_frame.pack(fill=tk.X, pady=5, padx=20)
        tk.Label(format_frame, text="📄 Export Format:", font=('Arial', 11),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        self.export_format_var = tk.StringVar(value="sql")
        format_combo = ttk.Combobox(format_frame, textvariable=self.export_format_var,
                                   values=["sql", "json", "csv"], state="readonly")
        format_combo.pack(side=tk.RIGHT, padx=5)
        
        # Export options
        options_frame = tk.Frame(export_options_frame, bg=self.colors['card'])
        options_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.export_schema_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="📋 Include schema",
                      variable=self.export_schema_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        self.export_data_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="📊 Include data",
                      variable=self.export_data_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        self.export_indexes_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="🔑 Include indexes",
                      variable=self.export_indexes_var, font=('Arial', 11),
                      fg=self.colors['text'], bg=self.colors['card'],
                      selectcolor=self.colors['bg']).pack(anchor='w', pady=2)
        
        # Export button
        export_button_frame = tk.Frame(export_options_frame, bg=self.colors['card'])
        export_button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(export_button_frame, text="📤 Export Database",
                 font=('Arial', 12, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=self.export_database).pack(fill=tk.X)
        
        # Preview
        preview_frame = tk.Frame(export_frame, bg=self.colors['card'], relief='raised', bd=1)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(preview_frame, text="👁️ Export Preview", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['card']).pack(pady=10)
        
        # Preview text
        preview_container = tk.Frame(preview_frame, bg=self.colors['card'])
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        preview_scrollbar = tk.Scrollbar(preview_container)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_text = tk.Text(preview_container, font=('Consolas', 10),
                                    bg=self.colors['bg'], fg=self.colors['text'],
                                    wrap=tk.NONE, yscrollcommand=preview_scrollbar.set)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.config(command=self.preview_text.yview)
    
    def connect_database(self):
        """Connect to database"""
        try:
            if os.path.exists(self.current_db):
                self.db_connection = sqlite3.connect(self.current_db)
                self.db_status_label.config(text=f"● Connected to {self.current_db}", fg=self.colors['success'])
                self.refresh_tables()
                self.refresh_schema()
            else:
                self.create_database()
        except Exception as e:
            self.db_status_label.config(text="● Connection failed", fg=self.colors['danger'])
            messagebox.showerror("Connection Error", f"Failed to connect to database: {e}")
    
    def open_database(self):
        """Open existing database"""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite files", "*.db *.sqlite"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if self.db_connection:
                    self.db_connection.close()
                
                self.current_db = filename
                self.connect_database()
                messagebox.showinfo("Success", f"Connected to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open database: {e}")
    
    def create_database(self):
        """Create new database"""
        filename = filedialog.asksaveasfilename(
            title="Create New Database",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if self.db_connection:
                    self.db_connection.close()
                
                self.current_db = filename
                self.db_connection = sqlite3.connect(filename)
                
                # Create basic tables
                self.create_basic_tables()
                
                self.db_status_label.config(text=f"● Created {filename}", fg=self.colors['success'])
                self.refresh_tables()
                self.refresh_schema()
                messagebox.showinfo("Success", f"Database created: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create database: {e}")
    
    def create_basic_tables(self):
        """Create basic tables for homelab"""
        cursor = self.db_connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                category TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Backups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                size_bytes INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Services table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'stopped',
                port INTEGER,
                config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_started TIMESTAMP
            )
        ''')
        
        # System stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                network_connections INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_connection.commit()
    
    def refresh_schema(self):
        """Refresh schema display"""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            schema_text = "DATABASE SCHEMA\n" + "="*50 + "\n\n"
            
            for table in tables:
                table_name = table[0]
                schema_text += f"TABLE: {table_name}\n"
                schema_text += "-"*30 + "\n"
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    schema_text += f"  {col_name} {col_type}"
                    if pk:
                        schema_text += " PRIMARY KEY"
                    if not_null:
                        schema_text += " NOT NULL"
                    if default_val:
                        schema_text += f" DEFAULT {default_val}"
                    schema_text += "\n"
                
                # Get indexes
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                
                for idx in indexes:
                    if idx[2]:  # Not auto-created index
                        schema_text += f"  INDEX: {idx[1]}\n"
                
                schema_text += "\n"
            
            self.schema_text.delete(1.0, tk.END)
            self.schema_text.insert(1.0, schema_text)
            
        except Exception as e:
            self.schema_text.delete(1.0, tk.END)
            self.schema_text.insert(1.0, f"Error loading schema: {e}")
    
    def show_tables(self):
        """Show all tables"""
        if not self.db_connection:
            messagebox.showwarning("Warning", "No database connected!")
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            tables_text = "DATABASE TABLES\n" + "="*30 + "\n\n"
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                tables_text += f"{table_name}: {count} rows\n"
            
            messagebox.showinfo("Tables", tables_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show tables: {e}")
    
    def refresh_tables(self):
        """Refresh tables list"""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            self.tables_listbox.delete(0, tk.END)
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                self.tables_listbox.insert(tk.END, f"{table_name} ({count} rows)")
                
        except Exception as e:
            print(f"Error refreshing tables: {e}")
    
    def show_table_structure(self, event=None):
        """Show table structure"""
        selection = self.tables_listbox.curselection()
        if not selection:
            return
        
        table_name = self.tables_listbox.get(selection[0]).split(" (")[0]
        
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            structure_text = f"TABLE STRUCTURE: {table_name}\n"
            structure_text += "="*50 + "\n\n"
            structure_text += f"{'Column':<20} {'Type':<15} {'PK':<5} {'NotNull':<8}\n"
            structure_text += "-"*50 + "\n"
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = "✓" if pk else ""
                not_null_str = "✓" if not_null else ""
                structure_text += f"{col_name:<20} {col_type:<15} {pk_str:<5} {not_null_str:<8}\n"
            
            messagebox.showinfo(f"Structure - {table_name}", structure_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show structure: {e}")
    
    def show_table_data(self):
        """Show table data"""
        selection = self.tables_listbox.curselection()
        if not selection:
            return
        
        table_name = self.tables_listbox.get(selection[0]).split(" (")[0]
        
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if not rows:
                messagebox.showinfo(f"Data - {table_name}", "No data in table")
                return
            
            # Format data
            data_text = f"TABLE DATA: {table_name} (First 100 rows)\n"
            data_text += "="*80 + "\n\n"
            
            # Header
            header = " | ".join(f"{col:<15}" for col in columns)
            data_text += header + "\n"
            data_text += "-"*len(header) + "\n"
            
            # Data rows
            for row in rows:
                data_text += " | ".join(f"{str(val):<15}" for val in row) + "\n"
            
            # Show in results tab
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, data_text)
            
            # Switch to query tab
            self.results_text.master.master.select(2)  # Query tab is index 2
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show data: {e}")
    
    def drop_table(self):
        """Drop selected table"""
        selection = self.tables_listbox.curselection()
        if not selection:
            return
        
        table_name = self.tables_listbox.get(selection[0]).split(" (")[0]
        
        if messagebox.askyesno("Confirm Drop", f"Drop table '{table_name}'? This cannot be undone!"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(f"DROP TABLE {table_name}")
                self.db_connection.commit()
                
                self.refresh_tables()
                self.refresh_schema()
                messagebox.showinfo("Success", f"Table '{table_name}' dropped successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to drop table: {e}")
    
    def execute_query(self):
        """Execute SQL query"""
        query = self.query_text.get(1.0, tk.END).strip()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a SQL query!")
            return
        
        if not self.db_connection:
            messagebox.showwarning("Warning", "No database connected!")
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query)
            
            if query.upper().startswith(('SELECT', 'PRAGMA', 'EXPLAIN')):
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    columns = [desc[0] for desc in cursor.description]
                    
                    # Format results
                    results_text = f"QUERY RESULTS ({len(rows)} rows)\n"
                    results_text += "="*80 + "\n\n"
                    
                    # Header
                    header = " | ".join(f"{col:<15}" for col in columns)
                    results_text += header + "\n"
                    results_text += "-"*len(header) + "\n"
                    
                    # Data rows
                    for row in rows:
                        results_text += " | ".join(f"{str(val):<15}" for val in row) + "\n"
                else:
                    results_text = "No results returned"
                
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, results_text)
            else:
                self.db_connection.commit()
                affected = cursor.rowcount
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, f"Query executed successfully!\n\nRows affected: {affected}")
            
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, f"Query Error:\n{e}")
    
    def clear_query(self):
        """Clear query text"""
        self.query_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
    
    def show_query_templates(self):
        """Show query templates"""
        templates = {
            "Select all users": "SELECT * FROM users;",
            "Get system settings": "SELECT * FROM settings WHERE category = 'system';",
            "Recent logs": "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50;",
            "Active services": "SELECT * FROM services WHERE status = 'running';",
            "System stats today": "SELECT * FROM system_stats WHERE DATE(timestamp) = DATE('now');",
            "Create user": "INSERT INTO users (username, password_hash, email, role) VALUES ('newuser', 'hash', 'email@example.com', 'user');",
            "Update setting": "UPDATE settings SET value = 'new_value' WHERE category = 'system' AND key = 'theme';",
            "Delete old logs": "DELETE FROM logs WHERE timestamp < datetime('now', '-30 days');"
        }
        
        # Create template window
        template_window = tk.Toplevel(self.root)
        template_window.title("Query Templates")
        template_window.geometry("400x500")
        template_window.configure(bg=self.colors['bg'])
        
        tk.Label(template_window, text="📋 Query Templates", font=('Arial', 14, 'bold'),
                fg=self.colors['primary'], bg=self.colors['bg']).pack(pady=10)
        
        # Template list
        template_listbox = tk.Listbox(template_window, font=('Consolas', 10),
                                      bg=self.colors['bg'], fg=self.colors['text'])
        template_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for name, query in templates.items():
            template_listbox.insert(tk.END, f"{name}: {query}")
        
        def use_template():
            selection = template_listbox.curselection()
            if selection:
                template_text = template_listbox.get(selection[0])
                query = template_text.split(": ", 1)[1]
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(1.0, query)
                template_window.destroy()
        
        tk.Button(template_window, text="Use Template",
                 font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 relief='flat', cursor='hand2',
                 command=use_template).pack(pady=10)
    
    def export_database(self):
        """Export database"""
        if not self.db_connection:
            messagebox.showwarning("Warning", "No database connected!")
            return
        
        export_format = self.export_format_var.get()
        
        if export_format == "sql":
            self.export_sql()
        elif export_format == "json":
            self.export_json()
        elif export_format == "csv":
            messagebox.showinfo("Info", "CSV export would be implemented here")
    
    def export_sql(self):
        """Export database as SQL"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                cursor = self.db_connection.cursor()
                
                with open(filename, 'w') as f:
                    if self.export_schema_var.get():
                        # Export schema
                        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
                        tables = cursor.fetchall()
                        
                        for table in tables:
                            f.write(f"-- Table: {table[0]}\n")
                            f.write(f"{table[1]};\n\n")
                    
                    if self.export_data_var.get():
                        # Export data
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = cursor.fetchall()
                        
                        for table in tables:
                            table_name = table[0]
                            cursor.execute(f"SELECT * FROM {table_name}")
                            rows = cursor.fetchall()
                            
                            if rows:
                                f.write(f"-- Data for {table_name}\n")
                                for row in rows:
                                    values = "', '".join(str(v) for v in row)
                                    f.write(f"INSERT INTO {table_name} VALUES ('{values}');\n")
                                f.write("\n")
                
                messagebox.showinfo("Success", f"Database exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export database: {e}")
    
    def export_json(self):
        """Export database as JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                cursor = self.db_connection.cursor()
                db_data = {}
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Convert rows to dict
                    table_data = []
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        table_data.append(row_dict)
                    
                    db_data[table_name] = table_data
                
                with open(filename, 'w') as f:
                    json.dump(db_data, f, indent=2, default=str)
                
                messagebox.showinfo("Success", f"Database exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export database: {e}")

def main():
    """Main function"""
    try:
        root = tk.Tk()
        app = DatabaseSchema(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting database schema manager: {e}")

if __name__ == "__main__":
    main()
