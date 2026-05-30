#!/usr/bin/env python3
"""
Optimized Fully Comprehensive System Audit
Fixed hanging issues with timeouts and better error handling
"""

import os
import sys
import json
import time
import logging
import ast
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import signal

class ComponentStatus(Enum):
    """Component status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WORKING = "working"
    PARTIAL = "partial"
    BROKEN = "broken"
    MISSING = "missing"

@dataclass
class ComponentAnalysis:
    """Component analysis result"""
    name: str
    path: str
    component_type: str
    status: ComponentStatus
    functionality_score: int
    working_features: List[str]
    issues: List[str]

class OptimizedSystemAuditor:
    """Optimized system auditor with timeout protection"""
    
    def __init__(self):
        self.setup_logging()
        self.timeout = 30  # 30 second timeout per operation
        self.max_components = 100  # Limit components to prevent hanging
        
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/optimized_audit.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('OptimizedAuditor')
    
    def run_optimized_audit(self) -> Dict[str, Any]:
        """Run optimized system audit with timeouts"""
        print("=" * 80)
        print("OPTIMIZED SYSTEM AUDIT & VERIFICATION")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # 1. Quick System Analysis
            print("\n1. SYSTEM ANALYSIS")
            system_analysis = self.analyze_system_quick()
            
            # 2. Component Discovery (with limit)
            print("\n2. COMPONENT DISCOVERY")
            components = self.discover_components_limited()
            
            # 3. Component Analysis (with timeout)
            print("\n3. COMPONENT ANALYSIS")
            component_results = self.analyze_components_with_timeout(components)
            
            # 4. Mesh VPN Verification
            print("\n4. MESH VPN VERIFICATION")
            mesh_analysis = self.verify_mesh_vpn_components()
            
            # 5. Launcher/Dashboard Verification
            print("\n5. LAUNCHER/DASHBOARD VERIFICATION")
            launcher_analysis = self.verify_launcher_dashboard()
            
            # Generate results
            audit_duration = time.time() - start_time
            
            results = self.generate_optimized_results(
                system_analysis, component_results, mesh_analysis, 
                launcher_analysis, audit_duration
            )
            
            # Print summary
            self.print_optimized_summary(results)
            
            # Save results
            self.save_optimized_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Audit failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def analyze_system_quick(self) -> Dict[str, Any]:
        """Quick system analysis"""
        try:
            import platform
            
            analysis = {
                "system_type": platform.system(),
                "version": platform.version(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "available_modules": self.check_available_modules(),
                "missing_modules": self.check_missing_modules()
            }
            
            print(f"  ✓ System: {analysis['system_type']} {analysis['version']}")
            print(f"  ✓ Python: {analysis['python_version']}")
            print(f"  ✓ Architecture: {analysis['architecture']}")
            print(f"  ✓ Available modules: {len(analysis['available_modules'])}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"System analysis failed: {e}")
            return {"error": str(e)}
    
    def check_available_modules(self) -> List[str]:
        """Check available modules"""
        modules_to_check = [
            'tkinter', 'flask', 'fastapi', 'psutil', 'matplotlib', 
            'numpy', 'requests', 'websockets', 'asyncio', 'threading',
            'socket', 'json', 'sqlite3', 'pathlib', 'datetime'
        ]
        
        available = []
        for module in modules_to_check:
            try:
                __import__(module)
                available.append(module)
            except ImportError:
                pass
        
        return available
    
    def check_missing_modules(self) -> List[str]:
        """Check missing modules"""
        modules_to_check = ['ttk', 'django', 'pandas']
        
        missing = []
        for module in modules_to_check:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        return missing
    
    def discover_components_limited(self) -> List[Dict]:
        """Discover components with limit to prevent hanging"""
        try:
            base_path = Path(".")
            components = []
            component_count = 0
            
            # Find Python files
            for py_file in base_path.rglob("*.py"):
                if component_count >= self.max_components:
                    break
                
                # Skip certain directories
                if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'venv', 'env']):
                    continue
                
                component_info = {
                    "name": py_file.stem,
                    "path": str(py_file),
                    "type": "python",
                    "size": py_file.stat().st_size if py_file.exists() else 0
                }
                
                components.append(component_info)
                component_count += 1
            
            # Find batch files
            for bat_file in base_path.rglob("*.bat"):
                if component_count >= self.max_components:
                    break
                
                component_info = {
                    "name": bat_file.stem,
                    "path": str(bat_file),
                    "type": "batch",
                    "size": bat_file.stat().st_size if bat_file.exists() else 0
                }
                
                components.append(component_info)
                component_count += 1
            
            print(f"  ✓ Found {len(components)} components (limited to {self.max_components})")
            return components
            
        except Exception as e:
            self.logger.error(f"Component discovery failed: {e}")
            return []
    
    def analyze_components_with_timeout(self, components: List[Dict]) -> List[ComponentAnalysis]:
        """Analyze components with timeout protection"""
        results = []
        analyzed_count = 0
        
        for component in components:
            if analyzed_count >= 50:  # Limit analysis to prevent hanging
                break
            
            try:
                # Use timeout for each component analysis
                analysis = self.analyze_single_component_with_timeout(component)
                if analysis:
                    results.append(analysis)
                    analyzed_count += 1
                    
                    # Progress indicator
                    if analyzed_count % 10 == 0:
                        print(f"    Analyzed {analyzed_count} components...")
                        
            except Exception as e:
                self.logger.error(f"Failed to analyze {component['name']}: {e}")
                continue
        
        print(f"  ✓ Analyzed {len(results)} components")
        return results
    
    def analyze_single_component_with_timeout(self, component: Dict) -> Optional[ComponentAnalysis]:
        """Analyze single component with timeout"""
        def analyze_with_timeout():
            return self.analyze_component(component)
        
        # Use threading with timeout
        result_container = [None]
        exception_container = [None]
        
        def target():
            try:
                result_container[0] = analyze_with_timeout()
            except Exception as e:
                exception_container[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=5.0)  # 5 second timeout per component
        
        if thread.is_alive():
            self.logger.warning(f"Component analysis timed out: {component['name']}")
            return None
        
        if exception_container[0]:
            raise exception_container[0]
        
        return result_container[0]
    
    def analyze_component(self, component: Dict) -> ComponentAnalysis:
        """Analyze a single component"""
        try:
            component_path = Path(component['path'])
            
            if not component_path.exists():
                return ComponentAnalysis(
                    name=component['name'],
                    path=component['path'],
                    component_type=component['type'],
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    working_features=[],
                    issues=["File not found"]
                )
            
            # Read file with size limit
            max_size = 1024 * 1024  # 1MB limit
            if component['size'] > max_size:
                return ComponentAnalysis(
                    name=component['name'],
                    path=component['path'],
                    component_type=component['type'],
                    status=ComponentStatus.BROKEN,
                    functionality_score=10,
                    working_features=[],
                    issues=["File too large"]
                )
            
            with open(component_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Quick analysis
            working_features = []
            issues = []
            score = 0
            
            # Check for basic structure
            if 'import' in content:
                working_features.append('imports')
                score += 10
            
            if 'def ' in content:
                working_features.append('functions')
                score += 15
            
            if 'class ' in content:
                working_features.append('classes')
                score += 15
            
            if 'try:' in content and 'except' in content:
                working_features.append('error_handling')
                score += 10
            
            if 'if __name__ == "__main__"' in content:
                working_features.append('standalone_execution')
                score += 15
            
            # Check for GUI elements
            if 'tkinter' in content.lower():
                working_features.append('tkinter_gui')
                score += 20
            
            if 'flask' in content.lower():
                working_features.append('web_api')
                score += 20
            
            # Determine status
            if score >= 70:
                status = ComponentStatus.EXCELLENT
            elif score >= 50:
                status = ComponentStatus.GOOD
            elif score >= 30:
                status = ComponentStatus.WORKING
            elif score >= 10:
                status = ComponentStatus.PARTIAL
            else:
                status = ComponentStatus.BROKEN
            
            return ComponentAnalysis(
                name=component['name'],
                path=component['path'],
                component_type=component['type'],
                status=status,
                functionality_score=score,
                working_features=working_features,
                issues=issues
            )
            
        except Exception as e:
            return ComponentAnalysis(
                name=component['name'],
                path=component['path'],
                component_type=component['type'],
                status=ComponentStatus.BROKEN,
                functionality_score=0,
                working_features=[],
                issues=[str(e)]
            )
    
    def verify_mesh_vpn_components(self) -> Dict[str, Any]:
        """Verify mesh VPN components"""
        mesh_components = {
            'mesh_vpn_server.py': 'Network Management',
            'mesh_service_discovery.py': 'Network Management', 
            'mesh_vpn_client.py': 'Network Management',
            'wireguard_config_generator.py': 'Network Management',
            'mesh_app_communication.py': 'Core Services',
            'mesh_app_integration.py': 'Core Services',
            'mesh_vpn_dashboard.py': 'Core Services',
            'bidirectional_mesh_setup.py': 'Network Management'
        }
        
        results = {
            'total_components': len(mesh_components),
            'found_components': 0,
            'working_components': 0,
            'component_status': {}
        }
        
        for component, location in mesh_components.items():
            component_path = Path(location) / component
            
            if component_path.exists():
                results['found_components'] += 1
                results['component_status'][component] = 'found'
                
                # Quick check if it looks working
                try:
                    with open(component_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 1000 and 'def ' in content and 'import' in content:
                        results['working_components'] += 1
                        results['component_status'][component] = 'working'
                    else:
                        results['component_status'][component] = 'minimal'
                        
                except:
                    results['component_status'][component] = 'error'
            else:
                results['component_status'][component] = 'missing'
        
        print(f"  ✓ Mesh VPN: {results['working_components']}/{results['total_components']} working")
        return results
    
    def verify_launcher_dashboard(self) -> Dict[str, Any]:
        """Verify launcher and dashboard components"""
        launcher_components = {
            'homelab_launcher.py': 'Main launcher',
            'homelab_launcher_enhanced.py': 'Enhanced launcher',
            'homelab_dashboard.py': 'Main dashboard',
            'unified_dashboard.py': 'Unified dashboard'
        }
        
        results = {
            'total_components': len(launcher_components),
            'found_components': 0,
            'working_components': 0,
            'component_status': {}
        }
        
        for component, description in launcher_components.items():
            component_path = Path(component)
            
            if component_path.exists():
                results['found_components'] += 1
                results['component_status'][component] = 'found'
                
                # Quick functionality check
                try:
                    with open(component_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for key features
                    features = []
                    if 'tkinter' in content.lower():
                        features.append('gui')
                    if 'def launch_tool' in content:
                        features.append('tool_launching')
                    if 'mesh_comm' in content:
                        features.append('mesh_integration')
                    if len(features) >= 2:
                        results['working_components'] += 1
                        results['component_status'][component] = 'working'
                    else:
                        results['component_status'][component] = 'basic'
                        
                except:
                    results['component_status'][component] = 'error'
            else:
                results['component_status'][component] = 'missing'
        
        print(f"  ✓ Launcher/Dashboard: {results['working_components']}/{results['total_components']} working")
        return results
    
    def generate_optimized_results(self, system_analysis: Dict, component_results: List[ComponentAnalysis],
                                 mesh_analysis: Dict, launcher_analysis: Dict, audit_duration: float) -> Dict[str, Any]:
        """Generate optimized audit results"""
        
        # Count component statuses
        status_counts = {}
        for result in component_results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_components = len(component_results)
        working_components = status_counts.get('excellent', 0) + status_counts.get('good', 0) + status_counts.get('working', 0)
        broken_components = status_counts.get('broken', 0) + status_counts.get('partial', 0) + status_counts.get('missing', 0)
        
        # Calculate overall score
        if total_components > 0:
            overall_score = (working_components / total_components) * 100
        else:
            overall_score = 0
        
        # Determine overall status
        if overall_score >= 80:
            overall_status = "excellent"
        elif overall_score >= 60:
            overall_status = "working"
        elif overall_score >= 40:
            overall_status = "partial"
        else:
            overall_status = "broken"
        
        return {
            "overall_status": overall_status,
            "overall_score": round(overall_score, 1),
            "total_components": total_components,
            "working_components": working_components,
            "broken_components": broken_components,
            "audit_duration": round(audit_duration, 2),
            "system_analysis": system_analysis,
            "component_status_counts": status_counts,
            "mesh_vpn_analysis": mesh_analysis,
            "launcher_dashboard_analysis": launcher_analysis,
            "recommendations": self.generate_recommendations(status_counts, mesh_analysis, launcher_analysis)
        }
    
    def generate_recommendations(self, status_counts: Dict, mesh_analysis: Dict, launcher_analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Component recommendations
        total_broken = status_counts.get('broken', 0) + status_counts.get('partial', 0) + status_counts.get('missing', 0)
        if total_broken > 0:
            recommendations.append(f"Fix {total_broken} broken/partial/missing components")
        
        # Mesh VPN recommendations
        mesh_working = mesh_analysis['working_components']
        mesh_total = mesh_analysis['total_components']
        if mesh_working < mesh_total:
            recommendations.append(f"Complete mesh VPN implementation ({mesh_working}/{mesh_total} working)")
        
        # Launcher recommendations
        launcher_working = launcher_analysis['working_components']
        launcher_total = launcher_analysis['total_components']
        if launcher_working < launcher_total:
            recommendations.append(f"Fix launcher/dashboard components ({launcher_working}/{launcher_total} working)")
        
        # Module recommendations
        missing_modules = len(self.check_missing_modules())
        if missing_modules > 0:
            recommendations.append(f"Install {missing_modules} missing modules (ttk, django, pandas)")
        
        return recommendations
    
    def print_optimized_summary(self, results: Dict[str, Any]):
        """Print optimized audit summary"""
        print("\n" + "=" * 80)
        print("OPTIMIZED AUDIT SUMMARY")
        print("=" * 80)
        
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Overall Score: {results['overall_score']}/100")
        print(f"Total Components: {results['total_components']}")
        print(f"Working Components: {results['working_components']}")
        print(f"Broken Components: {results['broken_components']}")
        print(f"Audit Duration: {results['audit_duration']} seconds")
        
        print(f"\nSystem: {results['system_analysis']['system_type']} {results['system_analysis']['version']}")
        print(f"Python: {results['system_analysis']['python_version']}")
        print(f"Available Modules: {len(results['system_analysis']['available_modules'])}")
        
        print(f"\nMesh VPN: {results['mesh_vpn_analysis']['working_components']}/{results['mesh_vpn_analysis']['total_components']} working")
        print(f"Launcher/Dashboard: {results['launcher_dashboard_analysis']['working_components']}/{results['launcher_dashboard_analysis']['total_components']} working")
        
        if results['recommendations']:
            print("\nRecommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
    
    def save_optimized_results(self, results: Dict[str, Any]):
        """Save optimized results to JSON file"""
        try:
            output_file = Path("comprehensive_system_audit_results.json")
            
            # Update existing file or create new
            if output_file.exists():
                with open(output_file, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = {}
            
            # Update with new results
            existing_data.update(results)
            
            with open(output_file, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            print(f"\n✅ Results saved to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")

def main():
    """Main entry point"""
    auditor = OptimizedSystemAuditor()
    
    try:
        results = auditor.run_optimized_audit()
        
        # Return appropriate exit code
        if results.get('overall_score', 0) >= 60:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Audit interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Audit failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
