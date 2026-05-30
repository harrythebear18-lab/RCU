#!/usr/bin/env python3
"""
Help System
Interactive tutorials, documentation, and help system.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import webbrowser
from typing import Dict, Any, List, Optional
import threading
import time
from datetime import datetime

class HelpSystem:
    """Interactive Help System"""
    
    def __init__(self):
        self.help_data_file = os.path.join(os.path.dirname(__file__), 'help_data.json')
        self.tutorials_file = os.path.join(os.path.dirname(__file__), 'tutorials.json')
        self.faq_file = os.path.join(os.path.dirname(__file__), 'faq.json')
        
        # Initialize help data
        self.help_data = self.load_help_data()
        self.tutorials = self.load_tutorials()
        self.faq = self.load_faq()
        
        # Tutorial state
        self.current_tutorial = None
        self.tutorial_step = 0
        self.tutorial_active = False
        
        # Create default help data if needed
        self.create_default_help_data()
    
    def load_help_data(self) -> Dict[str, Any]:
        """Load help documentation"""
        default_data = {
            'getting_started': {
                'title': 'Getting Started',
                'content': '''
# Getting Started with Windows 11 Resource Optimization System

## Overview
The Windows 11 Resource Optimization System is a comprehensive tool for monitoring and optimizing your system's performance.

## Main Features
- **System Dashboard**: Real-time monitoring of CPU, GPU, RAM, and disk usage
- **Resource Optimizer**: Advanced cleaning and optimization tools
- **Overclocking Dashboard**: Safe overclocking and underclocking controls
- **Performance Reports**: Detailed performance analysis and reports
- **Backup Manager**: System backup and restore functionality
- **API Server**: REST API for external integrations

## Quick Start
1. Launch the application using the launcher
2. Choose your preferred dashboard (System, Resource Optimizer, or Overclocking)
3. Monitor your system performance in real-time
4. Use optimization tools when needed
5. Configure alerts and notifications for automatic monitoring

## System Requirements
- Windows 10/11
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- Administrator privileges (recommended)
                '''
            },
            'system_dashboard': {
                'title': 'System Dashboard',
                'content': '''
# System Dashboard Guide

## Overview
The System Dashboard provides real-time monitoring of your system's performance metrics.

## Components
- **CPU Monitor**: Shows CPU usage, frequency, and temperature
- **Memory Monitor**: Displays RAM usage and available memory
- **GPU Monitor**: Tracks GPU usage, memory, and temperature
- **Disk Monitor**: Shows disk usage and I/O operations
- **Network Monitor**: Displays network activity and bandwidth

## Using the Dashboard
1. **Real-time Monitoring**: Metrics update automatically
2. **Historical Data**: View performance trends over time
3. **Alerts**: Configure custom alert thresholds
4. **Export Data**: Export performance data to CSV/JSON

## Tips
- Monitor CPU temperature to prevent overheating
- Keep an eye on memory usage for optimal performance
- Use historical data to identify performance patterns
                '''
            },
            'resource_optimizer': {
                'title': 'Resource Optimizer',
                'content': '''
# Resource Optimizer Guide

## Overview
The Resource Optimizer provides tools to clean and optimize your system's resources.

## Cleaning Options
- **Soft Clean**: Safe cleanup of temporary files and cache
- **Aggressive Clean**: Deep cleanup including system files
- **Deep Clean**: Maximum cleanup with advanced options

## Features
- **Memory Jolt**: Quick memory optimization
- **CPU Cleanup**: Optimize CPU processes
- **GPU Cleanup**: Clean GPU memory
- **RAM Cleanup**: Free up RAM memory

## Best Practices
- Start with Soft Clean for regular maintenance
- Use Aggressive Clean for monthly maintenance
- Deep Clean only when necessary
- Always create a backup before deep cleaning
                '''
            },
            'overclocking': {
                'title': 'Overclocking Dashboard',
                'content': '''
# Overclocking Dashboard Guide

## Overview
The Overclocking Dashboard allows safe overclocking and underclocking of system components.

## Components
- **CPU Overclock**: Adjust CPU frequency
- **GPU Overclock**: Modify GPU settings
- **RAM Overclock**: Optimize memory frequency

## Safety Features
- **Temperature Monitoring**: Real-time temperature tracking
- **Profile Management**: Save and load overclocking profiles
- **Safety Limits**: Automatic protection against dangerous settings
- **Rollback**: Quick rollback to safe settings

## Profiles
- **Stock**: Default factory settings
- **Gaming**: Optimized for gaming performance
- **Performance**: Balanced performance profile
- **Extreme**: Maximum safe overclock
- **Insane**: Beyond safe limits (advanced users only)
- **Suicide**: Maximum overclock (expert users only)

## Warnings
- Extreme overclocking can damage hardware
- Always monitor temperatures
- Ensure adequate cooling
- Use at your own risk
                '''
            },
            'backup_manager': {
                'title': 'Backup Manager',
                'content': '''
# Backup Manager Guide

## Overview
The Backup Manager provides comprehensive backup and restore functionality.

## Features
- **System Backup**: Complete system backup
- **Selective Backup**: Backup specific components
- **Compression**: Compressed backups to save space
- **Scheduling**: Automatic backup scheduling
- **Restore**: Quick restore from backups

## Backup Types
- **Full Backup**: Complete system backup
- **Incremental Backup**: Backup changes only
- **Differential Backup**: Backup since last full backup

## Best Practices
- Schedule regular backups
- Test restore functionality
- Keep multiple backup versions
- Store backups on external media
- Verify backup integrity
                '''
            },
            'api_server': {
                'title': 'API Server',
                'content': '''
# API Server Guide

## Overview
The API Server provides REST API endpoints for external integrations.

## Endpoints
- **GET /api/v1/system/status**: Get system status
- **POST /api/v1/system/optimize**: Trigger optimization
- **GET /api/v1/data/export**: Export system data
- **GET/POST /api/v1/alerts/configure**: Configure alerts
- **GET/POST/PUT/DELETE /api/v1/profiles/manage**: Manage profiles

## Authentication
- API key-based authentication
- Configurable rate limiting
- CORS support for web applications

## Usage Examples
```python
import requests

# Get system status
response = requests.get('http://localhost:5000/api/v1/system/status')
status = response.json()

# Trigger optimization
response = requests.post('http://localhost:5000/api/v1/system/optimize',
                        json={'type': 'gaming', 'intensity': 'medium'})
```

## Integration
- Compatible with monitoring tools
- Supports automation scripts
- Web dashboard integration
- Third-party application support
                '''
            },
            'troubleshooting': {
                'title': 'Troubleshooting',
                'content': '''
# Troubleshooting Guide

## Common Issues

### High CPU Usage
- Check for background processes
- Close unnecessary applications
- Run CPU cleanup
- Consider upgrading hardware

### High Memory Usage
- Use RAM cleanup
- Close memory-intensive applications
- Check for memory leaks
- Add more RAM if needed

### System Instability
- Check system temperatures
- Verify overclocking settings
- Update drivers
- Run system diagnostics

### Backup Failures
- Check disk space
- Verify permissions
- Test backup integrity
- Try different backup location

### API Connection Issues
- Check if API server is running
- Verify port configuration
- Check firewall settings
- Test with curl or browser

## Performance Tips
- Regular system maintenance
- Keep drivers updated
- Monitor system health
- Use appropriate optimization levels

## Getting Help
- Check this help system
- Review FAQ section
- Contact support
- Join community forums
                '''
            }
        }
        
        try:
            if os.path.exists(self.help_data_file):
                with open(self.help_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_help_data(default_data)
                return default_data
        except Exception:
            return default_data
    
    def save_help_data(self, data: Dict[str, Any]) -> bool:
        """Save help documentation"""
        try:
            with open(self.help_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_tutorials(self) -> List[Dict[str, Any]]:
        """Load interactive tutorials"""
        default_tutorials = [
            {
                'id': 'getting_started',
                'title': 'Getting Started',
                'description': 'Learn the basics of the system',
                'steps': [
                    {
                        'title': 'Launch the Application',
                        'content': 'Start by launching the application using the launcher.exe file.',
                        'action': 'launch',
                        'highlight': ['launcher_button'],
                        'duration': 30
                    },
                    {
                        'title': 'Choose Dashboard',
                        'content': 'Select your preferred dashboard from the launcher options.',
                        'action': 'select_dashboard',
                        'highlight': ['dashboard_buttons'],
                        'duration': 20
                    },
                    {
                        'title': 'Monitor System',
                        'content': 'Observe the real-time system metrics on the dashboard.',
                        'action': 'monitor',
                        'highlight': ['metrics_display'],
                        'duration': 30
                    },
                    {
                        'title': 'Try Optimization',
                        'content': 'Click on an optimization button to clean system resources.',
                        'action': 'optimize',
                        'highlight': ['optimize_buttons'],
                        'duration': 25
                    }
                ]
            },
            {
                'id': 'system_dashboard',
                'title': 'System Dashboard Tutorial',
                'description': 'Learn to use the system dashboard effectively',
                'steps': [
                    {
                        'title': 'Understanding Metrics',
                        'content': 'The dashboard shows CPU, GPU, RAM, and disk usage in real-time.',
                        'action': 'view_metrics',
                        'highlight': ['cpu_gauge', 'memory_gauge', 'gpu_gauge', 'disk_gauge'],
                        'duration': 30
                    },
                    {
                        'title': 'Reading Graphs',
                        'content': 'Graphs show historical performance trends.',
                        'action': 'view_graphs',
                        'highlight': ['performance_graphs'],
                        'duration': 25
                    },
                    {
                        'title': 'Setting Alerts',
                        'content': 'Configure alert thresholds for automatic monitoring.',
                        'action': 'configure_alerts',
                        'highlight': ['alert_settings'],
                        'duration': 35
                    }
                ]
            },
            {
                'id': 'resource_optimizer',
                'title': 'Resource Optimizer Tutorial',
                'description': 'Learn to optimize system resources',
                'steps': [
                    {
                        'title': 'Soft Clean',
                        'content': 'Start with a soft clean for safe optimization.',
                        'action': 'soft_clean',
                        'highlight': ['soft_clean_button'],
                        'duration': 20
                    },
                    {
                        'title': 'Memory Jolt',
                        'content': 'Use memory jolt for quick RAM optimization.',
                        'action': 'memory_jolt',
                        'highlight': ['memory_jolt_button'],
                        'duration': 15
                    },
                    {
                        'title': 'Deep Clean',
                        'content': 'Perform deep clean for maximum optimization.',
                        'action': 'deep_clean',
                        'highlight': ['deep_clean_button'],
                        'duration': 30
                    }
                ]
            },
            {
                'id': 'overclocking',
                'title': 'Overclocking Tutorial',
                'description': 'Learn safe overclocking techniques',
                'steps': [
                    {
                        'title': 'Safety First',
                        'content': 'Always monitor temperatures when overclocking.',
                        'action': 'check_temperature',
                        'highlight': ['temperature_display'],
                        'duration': 25
                    },
                    {
                        'title': 'Start with Stock',
                        'content': 'Begin with stock settings to establish baseline.',
                        'action': 'load_stock',
                        'highlight': ['stock_profile'],
                        'duration': 15
                    },
                    {
                        'title': 'Try Gaming Profile',
                        'content': 'Use the gaming profile for safe performance boost.',
                        'action': 'load_gaming',
                        'highlight': ['gaming_profile'],
                        'duration': 20
                    },
                    {
                        'title': 'Monitor Stability',
                        'content': 'Watch for system stability after changes.',
                        'action': 'monitor_stability',
                        'highlight': ['stability_indicator'],
                        'duration': 30
                    }
                ]
            }
        ]
        
        try:
            if os.path.exists(self.tutorials_file):
                with open(self.tutorials_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_tutorials(default_tutorials)
                return default_tutorials
        except Exception:
            return default_tutorials
    
    def save_tutorials(self, tutorials: List[Dict[str, Any]]) -> bool:
        """Save tutorials"""
        try:
            with open(self.tutorials_file, 'w', encoding='utf-8') as f:
                json.dump(tutorials, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_faq(self) -> List[Dict[str, Any]]:
        """Load FAQ"""
        default_faq = [
            {
                'question': 'How do I start the application?',
                'answer': 'Run the launcher.exe file and select your preferred dashboard from the options.',
                'category': 'Getting Started'
            },
            {
                'question': 'What is the difference between Soft, Aggressive, and Deep Clean?',
                'answer': 'Soft Clean is safe for regular use, Aggressive Clean provides deeper cleaning, and Deep Clean offers maximum cleanup with advanced options.',
                'category': 'Resource Optimizer'
            },
            {
                'question': 'Is overclocking safe?',
                'answer': 'Overclocking can be safe when done properly. Always monitor temperatures, start with conservative settings, and use safety features.',
                'category': 'Overclocking'
            },
            {
                'question': 'How often should I clean my system?',
                'answer': 'Soft Clean can be done weekly, Aggressive Clean monthly, and Deep Clean only when necessary.',
                'category': 'Maintenance'
            },
            {
                'question': 'What should I do if my system becomes unstable?',
                'answer': 'Reset to stock settings, check temperatures, update drivers, and run system diagnostics.',
                'category': 'Troubleshooting'
            },
            {
                'question': 'How do I backup my system?',
                'answer': 'Use the Backup Manager to create full or selective backups. Schedule regular backups for data protection.',
                'category': 'Backup'
            },
            {
                'question': 'Can I use the API with other applications?',
                'answer': 'Yes, the REST API supports external integrations. Check the API documentation for endpoint details.',
                'category': 'API'
            },
            {
                'question': 'Why is my CPU usage high?',
                'answer': 'High CPU usage can be caused by background processes, malware, or insufficient cooling. Use CPU cleanup and monitor processes.',
                'category': 'Performance'
            },
            {
                'question': 'How do I configure alerts?',
                'answer': 'Go to Settings > Alert Configuration to set custom thresholds for CPU, memory, GPU, and temperature.',
                'category': 'Configuration'
            },
            {
                'question': 'What are the system requirements?',
                'answer': 'Windows 10/11, 4GB RAM minimum (8GB recommended), 1GB free disk space, and administrator privileges.',
                'category': 'System Requirements'
            }
        ]
        
        try:
            if os.path.exists(self.faq_file):
                with open(self.faq_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.save_faq(default_faq)
                return default_faq
        except Exception:
            return default_faq
    
    def save_faq(self, faq: List[Dict[str, Any]]) -> bool:
        """Save FAQ"""
        try:
            with open(self.faq_file, 'w', encoding='utf-8') as f:
                json.dump(faq, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def create_default_help_data(self):
        """Create default help data files"""
        self.save_help_data(self.help_data)
        self.save_tutorials(self.tutorials)
        self.save_faq(self.faq)
    
    def get_help_content(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get help content for a topic"""
        return self.help_data.get(topic)
    
    def get_tutorial_list(self) -> List[Dict[str, Any]]:
        """Get list of available tutorials"""
        return self.tutorials
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Dict[str, Any]]:
        """Get tutorial by ID"""
        for tutorial in self.tutorials:
            if tutorial['id'] == tutorial_id:
                return tutorial
        return None
    
    def get_faq_list(self) -> List[Dict[str, Any]]:
        """Get FAQ list"""
        return self.faq
    
    def search_faq(self, query: str) -> List[Dict[str, Any]]:
        """Search FAQ"""
        query = query.lower()
        results = []
        
        for item in self.faq:
            if (query in item['question'].lower() or 
                query in item['answer'].lower() or
                query in item['category'].lower()):
                results.append(item)
        
        return results
    
    def start_tutorial(self, tutorial_id: str, callback: Callable = None) -> bool:
        """Start interactive tutorial"""
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial:
            return False
        
        self.current_tutorial = tutorial
        self.tutorial_step = 0
        self.tutorial_active = True
        self.callback = callback
        
        # Start tutorial in separate thread
        tutorial_thread = threading.Thread(target=self.run_tutorial, daemon=True)
        tutorial_thread.start()
        
        return True
    
    def run_tutorial(self):
        """Run tutorial steps"""
        if not self.current_tutorial or not self.tutorial_active:
            return
        
        steps = self.current_tutorial['steps']
        
        while self.tutorial_step < len(steps) and self.tutorial_active:
            step = steps[self.tutorial_step]
            
            # Show step content
            if self.callback:
                self.callback('show_step', {
                    'title': step['title'],
                    'content': step['content'],
                    'step_number': self.tutorial_step + 1,
                    'total_steps': len(steps),
                    'highlight': step.get('highlight', []),
                    'duration': step.get('duration', 20)
                })
            
            # Wait for step duration or user action
            time.sleep(step.get('duration', 20))
            
            # Move to next step
            self.tutorial_step += 1
        
        # Tutorial completed
        if self.callback:
            self.callback('tutorial_completed', {
                'tutorial_id': self.current_tutorial['id'],
                'title': self.current_tutorial['title']
            })
        
        self.tutorial_active = False
    
    def stop_tutorial(self):
        """Stop current tutorial"""
        self.tutorial_active = False
    
    def next_tutorial_step(self):
        """Move to next tutorial step"""
        if self.current_tutorial and self.tutorial_step < len(self.current_tutorial['steps']) - 1:
            self.tutorial_step += 1
    
    def previous_tutorial_step(self):
        """Move to previous tutorial step"""
        if self.current_tutorial and self.tutorial_step > 0:
            self.tutorial_step -= 1
    
    def create_help_dialog(self, parent, topic: str = None):
        """Create help dialog"""
        help_dialog = tk.Toplevel(parent)
        help_dialog.title("Help System")
        help_dialog.geometry("800x600")
        help_dialog.transient(parent)
        
        # Create help interface
        self.create_help_interface(help_dialog, topic)
        
        return help_dialog
    
    def create_help_interface(self, parent, topic: str = None):
        """Create help interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Documentation tab
        doc_frame = ttk.Frame(notebook)
        notebook.add(doc_frame, text="Documentation")
        self.create_documentation_tab(doc_frame, topic)
        
        # Tutorials tab
        tutorial_frame = ttk.Frame(notebook)
        notebook.add(tutorial_frame, text="Tutorials")
        self.create_tutorials_tab(tutorial_frame)
        
        # FAQ tab
        faq_frame = ttk.Frame(notebook)
        notebook.add(faq_frame, text="FAQ")
        self.create_faq_tab(faq_frame)
        
        # Search tab
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="Search")
        self.create_search_tab(search_frame)
    
    def create_documentation_tab(self, parent, topic: str = None):
        """Create documentation tab"""
        # Topic list
        topic_frame = tk.Frame(parent)
        topic_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        tk.Label(topic_frame, text="Topics:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        topic_listbox = tk.Listbox(topic_frame, width=25)
        topic_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add topics
        for topic_id, topic_data in self.help_data.items():
            topic_listbox.insert(tk.END, topic_data['title'])
        
        # Content display
        content_frame = tk.Frame(parent)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(content_frame, text="Content:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=60, height=30)
        content_text.pack(fill=tk.BOTH, expand=True)
        
        # Load initial topic
        if topic and topic in self.help_data:
            content_text.insert(tk.END, self.help_data[topic]['content'])
        else:
            # Load first topic
            first_topic = list(self.help_data.keys())[0]
            content_text.insert(tk.END, self.help_data[first_topic]['content'])
        
        # Topic selection handler
        def on_topic_select(event):
            selection = topic_listbox.curselection()
            if selection:
                topic_index = selection[0]
                topic_id = list(self.help_data.keys())[topic_index]
                content_text.delete(1.0, tk.END)
                content_text.insert(tk.END, self.help_data[topic_id]['content'])
        
        topic_listbox.bind('<<ListboxSelect>>', on_topic_select)
    
    def create_tutorials_tab(self, parent):
        """Create tutorials tab"""
        # Tutorial list
        tutorial_frame = tk.Frame(parent)
        tutorial_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        tk.Label(tutorial_frame, text="Tutorials:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        tutorial_listbox = tk.Listbox(tutorial_frame, width=25)
        tutorial_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add tutorials
        for tutorial in self.tutorials:
            tutorial_listbox.insert(tk.END, tutorial['title'])
        
        # Tutorial info
        info_frame = tk.Frame(parent)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(info_frame, text="Tutorial Info:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, width=60, height=20)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        # Start button
        start_btn = tk.Button(info_frame, text="Start Tutorial", 
                             command=lambda: self.start_selected_tutorial(tutorial_listbox, info_text))
        start_btn.pack(pady=10)
        
        # Tutorial selection handler
        def on_tutorial_select(event):
            selection = tutorial_listbox.curselection()
            if selection:
                tutorial_index = selection[0]
                tutorial = self.tutorials[tutorial_index]
                
                info_text.delete(1.0, tk.END)
                info_text.insert(tk.END, f"Title: {tutorial['title']}\n\n")
                info_text.insert(tk.END, f"Description: {tutorial['description']}\n\n")
                info_text.insert(tk.END, f"Steps: {len(tutorial['steps'])}\n\n")
                
                for i, step in enumerate(tutorial['steps'], 1):
                    info_text.insert(tk.END, f"{i}. {step['title']}\n")
                    info_text.insert(tk.END, f"   {step['content']}\n\n")
        
        tutorial_listbox.bind('<<ListboxSelect>>', on_tutorial_select)
    
    def create_faq_tab(self, parent):
        """Create FAQ tab"""
        # FAQ list
        faq_frame = tk.Frame(parent)
        faq_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        tk.Label(faq_frame, text="FAQ:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        faq_listbox = tk.Listbox(faq_frame, width=25)
        faq_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add FAQ items
        for item in self.faq:
            faq_listbox.insert(tk.END, item['question'])
        
        # Answer display
        answer_frame = tk.Frame(parent)
        answer_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(answer_frame, text="Answer:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        answer_text = scrolledtext.ScrolledText(answer_frame, wrap=tk.WORD, width=60, height=25)
        answer_text.pack(fill=tk.BOTH, expand=True)
        
        # FAQ selection handler
        def on_faq_select(event):
            selection = faq_listbox.curselection()
            if selection:
                faq_index = selection[0]
                faq_item = self.faq[faq_index]
                
                answer_text.delete(1.0, tk.END)
                answer_text.insert(tk.END, f"Q: {faq_item['question']}\n\n")
                answer_text.insert(tk.END, f"A: {faq_item['answer']}\n\n")
                answer_text.insert(tk.END, f"Category: {faq_item['category']}")
        
        faq_listbox.bind('<<ListboxSelect>>', on_faq_select)
    
    def create_search_tab(self, parent):
        """Create search tab"""
        # Search controls
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_frame, text="Search:", font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        
        search_entry = tk.Entry(search_frame, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(search_frame, text="Search", 
                             command=lambda: self.perform_search(search_entry, parent))
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Results display
        results_frame = tk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(results_frame, text="Results:", font=('Segoe UI', 12, 'bold')).pack(pady=5)
        
        results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=70, height=25)
        results_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind Enter key to search
        search_entry.bind('<Return>', lambda e: self.perform_search(search_entry, parent))
    
    def perform_search(self, search_entry, parent):
        """Perform search"""
        query = search_entry.get().strip()
        if not query:
            return
        
        # Search FAQ
        results = self.search_faq(query)
        
        # Display results
        results_text = None
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, scrolledtext.ScrolledText):
                        results_text = child
                        break
        
        if results_text:
            results_text.delete(1.0, tk.END)
            
            if results:
                results_text.insert(tk.END, f"Found {len(results)} results for '{query}':\n\n")
                
                for item in results:
                    results_text.insert(tk.END, f"Q: {item['question']}\n")
                    results_text.insert(tk.END, f"A: {item['answer']}\n")
                    results_text.insert(tk.END, f"Category: {item['category']}\n")
                    results_text.insert(tk.END, "-" * 50 + "\n\n")
            else:
                results_text.insert(tk.END, f"No results found for '{query}'")
    
    def start_selected_tutorial(self, listbox, info_text):
        """Start selected tutorial"""
        selection = listbox.curselection()
        if selection:
            tutorial_index = selection[0]
            tutorial = self.tutorials[tutorial_index]
            
            if messagebox.askyesno("Start Tutorial", f"Start tutorial '{tutorial['title']}'?"):
                self.start_tutorial(tutorial['id'])
                messagebox.showinfo("Tutorial Started", f"Tutorial '{tutorial['title']}' has started.\nFollow the on-screen instructions.")

# Global help system instance
help_system = HelpSystem()

# Convenience functions
def show_help(parent, topic: str = None):
    """Show help dialog"""
    return help_system.create_help_dialog(parent, topic)

def start_tutorial(tutorial_id: str, callback: Callable = None):
    """Start tutorial"""
    return help_system.start_tutorial(tutorial_id, callback)

def get_help_content(topic: str) -> Optional[Dict[str, Any]]:
    """Get help content"""
    return help_system.get_help_content(topic)

if __name__ == '__main__':
    # Test help system
    print("Testing Help System")
    print(f"Help topics: {list(help_system.help_data.keys())}")
    print(f"Tutorials: {len(help_system.tutorials)}")
    print(f"FAQ items: {len(help_system.faq)}")
    
    # Test search
    results = help_system.search_faq("cpu")
    print(f"Search results for 'cpu': {len(results)}")
    
    # Test getting help content
    content = help_system.get_help_content('getting_started')
    if content:
        print(f"Getting started help: {content['title']}")
