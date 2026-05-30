#!/usr/bin/env python3
"""
Complete System Verification - Validates ALL 152+ tools, batch files, and Python path files
Catches fundamental issues, missing functionality, and broken components
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import ast
import re

class CompleteSystemVerifier:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_tools': 0,
            'total_batch_files': 0,
            'total_python_files': 0,
            'categories': {},
            'summary': {'total_checks': 0, 'passed': 0, 'failed': 0, 'score': 0},
            'critical_issues': [],
            'missing_files': [],
            'broken_imports': [],
            'syntax_errors': []
        }
        self.issues_found = []
    
    def log_result(self, category, item_name, check_name, passed, details=""):
        """Log verification result"""
        if category not in self.results['categories']:
            self.results['categories'][category] = {
                'items': {},
                'summary': {'total': 0, 'passed': 0, 'failed': 0}
            }
        
        if item_name not in self.results['categories'][category]['items']:
            self.results['categories'][category]['items'][item_name] = []
        
        result = {
            'check': check_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results['categories'][category]['items'][item_name].append(result)
        self.results['categories'][category]['summary']['total'] += 1
        self.results['summary']['total_checks'] += 1
        
        if passed:
            self.results['categories'][category]['summary']['passed'] += 1
            self.results['summary']['passed'] += 1
            print(f"✓ {category}/{item_name} - {check_name}: {details}")
        else:
            self.results['categories'][category]['summary']['failed'] += 1
            self.results['summary']['failed'] += 1
            issue = f"{category}/{item_name} - {check_name}: {details}"
            self.issues_found.append(issue)
            
            # Categorize critical issues
            if 'syntax' in check_name.lower() or 'import' in check_name.lower():
                self.results['broken_imports'].append(issue)
            elif 'file_exists' in check_name.lower():
                self.results['missing_files'].append(issue)
            elif 'syntax' in details.lower():
                self.results['syntax_errors'].append(issue)
            else:
                self.results['critical_issues'].append(issue)
            
            print(f"✗ {category}/{item_name} - {check_name}: {details}")
    
    def find_all_files(self):
        """Find all Python files and batch files in the system"""
        print("Scanning for all files...")
        
        python_files = list(self.root_dir.rglob("*.py"))
        batch_files = list(self.root_dir.rglob("*.bat"))
        
        self.results['total_python_files'] = len(python_files)
        self.results['total_batch_files'] = len(batch_files)
        self.results['total_tools'] = len(python_files) + len(batch_files)
        
        print(f"Found {len(python_files)} Python files and {len(batch_files)} batch files")
        
        # Categorize files by directory
        categories = {}
        for py_file in python_files:
            category = py_file.parent.name
            if category not in categories:
                categories[category] = {'python': [], 'batch': []}
            categories[category]['python'].append(py_file)
        
        for bat_file in batch_files:
            category = bat_file.parent.name
            if category not in categories:
                categories[category] = {'python': [], 'batch': []}
            categories[category]['batch'].append(bat_file)
        
        return categories
    
    def verify_python_file(self, file_path):
        """Comprehensive Python file verification"""
        category = file_path.parent.name
        item_name = file_path.stem
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # 1. Syntax Check
            try:
                ast.parse(content)
                self.log_result(category, item_name, 'syntax_check', True, "Valid Python syntax")
            except SyntaxError as e:
                self.log_result(category, item_name, 'syntax_check', False, f"Syntax error: {e}")
                return
            except Exception as e:
                self.log_result(category, item_name, 'syntax_check', False, f"Parse error: {e}")
                return
            
            # 2. Import Verification
            imports = re.findall(r'^import\s+(\w+)|^from\s+(\w+)', content, re.MULTILINE)
            missing_imports = []
            
            for imp_match in imports:
                imp_name = imp_match[0] or imp_match[1]
                if imp_name and imp_name not in ['os', 'sys', 'time', 'json', 'datetime', 'pathlib', 'tkinter', 'threading']:
                    try:
                        __import__(imp_name)
                        self.log_result(category, item_name, f'import_{imp_name}', True, f"Import {imp_name} available")
                    except ImportError:
                        missing_imports.append(imp_name)
                        self.log_result(category, item_name, f'import_{imp_name}', False, f"Import {imp_name} missing")
            
            # 3. Class Structure Check
            classes = re.findall(r'class\s+(\w+)', content)
            if classes:
                self.log_result(category, item_name, 'classes_found', True, f"Found {len(classes)} classes: {', '.join(classes[:3])}")
            else:
                self.log_result(category, item_name, 'classes_found', False, "No classes found")
            
            # 4. Function Structure Check
            functions = re.findall(r'def\s+(\w+)', content)
            if functions:
                self.log_result(category, item_name, 'functions_found', True, f"Found {len(functions)} functions: {', '.join(functions[:3])}")
            else:
                self.log_result(category, item_name, 'functions_found', False, "No functions found")
            
            # 5. GUI Components Check (for GUI tools)
            if any(gui_lib in content for gui_lib in ['tkinter', 'PyQt', 'PySide', 'wxPython']):
                gui_checks = {
                    'tkinter': ['tk.Tk', 'tk.Frame', 'tk.Label', 'tk.Button', 'pack(', 'grid('],
                    'matplotlib': ['Figure', 'FigureCanvasTkAgg', 'plt.'],
                    'ttk': ['ttk.Frame', 'ttk.Label', 'ttk.Button']
                }
                
                for lib, components in gui_checks.items():
                    if lib in content:
                        found_components = [comp for comp in components if comp in content]
                        if found_components:
                            self.log_result(category, item_name, f'gui_{lib}', True, f"GUI components: {', '.join(found_components[:3])}")
                        else:
                            self.log_result(category, item_name, f'gui_{lib}', False, f"No {lib} GUI components")
            
            # 6. Main Execution Check
            if 'if __name__ == "__main__":' in content:
                self.log_result(category, item_name, 'main_execution', True, "Has main execution block")
            else:
                self.log_result(category, item_name, 'main_execution', False, "No main execution block")
            
            # 7. Error Handling Check
            if 'try:' in content and 'except' in content:
                self.log_result(category, item_name, 'error_handling', True, "Has error handling")
            else:
                self.log_result(category, item_name, 'error_handling', False, "No error handling")
            
            # 8. Window Scaling Check (for GUI tools)
            if 'tkinter' in content:
                window_checks = {
                    'geometry(': 'Window geometry',
                    'minsize(': 'Minimum window size',
                    'maxsize(': 'Maximum window size',
                    'resizable(': 'Window resizable',
                    'configure(bg=': 'Background color',
                    'winfo_screenwidth': 'Screen width detection',
                    'attributes(': 'Window attributes'
                }
                
                for check, desc in window_checks.items():
                    if check in content:
                        self.log_result(category, item_name, f'window_{check[:10]}', True, desc)
                    else:
                        self.log_result(category, item_name, f'window_{check[:10]}', False, f"Missing: {desc}")
            
            # 9. Data Collection Check (for monitoring tools)
            if any(monitor_lib in content for monitor_lib in ['psutil', 'GPUtil', 'py-cpuinfo']):
                monitor_checks = {
                    'psutil.cpu_percent': 'CPU usage monitoring',
                    'psutil.virtual_memory': 'Memory monitoring',
                    'psutil.disk_usage': 'Disk monitoring',
                    'psutil.net_io_counters': 'Network monitoring',
                    'psutil.sensors_temperatures': 'Temperature monitoring',
                    'deque(': 'Data history storage',
                    'threading.Thread': 'Threading support'
                }
                
                for check, desc in monitor_checks.items():
                    if check in content:
                        self.log_result(category, item_name, f'monitor_{check[:10]}', True, desc)
                    else:
                        self.log_result(category, item_name, f'monitor_{check[:10]}', False, f"Missing: {desc}")
            
            # 10. File Path Handling Check
            path_checks = {
                'Path(': 'Path object usage',
                'os.path.': 'OS path functions',
                '__file__': 'File path detection',
                'sys.path': 'Python path manipulation'
            }
            
            for check, desc in path_checks.items():
                if check in content:
                    self.log_result(category, item_name, f'path_{check[:8]}', True, desc)
                else:
                    self.log_result(category, item_name, f'path_{check[:8]}', False, f"Missing: {desc}")
            
        except Exception as e:
            self.log_result(category, item_name, 'file_read', False, f"Error reading file: {e}")
    
    def verify_batch_file(self, file_path):
        """Comprehensive batch file verification"""
        category = file_path.parent.name
        item_name = file_path.stem
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # 1. Basic Structure Check
            if '@echo off' in content or '@ECHO OFF' in content:
                self.log_result(category, item_name, 'echo_off', True, "Has echo off")
            else:
                self.log_result(category, item_name, 'echo_off', False, "Missing echo off")
            
            # 2. Python Path Check
            python_checks = {
                'python': 'Python command',
                'py': 'Py launcher',
                'python3': 'Python3 command',
                'PYTHONPATH': 'Python path variable'
            }
            
            for check, desc in python_checks.items():
                if check in content.upper():
                    self.log_result(category, item_name, f'python_{check}', True, desc)
                else:
                    self.log_result(category, item_name, f'python_{check}', False, f"Missing: {desc}")
            
            # 3. Path Variable Check
            path_vars = ['%PATH%', 'ProgramFiles', 'ProgramFiles(x86)', 'LocalAppData']
            for var in path_vars:
                if var in content:
                    self.log_result(category, item_name, f'path_var_{var[:10]}', True, f"Path variable: {var}")
            
            # 4. Error Handling Check
            if 'errorlevel' in content.lower() or 'if errorlevel' in content.lower():
                self.log_result(category, item_name, 'error_handling', True, "Has error handling")
            else:
                self.log_result(category, item_name, 'error_handling', False, "No error handling")
            
            # 5. Comment/Documentation Check
            if 'rem ' in content.lower() or '::' in content:
                self.log_result(category, item_name, 'comments', True, "Has comments")
            else:
                self.log_result(category, item_name, 'comments', False, "No comments")
            
            # 6. Launch Functionality Check
            launch_checks = {
                'start': 'Start command',
                'call': 'Call command',
                'cmd /c': 'Command execution'
            }
            
            for check, desc in launch_checks.items():
                if check in content.lower():
                    self.log_result(category, item_name, f'launch_{check}', True, desc)
            
        except Exception as e:
            self.log_result(category, item_name, 'file_read', False, f"Error reading file: {e}")
    
    def verify_core_services(self):
        """Verify Core Services specifically"""
        core_services_path = self.root_dir / "Core Services"
        if not core_services_path.exists():
            self.log_result('Core Services', 'directory', 'exists', False, "Core Services directory missing")
            return
        
        self.log_result('Core Services', 'directory', 'exists', True, "Core Services directory found")
        
        # Check essential Core Services files
        essential_files = [
            'homelab_portal.py',
            'rest_api.py', 
            'unified_dashboard.py',
            'event_bus.py',
            'config_manager.py'
        ]
        
        for file_name in essential_files:
            file_path = core_services_path / file_name
            if file_path.exists():
                self.log_result('Core Services', file_name, 'exists', True, "Essential file exists")
                self.verify_python_file(file_path)
            else:
                self.log_result('Core Services', file_name, 'exists', False, "Essential file missing")
    
    def verify_monitoring_tools(self):
        """Verify monitoring tools specifically"""
        monitoring_tools = [
            ("Cpu Monitor", "cpu_monitor.py"),
            ("Gpu Monitor", "gpu_monitor.py"),
            ("Network Monitor", "network_monitor.py"),
            ("Power Management", "power_manager.py")
        ]
        
        for category, file_name in monitoring_tools:
            file_path = self.root_dir / category / file_name
            if file_path.exists():
                self.verify_python_file(file_path)
            else:
                self.log_result(category, file_name, 'exists', False, "Monitoring tool missing")
    
    def verify_launchers(self):
        """Verify launcher files"""
        launcher_files = [
            "homelab_launcher.py",
            "Integrated_RAM_Launcher.py",
            "Simple_Launcher.py",
            "Universal_Launcher.bat"
        ]
        
        for file_name in launcher_files:
            file_path = self.root_dir / file_name
            if file_path.exists():
                if file_path.suffix == '.py':
                    self.verify_python_file(file_path)
                elif file_path.suffix == '.bat':
                    self.verify_batch_file(file_path)
            else:
                category = "Launchers"
                self.log_result(category, file_name, 'exists', False, "Launcher missing")
    
    def run_complete_verification(self):
        """Run complete system verification"""
        print("=" * 80)
        print("COMPLETE SYSTEM VERIFICATION - ALL 152+ TOOLS")
        print("=" * 80)
        
        # Find all files
        categories = self.find_all_files()
        
        # Verify Core Services
        self.verify_core_services()
        
        # Verify monitoring tools
        self.verify_monitoring_tools()
        
        # Verify launchers
        self.verify_launchers()
        
        # Verify all Python files
        print(f"\nVerifying {self.results['total_python_files']} Python files...")
        for category_name, files_dict in categories.items():
            if category_name not in ['Core Services', 'Cpu Monitor', 'Gpu Monitor', 'Network Monitor', 'Power Management']:
                for py_file in files_dict['python']:
                    self.verify_python_file(py_file)
        
        # Verify all batch files
        print(f"\nVerifying {self.results['total_batch_files']} batch files...")
        for category_name, files_dict in categories.items():
            for bat_file in files_dict['batch']:
                self.verify_batch_file(bat_file)
        
        # Calculate final score
        if self.results['summary']['total_checks'] > 0:
            self.results['summary']['score'] = (self.results['summary']['passed'] / self.results['summary']['total_checks']) * 100
        else:
            self.results['summary']['score'] = 0
        
        return self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive verification report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Files Checked: {self.results['total_tools']}")
        print(f"Python Files: {self.results['total_python_files']}")
        print(f"Batch Files: {self.results['total_batch_files']}")
        print(f"Total Checks: {self.results['summary']['total_checks']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Overall Score: {self.results['summary']['score']:.1f}%")
        
        # Category breakdown
        print("\nCATEGORY BREAKDOWN:")
        for category, data in self.results['categories'].items():
            total = data['summary']['total']
            passed = data['summary']['passed']
            score = (passed / total * 100) if total > 0 else 0
            print(f"  {category}: {passed}/{total} ({score:.1f}%)")
        
        # Critical issues summary
        print(f"\nCRITICAL ISSUES FOUND:")
        print(f"  Missing Files: {len(self.results['missing_files'])}")
        print(f"  Broken Imports: {len(self.results['broken_imports'])}")
        print(f"  Syntax Errors: {len(self.results['syntax_errors'])}")
        print(f"  Other Issues: {len(self.results['critical_issues'])}")
        
        # Show first 10 critical issues
        if self.issues_found:
            print(f"\nTOP ISSUES (first 10 of {len(self.issues_found)}):")
            for issue in self.issues_found[:10]:
                print(f"  - {issue}")
        
        # Save detailed report
        report_file = self.root_dir / "complete_verification_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return self.results['summary']['score']

def main():
    """Main verification runner"""
    verifier = CompleteSystemVerifier()
    score = verifier.run_complete_verification()
    
    if score >= 95:
        print("\n🎉 EXCELLENT: System verification passed with exceptional score!")
    elif score >= 85:
        print("\n✅ VERY GOOD: System verification passed with high score!")
    elif score >= 75:
        print("\n✅ GOOD: System verification passed with decent score!")
    elif score >= 60:
        print("\n⚠️  FAIR: System has some issues that need attention")
    elif score >= 40:
        print("\n❌ POOR: System has significant issues that need fixing")
    else:
        print("\n🚨 CRITICAL: System has major issues requiring immediate attention")
    
    return score

if __name__ == "__main__":
    main()
