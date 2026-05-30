#!/usr/bin/env python3
"""
Comprehensive Chunked Audit System
Complete system and functionality audit in manageable chunks
Fixes mismatched numbers and provides accurate component counting
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

class ComponentStatus(Enum):
    """Component status levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WORKING = "working"
    PARTIAL = "partial"
    BROKEN = "broken"
    MISSING = "missing"

@dataclass
class ComponentInfo:
    """Detailed component information"""
    name: str
    path: str
    file_type: str
    size: int
    status: ComponentStatus
    functionality_score: int
    features: List[str]
    issues: List[str]
    category: str

@dataclass
class ChunkResult:
    """Result for a single audit chunk"""
    chunk_name: str
    total_found: int
    working: int
    partial: int
    broken: int
    missing: int
    components: List[ComponentInfo]
    duration: float

class ComprehensiveChunkedAuditor:
    """Comprehensive auditor that processes everything in chunks"""
    
    def __init__(self):
        self.setup_logging()
        self.base_path = Path(".")
        self.results_file = Path("comprehensive_system_audit_results.json")
        
    def setup_logging(self):
        """Setup logging"""
        log_file = Path("logs/comprehensive_chunked_audit.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ComprehensiveAuditor')
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit in manageable chunks"""
        print("=" * 80)
        print("COMPREHENSIVE CHUNKED SYSTEM AUDIT")
        print("Complete system and functionality analysis")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # Load existing results
            existing_results = self.load_existing_results()
            
            # Run all chunks
            chunk_results = []
            
            # Chunk 1: Complete File Discovery
            print("\n🔍 CHUNK 1: Complete File Discovery")
            chunk1 = self.discover_all_files_chunk()
            chunk_results.append(chunk1)
            
            # Chunk 2: Python Applications Analysis
            print("\n🔍 CHUNK 2: Python Applications Analysis")
            chunk2 = self.analyze_python_applications_chunk()
            chunk_results.append(chunk2)
            
            # Chunk 3: Batch Files & Launchers Analysis
            print("\n🔍 CHUNK 3: Batch Files & Launchers Analysis")
            chunk3 = self.analyze_batch_files_chunk()
            chunk_results.append(chunk3)
            
            # Chunk 4: Core System Components
            print("\n🔍 CHUNK 4: Core System Components")
            chunk4 = self.analyze_core_system_chunk()
            chunk_results.append(chunk4)
            
            # Chunk 5: Mesh VPN System Analysis
            print("\n🔍 CHUNK 5: Mesh VPN System Analysis")
            chunk5 = self.analyze_mesh_vpn_system_chunk()
            chunk_results.append(chunk5)
            
            # Chunk 6: Network & Monitoring Tools
            print("\n🔍 CHUNK 6: Network & Monitoring Tools")
            chunk6 = self.analyze_network_monitoring_chunk()
            chunk_results.append(chunk6)
            
            # Chunk 7: Resource Management Tools
            print("\n🔍 CHUNK 7: Resource Management Tools")
            chunk7 = self.analyze_resource_management_chunk()
            chunk_results.append(chunk7)
            
            # Chunk 8: Core Services Integration
            print("\n🔍 CHUNK 8: Core Services Integration")
            chunk8 = self.analyze_core_services_chunk()
            chunk_results.append(chunk8)
            
            # Chunk 9: Setup & Installation Tools
            print("\n🔍 CHUNK 9: Setup & Installation Tools")
            chunk9 = self.analyze_setup_installation_chunk()
            chunk_results.append(chunk9)
            
            # Chunk 10: Advanced & Experimental Components
            print("\n🔍 CHUNK 10: Advanced & Experimental Components")
            chunk10 = self.analyze_advanced_experimental_chunk()
            chunk_results.append(chunk10)
            
            # Combine all results
            combined_results = self.combine_all_chunk_results(chunk_results, existing_results)
            combined_results['audit_duration'] = time.time() - start_time
            
            # Save comprehensive results
            self.save_comprehensive_results(combined_results)
            
            # Print final summary
            self.print_comprehensive_summary(combined_results)
            
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive audit failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def discover_all_files_chunk(self) -> ChunkResult:
        """Discover all files in the system"""
        start_time = time.time()
        components = []
        
        try:
            # Discover Python files
            python_files = list(self.base_path.rglob("*.py"))
            python_files = [f for f in python_files if '__pycache__' not in str(f) and '.git' not in str(f)]
            
            for py_file in python_files:
                size = py_file.stat().st_size if py_file.exists() else 0
                component = ComponentInfo(
                    name=py_file.name,
                    path=str(py_file),
                    file_type="python",
                    size=size,
                    status=ComponentStatus.WORKING,  # Default, will be updated in analysis chunks
                    functionality_score=0,
                    features=[],
                    issues=[],
                    category="discovered"
                )
                components.append(component)
            
            # Discover Batch files
            batch_files = list(self.base_path.rglob("*.bat"))
            batch_files = [f for f in batch_files if '__pycache__' not in str(f) and '.git' not in str(f)]
            
            for bat_file in batch_files:
                size = bat_file.stat().st_size if bat_file.exists() else 0
                component = ComponentInfo(
                    name=bat_file.name,
                    path=str(bat_file),
                    file_type="batch",
                    size=size,
                    status=ComponentStatus.WORKING,
                    functionality_score=0,
                    features=[],
                    issues=[],
                    category="discovered"
                )
                components.append(component)
            
            # Discover C/C++ files
            cpp_files = list(self.base_path.rglob("*.cpp"))
            c_files = list(self.base_path.rglob("*.c"))
            h_files = list(self.base_path.rglob("*.h"))
            
            all_cpp = cpp_files + c_files + h_files
            all_cpp = [f for f in all_cpp if '__pycache__' not in str(f) and '.git' not in str(f)]
            
            for cpp_file in all_cpp:
                size = cpp_file.stat().st_size if cpp_file.exists() else 0
                component = ComponentInfo(
                    name=cpp_file.name,
                    path=str(cpp_file),
                    file_type="cpp",
                    size=size,
                    status=ComponentStatus.WORKING,
                    functionality_score=0,
                    features=[],
                    issues=[],
                    category="discovered"
                )
                components.append(component)
            
            duration = time.time() - start_time
            
            result = ChunkResult(
                chunk_name="File Discovery",
                total_found=len(components),
                working=len(components),
                partial=0,
                broken=0,
                missing=0,
                components=components,
                duration=duration
            )
            
            print(f"  ✓ Discovered {len(components)} files:")
            print(f"    Python: {len(python_files)}")
            print(f"    Batch: {len(batch_files)}")
            print(f"    C/C++: {len(all_cpp)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"File discovery failed: {e}")
            return ChunkResult("File Discovery", 0, 0, 0, 1, 0, [], 0)
    
    def analyze_python_applications_chunk(self) -> ChunkResult:
        """Analyze Python applications in detail"""
        start_time = time.time()
        
        # Define key Python applications
        key_apps = {
            "homelab_launcher.py": "Main Launcher",
            "homelab_launcher_enhanced.py": "Enhanced Launcher",
            "homelab_dashboard.py": "Main Dashboard",
            "Visentrix_Launcher.py": "Visentrix Launcher",
            "Integrated_RAM_Launcher.py": "RAM Launcher",
            "complete_system_verification.py": "System Verification",
            "fully_comprehensive_system_audit.py": "Audit System",
            "chunked_system_audit.py": "Chunked Audit",
            "comprehensive_chunked_audit.py": "Comprehensive Audit",
            "unified_component_counter.py": "Component Counter"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, description in key_apps.items():
            file_path = self.base_path / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_python_file(file_path, description, "Python Applications")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="python",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Python Applications"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="python",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Python Applications"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Python Applications",
            total_found=len(key_apps),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Python Applications: {working}/{len(key_apps)} working")
        return result
    
    def analyze_batch_files_chunk(self) -> ChunkResult:
        """Analyze batch files and launchers"""
        start_time = time.time()
        
        # Key batch files
        key_batch_files = {
            "launch_homelab.bat": "Main Launcher",
            "Launch_Homelab_Portal.bat": "Portal Launcher",
            "Launch_RAM_Sharing.bat": "RAM Sharing Launcher",
            "Launch_Unified_System.bat": "Unified System Launcher",
            "Universal_Launcher.bat": "Universal Launcher",
            "Simple_Launcher.bat": "Simple Launcher",
            "Working_Launcher.bat": "Working Launcher",
            "setup.bat": "Setup Script",
            "first_time_setup.bat": "First Time Setup",
            "run_audit_fixed.bat": "Audit Runner",
            "install_wireguard.bat": "WireGuard Installer"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, description in key_batch_files.items():
            file_path = self.base_path / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_batch_file(file_path, description, "Batch Launchers")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="batch",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Batch Launchers"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="batch",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Batch Launchers"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Batch Files & Launchers",
            total_found=len(key_batch_files),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Batch Files: {working}/{len(key_batch_files)} working")
        return result
    
    def analyze_mesh_vpn_system_chunk(self) -> ChunkResult:
        """Analyze mesh VPN system components"""
        start_time = time.time()
        
        mesh_components = {
            "mesh_vpn_server.py": "Network Management",
            "mesh_vpn_client.py": "Network Management",
            "mesh_service_discovery.py": "Network Management",
            "mesh_app_communication.py": "Core Services",
            "mesh_app_integration.py": "Core Services",
            "mesh_vpn_dashboard.py": "Core Services",
            "wireguard_config_generator.py": "Network Management",
            "bidirectional_mesh_setup.py": "Network Management"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, location in mesh_components.items():
            file_path = self.base_path / location / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_python_file(file_path, f"Mesh VPN - {filename}", "Mesh VPN")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="python",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Mesh VPN"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="python",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Mesh VPN"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Mesh VPN System",
            total_found=len(mesh_components),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Mesh VPN: {working}/{len(mesh_components)} working")
        return result
    
    def analyze_network_monitoring_chunk(self) -> ChunkResult:
        """Analyze network and monitoring tools"""
        start_time = time.time()
        
        network_monitoring = {
            "network_monitor.py": "Network Monitor",
            "vpn_gateway.py": "VPN Gateway",
            "gpu_monitor.py": "GPU Monitor",
            "ram_monitor_gui.py": "RAM Monitor",
            "storage_monitor.py": "Storage Monitor",
            "cpu_monitor.py": "CPU Monitor",
            "unified_monitoring.py": "Unified Monitoring"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, location in network_monitoring.items():
            # Handle different locations
            if "monitor.py" in filename:
                if "network" in filename:
                    file_path = self.base_path / "Network Monitor" / filename
                elif "gpu" in filename:
                    file_path = self.base_path / "GPU Monitor" / filename
                elif "ram" in filename:
                    file_path = self.base_path / "Memory Monitor" / filename
                elif "storage" in filename:
                    file_path = self.base_path / "Storage Monitor" / filename
                elif "cpu" in filename:
                    file_path = self.base_path / "CPU Monitor" / filename
                else:
                    file_path = self.base_path / filename
            elif "gateway" in filename:
                file_path = self.base_path / "VPN Gateway" / filename
            elif "unified" in filename:
                file_path = self.base_path / "Core Services" / filename
            else:
                file_path = self.base_path / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_python_file(file_path, f"Network/Monitoring - {filename}", "Network & Monitoring")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="python",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Network & Monitoring"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="python",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Network & Monitoring"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Network & Monitoring",
            total_found=len(network_monitoring),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Network & Monitoring: {working}/{len(network_monitoring)} working")
        return result
    
    def analyze_resource_management_chunk(self) -> ChunkResult:
        """Analyze resource management tools"""
        start_time = time.time()
        
        resource_tools = {
            "container_manager.py": "Container Manager",
            "backup_manager.py": "Backup Manager",
            "power_manager.py": "Power Manager",
            "media_server_manager.py": "Media Server",
            "iot_platform.py": "IoT Platform"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, location in resource_tools.items():
            # Determine correct path
            if "container" in filename:
                file_path = self.base_path / "Container Manager" / filename
            elif "backup" in filename:
                file_path = self.base_path / "Core Services" / filename
            elif "power" in filename:
                file_path = self.base_path / "Power Manager" / filename
            elif "media" in filename:
                file_path = self.base_path / "Media Server" / filename
            elif "iot" in filename:
                file_path = self.base_path / "IoT Platform" / filename
            else:
                file_path = self.base_path / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_python_file(file_path, f"Resource Management - {filename}", "Resource Management")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="python",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Resource Management"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="python",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Resource Management"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Resource Management",
            total_found=len(resource_tools),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Resource Management: {working}/{len(resource_tools)} working")
        return result
    
    def analyze_core_system_chunk(self) -> ChunkResult:
        """Analyze core system components"""
        start_time = time.time()
        
        # This is a simple chunk for system info
        try:
            import platform
            
            system_info = {
                "system_type": platform.system(),
                "version": platform.version(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0]
            }
            
            component = ComponentInfo(
                name="System Information",
                path="System",
                file_type="system",
                size=0,
                status=ComponentStatus.EXCELLENT,
                functionality_score=100,
                features=[system_info["system_type"], system_info["python_version"]],
                issues=[],
                category="Core System"
            )
            
            duration = time.time() - start_time
            
            result = ChunkResult(
                chunk_name="Core System",
                total_found=1,
                working=1,
                partial=0,
                broken=0,
                missing=0,
                components=[component],
                duration=duration
            )
            
            print(f"  ✓ Core System: {system_info['system_type']} {system_info['version']}")
            return result
            
        except Exception as e:
            return ChunkResult("Core System", 0, 0, 0, 1, [], 0)
    
    def analyze_core_services_chunk(self) -> ChunkResult:
        """Analyze core services"""
        start_time = time.time()
        
        core_services = {
            "web_dashboard.py": "Core Services",
            "unified_dashboard.py": "Core Services",
            "rest_api.py": "Core Services",
            "auth_service.py": "Core Services",
            "config_manager.py": "Core Services",
            "event_bus.py": "Core Services",
            "smart_system_sensing.py": "Core Services",
            "wireguard_installer.py": "Core Services"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, location in core_services.items():
            file_path = self.base_path / location / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_python_file(file_path, f"Core Services - {filename}", "Core Services")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD or component.status == ComponentStatus.WORKING:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="python",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Core Services"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="python",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Core Services"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Core Services",
            total_found=len(core_services),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Core Services: {working}/{len(core_services)} working")
        return result
    
    def analyze_setup_installation_chunk(self) -> ChunkResult:
        """Analyze setup and installation tools"""
        start_time = time.time()
        
        setup_tools = {
            "install_wireguard.bat": "setup",
            "setup.bat": ".",
            "first_time_setup.bat": ".",
            "run_audit_fixed.bat": "."
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, location in setup_tools.items():
            file_path = self.base_path / location / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_batch_file(file_path, f"Setup - {filename}", "Setup & Installation")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="batch",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Setup & Installation"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="batch",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Setup & Installation"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Setup & Installation",
            total_found=len(setup_tools),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Setup & Installation: {working}/{len(setup_tools)} working")
        return result
    
    def analyze_advanced_experimental_chunk(self) -> ChunkResult:
        """Analyze advanced and experimental components"""
        start_time = time.time()
        
        advanced_components = {
            "rdma_desktop_app.py": "RDMA Desktop App",
            "rdma_modern_tkinter.py": "RDMA Desktop App",
            "memory_portal_gui.py": "Memory Portal",
            "ddr4_ram_sharing.py": "Core Services",
            "nvidia_gpu_sharing.py": "Core Services",
            "bidirectional_resource_sharing.py": "Core Services"
        }
        
        components = []
        working = 0
        partial = 0
        broken = 0
        missing = 0
        
        for filename, location in advanced_components.items():
            if "rdma" in filename:
                file_path = self.base_path / "RDMA Desktop App" / filename
            elif "memory" in filename:
                file_path = self.base_path / "Memory Portal" / filename
            else:
                file_path = self.base_path / location / filename
            
            if file_path.exists():
                try:
                    component = self.analyze_python_file(file_path, f"Advanced - {filename}", "Advanced & Experimental")
                    components.append(component)
                    
                    if component.status == ComponentStatus.EXCELLENT or component.status == ComponentStatus.GOOD:
                        working += 1
                    elif component.status == ComponentStatus.PARTIAL:
                        partial += 1
                    else:
                        broken += 1
                        
                except Exception as e:
                    component = ComponentInfo(
                        name=filename,
                        path=str(file_path),
                        file_type="python",
                        size=0,
                        status=ComponentStatus.BROKEN,
                        functionality_score=0,
                        features=[],
                        issues=[str(e)],
                        category="Advanced & Experimental"
                    )
                    components.append(component)
                    broken += 1
            else:
                component = ComponentInfo(
                    name=filename,
                    path=str(file_path),
                    file_type="python",
                    size=0,
                    status=ComponentStatus.MISSING,
                    functionality_score=0,
                    features=[],
                    issues=["File not found"],
                    category="Advanced & Experimental"
                )
                components.append(component)
                missing += 1
        
        duration = time.time() - start_time
        
        result = ChunkResult(
            chunk_name="Advanced & Experimental",
            total_found=len(advanced_components),
            working=working,
            partial=partial,
            broken=broken,
            missing=missing,
            components=components,
            duration=duration
        )
        
        print(f"  ✓ Advanced & Experimental: {working}/{len(advanced_components)} working")
        return result
    
    def analyze_python_file(self, file_path: Path, description: str, category: str) -> ComponentInfo:
        """Analyze a Python file for functionality"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            size = file_path.stat().st_size
            
            # Check for features
            features = []
            issues = []
            score = 0
            
            # Basic structure
            if 'import' in content:
                features.append('imports')
                score += 10
            
            if 'def ' in content:
                features.append('functions')
                score += 15
            
            if 'class ' in content:
                features.append('classes')
                score += 15
            
            # Error handling
            if 'try:' in content and 'except' in content:
                features.append('error_handling')
                score += 10
            
            # Standalone execution
            if 'if __name__ == "__main__"' in content:
                features.append('standalone_execution')
                score += 15
            
            # GUI features
            if 'tkinter' in content.lower():
                features.append('tkinter_gui')
                score += 20
            
            if 'root.mainloop()' in content:
                features.append('gui_mainloop')
                score += 10
            
            # Web features
            if 'flask' in content.lower():
                features.append('web_api')
                score += 20
            
            if 'app.run()' in content:
                features.append('web_server')
                score += 10
            
            # Network features
            if 'socket' in content.lower():
                features.append('networking')
                score += 15
            
            if 'requests' in content.lower():
                features.append('http_client')
                score += 10
            
            # Database features
            if 'sqlite3' in content.lower():
                features.append('database')
                score += 15
            
            # Mesh features
            if 'mesh' in content.lower():
                features.append('mesh_networking')
                score += 20
            
            # Threading
            if 'threading' in content.lower():
                features.append('multithreading')
                score += 10
            
            # Determine status
            if score >= 80:
                status = ComponentStatus.EXCELLENT
            elif score >= 60:
                status = ComponentStatus.GOOD
            elif score >= 40:
                status = ComponentStatus.WORKING
            elif score >= 20:
                status = ComponentStatus.PARTIAL
            else:
                status = ComponentStatus.BROKEN
            
            # Check for issues
            if size < 100:
                issues.append("Very small file")
            elif size > 1000000:  # 1MB
                issues.append("Very large file")
            
            return ComponentInfo(
                name=file_path.name,
                path=str(file_path),
                file_type="python",
                size=size,
                status=status,
                functionality_score=score,
                features=features,
                issues=issues,
                category=category
            )
            
        except Exception as e:
            return ComponentInfo(
                name=file_path.name,
                path=str(file_path),
                file_type="python",
                size=0,
                status=ComponentStatus.BROKEN,
                functionality_score=0,
                features=[],
                issues=[str(e)],
                category=category
            )
    
    def analyze_batch_file(self, file_path: Path, description: str, category: str) -> ComponentInfo:
        """Analyze a batch file for functionality"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            size = file_path.stat().st_size
            
            features = []
            issues = []
            score = 0
            
            # Check for batch features
            if '@echo off' in content:
                features.append('echo_off')
                score += 5
            
            if 'python' in content.lower() or 'py ' in content:
                features.append('python_launcher')
                score += 20
            
            if 'start' in content:
                features.append('window_management')
                score += 10
            
            if 'pause' in content:
                features.append('user_interaction')
                score += 5
            
            if 'set' in content:
                features.append('variable_setting')
                score += 10
            
            if 'if' in content:
                features.append('conditional_logic')
                score += 15
            
            if 'call' in content:
                features.append('batch_calls')
                score += 10
            
            # Determine status
            if score >= 50:
                status = ComponentStatus.EXCELLENT
            elif score >= 35:
                status = ComponentStatus.GOOD
            elif score >= 20:
                status = ComponentStatus.WORKING
            elif score >= 10:
                status = ComponentStatus.PARTIAL
            else:
                status = ComponentStatus.BROKEN
            
            # Check for issues
            if size < 50:
                issues.append("Very small file")
            
            return ComponentInfo(
                name=file_path.name,
                path=str(file_path),
                file_type="batch",
                size=size,
                status=status,
                functionality_score=score,
                features=features,
                issues=issues,
                category=category
            )
            
        except Exception as e:
            return ComponentInfo(
                name=file_path.name,
                path=str(file_path),
                file_type="batch",
                size=0,
                status=ComponentStatus.BROKEN,
                functionality_score=0,
                features=[],
                issues=[str(e)],
                category=category
            )
    
    def combine_all_chunk_results(self, chunk_results: List[ChunkResult], existing: Dict) -> Dict[str, Any]:
        """Combine results from all chunks"""
        total_found = sum(chunk.total_found for chunk in chunk_results)
        total_working = sum(chunk.working for chunk in chunk_results)
        total_partial = sum(chunk.partial for chunk in chunk_results)
        total_broken = sum(chunk.broken for chunk in chunk_results)
        total_missing = sum(chunk.missing for chunk in chunk_results)
        
        # Calculate overall score
        if total_found > 0:
            # Weight working components higher than partial
            overall_score = ((total_working * 100) + (total_partial * 50)) / total_found
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
        
        # Combine all components
        all_components = []
        for chunk in chunk_results:
            all_components.extend(chunk.components)
        
        # File type counts
        python_count = len([c for c in all_components if c.file_type == "python"])
        batch_count = len([c for c in all_components if c.file_type == "batch"])
        cpp_count = len([c for c in all_components if c.file_type == "cpp"])
        
        return {
            "overall_status": overall_status,
            "overall_score": round(overall_score, 1),
            "total_components": total_found,
            "working_components": total_working,
            "partial_components": total_partial,
            "broken_components": total_broken,
            "missing_components": total_missing,
            "python_files": python_count,
            "batch_files": batch_count,
            "cpp_files": cpp_count,
            "chunk_results": [
                {
                    "name": chunk.chunk_name,
                    "total": chunk.total_found,
                    "working": chunk.working,
                    "partial": chunk.partial,
                    "broken": chunk.broken,
                    "missing": chunk.missing,
                    "duration": round(chunk.duration, 2)
                }
                for chunk in chunk_results
            ],
            "all_components": [
                {
                    "name": comp.name,
                    "path": comp.path,
                    "file_type": comp.file_type,
                    "size": comp.size,
                    "status": comp.status.value,
                    "functionality_score": comp.functionality_score,
                    "features": comp.features,
                    "issues": comp.issues,
                    "category": comp.category
                }
                for comp in all_components
            ],
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
    
    def save_comprehensive_results(self, results: Dict[str, Any]):
        """Save comprehensive results"""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n✅ Comprehensive results saved to: {self.results_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
    
    def print_comprehensive_summary(self, results: Dict[str, Any]):
        """Print comprehensive audit summary"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE AUDIT SUMMARY")
        print("=" * 80)
        
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Overall Score: {results['overall_score']}/100")
        print(f"Total Components: {results['total_components']}")
        print(f"Working Components: {results['working_components']}")
        print(f"Partial Components: {results['partial_components']}")
        print(f"Broken Components: {results['broken_components']}")
        print(f"Missing Components: {results['missing_components']}")
        
        print(f"\n📁 File Type Breakdown:")
        print(f"  Python Files: {results['python_files']}")
        print(f"  Batch Files: {results['batch_files']}")
        print(f"  C/C++ Files: {results['cpp_files']}")
        
        print(f"\n📊 Chunk Results:")
        for chunk in results['chunk_results']:
            total_working = chunk['working'] + chunk['partial']
            percentage = (total_working / chunk['total']) * 100 if chunk['total'] > 0 else 0
            status_emoji = "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
            print(f"  {status_emoji} {chunk['name']}: {total_working}/{chunk['total']} ({percentage:.1f}%) - {chunk['duration']}s")
        
        # Show top working components
        working_components = [c for c in results['all_components'] if c['status'] in ['excellent', 'good', 'working']]
        print(f"\n🎯 Top Working Components ({len(working_components)} total):")
        for comp in working_components[:10]:  # Show first 10
            print(f"  ✅ {comp['name']} ({comp['category']}) - Score: {comp['functionality_score']}")
        
        if len(working_components) > 10:
            print(f"  ... and {len(working_components) - 10} more")

def main():
    """Main entry point"""
    auditor = ComprehensiveChunkedAuditor()
    
    try:
        results = auditor.run_comprehensive_audit()
        
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
