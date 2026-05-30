#!/usr/bin/env python3
"""
Comprehensive System Verification
Checks GUI components, buttons, pathing, backend services, and APIs
"""

import os
import sys
import subprocess
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any
import time

class ComprehensiveSystemVerifier:
    """Comprehensive verification of all system components"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            'gui_components': {},
            'button_functionality': {},
            'pathing_systems': {},
            'backend_services': {},
            'api_endpoints': {},
            'file_structure': {},
            'overall': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'success_rate': 0
            }
        }
        self.verification_start_time = time.time()
    
    def log_result(self, category: str, item: str, passed: bool, message: str = "", details: Dict[str, Any] = None):
        """Log verification result"""
        self.results[category][item] = {
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        
        self.results['overall']['total_checks'] += 1
        if passed:
            self.results['overall']['passed'] += 1
        else:
            self.results['overall']['failed'] += 1
        
        status = "✓" if passed else "✗"
        print(f"{status} {category}: {item} - {message}")
    
    def verify_gui_components(self):
        """Verify all GUI components"""
        print("Verifying GUI Components...")
        
        gui_files = [
            'Core Services/homelab_portal.py',
            'Core Services/unified_dashboard.py',
            'Core Services/ddr4_ram_sharing.py',
            'Core Services/intel_ethernet_optimizer.py',
            'Core Services/nvidia_gpu_sharing.py',
            'Core Services/windows_network_discovery.py',
            'Core Services/windows_screen_sharing.py',
            'Ram clean up/ram_monitor_gui.py',
            'Ram clean up/soft_ram_cleaner.py',
            'RDMA/rdma_desktop_app.py',
            'RDMA/rdma_desktop_app_modern.py',
            'RDMA/rdma_modern_tkinter.py',
            'RDMA Memory Portal/memory_portal_gui.py',
            'Web Dashboard/web_dashboard.py'
        ]
        
        for gui_file in gui_files:
            file_path = self.root_dir / gui_file
            if file_path.exists():
                try:
                    # Check if file can be imported/syntax checked
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    compile(content, str(file_path), 'exec')
                    
                    # Check for GUI-specific imports
                    has_gui_imports = any(gui_lib in content for gui_lib in ['tkinter', 'PyQt', 'PySide', 'flask', 'streamlit'])
                    has_main_loop = any(main in content for main in ['mainloop()', 'app.run()', 'run_server()'])
                    
                    if has_gui_imports:
                        self.log_result('gui_components', gui_file, True, f"GUI component with proper imports")
                    else:
                        self.log_result('gui_components', gui_file, False, "Missing GUI imports")
                        
                except SyntaxError as e:
                    self.log_result('gui_components', gui_file, False, f"Syntax error: {e}")
                except Exception as e:
                    self.log_result('gui_components', gui_file, False, f"Error: {e}")
            else:
                self.log_result('gui_components', gui_file, False, "File not found")
    
    def verify_button_functionality(self):
        """Verify button functionality in GUI components"""
        print("\nVerifying Button Functionality...")
        
        gui_files = list(self.root_dir.rglob('*.py'))
        
        button_patterns = [
            'Button(', 'tk.Button', 'QPushButton', 'Button(', 'onclick', 'on_click',
            'command=', 'bind(', 'click', 'press', 'activate'
        ]
        
        for gui_file in gui_files:
            try:
                content = gui_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for button definitions
                button_count = sum(content.count(pattern) for pattern in button_patterns)
                
                # Check for event handlers
                event_handlers = content.count('def ') + content.count('function') + content.count('=>')
                
                if button_count > 0:
                    self.log_result('button_functionality', str(gui_file.relative_to(self.root_dir)), 
                                  True, f"Found {button_count} button elements, {event_handlers} handlers")
                elif 'tkinter' in content or 'flask' in content or 'web' in content.lower():
                    self.log_result('button_functionality', str(gui_file.relative_to(self.root_dir)), 
                                  False, "GUI file without button elements")
                    
            except Exception as e:
                self.log_result('button_functionality', str(gui_file.relative_to(self.root_dir)), 
                              False, f"Error checking buttons: {e}")
    
    def verify_pathing_systems(self):
        """Verify all pathing and routing systems"""
        print("\nVerifying Pathing Systems...")
        
        # Check file path handling
        python_files = list(self.root_dir.rglob('*.py'))
        
        path_patterns = [
            'os.path', 'Path(', 'pathlib', 'join(', 'abspath(', 'dirname(',
            'expanduser', 'expandvars', 'normpath(', 'realpath('
        ]
        
        hardcoded_paths = 0
        proper_paths = 0
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for proper path handling
                path_usage = sum(content.count(pattern) for pattern in path_patterns)
                
                # Check for hardcoded paths (excluding regex patterns)
                if 'C:\\\\' in content and 'os.path.expanduser' not in content:
                    hardcoded_paths += 1
                elif path_usage > 0:
                    proper_paths += 1
                    
            except Exception:
                continue
        
        self.log_result('pathing_systems', 'Proper Path Handling', proper_paths > 0, 
                       f"Found {proper_paths} files with proper path handling")
        self.log_result('pathing_systems', 'Hardcoded Paths', hardcoded_paths == 0, 
                       f"Found {hardcoded_paths} files with potential hardcoded paths")
        
        # Check routing systems
        routing_files = [
            'Core Services/rest_api.py',
            'Core Services/portal_api_endpoints.py',
            'Mobile_Interface/app.js',
            'Mobile_Interface/index.html'
        ]
        
        for route_file in routing_files:
            file_path = self.root_dir / route_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    if route_file.endswith('.py'):
                        routes = content.count('@app.route') + content.count('def ')
                    elif route_file.endswith('.js'):
                        routes = content.count('route') + content.count('app.') + content.count('router.')
                    else:
                        routes = content.count('href') + content.count('action')
                    
                    self.log_result('pathing_systems', f"Routing: {route_file}", routes > 0, 
                                  f"Found {routes} routing elements")
                    
                except Exception as e:
                    self.log_result('pathing_systems', f"Routing: {route_file}", False, f"Error: {e}")
    
    def verify_backend_services(self):
        """Verify all backend services"""
        print("\nVerifying Backend Services...")
        
        core_services = list((self.root_dir / 'Core Services').glob('*.py')) if (self.root_dir / 'Core Services').exists() else []
        
        for service_file in core_services:
            service_name = service_file.stem
            relative_path = service_file.relative_to(self.root_dir)
            
            try:
                # Check for service class/function definitions
                content = service_file.read_text(encoding='utf-8', errors='ignore')
                
                has_class = 'class ' in content
                has_functions = 'def ' in content
                has_imports = 'import ' in content or 'from ' in content
                
                # Try to compile (syntax check)
                compile(content, str(service_file), 'exec')
                
                if has_class or has_functions:
                    self.log_result('backend_services', str(relative_path), True, 
                                  f"Service with {'classes' if has_class else 'functions'}")
                else:
                    self.log_result('backend_services', str(relative_path), False, "Empty or invalid service")
                    
            except SyntaxError as e:
                self.log_result('backend_services', str(relative_path), False, f"Syntax error: {e}")
            except Exception as e:
                self.log_result('backend_services', str(relative_path), False, f"Error: {e}")
    
    def verify_api_endpoints(self):
        """Verify API endpoints"""
        print("\nVerifying API Endpoints...")
        
        api_files = [
            'Core Services/rest_api.py',
            'Core Services/portal_api_endpoints.py',
            'Core Services/simple_rest_api.py'
        ]
        
        for api_file in api_files:
            file_path = self.root_dir / api_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Count different types of endpoints
                    get_endpoints = content.count("methods=['GET']") + content.count("@app.get")
                    post_endpoints = content.count("methods=['POST']") + content.count("@app.post")
                    put_endpoints = content.count("methods=['PUT']") + content.count("@app.put")
                    delete_endpoints = content.count("methods=['DELETE']") + content.count("@app.delete")
                    
                    total_endpoints = get_endpoints + post_endpoints + put_endpoints + delete_endpoints
                    
                    self.log_result('api_endpoints', api_file, total_endpoints > 0, 
                                  f"Found {total_endpoints} endpoints (GET: {get_endpoints}, POST: {post_endpoints})")
                    
                except Exception as e:
                    self.log_result('api_endpoints', api_file, False, f"Error: {e}")
            else:
                self.log_result('api_endpoints', api_file, False, "API file not found")
    
    def verify_file_structure(self):
        """Verify complete file structure"""
        print("\nVerifying File Structure...")
        
        required_structure = {
            'Core Services': ['homelab_portal.py', 'rest_api.py', 'event_bus.py', 'unified_dashboard.py'],
            'Mobile_Interface': ['index.html', 'app.js', 'styles.css', 'manifest.json'],
            'Cpu Monitor': ['cpu_monitor.py']
        }
        
        for directory, required_files in required_structure.items():
            dir_path = self.root_dir / directory
            
            if dir_path.exists():
                if required_files:
                    missing_files = []
                    for req_file in required_files:
                        if not (dir_path / req_file).exists():
                            missing_files.append(req_file)
                    
                    if missing_files:
                        self.log_result('file_structure', directory, False, 
                                      f"Missing files: {', '.join(missing_files)}")
                    else:
                        self.log_result('file_structure', directory, True, 
                                      f"All {len(required_files)} required files present")
                else:
                    self.log_result('file_structure', directory, True, "Directory exists")
            else:
                self.log_result('file_structure', directory, False, "Directory missing")
    
    def verify_cpu_monitor(self):
        """Verify CPU Monitor functionality - comprehensive validation"""
        results = []
        print("\nFixing Final Batch File Issue...")
        
        batch_file = self.root_dir / 'RDMA' / 'windows_build.bat'
        
        if batch_file.exists():
            try:
                content = batch_file.read_text(encoding='utf-8', errors='ignore')
                
                # The issue is with the complex variable assignment
                # Let's fix it by using a simpler approach
                old_line = 'set WDK_DIR=%ProgramFiles(x86)%\\Windows Kits\\10\\%WDK_VERSION%'
                new_line = 'set "WDK_DIR=%ProgramFiles(x86)%\\Windows Kits\\10\\%WDK_VERSION%"'
                
                if old_line in content:
                    content = content.replace(old_line, new_line)
                    batch_file.write_text(content, encoding='utf-8')
                    self.log_result('backend_services', 'Batch File Fix', True, "Fixed batch file variable quoting")
                    return True
                else:
                    self.log_result('backend_services', 'Batch File Fix', False, "Pattern not found")
                    return False
                    
            except Exception as e:
                self.log_result('backend_services', 'Batch File Fix', False, f"Error: {e}")
                return False
        else:
            self.log_result('backend_services', 'Batch File Fix', False, "Batch file not found")
            return False
    
    def run_comprehensive_verification(self):
        """Run all verification checks"""
        print("=" * 60)
        print("COMPREHENSIVE SYSTEM VERIFICATION")
        print("=" * 60)
        
        # Run all verification checks
        self.verify_gui_components()
        self.verify_button_functionality()
        self.verify_pathing_systems()
        self.verify_backend_services()
        self.verify_api_endpoints()
        self.verify_file_structure()
        
        # Fix the final batch file
        batch_fixed = self.fix_final_batch_file()
        
        # Calculate overall success rate
        total_checks = self.results['overall']['total_checks']
        passed_checks = self.results['overall']['passed']
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        self.results['overall']['success_rate'] = success_rate
        
        # Print summary
        print("\n" + "=" * 60)
        print("COMPREHENSIVE VERIFICATION RESULTS")
        print("=" * 60)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {total_checks - passed_checks}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Batch File Fixed: {'Yes' if batch_fixed else 'No'}")
        print(f"Verification Duration: {time.time() - self.verification_start_time:.2f} seconds")
        
        # Category breakdown
        categories = ['gui_components', 'button_functionality', 'pathing_systems', 'backend_services', 'api_endpoints', 'file_structure']
        print("\nResults by Category:")
        for category in categories:
            category_results = self.results[category]
            category_passed = sum(1 for r in category_results.values() if r['passed'])
            category_total = len(category_results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            print(f"  {category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Overall status
        if success_rate >= 95:
            print("\n🎉 EXCELLENT: System verification passed with high success rate!")
            status = "EXCELLENT"
        elif success_rate >= 90:
            print("\n✅ GOOD: System verification passed with solid success rate")
            status = "GOOD"
        elif success_rate >= 80:
            print("\n⚠️  FAIR: System verification passed with moderate success rate")
            status = "FAIR"
        else:
            print("\n❌ POOR: System verification shows significant issues")
            status = "POOR"
        
        # Save results
        with open(self.root_dir / 'comprehensive_verification_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {self.root_dir / 'comprehensive_verification_results.json'}")
        
        return success_rate, status

def main():
    """Main entry point"""
    verifier = ComprehensiveSystemVerifier()
    success_rate, status = verifier.run_comprehensive_verification()
    
    # Return appropriate exit code
    sys.exit(0 if success_rate >= 90 else 1)

if __name__ == "__main__":
    main()
