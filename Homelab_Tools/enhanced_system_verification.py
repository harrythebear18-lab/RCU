#!/usr/bin/env python3
"""
Enhanced System Verification - Catches fundamental issues like window scaling and missing functionality
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class EnhancedSystemVerifier:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'score': 0}
        }
        self.issues_found = []
    
    def log_result(self, category, check_name, passed, details=""):
        """Log verification result"""
        if category not in self.results['checks']:
            self.results['checks'][category] = []
        
        result = {
            'name': check_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results['checks'][category].append(result)
        self.results['summary']['total'] += 1
        
        if passed:
            self.results['summary']['passed'] += 1
            print(f"✓ {category} - {check_name}: {details}")
        else:
            self.results['summary']['failed'] += 1
            self.issues_found.append(f"{category} - {check_name}: {details}")
            print(f"✗ {category} - {check_name}: {details}")
    
    def verify_cpu_monitor_comprehensive(self):
        """Comprehensive CPU Monitor validation - catches fundamental issues"""
        print("\n" + "="*60)
        print("COMPREHENSIVE CPU MONITOR VERIFICATION")
        print("="*60)
        
        cpu_monitor_path = self.root_dir / "Cpu Monitor" / "cpu_monitor.py"
        
        if not cpu_monitor_path.exists():
            self.log_result('cpu_monitor', 'file_exists', False, "CPU Monitor file missing")
            return
        
        self.log_result('cpu_monitor', 'file_exists', True, "CPU Monitor file found")
        
        try:
            content = cpu_monitor_path.read_text(encoding='utf-8', errors='ignore')
            
            # 1. Essential Imports Check
            essential_imports = {
                'tkinter': 'GUI framework',
                'psutil': 'System monitoring',
                'matplotlib': 'Graphing library',
                'threading': 'Multi-threading support',
                'platform': 'Platform detection',
                'collections.deque': 'Data storage',
                'time': 'Time functions'
            }
            
            for imp, desc in essential_imports.items():
                if imp in content:
                    self.log_result('cpu_monitor', f'import_{imp}', True, f"{desc} imported")
                else:
                    self.log_result('cpu_monitor', f'import_{imp}', False, f"{desc} missing")
            
            # 2. Window Scaling & UI Fundamentals
            window_checks = {
                'geometry("1200x800")': 'Proper window size',
                'minsize(800, 600)': 'Minimum window size',
                'setup_window_scaling': 'Window scaling method',
                'setup_window_bindings': 'Window event bindings',
                'on_window_resize': 'Resize handler',
                'tk.call(\'tk\', \'scaling\'': 'DPI awareness',
                'winfo_screenwidth': 'Screen detection',
                'attributes(\'-fullscreen\'': 'Fullscreen support'
            }
            
            for check, desc in window_checks.items():
                if check in content:
                    self.log_result('cpu_monitor', f'window_{check[:20]}', True, desc)
                else:
                    self.log_result('cpu_monitor', f'window_{check[:20]}', False, f"Missing: {desc}")
            
            # 3. Core Data Collection Methods
            data_checks = {
                'psutil.cpu_percent()': 'Overall CPU usage',
                'psutil.cpu_percent(percpu=True)': 'Per-core CPU usage',
                'psutil.cpu_count(logical=False)': 'Physical cores',
                'psutil.cpu_count(logical=True)': 'Logical cores',
                'psutil.cpu_freq()': 'CPU frequency',
                'psutil.sensors_temperatures()': 'Temperature sensors',
                'psutil.sensors_power()': 'Power sensors',
                'psutil.getloadavg()': 'Load averages',
                'psutil.virtual_memory()': 'Memory info',
                'deque(maxlen=60)': 'Data history storage'
            }
            
            for check, desc in data_checks.items():
                if check in content:
                    self.log_result('cpu_monitor', f'data_{check[:15]}', True, desc)
                else:
                    self.log_result('cpu_monitor', f'data_{check[:15]}', False, f"Missing: {desc}")
            
            # 4. Essential Methods & Classes
            method_checks = {
                'class CPUMonitor': 'Main CPU Monitor class',
                '__init__(self, root)': 'Constructor',
                'setup_window_scaling': 'Window scaling setup',
                'create_main_interface': 'Main interface creation',
                'create_system_info_frame': 'System info display',
                'create_monitoring_display': 'Monitoring display',
                'create_process_management': 'Process management',
                'monitor_cpu': 'CPU monitoring loop',
                'update_displays': 'Display updates',
                'refresh_processes': 'Process refresh',
                'update_cpu_graph': 'Graph updates',
                'toggle_monitoring': 'Start/stop monitoring',
                'get_cpu_temperature': 'Temperature detection',
                'get_cpu_power': 'Power detection',
                'on_window_close': 'Proper window closing'
            }
            
            for check, desc in method_checks.items():
                if check in content:
                    self.log_result('cpu_monitor', f'method_{check[:15]}', True, desc)
                else:
                    self.log_result('cpu_monitor', f'method_{check[:15]}', False, f"Missing: {desc}")
            
            # 5. Interface Components
            interface_checks = {
                'monitor_notebook': 'Multi-tab interface',
                'core_fig': 'Individual core graphs',
                'core_axes': 'Core graph axes',
                'stats_text': 'Performance statistics',
                'process_tree': 'Process list',
                'TTk.Treeview': 'Treeview component',
                'FigureCanvasTkAgg': 'Canvas for graphs',
                'LabelFrame': 'Label frames for organization'
            }
            
            for check, desc in interface_checks.items():
                if check in content:
                    self.log_result('cpu_monitor', f'interface_{check[:15]}', True, desc)
                else:
                    self.log_result('cpu_monitor', f'interface_{check[:15]}', False, f"Missing: {desc}")
            
            # 6. Real-time Functionality
            realtime_checks = {
                'threading.Thread': 'Threading support',
                'daemon=True': 'Daemon threads',
                'self.monitoring = False': 'Monitoring state',
                'time.sleep(1)': 'Update interval',
                'root.after(0': 'Thread-safe GUI updates',
                'while self.monitoring:': 'Monitoring loop'
            }
            
            for check, desc in realtime_checks.items():
                if check in content:
                    self.log_result('cpu_monitor', f'realtime_{check[:15]}', True, desc)
                else:
                    self.log_result('cpu_monitor', f'realtime_{check[:15]}', False, f"Missing: {desc}")
            
            # 7. Error Handling & Robustness
            robustness_checks = {
                'try:': 'Error handling blocks',
                'except Exception': 'Exception catching',
                'print(f"': 'Debug output',
                'hasattr': 'Attribute checking',
                'if not': 'Condition checking'
            }
            
            for check, desc in robustness_checks.items():
                if check in content:
                    self.log_result('cpu_monitor', f'robust_{check[:15]}', True, desc)
                else:
                    self.log_result('cpu_monitor', f'robust_{check[:15]}', False, f"Missing: {desc}")
            
            # 8. Runtime Testing
            try:
                import sys
                sys.path.append(str(self.root_dir / "Cpu Monitor"))
                
                # Test psutil functionality
                import psutil
                
                cpu_count = psutil.cpu_count()
                cpu_logical = psutil.cpu_count(logical=True)
                cpu_percent = psutil.cpu_percent()
                cpu_freq = psutil.cpu_freq()
                
                self.log_result('cpu_monitor_runtime', 'cpu_count', True, f"Physical cores: {cpu_count}")
                self.log_result('cpu_monitor_runtime', 'cpu_logical', True, f"Logical cores: {cpu_logical}")
                self.log_result('cpu_monitor_runtime', 'cpu_percent', True, f"Current usage: {cpu_percent:.1f}%")
                self.log_result('cpu_monitor_runtime', 'cpu_freq', cpu_freq is not None, f"Frequency available: {cpu_freq is not None}")
                
                # Test sensors
                try:
                    temps = psutil.sensors_temperatures()
                    self.log_result('cpu_monitor_runtime', 'temperature_sensors', True, f"Temperature sensors: {len(temps) if temps else 0}")
                except:
                    self.log_result('cpu_monitor_runtime', 'temperature_sensors', False, "Temperature sensors not available")
                
                try:
                    power = psutil.sensors_power()
                    self.log_result('cpu_monitor_runtime', 'power_sensors', True, f"Power sensors: {len(power) if power else 0}")
                except:
                    self.log_result('cpu_monitor_runtime', 'power_sensors', False, "Power sensors not available")
                
                # Test load averages
                try:
                    load_avg = psutil.getloadavg()
                    self.log_result('cpu_monitor_runtime', 'load_average', True, f"Load averages: {load_avg}")
                except:
                    self.log_result('cpu_monitor_runtime', 'load_average', False, "Load averages not available")
                
            except Exception as e:
                self.log_result('cpu_monitor_runtime', 'runtime_test', False, f"Runtime test failed: {e}")
            
        except Exception as e:
            self.log_result('cpu_monitor', 'file_read', False, f"Error reading file: {e}")
    
    def verify_other_tools_basic(self):
        """Basic verification of other tools"""
        print("\n" + "="*60)
        print("BASIC OTHER TOOLS VERIFICATION")
        print("="*60)
        
        tools_to_check = {
            'GPU Monitor': 'Gpu Monitor/gpu_monitor.py',
            'Network Monitor': 'Network Monitor/network_monitor.py',
            'Launcher': 'homelab_launcher.py',
            'Unified Dashboard': 'Core Services/unified_dashboard.py'
        }
        
        for tool_name, file_path in tools_to_check.items():
            full_path = self.root_dir / file_path
            
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Basic checks
                    checks = {
                        'tkinter': 'GUI framework',
                        'class': 'Main class',
                        'def __init__': 'Constructor',
                        'def create': 'Interface creation',
                        'pack(': 'Layout management'
                    }
                    
                    for check, desc in checks.items():
                        if check in content:
                            self.log_result(f'{tool_name}_basic', check, True, desc)
                        else:
                            self.log_result(f'{tool_name}_basic', check, False, f"Missing: {desc}")
                
                except Exception as e:
                    self.log_result(tool_name, 'file_read', False, f"Error reading {file_path}: {e}")
            else:
                self.log_result(tool_name, 'file_exists', False, f"{file_path} missing")
    
    def calculate_score(self):
        """Calculate overall score"""
        if self.results['summary']['total'] > 0:
            self.results['summary']['score'] = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
        else:
            self.results['summary']['score'] = 0
    
    def generate_report(self):
        """Generate comprehensive report"""
        self.calculate_score()
        
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        print(f"Total Checks: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Score: {self.results['summary']['score']:.1f}%")
        
        if self.issues_found:
            print("\nISSUES FOUND:")
            for issue in self.issues_found[:10]:  # Show first 10 issues
                print(f"  - {issue}")
            if len(self.issues_found) > 10:
                print(f"  ... and {len(self.issues_found) - 10} more issues")
        
        # Save detailed report
        report_file = self.root_dir / "enhanced_verification_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return self.results['summary']['score']
    
    def run_all_checks(self):
        """Run all verification checks"""
        self.verify_cpu_monitor_comprehensive()
        self.verify_other_tools_basic()
        return self.generate_report()

def main():
    """Main verification runner"""
    verifier = EnhancedSystemVerifier()
    score = verifier.run_all_checks()
    
    if score >= 90:
        print("\n🎉 EXCELLENT: System verification passed with high score!")
    elif score >= 75:
        print("\n✅ GOOD: System verification passed with decent score!")
    elif score >= 60:
        print("\n⚠️  FAIR: System has some issues that need attention")
    else:
        print("\n❌ POOR: System has significant issues that need fixing")
    
    return score

if __name__ == "__main__":
    main()
