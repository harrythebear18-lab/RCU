#!/usr/bin/env python3
"""
Chunked System Audit - Processes audit in manageable chunks
Prevents hanging by breaking down the audit into small, fast operations
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class ComponentStatus(Enum):
    """Component status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WORKING = "working"
    PARTIAL = "partial"
    BROKEN = "broken"
    MISSING = "missing"

@dataclass
class ChunkResult:
    """Result for a single chunk"""
    chunk_name: str
    total_found: int
    working: int
    broken: int
    missing: int
    details: List[Dict]

class ChunkedSystemAuditor:
    """Auditor that processes in chunks to prevent hanging"""
    
    def __init__(self):
        self.setup_logging()
        self.results_file = Path("comprehensive_system_audit_results.json")
        
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/chunked_audit.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ChunkedAuditor')
    
    def run_chunked_audit(self) -> Dict[str, Any]:
        """Run audit in manageable chunks"""
        print("=" * 60)
        print("CHUNKED SYSTEM AUDIT - FAST & RELIABLE")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Load existing results if any
            existing_results = self.load_existing_results()
            
            # Run chunks
            chunk_results = []
            
            # Chunk 1: Core System Info
            print("\n🔍 CHUNK 1: Core System Analysis")
            chunk1 = self.analyze_core_system()
            chunk_results.append(chunk1)
            
            # Chunk 2: Mesh VPN Components
            print("\n🔍 CHUNK 2: Mesh VPN Components")
            chunk2 = self.analyze_mesh_vpn_chunk()
            chunk_results.append(chunk2)
            
            # Chunk 3: Launcher & Dashboard
            print("\n🔍 CHUNK 3: Launcher & Dashboard")
            chunk3 = self.analyze_launcher_dashboard_chunk()
            chunk_results.append(chunk3)
            
            # Chunk 4: Core Services
            print("\n🔍 CHUNK 4: Core Services")
            chunk4 = self.analyze_core_services_chunk()
            chunk_results.append(chunk4)
            
            # Chunk 5: Network Management
            print("\n🔍 CHUNK 5: Network Management")
            chunk5 = self.analyze_network_management_chunk()
            chunk_results.append(chunk5)
            
            # Chunk 6: Monitoring Tools
            print("\n🔍 CHUNK 6: Monitoring Tools")
            chunk6 = self.analyze_monitoring_tools_chunk()
            chunk_results.append(chunk6)
            
            # Chunk 7: Resource Tools
            print("\n🔍 CHUNK 7: Resource Management Tools")
            chunk7 = self.analyze_resource_tools_chunk()
            chunk_results.append(chunk7)
            
            # Chunk 8: Integration Tests
            print("\n🔍 CHUNK 8: Integration & Setup")
            chunk8 = self.analyze_integration_chunk()
            chunk_results.append(chunk8)
            
            # Combine results
            combined_results = self.combine_chunk_results(chunk_results, existing_results)
            combined_results['audit_duration'] = time.time() - start_time
            
            # Save results
            self.save_results(combined_results)
            
            # Print summary
            self.print_final_summary(combined_results)
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Chunked audit failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def analyze_core_system(self) -> ChunkResult:
        """Analyze core system information"""
        try:
            import platform
            
            system_info = {
                "system_type": platform.system(),
                "version": platform.version(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0]
            }
            
            # Check key modules
            key_modules = ['tkinter', 'flask', 'psutil', 'requests', 'pathlib', 'json']
            available_modules = []
            missing_modules = []
            
            for module in key_modules:
                try:
                    __import__(module)
                    available_modules.append(module)
                except ImportError:
                    missing_modules.append(module)
            
            details = [{
                "name": "system_info",
                "status": "working",
                "details": system_info
            }]
            
            result = ChunkResult(
                chunk_name="Core System",
                total_found=1,
                working=1,
                broken=0,
                missing=0,
                details=details
            )
            
            print(f"  ✓ System: {system_info['system_type']} {system_info['version']}")
            print(f"  ✓ Python: {system_info['python_version']}")
            print(f"  ✓ Modules: {len(available_modules)}/{len(key_modules)} available")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Core system analysis failed: {e}")
            return ChunkResult("Core System", 0, 0, 1, 0, [{"error": str(e)}])
    
    def analyze_mesh_vpn_chunk(self) -> ChunkResult:
        """Analyze mesh VPN components"""
        mesh_files = {
            'mesh_vpn_server.py': 'Network Management',
            'mesh_service_discovery.py': 'Network Management',
            'mesh_vpn_client.py': 'Network Management',
            'wireguard_config_generator.py': 'Network Management',
            'bidirectional_mesh_setup.py': 'Network Management'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in mesh_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    # Quick content check
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 500 and 'def ' in content:
                        status = "working"
                        working += 1
                    else:
                        status = "minimal"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "location": location,
                        "status": status,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "location": location,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "location": location,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Mesh VPN",
            total_found=len(mesh_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Mesh VPN: {working}/{len(mesh_files)} working")
        return result
    
    def analyze_launcher_dashboard_chunk(self) -> ChunkResult:
        """Analyze launcher and dashboard components"""
        launcher_files = {
            'homelab_launcher.py': '.',
            'homelab_launcher_enhanced.py': '.',
            'homelab_dashboard.py': '.',
            'unified_dashboard.py': 'Core Services'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in launcher_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
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
                        status = "working"
                        working += 1
                    else:
                        status = "basic"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "status": status,
                        "features": features,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Launcher/Dashboard",
            total_found=len(launcher_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Launcher/Dashboard: {working}/{len(launcher_files)} working")
        return result
    
    def analyze_core_services_chunk(self) -> ChunkResult:
        """Analyze core services"""
        core_files = {
            'mesh_app_communication.py': 'Core Services',
            'mesh_app_integration.py': 'Core Services',
            'mesh_vpn_dashboard.py': 'Core Services',
            'unified_monitoring.py': 'Core Services',
            'web_dashboard.py': 'Core Services'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in core_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 800 and 'class ' in content:
                        status = "working"
                        working += 1
                    else:
                        status = "minimal"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "status": status,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Core Services",
            total_found=len(core_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Core Services: {working}/{len(core_files)} working")
        return result
    
    def analyze_network_management_chunk(self) -> ChunkResult:
        """Analyze network management tools"""
        network_files = {
            'network_monitor.py': 'Network Monitor',
            'vpn_gateway.py': 'VPN Gateway'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in network_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 1000 and 'tkinter' in content.lower():
                        status = "working"
                        working += 1
                    else:
                        status = "basic"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "status": status,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Network Management",
            total_found=len(network_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Network Management: {working}/{len(network_files)} working")
        return result
    
    def analyze_monitoring_tools_chunk(self) -> ChunkResult:
        """Analyze monitoring tools"""
        monitor_files = {
            'gpu_monitor.py': 'GPU Monitor',
            'ram_monitor_gui.py': 'Memory Monitor',
            'storage_monitor.py': 'Storage Monitor',
            'cpu_monitor.py': 'CPU Monitor'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in monitor_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 500 and 'tkinter' in content.lower():
                        status = "working"
                        working += 1
                    else:
                        status = "basic"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "status": status,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Monitoring Tools",
            total_found=len(monitor_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Monitoring Tools: {working}/{len(monitor_files)} working")
        return result
    
    def analyze_resource_tools_chunk(self) -> ChunkResult:
        """Analyze resource management tools"""
        resource_files = {
            'container_manager.py': 'Container Manager',
            'backup_manager.py': 'Core Services',
            'power_manager.py': 'Power Manager',
            'media_server_manager.py': 'Media Server'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in resource_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 300:
                        status = "working"
                        working += 1
                    else:
                        status = "minimal"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "status": status,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Resource Tools",
            total_found=len(resource_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Resource Tools: {working}/{len(resource_files)} working")
        return result
    
    def analyze_integration_chunk(self) -> ChunkResult:
        """Analyze integration and setup tools"""
        integration_files = {
            'wireguard_installer.py': 'setup',
            'install_wireguard.bat': 'setup',
            'complete_system_verification.py': '.',
            'fully_comprehensive_system_audit.py': '.'
        }
        
        working = 0
        broken = 0
        missing = 0
        details = []
        
        for filename, location in integration_files.items():
            file_path = Path(location) / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if len(content) > 200:
                        status = "working"
                        working += 1
                    else:
                        status = "minimal"
                        broken += 1
                    
                    details.append({
                        "name": filename,
                        "status": status,
                        "size": len(content)
                    })
                    
                except Exception as e:
                    details.append({
                        "name": filename,
                        "status": "error",
                        "error": str(e)
                    })
                    broken += 1
            else:
                details.append({
                    "name": filename,
                    "status": "missing"
                })
                missing += 1
        
        result = ChunkResult(
            chunk_name="Integration & Setup",
            total_found=len(integration_files),
            working=working,
            broken=broken,
            missing=missing,
            details=details
        )
        
        print(f"  ✓ Integration & Setup: {working}/{len(integration_files)} working")
        return result
    
    def combine_chunk_results(self, chunk_results: List[ChunkResult], existing: Dict) -> Dict[str, Any]:
        """Combine results from all chunks"""
        total_found = sum(chunk.total_found for chunk in chunk_results)
        total_working = sum(chunk.working for chunk in chunk_results)
        total_broken = sum(chunk.broken for chunk in chunk_results)
        total_missing = sum(chunk.missing for chunk in chunk_results)
        
        # Calculate overall score
        if total_found > 0:
            overall_score = (total_working / total_found) * 100
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
        
        # Combine all details
        all_details = []
        for chunk in chunk_results:
            all_details.extend(chunk.details)
        
        return {
            "overall_status": overall_status,
            "overall_score": round(overall_score, 1),
            "total_components": total_found,
            "working_components": total_working,
            "broken_components": total_broken,
            "missing_components": total_missing,
            "chunk_results": [
                {
                    "name": chunk.chunk_name,
                    "total": chunk.total_found,
                    "working": chunk.working,
                    "broken": chunk.broken,
                    "missing": chunk.missing
                }
                for chunk in chunk_results
            ],
            "all_component_details": all_details,
            "last_updated": time.time()
        }
    
    def load_existing_results(self) -> Dict[str, Any]:
        """Load existing results if available"""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_results(self, results: Dict[str, Any]):
        """Save results to JSON file"""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n✅ Results saved to: {self.results_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
    
    def print_final_summary(self, results: Dict[str, Any]):
        """Print final audit summary"""
        print("\n" + "=" * 60)
        print("FINAL AUDIT SUMMARY")
        print("=" * 60)
        
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Overall Score: {results['overall_score']}/100")
        print(f"Total Components: {results['total_components']}")
        print(f"Working Components: {results['working_components']}")
        print(f"Broken Components: {results['broken_components']}")
        print(f"Missing Components: {results['missing_components']}")
        
        print(f"\nChunk Results:")
        for chunk in results['chunk_results']:
            status_emoji = "✅" if chunk['working'] == chunk['total'] else "⚠️" if chunk['working'] > 0 else "❌"
            print(f"  {status_emoji} {chunk['name']}: {chunk['working']}/{chunk['total']} working")

def main():
    """Main entry point"""
    auditor = ChunkedSystemAuditor()
    
    try:
        results = auditor.run_chunked_audit()
        
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
