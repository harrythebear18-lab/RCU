#!/usr/bin/env python3
"""
Comprehensive System Audit and Verification
Complete audit of Windows 10/11 compatibility, frontend GUI, backend components, tools, and systems
"""

import os
import sys
import json
import time
import logging
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from smart_system_sensing import get_smart_system_sensing, detect_system, is_windows_11, is_windows_10
    from unified_path_manager import get_unified_path_manager, PathType
    from frontend_backend_synchronization import get_frontend_backend_sync
    AUDIT_TOOLS_AVAILABLE = True
except ImportError as e:
    logging.getLogger("ComprehensiveSystemAudit").warning(f"Audit tools not available: {e}")
    AUDIT_TOOLS_AVAILABLE = False

class ComponentType(Enum):
    """Component types for audit"""
    FRONTEND_GUI = "frontend_gui"
    BACKEND_API = "backend_api"
    TOOL_CONSOLE = "tool_console"
    DASHBOARD = "dashboard"
    LAUNCHER = "launcher"
    SUBNET_PORTAL = "subnet_portal"
    UNIFIED_PORTAL = "unified_portal"

class AuditStatus(Enum):
    """Audit status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class ComponentAudit:
    """Component audit result"""
    component_name: str
    component_type: ComponentType
    file_path: str
    status: AuditStatus
    score: float
    issues: List[str]
    recommendations: List[str]
    features: Dict[str, Any]
    gui_elements: Dict[str, Any]
    backend_elements: Dict[str, Any]

@dataclass
class SystemAuditResult:
    """Complete system audit result"""
    total_components: int
    audited_components: int
    overall_status: AuditStatus
    overall_score: float
    windows_compatibility: Dict[str, Any]
    frontend_summary: Dict[str, Any]
    backend_summary: Dict[str, Any]
    tools_summary: Dict[str, Any]
    component_audits: List[ComponentAudit]
    recommendations: List[str]
    audit_time: float

class ComprehensiveSystemAudit:
    """Comprehensive system audit and verification"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.root_dir = Path(__file__).parent
        self.component_audits: List[ComponentAudit] = []
        self.issues_found: List[str] = []
        self.recommendations: List[str] = []
        
        # Initialize audit tools
        if AUDIT_TOOLS_AVAILABLE:
            self.system_sensor = get_smart_system_sensing()
            self.path_manager = get_unified_path_manager()
            self.sync_manager = get_frontend_backend_sync()
        else:
            self.system_sensor = None
            self.path_manager = None
            self.sync_manager = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("ComprehensiveSystemAudit")
    
    def run_comprehensive_audit(self) -> SystemAuditResult:
        """Run comprehensive system audit"""
        print("=" * 80)
        print("COMPREHENSIVE SYSTEM AUDIT & VERIFICATION")
        print("=" * 80)
        
        start_time = time.time()
        
        # 1. System Information Audit
        print("\n1. SYSTEM INFORMATION AUDIT")
        system_info = self._audit_system_information()
        
        # 2. Frontend GUI Components Audit
        print("\n2. FRONTEND GUI COMPONENTS AUDIT")
        frontend_results = self._audit_frontend_components()
        
        # 3. Backend Components Audit
        print("\n3. BACKEND COMPONENTS AUDIT")
        backend_results = self._audit_backend_components()
        
        # 4. Tools Audit
        print("\n4. TOOLS AUDIT")
        tools_results = self._audit_tools()
        
        # 5. Dashboard Audit
        print("\n5. DASHBOARD AUDIT")
        dashboard_results = self._audit_dashboard()
        
        # 6. Launcher Audit
        print("\n6. LAUNCHER AUDIT")
        launcher_results = self._audit_launcher()
        
        # 7. Subnet Portal Audit
        print("\n7. SUBNET PORTAL AUDIT")
        subnet_results = self._audit_subnet_portal()
        
        # 8. Unified Portal Audit
        print("\n8. UNIFIED PORTAL AUDIT")
        unified_results = self._audit_unified_portal()
        
        # 9. Windows Compatibility Audit
        print("\n9. WINDOWS COMPATIBILITY AUDIT")
        windows_results = self._audit_windows_compatibility()
        
        # Generate comprehensive results
        audit_time = time.time() - start_time
        result = self._generate_audit_result(
            system_info, frontend_results, backend_results, tools_results,
            dashboard_results, launcher_results, subnet_results, unified_results,
            windows_results, audit_time
        )
        
        # Print summary
        self._print_audit_summary(result)
        
        # Save results
        self._save_audit_results(result)
        
        return result
    
    def _audit_system_information(self) -> Dict[str, Any]:
        """Audit system information"""
        results = {
            'system_type': 'Unknown',
            'windows_version': 'Unknown',
            'hardware_profile': 'Unknown',
            'capabilities': [],
            'issues': [],
            'recommendations': []
        }
        
        try:
            if self.system_sensor:
                system_info = self.system_sensor.detect_system()
                results['system_type'] = system_info.system_type.value
                results['windows_version'] = system_info.version
                results['hardware_profile'] = system_info.hardware_profile.value
                results['capabilities'] = [cap.value for cap in system_info.capabilities]
                
                print(f"  ✓ System Type: {results['system_type']}")
                print(f"  ✓ Windows Version: {results['windows_version']}")
                print(f"  ✓ Hardware Profile: {results['hardware_profile']}")
                print(f"  ✓ Capabilities: {len(results['capabilities'])} detected")
                
                # Check for Windows 10/11 specific features
                if is_windows_11():
                    results['recommendations'].append("Windows 11 optimizations available")
                elif is_windows_10():
                    results['recommendations'].append("Windows 10 optimizations available")
                else:
                    results['issues'].append("Unsupported Windows version detected")
            else:
                results['issues'].append("System sensor not available")
                
        except Exception as e:
            results['issues'].append(f"System information audit failed: {e}")
            self.logger.error(f"System information audit error: {e}")
        
        return results
    
    def _audit_frontend_components(self) -> Dict[str, Any]:
        """Audit frontend GUI components"""
        results = {
            'total_gui_files': 0,
            'gui_files_with_buttons': 0,
            'gui_files_with_menus': 0,
            'gui_files_with_forms': 0,
            'total_buttons': 0,
            'total_menus': 0,
            'total_forms': 0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find all Python GUI files
            gui_files = []
            for pattern in ["*.py"]:
                gui_files.extend(self.root_dir.rglob(pattern))
            
            results['total_gui_files'] = len(gui_files)
            
            for gui_file in gui_files:
                try:
                    audit_result = self._audit_gui_file(gui_file)
                    if audit_result:
                        results['total_buttons'] += audit_result.get('buttons', 0)
                        results['total_menus'] += audit_result.get('menus', 0)
                        results['total_forms'] += audit_result.get('forms', 0)
                        
                        if audit_result.get('buttons', 0) > 0:
                            results['gui_files_with_buttons'] += 1
                        if audit_result.get('menus', 0) > 0:
                            results['gui_files_with_menus'] += 1
                        if audit_result.get('forms', 0) > 0:
                            results['gui_files_with_forms'] += 1
                except Exception as e:
                    results['issues'].append(f"Failed to audit {gui_file}: {e}")
            
            print(f"  ✓ Total GUI Files: {results['total_gui_files']}")
            print(f"  ✓ Files with Buttons: {results['gui_files_with_buttons']}")
            print(f"  ✓ Total Buttons: {results['total_buttons']}")
            print(f"  ✓ Files with Menus: {results['gui_files_with_menus']}")
            print(f"  ✓ Total Menus: {results['total_menus']}")
            print(f"  ✓ Files with Forms: {results['gui_files_with_forms']}")
            print(f"  ✓ Total Forms: {results['total_forms']}")
            
        except Exception as e:
            results['issues'].append(f"Frontend audit failed: {e}")
            self.logger.error(f"Frontend audit error: {e}")
        
        return results
    
    def _audit_gui_file(self, file_path: Path) -> Optional[Dict[str, int]]:
        """Audit individual GUI file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to find GUI elements
            try:
                tree = ast.parse(content)
            except:
                return None
            
            gui_elements = {
                'buttons': 0,
                'menus': 0,
                'forms': 0,
                'labels': 0,
                'entries': 0,
                'frames': 0
            }
            
            # Check for tkinter imports
            has_tkinter = any('tkinter' in node.names for node in ast.walk(tree) if isinstance(node, ast.Import))
            has_ttk = any('ttk' in node.names for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
            
            if not (has_tkinter or has_ttk):
                return None
            
            # Count GUI elements
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        # Check for button creation
                        if 'Button' in node.func.attr:
                            gui_elements['buttons'] += 1
                        elif 'Menu' in node.func.attr or 'Menubutton' in node.func.attr:
                            gui_elements['menus'] += 1
                        elif 'Label' in node.func.attr:
                            gui_elements['labels'] += 1
                        elif 'Entry' in node.func.attr:
                            gui_elements['entries'] += 1
                        elif 'Frame' in node.func.attr:
                            gui_elements['frames'] += 1
                    elif isinstance(node.func, ast.Name):
                        if node.func.id == 'Button':
                            gui_elements['buttons'] += 1
                        elif node.func.id in ['Menu', 'Menubutton']:
                            gui_elements['menus'] += 1
                        elif node.func.id == 'Label':
                            gui_elements['labels'] += 1
                        elif node.func.id == 'Entry':
                            gui_elements['entries'] += 1
                        elif node.func.id == 'Frame':
                            gui_elements['frames'] += 1
            
            # Count forms (frames with entries)
            if gui_elements['frames'] > 0 and gui_elements['entries'] > 0:
                gui_elements['forms'] = min(gui_elements['frames'], gui_elements['entries'])
            
            return gui_elements
            
        except Exception as e:
            self.logger.error(f"Failed to audit GUI file {file_path}: {e}")
            return None
    
    def _audit_backend_components(self) -> Dict[str, Any]:
        """Audit backend components"""
        results = {
            'total_backend_files': 0,
            'api_endpoints': 0,
            'database_connections': 0,
            'rest_apis': 0,
            'socket_servers': 0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find all backend files
            backend_files = []
            backend_patterns = ["rest_api.py", "api_*.py", "*_server.py", "*_service.py"]
            
            for pattern in backend_patterns:
                backend_files.extend(self.root_dir.rglob(pattern))
            
            results['total_backend_files'] = len(backend_files)
            
            for backend_file in backend_files:
                try:
                    audit_result = self._audit_backend_file(backend_file)
                    if audit_result:
                        results['api_endpoints'] += audit_result.get('api_endpoints', 0)
                        results['database_connections'] += audit_result.get('database_connections', 0)
                        results['rest_apis'] += audit_result.get('rest_apis', 0)
                        results['socket_servers'] += audit_result.get('socket_servers', 0)
                except Exception as e:
                    results['issues'].append(f"Failed to audit {backend_file}: {e}")
            
            print(f"  ✓ Total Backend Files: {results['total_backend_files']}")
            print(f"  ✓ API Endpoints: {results['api_endpoints']}")
            print(f"  ✓ Database Connections: {results['database_connections']}")
            print(f"  ✓ REST APIs: {results['rest_apis']}")
            print(f"  ✓ Socket Servers: {results['socket_servers']}")
            
        except Exception as e:
            results['issues'].append(f"Backend audit failed: {e}")
            self.logger.error(f"Backend audit error: {e}")
        
        return results
    
    def _audit_backend_file(self, file_path: Path) -> Optional[Dict[str, int]]:
        """Audit individual backend file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            backend_elements = {
                'api_endpoints': 0,
                'database_connections': 0,
                'rest_apis': 0,
                'socket_servers': 0
            }
            
            # Check for Flask/Django imports
            has_flask = 'flask' in content.lower()
            has_django = 'django' in content.lower()
            has_fastapi = 'fastapi' in content.lower()
            
            # Count API endpoints
            if has_flask:
                backend_elements['rest_apis'] += content.count('@app.route')
                backend_elements['api_endpoints'] += content.count('@app.route')
            elif has_django:
                backend_elements['rest_apis'] += content.count('def ')
                backend_elements['api_endpoints'] += content.count('def ')
            elif has_fastapi:
                backend_elements['rest_apis'] += content.count('@app.')
                backend_elements['api_endpoints'] += content.count('@app.')
            
            # Count database connections
            db_keywords = ['sqlite3', 'sqlalchemy', 'pymongo', 'psycopg2', 'mysql']
            for keyword in db_keywords:
                backend_elements['database_connections'] += content.count(keyword)
            
            # Count socket servers
            socket_keywords = ['socket.socket', 'asyncio.start_server', 'Flask-SocketIO']
            for keyword in socket_keywords:
                backend_elements['socket_servers'] += content.count(keyword)
            
            return backend_elements
            
        except Exception as e:
            self.logger.error(f"Failed to audit backend file {file_path}: {e}")
            return None
    
    def _audit_tools(self) -> Dict[str, Any]:
        """Audit all tools"""
        results = {
            'total_tools': 0,
            'tools_with_gui': 0,
            'tools_with_console': 0,
            'tools_with_both': 0,
            'monitoring_tools': 0,
            'utility_tools': 0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find all tool files
            tool_files = []
            tool_directories = [
                "Cpu Monitor", "Gpu Monitor", "Network Monitor", "Ram clean up",
                "RDMA", "Storage Management", "Core Services", "Subnet Portal"
            ]
            
            for tool_dir in tool_directories:
                tool_path = self.root_dir / tool_dir
                if tool_path.exists():
                    tool_files.extend(tool_path.glob("*.py"))
            
            results['total_tools'] = len(tool_files)
            
            for tool_file in tool_files:
                try:
                    audit_result = self._audit_tool_file(tool_file)
                    if audit_result:
                        if audit_result.get('has_gui', False):
                            results['tools_with_gui'] += 1
                        if audit_result.get('has_console', False):
                            results['tools_with_console'] += 1
                        if audit_result.get('has_gui', False) and audit_result.get('has_console', False):
                            results['tools_with_both'] += 1
                        
                        # Categorize tools
                        tool_name = tool_file.parent.name.lower()
                        if 'monitor' in tool_name:
                            results['monitoring_tools'] += 1
                        else:
                            results['utility_tools'] += 1
                except Exception as e:
                    results['issues'].append(f"Failed to audit tool {tool_file}: {e}")
            
            print(f"  ✓ Total Tools: {results['total_tools']}")
            print(f"  ✓ Tools with GUI: {results['tools_with_gui']}")
            print(f"  ✓ Tools with Console: {results['tools_with_console']}")
            print(f"  ✓ Tools with Both: {results['tools_with_both']}")
            print(f"  ✓ Monitoring Tools: {results['monitoring_tools']}")
            print(f"  ✓ Utility Tools: {results['utility_tools']}")
            
        except Exception as e:
            results['issues'].append(f"Tools audit failed: {e}")
            self.logger.error(f"Tools audit error: {e}")
        
        return results
    
    def _audit_tool_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Audit individual tool file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tool_info = {
                'has_gui': False,
                'has_console': False,
                'has_main': False,
                'gui_elements': 0
            }
            
            # Check for GUI elements
            if any(keyword in content for keyword in ['tkinter', 'ttk', 'Button', 'Label', 'Entry']):
                tool_info['has_gui'] = True
                tool_info['gui_elements'] = content.count('Button') + content.count('Label') + content.count('Entry')
            
            # Check for console elements
            if any(keyword in content for keyword in ['print(', 'input(', 'console', 'cmd']):
                tool_info['has_console'] = True
            
            # Check for main entry point
            if 'if __name__ == "__main__"' in content:
                tool_info['has_main'] = True
            
            return tool_info
            
        except Exception as e:
            self.logger.error(f"Failed to audit tool file {file_path}: {e}")
            return None
    
    def _audit_dashboard(self) -> Dict[str, Any]:
        """Audit dashboard components"""
        results = {
            'dashboard_files': 0,
            'has_unified_dashboard': False,
            'has_tool_branch_paths': False,
            'gui_components': 0,
            'real_time_updates': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find dashboard files
            dashboard_files = [
                self.root_dir / "Core Services" / "unified_dashboard.py",
                self.root_dir / "Core Services" / "homelab_portal.py",
                self.root_dir / "Web Dashboard" / "web_dashboard.py"
            ]
            
            results['dashboard_files'] = len([f for f in dashboard_files if f.exists()])
            
            for dashboard_file in dashboard_files:
                if dashboard_file.exists():
                    try:
                        with open(dashboard_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for unified dashboard
                        if 'unified_dashboard.py' in str(dashboard_file):
                            results['has_unified_dashboard'] = True
                        
                        # Check for tool branch paths
                        if any(keyword in content for keyword in ['tool_branch', 'main_tools', 'tool_paths']):
                            results['has_tool_branch_paths'] = True
                        
                        # Count GUI components
                        results['gui_components'] += content.count('Button') + content.count('Label') + content.count('Frame')
                        
                        # Check for real-time updates
                        if any(keyword in content for keyword in ['after', 'update', 'refresh', 'monitor']):
                            results['real_time_updates'] = True
                        
                    except Exception as e:
                        results['issues'].append(f"Failed to audit dashboard {dashboard_file}: {e}")
            
            print(f"  ✓ Dashboard Files: {results['dashboard_files']}")
            print(f"  ✓ Has Unified Dashboard: {results['has_unified_dashboard']}")
            print(f"  ✓ Has Tool Branch Paths: {results['has_tool_branch_paths']}")
            print(f"  ✓ GUI Components: {results['gui_components']}")
            print(f"  ✓ Real-time Updates: {results['real_time_updates']}")
            
        except Exception as e:
            results['issues'].append(f"Dashboard audit failed: {e}")
            self.logger.error(f"Dashboard audit error: {e}")
        
        return results
    
    def _audit_launcher(self) -> Dict[str, Any]:
        """Audit launcher components"""
        results = {
            'launcher_files': 0,
            'has_additional_buttons': False,
            'button_count': 0,
            'launch_options': 0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find launcher files
            launcher_files = list(self.root_dir.glob("*launcher*.bat"))
            launcher_files.extend(self.root_dir.glob("Launch_*.bat"))
            launcher_files.extend(self.root_dir.glob("*_Launcher*.py"))
            
            results['launcher_files'] = len(launcher_files)
            
            for launcher_file in launcher_files:
                try:
                    with open(launcher_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count buttons/launch options
                    if launcher_file.suffix == '.bat':
                        results['launch_options'] += content.count('call') + content.count('start')
                    else:
                        results['button_count'] += content.count('Button') + content.count('button')
                    
                    # Check for additional buttons
                    if any(keyword in content for keyword in ['additional', 'more', 'extra', 'advanced']):
                        results['has_additional_buttons'] = True
                        
                except Exception as e:
                    results['issues'].append(f"Failed to audit launcher {launcher_file}: {e}")
            
            print(f"  ✓ Launcher Files: {results['launcher_files']}")
            print(f"  ✓ Has Additional Buttons: {results['has_additional_buttons']}")
            print(f"  ✓ Button Count: {results['button_count']}")
            print(f"  ✓ Launch Options: {results['launch_options']}")
            
        except Exception as e:
            results['issues'].append(f"Launcher audit failed: {e}")
            self.logger.error(f"Launcher audit error: {e}")
        
        return results
    
    def _audit_subnet_portal(self) -> Dict[str, Any]:
        """Audit subnet portal components"""
        results = {
            'subnet_portal_files': 0,
            'has_comprehensive_features': False,
            'network_protocols': 0,
            'device_discovery': False,
            'file_transfer': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find subnet portal files
            subnet_dir = self.root_dir / "Subnet Portal"
            if subnet_dir.exists():
                results['subnet_portal_files'] = len(list(subnet_dir.glob("*.py")))
                
                for subnet_file in subnet_dir.glob("*.py"):
                    try:
                        with open(subnet_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for comprehensive features
                        if any(keyword in content for keyword in ['comprehensive', 'complete', 'full']):
                            results['has_comprehensive_features'] = True
                        
                        # Count network protocols
                        protocols = ['tcp', 'udp', 'http', 'websocket', 'socket']
                        for protocol in protocols:
                            results['network_protocols'] += content.lower().count(protocol)
                        
                        # Check for device discovery
                        if any(keyword in content for keyword in ['discovery', 'scan', 'detect']):
                            results['device_discovery'] = True
                        
                        # Check for file transfer
                        if any(keyword in content for keyword in ['file_transfer', 'send_file', 'receive_file']):
                            results['file_transfer'] = True
                        
                    except Exception as e:
                        results['issues'].append(f"Failed to audit subnet portal file {subnet_file}: {e}")
            
            print(f"  ✓ Subnet Portal Files: {results['subnet_portal_files']}")
            print(f"  ✓ Has Comprehensive Features: {results['has_comprehensive_features']}")
            print(f"  ✓ Network Protocols: {results['network_protocols']}")
            print(f"  ✓ Device Discovery: {results['device_discovery']}")
            print(f"  ✓ File Transfer: {results['file_transfer']}")
            
        except Exception as e:
            results['issues'].append(f"Subnet portal audit failed: {e}")
            self.logger.error(f"Subnet portal audit error: {e}")
        
        return results
    
    def _audit_unified_portal(self) -> Dict[str, Any]:
        """Audit unified portal components"""
        results = {
            'unified_portal_files': 0,
            'has_auto_device_discovery': False,
            'has_p2p_protocols': False,
            'has_listening_protocols': False,
            'device_count': 0,
            'protocol_count': 0,
            'issues': [],
            'recommendations': []
        }
        
        try:
            # Find unified portal files
            unified_files = [
                self.root_dir / "Core Services" / "unified_dashboard.py",
                self.root_dir / "Core Services" / "homelab_portal.py"
            ]
            
            results['unified_portal_files'] = len([f for f in unified_files if f.exists()])
            
            for unified_file in unified_files:
                if unified_file.exists():
                    try:
                        with open(unified_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for auto device discovery
                        if any(keyword in content for keyword in ['auto_discover', 'auto_device', 'automatic']):
                            results['has_auto_device_discovery'] = True
                        
                        # Check for P2P protocols
                        if any(keyword in content for keyword in ['p2p', 'peer', 'device_to_device']):
                            results['has_p2p_protocols'] = True
                        
                        # Check for listening protocols
                        if any(keyword in content for keyword in ['listen', 'bind', 'accept', 'receive']):
                            results['has_listening_protocols'] = True
                        
                        # Count devices and protocols
                        results['device_count'] += content.count('device')
                        protocols = ['tcp', 'udp', 'websocket', 'http', 'socket']
                        for protocol in protocols:
                            results['protocol_count'] += content.lower().count(protocol)
                        
                    except Exception as e:
                        results['issues'].append(f"Failed to audit unified portal {unified_file}: {e}")
            
            print(f"  ✓ Unified Portal Files: {results['unified_portal_files']}")
            print(f"  ✓ Has Auto Device Discovery: {results['has_auto_device_discovery']}")
            print(f"  ✓ Has P2P Protocols: {results['has_p2p_protocols']}")
            print(f"  ✓ Has Listening Protocols: {results['has_listening_protocols']}")
            print(f"  ✓ Device Count: {results['device_count']}")
            print(f"  ✓ Protocol Count: {results['protocol_count']}")
            
        except Exception as e:
            results['issues'].append(f"Unified portal audit failed: {e}")
            self.logger.error(f"Unified portal audit error: {e}")
        
        return results
    
    def _audit_windows_compatibility(self) -> Dict[str, Any]:
        """Audit Windows 10/11 compatibility"""
        results = {
            'windows_10_compatible': False,
            'windows_11_compatible': False,
            'compatibility_issues': [],
            'version_specific_features': [],
            'issues': [],
            'recommendations': []
        }
        
        try:
            if self.system_sensor:
                system_info = self.system_sensor.detect_system()
                
                results['windows_10_compatible'] = system_info.system_type.value in ['Windows 10', 'Windows 11']
                results['windows_11_compatible'] = system_info.system_type.value == 'Windows 11'
                
                # Check for version-specific features
                if system_info.system_type.value == 'Windows 11':
                    results['version_specific_features'].extend([
                        'Snap Layouts', 'Widgets', 'Centered Taskbar', 'Auto HDR'
                    ])
                elif system_info.system_type.value == 'Windows 10':
                    results['version_specific_features'].extend([
                        'Timeline', 'Cortana', 'Action Center', 'Virtual Desktops'
                    ])
                
                print(f"  ✓ Windows 10 Compatible: {results['windows_10_compatible']}")
                print(f"  ✓ Windows 11 Compatible: {results['windows_11_compatible']}")
                print(f"  ✓ Version-Specific Features: {len(results['version_specific_features'])}")
                
            else:
                results['issues'].append("System sensor not available for compatibility check")
                
        except Exception as e:
            results['issues'].append(f"Windows compatibility audit failed: {e}")
            self.logger.error(f"Windows compatibility audit error: {e}")
        
        return results
    
    def _generate_audit_result(self, system_info, frontend_results, backend_results, tools_results, dashboard_results, launcher_results, subnet_results, unified_results, windows_results, audit_time: float) -> SystemAuditResult:
        """Generate comprehensive audit result"""
        # Results are already passed as parameters
        
        # Calculate overall score
        total_score = 0
        max_score = 0
        
        # System info score
        if system_info.get('system_type') != 'Unknown':
            total_score += 20
        max_score += 20
        
        # Frontend score
        if frontend_results['total_gui_files'] > 0:
            frontend_score = min(20, (frontend_results['gui_files_with_buttons'] / max(frontend_results['total_gui_files'], 1)) * 20)
            total_score += frontend_score
        max_score += 20
        
        # Backend score
        if backend_results['total_backend_files'] > 0:
            backend_score = min(20, (backend_results['rest_apis'] / max(backend_results['total_backend_files'], 1)) * 20)
            total_score += backend_score
        max_score += 20
        
        # Tools score
        if tools_results['total_tools'] > 0:
            tools_score = min(20, (tools_results['tools_with_both'] / max(tools_results['total_tools'], 1)) * 20)
            total_score += tools_score
        max_score += 20
        
        # System components score
        component_score = 0
        if dashboard_results['has_unified_dashboard']:
            component_score += 5
        if launcher_results['has_additional_buttons']:
            component_score += 5
        if subnet_results['has_comprehensive_features']:
            component_score += 5
        if unified_results['has_auto_device_discovery']:
            component_score += 5
        total_score += component_score
        max_score += 20
        
        overall_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Determine overall status
        if overall_score >= 90:
            overall_status = AuditStatus.EXCELLENT
        elif overall_score >= 75:
            overall_status = AuditStatus.GOOD
        elif overall_score >= 60:
            overall_status = AuditStatus.FAIR
        elif overall_score >= 40:
            overall_status = AuditStatus.POOR
        else:
            overall_status = AuditStatus.CRITICAL
        
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        
        # Collect from all result dictionaries
        for result_dict in [system_info, frontend_results, backend_results, tools_results, 
                           dashboard_results, launcher_results, subnet_results, unified_results, windows_results]:
            if isinstance(result_dict, dict):
                all_issues.extend(result_dict.get('issues', []))
                all_recommendations.extend(result_dict.get('recommendations', []))
        
        # Create component audits
        component_audits = []
        
        return SystemAuditResult(
            total_components=len(list(self.root_dir.rglob("*.py"))),
            audited_components=len(self.component_audits),
            overall_status=overall_status,
            overall_score=overall_score,
            windows_compatibility=windows_results,
            frontend_summary=frontend_results,
            backend_summary=backend_results,
            tools_summary=tools_results,
            component_audits=component_audits,
            recommendations=all_recommendations,
            audit_time=audit_time
        )
    
    def _print_audit_summary(self, result: SystemAuditResult):
        """Print audit summary"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE SYSTEM AUDIT SUMMARY")
        print("=" * 80)
        
        print(f"Overall Status: {result.overall_status.value.upper()}")
        print(f"Overall Score: {result.overall_score:.1f}/100")
        print(f"Total Components: {result.total_components}")
        print(f"Audit Duration: {result.audit_time:.2f} seconds")
        
        print(f"\nWindows Compatibility:")
        print(f"  Windows 10 Compatible: {result.windows_compatibility.get('windows_10_compatible', False)}")
        print(f"  Windows 11 Compatible: {result.windows_compatibility.get('windows_11_compatible', False)}")
        print(f"  Version-Specific Features: {len(result.windows_compatibility.get('version_specific_features', []))}")
        
        print(f"\nFrontend Summary:")
        print(f"  Total GUI Files: {result.frontend_summary.get('total_gui_files', 0)}")
        print(f"  Files with Buttons: {result.frontend_summary.get('gui_files_with_buttons', 0)}")
        print(f"  Total Buttons: {result.frontend_summary.get('total_buttons', 0)}")
        
        print(f"\nBackend Summary:")
        print(f"  Total Backend Files: {result.backend_summary.get('total_backend_files', 0)}")
        print(f"  API Endpoints: {result.backend_summary.get('api_endpoints', 0)}")
        print(f"  REST APIs: {result.backend_summary.get('rest_apis', 0)}")
        
        print(f"\nTools Summary:")
        print(f"  Total Tools: {result.tools_summary.get('total_tools', 0)}")
        print(f"  Tools with GUI: {result.tools_summary.get('tools_with_gui', 0)}")
        print(f"  Tools with Console: {result.tools_summary.get('tools_with_console', 0)}")
        print(f"  Tools with Both: {result.tools_summary.get('tools_with_both', 0)}")
        
        print(f"\nRecommendations: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations[:10], 1):
            print(f"  {i}. {rec}")
        
        if len(result.recommendations) > 10:
            print(f"  ... and {len(result.recommendations) - 10} more recommendations")
        
        # Overall assessment
        if result.overall_status == AuditStatus.EXCELLENT:
            print(f"\n🎉 EXCELLENT: System is fully functional and optimized!")
        elif result.overall_status == AuditStatus.GOOD:
            print(f"\n✅ GOOD: System is mostly functional with minor issues!")
        elif result.overall_status == AuditStatus.FAIR:
            print(f"\n⚠️  FAIR: System needs some improvements!")
        elif result.overall_status == AuditStatus.POOR:
            print(f"\n❌ POOR: System has significant issues!")
        else:
            print(f"\n🚨 CRITICAL: System requires immediate attention!")
    
    def _save_audit_results(self, result: SystemAuditResult):
        """Save audit results"""
        try:
            output_file = self.root_dir / "comprehensive_system_audit_results.json"
            
            # Convert to serializable format
            audit_data = {
                'overall_status': result.overall_status.value,
                'overall_score': result.overall_score,
                'total_components': result.total_components,
                'audited_components': result.audited_components,
                'windows_compatibility': result.windows_compatibility,
                'frontend_summary': result.frontend_summary,
                'backend_summary': result.backend_summary,
                'tools_summary': result.tools_summary,
                'recommendations': result.recommendations,
                'audit_time': result.audit_time
            }
            
            with open(output_file, 'w') as f:
                json.dump(audit_data, f, indent=2, default=str)
            
            print(f"\nDetailed audit results saved to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save audit results: {e}")

def main():
    """Main entry point"""
    auditor = ComprehensiveSystemAudit()
    result = auditor.run_comprehensive_audit()
    
    # Return appropriate exit code based on overall status
    if result.overall_status in [AuditStatus.EXCELLENT, AuditStatus.GOOD]:
        sys.exit(0)
    elif result.overall_status == AuditStatus.FAIR:
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
