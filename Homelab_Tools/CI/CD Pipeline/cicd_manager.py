#!/usr/bin/env python3
"""
CI/CD Pipeline Manager - Development Workflow Automation
Complete CI/CD pipeline management system for homelab environments
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import json
import threading
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import shutil
import hashlib

class CICDManager:
    """Complete CI/CD pipeline management system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CI/CD Pipeline Manager - Development Workflow Automation")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'card_hover': '#3a3a3a',
            'primary': '#00ff88',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'danger': '#ff4444',
            'info': '#00d4ff',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#0078ff',
            'graph_bg': '#242424'
        }
        
        # CI/CD configuration
        self.config_file = Path("cicd_config.json")
        self.cicd_config = {
            'pipelines': {},
            'repositories': {},
            'build_queue': [],
            'deploy_queue': [],
            'settings': {
                'auto_build': False,
                'auto_deploy': False,
                'max_concurrent_builds': 2,
                'build_timeout': 300,
                'deploy_timeout': 600
            }
        }
        
        # Pipeline status
        self.running_pipelines = {}
        self.build_history = []
        self.deploy_history = []
        
        # Load configuration
        self.load_config()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Setup logging
        self.setup_logging()
        
        # Start monitoring
        self.start_monitoring()
        
        self.log_message("CI/CD Pipeline Manager initialized")
    
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        styles = {
            'Title.TLabel': {'background': self.colors['bg'], 'foreground': self.colors['primary'], 'font': ('Segoe UI', 24, 'bold')},
            'Card.TFrame': {'background': self.colors['card'], 'relief': 'flat', 'borderwidth': 1},
            'CICD.TButton': {'background': self.colors['card'], 'foreground': self.colors['text'], 'font': ('Segoe UI', 10), 'relief': 'flat', 'borderwidth': 1},
            'Status.TLabel': {'background': self.colors['card'], 'foreground': self.colors['success'], 'font': ('Segoe UI', 10, 'bold')}
        }
        
        for style_name, config in styles.items():
            style.configure(style_name, **config)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Header
        self.create_header()
        
        # Main container with tabs
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, style='Card.TFrame')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # CI/CD tabs
        self.create_pipelines_tab()
        self.create_builds_tab()
        self.create_deploys_tab()
        self.create_repositories_tab()
        self.create_settings_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create header"""
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side=tk.LEFT, anchor=tk.W)
        
        title_label = tk.Label(title_frame, text="CI/CD Pipeline Manager", 
                             font=('Segoe UI', 28, 'bold'), 
                             fg=self.colors['primary'], bg=self.colors['bg'])
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame, text="Development Workflow Automation", 
                                 font=('Segoe UI', 11), 
                                 fg=self.colors['text_secondary'], bg=self.colors['bg'])
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Pipeline status
        status_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        status_frame.pack(side=tk.RIGHT, anchor=tk.E, pady=20)
        
        self.pipeline_status_label = tk.Label(status_frame, text="● Ready", 
                                            font=('Segoe UI', 12, 'bold'), 
                                            fg=self.colors['success'], bg=self.colors['bg'])
        self.pipeline_status_label.pack(anchor=tk.E)
        
        self.active_pipelines_label = tk.Label(status_frame, text="Active: 0", 
                                             font=('Segoe UI', 10), 
                                             fg=self.colors['info'], bg=self.colors['bg'])
        self.active_pipelines_label.pack(anchor=tk.E, pady=(5, 0))
    
    def create_pipelines_tab(self):
        """Create pipelines management tab"""
        pipelines_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(pipelines_frame, text="Pipelines")
        
        # Toolbar
        toolbar = tk.Frame(pipelines_frame, bg=self.colors['card'])
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(toolbar, text="➕ Create Pipeline", command=self.create_pipeline,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Run Pipeline", command=self.run_pipeline,
                 bg=self.colors['info'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Pause Pipeline", command=self.pause_pipeline,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Delete Pipeline", command=self.delete_pipeline,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_pipelines,
                 bg=self.colors['primary'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        # Pipeline templates
        templates_frame = tk.LabelFrame(pipelines_frame, text="Pipeline Templates", 
                                      bg=self.colors['card'], fg=self.colors['text'],
                                      font=('Segoe UI', 12, 'bold'))
        templates_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Template buttons
        template_buttons = tk.Frame(templates_frame, bg=self.colors['card'])
        template_buttons.pack(fill=tk.X, padx=10, pady=10)
        
        templates = [
            ("Python App", "Python"),
            ("Web App", "Web"),
            ("Docker Build", "Docker"),
            ("Data Pipeline", "Data"),
            ("API Service", "API"),
            ("Mobile App", "Mobile")
        ]
        
        for name, icon in templates:
            tk.Button(template_buttons, text=f"{icon} {name}", 
                     command=lambda n=name: self.create_pipeline_from_template(n),
                     bg=self.colors['card_hover'], fg=self.colors['text'], font=('Segoe UI', 9),
                     relief='flat').pack(side=tk.LEFT, padx=5, pady=2)
        
        # Pipelines list
        list_frame = tk.Frame(pipelines_frame, bg=self.colors['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for pipelines
        columns = ('Name', 'Type', 'Status', 'Last Run', 'Duration', 'Success Rate')
        self.pipelines_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        for col in columns:
            self.pipelines_tree.heading(col, text=col)
            self.pipelines_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.pipelines_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.pipelines_tree.xview)
        self.pipelines_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.pipelines_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Load pipelines
        self.refresh_pipelines()
    
    def create_builds_tab(self):
        """Create builds management tab"""
        builds_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(builds_frame, text="Builds")
        
        # Build statistics
        stats_frame = tk.LabelFrame(builds_frame, text="Build Statistics", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Segoe UI', 12, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Stats display
        stats_display = tk.Frame(stats_frame, bg=self.colors['graph_bg'])
        stats_display.pack(fill=tk.X, padx=10, pady=10)
        
        # Current builds
        current_frame = tk.Frame(stats_display, bg=self.colors['graph_bg'])
        current_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(current_frame, text="Current Builds:", bg=self.colors['graph_bg'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.current_builds_label = tk.Label(current_frame, text="0", 
                                             bg=self.colors['graph_bg'], fg=self.colors['success'],
                                             font=('Segoe UI', 12, 'bold'))
        self.current_builds_label.pack(side=tk.LEFT, padx=10)
        
        # Queue size
        queue_frame = tk.Frame(stats_display, bg=self.colors['graph_bg'])
        queue_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(queue_frame, text="Queue Size:", bg=self.colors['graph_bg'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.queue_size_label = tk.Label(queue_frame, text="0", 
                                        bg=self.colors['graph_bg'], fg=self.colors['warning'],
                                        font=('Segoe UI', 12, 'bold'))
        self.queue_size_label.pack(side=tk.LEFT, padx=10)
        
        # Success rate
        success_frame = tk.Frame(stats_display, bg=self.colors['graph_bg'])
        success_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(success_frame, text="✅ Success Rate:", bg=self.colors['graph_bg'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.success_rate_label = tk.Label(success_frame, text="0%", 
                                         bg=self.colors['graph_bg'], fg=self.colors['info'],
                                         font=('Segoe UI', 12, 'bold'))
        self.success_rate_label.pack(side=tk.LEFT, padx=10)
        
        # Build history
        history_frame = tk.LabelFrame(builds_frame, text="Build History", 
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     font=('Segoe UI', 12, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # History list
        history_list = tk.Frame(history_frame, bg=self.colors['graph_bg'])
        history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for build history
        columns = ('Pipeline', 'Build ID', 'Status', 'Duration', 'Timestamp', 'Artifacts')
        self.builds_tree = ttk.Treeview(history_list, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.builds_tree.heading(col, text=col)
            self.builds_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(history_list, orient=tk.VERTICAL, command=self.builds_tree.yview)
        h_scrollbar = ttk.Scrollbar(history_list, orient=tk.HORIZONTAL, command=self.builds_tree.xview)
        self.builds_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.builds_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        history_list.grid_rowconfigure(0, weight=1)
        history_list.grid_columnconfigure(0, weight=1)
        
        # Load build history
        self.refresh_build_history()
    
    def create_deploys_tab(self):
        """Create deployments management tab"""
        deploys_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(deploys_frame, text="Deploys")
        
        # Deploy statistics
        stats_frame = tk.LabelFrame(deploys_frame, text="Deploy Statistics", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Segoe UI', 12, 'bold'))
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Stats display
        stats_display = tk.Frame(stats_frame, bg=self.colors['graph_bg'])
        stats_display.pack(fill=tk.X, padx=10, pady=10)
        
        # Active deployments
        active_frame = tk.Frame(stats_display, bg=self.colors['graph_bg'])
        active_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(active_frame, text="Active Deploys:", bg=self.colors['graph_bg'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.active_deploys_label = tk.Label(active_frame, text="0", 
                                            bg=self.colors['graph_bg'], fg=self.colors['success'],
                                            font=('Segoe UI', 12, 'bold'))
        self.active_deploys_label.pack(side=tk.LEFT, padx=10)
        
        # Deploy queue
        deploy_queue_frame = tk.Frame(stats_display, bg=self.colors['graph_bg'])
        deploy_queue_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(deploy_queue_frame, text="Deploy Queue:", bg=self.colors['graph_bg'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.deploy_queue_label = tk.Label(deploy_queue_frame, text="0", 
                                         bg=self.colors['graph_bg'], fg=self.colors['warning'],
                                         font=('Segoe UI', 12, 'bold'))
        self.deploy_queue_label.pack(side=tk.LEFT, padx=10)
        
        # Deploy success rate
        deploy_success_frame = tk.Frame(stats_display, bg=self.colors['graph_bg'])
        deploy_success_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(deploy_success_frame, text="✅ Deploy Success:", bg=self.colors['graph_bg'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self.deploy_success_label = tk.Label(deploy_success_frame, text="0%", 
                                           bg=self.colors['graph_bg'], fg=self.colors['info'],
                                           font=('Segoe UI', 12, 'bold'))
        self.deploy_success_label.pack(side=tk.LEFT, padx=10)
        
        # Deploy history
        history_frame = tk.LabelFrame(deploys_frame, text="Deploy History", 
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     font=('Segoe UI', 12, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # History list
        history_list = tk.Frame(history_frame, bg=self.colors['graph_bg'])
        history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for deploy history
        columns = ('Pipeline', 'Environment', 'Status', 'Duration', 'Timestamp', 'Version')
        self.deploys_tree = ttk.Treeview(history_list, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.deploys_tree.heading(col, text=col)
            self.deploys_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(history_list, orient=tk.VERTICAL, command=self.deploys_tree.yview)
        h_scrollbar = ttk.Scrollbar(history_list, orient=tk.HORIZONTAL, command=self.deploys_tree.xview)
        self.deploys_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.deploys_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        history_list.grid_rowconfigure(0, weight=1)
        history_list.grid_columnconfigure(0, weight=1)
        
        # Load deploy history
        self.refresh_deploy_history()
    
    def create_repositories_tab(self):
        """Create repositories management tab"""
        repos_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(repos_frame, text="Repositories")
        
        # Toolbar
        toolbar = tk.Frame(repos_frame, bg=self.colors['card'])
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(toolbar, text="Add Repository", command=self.add_repository,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Sync Repository", command=self.sync_repository,
                 bg=self.colors['info'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Remove Repository", command=self.remove_repository,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Repository Stats", command=self.show_repository_stats,
                 bg=self.colors['primary'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=2)
        
        # Repository list
        list_frame = tk.Frame(repos_frame, bg=self.colors['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for repositories
        columns = ('Name', 'URL', 'Branch', 'Last Commit', 'Status', 'Size')
        self.repos_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.repos_tree.heading(col, text=col)
            self.repos_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.repos_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.repos_tree.xview)
        self.repos_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.repos_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Load repositories
        self.refresh_repositories()
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = tk.Frame(self.notebook, bg=self.colors['card'])
        self.notebook.add(settings_frame, text="Settings")
        
        # General settings
        general_frame = tk.LabelFrame(settings_frame, text="General Settings", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Segoe UI', 12, 'bold'))
        general_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Auto build
        self.auto_build_var = tk.BooleanVar(value=self.cicd_config['settings']['auto_build'])
        tk.Checkbutton(general_frame, text="Auto-build on commit", variable=self.auto_build_var,
                      bg=self.colors['card'], fg=self.colors['text'], font=('Segoe UI', 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Auto deploy
        self.auto_deploy_var = tk.BooleanVar(value=self.cicd_config['settings']['auto_deploy'])
        tk.Checkbutton(general_frame, text="Auto-deploy successful builds", variable=self.auto_deploy_var,
                      bg=self.colors['card'], fg=self.colors['text'], font=('Segoe UI', 10)).pack(anchor=tk.W, padx=10, pady=5)
        
        # Build settings
        build_frame = tk.LabelFrame(settings_frame, text="Build Settings", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Segoe UI', 12, 'bold'))
        build_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Max concurrent builds
        concurrent_frame = tk.Frame(build_frame, bg=self.colors['card'])
        concurrent_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(concurrent_frame, text="Max Concurrent Builds:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        
        self.max_concurrent_var = tk.StringVar(value=str(self.cicd_config['settings']['max_concurrent_builds']))
        concurrent_spin = tk.Spinbox(concurrent_frame, from_=1, to=10, textvariable=self.max_concurrent_var,
                                    bg=self.colors['graph_bg'], fg=self.colors['text'], width=10)
        concurrent_spin.pack(side=tk.LEFT, padx=5)
        
        # Build timeout
        timeout_frame = tk.Frame(build_frame, bg=self.colors['card'])
        timeout_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(timeout_frame, text="Build Timeout (seconds):", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        
        self.build_timeout_var = tk.StringVar(value=str(self.cicd_config['settings']['build_timeout']))
        timeout_spin = tk.Spinbox(timeout_frame, from_=60, to=3600, textvariable=self.build_timeout_var,
                                 bg=self.colors['graph_bg'], fg=self.colors['text'], width=10)
        timeout_spin.pack(side=tk.LEFT, padx=5)
        
        # Deploy settings
        deploy_frame = tk.LabelFrame(settings_frame, text="Deploy Settings", 
                                    bg=self.colors['card'], fg=self.colors['text'],
                                    font=('Segoe UI', 12, 'bold'))
        deploy_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Deploy timeout
        deploy_timeout_frame = tk.Frame(deploy_frame, bg=self.colors['card'])
        deploy_timeout_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(deploy_timeout_frame, text="Deploy Timeout (seconds):", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10)
        
        self.deploy_timeout_var = tk.StringVar(value=str(self.cicd_config['settings']['deploy_timeout']))
        deploy_timeout_spin = tk.Spinbox(deploy_timeout_frame, from_=60, to=3600, textvariable=self.deploy_timeout_var,
                                        bg=self.colors['graph_bg'], fg=self.colors['text'], width=10)
        deploy_timeout_spin.pack(side=tk.LEFT, padx=5)
        
        # Save settings button
        save_btn_frame = tk.Frame(settings_frame, bg=self.colors['card'])
        save_btn_frame.pack(fill=tk.X, padx=10, pady=20)
        
        tk.Button(save_btn_frame, text="Save Settings", command=self.save_settings,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 12, 'bold'),
                 relief='flat', width=20).pack()
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['card'], height=30)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                   font=('Segoe UI', 10), 
                                   fg=self.colors['text_secondary'], bg=self.colors['card'])
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.uptime_label = tk.Label(status_frame, text="Uptime: 0s", 
                                     font=('Segoe UI', 10), 
                                     fg=self.colors['info'], bg=self.colors['card'])
        self.uptime_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def log_message(self, message, level="INFO"):
        """Log message to console and GUI"""
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        
        print(f"[CI/CD Manager] [{level}] {message}")
        self.status_label.config(text=message)
    
    def save_settings(self):
        """Save CI/CD settings"""
        try:
            # Update configuration from GUI variables
            self.cicd_config['settings']['auto_build'] = self.auto_build_var.get()
            self.cicd_config['settings']['auto_deploy'] = self.auto_deploy_var.get()
            self.cicd_config['settings']['parallel_builds'] = int(self.parallel_builds_var.get())
            self.cicd_config['settings']['deploy_timeout'] = int(self.deploy_timeout_var.get())
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(self.cicd_config, f, indent=2)
            
            self.log_message("CI/CD settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            self.log_message(f"Failed to save settings: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def load_config(self):
        """Load CI/CD configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.cicd_config.update(json.load(f))
                self.log_message("CI/CD configuration loaded")
            except Exception as e:
                self.log_message(f"Failed to load config: {e}", "ERROR")
    
    def save_config(self):
        """Save CI/CD configuration"""
        try:
            # Update settings from GUI
            self.cicd_config['settings']['auto_build'] = self.auto_build_var.get()
            self.cicd_config['settings']['auto_deploy'] = self.auto_deploy_var.get()
            self.cicd_config['settings']['max_concurrent_builds'] = int(self.max_concurrent_var.get())
            self.cicd_config['settings']['build_timeout'] = int(self.build_timeout_var.get())
            self.cicd_config['settings']['deploy_timeout'] = int(self.deploy_timeout_var.get())
            
            with open(self.config_file, 'w') as f:
                json.dump(self.cicd_config, f, indent=2)
            
            self.log_message("CI/CD configuration saved")
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            self.log_message(f"Failed to save config: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def create_pipeline(self):
        """Create new pipeline"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Pipeline")
        dialog.geometry("600x500")
        dialog.configure(bg=self.colors['card'])
        
        # Pipeline name
        tk.Label(dialog, text="Pipeline Name:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, width=60, bg=self.colors['graph_bg'], fg=self.colors['text'])
        name_entry.pack(pady=5)
        
        # Pipeline type
        tk.Label(dialog, text="Pipeline Type:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        type_var = tk.StringVar(value="build")
        type_combo = ttk.Combobox(dialog, textvariable=type_var,
                                 values=['build', 'deploy', 'test', 'release'], width=30)
        type_combo.pack(pady=5)
        
        # Repository
        tk.Label(dialog, text="Repository:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        repo_var = tk.StringVar()
        repo_frame = tk.Frame(dialog, bg=self.colors['card'])
        repo_frame.pack(pady=5)
        
        repo_entry = tk.Entry(repo_frame, textvariable=repo_var, width=55,
                             bg=self.colors['graph_bg'], fg=self.colors['text'])
        repo_entry.pack(side=tk.LEFT)
        
        def browse_repo():
            directory = filedialog.askdirectory()
            if directory:
                repo_var.set(directory)
        
        tk.Button(repo_frame, text="📁 Browse", command=browse_repo,
                 bg=self.colors['info'], fg='white', font=('Segoe UI', 9),
                 relief='flat').pack(side=tk.LEFT, padx=5)
        
        # Pipeline steps
        tk.Label(dialog, text="Pipeline Steps:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        steps_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=10,
                                              bg=self.colors['graph_bg'], fg=self.colors['text'],
                                              font=('Consolas', 9))
        steps_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Default pipeline steps
        default_steps = """# Build Pipeline Steps
1. Checkout code
2. Install dependencies
3. Run tests
4. Build application
5. Generate artifacts
6. Upload artifacts"""
        
        steps_text.insert(tk.END, default_steps)
        
        def save_pipeline():
            name = name_entry.get()
            pipeline_type = type_var.get()
            repository = repo_var.get()
            steps = steps_text.get(1.0, tk.END).strip()
            
            if not all([name, repository, steps]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            # Add to configuration
            pipeline_id = str(int(time.time()))
            self.cicd_config['pipelines'][pipeline_id] = {
                'name': name,
                'type': pipeline_type,
                'repository': repository,
                'steps': steps.split('\n'),
                'created_at': datetime.now().isoformat(),
                'status': 'inactive',
                'last_run': None,
                'success_count': 0,
                'total_runs': 0
            }
            
            self.save_config()
            self.refresh_pipelines()
            
            self.log_message(f"Created pipeline: {name}")
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save", command=save_pipeline,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10),
                 relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 10),
                 relief='flat', width=15).pack(side=tk.LEFT, padx=5)
    
    def create_pipeline_from_template(self, template_name):
        """Create pipeline from template"""
        templates = {
            "Python App": {
                "steps": [
                    "checkout",
                    "setup_python",
                    "install_dependencies",
                    "run_tests",
                    "build_package",
                    "upload_artifacts"
                ]
            },
            "Web App": {
                "steps": [
                    "checkout",
                    "install_dependencies",
                    "build_frontend",
                    "build_backend",
                    "run_tests",
                    "deploy_staging"
                ]
            },
            "Docker Build": {
                "steps": [
                    "checkout",
                    "build_docker_image",
                    "push_to_registry",
                    "update_kubernetes",
                    "health_check"
                ]
            },
            "Data Pipeline": {
                "steps": [
                    "checkout",
                    "validate_data",
                    "run_etl",
                    "generate_reports",
                    "upload_results"
                ]
            },
            "API Service": {
                "steps": [
                    "checkout",
                    "install_dependencies",
                    "run_unit_tests",
                    "run_integration_tests",
                    "build_api",
                    "deploy_production"
                ]
            },
            "Mobile App": {
                "steps": [
                    "checkout",
                    "install_dependencies",
                    "build_ios",
                    "build_android",
                    "run_tests",
                    "upload_to_store"
                ]
            }
        }
        
        template = templates.get(template_name, {})
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Create {template_name} Pipeline")
        dialog.geometry("500x300")
        dialog.configure(bg=self.colors['card'])
        
        # Pipeline name
        tk.Label(dialog, text="Pipeline Name:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, width=50, bg=self.colors['graph_bg'], fg=self.colors['text'])
        name_entry.pack(pady=5)
        name_entry.insert(0, f"{template_name} Pipeline")
        
        # Repository
        tk.Label(dialog, text="Repository:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        repo_var = tk.StringVar()
        repo_entry = tk.Entry(dialog, textvariable=repo_var, width=50,
                             bg=self.colors['graph_bg'], fg=self.colors['text'])
        repo_entry.pack(pady=5)
        
        def save_template_pipeline():
            name = name_entry.get()
            repository = repo_var.get()
            
            if not all([name, repository]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            # Add to configuration
            pipeline_id = str(int(time.time()))
            self.cicd_config['pipelines'][pipeline_id] = {
                'name': name,
                'type': 'build',
                'repository': repository,
                'steps': template.get('steps', []),
                'template': template_name,
                'created_at': datetime.now().isoformat(),
                'status': 'inactive',
                'last_run': None,
                'success_count': 0,
                'total_runs': 0
            }
            
            self.save_config()
            self.refresh_pipelines()
            
            self.log_message(f"Created {template_name} pipeline: {name}")
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Create", command=save_template_pipeline,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10),
                 relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 10),
                 relief='flat', width=15).pack(side=tk.LEFT, padx=5)
    
    def run_pipeline(self):
        """Run selected pipeline"""
        selection = self.pipelines_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a pipeline to run")
            return
        
        item = self.pipelines_tree.item(selection[0])
        pipeline_name = item['values'][0]
        
        # Find pipeline
        pipeline_id = None
        for pid, pipeline in self.cicd_config['pipelines'].items():
            if pipeline['name'] == pipeline_name:
                pipeline_id = pid
                break
        
        if pipeline_id:
            self.execute_pipeline(pipeline_id, self.cicd_config['pipelines'][pipeline_id])
    
    def execute_pipeline(self, pipeline_id, pipeline):
        """Execute pipeline"""
        try:
            # Update pipeline status
            pipeline['status'] = 'running'
            pipeline['last_run'] = datetime.now().isoformat()
            self.running_pipelines[pipeline_id] = {
                'start_time': time.time(),
                'pipeline': pipeline
            }
            
            # Update UI
            self.pipeline_status_label.config(text="● Running", fg=self.colors['warning'])
            self.active_pipelines_label.config(text=str(len(self.running_pipelines)))
            
            self.log_message(f"Running pipeline: {pipeline['name']}")
            
            # Execute pipeline in thread
            threading.Thread(target=self.run_pipeline_thread, args=(pipeline_id, pipeline), daemon=True).start()
            
        except Exception as e:
            self.log_message(f"Failed to run pipeline: {e}", "ERROR")
    
    def run_pipeline_thread(self, pipeline_id, pipeline):
        """Run pipeline in separate thread"""
        try:
            build_id = str(int(time.time()))
            start_time = time.time()
            
            # Simulate pipeline execution
            for i, step in enumerate(pipeline['steps']):
                step_name = step.strip()
                if not step_name or step_name.startswith('#'):
                    continue
                
                self.log_message(f"Step {i+1}: {step_name}")
                time.sleep(2)  # Simulate step execution
            
            # Update pipeline status
            duration = time.time() - start_time
            pipeline['status'] = 'completed'
            pipeline['success_count'] += 1
            pipeline['total_runs'] += 1
            
            # Add to build history
            self.build_history.append({
                'pipeline': pipeline['name'],
                'build_id': build_id,
                'status': 'success',
                'duration': f"{duration:.1f}s",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'artifacts': 'build.log, app.zip'
            })
            
            # Remove from running pipelines
            if pipeline_id in self.running_pipelines:
                del self.running_pipelines[pipeline_id]
            
            # Update UI
            self.refresh_pipelines()
            self.refresh_build_history()
            self.update_build_stats()
            
            self.log_message(f"Pipeline completed: {pipeline['name']} ({duration:.1f}s)")
            
        except Exception as e:
            # Update pipeline status
            pipeline['status'] = 'failed'
            pipeline['total_runs'] += 1
            
            # Add to build history
            self.build_history.append({
                'pipeline': pipeline['name'],
                'build_id': build_id,
                'status': 'failed',
                'duration': f"{duration:.1f}s",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'artifacts': 'error.log'
            })
            
            # Remove from running pipelines
            if pipeline_id in self.running_pipelines:
                del self.running_pipelines[pipeline_id]
            
            self.log_message(f"Pipeline failed: {pipeline['name']} - {e}", "ERROR")
        
        finally:
            # Update UI
            self.active_pipelines_label.config(text=str(len(self.running_pipelines)))
            if not self.running_pipelines:
                self.pipeline_status_label.config(text="● Ready", fg=self.colors['success'])
    
    def pause_pipeline(self):
        """Pause selected pipeline"""
        selection = self.pipelines_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a pipeline to pause")
            return
        
        item = self.pipelines_tree.item(selection[0])
        pipeline_name = item['values'][0]
        
        # Find pipeline
        pipeline_id = None
        for pid, pipeline in self.cicd_config['pipelines'].items():
            if pipeline['name'] == pipeline_name:
                pipeline_id = pid
                break
        
        if pipeline_id and pipeline_id in self.running_pipelines:
            # Remove from running pipelines
            del self.running_pipelines[pipeline_id]
            
            # Update pipeline status
            self.cicd_config['pipelines'][pipeline_id]['status'] = 'paused'
            
            self.refresh_pipelines()
            self.log_message(f"Paused pipeline: {pipeline_name}")
    
    def delete_pipeline(self):
        """Delete selected pipeline"""
        selection = self.pipelines_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a pipeline to delete")
            return
        
        item = self.pipelines_tree.item(selection[0])
        pipeline_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete pipeline '{pipeline_name}'?"):
            # Find and remove pipeline
            pipeline_id = None
            for pid, pipeline in self.cicd_config['pipelines'].items():
                if pipeline['name'] == pipeline_name:
                    pipeline_id = pid
                    break
            
            if pipeline_id:
                del self.cicd_config['pipelines'][pipeline_id]
                self.save_config()
                self.refresh_pipelines()
                self.log_message(f"Deleted pipeline: {pipeline_name}")
    
    def refresh_pipelines(self):
        """Refresh pipelines list"""
        self.pipelines_tree.delete(*self.pipelines_tree.get_children())
        
        for pipeline in self.cicd_config['pipelines'].values():
            success_rate = 0
            if pipeline['total_runs'] > 0:
                success_rate = (pipeline['success_count'] / pipeline['total_runs']) * 100
            
            self.pipelines_tree.insert('', 'end', values=(
                pipeline['name'],
                pipeline['type'],
                pipeline['status'],
                pipeline.get('last_run', 'Never'),
                f"{pipeline.get('duration', '0s')}",
                f"{success_rate:.1f}%"
            ))
    
    def refresh_build_history(self):
        """Refresh build history"""
        self.builds_tree.delete(*self.builds_tree.get_children())
        
        for build in self.build_history[-100:]:  # Show last 100 builds
            self.builds_tree.insert('', 'end', values=(
                build['pipeline'],
                build['build_id'],
                build['status'],
                build['duration'],
                build['timestamp'],
                build['artifacts']
            ))
    
    def refresh_deploy_history(self):
        """Refresh deploy history"""
        self.deploys_tree.delete(*self.deploys_tree.get_children())
        
        for deploy in self.deploy_history[-100:]:  # Show last 100 deploys
            self.deploys_tree.insert('', 'end', values=(
                deploy['pipeline'],
                deploy.get('environment', 'production'),
                deploy['status'],
                deploy['duration'],
                deploy['timestamp'],
                deploy.get('version', 'v1.0.0')
            ))
    
    def refresh_repositories(self):
        """Refresh repositories list"""
        self.repos_tree.delete(*self.repos_tree.get_children())
        
        for repo in self.cicd_config['repositories'].values():
            self.repos_tree.insert('', 'end', values=(
                repo['name'],
                repo['url'],
                repo.get('branch', 'main'),
                repo.get('last_commit', 'Unknown'),
                repo.get('status', 'Unknown'),
                repo.get('size', 'Unknown')
            ))
    
    def update_build_stats(self):
        """Update build statistics"""
        current_builds = len(self.running_pipelines)
        queue_size = len(self.cicd_config['build_queue'])
        
        # Calculate success rate
        total_builds = len(self.build_history)
        successful_builds = len([b for b in self.build_history if b['status'] == 'success'])
        success_rate = (successful_builds / total_builds * 100) if total_builds > 0 else 0
        
        # Update display
        self.current_builds_label.config(text=str(current_builds))
        self.queue_size_label.config(text=str(queue_size))
        self.success_rate_label.config(text=f"{success_rate:.1f}%")
    
    def add_repository(self):
        """Add new repository"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Repository")
        dialog.geometry("500x300")
        dialog.configure(bg=self.colors['card'])
        
        # Repository name
        tk.Label(dialog, text="Repository Name:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        name_entry = tk.Entry(dialog, width=50, bg=self.colors['graph_bg'], fg=self.colors['text'])
        name_entry.pack(pady=5)
        
        # Repository URL
        tk.Label(dialog, text="Repository URL:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        url_entry = tk.Entry(dialog, width=50, bg=self.colors['graph_bg'], fg=self.colors['text'])
        url_entry.pack(pady=5)
        
        # Branch
        tk.Label(dialog, text="Default Branch:", bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(pady=10)
        
        branch_entry = tk.Entry(dialog, width=50, bg=self.colors['graph_bg'], fg=self.colors['text'])
        branch_entry.pack(pady=5)
        branch_entry.insert(0, "main")
        
        def save_repository():
            name = name_entry.get()
            url = url_entry.get()
            branch = branch_entry.get()
            
            if not all([name, url]):
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            # Add to configuration
            repo_id = str(int(time.time()))
            self.cicd_config['repositories'][repo_id] = {
                'name': name,
                'url': url,
                'branch': branch,
                'added_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self.save_config()
            self.refresh_repositories()
            
            self.log_message(f"Added repository: {name}")
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.colors['card'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Save", command=save_repository,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10),
                 relief='flat', width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 10),
                 relief='flat', width=15).pack(side=tk.LEFT, padx=5)
    
    def sync_repository(self):
        """Sync selected repository"""
        selection = self.repos_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a repository to sync")
            return
        
        item = self.repos_tree.item(selection[0])
        repo_name = item['values'][0]
        
        self.log_message(f"Syncing repository: {repo_name}")
        
        # Simulate repository sync
        threading.Thread(target=self.simulate_repo_sync, args=(repo_name,), daemon=True).start()
    
    def simulate_repo_sync(self, repo_name):
        """Simulate repository synchronization"""
        time.sleep(3)  # Simulate sync time
        
        # Update repository status
        for repo in self.cicd_config['repositories'].values():
            if repo['name'] == repo_name:
                repo['last_commit'] = f"abc123 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                repo['status'] = 'synced'
                break
        
        self.refresh_repositories()
        self.log_message(f"Repository synced: {repo_name}")
    
    def remove_repository(self):
        """Remove selected repository"""
        selection = self.repos_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a repository to remove")
            return
        
        item = self.repos_tree.item(selection[0])
        repo_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove repository '{repo_name}'?"):
            # Find and remove repository
            repo_id = None
            for rid, repo in self.cicd_config['repositories'].items():
                if repo['name'] == repo_name:
                    repo_id = rid
                    break
            
            if repo_id:
                del self.cicd_config['repositories'][repo_id]
                self.save_config()
                self.refresh_repositories()
                self.log_message(f"Removed repository: {repo_name}")
    
    def show_repository_stats(self):
        """Show repository statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Repository Statistics")
        stats_window.geometry("600x400")
        stats_window.configure(bg=self.colors['card'])
        
        # Stats display
        stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD,
                                               bg=self.colors['graph_bg'], fg=self.colors['text'],
                                               font=('Consolas', 10))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generate stats
        total_repos = len(self.cicd_config['repositories'])
        active_repos = len([r for r in self.cicd_config['repositories'].values() if r.get('status') == 'active'])
        
        stats_content = f"""
Repository Statistics
====================
Total Repositories: {total_repos}
Active Repositories: {active_repos}

Repository Details:
"""
        
        for repo in self.cicd_config['repositories'].values():
            stats_content += f"""
- {repo['name']}
  URL: {repo['url']}
  Branch: {repo['branch']}
  Status: {repo.get('status', 'Unknown')}
  Added: {repo.get('added_at', 'Unknown')}
"""
        
        stats_text.insert(tk.END, stats_content)
        stats_text.config(state='disabled')
    
    def start_monitoring(self):
        """Start CI/CD monitoring"""
        def monitor_loop():
            while True:
                try:
                    # Update statistics
                    self.update_build_stats()
                    self.update_deploy_stats()
                    
                    # Check for auto-build triggers
                    if self.cicd_config['settings']['auto_build']:
                        self.check_auto_build_triggers()
                    
                    time.sleep(10)  # Update every 10 seconds
                    
                except Exception as e:
                    self.log_message(f"Monitoring error: {e}", "ERROR")
                    time.sleep(30)  # Wait before retrying
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def update_deploy_stats(self):
        """Update deploy statistics"""
        active_deploys = len([d for d in self.deploy_history if d.get('status') == 'running'])
        queue_size = len(self.cicd_config['deploy_queue'])
        
        # Calculate success rate
        total_deploys = len(self.deploy_history)
        successful_deploys = len([d for d in self.deploy_history if d['status'] == 'success'])
        success_rate = (successful_deploys / total_deploys * 100) if total_deploys > 0 else 0
        
        # Update display
        self.active_deploys_label.config(text=str(active_deploys))
        self.deploy_queue_label.config(text=str(queue_size))
        self.deploy_success_label.config(text=f"{success_rate:.1f}%")
    
    def check_auto_build_triggers(self):
        """Check for automatic build triggers"""
        # In a real implementation, this would check for Git commits, webhooks, etc.
        pass

def main():
    """Main entry point"""
    root = tk.Tk()
    app = CICDManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
