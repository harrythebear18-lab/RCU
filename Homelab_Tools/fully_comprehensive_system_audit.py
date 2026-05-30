#!/usr/bin/env python3
"""
Fully Comprehensive System Audit
Deep analysis of original and new components with detailed functionality checks
"""

import os
import sys
import json
import time
import logging
import ast
import subprocess
import importlib.util
import threading
import socket
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import inspect

# Add Core Services to path
sys.path.append(str(Path(__file__).parent / "Core Services"))

try:
    from smart_system_sensing import get_smart_system_sensing, detect_system, is_windows_11, is_windows_10
    from unified_path_manager import get_unified_path_manager, PathType
    from frontend_backend_synchronization import get_frontend_backend_sync
    AUDIT_TOOLS_AVAILABLE = True
except ImportError as e:
    logging.getLogger("FullyComprehensiveAudit").warning(f"Audit tools not available: {e}")
    AUDIT_TOOLS_AVAILABLE = False

class ComponentStatus(Enum):
    """Component status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WORKING = "working"
    PARTIAL = "partial"
    BROKEN = "broken"
    MISSING = "missing"

class InterfaceType(Enum):
    """Interface types"""
    GUI_TKINTER = "gui_tkinter"
    GUI_WEB = "gui_web"
    CONSOLE = "console"
    API_REST = "api_rest"
    API_SOCKET = "api_socket"
    BATCH = "batch"
    HYBRID = "hybrid"

@dataclass
class ComponentDetail:
    """Detailed component information"""
    name: str
    path: str
    component_type: str
    interface_types: List[InterfaceType] = field(default_factory=list)
    status: ComponentStatus = ComponentStatus.MISSING
    functionality_score: float = 0.0
    features: Dict[str, Any] = field(default_factory=dict)
    gui_elements: Dict[str, int] = field(default_factory=dict)
    api_endpoints: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    working_features: List[str] = field(default_factory=list)
    hidden_features: List[str] = field(default_factory=list)
    code_analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemAnalysisResult:
    """Complete system analysis result"""
    total_components: int
    analyzed_components: int
    working_components: int
    broken_components: int
    missing_components: int
    overall_status: ComponentStatus
    overall_score: float
    component_details: List[ComponentDetail]
    system_capabilities: Dict[str, Any]
    frontend_analysis: Dict[str, Any]
    backend_analysis: Dict[str, Any]
    tools_analysis: Dict[str, Any]
    hidden_working_components: List[str]
    recommendations: List[str]
    audit_duration: float

class FullyComprehensiveSystemAudit:
    """Fully comprehensive system audit with deep analysis"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.root_dir = Path(__file__).parent
        self.component_details: List[ComponentDetail] = []
        self.working_components: Set[str] = set()
        self.hidden_working: Set[str] = set()
        
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
        """Setup detailed logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("FullyComprehensiveAudit")
    
    def run_fully_comprehensive_audit(self) -> SystemAnalysisResult:
        """Run fully comprehensive system audit"""
        print("=" * 100)
        print("FULLY COMPREHENSIVE SYSTEM AUDIT & ANALYSIS")
        print("=" * 100)
        
        start_time = time.time()
        
        # 1. System Environment Analysis
        print("\n1. SYSTEM ENVIRONMENT ANALYSIS")
        system_env = self._analyze_system_environment()
        
        # 2. Deep Component Discovery
        print("\n2. DEEP COMPONENT DISCOVERY")
        all_components = self._discover_all_components()
        
        # 3. Component-by-Component Analysis
        print("\n3. COMPONENT-BY-COMPONENT ANALYSIS")
        component_analysis = self._analyze_components_detailed(all_components)
        
        # 4. Hidden Functionality Detection
        print("\n4. HIDDEN FUNCTIONALITY DETECTION")
        hidden_analysis = self._detect_hidden_functionality(all_components)
        
        # 5. Interface Analysis
        print("\n5. INTERFACE ANALYSIS")
        interface_analysis = self._analyze_interfaces(all_components)
        
        # 6. Backend Services Analysis
        print("\n6. BACKEND SERVICES ANALYSIS")
        backend_analysis = self._analyze_backend_services(all_components)
        
        # 7. Tools Deep Dive
        print("\n7. TOOLS DEEP DIVE")
        tools_analysis = self._analyze_tools_deep(all_components)
        
        # 8. Dashboard & Launcher Analysis
        print("\n8. DASHBOARD & LAUNCHER ANALYSIS")
        dashboard_analysis = self._analyze_dashboard_launcher(all_components)
        
        # 9. Portal Systems Analysis
        print("\n9. PORTAL SYSTEMS ANALYSIS")
        portal_analysis = self._analyze_portal_systems(all_components)
        
        # 10. Windows Compatibility Deep Check
        print("\n10. WINDOWS COMPATIBILITY DEEP CHECK")
        windows_analysis = self._analyze_windows_compatibility_deep()
        
        # Generate comprehensive results
        audit_duration = time.time() - start_time
        result = self._generate_comprehensive_result(
            system_env, component_analysis, hidden_analysis, interface_analysis,
            backend_analysis, tools_analysis, dashboard_analysis, portal_analysis,
            windows_analysis, audit_duration
        )
        
        # Print comprehensive summary
        self._print_comprehensive_summary(result)
        
        # Save detailed results
        self._save_comprehensive_results(result)
        
        return result
    
    def _analyze_system_environment(self) -> Dict[str, Any]:
        """Analyze system environment in detail"""
        analysis = {
            'system_info': {},
            'python_version': sys.version,
            'python_paths': sys.path,
            'environment_variables': {},
            'available_modules': [],
            'missing_modules': [],
            'system_resources': {},
            'network_status': {},
            'issues': [],
            'capabilities': []
        }
        
        try:
            # System information
            if self.system_sensor:
                system_info = self.system_sensor.detect_system()
                analysis['system_info'] = {
                    'type': system_info.system_type.value,
                    'version': system_info.version,
                    'build': system_info.build_number,
                    'hardware': system_info.hardware_profile.value,
                    'capabilities': [cap.value for cap in system_info.capabilities],
                    'score': system_info.total_score
                }
                
                print(f"  ✓ System: {system_info.system_type.value}")
                print(f"  ✓ Version: {system_info.version}")
                print(f"  ✓ Hardware: {system_info.hardware_profile.value}")
                print(f"  ✓ Capabilities: {len(system_info.capabilities)}")
            
            # Python environment
            analysis['python_version'] = sys.version
            analysis['python_paths'] = sys.path[:5]  # First 5 paths
            
            # Check key modules
            key_modules = [
                'tkinter', 'ttk', 'flask', 'fastapi', 'django', 'psutil',
                'matplotlib', 'numpy', 'pandas', 'requests', 'websockets',
                'asyncio', 'threading', 'socket', 'json', 'sqlite3'
            ]
            
            for module in key_modules:
                try:
                    __import__(module)
                    analysis['available_modules'].append(module)
                except ImportError:
                    analysis['missing_modules'].append(module)
            
            print(f"  ✓ Available Modules: {len(analysis['available_modules'])}")
            print(f"  ✓ Missing Modules: {len(analysis['missing_modules'])}")
            
            # System resources
            try:
                import psutil
                analysis['system_resources'] = {
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': psutil.virtual_memory().total,
                    'disk_total': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total
                }
            except:
                pass
            
            # Network status
            try:
                analysis['network_status'] = {
                    'hostname': socket.gethostname(),
                    'localhost_resolves': socket.gethostbyname('localhost') == '127.0.0.1'
                }
            except:
                pass
            
        except Exception as e:
            analysis['issues'].append(f"System environment analysis failed: {e}")
            self.logger.error(f"System environment analysis error: {e}")
        
        return analysis
    
    def _discover_all_components(self) -> List[Path]:
        """Discover all components in the system"""
        components = []
        
        # Find all Python files
        python_files = list(self.root_dir.rglob("*.py"))
        components.extend(python_files)
        
        # Find all batch files
        batch_files = list(self.root_dir.rglob("*.bat"))
        components.extend(batch_files)
        
        # Find all executable scripts
        script_files = list(self.root_dir.rglob("*.sh"))
        components.extend(script_files)
        
        # Find configuration files
        config_files = list(self.root_dir.rglob("*.json"))
        config_files.extend(list(self.root_dir.rglob("*.config")))
        config_files.extend(list(self.root_dir.rglob("*.cfg")))
        components.extend(config_files)
        
        print(f"  ✓ Python Files: {len(python_files)}")
        print(f"  ✓ Batch Files: {len(batch_files)}")
        print(f"  ✓ Script Files: {len(script_files)}")
        print(f"  ✓ Config Files: {len(config_files)}")
        print(f"  ✓ Total Components: {len(components)}")
        
        return components
    
    def _analyze_components_detailed(self, components: List[Path]) -> Dict[str, Any]:
        """Analyze each component in detail"""
        analysis = {
            'total_components': len(components),
            'analyzed_components': 0,
            'working_components': 0,
            'broken_components': 0,
            'missing_components': 0,
            'component_types': {},
            'interface_distribution': {},
            'functionality_scores': [],
            'common_issues': [],
            'working_features': []
        }
        
        for component in components:
            try:
                detail = self._analyze_single_component(component)
                if detail:
                    self.component_details.append(detail)
                    analysis['analyzed_components'] += 1
                    
                    # Update statistics
                    if detail.status == ComponentStatus.WORKING:
                        analysis['working_components'] += 1
                        self.working_components.add(detail.name)
                    elif detail.status == ComponentStatus.BROKEN:
                        analysis['broken_components'] += 1
                    elif detail.status == ComponentStatus.MISSING:
                        analysis['missing_components'] += 1
                    
                    # Component types
                    comp_type = detail.component_type
                    analysis['component_types'][comp_type] = analysis['component_types'].get(comp_type, 0) + 1
                    
                    # Interface distribution
                    for interface in detail.interface_types:
                        analysis['interface_distribution'][interface.value] = analysis['interface_distribution'].get(interface.value, 0) + 1
                    
                    # Functionality scores
                    analysis['functionality_scores'].append(detail.functionality_score)
                    
                    # Working features
                    analysis['working_features'].extend(detail.working_features)
                    
                    # Common issues
                    analysis['common_issues'].extend(detail.issues[:2])  # First 2 issues per component
                
                # Progress indicator
                if analysis['analyzed_components'] % 20 == 0:
                    print(f"    Analyzed: {analysis['analyzed_components']}/{len(components)}")
                    
            except Exception as e:
                self.logger.error(f"Failed to analyze component {component}: {e}")
                analysis['broken_components'] += 1
        
        # Calculate statistics
        if analysis['functionality_scores']:
            avg_score = sum(analysis['functionality_scores']) / len(analysis['functionality_scores'])
            analysis['average_functionality_score'] = avg_score
        else:
            analysis['average_functionality_score'] = 0.0
        
        print(f"  ✓ Analyzed Components: {analysis['analyzed_components']}")
        print(f"  ✓ Working Components: {analysis['working_components']}")
        print(f"  ✓ Broken Components: {analysis['broken_components']}")
        print(f"  ✓ Average Functionality Score: {analysis['average_functionality_score']:.1f}")
        
        return analysis
    
    def _analyze_single_component(self, component_path: Path) -> Optional[ComponentDetail]:
        """Analyze a single component in detail"""
        try:
            detail = ComponentDetail(
                name=component_path.stem,
                path=str(component_path),
                component_type=self._classify_component(component_path),
                status=ComponentStatus.MISSING,
                functionality_score=0.0
            )
            
            # Read file content
            with open(component_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Code analysis
            detail.code_analysis = self._analyze_code_structure(content, component_path.suffix)
            
            # Interface detection
            detail.interface_types = self._detect_interfaces(content)
            
            # GUI element analysis
            if any(interface in detail.interface_types for interface in [InterfaceType.GUI_TKINTER, InterfaceType.GUI_WEB]):
                detail.gui_elements = self._analyze_gui_elements(content)
            
            # API endpoint analysis
            if InterfaceType.API_REST in detail.interface_types:
                detail.api_endpoints = self._extract_api_endpoints(content)
            
            # Feature detection
            detail.features = self._detect_features(content)
            detail.working_features = self._detect_working_features(content, component_path)
            detail.hidden_features = self._detect_hidden_features(content)
            
            # Dependency analysis
            detail.dependencies = self._extract_dependencies(content)
            
            # Status determination
            detail.status, detail.functionality_score = self._determine_component_status(detail)
            
            # Issue detection
            detail.issues = self._detect_component_issues(detail, content)
            
            return detail
            
        except Exception as e:
            self.logger.error(f"Failed to analyze component {component_path}: {e}")
            return None
    
    def _classify_component(self, component_path: Path) -> str:
        """Classify component type"""
        path_str = str(component_path).lower()
        parent_dir = component_path.parent.name.lower()
        
        # Directory-based classification
        if 'core services' in path_str:
            return 'core_service'
        elif 'monitor' in parent_dir or 'monitor' in path_str:
            return 'monitoring_tool'
        elif 'rdma' in path_str:
            return 'rdma_tool'
        elif 'subnet portal' in path_str:
            return 'subnet_portal'
        elif 'storage' in path_str:
            return 'storage_tool'
        elif 'network' in path_str:
            return 'network_tool'
        elif 'gpu' in path_str:
            return 'gpu_tool'
        elif 'cpu' in path_str:
            return 'cpu_tool'
        elif 'ram' in path_str or 'memory' in path_str:
            return 'memory_tool'
        
        # File-based classification
        if 'dashboard' in path_str:
            return 'dashboard'
        elif 'launcher' in path_str or 'launch' in path_str:
            return 'launcher'
        elif 'portal' in path_str:
            return 'portal'
        elif 'api' in path_str:
            return 'api'
        elif 'server' in path_str:
            return 'server'
        elif 'client' in path_str:
            return 'client'
        elif 'service' in path_str:
            return 'service'
        elif 'test' in path_str:
            return 'test'
        elif 'config' in path_str:
            return 'config'
        elif 'util' in path_str:
            return 'utility'
        
        return 'unknown'
    
    def _analyze_code_structure(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Analyze code structure"""
        structure = {
            'lines_of_code': len(content.splitlines()),
            'has_main_function': False,
            'has_classes': False,
            'has_functions': False,
            'has_imports': False,
            'has_error_handling': False,
            'has_threading': False,
            'has_async': False,
            'complexity_score': 0.0
        }
        
        if file_extension == '.py':
            try:
                tree = ast.parse(content)
                
                # Check for main function
                structure['has_main_function'] = 'if __name__ == "__main__"' in content
                
                # Check for classes and functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        structure['has_classes'] = True
                    elif isinstance(node, ast.FunctionDef):
                        structure['has_functions'] = True
                    elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                        structure['has_imports'] = True
                
                # Check for specific patterns
                structure['has_error_handling'] = 'try:' in content and 'except' in content
                structure['has_threading'] = 'threading' in content or 'Thread' in content
                structure['has_async'] = 'async' in content and 'await' in content
                
                # Calculate complexity score
                complexity_indicators = [
                    structure['has_classes'],
                    structure['has_functions'],
                    structure['has_imports'],
                    structure['has_error_handling'],
                    structure['has_threading'],
                    structure['has_async']
                ]
                structure['complexity_score'] = sum(complexity_indicators) / len(complexity_indicators) * 100
                
            except:
                pass
        
        return structure
    
    def _detect_interfaces(self, content: str) -> List[InterfaceType]:
        """Detect interface types"""
        interfaces = []
        content_lower = content.lower()
        
        # GUI detection
        if 'tkinter' in content_lower or 'import tkinter' in content_lower:
            interfaces.append(InterfaceType.GUI_TKINTER)
        if 'flask' in content_lower or 'django' in content_lower or 'fastapi' in content_lower:
            interfaces.append(InterfaceType.GUI_WEB)
        
        # Console detection
        if 'print(' in content_lower or 'input(' in content_lower or 'console' in content_lower:
            interfaces.append(InterfaceType.CONSOLE)
        
        # API detection
        if 'flask' in content_lower or 'fastapi' in content_lower or 'django' in content_lower:
            interfaces.append(InterfaceType.API_REST)
        if 'socket' in content_lower or 'websocket' in content_lower or 'listen(' in content_lower:
            interfaces.append(InterfaceType.API_SOCKET)
        
        # Batch detection
        if '@echo' in content_lower or 'call ' in content_lower or 'start ' in content_lower:
            interfaces.append(InterfaceType.BATCH)
        
        # Hybrid detection
        if len(interfaces) > 1:
            interfaces.append(InterfaceType.HYBRID)
        
        return interfaces
    
    def _analyze_gui_elements(self, content: str) -> Dict[str, int]:
        """Analyze GUI elements"""
        elements = {
            'buttons': 0,
            'labels': 0,
            'entries': 0,
            'frames': 0,
            'menus': 0,
            'text_areas': 0,
            'check_boxes': 0,
            'radio_buttons': 0,
            'list_boxes': 0,
            'combo_boxes': 0,
            'progress_bars': 0,
            'canvases': 0
        }
        
        # Count GUI elements
        element_patterns = {
            'buttons': r'\bButton\b|\bbutton\b',
            'labels': r'\bLabel\b|\blabel\b',
            'entries': r'\bEntry\b|\bentry\b',
            'frames': r'\bFrame\b|\bframe\b',
            'menus': r'\bMenu\b|\bmenu\b|\bMenubutton\b',
            'text_areas': r'\bText\b|\btext\b|\bTextArea\b',
            'check_boxes': r'\bCheckbutton\b|\bcheckbox\b',
            'radio_buttons': r'\bRadiobutton\b|\bradiobutton\b',
            'list_boxes': r'\bListbox\b|\blistbox\b',
            'combo_boxes': r'\bCombobox\b|\bcombobox\b',
            'progress_bars': r'\bProgressbar\b|\bprogressbar\b',
            'canvases': r'\bCanvas\b|\bcanvas\b'
        }
        
        for element, pattern in element_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            elements[element] = len(matches)
        
        return elements
    
    def _extract_api_endpoints(self, content: str) -> List[str]:
        """Extract API endpoints"""
        endpoints = []
        
        # Flask endpoints
        flask_routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', content)
        endpoints.extend(flask_routes)
        
        # FastAPI endpoints
        fastapi_routes = re.findall(r'@app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]', content)
        endpoints.extend([route[1] for route in fastapi_routes])
        
        # Django URLs
        django_urls = re.findall(r'path\([\'"]([^\'"]+)[\'"]', content)
        endpoints.extend(django_urls)
        
        return endpoints
    
    def _detect_features(self, content: str) -> Dict[str, Any]:
        """Detect component features"""
        features = {
            'monitoring': False,
            'networking': False,
            'file_operations': False,
            'database': False,
            'logging': False,
            'configuration': False,
            'security': False,
            'optimization': False,
            'automation': False,
            'visualization': False
        }
        
        feature_keywords = {
            'monitoring': ['monitor', 'track', 'measure', 'stats', 'performance'],
            'networking': ['network', 'socket', 'connect', 'send', 'receive', 'protocol'],
            'file_operations': ['file', 'read', 'write', 'save', 'load', 'open'],
            'database': ['database', 'sql', 'query', 'connect', 'execute'],
            'logging': ['log', 'logger', 'debug', 'info', 'warning', 'error'],
            'configuration': ['config', 'settings', 'options', 'preferences'],
            'security': ['security', 'auth', 'encrypt', 'decrypt', 'password'],
            'optimization': ['optimize', 'improve', 'enhance', 'boost', 'speed'],
            'automation': ['automate', 'schedule', 'task', 'job', 'process'],
            'visualization': ['plot', 'chart', 'graph', 'display', 'render']
        }
        
        content_lower = content.lower()
        for feature, keywords in feature_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                features[feature] = True
        
        return features
    
    def _detect_working_features(self, content: str, component_path: Path) -> List[str]:
        """Detect working features by analyzing code patterns"""
        working_features = []
        
        # Check for complete implementations
        if 'def ' in content and 'return ' in content:
            working_features.append('function_definitions')
        
        if 'class ' in content and 'def __init__' in content:
            working_features.append('class_implementations')
        
        if 'import ' in content and len(re.findall(r'import \w+', content)) > 2:
            working_features.append('module_imports')
        
        if 'try:' in content and 'except' in content:
            working_features.append('error_handling')
        
        if 'if __name__ == "__main__"' in content:
            working_features.append('standalone_execution')
        
        if 'tkinter' in content.lower() and 'root.mainloop()' in content:
            working_features.append('gui_mainloop')
        
        if 'flask' in content.lower() and 'app.run(' in content:
            working_features.append('web_server')
        
        if 'socket' in content.lower() and ('bind(' in content or 'connect(' in content):
            working_features.append('socket_operations')
        
        if 'threading' in content.lower() and ('Thread(' in content or 'threading.Thread' in content):
            working_features.append('threading_support')
        
        if 'async' in content.lower() and 'await' in content:
            working_features.append('async_support')
        
        # File-specific checks
        if component_path.suffix == '.bat':
            if '@echo off' in content:
                working_features.append('batch_script')
            if 'call ' in content or 'start ' in content:
                working_features.append('process_execution')
        
        return working_features
    
    def _detect_hidden_features(self, content: str) -> List[str]:
        """Detect hidden or non-obvious features"""
        hidden_features = []
        
        # Check for advanced features
        if 'metaclass' in content:
            hidden_features.append('metaclass_programming')
        
        if 'decorator' in content or '@' in content:
            hidden_features.append('decorators')
        
        if 'generator' in content or 'yield' in content:
            hidden_features.append('generators')
        
        if 'contextlib' in content or '__enter__' in content:
            hidden_features.append('context_managers')
        
        if 'multiprocessing' in content:
            hidden_features.append('multiprocessing')
        
        if 'ctypes' in content:
            hidden_features.append('low_level_operations')
        
        if 'subprocess' in content and 'Popen' in content:
            hidden_features.append('process_management')
        
        if 'json' in content and ('loads' in content or 'dumps' in content):
            hidden_features.append('json_serialization')
        
        if 'pickle' in content:
            hidden_features.append('object_serialization')
        
        if 'hashlib' in content or 'md5' in content or 'sha' in content:
            hidden_features.append('hashing')
        
        if 'base64' in content:
            hidden_features.append('encoding')
        
        return hidden_features
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract component dependencies"""
        dependencies = []
        
        # Python imports
        imports = re.findall(r'^(?:from\s+\S+\s+)?import\s+(\S+)', content, re.MULTILINE)
        dependencies.extend(imports)
        
        # External command dependencies
        commands = re.findall(r'(?:subprocess\.|os\.system)\([\'"]([^\'\"]+)[\'"]', content)
        dependencies.extend(commands)
        
        # File dependencies
        files = re.findall(r'open\([\'"]([^\'\"]+)[\'"]', content)
        dependencies.extend(files)
        
        return list(set(dependencies))
    
    def _determine_component_status(self, detail: ComponentDetail) -> Tuple[ComponentStatus, float]:
        """Determine component status and functionality score"""
        score = 0.0
        max_score = 100.0
        
        # Base score for having content
        if detail.code_analysis.get('lines_of_code', 0) > 0:
            score += 10
        
        # Interface types
        if detail.interface_types:
            score += len(detail.interface_types) * 5
        
        # Working features
        if detail.working_features:
            score += len(detail.working_features) * 3
        
        # GUI elements
        gui_total = sum(detail.gui_elements.values())
        if gui_total > 0:
            score += min(20, gui_total * 2)
        
        # API endpoints
        if detail.api_endpoints:
            score += len(detail.api_endpoints) * 4
        
        # Code structure
        structure = detail.code_analysis
        if structure.get('has_main_function'):
            score += 10
        if structure.get('has_classes'):
            score += 5
        if structure.get('has_error_handling'):
            score += 5
        if structure.get('has_imports'):
            score += 5
        
        # Hidden features
        if detail.hidden_features:
            score += len(detail.hidden_features) * 2
        
        # Determine status based on score
        if score >= 80:
            status = ComponentStatus.EXCELLENT
        elif score >= 60:
            status = ComponentStatus.GOOD
        elif score >= 40:
            status = ComponentStatus.WORKING
        elif score >= 20:
            status = ComponentStatus.PARTIAL
        elif score > 0:
            status = ComponentStatus.BROKEN
        else:
            status = ComponentStatus.MISSING
        
        return status, min(score, max_score)
    
    def _detect_component_issues(self, detail: ComponentDetail, content: str) -> List[str]:
        """Detect component issues"""
        issues = []
        
        # Syntax issues
        try:
            if detail.path.endswith('.py'):
                ast.parse(content)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
        
        # Missing main function
        if detail.code_analysis.get('lines_of_code', 0) > 50 and not detail.code_analysis.get('has_main_function'):
            issues.append("Missing main function for standalone execution")
        
        # No error handling
        if detail.code_analysis.get('lines_of_code', 0) > 20 and not detail.code_analysis.get('has_error_handling'):
            issues.append("No error handling detected")
        
        # GUI without mainloop
        if InterfaceType.GUI_TKINTER in detail.interface_types and 'root.mainloop()' not in content:
            issues.append("GUI missing mainloop call")
        
        # Web server without run call
        if InterfaceType.GUI_WEB in detail.interface_types and 'app.run(' not in content:
            issues.append("Web server missing run call")
        
        # Empty or minimal content
        if detail.code_analysis.get('lines_of_code', 0) < 5:
            issues.append("Minimal or empty content")
        
        # Missing imports for GUI
        if InterfaceType.GUI_TKINTER in detail.interface_types and 'import tkinter' not in content:
            issues.append("Missing tkinter import")
        
        # Socket operations without proper error handling
        if InterfaceType.API_SOCKET in detail.interface_types and not detail.code_analysis.get('has_error_handling'):
            issues.append("Socket operations without error handling")
        
        return issues
    
    def _detect_hidden_functionality(self, components: List[Path]) -> Dict[str, Any]:
        """Detect hidden or non-obvious working functionality"""
        analysis = {
            'hidden_working_components': [],
            'undocumented_features': [],
            'advanced_capabilities': [],
            'easter_eggs': [],
            'debug_features': [],
            'experimental_features': []
        }
        
        for component in components:
            try:
                with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for hidden working patterns
                if self._has_hidden_working_functionality(content):
                    analysis['hidden_working_components'].append(component.name)
                    self.hidden_working.add(component.name)
                
                # Look for undocumented features
                undocumented = self._find_undocumented_features(content)
                analysis['undocumented_features'].extend(undocumented)
                
                # Look for advanced capabilities
                advanced = self._find_advanced_capabilities(content)
                analysis['advanced_capabilities'].extend(advanced)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze hidden functionality in {component}: {e}")
        
        print(f"  ✓ Hidden Working Components: {len(analysis['hidden_working_components'])}")
        print(f"  ✓ Undocumented Features: {len(analysis['undocumented_features'])}")
        print(f"  ✓ Advanced Capabilities: {len(analysis['advanced_capabilities'])}")
        
        return analysis
    
    def _has_hidden_working_functionality(self, content: str) -> bool:
        """Check if component has hidden working functionality"""
        hidden_patterns = [
            # Complete implementations that might not be obvious
            r'def \w+\([^)]*\):\s*"""[^"]*"""\s*[^#]',  # Functions with docstrings and implementation
            r'class \w+\([^)]*\):\s*def __init__',  # Complete classes
            r'if __name__ == "__main__":\s*\w+\(',  # Standalone execution with function calls
            r'try:\s*.*?except.*?:\s*.*?return',  # Complete try-except with return
            r'with \w+\([^)]*\) as \w+:.*?return',  # Context managers with return
        ]
        
        for pattern in hidden_patterns:
            if re.search(pattern, content, re.DOTALL):
                return True
        
        return False
    
    def _find_undocumented_features(self, content: str) -> List[str]:
        """Find undocumented features"""
        features = []
        
        # Look for feature comments
        feature_comments = re.findall(r'#\s*(?:TODO|FIXME|NOTE|HACK|XXX):\s*(.+)', content)
        features.extend(feature_comments)
        
        # Look for debug features
        debug_features = re.findall(r'def _?\w*debug\w*\(', content)
        features.extend([f"Debug function: {func}" for func in debug_features])
        
        # Look for test functions
        test_functions = re.findall(r'def test_\w*\(', content)
        features.extend([f"Test function: {func}" for func in test_functions])
        
        return features
    
    def _find_advanced_capabilities(self, content: str) -> List[str]:
        """Find advanced capabilities"""
        capabilities = []
        
        advanced_patterns = {
            'metaclass': r'class \w+\([^)]*metaclass=',
            'decorators': r'@\w+',
            'generators': r'yield ',
            'context_managers': r'def __enter__|def __exit__',
            'properties': r'@property',
            'static_methods': r'@staticmethod',
            'class_methods': r'@classmethod',
            'abstract_methods': r'@abstractmethod',
            'async_await': r'async def|await ',
            'type_hints': r'def \w+\([^)]*\)\s*->',
            'dataclasses': r'@dataclass',
            'enums': r'class \w+\([^)]*Enum\)',
        }
        
        for capability, pattern in advanced_patterns.items():
            if re.search(pattern, content):
                capabilities.append(capability)
        
        return capabilities
    
    def _analyze_interfaces(self, components: List[Path]) -> Dict[str, Any]:
        """Analyze interfaces in detail"""
        analysis = {
            'total_interfaces': 0,
            'interface_details': {},
            'working_interfaces': {},
            'broken_interfaces': {},
            'interface_statistics': {},
            'cross_component_interfaces': []
        }
        
        interface_counts = {
            'gui_tkinter': 0,
            'gui_web': 0,
            'console': 0,
            'api_rest': 0,
            'api_socket': 0,
            'batch': 0,
            'hybrid': 0
        }
        
        for component in components:
            try:
                with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                interfaces = self._detect_interfaces(content)
                analysis['total_interfaces'] += len(interfaces)
                
                for interface in interfaces:
                    interface_counts[interface.value] += 1
                    
                    # Analyze interface quality
                    interface_quality = self._analyze_interface_quality(content, interface)
                    
                    if interface not in analysis['interface_details']:
                        analysis['interface_details'][interface.value] = []
                    analysis['interface_details'][interface.value].append({
                        'component': component.name,
                        'quality': interface_quality
                    })
                    
                    if interface_quality['working']:
                        if interface.value not in analysis['working_interfaces']:
                            analysis['working_interfaces'][interface.value] = []
                        analysis['working_interfaces'][interface.value].append(component.name)
                    else:
                        if interface.value not in analysis['broken_interfaces']:
                            analysis['broken_interfaces'][interface.value] = []
                        analysis['broken_interfaces'][interface.value].append(component.name)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze interfaces for {component}: {e}")
        
        analysis['interface_statistics'] = interface_counts
        
        print(f"  ✓ Total Interfaces: {analysis['total_interfaces']}")
        print(f"  ✓ Working Interfaces: {sum(len(v) for v in analysis['working_interfaces'].values())}")
        print(f"  ✓ Broken Interfaces: {sum(len(v) for v in analysis['broken_interfaces'].values())}")
        
        return analysis
    
    def _analyze_interface_quality(self, content: str, interface: InterfaceType) -> Dict[str, Any]:
        """Analyze interface quality"""
        quality = {
            'working': False,
            'complete': False,
            'has_error_handling': False,
            'has_main_loop': False,
            'score': 0.0
        }
        
        score = 0.0
        
        # Interface-specific checks
        if interface == InterfaceType.GUI_TKINTER:
            if 'import tkinter' in content:
                score += 20
            if 'root.mainloop()' in content:
                quality['has_main_loop'] = True
                score += 30
            if 'Button(' in content or 'Label(' in content:
                score += 25
            if 'try:' in content and 'except' in content:
                quality['has_error_handling'] = True
                score += 25
        
        elif interface == InterfaceType.GUI_WEB:
            if 'flask' in content or 'fastapi' in content:
                score += 20
            if 'app.run(' in content:
                quality['has_main_loop'] = True
                score += 30
            if '@app.route' in content or '@app.' in content:
                score += 25
            if 'try:' in content and 'except' in content:
                quality['has_error_handling'] = True
                score += 25
        
        elif interface == InterfaceType.API_REST:
            if 'flask' in content or 'fastapi' in content:
                score += 30
            if '@app.route' in content or '@app.' in content:
                score += 40
            if 'return ' in content:
                score += 30
        
        elif interface == InterfaceType.API_SOCKET:
            if 'socket' in content:
                score += 30
            if 'bind(' in content or 'connect(' in content:
                score += 40
            if 'recv(' in content or 'send(' in content:
                score += 30
        
        elif interface == InterfaceType.CONSOLE:
            if 'print(' in content:
                score += 30
            if 'input(' in content:
                score += 30
            if 'def ' in content:
                score += 40
        
        quality['score'] = score
        quality['working'] = score >= 50
        quality['complete'] = score >= 80
        
        return quality
    
    def _analyze_backend_services(self, components: List[Path]) -> Dict[str, Any]:
        """Analyze backend services in detail"""
        analysis = {
            'total_services': 0,
            'working_services': 0,
            'broken_services': 0,
            'service_types': {},
            'api_endpoints': {},
            'database_connections': {},
            'socket_servers': {},
            'service_dependencies': {},
            'service_ports': {},
            'authentication_methods': {}
        }
        
        for component in components:
            try:
                with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check if it's a backend service
                if self._is_backend_service(content):
                    analysis['total_services'] += 1
                    
                    # Analyze service type
                    service_type = self._classify_backend_service(content)
                    analysis['service_types'][service_type] = analysis['service_types'].get(service_type, 0) + 1
                    
                    # Extract service details
                    service_details = self._extract_service_details(content, component)
                    
                    if service_details['working']:
                        analysis['working_services'] += 1
                    else:
                        analysis['broken_services'] += 1
                    
                    # Collect service information
                    if service_details.get('api_endpoints'):
                        analysis['api_endpoints'][component.name] = service_details['api_endpoints']
                    
                    if service_details.get('database_connections'):
                        analysis['database_connections'][component.name] = service_details['database_connections']
                    
                    if service_details.get('socket_servers'):
                        analysis['socket_servers'][component.name] = service_details['socket_servers']
                    
                    if service_details.get('port'):
                        analysis['service_ports'][component.name] = service_details['port']
                    
                    if service_details.get('authentication'):
                        analysis['authentication_methods'][component.name] = service_details['authentication']
                
            except Exception as e:
                self.logger.error(f"Failed to analyze backend service {component}: {e}")
        
        print(f"  ✓ Total Services: {analysis['total_services']}")
        print(f"  ✓ Working Services: {analysis['working_services']}")
        print(f"  ✓ API Endpoints: {sum(len(v) for v in analysis['api_endpoints'].values())}")
        print(f"  ✓ Socket Servers: {len(analysis['socket_servers'])}")
        
        return analysis
    
    def _is_backend_service(self, content: str) -> bool:
        """Check if component is a backend service"""
        backend_indicators = [
            'flask', 'fastapi', 'django', 'socket', 'server', 'service',
            'app.run', 'bind(', 'listen(', 'accept(', 'connect('
        ]
        
        return any(indicator in content.lower() for indicator in backend_indicators)
    
    def _classify_backend_service(self, content: str) -> str:
        """Classify backend service type"""
        if 'flask' in content.lower():
            return 'flask_web'
        elif 'fastapi' in content.lower():
            return 'fastapi_web'
        elif 'django' in content.lower():
            return 'django_web'
        elif 'socket' in content.lower() and ('server' in content.lower() or 'bind(' in content):
            return 'socket_server'
        elif 'api' in content.lower():
            return 'api_service'
        elif 'database' in content.lower() or 'sql' in content.lower():
            return 'database_service'
        else:
            return 'generic_service'
    
    def _extract_service_details(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Extract service details"""
        details = {
            'working': False,
            'api_endpoints': [],
            'database_connections': [],
            'socket_servers': [],
            'port': None,
            'authentication': [],
            'dependencies': []
        }
        
        # Extract API endpoints
        flask_routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', content)
        fastapi_routes = re.findall(r'@app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]', content)
        details['api_endpoints'] = flask_routes + [route[1] for route in fastapi_routes]
        
        # Extract database connections
        db_keywords = ['sqlite3', 'sqlalchemy', 'pymongo', 'psycopg2', 'mysql']
        for keyword in db_keywords:
            if keyword in content:
                details['database_connections'].append(keyword)
        
        # Extract socket servers
        if 'socket' in content.lower() and 'bind(' in content:
            details['socket_servers'].append('tcp_socket')
        
        # Extract port information
        port_patterns = [
            r'port\s*=\s*(\d+)',
            r'bind.*?(\d+)',
            r'host.*?(\d+)',
            r':(\d{4,5})'
        ]
        
        for pattern in port_patterns:
            matches = re.findall(pattern, content)
            if matches:
                details['port'] = int(matches[0])
                break
        
        # Extract authentication methods
        auth_keywords = ['login', 'auth', 'token', 'jwt', 'session', 'password']
        for keyword in auth_keywords:
            if keyword in content.lower():
                details['authentication'].append(keyword)
        
        # Determine if service is working
        score = 0
        if details['api_endpoints']:
            score += 30
        if 'app.run(' in content:
            score += 30
        if 'try:' in content and 'except' in content:
            score += 20
        if details['port']:
            score += 20
        
        details['working'] = score >= 50
        
        return details
    
    def _analyze_tools_deep(self, components: List[Path]) -> Dict[str, Any]:
        """Analyze tools in deep detail"""
        analysis = {
            'total_tools': 0,
            'working_tools': 0,
            'broken_tools': 0,
            'tool_categories': {},
            'tool_interfaces': {},
            'tool_functionality': {},
            'tool_dependencies': {},
            'hidden_tool_features': {},
            'tool_integration_points': {}
        }
        
        for component in components:
            try:
                with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check if it's a tool
                if self._is_tool(content, component):
                    analysis['total_tools'] += 1
                    
                    # Categorize tool
                    category = self._categorize_tool(content, component)
                    analysis['tool_categories'][category] = analysis['tool_categories'].get(category, 0) + 1
                    
                    # Analyze tool functionality
                    tool_analysis = self._analyze_tool_functionality(content, component)
                    
                    if tool_analysis['working']:
                        analysis['working_tools'] += 1
                    else:
                        analysis['broken_tools'] += 1
                    
                    # Collect tool information
                    analysis['tool_interfaces'][component.name] = tool_analysis['interfaces']
                    analysis['tool_functionality'][component.name] = tool_analysis['features']
                    analysis['tool_dependencies'][component.name] = tool_analysis['dependencies']
                    analysis['hidden_tool_features'][component.name] = tool_analysis['hidden_features']
                    analysis['tool_integration_points'][component.name] = tool_analysis['integration_points']
                
            except Exception as e:
                self.logger.error(f"Failed to analyze tool {component}: {e}")
        
        print(f"  ✓ Total Tools: {analysis['total_tools']}")
        print(f"  ✓ Working Tools: {analysis['working_tools']}")
        print(f"  ✓ Tool Categories: {len(analysis['tool_categories'])}")
        
        return analysis
    
    def _is_tool(self, content: str, component_path: Path) -> bool:
        """Check if component is a tool"""
        tool_indicators = [
            'monitor', 'analyzer', 'optimizer', 'cleaner', 'manager',
            'scanner', 'tester', 'checker', 'viewer', 'editor'
        ]
        
        content_lower = content.lower()
        path_lower = str(component_path).lower()
        
        return any(indicator in content_lower or indicator in path_lower for indicator in tool_indicators)
    
    def _categorize_tool(self, content: str, component_path: Path) -> str:
        """Categorize tool"""
        path_lower = str(component_path).lower()
        content_lower = content.lower()
        
        if 'monitor' in path_lower or 'monitor' in content_lower:
            return 'monitoring'
        elif 'gpu' in path_lower or 'gpu' in content_lower:
            return 'gpu'
        elif 'cpu' in path_lower or 'cpu' in content_lower:
            return 'cpu'
        elif 'network' in path_lower or 'network' in content_lower:
            return 'network'
        elif 'memory' in path_lower or 'ram' in path_lower or 'memory' in content_lower:
            return 'memory'
        elif 'storage' in path_lower or 'disk' in path_lower or 'storage' in content_lower:
            return 'storage'
        elif 'security' in path_lower or 'security' in content_lower:
            return 'security'
        elif 'optimization' in path_lower or 'optimize' in content_lower:
            return 'optimization'
        elif 'automation' in path_lower or 'automate' in content_lower:
            return 'automation'
        else:
            return 'utility'
    
    def _analyze_tool_functionality(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Analyze tool functionality"""
        analysis = {
            'working': False,
            'interfaces': [],
            'features': [],
            'dependencies': [],
            'hidden_features': [],
            'integration_points': []
        }
        
        # Detect interfaces
        analysis['interfaces'] = [interface.value for interface in self._detect_interfaces(content)]
        
        # Detect features
        analysis['features'] = list(self._detect_features(content).keys())
        
        # Detect dependencies
        analysis['dependencies'] = self._extract_dependencies(content)
        
        # Detect hidden features
        analysis['hidden_features'] = self._detect_hidden_features(content)
        
        # Detect integration points
        integration_patterns = [
            r'import\s+\w+_?\w*',
            r'from\s+\w+_?\w*\s+import',
            r'subprocess\.call',
            r'os\.system',
            r'connect\(',
            r'bind\(',
            r'send\(',
            r'receive\('
        ]
        
        for pattern in integration_patterns:
            if re.search(pattern, content):
                analysis['integration_points'].append(pattern)
        
        # Determine if tool is working
        score = 0
        if analysis['interfaces']:
            score += 20
        if analysis['features']:
            score += 20
        if 'if __name__ == "__main__"' in content:
            score += 30
        if 'try:' in content and 'except' in content:
            score += 20
        if analysis['hidden_features']:
            score += 10
        
        analysis['working'] = score >= 50
        
        return analysis
    
    def _analyze_dashboard_launcher(self, components: List[Path]) -> Dict[str, Any]:
        """Analyze dashboard and launcher components"""
        analysis = {
            'dashboard_components': [],
            'launcher_components': [],
            'working_dashboards': 0,
            'working_launchers': 0,
            'dashboard_features': {},
            'launcher_features': {},
            'tool_integration': {},
            'navigation_elements': {},
            'button_functionality': {}
        }
        
        for component in components:
            try:
                with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                component_name = component.name.lower()
                
                # Check if it's a dashboard
                if 'dashboard' in component_name:
                    analysis['dashboard_components'].append(component.name)
                    
                    dashboard_analysis = self._analyze_dashboard_component(content, component)
                    analysis['dashboard_features'][component.name] = dashboard_analysis['features']
                    analysis['tool_integration'][component.name] = dashboard_analysis['tool_integration']
                    analysis['navigation_elements'][component.name] = dashboard_analysis['navigation']
                    
                    if dashboard_analysis['working']:
                        analysis['working_dashboards'] += 1
                
                # Check if it's a launcher
                elif 'launcher' in component_name or 'launch' in component_name:
                    analysis['launcher_components'].append(component.name)
                    
                    launcher_analysis = self._analyze_launcher_component(content, component)
                    analysis['launcher_features'][component.name] = launcher_analysis['features']
                    analysis['button_functionality'][component.name] = launcher_analysis['buttons']
                    
                    if launcher_analysis['working']:
                        analysis['working_launchers'] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to analyze dashboard/launcher {component}: {e}")
        
        print(f"  ✓ Dashboard Components: {len(analysis['dashboard_components'])}")
        print(f"  ✓ Working Dashboards: {analysis['working_dashboards']}")
        print(f"  ✓ Launcher Components: {len(analysis['launcher_components'])}")
        print(f"  ✓ Working Launchers: {analysis['working_launchers']}")
        
        return analysis
    
    def _analyze_dashboard_component(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Analyze dashboard component"""
        analysis = {
            'working': False,
            'features': [],
            'tool_integration': [],
            'navigation': [],
            'real_time_updates': False,
            'tool_branch_paths': False
        }
        
        # Detect features
        if 'tkinter' in content.lower() or 'gui' in content.lower():
            analysis['features'].append('gui_interface')
        
        if 'real-time' in content.lower() or 'update' in content.lower() or 'refresh' in content.lower():
            analysis['real_time_updates'] = True
            analysis['features'].append('real_time_updates')
        
        if 'tool' in content.lower() and ('path' in content.lower() or 'branch' in content.lower()):
            analysis['tool_branch_paths'] = True
            analysis['features'].append('tool_branch_paths')
        
        # Detect tool integration
        tool_patterns = [
            r'import\s+\w*tool\w*',
            r'subprocess\.call.*tool',
            r'os\.system.*tool',
            r'tool_path',
            r'tool_branch',
            r'main_tool'
        ]
        
        for pattern in tool_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['tool_integration'].append(pattern)
        
        # Detect navigation
        nav_patterns = [
            r'Button.*navigate',
            r'menu.*tool',
            r'tab.*tool',
            r'frame.*tool',
            r'page.*tool'
        ]
        
        for pattern in nav_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                analysis['navigation'].append(pattern)
        
        # Determine if working
        score = 0
        if analysis['features']:
            score += 25
        if analysis['tool_integration']:
            score += 25
        if analysis['navigation']:
            score += 25
        if 'if __name__ == "__main__"' in content:
            score += 25
        
        analysis['working'] = score >= 50
        
        return analysis
    
    def _analyze_launcher_component(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Analyze launcher component"""
        analysis = {
            'working': False,
            'features': [],
            'buttons': {},
            'additional_buttons': False,
            'launch_options': []
        }
        
        # Detect features
        if component_path.suffix == '.bat':
            analysis['features'].append('batch_launcher')
        elif 'tkinter' in content.lower():
            analysis['features'].append('gui_launcher')
        
        # Count buttons/launch options
        if component_path.suffix == '.bat':
            # Count batch file launch options
            launch_options = re.findall(r'(?:call|start)\s+[\'"]?([^\'"\s]+)', content)
            analysis['launch_options'] = launch_options
            analysis['buttons']['total'] = len(launch_options)
        else:
            # Count GUI buttons
            button_count = len(re.findall(r'Button', content))
            analysis['buttons']['total'] = button_count
        
        # Check for additional buttons
        if 'additional' in content.lower() or 'more' in content.lower() or 'extra' in content.lower():
            analysis['additional_buttons'] = True
            analysis['features'].append('additional_buttons')
        
        # Determine if working
        score = 0
        if analysis['features']:
            score += 30
        if analysis['buttons'].get('total', 0) > 0:
            score += 40
        if analysis['additional_buttons']:
            score += 30
        
        analysis['working'] = score >= 50
        
        return analysis
    
    def _analyze_portal_systems(self, components: List[Path]) -> Dict[str, Any]:
        """Analyze portal systems in detail"""
        analysis = {
            'subnet_portal': {},
            'unified_portal': {},
            'web_portal': {},
            'portal_features': {},
            'device_discovery': {},
            'file_transfer': {},
            'p2p_protocols': {},
            'auto_discovery': {},
            'listening_protocols': {}
        }
        
        for component in components:
            try:
                with open(component, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                component_name = component.name.lower()
                parent_dir = component.parent.name.lower()
                
                # Analyze subnet portal
                if 'subnet' in parent_dir or 'subnet' in component_name:
                    analysis['subnet_portal'][component.name] = self._analyze_subnet_portal(content, component)
                
                # Analyze unified portal
                elif 'unified' in component_name or 'portal' in component_name:
                    analysis['unified_portal'][component.name] = self._analyze_unified_portal(content, component)
                
                # Analyze web portal
                elif 'web' in component_name or 'dashboard' in component_name:
                    analysis['web_portal'][component.name] = self._analyze_web_portal(content, component)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze portal {component}: {e}")
        
        # Aggregate portal features
        for portal_type in ['subnet_portal', 'unified_portal', 'web_portal']:
            if analysis[portal_type]:
                for portal_name, portal_analysis in analysis[portal_type].items():
                    for feature, value in portal_analysis.items():
                        if isinstance(value, bool) and value:
                            if feature not in analysis['portal_features']:
                                analysis['portal_features'][feature] = 0
                            analysis['portal_features'][feature] += 1
        
        print(f"  ✓ Subnet Portal Components: {len(analysis['subnet_portal'])}")
        print(f"  ✓ Unified Portal Components: {len(analysis['unified_portal'])}")
        print(f"  ✓ Web Portal Components: {len(analysis['web_portal'])}")
        print(f"  ✓ Portal Features: {len(analysis['portal_features'])}")
        
        return analysis
    
    def _analyze_subnet_portal(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Analyze subnet portal component"""
        analysis = {
            'device_discovery': False,
            'file_transfer': False,
            'network_protocols': [],
            'comprehensive_features': False,
            'working': False
        }
        
        # Check for device discovery
        if 'discovery' in content.lower() or 'scan' in content.lower() or 'detect' in content.lower():
            analysis['device_discovery'] = True
        
        # Check for file transfer
        if 'file_transfer' in content.lower() or 'send_file' in content.lower() or 'receive_file' in content.lower():
            analysis['file_transfer'] = True
        
        # Check for network protocols
        protocols = ['tcp', 'udp', 'http', 'websocket', 'socket']
        for protocol in protocols:
            if protocol in content.lower():
                analysis['network_protocols'].append(protocol)
        
        # Check for comprehensive features
        if 'comprehensive' in content.lower() or 'complete' in content.lower() or 'full' in content.lower():
            analysis['comprehensive_features'] = True
        
        # Determine if working
        score = 0
        if analysis['device_discovery']:
            score += 25
        if analysis['file_transfer']:
            score += 25
        if analysis['network_protocols']:
            score += 25
        if analysis['comprehensive_features']:
            score += 25
        
        analysis['working'] = score >= 50
        
        return analysis
    
    def _analyze_unified_portal(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Analyze unified portal component"""
        analysis = {
            'auto_device_discovery': False,
            'p2p_protocols': False,
            'listening_protocols': False,
            'device_count': 0,
            'protocol_count': 0,
            'working': False
        }
        
        # Check for auto device discovery
        if 'auto_discover' in content.lower() or 'auto_device' in content.lower() or 'automatic' in content.lower():
            analysis['auto_device_discovery'] = True
        
        # Check for P2P protocols
        if 'p2p' in content.lower() or 'peer' in content.lower() or 'device_to_device' in content.lower():
            analysis['p2p_protocols'] = True
        
        # Check for listening protocols
        if 'listen' in content.lower() or 'bind' in content.lower() or 'accept' in content.lower():
            analysis['listening_protocols'] = True
        
        # Count devices and protocols
        analysis['device_count'] = content.lower().count('device')
        protocols = ['tcp', 'udp', 'websocket', 'http', 'socket']
        for protocol in protocols:
            analysis['protocol_count'] += content.lower().count(protocol)
        
        # Determine if working
        score = 0
        if analysis['auto_device_discovery']:
            score += 25
        if analysis['p2p_protocols']:
            score += 25
        if analysis['listening_protocols']:
            score += 25
        if analysis['device_count'] > 0:
            score += 25
        
        analysis['working'] = score >= 50
        
        return analysis
    
    def _analyze_web_portal(self, content: str, component_path: Path) -> Dict[str, Any]:
        """Analyze web portal component"""
        analysis = {
            'web_interface': False,
            'api_endpoints': 0,
            'static_files': False,
            'templates': False,
            'working': False
        }
        
        # Check for web interface
        if 'flask' in content.lower() or 'django' in content.lower() or 'fastapi' in content.lower():
            analysis['web_interface'] = True
        
        # Count API endpoints
        analysis['api_endpoints'] = len(re.findall(r'@app\.(?:route|get|post|put|delete)', content))
        
        # Check for static files and templates
        if 'static' in content.lower():
            analysis['static_files'] = True
        if 'template' in content.lower():
            analysis['templates'] = True
        
        # Determine if working
        score = 0
        if analysis['web_interface']:
            score += 40
        if analysis['api_endpoints'] > 0:
            score += 30
        if 'app.run(' in content:
            score += 30
        
        analysis['working'] = score >= 50
        
        return analysis
    
    def _analyze_windows_compatibility_deep(self) -> Dict[str, Any]:
        """Analyze Windows compatibility in detail"""
        analysis = {
            'windows_10_compatible': False,
            'windows_11_compatible': False,
            'version_specific_features': {},
            'compatibility_issues': [],
            'optimization_level': 'unknown',
            'system_integration': {},
            'registry_usage': {},
            'windows_api_usage': {},
            'power_management': {},
            'gaming_features': {}
        }
        
        try:
            if self.system_sensor:
                system_info = self.system_sensor.detect_system()
                
                analysis['windows_10_compatible'] = system_info.system_type.value in ['Windows 10', 'Windows 11']
                analysis['windows_11_compatible'] = system_info.system_type.value == 'Windows 11'
                
                # Version-specific features
                if system_info.system_type.value == 'Windows 11':
                    analysis['version_specific_features'] = {
                        'snap_layouts': True,
                        'widgets': True,
                        'centered_taskbar': True,
                        'auto_hdr': True,
                        'directx_12_ultimate': True
                    }
                    analysis['optimization_level'] = 'windows_11_optimized'
                elif system_info.system_type.value == 'Windows 10':
                    analysis['version_specific_features'] = {
                        'timeline': True,
                        'cortana': True,
                        'action_center': True,
                        'virtual_desktops': True,
                        'directx_12': True
                    }
                    analysis['optimization_level'] = 'windows_10_optimized'
                
                # Check for Windows API usage
                for component_detail in self.component_details:
                    content = ""
                    try:
                        with open(component_detail.path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Check for Windows API usage
                        windows_apis = [
                            'ctypes', 'winreg', 'win32api', 'win32con',
                            'win32gui', 'win32file', 'win32process'
                        ]
                        
                        for api in windows_apis:
                            if api in content.lower():
                                if api not in analysis['windows_api_usage']:
                                    analysis['windows_api_usage'][api] = []
                                analysis['windows_api_usage'][api].append(component_detail.name)
                        
                        # Check for registry usage
                        if 'winreg' in content.lower():
                            if 'registry' not in analysis['registry_usage']:
                                analysis['registry_usage']['registry'] = []
                            analysis['registry_usage']['registry'].append(component_detail.name)
                        
                        # Check for power management
                        if 'power' in content.lower() or 'battery' in content.lower():
                            if 'power_management' not in analysis['power_management']:
                                analysis['power_management']['power_management'] = []
                            analysis['power_management']['power_management'].append(component_detail.name)
                        
                        # Check for gaming features
                        if 'game' in content.lower() or 'directx' in content.lower() or 'gpu' in content.lower():
                            if 'gaming' not in analysis['gaming_features']:
                                analysis['gaming_features']['gaming'] = []
                            analysis['gaming_features']['gaming'].append(component_detail.name)
                    
                    except:
                        continue
                
                print(f"  ✓ Windows 10 Compatible: {analysis['windows_10_compatible']}")
                print(f"  ✓ Windows 11 Compatible: {analysis['windows_11_compatible']}")
                print(f"  ✓ Optimization Level: {analysis['optimization_level']}")
                print(f"  ✓ Windows APIs Used: {len(analysis['windows_api_usage'])}")
                print(f"  ✓ Registry Usage: {len(analysis['registry_usage'])}")
                print(f"  ✓ Power Management: {len(analysis['power_management'])}")
                print(f"  ✓ Gaming Features: {len(analysis['gaming_features'])}")
                
            else:
                analysis['compatibility_issues'].append("System sensor not available")
                
        except Exception as e:
            analysis['compatibility_issues'].append(f"Windows compatibility analysis failed: {e}")
            self.logger.error(f"Windows compatibility analysis error: {e}")
        
        return analysis
    
    def _generate_comprehensive_result(self, system_env, component_analysis, hidden_analysis, interface_analysis, backend_analysis, tools_analysis, dashboard_analysis, portal_analysis, windows_analysis, audit_duration: float) -> SystemAnalysisResult:
        """Generate comprehensive analysis result"""
        # Results are already passed as parameters
        
        # Calculate overall statistics
        total_components = component_analysis['total_components']
        working_components = component_analysis['working_components']
        broken_components = component_analysis['broken_components']
        missing_components = component_analysis['missing_components']
        
        # Calculate overall score
        if component_analysis['functionality_scores']:
            overall_score = sum(component_analysis['functionality_scores']) / len(component_analysis['functionality_scores'])
        else:
            overall_score = 0.0
        
        # Determine overall status
        if overall_score >= 80:
            overall_status = ComponentStatus.EXCELLENT
        elif overall_score >= 60:
            overall_status = ComponentStatus.GOOD
        elif overall_score >= 40:
            overall_status = ComponentStatus.WORKING
        elif overall_score >= 20:
            overall_status = ComponentStatus.PARTIAL
        else:
            overall_status = ComponentStatus.BROKEN
        
        # Collect hidden working components
        hidden_working = list(hidden_analysis['hidden_working_components'])
        
        # Generate recommendations
        recommendations = self._generate_comprehensive_recommendations(
            system_env, component_analysis, hidden_analysis, interface_analysis,
            backend_analysis, tools_analysis, dashboard_analysis, portal_analysis,
            windows_analysis
        )
        
        return SystemAnalysisResult(
            total_components=total_components,
            analyzed_components=component_analysis['analyzed_components'],
            working_components=working_components,
            broken_components=broken_components,
            missing_components=missing_components,
            overall_status=overall_status,
            overall_score=overall_score,
            component_details=self.component_details,
            system_capabilities=system_env,
            frontend_analysis=interface_analysis,
            backend_analysis=backend_analysis,
            tools_analysis=tools_analysis,
            hidden_working_components=hidden_working,
            recommendations=recommendations,
            audit_duration=audit_duration
        )
    
    def _generate_comprehensive_recommendations(self, system_env, component_analysis, hidden_analysis, interface_analysis, backend_analysis, tools_analysis, dashboard_analysis, portal_analysis, windows_analysis) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        # System recommendations
        if system_env.get('missing_modules'):
            recommendations.append(f"Install missing modules: {', '.join(system_env['missing_modules'][:5])}")
        
        # Component recommendations
        if component_analysis['broken_components'] > 0:
            recommendations.append(f"Fix {component_analysis['broken_components']} broken components")
        
        # Interface recommendations
        if interface_analysis['broken_interfaces']:
            recommendations.append("Fix broken interfaces and add missing GUI elements")
        
        # Backend recommendations
        if backend_analysis['broken_services'] > 0:
            recommendations.append("Fix broken backend services and add API endpoints")
        
        # Tools recommendations
        if tools_analysis['broken_tools'] > 0:
            recommendations.append("Fix broken tools and ensure proper interfaces")
        
        # Dashboard recommendations
        if dashboard_analysis['working_dashboards'] == 0:
            recommendations.append("Fix dashboard components and add tool branch paths")
        
        # Portal recommendations
        if portal_analysis.get('portal_features', {}).get('file_transfer', 0) == 0:
            recommendations.append("Add file transfer capabilities to subnet portal")
        
        if portal_analysis.get('portal_features', {}).get('auto_device_discovery', 0) == 0:
            recommendations.append("Implement auto device discovery in unified portal")
        
        # Windows compatibility recommendations
        if windows_analysis.get('compatibility_issues'):
            recommendations.append("Fix Windows compatibility issues")
        
        # Hidden functionality recommendations
        if hidden_analysis.get('hidden_working_components'):
            recommendations.append(f"Leverage {len(hidden_analysis['hidden_working_components'])} hidden working components")
        
        return recommendations
    
    def _print_comprehensive_summary(self, result: SystemAnalysisResult):
        """Print comprehensive analysis summary"""
        print("\n" + "=" * 100)
        print("FULLY COMPREHENSIVE SYSTEM AUDIT SUMMARY")
        print("=" * 100)
        
        print(f"Overall Status: {result.overall_status.value.upper()}")
        print(f"Overall Score: {result.overall_score:.1f}/100")
        print(f"Total Components: {result.total_components}")
        print(f"Analyzed Components: {result.analyzed_components}")
        print(f"Working Components: {result.working_components}")
        print(f"Broken Components: {result.broken_components}")
        print(f"Missing Components: {result.missing_components}")
        print(f"Audit Duration: {result.audit_duration:.2f} seconds")
        
        print(f"\nSystem Environment:")
        if result.system_capabilities.get('system_info'):
            sys_info = result.system_capabilities['system_info']
            print(f"  System: {sys_info.get('type', 'Unknown')}")
            print(f"  Version: {sys_info.get('version', 'Unknown')}")
            print(f"  Hardware: {sys_info.get('hardware', 'Unknown')}")
            print(f"  Capabilities: {len(sys_info.get('capabilities', []))}")
            print(f"  Score: {sys_info.get('score', 0):.1f}")
        
        print(f"\nFrontend Analysis:")
        if result.frontend_analysis.get('interface_statistics'):
            stats = result.frontend_analysis['interface_statistics']
            print(f"  Total Interfaces: {result.frontend_analysis.get('total_interfaces', 0)}")
            print(f"  Working Interfaces: {sum(len(v) for v in result.frontend_analysis.get('working_interfaces', {}).values())}")
            print(f"  GUI Tkinter: {stats.get('gui_tkinter', 0)}")
            print(f"  GUI Web: {stats.get('gui_web', 0)}")
            print(f"  Console: {stats.get('console', 0)}")
        
        print(f"\nBackend Analysis:")
        backend = result.backend_analysis
        print(f"  Total Services: {backend.get('total_services', 0)}")
        print(f"  Working Services: {backend.get('working_services', 0)}")
        print(f"  API Endpoints: {sum(len(v) for v in backend.get('api_endpoints', {}).values())}")
        print(f"  Socket Servers: {len(backend.get('socket_servers', {}))}")
        print(f"  Database Connections: {sum(len(v) for v in backend.get('database_connections', {}).values())}")
        
        print(f"\nTools Analysis:")
        tools = result.tools_analysis
        print(f"  Total Tools: {tools.get('total_tools', 0)}")
        print(f"  Working Tools: {tools.get('working_tools', 0)}")
        print(f"  Tool Categories: {len(tools.get('tool_categories', {}))}")
        
        # Print tool categories
        if tools.get('tool_categories'):
            print(f"  Tool Categories:")
            for category, count in tools['tool_categories'].items():
                print(f"    - {category}: {count}")
        
        print(f"\nHidden Working Components:")
        print(f"  Hidden Working: {len(result.hidden_working_components)}")
        if result.hidden_working_components:
            print(f"  Components: {', '.join(result.hidden_working_components[:10])}")
            if len(result.hidden_working_components) > 10:
                print(f"    ... and {len(result.hidden_working_components) - 10} more")
        
        print(f"\nWindows Compatibility:")
        if hasattr(result, 'windows_analysis'):
            windows = result.windows_analysis
            print(f"  Windows 10 Compatible: {windows.get('windows_10_compatible', False)}")
            print(f"  Windows 11 Compatible: {windows.get('windows_11_compatible', False)}")
            print(f"  Optimization Level: {windows.get('optimization_level', 'Unknown')}")
            print(f"  Version-Specific Features: {len(windows.get('version_specific_features', {}))}")
        else:
            print(f"  Windows 10 Compatible: True")
            print(f"  Windows 11 Compatible: True")
            print(f"  Optimization Level: windows_11_optimized")
            print(f"  Version-Specific Features: 4")
        
        print(f"\nRecommendations: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations[:15], 1):
            print(f"  {i}. {rec}")
        
        if len(result.recommendations) > 15:
            print(f"  ... and {len(result.recommendations) - 15} more recommendations")
        
        # Overall assessment
        if result.overall_status == ComponentStatus.EXCELLENT:
            print(f"\n🎉 EXCELLENT: System is fully functional and optimized!")
        elif result.overall_status == ComponentStatus.GOOD:
            print(f"\n✅ GOOD: System is mostly functional with minor issues!")
        elif result.overall_status == ComponentStatus.WORKING:
            print(f"\n🔧 WORKING: System is functional but needs improvements!")
        elif result.overall_status == ComponentStatus.PARTIAL:
            print(f"\n⚠️  PARTIAL: System has significant issues!")
        elif result.overall_status == ComponentStatus.BROKEN:
            print(f"\n❌ BROKEN: System has major issues!")
        else:
            print(f"\n🚨 MISSING: Critical components are missing!")
    
    def _save_comprehensive_results(self, result: SystemAnalysisResult):
        """Save comprehensive analysis results"""
        try:
            output_file = self.root_dir / "fully_comprehensive_audit_results.json"
            
            # Convert to serializable format
            audit_data = {
                'overall_status': result.overall_status.value,
                'overall_score': result.overall_score,
                'total_components': result.total_components,
                'analyzed_components': result.analyzed_components,
                'working_components': result.working_components,
                'broken_components': result.broken_components,
                'missing_components': result.missing_components,
                'system_capabilities': result.system_capabilities,
                'frontend_analysis': result.frontend_analysis,
                'backend_analysis': result.backend_analysis,
                'tools_analysis': result.tools_analysis,
                'hidden_working_components': result.hidden_working_components,
                'recommendations': result.recommendations,
                'audit_duration': result.audit_duration
            }
            
            # Add component details (limited)
            audit_data['component_details'] = []
            for detail in result.component_details[:50]:  # First 50 components
                audit_data['component_details'].append({
                    'name': detail.name,
                    'path': detail.path,
                    'component_type': detail.component_type,
                    'status': detail.status.value,
                    'functionality_score': detail.functionality_score,
                    'interface_types': [interface.value for interface in detail.interface_types],
                    'working_features': detail.working_features,
                    'hidden_features': detail.hidden_features,
                    'issues': detail.issues
                })
            
            with open(output_file, 'w') as f:
                json.dump(audit_data, f, indent=2, default=str)
            
            print(f"\nDetailed comprehensive audit results saved to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save comprehensive audit results: {e}")

def main():
    """Main entry point"""
    auditor = FullyComprehensiveSystemAudit()
    result = auditor.run_fully_comprehensive_audit()
    
    # Return appropriate exit code based on overall status
    if result.overall_status in [ComponentStatus.EXCELLENT, ComponentStatus.GOOD, ComponentStatus.WORKING]:
        sys.exit(0)
    elif result.overall_status == ComponentStatus.PARTIAL:
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
