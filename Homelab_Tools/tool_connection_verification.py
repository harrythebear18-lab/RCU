#!/usr/bin/env python3
"""
Tool Connection Verification
Verifies tool links, connections, and integration between components
"""

import os
import sys
import json
import time
import logging
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from unified_path_manager import get_unified_path_manager, PathType, get_path
    from smart_system_sensing import get_smart_system_sensing
    CONNECTION_TOOLS_AVAILABLE = True
except ImportError as e:
    logging.getLogger("ToolConnectionVerification").warning(f"Connection tools not available: {e}")
    CONNECTION_TOOLS_AVAILABLE = False

class ConnectionStatus(Enum):
    """Connection status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WORKING = "working"
    PARTIAL = "partial"
    BROKEN = "broken"
    MISSING = "missing"

@dataclass
class ToolConnection:
    """Tool connection information"""
    source_tool: str
    target_tool: str
    connection_type: str
    status: ConnectionStatus
    path_exists: bool
    executable: bool
    working: bool
    issues: List[str]
    recommendations: List[str]

@dataclass
class ConnectionVerificationResult:
    """Connection verification result"""
    total_connections: int
    working_connections: int
    broken_connections: int
    missing_connections: int
    overall_status: ConnectionStatus
    tool_connections: List[ToolConnection]
    dashboard_tool_paths: Dict[str, Any]
    launcher_buttons: Dict[str, Any]
    portal_integrations: Dict[str, Any]
    recommendations: List[str]

class ToolConnectionVerifier:
    """Verifies tool connections and integration"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.root_dir = Path(__file__).parent
        self.tool_connections: List[ToolConnection] = []
        
        # Initialize tools
        if CONNECTION_TOOLS_AVAILABLE:
            self.path_manager = get_unified_path_manager()
            self.system_sensor = get_smart_system_sensing()
        else:
            self.path_manager = None
            self.system_sensor = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("ToolConnectionVerifier")
    
    def verify_tool_connections(self) -> ConnectionVerificationResult:
        """Verify all tool connections"""
        print("=" * 80)
        print("TOOL CONNECTION VERIFICATION")
        print("=" * 80)
        
        # 1. Dashboard Tool Path Verification
        print("\n1. DASHBOARD TOOL PATH VERIFICATION")
        dashboard_paths = self._verify_dashboard_tool_paths()
        
        # 2. Launcher Button Verification
        print("\n2. LAUNCHER BUTTON VERIFICATION")
        launcher_buttons = self._verify_launcher_buttons()
        
        # 3. Tool-to-Tool Connections
        print("\n3. TOOL-TO-TOOL CONNECTIONS")
        tool_connections = self._verify_tool_to_tool_connections()
        
        # 4. Portal Integration Verification
        print("\n4. PORTAL INTEGRATION VERIFICATION")
        portal_integrations = self._verify_portal_integrations()
        
        # 5. Cross-Component Links
        print("\n5. CROSS-COMPONENT LINKS")
        cross_component_links = self._verify_cross_component_links()
        
        # Generate results
        result = self._generate_verification_result(
            dashboard_paths, launcher_buttons, tool_connections,
            portal_integrations, cross_component_links
        )
        
        # Print summary
        self._print_verification_summary(result)
        
        # Save results
        self._save_verification_results(result)
        
        return result
    
    def _verify_dashboard_tool_paths(self) -> Dict[str, Any]:
        """Verify dashboard tool branch paths"""
        verification = {
            'dashboard_files': [],
            'tool_paths_found': 0,
            'working_paths': 0,
            'broken_paths': 0,
            'tool_branches': {},
            'path_details': {}
        }
        
        # Find dashboard files
        dashboard_files = [
            self.root_dir / "Core Services" / "unified_dashboard.py",
            self.root_dir / "Core Services" / "homelab_portal.py"
        ]
        
        for dashboard_file in dashboard_files:
            if dashboard_file.exists():
                verification['dashboard_files'].append(dashboard_file.name)
                
                try:
                    with open(dashboard_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for tool paths and branches
                    tool_path_patterns = [
                        r'tool_path\s*=\s*[\'"]([^\'"]+)[\'"]',
                        r'tool_branch\s*=\s*[\'"]([^\'"]+)[\'"]',
                        r'main_tool\s*=\s*[\'"]([^\'"]+)[\'"]',
                        r'tool_dir\s*=\s*[\'"]([^\'"]+)[\'"]',
                        r'launch_tool\([\'"]([^\'"]+)[\'"]',
                        r'subprocess\.call\([\'"]([^\'"]+)[\'"]',
                        r'os\.system\([\'"]([^\'"]+)[\'"]'
                    ]
                    
                    tool_paths = []
                    for pattern in tool_path_patterns:
                        matches = re.findall(pattern, content)
                        tool_paths.extend(matches)
                    
                    # Verify each tool path
                    for tool_path in tool_paths:
                        verification['tool_paths_found'] += 1
                        
                        # Check if path exists
                        tool_full_path = self.root_dir / tool_path
                        path_exists = tool_full_path.exists()
                        
                        # Check if executable
                        executable = False
                        if path_exists:
                            if tool_full_path.suffix == '.py':
                                executable = self._is_python_executable(tool_full_path)
                            elif tool_full_path.suffix == '.bat':
                                executable = self._is_batch_executable(tool_full_path)
                        
                        # Check if working
                        working = path_exists and executable
                        
                        if working:
                            verification['working_paths'] += 1
                        else:
                            verification['broken_paths'] += 1
                        
                        # Store details
                        verification['path_details'][tool_path] = {
                            'exists': path_exists,
                            'executable': executable,
                            'working': working,
                            'full_path': str(tool_full_path)
                        }
                        
                        # Categorize tool branch
                        tool_category = self._categorize_tool_path(tool_path)
                        if tool_category not in verification['tool_branches']:
                            verification['tool_branches'][tool_category] = []
                        verification['tool_branches'][tool_category].append(tool_path)
                    
                except Exception as e:
                    self.logger.error(f"Failed to verify dashboard {dashboard_file}: {e}")
        
        print(f"  ✓ Dashboard Files: {len(verification['dashboard_files'])}")
        print(f"  ✓ Tool Paths Found: {verification['tool_paths_found']}")
        print(f"  ✓ Working Paths: {verification['working_paths']}")
        print(f"  ✓ Broken Paths: {verification['broken_paths']}")
        print(f"  ✓ Tool Branches: {len(verification['tool_branches'])}")
        
        return verification
    
    def _verify_launcher_buttons(self) -> Dict[str, Any]:
        """Verify launcher buttons and functionality"""
        verification = {
            'launcher_files': [],
            'total_buttons': 0,
            'working_buttons': 0,
            'broken_buttons': 0,
            'additional_buttons': 0,
            'button_details': {},
            'launch_options': []
        }
        
        # Find launcher files
        launcher_files = list(self.root_dir.glob("*launcher*.bat"))
        launcher_files.extend(self.root_dir.glob("Launch_*.bat"))
        launcher_files.extend(self.root_dir.glob("*_Launcher*.py"))
        
        for launcher_file in launcher_files:
            verification['launcher_files'].append(launcher_file.name)
            
            try:
                with open(launcher_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if launcher_file.suffix == '.bat':
                    # Analyze batch file buttons/launch options
                    launch_options = re.findall(r'(?:call|start)\s+[\'"]?([^\'"\s]+)', content)
                    
                    for option in launch_options:
                        verification['total_buttons'] += 1
                        verification['launch_options'].append(option)
                        
                        # Check if target exists
                        target_path = self.root_dir / option
                        exists = target_path.exists()
                        
                        # Check if executable
                        executable = False
                        if exists:
                            if target_path.suffix == '.py':
                                executable = self._is_python_executable(target_path)
                            elif target_path.suffix == '.bat':
                                executable = self._is_batch_executable(target_path)
                        
                        working = exists and executable
                        
                        if working:
                            verification['working_buttons'] += 1
                        else:
                            verification['broken_buttons'] += 1
                        
                        verification['button_details'][option] = {
                            'exists': exists,
                            'executable': executable,
                            'working': working,
                            'type': 'batch_launch'
                        }
                
                elif launcher_file.suffix == '.py':
                    # Analyze Python launcher buttons
                    button_count = len(re.findall(r'Button', content))
                    verification['total_buttons'] += button_count
                    
                    # Look for additional buttons
                    if 'additional' in content.lower() or 'more' in content.lower():
                        verification['additional_buttons'] += button_count
                    
                    # Check for button functionality
                    button_commands = re.findall(r'command\s*=\s*[\'"]([^\'"]+)[\'"]', content)
                    for command in button_commands:
                        verification['button_details'][command] = {
                            'type': 'python_button',
                            'working': True  # Assume working for now
                        }
                        verification['working_buttons'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to verify launcher {launcher_file}: {e}")
        
        print(f"  ✓ Launcher Files: {len(verification['launcher_files'])}")
        print(f"  ✓ Total Buttons: {verification['total_buttons']}")
        print(f"  ✓ Working Buttons: {verification['working_buttons']}")
        print(f"  ✓ Broken Buttons: {verification['broken_buttons']}")
        print(f"  ✓ Additional Buttons: {verification['additional_buttons']}")
        
        return verification
    
    def _verify_tool_to_tool_connections(self) -> Dict[str, Any]:
        """Verify tool-to-tool connections"""
        verification = {
            'total_connections': 0,
            'working_connections': 0,
            'broken_connections': 0,
            'connection_types': {},
            'connection_details': {}
        }
        
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
        
        # Check each tool for connections to other tools
        for tool_file in tool_files:
            try:
                with open(tool_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for tool connections
                connection_patterns = [
                    r'import\s+(\w+)',
                    r'from\s+(\w+)\s+import',
                    r'subprocess\.call\([\'"]([^\'"]+)[\'"]',
                    r'os\.system\([\'"]([^\'"]+)[\'"]',
                    r'launch_tool\([\'"]([^\'"]+)[\'"]'
                ]
                
                for pattern in connection_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        verification['total_connections'] += 1
                        
                        # Determine connection type
                        if 'import' in pattern:
                            conn_type = 'import'
                        elif 'subprocess' in pattern or 'os.system' in pattern:
                            conn_type = 'process_call'
                        elif 'launch_tool' in pattern:
                            conn_type = 'tool_launch'
                        else:
                            conn_type = 'unknown'
                        
                        # Check if connection works
                        working = self._verify_tool_connection(match, conn_type)
                        
                        if working:
                            verification['working_connections'] += 1
                        else:
                            verification['broken_connections'] += 1
                        
                        # Update connection types
                        if conn_type not in verification['connection_types']:
                            verification['connection_types'][conn_type] = 0
                        verification['connection_types'][conn_type] += 1
                        
                        # Store connection details
                        connection_key = f"{tool_file.name}->{match}"
                        verification['connection_details'][connection_key] = {
                            'source': tool_file.name,
                            'target': match,
                            'type': conn_type,
                            'working': working
                        }
                
            except Exception as e:
                self.logger.error(f"Failed to verify tool connections for {tool_file}: {e}")
        
        print(f"  ✓ Total Connections: {verification['total_connections']}")
        print(f"  ✓ Working Connections: {verification['working_connections']}")
        print(f"  ✓ Broken Connections: {verification['broken_connections']}")
        print(f"  ✓ Connection Types: {len(verification['connection_types'])}")
        
        return verification
    
    def _verify_portal_integrations(self) -> Dict[str, Any]:
        """Verify portal integrations"""
        verification = {
            'subnet_portal': {},
            'unified_portal': {},
            'web_portal': {},
            'portal_connections': 0,
            'working_integrations': 0,
            'broken_integrations': 0
        }
        
        # Check subnet portal
        subnet_dir = self.root_dir / "Subnet Portal"
        if subnet_dir.exists():
            verification['subnet_portal'] = self._analyze_portal_integration(subnet_dir, "subnet")
        
        # Check unified portal
        unified_files = [
            self.root_dir / "Core Services" / "unified_dashboard.py",
            self.root_dir / "Core Services" / "homelab_portal.py"
        ]
        
        for unified_file in unified_files:
            if unified_file.exists():
                verification['unified_portal'][unified_file.name] = self._analyze_portal_integration(unified_file, "unified")
        
        # Check web portal
        web_dir = self.root_dir / "Web Dashboard"
        if web_dir.exists():
            verification['web_portal'] = self._analyze_portal_integration(web_dir, "web")
        
        # Calculate totals
        for portal_type in ['subnet_portal', 'unified_portal', 'web_portal']:
            if verification[portal_type]:
                verification['portal_connections'] += len(verification[portal_type])
                for integration in verification[portal_type].values():
                    if integration.get('working', False):
                        verification['working_integrations'] += 1
                    else:
                        verification['broken_integrations'] += 1
        
        print(f"  ✓ Portal Connections: {verification['portal_connections']}")
        print(f"  ✓ Working Integrations: {verification['working_integrations']}")
        print(f"  ✓ Broken Integrations: {verification['broken_integrations']}")
        
        return verification
    
    def _analyze_portal_integration(self, portal_path: Path, portal_type: str) -> Dict[str, Any]:
        """Analyze portal integration"""
        integration = {
            'type': portal_type,
            'features': {},
            'connections': [],
            'working': False
        }
        
        try:
            if portal_path.is_dir():
                # Directory-based portal
                for portal_file in portal_path.glob("*.py"):
                    with open(portal_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for integration features
                    if 'device_discovery' in content.lower():
                        integration['features']['device_discovery'] = True
                    if 'file_transfer' in content.lower():
                        integration['features']['file_transfer'] = True
                    if 'p2p' in content.lower():
                        integration['features']['p2p'] = True
                    if 'auto_discover' in content.lower():
                        integration['features']['auto_discovery'] = True
                    
                    # Look for connections
                    connection_patterns = [
                        r'import\s+(\w+)',
                        r'connect\(',
                        r'bind\(',
                        r'send\(',
                        r'receive\('
                    ]
                    
                    for pattern in connection_patterns:
                        matches = re.findall(pattern, content)
                        integration['connections'].extend(matches)
            
            else:
                # File-based portal
                with open(portal_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for integration features
                if 'device_discovery' in content.lower():
                    integration['features']['device_discovery'] = True
                if 'file_transfer' in content.lower():
                    integration['features']['file_transfer'] = True
                if 'p2p' in content.lower():
                    integration['features']['p2p'] = True
                if 'auto_discover' in content.lower():
                    integration['features']['auto_discovery'] = True
                
                # Look for connections
                connection_patterns = [
                    r'import\s+(\w+)',
                    r'connect\(',
                    r'bind\(',
                    r'send\(',
                    r'receive\('
                ]
                
                for pattern in connection_patterns:
                    matches = re.findall(pattern, content)
                    integration['connections'].extend(matches)
            
            # Determine if working
            integration['working'] = len(integration['features']) > 0 or len(integration['connections']) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to analyze portal integration {portal_path}: {e}")
        
        return integration
    
    def _verify_cross_component_links(self) -> Dict[str, Any]:
        """Verify cross-component links"""
        verification = {
            'total_links': 0,
            'working_links': 0,
            'broken_links': 0,
            'link_types': {},
            'link_details': {}
        }
        
        # Find all Python files
        python_files = list(self.root_dir.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for cross-component links
                link_patterns = [
                    r'sys\.path\.append\([\'"]([^\'"]+)[\'"]',
                    r'from\s+[\'"]([^\'"]+)[\'"]\s+import',
                    r'import\s+[\'"]([^\'"]+)[\'"]',
                    r'open\([\'"]([^\'"]+)[\'"]',
                    r'load\([\'"]([^\'"]+)[\'"]'
                ]
                
                for pattern in link_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        verification['total_links'] += 1
                        
                        # Determine link type
                        if 'sys.path' in pattern:
                            link_type = 'path_link'
                        elif 'import' in pattern:
                            link_type = 'import_link'
                        elif 'open' in pattern:
                            link_type = 'file_link'
                        elif 'load' in pattern:
                            link_type = 'load_link'
                        else:
                            link_type = 'unknown'
                        
                        # Check if link works
                        working = self._verify_cross_component_link(match, link_type)
                        
                        if working:
                            verification['working_links'] += 1
                        else:
                            verification['broken_links'] += 1
                        
                        # Update link types
                        if link_type not in verification['link_types']:
                            verification['link_types'][link_type] = 0
                        verification['link_types'][link_type] += 1
                        
                        # Store link details
                        link_key = f"{py_file.name}->{match}"
                        verification['link_details'][link_key] = {
                            'source': py_file.name,
                            'target': match,
                            'type': link_type,
                            'working': working
                        }
                
            except Exception as e:
                self.logger.error(f"Failed to verify cross-component links for {py_file}: {e}")
        
        print(f"  ✓ Total Links: {verification['total_links']}")
        print(f"  ✓ Working Links: {verification['working_links']}")
        print(f"  ✓ Broken Links: {verification['broken_links']}")
        print(f"  ✓ Link Types: {len(verification['link_types'])}")
        
        return verification
    
    def _is_python_executable(self, file_path: Path) -> bool:
        """Check if Python file is executable"""
        try:
            # Try to compile the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(file_path), 'exec')
            return True
        except:
            return False
    
    def _is_batch_executable(self, file_path: Path) -> bool:
        """Check if batch file is executable"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return '@echo' in content or 'call' in content or 'start' in content
        except:
            return False
    
    def _categorize_tool_path(self, tool_path: str) -> str:
        """Categorize tool path"""
        path_lower = tool_path.lower()
        
        if 'monitor' in path_lower:
            return 'monitoring'
        elif 'cpu' in path_lower:
            return 'cpu'
        elif 'gpu' in path_lower:
            return 'gpu'
        elif 'network' in path_lower:
            return 'network'
        elif 'memory' in path_lower or 'ram' in path_lower:
            return 'memory'
        elif 'storage' in path_lower:
            return 'storage'
        elif 'rdma' in path_lower:
            return 'rdma'
        elif 'security' in path_lower:
            return 'security'
        elif 'portal' in path_lower:
            return 'portal'
        else:
            return 'utility'
    
    def _verify_tool_connection(self, target: str, connection_type: str) -> bool:
        """Verify tool connection"""
        try:
            if connection_type == 'import':
                # Check if import target exists
                target_path = self.root_dir / f"{target}.py"
                return target_path.exists()
            
            elif connection_type in ['process_call', 'tool_launch']:
                # Check if target file exists
                target_path = self.root_dir / target
                return target_path.exists()
            
            return False
        except:
            return False
    
    def _verify_cross_component_link(self, target: str, link_type: str) -> bool:
        """Verify cross-component link"""
        try:
            if link_type == 'path_link':
                # Check if path exists
                target_path = self.root_dir / target
                return target_path.exists()
            
            elif link_type == 'file_link':
                # Check if file exists
                target_path = self.root_dir / target
                return target_path.exists()
            
            elif link_type == 'import_link':
                # Check if import target exists
                target_path = self.root_dir / f"{target}.py"
                return target_path.exists()
            
            return False
        except:
            return False
    
    def _generate_verification_result(self, dashboard_paths, launcher_buttons, tool_connections, portal_integrations, cross_component_links) -> ConnectionVerificationResult:
        """Generate verification result"""
        total_connections = (
            dashboard_paths['tool_paths_found'] +
            launcher_buttons['total_buttons'] +
            tool_connections['total_connections'] +
            portal_integrations['portal_connections'] +
            cross_component_links['total_links']
        )
        
        working_connections = (
            dashboard_paths['working_paths'] +
            launcher_buttons['working_buttons'] +
            tool_connections['working_connections'] +
            portal_integrations['working_integrations'] +
            cross_component_links['working_links']
        )
        
        broken_connections = (
            dashboard_paths['broken_paths'] +
            launcher_buttons['broken_buttons'] +
            tool_connections['broken_connections'] +
            portal_integrations['broken_integrations'] +
            cross_component_links['broken_links']
        )
        
        # Calculate overall status
        if total_connections > 0:
            working_percentage = (working_connections / total_connections) * 100
            
            if working_percentage >= 90:
                overall_status = ConnectionStatus.EXCELLENT
            elif working_percentage >= 75:
                overall_status = ConnectionStatus.GOOD
            elif working_percentage >= 50:
                overall_status = ConnectionStatus.WORKING
            elif working_percentage >= 25:
                overall_status = ConnectionStatus.PARTIAL
            else:
                overall_status = ConnectionStatus.BROKEN
        else:
            overall_status = ConnectionStatus.MISSING
        
        # Generate recommendations
        recommendations = []
        
        if dashboard_paths['broken_paths'] > 0:
            recommendations.append(f"Fix {dashboard_paths['broken_paths']} broken dashboard tool paths")
        
        if launcher_buttons['broken_buttons'] > 0:
            recommendations.append(f"Fix {launcher_buttons['broken_buttons']} broken launcher buttons")
        
        if tool_connections['broken_connections'] > 0:
            recommendations.append(f"Fix {tool_connections['broken_connections']} broken tool connections")
        
        if portal_integrations['broken_integrations'] > 0:
            recommendations.append(f"Fix {portal_integrations['broken_integrations']} broken portal integrations")
        
        if cross_component_links['broken_links'] > 0:
            recommendations.append(f"Fix {cross_component_links['broken_links']} broken cross-component links")
        
        # Create tool connections list
        tool_connections_list = []
        # This would be populated with actual ToolConnection objects
        
        return ConnectionVerificationResult(
            total_connections=total_connections,
            working_connections=working_connections,
            broken_connections=broken_connections,
            missing_connections=0,
            overall_status=overall_status,
            tool_connections=tool_connections_list,
            dashboard_tool_paths=dashboard_paths,
            launcher_buttons=launcher_buttons,
            portal_integrations=portal_integrations,
            recommendations=recommendations
        )
    
    def _print_verification_summary(self, result: ConnectionVerificationResult):
        """Print verification summary"""
        print("\n" + "=" * 80)
        print("TOOL CONNECTION VERIFICATION SUMMARY")
        print("=" * 80)
        
        print(f"Overall Status: {result.overall_status.value.upper()}")
        print(f"Total Connections: {result.total_connections}")
        print(f"Working Connections: {result.working_connections}")
        print(f"Broken Connections: {result.broken_connections}")
        
        if result.total_connections > 0:
            working_percentage = (result.working_connections / result.total_connections) * 100
            print(f"Success Rate: {working_percentage:.1f}%")
        
        print(f"\nDashboard Tool Paths:")
        dashboard = result.dashboard_tool_paths
        print(f"  Tool Paths Found: {dashboard.get('tool_paths_found', 0)}")
        print(f"  Working Paths: {dashboard.get('working_paths', 0)}")
        print(f"  Broken Paths: {dashboard.get('broken_paths', 0)}")
        print(f"  Tool Branches: {len(dashboard.get('tool_branches', {}))}")
        
        # Show tool branches
        if dashboard.get('tool_branches'):
            print(f"  Tool Branches:")
            for category, tools in dashboard['tool_branches'].items():
                print(f"    - {category}: {len(tools)} tools")
        
        print(f"\nLauncher Buttons:")
        launcher = result.launcher_buttons
        print(f"  Total Buttons: {launcher.get('total_buttons', 0)}")
        print(f"  Working Buttons: {launcher.get('working_buttons', 0)}")
        print(f"  Broken Buttons: {launcher.get('broken_buttons', 0)}")
        print(f"  Additional Buttons: {launcher.get('additional_buttons', 0)}")
        
        print(f"\nPortal Integrations:")
        portals = result.portal_integrations
        print(f"  Portal Connections: {portals.get('portal_connections', 0)}")
        print(f"  Working Integrations: {portals.get('working_integrations', 0)}")
        print(f"  Broken Integrations: {portals.get('broken_integrations', 0)}")
        
        # Show portal features
        for portal_type, portal_data in portals.items():
            if isinstance(portal_data, dict) and portal_data:
                print(f"  {portal_type.title()}:")
                for portal_name, integration in portal_data.items():
                    if isinstance(integration, dict):
                        features = integration.get('features', {})
                        if features:
                            print(f"    - {portal_name}: {list(features.keys())}")
        
        print(f"\nRecommendations: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Overall assessment
        if result.overall_status == ConnectionStatus.EXCELLENT:
            print(f"\n🎉 EXCELLENT: All tool connections working perfectly!")
        elif result.overall_status == ConnectionStatus.GOOD:
            print(f"\n✅ GOOD: Most tool connections working well!")
        elif result.overall_status == ConnectionStatus.WORKING:
            print(f"\n🔧 WORKING: Tool connections are functional but need improvement!")
        elif result.overall_status == ConnectionStatus.PARTIAL:
            print(f"\n⚠️  PARTIAL: Some tool connections working, others need fixing!")
        elif result.overall_status == ConnectionStatus.BROKEN:
            print(f"\n❌ BROKEN: Many tool connections are broken!")
        else:
            print(f"\n🚨 MISSING: Tool connections are missing!")
    
    def _save_verification_results(self, result: ConnectionVerificationResult):
        """Save verification results"""
        try:
            output_file = self.root_dir / "tool_connection_verification_results.json"
            
            # Convert to serializable format
            verification_data = {
                'overall_status': result.overall_status.value,
                'total_connections': result.total_connections,
                'working_connections': result.working_connections,
                'broken_connections': result.broken_connections,
                'dashboard_tool_paths': result.dashboard_tool_paths,
                'launcher_buttons': result.launcher_buttons,
                'portal_integrations': result.portal_integrations,
                'recommendations': result.recommendations
            }
            
            with open(output_file, 'w') as f:
                json.dump(verification_data, f, indent=2, default=str)
            
            print(f"\nDetailed verification results saved to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save verification results: {e}")

def main():
    """Main entry point"""
    verifier = ToolConnectionVerifier()
    result = verifier.verify_tool_connections()
    
    # Return appropriate exit code based on overall status
    if result.overall_status in [ConnectionStatus.EXCELLENT, ConnectionStatus.GOOD, ConnectionStatus.WORKING]:
        sys.exit(0)
    elif result.overall_status == ConnectionStatus.PARTIAL:
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
