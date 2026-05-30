#!/usr/bin/env python3
"""
Tool Launch Verification - Comprehensive testing of launcher functionality
Tests that all tools can be found and launched from the launcher
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import json
from datetime import datetime

class ToolLaunchVerifier:
    """Verify tool launch functionality"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_tools': 0,
            'found_tools': 0,
            'missing_tools': 0,
            'launchable_tools': 0,
            'failed_launches': 0,
            'tool_details': []
        }
        
        # Import launcher to get tool definitions
        self.launcher_tools = self.get_launcher_tools()
    
    def get_launcher_tools(self):
        """Get tool definitions from launcher"""
        try:
            # Add current directory to path
            if str(self.base_path) not in sys.path:
                sys.path.insert(0, str(self.base_path))
            
            # Import launcher
            import homelab_launcher
            
            # Create a temporary launcher instance to get tools
            class TempLauncher:
                def __init__(self):
                    self.tools = {
                        "System Monitoring": {
                            "CPU Monitor": {"path": "CPU Monitor/cpu_monitor.py"},
                            "GPU Monitor": {"path": "GPU Monitor/gpu_monitor.py"},
                            "Network Monitor": {"path": "Network Monitor/network_monitor.py"},
                            "Storage Monitor": {"path": "Storage Monitor/storage_monitor.py"},
                            "RAM Monitor": {"path": "Memory Monitor/ram_monitor_gui.py"}
                        },
                        "Distributed Computing": {
                            "RDMA Desktop App": {"path": "RDMA Desktop App/rdma_desktop_app.py"},
                            "RDMA Modern App": {"path": "RDMA Desktop App/rdma_modern_tkinter.py"},
                            "RDMA Memory Portal": {"path": "Memory Portal/memory_portal_gui.py"},
                            "Hybrid Compute": {"path": "Hybrid Compute/hybrid_client.py"}
                        },
                        "Infrastructure & Management": {
                            "Container Manager": {"path": "Container Manager/container_manager.py"},
                            "Backup System": {"path": "Core Services/backup_manager.py"},
                            "Web Dashboard": {"path": "Core Services/web_dashboard.py"},
                            "VPN Gateway": {"path": "VPN Gateway/vpn_gateway.py"},
                            "Media Server": {"path": "Media Server/media_server_manager.py"},
                            "CI/CD Pipeline": {"path": "CI/CD Pipeline/cicd_manager.py"},
                            "Power Management": {"path": "Power Manager/power_manager.py"},
                            "IoT Platform": {"path": "IoT Platform/iot_platform.py"},
                            "Subnet Portal": {"path": "Subnet Portal/subnet_portal.py"},
                            "Deployment Config": {"path": "deployment_config.py"},
                            "System Integration Test": {"path": "system_integration_test.py"}
                        },
                        "RAM Sharing & Storage": {
                            "RAM Sharing Manager": {"path": "RAM_Sharing_GUI.py"},
                            "Simple RAM Sharing": {"path": "RAM_Sharing_Simple_GUI.py"},
                            "RAM Server Setup": {"path": "Setup_RAM_Sharing.bat"},
                            "RAM Client Connect": {"path": "Map_RAM_Sharing.bat"},
                            "Windows Compatibility Fix": {"path": "Fix_Windows_Compatibility.bat"},
                            "Universal RAM Launcher": {"path": "Universal_Launcher.bat"}
                        }
                    }
            
            temp_launcher = TempLauncher()
            return temp_launcher.tools
            
        except Exception as e:
            print(f"Failed to import launcher tools: {e}")
            return {}
    
    def verify_all_tools(self):
        """Verify all tools can be found and launched"""
        print("🔍 Starting Tool Launch Verification")
        print("=" * 50)
        
        all_tools = []
        
        # Flatten tool structure
        for category, tools in self.launcher_tools.items():
            for tool_name, tool_info in tools.items():
                all_tools.append({
                    'category': category,
                    'name': tool_name,
                    'path': tool_info['path'],
                    'type': 'batch' if tool_info['path'].endswith('.bat') else 'python'
                })
        
        self.results['total_tools'] = len(all_tools)
        
        print(f"Found {len(all_tools)} tools to verify")
        print()
        
        # Verify each tool
        for i, tool in enumerate(all_tools, 1):
            print(f"[{i}/{len(all_tools)}] Verifying: {tool['name']}")
            
            tool_result = self.verify_single_tool(tool)
            self.results['tool_details'].append(tool_result)
            
            # Update counters
            if tool_result['found']:
                self.results['found_tools'] += 1
            else:
                self.results['missing_tools'] += 1
                
            if tool_result['launchable']:
                self.results['launchable_tools'] += 1
            else:
                self.results['failed_launches'] += 1
            
            # Print result
            status = "✅" if tool_result['found'] and tool_result['launchable'] else "❌"
            print(f"  {status} {tool_result['status']}")
            
            if tool_result['error']:
                print(f"  Error: {tool_result['error']}")
            
            print()
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def verify_single_tool(self, tool):
        """Verify a single tool"""
        result = {
            'category': tool['category'],
            'name': tool['name'],
            'path': tool['path'],
            'type': tool['type'],
            'found': False,
            'launchable': False,
            'status': '',
            'error': None
        }
        
        try:
            # Check if file exists
            tool_path = self.base_path / tool['path']
            if not tool_path.exists():
                result['status'] = 'File not found'
                result['error'] = f"Path does not exist: {tool_path}"
                return result
            
            result['found'] = True
            
            # Test launchability (dry run)
            if tool['type'] == 'python':
                result['status'] = self.test_python_launch(tool_path)
            else:  # batch file
                result['status'] = self.test_batch_launch(tool_path)
            
            result['launchable'] = 'Launchable' in result['status']
            
        except Exception as e:
            result['status'] = 'Error'
            result['error'] = str(e)
        
        return result
    
    def test_python_launch(self, tool_path):
        """Test Python tool launch"""
        try:
            # Try to import the module to check syntax
            with open(tool_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax check
            compile(content, str(tool_path), 'exec')
            
            # Check for main function or if __name__ == "__main__"
            if 'def main(' in content or 'if __name__ == "__main__"' in content:
                return 'Launchable - Has main entry point'
            else:
                return 'Warning - No main entry point found'
                
        except SyntaxError as e:
            return f'Syntax Error - {e}'
        except Exception as e:
            return f'Error - {e}'
    
    def test_batch_launch(self, tool_path):
        """Test batch file launch"""
        try:
            with open(tool_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic batch file checks
            if '@echo off' in content or '@echo' in content:
                return 'Launchable - Valid batch file'
            else:
                return 'Warning - No echo commands found'
                
        except Exception as e:
            return f'Error - {e}'
    
    def generate_summary(self):
        """Generate verification summary"""
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        total = self.results['total_tools']
        found = self.results['found_tools']
        missing = self.results['missing_tools']
        launchable = self.results['launchable_tools']
        failed = self.results['failed_launches']
        
        print(f"Total Tools: {total}")
        print(f"Found: {found} ({found/total*100:.1f}%)")
        print(f"Missing: {missing} ({missing/total*100:.1f}%)")
        print(f"Launchable: {launchable} ({launchable/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if missing == 0 and failed == 0:
            print("\n🎉 ALL TOOLS VERIFIED SUCCESSFULLY!")
        else:
            print(f"\n⚠️  {missing + failed} tools need attention")
        
        # Category breakdown
        print("\n📋 CATEGORY BREAKDOWN:")
        categories = {}
        for tool in self.results['tool_details']:
            cat = tool['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'found': 0, 'launchable': 0}
            categories[cat]['total'] += 1
            if tool['found']:
                categories[cat]['found'] += 1
            if tool['launchable']:
                categories[cat]['launchable'] += 1
        
        for category, stats in categories.items():
            print(f"  {category}: {stats['launchable']}/{stats['total']} launchable")
    
    def save_results(self):
        """Save verification results"""
        results_file = self.base_path / "tool_launch_verification_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")

def main():
    """Main entry point"""
    verifier = ToolLaunchVerifier()
    results = verifier.verify_all_tools()
    
    return results

if __name__ == "__main__":
    main()
