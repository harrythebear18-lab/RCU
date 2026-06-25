#!/usr/bin/env python3
"""
Unified Homelab Launcher
Easy connection to all dashboards/tools or solo mode operation.
"""

import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
import psutil
import socket
import logging
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class LauncherMode(Enum):
    """Launcher operation modes"""
    DASHBOARD = "dashboard"
    SOLO = "solo"
    INTEGRATED = "integrated"
    AUTH = "auth"
    LEGACY = "legacy"

class ToolStatus(Enum):
    """Tool status enumeration"""
    AVAILABLE = "available"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class ToolInfo:
    """Tool information structure"""
    id: str
    name: str
    description: str
    script_path: str
    mode: LauncherMode
    status: ToolStatus
    process_id: Optional[int] = None
    port: Optional[int] = None
    url: Optional[str] = None
    dependencies: List[str] = None
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.properties is None:
            self.properties = {}

class UnifiedLauncher:
    """Unified launcher for all homelab tools and dashboards"""
    
    def __init__(self):
        self.db_path = current_dir / "unified_launcher.db"
        self.settings_file = current_dir / "launcher_settings.json"
        self.log_file = current_dir / "launcher.log"
        
        # Setup logging
        self.setup_logging()
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.init_database()
        
        # Tool registry
        self.tools = {}
        self.running_processes = {}
        
        # Current mode
        self.current_mode = LauncherMode.DASHBOARD
        
        # Initialize tool registry
        self.initialize_tool_registry()
        
        # Load saved tool states
        self.load_tool_states()
        
        self.logger.info("Unified Launcher initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        self.logger = logging.getLogger('UnifiedLauncher')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def load_settings(self) -> Dict[str, Any]:
        """Load launcher settings"""
        default_settings = {
            'default_mode': 'dashboard',
            'auto_start_tools': [],
            'auto_discover': True,
            'check_dependencies': True,
            'health_check_interval': 30,
            'max_concurrent_tools': 5,
            'tool_timeout': 60,
            'preferred_ports': {
                'streamlined_dashboard': 8080,
                'pc_auth_gui': 8081,
                'streamlined_homelab': 8082,
                'pc_auth_system': 8083
            },
            'solo_mode_tools': ['streamlined_homelab', 'pc_auth_system'],
            'dashboard_mode_tools': ['streamlined_dashboard', 'pc_auth_gui'],
            'legacy_tools_path': 'C:/Users/htsou/Desktop/Homelab Tools'
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                default_settings.update(loaded_settings)
            else:
                self.save_settings(default_settings)
            return default_settings
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            return default_settings
    
    def save_settings(self, settings: Dict[str, Any] = None) -> bool:
        """Save launcher settings"""
        try:
            if settings:
                self.settings.update(settings)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def init_database(self):
        """Initialize launcher database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Tools table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tools (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                script_path TEXT NOT NULL,
                mode TEXT NOT NULL,
                status TEXT DEFAULT 'unknown',
                process_id INTEGER,
                port INTEGER,
                url TEXT,
                dependencies TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_run TIMESTAMP,
                run_count INTEGER DEFAULT 0
            )
        ''')
        
        # Launcher events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS launcher_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tool_id TEXT,
                event_type TEXT NOT NULL,
                description TEXT,
                details TEXT,
                success BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def initialize_tool_registry(self):
        """Initialize the tool registry with all available tools"""
        try:
            # Core streamlined tools
            self.register_tool(ToolInfo(
                id='streamlined_dashboard',
                name='Streamlined Dashboard',
                description='Main dashboard for streamlined homelab system',
                script_path=str(current_dir / 'streamlined_dashboard.py'),
                mode=LauncherMode.DASHBOARD,
                status=ToolStatus.AVAILABLE,
                port=self.settings.get('preferred_ports', {}).get('streamlined_dashboard', 8080),
                url=f'http://localhost:{self.settings.get("preferred_ports", {}).get("streamlined_dashboard", 8080)}',
                properties={'gui': True, 'web_interface': True}
            ))
            
            self.register_tool(ToolInfo(
                id='streamlined_homelab',
                name='Streamlined Homelab System',
                description='Core streamlined homelab system',
                script_path=str(current_dir / 'streamlined_homelab_system.py'),
                mode=LauncherMode.SOLO,
                status=ToolStatus.AVAILABLE,
                properties={'core_system': True, 'background': True}
            ))
            
            self.register_tool(ToolInfo(
                id='pc_auth_gui',
                name='PC Authentication GUI',
                description='GUI for PC-to-PC authentication management',
                script_path=str(current_dir / 'pc_auth_gui.py'),
                mode=LauncherMode.AUTH,
                status=ToolStatus.AVAILABLE,
                port=self.settings.get('preferred_ports', {}).get('pc_auth_gui', 8081),
                properties={'gui': True, 'authentication': True}
            ))
            
            self.register_tool(ToolInfo(
                id='pc_auth_system',
                name='PC Authentication System',
                description='PC-to-PC authentication system',
                script_path=str(current_dir / 'pc_auth_system.py'),
                mode=LauncherMode.SOLO,
                status=ToolStatus.AVAILABLE,
                properties={'authentication': True, 'background': True}
            ))
            
            self.register_tool(ToolInfo(
                id='integrated_homelab',
                name='Integrated Homelab with Auth',
                description='Integrated homelab system with PC authentication',
                script_path=str(current_dir / 'integrated_homelab_with_auth.py'),
                mode=LauncherMode.INTEGRATED,
                status=ToolStatus.AVAILABLE,
                properties={'integrated': True, 'authentication': True, 'background': True}
            ))
            
            # Legacy homelab tools
            self.discover_legacy_tools()
            
            self.logger.info(f"Registered {len(self.tools)} tools")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tool registry: {e}")
    
    def discover_legacy_tools(self):
        """Discover legacy homelab tools"""
        try:
            legacy_path = Path(self.settings.get('legacy_tools_path', 'C:/Users/htsou/Desktop/Homelab Tools'))
            
            if not legacy_path.exists():
                self.logger.warning(f"Legacy tools path not found: {legacy_path}")
                return
            
            # Look for key legacy tools
            legacy_tools = {
                'homelab_launcher': {
                    'name': 'Homelab Tools Launcher',
                    'description': 'Original Homelab Tools launcher',
                    'script': 'homelab_launcher.py'
                },
                'homelab_portal': {
                    'name': 'Homelab Portal',
                    'description': 'Main Homelab portal system',
                    'script': 'Core Services/homelab_portal.py'
                },
                'auto_ram_connect': {
                    'name': 'Auto RAM Connect',
                    'description': 'Automatic RAM connection tool',
                    'script': 'Auto_RAM_Connect.py'
                }
            }
            
            for tool_id, tool_info in legacy_tools.items():
                script_path = legacy_path / tool_info['script']
                
                if script_path.exists():
                    self.register_tool(ToolInfo(
                        id=tool_id,
                        name=tool_info['name'],
                        description=tool_info['description'],
                        script_path=str(script_path),
                        mode=LauncherMode.LEGACY,
                        status=ToolStatus.AVAILABLE,
                        properties={'legacy': True, 'original_homelab': True}
                    ))
            
            self.logger.info(f"Discovered {len(legacy_tools)} legacy tools")
            
        except Exception as e:
            self.logger.error(f"Failed to discover legacy tools: {e}")
    
    def register_tool(self, tool: ToolInfo) -> bool:
        """Register a tool in the registry"""
        try:
            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tools 
                (id, name, description, script_path, mode, status, process_id, port, url,
                 dependencies, properties, created_at, last_run, run_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tool.id, tool.name, tool.description, tool.script_path, tool.mode.value,
                  tool.status.value, tool.process_id, tool.port, tool.url,
                  json.dumps(tool.dependencies), json.dumps(tool.properties),
                  tool.created_at if hasattr(tool, 'created_at') else datetime.now(),
                  None, 0))
            
            conn.commit()
            conn.close()
            
            # Add to memory
            self.tools[tool.id] = tool
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool.id}: {e}")
            return False
    
    def load_tool_states(self):
        """Load saved tool states from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM tools')
            rows = cursor.fetchall()
            
            for row in rows:
                tool_id = row[0]
                if tool_id in self.tools:
                    # Update tool state from database
                    self.tools[tool_id].status = ToolStatus(row[5])
                    self.tools[tool_id].process_id = row[6]
                    self.tools[tool_id].port = row[7]
                    self.tools[tool_id].url = row[8]
                    
                    # Check if process is still running
                    if self.tools[tool_id].process_id:
                        if self.is_process_running(self.tools[tool_id].process_id):
                            self.tools[tool_id].status = ToolStatus.RUNNING
                        else:
                            self.tools[tool_id].status = ToolStatus.STOPPED
                            self.tools[tool_id].process_id = None
            
            conn.close()
            self.logger.info(f"Loaded states for {len(self.tools)} tools")
            
        except Exception as e:
            self.logger.error(f"Failed to load tool states: {e}")
    
    def is_process_running(self, pid: int) -> bool:
        """Check if a process is still running"""
        try:
            return psutil.pid_exists(pid)
        except:
            return False
    
    def start_tool(self, tool_id: str, mode: Optional[LauncherMode] = None) -> bool:
        """Start a tool"""
        try:
            if tool_id not in self.tools:
                self.logger.error(f"Tool not found: {tool_id}")
                return False
            
            tool = self.tools[tool_id]
            
            # Check if already running
            if tool.status == ToolStatus.RUNNING:
                self.logger.warning(f"Tool {tool.name} is already running")
                return True
            
            # Check dependencies
            if not self.check_dependencies(tool):
                self.logger.error(f"Dependencies not met for tool {tool.name}")
                return False
            
            # Determine mode
            target_mode = mode or tool.mode
            
            # Start the tool
            if target_mode == LauncherMode.SOLO:
                success = self.start_solo_tool(tool)
            elif target_mode == LauncherMode.DASHBOARD:
                success = self.start_dashboard_tool(tool)
            elif target_mode == LauncherMode.INTEGRATED:
                success = self.start_integrated_tool(tool)
            elif target_mode == LauncherMode.AUTH:
                success = self.start_auth_tool(tool)
            elif target_mode == LauncherMode.LEGACY:
                success = self.start_legacy_tool(tool)
            else:
                success = self.start_tool_direct(tool)
            
            if success:
                # Update tool status
                tool.status = ToolStatus.RUNNING
                tool.last_run = datetime.now()
                
                # Update database
                self.update_tool_state(tool)
                
                # Log event
                self.log_launcher_event(tool_id, 'start', f"Started {tool.name}")
                
                self.logger.info(f"Successfully started tool: {tool.name}")
                return True
            else:
                tool.status = ToolStatus.ERROR
                self.update_tool_state(tool)
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start tool {tool_id}: {e}")
            if tool_id in self.tools:
                self.tools[tool_id].status = ToolStatus.ERROR
                self.update_tool_state(self.tools[tool_id])
            return False
    
    def start_solo_tool(self, tool: ToolInfo) -> bool:
        """Start tool in solo mode"""
        try:
            # Start background tools first
            solo_tools = self.settings.get('solo_mode_tools', [])
            
            for solo_tool_id in solo_tools:
                if solo_tool_id in self.tools:
                    solo_tool = self.tools[solo_tool_id]
                    if solo_tool.status != ToolStatus.RUNNING:
                        self.start_tool_direct(solo_tool)
            
            # Start the main tool
            return self.start_tool_direct(tool)
            
        except Exception as e:
            self.logger.error(f"Failed to start solo tool {tool.id}: {e}")
            return False
    
    def start_dashboard_tool(self, tool: ToolInfo) -> bool:
        """Start tool in dashboard mode"""
        try:
            # Start dashboard tools
            dashboard_tools = self.settings.get('dashboard_mode_tools', [])
            
            for dashboard_tool_id in dashboard_tools:
                if dashboard_tool_id in self.tools:
                    dashboard_tool = self.tools[dashboard_tool_id]
                    if dashboard_tool.status != ToolStatus.RUNNING:
                        self.start_tool_direct(dashboard_tool)
            
            # Start the main dashboard tool
            return self.start_tool_direct(tool)
            
        except Exception as e:
            self.logger.error(f"Failed to start dashboard tool {tool.id}: {e}")
            return False
    
    def start_integrated_tool(self, tool: ToolInfo) -> bool:
        """Start integrated tool"""
        try:
            # Start authentication system first
            auth_tools = ['pc_auth_system']
            for auth_tool_id in auth_tools:
                if auth_tool_id in self.tools:
                    auth_tool = self.tools[auth_tool_id]
                    if auth_tool.status != ToolStatus.RUNNING:
                        self.start_tool_direct(auth_tool)
            
            # Start core homelab system
            core_tools = ['streamlined_homelab']
            for core_tool_id in core_tools:
                if core_tool_id in self.tools:
                    core_tool = self.tools[core_tool_id]
                    if core_tool.status != ToolStatus.RUNNING:
                        self.start_tool_direct(core_tool)
            
            # Start the integrated tool
            return self.start_tool_direct(tool)
            
        except Exception as e:
            self.logger.error(f"Failed to start integrated tool {tool.id}: {e}")
            return False
    
    def start_auth_tool(self, tool: ToolInfo) -> bool:
        """Start authentication tool"""
        try:
            # Start auth system first
            auth_system = self.tools.get('pc_auth_system')
            if auth_system and auth_system.status != ToolStatus.RUNNING:
                self.start_tool_direct(auth_system)
            
            # Start the auth GUI
            return self.start_tool_direct(tool)
            
        except Exception as e:
            self.logger.error(f"Failed to start auth tool {tool.id}: {e}")
            return False
    
    def start_legacy_tool(self, tool: ToolInfo) -> bool:
        """Start legacy tool"""
        try:
            # Check if we're in the right directory
            script_path = Path(tool.script_path)
            working_dir = script_path.parent
            
            # Start the legacy tool
            return self.start_tool_direct(tool, working_dir=str(working_dir))
            
        except Exception as e:
            self.logger.error(f"Failed to start legacy tool {tool.id}: {e}")
            return False
    
    def start_tool_direct(self, tool: ToolInfo, working_dir: Optional[str] = None) -> bool:
        """Start tool directly"""
        try:
            # Check if script exists
            script_path = Path(tool.script_path)
            if not script_path.exists():
                self.logger.error(f"Script not found: {tool.script_path}")
                return False
            
            # Prepare command
            cmd = [sys.executable, str(script_path)]
            
            # Set working directory
            if not working_dir:
                working_dir = str(script_path.parent)
            
            # Start the process
            if tool.properties.get('gui', False):
                # GUI tool - start in background
                process = subprocess.Popen(cmd, cwd=working_dir, 
                                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # Background tool - start detached
                process = subprocess.Popen(cmd, cwd=working_dir, 
                                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
            
            # Store process info
            tool.process_id = process.pid
            self.running_processes[tool.id] = process
            
            # Wait a bit to check if it started successfully
            time.sleep(2)
            
            if process.poll() is None:
                self.logger.info(f"Tool {tool.name} started successfully (PID: {process.pid})")
                return True
            else:
                self.logger.error(f"Tool {tool.name} failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start tool {tool.id}: {e}")
            return False
    
    def stop_tool(self, tool_id: str) -> bool:
        """Stop a running tool"""
        try:
            if tool_id not in self.tools:
                self.logger.error(f"Tool not found: {tool_id}")
                return False
            
            tool = self.tools[tool_id]
            
            if tool.status != ToolStatus.RUNNING:
                self.logger.warning(f"Tool {tool.name} is not running")
                return True
            
            # Get process
            process = self.running_processes.get(tool_id)
            
            if process and process.poll() is None:
                # Try to terminate gracefully
                process.terminate()
                
                # Wait for graceful termination
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination fails
                    process.kill()
                    process.wait()
                
                self.logger.info(f"Tool {tool.name} stopped successfully")
            else:
                # Try to kill by PID
                if tool.process_id:
                    try:
                        psutil.Process(tool.process_id).terminate()
                        self.logger.info(f"Tool {tool.name} killed by PID")
                    except:
                        self.logger.warning(f"Could not kill tool {tool.name} by PID")
            
            # Update tool status
            tool.status = ToolStatus.STOPPED
            tool.process_id = None
            
            # Remove from running processes
            if tool_id in self.running_processes:
                del self.running_processes[tool_id]
            
            # Update database
            self.update_tool_state(tool)
            
            # Log event
            self.log_launcher_event(tool_id, 'stop', f"Stopped {tool.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop tool {tool_id}: {e}")
            return False
    
    def check_dependencies(self, tool: ToolInfo) -> bool:
        """Check if tool dependencies are met"""
        try:
            if not self.settings.get('check_dependencies', True):
                return True
            
            for dep in tool.dependencies:
                if dep not in self.tools:
                    self.logger.error(f"Dependency not found: {dep}")
                    return False
                
                dep_tool = self.tools[dep]
                if dep_tool.status != ToolStatus.RUNNING:
                    self.logger.info(f"Starting dependency: {dep}")
                    if not self.start_tool(dep):
                        self.logger.error(f"Failed to start dependency: {dep}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check dependencies for {tool.id}: {e}")
            return False
    
    def update_tool_state(self, tool: ToolInfo):
        """Update tool state in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tools SET status=?, process_id=?, port=?, url=?, last_run=?, run_count=run_count+1
                WHERE id=?
            ''', (tool.status.value, tool.process_id, tool.port, tool.url, 
                  datetime.now(), tool.id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update tool state for {tool.id}: {e}")
    
    def log_launcher_event(self, tool_id: str, event_type: str, description: str, 
                          details: Dict[str, Any] = None, success: bool = True):
        """Log launcher event"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO launcher_events 
                (tool_id, event_type, description, details, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (tool_id, event_type, description, json.dumps(details or {}), success))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to log launcher event: {e}")
    
    def get_tools_by_mode(self, mode: LauncherMode) -> List[ToolInfo]:
        """Get tools filtered by mode"""
        return [tool for tool in self.tools.values() if tool.mode == mode]
    
    def get_running_tools(self) -> List[ToolInfo]:
        """Get all running tools"""
        return [tool for tool in self.tools.values() if tool.status == ToolStatus.RUNNING]
    
    def get_tool_status(self, tool_id: str) -> Dict[str, Any]:
        """Get detailed tool status"""
        try:
            if tool_id not in self.tools:
                return {'status': 'error', 'message': 'Tool not found'}
            
            tool = self.tools[tool_id]
            
            # Check if process is still running
            if tool.process_id and not self.is_process_running(tool.process_id):
                tool.status = ToolStatus.STOPPED
                tool.process_id = None
                self.update_tool_state(tool)
            
            return {
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'mode': tool.mode.value,
                'status': tool.status.value,
                'process_id': tool.process_id,
                'port': tool.port,
                'url': tool.url,
                'dependencies': tool.dependencies,
                'properties': tool.properties,
                'last_run': tool.last_run.isoformat() if tool.last_run else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get tool status for {tool_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_launcher_status(self) -> Dict[str, Any]:
        """Get overall launcher status"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'current_mode': self.current_mode.value,
                'total_tools': len(self.tools),
                'running_tools': len(self.get_running_tools()),
                'tools_by_mode': {
                    mode.value: len(self.get_tools_by_mode(mode))
                    for mode in LauncherMode
                },
                'settings': {
                    'auto_start_tools': self.settings.get('auto_start_tools', []),
                    'check_dependencies': self.settings.get('check_dependencies', True),
                    'max_concurrent_tools': self.settings.get('max_concurrent_tools', 5)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get launcher status: {e}")
            return {'status': 'error', 'message': str(e)}

# Global launcher instance
unified_launcher = UnifiedLauncher()

if __name__ == '__main__':
    # Test the unified launcher
    print("🚀 Testing Unified Homelab Launcher")
    
    # Get launcher status
    status = unified_launcher.get_launcher_status()
    print(f"Launcher Status: {status}")
    
    # Test starting a tool
    if 'streamlined_dashboard' in unified_launcher.tools:
        print("Starting Streamlined Dashboard...")
        if unified_launcher.start_tool('streamlined_dashboard'):
            print("✅ Dashboard started successfully")
            time.sleep(5)
            unified_launcher.stop_tool('streamlined_dashboard')
            print("⏹️ Dashboard stopped")
        else:
            print("❌ Failed to start dashboard")
    
    # Keep running
    try:
        while True:
            time.sleep(60)
            status = unified_launcher.get_launcher_status()
            print(f"🔄 Launcher running... Tools: {status['total_tools']}, Running: {status['running_tools']}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        
        # Stop all running tools
        for tool in unified_launcher.get_running_tools():
            unified_launcher.stop_tool(tool.id)
