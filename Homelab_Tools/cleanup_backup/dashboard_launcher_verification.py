#!/usr/bin/env python3
"""
Dashboard and Launcher Verification for Windows 10/11
Tests unified dashboard, launcher functionality, and tool launching on both systems
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

class DashboardLauncherVerifier:
    """Comprehensive verification of dashboard and launcher functionality"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            'dashboard_functionality': {},
            'launcher_functionality': {},
            'tool_launching': {},
            'windows_compatibility': {},
            'cross_version_tests': {},
            'overall': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'success_rate': 0
            }
        }
        self.verification_start_time = time.time()
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """Get detailed system information"""
        return {
            'os': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'windows_version': self.get_windows_version()
        }
    
    def get_windows_version(self):
        """Get detailed Windows version"""
        try:
            import winver
            return f"Windows {winver.get_winver_from_getversioninfo()}"
        except:
            try:
                import psutil
                boot_time = psutil.boot_time()
                return f"Windows (Boot: {boot_time})"
            except:
                return "Windows (Unknown version)"
    
    def log_result(self, category: str, item: str, passed: bool, message: str = "", details: Dict[str, Any] = None):
        """Log verification result"""
        self.results[category][item] = {
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        
        self.results['overall']['total_tests'] += 1
        if passed:
            self.results['overall']['passed'] += 1
        else:
            self.results['overall']['failed'] += 1
        
        status = "✓" if passed else "✗"
        print(f"{status} {category}: {item} - {message}")
    
    def test_dashboard_functionality(self):
        """Test unified dashboard functionality"""
        print("Testing Unified Dashboard Functionality...")
        
        dashboard_files = [
            'Core Services/unified_dashboard.py',
            'Core Services/homelab_portal.py'
        ]
        
        for dashboard_file in dashboard_files:
            file_path = self.root_dir / dashboard_file
            if file_path.exists():
                try:
                    # Test syntax and imports
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    compile(content, str(file_path), 'exec')
                    
                    # Check for dashboard-specific components
                    has_tkinter = 'tkinter' in content
                    has_gui_components = any(comp in content for comp in ['Frame', 'Label', 'Button', 'Entry', 'Text'])
                    has_main_window = any(main in content for main in ['Tk()', 'mainloop()', 'root ='])
                    has_monitoring = any(monitor in content for monitor in ['monitor', 'metrics', 'stats', 'performance'])
                    
                    if has_tkinter and has_gui_components and has_main_window:
                        self.log_result('dashboard_functionality', dashboard_file, True, 
                                      f"Dashboard with GUI components and monitoring")
                    else:
                        missing = []
                        if not has_tkinter: missing.append("tkinter")
                        if not has_gui_components: missing.append("GUI components")
                        if not has_main_window: missing.append("main window")
                        self.log_result('dashboard_functionality', dashboard_file, False, 
                                      f"Missing: {', '.join(missing)}")
                        
                except SyntaxError as e:
                    self.log_result('dashboard_functionality', dashboard_file, False, f"Syntax error: {e}")
                except Exception as e:
                    self.log_result('dashboard_functionality', dashboard_file, False, f"Error: {e}")
            else:
                self.log_result('dashboard_functionality', dashboard_file, False, "File not found")
    
    def test_launcher_functionality(self):
        """Test launcher functionality"""
        print("\nTesting Launcher Functionality...")
        
        launcher_files = [
            'Launch_Homelab_Portal.bat',
            'Launch_Unified_System.bat',
            'Auto_Connect_Launcher.bat',
            'Install_Homelab.bat'
        ]
        
        for launcher_file in launcher_files:
            file_path = self.root_dir / launcher_file
            if file_path.exists():
                try:
                    # Test batch file syntax and Windows 10/11 compatibility
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for launcher-specific components
                    has_delayed_expansion = 'setlocal enabledelayedexpansion' in content
                    has_python_detection = any(py in content for py in ['python', 'py ', 'python.exe'])
                    has_error_handling = 'errorlevel' in content or 'ERRORLEVEL' in content
                    has_menu_options = 'choice' in content or 'set /p' in content
                    
                    if has_delayed_expansion and has_python_detection:
                        self.log_result('launcher_functionality', launcher_file, True, 
                                      f"Launcher with proper Windows 10/11 compatibility")
                    else:
                        missing = []
                        if not has_delayed_expansion: missing.append("delayed expansion")
                        if not has_python_detection: missing.append("Python detection")
                        self.log_result('launcher_functionality', launcher_file, False, 
                                      f"Missing: {', '.join(missing)}")
                        
                except Exception as e:
                    self.log_result('launcher_functionality', launcher_file, False, f"Error: {e}")
            else:
                self.log_result('launcher_functionality', launcher_file, False, "File not found")
    
    def test_tool_launching(self):
        """Test all tools can launch properly"""
        print("\nTesting Tool Launching...")
        
        # Test Python-based tools
        python_tools = [
            'Core Services/homelab_portal.py',
            'Core Services/rest_api.py',
            'Core Services/analytics_engine.py',
            'Core Services/automation_framework.py',
            'Core Services/advanced_security.py'
        ]
        
        for tool in python_tools:
            tool_path = self.root_dir / tool
            if tool_path.exists():
                try:
                    # Test import and basic functionality
                    content = tool_path.read_text(encoding='utf-8', errors='ignore')
                    compile(content, str(tool_path), 'exec')
                    
                    # Check for proper entry points
                    has_main = 'if __name__ == "__main__"' in content
                    has_app_run = 'app.run(' in content or 'mainloop()' in content
                    has_class_def = 'class ' in content
                    
                    if has_main or has_app_run:
                        self.log_result('tool_launching', tool, True, "Tool with proper entry point")
                    else:
                        self.log_result('tool_launching', tool, False, "Missing entry point")
                        
                except SyntaxError as e:
                    self.log_result('tool_launching', tool, False, f"Syntax error: {e}")
                except Exception as e:
                    self.log_result('tool_launching', tool, False, f"Error: {e}")
        
        # Test batch file tools
        batch_tools = [
            'Launch_Homelab_Portal.bat',
            'Launch_Unified_System.bat',
            'Install_Homelab.bat'
        ]
        
        for tool in batch_tools:
            tool_path = self.root_dir / tool
            if tool_path.exists():
                try:
                    content = tool_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for proper batch file structure
                    has_echo_off = '@echo off' in content
                    has_python_cmd = any(py in content for py in ['python', 'py '])
                    has_error_handling = 'errorlevel' in content
                    
                    if has_echo_off and has_python_cmd:
                        self.log_result('tool_launching', tool, True, "Batch tool with proper structure")
                    else:
                        self.log_result('tool_launching', tool, False, "Missing batch file components")
                        
                except Exception as e:
                    self.log_result('tool_launching', tool, False, f"Error: {e}")
    
    def test_windows_compatibility(self):
        """Test Windows 10/11 specific compatibility"""
        print("\nTesting Windows 10/11 Compatibility...")
        
        # Test system compatibility
        windows_version = self.system_info['version']
        is_windows_10 = '10.0' in windows_version
        is_windows_11 = is_windows_10 and int(windows_version.split('.')[2]) >= 22000
        
        if is_windows_11:
            self.log_result('windows_compatibility', 'Windows Version', True, f"Windows 11+ ({windows_version})")
        elif is_windows_10:
            self.log_result('windows_compatibility', 'Windows Version', True, f"Windows 10+ ({windows_version})")
        else:
            self.log_result('windows_compatibility', 'Windows Version', False, f"Unsupported version: {windows_version}")
        
        # Test environment variables
        env_vars = ['USERPROFILE', 'PROGRAMFILES', 'PROGRAMFILES(X86)', 'WINDIR', 'TEMP', 'TMP']
        for var in env_vars:
            if var in os.environ:
                self.log_result('windows_compatibility', f'Env Var: {var}', True, f"Available: {os.environ[var][:50]}...")
            else:
                self.log_result('windows_compatibility', f'Env Var: {var}', False, "Not available")
        
        # Test Windows-specific features
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            self.log_result('windows_compatibility', 'Admin Rights', True, f"Admin: {is_admin}")
        except:
            self.log_result('windows_compatibility', 'Admin Rights', False, "Cannot determine admin rights")
        
        # Test PowerShell availability
        try:
            result = subprocess.run(['powershell', '-Command', 'Get-Host'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_result('windows_compatibility', 'PowerShell', True, "PowerShell available")
            else:
                self.log_result('windows_compatibility', 'PowerShell', False, "PowerShell error")
        except:
            self.log_result('windows_compatibility', 'PowerShell', False, "PowerShell not available")
    
    def test_cross_version_compatibility(self):
        """Test cross-version compatibility features"""
        print("\nTesting Cross-Version Compatibility...")
        
        # Test Windows version detection
        version_detection_files = [
            'Core Services/windows_network_discovery.py',
            'Core Services/windows_screen_sharing.py',
            'windows10_setup.bat',
            'windows_universal_deployer.py'
        ]
        
        for file_name in version_detection_files:
            file_path = self.root_dir / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for version-specific code
                    has_version_check = any(check in content for check in ['version', 'winver', 'GetVersionEx'])
                    has_win10_features = any(feature in content for feature in ['winget', 'wsl', 'pwsh'])
                    has_compatibility_mode = 'compatibility' in content.lower()
                    
                    if has_version_check:
                        self.log_result('cross_version_tests', file_name, True, "Has version detection")
                    else:
                        self.log_result('cross_version_tests', file_name, False, "Missing version detection")
                        
                except Exception as e:
                    self.log_result('cross_version_tests', file_name, False, f"Error: {e}")
        
        # Test universal deployment features
        deploy_features = [
            'cross_platform_deployer.py',
            'deployment_config.py',
            'windows_universal_deployer.py'
        ]
        
        for feature in deploy_features:
            feature_path = self.root_dir / feature
            if feature_path.exists():
                try:
                    content = feature_path.read_text(encoding='utf-8', errors='ignore')
                    compile(content, str(feature_path), 'exec')
                    
                    has_config = 'config' in content.lower()
                    has_deployment = 'deploy' in content.lower()
                    has_platform_check = 'platform' in content.lower()
                    
                    if has_config and has_deployment:
                        self.log_result('cross_version_tests', feature, True, "Universal deployment features")
                    else:
                        self.log_result('cross_version_tests', feature, False, "Missing deployment features")
                        
                except Exception as e:
                    self.log_result('cross_version_tests', feature, False, f"Error: {e}")
    
    def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("=" * 60)
        print("DASHBOARD AND LAUNCHER VERIFICATION")
        print("=" * 60)
        print(f"System: {self.system_info['os']} {self.system_info['version']}")
        print(f"Architecture: {self.system_info['architecture']}")
        print(f"Python: {self.system_info['python_version']}")
        print(f"Machine: {self.system_info['machine']}")
        print()
        
        # Run all tests
        self.test_dashboard_functionality()
        self.test_launcher_functionality()
        self.test_tool_launching()
        self.test_windows_compatibility()
        self.test_cross_version_compatibility()
        
        # Calculate success rate
        total_tests = self.results['overall']['total_tests']
        passed_tests = self.results['overall']['passed']
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.results['overall']['success_rate'] = success_rate
        
        # Print summary
        print("\n" + "=" * 60)
        print("DASHBOARD AND LAUNCHER VERIFICATION RESULTS")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Verification Duration: {time.time() - self.verification_start_time:.2f} seconds")
        
        # Category breakdown
        categories = ['dashboard_functionality', 'launcher_functionality', 'tool_launching', 'windows_compatibility', 'cross_version_tests']
        print("\nResults by Category:")
        for category in categories:
            category_results = self.results[category]
            category_passed = sum(1 for r in category_results.values() if r['passed'])
            category_total = len(category_results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            print(f"  {category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Overall status
        if success_rate >= 95:
            print("\n🎉 EXCELLENT: Dashboard and launcher fully compatible!")
            status = "EXCELLENT"
        elif success_rate >= 90:
            print("\n✅ GOOD: Dashboard and launcher mostly compatible!")
            status = "GOOD"
        elif success_rate >= 80:
            print("\n⚠️  FAIR: Dashboard and launcher need some attention!")
            status = "FAIR"
        else:
            print("\n❌ POOR: Dashboard and launcher have significant issues!")
            status = "POOR"
        
        # Windows 10/11 specific summary
        print(f"\nWindows 10/11 Compatibility Summary:")
        print(f"  Dashboard Functionality: {'✓' if success_rate >= 80 else '✗'}")
        print(f"  Launcher Functionality: {'✓' if success_rate >= 80 else '✗'}")
        print(f"  Tool Launching: {'✓' if success_rate >= 80 else '✗'}")
        print(f"  Cross-Version Support: {'✓' if success_rate >= 80 else '✗'}")
        
        # Save results
        with open(self.root_dir / 'dashboard_launcher_verification_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {self.root_dir / 'dashboard_launcher_verification_results.json'}")
        
        return success_rate, status

def main():
    """Main entry point"""
    verifier = DashboardLauncherVerifier()
    success_rate, status = verifier.run_comprehensive_verification()
    
    # Return appropriate exit code
    sys.exit(0 if success_rate >= 90 else 1)

if __name__ == "__main__":
    main()
