#!/usr/bin/env python3
"""
Unified Component Counter - Accurate counting of all Homelab Tools components
Fixes the mismatched numbers by using a comprehensive discovery system
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class UnifiedComponentCounter:
    """Unified counter for accurate component discovery"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.results = {
            "total_files": 0,
            "python_files": 0,
            "batch_files": 0,
            "cpp_files": 0,
            "other_files": 0,
            "directories": 0,
            "by_category": {},
            "by_location": {},
            "detailed_breakdown": {}
        }
    
    def count_all_components(self) -> Dict[str, Any]:
        """Count all components accurately"""
        print("🔍 UNIFIED COMPONENT COUNTING")
        print("=" * 50)
        
        # Count by file type
        self.count_by_file_types()
        
        # Count by categories
        self.count_by_categories()
        
        # Count by locations
        self.count_by_locations()
        
        # Generate detailed breakdown
        self.generate_detailed_breakdown()
        
        # Print results
        self.print_results()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def count_by_file_types(self):
        """Count components by file type"""
        print("\n📁 Counting by file types...")
        
        python_files = list(self.base_path.rglob("*.py"))
        batch_files = list(self.base_path.rglob("*.bat"))
        cpp_files = list(self.base_path.rglob("*.cpp"))
        c_files = list(self.base_path.rglob("*.c"))
        h_files = list(self.base_path.rglob("*.h"))
        
        # Filter out certain directories
        def filter_files(files):
            filtered = []
            for file in files:
                path_str = str(file)
                if any(skip in path_str for skip in ['__pycache__', '.git', 'venv', 'env', 'node_modules']):
                    continue
                filtered.append(file)
            return filtered
        
        python_files = filter_files(python_files)
        batch_files = filter_files(batch_files)
        cpp_files = filter_files(cpp_files)
        c_files = filter_files(c_files)
        h_files = filter_files(h_files)
        
        self.results["python_files"] = len(python_files)
        self.results["batch_files"] = len(batch_files)
        self.results["cpp_files"] = len(cpp_files) + len(c_files) + len(h_files)
        self.results["total_files"] = len(python_files) + len(batch_files) + len(cpp_files) + len(c_files) + len(h_files)
        
        print(f"  Python files: {len(python_files)}")
        print(f"  Batch files: {len(batch_files)}")
        print(f"  C/C++ files: {len(cpp_files) + len(c_files) + len(h_files)}")
        print(f"  Total files: {self.results['total_files']}")
    
    def count_by_categories(self):
        """Count components by functional categories"""
        print("\n📂 Counting by categories...")
        
        categories = {
            "Core Applications": [
                "homelab_launcher.py",
                "homelab_launcher_enhanced.py", 
                "homelab_dashboard.py",
                "Visentrix_Launcher.py",
                "Integrated_RAM_Launcher.py"
            ],
            "Mesh VPN Components": [
                "mesh_vpn_server.py",
                "mesh_vpn_client.py", 
                "mesh_service_discovery.py",
                "mesh_app_communication.py",
                "mesh_app_integration.py",
                "mesh_vpn_dashboard.py",
                "wireguard_config_generator.py",
                "bidirectional_mesh_setup.py"
            ],
            "Network Tools": [
                "network_monitor.py",
                "vpn_gateway.py",
                "subnet_manager.py",
                "windows_network_discovery.py"
            ],
            "Monitoring Tools": [
                "gpu_monitor.py",
                "ram_monitor_gui.py",
                "storage_monitor.py",
                "cpu_monitor.py",
                "unified_monitoring.py"
            ],
            "Resource Management": [
                "container_manager.py",
                "backup_manager.py",
                "power_manager.py",
                "media_server_manager.py",
                "iot_platform.py"
            ],
            "Core Services": [
                "web_dashboard.py",
                "unified_dashboard.py",
                "rest_api.py",
                "auth_service.py",
                "config_manager.py",
                "event_bus.py",
                "smart_system_sensing.py"
            ],
            "Setup & Installation": [
                "wireguard_installer.py",
                "install_wireguard.bat",
                "setup.bat",
                "first_time_setup.bat",
                "complete_system_verification.py",
                "fully_comprehensive_system_audit.py",
                "chunked_system_audit.py"
            ],
            "Batch Launchers": [
                "launch_homelab.bat",
                "Launch_Homelab_Portal.bat",
                "Launch_RAM_Sharing.bat",
                "Launch_Unified_System.bat",
                "Universal_Launcher.bat",
                "Simple_Launcher.bat",
                "Working_Launcher.bat"
            ],
            "RDMA & Advanced": [
                "rdma_desktop_app.py",
                "rdma_modern_tkinter.py",
                "memory_portal_gui.py",
                "ddr4_ram_sharing.py",
                "nvidia_gpu_sharing.py"
            ]
        }
        
        for category, files in categories.items():
            found = 0
            missing = 0
            details = []
            
            for file_name in files:
                file_path = self.base_path / file_name
                if file_path.exists():
                    found += 1
                    details.append({"name": file_name, "status": "found"})
                else:
                    # Try to find in subdirectories
                    found_path = None
                    for search_path in self.base_path.rglob(file_name):
                        if search_path.is_file():
                            found_path = search_path
                            break
                    
                    if found_path:
                        found += 1
                        details.append({"name": file_name, "status": "found", "location": str(found_path)})
                    else:
                        missing += 1
                        details.append({"name": file_name, "status": "missing"})
            
            self.results["by_category"][category] = {
                "total": len(files),
                "found": found,
                "missing": missing,
                "details": details
            }
            
            status = "✅" if missing == 0 else "⚠️" if found > 0 else "❌"
            print(f"  {status} {category}: {found}/{len(files)} found")
    
    def count_by_locations(self):
        """Count components by physical locations"""
        print("\n📍 Counting by locations...")
        
        locations = {}
        
        # Scan directories
        for item in self.base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                location_name = item.name
                python_files = list(item.rglob("*.py"))
                batch_files = list(item.rglob("*.bat"))
                
                # Filter out cache directories
                python_files = [f for f in python_files if '__pycache__' not in str(f)]
                batch_files = [f for f in batch_files if '__pycache__' not in str(f)]
                
                locations[location_name] = {
                    "python_files": len(python_files),
                    "batch_files": len(batch_files),
                    "total_files": len(python_files) + len(batch_files),
                    "python_files_list": [f.name for f in python_files],
                    "batch_files_list": [f.name for f in batch_files]
                }
                
                if locations[location_name]["total_files"] > 0:
                    print(f"  📁 {location_name}: {locations[location_name]['total_files']} files")
        
        # Count root level files
        root_python = list(self.base_path.glob("*.py"))
        root_batch = list(self.base_path.glob("*.bat"))
        
        locations["Root Level"] = {
            "python_files": len(root_python),
            "batch_files": len(root_batch),
            "total_files": len(root_python) + len(root_batch),
            "python_files_list": [f.name for f in root_python],
            "batch_files_list": [f.name for f in root_batch]
        }
        
        print(f"  📁 Root Level: {locations['Root Level']['total_files']} files")
        
        self.results["by_location"] = locations
    
    def generate_detailed_breakdown(self):
        """Generate detailed breakdown of all components"""
        print("\n📊 Generating detailed breakdown...")
        
        breakdown = {
            "summary": {
                "total_python_files": self.results["python_files"],
                "total_batch_files": self.results["batch_files"],
                "total_cpp_files": self.results["cpp_files"],
                "total_files": self.results["total_files"],
                "total_directories": len([d for d in self.base_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
            },
            "functional_components": {},
            "utility_files": {},
            "configuration_files": {}
        }
        
        # Categorize files by function
        all_python = list(self.base_path.rglob("*.py"))
        all_batch = list(self.base_path.rglob("*.bat"))
        
        # Filter files
        def filter_files(files):
            return [f for f in files if '__pycache__' not in str(f) and '.git' not in str(f)]
        
        all_python = filter_files(all_python)
        all_batch = filter_files(all_batch)
        
        # Functional components (main applications)
        functional_patterns = [
            "launcher", "dashboard", "monitor", "gateway", "server", "client", 
            "manager", "portal", "platform", "sharing", "vpn", "mesh"
        ]
        
        # Utility files (setup, configuration, etc.)
        utility_patterns = [
            "setup", "install", "config", "audit", "test", "verify", "batch",
            "launch", "start", "run", "build", "cleanup"
        ]
        
        for py_file in all_python:
            file_name = py_file.name.lower()
            file_size = py_file.stat().st_size if py_file.exists() else 0
            
            category = "other"
            for pattern in functional_patterns:
                if pattern in file_name:
                    category = "functional"
                    break
            
            for pattern in utility_patterns:
                if pattern in file_name:
                    category = "utility"
                    break
            
            if category == "functional":
                breakdown["functional_components"][py_file.name] = {
                    "path": str(py_file),
                    "size": file_size,
                    "type": "python"
                }
            elif category == "utility":
                breakdown["utility_files"][py_file.name] = {
                    "path": str(py_file),
                    "size": file_size,
                    "type": "python"
                }
        
        for bat_file in all_batch:
            file_name = bat_file.name.lower()
            file_size = bat_file.stat().st_size if bat_file.exists() else 0
            
            breakdown["utility_files"][bat_file.name] = {
                "path": str(bat_file),
                "size": file_size,
                "type": "batch"
            }
        
        self.results["detailed_breakdown"] = breakdown
        
        print(f"  Functional components: {len(breakdown['functional_components'])}")
        print(f"  Utility files: {len(breakdown['utility_files'])}")
    
    def print_results(self):
        """Print comprehensive results"""
        print("\n" + "=" * 60)
        print("UNIFIED COMPONENT COUNT RESULTS")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"  Total Python Files: {self.results['python_files']}")
        print(f"  Total Batch Files: {self.results['batch_files']}")
        print(f"  Total C/C++ Files: {self.results['cpp_files']}")
        print(f"  Total Files: {self.results['total_files']}")
        
        # Category breakdown
        print(f"\n📂 CATEGORY BREAKDOWN:")
        for category, data in self.results["by_category"].items():
            percentage = (data["found"] / data["total"]) * 100 if data["total"] > 0 else 0
            status = "✅" if data["missing"] == 0 else "⚠️" if data["found"] > 0 else "❌"
            print(f"  {status} {category}: {data['found']}/{data['total']} ({percentage:.1f}%)")
        
        # Location breakdown
        print(f"\n📍 LOCATION BREAKDOWN:")
        for location, data in self.results["by_location"].items():
            if data["total_files"] > 0:
                print(f"  📁 {location}: {data['total_files']} files ({data['python_files']} Python, {data['batch_files']} Batch)")
        
        # Detailed breakdown
        breakdown = self.results["detailed_breakdown"]["summary"]
        print(f"\n📋 DETAILED BREAKDOWN:")
        print(f"  Functional Components: {len(self.results['detailed_breakdown']['functional_components'])}")
        print(f"  Utility Files: {len(self.results['detailed_breakdown']['utility_files'])}")
        print(f"  Directories: {breakdown['total_directories']}")
    
    def save_results(self):
        """Save results to JSON file"""
        output_file = Path("unified_component_count.json")
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n✅ Results saved to: {output_file}")
            
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")

def main():
    """Main entry point"""
    counter = UnifiedComponentCounter()
    results = counter.count_all_components()
    
    print(f"\n🎯 FINAL COUNT: {results['total_files']} total files")
    print(f"   - Python: {results['python_files']}")
    print(f"   - Batch: {results['batch_files']}")
    print(f"   - C/C++: {results['cpp_files']}")

if __name__ == "__main__":
    main()
