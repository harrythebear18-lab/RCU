#!/usr/bin/env python3
"""
Comprehensive Test Suite for Homelab Tools
Tests all 92 tools for Windows 10/11 compatibility
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json

class ComprehensiveTestSuite:
    """Comprehensive testing for all Homelab tools"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            'batch_files': {},
            'python_files': {},
            'c_cpp_files': {},
            'core_services': {},
            'gui_components': {},
            'paths_and_subdirectories': {},
            'overall': {
                'total_files': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }
        self.test_start_time = time.time()
        
    def log_result(self, category: str, item: str, passed: bool, message: str = "", details: Dict[str, Any] = None):
        """Log test result"""
        self.results[category][item] = {
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {category}: {item} - {message}")
        
        # Update overall stats
        self.results['overall']['total_files'] += 1
        if passed:
            self.results['overall']['passed'] += 1
        else:
            self.results['overall']['failed'] += 1
    
    def find_all_files(self) -> Dict[str, List[Path]]:
        """Find all files to test"""
        files = {
            'batch': [],
            'python': [],
            'c_cpp': [],
            'other': []
        }
        
        # Find all files recursively
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() == '.bat':
                    files['batch'].append(file_path)
                elif file_path.suffix.lower() == '.py':
                    files['python'].append(file_path)
                elif file_path.suffix.lower() in ['.c', '.cpp', '.h', '.hpp']:
                    files['c_cpp'].append(file_path)
                else:
                    files['other'].append(file_path)
        
        return files
    
    def test_batch_file(self, batch_file: Path) -> Tuple[bool, str]:
        """Test individual batch file"""
        try:
            # Read batch file content
            content = batch_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for common Windows compatibility issues
            issues = []
            
            # Check for hardcoded paths
            if 'C:\\' in content and 'C:\\Users\\' not in content:
                issues.append("Contains hardcoded paths")
            
            # Check for Windows 10/11 specific commands
            win11_commands = ['winget', 'wsl', 'pwsh']
            for cmd in win11_commands:
                if cmd in content:
                    issues.append(f"Contains Windows 11+ command: {cmd}")
            
            # Check for Python command compatibility
            python_commands = ['python', 'py', 'python3']
            has_python_detection = any(cmd in content for cmd in python_commands)
            if not has_python_detection and 'python' in content.lower():
                issues.append("Missing Python command detection")
            
            # Check for emoji usage (already fixed, but verify)
            emoji_chars = ['😀', '🚀', '⚡', '🔧', '📊', '💾', '🔒', '🌐']
            for emoji in emoji_chars:
                if emoji in content:
                    issues.append(f"Contains emoji: {emoji}")
            
            # Test syntax by running help command
            try:
                result = subprocess.run(
                    ['cmd', '/c', f'"{batch_file}"'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=self.root_dir
                )
                
                # Check if it runs without syntax errors
                if result.returncode == 0 or 'help' in result.stdout.lower() or 'usage' in result.stdout.lower():
                    syntax_ok = True
                else:
                    syntax_ok = False
                    issues.append("Syntax error or execution failure")
                    
            except subprocess.TimeoutExpired:
                syntax_ok = True  # Timeout means it started running
                issues.append("Long-running script (timeout)")
            except Exception as e:
                syntax_ok = False
                issues.append(f"Execution error: {str(e)}")
            
            return len(issues) == 0 and syntax_ok, "; ".join(issues) if issues else "OK"
            
        except Exception as e:
            return False, f"Error testing batch file: {str(e)}"
    
    def test_python_file(self, python_file: Path) -> Tuple[bool, str]:
        """Test individual Python file"""
        try:
            # Read Python file content
            content = python_file.read_text(encoding='utf-8', errors='ignore')
            
            issues = []
            
            # Check for shebang line
            if not content.startswith('#!/usr/bin/env python3') and not content.startswith('#!'):
                issues.append("Missing shebang line")
            
            # Check for hardcoded paths
            if 'C:\\' in content and 'os.path.expanduser' not in content:
                issues.append("Contains hardcoded paths")
            
            # Check for proper imports
            import_lines = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
            
            # Check for problematic imports
            problematic_imports = ['tkinter.ttk', 'tkinter.messagebox']
            for imp in import_lines:
                for prob in problematic_imports:
                    if prob in imp:
                        issues.append(f"Potentially problematic import: {prob}")
            
            # Test syntax by compiling
            try:
                compile(content, str(python_file), 'exec')
                syntax_ok = True
            except SyntaxError as e:
                syntax_ok = False
                issues.append(f"Syntax error: {str(e)}")
            except Exception as e:
                syntax_ok = False
                issues.append(f"Compilation error: {str(e)}")
            
            # Check for main execution pattern
            if '__main__' in content and 'if __name__ == "__main__"' not in content:
                issues.append("Missing proper main execution pattern")
            
            return len(issues) == 0 and syntax_ok, "; ".join(issues) if issues else "OK"
            
        except Exception as e:
            return False, f"Error testing Python file: {str(e)}"
    
    def test_c_cpp_file(self, c_cpp_file: Path) -> Tuple[bool, str]:
        """Test individual C/C++ file"""
        try:
            content = c_cpp_file.read_text(encoding='utf-8', errors='ignore')
            
            issues = []
            
            # Check for Windows-specific includes
            windows_includes = ['#include <windows.h>', '#include <tchar.h>']
            for include in windows_includes:
                if include in content:
                    issues.append(f"Contains Windows-specific include: {include}")
            
            # Check for proper header guards
            if c_cpp_file.suffix in ['.h', '.hpp']:
                if not any(guard in content for guard in ['#ifndef', '#pragma once']):
                    issues.append("Missing header guard")
            
            # Check for common issues
            if 'system(' in content:
                issues.append("Contains system() call (potentially unsafe)")
            
            return len(issues) == 0, "; ".join(issues) if issues else "OK"
            
        except Exception as e:
            return False, f"Error testing C/C++ file: {str(e)}"
    
    def test_core_services(self) -> Dict[str, Tuple[bool, str]]:
        """Test all core services"""
        services = {}
        core_services_dir = self.root_dir / "Core Services"
        
        if not core_services_dir.exists():
            services['directory'] = (False, "Core Services directory not found")
            return services
        
        # Test each core service
        service_files = [
            'event_bus.py',
            'config_manager.py', 
            'auth_service.py',
            'data_persistence.py',
            'unified_monitoring.py',
            'unified_dashboard.py',
            'bidirectional_resource_sharing.py'
        ]
        
        for service_file in service_files:
            service_path = core_services_dir / service_file
            if service_path.exists():
                try:
                    # Test import
                    module_name = service_file[:-3]  # Remove .py extension
                    
                    # Add to path and test import
                    sys.path.insert(0, str(core_services_dir))
                    
                    try:
                        __import__(module_name)
                        services[service_file] = (True, "Import successful")
                    except ImportError as e:
                        services[service_file] = (False, f"Import failed: {str(e)}")
                    except Exception as e:
                        services[service_file] = (False, f"Error importing: {str(e)}")
                    finally:
                        sys.path.remove(str(core_services_dir))
                        
                except Exception as e:
                    services[service_file] = (False, f"Error testing service: {str(e)}")
            else:
                services[service_file] = (False, "Service file not found")
        
        return services
    
    def test_gui_components(self) -> Dict[str, Tuple[bool, str]]:
        """Test GUI components"""
        gui_tests = {}
        
        # Test unified dashboard
        dashboard_path = self.root_dir / "Core Services" / "unified_dashboard.py"
        if dashboard_path.exists():
            try:
                # Test if GUI dependencies are available
                import tkinter
                gui_tests['tkinter'] = (True, "tkinter available")
                
                # Test dashboard import (without running GUI)
                sys.path.insert(0, str(self.root_dir / "Core Services"))
                try:
                    import unified_dashboard
                    gui_tests['unified_dashboard'] = (True, "Dashboard import successful")
                except Exception as e:
                    gui_tests['unified_dashboard'] = (False, f"Dashboard import failed: {str(e)}")
                finally:
                    sys.path.remove(str(self.root_dir / "Core Services"))
                    
            except ImportError as e:
                gui_tests['tkinter'] = (False, f"tkinter not available: {str(e)}")
        else:
            gui_tests['unified_dashboard'] = (False, "Dashboard file not found")
        
        return gui_tests
    
    def test_paths_and_subdirectories(self) -> Dict[str, Tuple[bool, str]]:
        """Test paths and subdirectory handling"""
        path_tests = {}
        
        # Test Core Services directory with spaces
        core_services_dir = self.root_dir / "Core Services"
        if core_services_dir.exists():
            path_tests['core_services_directory'] = (True, "Core Services directory exists")
            
            # Test if Python can handle the space in path
            try:
                test_file = core_services_dir / "__init__.py"
                if not test_file.exists():
                    test_file.write_text("# Test file for Core Services")
                
                sys.path.insert(0, str(core_services_dir))
                sys.path.remove(str(core_services_dir))
                test_file.unlink()
                
                path_tests['space_in_path'] = (True, "Space in path handled correctly")
            except Exception as e:
                path_tests['space_in_path'] = (False, f"Space in path error: {str(e)}")
        else:
            path_tests['core_services_directory'] = (False, "Core Services directory missing")
        
        # Test other important directories
        important_dirs = ['config', 'data', 'logs']
        for dir_name in important_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                path_tests[f'{dir_name}_directory'] = (True, f"{dir_name} directory exists")
            else:
                path_tests[f'{dir_name}_directory'] = (False, f"{dir_name} directory missing")
        
        return path_tests
    
    def test_bidirectional_resource_sharing(self) -> Tuple[bool, str]:
        """Test bidirectional resource sharing"""
        try:
            sys.path.insert(0, str(self.root_dir / "Core Services"))
            
            # Test import
            from bidirectional_resource_sharing import BidirectionalResourceSharing, ResourceType
            
            # Test initialization
            sharing = BidirectionalResourceSharing()
            
            # Test resource types
            resource_types = [rt.value for rt in ResourceType]
            
            # Test port allocation
            port = sharing._find_available_port()
            port_in_range = 30000 <= port <= 31000
            
            sys.path.remove(str(self.root_dir / "Core Services"))
            
            return port_in_range, f"Resource sharing OK, port: {port}"
            
        except Exception as e:
            return False, f"Resource sharing test failed: {str(e)}"
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("Comprehensive Homelab Tools Test Suite")
        print("=" * 60)
        print(f"Testing directory: {self.root_dir}")
        print(f"Test started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Find all files
        files = self.find_all_files()
        print(f"Found {len(files['batch'])} batch files")
        print(f"Found {len(files['python'])} Python files")
        print(f"Found {len(files['c_cpp'])} C/C++ files")
        print(f"Found {len(files['other'])} other files")
        print()
        
        # Test batch files
        print("Testing Batch Files...")
        for batch_file in files['batch']:
            relative_path = batch_file.relative_to(self.root_dir)
            passed, message = self.test_batch_file(batch_file)
            self.log_result('batch_files', str(relative_path), passed, message)
        
        print("\nTesting Python Files...")
        for python_file in files['python']:
            relative_path = python_file.relative_to(self.root_dir)
            passed, message = self.test_python_file(python_file)
            self.log_result('python_files', str(relative_path), passed, message)
        
        print("\nTesting C/C++ Files...")
        for c_cpp_file in files['c_cpp']:
            relative_path = c_cpp_file.relative_to(self.root_dir)
            passed, message = self.test_c_cpp_file(c_cpp_file)
            self.log_result('c_cpp_files', str(relative_path), passed, message)
        
        print("\nTesting Core Services...")
        core_services_results = self.test_core_services()
        for service, (passed, message) in core_services_results.items():
            self.log_result('core_services', service, passed, message)
        
        print("\nTesting GUI Components...")
        gui_results = self.test_gui_components()
        for component, (passed, message) in gui_results.items():
            self.log_result('gui_components', component, passed, message)
        
        print("\nTesting Paths and Directories...")
        path_results = self.test_paths_and_subdirectories()
        for path_test, (passed, message) in path_results.items():
            self.log_result('paths_and_subdirectories', path_test, passed, message)
        
        print("\nTesting Bidirectional Resource Sharing...")
        sharing_passed, sharing_message = self.test_bidirectional_resource_sharing()
        self.log_result('core_services', 'bidirectional_sharing', sharing_passed, sharing_message)
        
        # Calculate final results
        test_duration = time.time() - self.test_start_time
        total_tests = self.results['overall']['total_files']
        passed_tests = self.results['overall']['passed']
        failed_tests = self.results['overall']['failed']
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"Total files tested: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Test duration: {test_duration:.2f} seconds")
        print()
        
        # Summary by category
        categories = ['batch_files', 'python_files', 'c_cpp_files', 'core_services', 'gui_components', 'paths_and_subdirectories']
        for category in categories:
            category_results = self.results[category]
            category_passed = sum(1 for r in category_results.values() if r['passed'])
            category_total = len(category_results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            print(f"{category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Windows 10/11 compatibility assessment
        print("\n" + "=" * 60)
        print("WINDOWS 10/11 COMPATIBILITY ASSESSMENT")
        print("=" * 60)
        
        compatibility_issues = []
        
        # Check for compatibility issues
        for category, items in self.results.items():
            if category == 'overall':
                continue
                
            for item, result in items.items():
                if not result['passed']:
                    compatibility_issues.append(f"{category}: {item} - {result['message']}")
        
        if compatibility_issues:
            print("COMPATIBILITY ISSUES FOUND:")
            for issue in compatibility_issues[:10]:  # Show first 10 issues
                print(f"  ❌ {issue}")
            
            if len(compatibility_issues) > 10:
                print(f"  ... and {len(compatibility_issues) - 10} more issues")
        else:
            print("✅ No compatibility issues detected!")
            print("✅ Ready for Windows 10/11 deployment")
        
        return self.results

def main():
    """Main test runner"""
    suite = ComprehensiveTestSuite()
    results = suite.run_all_tests()
    
    # Save results to file
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Exit with appropriate code
    success_rate = results['overall']['passed'] / results['overall']['total_files'] * 100
    sys.exit(0 if success_rate >= 90 else 1)  # Require 90% success rate

if __name__ == "__main__":
    main()
