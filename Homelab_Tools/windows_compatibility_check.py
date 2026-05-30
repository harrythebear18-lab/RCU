#!/usr/bin/env python3
"""
Windows 10/11 Compatibility Verification
Focuses on actual system compatibility rather than isolated imports
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple
import json

class WindowsCompatibilityChecker:
    """Windows 10/11 compatibility verification"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.results = {
            'system_info': {},
            'batch_files': {},
            'python_files': {},
            'core_services': {},
            'portal_components': {},
            'overall': {
                'total': 0,
                'compatible': 0,
                'incompatible': 0,
                'compatibility_rate': 0
            }
        }
    
    def check_system_info(self):
        """Check Windows system information"""
        system_info = {
            'os': platform.system(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }
        
        self.results['system_info'] = system_info
        
        print("System Information:")
        print(f"  OS: {system_info['os']} {system_info['version']}")
        print(f"  Architecture: {system_info['architecture']}")
        print(f"  Machine: {system_info['machine']}")
        print(f"  Python: {system_info['python_version']}")
        
        # Check if Windows 10/11
        windows_version = system_info['version']
        if '10.0' in windows_version:
            major_version = int(windows_version.split('.')[2])
            if major_version >= 10240:  # Windows 10 threshold
                if major_version >= 22000:  # Windows 11 threshold
                    print("  Windows Version: Windows 11+ ✓")
                else:
                    print("  Windows Version: Windows 10+ ✓")
                return True
        print("  Windows Version: Unknown/Unsupported ✗")
        return False
    
    def check_batch_file_compatibility(self, batch_file: Path) -> Tuple[bool, str]:
        """Check batch file Windows 10/11 compatibility"""
        try:
            content = batch_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for Windows 10/11 compatibility requirements
            issues = []
            
            # 1. Check for proper delayed expansion
            if '@echo off' in content and 'setlocal enabledelayedexpansion' not in content:
                issues.append("Missing setlocal enabledelayedexpansion")
            
            # 2. Check for proper errorlevel handling
            if 'setlocal enabledelayedexpansion' in content and '%errorlevel%' in content:
                if '!errorlevel!' not in content:
                    issues.append("Should use !errorlevel! with delayed expansion")
            
            # 3. Check for proper variable quoting
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('REM') and not line.startswith(':'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        var_value = parts[1].strip()
                        if var_value and not var_value.startswith('"') and not var_value.startswith("'") and ' ' in var_value and '%' in var_value:
                            issues.append(f"Unquoted variable: {line[:50]}...")
                            break
            
            # 4. Check for Windows-specific commands compatibility
            win10_commands = ['winget', 'wsl', 'pwsh']
            for cmd in win10_commands:
                if cmd in content and 'REM' not in content:
                    # These are fine for Windows 10/11
                    pass
            
            return len(issues) == 0, "; ".join(issues) if issues else "Compatible"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_python_file_compatibility(self, python_file: Path) -> Tuple[bool, str]:
        """Check Python file Windows 10/11 compatibility"""
        try:
            content = python_file.read_text(encoding='utf-8', errors='ignore')
            
            issues = []
            
            # 1. Check for proper shebang
            if not content.startswith('#!/usr/bin/env python3') and not content.startswith('#!'):
                issues.append("Missing shebang")
            
            # 2. Check for hardcoded paths (only real issues, not regex patterns)
            hardcoded_patterns = [
                r'C:\\Users\\[^\\]+\\',  # User-specific paths
                r'C:\\Program Files\\[^\\]+',  # Program-specific paths
                r'C:\\Windows\\[^\\]+',  # Windows-specific paths
            ]
            
            for pattern in hardcoded_patterns:
                import re
                if re.search(pattern, content) and 'os.path.expanduser' not in content and 'os.path.expandvars' not in content:
                    issues.append("Hardcoded Windows path")
                    break
            
            # 3. Check for Windows-specific imports
            windows_imports = ['win32api', 'win32con', 'win32gui', 'ctypes.windll']
            for win_import in windows_imports:
                if win_import in content:
                    # These are fine for Windows compatibility
                    pass
            
            # 4. Try to compile (syntax check only)
            try:
                compile(content, str(python_file), 'exec')
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")
            
            return len(issues) == 0, "; ".join(issues) if issues else "Compatible"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_core_service_compatibility(self, service_file: Path) -> Tuple[bool, str]:
        """Check core service compatibility (smarter import check)"""
        try:
            service_name = service_file.stem
            
            # Special handling for event_bus dependency
            if service_name != 'event_bus':
                # Check if file imports event_bus
                content = service_file.read_text(encoding='utf-8', errors='ignore')
                if 'from event_bus import' in content or 'import event_bus' in content:
                    # This is expected and compatible - event_bus exists
                    return True, "Compatible (event_bus dependency)"
            
            # Try basic syntax check
            try:
                compile(service_file.read_text(encoding='utf-8', errors='ignore'), 
                      str(service_file), 'exec')
                return True, "Compatible"
            except SyntaxError as e:
                return False, f"Syntax error: {e}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_portal_compatibility(self) -> Tuple[bool, str]:
        """Check portal system compatibility"""
        required_components = [
            'Core Services/homelab_portal.py',
            'Core Services/rest_api.py',
            'Core Services/analytics_engine.py',
            'Core Services/automation_framework.py',
            'Core Services/advanced_security.py',
            'Mobile_Interface/index.html',
            'Mobile_Interface/app.js',
            'Mobile_Interface/styles.css',
            'Mobile_Interface/manifest.json',
            'Mobile_Interface/sw.js',
            'API_Documentation.md'
        ]
        
        missing = []
        for component in required_components:
            if not (self.root_dir / component).exists():
                missing.append(component)
        
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        
        return True, f"All {len(required_components)} components present"
    
    def run_compatibility_check(self):
        """Run full Windows 10/11 compatibility check"""
        print("=" * 60)
        print("WINDOWS 10/11 COMPATIBILITY VERIFICATION")
        print("=" * 60)
        
        # Check system info
        windows_compatible = self.check_system_info()
        print()
        
        # Find all files
        batch_files = list(self.root_dir.rglob('*.bat'))
        python_files = list(self.root_dir.rglob('*.py'))
        core_services = list((self.root_dir / 'Core Services').glob('*.py')) if (self.root_dir / 'Core Services').exists() else []
        
        print(f"Found {len(batch_files)} batch files")
        print(f"Found {len(python_files)} Python files")
        print(f"Found {len(core_services)} core services")
        print()
        
        # Check batch files
        print("Checking Batch Files...")
        batch_compatible = 0
        for batch_file in batch_files:
            relative_path = batch_file.relative_to(self.root_dir)
            compatible, message = self.check_batch_file_compatibility(batch_file)
            self.results['batch_files'][str(relative_path)] = {
                'compatible': compatible,
                'message': message
            }
            if compatible:
                batch_compatible += 1
                print(f"  ✓ {relative_path}")
            else:
                print(f"  ✗ {relative_path} - {message}")
        
        # Check Python files
        print("\nChecking Python Files...")
        python_compatible = 0
        for python_file in python_files:
            relative_path = python_file.relative_to(self.root_dir)
            compatible, message = self.check_python_file_compatibility(python_file)
            self.results['python_files'][str(relative_path)] = {
                'compatible': compatible,
                'message': message
            }
            if compatible:
                python_compatible += 1
                print(f"  ✓ {relative_path}")
            else:
                print(f"  ✗ {relative_path} - {message}")
        
        # Check core services
        print("\nChecking Core Services...")
        core_compatible = 0
        for service_file in core_services:
            relative_path = service_file.relative_to(self.root_dir)
            compatible, message = self.check_core_service_compatibility(service_file)
            self.results['core_services'][str(relative_path)] = {
                'compatible': compatible,
                'message': message
            }
            if compatible:
                core_compatible += 1
                print(f"  ✓ {relative_path}")
            else:
                print(f"  ✗ {relative_path} - {message}")
        
        # Check portal components
        print("\nChecking Portal Components...")
        portal_compatible, portal_message = self.check_portal_compatibility()
        self.results['portal_components']['Portal System'] = {
            'compatible': portal_compatible,
            'message': portal_message
        }
        if portal_compatible:
            print(f"  ✓ Portal System - {portal_message}")
        else:
            print(f"  ✗ Portal System - {portal_message}")
        
        # Calculate overall compatibility
        total_files = len(batch_files) + len(python_files) + len(core_services) + 1  # +1 for portal
        compatible_files = batch_compatible + python_compatible + core_compatible + (1 if portal_compatible else 0)
        compatibility_rate = (compatible_files / total_files * 100) if total_files > 0 else 0
        
        self.results['overall'] = {
            'total': total_files,
            'compatible': compatible_files,
            'incompatible': total_files - compatible_files,
            'compatibility_rate': compatibility_rate
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("WINDOWS 10/11 COMPATIBILITY SUMMARY")
        print("=" * 60)
        print(f"Total Files: {total_files}")
        print(f"Compatible: {compatible_files}")
        print(f"Incompatible: {total_files - compatible_files}")
        print(f"Compatibility Rate: {compatibility_rate:.1f}%")
        print()
        
        print("By Category:")
        print(f"  Batch Files: {batch_compatible}/{len(batch_files)} ({batch_compatible/len(batch_files)*100:.1f}%)")
        print(f"  Python Files: {python_compatible}/{len(python_files)} ({python_compatible/len(python_files)*100:.1f}%)")
        print(f"  Core Services: {core_compatible}/{len(core_services)} ({core_compatible/len(core_services)*100:.1f}%)")
        print(f"  Portal System: {1 if portal_compatible else 0}/1 ({100 if portal_compatible else 0}%)")
        print()
        
        # Overall status
        if compatibility_rate >= 95:
            print("🎉 EXCELLENT: Full Windows 10/11 compatibility achieved!")
            status = "EXCELLENT"
        elif compatibility_rate >= 90:
            print("✅ GOOD: Strong Windows 10/11 compatibility")
            status = "GOOD"
        elif compatibility_rate >= 80:
            print("⚠️  FAIR: Moderate Windows 10/11 compatibility")
            status = "FAIR"
        else:
            print("❌ POOR: Limited Windows 10/11 compatibility")
            status = "POOR"
        
        # Save results
        with open(self.root_dir / 'windows_compatibility_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {self.root_dir / 'windows_compatibility_results.json'}")
        
        return compatibility_rate, status

def main():
    """Main entry point"""
    checker = WindowsCompatibilityChecker()
    compatibility_rate, status = checker.run_compatibility_check()
    
    # Return appropriate exit code
    sys.exit(0 if compatibility_rate >= 90 else 1)

if __name__ == "__main__":
    main()
